"""
Icon theme implementation for VSCode-compatible icon themes.

Supports file type icons, folder icons, and custom icon sets with
both SVG and font-based icons.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Union, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont, QFontDatabase
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSvg import QSvgRenderer

from .font_loader import IconFontLoader
from .svg_handler import SVGIconHandler
from .file_associations import FileAssociationManager
from ..errors import ThemeSystemError
from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class IconDefinition:
    """Represents an icon definition."""

    name: str
    path: Optional[str] = None
    font_character: Optional[str] = None
    font_family: Optional[str] = None
    svg_content: Optional[str] = None
    color: Optional[str] = None
    size: Optional[QSize] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IconProvider(ABC):
    """Abstract base class for icon providers."""

    @abstractmethod
    def get_icon(self, icon_name: str, size: QSize = None) -> Optional[QIcon]:
        """Get icon by name."""
        pass

    @abstractmethod
    def has_icon(self, icon_name: str) -> bool:
        """Check if provider has icon."""
        pass

    @abstractmethod
    def list_icons(self) -> List[str]:
        """List available icons."""
        pass


class SVGIconProvider(IconProvider):
    """Icon provider for SVG icons."""

    def __init__(self, base_path: Path):
        """
        Initialize SVG icon provider.

        Args:
            base_path: Base directory containing SVG files
        """
        self.base_path = base_path
        self.svg_handler = SVGIconHandler()
        self._icon_cache: Dict[str, QIcon] = {}
        self._discover_icons()

    def _discover_icons(self):
        """Discover SVG icons in base path."""
        if not self.base_path.exists():
            logger.warning(f"SVG icon directory not found: {self.base_path}")
            return

        self._svg_files = {}
        for svg_file in self.base_path.rglob("*.svg"):
            icon_name = svg_file.stem
            self._svg_files[icon_name] = svg_file

        logger.info(f"Discovered {len(self._svg_files)} SVG icons")

    def get_icon(self, icon_name: str, size: QSize = None) -> Optional[QIcon]:
        """Get SVG icon by name."""
        if icon_name not in self._svg_files:
            return None

        # Check cache first
        cache_key = f"{icon_name}_{size.width() if size else 'default'}_{size.height() if size else 'default'}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Load SVG
        svg_path = self._svg_files[icon_name]
        icon = self.svg_handler.load_svg_icon(svg_path, size)

        if icon:
            self._icon_cache[cache_key] = icon

        return icon

    def has_icon(self, icon_name: str) -> bool:
        """Check if SVG icon exists."""
        return icon_name in self._svg_files

    def list_icons(self) -> List[str]:
        """List available SVG icons."""
        return list(self._svg_files.keys())


class FontIconProvider(IconProvider):
    """Icon provider for font-based icons."""

    def __init__(self, font_path: Path, character_map: Dict[str, str]):
        """
        Initialize font icon provider.

        Args:
            font_path: Path to icon font file
            character_map: Mapping of icon names to font characters
        """
        self.font_path = font_path
        self.character_map = character_map
        self.font_loader = IconFontLoader()
        self._icon_cache: Dict[str, QIcon] = {}

        # Load font
        self.font_family = self.font_loader.load_font(font_path)
        if not self.font_family:
            logger.error(f"Failed to load icon font: {font_path}")

    def get_icon(self, icon_name: str, size: QSize = None) -> Optional[QIcon]:
        """Get font icon by name."""
        if not self.font_family or icon_name not in self.character_map:
            return None

        # Check cache
        cache_key = f"{icon_name}_{size.width() if size else 16}_{size.height() if size else 16}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Create icon from font character
        character = self.character_map[icon_name]
        icon = self.font_loader.create_icon_from_font(
            self.font_family, character, size or QSize(16, 16)
        )

        if icon:
            self._icon_cache[cache_key] = icon

        return icon

    def has_icon(self, icon_name: str) -> bool:
        """Check if font icon exists."""
        return icon_name in self.character_map and bool(self.font_family)

    def list_icons(self) -> List[str]:
        """List available font icons."""
        return list(self.character_map.keys()) if self.font_family else []


class IconTheme:
    """
    VSCode-compatible icon theme support.

    Manages file type icons, folder icons, and custom icon sets.
    Supports both SVG icons and icon fonts.
    """

    def __init__(self, theme_path: Optional[Path] = None):
        """
        Initialize icon theme.

        Args:
            theme_path: Path to icon theme directory or JSON file
        """
        self.theme_path = theme_path
        self.name = "Default"
        self.version = "1.0.0"
        self.description = ""

        # Icon definitions
        self.file_icons: Dict[str, IconDefinition] = {}
        self.folder_icons: Dict[str, IconDefinition] = {}
        self.language_icons: Dict[str, IconDefinition] = {}
        self.default_file_icon: Optional[IconDefinition] = None
        self.default_folder_icon: Optional[IconDefinition] = None

        # Icon providers
        self.providers: List[IconProvider] = []

        # File associations
        self.file_associations = FileAssociationManager()

        # Icon cache
        self._icon_cache: Dict[str, QIcon] = {}

        # Load theme if path provided
        if theme_path:
            self.load_theme(theme_path)

    def load_theme(self, theme_path: Path) -> None:
        """
        Load icon theme from path.

        Args:
            theme_path: Path to theme directory or JSON file

        Raises:
            ThemeSystemError: If theme loading fails
        """
        logger.info(f"Loading icon theme from: {theme_path}")

        if not theme_path.exists():
            raise ThemeSystemError(f"Icon theme path not found: {theme_path}")

        try:
            if theme_path.is_file() and theme_path.suffix == '.json':
                self._load_from_json(theme_path)
            elif theme_path.is_dir():
                self._load_from_directory(theme_path)
            else:
                raise ThemeSystemError(f"Unsupported icon theme format: {theme_path}")

            logger.info(f"Successfully loaded icon theme: {self.name}")

        except Exception as e:
            logger.error(f"Failed to load icon theme: {e}")
            raise ThemeSystemError(f"Icon theme loading failed: {e}")

    def _load_from_json(self, json_path: Path) -> None:
        """Load icon theme from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)

        self._parse_theme_data(theme_data, json_path.parent)

    def _load_from_directory(self, theme_dir: Path) -> None:
        """Load icon theme from directory."""
        # Look for theme definition file
        theme_files = ['iconTheme.json', 'icon-theme.json', 'theme.json']
        theme_file = None

        for filename in theme_files:
            candidate = theme_dir / filename
            if candidate.exists():
                theme_file = candidate
                break

        if not theme_file:
            raise ThemeSystemError("No icon theme definition file found")

        self._load_from_json(theme_file)

    def _parse_theme_data(self, theme_data: Dict[str, Any], base_path: Path) -> None:
        """Parse theme data from JSON."""
        # Basic theme info
        self.name = theme_data.get('name', 'Unnamed Icon Theme')
        self.version = theme_data.get('version', '1.0.0')
        self.description = theme_data.get('description', '')

        # Parse icon definitions
        self._parse_icon_definitions(theme_data, base_path)

        # Setup providers
        self._setup_providers(base_path)

    def _parse_icon_definitions(self, theme_data: Dict[str, Any], base_path: Path) -> None:
        """Parse icon definitions from theme data."""
        # File icons
        file_icons = theme_data.get('fileIcons', {})
        for name, icon_def in file_icons.items():
            self.file_icons[name] = self._create_icon_definition(name, icon_def, base_path)

        # Folder icons
        folder_icons = theme_data.get('folderIcons', {})
        for name, icon_def in folder_icons.items():
            self.folder_icons[name] = self._create_icon_definition(name, icon_def, base_path)

        # Language icons
        language_icons = theme_data.get('languageIcons', {})
        for name, icon_def in language_icons.items():
            self.language_icons[name] = self._create_icon_definition(name, icon_def, base_path)

        # Default icons
        if 'defaultFile' in theme_data:
            self.default_file_icon = self._create_icon_definition(
                'default_file', theme_data['defaultFile'], base_path
            )

        if 'defaultFolder' in theme_data:
            self.default_folder_icon = self._create_icon_definition(
                'default_folder', theme_data['defaultFolder'], base_path
            )

        # File associations
        file_extensions = theme_data.get('fileExtensions', {})
        for ext, icon_name in file_extensions.items():
            self.file_associations.add_extension_mapping(ext, icon_name)

        file_names = theme_data.get('fileNames', {})
        for name, icon_name in file_names.items():
            self.file_associations.add_filename_mapping(name, icon_name)

    def _create_icon_definition(self, name: str, icon_data: Union[str, Dict], base_path: Path) -> IconDefinition:
        """Create icon definition from data."""
        if isinstance(icon_data, str):
            # Simple path reference
            return IconDefinition(
                name=name,
                path=str(base_path / icon_data)
            )

        # Complex definition
        icon_def = IconDefinition(name=name)

        if 'path' in icon_data:
            icon_def.path = str(base_path / icon_data['path'])

        if 'fontCharacter' in icon_data:
            icon_def.font_character = icon_data['fontCharacter']

        if 'fontFamily' in icon_data:
            icon_def.font_family = icon_data['fontFamily']

        if 'color' in icon_data:
            icon_def.color = icon_data['color']

        return icon_def

    def _setup_providers(self, base_path: Path) -> None:
        """Setup icon providers based on theme content."""
        # SVG provider for icon directories
        svg_dirs = ['icons', 'svg', 'images']
        for dir_name in svg_dirs:
            svg_dir = base_path / dir_name
            if svg_dir.exists():
                provider = SVGIconProvider(svg_dir)
                self.providers.append(provider)

        # Font provider if font files exist
        font_files = list(base_path.glob('*.ttf')) + list(base_path.glob('*.woff')) + list(base_path.glob('*.woff2'))
        for font_file in font_files:
            # Look for character map
            char_map_file = font_file.with_suffix('.json')
            if char_map_file.exists():
                try:
                    with open(char_map_file, 'r') as f:
                        char_map = json.load(f)

                    provider = FontIconProvider(font_file, char_map)
                    self.providers.append(provider)

                except Exception as e:
                    logger.warning(f"Failed to load font character map {char_map_file}: {e}")

    def get_icon(self, file_path: Path, size: QSize = None) -> QIcon:
        """
        Get icon for file path.

        Args:
            file_path: Path to file
            size: Desired icon size

        Returns:
            QIcon for the file
        """
        if size is None:
            size = QSize(16, 16)

        # Create cache key
        cache_key = f"{file_path}_{size.width()}_{size.height()}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        icon = None

        # Try to get specific icon
        if file_path.is_dir():
            icon = self._get_folder_icon(file_path, size)
        else:
            icon = self._get_file_icon(file_path, size)

        # Use default if no specific icon found
        if not icon:
            icon = self._get_default_icon(file_path, size)

        # Cache and return
        if icon:
            self._icon_cache[cache_key] = icon
        else:
            # Create empty icon as fallback
            icon = QIcon()

        return icon

    def _get_file_icon(self, file_path: Path, size: QSize) -> Optional[QIcon]:
        """Get icon for file."""
        # Check filename mapping first
        icon_name = self.file_associations.get_icon_for_filename(file_path.name)

        # Check extension mapping
        if not icon_name:
            icon_name = self.file_associations.get_icon_for_extension(file_path.suffix.lstrip('.'))

        # Check language mapping
        if not icon_name:
            language = self._detect_language(file_path)
            if language and language in self.language_icons:
                icon_name = language

        return self._load_icon_by_name(icon_name, size) if icon_name else None

    def _get_folder_icon(self, folder_path: Path, size: QSize) -> Optional[QIcon]:
        """Get icon for folder."""
        # Check for specific folder icon
        folder_name = folder_path.name.lower()

        # Common folder mappings
        folder_mappings = {
            '.git': 'folder-git',
            '.vscode': 'folder-vscode',
            'node_modules': 'folder-node',
            'src': 'folder-src',
            'tests': 'folder-test',
            'test': 'folder-test',
            'docs': 'folder-docs',
            'images': 'folder-images',
            'assets': 'folder-assets',
        }

        icon_name = folder_mappings.get(folder_name)
        if not icon_name and folder_name in self.folder_icons:
            icon_name = folder_name

        return self._load_icon_by_name(icon_name, size) if icon_name else None

    def _get_default_icon(self, file_path: Path, size: QSize) -> Optional[QIcon]:
        """Get default icon for file or folder."""
        if file_path.is_dir():
            if self.default_folder_icon:
                return self._load_icon_from_definition(self.default_folder_icon, size)
        else:
            if self.default_file_icon:
                return self._load_icon_from_definition(self.default_file_icon, size)

        return None

    def _load_icon_by_name(self, icon_name: str, size: QSize) -> Optional[QIcon]:
        """Load icon by name from available sources."""
        # Check file icons
        if icon_name in self.file_icons:
            return self._load_icon_from_definition(self.file_icons[icon_name], size)

        # Check folder icons
        if icon_name in self.folder_icons:
            return self._load_icon_from_definition(self.folder_icons[icon_name], size)

        # Check language icons
        if icon_name in self.language_icons:
            return self._load_icon_from_definition(self.language_icons[icon_name], size)

        # Check providers
        for provider in self.providers:
            if provider.has_icon(icon_name):
                icon = provider.get_icon(icon_name, size)
                if icon:
                    return icon

        return None

    def _load_icon_from_definition(self, icon_def: IconDefinition, size: QSize) -> Optional[QIcon]:
        """Load icon from definition."""
        try:
            if icon_def.path:
                # SVG or image file
                icon_path = Path(icon_def.path)
                if icon_path.exists():
                    if icon_path.suffix.lower() == '.svg':
                        svg_handler = SVGIconHandler()
                        return svg_handler.load_svg_icon(icon_path, size, icon_def.color)
                    else:
                        # Raster image
                        pixmap = QPixmap(str(icon_path))
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            return QIcon(scaled_pixmap)

            elif icon_def.font_character and icon_def.font_family:
                # Font-based icon
                font_loader = IconFontLoader()
                return font_loader.create_icon_from_font(
                    icon_def.font_family,
                    icon_def.font_character,
                    size,
                    icon_def.color
                )

        except Exception as e:
            logger.warning(f"Failed to load icon {icon_def.name}: {e}")

        return None

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        ext = file_path.suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.vue': 'vue',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'sass',
            '.sass': 'sass',
            '.less': 'less',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'settings',
            '.cfg': 'settings',
            '.conf': 'settings',
            '.md': 'markdown',
            '.rst': 'text',
            '.txt': 'text',
            '.java': 'java',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.r': 'r',
            '.m': 'matlab',
            '.swift': 'swift',
        }

        return language_map.get(ext)

    def get_available_icons(self) -> List[str]:
        """Get list of all available icon names."""
        icons = set()

        icons.update(self.file_icons.keys())
        icons.update(self.folder_icons.keys())
        icons.update(self.language_icons.keys())

        for provider in self.providers:
            icons.update(provider.list_icons())

        return sorted(list(icons))

    def has_icon(self, icon_name: str) -> bool:
        """Check if icon theme has specific icon."""
        if icon_name in self.file_icons:
            return True
        if icon_name in self.folder_icons:
            return True
        if icon_name in self.language_icons:
            return True

        for provider in self.providers:
            if provider.has_icon(icon_name):
                return True

        return False

    def reload(self) -> None:
        """Reload icon theme from disk."""
        if self.theme_path:
            # Clear cache
            self._icon_cache.clear()

            # Reload theme
            self.load_theme(self.theme_path)

    def export_theme_info(self) -> Dict[str, Any]:
        """Export theme information."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'file_icons_count': len(self.file_icons),
            'folder_icons_count': len(self.folder_icons),
            'language_icons_count': len(self.language_icons),
            'providers_count': len(self.providers),
            'available_icons': len(self.get_available_icons()),
            'has_default_file_icon': self.default_file_icon is not None,
            'has_default_folder_icon': self.default_folder_icon is not None,
        }