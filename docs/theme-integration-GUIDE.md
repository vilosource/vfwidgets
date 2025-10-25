# Theme Integration Guide

**Quick reference for ensuring proper theme support in VFWidgets applications.**

## The Golden Rule

> **If your application uses ANY widget that inherits from `ThemedWidget`, your `QApplication` MUST be theme-aware.**

### Widgets That Require Theme-Aware QApplication

- `ViloCodeWindow`
- `ChromeTabbedWindow`
- `MarkdownViewer`
- `TerminalWidget`
- `WorkspaceWidget`
- Any custom widget inheriting from `ThemedWidget`

## Quick Start

### Step 1: Check Your Widgets

Look at your imports:

```python
from vfwidgets_vilocode_window import ViloCodeWindow  # ← ThemedWidget
from chrome_tabbed_window import ChromeTabbedWindow   # ← ThemedWidget
from vfwidgets_markdown import MarkdownViewer         # ← ThemedWidget
from vfwidgets_workspace import WorkspaceWidget       # ← ThemedWidget
```

**If you're using any of these → You need theme support**

### Step 2: Choose Correct Application Class

#### Option A: Theme Support Only

```python
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)
window = ViloCodeWindow()
window.show()
sys.exit(app.exec())
```

**Use when:**
- Using themed widgets
- Multiple instances allowed
- Simple application

#### Option B: Single-Instance + Theme Support (RECOMMENDED)

```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
        # Theme support automatic if vfwidgets-theme installed

app = MyApp(sys.argv)
window = ViloCodeWindow()
window.show()
sys.exit(app.exec())
```

**Use when:**
- Using themed widgets
- Single-instance behavior needed
- Most applications

### Step 3: Verify (During Development)

Add this verification code during development:

```python
from PySide6.QtWidgets import QApplication

app = QApplication.instance()
print(f"App type: {type(app).__name__}")

try:
    from vfwidgets_theme import ThemedApplication
    if isinstance(app, ThemedApplication):
        print("✅ Theme support: OK")
    else:
        print("⚠️  WARNING: Using themed widgets without ThemedApplication!")
except ImportError:
    print("⚠️  Theme system not installed")
```

**Expected output for themed apps:**
```
App type: SingleInstanceApplication
✅ Theme support: OK
```

### Step 4: Visual Test

1. Launch your application
2. Check all components have the same theme
3. If theme switching is available:
   - Switch to dark theme → All components update
   - Switch to light theme → All components update

**If components have different themes → Theme propagation is broken**

## Common Mistakes

### ❌ Mistake 1: Using QApplication with Themed Widgets

```python
# WRONG
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
window = ViloCodeWindow()  # Uses ThemedWidget - theme won't work!
```

**What happens:**
- Each widget uses its own independent default theme
- ViloCodeWindow might be dark
- ChromeTabbedWindow might be light
- Theme changes don't propagate

**Fix:**
```python
# CORRECT
from vfwidgets_theme import ThemedApplication
app = ThemedApplication(sys.argv)
window = ViloCodeWindow()
```

### ❌ Mistake 2: Multiple Inheritance of QApplication

```python
# WRONG - Multiple inheritance of QApplication doesn't work
class MyApp(ThemedApplication, SingleInstanceApplication):
    pass
```

**Fix:**
```python
# CORRECT - SingleInstanceApplication is already theme-aware
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
```

### ❌ Mistake 3: No Visual Testing

```python
# Testing only with unit tests
pytest tests/  # ← Won't catch visual theme issues
```

**Fix:**
```python
# Always launch and visually inspect
python -m myapp
# Check: Do all components have the same theme?
```

## How Theme Propagation Works

### Architecture

```
ThemedApplication (or SingleInstanceApplication with theme support)
    ↓ (initializes)
ThemeManager (singleton)
    ↓ (emits theme_changed signal)
ThemedWidget instances (ViloCodeWindow, ChromeTabbedWindow, etc.)
    ↓ (receive signal and update)
Visual update (all components update simultaneously)
```

### What ThemedApplication Provides

1. **Centralized Theme Manager**: Single source of truth for current theme
2. **Signal Propagation**: Broadcasts theme changes to all ThemedWidget instances
3. **Automatic Updates**: All themed components update simultaneously
4. **Theme Persistence**: Remembers user's theme choice

### What Happens WITHOUT ThemedApplication

1. ❌ No centralized theme manager
2. ❌ No signal propagation
3. ❌ Each ThemedWidget uses its own independent default
4. ❌ Result: Different widgets have different themes (broken UI)

## Debugging Theme Issues

### Issue: Components Have Different Themes

**Symptoms:**
- Title bar is dark
- Tab bar is light
- Content area is dark

**Diagnosis:**
```python
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedApplication

app = QApplication.instance()
print(f"Is themed app: {isinstance(app, ThemedApplication)}")
# If False → This is the problem
```

**Fix:** Use ThemedApplication or theme-aware SingleInstanceApplication

### Issue: Theme Changes Don't Propagate

**Symptoms:**
- Calling `get_theme_manager().set_theme("dark")` works for some components but not others

**Diagnosis:**
```python
from vfwidgets_theme import get_theme_manager

manager = get_theme_manager()
print(f"Theme manager: {manager}")
print(f"Current theme: {manager.get_current_theme()}")

# Check if widgets are connected
# (implementation specific)
```

**Common causes:**
1. QApplication is not ThemedApplication
2. Widget created before ThemeManager initialized
3. Widget not properly inheriting from ThemedWidget

### Issue: Theme Support Not Available

**Symptoms:**
```python
ImportError: cannot import name 'ThemedApplication' from 'vfwidgets_theme'
```

**Fix:** Install theme system
```bash
pip install vfwidgets-theme
```

**Or:** Use graceful degradation
```python
try:
    from vfwidgets_theme import ThemedApplication
    app = ThemedApplication(sys.argv)
except ImportError:
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print("Theme support not available - using default styling")
```

## Decision Tree

```
Creating new VFWidgets application?
    ↓
Using ViloCodeWindow, ChromeTabbedWindow, or other ThemedWidget?
    ↓
    YES ────────────────────┐
    ↓                       ↓
Need single-instance?   Need single-instance?
    ↓                       ↓
    YES                     NO
    ↓                       ↓
Use:                    Use:
SingleInstance-         ThemedApplication
Application
(theme-aware)
    ↓                       ↓
    └───────────────────────┘
                ↓
        ✅ Theme support works!
```

## Testing Checklist

### During Development
- [ ] Verify QApplication type is theme-aware
- [ ] Launch app and visually inspect
- [ ] Check all components have consistent theme
- [ ] Test theme switching (if applicable)

### Before Commit
- [ ] Visual test with dark theme
- [ ] Visual test with light theme
- [ ] Verify all components update together
- [ ] Check no console warnings about theming

### In CI/CD
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Screenshot tests pass (if available)

## Quick Reference Commands

### Verify Theme Support
```bash
python -c "
from PySide6.QtWidgets import QApplication
import sys

# Create your app
from myapp import MyApp
app = MyApp(sys.argv)

# Check type
from vfwidgets_theme import ThemedApplication
print(f'Theme-aware: {isinstance(app, ThemedApplication)}')
"
```

### List Available Themes
```bash
python -c "
from vfwidgets_theme import get_theme_manager
manager = get_theme_manager()
print('Available themes:')
for name in manager.get_available_themes():
    print(f'  - {name}')
"
```

### Switch Theme Programmatically
```python
from vfwidgets_theme import get_theme_manager
get_theme_manager().set_theme("dark")
```

## Summary

**Three steps to proper theme support:**

1. ✅ **Use theme-aware QApplication**
   - `ThemedApplication` for simple apps
   - `SingleInstanceApplication` for single-instance apps (automatically theme-aware)

2. ✅ **Visual testing**
   - Launch app and inspect
   - Verify all components have consistent theme
   - Test theme switching

3. ✅ **Document in README**
   - State that app uses ThemedApplication
   - Show theme switching example
   - Document graceful degradation

**Remember:** Widget-level theme support (inheriting from ThemedWidget) is necessary but not sufficient. You must also use theme-aware QApplication for theme propagation to work.
