"""ComfyUI RunningHub Integration - Custom Node Library

This package provides ComfyUI custom nodes for interacting with the RunningHub
cloud AI platform. It enables workflow execution, AI model invocation, file
upload/download, and utility operations.

Install:
    # Method 1: Clone into ComfyUI custom_nodes
    cd ComfyUI/custom_nodes/
    git clone https://github.com/YOUR_USERNAME/ComfyUI-RunningHub.git

    # Method 2: pip install
    pip install ComfyUI-RunningHub
"""

from .runninghub_nodes.nodes.settings import RH_Settings
from .runninghub_nodes.nodes.node_info import RH_NodeInfo
from .runninghub_nodes.nodes.task_execute import RH_ExecuteWorkflow
from .runninghub_nodes.nodes.task_ai_app import RH_ExecuteAIApp
from .runninghub_nodes.nodes.task_status import RH_TaskStatus
from .runninghub_nodes.nodes.task_cancel import RH_TaskCancel
from .runninghub_nodes.nodes.task_outputs import RH_TaskOutputs
from .runninghub_nodes.nodes.upload_image import RH_UploadImage
from .runninghub_nodes.nodes.upload_file import RH_UploadFile
from .runninghub_nodes.nodes.download_image import RH_DownloadImage
from .runninghub_nodes.nodes.download_video import RH_DownloadVideo
from .runninghub_nodes.nodes.text_to_image import RH_TextToImage
from .runninghub_nodes.nodes.image_to_image import RH_ImageToImage
from .runninghub_nodes.nodes.image_to_video import RH_ImageToVideo
from .runninghub_nodes.nodes.text_to_video import RH_TextToVideo
from .runninghub_nodes.nodes.text_to_audio import RH_TextToAudio
from .runninghub_nodes.nodes.utils import (
    RH_AnyToString,
    RH_ExtractImage,
    RH_BatchImages,
    RH_SplitOutput,
)

NODE_CLASS_MAPPINGS = {
    "RH_Settings": RH_Settings,
    "RH_NodeInfo": RH_NodeInfo,
    "RH_ExecuteWorkflow": RH_ExecuteWorkflow,
    "RH_ExecuteAIApp": RH_ExecuteAIApp,
    "RH_TaskStatus": RH_TaskStatus,
    "RH_TaskCancel": RH_TaskCancel,
    "RH_TaskOutputs": RH_TaskOutputs,
    "RH_UploadImage": RH_UploadImage,
    "RH_UploadFile": RH_UploadFile,
    "RH_DownloadImage": RH_DownloadImage,
    "RH_DownloadVideo": RH_DownloadVideo,
    "RH_TextToImage": RH_TextToImage,
    "RH_ImageToImage": RH_ImageToImage,
    "RH_ImageToVideo": RH_ImageToVideo,
    "RH_TextToVideo": RH_TextToVideo,
    "RH_TextToAudio": RH_TextToAudio,
    "RH_AnyToString": RH_AnyToString,
    "RH_ExtractImage": RH_ExtractImage,
    "RH_BatchImages": RH_BatchImages,
    "RH_SplitOutput": RH_SplitOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RH_Settings": "RH Settings",
    "RH_NodeInfo": "RH Node Info",
    "RH_ExecuteWorkflow": "RH Execute Workflow",
    "RH_ExecuteAIApp": "RH Execute AI App",
    "RH_TaskStatus": "RH Task Status",
    "RH_TaskCancel": "RH Task Cancel",
    "RH_TaskOutputs": "RH Task Outputs",
    "RH_UploadImage": "RH Upload Image",
    "RH_UploadFile": "RH Upload File",
    "RH_DownloadImage": "RH Download Image",
    "RH_DownloadVideo": "RH Download Video",
    "RH_TextToImage": "RH Text to Image",
    "RH_ImageToImage": "RH Image to Image",
    "RH_ImageToVideo": "RH Image to Video",
    "RH_TextToVideo": "RH Text to Video",
    "RH_TextToAudio": "RH Text to Audio",
    "RH_AnyToString": "RH Any to String",
    "RH_ExtractImage": "RH Extract Image",
    "RH_BatchImages": "RH Batch Images",
    "RH_SplitOutput": "RH Split Output URLs",
}

WEB_DIRECTORY = "./runninghub_nodes/web/js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
