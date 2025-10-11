"""SVG icon handler for rendering SVG icons to QIcon objects.

Provides SVG loading, color customization, and caching capabilities.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from ..logging import get_logger

logger = get_logger(__name__)


class SVGIconHandler:
    """Handles loading and rendering SVG icons.

    Provides SVG icon loading with color customization and caching.
    """

    def __init__(self):
        """Initialize SVG icon handler."""
        self._svg_cache: dict[str, QByteArray] = {}
        self._renderer_cache: dict[str, QSvgRenderer] = {}

    def load_svg_icon(
        self, svg_path: Path, size: Optional[QSize] = None, color: Optional[str] = None
    ) -> Optional[QIcon]:
        """Load SVG icon from file.

        Args:
            svg_path: Path to SVG file
            size: Desired icon size
            color: Color to apply to icon (hex format)

        Returns:
            QIcon object or None if loading fails

        """
        if not svg_path.exists():
            logger.error(f"SVG file not found: {svg_path}")
            return None

        if size is None:
            size = QSize(16, 16)

        try:
            # Load SVG content
            svg_content = self._load_svg_content(svg_path)
            if not svg_content:
                return None

            # Apply color modification if requested
            if color:
                svg_content = self._modify_svg_color(svg_content, color)

            # Create cache key
            cache_key = f"{svg_path}_{size.width()}x{size.height()}_{color or 'default'}"

            # Get or create renderer
            renderer = self._get_renderer(cache_key, svg_content)
            if not renderer or not renderer.isValid():
                logger.error(f"Invalid SVG content in: {svg_path}")
                return None

            # Render to pixmap
            pixmap = self._render_to_pixmap(renderer, size)
            if pixmap.isNull():
                logger.error(f"Failed to render SVG: {svg_path}")
                return None

            return QIcon(pixmap)

        except Exception as e:
            logger.error(f"Error loading SVG icon {svg_path}: {e}")
            return None

    def _load_svg_content(self, svg_path: Path) -> Optional[QByteArray]:
        """Load SVG content from file."""
        cache_key = str(svg_path)
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]

        try:
            with open(svg_path, "rb") as f:
                content = f.read()

            svg_content = QByteArray(content)
            self._svg_cache[cache_key] = svg_content
            return svg_content

        except Exception as e:
            logger.error(f"Error reading SVG file {svg_path}: {e}")
            return None

    def _modify_svg_color(self, svg_content: QByteArray, color: str) -> QByteArray:
        """Modify SVG content to apply color.

        Args:
            svg_content: Original SVG content
            color: Color to apply

        Returns:
            Modified SVG content

        """
        try:
            # Convert to string for manipulation
            svg_str = svg_content.data().decode("utf-8")

            # Parse SVG XML
            root = ET.fromstring(svg_str)

            # Apply color to all fill and stroke attributes
            self._apply_color_to_element(root, color)

            # Convert back to bytes
            modified_svg = ET.tostring(root, encoding="utf-8", method="xml")
            return QByteArray(modified_svg)

        except Exception as e:
            logger.warning(f"Failed to modify SVG color: {e}")
            return svg_content

    def _apply_color_to_element(self, element: ET.Element, color: str) -> None:
        """Recursively apply color to SVG element and children."""
        # Skip elements that should keep their original color
        skip_elements = {"defs", "metadata", "title", "desc"}
        if element.tag.split("}")[-1] in skip_elements:
            return

        # Apply color to fill attribute
        if "fill" in element.attrib and element.attrib["fill"] != "none":
            element.attrib["fill"] = color

        # Apply color to stroke attribute
        if "stroke" in element.attrib and element.attrib["stroke"] != "none":
            element.attrib["stroke"] = color

        # Check style attribute
        if "style" in element.attrib:
            style = element.attrib["style"]
            style = self._modify_style_color(style, color)
            element.attrib["style"] = style

        # Recursively process children
        for child in element:
            self._apply_color_to_element(child, color)

    def _modify_style_color(self, style: str, color: str) -> str:
        """Modify CSS style string to apply color."""
        style_parts = style.split(";")
        modified_parts = []

        for part in style_parts:
            if ":" in part:
                prop, value = part.split(":", 1)
                prop = prop.strip()
                value = value.strip()

                if prop in ["fill", "stroke"] and value != "none":
                    value = color

                modified_parts.append(f"{prop}:{value}")
            else:
                modified_parts.append(part)

        return ";".join(modified_parts)

    def _get_renderer(self, cache_key: str, svg_content: QByteArray) -> Optional[QSvgRenderer]:
        """Get or create SVG renderer."""
        if cache_key in self._renderer_cache:
            return self._renderer_cache[cache_key]

        try:
            renderer = QSvgRenderer(svg_content)
            if renderer.isValid():
                self._renderer_cache[cache_key] = renderer
                return renderer

        except Exception as e:
            logger.error(f"Error creating SVG renderer: {e}")

        return None

    def _render_to_pixmap(self, renderer: QSvgRenderer, size: QSize) -> QPixmap:
        """Render SVG to pixmap."""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.end()

        return pixmap

    def create_multi_size_icon(
        self, svg_path: Path, sizes: list, color: Optional[str] = None
    ) -> Optional[QIcon]:
        """Create icon with multiple sizes from SVG.

        Args:
            svg_path: Path to SVG file
            sizes: List of QSize objects
            color: Color to apply

        Returns:
            QIcon with multiple sizes

        """
        if not sizes:
            return self.load_svg_icon(svg_path, QSize(16, 16), color)

        try:
            icon = QIcon()

            for size in sizes:
                pixmap = self._create_pixmap_from_svg(svg_path, size, color)
                if pixmap and not pixmap.isNull():
                    icon.addPixmap(pixmap)

            return icon if not icon.isNull() else None

        except Exception as e:
            logger.error(f"Error creating multi-size icon: {e}")
            return None

    def _create_pixmap_from_svg(
        self, svg_path: Path, size: QSize, color: Optional[str]
    ) -> Optional[QPixmap]:
        """Create single pixmap from SVG."""
        svg_content = self._load_svg_content(svg_path)
        if not svg_content:
            return None

        if color:
            svg_content = self._modify_svg_color(svg_content, color)

        renderer = QSvgRenderer(svg_content)
        if not renderer.isValid():
            return None

        return self._render_to_pixmap(renderer, size)

    def get_svg_size(self, svg_path: Path) -> Optional[QSize]:
        """Get default size of SVG file.

        Args:
            svg_path: Path to SVG file

        Returns:
            Default SVG size or None

        """
        try:
            svg_content = self._load_svg_content(svg_path)
            if not svg_content:
                return None

            renderer = QSvgRenderer(svg_content)
            if renderer.isValid():
                return renderer.defaultSize()

        except Exception as e:
            logger.error(f"Error getting SVG size for {svg_path}: {e}")

        return None

    def is_valid_svg(self, svg_path: Path) -> bool:
        """Check if SVG file is valid.

        Args:
            svg_path: Path to SVG file

        Returns:
            True if SVG is valid

        """
        try:
            svg_content = self._load_svg_content(svg_path)
            if not svg_content:
                return False

            renderer = QSvgRenderer(svg_content)
            return renderer.isValid()

        except Exception:
            return False

    def clear_cache(self) -> None:
        """Clear SVG and renderer caches."""
        self._svg_cache.clear()
        self._renderer_cache.clear()
        logger.info("SVG caches cleared")

    def get_cache_info(self) -> dict[str, int]:
        """Get cache information."""
        return {
            "svg_cache_size": len(self._svg_cache),
            "renderer_cache_size": len(self._renderer_cache),
        }

    def preload_svg(self, svg_path: Path) -> bool:
        """Preload SVG into cache.

        Args:
            svg_path: Path to SVG file

        Returns:
            True if successfully preloaded

        """
        try:
            svg_content = self._load_svg_content(svg_path)
            return svg_content is not None

        except Exception as e:
            logger.error(f"Error preloading SVG {svg_path}: {e}")
            return False

    def extract_colors_from_svg(self, svg_path: Path) -> list:
        """Extract colors used in SVG file.

        Args:
            svg_path: Path to SVG file

        Returns:
            List of color strings found in SVG

        """
        colors = set()

        try:
            with open(svg_path, encoding="utf-8") as f:
                svg_content = f.read()

            # Parse XML
            root = ET.fromstring(svg_content)
            self._extract_colors_from_element(root, colors)

        except Exception as e:
            logger.error(f"Error extracting colors from SVG {svg_path}: {e}")

        return list(colors)

    def _extract_colors_from_element(self, element: ET.Element, colors: set) -> None:
        """Recursively extract colors from SVG element."""
        # Check fill attribute
        if "fill" in element.attrib:
            fill = element.attrib["fill"]
            if fill and fill != "none" and fill != "transparent":
                colors.add(fill)

        # Check stroke attribute
        if "stroke" in element.attrib:
            stroke = element.attrib["stroke"]
            if stroke and stroke != "none" and stroke != "transparent":
                colors.add(stroke)

        # Check style attribute
        if "style" in element.attrib:
            style = element.attrib["style"]
            self._extract_colors_from_style(style, colors)

        # Process children
        for child in element:
            self._extract_colors_from_element(child, colors)

    def _extract_colors_from_style(self, style: str, colors: set) -> None:
        """Extract colors from CSS style string."""
        import re

        # Find color values in style
        color_patterns = [
            r"fill:\s*([^;]+)",
            r"stroke:\s*([^;]+)",
            r"color:\s*([^;]+)",
        ]

        for pattern in color_patterns:
            matches = re.findall(pattern, style)
            for match in matches:
                color = match.strip()
                if color and color != "none" and color != "transparent":
                    colors.add(color)
