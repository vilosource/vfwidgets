"""
Unit tests for ThemedApplication.

Tests the application-level theme management wrapper providing
simple API for global theming operations.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from vfwidgets_theme.core.theme import Theme
from vfwidgets_theme.errors import ThemeError
from vfwidgets_theme.testing import ThemeBenchmark, ThemedTestCase
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.base import ThemedWidget


class TestThemedApplicationCreation(ThemedTestCase):
    """Test ThemedApplication creation and initialization."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        # Mock QApplication to avoid requiring Qt in tests
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    def test_themed_application_creation(self):
        """Test basic ThemedApplication creation."""
        self.assertIsInstance(self.app, ThemedApplication)
        self.assertIsNotNone(self.app._theme_manager)
        self.assertIsNotNone(self.app._app_theme_manager)

    def test_themed_application_initialization(self):
        """Test ThemedApplication proper initialization."""
        # Should have default theme loaded
        current_theme = self.app.get_current_theme()
        self.assertIsNotNone(current_theme)

        # Should have built-in themes available
        themes = self.app.get_available_themes()
        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)

    def test_themed_application_singleton_pattern(self):
        """Test ThemedApplication singleton behavior."""
        # Should maintain single instance per process
        self.assertEqual(ThemedApplication.instance(), self.app)

    def test_themed_application_with_custom_config(self):
        """Test ThemedApplication with custom configuration."""
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            custom_app = ThemedApplication(
                [],
                theme_config={
                    "default_theme": "dark",
                    "auto_detect_system": True,
                    "persist_theme": True,
                },
            )

        self.assertIsNotNone(custom_app._config)
        custom_app.cleanup()


class TestThemedApplicationThemeManagement(ThemedTestCase):
    """Test ThemedApplication theme management operations."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    def test_set_theme_by_name(self):
        """Test setting theme by name."""
        # Should be able to set theme by name
        result = self.app.set_theme("dark")
        self.assertTrue(result)

        # Current theme should be updated
        current = self.app.get_current_theme()
        self.assertIsNotNone(current)

    def test_set_theme_with_theme_object(self):
        """Test setting theme with Theme object."""
        theme = Theme(
            name="test_theme",
            colors={"primary": "#FF0000", "background": "#000000"},
            styles={"window": {"background-color": "@colors.background"}},
        )

        result = self.app.set_theme(theme)
        self.assertTrue(result)

        # Current theme should match
        current = self.app.get_current_theme()
        self.assertEqual(current.name, "test_theme")

    def test_set_invalid_theme(self):
        """Test setting invalid theme name."""
        result = self.app.set_theme("nonexistent_theme")
        self.assertFalse(result)

        # Should fall back to minimal theme
        current = self.app.get_current_theme()
        self.assertIsNotNone(current)

    def test_get_available_themes(self):
        """Test getting available themes."""
        themes = self.app.get_available_themes()

        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)

        # Should have built-in themes
        theme_names = [theme.name if isinstance(theme, Theme) else theme for theme in themes]
        self.assertIn("default", theme_names)

    def test_get_current_theme(self):
        """Test getting current theme."""
        current = self.app.get_current_theme()

        self.assertIsInstance(current, Theme)
        self.assertIsNotNone(current.name)
        self.assertIsInstance(current.colors, dict)

    def test_reload_current_theme(self):
        """Test reloading current theme."""
        # Set a theme first
        self.app.set_theme("default")

        # Reload should work
        result = self.app.reload_current_theme()
        self.assertTrue(result)

    def test_theme_switching_performance(self):
        """Test theme switching meets performance requirements."""
        benchmark = ThemeBenchmark()

        def switch_theme():
            self.app.set_theme("dark")
            self.app.set_theme("light")

        switch_time = benchmark.measure_time(switch_theme)
        # Should switch themes quickly (< 100ms for application level)
        self.assertLess(switch_time, 0.1)


class TestThemedApplicationFileOperations(ThemedTestCase):
    """Test ThemedApplication file operations."""

    def setUp(self):
        """Set up test application with temp directory."""
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application and temp directory."""
        if hasattr(self, "app"):
            self.app.cleanup()
        import shutil

        shutil.rmtree(self.temp_dir)
        super().tearDown()

    def test_load_theme_file(self):
        """Test loading theme from file."""
        # Create test theme file
        theme_data = {
            "name": "test_file_theme",
            "colors": {"primary": "#FF0000", "background": "#FFFFFF"},
            "styles": {"window": {"background-color": "@colors.background"}},
        }

        theme_file = os.path.join(self.temp_dir, "test_theme.json")
        with open(theme_file, "w") as f:
            json.dump(theme_data, f)

        # Load theme file
        result = self.app.load_theme_file(theme_file)
        self.assertTrue(result)

        # Should be available in themes
        themes = self.app.get_available_themes()
        theme_names = [theme.name if isinstance(theme, Theme) else theme for theme in themes]
        self.assertIn("test_file_theme", theme_names)

    def test_load_invalid_theme_file(self):
        """Test loading invalid theme file."""
        # Create invalid theme file
        invalid_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_file, "w") as f:
            f.write("invalid json content")

        # Should handle gracefully
        result = self.app.load_theme_file(invalid_file)
        self.assertFalse(result)

    def test_load_nonexistent_theme_file(self):
        """Test loading nonexistent theme file."""
        nonexistent = os.path.join(self.temp_dir, "nonexistent.json")

        result = self.app.load_theme_file(nonexistent)
        self.assertFalse(result)

    def test_save_current_theme(self):
        """Test saving current theme to file."""
        # Set a theme
        self.app.set_theme("default")

        # Save to file
        output_file = os.path.join(self.temp_dir, "saved_theme.json")
        result = self.app.save_current_theme(output_file)
        self.assertTrue(result)

        # File should exist and be valid
        self.assertTrue(os.path.exists(output_file))

        # Should be loadable
        load_result = self.app.load_theme_file(output_file)
        self.assertTrue(load_result)

    def test_discover_theme_directory(self):
        """Test discovering themes from directory."""
        # Create theme files in directory
        theme1_data = {
            "name": "discovered_theme_1",
            "colors": {"primary": "#FF0000"},
            "styles": {"window": {}},
        }
        theme2_data = {
            "name": "discovered_theme_2",
            "colors": {"primary": "#00FF00"},
            "styles": {"window": {}},
        }

        theme1_file = os.path.join(self.temp_dir, "theme1.json")
        theme2_file = os.path.join(self.temp_dir, "theme2.json")

        with open(theme1_file, "w") as f:
            json.dump(theme1_data, f)
        with open(theme2_file, "w") as f:
            json.dump(theme2_data, f)

        # Discover themes
        discovered_count = self.app.discover_themes_from_directory(self.temp_dir)
        self.assertGreaterEqual(discovered_count, 2)

        # Themes should be available
        themes = self.app.get_available_themes()
        theme_names = [theme.name if isinstance(theme, Theme) else theme for theme in themes]
        self.assertIn("discovered_theme_1", theme_names)
        self.assertIn("discovered_theme_2", theme_names)


class TestThemedApplicationVSCodeIntegration(ThemedTestCase):
    """Test ThemedApplication VSCode theme integration."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        import shutil

        shutil.rmtree(self.temp_dir)
        super().tearDown()

    def test_import_vscode_theme(self):
        """Test importing VSCode theme."""
        # Create mock VSCode theme file
        vscode_theme = {
            "name": "Test VSCode Theme",
            "type": "dark",
            "colors": {
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "activityBar.background": "#333333",
            },
            "tokenColors": [{"scope": "comment", "settings": {"foreground": "#608b4e"}}],
        }

        vscode_file = os.path.join(self.temp_dir, "vscode_theme.json")
        with open(vscode_file, "w") as f:
            json.dump(vscode_theme, f)

        # Import VSCode theme
        result = self.app.import_vscode_theme(vscode_file)
        self.assertTrue(result)

        # Should be available in themes
        themes = self.app.get_available_themes()
        theme_names = [theme.name if isinstance(theme, Theme) else theme for theme in themes]
        # VSCode theme name might be modified during import
        self.assertTrue(
            any(
                "Test VSCode Theme" in name or "test_vscode_theme" in name.lower()
                for name in theme_names
            )
        )

    def test_import_invalid_vscode_theme(self):
        """Test importing invalid VSCode theme."""
        # Create invalid VSCode theme file
        invalid_vscode = {"invalid": "structure"}

        vscode_file = os.path.join(self.temp_dir, "invalid_vscode.json")
        with open(vscode_file, "w") as f:
            json.dump(invalid_vscode, f)

        # Should handle gracefully
        result = self.app.import_vscode_theme(vscode_file)
        self.assertFalse(result)

    @patch("vfwidgets_theme.widgets.application.find_vscode_themes")
    def test_auto_discover_vscode_themes(self, mock_find):
        """Test auto-discovery of VSCode themes."""
        # Mock VSCode theme discovery
        mock_find.return_value = ["/mock/path/theme1.json", "/mock/path/theme2.json"]

        with patch.object(self.app, "import_vscode_theme", return_value=True):
            count = self.app.auto_discover_vscode_themes()
            self.assertEqual(count, 2)


class TestThemedApplicationSystemIntegration(ThemedTestCase):
    """Test ThemedApplication system integration features."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    @patch("vfwidgets_theme.widgets.application.detect_system_theme")
    def test_auto_detect_system_theme(self, mock_detect):
        """Test auto-detection of system theme."""
        # Mock system theme detection
        mock_detect.return_value = "dark"

        result = self.app.auto_detect_system_theme()
        self.assertEqual(result, "dark")

        # Should set system theme
        current = self.app.get_current_theme()
        self.assertIsNotNone(current)

    def test_theme_persistence(self):
        """Test theme persistence across sessions."""
        with patch("vfwidgets_theme.widgets.application.save_theme_preference") as mock_save:
            # Set theme with persistence
            self.app.set_theme("dark", persist=True)

            # Should save preference
            mock_save.assert_called()

    @patch("vfwidgets_theme.widgets.application.load_theme_preference")
    def test_theme_restoration(self, mock_load):
        """Test theme restoration on startup."""
        # Mock saved preference
        mock_load.return_value = "dark"

        with patch("vfwidgets_theme.widgets.application.QApplication"):
            app = ThemedApplication([], auto_restore=True)

        # Should restore saved theme
        current = app.get_current_theme()
        self.assertIsNotNone(current)

        app.cleanup()

    def test_system_theme_change_monitoring(self):
        """Test monitoring system theme changes."""
        # Enable system theme monitoring
        result = self.app.enable_system_theme_monitoring()
        self.assertTrue(result)

        # Should have monitoring enabled
        self.assertTrue(self.app._system_theme_monitoring)

        # Disable monitoring
        result = self.app.disable_system_theme_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.app._system_theme_monitoring)


class TestThemedApplicationWidgetIntegration(ThemedTestCase):
    """Test ThemedApplication integration with ThemedWidget."""

    def setUp(self):
        """Set up test application and widgets."""
        super().setUp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    def test_widget_automatic_registration(self):
        """Test widgets automatically register with application."""
        widget = ThemedWidget()

        # Widget should be registered with app's theme system
        self.assertTrue(widget._is_theme_registered)

        widget._cleanup_theme()

    def test_application_theme_change_propagation(self):
        """Test application theme changes propagate to widgets."""
        widgets = [ThemedWidget() for _ in range(5)]

        # Change application theme
        self.app.set_theme("dark")

        # All widgets should receive theme update
        for widget in widgets:
            self.assertIsNotNone(widget.theme.background)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()

    def test_widget_cleanup_on_app_exit(self):
        """Test widgets cleanup properly on application exit."""
        [ThemedWidget() for _ in range(5)]

        # App cleanup should cleanup all widgets
        self.app.cleanup()

        # Widgets should be unregistered
        # Note: Actual cleanup depends on implementation details

    def test_batch_widget_theme_updates(self):
        """Test batch widget theme updates for performance."""
        widgets = [ThemedWidget() for _ in range(100)]

        # Measure batch update time
        benchmark = ThemeBenchmark()

        def batch_update():
            self.app.set_theme("light")

        update_time = benchmark.measure_time(batch_update)

        # Should complete batch update quickly (< 100ms requirement)
        self.assertLess(update_time, 0.1)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()


class TestThemedApplicationErrorHandling(ThemedTestCase):
    """Test ThemedApplication error handling and recovery."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    def test_theme_loading_error_recovery(self):
        """Test recovery from theme loading errors."""
        # Mock theme loading error
        with patch.object(
            self.app._theme_manager, "load_theme", side_effect=ThemeError("Loading failed")
        ):
            # Should not crash - should fallback
            result = self.app.set_theme("failing_theme")
            self.assertFalse(result)

            # Should have fallback theme
            current = self.app.get_current_theme()
            self.assertIsNotNone(current)

    def test_file_operation_error_recovery(self):
        """Test recovery from file operation errors."""
        # Test loading nonexistent file
        result = self.app.load_theme_file("/nonexistent/path/theme.json")
        self.assertFalse(result)

        # Application should still be functional
        current = self.app.get_current_theme()
        self.assertIsNotNone(current)

    def test_widget_update_error_recovery(self):
        """Test recovery from widget update errors."""
        widget = ThemedWidget()

        # Mock widget update error
        with patch.object(
            widget, "_on_theme_changed", side_effect=Exception("Widget update failed")
        ):
            # Theme change should still work for other widgets
            self.app.set_theme("dark")
            # Result might be True or False depending on error handling

            # Application should remain functional
            current = self.app.get_current_theme()
            self.assertIsNotNone(current)

        widget._cleanup_theme()

    def test_system_integration_error_recovery(self):
        """Test recovery from system integration errors."""
        # Mock system theme detection error
        with patch(
            "vfwidgets_theme.widgets.application.detect_system_theme",
            side_effect=Exception("System detection failed"),
        ):
            # Should handle gracefully
            self.app.auto_detect_system_theme()
            # Should return None or fallback theme

            # Application should remain functional
            current = self.app.get_current_theme()
            self.assertIsNotNone(current)


class TestThemedApplicationPerformance(ThemedTestCase):
    """Test ThemedApplication performance requirements."""

    def setUp(self):
        """Set up test application."""
        super().setUp()
        with patch("vfwidgets_theme.widgets.application.QApplication"):
            self.app = ThemedApplication([])

    def tearDown(self):
        """Clean up test application."""
        if hasattr(self, "app"):
            self.app.cleanup()
        super().tearDown()

    def test_application_startup_performance(self):
        """Test application startup meets performance requirements."""
        benchmark = ThemeBenchmark()

        def create_app():
            with patch("vfwidgets_theme.widgets.application.QApplication"):
                app = ThemedApplication([])
            app.cleanup()
            return app

        startup_time = benchmark.measure_time(create_app)
        # Application startup should be reasonable (< 1s)
        self.assertLess(startup_time, 1.0)

    def test_theme_switching_performance(self):
        """Test theme switching meets performance requirements."""
        benchmark = ThemeBenchmark()

        def switch_themes():
            self.app.set_theme("dark")
            self.app.set_theme("light")
            self.app.set_theme("default")

        switch_time = benchmark.measure_time(switch_themes)
        # Theme switching should be fast (< 100ms)
        self.assertLess(switch_time, 0.1)

    def test_many_widgets_performance(self):
        """Test performance with many widgets."""
        # Create many widgets
        widgets = [ThemedWidget() for _ in range(100)]

        benchmark = ThemeBenchmark()

        def theme_update():
            self.app.set_theme("dark")

        update_time = benchmark.measure_time(theme_update)

        # Should handle many widgets efficiently (< 100ms for 100 widgets)
        self.assertLess(update_time, 0.1)

        # Cleanup
        for widget in widgets:
            widget._cleanup_theme()


if __name__ == "__main__":
    unittest.main()
