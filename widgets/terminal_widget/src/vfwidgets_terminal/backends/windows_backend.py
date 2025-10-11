"""Windows terminal backend implementation using ConPTY."""

import logging
import time
from typing import TYPE_CHECKING, Optional

from .base import TerminalBackend

if TYPE_CHECKING:
    from ..session import TerminalSession

logger = logging.getLogger(__name__)


class WindowsTerminalBackend(TerminalBackend):
    """
    Terminal backend for Windows systems using ConPTY.

    Requires pywinpty package to be installed.
    """

    def __init__(self):
        """Initialize Windows backend."""
        try:
            import winpty

            self.winpty = winpty
        except ImportError as e:
            raise RuntimeError(
                "Windows terminal backend requires pywinpty. "
                "Install with: pip install pywinpty"
            ) from e

    def start_process(self, session: "TerminalSession") -> bool:
        """Start a terminal process using ConPTY."""
        try:
            # Build command
            cmd = session.command
            if session.args:
                cmd = f"{cmd} {' '.join(session.args)}"

            # Create PTY process
            pty = self.winpty.PtyProcess.spawn(
                cmd,
                cwd=session.cwd,
                env=session.env if session.env else None,
                dimensions=(session.rows, session.cols),
            )

            # Store in session metadata
            session.metadata["pty"] = pty
            session.child_pid = pty.pid if hasattr(pty, "pid") else None
            session.active = True

            logger.info(
                f"Started Windows terminal process for session {session.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start Windows terminal process: {e}")
            return False

    def read_output(
        self, session: "TerminalSession", max_bytes: int = 1024 * 20
    ) -> Optional[str]:
        """Read output from the terminal process."""
        pty = session.metadata.get("pty")
        if not pty:
            return None

        try:
            # Try to read non-blocking
            output = pty.read(max_bytes)
            if output:
                session.last_activity = time.time()
                return output
            return None

        except Exception as e:
            logger.debug(f"Read error for session {session.session_id}: {e}")
            session.active = False
            return None

    def write_input(self, session: "TerminalSession", data: str) -> bool:
        """Write input to the terminal process."""
        pty = session.metadata.get("pty")
        if not pty:
            return False

        try:
            pty.write(data)
            session.last_activity = time.time()
            return True
        except Exception as e:
            logger.error(f"Write error for session {session.session_id}: {e}")
            return False

    def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
        """Resize the terminal window."""
        pty = session.metadata.get("pty")
        if not pty:
            return False

        try:
            pty.setwinsize(rows, cols)
            session.rows = rows
            session.cols = cols
            return True
        except Exception as e:
            logger.error(f"Resize error for session {session.session_id}: {e}")
            return False

    def is_process_alive(self, session: "TerminalSession") -> bool:
        """Check if the terminal process is still running."""
        pty = session.metadata.get("pty")
        if not pty:
            return False

        try:
            return pty.isalive()
        except Exception:
            return False

    def terminate_process(self, session: "TerminalSession") -> bool:
        """Terminate the terminal process."""
        pty = session.metadata.get("pty")
        if not pty:
            return True

        try:
            if pty.isalive():
                pty.terminate()
            return True
        except Exception as e:
            logger.error(
                f"Failed to terminate process for session {session.session_id}: {e}"
            )
            return False

    def cleanup(self, session: "TerminalSession") -> None:
        """Clean up resources for a terminal session."""
        pty = session.metadata.get("pty")
        if pty:
            try:
                if pty.isalive():
                    pty.terminate()
                pty.close()
            except Exception:
                pass
            session.metadata.pop("pty", None)

        session.child_pid = None
        session.active = False

    def poll_process(self, session: "TerminalSession", timeout: float = 0.01) -> bool:
        """Poll the terminal process for available data."""
        pty = session.metadata.get("pty")
        if not pty:
            return False

        try:
            # Windows ptyprocess doesn't have direct poll
            # We'll just check if process is alive
            return pty.isalive()
        except Exception:
            return False
