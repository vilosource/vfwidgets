# ChromeTabbedWindow Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage Patterns](#basic-usage-patterns)
3. [Working with Tabs](#working-with-tabs)
4. [Signal Handling](#signal-handling)
5. [Embedded vs Top-Level Mode](#embedded-vs-top-level-mode)
6. [Common Patterns](#common-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Install from PyPI (when published)
pip install chrome-tabbed-window

# Install from local development
pip install -e ./widgets/chrome-tabbed-window

# Install with development dependencies
pip install -e "./widgets/chrome-tabbed-window[dev]"
```

### Minimal Example

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from chrome_tabbed_window import ChromeTabbedWindow

app = QApplication([])

# Create the window
window = ChromeTabbedWindow()
window.setWindowTitle("My Application")
window.resize(800, 600)

# Add some tabs
window.addTab(QTextEdit("Hello, World!"), "Welcome")
window.addTab(QTextEdit(), "Document")

window.show()
app.exec()
```

## Basic Usage Patterns

### Creating a Document Editor

```python
from PySide6.QtWidgets import QApplication, QTextEdit, QMessageBox
from PySide6.QtCore import QTimer
from chrome_tabbed_window import ChromeTabbedWindow

class DocumentEditor(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()

        # Configure the window
        self.setWindowTitle("Document Editor")
        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self.handle_close_request)
        self.currentChanged.connect(self.on_tab_changed)

        # Create initial tab
        self.new_document()

    def new_document(self):
        """Create a new document tab"""
        editor = QTextEdit()
        index = self.addTab(editor, "Untitled")
        self.setCurrentIndex(index)
        return editor

    def handle_close_request(self, index):
        """Handle tab close with confirmation"""
        editor = self.widget(index)
        if editor and editor.document().isModified():
            reply = QMessageBox.question(
                self, "Close Document",
                "Save changes before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                # Save document logic here
                pass

        self.removeTab(index)

        # Keep at least one tab open
        if self.count() == 0:
            self.new_document()

    def on_tab_changed(self, index):
        """Update window title based on current tab"""
        if index >= 0:
            tab_text = self.tabText(index)
            self.setWindowTitle(f"{tab_text} - Document Editor")

# Usage
app = QApplication([])
editor = DocumentEditor()
editor.show()
app.exec()
```

### Creating a Settings Dialog

```python
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                              QListWidget, QLabel, QPushButton)
from chrome_tabbed_window import ChromeTabbedWindow

class SettingsDialog(ChromeTabbedWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure as embedded widget
        self.setWindowTitle("Settings")
        self.setTabsClosable(False)
        self.setMovable(False)

        # Add settings pages
        self.add_general_settings()
        self.add_appearance_settings()
        self.add_advanced_settings()

        # Select first tab
        self.setCurrentIndex(0)

    def add_general_settings(self):
        """Add general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("General Settings"))
        # Add settings controls
        self.addTab(widget, "General")

    def add_appearance_settings(self):
        """Add appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Appearance Settings"))
        # Add appearance controls
        self.addTab(widget, "Appearance")

    def add_advanced_settings(self):
        """Add advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Advanced Settings"))
        # Add advanced controls
        self.addTab(widget, "Advanced")
```

## Working with Tabs

### Dynamic Tab Management

```python
class DynamicTabExample(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)

        # Add "+" button to create new tabs
        add_button = QPushButton("+")
        add_button.setFixedSize(30, 30)
        add_button.clicked.connect(self.add_new_tab)
        self.setCornerWidget(add_button, Qt.TopRightCorner)

        # Create first tab
        self.add_new_tab()

    def add_new_tab(self):
        """Add a new numbered tab"""
        count = self.count()
        widget = QTextEdit(f"Content for Tab {count + 1}")
        index = self.addTab(widget, f"Tab {count + 1}")
        self.setCurrentIndex(index)
```

### Tab Icons and Tooltips

```python
from PySide6.QtGui import QIcon

def setup_tabs_with_metadata(window):
    """Configure tabs with icons, tooltips, and data"""

    # Add tab with icon
    icon = QIcon.fromTheme("document-new")
    editor = QTextEdit()
    index = window.addTab(editor, "Document")
    window.setTabIcon(index, icon)

    # Set tooltip
    window.setTabToolTip(index, "Main document (Ctrl+1)")

    # Store custom data
    window.setTabData(index, {"file_path": "/path/to/file.txt",
                              "modified": False})

    # Retrieve custom data later
    data = window.tabData(index)
    print(f"File: {data.get('file_path')}")
```

### Tab State Management

```python
class StatefulTabs(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)

    def mark_tab_modified(self, index, modified=True):
        """Mark a tab as modified with visual indicator"""
        current_text = self.tabText(index)

        # Remove existing marker
        if current_text.startswith("• "):
            current_text = current_text[2:]

        # Add marker if modified
        if modified:
            self.setTabText(index, f"• {current_text}")
        else:
            self.setTabText(index, current_text)

    def disable_tab(self, index):
        """Disable a tab (keep visible but not selectable)"""
        self.setTabEnabled(index, False)
        self.setTabToolTip(index, "This tab is currently disabled")

    def hide_tab(self, index):
        """Hide a tab completely"""
        self.setTabVisible(index, False)
```

## Signal Handling

### Comprehensive Signal Handling

```python
class SignalExample(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setup_signals()

    def setup_signals(self):
        """Connect all available signals"""

        # Tab change signal
        self.currentChanged.connect(self.on_current_changed)

        # Tab interaction signals
        self.tabCloseRequested.connect(self.on_close_requested)
        self.tabBarClicked.connect(self.on_tab_clicked)
        self.tabBarDoubleClicked.connect(self.on_tab_double_clicked)

    def on_current_changed(self, index):
        """Handle tab switch"""
        if index >= 0:
            widget = self.widget(index)
            print(f"Switched to tab {index}: {self.tabText(index)}")

            # Update UI based on current tab
            if hasattr(widget, 'update_ui'):
                widget.update_ui()

    def on_close_requested(self, index):
        """Handle close request with veto option"""
        widget = self.widget(index)

        # Check if widget can be closed
        if hasattr(widget, 'can_close'):
            if not widget.can_close():
                return  # Veto the close

        # Proceed with close
        self.removeTab(index)

    def on_tab_clicked(self, index):
        """Handle single click on tab"""
        print(f"Tab {index} clicked")

    def on_tab_double_clicked(self, index):
        """Handle double click on tab - maybe rename"""
        from PySide6.QtWidgets import QInputDialog

        current_text = self.tabText(index)
        new_text, ok = QInputDialog.getText(
            self, "Rename Tab",
            "New name:", text=current_text
        )
        if ok and new_text:
            self.setTabText(index, new_text)
```

### Keyboard Shortcuts

```python
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

class ShortcutExample(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""

        # Ctrl+T: New tab
        new_tab = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab.activated.connect(self.create_new_tab)

        # Ctrl+W: Close current tab
        close_tab = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab.activated.connect(self.close_current_tab)

        # Ctrl+Tab: Next tab
        next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab.activated.connect(self.next_tab)

        # Ctrl+Shift+Tab: Previous tab
        prev_tab = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab.activated.connect(self.previous_tab)

        # Ctrl+1-9: Jump to tab
        for i in range(1, 10):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(
                lambda idx=i-1: self.setCurrentIndex(idx)
                if idx < self.count() else None
            )

    def create_new_tab(self):
        widget = QTextEdit()
        self.addTab(widget, "New Tab")
        self.setCurrentWidget(widget)

    def close_current_tab(self):
        current = self.currentIndex()
        if current >= 0:
            self.tabCloseRequested.emit(current)

    def next_tab(self):
        current = self.currentIndex()
        if current < self.count() - 1:
            self.setCurrentIndex(current + 1)
        else:
            self.setCurrentIndex(0)  # Wrap around

    def previous_tab(self):
        current = self.currentIndex()
        if current > 0:
            self.setCurrentIndex(current - 1)
        else:
            self.setCurrentIndex(self.count() - 1)  # Wrap around
```

## Embedded vs Top-Level Mode

### Top-Level Window Mode

```python
# Top-level mode: Frameless window with chrome
window = ChromeTabbedWindow()  # No parent
window.setWindowTitle("My App")
window.resize(1024, 768)

# Window will have:
# - Frameless chrome (if supported)
# - Integrated window controls
# - System move/resize
# - New tab button

window.show()
```

### Embedded Widget Mode

```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

# Embedded mode: Regular widget in layout
main_window = QMainWindow()
central = QWidget()
layout = QVBoxLayout(central)

tabs = ChromeTabbedWindow(parent=central)  # Has parent
tabs.addTab(QTextEdit(), "Editor")

# Widget will have:
# - Standard tab appearance
# - No window controls
# - No frameless features
# - Follows layout rules

layout.addWidget(tabs)
main_window.setCentralWidget(central)
main_window.show()
```

### Split Pane Example

```python
from PySide6.QtWidgets import QSplitter

class SplitPaneExample(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left pane: ChromeTabbedWindow
        left_tabs = ChromeTabbedWindow(parent=splitter)
        left_tabs.addTab(QListWidget(), "Files")
        left_tabs.addTab(QTextEdit(), "Notes")

        # Right pane: Another ChromeTabbedWindow
        right_tabs = ChromeTabbedWindow(parent=splitter)
        right_tabs.addTab(QTextEdit(), "Editor")
        right_tabs.addTab(QTextEdit(), "Output")

        splitter.addWidget(left_tabs)
        splitter.addWidget(right_tabs)
        splitter.setSizes([300, 700])

        self.setCentralWidget(splitter)
        self.setWindowTitle("Split Pane IDE")
        self.resize(1000, 700)
```

## Common Patterns

### IDE-Style Interface

```python
from PySide6.QtWidgets import (QMainWindow, QSplitter, QTreeWidget,
                              QTextEdit, QDockWidget)

class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IDE Example")

        # Central editor tabs
        self.editor_tabs = ChromeTabbedWindow()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.setCentralWidget(self.editor_tabs)

        # File browser dock
        dock = QDockWidget("Files", self)
        file_tree = QTreeWidget()
        dock.setWidget(file_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # Output tabs at bottom
        bottom_tabs = ChromeTabbedWindow()
        bottom_tabs.addTab(QTextEdit(), "Console")
        bottom_tabs.addTab(QListWidget(), "Problems")
        bottom_tabs.addTab(QTextEdit(), "Output")

        bottom_dock = QDockWidget("Output", self)
        bottom_dock.setWidget(bottom_tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock)

        # Connect file tree to open files
        file_tree.itemDoubleClicked.connect(self.open_file)

    def open_file(self, item, column):
        """Open file in new tab"""
        file_name = item.text(0)
        editor = QTextEdit()
        # Load file content here
        self.editor_tabs.addTab(editor, file_name)
```

### Browser-Style Interface

```python
from PySide6.QtWidgets import QLineEdit, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView

class BrowserWindow(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Example")
        self.setTabsClosable(True)
        self.setMovable(True)

        # Add new tab button
        self.setup_new_tab_button()

        # Create home tab
        self.new_tab("https://www.example.com")

    def setup_new_tab_button(self):
        """Add + button for new tabs"""
        btn = QPushButton("+")
        btn.setFixedSize(30, 30)
        btn.clicked.connect(lambda: self.new_tab())
        self.setCornerWidget(btn, Qt.TopRightCorner)

    def new_tab(self, url="about:blank"):
        """Create new browser tab"""
        # Create web view
        web_view = QWebEngineView()
        web_view.load(QUrl(url))

        # Add to tabs
        index = self.addTab(web_view, "Loading...")
        self.setCurrentIndex(index)

        # Update tab title when page loads
        web_view.titleChanged.connect(
            lambda title: self.setTabText(
                self.indexOf(web_view), title[:20]
            )
        )

        return web_view
```

### Dashboard with Multiple Views

```python
from PySide6.QtWidgets import QTableWidget, QListWidget
from PySide6.QtCharts import QChartView

class DashboardWindow(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setTabsClosable(False)
        self.setMovable(True)

        # Overview tab
        self.add_overview_tab()

        # Data table tab
        self.add_data_tab()

        # Charts tab
        self.add_charts_tab()

        # Settings tab
        self.add_settings_tab()

    def add_overview_tab(self):
        """Add overview with summary widgets"""
        widget = QWidget()
        layout = QGridLayout(widget)

        # Add summary cards
        for i in range(4):
            card = self.create_summary_card(f"Metric {i+1}")
            layout.addWidget(card, i // 2, i % 2)

        self.addTab(widget, "Overview")

    def add_data_tab(self):
        """Add data table view"""
        table = QTableWidget(100, 5)
        table.setHorizontalHeaderLabels(
            ["ID", "Name", "Value", "Status", "Date"]
        )
        self.addTab(table, "Data")

    def add_charts_tab(self):
        """Add charts view"""
        # Would use QChartView here
        chart_widget = QWidget()
        self.addTab(chart_widget, "Analytics")

    def add_settings_tab(self):
        """Add settings panel"""
        settings = QWidget()
        # Add settings controls
        self.addTab(settings, "Settings")

    def create_summary_card(self, title):
        """Create a summary card widget"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.addWidget(QLabel(title))
        layout.addWidget(QLabel("Value: 42"))
        return card
```

## Best Practices

### 1. Tab Lifecycle Management

```python
class TabLifecycleManager:
    """Best practices for tab lifecycle"""

    def safe_add_tab(self, window, widget, title):
        """Safely add a tab with error handling"""
        try:
            index = window.addTab(widget, title)

            # Set up widget if needed
            if hasattr(widget, 'initialize'):
                widget.initialize()

            return index
        except Exception as e:
            print(f"Failed to add tab: {e}")
            return -1

    def safe_remove_tab(self, window, index):
        """Safely remove a tab with cleanup"""
        widget = window.widget(index)

        if widget:
            # Cleanup widget resources
            if hasattr(widget, 'cleanup'):
                widget.cleanup()

            # Remove from window
            window.removeTab(index)

            # Schedule deletion
            widget.deleteLater()
```

### 2. Memory Management

```python
class MemoryEfficientTabs(ChromeTabbedWindow):
    """Memory-efficient tab management"""

    def __init__(self):
        super().__init__()
        self._tab_cache = {}

    def add_lazy_tab(self, factory, title):
        """Add tab with lazy loading"""
        # Create placeholder
        placeholder = QLabel("Loading...")
        index = self.addTab(placeholder, title)

        # Store factory for lazy creation
        self._tab_cache[index] = factory

        return index

    def currentChanged(self, index):
        """Load tab content when selected"""
        if index in self._tab_cache:
            # Create actual widget
            factory = self._tab_cache.pop(index)
            widget = factory()

            # Replace placeholder
            old_widget = self.widget(index)
            self.removeTab(index)
            self.insertTab(index, widget, self.tabText(index))
            old_widget.deleteLater()
```

### 3. State Persistence

```python
import json

class PersistentTabs(ChromeTabbedWindow):
    """Save and restore tab state"""

    def save_state(self):
        """Save current tab state"""
        state = {
            'tabs': [],
            'current_index': self.currentIndex()
        }

        for i in range(self.count()):
            widget = self.widget(i)
            tab_state = {
                'title': self.tabText(i),
                'enabled': self.isTabEnabled(i),
                'data': self.tabData(i)
            }

            # Save widget-specific state
            if hasattr(widget, 'save_state'):
                tab_state['widget_state'] = widget.save_state()

            state['tabs'].append(tab_state)

        return state

    def restore_state(self, state):
        """Restore tab state"""
        # Clear existing tabs
        self.clear()

        # Restore tabs
        for tab_state in state.get('tabs', []):
            # Create widget (application-specific)
            widget = self.create_widget_from_state(tab_state)

            # Add tab
            index = self.addTab(widget, tab_state['title'])
            self.setTabEnabled(index, tab_state.get('enabled', True))
            self.setTabData(index, tab_state.get('data'))

        # Restore current tab
        current = state.get('current_index', 0)
        if 0 <= current < self.count():
            self.setCurrentIndex(current)
```

### 4. Performance Optimization

```python
class OptimizedTabs(ChromeTabbedWindow):
    """Performance-optimized tab handling"""

    def __init__(self):
        super().__init__()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._batch_update)
        self._pending_updates = []

    def schedule_update(self, index, update_fn):
        """Batch updates to prevent flickering"""
        self._pending_updates.append((index, update_fn))

        if not self._update_timer.isActive():
            self._update_timer.start(50)  # 50ms debounce

    def _batch_update(self):
        """Process batched updates"""
        self._update_timer.stop()

        for index, update_fn in self._pending_updates:
            if 0 <= index < self.count():
                update_fn(index)

        self._pending_updates.clear()
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Tabs not showing close buttons
```python
# Solution: Enable closable tabs
window.setTabsClosable(True)

# Connect close signal
window.tabCloseRequested.connect(window.removeTab)
```

#### Issue: Cannot reorder tabs
```python
# Solution: Enable movable tabs
window.setMovable(True)
```

#### Issue: Tab text is cut off
```python
# Solution: Set elide mode
window.setElideMode(Qt.ElideMiddle)

# Or increase tab width (in custom style)
window.setStyleSheet("""
    QTabBar::tab {
        min-width: 100px;
        max-width: 200px;
    }
""")
```

#### Issue: Memory leaks with dynamic tabs
```python
# Solution: Properly clean up widgets
def remove_tab_safely(window, index):
    widget = window.widget(index)
    window.removeTab(index)

    # Schedule deletion
    if widget:
        widget.deleteLater()
```

#### Issue: Frameless window not working
```python
# The window automatically detects platform capabilities
# Check if platform supports frameless:

window = ChromeTabbedWindow()
if not window.isTopLevel():
    print("Window is embedded, frameless not available")

# On some platforms (WSL), frameless may not be supported
# The window will automatically fall back to native decorations
```

### Platform-Specific Notes

#### Windows
- Full frameless support with Aero snap
- Window controls integrated into tab bar
- DWM composition effects supported

#### macOS
- Frameless mode available but may default to native
- Full native fullscreen support
- Traffic light buttons can be customized

#### Linux
- Behavior depends on window manager
- Wayland vs X11 detected automatically
- Some compositors may not support all features

#### WSL/WSLg
- May fall back to native decorations
- Test thoroughly in WSL environment
- Consider using embedded mode for consistency

## See Also

- [API Reference](api.md) - Complete API documentation
- [Architecture](architecture.md) - Internal design details
- [Platform Notes](platform-notes.md) - Platform-specific information
- [Examples](../examples/) - Full example applications