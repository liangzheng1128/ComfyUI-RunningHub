"""RH_TextToVideo — Text to Video via RunningHub workflow."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TextToVideo:
    """Generate video from text using a RunningHub workflow."""

    CATEGORY = "RunningHub/Model"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    OUTPUT_NODE = True
    DESCRIPTION = "Generate video from text via RunningHub workflow"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": "", "tooltip": "Text prompt for video generation"},
                ),
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "workflow_id": (
                    "STRING",
                    {"default": "", "tooltip": "RunningHub workflow ID for text-to-video"},
                ),
            },
            "optional": {
                "negative_prompt": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "timeout": ("INT", {"default": 600, "min": 1, "max": 9999999}),
            },
        }

    def generate(self, prompt, api_key, base_url, workflow_id,
                 negative_prompt="", timeout=600):
        if not api_key or not workflow_id:
            return ("Error: Missing API key or workflow ID", "")

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Build nodeInfoList
        node_info_list = [
            {"nodeId": "6", "fieldName": "text", "fieldValue": prompt},
        ]
        if negative_prompt:
            node_info_list.append(
                {"nodeId": "7", "fieldName": "text", "fieldValue": negative_prompt}
            )

        # Submit and wait
        task_id = ""
        try:
            task_data = client.create_task(
                workflow_id=workflow_id, node_info_list=node_info_list
            )
            task_id = task_data.get("taskId", "")
            results = client.wait_for_task(task_id=task_id, timeout=timeout)
        except Exception as e:
            return (f"Task failed: {e}", task_id)

        # Find video result
        for r in results:
            if r.is_video:
                return (r.file_url, task_id)

        if results:
            return (results[0].file_url, task_id)
        return ("No output", task_id)
