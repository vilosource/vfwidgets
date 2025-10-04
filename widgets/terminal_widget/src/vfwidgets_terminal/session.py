"""Terminal session data model."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TerminalSession:
    """
    Represents a single terminal session.

    Tracks session state, process information, and lifecycle metadata.
    """

    # Session identification
    session_id: str

    # Process configuration
    command: str = "bash"
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)

    # Terminal dimensions
    rows: int = 24
    cols: int = 80

    # Process information (set by backend)
    fd: Optional[int] = None  # PTY file descriptor (Unix)
    child_pid: Optional[int] = None  # Process ID

    # Lifecycle tracking
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    active: bool = True

    # Platform-specific data and extensibility
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()

    def inactive_duration(self) -> float:
        """
        Get duration in seconds since last activity.

        Returns:
            Seconds since last activity
        """
        return time.time() - self.last_activity

    def age(self) -> float:
        """
        Get session age in seconds.

        Returns:
            Seconds since session creation
        """
        return time.time() - self.created_at

    def is_inactive(self, timeout_seconds: float) -> bool:
        """
        Check if session has been inactive for longer than timeout.

        Args:
            timeout_seconds: Inactivity timeout threshold

        Returns:
            True if session is inactive for > timeout, False otherwise
        """
        return self.inactive_duration() > timeout_seconds
