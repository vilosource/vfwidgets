# VFWidgets Theme System - Examples

## Learning Path: Progressive Disclosure

This directory is organized to teach you the theme system through **progressive complexity**. Start at Example 01 and work your way up. Each example introduces only what you need at that stage.

---

## Stage 1: Simple Apps (Examples 01-04)

**You are here if:** Building a themed application with standard Qt widgets

**What you'll learn:** The simple API for 90% of use cases

### Example 01: Hello World
**File:** `01_hello_world.py`

The simplest possible themed application - just a few lines!

```python
from vfwidgets_theme import ThemedApplication, ThemedQWidget

class HelloWidget(ThemedQWidget):
    """Dead simple - one base class."""
    pass
```

**Key concepts:**
- Creating a ThemedApplication
- Using ThemedQWidget for simple container widgets
- Automatic theme application with zero configuration

---

### Example 02: Buttons and Layout
**File:** `02_buttons_and_layout.py`

Building a real application window with buttons and layouts.

```python
from vfwidgets_theme import ThemedMainWindow

class MyApp(ThemedMainWindow):
    """Main application window - still simple!"""
    pass
```

**Key concepts:**
- Using ThemedMainWindow for application windows
- Standard Qt widgets (QPushButton, QLabel) work automatically
- All widgets inherit theme from parent

---

### Example 03: Theme Switching
**File:** `03_theme_switching.py`

Switching between light and dark themes dynamically.

```python
app = ThemedApplication(sys.argv)
app.set_theme('dark')  # Or 'light', 'default', 'minimal'
```

**Key concepts:**
- Available built-in themes
- Dynamic theme switching
- Theme changes propagate automatically to all widgets

---

### Example 04: Input Forms and Dialogs
**File:** `04_input_forms.py`

Building forms with input widgets and themed dialogs.

```python
from vfwidgets_theme import ThemedDialog

class PreferencesDialog(ThemedDialog):
    """Dialogs get themed automatically too!"""
    pass
```

**Key concepts:**
- Using ThemedDialog for dialog windows
- Themed input widgets (QLineEdit, QTextEdit, QCheckBox)
- Form layouts with themed widgets

**API so far:**
- `ThemedApplication` - Your application class
- `ThemedMainWindow` - For main windows
- `ThemedDialog` - For dialog windows
- `ThemedQWidget` - For simple container widgets

**That's it! 90% of users never need more than this.**

---

## Stage 2: Custom Widgets (Example 05+)

**Go here when:** You need widgets beyond plain QWidget (like QTextEdit, QFrame, QPushButton subclasses)

### Example 05: Custom Text Editor (THE BRIDGE)
**File:** `05_vscode_editor.py`

**START HERE when you need custom widgets!**

This example introduces `ThemedWidget` for the first time, with a clear explanation of WHY and WHEN you need it.

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """Now we're using the advanced API!

    WHY: We need a QTextEdit subclass, and ThemedQWidget only works with QWidget.

    PATTERN: class MyWidget(ThemedWidget, QtBaseClass)
             ThemedWidget MUST come first!
    """
    pass
```

**The "Aha!" moment:**
```python
# ThemedQWidget is actually just this:
class ThemedQWidget(ThemedWidget, QWidget):
    pass

# Now you understand the full pattern!
```

**Key concepts:**
- When you need `ThemedWidget` (the mixin)
- Multiple inheritance rules (ThemedWidget comes FIRST)
- The relationship between ThemedQWidget and ThemedWidget
- Building a VS Code-inspired editor

**API added:**
- `ThemedWidget` - The powerful mixin that works with ANY Qt base class

---

### Example 06: Role Markers
**File:** `06_role_markers.py`

Semantic widget styling using role properties.

```python
# Apply semantic styling without custom CSS
danger_btn = QPushButton("Delete")
danger_btn.setProperty("role", "danger")  # Automatically styled red

editor = QTextEdit()
editor.setProperty("role", "editor")  # Automatically uses monospace font
```

**Key concepts:**
- Built-in role markers (danger, success, warning, editor, secondary)
- Semantic styling without writing CSS
- Role-based theme customization

---

## Stage 3: Phase 2 Features (Examples 07-11)

### Example 07: Theme Menu
**File:** `07_theme_menu.py`

Add a theme switcher menu to your application.

**Key concepts:**
- Pre-built theme menu widget
- Integration with application menu bar
- User theme preferences

---

### Example 08: Theme Toolbar
**File:** `08_theme_toolbar.py`

Add a theme switcher toolbar to your application.

**Key concepts:**
- Theme toolbar widget
- Icon-based theme selection
- Quick theme switching UI

---

### Example 09: Settings Dialog
**File:** `09_settings_dialog.py`

Comprehensive settings dialog with theme preferences.

**Key concepts:**
- Settings integration
- Theme preview in settings
- Saving user preferences

---

### Example 10: Live Preview
**File:** `10_live_preview.py`

Real-time theme preview while editing.

**Key concepts:**
- Live theme preview widget
- Sample widget rendering
- Real-time theme updates

---

### Example 11: Keyboard Shortcuts
**File:** `11_keyboard_shortcuts.py`

Keyboard shortcuts for theme operations.

**Key concepts:**
- Theme switching with keyboard
- Shortcut registration
- KeybindingManager integration

---

## Stage 4: Theme Editor & Developer Tools (Examples 12-15)

**Status:** Design phase - templates ready for implementation

### Example 12: Standalone Theme Editor Dialog
**File:** `12_theme_editor_standalone.py`

Open the theme editor as a standalone dialog for creating or editing themes.

```python
from vfwidgets_theme.widgets import ThemeEditorDialog

dialog = ThemeEditorDialog(
    parent=self,
    base_theme="dark",
    mode="create"  # "create", "edit", or "clone"
)
dialog.exec()
```

**Key concepts:**
- Creating themes from scratch
- Editing existing themes
- Cloning and customizing themes
- Visual token editor

---

### Example 13: Embedded Theme Editor Widget
**File:** `13_theme_editor_embedded.py`

Embed the theme editor directly into your settings page.

```python
from vfwidgets_theme.widgets import ThemeEditorWidget

editor = ThemeEditorWidget(
    parent=settings_tab,
    show_preview=True,
    show_validation=True
)
```

**Key concepts:**
- Embedding theme editor in application UI
- Settings page integration
- Live preview panel
- Accessibility validation

---

### Example 14: Quick Theme Customization
**File:** `14_theme_editor_quick_edit.py`

Simple quick-edit UI for basic color customization.

**Key concepts:**
- Quick color pickers for key tokens
- Simplified customization UI
- "Change App Color" feature implementation
- Real-time preview

---

### Example 15: Theme Code Generation (DX Feature)
**File:** `15_theme_code_generation.py`

Generate code from visual themes - a Developer Experience feature.

```python
from vfwidgets_theme.generators import ThemeCodeGenerator

generator = ThemeCodeGenerator()
python_code = generator.generate_python_code(theme)
typescript = generator.generate_typescript_types(theme)
css_vars = generator.generate_css_variables(theme)
```

**Output formats:**
- Python ThemeBuilder code
- TypeScript type definitions
- CSS custom properties
- QSS stylesheets
- JSON export

**Key concepts:**
- Code generation from visual editor
- Multi-format export
- Developer workflow integration
- Theme sharing and distribution

---

## Stage 5: Advanced Features

**See:** `legacy/` directory for more complex examples (being reorganized)

**Coming soon:**
- Theme templates and presets
- Advanced token management
- Building reusable widget libraries

---

## Quick Decision Tree

**Q: Building a main window?**
→ Use `ThemedMainWindow` (Example 01)

**Q: Building a dialog?**
→ Use `ThemedDialog` (Example 04)

**Q: Building a simple container widget?**
→ Use `ThemedQWidget` (Examples 01-02)

**Q: Need QTextEdit/QFrame/QPushButton/etc. subclass?**
→ Use `ThemedWidget` mixin (Example 05) ⭐ **Bridge example**

**Q: Building a widget library?**
→ See advanced examples (coming soon)

---

## Running Examples

### Prerequisites

```bash
# Ensure PySide6 is installed
pip install PySide6

# Navigate to theme system directory
cd widgets/theme_system
```

### Running Individual Examples

```bash
# Stage 1: Simple Apps
python examples/01_hello_world.py
python examples/02_buttons_and_layout.py
python examples/03_theme_switching.py
python examples/04_input_forms.py

# Stage 2: Custom Widgets (The Bridge!)
python examples/05_vscode_editor.py
python examples/06_role_markers.py

# Stage 3: Phase 2 Features
python examples/07_theme_menu.py
python examples/08_theme_toolbar.py
python examples/09_settings_dialog.py
python examples/10_live_preview.py
python examples/11_keyboard_shortcuts.py

# Stage 4: Theme Editor & Developer Tools (Templates - not yet implemented)
python examples/12_theme_editor_standalone.py
python examples/13_theme_editor_embedded.py
python examples/14_theme_editor_quick_edit.py
python examples/15_theme_code_generation.py
```

### Running All Examples (Test Suite)

```bash
cd examples
./run_tests.sh
```

---

## Understanding the API Structure

The theme system uses **progressive disclosure** - you start simple and graduate to advanced features only when needed:

```
Simple API (Training Wheels)        Advanced API (Full Bicycle)
├─ ThemedMainWindow                 ├─ ThemedWidget mixin
├─ ThemedDialog              →      ├─ Works with ANY Qt base
└─ ThemedQWidget                    └─ Maximum flexibility
```

**The secret:** All the convenience classes (ThemedMainWindow, ThemedDialog, ThemedQWidget) are just pre-combined versions of ThemedWidget!

```python
# Under the hood:
class ThemedMainWindow(ThemedWidget, QMainWindow):
    pass

class ThemedDialog(ThemedWidget, QDialog):
    pass

class ThemedQWidget(ThemedWidget, QWidget):
    pass
```

When you discover you need ThemedWidget (Example 05), you'll understand the pattern that was there all along!

---

## Best Practices

### For App Developers (Examples 01-04)
- Start with ThemedMainWindow or ThemedDialog
- Use ThemedQWidget for simple containers
- Let standard Qt widgets inherit theming automatically
- Don't overthink it - the simple API is enough!

### For Custom Widget Developers (Example 05+)
- Only use ThemedWidget when you need non-QWidget bases
- Always put ThemedWidget FIRST in inheritance: `class MyWidget(ThemedWidget, QtBaseClass)`
- Use role markers for semantic styling
- Read Example 05 carefully - it explains the transition

### For Widget Library Authors
- See advanced examples (coming soon)
- Use token constants and ThemeProperty descriptors
- Implement lifecycle hooks for complex widgets
- Read the widget-development-GUIDE.md

---

## Troubleshooting

### "I don't know which class to use"
→ Follow the decision tree above, or start with Example 01

### "My widget isn't getting themed"
→ Make sure it's a child of a themed widget (ThemedMainWindow, ThemedDialog, or ThemedQWidget)

### "I need a QTextEdit subclass but ThemedQWidget doesn't work"
→ You've reached Example 05! Use ThemedWidget mixin instead

### "TypeError about inheritance order"
→ ThemedWidget must come FIRST: `class MyWidget(ThemedWidget, QTextEdit)` not `class MyWidget(QTextEdit, ThemedWidget)`

---

## What's in legacy/?

The `legacy/` directory contains older examples that are being reorganized:
- `tutorials/` - Old tutorial series (being updated)
- `basic/` - Basic widget examples (being migrated)
- `layouts/` - Layout examples (being migrated)
- `user_examples/` - User-contributed examples
- `development_examples/` - Development/testing examples

These will be reorganized into the new progressive structure in upcoming releases.

---

## Next Steps

After completing these examples:

1. **Read the guides:**
   - `docs/quick-start-GUIDE.md` - Quick reference for simple API
   - `docs/widget-development-GUIDE.md` - Deep dive into ThemedWidget
   - `docs/api-REFERENCE.md` - Complete API documentation

2. **Build your own app** using the patterns shown

3. **Create custom themes** for your brand or preferences

4. **Contribute** new examples or improvements!

---

**Happy theming!**

The VFWidgets theme system makes it easy to create beautiful, consistent, and accessible user interfaces. Start simple with Examples 01-04, then naturally graduate to advanced features when you need them.
