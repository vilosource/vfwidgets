#!/usr/bin/env python3
"""
Example: Live Editor with Preview

This example demonstrates:
1. Live markdown preview with debouncing
2. Sync mode to preserve scroll position
3. Signal handling (scroll, heading clicks, link clicks)
4. Split-pane editor layout
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown import MarkdownViewer


class LiveEditorDemo(QWidget):
    """Live markdown editor with preview."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Live Editor Demo")
        self.resize(1400, 800)

        # Create main layout
        layout = QVBoxLayout(self)

        # Create splitter for editor and preview
        splitter = QSplitter(Qt.Horizontal)

        # Create editor panel
        editor_panel = self._create_editor_panel()
        splitter.addWidget(editor_panel)

        # Create preview panel
        preview_panel = self._create_preview_panel()
        splitter.addWidget(preview_panel)

        # Set splitter sizes (40% editor, 60% preview)
        splitter.setSizes([560, 840])

        layout.addWidget(splitter, stretch=1)  # Splitter takes all available space

        # Create status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar, stretch=0)  # Status bar shrinks to content
        self.status_bar.showMessage("Ready")

        # Load initial content when viewer is ready
        self.viewer.viewer_ready.connect(self._on_viewer_ready)

    def _create_editor_panel(self) -> QWidget:
        """Create editor text area."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Label
        label = QLabel("Markdown Editor:")
        label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(label, stretch=0)  # Label shrinks to content

        # Text editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setPlaceholderText("Type markdown here...")
        layout.addWidget(self.editor, stretch=1)  # Editor takes remaining space

        # Connect text changed signal
        self.editor.textChanged.connect(self._on_text_changed)

        # Info label
        info = QLabel("Live preview with 25ms debounce")
        info.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(info, stretch=0)  # Info label shrinks to content

        return panel

    def _create_preview_panel(self) -> QWidget:
        """Create preview viewer."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Label
        label = QLabel("Live Preview:")
        label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(label, stretch=0)  # Label shrinks to content

        # Markdown viewer
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer, stretch=1)  # Viewer takes remaining space

        # Enable editor integration features
        self.viewer.enable_sync_mode(True)
        self.viewer.set_debounce_delay(25)  # 25ms debounce for instant feel

        # Connect signals
        self.viewer.scroll_position_changed.connect(self._on_scroll_changed)
        self.viewer.heading_clicked.connect(self._on_heading_clicked)
        self.viewer.link_clicked.connect(self._on_link_clicked)

        return panel

    def _on_viewer_ready(self):
        """Called when viewer is ready - load initial content."""
        # Temporarily disconnect scroll signal to avoid overwriting status
        self.viewer.scroll_position_changed.disconnect(self._on_scroll_changed)

        initial_content = """# Live Markdown Editor

Welcome to the live markdown editor demo!

## Features

This demo showcases:

1. **Live Preview** - See changes as you type
2. **Debouncing** - Updates are delayed by 25ms for instant feel
3. **Sync Mode** - Scroll position is preserved during updates
4. **Signal Handling** - Events are captured and displayed

## Try It Out

- Edit the text in the left panel
- Scroll in the preview
- Click on headings
- Click on links

### Scroll Position Tracking

The current scroll position is displayed in the status bar below.

### Interactive Elements

Click this heading or any other heading to see the event.

[Click this link](https://www.python.org) to see link click events.

## Code Example

```python
from vfwidgets_markdown import MarkdownViewer

viewer = MarkdownViewer()
viewer.enable_sync_mode(True)
viewer.set_debounce_delay(25)  # 25ms for near-instant updates

# Connect signals
viewer.scroll_position_changed.connect(lambda pos: print(f"Scrolled: {pos:.2%}"))
viewer.heading_clicked.connect(lambda id: print(f"Heading: {id}"))
viewer.link_clicked.connect(lambda url: print(f"Link: {url}"))
```

## Math Support

Inline math: $E=mc^2$

Block math:
$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$

## Diagram Support

```mermaid
graph LR
    A[Editor] -->|Text Change| B[Debounce]
    B -->|300ms delay| C[Render]
    C -->|Sync Mode| D[Restore Scroll]
```

## Keep Editing!

The preview updates automatically as you type, with smooth scrolling
preserved thanks to sync mode.
"""
        self.editor.setPlainText(initial_content)
        self.status_bar.showMessage("Editor ready - Start typing!", 5000)  # Show for 5 seconds

        # Reconnect scroll signal after a delay
        from PySide6.QtCore import QTimer

        QTimer.singleShot(
            1000, lambda: self.viewer.scroll_position_changed.connect(self._on_scroll_changed)
        )

    def _on_text_changed(self):
        """Handle text changes in editor."""
        content = self.editor.toPlainText()
        self.viewer.set_markdown(content)

    def _on_scroll_changed(self, position: float):
        """Handle scroll position changes."""
        percentage = position * 100
        self.status_bar.showMessage(f"Scroll position: {percentage:.1f}%")

    def _on_heading_clicked(self, heading_id: str):
        """Handle heading clicks."""
        message = f"Heading clicked: #{heading_id}"
        self.status_bar.showMessage(message, 3000)  # Show for 3 seconds
        print(f"[Demo] {message}")

    def _on_link_clicked(self, url: str):
        """Handle link clicks."""
        message = f"Link clicked: {url}"
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds
        print(f"[Demo] {message}")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    demo = LiveEditorDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
