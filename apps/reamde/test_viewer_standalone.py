#!/usr/bin/env python3
"""Test MarkdownViewer standalone to verify it works."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownViewer


def main():
    app = QApplication(sys.argv)

    viewer = MarkdownViewer()
    viewer.resize(800, 600)
    viewer.show()

    # Load test file
    test_file = Path("DEMO1.md")
    if test_file.exists():
        content = test_file.read_text()
        print(f"[test] Read {len(content)} chars from {test_file}")
        viewer.set_markdown(content)
        viewer.set_base_path(test_file.parent)
        print("[test] Markdown content set")
    else:
        print(f"[test] ERROR: {test_file} not found")
        viewer.set_markdown("# Test\n\nThis is a test.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
