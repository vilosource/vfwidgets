"""Icon font loader for font-based icon themes.

Handles loading icon fonts and creating QIcon objects from font characters.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen, QPixmap

from ..logging import get_logger

logger = get_logger(__name__)


class IconFontLoader:
    """Loads and manages icon fonts for creating icons from font characters.

    Supports TTF, OTF, WOFF, and WOFF2 font formats.
    """

    def __init__(self):
        """Initialize icon font loader."""
        self._loaded_fonts: dict[str, str] = {}  # path -> family_name
        self._font_database = QFontDatabase()

    def load_font(self, font_path: Path) -> Optional[str]:
        """Load icon font from file.

        Args:
            font_path: Path to font file

        Returns:
            Font family name if successful, None otherwise

        """
        logger.info(f"Loading icon font: {font_path}")

        if not font_path.exists():
            logger.error(f"Font file not found: {font_path}")
            return None

        # Check if already loaded
        font_path_str = str(font_path)
        if font_path_str in self._loaded_fonts:
            return self._loaded_fonts[font_path_str]

        try:
            # Add font to database
            font_id = self._font_database.addApplicationFont(font_path_str)

            if font_id == -1:
                logger.error(f"Failed to load font: {font_path}")
                return None

            # Get font families
            families = self._font_database.applicationFontFamilies(font_id)

            if not families:
                logger.error(f"No font families found in: {font_path}")
                return None

            family_name = families[0]
            self._loaded_fonts[font_path_str] = family_name

            logger.info(f"Successfully loaded font: {family_name}")
            return family_name

        except Exception as e:
            logger.error(f"Error loading font {font_path}: {e}")
            return None

    def create_icon_from_font(
        self, font_family: str, character: str, size: QSize, color: Optional[str] = None
    ) -> Optional[QIcon]:
        """Create QIcon from font character.

        Args:
            font_family: Font family name
            character: Unicode character or hex code
            size: Icon size
            color: Icon color (hex format)

        Returns:
            QIcon object or None if creation fails

        """
        try:
            # Parse character
            if character.startswith("\\u") or character.startswith("\\x"):
                # Handle unicode escapes
                char = character.encode().decode("unicode_escape")
            elif character.startswith("0x"):
                # Handle hex codes
                char = chr(int(character, 16))
            else:
                # Direct character
                char = character

            # Create font
            font = QFont(font_family)
            font.setPixelSize(min(size.width(), size.height()))

            # Create pixmap
            pixmap = QPixmap(size)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Paint character
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setFont(font)

            # Set color
            if color:
                paint_color = self._parse_color(color)
            else:
                paint_color = QColor(Qt.GlobalColor.black)

            painter.setPen(QPen(paint_color))

            # Calculate text position (centered)
            font_metrics = painter.fontMetrics()
            text_rect = font_metrics.boundingRect(char)

            x = (size.width() - text_rect.width()) // 2 - text_rect.x()
            y = (size.height() - text_rect.height()) // 2 - text_rect.y()

            painter.drawText(x, y, char)
            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            logger.error(f"Error creating icon from font character {character}: {e}")
            return None

    def _parse_color(self, color_str: str) -> QColor:
        """Parse color string to QColor."""
        if color_str.startswith("#"):
            return QColor(color_str)
        elif color_str.startswith("rgb("):
            # Parse rgb(r, g, b) format
            rgb_str = color_str[4:-1]  # Remove 'rgb(' and ')'
            components = [int(x.strip()) for x in rgb_str.split(",")]
            if len(components) >= 3:
                return QColor(components[0], components[1], components[2])
        elif color_str.startswith("rgba("):
            # Parse rgba(r, g, b, a) format
            rgba_str = color_str[5:-1]  # Remove 'rgba(' and ')'
            components = [float(x.strip()) for x in rgba_str.split(",")]
            if len(components) >= 4:
                return QColor(
                    int(components[0]),
                    int(components[1]),
                    int(components[2]),
                    int(components[3] * 255),
                )

        # Try named colors or fallback to black
        color = QColor(color_str)
        return color if color.isValid() else QColor(Qt.GlobalColor.black)

    def get_loaded_fonts(self) -> dict[str, str]:
        """Get dictionary of loaded fonts (path -> family_name)."""
        return self._loaded_fonts.copy()

    def is_font_loaded(self, font_path: Path) -> bool:
        """Check if font is already loaded."""
        return str(font_path) in self._loaded_fonts

    def get_font_family(self, font_path: Path) -> Optional[str]:
        """Get font family name for loaded font."""
        return self._loaded_fonts.get(str(font_path))

    def unload_font(self, font_path: Path) -> bool:
        """Unload font from application.

        Args:
            font_path: Path to font file

        Returns:
            True if successfully unloaded

        """
        font_path_str = str(font_path)
        if font_path_str not in self._loaded_fonts:
            return False

        try:
            # Note: QFontDatabase doesn't provide a direct way to unload fonts
            # We can only remove from our tracking
            del self._loaded_fonts[font_path_str]
            logger.info(f"Unloaded font tracking for: {font_path}")
            return True

        except Exception as e:
            logger.error(f"Error unloading font {font_path}: {e}")
            return False

    def create_preview_icon(
        self, font_family: str, sample_chars: str = "Aa", size: QSize = None
    ) -> Optional[QIcon]:
        """Create preview icon showing font sample.

        Args:
            font_family: Font family name
            sample_chars: Characters to display
            size: Icon size

        Returns:
            Preview icon

        """
        if size is None:
            size = QSize(32, 32)

        try:
            # Create font
            font = QFont(font_family)
            font.setPixelSize(size.height() // 2)

            # Create pixmap
            pixmap = QPixmap(size)
            pixmap.fill(Qt.GlobalColor.white)

            # Paint sample text
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setFont(font)
            painter.setPen(QColor(Qt.GlobalColor.black))

            # Center text
            font_metrics = painter.fontMetrics()
            text_rect = font_metrics.boundingRect(sample_chars)

            x = (size.width() - text_rect.width()) // 2 - text_rect.x()
            y = (size.height() - text_rect.height()) // 2 - text_rect.y()

            painter.drawText(x, y, sample_chars)

            # Draw border
            painter.setPen(QColor(Qt.GlobalColor.gray))
            painter.drawRect(0, 0, size.width() - 1, size.height() - 1)

            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            logger.error(f"Error creating font preview: {e}")
            return None

    def get_font_info(self, font_family: str) -> dict[str, any]:
        """Get information about loaded font.

        Args:
            font_family: Font family name

        Returns:
            Dictionary with font information

        """
        try:
            font = QFont(font_family)
            QFontDatabase().font(font_family, "Regular", 12)

            return {
                "family": font_family,
                "style_hint": font.styleHint(),
                "weight": font.weight(),
                "italic": font.italic(),
                "point_size": font.pointSize(),
                "pixel_size": font.pixelSize(),
                "exact_match": QFontDatabase().exactMatch(font_family, "Regular", 12),
                "writing_systems": QFontDatabase().writingSystems(font_family),
                "styles": QFontDatabase().styles(font_family),
            }

        except Exception as e:
            logger.error(f"Error getting font info for {font_family}: {e}")
            return {}

    def test_character_support(self, font_family: str, character: str) -> bool:
        """Test if font supports a specific character.

        Args:
            font_family: Font family name
            character: Character to test

        Returns:
            True if character is supported

        """
        try:
            font = QFont(font_family)

            # Parse character like in create_icon_from_font
            if character.startswith("\\u") or character.startswith("\\x"):
                char = character.encode().decode("unicode_escape")
            elif character.startswith("0x"):
                char = chr(int(character, 16))
            else:
                char = character

            # Create temporary pixmap to test rendering
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(pixmap)
            painter.setFont(font)

            # Check if character has visible rendering
            font_metrics = painter.fontMetrics()
            char_width = font_metrics.horizontalAdvance(char)

            painter.end()

            # Character is supported if it has non-zero width
            return char_width > 0

        except Exception as e:
            logger.warning(f"Error testing character support for {character}: {e}")
            return False
