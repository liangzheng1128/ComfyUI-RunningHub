"""Shared pytest fixtures for RunningHub tests."""

import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_api_key():
    return "test_api_key_12345678901234567890"


@pytest.fixture
def mock_base_url():
    return "https://www.runninghub.cn"


@pytest.fixture
def mock_workflow_id():
    return "1234567890123456789"


@pytest.fixture
def mock_task_id():
    return "task_abc123def456"


@pytest.fixture
def sample_api_config(mock_api_key, mock_base_url, mock_workflow_id):
    return {
        "apiKey": mock_api_key,
        "base_url": mock_base_url,
        "workflowId": mock_workflow_id,
        "webappId": "",
    }


@pytest.fixture
def sample_node_info_list():
    return [
        {"nodeId": "6", "fieldName": "text", "fieldValue": "a beautiful sunset"},
        {"nodeId": "3", "fieldName": "seed", "fieldValue": "42"},
    ]
