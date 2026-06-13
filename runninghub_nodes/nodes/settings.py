"""RH_Settings — RunningHub API configuration node.

This node collects the API key, base URL, and workflow ID into a STRUCT
that flows to other RunningHub nodes.
"""

import logging

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_Settings:
    """Configure RunningHub API connection settings."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("STRUCT",)
    RETURN_NAMES = ("api_config",)
    FUNCTION = "process"
    DESCRIPTION = "Configure RunningHub API key, base URL, and workflow ID"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Your RunningHub API Key (32 characters)",
                    },
                ),
                "base_url": (
                    "STRING",
                    {
                        "default": "https://www.runninghub.cn",
                        "tooltip": "API base URL: https://www.runninghub.cn (China) or https://www.runninghub.ai (International)",
                    },
                ),
                "workflow_id": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Workflow ID from RunningHub task URL",
                    },
                ),
            },
        }

    def process(self, api_key, base_url, workflow_id):
        if not api_key:
            logger.warning("RH_Settings: API key is empty")

        config = {
            "apiKey": api_key,
            "base_url": base_url.rstrip("/"),
            "workflowId": str(workflow_id),
            "webappId": "",
        }

        logger.info(
            "RH_Settings configured: base_url=%s, workflow_id=%s",
            base_url,
            workflow_id,
        )
        return (config,)
