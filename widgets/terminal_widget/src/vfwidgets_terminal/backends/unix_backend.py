"""Unix/Linux terminal backend implementation using pty."""

import fcntl
import logging
import os
import pty
import select
import signal
import struct
import termios
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .base import TerminalBackend

if TYPE_CHECKING:
    from ..session import TerminalSession

logger = logging.getLogger(__name__)


class UnixTerminalBackend(TerminalBackend):
    """
    Terminal backend for Unix/Linux systems using pty.

    Uses traditional Unix PTY (pseudo-terminal) system for terminal emulation.
    """

    # Version of shell integration scripts (update when changing)
    SHELL_INTEGRATION_VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self._shell_integration_dir: Optional[Path] = None
        self._ensure_shell_integration_dir()

    def _ensure_shell_integration_dir(self) -> None:
        """Ensure shell integration directory exists.

        Creates ~/.config/viloxterm/shell_integration/ if it doesn't exist.
        Falls back to temp directory if creation fails.
        """
        try:
            # Use XDG_CONFIG_HOME if set, otherwise ~/.config
            config_home = os.environ.get("XDG_CONFIG_HOME")
            if config_home:
                config_dir = Path(config_home) / "viloxterm"
            else:
                config_dir = Path.home() / ".config" / "viloxterm"

            self._shell_integration_dir = config_dir / "shell_integration"
            self._shell_integration_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Shell integration directory: {self._shell_integration_dir}")

        except Exception as e:
            logger.warning(f"Failed to create shell integration directory: {e}")
            logger.warning("Will fall back to temporary files if needed")
            self._shell_integration_dir = None

    def _get_shell_type(self, command: str) -> str:
        """Detect shell type from command.

        Args:
            command: Shell command path

        Returns:
            One of: 'bash', 'zsh', 'fish', 'unknown'
        """
        command_lower = os.path.basename(command).lower()

        if "bash" in command_lower:
            return "bash"
        elif "zsh" in command_lower:
            return "zsh"
        elif "fish" in command_lower:
            return "fish"
        else:
            return "unknown"

    def _get_or_create_bash_integration(self) -> Path:
        """Get or create bash integration file.

        Returns:
            Path to bash integration file
        """
        if not self._shell_integration_dir:
            # Fallback: create temp file
            import tempfile

            fd, path = tempfile.mkstemp(prefix="vfterm_osc7_bash_", suffix=".bashrc")
            os.close(fd)
            logger.warning("Using temporary bash rcfile (config dir unavailable)")
            bash_file = Path(path)
        else:
            bash_file = self._shell_integration_dir / "bashrc"

        # Check if file exists and has correct version
        needs_update = True
        if bash_file.exists():
            try:
                content = bash_file.read_text()
                if f"# Version: {self.SHELL_INTEGRATION_VERSION}" in content:
                    needs_update = False
                    logger.debug(f"Using existing bash integration: {bash_file}")
            except Exception as e:
                logger.warning(f"Failed to read bash integration file: {e}")

        if needs_update:
            rcfile_content = f"""# VFWidgets Terminal - OSC 7 Shell Integration (Bash)
# Version: {self.SHELL_INTEGRATION_VERSION}
# This file enables working directory tracking for ViloxTerm
# Generated automatically - manual edits will be preserved unless version changes

# OSC 7: Report working directory to terminal emulator
__vfterm_osc7_cwd() {{
    # Get hostname with fallback for minimal environments
    local host="${{HOSTNAME:-localhost}}"
    if command -v hostname >/dev/null 2>&1; then
        host="$(hostname)"
    fi
    printf '\\033]7;file://%s%s\\033\\\\' "$host" "$(pwd)"
}}

# Set up PROMPT_COMMAND to report directory changes
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="__vfterm_osc7_cwd"
else
    # Preserve existing PROMPT_COMMAND
    PROMPT_COMMAND="__vfterm_osc7_cwd;$PROMPT_COMMAND"
fi

# Source user's bashrc if it exists (preserve user environment)
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Report initial directory immediately
__vfterm_osc7_cwd
"""
            try:
                bash_file.write_text(rcfile_content)
                logger.info(f"Created/updated bash integration: {bash_file}")
            except Exception as e:
                logger.error(f"Failed to write bash integration file: {e}")

        return bash_file

    def start_process(self, session: "TerminalSession") -> bool:
        """Start a terminal process using pty.fork()."""
        try:
            # Detect shell type and inject OSC 7 integration if supported
            shell_type = self._get_shell_type(session.command)
            original_args = session.args.copy() if session.args else []

            # Inject shell integration for bash
            if shell_type == "bash":
                rcfile = self._get_or_create_bash_integration()
                session.args = ["--rcfile", str(rcfile)] + original_args
                logger.info(f"Injected OSC 7 for bash: {rcfile}")
            elif shell_type == "unknown":
                logger.warning(
                    f"OSC 7 not supported for shell: {session.command}. "
                    f"CWD tracking will not work automatically."
                )

            # Fork PTY
            child_pid, fd = pty.fork()

            if child_pid == 0:
                # Child process - execute shell
                # Change to working directory if specified
                if session.cwd and os.path.exists(session.cwd):
                    os.chdir(session.cwd)

                # Set environment variables if specified
                if session.env:
                    os.environ.update(session.env)

                # Execute command
                subprocess_cmd = [session.command] + session.args
                os.execvp(subprocess_cmd[0], subprocess_cmd)
            else:
                # Parent process - store session info
                session.fd = fd
                session.child_pid = child_pid

                # Set initial window size
                self.resize(session, session.rows, session.cols)

                logger.info(
                    f"Started Unix terminal process for session {session.session_id}, "
                    f"PID: {child_pid}"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to start Unix terminal process: {e}")
            return False

    def read_output(
        self, session: "TerminalSession", max_bytes: int = 1024 * 20
    ) -> Optional[str]:
        """Read output from the terminal process."""
        if not session.fd:
            return None

        try:
            # Check if data is available using select
            timeout_sec = 0.01
            data_ready, _, _ = select.select([session.fd], [], [], timeout_sec)

            if data_ready:
                output = os.read(session.fd, max_bytes).decode(errors="ignore")
                session.last_activity = time.time()
                return output
            return None

        except OSError as e:
            # Terminal process ended or error occurred
            logger.debug(f"Read error for session {session.session_id}: {e}")
            session.active = False
            return None

    def write_input(self, session: "TerminalSession", data: str) -> bool:
        """Write input to the terminal process."""
        if not session.fd:
            return False

        try:
            os.write(session.fd, data.encode())
            session.last_activity = time.time()
            return True
        except OSError as e:
            logger.error(f"Write error for session {session.session_id}: {e}")
            return False

    def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
        """Resize the terminal window using ioctl."""
        if not session.fd:
            return False

        try:
            # Pack window size structure
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(session.fd, termios.TIOCSWINSZ, winsize)

            session.rows = rows
            session.cols = cols
            return True
        except OSError as e:
            logger.error(f"Resize error for session {session.session_id}: {e}")
            return False

    def is_process_alive(self, session: "TerminalSession") -> bool:
        """Check if the terminal process is still running."""
        if not session.child_pid:
            return False

        try:
            # Try to reap zombie process (non-blocking)
            pid, status = os.waitpid(session.child_pid, os.WNOHANG)
            if pid != 0:
                # Process has exited
                logger.debug(
                    f"Process {session.child_pid} exited with status {status} "
                    f"(session {session.session_id})"
                )
                return False

            # Process still running, verify with signal 0
            os.kill(session.child_pid, 0)
            return True
        except ProcessLookupError:
            return False
        except ChildProcessError:
            # Process already reaped or not our child
            return False
        except PermissionError:
            # Process exists but we don't have permission
            return True

    def terminate_process(self, session: "TerminalSession") -> bool:
        """Terminate the terminal process."""
        if not session.child_pid:
            return True

        try:
            # Try graceful termination first
            os.kill(session.child_pid, signal.SIGTERM)
            time.sleep(0.1)

            # Check if still alive and force kill if needed
            if self.is_process_alive(session):
                os.kill(session.child_pid, signal.SIGKILL)

            return True
        except ProcessLookupError:
            # Already dead
            return True
        except Exception as e:
            logger.error(
                f"Failed to terminate process for session {session.session_id}: {e}"
            )
            return False

    def cleanup(self, session: "TerminalSession") -> None:
        """Clean up resources for a terminal session."""
        # Terminate process if still running
        if session.child_pid:
            self.terminate_process(session)
            session.child_pid = None

        # Close file descriptor
        if session.fd:
            try:
                os.close(session.fd)
            except OSError:
                pass
            session.fd = None

        session.active = False

    def poll_process(self, session: "TerminalSession", timeout: float = 0.01) -> bool:
        """Poll the terminal process for available data."""
        if not session.fd:
            return False

        try:
            # Use select to check if data is available
            data_ready, _, _ = select.select([session.fd], [], [], timeout)
            return bool(data_ready)
        except OSError:
            return False
