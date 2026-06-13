"""RH_UploadImage — Upload a ComfyUI IMAGE tensor to RunningHub cloud."""

import io
import logging

import numpy as np
from PIL import Image

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_UploadImage:
    """Upload an IMAGE tensor to RunningHub and return the remote filename."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "upload"
    DESCRIPTION = "Upload a ComfyUI IMAGE tensor to RunningHub"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_config": (
                    "STRUCT",
                    {"tooltip": "Connect RH_Settings output here"},
                ),
                "image": ("IMAGE", {"tooltip": "Image tensor to upload"}),
            },
        }

    def upload(self, api_config, image):
        api_key = api_config.get("apiKey", "")
        base_url = api_config.get("base_url", "https://www.runninghub.cn")

        if not api_key:
            return ("Error: No API key configured",)

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Convert tensor [B, H, W, 3] float32 to PIL Image
        # Use first image if batch
        img_array = image[0].cpu().numpy()
        img_array = (img_array * 255).clip(0, 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode="RGB")

        # Encode to PNG bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        try:
            filename = client.upload_bytes(png_bytes, "image.png", "image")
            return (filename,)
        except Exception as e:
            logger.error("Upload failed: %s", e)
            return (f"Error: {e}",)
