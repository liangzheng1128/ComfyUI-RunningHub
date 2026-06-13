"""RH_TextToAudio — Text to Audio via RunningHub workflow."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TextToAudio:
    """Generate audio from text using a RunningHub workflow."""

    CATEGORY = "RunningHub/Model"
    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "audio_url")
    FUNCTION = "generate"
    OUTPUT_NODE = True
    DESCRIPTION = "Generate audio from text via RunningHub workflow"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING",
                    {"multiline": True, "default": "", "tooltip": "Text to convert to audio"},
                ),
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "workflow_id": (
                    "STRING",
                    {"default": "", "tooltip": "RunningHub workflow ID for text-to-audio"},
                ),
            },
            "optional": {
                "timeout": ("INT", {"default": 300, "min": 1, "max": 9999999}),
            },
        }

    def generate(self, text, api_key, base_url, workflow_id, timeout=300):
        if not api_key or not workflow_id:
            return (None, "Error: Missing API key or workflow ID")

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        node_info_list = [
            {"nodeId": "6", "fieldName": "text", "fieldValue": text},
        ]

        task_id = ""
        try:
            task_data = client.create_task(
                workflow_id=workflow_id, node_info_list=node_info_list
            )
            task_id = task_data.get("taskId", "")
            results = client.wait_for_task(task_id=task_id, timeout=timeout)
        except Exception as e:
            return (None, f"Task failed: {e}")

        # Find audio result
        from .task_execute import _url_to_audio

        for r in results:
            if r.is_audio:
                try:
                    audio = _url_to_audio(r.file_url)
                    return (audio, r.file_url)
                except Exception as e:
                    logger.warning("Audio download failed: %s", e)
                    return (None, r.file_url)

        # No audio found
        if results:
            return (None, results[0].file_url)
        return (None, "No output")
