"""Tests for RunningHub API client."""

import json
from unittest.mock import MagicMock, patch

import pytest

from runninghub_nodes.api.client import RunningHubClient
from runninghub_nodes.api.exceptions import (
    AuthenticationError,
    NetworkError,
    TaskSubmissionError,
    TaskTimeoutError,
    UploadError,
)
from runninghub_nodes.api.models import ApiConfig, NodeInfo, TaskResult, TaskStatus


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------


class TestApiConfig:
    def test_to_dict(self, mock_api_key, mock_base_url, mock_workflow_id):
        config = ApiConfig(
            api_key=mock_api_key,
            base_url=mock_base_url,
            workflow_id=mock_workflow_id,
        )
        d = config.to_dict()
        assert d["apiKey"] == mock_api_key
        assert d["base_url"] == mock_base_url
        assert d["workflowId"] == mock_workflow_id

    def test_from_dict(self, mock_api_key):
        d = {"apiKey": mock_api_key, "base_url": "https://example.com"}
        config = ApiConfig.from_dict(d)
        assert config.api_key == mock_api_key
        assert config.base_url == "https://example.com"


class TestNodeInfo:
    def test_to_dict(self):
        info = NodeInfo(node_id="6", field_name="text", field_value="hello")
        d = info.to_dict()
        assert d == {"nodeId": "6", "fieldName": "text", "fieldValue": "hello"}

    def test_from_dict(self):
        d = {"nodeId": "3", "fieldName": "seed", "fieldValue": "42"}
        info = NodeInfo.from_dict(d)
        assert info.node_id == "3"
        assert info.field_name == "seed"
        assert info.field_value == "42"


class TestTaskResult:
    def test_is_image(self):
        r = TaskResult(file_url="http://x/1.png", file_type="png")
        assert r.is_image is True
        assert r.is_video is False
        assert r.is_audio is False

    def test_is_video(self):
        r = TaskResult(file_url="http://x/1.mp4", file_type="mp4")
        assert r.is_video is True
        assert r.is_image is False

    def test_is_audio(self):
        r = TaskResult(file_url="http://x/1.wav", file_type="wav")
        assert r.is_audio is True

    def test_from_api_response(self):
        data = {"fileUrl": "http://x/1.png", "fileType": "png", "nodeId": "17"}
        r = TaskResult.from_api_response(data)
        assert r.file_url == "http://x/1.png"
        assert r.file_type == "png"
        assert r.node_id == "17"


class TestTaskStatus:
    def test_is_completed(self):
        s = TaskStatus(task_id="t1", status="SUCCESS")
        assert s.is_completed is True
        assert s.is_success is True

    def test_is_failed(self):
        s = TaskStatus(task_id="t1", status="FAILED")
        assert s.is_failed is True
        assert s.is_completed is True

    def test_is_running(self):
        s = TaskStatus(task_id="t1", status="RUNNING")
        assert s.is_completed is False
        assert s.is_success is False


# ---------------------------------------------------------------------------
# Client Tests
# ---------------------------------------------------------------------------


class TestRunningHubClient:
    def test_init(self, mock_api_key, mock_base_url):
        client = RunningHubClient(api_key=mock_api_key, base_url=mock_base_url)
        assert client.api_key == mock_api_key
        assert client.base_url == mock_base_url.rstrip("/")

    def test_init_strips_trailing_slash(self, mock_api_key):
        client = RunningHubClient(api_key=mock_api_key, base_url="https://example.com/")
        assert client.base_url == "https://example.com"

    @patch("runninghub_nodes.api.client.requests.Session")
    def test_create_task_success(self, mock_session_cls, mock_api_key, mock_base_url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "code": 0,
            "data": {
                "taskId": "task123",
                "taskStatus": "QUEUED",
                "netWssUrl": "wss://example.com/ws",
            },
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        client = RunningHubClient(api_key=mock_api_key, base_url=mock_base_url)
        client._session = mock_session

        result = client.create_task(workflow_id="wf123")
        assert result["taskId"] == "task123"
        assert result["taskStatus"] == "QUEUED"

    @patch("runninghub_nodes.api.client.requests.Session")
    def test_create_task_failure(self, mock_session_cls, mock_api_key, mock_base_url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"code": 1, "msg": "Invalid workflow"}

        mock_session = MagicMock()
        mock_session.request.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        client = RunningHubClient(api_key=mock_api_key, base_url=mock_base_url)
        client._session = mock_session

        with pytest.raises(TaskSubmissionError):
            client.create_task(workflow_id="bad_id")

    def test_wait_for_task_timeout(self, mock_api_key, mock_base_url):
        client = RunningHubClient(api_key=mock_api_key, base_url=mock_base_url)

        with patch.object(client, "get_task_outputs", return_value={"data": {"taskStatus": "RUNNING"}}):
            with pytest.raises(TaskTimeoutError):
                client.wait_for_task(task_id="t1", timeout=1, poll_interval=0.1)

    @patch("runninghub_nodes.api.client.requests.Session")
    def test_get_task_status(self, mock_session_cls, mock_api_key, mock_base_url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "code": 0,
            "data": {"taskStatus": "RUNNING", "netWssUrl": "wss://x"},
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        client = RunningHubClient(api_key=mock_api_key, base_url=mock_base_url)
        client._session = mock_session

        status = client.get_task_status("task123")
        assert status.status == "RUNNING"
        assert status.wss_url == "wss://x"
