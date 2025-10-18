"""
Test fixtures for Theme Overlay System testing.

This module provides pytest fixtures specifically for testing the overlay
system functionality including OverrideRegistry, ThemeManager overlay methods,
and VFThemedApplication.

These fixtures extend the base theme system fixtures and focus on:
- Override registry operations
- Layered override resolution
- Theme manager integration
- User/app override persistence
- Widget notification on override changes
"""


import pytest
from PySide6.QtCore import QSettings

# ============================================================================
# Override Data Fixtures
# ============================================================================


@pytest.fixture
def sample_app_overrides() -> dict[str, str]:
    """Sample application-level overrides for testing.

    Returns a dict of token -> color overrides that an app
    might use for branding purposes.
    """
    return {
        "editor.background": "#1e1e2e",  # App branded background
        "tab.activeBackground": "#89b4fa",  # App branded active tab
        "button.background": "#313244",  # App branded button
    }


@pytest.fixture
def sample_user_overrides() -> dict[str, str]:
    """Sample user-level overrides for testing.

    Returns a dict of token -> color overrides that a user
    might customize for personal preferences.
    """
    return {
        "editor.background": "#2d2d2d",  # User custom background
        "statusBar.background": "#3e3e3e",  # User custom status bar
    }


@pytest.fixture
def bulk_overrides() -> dict[str, str]:
    """Large set of overrides for bulk operation testing.

    Returns 50 overrides to test performance of bulk operations.
    """
    return {f"token.test{i:03d}": f"#color{i:03d}" for i in range(50)}


@pytest.fixture
def invalid_color_overrides() -> dict[str, str]:
    """Invalid color overrides for validation testing."""
    return {
        "editor.background": "not-a-color",
        "tab.activeBackground": "#gggggg",  # Invalid hex
        "button.background": "rgb(999, 999, 999)",  # Invalid RGB
    }


@pytest.fixture
def edge_case_tokens() -> dict[str, str]:
    """Edge case token names for validation testing."""
    return {
        "": "#ffffff",  # Empty token
        "a" * 300: "#000000",  # Too long (>255 chars)
        "123invalid": "#ffffff",  # Starts with number
        "has space": "#ffffff",  # Contains space
        "has-dash": "#ffffff",  # Contains dash (invalid)
    }


# ============================================================================
# QSettings Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_qsettings(tmp_path, monkeypatch):
    """Mock QSettings that uses temporary file storage.

    Provides isolated QSettings for each test without polluting
    user's actual settings.
    """
    # Create temporary settings file
    settings_file = tmp_path / "test_settings.ini"

    # Monkeypatch QSettings to use temp file
    original_qsettings_init = QSettings.__init__

    def mock_init(self, *args, **kwargs):
        # Redirect to temp file regardless of arguments
        original_qsettings_init(self, str(settings_file), QSettings.Format.IniFormat)

    monkeypatch.setattr(QSettings, "__init__", mock_init)

    yield str(settings_file)

    # Cleanup
    if settings_file.exists():
        settings_file.unlink()


@pytest.fixture
def qsettings_with_overrides(mock_qsettings, sample_user_overrides):
    """QSettings pre-populated with user overrides.

    Returns a QSettings instance that already contains
    user override data for testing load operations.
    """
    settings = QSettings()

    # Write sample overrides
    settings.beginGroup("theme_overrides")
    for token, color in sample_user_overrides.items():
        settings.setValue(token, color)
    settings.endGroup()
    settings.sync()

    return settings


# ============================================================================
# Theme Manager Fixtures
# ============================================================================


@pytest.fixture
def clean_theme_manager():
    """Clean ThemeManager instance for testing.

    Ensures ThemeManager starts in a clean state with no
    overrides or cached data.
    """
    from vfwidgets_theme.core.theme_manager import ThemeManager

    # Get singleton instance
    manager = ThemeManager.instance()

    # Clear any existing overrides (will be implemented)
    # For now, just return the manager

    yield manager

    # Cleanup after test
    # Clear overrides again
    pass


@pytest.fixture
def theme_manager_with_app_overrides(clean_theme_manager, sample_app_overrides):
    """ThemeManager with app-level overrides pre-configured."""
    manager = clean_theme_manager

    # Set app overrides (will implement set_app_overrides_bulk in Phase 2)
    # For now, return the manager

    return manager


@pytest.fixture
def theme_manager_with_all_overrides(
    clean_theme_manager,
    sample_app_overrides,
    sample_user_overrides
):
    """ThemeManager with both app and user overrides configured.

    Useful for testing priority resolution where user overrides
    should win over app overrides.
    """
    manager = clean_theme_manager

    # Set both layers of overrides
    # Will implement in Phase 2

    return manager


# ============================================================================
# Color Validation Fixtures
# ============================================================================


@pytest.fixture
def valid_colors() -> list[str]:
    """List of valid color formats for testing validation.

    Note: These are colors that QColor.isValidColor() accepts.
    QColor is stricter than CSS and doesn't accept all formats.
    """
    return [
        "#ffffff",  # 6-digit hex
        "#fff",  # 3-digit hex
        "#ffffff00",  # 8-digit hex with alpha
        "red",  # Named color
        "green",
        "blue",
        "white",
        "black",
    ]


@pytest.fixture
def invalid_colors() -> list[str]:
    """List of invalid color formats for testing validation."""
    return [
        "not-a-color",
        "#gggggg",  # Invalid hex
        "#12",  # Too short
        "rgb(999, 999, 999)",  # Out of range
        "rgba(255, 255, 255)",  # Missing alpha
        "",  # Empty
        None,  # None (will be tested separately)
    ]


@pytest.fixture
def color_validator():
    """Color validation helper using QColor."""
    from PySide6.QtGui import QColor

    def validate(color: str) -> bool:
        """Validate color string using Qt's QColor validation."""
        return QColor.isValidColor(color)

    return validate


# ============================================================================
# Threading Test Fixtures
# ============================================================================


@pytest.fixture
def thread_pool():
    """Thread pool for concurrent testing.

    Provides a controlled way to test thread safety
    with predictable thread count.
    """
    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=10)

    yield executor

    executor.shutdown(wait=True)


@pytest.fixture
def concurrent_operation_helper(thread_pool):
    """Helper for running concurrent operations in tests.

    Simplifies testing of thread-safe operations by providing
    a clean interface for parallel execution.
    """
    def run_concurrent(func, args_list, expected_success=True):
        """Run function concurrently with different arguments.

        Args:
            func: Function to execute
            args_list: List of argument tuples for each call
            expected_success: Whether operations should succeed

        Returns:
            List of results from each call
        """
        futures = [thread_pool.submit(func, *args) for args in args_list]
        results = [f.result() for f in futures]

        if expected_success:
            assert all(r is not None for r in results), "Some operations failed"

        return results

    return run_concurrent


# ============================================================================
# Widget Notification Test Fixtures
# ============================================================================


@pytest.fixture
def notification_tracker():
    """Tracker for theme change notifications.

    Helps verify that widgets are properly notified when
    overrides change.
    """
    class NotificationTracker:
        def __init__(self):
            self.notifications = []
            self.call_count = 0

        def on_notification(self, *args, **kwargs):
            """Callback for theme notifications."""
            self.call_count += 1
            self.notifications.append({
                "args": args,
                "kwargs": kwargs,
                "timestamp": None,  # Could add timing if needed
            })

        def reset(self):
            """Reset tracking state."""
            self.notifications.clear()
            self.call_count = 0

        def assert_notified(self, min_count=1):
            """Assert that notifications occurred."""
            assert self.call_count >= min_count, (
                f"Expected at least {min_count} notifications, got {self.call_count}"
            )

        def assert_not_notified(self):
            """Assert that no notifications occurred."""
            assert self.call_count == 0, (
                f"Expected no notifications, got {self.call_count}"
            )

    return NotificationTracker()


# ============================================================================
# Performance Test Fixtures (Overlay-Specific)
# ============================================================================


@pytest.fixture
def override_performance_benchmark():
    """Benchmark fixture for override operations.

    Measures performance of override resolution, setting,
    and bulk operations.
    """
    import time

    def benchmark(operation, iterations=1000):
        """Benchmark an override operation.

        Args:
            operation: Callable to benchmark
            iterations: Number of times to execute

        Returns:
            Dict with timing statistics
        """
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            operation()
            end = time.perf_counter()
            times.append(end - start)

        return {
            "total_time": sum(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "iterations": iterations,
        }

    return benchmark


# ============================================================================
# Integration Test Fixtures
# ============================================================================


@pytest.fixture
def integration_test_app(qapp):
    """Full application setup for integration testing.

    Provides a complete application with ThemeManager,
    multiple widgets, and theme loaded for end-to-end testing.
    """
    from vfwidgets_theme.core.theme_manager import ThemeManager
    from vfwidgets_theme.themes import load_builtin_theme

    # Get manager and load theme
    manager = ThemeManager.instance()
    theme = load_builtin_theme("dark")
    manager.set_theme(theme)

    return {
        "app": qapp,
        "manager": manager,
        "theme": theme,
    }


# ============================================================================
# Cleanup
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_overlay_state():
    """Automatic cleanup of overlay system state after each test.

    Ensures that override registry and theme manager state
    doesn't leak between tests.
    """
    yield  # Run the test

    # Cleanup will be implemented as we build the system
    # For now, just force garbage collection
    import gc
    gc.collect()
