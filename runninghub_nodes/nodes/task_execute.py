"""RH_ExecuteWorkflow — Execute a RunningHub cloud workflow and retrieve results.

This is the main workhorse node. It submits a ComfyUI workflow to RunningHub,
monitors progress via WebSocket + HTTP polling, downloads results, and converts
them to native ComfyUI types (IMAGE, VIDEO, AUDIO, STRING).
"""

import logging
import os
import tempfile

import numpy as np

from ..api.client import RunningHubClient
from ..api.exceptions import (
    NoOutputError,
    TaskFailedError,
    TaskTimeoutError,
)
from ..api.websocket_handler import WebSocketProgressHandler

logger = logging.getLogger("ComfyUI.RunningHub")


def _try_import_comfy():
    """Attempt to import comfy modules. Returns (comfy_utils, folder_paths)."""
    try:
        import comfy.utils
        import folder_paths
        return comfy.utils, folder_paths
    except ImportError:
        return None, None


def _download_file(url: str, suffix: str = ".png") -> str:
    """Download a file from URL to a temp directory."""
    import requests

    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()

    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, f"output{suffix}")
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return filepath


def _url_to_image_tensor(url):
    """Download an image URL and convert to ComfyUI IMAGE tensor [1, H, W, 3]."""
    import torch
    from PIL import Image

    filepath = _download_file(url, ".png")
    img = Image.open(filepath).convert("RGB")
    arr = np.array(img).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)  # [1, H, W, 3]


def _url_to_video_path(url: str) -> str:
    """Download a video URL and return the local file path."""
    return _download_file(url, ".mp4")


def _url_to_audio(url: str):
    """Download audio from URL and return ComfyUI AUDIO dict."""
    try:
        import torchaudio

        filepath = _download_file(url, ".wav")
        waveform, sample_rate = torchaudio.load(filepath)
        return {
            "waveform": waveform.unsqueeze(0),  # [1, channels, samples]
            "sample_rate": sample_rate,
        }
    except ImportError:
        logger.warning("torchaudio not available, returning URL as string")
        return None


class RH_ExecuteWorkflow:
    """Execute a RunningHub cloud workflow and return results as native types."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = (
        "IMAGE",
        "IMAGE",
        "STRING",
        "AUDIO",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
    )
    RETURN_NAMES = (
        "images",
        "video_frames",
        "text",
        "audio",
        "output_url1",
        "output_url2",
        "output_url3",
        "output_url4",
        "output_url5",
        "task_id",
    )
    FUNCTION = "process"
    OUTPUT_NODE = True
    DESCRIPTION = "Execute a RunningHub workflow and download results as images, video, audio, or text"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_config": (
                    "STRUCT",
                    {"tooltip": "Connect RH_Settings output here"},
                ),
            },
            "optional": {
                "node_info_list": (
                    "ARRAY",
                    {"default": [], "tooltip": "Connect RH_NodeInfo output(s) here"},
                ),
                "run_timeout": (
                    "INT",
                    {
                        "default": 600,
                        "min": 1,
                        "max": 9999999,
                        "tooltip": "Maximum execution time in seconds",
                    },
                ),
                "poll_interval": (
                    "INT",
                    {
                        "default": 3,
                        "min": 1,
                        "max": 60,
                        "tooltip": "Seconds between status polls",
                    },
                ),
                "use_rtx4090": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Use RTX 4090 GPU (higher cost)"},
                ),
            },
        }

    def process(
        self,
        api_config,
        node_info_list=None,
        run_timeout=600,
        poll_interval=3,
        use_rtx4090=False,
    ):
        api_key = api_config.get("apiKey", "")
        base_url = api_config.get("base_url", "https://www.runninghub.cn")
        workflow_id = api_config.get("workflowId", api_config.get("workflow_id", ""))

        if not api_key:
            return self._empty_result("No API key configured")
        if not workflow_id:
            return self._empty_result("No workflow ID configured")

        client = RunningHubClient(api_key=api_key, base_url=base_url)

        # Submit task
        instance_type = "rtx4090" if use_rtx4090 else None
        task_data = client.create_task(
            workflow_id=workflow_id,
            node_info_list=node_info_list or [],
            instance_type=instance_type,
        )

        task_id = task_data.get("taskId", "")
        wss_url = task_data.get("netWssUrl", "")

        logger.info("Task submitted: %s", task_id)

        # WebSocket progress tracking
        comfy_utils, _ = _try_import_comfy()
        pbar = None
        ws_handler = None

        if wss_url:
            ws_handler = WebSocketProgressHandler(total_nodes=10)
            if comfy_utils:
                pbar = comfy_utils.ProgressBar(10)
            ws_handler.connect(wss_url, pbar=pbar)

        # Progress callback for HTTP polling
        def on_progress(current, total):
            if pbar and total > 0:
                try:
                    pbar.update_absolute(current, total)
                except Exception:
                    pass

        # Wait for completion
        try:
            results = client.wait_for_task(
                task_id=task_id,
                timeout=run_timeout,
                poll_interval=poll_interval,
                progress_callback=on_progress,
            )
        except TaskTimeoutError as e:
            logger.error("Task timed out: %s", e)
            return self._empty_result(f"Task timed out: {task_id}")
        except TaskFailedError as e:
            logger.error("Task failed: %s", e)
            return self._empty_result(f"Task failed: {task_id}")
        except NoOutputError:
            logger.warning("Task completed with no output")
            return self._empty_result(f"No output: {task_id}")
        finally:
            if ws_handler:
                ws_handler.disconnect()

        # Process results
        return self._process_results(results, task_id)

    def _process_results(self, results, task_id):
        """Convert TaskResult list to ComfyUI output types."""
        import torch

        images_list = []
        video_frames = torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        text_output = ""
        audio_output = None
        output_urls = [""] * 5

        for i, result in enumerate(results):
            url = result.file_url
            if i < 5:
                output_urls[i] = url

            try:
                if result.is_image:
                    img_tensor = _url_to_image_tensor(url)
                    images_list.append(img_tensor)

                elif result.is_video:
                    # Return URL for video (download handled by download nodes)
                    pass

                elif result.is_audio:
                    audio_output = _url_to_audio(url)

                else:
                    # Text or other — try to download as text
                    try:
                        import requests

                        resp = requests.get(url, timeout=30)
                        text_output += resp.text + "\n"
                    except Exception:
                        text_output += url + "\n"
            except Exception as e:
                logger.warning("Failed to process result %s: %s", url, e)
                text_output += f"Error: {url} ({e})\n"

        # Stack images
        if images_list:
            images = torch.cat(images_list, dim=0)
        else:
            images = torch.zeros(1, 64, 64, 3, dtype=torch.float32)

        return (
            images,
            video_frames,
            text_output.strip(),
            audio_output,
            *output_urls,
            task_id,
        )

    @staticmethod
    def _empty_result(error_msg=""):
        """Return empty/placeholder results."""
        import torch

        return (
            torch.zeros(1, 64, 64, 3, dtype=torch.float32),  # images
            torch.zeros(1, 64, 64, 3, dtype=torch.float32),  # video_frames
            error_msg,  # text
            None,  # audio
            "", "", "", "", "",  # output_urls
            "",  # task_id
        )
