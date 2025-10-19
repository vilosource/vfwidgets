"""Application preferences manager for ViloxWeb.

Handles loading, saving, and validating application preferences.
"""

import json
import logging
from pathlib import Path

from .models.preferences_model import PreferencesModel

logger = logging.getLogger(__name__)


class PreferencesManager:
    """Manager for ViloxWeb application preferences.

    Handles persistence of app-wide settings to ~/.config/viloweb/preferences.json
    """

    def __init__(self, config_dir: Path | None = None):
        """Initialize the preferences manager.

        Args:
            config_dir: Directory for storing preferences. Defaults to ~/.config/viloweb
        """
        if config_dir is None:
            config_dir = Path.home() / ".config" / "viloweb"

        self.config_dir = Path(config_dir)
        self.preferences_file = self.config_dir / "preferences.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PreferencesManager initialized: {self.preferences_file}")

    def load_preferences(self) -> PreferencesModel:
        """Load preferences from disk.

        Returns:
            PreferencesModel with loaded or default values
        """
        if not self.preferences_file.exists():
            logger.info("No preferences file found, using defaults")
            return PreferencesModel.get_defaults()

        try:
            with open(self.preferences_file, encoding="utf-8") as f:
                data = json.load(f)

            preferences = PreferencesModel.from_dict(data)
            logger.info("Loaded preferences from disk")
            return preferences

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse preferences file: {e}, using defaults")
            return PreferencesModel.get_defaults()
        except Exception as e:
            logger.error(f"Error loading preferences: {e}, using defaults")
            return PreferencesModel.get_defaults()

    def save_preferences(self, preferences: PreferencesModel) -> bool:
        """Save preferences to disk.

        Args:
            preferences: PreferencesModel to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Convert to dict and save with pretty formatting
            data = preferences.to_dict()

            with open(self.preferences_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved preferences to {self.preferences_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def validate_preferences(self, preferences: PreferencesModel) -> list[str]:
        """Validate preferences and return list of errors.

        Args:
            preferences: PreferencesModel to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate opacity
        if not (10 <= preferences.appearance.window_opacity <= 100):
            errors.append("Window opacity must be between 10 and 100")

        # Validate color formats (if specified)
        if preferences.appearance.top_bar_background_color:
            color = preferences.appearance.top_bar_background_color
            if not (color.startswith("#") and len(color) in [7, 9]):
                errors.append("Top bar background color must be in #RRGGBB or #RRGGBBAA format")

        if preferences.appearance.accent_line_color:
            color = preferences.appearance.accent_line_color
            if not (color.startswith("#") and len(color) in [7, 9]):
                errors.append("Accent line color must be in #RRGGBB or #RRGGBBAA format")

        return errors
