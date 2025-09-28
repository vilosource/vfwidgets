"""
API compatibility tests for ChromeTabbedWindow.

Ensures 100% QTabWidget API compatibility by comparing behavior
directly with QTabWidget instances.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtTest import QSignalSpy
    from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QWidget
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

if QT_AVAILABLE:
    from chrome_tabbed_window import ChromeTabbedWindow


@pytest.fixture
def qapp():
    """Ensure QApplication exists."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def widget_pair(qapp):
    """Create QTabWidget and ChromeTabbedWindow pair for comparison."""
    qt_widget = QTabWidget()
    chrome_widget = ChromeTabbedWindow()
    yield qt_widget, chrome_widget
    qt_widget.deleteLater()
    chrome_widget.deleteLater()


@pytest.fixture
def test_widgets():
    """Create test widgets for tabs."""
    widgets = []
    for i in range(5):
        widget = QLabel(f"Content {i}")
        widgets.append(widget)
    yield widgets
    for widget in widgets:
        widget.deleteLater()


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt not available")
class TestAPICompatibility:
    """Test that ChromeTabbedWindow has identical API to QTabWidget."""

    def test_api_methods_exist(self, widget_pair):
        """Test that all QTabWidget methods exist in ChromeTabbedWindow."""
        qt_widget, chrome_widget = widget_pair

        # Get all public methods from QTabWidget
        qt_methods = [
            method for method in dir(qt_widget)
            if not method.startswith('_') and callable(getattr(qt_widget, method))
        ]

        # Check each method exists in ChromeTabbedWindow
        missing_methods = []
        for method in qt_methods:
            if not hasattr(chrome_widget, method):
                missing_methods.append(method)

        assert not missing_methods, f"Missing methods: {missing_methods}"

    def test_api_properties_exist(self, widget_pair):
        """Test that all QTabWidget properties exist in ChromeTabbedWindow."""
        qt_widget, chrome_widget = widget_pair

        # Key properties that must exist
        properties = [
            'count', 'currentIndex', 'tabPosition', 'tabShape',
            'tabsClosable', 'movable', 'documentMode',
            'iconSize', 'elideMode', 'usesScrollButtons'
        ]

        for prop in properties:
            # Check property exists
            assert hasattr(chrome_widget, prop), f"Missing property: {prop}"

            # Check it's accessible via property() method (Qt property)
            try:
                qt_value = qt_widget.property(prop)
                chrome_value = chrome_widget.property(prop)
                # Values should be comparable types
                assert type(qt_value) == type(chrome_value), f"Property {prop} type mismatch"
            except Exception as e:
                pytest.fail(f"Property {prop} access failed: {e}")

    def test_signals_exist(self, widget_pair):
        """Test that all QTabWidget signals exist in ChromeTabbedWindow."""
        qt_widget, chrome_widget = widget_pair

        # Required signals
        signals = [
            'currentChanged', 'tabCloseRequested', 'tabBarClicked',
            'tabBarDoubleClicked', 'tabMoved'
        ]

        for signal_name in signals:
            assert hasattr(chrome_widget, signal_name), f"Missing signal: {signal_name}"
            signal = getattr(chrome_widget, signal_name)
            assert hasattr(signal, 'connect'), f"Signal {signal_name} not connectable"


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt not available")
class TestBehaviorCompatibility:
    """Test that ChromeTabbedWindow behaves identically to QTabWidget."""

    def test_empty_state_behavior(self, widget_pair):
        """Test behavior when no tabs are present."""
        qt_widget, chrome_widget = widget_pair

        # Both should start with no tabs
        assert qt_widget.count() == chrome_widget.count() == 0

        # Both should have no current index
        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == -1

        # Both should have no current widget
        assert qt_widget.currentWidget() is None
        assert chrome_widget.currentWidget() is None

    def test_add_tab_behavior(self, widget_pair, test_widgets):
        """Test addTab behavior matches QTabWidget exactly."""
        qt_widget, chrome_widget = widget_pair

        # Add first tab to both
        qt_idx = qt_widget.addTab(test_widgets[0], "Tab 0")
        chrome_idx = chrome_widget.addTab(test_widgets[1], "Tab 0")

        # Should return same index
        assert qt_idx == chrome_idx == 0

        # Should have same count
        assert qt_widget.count() == chrome_widget.count() == 1

        # Should have same current index
        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == 0

        # Should have same tab text
        assert qt_widget.tabText(0) == chrome_widget.tabText(0) == "Tab 0"

    def test_add_tab_with_icon_behavior(self, widget_pair, test_widgets):
        """Test addTab with icon behavior."""
        qt_widget, chrome_widget = widget_pair

        icon = QIcon()  # Empty icon for testing

        # Add tab with icon
        qt_idx = qt_widget.addTab(test_widgets[0], icon, "Tab with Icon")
        chrome_idx = chrome_widget.addTab(test_widgets[1], icon, "Tab with Icon")

        # Should behave identically
        assert qt_idx == chrome_idx == 0
        assert qt_widget.count() == chrome_widget.count() == 1
        assert qt_widget.tabText(0) == chrome_widget.tabText(0) == "Tab with Icon"

    def test_insert_tab_behavior(self, widget_pair, test_widgets):
        """Test insertTab behavior matches QTabWidget exactly."""
        qt_widget, chrome_widget = widget_pair

        # Add a few tabs first
        qt_widget.addTab(test_widgets[0], "Tab 0")
        chrome_widget.addTab(test_widgets[1], "Tab 0")

        # Insert in the middle
        qt_idx = qt_widget.insertTab(0, test_widgets[2], "Inserted Tab")
        chrome_idx = chrome_widget.insertTab(0, test_widgets[3], "Inserted Tab")

        # Should behave identically
        assert qt_idx == chrome_idx == 0
        assert qt_widget.count() == chrome_widget.count() == 2
        assert qt_widget.tabText(0) == chrome_widget.tabText(0) == "Inserted Tab"
        assert qt_widget.tabText(1) == chrome_widget.tabText(1) == "Tab 0"

    def test_remove_tab_behavior(self, widget_pair, test_widgets):
        """Test removeTab behavior matches QTabWidget exactly."""
        qt_widget, chrome_widget = widget_pair

        # Add several tabs
        for i in range(3):
            qt_widget.addTab(QLabel(f"QT Content {i}"), f"QT Tab {i}")
            chrome_widget.addTab(QLabel(f"Chrome Content {i}"), f"Chrome Tab {i}")

        # Remove middle tab
        qt_widget.removeTab(1)
        chrome_widget.removeTab(1)

        # Should behave identically
        assert qt_widget.count() == chrome_widget.count() == 2
        assert qt_widget.tabText(0) == "QT Tab 0"
        assert chrome_widget.tabText(0) == "Chrome Tab 0"
        assert qt_widget.tabText(1) == "QT Tab 2"
        assert chrome_widget.tabText(1) == "Chrome Tab 2"

    def test_set_current_index_behavior(self, widget_pair, test_widgets):
        """Test setCurrentIndex behavior matches QTabWidget exactly."""
        qt_widget, chrome_widget = widget_pair

        # Add tabs
        for i in range(3):
            qt_widget.addTab(QLabel(f"QT Content {i}"), f"QT Tab {i}")
            chrome_widget.addTab(QLabel(f"Chrome Content {i}"), f"Chrome Tab {i}")

        # Set current index
        qt_widget.setCurrentIndex(2)
        chrome_widget.setCurrentIndex(2)

        # Should behave identically
        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == 2

        # Test invalid index (should be ignored)
        qt_widget.setCurrentIndex(10)
        chrome_widget.setCurrentIndex(10)

        # Should still be 2
        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == 2

    def test_null_widget_handling(self, widget_pair):
        """Test that null widgets are handled identically."""
        qt_widget, chrome_widget = widget_pair

        # Both should reject None widgets
        qt_result = qt_widget.addTab(None, "Null Tab")
        chrome_result = chrome_widget.addTab(None, "Null Tab")

        # Should return same result (-1)
        assert qt_result == chrome_result == -1

        # Should not add any tabs
        assert qt_widget.count() == chrome_widget.count() == 0

    def test_tab_properties_behavior(self, widget_pair, test_widgets):
        """Test tab property methods behave identically."""
        qt_widget, chrome_widget = widget_pair

        # Add a tab
        qt_widget.addTab(test_widgets[0], "Test Tab")
        chrome_widget.addTab(test_widgets[1], "Test Tab")

        # Test tooltip
        qt_widget.setTabToolTip(0, "Test Tooltip")
        chrome_widget.setTabToolTip(0, "Test Tooltip")

        assert qt_widget.tabToolTip(0) == chrome_widget.tabToolTip(0) == "Test Tooltip"

        # Test enabled state
        qt_widget.setTabEnabled(0, False)
        chrome_widget.setTabEnabled(0, False)

        assert qt_widget.isTabEnabled(0) == chrome_widget.isTabEnabled(0) == False

        # Test visible state
        qt_widget.setTabVisible(0, False)
        chrome_widget.setTabVisible(0, False)

        assert qt_widget.isTabVisible(0) == chrome_widget.isTabVisible(0) == False

    def test_invalid_index_handling(self, widget_pair):
        """Test that invalid indices are handled identically."""
        qt_widget, chrome_widget = widget_pair

        # Test with empty widget
        assert qt_widget.tabText(-1) == chrome_widget.tabText(-1) == ""
        assert qt_widget.tabText(0) == chrome_widget.tabText(0) == ""
        assert qt_widget.tabText(100) == chrome_widget.tabText(100) == ""

        assert qt_widget.widget(-1) is None
        assert chrome_widget.widget(-1) is None
        assert qt_widget.widget(0) is None
        assert chrome_widget.widget(0) is None

        assert qt_widget.isTabEnabled(-1) == chrome_widget.isTabEnabled(-1) == False
        assert qt_widget.isTabEnabled(100) == chrome_widget.isTabEnabled(100) == False


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt not available")
class TestSignalCompatibility:
    """Test that signals are emitted at the same times as QTabWidget."""

    def test_current_changed_signal_timing(self, widget_pair, test_widgets):
        """Test currentChanged signal is emitted at the same times."""
        qt_widget, chrome_widget = widget_pair

        # Set up signal spies
        qt_spy = QSignalSpy(qt_widget.currentChanged)
        chrome_spy = QSignalSpy(chrome_widget.currentChanged)

        # Add first tab (should emit currentChanged with index 0)
        qt_widget.addTab(test_widgets[0], "Tab 0")
        chrome_widget.addTab(test_widgets[1], "Tab 0")

        # Should have emitted currentChanged(0)
        assert qt_spy.count() == chrome_spy.count() == 1

        # Add second tab (should not emit currentChanged)
        qt_widget.addTab(test_widgets[2], "Tab 1")
        chrome_widget.addTab(test_widgets[3], "Tab 1")

        # Should still be 1 signal
        assert qt_spy.count() == chrome_spy.count() == 1

        # Change current index (should emit currentChanged)
        qt_widget.setCurrentIndex(1)
        chrome_widget.setCurrentIndex(1)

        # Should have 2 signals now
        assert qt_spy.count() == chrome_spy.count() == 2

        # Set same index (should not emit)
        qt_widget.setCurrentIndex(1)
        chrome_widget.setCurrentIndex(1)

        # Should still be 2 signals
        assert qt_spy.count() == chrome_spy.count() == 2

    def test_tab_close_requested_signal(self, widget_pair, test_widgets):
        """Test tabCloseRequested signal can be connected."""
        qt_widget, chrome_widget = widget_pair

        # Should be able to connect to signals
        qt_mock = Mock()
        chrome_mock = Mock()

        qt_widget.tabCloseRequested.connect(qt_mock)
        chrome_widget.tabCloseRequested.connect(chrome_mock)

        # Enable close buttons
        qt_widget.setTabsClosable(True)
        chrome_widget.setTabsClosable(True)

        # Add a tab
        qt_widget.addTab(test_widgets[0], "Test Tab")
        chrome_widget.addTab(test_widgets[1], "Test Tab")

        # Signals should be connectable (we can't easily test emission without
        # complex mouse event simulation)
        assert qt_widget.tabsClosable() == chrome_widget.tabsClosable() == True


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt not available")
class TestConfigurationCompatibility:
    """Test that configuration methods behave identically."""

    def test_tabs_closable_property(self, widget_pair):
        """Test tabsClosable property behaves identically."""
        qt_widget, chrome_widget = widget_pair

        # Default should be False
        assert qt_widget.tabsClosable() == chrome_widget.tabsClosable() == False

        # Set to True
        qt_widget.setTabsClosable(True)
        chrome_widget.setTabsClosable(True)

        assert qt_widget.tabsClosable() == chrome_widget.tabsClosable() == True

        # Set back to False
        qt_widget.setTabsClosable(False)
        chrome_widget.setTabsClosable(False)

        assert qt_widget.tabsClosable() == chrome_widget.tabsClosable() == False

    def test_movable_property(self, widget_pair):
        """Test movable property behaves identically."""
        qt_widget, chrome_widget = widget_pair

        # Default should be False
        assert qt_widget.isMovable() == chrome_widget.isMovable() == False

        # Set to True
        qt_widget.setMovable(True)
        chrome_widget.setMovable(True)

        assert qt_widget.isMovable() == chrome_widget.isMovable() == True

    def test_document_mode_property(self, widget_pair):
        """Test document mode property behaves identically."""
        qt_widget, chrome_widget = widget_pair

        # Default should be False
        assert qt_widget.documentMode() == chrome_widget.documentMode() == False

        # Set to True
        qt_widget.setDocumentMode(True)
        chrome_widget.setDocumentMode(True)

        assert qt_widget.documentMode() == chrome_widget.documentMode() == True

    def test_icon_size_property(self, widget_pair):
        """Test icon size property behaves identically."""
        qt_widget, chrome_widget = widget_pair

        # Test setting icon size
        new_size = QSize(24, 24)
        qt_widget.setIconSize(new_size)
        chrome_widget.setIconSize(new_size)

        assert qt_widget.iconSize() == chrome_widget.iconSize() == new_size


@pytest.mark.skipif(not QT_AVAILABLE, reason="Qt not available")
class TestEdgeCases:
    """Test edge cases that QTabWidget handles."""

    def test_many_tabs_behavior(self, widget_pair):
        """Test behavior with many tabs."""
        qt_widget, chrome_widget = widget_pair

        # Add many tabs
        for i in range(50):
            qt_widget.addTab(QLabel(f"QT Content {i}"), f"QT Tab {i}")
            chrome_widget.addTab(QLabel(f"Chrome Content {i}"), f"Chrome Tab {i}")

        # Should handle large numbers of tabs
        assert qt_widget.count() == chrome_widget.count() == 50

        # Current index should still work
        qt_widget.setCurrentIndex(25)
        chrome_widget.setCurrentIndex(25)

        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == 25

    def test_rapid_operations(self, widget_pair):
        """Test rapid add/remove operations."""
        qt_widget, chrome_widget = widget_pair

        # Rapidly add and remove tabs
        for i in range(10):
            qt_widget.addTab(QLabel(f"QT Content {i}"), f"QT Tab {i}")
            chrome_widget.addTab(QLabel(f"Chrome Content {i}"), f"Chrome Tab {i}")

        for i in range(5):
            qt_widget.removeTab(0)
            chrome_widget.removeTab(0)

        # Should end up in consistent state
        assert qt_widget.count() == chrome_widget.count() == 5
        assert qt_widget.currentIndex() == chrome_widget.currentIndex()

    def test_clear_behavior(self, widget_pair, test_widgets):
        """Test clear behavior matches QTabWidget."""
        qt_widget, chrome_widget = widget_pair

        # Add several tabs
        for i in range(3):
            qt_widget.addTab(QLabel(f"QT Content {i}"), f"QT Tab {i}")
            chrome_widget.addTab(QLabel(f"Chrome Content {i}"), f"Chrome Tab {i}")

        # Clear all tabs
        qt_widget.clear()
        chrome_widget.clear()

        # Should be back to empty state
        assert qt_widget.count() == chrome_widget.count() == 0
        assert qt_widget.currentIndex() == chrome_widget.currentIndex() == -1
        assert qt_widget.currentWidget() is None
        assert chrome_widget.currentWidget() is None


if __name__ == "__main__":
    pytest.main([__file__])
