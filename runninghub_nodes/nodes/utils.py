"""Utility nodes for RunningHub — type conversion, batch operations, output splitting."""

import logging

logger = logging.getLogger("ComfyUI.RunningHub")


# ---------------------------------------------------------------------------
# RH_AnyToString — Convert any type to a string representation
# ---------------------------------------------------------------------------

class RH_AnyToString:
    """Convert any input to its string representation."""

    CATEGORY = "RunningHub/Utils"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    DESCRIPTION = "Convert any value to a string"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "anything": ("STRING", {"default": ""}),
            },
        }

    def convert(self, anything):
        return (str(anything),)


# ---------------------------------------------------------------------------
# RH_ExtractImage — Extract a single image from a batch
# ---------------------------------------------------------------------------

class RH_ExtractImage:
    """Extract a single image from an image batch by index."""

    CATEGORY = "RunningHub/Utils"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract"
    DESCRIPTION = "Extract a single image from a batch by index"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "image_index": (
                    "INT",
                    {"default": 0, "min": 0, "max": 999999, "tooltip": "0-based index"},
                ),
            },
        }

    def extract(self, images, image_index):
        batch_size = images.shape[0]
        idx = min(image_index, batch_size - 1)
        return (images[idx : idx + 1],)


# ---------------------------------------------------------------------------
# RH_BatchImages — Select images by index range from a batch
# ---------------------------------------------------------------------------

class RH_BatchImages:
    """Select images from a batch using index ranges (e.g. '0-3,5,7-9')."""

    CATEGORY = "RunningHub/Utils"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "batch"
    DESCRIPTION = "Select images from a batch by index ranges (e.g. '0-3,5,7-9')"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "image_indices": (
                    "STRING",
                    {
                        "default": "0",
                        "tooltip": "Comma-separated indices or ranges, e.g. '0-3,5,7-9'",
                    },
                ),
            },
        }

    def batch(self, images, image_indices):
        indices = self._parse_indices(image_indices, images.shape[0])
        selected = images[indices]
        return (selected,)

    @staticmethod
    def _parse_indices(spec: str, max_count: int) -> list:
        """Parse index specification string into a list of indices."""
        result = []
        for part in spec.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                start = int(start.strip())
                end = int(end.strip())
                for i in range(start, min(end + 1, max_count)):
                    result.append(i)
            else:
                idx = int(part)
                if 0 <= idx < max_count:
                    result.append(idx)
        return result


# ---------------------------------------------------------------------------
# RH_SplitOutput — Split a multi-line output URL string into individual URLs
# ---------------------------------------------------------------------------

class RH_SplitOutput:
    """Split multi-line output URLs into individual string outputs."""

    CATEGORY = "RunningHub/Utils"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("url1", "url2", "url3", "url4", "url5")
    FUNCTION = "split"
    OUTPUT_NODE = True
    DESCRIPTION = "Split newline-separated URLs into individual outputs (up to 5)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_urls": (
                    "STRING",
                    {"default": "", "multiline": True, "tooltip": "Newline-separated URLs"},
                ),
            },
        }

    def split(self, output_urls):
        urls = [u.strip() for u in output_urls.split("\n") if u.strip()]
        # Pad to 5 outputs
        while len(urls) < 5:
            urls.append("")
        return tuple(urls[:5])
