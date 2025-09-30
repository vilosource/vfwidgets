# 🚀 VFWidgets Theme System - Start Here!

**Make your Qt widgets beautiful in 30 seconds.**

## Three Steps to Themed Widgets

### 1️⃣ Install
```bash
pip install vfwidgets-theme
```

### 2️⃣ Create Your Widget
```python
from vfwidgets_theme import ThemedWidget

class YourWidget(ThemedWidget):
    pass  # ✅ That's it! Your widget is now themed!
```

### 3️⃣ Run Your App
```python
from vfwidgets_theme import ThemedApplication
import sys

app = ThemedApplication(sys.argv)
app.set_theme("dark-modern")  # or "light-default"

window = YourWidget()
window.show()

app.exec()
```

## 🎉 You're Done!

Your widget now:
- ✅ **Automatically themed** - Inherits beautiful colors from the theme
- ✅ **Theme switching** - Changes when user switches themes
- ✅ **Memory safe** - No leaks, proper cleanup handled
- ✅ **Thread safe** - Works correctly in multi-threaded apps
- ✅ **Testable** - Clean architecture enables easy testing

## Want Custom Colors?

```python
class YourWidget(ThemedWidget):
    # Declare the theme properties you need
    theme_config = {
        'accent': 'button.accent',
        'glow': 'button.glow'
    }

    def paintEvent(self, event):
        color = self.theme.accent  # Use your theme colors!
```

## Common Patterns

```python
# Basic Widget - Just inherit ThemedWidget
class MyLabel(ThemedWidget):
    pass

# Widget with Custom Colors
class MyButton(ThemedWidget):
    theme_config = {
        'bg': 'button.background',
        'hover': 'button.hoverBackground'
    }

# Widget that Reacts to Theme Changes
class MyEditor(ThemedWidget):
    def on_theme_changed(self):
        self.update_syntax_colors()
```

## What's Next?

- **5 min**: [Your First Themed Widget](tutorials/first-widget.md)
- **10 min**: [Common Widget Patterns](patterns-cookbook.md)
- **When needed**: [Full API Reference](api-REFERENCE.md)
- **If curious**: [How It Works](architecture-DESIGN.md)

---

**Remember:** `ThemedWidget` handles all the complexity for you - proper memory management, thread safety, and clean architecture are built in. You just focus on your widget's functionality!

**Need help?** The [Troubleshooting Guide](troubleshooting-GUIDE.md) has solutions to common issues.