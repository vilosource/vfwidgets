#!/usr/bin/env python3
"""
Visual Testing Framework for VFWidgets Theme System
Task 22: Screenshot-based visual regression testing
"""

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ComparisonResult(Enum):
    """Result of image comparison."""

    IDENTICAL = "identical"
    SIMILAR = "similar"
    DIFFERENT = "different"
    ERROR = "error"


@dataclass
class VisualTestResult:
    """Result of a visual test."""

    name: str
    result: ComparisonResult
    difference_percentage: float
    baseline_path: Optional[Path] = None
    actual_path: Optional[Path] = None
    diff_path: Optional[Path] = None
    error_message: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class VisualTestFramework:
    """
    Visual regression testing framework for themed widgets.

    This framework provides comprehensive visual testing capabilities including:
    - Widget screenshot capture
    - Image comparison with configurable tolerance
    - Visual diff generation
    - Baseline management
    - CI/CD integration support
    """

    def __init__(
        self,
        baseline_dir: Union[str, Path] = "tests/visual/baselines",
        output_dir: Union[str, Path] = "tests/visual/output",
        tolerance: float = 0.01,
    ):
        """
        Initialize the visual testing framework.

        Args:
            baseline_dir: Directory containing baseline images
            output_dir: Directory for test outputs and diffs
            tolerance: Default comparison tolerance (0.0-1.0)
        """
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.tolerance = tolerance

        # Create directories if they don't exist
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Results tracking
        self.test_results: list[VisualTestResult] = []

        # Ensure PIL is available for image operations
        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL (Pillow) is required for visual testing. Install with: pip install Pillow"
            )

    def capture_widget(
        self, widget: QWidget, size: Optional[QSize] = None, wait_time: float = 0.1
    ) -> QImage:
        """
        Capture a screenshot of a widget.

        Args:
            widget: Widget to capture
            size: Optional size to render at
            wait_time: Time to wait before capture for rendering

        Returns:
            QImage of the widget
        """
        # Ensure widget is properly sized and shown
        if size:
            widget.resize(size)

        # Ensure widget is visible and rendered
        widget.show()
        widget.raise_()
        widget.activateWindow()

        # Process events to ensure rendering is complete
        app = QApplication.instance()
        if app:
            app.processEvents()

        # Small delay to ensure rendering is complete
        if wait_time > 0:
            QTimer.singleShot(int(wait_time * 1000), lambda: None)
            if app:
                app.processEvents()
                time.sleep(wait_time)

        # Capture the widget
        if hasattr(widget, "grab"):
            # Modern Qt method
            pixmap = widget.grab()
            image = pixmap.toImage()
        else:
            # Fallback method
            pixmap = QPixmap(widget.size())
            widget.render(pixmap)
            image = pixmap.toImage()

        return image

    def save_image(self, image: QImage, path: Path) -> bool:
        """
        Save a QImage to file.

        Args:
            image: Image to save
            path: File path to save to

        Returns:
            True if saved successfully
        """
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            return image.save(str(path))
        except Exception as e:
            print(f"Error saving image to {path}: {e}")
            return False

    def load_image(self, path: Path) -> Optional[QImage]:
        """
        Load a QImage from file.

        Args:
            path: File path to load from

        Returns:
            QImage if loaded successfully, None otherwise
        """
        try:
            if not path.exists():
                return None

            image = QImage(str(path))
            return image if not image.isNull() else None
        except Exception as e:
            print(f"Error loading image from {path}: {e}")
            return None

    def qimage_to_pil(self, qimage: QImage) -> Optional[Image.Image]:
        """Convert QImage to PIL Image."""
        try:
            # Convert QImage to bytes
            width = qimage.width()
            height = qimage.height()

            # Ensure format is RGB32 or ARGB32
            if qimage.format() != QImage.Format.Format_RGB32:
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB32)

            # Get image data
            bytes_per_line = qimage.bytesPerLine()
            image_data = qimage.constBits()

            # Create PIL image
            pil_image = Image.frombuffer(
                "RGB", (width, height), image_data, "raw", "BGRX", bytes_per_line, 1
            )

            return pil_image
        except Exception as e:
            print(f"Error converting QImage to PIL: {e}")
            return None

    def pil_to_qimage(self, pil_image: Image.Image) -> Optional[QImage]:
        """Convert PIL Image to QImage."""
        try:
            # Convert to RGB if necessary
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            width, height = pil_image.size

            # Convert to QImage
            qimage = QImage(pil_image.tobytes(), width, height, QImage.Format.Format_RGB888)

            # Convert to RGB32 for consistency
            return qimage.convertToFormat(QImage.Format.Format_RGB32)
        except Exception as e:
            print(f"Error converting PIL to QImage: {e}")
            return None

    def compare_images(
        self, actual: QImage, expected: QImage, tolerance: Optional[float] = None
    ) -> tuple[ComparisonResult, float]:
        """
        Compare two images with tolerance.

        Args:
            actual: Actual captured image
            expected: Expected baseline image
            tolerance: Comparison tolerance (uses default if None)

        Returns:
            Tuple of (result, difference_percentage)
        """
        if tolerance is None:
            tolerance = self.tolerance

        try:
            # Check if images have same dimensions
            if actual.size() != expected.size():
                return ComparisonResult.DIFFERENT, 1.0

            # Convert to PIL for comparison
            actual_pil = self.qimage_to_pil(actual)
            expected_pil = self.qimage_to_pil(expected)

            if not actual_pil or not expected_pil:
                return ComparisonResult.ERROR, 0.0

            # Calculate difference
            diff = ImageChops.difference(actual_pil, expected_pil)
            stat = ImageStat.Stat(diff)

            # Calculate difference percentage
            # Use RMS (root mean square) for more accurate comparison
            rms = stat.rms
            max_rms = [255.0] * len(rms)  # Maximum possible difference
            diff_percentage = sum(r / m for r, m in zip(rms, max_rms)) / len(rms)

            # Determine result
            if diff_percentage == 0.0:
                result = ComparisonResult.IDENTICAL
            elif diff_percentage <= tolerance:
                result = ComparisonResult.SIMILAR
            else:
                result = ComparisonResult.DIFFERENT

            return result, diff_percentage

        except Exception as e:
            print(f"Error comparing images: {e}")
            return ComparisonResult.ERROR, 0.0

    def generate_diff(
        self, actual: QImage, expected: QImage, highlight_color: tuple[int, int, int] = (255, 0, 0)
    ) -> Optional[QImage]:
        """
        Generate a visual diff image highlighting differences.

        Args:
            actual: Actual captured image
            expected: Expected baseline image
            highlight_color: RGB color for highlighting differences

        Returns:
            QImage showing differences, None if error
        """
        try:
            # Convert to PIL
            actual_pil = self.qimage_to_pil(actual)
            expected_pil = self.qimage_to_pil(expected)

            if not actual_pil or not expected_pil:
                return None

            # Ensure same size
            if actual_pil.size != expected_pil.size:
                expected_pil = expected_pil.resize(actual_pil.size, Image.Resampling.LANCZOS)

            # Create difference image
            diff = ImageChops.difference(actual_pil, expected_pil)

            # Create a composite showing the diff
            # Start with the actual image
            result = actual_pil.copy().convert("RGB")

            # Highlight differences
            diff_data = diff.getdata()
            result_data = result.getdata()

            new_data = []
            threshold = 10  # Threshold for considering pixels different

            for _i, (diff_pixel, orig_pixel) in enumerate(zip(diff_data, result_data)):
                # Check if pixel is significantly different
                if isinstance(diff_pixel, tuple):
                    diff_intensity = sum(diff_pixel) / len(diff_pixel)
                else:
                    diff_intensity = diff_pixel

                if diff_intensity > threshold:
                    # Highlight with the specified color
                    new_data.append(highlight_color)
                else:
                    # Keep original pixel
                    new_data.append(orig_pixel)

            result.putdata(new_data)

            # Convert back to QImage
            return self.pil_to_qimage(result)

        except Exception as e:
            print(f"Error generating diff image: {e}")
            return None

    def run_visual_test(
        self,
        test_name: str,
        widget: QWidget,
        tolerance: Optional[float] = None,
        size: Optional[QSize] = None,
        update_baseline: bool = False,
    ) -> VisualTestResult:
        """
        Run a complete visual test.

        Args:
            test_name: Name of the test
            widget: Widget to test
            tolerance: Comparison tolerance (uses default if None)
            size: Size to render widget at
            update_baseline: Whether to update baseline instead of comparing

        Returns:
            VisualTestResult with test outcome
        """
        baseline_path = self.baseline_dir / f"{test_name}.png"
        actual_path = self.output_dir / f"{test_name}_actual.png"
        diff_path = self.output_dir / f"{test_name}_diff.png"

        try:
            # Capture current state
            actual_image = self.capture_widget(widget, size)

            # Save actual image
            self.save_image(actual_image, actual_path)

            if update_baseline or not baseline_path.exists():
                # Update or create baseline
                self.save_image(actual_image, baseline_path)

                result = VisualTestResult(
                    name=test_name,
                    result=ComparisonResult.IDENTICAL,
                    difference_percentage=0.0,
                    baseline_path=baseline_path,
                    actual_path=actual_path,
                )
            else:
                # Load baseline and compare
                baseline_image = self.load_image(baseline_path)

                if not baseline_image:
                    result = VisualTestResult(
                        name=test_name,
                        result=ComparisonResult.ERROR,
                        difference_percentage=0.0,
                        error_message="Could not load baseline image",
                        actual_path=actual_path,
                    )
                else:
                    # Compare images
                    comparison_result, diff_percentage = self.compare_images(
                        actual_image, baseline_image, tolerance
                    )

                    # Generate diff if different
                    if comparison_result in (ComparisonResult.DIFFERENT, ComparisonResult.SIMILAR):
                        diff_image = self.generate_diff(actual_image, baseline_image)
                        if diff_image:
                            self.save_image(diff_image, diff_path)

                    result = VisualTestResult(
                        name=test_name,
                        result=comparison_result,
                        difference_percentage=diff_percentage,
                        baseline_path=baseline_path,
                        actual_path=actual_path,
                        diff_path=(
                            diff_path if comparison_result != ComparisonResult.IDENTICAL else None
                        ),
                    )

            self.test_results.append(result)
            return result

        except Exception as e:
            error_result = VisualTestResult(
                name=test_name,
                result=ComparisonResult.ERROR,
                difference_percentage=0.0,
                error_message=str(e),
                actual_path=actual_path,
            )
            self.test_results.append(error_result)
            return error_result

    def test_themed_widget(
        self,
        widget_class: type = ThemedWidget,
        theme_name: str = "default",
        test_name: Optional[str] = None,
        size: QSize = QSize(200, 100),
    ) -> VisualTestResult:
        """
        Test a themed widget with a specific theme.

        Args:
            widget_class: Widget class to test
            theme_name: Theme to apply
            test_name: Test name (auto-generated if None)
            size: Widget size

        Returns:
            VisualTestResult
        """
        if not test_name:
            test_name = f"{widget_class.__name__}_{theme_name}"

        # Create widget
        widget = widget_class()

        # Apply theme if application exists
        app = QApplication.instance()
        if hasattr(app, "set_theme"):
            try:
                app.set_theme(theme_name)
            except:
                pass  # Theme might not exist

        # Run test
        return self.run_visual_test(test_name, widget, size=size)

    def batch_test_themes(
        self,
        widget_class: type = ThemedWidget,
        theme_names: list[str] = None,
        size: QSize = QSize(200, 100),
    ) -> list[VisualTestResult]:
        """
        Test a widget class with multiple themes.

        Args:
            widget_class: Widget class to test
            theme_names: List of theme names to test
            size: Widget size

        Returns:
            List of VisualTestResult
        """
        if not theme_names:
            theme_names = ["default", "dark", "light"]

        results = []
        for theme_name in theme_names:
            result = self.test_themed_widget(widget_class, theme_name, size=size)
            results.append(result)

        return results

    def generate_test_report(self) -> dict[str, Any]:
        """
        Generate a comprehensive test report.

        Returns:
            Dictionary with test results and statistics
        """
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {"total": 0, "results": []}

        # Count results by type
        identical = sum(1 for r in self.test_results if r.result == ComparisonResult.IDENTICAL)
        similar = sum(1 for r in self.test_results if r.result == ComparisonResult.SIMILAR)
        different = sum(1 for r in self.test_results if r.result == ComparisonResult.DIFFERENT)
        errors = sum(1 for r in self.test_results if r.result == ComparisonResult.ERROR)

        # Calculate average difference
        valid_diffs = [
            r.difference_percentage for r in self.test_results if r.result != ComparisonResult.ERROR
        ]
        avg_diff = sum(valid_diffs) / len(valid_diffs) if valid_diffs else 0.0

        return {
            "total": total_tests,
            "identical": identical,
            "similar": similar,
            "different": different,
            "errors": errors,
            "average_difference": avg_diff,
            "success_rate": (identical + similar) / total_tests,
            "results": [
                {
                    "name": r.name,
                    "result": r.result.value,
                    "difference": r.difference_percentage,
                    "error": r.error_message,
                    "timestamp": r.timestamp,
                }
                for r in self.test_results
            ],
        }

    def cleanup(self):
        """Clean up temporary files and results."""
        self.test_results.clear()

        # Optionally clean up output directory
        # (be careful not to delete important files)
        pass


if __name__ == "__main__":
    # Example usage
    from PySide6.QtWidgets import QApplication

    from vfwidgets_theme import ThemedApplication, ThemedWidget

    app = ThemedApplication()
    framework = VisualTestFramework()

    # Test basic themed widget
    result = framework.test_themed_widget()

    print(f"Test result: {result.result.value}")
    print(f"Difference: {result.difference_percentage:.2%}")

    # Generate report
    report = framework.generate_test_report()
    print(f"Visual tests completed: {report['success_rate']:.1%} success rate")
