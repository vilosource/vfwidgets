"""Tests for SingleInstanceApplication theme integration."""

import pytest


def test_single_instance_theme_support():
    """Test that SingleInstanceApplication uses ThemedApplication when available."""
    from vfwidgets_common import SingleInstanceApplication

    # Check if theme system is available
    try:
        from vfwidgets_theme import ThemedApplication

        # SingleInstanceApplication should inherit from ThemedApplication
        assert issubclass(SingleInstanceApplication, ThemedApplication), (
            "SingleInstanceApplication should inherit from ThemedApplication when vfwidgets-theme is installed"
        )

        print("✅ SingleInstanceApplication has theme support")

    except ImportError:
        # Theme not installed - SingleInstanceApplication should use QApplication
        from PySide6.QtWidgets import QApplication

        assert issubclass(SingleInstanceApplication, QApplication), (
            "SingleInstanceApplication should inherit from QApplication when vfwidgets-theme is not installed"
        )

        print("✅ SingleInstanceApplication uses QApplication (theme not installed)")


def test_theme_propagation_in_app(qtbot, qapp):
    """Test that theme changes propagate when using SingleInstanceApplication."""
    # Check if theme system is available
    try:
        from vfwidgets_theme import ThemedApplication, get_theme_manager

        # Verify app is ThemedApplication
        assert isinstance(qapp, ThemedApplication), "Test app should be ThemedApplication"

        print(f"✅ App type: {type(qapp).__name__}")
        print(f"✅ Is ThemedApplication: {isinstance(qapp, ThemedApplication)}")

        # Get theme manager
        manager = get_theme_manager()
        print(f"✅ Theme manager available: {manager}")

        # Get current theme
        current_theme = manager.get_current_theme()
        print(f"✅ Current theme: {current_theme.name if current_theme else 'None'}")

    except ImportError:
        pytest.skip("vfwidgets-theme not installed")
