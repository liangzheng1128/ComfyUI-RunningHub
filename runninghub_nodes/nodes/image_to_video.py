"""RH_ImageToVideo — Image to Video via RunningHub workflow."""

import io
import logging

import numpy as np
from PIL import Image

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_ImageToVideo:
    """Generate video from an image using a RunningHub workflow."""

    CATEGORY = "RunningHub/Model"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    OUTPUT_NODE = True
    DESCRIPTION = "Generate video from an image via RunningHub workflow"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image tensor"}),
                "api_key": ("STRING", {"default": ""}),
                "base_url": (
                    "STRING",
                    {"default": "https://www.runninghub.cn"},
                ),
                "workflow_id": (
                    "STRING",
                    {"default": "", "tooltip": "RunningHub workflow ID for image-to-video"},
                ),
            },
            "optional": {
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "timeout": ("INT", {"default": 600, "min": 1, "max": 9999999}),
            },
        }

    def generate(self, image, api_key, base_url, workflow_id,
                 prompt="", timeout=600):
        if not api_key or not workflow_id:
            return ("Error: Missing API key or workflow ID", "")

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Upload input image
        img_array = image[0].cpu().numpy()
        img_array = (img_array * 255).clip(0, 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode="RGB")
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        try:
            uploaded_filename = client.upload_bytes(png_bytes, "input.png", "image")
        except Exception as e:
            return (f"Upload error: {e}", "")

        # Build nodeInfoList
        node_info_list = [
            {"nodeId": "10", "fieldName": "image", "fieldValue": uploaded_filename},
        ]
        if prompt:
            node_info_list.append(
                {"nodeId": "6", "fieldName": "text", "fieldValue": prompt}
            )

        # Submit and wait
        try:
            task_data = client.create_task(
                workflow_id=workflow_id, node_info_list=node_info_list
            )
            task_id = task_data.get("taskId", "")
            results = client.wait_for_task(task_id=task_id, timeout=timeout)
        except Exception as e:
            return (f"Task failed: {e}", task_id if 'task_id' in dir() else "")

        # Find video result
        for r in results:
            if r.is_video:
                return (r.file_url, task_id)

        # Fallback: return first result URL
        if results:
            return (results[0].file_url, task_id)
        return ("No output", task_id)
