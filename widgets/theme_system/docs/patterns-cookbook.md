# Patterns Cookbook - VFWidgets Theme System

A collection of common widget patterns using ThemedWidget. Copy, paste, and customize!

## Table of Contents

1. [Basic Patterns](#basic-patterns)
2. [Button Patterns](#button-patterns)
3. [Editor Patterns](#editor-patterns)
4. [List & Table Patterns](#list--table-patterns)
5. [Custom Paint Patterns](#custom-paint-patterns)
6. [Container Patterns](#container-patterns)
7. [Dialog Patterns](#dialog-patterns)
8. [Status & Notification Patterns](#status--notification-patterns)
9. [Animation Patterns](#animation-patterns)
10. [Advanced Patterns](#advanced-patterns)

## Basic Patterns

### Minimal Themed Widget

```python
from vfwidgets_theme import ThemedWidget

class MinimalWidget(ThemedWidget):
    """The absolute minimum - automatically themed!"""
    pass
```

### Widget with Theme Properties

```python
class ColoredWidget(ThemedWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

    def paintEvent(self, event):
        # Use theme colors
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme.bg))
```

### Widget That Reacts to Theme Changes

```python
class ReactiveWidget(ThemedWidget):
    def on_theme_changed(self):
        """Automatically called when theme changes"""
        print(f"Now using {'dark' if self.is_dark_theme else 'light'} theme")
        self.update()  # Trigger repaint
```

## Button Patterns

### Basic Themed Button

```python
class ThemedButton(ThemedWidget, QPushButton):
    """QPushButton with automatic theming"""

    theme_config = {
        'bg': 'button.background',
        'hover': 'button.hoverBackground',
        'pressed': 'button.activeBackground',
        'fg': 'button.foreground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.bg};
                color: {self.theme.fg};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.hover};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.pressed};
            }}
        """)
```

### Icon Button with Theme-Aware Icons

```python
class IconButton(ThemedWidget, QPushButton):
    """Button that switches icons based on theme"""

    def __init__(self, icon_name: str, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.update_icon()

    def on_theme_changed(self):
        self.update_icon()

    def update_icon(self):
        # Use different icons for dark/light themes
        theme_folder = "dark" if self.is_dark_theme else "light"
        icon_path = f"icons/{theme_folder}/{self.icon_name}.svg"
        self.setIcon(QIcon(icon_path))
```

### Accent Button

```python
class AccentButton(ThemedWidget, QPushButton):
    """Button using accent colors"""

    theme_config = {
        'accent': 'accent.primary',
        'accent_hover': 'accent.primaryHover',
        'text': 'accent.foreground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent};
                color: {self.theme.text};
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_hover};
            }}
        """)
```

## Editor Patterns

### Themed Text Editor

```python
class ThemedEditor(ThemedWidget, QTextEdit):
    """Text editor with syntax highlighting support"""

    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'selection': 'editor.selectionBackground',
        'line_number': 'editorLineNumber.foreground',
        'current_line': 'editor.lineHighlightBackground'
    }

    def on_theme_changed(self):
        # Update editor palette
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(self.theme.bg))
        palette.setColor(QPalette.Text, QColor(self.theme.fg))
        palette.setColor(QPalette.Highlight, QColor(self.theme.selection))
        self.setPalette(palette)

        # Update syntax highlighter if present
        if hasattr(self, 'highlighter'):
            self.highlighter.update_theme_colors()
```

### Code Editor with Line Numbers

```python
class CodeEditor(ThemedWidget):
    """Code editor with themed line numbers"""

    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground',
        'line_bg': 'editorLineNumber.background',
        'line_fg': 'editorLineNumber.foreground',
        'active_line': 'editorLineNumber.activeForeground'
    }

    def __init__(self):
        super().__init__()
        self.editor = QPlainTextEdit()
        self.line_numbers = LineNumberWidget(self.editor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_numbers)
        layout.addWidget(self.editor)

    def on_theme_changed(self):
        # Update editor
        self.editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme.bg};
                color: {self.theme.fg};
            }}
        """)

        # Update line numbers
        self.line_numbers.setStyleSheet(f"""
            background-color: {self.theme.line_bg};
            color: {self.theme.line_fg};
        """)
```

## List & Table Patterns

### Themed List Widget

```python
class ThemedList(ThemedWidget, QListWidget):
    """List with alternating row colors"""

    theme_config = {
        'bg': 'list.background',
        'fg': 'list.foreground',
        'alt_bg': 'list.alternateBackground',
        'hover': 'list.hoverBackground',
        'selected': 'list.activeSelectionBackground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme.bg};
                color: {self.theme.fg};
                alternate-background-color: {self.theme.alt_bg};
            }}
            QListWidget::item:hover {{
                background-color: {self.theme.hover};
            }}
            QListWidget::item:selected {{
                background-color: {self.theme.selected};
            }}
        """)
        self.setAlternatingRowColors(True)
```

### Themed Table

```python
class ThemedTable(ThemedWidget, QTableWidget):
    """Table with themed headers and cells"""

    theme_config = {
        'bg': 'table.background',
        'fg': 'table.foreground',
        'header_bg': 'table.headerBackground',
        'header_fg': 'table.headerForeground',
        'grid': 'table.gridColor',
        'selected': 'table.selectionBackground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme.bg};
                color: {self.theme.fg};
                gridline-color: {self.theme.grid};
            }}
            QHeaderView::section {{
                background-color: {self.theme.header_bg};
                color: {self.theme.header_fg};
                padding: 4px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme.selected};
            }}
        """)
```

## Custom Paint Patterns

### Custom Painted Widget

```python
class CustomPaintWidget(ThemedWidget):
    """Widget with custom painting using theme colors"""

    theme_config = {
        'primary': 'accent.primary',
        'secondary': 'accent.secondary',
        'bg': 'panel.background',
        'border': 'panel.border'
    }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(self.theme.bg))

        # Border
        painter.setPen(QPen(QColor(self.theme.border), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        # Custom drawing with theme colors
        painter.setBrush(QColor(self.theme.primary))
        painter.drawEllipse(self.rect().center(), 50, 50)

    def on_theme_changed(self):
        self.update()  # Trigger repaint
```

### Gradient Widget

```python
class GradientWidget(ThemedWidget):
    """Widget with themed gradient background"""

    theme_config = {
        'start': 'gradient.start',
        'end': 'gradient.end'
    }

    def paintEvent(self, event):
        painter = QPainter(self)

        # Create gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(self.theme.start))
        gradient.setColorAt(1, QColor(self.theme.end))

        painter.fillRect(self.rect(), gradient)

    def on_theme_changed(self):
        self.update()
```

## Container Patterns

### Themed Panel

```python
class ThemedPanel(ThemedWidget):
    """Panel with title and content area"""

    theme_config = {
        'title_bg': 'panel.titleBackground',
        'title_fg': 'panel.titleForeground',
        'content_bg': 'panel.background',
        'border': 'panel.border'
    }

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        self.title_label = QLabel(title)
        self.title_label.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(self.title_label)

        # Content area
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        layout.addWidget(self.content)

    def on_theme_changed(self):
        self.title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme.title_bg};
                color: {self.theme.title_fg};
                font-weight: bold;
            }}
        """)
        self.content.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.content_bg};
                border: 1px solid {self.theme.border};
                border-top: none;
            }}
        """)

    def add_widget(self, widget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)
```

### Collapsible Section

```python
class CollapsibleSection(ThemedWidget):
    """Collapsible section with theme-aware chevron"""

    theme_config = {
        'header_bg': 'sideBar.background',
        'header_fg': 'sideBar.foreground',
        'content_bg': 'editor.background',
        'chevron': 'icon.foreground'
    }

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.collapsed = False
        self.setup_ui(title)

    def setup_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)

        # Header
        self.header = QPushButton(f"▶ {title}")
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)

        # Content
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        layout.addWidget(self.content)

    def toggle(self):
        self.collapsed = not self.collapsed
        self.content.setVisible(not self.collapsed)
        chevron = "▼" if not self.collapsed else "▶"
        text = self.header.text()[2:]  # Remove old chevron
        self.header.setText(f"{chevron} {text}")

    def on_theme_changed(self):
        self.header.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.header_bg};
                color: {self.theme.header_fg};
                text-align: left;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.theme.header_bg};
                filter: brightness(110%);
            }}
        """)
        self.content.setStyleSheet(f"""
            background-color: {self.theme.content_bg};
            padding: 10px;
        """)
```

## Dialog Patterns

### Themed Dialog

```python
class ThemedDialog(ThemedWidget, QDialog):
    """Dialog with themed title and buttons"""

    theme_config = {
        'bg': 'dialog.background',
        'fg': 'dialog.foreground',
        'button_bg': 'button.background',
        'button_fg': 'button.foreground'
    }

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setup_ui(message)

    def setup_ui(self, message):
        layout = QVBoxLayout(self)

        # Message
        self.message = QLabel(message)
        layout.addWidget(self.message)

        # Buttons
        buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.bg};
            }}
            QLabel {{
                color: {self.theme.fg};
            }}
            QPushButton {{
                background-color: {self.theme.button_bg};
                color: {self.theme.button_fg};
                padding: 6px 12px;
                border-radius: 4px;
            }}
        """)
```

## Status & Notification Patterns

### Status Bar

```python
class ThemedStatusBar(ThemedWidget, QStatusBar):
    """Status bar with context-aware colors"""

    theme_config = {
        'bg': 'statusBar.background',
        'fg': 'statusBar.foreground',
        'error': 'statusBar.errorForeground',
        'warning': 'statusBar.warningForeground',
        'success': 'statusBar.successForeground'
    }

    def on_theme_changed(self):
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.theme.bg};
                color: {self.theme.fg};
            }}
        """)

    def show_error(self, message: str):
        self.setStyleSheet(f"color: {self.theme.error};")
        self.showMessage(message, 5000)

    def show_success(self, message: str):
        self.setStyleSheet(f"color: {self.theme.success};")
        self.showMessage(message, 5000)
```

### Notification Toast

```python
class NotificationToast(ThemedWidget):
    """Toast notification with theme colors"""

    theme_config = {
        'bg': 'notification.background',
        'fg': 'notification.foreground',
        'border': 'notification.border',
        'error_bg': 'notification.errorBackground',
        'success_bg': 'notification.successBackground'
    }

    def __init__(self, message: str, notification_type="info"):
        super().__init__()
        self.notification_type = notification_type
        self.setup_ui(message)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def setup_ui(self, message):
        layout = QHBoxLayout(self)
        self.label = QLabel(message)
        layout.addWidget(self.label)

    def on_theme_changed(self):
        bg_color = {
            'error': self.theme.error_bg,
            'success': self.theme.success_bg,
            'info': self.theme.bg
        }.get(self.notification_type, self.theme.bg)

        self.setStyleSheet(f"""
            NotificationToast {{
                background-color: {bg_color};
                border: 2px solid {self.theme.border};
                border-radius: 8px;
            }}
            QLabel {{
                color: {self.theme.fg};
                padding: 10px;
            }}
        """)
```

## Animation Patterns

### Animated Theme Transition

```python
class AnimatedWidget(ThemedWidget):
    """Widget with animated color transitions"""

    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }

    def __init__(self):
        super().__init__()
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(300)

    color = Property(QColor, lambda self: self._color,
                    lambda self, c: self.set_color(c))

    def set_color(self, color):
        self._color = color
        self.update()

    def on_theme_changed(self):
        # Animate color transition
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(QColor(self.theme.bg))
        self.animation.start()
```

## Advanced Patterns

### Multi-Theme Widget

```python
class MultiThemeWidget(ThemedWidget):
    """Widget supporting multiple theme contexts"""

    def __init__(self, context="default"):
        self.theme_context = context
        super().__init__()

    def set_context(self, context: str):
        """Switch theme context (e.g., 'danger', 'success', 'warning')"""
        self.theme_context = context
        self.refresh_theme()

    def get_theme_color(self, key: str, default=None):
        """Override to use context-specific colors"""
        context_key = f"{self.theme_context}.{key}"
        return super().get_theme_color(context_key, default)
```

### Theme Preview Widget

```python
class ThemePreview(ThemedWidget):
    """Widget showing all theme colors"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)

        self.color_widgets = {}
        theme_properties = [
            'window.background', 'window.foreground',
            'button.background', 'button.foreground',
            'editor.background', 'editor.foreground',
            'panel.background', 'panel.border'
        ]

        for i, prop in enumerate(theme_properties):
            label = QLabel(prop)
            color_widget = QWidget()
            color_widget.setFixedSize(50, 30)

            layout.addWidget(label, i, 0)
            layout.addWidget(color_widget, i, 1)

            self.color_widgets[prop] = color_widget

    def on_theme_changed(self):
        for prop, widget in self.color_widgets.items():
            color = self.get_theme_color(prop, "#000000")
            widget.setStyleSheet(f"background-color: {color};")
```

### Composite Widget Pattern

```python
class CompositeThemedWidget(ThemedWidget):
    """Complex widget composed of multiple themed components"""

    def __init__(self):
        super().__init__()
        self.setup_components()

    def setup_components(self):
        layout = QVBoxLayout(self)

        # All child widgets automatically get themed!
        self.toolbar = ThemedToolbar()
        self.editor = ThemedEditor()
        self.status = ThemedStatusBar()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.editor)
        layout.addWidget(self.status)

    def on_theme_changed(self):
        # Parent theme change automatically propagates to children
        # No need to manually update child widgets!
        pass
```

## Best Practices Reminder

1. **Always inherit from ThemedWidget** - It handles all complexity
2. **Use theme_config** to declare needed properties
3. **Override on_theme_changed()** to update custom painting
4. **Call self.update()** in on_theme_changed() if doing custom painting
5. **Never hardcode colors** - Always use theme properties
6. **Child widgets are automatically themed** if parent is ThemedWidget

---

*These patterns demonstrate the simplicity of ThemedWidget - clean architecture is built in, you just focus on your widget logic!*