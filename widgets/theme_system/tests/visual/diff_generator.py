#!/usr/bin/env python3
"""
Visual Diff Generator for Theme Testing
"""

import colorsys
from enum import Enum

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class DiffMode(Enum):
    """Visual diff display modes."""

    HIGHLIGHT = "highlight"  # Highlight differences
    SIDE_BY_SIDE = "side_by_side"  # Show images side by side
    OVERLAY = "overlay"  # Overlay differences
    HEATMAP = "heatmap"  # Heatmap of differences


class DiffGenerator:
    """Generate visual diffs between images."""

    def __init__(self):
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is required for diff generation")

    def generate_highlight_diff(
        self,
        actual: Image.Image,
        expected: Image.Image,
        highlight_color: tuple[int, int, int] = (255, 0, 0),
        threshold: int = 10,
    ) -> Image.Image:
        """
        Generate diff with differences highlighted.

        Args:
            actual: Actual image
            expected: Expected image
            highlight_color: RGB color for highlighting
            threshold: Pixel difference threshold

        Returns:
            Image with differences highlighted
        """
        # Ensure same size
        if actual.size != expected.size:
            expected = expected.resize(actual.size, Image.Resampling.LANCZOS)

        # Convert to same mode
        if actual.mode != expected.mode:
            expected = expected.convert(actual.mode)

        result = actual.copy()
        actual_data = actual.getdata()
        expected_data = expected.getdata()

        new_data = []
        for actual_pixel, expected_pixel in zip(actual_data, expected_data):
            # Calculate pixel difference
            if isinstance(actual_pixel, tuple) and isinstance(expected_pixel, tuple):
                diff = sum(abs(a - e) for a, e in zip(actual_pixel, expected_pixel))
                diff /= len(actual_pixel)
            else:
                diff = abs(actual_pixel - expected_pixel)

            if diff > threshold:
                new_data.append(highlight_color)
            else:
                new_data.append(actual_pixel)

        result.putdata(new_data)
        return result

    def generate_side_by_side_diff(
        self,
        actual: Image.Image,
        expected: Image.Image,
        separator_width: int = 2,
        separator_color: tuple[int, int, int] = (128, 128, 128),
    ) -> Image.Image:
        """
        Generate side-by-side comparison.

        Args:
            actual: Actual image
            expected: Expected image
            separator_width: Width of separator line
            separator_color: Color of separator

        Returns:
            Side-by-side comparison image
        """
        # Make images same height
        max_height = max(actual.height, expected.height)
        if actual.height != max_height:
            actual = actual.resize((actual.width, max_height), Image.Resampling.LANCZOS)
        if expected.height != max_height:
            expected = expected.resize((expected.width, max_height), Image.Resampling.LANCZOS)

        # Create result image
        total_width = actual.width + expected.width + separator_width
        result = Image.new("RGB", (total_width, max_height), separator_color)

        # Paste images
        result.paste(expected, (0, 0))
        result.paste(actual, (expected.width + separator_width, 0))

        # Add labels
        try:
            draw = ImageDraw.Draw(result)
            # Try to use default font, fallback if not available
            try:
                font = ImageFont.load_default()
            except:
                font = None

            # Add labels
            draw.text((10, 10), "Expected", fill=(255, 255, 255), font=font)
            draw.text(
                (expected.width + separator_width + 10, 10),
                "Actual",
                fill=(255, 255, 255),
                font=font,
            )

        except Exception:
            # If text drawing fails, continue without labels
            pass

        return result

    def generate_overlay_diff(
        self, actual: Image.Image, expected: Image.Image, alpha: float = 0.5
    ) -> Image.Image:
        """
        Generate overlay diff showing both images blended.

        Args:
            actual: Actual image
            expected: Expected image
            alpha: Blend factor (0.0 = expected only, 1.0 = actual only)

        Returns:
            Blended overlay image
        """
        # Ensure same size and mode
        if actual.size != expected.size:
            expected = expected.resize(actual.size, Image.Resampling.LANCZOS)

        if actual.mode != expected.mode:
            expected = expected.convert(actual.mode)

        # Blend images
        return Image.blend(expected, actual, alpha)

    def generate_heatmap_diff(
        self, actual: Image.Image, expected: Image.Image, colormap: str = "hot"
    ) -> Image.Image:
        """
        Generate heatmap showing difference intensity.

        Args:
            actual: Actual image
            expected: Expected image
            colormap: Colormap style ('hot', 'cool', 'rainbow')

        Returns:
            Heatmap image
        """
        # Ensure same size
        if actual.size != expected.size:
            expected = expected.resize(actual.size, Image.Resampling.LANCZOS)

        # Convert to grayscale for difference calculation
        actual_gray = actual.convert("L")
        expected_gray = expected.convert("L")

        # Calculate difference
        actual_data = list(actual_gray.getdata())
        expected_data = list(expected_gray.getdata())

        diff_data = []
        max_diff = 0

        for a, e in zip(actual_data, expected_data):
            diff = abs(a - e)
            diff_data.append(diff)
            max_diff = max(max_diff, diff)

        # Normalize differences
        if max_diff > 0:
            diff_data = [d / max_diff for d in diff_data]

        # Create heatmap
        heatmap_data = []
        for diff in diff_data:
            color = self._get_heatmap_color(diff, colormap)
            heatmap_data.append(color)

        # Create result image
        result = Image.new("RGB", actual.size)
        result.putdata(heatmap_data)

        return result

    def _get_heatmap_color(self, intensity: float, colormap: str) -> tuple[int, int, int]:
        """
        Get color for heatmap based on intensity.

        Args:
            intensity: Intensity value (0.0-1.0)
            colormap: Colormap style

        Returns:
            RGB color tuple
        """
        if colormap == "hot":
            # Hot colormap: black -> red -> yellow -> white
            if intensity < 0.33:
                # Black to red
                r = int(255 * (intensity / 0.33))
                g = 0
                b = 0
            elif intensity < 0.66:
                # Red to yellow
                r = 255
                g = int(255 * ((intensity - 0.33) / 0.33))
                b = 0
            else:
                # Yellow to white
                r = 255
                g = 255
                b = int(255 * ((intensity - 0.66) / 0.34))
        elif colormap == "cool":
            # Cool colormap: cyan -> magenta
            r = int(255 * intensity)
            g = int(255 * (1 - intensity))
            b = 255
        elif colormap == "rainbow":
            # Rainbow colormap using HSV
            h = (1 - intensity) * 0.8  # Hue from red to blue
            s = 1.0  # Full saturation
            v = 1.0  # Full value
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
        else:
            # Default: grayscale
            gray = int(255 * intensity)
            r, g, b = gray, gray, gray

        return (r, g, b)

    def generate_diff(
        self,
        actual: Image.Image,
        expected: Image.Image,
        mode: DiffMode = DiffMode.HIGHLIGHT,
        **kwargs,
    ) -> Image.Image:
        """
        Generate visual diff using specified mode.

        Args:
            actual: Actual image
            expected: Expected image
            mode: Diff generation mode
            **kwargs: Additional parameters for specific modes

        Returns:
            Generated diff image
        """
        if mode == DiffMode.HIGHLIGHT:
            return self.generate_highlight_diff(actual, expected, **kwargs)
        elif mode == DiffMode.SIDE_BY_SIDE:
            return self.generate_side_by_side_diff(actual, expected, **kwargs)
        elif mode == DiffMode.OVERLAY:
            return self.generate_overlay_diff(actual, expected, **kwargs)
        elif mode == DiffMode.HEATMAP:
            return self.generate_heatmap_diff(actual, expected, **kwargs)
        else:
            # Default to highlight
            return self.generate_highlight_diff(actual, expected, **kwargs)

    def generate_comprehensive_diff(
        self, actual: Image.Image, expected: Image.Image, difference_percentage: float
    ) -> Image.Image:
        """
        Generate comprehensive diff with multiple views.

        Args:
            actual: Actual image
            expected: Expected image
            difference_percentage: Overall difference percentage

        Returns:
            Comprehensive diff image
        """
        # Generate individual diffs
        highlight = self.generate_highlight_diff(actual, expected)
        side_by_side = self.generate_side_by_side_diff(actual, expected)
        heatmap = self.generate_heatmap_diff(actual, expected)

        # Calculate dimensions
        width = max(highlight.width, side_by_side.width, heatmap.width)
        height = highlight.height + side_by_side.height + heatmap.height + 100  # Extra for text

        # Create comprehensive result
        result = Image.new("RGB", (width, height), (255, 255, 255))

        # Paste components
        y_offset = 0

        # Title
        try:
            draw = ImageDraw.Draw(result)
            title = f"Visual Diff Report - {difference_percentage:.2%} difference"
            draw.text((10, y_offset), title, fill=(0, 0, 0))
            y_offset += 30
        except Exception:
            y_offset += 30

        # Side by side
        result.paste(side_by_side, (0, y_offset))
        y_offset += side_by_side.height + 10

        # Highlight diff
        try:
            draw.text((10, y_offset), "Differences Highlighted:", fill=(0, 0, 0))
            y_offset += 20
        except Exception:
            y_offset += 20

        result.paste(highlight, (0, y_offset))
        y_offset += highlight.height + 10

        # Heatmap
        try:
            draw.text((10, y_offset), "Difference Heatmap:", fill=(0, 0, 0))
            y_offset += 20
        except Exception:
            y_offset += 20

        result.paste(heatmap, (0, y_offset))

        return result
