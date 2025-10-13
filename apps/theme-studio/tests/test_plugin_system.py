"""Tests for plugin discovery system.

Tests cover:
- PluginRegistry (controller)
- PluginWidgetFactory (controller)
- DiscoveredWidgetPlugin (view adapter)
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtWidgets import QWidget
from vfwidgets_theme import PluginAvailability, WidgetMetadata

from theme_studio.controllers import PluginRegistry, PluginWidgetFactory
from theme_studio.plugins import DiscoveredWidgetPlugin


@pytest.fixture
def mock_available_metadata():
    """Create mock metadata for an available plugin."""
    return WidgetMetadata(
        name="Test Widget",
        widget_class_name="TestWidget",
        package_name="test_package",
        version="1.0.0",
        theme_tokens={"background": "editor.background"},
        preview_factory=lambda parent: QWidget(parent),
        preview_description="A test widget",
        availability=PluginAvailability.AVAILABLE,
    )


@pytest.fixture
def mock_unavailable_metadata():
    """Create mock metadata for an unavailable plugin."""
    return WidgetMetadata(
        name="Broken Widget",
        widget_class_name="BrokenWidget",
        package_name="broken_package",
        version="1.0.0",
        theme_tokens={"background": "editor.background"},
        availability=PluginAvailability.IMPORT_ERROR,
        error_message="Failed to import module",
    )


@pytest.fixture
def mock_entry_point_available(mock_available_metadata):
    """Create a mock entry point that returns available metadata."""
    mock_ep = Mock()
    mock_ep.name = "test_plugin"
    mock_ep.value = "test_package:get_metadata"
    mock_ep.load.return_value = lambda: mock_available_metadata
    return mock_ep


@pytest.fixture
def mock_entry_point_unavailable(mock_unavailable_metadata):
    """Create a mock entry point that returns unavailable metadata."""
    mock_ep = Mock()
    mock_ep.name = "broken_plugin"
    mock_ep.value = "broken_package:get_metadata"
    mock_ep.load.return_value = lambda: mock_unavailable_metadata
    return mock_ep


class TestPluginRegistry:
    """Test PluginRegistry controller."""

    def test_initialization(self, qtbot):
        """Test registry initialization."""
        registry = PluginRegistry()
        # Note: PluginRegistry is QObject, not QWidget, so don't add to qtbot

        assert registry.plugins == {}
        assert registry.available_plugins == {}

    def test_discover_no_plugins(self, qtbot):
        """Test discovery with no plugins."""
        registry = PluginRegistry()

        with patch("theme_studio.controllers.plugin_registry.entry_points") as mock_ep:
            mock_ep.return_value = []

            # Connect signals to verify they fire
            started_spy = []
            completed_spy = []
            registry.discovery_started.connect(lambda: started_spy.append(True))
            registry.discovery_completed.connect(lambda count: completed_spy.append(count))

            plugins = registry.discover_plugins()

            assert plugins == {}
            assert len(started_spy) == 1
            assert len(completed_spy) == 1
            assert completed_spy[0] == 0

    def test_discover_available_plugin(
        self, qtbot, mock_entry_point_available, mock_available_metadata
    ):
        """Test discovering an available plugin."""
        registry = PluginRegistry()

        with patch(
            "theme_studio.controllers.plugin_registry.entry_points"
        ) as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point_available]

            # Connect signals
            discovered_plugins = []
            registry.plugin_discovered.connect(
                lambda name, meta: discovered_plugins.append((name, meta))
            )

            plugins = registry.discover_plugins()

            assert len(plugins) == 1
            assert "test_plugin" in plugins
            assert plugins["test_plugin"].name == "Test Widget"
            assert plugins["test_plugin"].is_available

            # Verify signal was emitted
            assert len(discovered_plugins) == 1
            assert discovered_plugins[0][0] == "test_plugin"

    def test_discover_unavailable_plugin(
        self, qtbot, mock_entry_point_unavailable, mock_unavailable_metadata
    ):
        """Test discovering an unavailable plugin."""
        registry = PluginRegistry()

        with patch(
            "theme_studio.controllers.plugin_registry.entry_points"
        ) as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point_unavailable]

            # Connect signals
            failed_plugins = []
            registry.plugin_failed.connect(
                lambda name, msg: failed_plugins.append((name, msg))
            )

            plugins = registry.discover_plugins()

            assert len(plugins) == 1
            assert "broken_plugin" in plugins
            assert not plugins["broken_plugin"].is_available

            # Verify signal was emitted
            assert len(failed_plugins) == 1
            assert failed_plugins[0][0] == "broken_plugin"
            assert "Failed to import module" in failed_plugins[0][1]

    def test_available_plugins_property(
        self, qtbot, mock_entry_point_available, mock_entry_point_unavailable
    ):
        """Test available_plugins property filters correctly."""
        registry = PluginRegistry()

        with patch(
            "theme_studio.controllers.plugin_registry.entry_points"
        ) as mock_entry_points:
            mock_entry_points.return_value = [
                mock_entry_point_available,
                mock_entry_point_unavailable,
            ]

            registry.discover_plugins()

            # All plugins
            assert len(registry.plugins) == 2

            # Only available
            available = registry.available_plugins
            assert len(available) == 1
            assert "test_plugin" in available
            assert "broken_plugin" not in available

    def test_get_plugin(self, qtbot, mock_entry_point_available):
        """Test getting plugin by name."""
        registry = PluginRegistry()

        with patch(
            "theme_studio.controllers.plugin_registry.entry_points"
        ) as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point_available]
            registry.discover_plugins()

            plugin = registry.get_plugin("test_plugin")
            assert plugin is not None
            assert plugin.name == "Test Widget"

            not_found = registry.get_plugin("nonexistent")
            assert not_found is None


class TestPluginWidgetFactory:
    """Test PluginWidgetFactory controller."""

    def test_create_widget_available(self, qtbot, mock_available_metadata):
        """Test creating widget from available plugin."""
        factory = PluginWidgetFactory(mock_available_metadata)

        widget = factory.create_widget()
        qtbot.addWidget(widget)

        assert isinstance(widget, QWidget)
        # Verify it's the actual widget (fallback widgets have children with text)
        # A plain QWidget from the mock factory has no child widgets
        assert len(widget.findChildren(QWidget)) == 0

    def test_create_widget_unavailable(self, qtbot, mock_unavailable_metadata):
        """Test creating widget from unavailable plugin."""
        factory = PluginWidgetFactory(mock_unavailable_metadata)

        widget = factory.create_widget()
        qtbot.addWidget(widget)

        assert isinstance(widget, QWidget)
        # Verify it's the fallback widget (has specific layout)
        assert widget.layout() is not None

    def test_create_widget_no_factory(self, qtbot):
        """Test creating widget when preview_factory is None."""
        metadata = WidgetMetadata(
            name="No Factory",
            widget_class_name="NoFactory",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
            preview_factory=None,  # No factory
        )

        factory = PluginWidgetFactory(metadata)
        widget = factory.create_widget()
        qtbot.addWidget(widget)

        # Should return error widget
        assert isinstance(widget, QWidget)
        assert widget.layout() is not None

    def test_create_widget_factory_raises_exception(self, qtbot):
        """Test handling factory that raises exception."""

        def broken_factory(parent):
            raise RuntimeError("Factory failed")

        metadata = WidgetMetadata(
            name="Broken Factory",
            widget_class_name="BrokenFactory",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
            preview_factory=broken_factory,
        )

        factory = PluginWidgetFactory(metadata)
        widget = factory.create_widget()
        qtbot.addWidget(widget)

        # Should return error widget
        assert isinstance(widget, QWidget)
        assert widget.layout() is not None


class TestDiscoveredWidgetPlugin:
    """Test DiscoveredWidgetPlugin adapter."""

    def test_get_name(self, mock_available_metadata):
        """Test getting plugin name."""
        plugin = DiscoveredWidgetPlugin(mock_available_metadata)
        assert plugin.get_name() == "Test Widget"

    def test_get_description(self, mock_available_metadata):
        """Test getting plugin description."""
        plugin = DiscoveredWidgetPlugin(mock_available_metadata)
        assert plugin.get_description() == "A test widget"

    def test_get_description_generated(self):
        """Test description is generated when not provided."""
        metadata = WidgetMetadata(
            name="Auto Desc",
            widget_class_name="AutoDesc",
            package_name="auto_pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background", "fg": "editor.foreground"},
            preview_description="",  # No description
        )

        plugin = DiscoveredWidgetPlugin(metadata)
        desc = plugin.get_description()

        assert "AutoDesc" in desc
        assert "auto_pkg" in desc
        assert "2 theme tokens" in desc

    def test_create_preview_widget(self, qtbot, mock_available_metadata):
        """Test creating preview widget through adapter."""
        plugin = DiscoveredWidgetPlugin(mock_available_metadata)

        widget = plugin.create_preview_widget()
        qtbot.addWidget(widget)

        assert isinstance(widget, QWidget)

    def test_is_available(self, mock_available_metadata, mock_unavailable_metadata):
        """Test is_available method."""
        available_plugin = DiscoveredWidgetPlugin(mock_available_metadata)
        assert available_plugin.is_available() is True

        unavailable_plugin = DiscoveredWidgetPlugin(mock_unavailable_metadata)
        assert unavailable_plugin.is_available() is False

    def test_get_token_categories(self):
        """Test getting token categories."""
        metadata = WidgetMetadata(
            name="Multi Category",
            widget_class_name="MultiCategory",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={
                "bg": "editor.background",
                "fg": "editor.foreground",
                "black": "terminal.ansiBlack",
            },
        )

        plugin = DiscoveredWidgetPlugin(metadata)
        categories = plugin.get_token_categories()

        assert "editor" in categories
        assert "terminal" in categories

    def test_get_token_count(self, mock_available_metadata):
        """Test getting token count."""
        plugin = DiscoveredWidgetPlugin(mock_available_metadata)
        assert plugin.get_token_count() == 1
