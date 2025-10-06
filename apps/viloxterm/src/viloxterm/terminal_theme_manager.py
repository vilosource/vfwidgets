"""Terminal Theme Manager - Storage and management for terminal themes."""

import json
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


class TerminalThemeManager:
    """Manages terminal theme storage, loading, and application.

    Terminal themes are stored separately from application themes to allow
    independent customization (e.g., dark app UI with light terminal).

    Storage:
        - Bundled themes: apps/viloxterm/themes/
        - User themes: ~/.config/viloxterm/terminal_themes/
        - Config: ~/.config/viloxterm/config.json
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize theme manager.

        Args:
            config_dir: Directory for storing themes (default: ~/.config/viloxterm)
        """
        self.config_dir = config_dir or Path.home() / ".config" / "viloxterm"
        self.themes_dir = self.config_dir / "terminal_themes"
        self.config_file = self.config_dir / "config.json"

        # Create directories
        self.themes_dir.mkdir(parents=True, exist_ok=True)

        # Cache for loaded themes
        self._theme_cache: dict[str, dict] = {}

        # Load or create config
        self._config = self._load_config()

        logger.info(f"TerminalThemeManager initialized: {self.themes_dir}")

    def _load_config(self) -> dict:
        """Load application config file.

        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return {}
        return {}

    def _save_config(self) -> None:
        """Save application config file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get_default_theme(self) -> dict:
        """Get the default terminal theme.

        Returns:
            Terminal theme dictionary
        """
        default_name = self._config.get("default_terminal_theme", "default-dark")

        try:
            return self.load_theme(default_name)
        except Exception as e:
            logger.warning(f"Failed to load default theme '{default_name}': {e}")
            return self._get_builtin_default_dark()

    def set_default_theme(self, theme_name: str) -> None:
        """Set the default theme for new terminals.

        Args:
            theme_name: Name of theme to set as default
        """
        self._config["default_terminal_theme"] = theme_name
        self._save_config()
        logger.info(f"Set default terminal theme to: {theme_name}")

    def save_theme(self, theme: dict, name: str) -> None:
        """Save custom theme to JSON file.

        Args:
            theme: Terminal theme dictionary
            name: Theme name (will be used as filename)
        """
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_name = safe_name.replace(" ", "-").lower()

        file_path = self.themes_dir / f"{safe_name}.json"

        try:
            with open(file_path, "w") as f:
                json.dump(theme, f, indent=2)

            # Update cache
            self._theme_cache[name] = theme

            logger.info(f"Saved theme '{name}' to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save theme '{name}': {e}")
            raise

    def load_theme(self, name: str) -> dict:
        """Load theme from JSON file.

        Args:
            name: Theme name to load

        Returns:
            Terminal theme dictionary

        Raises:
            FileNotFoundError: If theme file not found
        """
        # Check cache first
        if name in self._theme_cache:
            return self._theme_cache[name].copy()

        # Try user themes directory
        safe_name = name.replace(" ", "-").lower()
        file_path = self.themes_dir / f"{safe_name}.json"

        if not file_path.exists():
            # Try bundled themes (relative to this file)
            # Path(__file__) = .../apps/viloxterm/src/viloxterm/terminal_theme_manager.py
            # We need: .../apps/viloxterm/themes/
            bundled_path = Path(__file__).parent.parent.parent / "themes" / f"{safe_name}.json"
            if bundled_path.exists():
                file_path = bundled_path
            else:
                raise FileNotFoundError(f"Theme not found: {name}")

        try:
            with open(file_path, "r") as f:
                theme = json.load(f)

            # Cache it
            self._theme_cache[name] = theme

            logger.debug(f"Loaded theme '{name}' from {file_path}")
            return theme.copy()
        except Exception as e:
            logger.error(f"Failed to load theme '{name}': {e}")
            raise

    def list_themes(self) -> list[str]:
        """List all available theme names.

        Returns:
            List of theme names
        """
        themes = set()

        # Scan user themes directory
        if self.themes_dir.exists():
            for file_path in self.themes_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        theme = json.load(f)
                        themes.add(theme.get("name", file_path.stem))
                except Exception:
                    pass

        # Scan bundled themes
        bundled_dir = Path(__file__).parent.parent.parent / "themes"
        if bundled_dir.exists():
            for file_path in bundled_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        theme = json.load(f)
                        themes.add(theme.get("name", file_path.stem))
                except Exception:
                    pass

        return sorted(list(themes))

    def delete_theme(self, name: str) -> bool:
        """Delete a custom theme.

        Args:
            name: Theme name to delete

        Returns:
            True if successful, False otherwise
        """
        safe_name = name.replace(" ", "-").lower()
        file_path = self.themes_dir / f"{safe_name}.json"

        if not file_path.exists():
            logger.warning(f"Theme '{name}' not found for deletion")
            return False

        try:
            file_path.unlink()

            # Remove from cache
            if name in self._theme_cache:
                del self._theme_cache[name]

            logger.info(f"Deleted theme '{name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete theme '{name}': {e}")
            return False

    def export_theme(self, name: str, path: Path) -> None:
        """Export theme to external JSON file.

        Args:
            name: Theme name to export
            path: Destination file path
        """
        theme = self.load_theme(name)

        try:
            with open(path, "w") as f:
                json.dump(theme, f, indent=2)
            logger.info(f"Exported theme '{name}' to {path}")
        except Exception as e:
            logger.error(f"Failed to export theme '{name}': {e}")
            raise

    def import_theme(self, path: Path) -> str:
        """Import theme from JSON file.

        Args:
            path: Source file path

        Returns:
            Imported theme name
        """
        try:
            with open(path, "r") as f:
                theme = json.load(f)

            # Validate theme has required fields
            if "name" not in theme:
                raise ValueError("Theme must have 'name' field")

            name = theme["name"]

            # Save to user themes directory
            self.save_theme(theme, name)

            logger.info(f"Imported theme '{name}' from {path}")
            return name
        except Exception as e:
            logger.error(f"Failed to import theme from {path}: {e}")
            raise

    def validate_theme(self, theme: dict) -> list[str]:
        """Validate theme for WCAG compliance.

        Args:
            theme: Terminal theme dictionary

        Returns:
            List of warning messages (empty if no issues)
        """
        warnings = []

        terminal = theme.get("terminal", {})
        fg = terminal.get("foreground")
        bg = terminal.get("background")

        if not fg or not bg:
            warnings.append("Theme must define foreground and background colors")
            return warnings

        # Calculate contrast ratio
        try:
            ratio = self._calculate_contrast_ratio(fg, bg)

            if ratio < 3.0:
                warnings.append(f"Very low contrast ({ratio:.1f}:1) - text may be unreadable")
            elif ratio < 4.5:
                warnings.append(f"Low contrast ({ratio:.1f}:1) - fails WCAG AA standard (4.5:1)")
            elif ratio < 7.0:
                warnings.append(f"Medium contrast ({ratio:.1f}:1) - fails WCAG AAA standard (7:1)")
            else:
                # No warnings, good contrast
                pass

        except Exception as e:
            warnings.append(f"Could not validate contrast: {e}")

        return warnings

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors.

        Args:
            color1: First color (hex or rgb string)
            color2: Second color (hex or rgb string)

        Returns:
            Contrast ratio (1.0 to 21.0)
        """

        def parse_color(color_str: str) -> tuple[int, int, int]:
            """Parse color string to RGB tuple."""
            qcolor = QColor(color_str)
            if not qcolor.isValid():
                raise ValueError(f"Invalid color: {color_str}")
            return (qcolor.red(), qcolor.green(), qcolor.blue())

        def relative_luminance(rgb: tuple[int, int, int]) -> float:
            """Calculate relative luminance."""
            r, g, b = [c / 255.0 for c in rgb]

            # Apply gamma correction
            def gamma(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            r, g, b = gamma(r), gamma(g), gamma(b)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        rgb1 = parse_color(color1)
        rgb2 = parse_color(color2)

        lum1 = relative_luminance(rgb1)
        lum2 = relative_luminance(rgb2)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)

    def _get_builtin_default_dark(self) -> dict:
        """Get built-in default dark theme.

        Returns:
            Default dark theme dictionary
        """
        return {
            "name": "Default Dark",
            "version": "1.0.0",
            "author": "ViloxTerm",
            "description": "Default dark theme inspired by VS Code",
            "terminal": {
                "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                "fontSize": 14,
                "lineHeight": 1.2,
                "letterSpacing": 0,
                "cursorBlink": True,
                "cursorStyle": "block",
                "background": "#1e1e1e",
                "foreground": "#d4d4d4",
                "cursor": "#ffcc00",
                "cursorAccent": "#1e1e1e",
                "selectionBackground": "rgba(38, 79, 120, 0.3)",
                "black": "#000000",
                "red": "#cd3131",
                "green": "#0dbc79",
                "yellow": "#e5e510",
                "blue": "#2472c8",
                "magenta": "#bc3fbc",
                "cyan": "#11a8cd",
                "white": "#e5e5e5",
                "brightBlack": "#555753",
                "brightRed": "#f14c4c",
                "brightGreen": "#23d18b",
                "brightYellow": "#f5f543",
                "brightBlue": "#3b8eea",
                "brightMagenta": "#d670d6",
                "brightCyan": "#29b8db",
                "brightWhite": "#f5f5f5",
            },
        }
