"""RunningHub API client — handles all HTTP communication with RunningHub cloud."""

import io
import json
import logging
import os
import time
from typing import Callable, Optional

import requests

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NoOutputError,
    TaskFailedError,
    TaskSubmissionError,
    TaskTimeoutError,
    UploadError,
)
from .models import TaskResult, TaskStatus

logger = logging.getLogger("ComfyUI.RunningHub")


class RunningHubClient:
    """Reusable RunningHub API client.

    Each method call is self-contained (no session state beyond auth),
    so the client is safe to share across nodes.
    """

    DEFAULT_CN_BASE = "https://www.runninghub.cn"
    DEFAULT_INTL_BASE = "https://www.runninghub.ai"

    def __init__(self, api_key: str, base_url: str = DEFAULT_CN_BASE):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ComfyUI-RunningHub/1.0.0",
        })

    # ------------------------------------------------------------------
    # Task Management
    # ------------------------------------------------------------------

    def create_task(
        self,
        workflow_id: str,
        node_info_list: Optional[list] = None,
        instance_type: Optional[str] = None,
    ) -> dict:
        """Submit a ComfyUI workflow task.

        Args:
            workflow_id: RunningHub workflow ID.
            node_info_list: List of dicts with nodeId/fieldName/fieldValue.
            instance_type: GPU type, e.g. "rtx4090".

        Returns:
            API response dict with taskId, taskStatus, netWssUrl, etc.

        Raises:
            TaskSubmissionError: If the API rejects the request.
        """
        payload = {
            "workflowId": str(workflow_id),
            "apiKey": self.api_key,
        }
        if node_info_list:
            payload["nodeInfoList"] = node_info_list
        if instance_type:
            payload["instanceType"] = instance_type

        resp = self._request("POST", "/task/openapi/create", json_data=payload)
        data = resp.get("data", {})
        code = resp.get("code", -1)

        if code != 0:
            msg = resp.get("msg", "Unknown error")
            raise TaskSubmissionError(
                f"Task submission failed (code={code}): {msg}", code=code
            )

        logger.info("Task created: %s", data.get("taskId", ""))
        return data

    def create_ai_app_task(
        self,
        webapp_id: str,
        node_info_list: Optional[list] = None,
        instance_type: Optional[str] = None,
    ) -> dict:
        """Submit an AI App task.

        Args:
            webapp_id: RunningHub AI App ID (will be cast to int).
            node_info_list: List of dicts with nodeId/fieldName/fieldValue.
            instance_type: GPU type.

        Returns:
            API response dict with taskId, etc.
        """
        payload = {
            "webappId": int(webapp_id),
            "apiKey": self.api_key,
        }
        if node_info_list:
            payload["nodeInfoList"] = node_info_list
        if instance_type:
            payload["instanceType"] = instance_type

        resp = self._request("POST", "/task/openapi/ai-app/run", json_data=payload)
        data = resp.get("data", {})
        code = resp.get("code", -1)

        if code != 0:
            msg = resp.get("msg", "Unknown error")
            raise TaskSubmissionError(
                f"AI App task submission failed (code={code}): {msg}", code=code
            )

        logger.info("AI App task created: %s", data.get("taskId", ""))
        return data

    def get_task_outputs(self, task_id: str) -> dict:
        """Query task outputs.

        Returns:
            If task is still running/queued: {"taskStatus": "RUNNING", ...}
            If task succeeded: {"data": [TaskResult, ...]}
            If task failed: {"data": {"taskStatus": "FAILED", ...}}
        """
        payload = {
            "taskId": str(task_id),
            "apiKey": self.api_key,
        }
        return self._request("POST", "/task/openapi/outputs", json_data=payload)

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Check task status.

        Returns:
            TaskStatus dataclass.
        """
        payload = {
            "taskId": str(task_id),
            "apiKey": self.api_key,
        }
        resp = self._request("POST", "/task/openapi/status", json_data=payload)
        data = resp.get("data", {})
        return TaskStatus(
            task_id=str(task_id),
            status=data.get("taskStatus", "UNKNOWN"),
            wss_url=data.get("netWssUrl"),
        )

    def cancel_task(self, task_id: str) -> dict:
        """Cancel a running task.

        Returns:
            API response dict.
        """
        payload = {
            "taskId": str(task_id),
            "apiKey": self.api_key,
        }
        return self._request("POST", "/task/openapi/cancel", json_data=payload)

    def wait_for_task(
        self,
        task_id: str,
        timeout: int = 600,
        poll_interval: int = 3,
        progress_callback: Optional[Callable] = None,
    ) -> list:
        """Poll task outputs until completion or timeout.

        Args:
            task_id: The task to wait for.
            timeout: Maximum wait time in seconds.
            poll_interval: Seconds between polls.
            progress_callback: Optional callback(current, total) for progress bar.

        Returns:
            List of TaskResult objects.

        Raises:
            TaskTimeoutError: If timeout is reached.
            TaskFailedError: If the task fails.
            NoOutputError: If task completes with no output.
        """
        start_time = time.time()
        poll_count = 0

        while time.time() - start_time < timeout:
            try:
                resp = self.get_task_outputs(task_id)
            except Exception as e:
                logger.warning("Error polling task %s: %s", task_id, e)
                time.sleep(poll_interval)
                continue

            data = resp.get("data", {})

            # Task still running
            if isinstance(data, dict):
                status = data.get("taskStatus", "")
                if status in ("RUNNING", "QUEUED"):
                    poll_count += 1
                    if progress_callback:
                        progress_callback(poll_count, 0)
                    time.sleep(poll_interval)
                    continue
                if status == "FAILED":
                    raise TaskFailedError(
                        f"Task {task_id} failed", task_id=task_id
                    )
                if status == "completed_no_output":
                    raise NoOutputError(
                        f"Task {task_id} completed with no output",
                        task_id=task_id,
                    )

            # Task succeeded — data is a list of results
            if isinstance(data, list):
                results = [TaskResult.from_api_response(item) for item in data]
                if progress_callback:
                    progress_callback(1, 1)
                return results

            # Unexpected response shape
            poll_count += 1
            time.sleep(poll_interval)

        raise TaskTimeoutError(
            f"Task {task_id} timed out after {timeout}s", task_id=task_id
        )

    # ------------------------------------------------------------------
    # File Upload
    # ------------------------------------------------------------------

    def upload_file(self, file_path: str, file_type: str = "image") -> str:
        """Upload a local file to RunningHub.

        Args:
            file_path: Absolute path to the file.
            file_type: One of "image", "video", "audio".

        Returns:
            Remote filename string (e.g. "api/xxx.png").
        """
        if not os.path.isfile(file_path):
            raise UploadError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_data = f.read()

        return self.upload_bytes(file_data, filename, file_type)

    def upload_bytes(
        self, data: bytes, filename: str, file_type: str = "image"
    ) -> str:
        """Upload raw bytes to RunningHub.

        Args:
            data: File content as bytes.
            filename: Filename for the upload.
            file_type: One of "image", "video", "audio".

        Returns:
            Remote filename string (e.g. "api/xxx.png").
        """
        url = f"{self.base_url}/task/openapi/upload"
        files = {"file": (filename, io.BytesIO(data))}
        form_data = {
            "apiKey": (None, self.api_key),
            "fileType": (None, file_type),
        }

        try:
            resp = requests.post(url, files=files, data=form_data, timeout=120)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise UploadError(f"Upload failed: {e}") from e

        result = resp.json()
        code = result.get("code", -1)
        if code != 0:
            msg = result.get("msg", "Unknown error")
            raise UploadError(f"Upload rejected (code={code}): {msg}")

        remote_name = result.get("data", {}).get("fileName", "")
        if not remote_name:
            raise UploadError("Upload succeeded but no filename returned")

        logger.info("Uploaded %s -> %s", filename, remote_name)
        return remote_name

    def upload_lora(self, file_path: str) -> str:
        """Upload a LoRA model file.

        Returns:
            Remote filename string.
        """
        return self.upload_file(file_path, file_type="lora")

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_account_status(self) -> dict:
        """Check account status and current task count."""
        payload = {"apikey": self.api_key}
        resp = self._request("POST", "/uc/openapi/accountStatus", json_data=payload)
        return resp.get("data", {})

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def get_workflow_json(self, workflow_id: str) -> dict:
        """Fetch the JSON definition of a workflow."""
        payload = {
            "apiKey": self.api_key,
            "workflowId": str(workflow_id),
        }
        resp = self._request("POST", "/api/openapi/getJsonApiFormat", json_data=payload)
        return resp.get("data", {})

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None,
        files: Optional[dict] = None,
        retry: int = 3,
        retry_delay: float = 1.0,
    ) -> dict:
        """Core request method with retry and exponential backoff.

        Args:
            method: HTTP method ("POST", "GET").
            endpoint: API endpoint path (e.g. "/task/openapi/create").
            json_data: JSON body.
            files: Multipart files.
            retry: Max retry attempts.
            retry_delay: Initial delay between retries (seconds).

        Returns:
            Parsed JSON response dict.

        Raises:
            AuthenticationError: On 401 responses.
            NetworkError: On connection failures after retries.
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retry):
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    files=files,
                    timeout=60,
                )
                resp.raise_for_status()
                result = resp.json()

                # Check for auth errors in the response body
                code = result.get("code", -1)
                msg = result.get("msg", "")
                if code in (401, 403) or "apiKey" in msg.lower():
                    raise AuthenticationError(f"Authentication failed: {msg}")

                return result

            except requests.ConnectionError as e:
                logger.warning(
                    "Connection error (attempt %d/%d): %s", attempt + 1, retry, e
                )
                if attempt == retry - 1:
                    raise NetworkError(
                        f"Failed to connect to {url} after {retry} attempts"
                    ) from e
                time.sleep(retry_delay * (2 ** attempt))

            except requests.Timeout as e:
                logger.warning(
                    "Request timeout (attempt %d/%d): %s", attempt + 1, retry, e
                )
                if attempt == retry - 1:
                    raise NetworkError(
                        f"Request to {url} timed out after {retry} attempts"
                    ) from e
                time.sleep(retry_delay * (2 ** attempt))

            except requests.HTTPError as e:
                status = e.response.status_code if e.response else 0
                if status in (401, 403):
                    raise AuthenticationError(
                        f"HTTP {status}: Authentication failed"
                    ) from e
                if status >= 500:
                    logger.warning(
                        "Server error %d (attempt %d/%d)", status, attempt + 1, retry
                    )
                    if attempt == retry - 1:
                        raise NetworkError(
                            f"Server error {status} after {retry} attempts"
                        ) from e
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    raise NetworkError(f"HTTP {status}: {e}") from e

            except json.JSONDecodeError as e:
                raise NetworkError(f"Invalid JSON response from {url}") from e

        # Should not reach here, but just in case
        raise NetworkError(f"Request to {url} failed after {retry} attempts")
