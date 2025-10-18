"""VFThemedApplication - Base application class with declarative theme configuration.

This module provides VFThemedApplication, which extends ThemedApplication with:
- Declarative theme_config for common use cases
- Automatic app override application
- User override loading/saving
- Convenience methods for customization

VFThemedApplication adds overlay system support on top of ThemedApplication,
providing a declarative, class-based configuration pattern.

Example:
    >>> class MyApp(VFThemedApplication):
    ...     theme_config = {
    ...         "base_theme": "dark",
    ...         "app_overrides": {
    ...             "editor.background": "#1e1e2e",
    ...             "tab.activeBackground": "#89b4fa",
    ...         },
    ...         "allow_user_customization": True,
    ...         "customizable_tokens": [
    ...             "editor.background",
    ...             "editor.foreground",
    ...         ],
    ...     }
    ...
    >>> app = MyApp(sys.argv)
    >>> app.run()
"""

from typing import Dict, List, Optional
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from .application import ThemedApplication
from ..core.manager import ThemeManager
from ..logging import get_debug_logger

logger = get_debug_logger(__name__)


class VFThemedApplication(ThemedApplication):
    """Base application class with declarative theme configuration.

    VFThemedApplication extends ThemedApplication with overlay system support:
    - Declarative theme_config class attribute
    - Automatic app-level override application
    - User preference persistence via QSettings
    - Customization restrictions via customizable_tokens

    Attributes:
        theme_config: Declarative configuration dictionary with keys:
            - base_theme: Theme name to load (default: "dark")
            - app_overrides: App-level color overrides (default: {})
            - allow_user_customization: Allow user customization (default: True)
            - customizable_tokens: List of tokens users can customize (default: [])
            - persist_base_theme: Save base theme selection (default: True)
            - persist_user_overrides: Save user overrides (default: True)
            - settings_key_prefix: QSettings key prefix (default: "theme/")

    Example:
        >>> class BrandedApp(VFThemedApplication):
        ...     theme_config = {
        ...         "base_theme": "dark",
        ...         "app_overrides": {
        ...             "editor.background": "#1e1e2e",
        ...             "button.background": "#313244",
        ...         },
        ...     }
        ...
        >>> app = BrandedApp(sys.argv)
    """

    # Default theme configuration (can be overridden in subclasses)
    theme_config: Dict = {
        "base_theme": "dark",
        "app_overrides": {},
        "allow_user_customization": True,
        "customizable_tokens": [],
        "persist_base_theme": True,
        "persist_user_overrides": True,
        "settings_key_prefix": "theme/",
    }

    def __init__(
        self,
        argv: Optional[List[str]] = None,
        app_id: Optional[str] = None
    ):
        """Initialize application with theme configuration.

        Args:
            argv: Command line arguments (default: None)
            app_id: Application ID for QSettings (default: None)
        """
        # Initialize ThemedApplication (parent class)
        super().__init__(argv)

        # Store app ID for QSettings
        self._app_id = app_id

        # Set application metadata if app_id provided
        if app_id:
            self.setApplicationName(app_id)

        # Apply theme configuration
        self._apply_theme_config()

        logger.debug(
            f"VFThemedApplication initialized with base_theme='{self.theme_config.get('base_theme')}', "
            f"app_overrides={len(self.theme_config.get('app_overrides', {}))}, "
            f"allow_user_customization={self.theme_config.get('allow_user_customization')}"
        )

    def _apply_theme_config(self) -> None:
        """Apply theme configuration from theme_config.

        This method is called during initialization to:
        1. Load base theme
        2. Apply app-level overrides
        3. Load user preferences (if persistence enabled)
        """
        try:
            # Get ThemeManager instance
            theme_manager = ThemeManager.get_instance()

            # 1. Load base theme
            base_theme = self.theme_config.get("base_theme", "dark")

            # Load from QSettings if persistence enabled
            if self.theme_config.get("persist_base_theme", True):
                settings = self._get_settings()
                prefix = self.theme_config.get("settings_key_prefix", "theme/")
                saved_theme = settings.value(f"{prefix}base_theme", None)
                if saved_theme:
                    base_theme = saved_theme
                    logger.debug(f"Loaded base_theme from QSettings: {base_theme}")

            # Set the base theme
            self.set_theme(base_theme)
            logger.debug(f"Applied base theme: {base_theme}")

            # 2. Apply app-level overrides
            app_overrides = self.theme_config.get("app_overrides", {})
            if app_overrides:
                theme_manager.set_app_overrides_bulk(app_overrides)
                logger.debug(f"Applied {len(app_overrides)} app-level overrides")

            # 3. Load user preferences (if enabled)
            if self.theme_config.get("persist_user_overrides", True):
                user_overrides = self.load_user_preferences()
                if user_overrides:
                    theme_manager.set_user_overrides_bulk(user_overrides)
                    logger.debug(f"Loaded {len(user_overrides)} user overrides from QSettings")

        except Exception as e:
            logger.error(f"Error applying theme config: {e}")
            # Non-fatal - application can continue with defaults

    # ========================================================================
    # Persistence Methods
    # ========================================================================

    def load_user_preferences(self) -> Dict[str, str]:
        """Load user override preferences from QSettings.

        Returns:
            Dictionary of user overrides (token -> color)
        """
        try:
            settings = self._get_settings()
            prefix = self.theme_config.get("settings_key_prefix", "theme/")
            overrides = settings.value(f"{prefix}user_overrides", {})

            # QSettings may return None or wrong type
            if not isinstance(overrides, dict):
                logger.debug("No user overrides found in QSettings")
                return {}

            logger.debug(f"Loaded {len(overrides)} user overrides from QSettings")
            return overrides

        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            return {}

    def save_user_preferences(self, overrides: Optional[Dict[str, str]] = None) -> None:
        """Save user override preferences to QSettings.

        Args:
            overrides: Overrides to save (default: current user overrides)
        """
        try:
            # Get current user overrides if not provided
            if overrides is None:
                theme_manager = ThemeManager.get_instance()
                overrides = theme_manager.get_user_overrides()

            settings = self._get_settings()
            prefix = self.theme_config.get("settings_key_prefix", "theme/")
            settings.setValue(f"{prefix}user_overrides", overrides)
            settings.sync()

            logger.debug(f"Saved {len(overrides)} user overrides to QSettings")

        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")

    def save_base_theme(self, theme_name: str) -> None:
        """Save base theme selection to QSettings.

        Args:
            theme_name: Name of theme to save
        """
        try:
            if not self.theme_config.get("persist_base_theme", True):
                logger.debug("Base theme persistence is disabled")
                return

            settings = self._get_settings()
            prefix = self.theme_config.get("settings_key_prefix", "theme/")
            settings.setValue(f"{prefix}base_theme", theme_name)
            settings.sync()

            logger.debug(f"Saved base theme to QSettings: {theme_name}")

        except Exception as e:
            logger.error(f"Error saving base theme: {e}")

    def clear_user_preferences(self) -> None:
        """Clear all saved user preferences."""
        try:
            settings = self._get_settings()
            prefix = self.theme_config.get("settings_key_prefix", "theme/")
            settings.remove(f"{prefix}user_overrides")
            settings.sync()

            # Also clear from ThemeManager
            theme_manager = ThemeManager.get_instance()
            theme_manager.clear_user_overrides()

            logger.debug("Cleared all user preferences")

        except Exception as e:
            logger.error(f"Error clearing user preferences: {e}")

    # ========================================================================
    # Customization Methods
    # ========================================================================

    def customize_color(
        self,
        token: str,
        color: str,
        persist: bool = True
    ) -> bool:
        """Customize a color token (user override).

        Args:
            token: Token to customize
            color: New color value
            persist: Whether to save immediately (default: True)

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If token is not customizable (when customizable_tokens is defined)
        """
        try:
            # Check if user customization is allowed
            if not self.theme_config.get("allow_user_customization", True):
                logger.warning("User customization is disabled")
                return False

            # Check if token is customizable (if list is defined)
            customizable = self.theme_config.get("customizable_tokens", [])
            if customizable and token not in customizable:
                raise ValueError(
                    f"Token '{token}' is not customizable. "
                    f"Allowed tokens: {', '.join(customizable)}"
                )

            # Set user override
            theme_manager = ThemeManager.get_instance()
            theme_manager.set_user_override(token, color)

            # Persist if requested
            if persist:
                self.save_user_preferences()

            logger.debug(f"Customized color: {token} = {color} (persist={persist})")
            return True

        except Exception as e:
            logger.error(f"Error customizing color: {e}")
            return False

    def reset_color(self, token: str, persist: bool = True) -> bool:
        """Reset a color token to its default (remove user override).

        Args:
            token: Token to reset
            persist: Whether to save immediately (default: True)

        Returns:
            True if successful, False otherwise
        """
        try:
            theme_manager = ThemeManager.get_instance()
            removed = theme_manager.remove_user_override(token)

            # Persist if requested
            if persist:
                self.save_user_preferences()

            logger.debug(f"Reset color: {token} (removed={removed}, persist={persist})")
            return removed

        except Exception as e:
            logger.error(f"Error resetting color: {e}")
            return False

    def get_customizable_tokens(self) -> List[str]:
        """Get list of tokens that users can customize.

        Returns:
            List of customizable token names (empty list means all tokens allowed)
        """
        return self.theme_config.get("customizable_tokens", [])

    def is_token_customizable(self, token: str) -> bool:
        """Check if a token is customizable.

        Args:
            token: Token to check

        Returns:
            True if token is customizable, False otherwise
        """
        if not self.theme_config.get("allow_user_customization", True):
            return False

        customizable = self.theme_config.get("customizable_tokens", [])
        # Empty list means all tokens are customizable
        if not customizable:
            return True

        return token in customizable

    # ========================================================================
    # QSettings Helper
    # ========================================================================

    def _get_settings(self) -> QSettings:
        """Get QSettings instance for this application.

        Returns:
            QSettings instance
        """
        organization = self.organizationName() or "VFWidgets"
        application = self.applicationName() or "VFApp"

        return QSettings(organization, application)

    # ========================================================================
    # Override set_theme to save preference
    # ========================================================================

    def set_theme(self, theme_name: str) -> bool:
        """Set theme and optionally save to preferences.

        Args:
            theme_name: Name of theme to set

        Returns:
            True if successful, False otherwise
        """
        # Call parent implementation
        success = super().set_theme(theme_name)

        # Save to preferences if enabled
        if success and self.theme_config.get("persist_base_theme", True):
            self.save_base_theme(theme_name)

        return success

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"VFThemedApplication("
            f"base_theme='{self.theme_config.get('base_theme')}', "
            f"app_overrides={len(self.theme_config.get('app_overrides', {}))}, "
            f"allow_customization={self.theme_config.get('allow_user_customization')}"
            f")"
        )
