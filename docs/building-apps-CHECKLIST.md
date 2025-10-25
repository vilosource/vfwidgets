# VFWidgets Application Development Checklist

This checklist ensures you don't miss critical integration requirements when building applications with VFWidgets components.

## Phase 1: Requirements Analysis

### Functional Requirements
- [ ] List all primary features
- [ ] List all user interactions
- [ ] Define application lifecycle (startup, shutdown, crash recovery)

### Component Requirements
- [ ] List all VFWidgets components to be used
  - [ ] ViloCodeWindow?
  - [ ] ChromeTabbedWindow?
  - [ ] MarkdownViewer?
  - [ ] TerminalWidget?
  - [ ] WorkspaceWidget?
  - [ ] KeybindingManager?
  - [ ] Other themed widgets?

### Special Behaviors
- [ ] Single-instance behavior needed?
  - [ ] How should multiple launches behave?
  - [ ] What data needs to be passed between instances?
- [ ] System tray integration needed?
- [ ] Desktop integration needed? (.desktop files, icons)
- [ ] Auto-start needed?
- [ ] Update mechanism needed?

### Theme Requirements ⚠️ CRITICAL
- [ ] Does ANY component use `ThemedWidget`?
- [ ] Does ANY component use `ThemedMainWindow`?
- [ ] Check component documentation for theme requirements

**If YES to any above:**
- [ ] Application MUST use `ThemedApplication` (or theme-aware base)
- [ ] Document why if not using `ThemedApplication`
- [ ] Plan fallback behavior for non-themed mode

## Phase 2: Architecture Design

### Application Base Class Selection

Choose ONE of the following patterns:

#### Pattern A: No Theme Support
```python
from PySide6.QtWidgets import QApplication

class MyApp(QApplication):
    pass
```
**Use when**: No themed widgets, simple application, minimal dependencies
**Limitations**: Cannot use ViloCodeWindow, ChromeTabbedWindow, or any ThemedWidget-based components

#### Pattern B: Theme Support Only
```python
from vfwidgets_theme import ThemedApplication

class MyApp(ThemedApplication):
    pass
```
**Use when**: Need consistent theming, using themed widgets
**Limitations**: Multiple instances allowed (no single-instance enforcement)

#### Pattern C: Single-Instance Only (No Theme)
```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
```
**Use when**: Single-instance required, no themed widgets
**Limitations**: Theme support disabled (even if widgets support it)

#### Pattern D: Single-Instance + Theme Support ✅ RECOMMENDED
```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
        # Automatically uses ThemedApplication if vfwidgets-theme installed
```
**Use when**: Most applications using ViloCodeWindow or ChromeTabbedWindow
**Benefits**: Single-instance behavior + theme support + optional theme dependency

#### Pattern E: Modern Desktop Integration ✅ HIGHLY RECOMMENDED
```python
from vfwidgets_common.desktop import configure_desktop

app = configure_desktop(
    app_name="myapp",
    app_display_name="My Application",
    icon_name="myapp",
    desktop_categories="Utility;",
)
window = ViloCodeWindow()
window.show()
sys.exit(app.exec())
```
**Use when**: Building production applications that need full desktop integration
**Benefits**:
- Automatic platform detection (WSL, Wayland, X11, Remote Desktop)
- Automatic platform quirks (software rendering, scaling fixes)
- Desktop integration (icons, .desktop files) with auto-install
- QApplication creation with proper metadata
- Works with any QApplication subclass (including ThemedApplication, SingleInstanceApplication)

**Note**: To use with SingleInstanceApplication, pass `application_class` parameter:
```python
from vfwidgets_common import SingleInstanceApplication
from vfwidgets_common.desktop import configure_desktop

app = configure_desktop(
    app_name="myapp",
    app_display_name="My Application",
    icon_name="myapp",
    desktop_categories="Utility;",
    application_class=SingleInstanceApplication,
    app_id="myapp",  # Passed to SingleInstanceApplication
)
```

### Architecture Checklist
- [ ] Base class selected and documented
- [ ] If using themed widgets:
  - [ ] Verify base class is theme-aware
  - [ ] Document theme propagation mechanism
- [ ] If combining multiple features (single-instance + theme):
  - [ ] Verify compatibility (no multiple inheritance of QApplication)
  - [ ] Use composition pattern or enhanced base class

### Dependency Management
- [ ] List all required dependencies in `pyproject.toml`
- [ ] List all optional dependencies
- [ ] Document feature availability matrix
  - [ ] What works without optional dependencies?
  - [ ] What requires optional dependencies?

Example:
```toml
[project]
dependencies = [
    "PySide6>=6.5.0",
    "vfwidgets-common>=1.0.0",
]

[project.optional-dependencies]
theme = ["vfwidgets-theme>=2.0.0"]
full = ["vfwidgets-theme>=2.0.0", "vfwidgets-terminal>=1.0.0"]
```

## Phase 3: Implementation

### Application Setup
- [ ] QApplication base class correct
- [ ] Application metadata set
  - [ ] `setApplicationName()`
  - [ ] `setApplicationVersion()`
  - [ ] `setOrganizationName()`
  - [ ] `setOrganizationDomain()`
- [ ] Application icon set (if applicable)
- [ ] Desktop integration configured (if applicable)

### Window Initialization
- [ ] Main window created with correct parent (None for top-level)
- [ ] Window size set appropriately
- [ ] Window title set
- [ ] Window icon set (if different from app icon)

### Theme Integration (if using themed widgets)
- [ ] Verify `QApplication.instance()` is `ThemedApplication`
- [ ] Verify theme manager is accessible
- [ ] Set default theme (if needed)
- [ ] Handle theme not available gracefully

Example verification:
```python
from PySide6.QtWidgets import QApplication

app = QApplication.instance()
print(f"App type: {type(app).__name__}")

try:
    from vfwidgets_theme import ThemedApplication
    is_themed = isinstance(app, ThemedApplication)
    print(f"Theme support: {is_themed}")
    if not is_themed:
        print("WARNING: Using themed widgets without ThemedApplication!")
except ImportError:
    print("Theme system not available")
```

### Component Integration
- [ ] All widgets initialized with correct parents
- [ ] Signal/slot connections established
- [ ] Theme config verified (if using themed widgets)

### Error Handling
- [ ] Graceful degradation if optional features unavailable
- [ ] User-friendly error messages
- [ ] Logging configured

## Phase 4: Testing

### Functional Testing
- [ ] All features work as expected
- [ ] Edge cases handled
- [ ] Error conditions handled gracefully

### Visual Testing ⚠️ CRITICAL
- [ ] Launch application and visually inspect
- [ ] Check theme consistency across all components
  - [ ] Title bar
  - [ ] Menu bar
  - [ ] Tool bars
  - [ ] Main content area
  - [ ] Status bar
  - [ ] Dialogs
- [ ] Test with multiple themes (if supported)
  - [ ] Switch to dark theme → all components update
  - [ ] Switch to light theme → all components update
  - [ ] Switch to custom theme → all components update
- [ ] Test on all target platforms
  - [ ] Linux (X11)
  - [ ] Linux (Wayland)
  - [ ] macOS
  - [ ] Windows
  - [ ] WSL (if applicable)

### Visual Testing Checklist
For each theme:
- [ ] Title bar color correct
- [ ] Menu text readable
- [ ] Button colors correct
- [ ] Text contrast sufficient
- [ ] Icons visible
- [ ] Borders visible but not intrusive
- [ ] No "mixed theme" appearance (some components light, some dark)

### Integration Testing
- [ ] Single-instance behavior works (if applicable)
- [ ] IPC communication works (if applicable)
- [ ] Theme changes propagate to all components (if applicable)
- [ ] Desktop integration works (if applicable)

### Performance Testing
- [ ] Application starts quickly
- [ ] Theme switching is responsive (<100ms)
- [ ] No memory leaks
- [ ] No excessive CPU usage

## Phase 5: Documentation

### README.md
- [ ] Installation instructions
- [ ] Usage instructions
- [ ] Command-line arguments documented
- [ ] Features documented
- [ ] Screenshots included (light and dark themes)

### Architecture Documentation
- [ ] QApplication type documented
- [ ] Component hierarchy documented
- [ ] Theme integration documented
- [ ] Dependencies documented (required vs optional)

### Example Code
- [ ] Basic usage example
- [ ] Theme integration example (if applicable)
- [ ] Advanced usage examples
- [ ] All examples tested and working

### Theme Integration Documentation Template

Add this section to your README if using themed widgets:

```markdown
## Theme Support

This application uses VFWidgets themed components and requires `ThemedApplication` for proper theme support.

### How It Works
- Application uses `SingleInstanceApplication` which automatically wraps `ThemedApplication` when available
- All themed widgets (ViloCodeWindow, ChromeTabbedWindow, etc.) receive theme updates automatically
- Theme changes propagate to all components simultaneously

### Verifying Theme Support
```python
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
print(f"Theme support: {type(app).__name__}")
# Should print: SingleInstanceApplication (theme-aware)
```

### Switching Themes
```python
from vfwidgets_theme import get_theme_manager
get_theme_manager().set_theme("dark")  # or "light", "monokai", etc.
```

### Without Theme Support
If `vfwidgets-theme` is not installed:
- Application still works
- Uses default Qt styling
- Theme switching not available
```

## Phase 6: Code Review

### Self-Review Checklist
- [ ] Application base class correct for requirements
- [ ] All themed widgets have theme-aware QApplication
- [ ] No `QApplication` used when themed widgets present
- [ ] Visual inspection completed
- [ ] Documentation complete
- [ ] Tests pass

### Common Mistakes to Check

#### ❌ Mistake 1: QApplication with Themed Widgets
```python
# WRONG
app = QApplication(sys.argv)
window = ViloCodeWindow()  # Uses ThemedWidget - won't work!
```

#### ✅ Fix 1: Use ThemedApplication
```python
# CORRECT
from vfwidgets_theme import ThemedApplication
app = ThemedApplication(sys.argv)
window = ViloCodeWindow()
```

#### ❌ Mistake 2: Multiple Inheritance of QApplication
```python
# WRONG - Won't work
class MyApp(ThemedApplication, SingleInstanceApplication):
    pass
```

#### ✅ Fix 2: Use Theme-Aware SingleInstanceApplication
```python
# CORRECT - SingleInstanceApplication is already theme-aware
from vfwidgets_common import SingleInstanceApplication
class MyApp(SingleInstanceApplication):
    pass
```

#### ❌ Mistake 3: No Visual Testing
```python
# WRONG - Only unit tests
pytest tests/
# Assume it works ← Visual issues missed!
```

#### ✅ Fix 3: Always Visual Test
```python
# CORRECT - Run and inspect
python -m myapp
# Visually verify:
# - All components same theme
# - Switch themes (if supported)
# - Check all windows/dialogs
```

## Quick Reference: Application Type Decision Tree

```
START: Creating a new VFWidgets application
  ↓
Does app use ANY themed widgets?
(ViloCodeWindow, ChromeTabbedWindow, MarkdownViewer, etc.)
  ↓
  YES → Does app need single-instance behavior?
         ↓
         YES → Use: SingleInstanceApplication (theme-aware) ✅
         ↓
         NO → Use: ThemedApplication ✅
  ↓
  NO → Does app need single-instance behavior?
        ↓
        YES → Use: SingleInstanceApplication (non-themed) ✅
        ↓
        NO → Use: QApplication ✅
```

## Summary

**Critical Requirements:**
1. ✅ Choose correct QApplication base class
2. ✅ Verify theme support if using themed widgets
3. ✅ Visual testing with multiple themes
4. ✅ Document theme integration

**Most Common Pattern:**
```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")
        # Theme support automatic if vfwidgets-theme installed

app = MyApp(sys.argv)
sys.exit(app.run())
```

**Remember:** When in doubt, check if any component uses `ThemedWidget`. If YES, your QApplication must be theme-aware (ThemedApplication or SingleInstanceApplication with theme support).
