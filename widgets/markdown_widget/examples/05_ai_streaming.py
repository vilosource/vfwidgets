"""AI Streaming Simulation Demo.

This demo simulates an AI assistant streaming markdown responses in real-time.
It demonstrates:
- Efficient append operations for streaming text
- Real-time preview updates
- Performance optimization for rapid updates
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_markdown import (
    MarkdownDocument,
    MarkdownTextEditor,
    MarkdownViewer,
)


class AIStreamingDemo(QMainWindow):
    """Simulates AI streaming markdown responses."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Streaming Simulation")
        self.resize(1200, 700)

        # Create shared document
        self._document = MarkdownDocument()

        # Streaming state
        self._stream_index = 0
        self._stream_chunks = []
        self._stream_timer = QTimer()
        self._stream_timer.timeout.connect(self._stream_next_chunk)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # Control bar
        control_layout = QHBoxLayout()

        self._status_label = QLabel("Ready to stream")
        control_layout.addWidget(self._status_label)

        control_layout.addStretch()

        # Stream buttons
        stream1_btn = QPushButton("Stream: Code Tutorial")
        stream1_btn.clicked.connect(lambda: self._start_stream(self._get_code_tutorial()))
        control_layout.addWidget(stream1_btn)

        stream2_btn = QPushButton("Stream: Documentation")
        stream2_btn.clicked.connect(lambda: self._start_stream(self._get_documentation()))
        control_layout.addWidget(stream2_btn)

        stream3_btn = QPushButton("Stream: Analysis")
        stream3_btn.clicked.connect(lambda: self._start_stream(self._get_analysis()))
        control_layout.addWidget(stream3_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        control_layout.addWidget(clear_btn)

        layout.addLayout(control_layout)

        # Split view: Editor | Preview
        splitter = QSplitter(Qt.Horizontal)

        # Editor (left)
        self._editor = MarkdownTextEditor(self._document)
        self._editor.setReadOnly(True)  # Read-only for demo
        splitter.addWidget(self._editor)

        # Preview (right)
        self._viewer = MarkdownViewer(document=self._document)
        splitter.addWidget(self._viewer)

        # Equal sizes
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # Info bar
        info_label = QLabel(
            "💡 This demo simulates AI streaming responses with efficient append operations. "
            "Watch how the preview updates in real-time as chunks arrive."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { padding: 8px; background: #f0f0f0; }")
        layout.addWidget(info_label)

    def _get_code_tutorial(self) -> list:
        """Get code tutorial chunks."""
        content = """# Python Functions Tutorial

Let me explain Python functions step by step.

## Basic Function Definition

Here's how to define a simple function:

```python
def greet(name):
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # Output: Hello, Alice!
```

## Function Arguments

Functions can have different types of arguments:

### Positional Arguments

```python
def add(a, b):
    return a + b

result = add(5, 3)  # result = 8
```

### Default Arguments

```python
def power(base, exponent=2):
    return base ** exponent

print(power(5))      # 25 (uses default exponent=2)
print(power(5, 3))   # 125 (uses exponent=3)
```

### Keyword Arguments

```python
def describe_pet(animal, name):
    print(f"I have a {animal} named {name}")

describe_pet(animal="dog", name="Buddy")
describe_pet(name="Whiskers", animal="cat")
```

## Return Values

Functions can return multiple values:

```python
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers)

minimum, maximum, total = get_stats([1, 2, 3, 4, 5])
```

## Lambda Functions

For simple operations, use lambda functions:

```python
square = lambda x: x ** 2
print(square(5))  # 25

numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
# Result: [1, 4, 9, 16, 25]
```

## Best Practices

1. **Use descriptive names**: `calculate_total()` not `ct()`
2. **Keep functions focused**: One function, one task
3. **Document your functions**: Use docstrings
4. **Avoid side effects**: Return values instead of modifying globals

Happy coding! 🚀
"""
        # Split into chunks for streaming (word-by-word for realistic effect)
        words = content.split(" ")
        chunks = []
        current_chunk = ""

        for i, word in enumerate(words):
            current_chunk += word + " "
            # Create chunk every 3-5 words
            if i % 4 == 0 or i == len(words) - 1:
                chunks.append(current_chunk)
                current_chunk = ""

        return chunks

    def _get_documentation(self) -> list:
        """Get documentation chunks."""
        content = """# MarkdownWidget Documentation

## Overview

The MarkdownWidget is a professional markdown editor with MVC architecture.

## Architecture

### Model Layer

The **MarkdownDocument** class represents the markdown content:

```python
from vfwidgets_markdown import MarkdownDocument

# Create document
document = MarkdownDocument("# Hello World")

# Get content
text = document.get_text()

# Update content
document.set_text("# Updated Content")

# Efficient append for streaming
document.append_text("\\n\\nMore content here")
```

### View Layer

Multiple views can observe the same document:

1. **MarkdownTextEditor** - Source editing
2. **MarkdownViewer** - HTML preview
3. **MarkdownTocView** - Table of contents

### Observer Pattern

Views automatically update when the document changes:

```python
# Create shared document
doc = MarkdownDocument()

# Create multiple views
editor = MarkdownTextEditor(doc)
viewer = MarkdownViewer(document=doc)
toc = MarkdownTocView(doc)

# Update document - all views update automatically!
doc.set_text("# New Content")
```

## API Reference

### MarkdownDocument

**Methods:**
- `get_text() -> str` - Get current content
- `set_text(text: str)` - Replace all content
- `append_text(text: str)` - Append content (efficient)
- `get_toc() -> List[TocEntry]` - Get table of contents

**Observer Pattern:**
- `add_observer(observer)` - Register observer
- `remove_observer(observer)` - Unregister observer

### MarkdownViewer

**Auto-Wrapping Pattern:**

```python
# Simple mode - creates internal document
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")

# Advanced mode - uses external document
document = MarkdownDocument()
viewer = MarkdownViewer(document=document)
```

## Performance

- **Efficient streaming**: Use `append_text()` for AI responses
- **Observer pattern**: Minimal overhead
- **Memory safety**: Automatic cleanup on widget close

## Examples

See the `examples/` directory for working demonstrations.
"""
        return [content[i : i + 80] for i in range(0, len(content), 80)]

    def _get_analysis(self) -> list:
        """Get analysis chunks."""
        content = """# Code Analysis Report

## Executive Summary

I've analyzed your markdown widget implementation. Here are my findings:

### Strengths ✅

1. **Clean Architecture**
   - Proper MVC separation
   - Model is Qt-independent
   - Observer pattern implementation

2. **Performance Optimizations**
   - Efficient `append_text()` for streaming
   - Minimal repaints
   - Smart memory management

3. **API Design**
   - Auto-wrapping pattern for MarkdownViewer
   - Intuitive method names
   - Good documentation

### Areas for Improvement 🔧

1. **Test Coverage**
   - Unit tests: ✅ Complete
   - Integration tests: ✅ Complete
   - Performance benchmarks: ⚠️ Could add more

2. **Documentation**
   - API docs: ✅ Good
   - Architecture guide: ✅ Excellent
   - Tutorial examples: ✅ Well done

### Code Quality Metrics

| Metric | Score | Status |
|--------|-------|--------|
| Test Coverage | 95% | ✅ Excellent |
| Documentation | 90% | ✅ Excellent |
| Code Style | 98% | ✅ Excellent |
| Architecture | 100% | ✅ Perfect |

## Detailed Analysis

### Observer Pattern Implementation

The observer pattern is correctly implemented:

```python
class MarkdownDocument:
    def _notify_observers(self, event):
        for observer in self._observers:
            observer.on_document_changed(event)
```

**Benefits:**
- Decouples model from views
- Supports multiple observers
- Easy to test

### Memory Management

Proper cleanup prevents memory leaks:

```python
def closeEvent(self, event):
    self._document.remove_observer(self)
    super().closeEvent(event)
```

## Recommendations

1. **Add Performance Benchmarks**
   - Measure streaming throughput
   - Profile memory usage
   - Test with large documents

2. **Consider Plugin System**
   - Custom markdown extensions
   - Syntax highlighting themes
   - Export formats

3. **Add More Examples**
   - Real-time collaboration
   - File watching
   - Custom preview templates

## Conclusion

The markdown widget is **production-ready** with excellent architecture and code quality. The MVC pattern is properly implemented, and the API is user-friendly.

**Overall Rating: 9.5/10** ⭐⭐⭐⭐⭐

Great work!
"""
        return [content[i : i + 60] for i in range(0, len(content), 60)]

    def _start_stream(self, chunks: list):
        """Start streaming chunks."""
        if self._stream_timer.isActive():
            return  # Already streaming

        self._clear()
        self._stream_chunks = chunks
        self._stream_index = 0
        self._status_label.setText(f"Streaming... (0/{len(chunks)} chunks)")

        # Stream chunks every 50ms for realistic effect
        self._stream_timer.start(50)

    def _stream_next_chunk(self):
        """Stream the next chunk."""
        if self._stream_index >= len(self._stream_chunks):
            # Done streaming
            self._stream_timer.stop()
            self._status_label.setText(
                f"✅ Streaming complete! ({len(self._stream_chunks)} chunks)"
            )
            return

        # Append next chunk using efficient append operation
        chunk = self._stream_chunks[self._stream_index]
        self._document.append_text(chunk)

        self._stream_index += 1
        self._status_label.setText(
            f"Streaming... ({self._stream_index}/{len(self._stream_chunks)} chunks)"
        )

    def _clear(self):
        """Clear the document."""
        self._document.set_text("")
        self._status_label.setText("Ready to stream")


def main():
    """Run the AI streaming demo."""
    app = QApplication(sys.argv)

    print("=" * 70)
    print("AI Streaming Simulation Demo")
    print("=" * 70)
    print()
    print("This demo simulates an AI assistant streaming markdown responses.")
    print()
    print("Features:")
    print("  • Efficient append operations (O(m) where m = chunk size)")
    print("  • Real-time preview updates")
    print("  • Observer pattern for synchronization")
    print("  • Performance optimized for rapid streaming")
    print()
    print("Try:")
    print("  1. Click 'Stream: Code Tutorial' for a programming tutorial")
    print("  2. Click 'Stream: Documentation' for API documentation")
    print("  3. Click 'Stream: Analysis' for code analysis report")
    print()
    print("Watch how the editor and preview stay synchronized as chunks arrive!")
    print()
    print("=" * 70)
    print()

    window = AIStreamingDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
