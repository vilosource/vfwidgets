"""Application preferences manager for ViloxTerm.

Handles loading, saving, and validating application preferences.
Similar to TerminalPreferencesManager but for app-wide settings.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .models.preferences_model import PreferencesModel

logger = logging.getLogger(__name__)


class AppPreferencesManager:
    """Manager for ViloxTerm application preferences.

    Handles persistence of app-wide settings to ~/.config/viloxterm/app_preferences.json
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the preferences manager.

        Args:
            config_dir: Directory for storing preferences. Defaults to ~/.config/viloxterm
        """
        if config_dir is None:
            config_dir = Path.home() / ".config" / "viloxterm"

        self.config_dir = Path(config_dir)
        self.preferences_file = self.config_dir / "app_preferences.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AppPreferencesManager initialized: {self.preferences_file}")

    def load_preferences(self) -> PreferencesModel:
        """Load preferences from disk.

        Returns:
            PreferencesModel with loaded or default values
        """
        if not self.preferences_file.exists():
            logger.info("No preferences file found, using defaults")
            return PreferencesModel.get_defaults()

        try:
            with open(self.preferences_file, "r", encoding="utf-8") as f:
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

        # Validate general preferences
        if preferences.general.tabs_on_startup < 1:
            errors.append("Tabs on startup must be at least 1")

        if preferences.general.starting_directory == "custom":
            if not preferences.general.custom_directory:
                errors.append("Custom directory must be specified")
            elif not Path(preferences.general.custom_directory).exists():
                errors.append(
                    f"Custom directory does not exist: {preferences.general.custom_directory}"
                )

        if preferences.general.default_shell:
            shell_path = Path(preferences.general.default_shell)
            if not shell_path.exists():
                errors.append(f"Default shell not found: {preferences.general.default_shell}")

        # Validate appearance preferences
        if not 10 <= preferences.appearance.window_opacity <= 100:
            errors.append("Window opacity must be between 10 and 100")

        if preferences.appearance.tab_bar_position not in ["top", "bottom"]:
            errors.append("Tab bar position must be 'top' or 'bottom'")

        if not 0 <= preferences.appearance.unfocused_dim_amount <= 50:
            errors.append("Unfocused dim amount must be between 0 and 50")

        if (
            preferences.appearance.focus_border_width < 0
            or preferences.appearance.focus_border_width > 10
        ):
            errors.append("Focus border width must be between 0 and 10")

        if preferences.appearance.custom_theme_path:
            theme_path = Path(preferences.appearance.custom_theme_path)
            if not theme_path.exists():
                errors.append(
                    f"Custom theme file not found: {preferences.appearance.custom_theme_path}"
                )

        # Validate advanced preferences
        if preferences.advanced.hardware_acceleration not in ["auto", "on", "off"]:
            errors.append("Hardware acceleration must be 'auto', 'on', or 'off'")

        if preferences.advanced.webengine_cache_size < 0:
            errors.append("WebEngine cache size must be non-negative")

        if preferences.advanced.max_tabs < 1:
            errors.append("Maximum tabs must be at least 1")

        if (
            preferences.advanced.terminal_server_port < 0
            or preferences.advanced.terminal_server_port > 65535
        ):
            errors.append("Terminal server port must be between 0 and 65535")

        if preferences.advanced.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")

        return errors

    def reset_to_defaults(self) -> PreferencesModel:
        """Reset all preferences to defaults without saving.

        Returns:
            PreferencesModel with default values
        """
        logger.info("Reset preferences to defaults")
        return PreferencesModel.get_defaults()
