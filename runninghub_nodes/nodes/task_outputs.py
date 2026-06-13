"""RH_TaskOutputs — Retrieve task output results (with optional wait)."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TaskOutputs:
    """Retrieve outputs from a completed or running task."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "output_urls", "task_id")
    FUNCTION = "get_outputs"
    OUTPUT_NODE = True
    DESCRIPTION = "Get output results from a RunningHub task"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "task_id": ("STRING", {"default": ""}),
                "wait_for_result": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Wait until task completes"},
                ),
                "timeout": (
                    "INT",
                    {"default": 300, "min": 1, "max": 9999999},
                ),
            },
        }

    def get_outputs(self, api_key, base_url, task_id, wait_for_result=True, timeout=300):
        import torch

        if not api_key or not task_id:
            return (
                torch.zeros(1, 64, 64, 3, dtype=torch.float32),
                "Missing API key or task ID",
                task_id,
            )

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        if wait_for_result:
            try:
                results = client.wait_for_task(task_id=task_id, timeout=timeout)
            except Exception as e:
                return (
                    torch.zeros(1, 64, 64, 3, dtype=torch.float32),
                    f"Error: {e}",
                    task_id,
                )
        else:
            resp = client.get_task_outputs(task_id)
            data = resp.get("data", {})
            if isinstance(data, dict):
                status = data.get("taskStatus", "UNKNOWN")
                return (
                    torch.zeros(1, 64, 64, 3, dtype=torch.float32),
                    f"Task status: {status}",
                    task_id,
                )
            from ..api.models import TaskResult

            results = [TaskResult.from_api_response(item) for item in data]

        # Process results
        from .task_execute import _url_to_image_tensor

        images_list = []
        urls = []
        for r in results:
            urls.append(r.file_url)
            if r.is_image:
                try:
                    images_list.append(_url_to_image_tensor(r.file_url))
                except Exception as e:
                    logger.warning("Failed to download image: %s", e)

        images = torch.cat(images_list, dim=0) if images_list else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        url_text = "\n".join(urls)

        return (images, url_text, task_id)
