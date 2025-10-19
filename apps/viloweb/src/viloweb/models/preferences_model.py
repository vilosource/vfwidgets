"""Data models for ViloxWeb preferences.

This module defines the structure and defaults for all application preferences.
"""

from dataclasses import asdict, dataclass, field


@dataclass
class AppearancePreferences:
    """Appearance and UI preferences for ViloxWeb."""

    # Theme
    application_theme: str = "dark"
    sync_with_system: bool = False
    custom_theme_path: str = ""

    # Window
    window_opacity: int = 100  # 10-100%
    frameless_window: bool = True

    # Color Customization
    top_bar_background_color: str = ""  # Empty = use theme default

    # Accent Line
    show_accent_line: bool = True  # Show line below tab bar
    accent_line_color: str = ""  # Empty = use active tab color

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppearancePreferences":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class PreferencesModel:
    """Complete preferences model for ViloxWeb.

    This combines all preference categories into a single model.
    Each category can be accessed as a property.
    """

    appearance: AppearancePreferences = field(default_factory=AppearancePreferences)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with all preferences organized by category
        """
        return {
            "appearance": self.appearance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PreferencesModel":
        """Create preferences model from dictionary.

        Args:
            data: Dictionary with preferences (typically loaded from JSON)

        Returns:
            PreferencesModel instance
        """
        appearance = AppearancePreferences.from_dict(data.get("appearance", {}))

        return cls(appearance=appearance)

    @classmethod
    def get_defaults(cls) -> "PreferencesModel":
        """Get default preferences.

        Returns:
            PreferencesModel with all default values
        """
        return cls()
