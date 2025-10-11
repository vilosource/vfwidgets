#!/usr/bin/env python3
"""
Example: Keyboard Shortcuts

This example demonstrates:
1. Built-in keyboard shortcuts (find, zoom, scroll)
2. Custom keyboard shortcuts
3. Shortcut event handling
"""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QStatusBar, QVBoxLayout, QWidget
from vfwidgets_markdown import MarkdownViewer


class ShortcutsDemo(QWidget):
    """Demo widget showing keyboard shortcuts."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Keyboard Shortcuts Demo")
        self.resize(1000, 700)

        # Create layout
        layout = QVBoxLayout(self)

        # Info label
        info = QLabel("Keyboard shortcuts enabled! Try the shortcuts listed below.")
        info.setStyleSheet("font-weight: bold; padding: 10px; background: #e3f2fd;")
        layout.addWidget(info, stretch=0)

        # Create markdown viewer
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar, stretch=0)
        self.status_bar.showMessage("Ready - Try pressing Ctrl+F, Ctrl+Plus, Home, End...")

        # Enable shortcuts
        self.viewer.enable_shortcuts(True)

        # Set custom shortcuts
        self.viewer.set_custom_shortcuts(
            {"Ctrl+k": "clear_content", "Ctrl+r": "reload_content", "Ctrl+t": "toggle_theme"}
        )

        # Connect custom shortcut signal
        self.viewer.shortcut_triggered.connect(self._on_shortcut_triggered)

        # Load content when ready
        self.viewer.viewer_ready.connect(self._on_viewer_ready)

    def _on_viewer_ready(self):
        """Load demo content."""
        content = """# Keyboard Shortcuts Demo

This demo showcases the built-in and custom keyboard shortcuts.

## Built-in Shortcuts

### Find
- **Ctrl+F** (Cmd+F on Mac): Open browser's find dialog
- Try it: Press Ctrl+F and search for "zoom"

### Zoom
- **Ctrl+Plus** (Cmd+Plus): Zoom in
- **Ctrl+Minus** (Cmd+Minus): Zoom out
- **Ctrl+0** (Cmd+0): Reset zoom to 100%

Try zooming in and out with the keyboard!

### Scroll Navigation
- **Home**: Scroll to top of document
- **End**: Scroll to bottom of document
- **Page Up**: Scroll up one page
- **Page Down**: Scroll down one page

### Other
- **Escape**: Clear text selection

## Custom Shortcuts

This demo has 3 custom shortcuts defined:

- **Ctrl+K**: Clear content (custom action: `clear_content`)
- **Ctrl+R**: Reload content (custom action: `reload_content`)
- **Ctrl+T**: Toggle theme (custom action: `toggle_theme`)

Try pressing these shortcuts! The status bar will show which action was triggered.

## Code Example

```python
from vfwidgets_markdown import MarkdownViewer

viewer = MarkdownViewer()

# Enable built-in shortcuts
viewer.enable_shortcuts(True)

# Set custom shortcuts
viewer.set_custom_shortcuts({
    "Ctrl+k": "clear_content",
    "Ctrl+r": "reload_content",
    "Ctrl+t": "toggle_theme"
})

# Handle custom shortcuts
viewer.shortcut_triggered.connect(
    lambda action, combo: print(f"Triggered: {action} ({combo})")
)
```

## Implementation Details

### Built-in Shortcuts
- Cross-platform support (Ctrl on Windows/Linux, Cmd on Mac)
- Smooth scrolling animations
- Browser native find dialog
- CSS zoom for responsive scaling

### Custom Shortcuts
- Define any key combination: "Ctrl+K", "Shift+Alt+F", etc.
- Map to custom action names
- Receive signals when triggered
- Full modifier key support (Ctrl, Shift, Alt)

## Test Section

Scroll down to test Home/End keys...

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris.

### More Content

Press **Home** to jump to the top, or **End** to jump to the bottom.

### Math Example

Try zooming in/out on this equation:

$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$

### Diagram Example

Zoom affects diagrams too:

```mermaid
graph LR
    A[Press Ctrl+F] --> B[Find Text]
    C[Press Ctrl+Plus] --> D[Zoom In]
    E[Press Home] --> F[Scroll Top]
```

## Bottom of Document

You made it! Press **Home** to go back to the top, or try the other shortcuts.
"""
        self.viewer.set_markdown(content)
        print("[Demo] Loaded keyboard shortcuts demo")

    def _on_shortcut_triggered(self, action: str, combo: str):
        """Handle custom shortcut triggers."""
        message = f"Custom shortcut: {action} ({combo})"
        self.status_bar.showMessage(message, 5000)
        print(f"[Demo] {message}")

        # Handle the actions
        if action == "clear_content":
            self.viewer.set_markdown("# Content Cleared\n\nPress Ctrl+R to reload.")
        elif action == "reload_content":
            self._on_viewer_ready()  # Reload original content
        elif action == "toggle_theme":
            # This would toggle theme if theme system is available
            self.status_bar.showMessage("Theme toggle not implemented in this demo", 3000)


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    demo = ShortcutsDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
