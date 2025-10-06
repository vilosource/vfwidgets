"""Persistent storage for keyboard shortcuts.

Provides JSON-based storage for saving and loading user-customized
keyboard shortcuts. Supports default keybindings, user overrides,
and validation.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class KeybindingStorage:
    """Manages persistent storage of keyboard shortcuts.

    Stores keybindings in JSON format with support for:
    - Default keybindings (application-defined)
    - User overrides (user-customized)
    - Validation on load
    - Atomic writes (prevents corruption)

    File Format:
        {
            "file.save": "Ctrl+S",
            "edit.copy": "Ctrl+C",
            "custom.action": null  // Unbound action
        }

    Example:
        >>> storage = KeybindingStorage("~/.config/myapp/keybindings.json")
        >>> storage.save({"file.save": "Ctrl+S"})
        >>> bindings = storage.load()
        >>> print(bindings.get("file.save"))
        Ctrl+S
    """

    def __init__(self, file_path: Optional[str] = None):
        """Initialize keybinding storage.

        Args:
            file_path: Path to JSON file for storage. If None, uses in-memory only.

        Example:
            >>> storage = KeybindingStorage("~/.config/myapp/keybindings.json")
        """
        self._file_path = Path(file_path).expanduser() if file_path else None
        self._in_memory_bindings: dict[str, Optional[str]] = {}
        logger.info(f"KeybindingStorage initialized: {self._file_path or 'in-memory'}")

    def load(self) -> dict[str, Optional[str]]:
        """Load keybindings from file.

        Returns:
            Dictionary mapping action IDs to shortcuts.
            Returns empty dict if file doesn't exist or is invalid.

        Example:
            >>> bindings = storage.load()
            >>> if "file.save" in bindings:
            ...     print(f"Save is bound to: {bindings['file.save']}")
        """
        # If no file path, return in-memory bindings
        if not self._file_path:
            logger.debug("No file path - returning in-memory bindings")
            return self._in_memory_bindings.copy()

        # If file doesn't exist, return empty dict
        if not self._file_path.exists():
            logger.debug(f"Keybinding file not found: {self._file_path}")
            return {}

        try:
            with open(self._file_path, encoding="utf-8") as f:
                bindings = json.load(f)

            # Validate format
            if not isinstance(bindings, dict):
                logger.error(f"Invalid keybinding file format: expected dict, got {type(bindings)}")
                return {}

            # Validate keys and values
            validated_bindings = {}
            for action_id, shortcut in bindings.items():
                if not isinstance(action_id, str):
                    logger.warning(f"Skipping non-string action ID: {action_id}")
                    continue

                if shortcut is not None and not isinstance(shortcut, str):
                    logger.warning(f"Skipping invalid shortcut for '{action_id}': {shortcut}")
                    continue

                validated_bindings[action_id] = shortcut

            logger.info(f"Loaded {len(validated_bindings)} keybindings from {self._file_path}")
            return validated_bindings

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse keybinding file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load keybindings: {e}")
            return {}

    def save(self, bindings: dict[str, Optional[str]]) -> bool:
        """Save keybindings to file.

        Uses atomic write (write to temp file, then rename) to prevent corruption.

        Args:
            bindings: Dictionary mapping action IDs to shortcuts

        Returns:
            True if save succeeded, False otherwise

        Example:
            >>> success = storage.save({
            ...     "file.save": "Ctrl+S",
            ...     "edit.copy": "Ctrl+C"
            ... })
            >>> if success:
            ...     print("Keybindings saved!")
        """
        # If no file path, store in memory
        if not self._file_path:
            self._in_memory_bindings = bindings.copy()
            logger.debug("Saved bindings to in-memory storage")
            return True

        try:
            # Ensure parent directory exists
            self._file_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write: write to temp file, then rename
            temp_file = self._file_path.with_suffix(".tmp")

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(bindings, f, indent=2, sort_keys=True)

            # Atomic rename (overwrites existing file)
            temp_file.replace(self._file_path)

            logger.info(f"Saved {len(bindings)} keybindings to {self._file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save keybindings: {e}")
            return False

    def merge(
        self,
        defaults: dict[str, Optional[str]],
        overrides: Optional[dict[str, Optional[str]]] = None,
    ) -> dict[str, Optional[str]]:
        """Merge default keybindings with user overrides.

        User overrides take precedence. Use None value to unbind an action.

        Args:
            defaults: Default keybindings (from ActionRegistry)
            overrides: User-customized keybindings (from file)

        Returns:
            Merged keybindings

        Example:
            >>> defaults = {"file.save": "Ctrl+S", "edit.copy": "Ctrl+C"}
            >>> overrides = {"file.save": "Ctrl+Alt+S"}  # User changed this
            >>> merged = storage.merge(defaults, overrides)
            >>> print(merged["file.save"])
            Ctrl+Alt+S
        """
        merged = defaults.copy()

        if overrides:
            merged.update(overrides)

        logger.debug(f"Merged {len(defaults)} defaults with {len(overrides or {})} overrides")
        return merged

    def reset(self) -> bool:
        """Delete stored keybindings file.

        This will reset to application defaults on next load.

        Returns:
            True if file was deleted or doesn't exist, False on error

        Example:
            >>> storage.reset()  # Delete custom keybindings
            >>> bindings = storage.load()  # Will be empty
        """
        if not self._file_path:
            self._in_memory_bindings.clear()
            logger.info("Cleared in-memory bindings")
            return True

        try:
            if self._file_path.exists():
                self._file_path.unlink()
                logger.info(f"Deleted keybinding file: {self._file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete keybinding file: {e}")
            return False
