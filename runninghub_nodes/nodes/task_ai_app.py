"""RH_ExecuteAIApp — Execute a RunningHub AI App and retrieve results."""

import logging

from ..api.client import RunningHubClient

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_ExecuteAIApp:
    """Execute a RunningHub AI App and return results."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("IMAGE", "STRING", "AUDIO", "STRING")
    RETURN_NAMES = ("images", "text", "audio", "task_id")
    FUNCTION = "process"
    OUTPUT_NODE = True
    DESCRIPTION = "Execute a RunningHub AI App and download results"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_config": (
                    "STRUCT",
                    {"tooltip": "Connect RH_Settings output here"},
                ),
                "webapp_id": (
                    "STRING",
                    {"default": "", "tooltip": "AI App ID from RunningHub"},
                ),
            },
            "optional": {
                "node_info_list": (
                    "ARRAY",
                    {"default": [], "tooltip": "Connect RH_NodeInfo output(s) here"},
                ),
                "run_timeout": (
                    "INT",
                    {"default": 600, "min": 1, "max": 9999999},
                ),
                "poll_interval": (
                    "INT",
                    {"default": 3, "min": 1, "max": 60},
                ),
                "use_rtx4090": (
                    "BOOLEAN",
                    {"default": False},
                ),
            },
        }

    def process(
        self,
        api_config,
        webapp_id,
        node_info_list=None,
        run_timeout=600,
        poll_interval=3,
        use_rtx4090=False,
    ):
        from .task_execute import _url_to_image_tensor, _url_to_audio

        api_key = api_config.get("apiKey", "")
        base_url = api_config.get("base_url", "https://www.runninghub.cn")

        if not api_key:
            return self._empty_result("No API key configured")
        if not webapp_id:
            return self._empty_result("No AI App ID configured")

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Submit AI App task
        instance_type = "rtx4090" if use_rtx4090 else None
        task_data = client.create_ai_app_task(
            webapp_id=webapp_id,
            node_info_list=node_info_list or [],
            instance_type=instance_type,
        )

        task_id = task_data.get("taskId", "")
        logger.info("AI App task submitted: %s", task_id)

        # Wait for completion
        try:
            results = client.wait_for_task(
                task_id=task_id,
                timeout=run_timeout,
                poll_interval=poll_interval,
            )
        except Exception as e:
            logger.error("AI App task failed: %s", e)
            return self._empty_result(f"Task failed: {e}")

        # Process results
        import torch

        images_list = []
        text_output = ""
        audio_output = None

        for result in results:
            try:
                if result.is_image:
                    img_tensor = _url_to_image_tensor(result.file_url)
                    images_list.append(img_tensor)
                elif result.is_audio:
                    audio_output = _url_to_audio(result.file_url)
                else:
                    text_output += result.file_url + "\n"
            except Exception as e:
                logger.warning("Failed to process result: %s", e)

        images = torch.cat(images_list, dim=0) if images_list else torch.zeros(1, 64, 64, 3, dtype=torch.float32)

        return (images, text_output.strip(), audio_output, task_id)

    @staticmethod
    def _empty_result(error_msg=""):
        import torch

        return (
            torch.zeros(1, 64, 64, 3, dtype=torch.float32),
            error_msg,
            None,
            "",
        )
