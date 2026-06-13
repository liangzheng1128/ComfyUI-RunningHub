"""RH_TextToImage — Text to Image via RunningHub workflow."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_TextToImage:
    """Generate images from text prompt using a RunningHub workflow."""

    CATEGORY = "RunningHub/Model"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    OUTPUT_NODE = True
    DESCRIPTION = "Generate images from text using a RunningHub workflow"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
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
                    {"default": "", "tooltip": "RunningHub workflow ID for text-to-image"},
                ),
            },
            "optional": {
                "negative_prompt": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xFFFFFFFFFFFFFFFF}),
                "timeout": ("INT", {"default": 300, "min": 1, "max": 9999999}),
            },
        }

    def generate(self, prompt, api_key, base_url, workflow_id,
                 negative_prompt="", seed=-1, timeout=300):
        import torch

        if not api_key or not workflow_id:
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Build nodeInfoList
        node_info_list = [
            {"nodeId": "6", "fieldName": "text", "fieldValue": prompt},
        ]
        if negative_prompt:
            node_info_list.append(
                {"nodeId": "7", "fieldName": "text", "fieldValue": negative_prompt}
            )
        if seed >= 0:
            node_info_list.append(
                {"nodeId": "3", "fieldName": "seed", "fieldValue": str(seed)}
            )

        # Submit and wait
        try:
            task_data = client.create_task(
                workflow_id=workflow_id, node_info_list=node_info_list
            )
            task_id = task_data.get("taskId", "")
            results = client.wait_for_task(task_id=task_id, timeout=timeout)
        except Exception as e:
            logger.error("TextToImage failed: %s", e)
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

        # Process image results
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
