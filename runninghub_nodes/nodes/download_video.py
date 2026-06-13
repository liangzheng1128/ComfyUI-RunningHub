"""RH_DownloadVideo — Download a video URL and return as VIDEO or frame sequence."""

import logging

logger = logging.getLogger("ComfyUI.RunningHub")


class RH_DownloadVideo:
    """Download a video from URL. Returns video path and optionally extracted frames."""

    CATEGORY = "RunningHub"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("frames", "video_path")
    FUNCTION = "download"
    DESCRIPTION = "Download a video from URL. Optionally extract frames as IMAGE."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": (
                    "STRING",
                    {"default": "", "tooltip": "Video URL to download"},
                ),
                "extract_frames": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Extract frames as IMAGE tensor (may use a lot of memory)",
                    },
                ),
                "max_frames": (
                    "INT",
                    {
                        "default": 100,
                        "min": 1,
                        "max": 10000,
                        "tooltip": "Maximum number of frames to extract",
                    },
                ),
            },
        }

    def download(self, url, extract_frames=False, max_frames=100):
        import torch

        if not url:
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32), "")

        try:
            from .task_execute import _url_to_video_path

            video_path = _url_to_video_path(url)
        except Exception as e:
            logger.error("Video download failed: %s", e)
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32), "")

        if extract_frames:
            frames = self._extract_frames(video_path, max_frames)
        else:
            frames = torch.zeros(1, 64, 64, 3, dtype=torch.float32)

        return (frames, video_path)

    @staticmethod
    def _extract_frames(video_path, max_frames):
        """Extract frames from video using OpenCV."""
        import torch

        try:
            import cv2
            import numpy as np

            cap = cv2.VideoCapture(video_path)
            frames = []
            count = 0

            while count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                # BGR -> RGB, normalize to 0-1 float32
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                tensor = torch.from_numpy(frame_rgb.astype(np.float32) / 255.0)
                frames.append(tensor)
                count += 1

            cap.release()

            if frames:
                return torch.stack(frames)
            return torch.zeros(1, 64, 64, 3, dtype=torch.float32)

        except ImportError:
            logger.warning("OpenCV not available for frame extraction")
            return torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        except Exception as e:
            logger.error("Frame extraction failed: %s", e)
            return torch.zeros(1, 64, 64, 3, dtype=torch.float32)
