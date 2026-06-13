"""RH_ImageToImage — Image to Image via RunningHub workflow."""

import io
import logging

import numpy as np
from PIL import Image

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_ImageToImage:
    """Transform an image using a prompt and RunningHub workflow."""

    CATEGORY = "RunningHub/Model"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    OUTPUT_NODE = True
    DESCRIPTION = "Transform an image using a prompt via RunningHub workflow"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image tensor"}),
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": "", "tooltip": "Text prompt"},
                ),
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "workflow_id": (
                    "STRING",
                    {"default": "", "tooltip": "RunningHub workflow ID for image-to-image"},
                ),
            },
            "optional": {
                "negative_prompt": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "timeout": ("INT", {"default": 300, "min": 1, "max": 9999999}),
            },
        }

    def generate(self, image, prompt, api_key, base_url, workflow_id,
                 negative_prompt="", timeout=300):
        import torch

        if not api_key or not workflow_id:
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Convert and upload input image
        img_array = image[0].cpu().numpy()
        img_array = (img_array * 255).clip(0, 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode="RGB")
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        try:
            uploaded_filename = client.upload_bytes(png_bytes, "input.png", "image")
        except Exception as e:
            logger.error("Image upload failed: %s", e)
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        # Build nodeInfoList
        node_info_list = [
            {"nodeId": "6", "fieldName": "text", "fieldValue": prompt},
            {"nodeId": "10", "fieldName": "image", "fieldValue": uploaded_filename},
        ]
        if negative_prompt:
            node_info_list.append(
                {"nodeId": "7", "fieldName": "text", "fieldValue": negative_prompt}
            )

        # Submit and wait
        try:
            task_data = client.create_task(
                workflow_id=workflow_id, node_info_list=node_info_list
            )
            task_id = task_data.get("taskId", "")
            results = client.wait_for_task(task_id=task_id, timeout=timeout)
        except Exception as e:
            logger.error("ImageToImage failed: %s", e)
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        # Process results
        from .task_execute import _url_to_image_tensor

        images = []
        for r in results:
            if r.is_image:
                try:
                    images.append(_url_to_image_tensor(r.file_url))
                except Exception as e:
                    logger.warning("Failed to download image: %s", e)

        if images:
            return (torch.cat(images, dim=0),)
        return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)
