# Theme Overlay System - Quick Start Guide

**Version**: 2.0.0
**Time to Complete**: 5-10 minutes
**Difficulty**: Beginner

Get started with runtime color customization in vfwidgets-theme v2.0.0!

## What is the Overlay System?

The overlay system lets you customize colors at runtime without modifying theme files:

- 🎨 **Override colors** - Change specific colors while keeping the theme intact
- 🏢 **Brand your app** - Apply brand colors across all themes
- 👤 **User customization** - Let users personalize colors
- 💾 **Automatic persistence** - User preferences save automatically

## Quick Start in 3 Steps

### Step 1: Create Your App Class (30 seconds)

```python
from vfwidgets_theme.widgets import VFThemedApplication

class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",  # Starting theme
        "app_overrides": {
            # Your brand colors (optional)
            "tab.activeBackground": "#7c3aed",  # Purple tabs
        },
    }
```

### Step 2: Create the App (10 seconds)

```python
import sys

app = MyApp(sys.argv, app_id="MyApp")
```

### Step 3: Create Your Main Window (standard code)

```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTextEdit

class MainWindow(ThemedWidget):
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        label = QLabel("My Themed App")
        layout.addWidget(label)

        editor = QTextEdit("Type here...")
        layout.addWidget(editor)

        self.setWindowTitle("My App")
        self.resize(600, 400)

# Show and run
window = MainWindow()
window.show()
sys.exit(app.exec())
```

**Done! You now have:**
- ✅ Automatic theme loading
- ✅ Brand colors applied
- ✅ Theme preference persistence

## What Just Happened?

1. **VFThemedApplication** created your app with theme support
2. **theme_config["app_overrides"]** applied your brand color (purple tabs)
3. **app_id="MyApp"** enables automatic QSettings persistence
4. **ThemedWidget** made your window theme-aware

User's theme choice saves automatically and loads on next startup!

## Next Steps

### Add More Brand Colors

```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "tab.activeBackground": "#7c3aed",      # Purple
            "statusBar.background": "#14b8a6",      # Teal
            "button.hoverBackground": "#7c3aed",    # Purple hover
            "editor.background": "#1e1e2e",         # Custom dark
        },
    }
```

### Let Users Customize Colors

```python
class MyApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": True,
        "customizable_tokens": [
            "editor.background",
            "editor.foreground",
        ],
        "persist_user_overrides": True,  # Auto-save!
    }

# In your preferences dialog:
app = VFThemedApplication.instance()
app.customize_color("editor.background", "#ff0000", persist=True)
```

### Add a Theme Switcher

```python
from PySide6.QtWidgets import QComboBox

theme_selector = QComboBox()
theme_selector.addItems(["dark", "light"])
theme_selector.currentTextChanged.connect(app.set_theme)
layout.addWidget(theme_selector)
```

The selected theme auto-saves!

## Common Use Cases

### Use Case 1: Simple Branded App

**Goal**: Override a few colors for branding

```python
class BrandedApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "tab.activeBackground": "#7c3aed",
        },
    }
```

### Use Case 2: User Customizable App

**Goal**: Let users change editor colors

```python
class CustomizableApp(VFThemedApplication):
    theme_config = {
        "base_theme": "dark",
        "allow_user_customization": True,
        "customizable_tokens": ["editor.background", "editor.foreground"],
        "persist_user_overrides": True,
    }

# In preferences dialog
from PySide6.QtWidgets import QColorDialog

def choose_background_color():
    app = VFThemedApplication.instance()
    current = app._theme_manager.get_effective_color("editor.background", "#1e1e2e")

    color = QColorDialog.getColor(QColor(current), None, "Choose Background")
    if color.isValid():
        app.customize_color("editor.background", color.name(), persist=True)
```

### Use Case 3: Manual Override (No VFThemedApplication)

**Goal**: Quick color tweaks without subclassing

```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.core.manager import ThemeManager

app = ThemedApplication(sys.argv)
app.set_theme("dark")

# Override specific colors
manager = ThemeManager.get_instance()
manager.set_app_override("editor.background", "#1e1e2e")
manager.set_app_override("tab.activeBackground", "#7c3aed")
```

## Available Tokens

Common color tokens you can override:

**Editor**:
- `editor.background`
- `editor.foreground`
- `editor.selectionBackground`
- `editor.lineHighlight`

**UI Elements**:
- `tab.activeBackground`
- `tab.inactiveBackground`
- `button.background`
- `button.foreground`
- `button.hoverBackground`

**Status & Panels**:
- `statusBar.background`
- `statusBar.foreground`
- `sideBar.background`
- `panel.background`

See the theme browser in examples for a complete list!

## Running the Examples

Try the included examples to see the overlay system in action:

```bash
# Basic runtime overrides
python examples/16_simple_overlay.py

# Declarative branding
python examples/17_branded_app.py

# User customization with color picker
python examples/18_customizable_app.py

# Advanced ThemeManager API
python examples/19_advanced_manual.py
```

## Troubleshooting

### Colors Don't Change?

**Check**: Did you call `set_app_override` or `set_user_override`?

```python
manager = ThemeManager.get_instance()
manager.set_app_override("editor.background", "#1e1e2e")
# Widgets should update immediately
```

### Preferences Don't Save?

**Check**: Did you provide `app_id`?

```python
# ❌ Won't save
app = MyApp(sys.argv)

# ✅ Will save
app = MyApp(sys.argv, app_id="MyApp")
```

**Check**: Is `persist_user_overrides` enabled?

```python
class MyApp(VFThemedApplication):
    theme_config = {
        "persist_user_overrides": True,  # Must be True
    }
```

### Widget Doesn't See Override?

**Check**: Is the widget a ThemedWidget?

```python
from vfwidgets_theme import ThemedWidget

class MyWidget(ThemedWidget):  # ✅ Correct
    theme_config = {
        "background": "editor.background",
    }
```

### Old QSettings Key?

**Check**: Are you migrating from manual persistence?

See "Scenario 3: Migrating Existing Theme Persistence" in OVERLAY-MIGRATION-GUIDE.md

## Tips & Tricks

### Tip 1: Inspect Current Overrides

```python
manager = ThemeManager.get_instance()
print("App overrides:", manager.get_app_overrides())
print("User overrides:", manager.get_user_overrides())
print("All effective:", manager.get_all_effective_overrides())
```

### Tip 2: Preview Colors Before Saving

```python
# Set without persist
app.customize_color("editor.background", "#ff0000", persist=False)

# User sees the change
# If they like it: save manually
app.save_user_preferences()

# If they don't like it: reset
manager.remove_user_override("editor.background")
```

### Tip 3: Bulk Color Changes

```python
# Apply multiple colors at once (faster)
manager.set_app_overrides_bulk({
    "editor.background": "#1e1e2e",
    "tab.activeBackground": "#7c3aed",
    "button.background": "#313244",
})
```

### Tip 4: Check What's Customizable

```python
app = VFThemedApplication.instance()

# Get list of customizable tokens
customizable = app.get_customizable_tokens()

# Check if specific token is customizable
if app.is_token_customizable("editor.background"):
    # Show customization UI
    pass
```

## What's Next?

**Learn More**:
- Read: `docs/overlay-system-specification.md` - Full specification
- Read: `docs/OVERLAY-MIGRATION-GUIDE.md` - Detailed migration guide
- Browse: `examples/16-19_*.py` - Complete working examples

**Try Advanced Features**:
- Restrict customizable tokens
- Implement color picker UI
- Create color presets
- Export/import user preferences

**Get Help**:
- Check examples for working code
- Read the migration guide for common scenarios
- Review test files for API usage examples

## Complete Example

Here's a complete minimal example in one file:

```python
#!/usr/bin/env python3
"""Minimal overlay system example"""

import sys
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QPushButton
from vfwidgets_theme import ThemedWidget
from vfwidgets_theme.widgets import VFThemedApplication
from vfwidgets_theme.core.manager import ThemeManager


class BrandedApp(VFThemedApplication):
    """App with purple branding"""
    theme_config = {
        "base_theme": "dark",
        "app_overrides": {
            "tab.activeBackground": "#7c3aed",  # Purple!
        },
    }


class MainWindow(ThemedWidget):
    """Main window"""
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        label = QLabel("🎨 My Branded App")
        label.setStyleSheet("font-size: 18pt; padding: 10px;")
        layout.addWidget(label)

        editor = QTextEdit("The tabs above are purple - that's our brand color!")
        layout.addWidget(editor)

        btn = QPushButton("Click Me")
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)

        self.setWindowTitle("Branded App Example")
        self.resize(600, 400)

    def on_click(self):
        # Example: override another color at runtime
        manager = ThemeManager.get_instance()
        manager.set_app_override("button.background", "#ff0000")
        print("Button is now red!")


def main():
    app = BrandedApp(sys.argv, app_id="BrandedApp")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

Save as `my_app.py`, run with `python my_app.py` - done!

---

**🎉 Congratulations!** You now know how to use the Theme Overlay System!

**Next**: Try the examples and explore advanced features in the migration guide.
