# VFWidgets Markdown Editor

A professional markdown editor widget for PySide6 with clean MVC architecture, optimized for AI streaming and live collaboration.

## Features

- **Clean MVC Architecture** - Separation of concerns with pure Python model
- **Dual Pattern Approach** - Python observer pattern + Qt signals/slots
- **Performance Optimizations** - Pause/resume rendering, throttling for smooth typing
- **Table of Contents** - Auto-generated, clickable TOC with navigation
- **AI Streaming Ready** - Efficient append operations for streaming content
- **Multiple Views** - Keep multiple editors synchronized via shared model
- **Simple API** - Easy to use composite widget hides complexity

## Quick Start

### Installation

```bash
pip install vfwidgets-markdown
```

### Basic Usage

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownEditorWidget

app = QApplication([])

# Create editor - that's it!
editor = MarkdownEditorWidget()
editor.set_text("# Hello World\n\nStart editing...")
editor.show()

app.exec()
```

### AI Streaming Example

```python
from vfwidgets_markdown import MarkdownEditorWidget

editor = MarkdownEditorWidget()
editor.show()

# Efficient streaming - uses append events, not full replacement
for chunk in ai_response_stream():
    editor.append_text(chunk)  # ✅ Efficient!
    # NOT: editor.set_text(editor.get_text() + chunk)  # ❌ Slow!
```

### Advanced: Direct Model Access

```python
from vfwidgets_markdown import MarkdownEditorWidget

editor = MarkdownEditorWidget()

# Get the document model for advanced usage
document = editor.get_document()

# Add custom observer
class MyObserver:
    def on_document_changed(self, event):
        print(f"Document changed! Version: {event.version}")

document.add_observer(MyObserver())
```

### MarkdownViewer - Display Only Widget

For read-only markdown display (without editing), use `MarkdownViewer`:

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownViewer

app = QApplication([])

# Simple usage - content in constructor
viewer = MarkdownViewer(initial_content="# Hello World\\n\\nThis is **markdown**!")
viewer.show()

# Or load from file
viewer = MarkdownViewer()
viewer.load_file("README.md")  # Automatic base path handling
viewer.show()

app.exec()
```

**Important: Async Initialization**

MarkdownViewer uses QWebEngineView which initializes asynchronously.
**You don't need to worry about this** - the widget automatically queues
content until ready.

```python
# ✅ This works - content is queued automatically
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")  # Safe to call immediately!

# ✅ This also works - content passed to constructor
viewer = MarkdownViewer(initial_content="# Hello")

# ✅ This works too - explicit signal handling (advanced)
viewer = MarkdownViewer()
viewer.viewer_ready.connect(lambda: viewer.set_markdown("# Hello"))
```

**When to use viewer_ready signal?**

Most applications don't need to handle `viewer_ready` explicitly. However,
you should connect to it if:
- You need to perform actions exactly when rendering completes
- You're doing complex initialization sequences
- You want to show a loading indicator

See `examples/00_quick_start.py` for the simplest usage.

## Architecture

This widget implements a clean **MVC (Model-View-Controller)** architecture:

```
┌─────────────────────────────────────────┐
│       MarkdownDocument (Model)          │
│       Pure Python, No Qt                │
└────────────┬────────────────────────────┘
             │ Python Observer Pattern
    ┌────────┴─────────┬──────────────────┐
    ↓                  ↓                   ↓
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│  Editor  │   │   TOC View   │   │   Viewer     │
│  (View)  │   │    (View)    │   │   (View)     │
└──────────┘   └──────────────┘   └──────────────┘
    ↕                  ↕
 Qt Signals      Qt Signals
(View ↔ View coordination)
```

### Key Architectural Decisions

1. **Python Observer Pattern** (Model → Views)
   - Model stays pure Python (testable without Qt)
   - Views react to model changes
   - Clean separation of concerns

2. **Qt Signals/Slots** (View ↔ View)
   - Native Qt for UI coordination
   - Type-safe, automatic cleanup
   - TOC clicks → Editor scrolls

3. **Performance Controller**
   - Pause/resume for batch operations
   - Throttling for smooth typing
   - Optimized for large documents

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## API Reference

### MarkdownEditorWidget

The main composite widget that combines everything.

**Constructor:**
```python
MarkdownEditorWidget(initial_text="", parent=None)
```

**Methods:**
- `set_text(text: str)` - Set complete markdown content
- `append_text(text: str)` - Append text (optimized for streaming)
- `get_text() -> str` - Get current content
- `clear()` - Clear all content
- `set_read_only(read_only: bool)` - Make editor read-only
- `is_read_only() -> bool` - Check if read-only

**Advanced Access:**
- `get_document() -> MarkdownDocument` - Direct model access
- `get_editor() -> MarkdownTextEditor` - Direct editor access
- `get_toc_view() -> MarkdownTocView` - Direct TOC access

**Signals:**
- `content_changed` - Emitted when content changes
- `cursor_moved(int, int)` - Emitted on cursor move (line, column)

## Examples

See the `examples/` directory for comprehensive demos:

- `demo_multiple_views.py` - Multiple editors sharing one model
- `demo_controller_features.py` - Performance optimizations
- `demo_complete_editor.py` - Full editor with all features

## Development

### Setup

```bash
# Clone the repo
git clone https://github.com/vfwidgets/vfwidgets.git
cd vfwidgets/widgets/markdown_widget

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=vfwidgets_markdown --cov-report=html

# Specific test file
pytest tests/models/test_document.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/

# Type check
mypy src/
```

## Design Philosophy

This widget follows these principles:

1. **Evidence-Based Development** - All features tested with real output
2. **Clean Architecture** - Clear separation between Model/View/Controller
3. **Performance First** - Optimized for AI streaming and large documents
4. **Simple API** - Hide complexity, expose power when needed
5. **Pure Python Model** - Testable without Qt framework

## Use Cases

### Perfect For:

- ✅ AI chat interfaces (streaming markdown responses)
- ✅ Note-taking applications
- ✅ Documentation editors
- ✅ Live markdown preview tools
- ✅ Collaborative editing (multiple views, one model)

### Not Designed For:

- ❌ WYSIWYG editing (use HTML editor instead)
- ❌ Syntax highlighting for code (add separately)
- ❌ Spell checking (add separately)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Read `docs/ARCHITECTURE.md` to understand the design
2. Add tests for new features
3. Follow the existing code style
4. Update documentation

## Changelog

### Version 2.0.0 (Current)

- Complete rewrite with MVC architecture
- Dual pattern approach (Python observer + Qt signals)
- Performance controller with pause/resume and throttling
- Composite widget for simple API
- Comprehensive test suite
- Full documentation

### Version 1.0.0 (Archived)

- Basic markdown editor
- WebEngine-based viewer
- Simple observer pattern
- (Archived to `markdown_widget_OLD_2025-01-11`)

## Documentation

- **[Architecture Documentation](docs/ARCHITECTURE.md)** - Complete MVC architecture, design patterns, and implementation details
- **[API Documentation](docs/API.md)** - Full API reference for all public classes and methods
- **[Theme Integration Guide](docs/theme-integration-GUIDE.md)** - How MarkdownViewer integrates with VFWidgets theme system

## Links

- [GitHub Repository](https://github.com/vfwidgets/vfwidgets)
- [Issue Tracker](https://github.com/vfwidgets/vfwidgets/issues)
