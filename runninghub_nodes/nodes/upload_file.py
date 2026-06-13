"""RH_UploadFile — Upload a local file to RunningHub cloud."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_UploadFile:
    """Upload a local file (image/video/audio) to RunningHub."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "upload"
    DESCRIPTION = "Upload a local file to RunningHub cloud"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_config": (
                    "STRUCT",
                    {"tooltip": "Connect RH_Settings output here"},
                ),
                "file_path": (
                    "STRING",
                    {"default": "", "tooltip": "Absolute path to the file to upload"},
                ),
                "file_type": (
                    "STRING",
                    {
                        "default": "image",
                        "tooltip": "File type: image, video, or audio",
                    },
                ),
            },
        }

    def upload(self, api_config, file_path, file_type="image"):
        api_key = api_config.get("apiKey", "")
        base_url = api_config.get("base_url", "https://www.runninghub.cn")

        if not api_key:
            return ("Error: No API key configured",)
        if not file_path:
            return ("Error: No file path provided",)

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        try:
            filename = client.upload_file(file_path, file_type=file_type)
            return (filename,)
        except Exception as e:
            logger.error("Upload failed: %s", e)
            return (f"Error: {e}",)
