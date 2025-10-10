#!/usr/bin/env python3
"""Basic usage example for MarkdownViewer widget.

This example demonstrates loading and displaying the SAMPLE.md file which
showcases all supported markdown features including:
- Basic formatting (bold, italic, headings, lists)
- Code blocks with syntax highlighting
- Mermaid diagrams (flowchart, sequence, class, gantt, state)
- Math equations (inline and block with KaTeX)
- Tables, task lists, emoji
- Footnotes, subscript, superscript
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_markdown import MarkdownViewer


def main():
    """Run the example application."""
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("MarkdownViewer - Feature Demonstration")
    window.resize(1200, 800)

    # Create markdown viewer widget
    viewer = MarkdownViewer()
    window.setCentralWidget(viewer)

    # Load SAMPLE.md from the same directory
    sample_path = Path(__file__).parent / "SAMPLE.md"
    if sample_path.exists():
        with open(sample_path, encoding="utf-8") as f:
            markdown_content = f.read()
        viewer.set_markdown(markdown_content)
        print(f"Loaded {len(markdown_content)} bytes from {sample_path}")
    else:
        # Fallback to simple content if SAMPLE.md not found
        viewer.set_markdown("""
# MarkdownViewer Demo

**SAMPLE.md not found!**

This is a fallback example showing basic markdown rendering.

- Feature 1
- Feature 2
- Feature 3

```python
print("Hello from MarkdownViewer!")
```
        """)
        print(f"Warning: {sample_path} not found, using fallback content")

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
