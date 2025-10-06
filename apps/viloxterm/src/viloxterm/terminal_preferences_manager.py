"""Terminal Preferences Manager for ViloxTerm.

Manages storage and loading of terminal behavior preferences.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from vfwidgets_terminal import presets

logger = logging.getLogger(__name__)


class TerminalPreferencesManager:
    """Manages terminal behavior preferences storage and retrieval."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the preferences manager.

        Args:
            config_dir: Directory for storing preferences. Defaults to ~/.config/viloxterm
        """
        if config_dir is None:
            config_dir = Path.home() / ".config" / "viloxterm"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.preferences_file = self.config_dir / "terminal_preferences.json"

        logger.info(f"TerminalPreferencesManager initialized: {self.preferences_file}")

    def get_default_preferences(self) -> dict:
        """Get default terminal preferences.

        Returns:
            Dictionary with default terminal preferences
        """
        # Use the default preset from terminal widget for consistency
        return presets.DEFAULT_CONFIG.copy()

    def load_preferences(self) -> dict:
        """Load terminal preferences from disk.

        Returns:
            Dictionary with terminal preferences, or defaults if not found
        """
        if not self.preferences_file.exists():
            logger.debug("No preferences file found, using defaults")
            return self.get_default_preferences()

        try:
            with open(self.preferences_file, "r", encoding="utf-8") as f:
                preferences = json.load(f)

            # Merge with defaults to ensure all keys exist
            defaults = self.get_default_preferences()
            defaults.update(preferences)

            logger.info(f"Loaded terminal preferences from {self.preferences_file}")
            return defaults

        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
            return self.get_default_preferences()

    def save_preferences(self, preferences: dict) -> bool:
        """Save terminal preferences to disk.

        Args:
            preferences: Dictionary with terminal preferences to save

        Returns:
            True if save successful, False otherwise
        """
        try:
            with open(self.preferences_file, "w", encoding="utf-8") as f:
                json.dump(preferences, f, indent=2)

            logger.info(f"Saved terminal preferences to {self.preferences_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def reset_to_defaults(self) -> dict:
        """Reset preferences to defaults and save.

        Returns:
            Dictionary with default preferences
        """
        defaults = self.get_default_preferences()
        self.save_preferences(defaults)
        logger.info("Reset terminal preferences to defaults")
        return defaults
