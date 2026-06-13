"""WebSocket handler for real-time RunningHub task progress tracking."""

import json
import logging
import threading
from typing import Optional

logger = logging.getLogger("ComfyUI.RunningHub")


class WebSocketProgressHandler:
    """Handles WebSocket connection for real-time task progress.

    Connects to the RunningHub WebSocket endpoint and tracks node execution
    progress. Falls back gracefully to HTTP polling if WS fails.
    """

    def __init__(self, total_nodes: int = 10):
        self.total_nodes = total_nodes
        self.executed_nodes: set = set()
        self.completed: bool = False
        self.error: Optional[Exception] = None
        self._lock = threading.Lock()
        self._ws = None
        self._thread: Optional[threading.Thread] = None
        self._pbar = None

    def connect(self, wss_url: str, pbar=None) -> None:
        """Start WebSocket connection in a daemon thread.

        Args:
            wss_url: WebSocket URL from task creation response.
            pbar: Optional comfy.utils.ProgressBar instance.
        """
        if not wss_url:
            logger.debug("No WSS URL provided, skipping WebSocket progress")
            return

        self._pbar = pbar

        try:
            import websocket
        except ImportError:
            logger.warning("websocket-client not installed, skipping WS progress")
            return

        def _run():
            try:
                self._ws = websocket.WebSocketApp(
                    wss_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open,
                )
                self._ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                logger.warning("WebSocket thread error: %s", e)
                with self._lock:
                    self.error = e

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def disconnect(self) -> None:
        """Clean up WebSocket connection."""
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None

    @property
    def progress(self) -> float:
        """Return current progress as 0.0 - 1.0."""
        with self._lock:
            if self.total_nodes <= 0:
                return 0.0
            return len(self.executed_nodes) / self.total_nodes

    def _on_open(self, ws):
        logger.debug("WebSocket connected")

    def _on_message(self, ws, message):
        """Parse WebSocket messages for progress updates."""
        try:
            data = json.loads(message)
        except (json.JSONDecodeError, TypeError):
            return

        msg_type = data.get("type", "")
        msg_data = data.get("data", {})

        with self._lock:
            if msg_type == "executing":
                node_id = str(msg_data.get("node", ""))
                if node_id and node_id != "None":
                    self.executed_nodes.add(node_id)
                    count = len(self.executed_nodes)
                    logger.debug("WS progress: %d/%d nodes", count, self.total_nodes)
                    if self._pbar:
                        try:
                            self._pbar.update_absolute(count, self.total_nodes)
                        except Exception:
                            pass

            elif msg_type == "execution_success":
                self.completed = True
                logger.debug("WS: execution_success")
                if self._ws:
                    try:
                        self._ws.close()
                    except Exception:
                        pass

            elif msg_type == "execution_error":
                self.error = Exception(
                    f"Workflow execution error: {msg_data.get('message', 'Unknown')}"
                )
                logger.error("WS: execution_error: %s", msg_data)
                if self._ws:
                    try:
                        self._ws.close()
                    except Exception:
                        pass

    def _on_error(self, ws, error):
        """Handle WebSocket errors — don't fail, HTTP polling continues."""
        logger.warning("WebSocket error (falling back to HTTP polling): %s", error)

    def _on_close(self, ws, close_code, close_msg):
        logger.debug("WebSocket closed: code=%s", close_code)
