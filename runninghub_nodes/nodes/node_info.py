"""RH_NodeInfo — Build nodeInfoList entries for RunningHub workflows.

Each instance represents one parameter override for a specific workflow node.
Chain multiple RH_NodeInfo nodes together to set multiple parameters.
"""

import logging

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_NodeInfo:
    """Build a nodeInfoList entry for RunningHub workflow execution."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("ARRAY",)
    RETURN_NAMES = ("node_info_list",)
    FUNCTION = "process"
    DESCRIPTION = "Set a workflow node parameter (nodeId + fieldName + fieldValue). Chain multiple to set multiple parameters."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_id": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 999999,
                        "tooltip": "The nodeId of the target workflow node",
                    },
                ),
                "field_name": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "The parameter field name (e.g. 'text', 'seed', 'image')",
                    },
                ),
                "field_value": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "The parameter value to set",
                    },
                ),
            },
            "optional": {
                "previous_list": (
                    "ARRAY",
                    {
                        "default": [],
                        "tooltip": "Connect another RH_NodeInfo output here to chain entries",
                    },
                ),
            },
        }

    def process(self, node_id, field_name, field_value, previous_list=None):
        existing = list(previous_list) if previous_list else []

        entry = {
            "nodeId": str(node_id),
            "fieldName": field_name,
            "fieldValue": field_value,
        }
        existing.append(entry)

        logger.debug(
            "RH_NodeInfo: nodeId=%s, field=%s, total_entries=%d",
            node_id,
            field_name,
            len(existing),
        )
        return (existing,)
