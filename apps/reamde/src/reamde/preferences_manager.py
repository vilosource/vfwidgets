"""Preferences manager for Reamde.

Handles loading, saving, and validation of application preferences.
"""

import json
import logging
from pathlib import Path

from .models.preferences_model import PreferencesModel

logger = logging.getLogger(__name__)


class PreferencesManager:
    """Manages application preferences persistence.

    Saves preferences to: ~/.config/reamde/preferences.json

    Example:
        >>> manager = PreferencesManager()
        >>> prefs = manager.load_preferences()
        >>> prefs.appearance.window_opacity = 90
        >>> manager.save_preferences(prefs)
        True
    """

    def __init__(self):
        """Initialize preferences manager."""
        self.config_dir = Path.home() / ".config" / "reamde"
        self.config_file = self.config_dir / "preferences.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Preferences file: {self.config_file}")

    def load_preferences(self) -> PreferencesModel:
        """Load preferences from disk.

        Returns:
            PreferencesModel with loaded or default values

        Example:
            >>> manager = PreferencesManager()
            >>> prefs = manager.load_preferences()
            >>> prefs.general.restore_previous_session
            True
        """
        if not self.config_file.exists():
            logger.info("No preferences file found, using defaults")
            return PreferencesModel()

        try:
            with open(self.config_file, encoding="utf-8") as f:
                data = json.load(f)

            prefs = PreferencesModel.from_dict(data)
            logger.info("Preferences loaded successfully")
            return prefs

        except Exception as e:
            logger.error(f"Failed to load preferences: {e}", exc_info=True)
            logger.info("Using default preferences")
            return PreferencesModel()

    def save_preferences(self, preferences: PreferencesModel) -> bool:
        """Save preferences to disk.

        Args:
            preferences: PreferencesModel to save

        Returns:
            True if saved successfully, False otherwise

        Example:
            >>> manager = PreferencesManager()
            >>> prefs = PreferencesModel()
            >>> manager.save_preferences(prefs)
            True
        """
        try:
            # Validate first
            if not self.validate_preferences(preferences):
                logger.error("Preferences validation failed, not saving")
                return False

            # Save to file with pretty formatting
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(preferences.to_dict(), f, indent=2)

            logger.info("Preferences saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}", exc_info=True)
            return False

    def validate_preferences(self, preferences: PreferencesModel) -> bool:
        """Validate preference values.

        Args:
            preferences: PreferencesModel to validate

        Returns:
            True if all values are valid

        Example:
            >>> manager = PreferencesManager()
            >>> prefs = PreferencesModel()
            >>> manager.validate_preferences(prefs)
            True
        """
        # Window opacity
        if not (10 <= preferences.appearance.window_opacity <= 100):
            logger.error("Invalid window opacity (must be 10-100)")
            return False

        # Font size
        if not (8 <= preferences.appearance.font_size <= 72):
            logger.error("Invalid font size (must be 8-72)")
            return False

        # Line height
        if not (1.0 <= preferences.appearance.line_height <= 3.0):
            logger.error("Invalid line height (must be 1.0-3.0)")
            return False

        # Max content width
        if preferences.appearance.max_content_width < 0:
            logger.error("Invalid max content width (must be >= 0)")
            return False

        # Recent files count
        if not (1 <= preferences.general.max_recent_files <= 100):
            logger.error("Invalid max recent files (must be 1-100)")
            return False

        return True

    def reset_to_defaults(self) -> PreferencesModel:
        """Reset preferences to defaults (in memory only).

        Returns:
            New PreferencesModel with default values

        Example:
            >>> manager = PreferencesManager()
            >>> prefs = manager.reset_to_defaults()
            >>> prefs.appearance.window_opacity
            100
        """
        logger.info("Resetting preferences to defaults (in memory)")
        return PreferencesModel()
