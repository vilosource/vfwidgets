# VFWidgets Markdown Widget - API Reference

**Version**: 2.0.0
**Architecture**: MVC (Model-View-Controller)

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Model Layer](#model-layer)
- [View Layer](#view-layer)
- [Controller Layer](#controller-layer)
- [Events](#events)
- [Advanced Usage](#advanced-usage)
- [Migration Guide](#migration-guide)

---

## Quick Start

### Simple Usage (Recommended for Most Cases)

```python
from vfwidgets_markdown import MarkdownEditorWidget

# Create a complete markdown editor
editor = MarkdownEditorWidget("# Hello World\n\nWelcome!")
editor.show()

# Set content
editor.set_text("# New Content")

# Get content
content = editor.get_text()

# Append efficiently (for AI streaming)
editor.append_text("\n## New Section")
```

### HTML Preview Only

```python
from vfwidgets_markdown import MarkdownViewer

# Simple mode - creates internal document
viewer = MarkdownViewer()
viewer.set_markdown("# Hello\n\nWorld")
viewer.show()
```

### Advanced MVC Usage

```python
from vfwidgets_markdown import (
    MarkdownDocument,
    MarkdownTextEditor,
    MarkdownViewer,
    MarkdownTocView,
)

# Create shared document (model)
document = MarkdownDocument("# Title\n\n## Section")

# Create multiple synchronized views
editor = MarkdownTextEditor(document)
viewer = MarkdownViewer(document=document)
toc = MarkdownTocView(document)

# All views automatically update when document changes
document.set_text("# Updated")
```

---

## Architecture Overview

The markdown widget follows **MVC (Model-View-Controller)** architecture with the **Observer Pattern**:

```
┌─────────────────────────────────────────────┐
│  Model (MarkdownDocument)                   │
│  - Pure Python, no Qt dependencies          │
│  - Single source of truth                   │
│  - Notifies observers via callbacks         │
└────────────┬────────────────────────────────┘
             │ Observer Pattern
             ↓
┌─────────────────────────────────────────────┐
│  Views (Qt Widgets)                         │
│  - MarkdownTextEditor (source editing)      │
│  - MarkdownViewer (HTML preview)            │
│  - MarkdownTocView (navigation)             │
│  - MarkdownEditorWidget (composite)         │
└─────────────────────────────────────────────┘
```

**Key Benefits**:
- **Separation**: Model can be tested without Qt
- **Synchronization**: Multiple views stay in sync automatically
- **Performance**: Efficient updates via observer pattern
- **Flexibility**: Mix and match components as needed

---

## Model Layer

### MarkdownDocument

**The core model class - single source of truth for document content.**

Pure Python with NO Qt dependencies. Can be used without QApplication.

#### Constructor

```python
MarkdownDocument(content: str = "")
```

**Parameters**:
- `content` (str, optional): Initial document content. Default: `""`

**Example**:
```python
from vfwidgets_markdown import MarkdownDocument

# Empty document
doc = MarkdownDocument()

# With initial content
doc = MarkdownDocument("# Hello World")
```

#### Core Methods

##### `get_text() -> str`

Get the current document text.

**Returns**: Complete document text as string

**Example**:
```python
content = doc.get_text()
print(content)  # "# Hello World"
```

---

##### `set_text(text: str) -> None`

Replace the entire document text.

**Parameters**:
- `text` (str): The new document text

**Performance**: O(n) operation. Use `append_text()` for better performance when adding to the end.

**Triggers**: Notifies all observers with `TextReplaceEvent`

**Example**:
```python
doc.set_text("# New Content\n\nCompletely replaced")
```

---

##### `append_text(text: str) -> None`

Append text to the end of the document.

**Parameters**:
- `text` (str): The text to append

**Performance**: O(m) where m = len(text). Much better than `set_text()` for incremental updates.

**Use Case**: AI streaming, incremental content generation

**Triggers**: Notifies all observers with `TextAppendEvent`

**Example**:
```python
# Efficient for AI streaming
for chunk in ai_response_stream:
    doc.append_text(chunk)
```

---

##### `get_toc() -> list[dict]`

Get the table of contents.

**Returns**: List of TOC entries, each dict containing:
- `level` (int): Heading level (1-6)
- `text` (str): Heading text
- `id` (str): GitHub-style ID for linking

**Performance**: Cached automatically, only re-parsed when document changes

**Example**:
```python
toc = doc.get_toc()
for entry in toc:
    print(f"{'  ' * (entry['level'] - 1)}{entry['text']}")
# Output:
# Title
#   Section 1
#   Section 2
```

---

##### `get_version() -> int`

Get the current document version number.

**Returns**: Integer version number (increments with each change)

**Use Case**: Detect if views are out of sync, optimize updates

**Example**:
```python
v1 = doc.get_version()  # 0
doc.set_text("changed")
v2 = doc.get_version()  # 1
```

---

#### Observer Pattern

##### `add_observer(observer: DocumentObserver) -> None`

Register an observer to receive document change notifications.

**Parameters**:
- `observer`: Object implementing `on_document_changed(event)` method

**Example**:
```python
class MyObserver:
    def on_document_changed(self, event):
        print(f"Document changed: {event}")

observer = MyObserver()
doc.add_observer(observer)
```

---

##### `remove_observer(observer: DocumentObserver) -> None`

Unregister an observer.

**Parameters**:
- `observer`: Previously registered observer

**Important**: Always remove observers when widgets close to prevent memory leaks

**Example**:
```python
def closeEvent(self, event):
    doc.remove_observer(self)
    super().closeEvent(event)
```

---

## View Layer

### MarkdownEditorWidget

**Complete markdown editor with text editing and table of contents (TOC).**

This is the **recommended** widget for most use cases. It internally creates and manages all MVC components.

#### Constructor

```python
MarkdownEditorWidget(initial_text: str = "", parent: QWidget = None)
```

**Parameters**:
- `initial_text` (str, optional): Initial markdown content
- `parent` (QWidget, optional): Parent widget

**Example**:
```python
from vfwidgets_markdown import MarkdownEditorWidget

editor = MarkdownEditorWidget("# Welcome\n\nStart typing...")
editor.show()
```

#### Signals

##### `content_changed`

Emitted when document content changes via user editing.

**Type**: `Signal()`

**Example**:
```python
editor.content_changed.connect(lambda: print("Content changed!"))
```

---

##### `cursor_moved`

Emitted when cursor position changes.

**Type**: `Signal(int, int)` - (line, column)

**Example**:
```python
def on_cursor_moved(line, col):
    print(f"Cursor at line {line + 1}, column {col + 1}")

editor.cursor_moved.connect(on_cursor_moved)
```

#### Methods

##### `set_text(text: str) -> None`

Set the complete markdown text.

**Parameters**:
- `text` (str): The markdown content to display

**Example**:
```python
editor.set_text("# New Document\n\nFresh start")
```

---

##### `get_text() -> str`

Get the current markdown text.

**Returns**: Complete markdown content

**Example**:
```python
content = editor.get_text()
with open("document.md", "w") as f:
    f.write(content)
```

---

##### `append_text(text: str) -> None`

Append text to the end of the document.

**Parameters**:
- `text` (str): Text to append

**Use Case**: AI streaming, incremental updates

**Example**:
```python
editor.append_text("\n## New Section\n")
```

---

##### `clear() -> None`

Clear all document content.

**Example**:
```python
editor.clear()
```

---

##### `set_read_only(read_only: bool) -> None`

Set read-only mode.

**Parameters**:
- `read_only` (bool): True for read-only, False for editable

**Example**:
```python
editor.set_read_only(True)  # Prevent editing
```

---

##### `is_read_only() -> bool`

Check if editor is in read-only mode.

**Returns**: True if read-only, False if editable

**Example**:
```python
if editor.is_read_only():
    print("Editor is locked")
```

---

##### `get_document() -> MarkdownDocument`

Get the underlying document model (for advanced usage).

**Returns**: The `MarkdownDocument` instance

**Use Case**: Direct document manipulation, adding custom observers

**Example**:
```python
doc = editor.get_document()
doc.add_observer(my_custom_observer)
```

---

##### `get_editor() -> MarkdownTextEditor`

Get the text editor widget (for advanced customization).

**Returns**: The `MarkdownTextEditor` instance

**Example**:
```python
text_editor = editor.get_editor()
text_editor.setFont(QFont("Consolas", 12))
```

---

##### `get_toc_view() -> MarkdownTocView`

Get the table of contents widget.

**Returns**: The `MarkdownTocView` instance

**Example**:
```python
toc = editor.get_toc_view()
toc.setMaximumWidth(200)
```

---

### MarkdownViewer

**HTML preview widget with markdown rendering.**

Supports both simple standalone mode and advanced MVC mode.

#### Auto-Wrapping Pattern

The `MarkdownViewer` uses an **auto-wrapping pattern** for maximum flexibility:

**Simple Mode** (creates internal document):
```python
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")
```

**Advanced Mode** (uses external document for MVC):
```python
document = MarkdownDocument()
viewer = MarkdownViewer(document=document)
```

#### Constructor

```python
MarkdownViewer(document: MarkdownDocument = None, parent: QWidget = None)
```

**Parameters**:
- `document` (MarkdownDocument, optional): External document to observe. If None, creates internal document.
- `parent` (QWidget, optional): Parent widget

**Example**:
```python
# Simple standalone usage
viewer = MarkdownViewer()
viewer.set_markdown("# Preview")
viewer.show()

# MVC usage with shared document
doc = MarkdownDocument()
viewer = MarkdownViewer(document=doc)
editor = MarkdownTextEditor(doc)
```

#### Methods

##### `set_markdown(content: str) -> None`

Set markdown content to render.

**Parameters**:
- `content` (str): Markdown text to render as HTML

**Works in both modes**:
- Simple mode: Updates internal document
- Advanced mode: Updates external document

**Example**:
```python
viewer.set_markdown("# Title\n\n**Bold** and *italic*")
```

---

##### `load_file(path: str) -> None`

Load markdown from a file.

**Parameters**:
- `path` (str): Path to markdown file

**Example**:
```python
viewer.load_file("/path/to/document.md")
```

---

##### `get_toc() -> list[dict]`

Get the table of contents from rendered content.

**Returns**: List of TOC entries

**Example**:
```python
toc = viewer.get_toc()
for entry in toc:
    print(f"{entry['level']}: {entry['text']}")
```

---

##### `scroll_to_heading(heading_id: str) -> None`

Scroll preview to a specific heading.

**Parameters**:
- `heading_id` (str): GitHub-style heading ID

**Example**:
```python
# From TOC click
toc_view.heading_clicked.connect(viewer.scroll_to_heading)
```

---

##### `set_theme(theme: str) -> None`

Set the preview theme.

**Parameters**:
- `theme` (str): Theme name ("light", "dark", or custom)

**Example**:
```python
viewer.set_theme("dark")
```

---

##### `set_syntax_theme(theme: str) -> None`

Set the code syntax highlighting theme.

**Parameters**:
- `theme` (str): Syntax theme name

**Available themes**: Based on highlight.js themes

**Example**:
```python
viewer.set_syntax_theme("github-dark")
```

---

##### `set_base_path(path: str) -> None`

Set base path for resolving relative links and images.

**Parameters**:
- `path` (str): Base directory path

**Example**:
```python
viewer.set_base_path("/home/user/documents")
viewer.set_markdown("![image](./images/photo.png)")  # Resolves relative to base
```

---

##### `set_image_resolver(resolver: callable) -> None`

Set custom image path resolver.

**Parameters**:
- `resolver` (callable): Function that takes `src: str` and returns resolved path

**Use Case**: Custom image loading, cloud storage, data URIs

**Example**:
```python
def my_resolver(src: str) -> str:
    if src.startswith("http"):
        return src
    return f"/cdn/images/{src}"

viewer.set_image_resolver(my_resolver)
```

---

##### `enable_sync_mode(enabled: bool = True) -> None`

Enable/disable sync mode for instant updates.

**Parameters**:
- `enabled` (bool): True for sync mode, False for async

**Use Case**: Disable sync for better performance during rapid updates

**Example**:
```python
# Disable sync during bulk updates
viewer.enable_sync_mode(False)
for chunk in large_chunks:
    doc.append_text(chunk)
viewer.enable_sync_mode(True)
```

---

##### `set_debounce_delay(delay_ms: int) -> None`

Set debounce delay for rendering updates.

**Parameters**:
- `delay_ms` (int): Delay in milliseconds (0 to disable)

**Use Case**: Reduce rendering frequency during fast typing

**Example**:
```python
viewer.set_debounce_delay(300)  # Wait 300ms before rendering
```

---

##### `enable_shortcuts(enabled: bool = True) -> None`

Enable/disable keyboard shortcuts in preview.

**Parameters**:
- `enabled` (bool): True to enable shortcuts

**Default shortcuts**: Copy, search, zoom

**Example**:
```python
viewer.enable_shortcuts(True)
```

---

##### `export_html(include_styles: bool = True) -> str`

Export rendered HTML.

**Parameters**:
- `include_styles` (bool): Include CSS styles in output

**Returns**: Complete HTML string

**Example**:
```python
html = viewer.export_html(include_styles=True)
with open("output.html", "w") as f:
    f.write(html)
```

---

##### `is_ready() -> bool`

Check if viewer is ready (web engine loaded).

**Returns**: True if ready to render

**Example**:
```python
if viewer.is_ready():
    viewer.set_markdown("# Ready!")
```

---

### MarkdownTextEditor

**Plain text editor for markdown source code.**

Observes `MarkdownDocument` and stays synchronized.

#### Constructor

```python
MarkdownTextEditor(document: MarkdownDocument, parent: QWidget = None)
```

**Parameters**:
- `document` (MarkdownDocument): Document model to observe (**required**)
- `parent` (QWidget, optional): Parent widget

**Example**:
```python
from vfwidgets_markdown import MarkdownDocument, MarkdownTextEditor

doc = MarkdownDocument("# Hello")
editor = MarkdownTextEditor(doc)
editor.show()
```

#### Signals

##### `content_modified`

Emitted when user modifies content.

**Type**: `Signal()`

**Example**:
```python
editor.content_modified.connect(lambda: print("User edited content"))
```

---

##### `cursor_moved`

Emitted when cursor position changes.

**Type**: `Signal(int, int)` - (line, column)

**Example**:
```python
editor.cursor_moved.connect(lambda line, col: print(f"Line {line}, Col {col}"))
```

#### Methods

##### `scroll_to_heading(heading_id: str) -> None`

Scroll editor to show a specific heading.

**Parameters**:
- `heading_id` (str): GitHub-style heading ID

**Use Case**: Connect to TOC clicks for navigation

**Example**:
```python
toc_view.heading_clicked.connect(editor.scroll_to_heading)
```

---

### MarkdownTocView

**Table of contents navigation widget.**

Displays document headings in a tree structure.

#### Constructor

```python
MarkdownTocView(document: MarkdownDocument, parent: QWidget = None)
```

**Parameters**:
- `document` (MarkdownDocument): Document model to observe (**required**)
- `parent` (QWidget, optional): Parent widget

**Example**:
```python
from vfwidgets_markdown import MarkdownDocument, MarkdownTocView

doc = MarkdownDocument("# Title\n## Section")
toc = MarkdownTocView(doc)
toc.show()
```

#### Signals

##### `heading_clicked`

Emitted when user clicks a TOC entry.

**Type**: `Signal(str)` - heading ID

**Use Case**: Scroll editor/viewer to clicked heading

**Example**:
```python
toc.heading_clicked.connect(editor.scroll_to_heading)
toc.heading_clicked.connect(viewer.scroll_to_heading)
```

---

## Controller Layer

### MarkdownEditorController

**Optional controller for advanced rendering control.**

Provides pause/resume and throttling capabilities.

#### Constructor

```python
MarkdownEditorController(
    document: MarkdownDocument,
    editor: MarkdownTextEditor,
    viewer: MarkdownViewer
)
```

**Parameters**:
- `document` (MarkdownDocument): The document model
- `editor` (MarkdownTextEditor): The text editor
- `viewer` (MarkdownViewer): The HTML viewer

**Example**:
```python
from vfwidgets_markdown.controllers import MarkdownEditorController

controller = MarkdownEditorController(document, editor, viewer)
```

#### Methods

##### `pause_rendering() -> None`

Pause viewer updates temporarily.

**Use Case**: Bulk document updates without intermediate renders

**Example**:
```python
controller.pause_rendering()
# Make multiple changes
doc.set_text("Line 1\n")
doc.append_text("Line 2\n")
doc.append_text("Line 3\n")
controller.resume_rendering()  # Renders once with final content
```

---

##### `resume_rendering() -> None`

Resume viewer updates and render pending changes.

**Example**:
```python
controller.resume_rendering()
```

---

##### `set_throttle_mode(enabled: bool, interval_ms: int = 100) -> None`

Enable/disable throttled rendering.

**Parameters**:
- `enabled` (bool): True to enable throttling
- `interval_ms` (int): Minimum interval between renders in milliseconds

**Use Case**: Performance optimization during rapid updates

**Example**:
```python
# Render at most once per 200ms
controller.set_throttle_mode(True, 200)
```

---

## Events

### TextReplaceEvent

Emitted when entire document text is replaced via `set_text()`.

**Attributes**:
- `version` (int): New document version
- `text` (str): New complete text

---

### TextAppendEvent

Emitted when text is appended via `append_text()`.

**Attributes**:
- `version` (int): New document version
- `text` (str): Appended text
- `start_position` (int): Position where text was appended

---

### SectionUpdateEvent

Emitted when a specific section is updated.

**Attributes**:
- `version` (int): New document version
- `section_id` (str): ID of updated section
- `new_content` (str): New section content

---

## Advanced Usage

### Custom Observers

Implement the `DocumentObserver` protocol:

```python
from vfwidgets_markdown import MarkdownDocument, DocumentObserver

class MyObserver(DocumentObserver):
    def on_document_changed(self, event):
        print(f"Document version: {event.version}")
        if hasattr(event, 'text'):
            print(f"New content: {event.text[:50]}...")

doc = MarkdownDocument()
observer = MyObserver()
doc.add_observer(observer)

doc.set_text("This triggers the observer!")
```

---

### AI Streaming Pattern

Efficient pattern for streaming AI responses:

```python
from vfwidgets_markdown import MarkdownEditorWidget
import time

editor = MarkdownEditorWidget()
editor.show()

# Simulate AI streaming
chunks = ["# AI", " Response", "\n\n", "This is", " streaming", "..."]

for chunk in chunks:
    editor.append_text(chunk)  # O(m) operation - efficient!
    time.sleep(0.1)  # Simulated delay
```

---

### Multi-View Synchronization

Multiple views of same document:

```python
from vfwidgets_markdown import (
    MarkdownDocument,
    MarkdownTextEditor,
    MarkdownViewer,
)

# Shared document
doc = MarkdownDocument("# Shared Content")

# Multiple editors (split view)
editor1 = MarkdownTextEditor(doc)
editor2 = MarkdownTextEditor(doc)

# Preview
viewer = MarkdownViewer(document=doc)

# All stay synchronized automatically!
doc.set_text("# Updated")  # All widgets update
```

---

### Theme Integration

The widget automatically integrates with `vfwidgets-theme` if available:

```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_markdown import MarkdownEditorWidget

app = ThemedApplication(sys.argv)
app.set_theme("dark")

editor = MarkdownEditorWidget()
editor.show()  # Automatically themed!
```

---

### Performance Optimization

For large documents or rapid updates:

```python
from vfwidgets_markdown import MarkdownViewer
from vfwidgets_markdown.controllers import MarkdownEditorController

# 1. Use debouncing
viewer.set_debounce_delay(300)  # Wait 300ms before rendering

# 2. Use controller pause/resume
controller.pause_rendering()
for i in range(1000):
    doc.append_text(f"Line {i}\n")
controller.resume_rendering()  # Single render

# 3. Use throttling
controller.set_throttle_mode(True, 200)  # Max 5 renders/second
```

---

## DX Improvement Recommendations

### 1. ✅ Good: Auto-Wrapping Pattern in MarkdownViewer

The viewer intelligently handles both simple and advanced modes:

```python
# Simple - great DX!
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")

# Advanced - MVC compliant!
viewer = MarkdownViewer(document=doc)
```

### 2. ✅ Good: Composite Widget Pattern

`MarkdownEditorWidget` hides complexity:

```python
# One line gets you a full editor!
editor = MarkdownEditorWidget("# Hello")
```

### 3. ⚠️ Consider: MarkdownTextEditor Requires Document

**Current**:
```python
# Must create document first
doc = MarkdownDocument()
editor = MarkdownTextEditor(doc)
```

**Suggested Improvement**:
```python
# Optional document parameter (like MarkdownViewer)
editor = MarkdownTextEditor()  # Creates internal document
editor.set_text("# Hello")

# Advanced mode still works
editor = MarkdownTextEditor(document=doc)
```

### 4. ⚠️ Consider: MarkdownTocView Requires Document

Same as MarkdownTextEditor - could auto-create document.

### 5. ✅ Good: Clear Method Names

Methods are self-documenting:
- `set_text()` - replace all
- `append_text()` - add to end
- `get_text()` - retrieve content

### 6. ✅ Good: Signals Follow Qt Conventions

Signals use standard Qt patterns:
- `content_changed` - past tense
- `cursor_moved` - past tense
- `heading_clicked` - past tense

### 7. ⚠️ Consider: Export Methods

**Suggested Addition**:
```python
# Export to various formats
editor.export_to_html("output.html")
editor.export_to_pdf("output.pdf")
editor.export_to_markdown("output.md")  # With formatting

# Or as strings
html_content = editor.to_html()
pdf_bytes = editor.to_pdf()
```

### 8. ✅ Good: Performance Methods Are Discoverable

Methods like `append_text()` have clear performance docs.

---

## Migration Guide

### From v1.x to v2.0

**Breaking Changes**:

1. **Architecture**: Now uses MVC pattern

   **Before (v1.x)**:
   ```python
   editor = OldMarkdownEditor()
   editor.setText("# Hello")
   ```

   **After (v2.0)**:
   ```python
   editor = MarkdownEditorWidget()
   editor.set_text("# Hello")
   ```

2. **Method Names**: Changed for consistency

   - `setText()` → `set_text()`
   - `getText()` → `get_text()`
   - `appendText()` → `append_text()`

3. **Viewer Integration**: New auto-wrapping pattern

   **Before (v1.x)**:
   ```python
   viewer = MarkdownViewer()
   viewer.setMarkdown("# Hello")
   ```

   **After (v2.0)**:
   ```python
   viewer = MarkdownViewer()
   viewer.set_markdown("# Hello")
   ```

**Benefits of v2.0**:
- Clean MVC architecture
- Better testability
- Multiple synchronized views
- Performance improvements
- More flexible API

---

## Examples

### Complete Working Examples

See the `examples/` directory for full working demonstrations:

1. **demo_model_foundation.py** - Model layer basics
2. **demo_multiple_views.py** - Multi-view synchronization
3. **demo_controller_features.py** - Advanced controller usage
4. **demo_complete_editor.py** - Full editor with preview
5. **demo_ai_streaming.py** - AI streaming simulation

---

## Best Practices

### 1. Use MarkdownEditorWidget for Simple Cases

```python
# ✅ Good - simple and effective
editor = MarkdownEditorWidget("# Content")

# ❌ Avoid - unnecessary complexity
doc = MarkdownDocument("# Content")
editor = MarkdownTextEditor(doc)
toc = MarkdownTocView(doc)
# ... manual wiring
```

### 2. Use Shared Document for Custom Layouts

```python
# ✅ Good - when you need custom layout
doc = MarkdownDocument()
editor = MarkdownTextEditor(doc)
viewer = MarkdownViewer(document=doc)
# Arrange in your custom layout
```

### 3. Always Remove Observers on Close

```python
# ✅ Good - prevents memory leaks
def closeEvent(self, event):
    self._document.remove_observer(self)
    super().closeEvent(event)
```

### 4. Use append_text() for Streaming

```python
# ✅ Good - O(m) performance
for chunk in stream:
    doc.append_text(chunk)

# ❌ Avoid - O(n) performance
for chunk in stream:
    doc.set_text(doc.get_text() + chunk)
```

### 5. Use Controller for Bulk Updates

```python
# ✅ Good - single render
controller.pause_rendering()
for line in lines:
    doc.append_text(line)
controller.resume_rendering()

# ❌ Avoid - renders n times
for line in lines:
    doc.append_text(line)  # Renders each time!
```

---

## FAQ

**Q: Do I need to understand MVC to use this widget?**

A: No! Use `MarkdownEditorWidget` for simple cases. MVC is for advanced usage.

**Q: Can I use the model without Qt?**

A: Yes! `MarkdownDocument` is pure Python and works without QApplication.

**Q: How do I integrate with vfwidgets-theme?**

A: It's automatic! If `vfwidgets-theme` is installed, widgets are automatically themed.

**Q: What's the difference between set_text() and append_text()?**

A: `set_text()` replaces all content (O(n)). `append_text()` adds to end (O(m)). Use `append_text()` for streaming.

**Q: Can I have multiple views of the same document?**

A: Yes! Create a shared `MarkdownDocument` and pass it to multiple views.

**Q: Is the widget thread-safe?**

A: No. All operations must be on the Qt main thread, per Qt conventions.

---

## Support

**Documentation**: https://github.com/yourusername/vfwidgets/widgets/markdown_widget
**Issues**: https://github.com/yourusername/vfwidgets/issues
**Examples**: See `examples/` directory

---

**Last Updated**: 2025-10-11
**Version**: 2.0.0
