"""Data models for RunningHub API communication."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ApiConfig:
    """RunningHub API configuration, passed between nodes via STRUCT type."""

    api_key: str
    base_url: str = "https://www.runninghub.cn"
    workflow_id: str = ""
    webapp_id: str = ""

    def to_dict(self) -> dict:
        return {
            "apiKey": self.api_key,
            "base_url": self.base_url,
            "workflowId": self.workflow_id,
            "webappId": self.webapp_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ApiConfig":
        return cls(
            api_key=data.get("apiKey", ""),
            base_url=data.get("base_url", "https://www.runninghub.cn"),
            workflow_id=data.get("workflowId", ""),
            webapp_id=data.get("webappId", ""),
        )


@dataclass
class NodeInfo:
    """A single node parameter entry for the nodeInfoList."""

    node_id: str
    field_name: str
    field_value: str

    def to_dict(self) -> dict:
        return {
            "nodeId": self.node_id,
            "fieldName": self.field_name,
            "fieldValue": self.field_value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NodeInfo":
        return cls(
            node_id=str(data.get("nodeId", "")),
            field_name=data.get("fieldName", ""),
            field_value=data.get("fieldValue", ""),
        )


@dataclass
class TaskResult:
    """A single output file from a completed task."""

    file_url: str
    file_type: str  # "png", "jpg", "mp4", "wav", "txt", "latent"
    node_id: str = ""
    task_cost_time: int = 0

    @property
    def is_image(self) -> bool:
        return self.file_type.lower() in ("png", "jpg", "jpeg", "webp", "bmp")

    @property
    def is_video(self) -> bool:
        return self.file_type.lower() in ("mp4", "webm", "avi", "mov")

    @property
    def is_audio(self) -> bool:
        return self.file_type.lower() in ("wav", "mp3", "ogg", "flac")

    @classmethod
    def from_api_response(cls, data: dict) -> "TaskResult":
        return cls(
            file_url=data.get("fileUrl", ""),
            file_type=data.get("fileType", ""),
            node_id=str(data.get("nodeId", "")),
        )


@dataclass
class TaskStatus:
    """Status of a RunningHub task."""

    task_id: str
    status: str  # "QUEUED", "RUNNING", "SUCCESS", "FAILED", "completed_no_output"
    wss_url: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0

    @property
    def is_completed(self) -> bool:
        return self.status in ("SUCCESS", "FAILED", "completed_no_output")

    @property
    def is_success(self) -> bool:
        return self.status == "SUCCESS"

    @property
    def is_failed(self) -> bool:
        return self.status in ("FAILED", "completed_no_output")
