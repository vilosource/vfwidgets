"""Session state management for Reamde.

This module provides session persistence - saving and loading the state
of open files and active tab.
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Represents the current application session state.

    This is a pure data class with no Qt dependencies, following
    clean architecture principles.

    Attributes:
        open_files: List of file paths currently open (absolute paths)
        active_file_index: Index of the currently active file (or -1 if none)
        window_geometry: Window geometry as QByteArray base64 string (optional)
        scroll_positions: Dict mapping file paths to scroll positions

    Example:
        >>> state = SessionState(
        ...     open_files=["/home/user/README.md", "/home/user/TODO.md"],
        ...     active_file_index=1
        ... )
        >>> state.active_file_index
        1
    """

    open_files: list[str]
    active_file_index: int = -1
    window_geometry: Optional[str] = None
    scroll_positions: Optional[dict[str, int]] = None

    def __post_init__(self):
        """Validate session state after initialization."""
        if self.scroll_positions is None:
            self.scroll_positions = {}


class SessionManager:
    """Manages session persistence using QSettings.

    Saves and loads session state to platform-specific locations:
    - Linux: ~/.config/reamde/reamde.conf
    - macOS: ~/Library/Preferences/com.reamde.reamde.plist
    - Windows: Registry

    This class uses QSettings for cross-platform compatibility.

    Example:
        >>> manager = SessionManager()
        >>> state = SessionState(open_files=["/tmp/file.md"], active_file_index=0)
        >>> manager.save_session(state)
        >>> loaded = manager.load_session()
        >>> loaded.open_files
        ['/tmp/file.md']
    """

    # Version for migration handling
    SESSION_VERSION = 1

    def __init__(self):
        """Initialize session manager with QSettings."""
        self.settings = QSettings("reamde", "reamde")
        logger.info(f"Session manager initialized, settings path: {self.settings.fileName()}")

    def save_session(self, state: SessionState) -> None:
        """Save session state to QSettings.

        Args:
            state: Session state to save

        Example:
            >>> state = SessionState(open_files=["/tmp/file.md"], active_file_index=0)
            >>> manager.save_session(state)
        """
        try:
            self.settings.beginGroup("session")

            # Save version for future migration
            self.settings.setValue("version", self.SESSION_VERSION)

            # Save state as JSON for easy serialization
            state_dict = asdict(state)
            self.settings.setValue("state", json.dumps(state_dict))

            self.settings.endGroup()
            self.settings.sync()

            logger.info(
                f"Session saved: {len(state.open_files)} files, active: {state.active_file_index}"
            )

        except Exception as e:
            logger.error(f"Failed to save session: {e}", exc_info=True)
            raise

    def load_session(self) -> Optional[SessionState]:
        """Load session state from QSettings.

        Returns:
            SessionState if found, None if no session exists

        Example:
            >>> manager = SessionManager()
            >>> state = manager.load_session()
            >>> if state:
            ...     print(f"Loaded {len(state.open_files)} files")
        """
        try:
            self.settings.beginGroup("session")

            # Check if session exists
            state_json = self.settings.value("state")
            if not state_json:
                logger.info("No previous session found")
                self.settings.endGroup()
                return None

            # Load and validate version
            version = self.settings.value("version", 1, type=int)
            if version != self.SESSION_VERSION:
                logger.warning(
                    f"Session version mismatch: {version} != {self.SESSION_VERSION}, "
                    f"attempting migration"
                )
                # Future: Add migration logic here

            # Parse JSON
            state_dict = json.loads(state_json)

            # Create SessionState from dict
            state = SessionState(**state_dict)

            self.settings.endGroup()

            # Validate file paths exist
            valid_files = [f for f in state.open_files if Path(f).exists()]
            removed_count = len(state.open_files) - len(valid_files)

            if removed_count > 0:
                logger.warning(f"Removed {removed_count} non-existent files from session")
                state.open_files = valid_files

                # Adjust active index if needed
                if state.active_file_index >= len(valid_files):
                    state.active_file_index = max(0, len(valid_files) - 1)

            logger.info(
                f"Session loaded: {len(state.open_files)} files, active: {state.active_file_index}"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to load session: {e}", exc_info=True)
            return None

    def clear_session(self) -> None:
        """Clear the saved session.

        Example:
            >>> manager = SessionManager()
            >>> manager.clear_session()
        """
        try:
            self.settings.beginGroup("session")
            self.settings.remove("")  # Remove all keys in group
            self.settings.endGroup()
            self.settings.sync()
            logger.info("Session cleared")

        except Exception as e:
            logger.error(f"Failed to clear session: {e}", exc_info=True)
            raise
