# Migration Guide: Using the New Convenience Classes

## Overview

VFWidgets Theme System now provides convenient single-inheritance classes that simplify widget creation.

## Old Pattern (Still Supported)

```python
from PySide6.QtWidgets import QWidget, QMainWindow
from vfwidgets_theme import ThemedWidget

class MyWidget(ThemedWidget, QWidget):  # Multiple inheritance
    pass

class MyWindow(ThemedWidget, QMainWindow):  # Multiple inheritance
    pass
```

## New Pattern (Recommended)

```python
from vfwidgets_theme import ThemedQWidget, ThemedMainWindow

class MyWidget(ThemedQWidget):  # Single inheritance - simpler!
    pass

class MyWindow(ThemedMainWindow):  # Single inheritance - simpler!
    pass
```

## Benefits of New Pattern

1. **Simpler** - Single inheritance instead of multiple
2. **Safer** - No inheritance order concerns
3. **Clearer** - Intent is obvious from the class name
4. **Backwards Compatible** - Old code keeps working

## Migration Steps

### Step 1: Identify Widget Type
- Using QWidget? → Switch to ThemedQWidget
- Using QMainWindow? → Switch to ThemedMainWindow
- Using QDialog? → Switch to ThemedDialog

### Step 2: Update Imports
```python
# Old
from PySide6.QtWidgets import QWidget
from vfwidgets_theme import ThemedWidget

# New
from vfwidgets_theme import ThemedQWidget
```

### Step 3: Update Class Definition
```python
# Old
class MyWidget(ThemedWidget, QWidget):
    pass

# New
class MyWidget(ThemedQWidget):
    pass
```

That's it! Everything else stays the same.

## Smart Property Defaults

The new API also includes smart defaults for theme properties:

```python
# Old - required getattr with defaults
bg = getattr(self.theme, 'background', '#ffffff')
fg = getattr(self.theme, 'foreground', '#000000')

# New - direct access with automatic smart defaults
bg = self.theme.background  # Returns sensible default if not in theme
fg = self.theme.foreground  # Returns sensible default if not in theme
```

## Complete Example: Before & After

### Before
```python
from PySide6.QtWidgets import QMainWindow, QLabel
from vfwidgets_theme import ThemedWidget, ThemedApplication
import sys

class MyWindow(ThemedWidget, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        # Verbose property access
        bg = getattr(self.theme, 'background', '#ffffff')
        self.setStyleSheet(f"background: {bg}")

app = ThemedApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

### After
```python
from vfwidgets_theme import ThemedMainWindow, ThemedApplication
import sys

class MyWindow(ThemedMainWindow):  # Simpler!
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        # Clean property access with smart defaults
        bg = self.theme.background
        self.setStyleSheet(f"background: {bg}")

app = ThemedApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

## No Breaking Changes

The old API continues to work. You can migrate at your own pace.