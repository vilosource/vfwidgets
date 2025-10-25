"""Workspace configuration for Reamde.

Extends vfwidgets-workspace WorkspaceConfig with markdown-specific settings.
"""

from dataclasses import dataclass
from typing import Any

try:
    from vfwidgets_workspace import WorkspaceConfig

    WORKSPACE_AVAILABLE = True
except ImportError:
    # Fallback if workspace widget not installed
    WORKSPACE_AVAILABLE = False
    from dataclasses import dataclass, field

    @dataclass
    class WorkspaceConfig:
        """Minimal fallback WorkspaceConfig."""

        name: str = ""
        version: int = 1
        folders: list = field(default_factory=list)
        excluded_folders: list = field(default_factory=list)
        included_extensions: list = field(default_factory=list)
        theme_overrides: dict = field(default_factory=dict)
        recent_files: list = field(default_factory=list)
        custom_data: dict = field(default_factory=dict)


@dataclass
class ReamdeWorkspaceConfig(WorkspaceConfig):
    """Reamde-specific workspace configuration.

    Extends WorkspaceConfig with markdown-specific settings for view modes,
    auto-save, and rendering preferences.
    """

    # Markdown-specific settings
    default_view_mode: str = "preview"  # "preview" | "split" | "editor"
    auto_save: bool = True  # Auto-save in split/editor modes
    auto_save_delay: float = 1.5  # Debounce delay in seconds

    # Markdown rendering preferences
    render_math: bool = True  # Render LaTeX math
    render_mermaid: bool = True  # Render Mermaid diagrams
    syntax_theme: str = "prism"  # Code syntax highlighting theme

    # Editor preferences
    line_numbers: bool = True
    word_wrap: bool = True
    spell_check: bool = False

    def __post_init__(self):
        """Set markdown extensions if not specified."""
        if hasattr(super(), "__post_init__"):
            super().__post_init__()

        # Note: included_extensions is only in the fallback WorkspaceConfig
        # The real WorkspaceConfig from vfwidgets_workspace doesn't have this field
        # So we only set it if the attribute exists
        if hasattr(self, "included_extensions") and not self.included_extensions:
            self.included_extensions = [".md", ".markdown", ".mdown", ".mkd"]

    @classmethod
    def from_workspace_config(cls, config: WorkspaceConfig) -> "ReamdeWorkspaceConfig":
        """Convert generic WorkspaceConfig to ReamdeWorkspaceConfig.

        Used when loading .workspace.json (generic) instead of .reamde-workspace.json.

        Args:
            config: Generic workspace configuration

        Returns:
            ReamdeWorkspaceConfig with markdown defaults
        """
        # Only copy fields that exist in the real WorkspaceConfig
        # (version, name, folders, excluded_folders, custom_data)
        return cls(
            name=config.name,
            version=config.version,
            folders=config.folders,
            excluded_folders=config.excluded_folders,
            custom_data=config.custom_data,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON storage.

        Returns:
            Dictionary representation of configuration
        """
        # Get base config dict
        base_dict = super().to_dict() if hasattr(super(), "to_dict") else {}

        # Add Reamde-specific fields
        base_dict.update(
            {
                "default_view_mode": self.default_view_mode,
                "auto_save": self.auto_save,
                "auto_save_delay": self.auto_save_delay,
                "render_math": self.render_math,
                "render_mermaid": self.render_mermaid,
                "syntax_theme": self.syntax_theme,
                "line_numbers": self.line_numbers,
                "word_wrap": self.word_wrap,
                "spell_check": self.spell_check,
            }
        )

        return base_dict

    def set_session_data(
        self, open_files: list[str], active_index: int, view_modes: dict[str, str]
    ) -> None:
        """Store Reamde session data in custom_data.

        Used when saving workspace file to include current session state.

        Args:
            open_files: List of open file paths
            active_index: Index of active file
            view_modes: Dict mapping file paths to view modes
        """
        self.custom_data["reamde_session"] = {
            "open_files": open_files,
            "active_file_index": active_index,
            "view_modes": view_modes,
        }

    def get_session_data(self) -> tuple[list[str], int, dict[str, str]]:
        """Get Reamde session data from custom_data.

        Used when loading workspace file to restore session state.

        Returns:
            Tuple of (open_files, active_index, view_modes)
        """
        session = self.custom_data.get("reamde_session", {})
        return (
            session.get("open_files", []),
            session.get("active_file_index", -1),
            session.get("view_modes", {}),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReamdeWorkspaceConfig":
        """Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ReamdeWorkspaceConfig instance
        """
        # Extract Reamde-specific fields
        reamde_fields = {
            "default_view_mode": data.get("default_view_mode", "preview"),
            "auto_save": data.get("auto_save", True),
            "auto_save_delay": data.get("auto_save_delay", 1.5),
            "render_math": data.get("render_math", True),
            "render_mermaid": data.get("render_mermaid", True),
            "syntax_theme": data.get("syntax_theme", "prism"),
            "line_numbers": data.get("line_numbers", True),
            "word_wrap": data.get("word_wrap", True),
            "spell_check": data.get("spell_check", False),
        }

        # Create base config
        if WORKSPACE_AVAILABLE and hasattr(WorkspaceConfig, "from_dict"):
            base_config = WorkspaceConfig.from_dict(data)
            # Merge with Reamde fields (only use fields that exist in real WorkspaceConfig)
            return cls(
                name=base_config.name,
                version=base_config.version,
                folders=base_config.folders,
                excluded_folders=base_config.excluded_folders,
                custom_data=base_config.custom_data,
                **reamde_fields,
            )
        else:
            # Fallback: create from data dict directly (fallback WorkspaceConfig has more fields)
            return cls(
                name=data.get("name", ""),
                version=data.get("version", 1),
                folders=data.get("folders", []),
                excluded_folders=data.get("excluded_folders", []),
                included_extensions=data.get("included_extensions", []),
                theme_overrides=data.get("theme_overrides", {}),
                recent_files=data.get("recent_files", []),
                custom_data=data.get("custom_data", {}),
                **reamde_fields,
            )
