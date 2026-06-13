"""Custom exception hierarchy for RunningHub API errors."""


class RunningHubError(Exception):
    """Base exception for all RunningHub errors."""

    def __init__(self, message: str = "", code: int = -1):
        self.code = code
        super().__init__(message)


class AuthenticationError(RunningHubError):
    """Invalid or missing API key."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, code=401)


class TaskSubmissionError(RunningHubError):
    """Task creation or submission failed."""

    def __init__(self, message: str = "Failed to submit task", code: int = -1):
        super().__init__(message, code=code)


class TaskTimeoutError(RunningHubError):
    """Task did not complete within the expected time."""

    def __init__(self, message: str = "Task timed out", task_id: str = ""):
        self.task_id = task_id
        super().__init__(message, code=408)


class TaskFailedError(RunningHubError):
    """Task execution failed on the server."""

    def __init__(self, message: str = "Task execution failed", task_id: str = ""):
        self.task_id = task_id
        super().__init__(message, code=500)


class UploadError(RunningHubError):
    """File upload failed."""

    def __init__(self, message: str = "File upload failed"):
        super().__init__(message, code=-1)


class NoOutputError(RunningHubError):
    """Task completed but produced no output."""

    def __init__(self, message: str = "Task completed with no output", task_id: str = ""):
        self.task_id = task_id
        super().__init__(message, code=-1)


class NetworkError(RunningHubError):
    """Network connectivity issue."""

    def __init__(self, message: str = "Network error"):
        super().__init__(message, code=-1)
