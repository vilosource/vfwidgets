#!/usr/bin/env python3
"""Quick test for fixes."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_markdown import MarkdownViewer


def main():
    """Run quick test."""
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Test Fixes - Code Highlighting & Mermaid")
    window.resize(1000, 700)

    viewer = MarkdownViewer()
    window.setCentralWidget(viewer)

    def load_test():
        test_path = Path(__file__).parent.parent / "test_fixes.md"
        if test_path.exists():
            with open(test_path, encoding="utf-8") as f:
                content = f.read()
            viewer.set_markdown(content)
            print(f"Loaded test file: {test_path}")
        else:
            viewer.set_markdown(
                """
# Test

```python
# Code should be readable
print("test")
```

```mermaid
graph TD
    A --> B
```

```mermaid
classDiagram
    class Test
```
            """
            )

    viewer.viewer_ready.connect(load_test)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
