#!/usr/bin/env python3
"""Test links and images."""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_markdown import MarkdownViewer


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Test Links & Images")
    window.resize(800, 600)

    viewer = MarkdownViewer()
    window.setCentralWidget(viewer)

    def load_test():
        viewer.set_markdown(
            """
# Links and Images Test

## Links
[Visit Google](https://www.google.com)
[Visit GitHub](https://github.com)

## Base64 Image
![Test SVG](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMTIwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iIzMzMyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjI0IiBmaWxsPSIjZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+VGVzdDwvdGV4dD48L3N2Zz4=)

## Regular Image (from web)
![Python Logo](https://www.python.org/static/community_logos/python-logo.png)

Links should be clickable and images should display.
        """
        )
        print("Test content loaded")

    viewer.viewer_ready.connect(load_test)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
