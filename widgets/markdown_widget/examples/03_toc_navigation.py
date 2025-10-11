#!/usr/bin/env python3
"""
Example: TOC Extraction and Navigation

This example demonstrates:
1. Extracting table of contents from markdown
2. Displaying TOC in a sidebar
3. Navigating to headings by clicking TOC items
4. Responding to TOC changes when content updates
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown import MarkdownViewer


class TOCNavigationDemo(QWidget):
    """Demo widget showing TOC extraction and navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - TOC & Navigation Demo")
        self.resize(1200, 800)

        # Create layout
        layout = QVBoxLayout(self)

        # Create splitter for TOC sidebar and viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: TOC panel
        toc_panel = self._create_toc_panel()
        splitter.addWidget(toc_panel)

        # Right side: Markdown viewer
        self.viewer = MarkdownViewer()
        splitter.addWidget(self.viewer)

        # Set splitter proportions (20% TOC, 80% viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)

        # Connect signals
        self.viewer.viewer_ready.connect(self._on_viewer_ready)
        self.viewer.toc_changed.connect(self._on_toc_changed)
        self.toc_list.itemClicked.connect(self._on_toc_item_clicked)

        # Connect demo buttons
        self.load_sample_btn.clicked.connect(self._load_sample)
        self.load_simple_btn.clicked.connect(self._load_simple)
        self.print_toc_btn.clicked.connect(self._print_toc)

    def _create_toc_panel(self) -> QWidget:
        """Create TOC sidebar panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        layout.addWidget(QPushButton("Table of Contents"))

        # TOC list
        self.toc_list = QListWidget()
        layout.addWidget(self.toc_list)

        # Demo buttons
        self.load_sample_btn = QPushButton("Load SAMPLE.md")
        self.load_simple_btn = QPushButton("Load Simple Example")
        self.print_toc_btn = QPushButton("Print TOC to Console")

        layout.addWidget(self.load_sample_btn)
        layout.addWidget(self.load_simple_btn)
        layout.addWidget(self.print_toc_btn)

        return panel

    def _on_viewer_ready(self):
        """Called when viewer is ready - load initial content."""
        print("[Demo] Viewer ready - loading initial content")
        self._load_sample()

    def _on_toc_changed(self, toc: list):
        """Called when TOC changes - update sidebar.

        Args:
            toc: List of heading dictionaries
        """
        print(f"[Demo] TOC changed: {len(toc)} headings")

        # Clear and repopulate list
        self.toc_list.clear()

        for heading in toc:
            level = heading["level"]
            text = heading["text"]
            heading_id = heading["id"]

            # Create indented item based on level (without ### markers)
            indent = "  " * (level - 1)
            item_text = f"{indent}{text}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, heading_id)  # Store ID for navigation

            self.toc_list.addItem(item)

    def _on_toc_item_clicked(self, item: QListWidgetItem):
        """Navigate to heading when TOC item is clicked.

        Args:
            item: Clicked list item
        """
        heading_id = item.data(Qt.ItemDataRole.UserRole)
        print(f"[Demo] Navigating to heading: {heading_id}")
        self.viewer.scroll_to_heading(heading_id)

    def _load_sample(self):
        """Load the full SAMPLE.md file."""
        sample_path = Path(__file__).parent / "SAMPLE.md"

        if sample_path.exists():
            print(f"[Demo] Loading {sample_path}")
            self.viewer.load_file(str(sample_path))
        else:
            print(f"[Demo] SAMPLE.md not found at {sample_path}")
            self._load_simple()

    def _load_simple(self):
        """Load a simple example with multiple headings."""
        markdown = """# Main Title

This is the introduction with some **bold text**.

## Section 1: Getting Started

Here's some content in the first section.

### Subsection 1.1

More detailed content here.

### Subsection 1.2

Additional details.

## Section 2: Advanced Topics

Second major section with interesting content.

### Subsection 2.1: Deep Dive

In-depth exploration of the topic.

#### Sub-subsection 2.1.1

Very detailed information here.

## Section 3: Conclusion

Final thoughts and summary.

### Resources

- [Documentation](https://example.com)
- [GitHub](https://github.com)

### Next Steps

What to do after reading this document.
"""
        print("[Demo] Loading simple example")
        self.viewer.set_markdown(markdown)

    def _print_toc(self):
        """Print current TOC to console."""
        toc = self.viewer.get_toc()
        print("\n=== Table of Contents ===")
        for heading in toc:
            level = heading["level"]
            text = heading["text"]
            heading_id = heading["id"]
            indent = "  " * (level - 1)
            # Use bullet points instead of ### markers
            bullet = "•" if level > 1 else "▸"
            print(f"{indent}{bullet} {text} (id: {heading_id})")
        print(f"\nTotal: {len(toc)} headings\n")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)

    demo = TOCNavigationDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
