"""Data models for Reamde preferences.

This module defines the structure and defaults for all application preferences.
"""

from dataclasses import asdict, dataclass, field

from vfwidgets_common import ThemeOverrides


@dataclass
class GeneralPreferences:
    """General application preferences."""

    # Startup
    restore_previous_session: bool = True
    max_recent_files: int = 10

    # Window Behavior
    confirm_close_multiple_tabs: bool = True
    show_tab_bar_single_tab: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GeneralPreferences":
        """Create from dictionary.

        Args:
            data: Dictionary with preference values

        Returns:
            GeneralPreferences instance
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class AppearancePreferences:
    """Appearance and UI preferences."""

    # Theme
    application_theme: str = "dark"  # "dark", "light", "default"
    sync_with_system: bool = False

    # Window
    window_opacity: int = 100  # 10-100%

    # Markdown Rendering
    font_family: str = ""  # Empty = default
    font_size: int = 16
    line_height: float = 1.6
    max_content_width: int = 800  # pixels, 0 = full width

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppearancePreferences":
        """Create from dictionary.

        Args:
            data: Dictionary with preference values

        Returns:
            AppearancePreferences instance
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class MarkdownPreferences:
    """Markdown rendering preferences."""

    # Rendering Features
    enable_syntax_highlighting: bool = True
    enable_math_rendering: bool = True
    enable_mermaid_diagrams: bool = True

    # Behavior
    auto_reload_on_change: bool = True
    scroll_sync: bool = False  # Future: sync scroll with source

    # Theme Color Overrides
    theme_overrides: ThemeOverrides = field(default_factory=ThemeOverrides)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert ThemeOverrides to dict
        data["theme_overrides"] = self.theme_overrides.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MarkdownPreferences":
        """Create from dictionary.

        Args:
            data: Dictionary with preference values

        Returns:
            MarkdownPreferences instance
        """
        # Extract theme_overrides separately
        theme_overrides_data = data.pop("theme_overrides", {})

        # Create instance with other fields
        prefs = cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

        # Reconstruct ThemeOverrides
        if theme_overrides_data:
            prefs.theme_overrides = ThemeOverrides.from_dict(theme_overrides_data)

        return prefs


@dataclass
class PreferencesModel:
    """Complete application preferences.

    Combines all preference categories into a single model.
    """

    general: GeneralPreferences = field(default_factory=GeneralPreferences)
    appearance: AppearancePreferences = field(default_factory=AppearancePreferences)
    markdown: MarkdownPreferences = field(default_factory=MarkdownPreferences)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with all preferences
        """
        return {
            "general": self.general.to_dict(),
            "appearance": self.appearance.to_dict(),
            "markdown": self.markdown.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PreferencesModel":
        """Create from dictionary.

        Args:
            data: Dictionary with preference values

        Returns:
            PreferencesModel instance
        """
        return cls(
            general=GeneralPreferences.from_dict(data.get("general", {})),
            appearance=AppearancePreferences.from_dict(data.get("appearance", {})),
            markdown=MarkdownPreferences.from_dict(data.get("markdown", {})),
        )
