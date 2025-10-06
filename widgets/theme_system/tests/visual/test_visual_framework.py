#!/usr/bin/env python3
"""
Tests for Visual Testing Framework
"""

import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from vfwidgets_theme import ThemedApplication, ThemedWidget

from .comparison import ImageComparator
from .framework import ComparisonResult, VisualTestFramework


class TestVisualFramework:
    """Test the visual testing framework."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def visual_framework(self, temp_dir):
        """Create visual framework with temporary directories."""
        baseline_dir = temp_dir / "baselines"
        output_dir = temp_dir / "output"

        return VisualTestFramework(baseline_dir=baseline_dir, output_dir=output_dir, tolerance=0.01)

    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        existing_app = QApplication.instance()
        if existing_app:
            yield existing_app
        else:
            app = ThemedApplication()
            yield app

    def test_framework_initialization(self, visual_framework):
        """Test framework initializes correctly."""
        assert visual_framework.baseline_dir.exists()
        assert visual_framework.output_dir.exists()
        assert visual_framework.tolerance == 0.01
        assert len(visual_framework.test_results) == 0

    def test_widget_capture(self, visual_framework, app):
        """Test widget screenshot capture."""
        # Create a simple widget
        widget = QLabel("Test Label")
        widget.resize(100, 50)

        # Capture screenshot
        image = visual_framework.capture_widget(widget)

        assert image is not None
        assert not image.isNull()
        assert image.width() > 0
        assert image.height() > 0

    def test_image_save_load(self, visual_framework):
        """Test image save and load functionality."""
        # Create a simple widget and capture it
        widget = QLabel("Save Test")
        widget.resize(100, 50)

        image = visual_framework.capture_widget(widget)

        # Save image
        test_path = visual_framework.output_dir / "test_image.png"
        success = visual_framework.save_image(image, test_path)

        assert success
        assert test_path.exists()

        # Load image
        loaded_image = visual_framework.load_image(test_path)
        assert loaded_image is not None
        assert not loaded_image.isNull()

    def test_visual_test_new_baseline(self, visual_framework, app):
        """Test visual test with new baseline creation."""
        widget = QLabel("Baseline Test")
        widget.resize(150, 75)

        result = visual_framework.run_visual_test("test_baseline", widget, update_baseline=True)

        assert result.result == ComparisonResult.IDENTICAL
        assert result.difference_percentage == 0.0
        assert result.baseline_path.exists()
        assert result.actual_path.exists()

    def test_visual_test_comparison(self, visual_framework, app):
        """Test visual test with baseline comparison."""
        widget = QLabel("Comparison Test")
        widget.resize(150, 75)

        # Create baseline
        result1 = visual_framework.run_visual_test("test_comparison", widget, update_baseline=True)

        # Test against same widget (should be identical)
        result2 = visual_framework.run_visual_test("test_comparison", widget)

        assert result2.result == ComparisonResult.IDENTICAL
        assert result2.difference_percentage == 0.0

    def test_themed_widget_test(self, visual_framework, app):
        """Test themed widget visual testing."""
        result = visual_framework.test_themed_widget(
            widget_class=ThemedWidget, theme_name="default", size=QSize(200, 100)
        )

        assert result is not None
        assert result.name == "ThemedWidget_default"

    def test_batch_theme_testing(self, visual_framework, app):
        """Test batch testing with multiple themes."""
        results = visual_framework.batch_test_themes(
            widget_class=ThemedWidget, theme_names=["default", "dark"], size=QSize(150, 80)
        )

        assert len(results) == 2
        assert results[0].name == "ThemedWidget_default"
        assert results[1].name == "ThemedWidget_dark"

    def test_test_report_generation(self, visual_framework, app):
        """Test test report generation."""
        # Run a few tests
        widget = QLabel("Report Test")
        visual_framework.run_visual_test("test1", widget, update_baseline=True)
        visual_framework.run_visual_test("test2", widget, update_baseline=True)

        report = visual_framework.generate_test_report()

        assert report["total"] == 2
        assert report["identical"] == 2
        assert report["success_rate"] == 1.0
        assert len(report["results"]) == 2


class TestImageComparator:
    """Test image comparison utilities."""

    @pytest.fixture
    def comparator(self):
        """Create image comparator."""
        return ImageComparator()

    @pytest.fixture
    def test_images(self):
        """Create test images."""
        try:
            from PIL import Image

            # Create identical images
            img1 = Image.new("RGB", (100, 100), color="red")
            img2 = Image.new("RGB", (100, 100), color="red")

            # Create different image
            img3 = Image.new("RGB", (100, 100), color="blue")

            return img1, img2, img3
        except ImportError:
            pytest.skip("PIL not available")

    def test_identical_images(self, comparator, test_images):
        """Test comparison of identical images."""
        img1, img2, _ = test_images

        diff = comparator.compare_rms(img1, img2)
        assert diff == 0.0

        assert comparator.is_similar(img1, img2, tolerance=0.01)

    def test_different_images(self, comparator, test_images):
        """Test comparison of different images."""
        img1, _, img3 = test_images

        diff = comparator.compare_rms(img1, img3)
        assert diff > 0.5  # Should be quite different

        assert not comparator.is_similar(img1, img3, tolerance=0.01)

    def test_multi_metric_comparison(self, comparator, test_images):
        """Test multi-metric comparison."""
        img1, _, img3 = test_images

        results = comparator.multi_metric_comparison(img1, img3)

        assert "rms" in results
        assert "histogram" in results
        assert "ssim" in results
        assert "perceptual" in results

        # All metrics should show significant difference
        for metric, value in results.items():
            assert value > 0.1  # Significantly different


def test_visual_framework_integration():
    """Integration test for visual framework."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create framework
        framework = VisualTestFramework(
            baseline_dir=Path(temp_dir) / "baselines", output_dir=Path(temp_dir) / "output"
        )

        # Create test widget
        app = QApplication.instance()
        if not app:
            app = ThemedApplication()

        widget = QPushButton("Integration Test")
        widget.resize(120, 40)

        # Run visual test
        result = framework.run_visual_test("integration_test", widget, update_baseline=True)

        assert result.result == ComparisonResult.IDENTICAL
        assert result.baseline_path.exists()

        # Generate report
        report = framework.generate_test_report()
        assert report["total"] == 1
        assert report["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
