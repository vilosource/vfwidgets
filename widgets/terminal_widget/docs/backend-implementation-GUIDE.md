# Terminal Backend Implementation Guide

## Overview

This guide shows you how to implement custom terminal backends for the vfwidgets-terminal package. A backend handles platform-specific PTY (pseudoterminal) operations, abstracting away the differences between Unix/Linux and Windows.

**Audience:** Developers who need to:
- Add support for new platforms
- Customize PTY behavior
- Integrate with existing process management systems
- Create specialized terminal backends (e.g., Docker containers, SSH)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [The TerminalBackend Interface](#the-terminalbackend-interface)
3. [Implementing a Unix Backend](#implementing-a-unix-backend)
4. [Implementing a Windows Backend](#implementing-a-windows-backend)
5. [Testing Your Backend](#testing-your-backend)
6. [Common Pitfalls](#common-pitfalls)
7. [Advanced Topics](#advanced-topics)

---

## Architecture Overview

### Component Relationship

```
MultiSessionTerminalServer
    ↓ uses
TerminalBackend (abstract interface) ← You implement this
    ↓ implements
UnixTerminalBackend / WindowsTerminalBackend / YourCustomBackend
    ↓ manages
PTY processes (bash, zsh, etc.)
```

### Why Backend Abstraction?

**Benefits:**
- **Cross-platform:** Single server code works on all platforms
- **Testability:** Easy to mock backends for unit tests
- **Extensibility:** Add new platforms without changing server logic
- **Separation of concerns:** Server handles networking, backend handles processes

---

## The TerminalBackend Interface

### Core Abstract Class

Located in `src/vfwidgets_terminal/backends/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Optional

class TerminalBackend(ABC):
    """Abstract base class for terminal backend implementations."""

    @abstractmethod
    def start_process(self, session: "TerminalSession") -> bool:
        """Start a terminal process for the given session.

        Args:
            session: TerminalSession object containing:
                - command: Shell command to execute (e.g., "bash")
                - args: List of command arguments
                - cwd: Working directory (optional)
                - env: Environment variables dict (optional)
                - rows, cols: Terminal dimensions

        Returns:
            True if process started successfully, False otherwise

        Side Effects:
            Must set session.fd and session.child_pid on success
        """
        pass

    @abstractmethod
    def read_output(self, session: "TerminalSession",
                    max_bytes: int = 1024 * 20) -> Optional[str]:
        """Read output from the terminal process.

        Args:
            session: The session to read from
            max_bytes: Maximum bytes to read in one call

        Returns:
            Output string (UTF-8 decoded) if available, None otherwise
        """
        pass

    @abstractmethod
    def write_input(self, session: "TerminalSession", data: str) -> bool:
        """Write input to the terminal process.

        Args:
            session: The session to write to
            data: Input string (will be UTF-8 encoded)

        Returns:
            True if write successful, False otherwise
        """
        pass

    @abstractmethod
    def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
        """Resize the terminal window.

        Args:
            session: The session to resize
            rows: Number of rows
            cols: Number of columns

        Returns:
            True if resize successful, False otherwise
        """
        pass

    @abstractmethod
    def is_process_alive(self, session: "TerminalSession") -> bool:
        """Check if the terminal process is still running.

        Args:
            session: The session to check

        Returns:
            True if process is alive, False if exited/killed
        """
        pass

    @abstractmethod
    def poll_process(self, session: "TerminalSession", timeout: float = 0.0) -> bool:
        """Check if data is available to read.

        Args:
            session: The session to poll
            timeout: Timeout in seconds (0.0 = non-blocking)

        Returns:
            True if data is available to read, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self, session: "TerminalSession") -> None:
        """Clean up resources for a session.

        Args:
            session: The session to clean up

        Side Effects:
            Should close file descriptors, kill process if needed
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform name for this backend.

        Returns:
            Platform name string (e.g., "Unix", "Windows")
        """
        pass
```

---

## Implementing a Unix Backend

### Step 1: Import Required Modules

```python
import errno
import fcntl
import logging
import os
import pty
import select
import signal
import struct
import subprocess
import termios
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import TerminalSession

from .base import TerminalBackend

logger = logging.getLogger(__name__)
```

### Step 2: Create Backend Class

```python
class UnixTerminalBackend(TerminalBackend):
    """Unix/Linux PTY backend using pty.fork()."""

    def get_platform_name(self) -> str:
        return "Unix"
```

### Step 3: Implement start_process()

This is the most critical method. It uses `pty.fork()` to create a pseudoterminal.

```python
def start_process(self, session: "TerminalSession") -> bool:
    """Start a PTY process using pty.fork()."""
    try:
        # Fork a new process with a PTY
        child_pid, fd = pty.fork()

        if child_pid == 0:
            # ===== CHILD PROCESS =====
            # This code runs in the child process

            # Change working directory if specified
            if session.cwd and os.path.exists(session.cwd):
                os.chdir(session.cwd)

            # Update environment variables
            if session.env:
                os.environ.update(session.env)

            # Construct command
            subprocess_cmd = [session.command] + session.args

            # Replace this process with the shell
            os.execvp(subprocess_cmd[0], subprocess_cmd)

        else:
            # ===== PARENT PROCESS =====
            # Store PTY file descriptor and child PID
            session.fd = fd
            session.child_pid = child_pid

            # Make file descriptor non-blocking
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Set initial terminal size
            self.resize(session, session.rows, session.cols)

            logger.info(f"Started Unix PTY process: PID {child_pid}")
            return True

    except Exception as e:
        logger.error(f"Failed to start Unix PTY process: {e}", exc_info=True)
        return False
```

**Key Concepts:**
- `pty.fork()` creates both a child process and a PTY in one call
- Child process (PID 0) execs the shell
- Parent process stores FD and PID in session
- Non-blocking I/O prevents read/write operations from hanging

### Step 4: Implement read_output()

```python
def read_output(self, session: "TerminalSession",
                max_bytes: int = 1024 * 20) -> Optional[str]:
    """Read output from PTY using non-blocking I/O."""
    if not session.fd:
        return None

    try:
        # Non-blocking read
        output = os.read(session.fd, max_bytes)
        return output.decode("utf-8", errors="replace")

    except OSError as e:
        if e.errno == errno.EAGAIN:
            # No data available (non-blocking FD)
            return None
        else:
            logger.error(f"Error reading from PTY: {e}")
            return None

    except Exception as e:
        logger.error(f"Unexpected error reading PTY: {e}")
        return None
```

**Key Concepts:**
- Non-blocking read returns immediately if no data
- `EAGAIN` error means "try again" (no data available)
- UTF-8 decoding with error replacement for invalid sequences

### Step 5: Implement write_input()

```python
def write_input(self, session: "TerminalSession", data: str) -> bool:
    """Write input to PTY."""
    if not session.fd:
        return False

    try:
        # Encode and write
        os.write(session.fd, data.encode("utf-8"))
        return True

    except OSError as e:
        logger.error(f"Error writing to PTY: {e}")
        return False
```

### Step 6: Implement resize()

```python
def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
    """Resize the PTY using TIOCSWINSZ ioctl."""
    if not session.fd:
        return False

    try:
        # Pack window size into struct
        winsize = struct.pack("HHHH", rows, cols, 0, 0)

        # Send TIOCSWINSZ ioctl to PTY
        fcntl.ioctl(session.fd, termios.TIOCSWINSZ, winsize)

        logger.debug(f"Resized PTY to {rows}x{cols}")
        return True

    except Exception as e:
        logger.error(f"Error resizing PTY: {e}")
        return False
```

**Key Concepts:**
- `TIOCSWINSZ` is the terminal ioctl for setting window size
- Struct format: `HHHH` = rows, cols, xpixel, ypixel
- Most terminals ignore xpixel/ypixel (set to 0)

### Step 7: Implement is_process_alive()

```python
def is_process_alive(self, session: "TerminalSession") -> bool:
    """Check if process is alive using waitpid()."""
    if not session.child_pid:
        return False

    try:
        # Non-blocking wait (WNOHANG)
        pid, status = os.waitpid(session.child_pid, os.WNOHANG)

        if pid == 0:
            # Process still running
            return True
        else:
            # Process exited
            logger.info(f"Process {session.child_pid} exited with status {status}")
            return False

    except ChildProcessError:
        # Process doesn't exist
        return False
```

**Key Concepts:**
- `os.WNOHANG` makes waitpid() non-blocking
- Return value 0 means process is still running
- Non-zero return means process exited

### Step 8: Implement poll_process()

```python
def poll_process(self, session: "TerminalSession", timeout: float = 0.0) -> bool:
    """Poll if data is available using select()."""
    if not session.fd:
        return False

    try:
        # Use select to check for readable data
        readable, _, _ = select.select([session.fd], [], [], timeout)
        return len(readable) > 0

    except Exception as e:
        logger.error(f"Error polling PTY: {e}")
        return False
```

**Key Concepts:**
- `select()` checks if FD is readable without blocking
- Timeout 0.0 = immediate return (non-blocking poll)
- Returns True if data is available to read

### Step 9: Implement cleanup()

```python
def cleanup(self, session: "TerminalSession") -> None:
    """Clean up PTY resources."""
    # Close file descriptor
    if session.fd:
        try:
            os.close(session.fd)
            logger.debug(f"Closed PTY FD {session.fd}")
        except OSError:
            pass
        session.fd = None

    # Kill process if still running
    if session.child_pid:
        try:
            # Send SIGTERM
            os.kill(session.child_pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to process {session.child_pid}")

            # Wait briefly for graceful exit
            os.waitpid(session.child_pid, 0)

        except ProcessLookupError:
            # Process already exited
            pass
        except Exception as e:
            logger.error(f"Error cleaning up process: {e}")

        session.child_pid = None
```

**Key Concepts:**
- Always close FD to prevent resource leaks
- Send SIGTERM before SIGKILL (graceful shutdown)
- Handle exceptions (process may already be dead)

---

## Implementing a Windows Backend

Windows doesn't have PTYs in the traditional sense. We use `winpty` or `conpty`.

### Option 1: Using pywinpty

```python
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import TerminalSession

from .base import TerminalBackend

logger = logging.getLogger(__name__)

# Conditional import - pywinpty is optional
try:
    import winpty
    WINPTY_AVAILABLE = True
except ImportError:
    WINPTY_AVAILABLE = False
    logger.warning("pywinpty not available - Windows backend disabled")


class WindowsTerminalBackend(TerminalBackend):
    """Windows ConPTY backend using pywinpty."""

    def __init__(self):
        if not WINPTY_AVAILABLE:
            raise RuntimeError("pywinpty is required for Windows backend")

    def get_platform_name(self) -> str:
        return "Windows"

    def start_process(self, session: "TerminalSession") -> bool:
        """Start ConPTY process."""
        try:
            # Build command
            command = session.command
            if session.args:
                command += " " + " ".join(session.args)

            # Start PTY process
            pty_process = winpty.PtyProcess.spawn(
                command,
                dimensions=(session.rows, session.cols),
                cwd=session.cwd,
                env=session.env
            )

            # Store process reference in session metadata
            session.metadata["pty_process"] = pty_process
            session.child_pid = pty_process.pid

            logger.info(f"Started Windows ConPTY process: PID {pty_process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start Windows ConPTY: {e}", exc_info=True)
            return False

    def read_output(self, session: "TerminalSession",
                    max_bytes: int = 1024 * 20) -> Optional[str]:
        """Read from ConPTY."""
        pty_process = session.metadata.get("pty_process")
        if not pty_process:
            return None

        try:
            # Read with timeout
            output = pty_process.read(max_bytes, blocking=False)
            return output if output else None
        except Exception:
            return None

    def write_input(self, session: "TerminalSession", data: str) -> bool:
        """Write to ConPTY."""
        pty_process = session.metadata.get("pty_process")
        if not pty_process:
            return False

        try:
            pty_process.write(data)
            return True
        except Exception as e:
            logger.error(f"Error writing to ConPTY: {e}")
            return False

    def resize(self, session: "TerminalSession", rows: int, cols: int) -> bool:
        """Resize ConPTY."""
        pty_process = session.metadata.get("pty_process")
        if not pty_process:
            return False

        try:
            pty_process.setwinsize(rows, cols)
            return True
        except Exception as e:
            logger.error(f"Error resizing ConPTY: {e}")
            return False

    def is_process_alive(self, session: "TerminalSession") -> bool:
        """Check if ConPTY process is alive."""
        pty_process = session.metadata.get("pty_process")
        if not pty_process:
            return False

        return pty_process.isalive()

    def poll_process(self, session: "TerminalSession", timeout: float = 0.0) -> bool:
        """Windows doesn't need polling - always return True."""
        return True

    def cleanup(self, session: "TerminalSession") -> None:
        """Clean up ConPTY."""
        pty_process = session.metadata.get("pty_process")
        if pty_process:
            try:
                if pty_process.isalive():
                    pty_process.terminate()
                logger.info(f"Terminated ConPTY process {session.child_pid}")
            except Exception as e:
                logger.error(f"Error terminating ConPTY: {e}")

            session.metadata.pop("pty_process", None)
```

---

## Testing Your Backend

### Unit Tests

```python
import pytest
from vfwidgets_terminal.session import TerminalSession
from your_backend import YourBackend


def test_backend_start_process():
    """Test starting a process."""
    backend = YourBackend()
    session = TerminalSession(
        session_id="test-001",
        command="bash",
        args=["-c", "echo 'Hello World'"],
        rows=24,
        cols=80
    )

    # Start process
    assert backend.start_process(session) is True
    assert session.child_pid is not None

    # Cleanup
    backend.cleanup(session)


def test_backend_read_write():
    """Test reading and writing."""
    backend = YourBackend()
    session = TerminalSession(
        session_id="test-002",
        command="bash",
        rows=24,
        cols=80
    )

    backend.start_process(session)

    # Write command
    assert backend.write_input(session, "echo 'test'\n") is True

    # Wait for output
    import time
    time.sleep(0.5)

    # Read output
    output = backend.read_output(session)
    assert output is not None
    assert "test" in output

    backend.cleanup(session)


def test_backend_resize():
    """Test terminal resize."""
    backend = YourBackend()
    session = TerminalSession(session_id="test-003", command="bash")

    backend.start_process(session)

    # Resize
    assert backend.resize(session, 30, 100) is True

    backend.cleanup(session)


def test_backend_process_lifecycle():
    """Test process lifecycle."""
    backend = YourBackend()
    session = TerminalSession(session_id="test-004", command="bash")

    # Process not started
    assert backend.is_process_alive(session) is False

    # Start process
    backend.start_process(session)
    assert backend.is_process_alive(session) is True

    # Cleanup
    backend.cleanup(session)
    assert backend.is_process_alive(session) is False
```

---

## Common Pitfalls

### 1. Forgetting Non-Blocking I/O

**Problem:** Blocking reads hang the server thread.

**Solution:** Always set FDs to non-blocking mode.

```python
# ❌ WRONG - blocking
output = os.read(fd, 1024)

# ✅ CORRECT - non-blocking
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
output = os.read(fd, 1024)  # Returns immediately if no data
```

### 2. Not Handling EAGAIN

**Problem:** Code treats EAGAIN as fatal error.

**Solution:** EAGAIN means "no data available" (normal for non-blocking I/O).

```python
try:
    output = os.read(fd, 1024)
except OSError as e:
    if e.errno == errno.EAGAIN:
        return None  # Normal - no data available
    else:
        raise  # Actual error
```

### 3. Resource Leaks

**Problem:** Not closing FDs or killing processes.

**Solution:** Always implement cleanup() properly.

```python
def cleanup(self, session):
    # Close ALL resources
    if session.fd:
        os.close(session.fd)
        session.fd = None

    if session.child_pid:
        os.kill(session.child_pid, signal.SIGTERM)
        session.child_pid = None
```

---

## Advanced Topics

### Custom Backends for Special Cases

#### SSH Backend

```python
class SSHTerminalBackend(TerminalBackend):
    """Backend that connects to remote host via SSH."""

    def start_process(self, session):
        # Use paramiko or similar to establish SSH connection
        # Store SSH channel in session.metadata
        pass
```

#### Docker Backend

```python
class DockerTerminalBackend(TerminalBackend):
    """Backend that runs shell in Docker container."""

    def start_process(self, session):
        # Use docker-py to exec into container
        # Store container exec instance in session.metadata
        pass
```

---

## Conclusion

Implementing a custom backend involves:

1. Subclass `TerminalBackend`
2. Implement all abstract methods
3. Handle platform-specific PTY APIs
4. Use non-blocking I/O
5. Properly clean up resources
6. Test thoroughly

The backend abstraction allows the terminal widget to work on any platform or process management system.

**Next Steps:**
- Read [Server Implementation Guide](./server-implementation-GUIDE.md) to integrate your backend
- Review [Lessons Learned](./lessons-learned-GUIDE.md) for common issues
- Check existing backends in `src/vfwidgets_terminal/backends/` for reference

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-02
