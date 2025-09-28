# ChromeTabbedWindow API Reference (v1.0)

## Overview

`ChromeTabbedWindow` is a drop-in replacement for Qt's `QTabWidget` that provides a Chrome-style tabbed interface with 100% API compatibility. This document covers the complete public API for v1.0.

## Class Hierarchy

```
QWidget
    └── ChromeTabbedWindow
```

## Constructor

```python
ChromeTabbedWindow(parent: Optional[QWidget] = None)
```

Creates a new ChromeTabbedWindow instance.

- **parent**: Optional parent widget. If None, the window operates in top-level mode with frameless window support. If provided, operates in embedded mode as a regular widget.

## Core Methods

### Tab Management

#### `addTab(widget: QWidget, label: str) -> int`
Adds a new tab with the specified widget and label at the end of the tab bar.

**Parameters:**
- `widget`: The widget to display in the tab
- `label`: The text to display on the tab

**Returns:** The index of the newly added tab

**Example:**
```python
editor = QTextEdit()
index = window.addTab(editor, "Document.txt")
```

#### `insertTab(index: int, widget: QWidget, label: str) -> int`
Inserts a new tab at the specified position.

**Parameters:**
- `index`: Position where to insert the tab (0-based)
- `widget`: The widget to display in the tab
- `label`: The text to display on the tab

**Returns:** The actual index where the tab was inserted

**Example:**
```python
editor = QTextEdit()
index = window.insertTab(0, editor, "First Tab")
```

#### `removeTab(index: int) -> None`
Removes the tab at the specified index.

**Parameters:**
- `index`: The index of the tab to remove

**Note:** The widget is not deleted, just removed from the tab widget. Parent ownership is cleared.

#### `clear() -> None`
Removes all tabs from the widget.

**Note:** Widgets are not deleted, just removed.

#### `count() -> int`
Returns the number of tabs.

**Returns:** The total number of tabs

#### `currentIndex() -> int`
Returns the index of the currently visible tab.

**Returns:** Index of current tab, or -1 if no tabs exist

#### `setCurrentIndex(index: int) -> None`
Makes the tab at the specified index current.

**Parameters:**
- `index`: The index of the tab to make current

**Emits:** `currentChanged(int)` if the current tab changes

#### `setCurrentWidget(widget: QWidget) -> None`
Makes the tab containing the specified widget current.

**Parameters:**
- `widget`: The widget whose tab should become current

#### `currentWidget() -> QWidget`
Returns the widget shown in the current tab.

**Returns:** Current widget or None if no tabs exist

#### `widget(index: int) -> QWidget`
Returns the widget at the specified tab index.

**Parameters:**
- `index`: The tab index

**Returns:** Widget at index or None if index is invalid

#### `indexOf(widget: QWidget) -> int`
Returns the index of the tab containing the specified widget.

**Parameters:**
- `widget`: The widget to find

**Returns:** Tab index or -1 if widget not found

## Tab Attributes

### Text and Icons

#### `setTabText(index: int, text: str) -> None`
Sets the text for the tab at the specified index.

**Parameters:**
- `index`: The tab index
- `text`: The new text for the tab

#### `tabText(index: int) -> str`
Returns the text of the tab at the specified index.

**Parameters:**
- `index`: The tab index

**Returns:** Tab text or empty string if index is invalid

#### `setTabIcon(index: int, icon: QIcon) -> None`
Sets the icon for the tab at the specified index.

**Parameters:**
- `index`: The tab index
- `icon`: The icon to display

#### `tabIcon(index: int) -> QIcon`
Returns the icon of the tab at the specified index.

**Parameters:**
- `index`: The tab index

**Returns:** Tab icon or null icon if index is invalid

### Tooltips and Accessibility

#### `setTabToolTip(index: int, tip: str) -> None`
Sets the tooltip for the tab at the specified index.

**Parameters:**
- `index`: The tab index
- `tip`: The tooltip text

#### `tabToolTip(index: int) -> str`
Returns the tooltip of the tab at the specified index.

**Parameters:**
- `index`: The tab index

**Returns:** Tooltip text or empty string if index is invalid

#### `setTabWhatsThis(index: int, text: str) -> None`
Sets the "What's This?" help text for the tab.

**Parameters:**
- `index`: The tab index
- `text`: The help text

#### `tabWhatsThis(index: int) -> str`
Returns the "What's This?" help text for the tab.

**Parameters:**
- `index`: The tab index

**Returns:** Help text or empty string if index is invalid

### Tab State

#### `setTabEnabled(index: int, enabled: bool) -> None`
Enables or disables the tab at the specified index.

**Parameters:**
- `index`: The tab index
- `enabled`: True to enable, False to disable

#### `isTabEnabled(index: int) -> bool`
Returns whether the tab at the specified index is enabled.

**Parameters:**
- `index`: The tab index

**Returns:** True if enabled, False otherwise

#### `setTabVisible(index: int, visible: bool) -> None`
Shows or hides the tab at the specified index.

**Parameters:**
- `index`: The tab index
- `visible`: True to show, False to hide

#### `isTabVisible(index: int) -> bool`
Returns whether the tab at the specified index is visible.

**Parameters:**
- `index`: The tab index

**Returns:** True if visible, False otherwise

### User Data

#### `setTabData(index: int, data: Any) -> None`
Stores arbitrary data with the tab.

**Parameters:**
- `index`: The tab index
- `data`: Any Python object to store

#### `tabData(index: int) -> Any`
Retrieves the user data stored with the tab.

**Parameters:**
- `index`: The tab index

**Returns:** The stored data or None

## Behavior and Appearance

### Tab Features

#### `setTabsClosable(closable: bool) -> None`
Sets whether tabs should show close buttons.

**Parameters:**
- `closable`: True to show close buttons

**Property:** `tabsClosable`

#### `tabsClosable() -> bool`
Returns whether tabs show close buttons.

**Returns:** True if tabs are closable

#### `setMovable(movable: bool) -> None`
Sets whether tabs can be reordered by dragging.

**Parameters:**
- `movable`: True to allow tab reordering

**Property:** `movable`

#### `isMovable() -> bool`
Returns whether tabs can be reordered.

**Returns:** True if tabs are movable

### Visual Properties

#### `setIconSize(size: QSize) -> None`
Sets the size for tab icons.

**Parameters:**
- `size`: The icon size

**Property:** `iconSize`

#### `iconSize() -> QSize`
Returns the size used for tab icons.

**Returns:** Current icon size

#### `setElideMode(mode: Qt.TextElideMode) -> None`
Sets how tab text should be elided when too long.

**Parameters:**
- `mode`: One of Qt.ElideLeft, Qt.ElideRight, Qt.ElideMiddle, Qt.ElideNone

**Property:** `elideMode`

#### `elideMode() -> Qt.TextElideMode`
Returns the current text elide mode.

**Returns:** Current elide mode

#### `setUsesScrollButtons(useButtons: bool) -> None`
Sets whether to show scroll buttons when tabs don't fit.

**Parameters:**
- `useButtons`: True to show scroll buttons

**Property:** `usesScrollButtons`

#### `usesScrollButtons() -> bool`
Returns whether scroll buttons are shown.

**Returns:** True if scroll buttons are used

### Tab Bar Configuration

#### `setTabPosition(position: QTabWidget.TabPosition) -> None`
Sets the position of the tab bar.

**Parameters:**
- `position`: One of North, South, West, East

**Property:** `tabPosition`

**Note:** ChromeTabbedWindow optimizes for North (top) position. Other positions are supported but may not have Chrome styling.

#### `tabPosition() -> QTabWidget.TabPosition`
Returns the tab bar position.

**Returns:** Current tab position

#### `setTabShape(shape: QTabWidget.TabShape) -> None`
Sets the shape of the tabs.

**Parameters:**
- `shape`: One of Rounded or Triangular

**Property:** `tabShape`

#### `tabShape() -> QTabWidget.TabShape`
Returns the tab shape.

**Returns:** Current tab shape

#### `setDocumentMode(enabled: bool) -> None`
Sets document mode (tabs suitable for document pages).

**Parameters:**
- `enabled`: True for document mode

**Property:** `documentMode`

#### `documentMode() -> bool`
Returns whether document mode is enabled.

**Returns:** True if in document mode

## Corner Widgets

#### `setCornerWidget(widget: QWidget, corner: Qt.Corner = Qt.TopRightCorner) -> None`
Sets a widget to display in the specified corner of the tab bar.

**Parameters:**
- `widget`: The widget to display (None to remove)
- `corner`: Which corner (TopLeftCorner or TopRightCorner)

#### `cornerWidget(corner: Qt.Corner = Qt.TopRightCorner) -> QWidget`
Returns the widget shown in the specified corner.

**Parameters:**
- `corner`: Which corner

**Returns:** Corner widget or None

## Tab Bar Access

#### `tabBar() -> QTabBar`
Returns the tab bar widget used by the tab widget.

**Returns:** The tab bar widget

**Note:** In ChromeTabbedWindow, this returns a Chrome-styled tab bar that extends QTabBar.

## Signals

### Current Tab Changed

#### `currentChanged(index: int)`
Emitted when the current tab changes.

**Parameters:**
- `index`: Index of the new current tab (-1 if no tabs)

**Example:**
```python
window.currentChanged.connect(lambda i: print(f"Switched to tab {i}"))
```

### Tab Interaction

#### `tabCloseRequested(index: int)`
Emitted when a tab's close button is clicked.

**Parameters:**
- `index`: Index of the tab to be closed

**Note:** The tab is not automatically closed. You must call `removeTab()` if you want to close it.

**Example:**
```python
window.tabCloseRequested.connect(window.removeTab)
```

#### `tabBarClicked(index: int)`
Emitted when a tab is clicked.

**Parameters:**
- `index`: Index of the clicked tab

#### `tabBarDoubleClicked(index: int)`
Emitted when a tab is double-clicked.

**Parameters:**
- `index`: Index of the double-clicked tab

## Properties

ChromeTabbedWindow exposes the following Qt properties:

| Property | Type | Getter | Setter | Description |
|----------|------|--------|--------|-------------|
| `tabPosition` | TabPosition | `tabPosition()` | `setTabPosition()` | Position of tab bar |
| `tabShape` | TabShape | `tabShape()` | `setTabShape()` | Shape of tabs |
| `currentIndex` | int | `currentIndex()` | `setCurrentIndex()` | Current tab index |
| `count` | int | `count()` | - | Number of tabs (read-only) |
| `iconSize` | QSize | `iconSize()` | `setIconSize()` | Size of tab icons |
| `elideMode` | Qt.TextElideMode | `elideMode()` | `setElideMode()` | Text eliding mode |
| `usesScrollButtons` | bool | `usesScrollButtons()` | `setUsesScrollButtons()` | Show scroll buttons |
| `documentMode` | bool | `documentMode()` | `setDocumentMode()` | Document mode |
| `tabsClosable` | bool | `tabsClosable()` | `setTabsClosable()` | Show close buttons |
| `movable` | bool | `isMovable()` | `setMovable()` | Allow tab reordering |

## Chrome-Specific Features (v1.0)

While maintaining 100% QTabWidget compatibility, ChromeTabbedWindow provides Chrome-style visuals:

- Chrome-style tab appearance with proper curves and shadows
- Smooth tab animations
- Tab hover effects
- New tab button (when in top-level mode)
- Integrated window controls (minimize, maximize, close) when frameless
- Platform-aware rendering

These features are automatic and require no additional API calls.

## Platform Behavior

ChromeTabbedWindow automatically detects and adapts to the platform:

| Platform | Frameless | System Move | System Resize | Notes |
|----------|-----------|-------------|---------------|-------|
| Windows | ✅ | ✅ | ✅ | Full support with Aero snap |
| macOS | ✅ | ✅ | ✅ | Native fullscreen support |
| Linux X11 | ✅ | ✅ | ✅ | Full support |
| Linux Wayland | ✅ | ✅* | ✅* | Compositor-dependent |
| WSL/WSLg | ⚠️ | ⚠️ | ⚠️ | Falls back to native decorations |

*Requires Qt 6.5+ and compositor support

## Usage Examples

### Basic Usage

```python
from PySide6.QtWidgets import QApplication, QTextEdit
from chrome_tabbed_window import ChromeTabbedWindow

app = QApplication([])

# Create window
window = ChromeTabbedWindow()

# Add tabs
window.addTab(QTextEdit("Content 1"), "Tab 1")
window.addTab(QTextEdit("Content 2"), "Tab 2")

# Enable features
window.setTabsClosable(True)
window.setMovable(True)

# Connect signals
window.currentChanged.connect(lambda i: print(f"Current tab: {i}"))
window.tabCloseRequested.connect(window.removeTab)

window.show()
app.exec()
```

### Embedded Mode

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

main = QMainWindow()
central = QWidget()
layout = QVBoxLayout(central)

# Create as child widget
tabs = ChromeTabbedWindow(parent=central)
tabs.addTab(QTextEdit(), "Document 1")
tabs.addTab(QTextEdit(), "Document 2")

layout.addWidget(tabs)
main.setCentralWidget(central)
main.show()
```

## Migration from QTabWidget

ChromeTabbedWindow is a drop-in replacement for QTabWidget:

```python
# Before
from PySide6.QtWidgets import QTabWidget
tabs = QTabWidget()

# After
from chrome_tabbed_window import ChromeTabbedWindow
tabs = ChromeTabbedWindow()
# No other code changes needed!
```

## Thread Safety

Like QTabWidget, ChromeTabbedWindow is not thread-safe. All methods must be called from the main GUI thread.

## Memory Management

ChromeTabbedWindow follows Qt's parent-child ownership model:

- Widgets added to tabs become children of the tab widget
- Removing a tab clears the widget's parent (widget is not deleted)
- Deleting the tab widget deletes all child widgets
- Use `QWidget.deleteLater()` for safe deletion

## Performance

- Tab operations: < 50ms on typical hardware
- Smooth 60 FPS animations
- Efficient repainting (only affected areas)
- No per-frame heap allocations

## See Also

- [Usage Guide](usage.md) - Practical examples and patterns
- [Architecture](architecture.md) - Internal design for contributors
- [Platform Notes](platform-notes.md) - Platform-specific details
- [Extension Guide](extension-guide.md) - Future extensibility (v2.0+)