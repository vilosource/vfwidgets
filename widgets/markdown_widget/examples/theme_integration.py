#!/usr/bin/env python3
"""
Example: Theme System Integration

This example demonstrates:
1. Automatic theme integration with vfwidgets-theme
2. Theme switching between light and dark
3. Custom theme colors applied to markdown rendering
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown import MarkdownViewer

# Check if theme system is available
try:
    from vfwidgets_theme import ThemedApplication

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    print("[Warning] vfwidgets-theme not available. Install with: pip install vfwidgets-theme")


class ThemeDemo(QWidget):
    """Demo widget showing theme integration."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Theme Integration Demo")
        self.resize(1200, 800)

        # Create layout
        layout = QVBoxLayout(self)

        # Create button panel
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel)

        # Create markdown viewer
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer)

        # Load initial content when ready
        self.viewer.viewer_ready.connect(self._on_viewer_ready)

    def _create_button_panel(self) -> QWidget:
        """Create panel with theme control buttons."""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Theme switching buttons
        if THEME_AVAILABLE:
            self.light_btn = QPushButton("Light Default")
            self.dark_btn = QPushButton("Dark Default")
            self.vscode_btn = QPushButton("VS Code Dark+")
            self.vilo_btn = QPushButton("Vilo Theme")

            self.light_btn.clicked.connect(lambda: self._switch_theme("Light Default"))
            self.dark_btn.clicked.connect(lambda: self._switch_theme("Dark Default"))
            self.vscode_btn.clicked.connect(lambda: self._switch_theme("VSCode Dark+"))
            self.vilo_btn.clicked.connect(lambda: self._switch_theme("Vilo"))

            layout.addWidget(self.light_btn)
            layout.addWidget(self.dark_btn)
            layout.addWidget(self.vscode_btn)
            layout.addWidget(self.vilo_btn)
        else:
            # Fallback to manual theme switching
            self.light_btn = QPushButton("Light")
            self.dark_btn = QPushButton("Dark")

            self.light_btn.clicked.connect(lambda: self.viewer.set_theme("light"))
            self.dark_btn.clicked.connect(lambda: self.viewer.set_theme("dark"))

            layout.addWidget(self.light_btn)
            layout.addWidget(self.dark_btn)

        layout.addStretch()

        return panel

    def _switch_theme(self, theme_name: str):
        """Switch the application theme."""
        if THEME_AVAILABLE:
            app = QApplication.instance()
            if hasattr(app, "set_theme"):
                app.set_theme(theme_name)
                print(f"[Demo] Switched to theme: {theme_name}")

    def _on_viewer_ready(self):
        """Called when viewer is ready - load demo content."""
        print("[Demo] Viewer ready - loading demo content")

        # Load markdown content
        markdown = """# Theme Integration Demo

This document demonstrates **automatic theme integration** with the VFWidgets theme system.

## Features

The MarkdownViewer automatically:
- 🎨 Adapts to the current application theme
- 🌗 Switches between light and dark modes
- 🔄 Updates colors dynamically when theme changes
- 💡 Uses theme tokens for consistent styling

## Themed Elements

### Text and Headings

All text colors are derived from the current theme, including:
- **Bold text** inherits the foreground color
- *Italic text* uses the same theme-aware colors
- ~~Strikethrough~~ follows theme conventions

### Code Blocks

Code blocks use theme-aware syntax highlighting:

```python
def fibonacci(n):
    \"\"\"Calculate fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# The colors adapt to your theme!
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### Tables

Tables use theme tokens for borders and backgrounds:

| Feature | Light Theme | Dark Theme |
|---------|-------------|------------|
| Background | Light | Dark |
| Text | Dark | Light |
| Borders | Gray | Darker Gray |
| Headers | Subtle BG | Subtle BG |

### Blockquotes

> Blockquotes also adapt to the current theme.
>
> The border color and background color are derived from theme tokens.

### Links

Links use the theme's accent color: [VFWidgets GitHub](https://github.com/vilosource/vfwidgets)

## Try It Out!

Use the buttons above to switch between different themes and watch the markdown adapt in real-time!

- **Light Theme** - Clean, bright GitHub-style
- **Dark Theme** - Easy on the eyes for night coding
- **VS Code Dark** - Familiar VS Code colors
- **GitHub Light** - Classic GitHub markdown style

## Theme System Integration

When vfwidgets-theme is installed, the MarkdownViewer:

1. **Inherits from ThemedWidget** - Automatically receives theme updates
2. **Maps theme tokens** - Uses semantic color tokens like `editor.background`
3. **Updates dynamically** - No manual theme switching needed
4. **Falls back gracefully** - Works without theme system too

### Theme Token Mapping

The viewer maps these theme tokens:

- `editor.background` → Markdown background
- `editor.foreground` → Text color
- `textLink.foreground` → Link color
- `editor.code.background` → Code block background
- `widget.border` → Table borders

This ensures the markdown viewer integrates seamlessly with your application's theme!
"""

        self.viewer.set_markdown(markdown)


def main():
    """Run the demo."""
    # Create application with theme support if available
    if THEME_AVAILABLE:
        app = ThemedApplication(sys.argv)
        app.set_theme("github-light")  # Start with light theme
    else:
        app = QApplication(sys.argv)

    demo = ThemeDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
