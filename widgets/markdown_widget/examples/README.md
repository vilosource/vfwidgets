# VFWidgets Markdown Widget - Examples  Being Updated Here. 

This directory contains example demonstrations showing the markdown widget's capabilities, organized from simplest to most complex.

## Running the Examples

All examples can be run directly:

```bash
python examples/01_model_foundation.py
python examples/02_multiple_views.py
# ... etc
```

Or from the repository root:

```bash
python -m examples.01_model_foundation
```

## Example Progression

### 01_model_foundation.py - Pure Model Layer
**Complexity**: ⭐ Beginner
**Concepts**: Model-only, no GUI

**What it demonstrates**:
- Pure Python `MarkdownDocument` class
- No Qt dependencies required
- Basic document operations
- Table of contents parsing
- Version tracking

**Run this first to understand**: How the model layer works independently of any UI framework.

```python
from vfwidgets_markdown import MarkdownDocument

doc = MarkdownDocument("# Hello World")
text = doc.get_text()
toc = doc.get_toc()
```

---

### 02_multiple_views.py - Observer Pattern
**Complexity**: ⭐⭐ Intermediate
**Concepts**: MVC, Observer pattern, Multiple views

**What it demonstrates**:
- Multiple synchronized views
- Observer pattern in action
- Text editor and TOC view
- Automatic view updates
- View-to-view coordination

**Run this to understand**: How multiple widgets stay synchronized through the observer pattern.

```python
doc = MarkdownDocument()
editor = MarkdownTextEditor(doc)
toc = MarkdownTocView(doc)
# All views stay synchronized automatically!
```

---

### 03_controller_features.py - Advanced Control
**Complexity**: ⭐⭐⭐ Advanced
**Concepts**: Controller layer, Performance optimization

**What it demonstrates**:
- Controller for pause/resume
- Throttled rendering
- Performance optimization
- Batch updates
- Custom rendering control

**Run this to understand**: How to optimize rendering for performance-critical scenarios.

```python
controller = MarkdownEditorController(doc, editor, viewer)
controller.pause_rendering()  # Make bulk changes
controller.resume_rendering()  # Single render
```

---

### 04_complete_editor.py - Full Editor Application
**Complexity**: ⭐⭐⭐⭐ Expert
**Concepts**: Complete application, File I/O, Full MVC

**What it demonstrates**:
- Complete markdown editor
- Source editor (left)
- HTML preview (right)
- Table of contents (side panel)
- File operations (open/save)
- Real-time synchronization
- Production-ready application

**Run this to see**: A fully-featured markdown editor in action.

```python
editor = MarkdownEditorWindow()
# Complete editor with preview, TOC, file I/O
editor.show()
```

---

### 05_ai_streaming.py - AI Response Streaming
**Complexity**: ⭐⭐⭐⭐ Expert
**Concepts**: Streaming, Performance, Real-time updates

**What it demonstrates**:
- Efficient AI response streaming
- `append_text()` for O(m) performance
- Real-time preview updates
- Performance optimization
- Simulated streaming scenarios

**Run this to understand**: How to efficiently stream AI-generated content.

```python
for chunk in ai_response_stream:
    document.append_text(chunk)  # Efficient O(m) operation
# Preview updates in real-time
```

---

## Learning Path

### For Beginners

1. Start with **01_model_foundation.py** - Understand the model
2. Move to **02_multiple_views.py** - See MVC in action
3. Try **04_complete_editor.py** - Use the complete editor

### For Advanced Users

1. Review **03_controller_features.py** - Performance optimization
2. Study **05_ai_streaming.py** - Streaming patterns
3. Explore source code for implementation details

### For Integration

Use **MarkdownEditorWidget** for the simplest integration:

```python
from vfwidgets_markdown import MarkdownEditorWidget

editor = MarkdownEditorWidget("# Hello World")
editor.show()
```

This gives you a complete editor without needing to understand MVC architecture.

---

## Key Concepts Demonstrated

### Observer Pattern (Examples 02, 03, 04, 05)

The model notifies views of changes automatically:

```
MarkdownDocument (Model)
    ↓ (notifies)
MarkdownTextEditor (View)
MarkdownViewer (View)
MarkdownTocView (View)
```

### Performance (Examples 03, 05)

Two types of operations:
- `set_text()` - O(n) - Replaces all content
- `append_text()` - O(m) - Appends efficiently (m = chunk size)

Use `append_text()` for streaming!

### MVC Architecture (All Examples)

**Model** (MarkdownDocument):
- Pure Python, no Qt
- Single source of truth
- Notifies observers

**View** (Qt Widgets):
- Displays model data
- Reacts to model changes
- Emits signals for UI coordination

**Controller** (Optional):
- Coordinates operations
- Optimizes performance
- Batches updates

---

## Troubleshooting

### "QWidget: Must construct a QApplication"

Make sure to create QApplication before widgets:

```python
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
# Now create widgets
sys.exit(app.exec())
```

### Examples don't run

Make sure the package is installed:

```bash
pip install -e .
```

Or install in development mode:

```bash
pip install -e ".[dev]"
```

---

## What's Next?

After running the examples:

1. Read `docs/API.md` for complete API reference
2. Read `docs/ARCHITECTURE.md` for architecture details
3. Explore the source code in `src/vfwidgets_markdown/`
4. Build your own applications!

---

## Questions?

- **Documentation**: See `docs/` directory
- **API Reference**: See `docs/API.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Issues**: GitHub issues

---

**Happy coding!** 🚀
