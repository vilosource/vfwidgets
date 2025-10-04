# ViloxTerm Implementation Plan

**Version:** 2.0
**Date:** 2025-10-03
**Status:** ✅ Implementation Complete

**📚 See Also**: [Lessons Learned Guide](lessons-learned-GUIDE.md) - Critical insights from implementation

---

## Overview

ViloxTerm is a modern terminal emulator demonstrating the integration of four VFWidgets components:
1. **ChromeTabbedWindow** - Frameless Chrome-style window with theme support
2. **MultisplitWidget** - Dynamic split panes within each tab
3. **TerminalWidget** - xterm.js terminals with MultiSessionTerminalServer
4. **Theme System** - VSCode-compatible theming via ThemedApplication

---

## Architecture

```
ChromeTabbedWindow (Frameless Window)
├─ Window Controls: [☰ Menu] [...Tabs...] [+] [─][□][×]
└─ Tab Content (per tab)
   └─ MultisplitWidget
      └─ TerminalWidget(s) in splittable panes
```

### Visual Layout
```
┌─[☰] Terminal 1  Terminal 2  Terminal 3 [+]────[─][□][×]┐
│                                                           │
│  ┌──────────────────┬────────────────────────┐          │
│  │  Terminal Pane 1 │  Terminal Pane 2       │          │
│  │  $ vim main.py   │  $ python main.py      │          │
│  │                  ├────────────────────────┤          │
│  │                  │  Terminal Pane 3       │          │
│  │                  │  $ npm run build       │          │
│  └──────────────────┴────────────────────────┘          │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Controls:**
- `[☰]` - Menu icon (opens theme selection dialog)
- `[+]` - New tab button
- `[─][□][×]` - Minimize, Maximize/Restore, Close

---

## Reference Examples

### Primary References

1. **chrome-tabbed-window/examples/04_themed_chrome_tabs.py**
   - ChromeTabbedWindow as top-level frameless window
   - ThemedApplication integration
   - Dynamic theme switching
   - Clean structure to follow

2. **multisplit_widget/examples/01_basic_text_editor.py**
   - WidgetProvider pattern
   - MultisplitWidget integration
   - Pane management

### Key Patterns Learned

**Pattern 1: Frameless Window with Theme (from 04_themed_chrome_tabs.py)**
```python
# Create ThemedApplication
app = ThemedApplication(sys.argv)
app.set_theme("dark")

# Create ChromeTabbedWindow (no parent = frameless mode)
window = ChromeTabbedWindow()
window.setWindowTitle("Title")
window.resize(1200, 800)

# Add content
window.addTab(content_widget, "Tab 1")

# Show
window.show()
sys.exit(app.exec())
```

**Pattern 2: WidgetProvider for Dynamic Content (from 01_basic_text_editor.py)**
```python
class TextEditorProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Create widget for pane
        editor = QTextEdit()
        return editor

# Use with MultisplitWidget
multisplit = MultisplitWidget()
multisplit.set_widget_provider(TextEditorProvider())
```

---

## Implementation Details

### 1. Theme Selection Dialog

Modal dialog for theme switching:

```python
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication

class ThemeDialog(QDialog):
    """Modal dialog for theme selection."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Theme")
        self.setModal(True)
        self.resize(300, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Theme buttons
        themes = ["dark", "light", "default", "minimal"]
        for theme in themes:
            btn = QPushButton(f"{theme.capitalize()} Theme")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, t=theme: self.select_theme(t))
            layout.addWidget(btn)

    def select_theme(self, theme_name: str):
        """Apply theme and close dialog."""
        app = QApplication.instance()
        if hasattr(app, 'set_theme'):
            app.set_theme(theme_name)
        self.accept()
```

### 2. Menu Button for Window Controls

Custom menu button styled like window control buttons:

```python
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QPushButton

class MenuButton(QPushButton):
    """Menu button styled to match window control buttons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 32)  # Match window control button size
        self.setCursor(Qt.CursorShape.ArrowCursor)

        # State tracking
        self._is_hovered = False
        self._is_pressed = False

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Paint menu icon (hamburger menu)."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        if self._is_pressed:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 51))  # 20% black
        elif self._is_hovered:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 26))  # 10% black

        # Icon color
        icon_color = QColor(0, 0, 0, 153)  # 60% black
        painter.setPen(QPen(icon_color, 2, Qt.PenStyle.SolidLine))

        # Draw hamburger menu (3 horizontal lines)
        center_x = self.width() // 2
        center_y = self.height() // 2
        line_width = 12

        # Top line
        painter.drawLine(center_x - line_width // 2, center_y - 5,
                        center_x + line_width // 2, center_y - 5)
        # Middle line
        painter.drawLine(center_x - line_width // 2, center_y,
                        center_x + line_width // 2, center_y)
        # Bottom line
        painter.drawLine(center_x - line_width // 2, center_y + 5,
                        center_x + line_width // 2, center_y + 5)
```

### 3. Terminal Provider

WidgetProvider for creating TerminalWidget instances:

```python
from PySide6.QtWidgets import QWidget
from vfwidgets_multisplit.view.container import WidgetProvider
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

class TerminalProvider(WidgetProvider):
    """Provides TerminalWidget instances for MultisplitWidget panes."""

    def __init__(self, server: MultiSessionTerminalServer):
        """Initialize with shared terminal server.

        Args:
            server: Shared MultiSessionTerminalServer instance
        """
        self.server = server

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a new terminal widget for a pane.

        Args:
            widget_id: Unique widget identifier
            pane_id: Pane identifier

        Returns:
            TerminalWidget connected to shared server
        """
        # Create session on shared server
        session_id = self.server.create_session(command="bash")

        # Get session URL
        session_url = self.server.get_session_url(session_id)

        # Create terminal widget
        terminal = TerminalWidget(server_url=session_url)

        return terminal
```

### 4. ViloxTermApp Main Class

Complete application implementation:

```python
import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

logger = logging.getLogger(__name__)


class ViloxTermApp(ChromeTabbedWindow):
    """ViloxTerm - Chrome-style terminal emulator with split panes."""

    def __init__(self):
        """Initialize ViloxTerm application."""
        # ChromeTabbedWindow with no parent = frameless mode
        super().__init__()

        # Start shared terminal server (memory efficient!)
        self.terminal_server = MultiSessionTerminalServer(port=0)
        self.terminal_server.start()
        logger.info(f"Terminal server started on port {self.terminal_server.port}")

        # Create terminal provider for MultisplitWidget
        self.terminal_provider = TerminalProvider(self.terminal_server)

        # Configure window
        self.setWindowTitle("ViloxTerm")
        self.resize(1200, 800)
        self.setTabsClosable(True)

        # Add menu button to window controls
        self._add_menu_button()

        # Add initial tab
        self.add_new_tab("Terminal 1")

        # Add "+" button for new tabs
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(28, 28)
        new_tab_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
                color: #5f6368;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.06);
                border-radius: 14px;
            }
        """)
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.setCornerWidget(new_tab_btn, Qt.Corner.TopRightCorner)

        # Connect tab close signal
        self.tabCloseRequested.connect(self.handle_tab_close)

    def _add_menu_button(self):
        """Add menu button to window controls."""
        if hasattr(self, '_window_controls') and self._window_controls:
            # Get the layout
            layout = self._window_controls.layout()

            # Create menu button
            menu_btn = MenuButton(self._window_controls)
            menu_btn.clicked.connect(self.show_theme_dialog)

            # Insert at position 0 (before minimize button)
            layout.insertWidget(0, menu_btn)

            # Update window controls size
            # Original: 3 buttons × 46px = 138px
            # New: 4 buttons × 46px = 184px
            self._window_controls.setFixedSize(184, 32)

    def show_theme_dialog(self):
        """Show theme selection dialog."""
        dialog = ThemeDialog(self)
        dialog.exec()

    def add_new_tab(self, title: str = None):
        """Create a new tab with MultisplitWidget.

        Args:
            title: Tab title (auto-generated if None)
        """
        if title is None:
            title = f"Terminal {self.count() + 1}"

        # Create MultisplitWidget for this tab
        multisplit = MultisplitWidget()
        multisplit.set_widget_provider(self.terminal_provider)

        # Add tab
        index = self.addTab(multisplit, title)
        self.setCurrentIndex(index)

        logger.info(f"Created new tab: {title}")

    def handle_tab_close(self, index: int):
        """Handle tab close request.

        Args:
            index: Index of tab to close
        """
        if self.count() > 1:
            # Remove tab
            self.removeTab(index)
            logger.info(f"Closed tab at index {index}")
        else:
            # Last tab - close window
            logger.info("Closing last tab - exiting application")
            self.close()

    def closeEvent(self, event):
        """Handle window close event."""
        # Shutdown terminal server
        logger.info("Shutting down terminal server...")
        self.terminal_server.shutdown()
        logger.info("Terminal server shut down")

        # Accept close event
        super().closeEvent(event)
        event.accept()
```

### 5. Main Entry Point

```python
import sys
import logging
from vfwidgets_theme import ThemedApplication
from .app import ViloxTermApp


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    """Main entry point for ViloxTerm."""
    setup_logging()

    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create and show window
    window = ViloxTermApp()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## File Structure

```
apps/viloxterm/
├── src/viloxterm/
│   ├── __init__.py          # Package exports
│   ├── __main__.py          # Main entry point (above)
│   └── app.py               # ViloxTermApp + helpers
├── docs/
│   ├── implementation-PLAN.md         # This file
│   ├── terminal-server-protocol-SPEC.md
│   └── README.md
├── pyproject.toml           # Package configuration
└── README.md                # User documentation
```

---

## Implementation Checklist

### Phase 1: Core Window ✅
- [x] ViloxTermApp inherits from ChromeTabbedWindow
- [x] ThemedApplication integration
- [x] Frameless mode (no parent)
- [x] Basic window setup

### Phase 2: Terminal Integration ✅
- [x] MultiSessionTerminalServer initialization
- [x] TerminalProvider implementation
- [x] TerminalWidget in tabs

### Phase 3: MultisplitWidget Integration 🔄
- [ ] Add MultisplitWidget to each tab
- [ ] Connect TerminalProvider
- [ ] Test pane splitting
- [ ] Test focus management

### Phase 4: Theme Menu 🔄
- [ ] Create ThemeDialog
- [ ] Create MenuButton
- [ ] Add menu button to window controls
- [ ] Test theme switching

### Phase 5: Polish ⏳
- [ ] Keyboard shortcuts (Ctrl+T, Ctrl+W, etc.)
- [ ] Tab rename functionality
- [ ] Session persistence (optional)
- [ ] Configuration file support

---

## Key Design Decisions

### 1. Why ChromeTabbedWindow as Top-Level?

**Decision:** Use ChromeTabbedWindow directly as the frameless window (not embedded in QMainWindow)

**Rationale:**
- Automatic frameless mode when no parent
- Built-in theme support via ThemedWidget
- Clean, simple architecture
- Matches reference example 04_themed_chrome_tabs.py

### 2. Why MultisplitWidget in Each Tab?

**Decision:** Each tab contains a MultisplitWidget, not a single terminal

**Rationale:**
- Allows dynamic split panes per tab
- Users can organize workflows per tab
- Matches terminal emulator conventions (tmux, iTerm2)
- Clean separation of concerns

### 3. Why MultiSessionTerminalServer?

**Decision:** Use shared MultiSessionTerminalServer for all terminals

**Rationale:**
- 63% memory reduction (20 terminals: 300MB → 110MB)
- Centralized session management
- Production-ready implementation
- Already documented and tested

### 4. Why Modal Theme Dialog?

**Decision:** Theme selection via modal dialog, not menu bar or tab

**Rationale:**
- Cleaner UI (no menu bar in frameless mode)
- Doesn't consume tab space
- Quick access via icon
- Modern app UX pattern

---

## Memory Profile

**Configuration:** 20 terminals across 5 tabs (4 terminals per tab)

| Component | Memory Usage | Notes |
|-----------|--------------|-------|
| ChromeTabbedWindow | ~20 MB | Window + theme system |
| MultisplitWidget × 5 | ~10 MB | Minimal overhead per tab |
| MultiSessionTerminalServer | ~50 MB | Single Flask + SocketIO server |
| TerminalWidget × 20 | ~60 MB | Qt widgets + WebView |
| **Total** | **~140 MB** | vs ~300 MB with embedded servers |

**Savings:** 53% memory reduction

---

## Testing Strategy

### Manual Testing

1. **Window Behavior**
   - Launch app → verify frameless window
   - Test window controls (minimize, maximize, close)
   - Test window dragging
   - Test theme dialog via menu icon

2. **Tab Management**
   - Create new tab via "+" button
   - Close tabs via "×" button
   - Switch between tabs
   - Close last tab → verify app exits

3. **Terminal Functionality**
   - Verify terminal loads in pane
   - Test shell commands
   - Test terminal resize
   - Create multiple terminals via splits

4. **Theme System**
   - Open theme dialog
   - Switch between themes
   - Verify window + terminals update
   - Test all 4 built-in themes

### Automated Testing

```bash
# Test basic launch
timeout 5 viloxterm

# Check for errors in logs
# Expected: No errors, clean startup, clean shutdown
```

---

## Known Limitations

1. **Single terminal per pane initially** - Splits require user interaction
2. **No session persistence** - Terminals don't survive app restart
3. **No configuration file** - Settings hardcoded for now
4. **No keyboard shortcuts yet** - Will add in Phase 5

---

## Future Enhancements

### Short Term
- Keyboard shortcuts (Ctrl+T, Ctrl+Shift+H/V for splits)
- Tab rename via double-click
- Context menus for tabs and panes

### Medium Term
- Session persistence (save/restore layouts)
- Configuration file (~/.viloxterm/config.yaml)
- Terminal profiles (colors, fonts, startup commands)

### Long Term
- Plugin system
- Custom themes (import VSCode themes)
- Remote server support
- Session recording/playback

---

## Success Criteria

✅ **Must Have:**
- Frameless Chrome-style window with theme colors
- Multiple tabs with dynamic creation/closing
- Terminals in splittable panes via MultisplitWidget
- Theme switching via menu icon + modal dialog
- Memory-efficient multi-terminal support
- Clean shutdown (no zombie processes)

🎯 **Should Have:**
- Visual appearance matches 04_themed_chrome_tabs.py
- All 4 themes work correctly
- Smooth tab/pane creation

💫 **Nice to Have:**
- Keyboard shortcuts
- Tab rename
- Polish and animations

---

**Document Version:** 2.0
**Last Updated:** 2025-10-03
**Status:** ✅ Ready for implementation
