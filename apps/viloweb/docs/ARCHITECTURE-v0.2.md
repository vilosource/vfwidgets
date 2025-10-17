# ViloWeb v0.2 Architecture - Chrome Frameless Window

**Version**: 0.2.0
**Date**: 2025-10-17
**Status**: In Development

---

## Overview

ViloWeb v0.2 represents a major architectural shift from traditional QMainWindow to a Chrome-style frameless window using VFWidgets' `ChromeTabbedWindow` component.

---

## Architecture Comparison

### v0.1.0 (Previous)

```
┌─────────────────────────────────────────┐
│ OS Window Title Bar                     │ ← Native OS chrome
├─────────────────────────────────────────┤
│ Menu Bar (File | Bookmarks | Help)      │
├─────────────────────────────────────────┤
│ Toolbar (Back Forward Reload Stop...)   │
├─────────────────────────────────────────┤
│ ┌─────┬─────┬─────┐                     │
│ │Tab 1│Tab 2│Tab 3│ [+]                 │ ← QTabWidget tabs
│ ├─────┴─────┴─────┴─────────────────────┤
│ │                                        │
│ │ Browser Content (QWebEngineView)      │
│ │                                        │
│ └────────────────────────────────────────┘
├─────────────────────────────────────────┤
│ Status Bar                               │
└─────────────────────────────────────────┘

Components:
- QMainWindow as base
- QTabWidget for tabs
- QMenuBar for menus
- QToolBar for navigation
- Standard OS window frame
```

### v0.2.0 (New)

```
┌─────────────────────────────────────────┐
│☰ Tab1 Tab2 Tab3 [+]          [─][□][×]│ ← All in ONE row!
│                                         │    (ChromeTabbedWindow)
├─────────────────────────────────────────┤
│                                         │
│ Browser Content (QWebEngineView)        │
│                                         │
│                                         │
└─────────────────────────────────────────┘

Components:
- ChromeTabbedWindow as base (no parent = frameless)
- Chrome-style tabs with compression
- Hamburger menu (☰) as corner widget
- Window controls ([─][□][×]) built-in
- No OS window frame
```

---

## Component Architecture

### Class Hierarchy

```
ChromeTabbedWindow (from chrome-tabbed-window widget)
├── ThemedWidget (mixin from vfwidgets-theme)
├── QWidget (base)
└── FramelessWindowBehavior (composition)

ChromeMainWindow (viloweb.ui.chrome_main_window)
└── ChromeTabbedWindow
    ├── _tab_bar: ChromeTabBar (built-in)
    ├── _content_area: TabContentArea (built-in)
    ├── _window_controls: WindowControls (built-in, frameless mode only)
    ├── _hamburger_menu: QToolButton + QMenu (custom, corner widget)
    ├── _bookmark_manager: BookmarkManager (reused from v0.1)
    ├── _bridge: ViloWebBridge (reused from v0.1)
    ├── _channel: QWebChannel (shared across tabs)
    └── _browser_tabs: List[BrowserTab] (tracking)
```

### Component Responsibilities

#### ChromeTabbedWindow (provided by widget)
**Responsibilities**:
- Chrome-style tab rendering with compression
- Frameless window mode (when parent=None)
- Window controls (minimize, maximize, close)
- Drag-to-move window functionality
- Edge resizing
- Theme integration (ThemedWidget mixin)
- QTabWidget-compatible API

**Does NOT Provide**:
- Hamburger menu (we add as corner widget)
- Browser-specific logic (we add via ChromeMainWindow)

#### ChromeMainWindow (custom implementation)
**Responsibilities**:
- Extend ChromeTabbedWindow with browser functionality
- Create and manage BrowserTab instances
- Setup hamburger menu with browser actions
- Share QWebChannel across all tabs
- Integrate bookmark manager
- Handle tab lifecycle (create, close, track)
- Connect signals between tabs and UI

**Key Methods**:
```python
def __init__(self):
    """Initialize frameless browser window."""

def _setup_hamburger_menu(self):
    """Create hamburger menu with browser actions."""

def _on_new_tab_requested(self):
    """Override to create browser tab (not placeholder)."""

def new_browser_tab(self, url: str) -> BrowserTab:
    """Create new browser tab with QWebChannel."""

def _add_bookmark(self):
    """Add current page to bookmarks."""

def _show_bookmarks(self):
    """Show bookmarks dialog."""
```

#### BrowserTab (reused from v0.1)
**Responsibilities**:
- Wrap BrowserWidget from vfwidgets-webview
- Forward signals (title_changed, icon_changed, url_changed)
- Provide navigation methods (back, forward, reload)
- Manage tab-specific state

**No Changes Needed**: Works identically in v0.2

#### BookmarkManager (reused from v0.1)
**Responsibilities**:
- JSON-based bookmark storage
- Add, remove, search bookmarks
- Import/export functionality
- Atomic file writes

**No Changes Needed**: Works identically in v0.2

#### ViloWebBridge (reused from v0.1)
**Responsibilities**:
- QWebChannel bridge for Python↔JavaScript
- Expose bookmark actions to JavaScript
- Logging from JavaScript console

**No Changes Needed**: Works identically in v0.2

---

## Data Flow

### Tab Creation Flow

```
User Action: Click "+" or Ctrl+T
    ↓
ChromeMainWindow._on_new_tab_requested()
    ↓
ChromeMainWindow.new_browser_tab("about:blank")
    ↓
├─→ Create BrowserTab(parent=self)
│       ↓
│   BrowserTab creates BrowserWidget
│       ↓
│   BrowserWidget creates QWebEngineView
│
├─→ Setup QWebChannel
│   ├─→ First tab: WebChannelHelper.setup_channel() → creates QWebChannel
│   └─→ Other tabs: page().setWebChannel(existing_channel) → reuses
│
├─→ Connect signals
│   ├─→ title_changed → update tab title
│   ├─→ icon_changed → update tab icon
│   └─→ url_changed → track navigation
│
├─→ Add to ChromeTabbedWindow
│   └─→ self.addTab(tab.widget, "New Tab")
│
└─→ Navigate to URL
    └─→ tab.navigate(url)
```

### QWebChannel Sharing Pattern

```
Tab 1 Created:
    ChromeMainWindow._channel = WebChannelHelper.setup_channel(...)
    ↓
    QWebChannel created
    ↓
    ViloWebBridge registered as "viloWeb"
    ↓
    Tab 1 page.setWebChannel(channel)

Tab 2 Created:
    ChromeMainWindow._channel already exists
    ↓
    Tab 2 page.setWebChannel(ChromeMainWindow._channel)  ← Reuse!
    ↓
    Both tabs share same channel and bridge

JavaScript in Tab 1:
    window.viloWeb.log_from_js("info", "Hello from tab 1")

JavaScript in Tab 2:
    window.viloWeb.log_from_js("info", "Hello from tab 2")

Both call same Python ViloWebBridge instance ✓
```

**Why This Works**:
- QWebChannel can be shared across multiple QWebEnginePage instances
- JavaScript in each page gets its own `window.viloWeb` object
- All pages call the same Python bridge object
- Prevents "double registration" crash from v0.1

---

## Frameless Window Mechanics

### Mode Detection

```python
class ChromeTabbedWindow:
    def _detect_window_mode(self) -> WindowMode:
        if self.parent() is None:
            return WindowMode.Frameless  # Top-level widget
        else:
            return WindowMode.Embedded    # Child widget
```

### Frameless Features

When `WindowMode.Frameless`:

1. **Window Flags Set**:
   ```python
   self.setWindowFlags(Qt.FramelessWindowHint)
   ```

2. **Window Controls Added**:
   ```python
   self._window_controls = WindowControls(self)
   # Adds minimize, maximize, close buttons to tab bar
   ```

3. **Frameless Behavior Initialized**:
   ```python
   self._frameless_behavior = FramelessWindowBehavior(
       draggable_widget=self._tab_bar,
       resize_margin=4,
       enable_resize=True,
   )
   ```

4. **Mouse Events Routed**:
   ```python
   def mousePressEvent(self, event):
       if self._frameless_behavior.handle_press(self, event):
           return  # Handled by frameless behavior
       super().mousePressEvent(event)
   ```

### Drag and Resize

**Window Dragging**:
- Click and drag tab bar → `window.startSystemMove()`
- Wayland-compatible, native window manager integration
- Fallback to manual position tracking on older platforms

**Edge Resizing**:
- 4px margin around window edge
- Cursor changes to resize cursor near edges
- Click edge → `window.startSystemResize(edge)`
- Works on corners (diagonal resize) and edges

---

## Theme Integration

### Theme Flow

```
Application Startup
    ↓
ViloWebApplication.__init__()
    ↓
ThemedApplication created (from vfwidgets-theme)
    ↓
ViloWebApplication._setup_theme()
    ↓
Load "dark" theme
    ↓
ThemedApplication.set_theme(dark_theme)
    ↓
ChromeMainWindow created
    ↓
ChromeTabbedWindow inherits ThemedWidget
    ↓
_on_theme_changed() called automatically
    ↓
├─→ Tab bar updates colors
├─→ Window controls update colors
└─→ Background updates color
```

### Theme Tokens

ChromeTabbedWindow uses these theme tokens:

```python
theme_config = {
    "tab_background": "tab.activeBackground",
    "tab_inactive_background": "tab.inactiveBackground",
    "tab_hover_background": "tab.hoverBackground",
    "tab_border": "tab.border",
    "tab_active_foreground": "tab.activeForeground",
    "tab_inactive_foreground": "tab.inactiveForeground",
    "background": "editorGroupHeader.tabsBackground",
    "border": "editorGroupHeader.tabsBorder",
}
```

Window controls auto-detect dark/light theme and style accordingly.

---

## Migration Path

### From v0.1 to v0.2

**Breaking Changes**:
- MainWindow class replaced with ChromeMainWindow
- No QMenuBar (hamburger menu instead)
- No QToolBar (actions in hamburger menu)
- No QStatusBar (removed in v0.2)

**Backwards Compatible**:
- BrowserTab API unchanged
- BookmarkManager API unchanged
- ViloWebBridge API unchanged
- QWebChannel setup improved (but compatible)

**Migration Steps**:
1. Update application.py to use ChromeMainWindow
2. All existing browser logic works as-is
3. Tests may need UI interaction updates

---

## File Structure

```
apps/viloweb/
├── src/viloweb/
│   ├── __init__.py              (updated: export ChromeMainWindow)
│   ├── __main__.py              (no changes)
│   ├── application.py           (updated: use ChromeMainWindow, dark theme)
│   ├── browser/
│   │   ├── browser_tab.py       (no changes - reused)
│   │   └── viloweb_bridge.py    (no changes - reused)
│   ├── managers/
│   │   └── bookmark_manager.py  (no changes - reused)
│   └── ui/
│       ├── chrome_main_window.py (NEW - main implementation)
│       └── main_window.py       (OLD - can be kept for reference)
├── docs/
│   └── ARCHITECTURE-v0.2.md     (NEW - this document)
├── wip/
│   └── chrome-frameless-IMPLEMENTATION.md (NEW - task list)
└── README.md                    (updated)
```

---

## Dependencies

### New Dependencies (v0.2)
- `chrome-tabbed-window` >= 0.1.0 (VFWidgets widget)

### Existing Dependencies
- `vfwidgets-webview` >= 0.2.0
- `vfwidgets-theme-system`
- `vfwidgets-common` (provides FramelessWindowBehavior)
- `PySide6` >= 6.9.0

### Dependency Graph

```
viloweb (0.2.0)
├── chrome-tabbed-window
│   ├── vfwidgets-common (FramelessWindowBehavior)
│   └── vfwidgets-theme (ThemedWidget mixin)
├── vfwidgets-webview
│   └── PySide6.QtWebEngineCore
├── vfwidgets-theme-system
└── PySide6 >= 6.9.0
```

---

## Testing Strategy

### Unit Tests
- Test ChromeMainWindow initialization
- Test tab creation/removal
- Test QWebChannel sharing
- Test bookmark integration
- Test signal connections

### Integration Tests
- Test frameless window behavior
- Test theme switching
- Test multiple tabs
- Test keyboard shortcuts
- Test menu actions

### Manual Tests
- Visual inspection (Chrome-like appearance)
- Window dragging and resizing
- Theme switching
- Cross-platform testing (Windows, macOS, Linux)

---

## Performance Considerations

### Optimizations
- QWebChannel shared across tabs (vs one per tab)
- Chrome tab compression reduces memory (vs fixed-width tabs)
- ThemedWidget caching reduces theme application time

### Known Limitations
- Tab compression requires recalculation on add/remove
- Frameless window may have slight startup delay on some platforms

---

## Future Enhancements

### v0.3.0 - Advanced Tab Management
- Tab detach/reattach to new window
- Tab drag between windows
- Tab groups/pinning

### v0.4.0 - Browser Features
- Download manager
- History view
- Developer tools integration
- Custom new tab page

### v0.5.0 - Extension System
- Plugin architecture
- User scripts
- Content scripts
- Background workers

---

## References

### Related Documentation
- [ChromeTabbedWindow Specification](../../../widgets/chrome-tabbed-window/docs/chrome-tabbed-window-SPECIFICATION.md)
- [FramelessWindow Guide](../../../shared/vfwidgets_common/docs/frameless-window-GUIDE.md)
- [Theme System Guide](../../../widgets/theme_system/README.md)
- [WebView Widget Guide](../../../widgets/webview_widget/README.md)

### Example Code
- [ChromeTabbedWindow Frameless Example](../../../widgets/chrome-tabbed-window/examples/02_frameless_chrome.py)
- [ViloxTerm Frameless Implementation](../../../tmp/viloxterm/packages/viloapp/src/viloapp/ui/frameless_window.py)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-17
**Author**: Claude Code
**Status**: Complete
