#!/usr/bin/env python3
"""
Quick Start: MarkdownViewer in 10 Lines

This is the simplest possible usage of MarkdownViewer.
No observers, no signals, no async handling - just show markdown!

The viewer automatically handles async initialization - content is
queued and loaded when ready. You don't need to worry about it.
"""

import sys

from PySide6.QtWidgets import QApplication

from vfwidgets_markdown import MarkdownViewer

# Create application
app = QApplication(sys.argv)

# Create viewer with content - that's it!
viewer = MarkdownViewer(
    initial_content="""
# Quick Start Example

This demonstrates the **simplest** usage of MarkdownViewer.

## Features Demonstrated

1. Content in constructor
2. Automatic async handling
3. No manual signals needed

## Code Highlighting

```python
def hello():
    print("Hello from MarkdownViewer!")
```

## Math Support

Inline: $E = mc^2$

Block:
$$
\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
$$

## Mermaid Diagram

```mermaid
graph LR
    A[Create Viewer] --> B[Set Content]
    B --> C[Show Widget]
    C --> D[Done!]
```

---

**That's it!** The viewer handles all the complexity internally.
"""
)

viewer.resize(800, 600)
viewer.setWindowTitle("MarkdownViewer - Quick Start")
viewer.show()

sys.exit(app.exec())
