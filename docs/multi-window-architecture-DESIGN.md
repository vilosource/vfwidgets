# Multi-Window Architecture Design

**Decision Document: Where Should "New Window" Functionality Live?**

Date: 2025-10-08
Status: Proposed
Context: Adding ability to open new windows in ViloxTerm

---

## Question

Should "New Window" functionality be implemented in:
- **Option A**: ChromeTabbedWindow widget library (generic widget)
- **Option B**: ViloxTerm application layer (application-specific)

## Analysis

### Qt's Pattern (WebEngine Simple Browser Example)

Qt's official browser example demonstrates the industry-standard pattern:

```
Browser (Application Manager)
├── createWindow() method
├── createHiddenWindow() method
└── Owns all BrowserWindow instances
    └── Each BrowserWindow contains TabWidget (QTabWidget)
        └── TabWidget manages tabs, NOT windows
```

**Key Insight**: QTabWidget does NOT create or manage windows. A higher-level application class does.

**Source**: https://doc.qt.io/qt-6/qtwebengine-webenginewidgets-simplebrowser-example.html

### Chrome Browser Architecture

From Chromium documentation:
- **Browser class** - Owns and manages browser windows
- **BrowserWindow class** - Individual window instances
- **TabStrip** - Just manages tabs within a window
- Window creation is application-level, not widget-level

**Source**: https://www.chromium.org/developers/design-documents/browser-window/

### Single Responsibility Principle

**ChromeTabbedWindow Responsibilities:**
- ✅ Manage tabs within ONE window
- ✅ Render Chrome-style UI
- ✅ Provide QTabWidget-compatible API
- ✅ Emit signals for user actions
- ❌ Create new window instances
- ❌ Manage window lifecycle
- ❌ Handle application resources

**ViloxTermApp Responsibilities:**
- ✅ Create and manage multiple window instances
- ✅ Handle application resources (terminal_server, theme_manager)
- ✅ Decide window creation strategy (shared vs independent)
- ✅ Track window lifecycle
- ✅ Handle cleanup and shutdown

### Content-Agnostic Widget Design

ChromeTabbedWindow is a **general-purpose widget** that could be used in:
- Terminal applications (ViloxTerm)
- Text editors (multi-document editors)
- Web browsers (browser tabs)
- Image viewers (image tabs)
- Any tabbed application

**Problem**: Each application needs different window creation logic:
- ViloxTerm: Share terminal server? Track sessions?
- Text Editor: Share document manager? Handle unsaved changes?
- Browser: Share profile? Private browsing mode?

**Conclusion**: Widget cannot know application-specific requirements.

---

## Decision: **Option B - Application Layer Implementation**

**Rationale:**
1. Follows Qt/Chrome industry patterns
2. Maintains single responsibility principle
3. Keeps ChromeTabbedWindow reusable and content-agnostic
4. Allows application-specific customization
5. Matches existing architecture (Browser class pattern)

---

## Recommended Architecture

### Layer 1: ChromeTabbedWindow (Widget Library)

**What to Add:**

```python
class ChromeTabbedWindow(QWidget):
    # New signals for applications to handle
    newWindowRequested = Signal()  # User clicked "New Window"
    tabDetachRequested = Signal(int)  # User wants to detach tab index

    # Helper method for tab transfer
    def get_tab_data(self, index: int) -> dict:
        """Get tab data for transfer to another window.

        Returns:
            dict with keys: widget, text, icon, tooltip
        """
        return {
            "widget": self.widget(index),
            "text": self.tabText(index),
            "icon": self.tabIcon(index),
            "tooltip": self.tabToolTip(index)
        }

    # Optional: Context menu on tab bar
    def _show_tab_context_menu(self, index: int, pos: QPoint):
        """Show context menu for tab (right-click)."""
        menu = QMenu(self)
        menu.addAction("Open in New Window", lambda: self.newWindowRequested.emit())
        menu.exec(pos)
```

**What ChromeTabbedWindow Provides:**
- ✅ Signals when user wants new window
- ✅ Context menu infrastructure (optional)
- ✅ Helper methods to extract tab data
- ✅ Tab bar right-click support

**What ChromeTabbedWindow Does NOT Do:**
- ❌ Create new window instances
- ❌ Manage window lifecycle
- ❌ Handle shared resources
- ❌ Know anything about application context

### Layer 2: ViloxTerm (Application)

**Implementation:**

```python
class ViloxTermApp(ChromeTabbedWindow):
    """ViloxTerm application - manages windows and application resources."""

    def __init__(self, shared_server=None, parent=None):
        super().__init__(parent)

        # Application-level resource management
        if shared_server:
            # Share server with other windows
            self.terminal_server = shared_server
            self._owns_server = False
        else:
            # Create own server (first window)
            self.terminal_server = MultiSessionTerminalServer(port=0)
            self.terminal_server.start()
            self._owns_server = True

        # Track child windows (prevent garbage collection)
        self._child_windows = []

        # Connect widget signals to application handlers
        self.newWindowRequested.connect(self._open_new_window)
        self.tabDetachRequested.connect(self._detach_tab_to_window)

        # Other initialization...
        self._setup_terminal_managers()
        self._setup_menu()

    def _open_new_window(self):
        """Application-level window creation logic."""
        # Decide: Share server or create new one?
        # Option A: Share server (memory efficient)
        new_window = ViloxTermApp(shared_server=self.terminal_server)

        # Option B: Independent server (isolated)
        # new_window = ViloxTermApp(shared_server=None)

        # Track window to prevent garbage collection
        self._child_windows.append(new_window)

        # Handle cleanup when child closes
        new_window.destroyed.connect(
            lambda: self._on_child_window_closed(new_window)
        )

        # Show the window
        new_window.show()

    def _detach_tab_to_window(self, index: int):
        """Move tab to new window (future implementation)."""
        # Get tab data using widget helper
        tab_data = self.get_tab_data(index)

        # Create new window
        new_window = ViloxTermApp(shared_server=self.terminal_server)

        # Transfer tab
        self.removeTab(index)  # Remove from source
        new_window.addTab(
            tab_data["widget"],
            tab_data["text"],
            tab_data["icon"]
        )

        # Track and show
        self._child_windows.append(new_window)
        new_window.show()

    def _on_child_window_closed(self, window):
        """Cleanup when child window closes."""
        if window in self._child_windows:
            self._child_windows.remove(window)

    def closeEvent(self, event):
        """Handle application shutdown."""
        # If this window owns the server, shut it down
        if self._owns_server:
            self.terminal_server.shutdown()

        super().closeEvent(event)
```

---

## Implementation Plan

### Phase 1: ChromeTabbedWindow Enhancements

**Files to Modify:**
- `widgets/chrome-tabbed-window/src/chrome_tabbed_window/chrome_tabbed_window.py`
- `widgets/chrome-tabbed-window/src/chrome_tabbed_window/view/chrome_tab_bar.py`

**Changes:**

1. **Add signals:**
   ```python
   class ChromeTabbedWindow:
       newWindowRequested = Signal()
       tabDetachRequested = Signal(int)
   ```

2. **Add helper method:**
   ```python
   def get_tab_data(self, index: int) -> dict:
       """Extract tab data for transfer."""
   ```

3. **Add context menu support (optional):**
   - Right-click on tab shows menu
   - "Open in New Window" option
   - Emits `newWindowRequested`

### Phase 2: ViloxTerm Application Logic

**Files to Modify:**
- `apps/viloxterm/src/viloxterm/app.py`
- `apps/viloxterm/src/viloxterm/components/menu_button.py`

**Changes:**

1. **Add menu item:**
   - "New Window" in hamburger menu
   - Keyboard shortcut: Ctrl+Shift+N (optional)

2. **Connect signals:**
   ```python
   self.newWindowRequested.connect(self._open_new_window)
   ```

3. **Implement window management:**
   - `_open_new_window()` method
   - `_child_windows` list for tracking
   - `_on_child_window_closed()` cleanup

4. **Server strategy decision:**
   - **Option A**: Share server (recommended for now)
   - **Option B**: Independent servers
   - Make configurable if needed

### Phase 3: Testing

**Test Scenarios:**

1. **Basic window creation:**
   - Open ViloxTerm
   - Menu → "New Window"
   - Verify second window appears

2. **Terminal functionality:**
   - Create terminal in each window
   - Run commands in both
   - Verify both work independently

3. **Window independence:**
   - Close one window
   - Verify other stays open
   - Verify terminals keep working

4. **Clean shutdown:**
   - Close all windows
   - Verify no zombie processes
   - Verify server shuts down cleanly

5. **Theme system:**
   - Change theme in one window
   - Verify saved to config
   - Open new window
   - Verify theme is loaded

---

## Benefits of This Architecture

### For ChromeTabbedWindow Widget

✅ **Reusable** - Can be used in any tabbed application
✅ **Simple** - Focused on tab management only
✅ **Testable** - Can test widget independently
✅ **Maintainable** - Clear responsibilities
✅ **Compatible** - Matches QTabWidget pattern

### For ViloxTerm Application

✅ **Flexible** - Full control over window creation
✅ **Customizable** - Application-specific logic
✅ **Resource Management** - Controls server lifecycle
✅ **Future-Proof** - Easy to add features like:
  - Tab detachment (drag to new window)
  - Window merging
  - Session persistence
  - Multi-monitor support

---

## Alternative Approaches (Rejected)

### Approach 1: ChromeTabbedWindow Creates Windows ❌

**Why Rejected:**
- Violates single responsibility
- Makes widget application-specific
- Cannot handle shared resources
- Not reusable in other applications

### Approach 2: Global Window Manager Class ❌

**Why Rejected:**
- Adds unnecessary complexity
- Global state is hard to test
- Doesn't match Qt patterns
- Overkill for this use case

---

## Future Enhancements

Once basic window creation works, we can add:

### Phase 4: Tab Detachment
- Drag tab out of tab bar → new window
- Drag tab back → reattach
- Uses `tabDetachRequested` signal

### Phase 5: Advanced Features
- Remember window positions
- "Merge All Windows" option
- Session persistence across restarts
- Multi-monitor window placement

---

## References

- Qt Simple Browser Example: https://doc.qt.io/qt-6/qtwebengine-webenginewidgets-simplebrowser-example.html
- Chromium Browser Window Design: https://www.chromium.org/developers/design-documents/browser-window/
- Qt QTabWidget Documentation: https://doc.qt.io/qt-6/qtabwidget.html
- Our research findings: See conversation history 2025-10-08

---

## Decision Status

**Status**: ✅ Approved for Implementation
**Next Steps**: Implement Phase 1 (ChromeTabbedWindow signals)
**Approved By**: User (2025-10-08)
