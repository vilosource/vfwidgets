#!/usr/bin/env python3
"""
Example: Export Functionality

This example demonstrates:
1. Exporting to HTML (with and without styles)
2. Exporting to PDF
3. Export callbacks
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown import MarkdownViewer


class ExportDemo(QWidget):
    """Demo widget showing export functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkdownViewer - Export Functionality Demo")
        self.resize(1000, 700)

        # Create layout
        layout = QVBoxLayout(self)

        # Info label
        info = QLabel("Export the rendered markdown to HTML or PDF")
        info.setStyleSheet("font-weight: bold; padding: 10px; background: #e8f5e9;")
        layout.addWidget(info, stretch=0)

        # Create markdown viewer
        self.viewer = MarkdownViewer()
        layout.addWidget(self.viewer, stretch=1)

        # Button panel
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel, stretch=0)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar, stretch=0)
        self.status_bar.showMessage("Ready")

        # Load content when viewer is ready
        self.viewer.viewer_ready.connect(self._on_viewer_ready)

    def _create_button_panel(self) -> QWidget:
        """Create export button panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # HTML export buttons
        html_full_btn = QPushButton("Export HTML (with styles)")
        html_full_btn.clicked.connect(self._export_html_full)

        html_content_btn = QPushButton("Export HTML (content only)")
        html_content_btn.clicked.connect(self._export_html_content)

        # PDF export button
        pdf_btn = QPushButton("Export PDF")
        pdf_btn.clicked.connect(self._export_pdf)

        layout.addWidget(html_full_btn)
        layout.addWidget(html_content_btn)
        layout.addWidget(pdf_btn)

        return panel

    def _on_viewer_ready(self):
        """Load demo content."""
        content = """# Export Functionality Demo

This document demonstrates the export capabilities of MarkdownViewer.

## Export Formats

### HTML Export
The viewer can export to HTML in two modes:

1. **Full HTML** - Complete document with embedded CSS styles
2. **Content Only** - Just the rendered HTML content

### PDF Export
Export directly to PDF using Qt's printing functionality with:
- A4 page size
- Portrait orientation
- 15mm margins
- High resolution

## Features Preserved in Export

### Text Formatting
- **Bold text**
- *Italic text*
- `inline code`
- ~~Strikethrough~~

### Lists
- Unordered lists
- Ordered lists
  1. First item
  2. Second item
- Task lists
  - [x] Completed task
  - [ ] Pending task

### Code Blocks

```python
def hello_world():
    print("Hello from exported markdown!")
    return 42
```

### Math Equations

Inline math: $E=mc^2$

Block math:
$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$

### Tables

| Feature | HTML | PDF |
|---------|------|-----|
| Styles | ✓ | ✓ |
| Math | ✓ | ✓ |
| Diagrams | ✓ | ✓ |

### Diagrams

```mermaid
graph LR
    A[Markdown] --> B[Render]
    B --> C[Export HTML]
    B --> D[Export PDF]
```

### Blockquotes

> This is a blockquote that will be preserved in the export.
> It can span multiple lines.

## Try It Out!

1. Click "Export HTML (with styles)" to get a complete HTML file
2. Click "Export HTML (content only)" to get just the rendered content
3. Click "Export PDF" to generate a PDF document

The status bar will show the export progress and results.

## Code Example

```python
from vfwidgets_markdown import MarkdownViewer

viewer = MarkdownViewer()
viewer.set_markdown("# Hello World")

# Export to HTML with styles
viewer.export_html("output.html", include_styles=True)

# Export to HTML (content only)
viewer.export_html("content.html", include_styles=False)

# Export to PDF
viewer.export_pdf("output.pdf")

# With callback
def on_export(success, result):
    if success:
        print(f"Exported to: {result}")
    else:
        print(f"Export failed: {result}")

viewer.export_html("output.html", callback=on_export)
```
"""
        self.viewer.set_markdown(content)
        print("[Demo] Loaded export demo content")

    def _export_html_full(self):
        """Export HTML with styles."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML", "markdown_export.html", "HTML Files (*.html)"
        )

        if file_path:
            self.status_bar.showMessage(f"Exporting to {file_path}...")
            self.viewer.export_html(
                file_path, include_styles=True, callback=self._on_export_complete
            )

    def _export_html_content(self):
        """Export HTML content only."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML Content", "markdown_content.html", "HTML Files (*.html)"
        )

        if file_path:
            self.status_bar.showMessage(f"Exporting to {file_path}...")
            self.viewer.export_html(
                file_path, include_styles=False, callback=self._on_export_complete
            )

    def _export_pdf(self):
        """Export to PDF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "markdown_export.pdf", "PDF Files (*.pdf)"
        )

        if file_path:
            self.status_bar.showMessage(f"Exporting to {file_path}...")
            self.viewer.export_pdf(file_path, callback=self._on_export_complete)

    def _on_export_complete(self, success: bool, result: str):
        """Handle export completion."""
        if success:
            file_size = Path(result).stat().st_size
            size_kb = file_size / 1024
            message = f"✓ Exported successfully: {result} ({size_kb:.1f} KB)"
            self.status_bar.showMessage(message, 10000)
            print(f"[Demo] {message}")
        else:
            message = f"✗ Export failed: {result}"
            self.status_bar.showMessage(message, 10000)
            print(f"[Demo] {message}")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    demo = ExportDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
