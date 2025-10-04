# ViloxTerm Implementation Lessons Learned

**Document Purpose**: Critical insights from building ViloxTerm - a multi-widget integration application combining ChromeTabbedWindow, MultisplitWidget, TerminalWidget, and Theme System.

**Created From**: Real-world implementation experience building a production-ready terminal emulator application.

**Audience**: Developers integrating multiple VFWidgets in a single application.

---

## Table of Contents

1. [ChromeTabbedWindow Integration Pitfalls](#chrometabbedwindow-integration-pitfalls)
2. [ChromeTabbedWindow Built-in New Tab Button](#chrometabbedwindow-built-in-new-tab-button)
3. [MultisplitWidget Import Paths - Check Examples First](#multisplitwidget-import-paths---check-examples-first)
4. [MultisplitWidget + WidgetProvider Pattern](#multisplitwidget--widgetprovider-pattern)
5. [Extending Window Controls Safely](#extending-window-controls-safely)
6. [Reference Example Best Practices](#reference-example-best-practices)
7. [ThemedApplication Integration](#themedapplication-integration)
8. [Debugging Multi-Widget Applications](#debugging-multi-widget-applications)

---

## ChromeTabbedWindow Integration Pitfalls

### Critical Lesson: Don't Override `_setup_ui()` Without Calling Parent

**The Problem**:
```python
# ❌ WRONG - Breaks window controls
class MyApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()  # Replaces parent's UI setup!

    def _setup_ui(self):
        # Custom UI setup
        self.setWindowTitle("My App")
        # Missing: super()._setup_ui()
```

**What Happens**:
- ChromeTabbedWindow's `__init__()` calls `_setup_ui()` which creates window controls
- Your override replaces this entirely
- Window controls (`_window_controls`) are never created
- `hasattr(self, '_window_controls')` returns False or None

**The Solution**:
```python
# ✅ CORRECT - Customize after parent init
class MyApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()  # Parent creates window controls

        # Now customize the window
        self.setWindowTitle("My App")
        self.resize(1200, 800)
        self.setTabsClosable(True)

        # Access window controls safely
        if hasattr(self, '_window_controls'):
            self._customize_window_controls()
```

**Key Insight**: ChromeTabbedWindow's `_setup_ui()` is called during parent's `__init__()`. Don't override it unless you call `super()._setup_ui()` first.

### Window Mode Detection

ChromeTabbedWindow automatically detects its mode based on parent widget:

```python
def _detect_window_mode(self) -> WindowMode:
    if self.parent() is None:
        return WindowMode.Frameless  # Value: 1
    else:
        return WindowMode.Embedded    # Value: 0
```

**Implications**:
- **Frameless mode** (no parent): Creates custom window controls, frameless window
- **Embedded mode** (has parent): No window controls, normal widget behavior
- Window controls only exist when `_window_mode == WindowMode.Frameless`

**Access Window Controls Safely**:
```python
def __init__(self):
    super().__init__()  # Must complete first

    # Now window controls exist (if frameless mode)
    if self._window_mode == WindowMode.Frameless:
        # Customize window controls here
        self._customize_window_controls()
```

**Reference**: See `chrome-tabbed-window/examples/04_themed_chrome_tabs.py` for the canonical minimal example.

---

## ChromeTabbedWindow Built-in New Tab Button

### Critical Lesson: Don't Create a Custom "+" Button

**The Problem**:
```python
# ❌ WRONG - This button will never be clicked!
class MyApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()

        # Create custom "+" button
        new_tab_button = QPushButton("+")
        new_tab_button.clicked.connect(self._on_new_tab)
        self.setCornerWidget(new_tab_button, Qt.Corner.TopRightCorner)

    def _on_new_tab(self):
        # This method is NEVER called!
        self.addTab(MyWidget(), "New Tab")
```

**What Happens**:
- ChromeTabbedWindow **already has** a built-in "+" button
- It's **painted directly on the tab bar**, not a QWidget
- Clicking it calls `_on_new_tab_requested()` which creates a placeholder QLabel
- Your custom button via `setCornerWidget()` is ignored/invisible
- Result: You see "New Tab" placeholders instead of your custom widgets

**The Solution**:
```python
# ✅ CORRECT - Override the built-in handler
class MyApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()

        # Don't create a custom button!
        # ChromeTabbedWindow already has one.

        # Create your first tab
        self.add_custom_tab("Tab 1")

    def _on_new_tab_requested(self):
        """Override ChromeTabbedWindow's built-in new tab handler.

        This is called when the user clicks the built-in "+" button.
        """
        tab_count = self.count()
        self.add_custom_tab(f"Tab {tab_count + 1}")

    def add_custom_tab(self, title: str):
        """Create and add a custom tab."""
        widget = MyCustomWidget()
        self.addTab(widget, title)
```

**Key Insights**:

1. **Built-in "+" Button Location**: The "+" button is rendered by `ChromeTabBar` immediately after the last tab. It's part of the tab bar's paint event, not a separate widget.

2. **Default Behavior**: By default, clicking "+" creates:
   ```python
   widget = QLabel("New Tab")
   widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
   self.addTab(widget, "New Tab")
   ```

3. **Override Pattern**: Always override `_on_new_tab_requested()` to customize new tab creation. Do NOT create a separate button.

4. **Why This Matters**: The painted "+" button is integral to Chrome's tab bar design and cannot be replaced. It's positioned dynamically after the last tab and handles hover states internally.

**Reference**: See `chrome-tabbed-window/examples/02_frameless_chrome.py` for the default behavior, and ViloxTerm's `src/viloxterm/app.py` for the override pattern.

---

## MultisplitWidget Import Paths - Check Examples First

### Critical Lesson: WherePosition Import Error

**The Problem**:
```python
# ❌ WRONG - ImportError: cannot import name 'WherePosition'
from vfwidgets_multisplit import WherePosition

def split_pane(self):
    multisplit.split_pane(pane_id, widget_id, WherePosition.RIGHT)
```

**What Happens**:
- `WherePosition` is NOT exported from `vfwidgets_multisplit/__init__.py`
- Only `MultisplitWidget` is in `__all__`
- Runtime error when trying to use split operations

**The Solution - Check the Working Example**:
```python
# ✅ CORRECT - Import from core.types (as shown in examples)
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.core.types import WherePosition

def split_pane(self):
    multisplit.split_pane(pane_id, widget_id, WherePosition.RIGHT, 0.5)
```

**Lesson Learned**:
1. **Always check the working examples FIRST** - They show the correct import paths
2. **Don't assume package structure** - Check `__init__.py` to see what's exported
3. **Read error messages carefully** - "cannot import name" means wrong import path
4. **Test before theorizing** - Run the code to see the actual error

**Example Reference**:
- See `multisplit_widget/examples/01_basic_text_editor.py` line 46:
  ```python
  from vfwidgets_multisplit.core.types import WherePosition
  ```

**Why This Matters**:
- Without correct import, split operations fail at runtime
- Error only appears when menu actions are triggered
- Easy to miss in initial testing if you don't try splitting

**Documentation Added**:
- MultisplitWidget README now has "API Reference" section with correct import paths
- Common import error examples included

---

## MultisplitWidget + WidgetProvider Pattern

### Critical: Provider Must Be in Constructor

**The Most Common Mistake:**
```python
# ❌ WRONG - Provider not recognized!
multisplit = MultisplitWidget()
multisplit.set_widget_provider(provider)  # Method doesn't exist!
```

**The Correct Way:**
```python
# ✅ CORRECT - Provider in constructor
multisplit = MultisplitWidget(provider=provider)
```

**Why This Matters:**
- `set_widget_provider()` method does NOT exist in the MultisplitWidget API
- Provider must be passed in the `__init__()` constructor
- If provider is missing, you'll see placeholder widgets with warning: `"No provider available"`

**Reference**: See `multisplit_widget/examples/01_basic_text_editor.py` line 248

### Understanding Lazy Widget Creation

MultisplitWidget doesn't create widgets immediately - it uses a **WidgetProvider** to create them on-demand:

```python
from vfwidgets_multisplit.view.container import WidgetProvider

class TerminalProvider(WidgetProvider):
    def __init__(self, server: MultiSessionTerminalServer):
        self.server = server  # Shared resource

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Called when MultisplitWidget needs a new widget for a pane."""
        # Create session on shared server
        session_id = self.server.create_session(command="bash")
        session_url = self.server.get_session_url(session_id)

        # Return the widget
        return TerminalWidget(server_url=session_url)
```

### Key Insights

**1. Provider is Called On-Demand**
- `provide_widget()` is called when a pane is created (initial widget or after split)
- Not called during MultisplitWidget initialization
- Perfect for resource-intensive widgets (terminals, editors)

**2. Share Resources via Provider Constructor**
```python
# ✅ CORRECT - Share server across all terminals
self.terminal_server = MultiSessionTerminalServer(port=0)
self.terminal_provider = TerminalProvider(self.terminal_server)

multisplit = MultisplitWidget(provider=self.terminal_provider)
```

**3. Each Pane Gets Unique Widget**
- Every call to `provide_widget()` should return a NEW widget instance
- Don't return the same widget instance multiple times
- Use `widget_id` and `pane_id` for tracking if needed

**Memory Efficiency**:
Using a shared MultiSessionTerminalServer instead of embedded servers:
- **63% memory reduction** (measured)
- Single Flask server handles all terminal sessions
- Sessions isolated via SocketIO rooms

**Reference**: See `multisplit_widget/examples/01_basic_text_editor.py` for complete WidgetProvider pattern.

---

## Extending Window Controls Safely

### Adding Custom Buttons to Window Controls

WindowControls uses a `QHBoxLayout` internally with 3 buttons (minimize, maximize, close):

```python
# WindowControls internal structure
layout = QHBoxLayout()
layout.addWidget(minimize_button)  # Index 0
layout.addWidget(maximize_button)  # Index 1
layout.addWidget(close_button)     # Index 2
# Total width: 138px (3 buttons × 46px)
```

### How to Add a Menu Button

```python
from chrome_tabbed_window.components.window_controls import WindowControlButton

class MenuButton(WindowControlButton):
    """Custom button extending WindowControlButton base class."""

    menu_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self.menu_clicked.emit)

    def draw_icon(self, painter: QPainter):
        """Draw hamburger menu icon."""
        colors = self._get_theme_colors()
        painter.setPen(QPen(colors['icon'], 2))

        center_x = self.width() // 2
        center_y = self.height() // 2

        # Three horizontal lines
        painter.drawLine(center_x - 6, center_y - 5, center_x + 6, center_y - 5)
        painter.drawLine(center_x - 6, center_y, center_x + 6, center_y)
        painter.drawLine(center_x - 6, center_y + 5, center_x + 6, center_y + 5)
```

### Integration into ViloxTermApp

```python
class ViloxTermApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()

        # After parent init, window controls exist
        self._add_menu_button()

    def _add_menu_button(self):
        if not hasattr(self, '_window_controls') or not self._window_controls:
            return

        # Get the layout
        layout = self._window_controls.layout()

        # Create and insert menu button at beginning
        self.menu_button = MenuButton(self._window_controls)
        layout.insertWidget(0, self.menu_button)

        # Update container size (4 buttons × 46px = 184px)
        self._window_controls.setFixedSize(184, 32)

        # Connect signal
        self.menu_button.menu_clicked.connect(self._show_theme_dialog)
```

### Key Points

- **Extend WindowControlButton**: Inherit from base class for consistent styling
- **Override `draw_icon()`**: Implement custom icon drawing
- **Use `insertWidget()`**: Add at specific index (0 = leftmost)
- **Update container size**: Add 46px per additional button
- **Theme colors available**: Use `self._get_theme_colors()` for theme-aware colors

---

## Reference Example Best Practices

### Always Check Examples First

VFWidgets examples are **production-quality reference implementations**. They are:
- Minimal and focused
- Tested and working
- Follow best practices
- Show canonical usage patterns

### Example: Finding the Right Pattern

**Problem**: "How do I use ChromeTabbedWindow as a frameless window?"

**Solution Path**:
1. Check `chrome-tabbed-window/examples/`
2. Find `04_themed_chrome_tabs.py`
3. See the minimal pattern:

```python
# This is ALL you need for frameless window
app = ThemedApplication(sys.argv)
window = ChromeTabbedWindow()  # No parent = frameless!
window.setWindowTitle("My App")
window.resize(900, 600)
window.addTab(content, "Tab 1")
window.show()
sys.exit(app.exec())
```

### Common Example Patterns

| Widget | Key Example | Shows |
|--------|------------|-------|
| ChromeTabbedWindow | `04_themed_chrome_tabs.py` | Frameless window + ThemedApplication |
| MultisplitWidget | `01_basic_text_editor.py` | WidgetProvider pattern |
| TerminalWidget | `01_simple_terminal.py` | Basic terminal usage |
| TerminalWidget | `02_multi_terminal_app.py` | MultiSessionTerminalServer pattern |

### Lesson: Start Simple, Add Complexity Gradually

**Anti-pattern**:
```python
# ❌ Over-engineering from the start
class MyApp(ThemedMainWindow):
    def __init__(self):
        super().__init__()
        self.chrome_tabs = ChromeTabbedWindow()
        self.setCentralWidget(self.chrome_tabs)
        # Complex custom UI setup...
```

**Best practice**:
```python
# ✅ Start with working example pattern
class MyApp(ChromeTabbedWindow):
    def __init__(self):
        super().__init__()
        # Add features incrementally
```

---

## ThemedApplication Integration

### ChromeTabbedWindow is Already Themed

ChromeTabbedWindow inherits from `ThemedWidget`, so theme integration is automatic:

```python
# This is ALL you need
app = ThemedApplication(sys.argv)
app.set_theme("dark")

window = ChromeTabbedWindow()  # Already themed!
window.show()
```

**No special integration needed**:
- ❌ Don't create custom theme bridges
- ❌ Don't manually apply themes
- ❌ Don't override theme methods

**Theme switching just works**:
```python
# Theme switching updates all themed widgets automatically
app.set_theme("light")  # ChromeTabbedWindow updates automatically
```

### Adding Theme Switching UI

**Option 1: Theme buttons in tab content** (like `04_themed_chrome_tabs.py`):
```python
btn = QPushButton("Dark Theme")
btn.clicked.connect(lambda: app.set_theme("dark"))
```

**Option 2: Modal theme dialog** (ViloxTerm approach):
```python
class ThemeDialog(QDialog):
    def select_theme(self, theme_name: str):
        app = QApplication.instance()
        if hasattr(app, 'set_theme'):
            app.set_theme(theme_name)
        self.accept()
```

**Reference**: See `theme_system/docs/THEMING-GUIDE-OFFICIAL.md` for complete ThemedApplication documentation.

---

## Debugging Multi-Widget Applications

### Common Issues and Solutions

#### 1. "Window controls don't exist"

**Symptom**:
```python
AttributeError: 'MyApp' object has no attribute '_window_controls'
```

**Debug checklist**:
```python
# Add debug logging
logger.info(f"Parent: {self.parent()}")
logger.info(f"Window mode: {self._window_mode}")
logger.info(f"Has controls: {hasattr(self, '_window_controls')}")
```

**Common causes**:
- Accessing controls before `super().__init__()` completes
- Widget has a parent (embedded mode, not frameless)
- Overriding `_setup_ui()` without calling parent

#### 2. "MultisplitWidget shows no widgets"

**Symptom**: Empty panes, "No provider available" warning

**Debug checklist**:
```python
# Check provider is set
logger.info(f"Provider: {multisplit._widget_provider}")

# Check provide_widget is being called
class TerminalProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        logger.info(f"provide_widget called: {widget_id}, {pane_id}")
        return TerminalWidget(...)
```

**Common causes**:
- Forgot to call `multisplit.set_widget_provider(provider)`
- Provider's `provide_widget()` returning None
- Exception in `provide_widget()` (check logs)

#### 3. "Theme not updating"

**Symptom**: Widgets don't change when calling `app.set_theme()`

**Debug checklist**:
```python
# Check ThemedApplication is being used
app = QApplication.instance()
logger.info(f"App type: {type(app)}")  # Should be ThemedApplication

# Check widget is registered
logger.info(f"Widget ID: {widget._widget_id}")
```

**Common causes**:
- Using `QApplication` instead of `ThemedApplication`
- Widget not inheriting from `ThemedWidget`
- Theme system not initialized

### Useful Logging Patterns

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Per-module loggers
logger = logging.getLogger(__name__)

# Debug widget lifecycle
logger.info(f"Widget created: {self.__class__.__name__}")
logger.info(f"Parent: {self.parent()}")
logger.info(f"Window mode: {self._window_mode if hasattr(self, '_window_mode') else 'N/A'}")
```

---

## Cross-References

### Widget Documentation
- [ChromeTabbedWindow README](../../../widgets/chrome-tabbed-window/README.md) - Window modes, API reference
- [ChromeTabbedWindow Example 04](../../../widgets/chrome-tabbed-window/examples/04_themed_chrome_tabs.py) - Canonical usage pattern
- [MultisplitWidget Example 01](../../../widgets/multisplit_widget/examples/01_basic_text_editor.py) - WidgetProvider pattern
- [TerminalWidget Example 02](../../../widgets/terminal_widget/examples/02_multi_terminal_app.py) - MultiSessionTerminalServer pattern

### Theme System
- [Official Theming Guide](../../../widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md) - ThemedApplication, ThemedWidget
- [TerminalWidget Theme Integration](../../../widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md) - WebView + Theme lessons

### ViloxTerm Implementation
- [Implementation Plan](implementation-PLAN.md) - Complete implementation guide
- [README.md](../README.md) - Architecture overview, development status

---

## Summary: Top 8 Critical Lessons

1. **Provider MUST be in MultisplitWidget constructor** - `MultisplitWidget(provider=...)` not `set_widget_provider()`
2. **Override `_on_new_tab_requested()`, don't create custom "+" button** - ChromeTabbedWindow has a built-in painted "+" button
3. **Import WherePosition from core.types, not main package** - Check examples for correct import paths
4. **Don't override `_setup_ui()` in ChromeTabbedWindow** - Customize in `__init__` after `super().__init__()`
5. **Always check widget examples first** - They show the correct minimal pattern (saved us three times!)
6. **WidgetProvider creates widgets lazily** - Share resources via provider constructor
7. **Window controls only exist in frameless mode** - Check `_window_mode` before accessing
8. **ThemedApplication integration is automatic** - ChromeTabbedWindow is already a ThemedWidget

These lessons could save hours of debugging and trial-and-error for developers building multi-widget applications with VFWidgets.
