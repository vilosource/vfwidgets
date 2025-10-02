# Theme Integration Tasks - Implementation Guide

## Overview
Integrate ChromeTabbedWindow with the VFWidgets theme system to support dynamic theme switching and theme-aware styling.

**Working Directory:** `/home/kuja/GitHub/vfwidgets/widgets/chrome-tabbed-window/`

**Goal:** Make ChromeTabbedWindow work seamlessly with ThemedApplication and support all theme system features.

---

## Prerequisites

### Understanding the Theme System
The theme system is located at: `../theme_system/`

**Key Components:**
- `ThemedWidget` - Base mixin for all themed widgets
- `ThemedMainWindow` - Themed version of QMainWindow
- `ThemedApplication` - Application-level theme management
- Theme objects with `.colors` dict containing color tokens

**Critical Pattern:**
```python
# ThemedWidget MUST come first in inheritance!
class MyWidget(ThemedWidget, QtBaseClass):  # ✅ Correct
    pass

class MyWidget(QtBaseClass, ThemedWidget):  # ❌ Wrong - won't work!
    pass
```

**Key Lesson from Recent Fix:**
- Windows MUST inherit from `ThemedMainWindow` not `QMainWindow` to receive visual theme updates
- Container widgets should use `ThemedQWidget` not `QWidget`
- Regular Qt widgets inside themed parents get styled via CSS cascade

---

## Task 1: Make ChromeTabbedWindow Theme-Aware

### 1.1 Add Theme System Dependency
**File:** `pyproject.toml`

**Action:** Add theme system as dependency

```toml
[project]
dependencies = [
    "PySide6>=6.5.0",
    "vfwidgets-theme>=2.0.0",  # Add this line
]

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies
]
```

**Alternative for development:**
Add relative import path during development (before packaging):
```python
# In src/chrome_tabbed_window/__init__.py
import sys
from pathlib import Path
# Add theme_system to path for development
theme_system_path = Path(__file__).parent.parent.parent.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))
```

### 1.2 Update ChromeTabbedWindow Class
**File:** `src/chrome_tabbed_window/chrome_tabbed_window.py`

**Current inheritance:**
```python
class ChromeTabbedWindow(QTabWidget):
    pass
```

**Change to:**
```python
from vfwidgets_theme import ThemedWidget

class ChromeTabbedWindow(ThemedWidget, QTabWidget):
    """Chrome-style tabbed window with theme support.

    IMPORTANT: ThemedWidget MUST come first for theming to work!
    """
    pass
```

**Why this works:**
- `ThemedWidget` is a mixin that adds theme functionality
- `QTabWidget` provides all the tab widget functionality
- Order matters: ThemedWidget's `__init__` must run first

### 1.3 Initialize Theme System
**File:** `src/chrome_tabbed_window/chrome_tabbed_window.py`

**In `__init__` method, after `super().__init__(parent)`:**

```python
def __init__(self, parent: Optional[QWidget] = None):
    # IMPORTANT: super().__init__() now calls both ThemedWidget and QTabWidget
    super().__init__(parent)

    # ThemedWidget initialization happens automatically via super()
    # Access current theme via self.get_current_theme()

    # ... rest of initialization
```

**Add method to handle theme changes:**
```python
def _on_theme_changed(self):
    """Handle theme change events.

    This method is automatically called by ThemedWidget when theme changes.
    Update tab bar colors and trigger repaint.
    """
    # Update tab bar with new theme colors
    if hasattr(self, '_tab_bar') and self._tab_bar:
        self._tab_bar.update_theme_colors()
        self._tab_bar.update()

    # Update window controls if in frameless mode
    if hasattr(self, '_window_controls') and self._window_controls:
        self._window_controls.update_theme_colors()
        self._window_controls.update()

    # Force full repaint
    self.update()
```

---

## Task 2: Make ChromeTabRenderer Theme-Aware

### 2.1 Update ChromeTabRenderer
**File:** `src/chrome_tabbed_window/components/chrome_tab_renderer.py`

**Current approach:** Uses hardcoded Chrome colors
```python
# Hardcoded colors (current)
INACTIVE_TAB_COLOR = QColor("#DEE1E6")
ACTIVE_TAB_COLOR = QColor("#FFFFFF")
```

**Change to theme-based colors:**

```python
from vfwidgets_theme import ThemedWidget
from typing import Optional

class ChromeTabRenderer:
    """Renders Chrome-style tabs using theme system colors."""

    @staticmethod
    def get_tab_colors(theme=None):
        """Get tab colors from current theme.

        Args:
            theme: Theme object from ThemedWidget, or None to use fallback

        Returns:
            dict with color keys: inactive_bg, active_bg, text, border, hover, etc.
        """
        if theme is None:
            # Fallback to Chrome defaults if no theme
            return {
                'inactive_bg': QColor("#DEE1E6"),
                'active_bg': QColor("#FFFFFF"),
                'text': QColor("#000000"),
                'text_inactive': QColor("#5F6368"),
                'border': QColor("#DADCE0"),
                'hover_bg': QColor("#F1F3F4"),
                'close_hover': QColor("#E8EAED"),
            }

        # Get colors from theme
        colors = theme.colors if hasattr(theme, 'colors') else {}

        return {
            'inactive_bg': QColor(colors.get('colors.surface', "#DEE1E6")),
            'active_bg': QColor(colors.get('colors.background', "#FFFFFF")),
            'text': QColor(colors.get('colors.text', "#000000")),
            'text_inactive': QColor(colors.get('colors.text_secondary', "#5F6368")),
            'border': QColor(colors.get('colors.border', "#DADCE0")),
            'hover_bg': QColor(colors.get('colors.hover', "#F1F3F4")),
            'close_hover': QColor(colors.get('colors.disabled_bg', "#E8EAED")),
        }

    @staticmethod
    def draw_tab(painter, rect, state, text, icon=None, closable=False, theme=None):
        """Draw a Chrome-style tab using theme colors.

        Args:
            painter: QPainter to draw with
            rect: QRect for tab bounds
            state: TabState enum value
            text: Tab text
            icon: Optional QIcon
            closable: Whether to show close button
            theme: Optional theme object from ThemedWidget
        """
        # Get theme-based colors
        colors = ChromeTabRenderer.get_tab_colors(theme)

        # Use theme colors instead of hardcoded ones
        if state == TabState.ACTIVE:
            bg_color = colors['active_bg']
            text_color = colors['text']
        else:
            bg_color = colors['inactive_bg']
            text_color = colors['text_inactive']

        if state == TabState.HOVER:
            bg_color = colors['hover_bg']

        # ... rest of drawing code using theme colors
```

### 2.2 Update draw_new_tab_button
```python
@staticmethod
def draw_new_tab_button(painter, rect, state, theme=None):
    """Draw new tab (+) button using theme colors."""
    colors = ChromeTabRenderer.get_tab_colors(theme)

    # Use theme colors
    if state == TabState.HOVER:
        bg_color = colors['hover_bg']
    else:
        bg_color = colors['inactive_bg']

    # ... rest of drawing
```

### 2.3 Update draw_window_controls
```python
@staticmethod
def draw_minimize_button(painter, rect, state, theme=None):
    """Draw minimize button using theme colors."""
    colors = ChromeTabRenderer.get_tab_colors(theme)
    # Use theme colors for buttons
```

---

## Task 3: Update ChromeTabBar to Use Theme

### 3.1 Pass Theme to Renderer
**File:** `src/chrome_tabbed_window/view/chrome_tab_bar.py`

**In `paintEvent` method:**

```python
def paintEvent(self, event):
    """Paint the tab bar with theme-aware colors."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)

    # Get theme from parent ChromeTabbedWindow
    theme = None
    parent_window = self.parent()
    while parent_window:
        if isinstance(parent_window, ChromeTabbedWindow):
            theme = parent_window.get_current_theme()  # ThemedWidget method
            break
        parent_window = parent_window.parent()

    # Paint each tab with theme
    for i in range(self.count()):
        rect = self.tabRect(i)
        if not rect.intersects(event.rect()):
            continue

        state = self._get_tab_state(i)
        text = self.tabText(i)
        icon = self.tabIcon(i)
        closable = self.tabsClosable()

        # Pass theme to renderer
        ChromeTabRenderer.draw_tab(
            painter, rect, state, text, icon, closable,
            theme=theme  # Add theme parameter
        )

    # Paint new tab button with theme
    if hasattr(self, 'new_tab_button_rect'):
        state = TabState.HOVER if self.new_tab_button_hovered else TabState.NORMAL
        ChromeTabRenderer.draw_new_tab_button(
            painter, self.new_tab_button_rect, state,
            theme=theme  # Add theme parameter
        )
```

### 3.2 Add Theme Update Method
```python
def update_theme_colors(self):
    """Update colors when theme changes.

    Called by ChromeTabbedWindow._on_theme_changed().
    """
    # Trigger repaint with new theme colors
    self.update()
```

---

## Task 4: Update Window Controls

### 4.1 Make WindowControls Theme-Aware
**File:** `src/chrome_tabbed_window/components/window_controls.py`

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class WindowControls(ThemedWidget, QWidget):
    """Window control buttons (minimize, maximize, close) with theme support.

    IMPORTANT: ThemedWidget MUST come first!
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setMinimumWidth(120)

    def paintEvent(self, event):
        """Paint window controls with theme colors."""
        painter = QPainter(self)

        # Get current theme
        theme = self.get_current_theme()  # From ThemedWidget

        # Draw each button with theme
        ChromeTabRenderer.draw_minimize_button(
            painter, self._minimize_rect, self._minimize_state, theme
        )
        ChromeTabRenderer.draw_maximize_button(
            painter, self._maximize_rect, self._maximize_state, theme
        )
        ChromeTabRenderer.draw_close_button(
            painter, self._close_rect, self._close_state, theme
        )

    def update_theme_colors(self):
        """Update when theme changes."""
        self.update()
```

---

## Task 5: Create ThemedChromeTabbed Window Example

### 5.1 Create Example File
**File:** `examples/themed_chrome_tabs.py`

```python
#!/usr/bin/env python3
"""
Example: ChromeTabbedWindow with Theme System Integration

Demonstrates ChromeTabbedWindow working with ThemedApplication
to support dynamic theme switching.

Run:
    python examples/themed_chrome_tabs.py
"""

import sys
from pathlib import Path

# Add both chrome-tabbed-window and theme_system to path
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir / "src"))

theme_system_path = base_dir.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from PySide6.QtWidgets import QTextEdit, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import add_theme_menu


def main():
    # Create themed application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create chrome tabbed window (automatically themed!)
    window = ChromeTabbedWindow()
    window.setWindowTitle("Themed Chrome Tabs Example")
    window.resize(900, 600)

    # Add theme menu for switching
    add_theme_menu(window)

    # Add some tabs
    for i in range(1, 4):
        editor = QTextEdit()
        editor.setPlaceholderText(f"Content for Tab {i}...")
        window.addTab(editor, f"Tab {i}")

    # Add a tab explaining theme switching
    info_widget = QLabel(
        "<h2>Chrome Tabs with Theme System</h2>"
        "<p>Use the <b>Theme</b> menu to switch themes.</p>"
        "<p>Notice how the tab colors change automatically!</p>"
        "<ul>"
        "<li>Dark theme: Tabs use dark colors</li>"
        "<li>Light theme: Tabs use light colors</li>"
        "<li>Theme colors come from the theme system</li>"
        "</ul>"
    )
    info_widget.setWordWrap(True)
    info_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
    info_widget.setTextFormat(Qt.TextFormat.RichText)
    info_widget.setStyleSheet("padding: 20px; font-size: 14px;")
    window.addTab(info_widget, "Theme Info")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 5.2 Create Embedded Theme Example
**File:** `examples/themed_chrome_embedded.py`

```python
#!/usr/bin/env python3
"""
Example: Embedded ChromeTabbedWindow with Themes

Shows ChromeTabbedWindow embedded in a ThemedMainWindow.

Run:
    python examples/themed_chrome_embedded.py
"""

import sys
from pathlib import Path

# Add paths
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir / "src"))
theme_system_path = base_dir.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLabel
from PySide6.QtCore import Qt

from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget, add_theme_menu


class MainWindow(ThemedMainWindow):
    """Main window with embedded chrome tabs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Chrome Tabs with Themes")
        self.resize(1000, 700)

        # Create central widget
        central = ThemedQWidget()
        layout = QVBoxLayout(central)

        # Add title
        title = QLabel("Embedded ChromeTabbedWindow with Theme Support")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Add chrome tabbed widget (embedded mode - no window controls)
        self.tabs = ChromeTabbedWindow(parent=central)

        # Add tabs
        for i in range(1, 5):
            editor = QTextEdit()
            editor.setPlaceholderText(f"Editor {i}")
            self.tabs.addTab(editor, f"File {i}.txt")

        layout.addWidget(self.tabs)

        self.setCentralWidget(central)

        # Add theme menu
        add_theme_menu(self)


def main():
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## Task 6: Add Tests for Theme Integration

### 6.1 Create Theme Integration Tests
**File:** `tests/test_theme_integration.py`

```python
"""Tests for theme system integration."""

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit
from chrome_tabbed_window import ChromeTabbedWindow

# Import theme system
import sys
from pathlib import Path
theme_system_path = Path(__file__).parent.parent.parent / "theme_system" / "src"
if theme_system_path.exists():
    sys.path.insert(0, str(theme_system_path))

from vfwidgets_theme import ThemedApplication


@pytest.fixture
def themed_app(qapp):
    """Create a themed application."""
    app = ThemedApplication.instance()
    if app is None:
        app = ThemedApplication([])
    yield app
    # Cleanup handled by qapp fixture


def test_chrome_window_is_themed_widget(themed_app):
    """Test that ChromeTabbedWindow inherits from ThemedWidget."""
    from vfwidgets_theme import ThemedWidget

    window = ChromeTabbedWindow()
    assert isinstance(window, ThemedWidget)
    window.close()


def test_chrome_window_receives_theme_changes(themed_app):
    """Test that ChromeTabbedWindow updates when theme changes."""
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")

    # Get initial theme
    initial_theme = window.get_current_theme()
    assert initial_theme is not None

    # Change theme
    themed_app.set_theme("dark")

    # Verify theme changed
    new_theme = window.get_current_theme()
    assert new_theme is not None
    assert new_theme.name == "dark"

    window.close()


def test_tab_renderer_uses_theme_colors(themed_app):
    """Test that tab renderer uses theme colors."""
    from chrome_tabbed_window.components.chrome_tab_renderer import ChromeTabRenderer

    # Set dark theme
    themed_app.set_theme("dark")

    window = ChromeTabbedWindow()
    theme = window.get_current_theme()

    # Get colors from renderer
    colors = ChromeTabRenderer.get_tab_colors(theme)

    # Verify colors come from theme, not hardcoded
    assert colors is not None
    assert 'active_bg' in colors
    assert 'text' in colors

    # Colors should be different from hardcoded defaults
    # (unless theme happens to use same colors)

    window.close()


def test_embedded_mode_with_themed_parent(themed_app):
    """Test embedded ChromeTabbedWindow in ThemedMainWindow."""
    from vfwidgets_theme.widgets import ThemedMainWindow, ThemedQWidget
    from PySide6.QtWidgets import QVBoxLayout

    main_window = ThemedMainWindow()
    central = ThemedQWidget()
    layout = QVBoxLayout(central)

    # Create embedded chrome tabs
    tabs = ChromeTabbedWindow(parent=central)
    tabs.addTab(QTextEdit(), "Tab 1")
    layout.addWidget(tabs)

    main_window.setCentralWidget(central)

    # Verify both use same theme
    main_theme = main_window.get_current_theme()
    tabs_theme = tabs.get_current_theme()

    assert main_theme.name == tabs_theme.name

    main_window.close()


def test_theme_switching_updates_tabs(themed_app):
    """Test that switching themes updates tab appearance."""
    window = ChromeTabbedWindow()
    window.addTab(QTextEdit(), "Tab 1")
    window.show()

    # Track repaint calls
    repaint_count = 0
    original_update = window.update

    def track_update():
        nonlocal repaint_count
        repaint_count += 1
        original_update()

    window.update = track_update

    # Change theme
    themed_app.set_theme("light")

    # Verify update was called
    assert repaint_count > 0

    window.close()
```

---

## Task 7: Update Documentation

### 7.1 Update README
**File:** `README.md`

Add section after "Features":

```markdown
## Theme System Integration

ChromeTabbedWindow integrates seamlessly with the VFWidgets theme system:

```python
from chrome_tabbed_window import ChromeTabbedWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import add_theme_menu

# Create themed application
app = ThemedApplication(sys.argv)

# ChromeTabbedWindow automatically uses theme colors!
window = ChromeTabbedWindow()

# Add theme switching menu
add_theme_menu(window)

window.show()
app.exec()
```

**Theme Features:**
- ✅ Automatic color adaptation from theme
- ✅ Dynamic theme switching support
- ✅ Works with all built-in themes (dark, light, default, minimal)
- ✅ Custom theme support
- ✅ Embedded mode respects parent theme

See [examples/themed_chrome_tabs.py](examples/themed_chrome_tabs.py) for complete example.
```

### 7.2 Create Theme Integration Guide
**File:** `docs/theme-integration-GUIDE.md`

```markdown
# Theme System Integration Guide

## Overview

ChromeTabbedWindow integrates with the VFWidgets theme system to provide automatic color adaptation and dynamic theme switching.

## Architecture

ChromeTabbedWindow inherits from `ThemedWidget` mixin:

```python
class ChromeTabbedWindow(ThemedWidget, QTabWidget):
    pass
```

This provides:
- Automatic theme detection
- Theme change notifications
- Access to theme colors via `get_current_theme()`

## Color Mapping

Chrome tab colors are mapped to theme tokens:

| Tab Element | Theme Token | Fallback |
|-------------|-------------|----------|
| Active tab background | `colors.background` | `#FFFFFF` |
| Inactive tab background | `colors.surface` | `#DEE1E6` |
| Tab text | `colors.text` | `#000000` |
| Inactive text | `colors.text_secondary` | `#5F6368` |
| Tab border | `colors.border` | `#DADCE0` |
| Hover background | `colors.hover` | `#F1F3F4` |

## Usage Examples

### Basic Theme Support

```python
from vfwidgets_theme import ThemedApplication
from chrome_tabbed_window import ChromeTabbedWindow

app = ThemedApplication(sys.argv)
window = ChromeTabbedWindow()
# Tabs automatically use theme colors!
```

### Theme Switching

```python
from vfwidgets_theme.widgets import add_theme_menu

# Add theme menu to window
add_theme_menu(window)

# Or programmatically
app.set_theme("dark")
```

### Custom Themes

Create custom themes and ChromeTabbedWindow will use them:

```python
custom_theme = {
    "name": "custom",
    "colors": {
        "colors.background": "#1E1E1E",
        "colors.surface": "#2D2D2D",
        "colors.text": "#FFFFFF",
        # ... other colors
    }
}

app.add_custom_theme(custom_theme)
app.set_theme("custom")
```

## Implementation Details

### ThemedWidget Inheritance

IMPORTANT: `ThemedWidget` must come FIRST in inheritance:

```python
# ✅ Correct
class ChromeTabbedWindow(ThemedWidget, QTabWidget):
    pass

# ❌ Wrong - theming won't work!
class ChromeTabbedWindow(QTabWidget, ThemedWidget):
    pass
```

### Theme Change Handling

Override `_on_theme_changed()` to handle theme updates:

```python
def _on_theme_changed(self):
    """Called automatically when theme changes."""
    # Update child widgets
    self._tab_bar.update_theme_colors()
    self._window_controls.update_theme_colors()

    # Trigger repaint
    self.update()
```

### Accessing Theme Colors

```python
# Get current theme object
theme = self.get_current_theme()

# Access colors
if theme and hasattr(theme, 'colors'):
    bg_color = theme.colors.get('colors.background', '#FFFFFF')
```

## Testing

Test theme integration:

```python
def test_theme_integration():
    app = ThemedApplication([])
    window = ChromeTabbedWindow()

    # Verify themed widget
    from vfwidgets_theme import ThemedWidget
    assert isinstance(window, ThemedWidget)

    # Test theme switching
    app.set_theme("dark")
    assert window.get_current_theme().name == "dark"
```

## Troubleshooting

**Problem:** Tabs don't update when theme changes

**Solution:** Ensure ChromeTabbedWindow inherits from ThemedWidget FIRST:
```python
class ChromeTabbedWindow(ThemedWidget, QTabWidget):  # ✅ Correct order
```

**Problem:** Custom colors not showing

**Solution:** Check theme token names match exactly:
```python
# Correct - with "colors." prefix
theme.colors["colors.background"] = "#FFFFFF"

# Wrong - missing prefix
theme.colors["background"] = "#FFFFFF"
```

**Problem:** Embedded tabs don't match parent theme

**Solution:** Ensure parent window uses ThemedMainWindow:
```python
# ✅ Correct
from vfwidgets_theme.widgets import ThemedMainWindow
main_window = ThemedMainWindow()

# ❌ Wrong - won't receive theme updates
from PySide6.QtWidgets import QMainWindow
main_window = QMainWindow()
```
```

---

## Success Criteria

**After completing all tasks:**

✅ ChromeTabbedWindow inherits from ThemedWidget
✅ Tab colors come from theme system, not hardcoded
✅ Theme switching updates tab appearance automatically
✅ Examples demonstrate theme integration
✅ Tests verify theme functionality
✅ Documentation explains theme usage
✅ Both top-level and embedded modes support themes
✅ No breaking changes to existing API

---

## Implementation Notes for Developer Agent

### MVC Architecture Compliance
- Keep theme logic in View layer (ChromeTabRenderer, ChromeTabBar)
- Model (TabModel) remains theme-agnostic
- Controller coordinates theme updates

### Performance Considerations
- Theme color lookup should be fast (< 1ms)
- Cache theme colors in ChromeTabBar to avoid repeated lookups
- Only repaint on actual theme change, not on every access

### Backward Compatibility
- Theme integration is opt-in (works without ThemedApplication)
- Fallback to hardcoded Chrome colors if no theme available
- No API changes to existing methods

### Testing Strategy
1. Unit test ChromeTabRenderer.get_tab_colors()
2. Integration test theme switching with ChromeTabbedWindow
3. Visual test comparing themed vs non-themed rendering
4. Performance test theme color lookup speed

### Error Handling
- Graceful fallback if theme system not available
- Default to Chrome colors if theme colors missing
- No crashes if theme object malformed

---

## Timeline Estimate

**Day 1:**
- Tasks 1 & 2: Make ChromeTabbedWindow and renderer theme-aware (4-6 hours)

**Day 2:**
- Tasks 3 & 4: Update ChromeTabBar and WindowControls (4-6 hours)

**Day 3:**
- Tasks 5, 6, 7: Examples, tests, documentation (4-6 hours)

**Total: 3-5 days**
