"""Complete Markdown Editor Demo.

This demo showcases the full markdown editor system with:
- Source editor (MarkdownTextEditor)
- HTML preview (MarkdownViewer) with 20ms debouncing
- Table of Contents (MarkdownTocView)
- All synchronized via shared MarkdownDocument

The preview uses debouncing to avoid lag during typing - it waits 20ms
after the last keystroke before rendering.
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_markdown import (
    MarkdownDocument,
    MarkdownTextEditor,
    MarkdownTocView,
    MarkdownViewer,
)


class MarkdownEditorWindow(QMainWindow):
    """Complete markdown editor with source, preview, and TOC."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Complete Markdown Editor")
        self.resize(1400, 800)

        # Create the model (shared by all views)
        self._document = MarkdownDocument()
        self._current_file = None

        # Setup UI
        self._setup_toolbar()
        self._setup_ui()
        self._load_demo_content()

    def _setup_toolbar(self):
        """Create toolbar with file operations."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # File operations
        open_btn = QPushButton("Open...")
        open_btn.clicked.connect(self._open_file)
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_file)
        toolbar.addWidget(save_btn)

        save_as_btn = QPushButton("Save As...")
        save_as_btn.clicked.connect(self._save_file_as)
        toolbar.addWidget(save_as_btn)

        toolbar.addSeparator()

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_document)
        toolbar.addWidget(clear_btn)

        toolbar.addSeparator()

        # Status label
        self._status_label = QLabel("Ready")
        toolbar.addWidget(self._status_label)

    def _setup_ui(self):
        """Setup the main UI with editor, preview, and TOC."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter: TOC | Editor | Preview
        main_splitter = QSplitter(Qt.Horizontal)

        # 1. TOC View (left)
        self._toc_view = MarkdownTocView(self._document)
        main_splitter.addWidget(self._toc_view)

        # 2. Source Editor (center)
        self._editor = MarkdownTextEditor(self._document)
        self._editor.content_modified.connect(self._on_content_modified)
        self._editor.cursor_moved.connect(self._on_cursor_moved)
        main_splitter.addWidget(self._editor)

        # 3. HTML Preview (right)
        self._viewer = MarkdownViewer(document=self._document)
        # Add debouncing for better typing performance (20ms delay)
        self._viewer.set_debounce_delay(20)
        main_splitter.addWidget(self._viewer)

        # Set initial sizes: TOC (20%), Editor (40%), Preview (40%)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 4)
        main_splitter.setStretchFactor(2, 4)

        layout.addWidget(main_splitter)

        # Connect TOC to editor scrolling
        self._toc_view.heading_clicked.connect(self._editor.scroll_to_heading)

        # Status bar
        self.statusBar().showMessage("MVC Architecture: Model-View separation")

    def _load_demo_content(self):
        """Load demo markdown content."""
        demo_content = """# Complete Markdown Editor Demo

Welcome to the **complete markdown editor** demonstration!

## Features

This editor showcases the full MVC architecture:

### Architecture Components

1. **Model Layer**: `MarkdownDocument`
   - Pure business logic
   - No Qt dependencies
   - Python observer pattern

2. **View Layer**: Multiple synchronized views
   - `MarkdownTextEditor` - Source editing
   - `MarkdownViewer` - HTML preview
   - `MarkdownTocView` - Navigation

3. **Synchronization**: All views observe the same model
   - Changes in editor update preview and TOC
   - TOC clicks scroll editor
   - Clean separation of concerns

### Markdown Features

#### Text Formatting

- **Bold text** with `**text**`
- *Italic text* with `*text*`
- `Code spans` with backticks
- ~~Strikethrough~~ with `~~text~~`

#### Code Blocks

```python
def hello_world():
    print("Hello from markdown!")
    return 42
```

#### Lists

**Ordered:**
1. First item
2. Second item
3. Third item

**Unordered:**
- Item one
- Item two
  - Nested item
  - Another nested

#### Links and Images

[VFWidgets on GitHub](https://github.com/user/vfwidgets)

> **Note**: This is a blockquote.
> It can span multiple lines.

## Interactive Demo

Try these actions:

1. **Edit the source** (center pane) - Watch the preview and TOC update
2. **Click TOC entries** (left pane) - Editor scrolls to heading
3. **Save/Open files** - Full file I/O support
4. **Observe MVC** - Clean architecture at work

### Technical Details

**Pattern Used**: Observer pattern
- Model notifies observers via callbacks
- Views react to model changes
- No view-to-view direct coupling

**Performance**: Optimized for real-time editing
- Efficient append operations for streaming
- Optional throttling for heavy updates
- Memory-safe observer cleanup

## Next Steps

Explore the code to understand:
- How the observer pattern works
- How Qt signals enable view coordination
- How the model stays Qt-independent

Happy editing!
"""
        self._document.set_text(demo_content)
        self._update_status("Demo content loaded")

    def _on_content_modified(self):
        """Handle content modification."""
        self._update_status("Modified")

    def _on_cursor_moved(self, line: int, column: int):
        """Handle cursor movement."""
        self._update_status(f"Line {line + 1}, Col {column + 1}")

    def _update_status(self, message: str):
        """Update status label."""
        self._status_label.setText(f"  {message}")

    def _open_file(self):
        """Open a markdown file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )

        if file_path:
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                self._document.set_text(content)
                self._current_file = file_path
                self._update_status(f"Opened: {Path(file_path).name}")
            except Exception as e:
                self._update_status(f"Error opening file: {e}")

    def _save_file(self):
        """Save to current file or prompt for new file."""
        if self._current_file:
            self._save_to_file(self._current_file)
        else:
            self._save_file_as()

    def _save_file_as(self):
        """Save to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)",
        )

        if file_path:
            self._save_to_file(file_path)
            self._current_file = file_path

    def _save_to_file(self, file_path: str):
        """Save content to file."""
        try:
            Path(file_path).write_text(self._document.get_text(), encoding="utf-8")
            self._update_status(f"Saved: {Path(file_path).name}")
        except Exception as e:
            self._update_status(f"Error saving file: {e}")

    def _clear_document(self):
        """Clear the document."""
        self._document.set_text("")
        self._current_file = None
        self._update_status("Cleared")


def main():
    """Run the complete editor demo."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("Complete Markdown Editor Demo")
    print("=" * 70)
    print()
    print("This demo showcases the full markdown editor system:")
    print()
    print("Architecture:")
    print("  • Model: MarkdownDocument (shared by all views)")
    print("  • Views: Editor (source), Viewer (preview), TOC (navigation)")
    print("  • Pattern: Observer pattern for model-view synchronization")
    print()
    print("Features:")
    print("  • Real-time HTML preview")
    print("  • Interactive table of contents")
    print("  • File I/O (open/save)")
    print("  • Cursor position tracking")
    print("  • Clean MVC separation")
    print()
    print("Try:")
    print("  1. Edit source code (center) → watch preview update")
    print("  2. Click TOC entries (left) → editor scrolls")
    print("  3. Open/Save files → full persistence")
    print()
    print("=" * 70)
    print()

    window = MarkdownEditorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
