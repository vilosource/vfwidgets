# MarkdownViewer DX Improvements Plan

## Context

While integrating MarkdownViewer into the reamde application, we encountered a critical DX issue:
- **Problem**: Calling `set_markdown()` immediately after widget creation resulted in no content being displayed
- **Root Cause**: QWebEngineView initializes asynchronously, but the API doesn't protect against premature usage
- **Impact**: Silent failure - no errors, no warnings, content just doesn't appear

This plan addresses DX improvements to prevent future developers from encountering this issue.

---

## Design Principles

1. **Fail Fast**: Errors should be caught immediately, not silently ignored
2. **Pit of Success**: The API should make the correct usage the easiest path
3. **Progressive Disclosure**: Simple cases should be simple, complex cases should be possible
4. **Clear Feedback**: Developers should know what's happening and why

---

## Tasks

### Phase 1: Immediate Safety Improvements (Critical)

#### Task 1.1: Add Content Queueing to MarkdownViewer
**Priority**: Critical
**Effort**: 2 hours

Make `set_markdown()` safe to call before viewer is ready by automatically queueing content.

**Implementation**:
```python
class MarkdownViewer:
    def __init__(self):
        super().__init__()
        self._is_ready = False
        self._pending_content: Optional[str] = None
        self._pending_base_path: Optional[Path] = None
        self.viewer_ready.connect(self._on_ready)

    def _on_ready(self):
        self._is_ready = True
        if self._pending_content is not None:
            self._actually_set_markdown(self._pending_content)
            self._pending_content = None
        if self._pending_base_path is not None:
            self._actually_set_base_path(self._pending_base_path)
            self._pending_base_path = None

    def set_markdown(self, content: str):
        """Set markdown content. Safe to call before viewer_ready."""
        if self._is_ready:
            self._actually_set_markdown(content)
        else:
            self._pending_content = content

    def set_base_path(self, path: Path):
        """Set base path. Safe to call before viewer_ready."""
        if self._is_ready:
            self._actually_set_base_path(path)
        else:
            self._pending_base_path = path
```

**Test Cases**:
- ✅ Call `set_markdown()` immediately after construction
- ✅ Call `set_markdown()` multiple times before ready (last one wins)
- ✅ Call `set_markdown()` after ready (immediate effect)
- ✅ Call `set_base_path()` before ready
- ✅ Verify content loads when viewer becomes ready

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

#### Task 1.2: Add Constructor Parameter for Initial Content
**Priority**: High
**Effort**: 1 hour

Allow developers to pass content in constructor for the most common use case.

**Implementation**:
```python
class MarkdownViewer(ThemedWidget, QWebEngineView):
    def __init__(
        self,
        initial_content: str = "",
        base_path: Optional[Path] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize MarkdownViewer.

        Args:
            initial_content: Markdown content to load when viewer is ready
            base_path: Base path for resolving relative URLs
            parent: Parent widget
        """
        super().__init__(parent)
        # ... existing initialization ...

        if initial_content:
            self.set_markdown(initial_content)
        if base_path:
            self.set_base_path(base_path)
```

**Usage**:
```python
# Simple case - content in constructor
viewer = MarkdownViewer(initial_content="# Hello\n\nWorld!")

# More explicit - set after creation (also works)
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")  # Automatically queued
```

**Test Cases**:
- ✅ Create with initial_content
- ✅ Create with base_path
- ✅ Create with both
- ✅ Create with empty content (default)
- ✅ Verify content loads when ready

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

#### Task 1.3: Add Logging/Warnings for Edge Cases
**Priority**: Medium
**Effort**: 1 hour

Provide clear feedback when unusual patterns are detected.

**Implementation**:
```python
import logging

logger = logging.getLogger(__name__)

class MarkdownViewer:
    def set_markdown(self, content: str):
        if not self._is_ready:
            logger.debug(
                "MarkdownViewer: set_markdown() called before viewer ready. "
                "Content will be loaded when initialization completes."
            )
            self._pending_content = content
        else:
            self._actually_set_markdown(content)

    def _on_ready(self):
        self._is_ready = True
        logger.debug("MarkdownViewer: Initialization complete, viewer ready")
        if self._pending_content is not None:
            logger.debug(f"MarkdownViewer: Loading queued content ({len(self._pending_content)} chars)")
            # ... load content ...
```

**Log Levels**:
- `DEBUG`: Normal operations (queueing, loading)
- `WARNING`: Unusual but recoverable (multiple sets before ready)
- `ERROR`: Actual problems (failed to load, JavaScript errors)

**Test Cases**:
- ✅ Verify debug logs appear in development
- ✅ Verify logs don't spam in production
- ✅ Test with logging disabled

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

### Phase 2: Documentation Improvements (High Priority)

#### Task 2.1: Update API Documentation
**Priority**: High
**Effort**: 2 hours

Make async initialization behavior crystal clear in docstrings.

**Implementation**:
```python
class MarkdownViewer(ThemedWidget, QWebEngineView):
    """Full-featured markdown viewer widget with live rendering.

    This widget uses QWebEngineView for rendering, which initializes
    asynchronously. The widget handles this automatically - you can call
    set_markdown() immediately and content will be queued until ready.

    Quick Start:
        # Simple usage - content in constructor
        viewer = MarkdownViewer(initial_content="# Hello")

        # Or set content after creation (automatically queued)
        viewer = MarkdownViewer()
        viewer.set_markdown("# Hello")  # Safe to call immediately

        # Or wait for ready signal explicitly
        viewer = MarkdownViewer()
        viewer.viewer_ready.connect(lambda: viewer.set_markdown("# Hello"))

    Signals:
        viewer_ready: Emitted when viewer is initialized and ready
        content_loaded: Emitted when markdown content finishes rendering
        ...

    Thread Safety:
        All methods must be called from the main Qt thread.
    """

    def set_markdown(self, content: str):
        """Set markdown content for rendering.

        This method is safe to call immediately after widget creation.
        If the viewer is not yet ready, content will be queued and loaded
        automatically when initialization completes.

        Args:
            content: Markdown text to render

        Signals Emitted:
            content_loaded: When rendering completes (after viewer_ready)

        Example:
            viewer = MarkdownViewer()
            viewer.set_markdown("# Title\\n\\nContent")  # Works immediately
        """
```

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

#### Task 2.2: Create Quick Start Example
**Priority**: High
**Effort**: 1 hour

Add a minimal "00_quick_start.py" example showing the simplest usage.

**Implementation**:
```python
#!/usr/bin/env python3
"""
Quick Start: MarkdownViewer in 10 Lines

This is the simplest possible usage of MarkdownViewer.
No observers, no signals, no async handling - just show markdown.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown import MarkdownViewer

app = QApplication(sys.argv)

# That's it - content loads automatically when viewer is ready
viewer = MarkdownViewer(initial_content="# Hello World\n\nThis is **markdown**!")
viewer.resize(800, 600)
viewer.show()

sys.exit(app.exec())
```

**Files to Create**:
- `examples/00_quick_start.py`

---

#### Task 2.3: Update README with Async Warning
**Priority**: Medium
**Effort**: 30 minutes

Add prominent notice about async initialization in README.

**Implementation**:
Add section to README.md:
```markdown
## Important: Async Initialization

MarkdownViewer uses QWebEngineView which initializes asynchronously.
**You don't need to worry about this** - the widget automatically queues
content until ready.

```python
# ✅ This works - content is queued automatically
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")  # Safe!

# ✅ This also works - content passed to constructor
viewer = MarkdownViewer(initial_content="# Hello")

# ✅ This works too - explicit signal handling (advanced)
viewer = MarkdownViewer()
viewer.viewer_ready.connect(lambda: viewer.set_markdown("# Hello"))
```

### When to use viewer_ready signal?

Most applications don't need to handle `viewer_ready` explicitly. However,
you should connect to it if:
- You need to perform actions exactly when rendering completes
- You're doing complex initialization sequences
- You want to show a loading indicator

See `examples/00_quick_start.py` for the simplest usage.
```

**Files to Modify**:
- `README.md`

---

### Phase 3: API Enhancements (Medium Priority)

#### Task 3.1: Add `is_ready()` Method
**Priority**: Medium
**Effort**: 30 minutes

Allow developers to check ready state programmatically.

**Implementation**:
```python
class MarkdownViewer:
    def is_ready(self) -> bool:
        """Check if viewer is fully initialized and ready.

        Returns:
            True if viewer is ready, False if still initializing

        Note:
            You usually don't need to check this - set_markdown()
            automatically queues content if not ready.
        """
        return self._is_ready
```

**Test Cases**:
- ✅ Returns False immediately after creation
- ✅ Returns True after viewer_ready signal
- ✅ Stays True for lifetime of widget

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

#### Task 3.2: Add `load_file()` Convenience Method
**Priority**: Medium
**Effort**: 1 hour

Make file loading a first-class operation.

**Implementation**:
```python
class MarkdownViewer:
    def load_file(self, file_path: str | Path) -> bool:
        """Load markdown content from a file.

        This is a convenience method that:
        1. Reads the file
        2. Sets the markdown content
        3. Sets the base path for relative URLs

        Args:
            file_path: Path to markdown file

        Returns:
            True if file was loaded successfully, False otherwise

        Example:
            viewer = MarkdownViewer()
            viewer.load_file("README.md")  # That's it!
        """
        try:
            file_path = Path(file_path)
            content = file_path.read_text(encoding="utf-8")
            self.set_markdown(content)
            self.set_base_path(file_path.parent)
            return True
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return False
```

**Test Cases**:
- ✅ Load existing file
- ✅ Load file with relative images
- ✅ Handle missing file gracefully
- ✅ Handle encoding errors
- ✅ Returns correct boolean status

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

#### Task 3.3: Add Content Loading State Signal
**Priority**: Low
**Effort**: 1 hour

Emit a signal when content is queued vs actually loaded.

**Implementation**:
```python
class MarkdownViewer:
    # Add new signal
    content_queued = Signal()  # Emitted when content set before ready

    def set_markdown(self, content: str):
        if self._is_ready:
            self._actually_set_markdown(content)
            # content_loaded signal already exists
        else:
            self._pending_content = content
            self.content_queued.emit()  # New signal
```

**Use Case**:
```python
viewer = MarkdownViewer()
viewer.content_queued.connect(lambda: print("Content queued, loading soon..."))
viewer.content_loaded.connect(lambda: print("Content displayed!"))
viewer.set_markdown("# Hello")
```

**Test Cases**:
- ✅ content_queued emitted when set before ready
- ✅ content_loaded emitted when rendering completes
- ✅ Only content_loaded if set after ready

**Files to Modify**:
- `src/vfwidgets_markdown/widgets/markdown_viewer.py`

---

### Phase 4: Testing & Validation (High Priority)

#### Task 4.1: Add Integration Test for Immediate Usage
**Priority**: High
**Effort**: 2 hours

Create comprehensive test covering the common usage pattern.

**Test File**: `tests/test_viewer_initialization.py`

**Test Cases**:
```python
def test_set_markdown_before_ready(qtbot):
    """Test that set_markdown() works immediately after construction."""
    viewer = MarkdownViewer()

    # Should not raise, should not display nothing
    viewer.set_markdown("# Test")

    # Wait for viewer to be ready
    with qtbot.waitSignal(viewer.viewer_ready, timeout=3000):
        pass

    # Wait for content to load
    with qtbot.waitSignal(viewer.content_loaded, timeout=3000):
        pass

    # Verify content is actually displayed
    # (implementation depends on how to query rendered content)

def test_constructor_with_initial_content(qtbot):
    """Test passing content in constructor."""
    viewer = MarkdownViewer(initial_content="# Hello")

    with qtbot.waitSignal(viewer.viewer_ready, timeout=3000):
        pass

    with qtbot.waitSignal(viewer.content_loaded, timeout=3000):
        pass

    # Verify content loaded

def test_multiple_sets_before_ready(qtbot):
    """Test calling set_markdown() multiple times before ready."""
    viewer = MarkdownViewer()

    viewer.set_markdown("# First")
    viewer.set_markdown("# Second")
    viewer.set_markdown("# Third")  # This should win

    with qtbot.waitSignal(viewer.viewer_ready, timeout=3000):
        pass

    with qtbot.waitSignal(viewer.content_loaded, timeout=3000):
        pass

    # Verify only "Third" is displayed

def test_load_file_convenience(qtbot, tmp_path):
    """Test load_file() convenience method."""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test File")

    viewer = MarkdownViewer()
    result = viewer.load_file(test_file)

    assert result is True

    with qtbot.waitSignal(viewer.viewer_ready, timeout=3000):
        pass

    with qtbot.waitSignal(viewer.content_loaded, timeout=3000):
        pass

def test_is_ready_state(qtbot):
    """Test is_ready() returns correct state."""
    viewer = MarkdownViewer()

    assert viewer.is_ready() is False

    with qtbot.waitSignal(viewer.viewer_ready, timeout=3000):
        pass

    assert viewer.is_ready() is True
```

**Files to Create**:
- `tests/test_viewer_initialization.py`

---

#### Task 4.2: Add Example Showing File Loading
**Priority**: Medium
**Effort**: 1 hour

Demonstrate the complete reamde use case.

**File**: `examples/06_file_viewer.py`

```python
#!/usr/bin/env python3
"""
Example: Simple File Viewer

This demonstrates the simplest way to build a file viewer like reamde.
Shows best practices for loading files into MarkdownViewer.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtGui import QAction
from vfwidgets_markdown import MarkdownViewer

class SimpleFileViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Markdown Viewer")
        self.resize(800, 600)

        # Create viewer as central widget
        self.viewer = MarkdownViewer()
        self.setCentralWidget(self.viewer)

        # Add menu
        self._create_menu()

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open...", self)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )

        if file_path:
            # That's it - one line to load the file!
            success = self.viewer.load_file(file_path)
            if success:
                self.setWindowTitle(f"Simple Markdown Viewer - {Path(file_path).name}")

def main():
    app = QApplication(sys.argv)

    viewer = SimpleFileViewer()
    viewer.show()

    # Load file from command line if provided
    if len(sys.argv) > 1:
        viewer.viewer.load_file(sys.argv[1])

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

**Files to Create**:
- `examples/06_file_viewer.py`

---

### Phase 5: Migration Guide (Low Priority)

#### Task 5.1: Document Breaking Changes
**Priority**: Low
**Effort**: 1 hour

If any of the changes are breaking, document migration path.

**File**: `docs/MIGRATION.md`

```markdown
# Migration Guide: MarkdownViewer v2.1

## Overview

Version 2.1 improves DX by making the widget safe to use immediately
after construction. No breaking changes - all existing code continues to work.

## What's New

### Automatic Content Queueing

You no longer need to manually handle the `viewer_ready` signal:

```python
# ❌ Old way (still works)
viewer = MarkdownViewer()
viewer.viewer_ready.connect(lambda: viewer.set_markdown("# Hello"))

# ✅ New way (recommended)
viewer = MarkdownViewer()
viewer.set_markdown("# Hello")  # Automatically queued

# ✅ Or use constructor
viewer = MarkdownViewer(initial_content="# Hello")
```

### New Methods

- `is_ready()` - Check initialization state
- `load_file(path)` - Load markdown from file in one call

## Upgrading

No code changes required - the widget is backward compatible.
However, you can simplify your code by removing manual viewer_ready handling.
```

**Files to Create**:
- `docs/MIGRATION.md`

---

## Implementation Order

### Sprint 1 (Critical - Do First)
1. Task 1.1: Content Queueing ⭐⭐⭐
2. Task 1.2: Constructor Parameter ⭐⭐⭐
3. Task 4.1: Integration Tests ⭐⭐⭐

### Sprint 2 (High Priority)
4. Task 2.1: API Documentation ⭐⭐
5. Task 2.2: Quick Start Example ⭐⭐
6. Task 3.2: load_file() Method ⭐⭐

### Sprint 3 (Polish)
7. Task 1.3: Logging/Warnings ⭐
8. Task 2.3: README Updates ⭐
9. Task 3.1: is_ready() Method ⭐
10. Task 4.2: File Viewer Example ⭐

### Sprint 4 (Optional)
11. Task 3.3: Content State Signals
12. Task 5.1: Migration Guide

---

## Success Metrics

After implementation, a new developer should be able to:

✅ Create a working viewer in 3 lines of code
✅ Load a file without reading docs
✅ Never encounter silent content failures
✅ Find clear examples in under 30 seconds
✅ Understand async behavior from docstrings

## Testing Strategy

Each task should include:
1. Unit tests (pytest)
2. Integration tests (pytest-qt)
3. Manual testing with examples
4. Documentation review

## Notes

- All changes should be backward compatible
- Existing code using viewer_ready explicitly should continue to work
- Focus on making simple cases simple while keeping advanced cases possible
- Prioritize safety (queuing) over performance (minor delay acceptable)
