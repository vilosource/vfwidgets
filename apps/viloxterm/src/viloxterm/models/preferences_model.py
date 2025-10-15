"""Data models for ViloxTerm preferences.

This module defines the structure and defaults for all application preferences.
"""

from dataclasses import dataclass, field, asdict


@dataclass
class GeneralPreferences:
    """General application preferences."""

    # Startup
    restore_session: bool = False
    default_shell: str = ""  # Empty = system default
    starting_directory: str = "home"  # "home", "last", "custom"
    custom_directory: str = ""
    tabs_on_startup: int = 1

    # Window Behavior
    close_on_last_tab: bool = True
    confirm_close_multiple_tabs: bool = True
    show_tab_bar_single_tab: bool = True
    frameless_window: bool = True

    # Session Management
    save_tab_layout: bool = False
    save_working_directories: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GeneralPreferences":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class AppearancePreferences:
    """Appearance and UI preferences."""

    # Theme
    application_theme: str = "dark"
    sync_with_system: bool = False
    custom_theme_path: str = ""

    # Window
    window_opacity: int = 100  # 10-100%
    background_blur: bool = False
    window_padding: int = 0

    # UI Elements
    tab_bar_position: str = "top"  # "top" or "bottom"
    show_menu_button: bool = True
    show_window_title: bool = True
    ui_font_size: int = 9  # System default

    # Focus Indicators
    focus_border_width: int = 3
    focus_border_color: str = ""  # Empty = theme default
    unfocused_dim_amount: int = 0  # 0-50%

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppearancePreferences":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class AdvancedPreferences:
    """Advanced and experimental preferences."""

    # Performance
    hardware_acceleration: str = "auto"  # "auto", "on", "off"
    webengine_cache_size: int = 50  # MB
    max_tabs: int = 100
    terminal_renderer: str = "auto"

    # Behavior
    enable_animations: bool = True
    terminal_server_port: int = 0  # 0 = auto
    log_level: str = "INFO"

    # Experimental
    ligature_support: bool = False
    gpu_rendering: bool = False
    custom_css: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AdvancedPreferences":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class PreferencesModel:
    """Complete preferences model for ViloxTerm.

    This combines all preference categories into a single model.
    Each category can be accessed as a property.
    """

    general: GeneralPreferences = field(default_factory=GeneralPreferences)
    appearance: AppearancePreferences = field(default_factory=AppearancePreferences)
    advanced: AdvancedPreferences = field(default_factory=AdvancedPreferences)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with all preferences organized by category
        """
        return {
            "general": self.general.to_dict(),
            "appearance": self.appearance.to_dict(),
            "advanced": self.advanced.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PreferencesModel":
        """Create preferences model from dictionary.

        Args:
            data: Dictionary with preferences (typically loaded from JSON)

        Returns:
            PreferencesModel instance
        """
        general = GeneralPreferences.from_dict(data.get("general", {}))
        appearance = AppearancePreferences.from_dict(data.get("appearance", {}))
        advanced = AdvancedPreferences.from_dict(data.get("advanced", {}))

        return cls(general=general, appearance=appearance, advanced=advanced)

    @classmethod
    def get_defaults(cls) -> "PreferencesModel":
        """Get default preferences.

        Returns:
            PreferencesModel with all default values
        """
        return cls()
