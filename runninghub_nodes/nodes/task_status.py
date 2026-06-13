"""RH_TaskStatus — Query RunningHub task status."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TaskStatus:
    """Query the status of a RunningHub task."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "task_id")
    FUNCTION = "check"
    OUTPUT_NODE = True
    DESCRIPTION = "Query the current status of a RunningHub task"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "task_id": ("STRING", {"default": "", "tooltip": "Task ID to check"}),
            },
        }

    def check(self, api_key, base_url, task_id):
        if not api_key or not task_id:
            return ("Missing API key or task ID", task_id)

        client = RunningHubClient(api_key=api_key, base_url=base_url)
        status = client.get_task_status(task_id)
        return (status.status, task_id)
