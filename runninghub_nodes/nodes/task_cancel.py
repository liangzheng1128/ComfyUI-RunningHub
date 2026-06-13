"""RH_TaskCancel — Cancel a running RunningHub task."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TaskCancel:
    """Cancel a running RunningHub task."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "cancel"
    OUTPUT_NODE = True
    DESCRIPTION = "Cancel a running RunningHub task"

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
            },
        }

    def cancel(self, api_key, base_url, task_id):
        if not api_key or not task_id:
            return ("Missing API key or task ID",)

        client = RunningHubClient(api_key=api_key, base_url=base_url)
        try:
            result = client.cancel_task(task_id)
            msg = result.get("msg", "Cancelled")
            return (f"Task {task_id}: {msg}",)
        except Exception as e:
            return (f"Cancel failed: {e}",)
