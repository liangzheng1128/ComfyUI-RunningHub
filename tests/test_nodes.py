"""Tests for ComfyUI node classes — verify INPUT_TYPES, RETURN_TYPES, FUNCTION, etc."""

import pytest

# Node classes
from runninghub_nodes.nodes.settings import RH_Settings
from runninghub_nodes.nodes.node_info import RH_NodeInfo
from runninghub_nodes.nodes.task_status import RH_TaskStatus
from runninghub_nodes.nodes.task_cancel import RH_TaskCancel
from runninghub_nodes.nodes.utils import (
    RH_AnyToString,
    RH_ExtractImage,
    RH_BatchImages,
    RH_SplitOutput,
)


# ---------------------------------------------------------------------------
# Contract Tests — every node must have these attributes
# ---------------------------------------------------------------------------

ALL_NODE_CLASSES = [
    RH_Settings,
    RH_NodeInfo,
    RH_TaskStatus,
    RH_TaskCancel,
    RH_AnyToString,
    RH_ExtractImage,
    RH_BatchImages,
    RH_SplitOutput,
]


@pytest.mark.parametrize("node_cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
class TestNodeContract:
    def test_has_category(self, node_cls):
        assert hasattr(node_cls, "CATEGORY")
        assert isinstance(node_cls.CATEGORY, str)
        assert "RunningHub" in node_cls.CATEGORY

    def test_has_return_types(self, node_cls):
        assert hasattr(node_cls, "RETURN_TYPES")
        assert isinstance(node_cls.RETURN_TYPES, tuple)
        assert len(node_cls.RETURN_TYPES) > 0

    def test_has_function(self, node_cls):
        assert hasattr(node_cls, "FUNCTION")
        assert isinstance(node_cls.FUNCTION, str)
        assert hasattr(node_cls, node_cls.FUNCTION)

    def test_has_input_types_classmethod(self, node_cls):
        assert hasattr(node_cls, "INPUT_TYPES")
        input_types = node_cls.INPUT_TYPES()
        assert isinstance(input_types, dict)
        assert "required" in input_types

    def test_has_description(self, node_cls):
        assert hasattr(node_cls, "DESCRIPTION")
        assert isinstance(node_cls.DESCRIPTION, str)
        assert len(node_cls.DESCRIPTION) > 0


# ---------------------------------------------------------------------------
# Functional Tests
# ---------------------------------------------------------------------------


class TestRHSettings:
    def test_process(self, sample_api_config):
        node = RH_Settings()
        result = node.process(
            api_key="test_key",
            base_url="https://www.runninghub.cn",
            workflow_id="wf123",
        )
        assert isinstance(result, tuple)
        assert len(result) == 1
        config = result[0]
        assert config["apiKey"] == "test_key"
        assert config["workflowId"] == "wf123"

    def test_empty_api_key_warning(self):
        """Should not crash with empty API key."""
        node = RH_Settings()
        result = node.process(api_key="", base_url="https://x.com", workflow_id="wf1")
        assert result[0]["apiKey"] == ""


class TestRHNodeInfo:
    def test_single_entry(self):
        node = RH_NodeInfo()
        result = node.process(node_id=6, field_name="text", field_value="hello")
        assert isinstance(result, tuple)
        assert len(result[0]) == 1
        assert result[0][0]["nodeId"] == "6"

    def test_chained_entries(self):
        node = RH_NodeInfo()
        # First entry
        r1 = node.process(node_id=6, field_name="text", field_value="hello")
        # Chain second
        r2 = node.process(
            node_id=3, field_name="seed", field_value="42", previous_list=r1[0]
        )
        assert len(r2[0]) == 2
        assert r2[0][1]["nodeId"] == "3"


class TestRHExtractImage:
    def test_extract(self):
        import torch

        node = RH_ExtractImage()
        batch = torch.rand(5, 64, 64, 3)
        result = node.extract(batch, image_index=2)
        assert result[0].shape == (1, 64, 64, 3)

    def test_extract_out_of_range(self):
        import torch

        node = RH_ExtractImage()
        batch = torch.rand(3, 64, 64, 3)
        result = node.extract(batch, image_index=10)
        # Should clamp to last index
        assert result[0].shape == (1, 64, 64, 3)


class TestRHBatchImages:
    def test_parse_indices(self):
        result = RH_BatchImages._parse_indices("0-2,4", 10)
        assert result == [0, 1, 2, 4]

    def test_parse_single(self):
        result = RH_BatchImages._parse_indices("3", 10)
        assert result == [3]

    def test_parse_out_of_range(self):
        result = RH_BatchImages._parse_indices("0,99", 5)
        assert result == [0]


class TestRHSplitOutput:
    def test_split(self):
        node = RH_SplitOutput()
        result = node.split("url1\nurl2\nurl3")
        assert result[0] == "url1"
        assert result[1] == "url2"
        assert result[2] == "url3"
        assert result[3] == ""
        assert result[4] == ""

    def test_split_empty(self):
        node = RH_SplitOutput()
        result = node.split("")
        assert all(r == "" for r in result)


class TestRHAnyToString:
    def test_convert(self):
        node = RH_AnyToString()
        result = node.convert("hello")
        assert result == ("hello",)

    def test_convert_number(self):
        node = RH_AnyToString()
        result = node.convert("42")
        assert result == ("42",)


# ---------------------------------------------------------------------------
# Registration Test — verify NODE_CLASS_MAPPINGS integrity
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_node_class_mappings_importable(self):
        """Verify the root __init__.py NODE_CLASS_MAPPINGS loads without error."""
        # Import the root package
        import importlib
        import sys

        # Add project root to path
        sys.path.insert(0, "/Users/liangzheng/rh")
        import __init__ as rh_init

        mappings = rh_init.NODE_CLASS_MAPPINGS
        assert isinstance(mappings, dict)
        assert len(mappings) == 20

        display_mappings = rh_init.NODE_DISPLAY_NAME_MAPPINGS
        assert len(display_mappings) == 20

        # Every key in mappings must have a corresponding display name
        for key in mappings:
            assert key in display_mappings, f"Missing display name for {key}"
