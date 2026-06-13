"""RH_DownloadImage — Download an image URL and convert to ComfyUI IMAGE tensor."""

import logging

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_DownloadImage:
    """Download an image from URL and return as ComfyUI IMAGE tensor."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "download"
    DESCRIPTION = "Download an image from URL and convert to IMAGE tensor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": (
                    "STRING",
                    {"default": "", "tooltip": "Image URL to download"},
                ),
            },
        }

    def download(self, url):
        import torch

        if not url:
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        try:
            from .task_execute import _url_to_image_tensor

            tensor = _url_to_image_tensor(url)
            return (tensor,)
        except Exception as e:
            logger.error("Download failed: %s", e)
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)
