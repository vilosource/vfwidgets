# Markdown Widget MVC Architecture

**Status**: ✅ Architecture Complete - Ready for Implementation
**Date**: 2025-01-11 (Enhanced with critical patterns and advanced topics)
**Approach**: Proper MVC from the ground up

---

## Philosophy

**We are building this widget RIGHT from the start.**

### Core Principles

1. **Model-View-Controller** - Strict separation of concerns
2. **Observer Pattern** - Model notifies views of changes
3. **No Qt in Model** - Pure Python business logic
4. **Single Source of Truth** - Document state lives in model only
5. **Multiple Views Support** - Built-in from day one

### What We're NOT Doing

- ❌ No backward compatibility concerns
- ❌ No shortcuts or hacks
- ❌ No Qt dependencies in model
- ❌ No state duplication
- ❌ No tightly coupled components

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION                             │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ┌───────────────┐          ┌──────────────┐
        │  CONTROLLER   │          │    MODEL     │
        │               │◄─────────│              │
        │ Coordinates   │          │ Document     │
        │ Operations    │          │ State        │
        └───────────────┘          └──────────────┘
                                          │
                                          │ Observes
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                    ┌──────────┐    ┌──────────┐   ┌──────────┐
                    │  VIEW 1  │    │  VIEW 2  │   │  VIEW N  │
                    │          │    │          │   │          │
                    │ Editor   │    │ Viewer   │   │ TOC      │
                    └──────────┘    └──────────┘   └──────────┘
```

**Key Flow**:
1. User interacts with View
2. View notifies Controller
3. Controller updates Model
4. Model notifies all Observers
5. All Views update automatically

---

## Layer Breakdown

### 1. Model Layer (`src/vfwidgets_markdown/models/`)

**Purpose**: Single source of truth for document state

**Characteristics**:
- **Pure Python** - ZERO Qt dependencies
- **Observable** - Implements observer pattern
- **Testable** - Can test without QApplication
- **Versioned** - Tracks document changes

**Components**:

#### `MarkdownDocument` (models/document.py)
```python
class MarkdownDocument:
    """The document model - owns all document state."""

    def __init__(self, content: str = ""):
        self._content: str = content
        self._version: int = 0
        self._observers: list[DocumentObserver] = []

    # State access
    def get_text(self) -> str
    def get_version(self) -> int
    def get_toc(self) -> list[dict]

    # State mutation
    def set_text(text: str) -> None
    def append_text(text: str) -> None
    def update_section(heading_id: str, content: str) -> bool

    # Observer pattern
    def add_observer(observer: DocumentObserver) -> None
    def remove_observer(observer: DocumentObserver) -> None
```

**Key Features**:
- TOC parsing with caching
- Section-based operations
- Efficient append (O(1) not O(n))
- Change events for granular updates

#### `DocumentObserver` (models/protocols.py)
```python
class DocumentObserver(Protocol):
    """Protocol for observing document changes."""

    def on_document_changed(self, event: DocumentChangeEvent) -> None:
        """Called when document changes."""
        ...
```

#### Change Events (models/events.py)
```python
@dataclass
class TextReplaceEvent:
    """Full text replacement."""
    version: int
    text: str

@dataclass
class TextAppendEvent:
    """Text appended to end."""
    version: int
    text: str
    start_position: int

@dataclass
class SectionUpdateEvent:
    """Section updated."""
    version: int
    heading_id: str
    content: str
```

---

### 2. View Layer (`src/vfwidgets_markdown/widgets/`)

**Purpose**: Display document state, react to changes

**Characteristics**:
- **Observes Model** - Implements DocumentObserver
- **Qt Widgets** - Uses PySide6
- **No Business Logic** - Pure display
- **Reactive** - Updates on model changes

**Components**:

#### `MarkdownTextEditor` (widgets/text_editor.py)
```python
class MarkdownTextEditor(QPlainTextEdit):
    """Text editor that observes document model."""

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)  # ← OBSERVES

    def on_document_changed(self, event):
        """Model changed - update view."""
        if isinstance(event, TextReplaceEvent):
            self.setPlainText(event.text)
        elif isinstance(event, TextAppendEvent):
            # Efficient append
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(event.text)
```

**Key**: No state stored - just displays what model contains

#### `MarkdownViewer` (markdown_viewer.py)
```python
class MarkdownViewer(QWebEngineView):
    """HTML viewer that observes document model."""

    def __init__(self, document: Optional[MarkdownDocument] = None):
        super().__init__()
        if document:
            self.set_document(document)

    def set_document(self, document: MarkdownDocument):
        self._document = document
        self._document.add_observer(self)

    def on_document_changed(self, event):
        """Model changed - re-render."""
        html = markdown_to_html(self._document.get_text())
        self.setHtml(html)
```

#### `MarkdownTocView` (widgets/toc_view.py)
```python
class MarkdownTocView(QWidget):
    """TOC view that observes document model."""

    def on_document_changed(self, event):
        """Model changed - update TOC."""
        toc = self._document.get_toc()
        self.display_toc(toc)
```

---

## Critical Pattern: Preventing Update Loops

**Problem**: When a view observes the model and also updates it, you can create infinite loops:

```
User types → View updates model → Model notifies view → View updates itself →
View's text change triggers update to model → Model notifies view → ...
```

**Solution**: Use a flag to track when the view is updating from the model:

```python
class MarkdownTextEditor(QPlainTextEdit):
    """Text editor that observes document model."""

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)

        # ← CRITICAL: Flag to prevent update loops
        self._updating_from_model = False

        # Connect to Qt's text change signal
        self.textChanged.connect(self._on_qt_text_changed)

    def on_document_changed(self, event):
        """Model changed - update view."""
        # Set flag BEFORE updating Qt widget
        self._updating_from_model = True
        try:
            if isinstance(event, TextReplaceEvent):
                self.setPlainText(event.text)
            elif isinstance(event, TextAppendEvent):
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(event.text)
        finally:
            # Always clear flag, even if exception occurs
            self._updating_from_model = False

    def _on_qt_text_changed(self):
        """Qt widget changed (user typed) - update model."""
        # ← CRITICAL: Don't update model if we're updating from model!
        if not self._updating_from_model:
            self._document.set_text(self.toPlainText())
```

**Key Points**:
- **Every view that can update the model MUST use this pattern**
- Flag name: `_updating_from_model` (consistent across all views)
- Always use try/finally to ensure flag is cleared
- Check flag before updating model from Qt signals

**Why This Works**:
1. User types "A" → `textChanged` fires → flag is False → model updated
2. Model notifies observers → `on_document_changed()` called → flag set to True
3. View updates itself → `textChanged` fires → flag is True → model NOT updated
4. Loop prevented!

---

## Qt Signals vs Observer Pattern: A Dual Approach

**Question**: Why not use Qt signals for everything instead of the Python observer pattern?

**Answer**: We use **both patterns strategically** for maximum benefit.

### The Dual Pattern Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    DUAL PATTERN ARCHITECTURE             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Model (Pure Python)                                     │
│    → Python Observer Pattern → Views                     │
│    (Keeps model Qt-independent)                          │
│                                                          │
│  Views (Qt Widgets)                                      │
│    → Qt Signals/Slots ↔ Other Views                     │
│    (Native Qt for UI coordination)                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### When to Use Each Pattern

| Communication | Pattern | Reason |
|---------------|---------|--------|
| Model → Views | Python observer | Model stays pure Python (testable without Qt) |
| View internal signals | Qt signals/slots | Using Qt's native `textChanged`, etc. |
| View → View (UI state) | Qt signals/slots | Native Qt, best for UI coordination |
| View → Model | Direct method calls | Simple, pragmatic (Pragmatic MVC) |

### Pattern 1: Python Observer (Model → View)

**Use for**: Document content changes

```python
from vfwidgets_markdown.models import MarkdownDocument

class MarkdownTextEditor(QPlainTextEdit):
    """Editor that observes the pure Python model."""

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)  # ← Python observer pattern
        self._updating_from_model = False

    def on_document_changed(self, event):
        """Observer callback - NOT a Qt slot."""
        self._updating_from_model = True
        try:
            if isinstance(event, TextReplaceEvent):
                self.setPlainText(event.text)
            elif isinstance(event, TextAppendEvent):
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(event.text)
        finally:
            self._updating_from_model = False
```

**Why not Qt signals here?**
- ✅ Model has ZERO Qt dependencies
- ✅ Can test model without QApplication
- ✅ Model can be used in CLI tools, web servers, etc.
- ✅ Simpler model implementation

### Pattern 2: Qt Signals (View ↔ View)

**Use for**: UI state changes, view coordination

```python
from PySide6.QtCore import Signal, Slot

class MarkdownTocView(QWidget):
    """TOC view with Qt signals for UI coordination."""

    # Qt signals for UI events
    heading_clicked = Signal(str)  # heading_id
    heading_hovered = Signal(str)  # heading_id

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)  # Observer for model changes
        self._setup_ui()

    def on_document_changed(self, event):
        """Observer callback for model changes."""
        toc = self._document.get_toc()
        self.display_toc(toc)

    def _on_item_clicked(self, item):
        """Internal Qt slot."""
        heading_id = item.data(Qt.UserRole)
        self.heading_clicked.emit(heading_id)  # ← Emit Qt signal


class MarkdownTextEditor(QPlainTextEdit):
    """Editor that can receive signals from other views."""

    # Qt signals for editor events
    content_modified = Signal()  # Emitted when user edits
    cursor_moved = Signal(int, int)  # line, column

    @Slot(str)
    def scroll_to_heading(self, heading_id: str):
        """Qt slot - can be connected to TOC's heading_clicked signal."""
        # Find and scroll to heading
        text = self.toPlainText()
        # ... scroll logic ...


# In application or composite widget:
toc_view = MarkdownTocView(document)
editor = MarkdownTextEditor(document)

# Connect views with Qt signals (UI coordination)
toc_view.heading_clicked.connect(editor.scroll_to_heading)
```

**Why Qt signals here?**
- ✅ Native Qt pattern for UI events
- ✅ Type-safe connections
- ✅ Automatic disconnect on widget destruction
- ✅ Thread-safe with Qt::QueuedConnection
- ✅ Can use Qt's debugging tools

### Pattern 3: Internal Qt Signals (View → Model)

**Use for**: Capturing Qt widget events

```python
class MarkdownTextEditor(QPlainTextEdit):
    """Editor using Qt's internal signals."""

    # Define custom Qt signal
    content_modified = Signal()

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)
        self._updating_from_model = False

        # Connect Qt's built-in signal to our slot
        self.textChanged.connect(self._on_qt_text_changed)

    @Slot()
    def _on_qt_text_changed(self):
        """Qt slot responding to textChanged signal."""
        if not self._updating_from_model:
            # Update model directly (Pragmatic MVC)
            self._document.set_text(self.toPlainText())
            # Emit our custom signal
            self.content_modified.emit()
```

### Complete Data Flow with Both Patterns

```
USER TYPES "Hello"
    ↓
1. Qt's textChanged signal fires
    ↓
2. _on_qt_text_changed() slot called
    ↓
3. document.set_text("Hello")  [Direct call to model]
    ↓
4. Model updates, increments version
    ↓
5. Model calls: observer.on_document_changed(event)  [Python observer]
    ↓
6. All views receive callback:
   • Editor 1: on_document_changed() → updates display
   • Editor 2: on_document_changed() → updates display
   • Viewer: on_document_changed() → re-renders HTML
   • TOC: on_document_changed() → updates TOC list
    ↓
7. Editor emits: content_modified.emit()  [Qt signal]
    ↓
8. Any connected slots can respond (auto-save, etc.)
```

### Optional: Qt Adapter Pattern

If you **really want** Qt signals for model changes, create an adapter:

```python
from PySide6.QtCore import QObject, Signal

class QtMarkdownDocument(QObject):
    """Qt adapter that wraps the pure Python model."""

    # Qt signals mirroring model events
    text_replaced = Signal(object)  # TextReplaceEvent
    text_appended = Signal(object)  # TextAppendEvent
    section_updated = Signal(object)  # SectionUpdateEvent

    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)

    def on_document_changed(self, event):
        """Convert Python observer callback → Qt signal."""
        if isinstance(event, TextReplaceEvent):
            self.text_replaced.emit(event)
        elif isinstance(event, TextAppendEvent):
            self.text_appended.emit(event)
        elif isinstance(event, SectionUpdateEvent):
            self.section_updated.emit(event)

    # Delegate all model methods
    def set_text(self, text: str) -> None:
        self._document.set_text(text)

    def append_text(self, text: str) -> None:
        self._document.append_text(text)

    def get_text(self) -> str:
        return self._document.get_text()


# Usage: Views can choose Python observer OR Qt signals
qt_document = QtMarkdownDocument(document)

# Option 1: Python observer (direct)
editor1 = MarkdownTextEditor(document)

# Option 2: Qt signals (via adapter)
editor2 = MarkdownTextEditor(document)
qt_document.text_replaced.connect(lambda event: editor2.handle_replace(event))
```

### Summary: Best of Both Worlds

**Python Observer Pattern**:
- ✅ Model → View notifications
- ✅ Keeps model pure Python
- ✅ Testable without Qt
- ✅ Maximum reusability

**Qt Signals/Slots**:
- ✅ View internal events (textChanged, clicked, etc.)
- ✅ View → View coordination (UI state)
- ✅ Custom view events (content_modified, heading_clicked)
- ✅ Native Qt, type-safe, debuggable

**This architecture gives you**:
- Pure Python model (reusable, testable)
- Native Qt views (signals/slots for UI)
- Clean separation of concerns
- Best tool for each job

---

### 3. Controller Layer (`src/vfwidgets_markdown/controllers/`)

**Purpose**: Coordinate model operations and view behaviors

**Characteristics**:
- **No Qt Widgets** - Pure coordination logic
- **Has Timers** - For debouncing/throttling (uses Qt timers)
- **Operates on Model** - Not on views directly
- **Manages Timing** - When updates happen

**Components**:

#### `MarkdownEditorController` (controllers/editor_controller.py)
```python
class MarkdownEditorController:
    """Coordinates editor operations."""

    def __init__(self,
                 document: MarkdownDocument,
                 editor: MarkdownTextEditor,
                 viewer: MarkdownViewer):
        self._document = document  # ← Operates on model
        self._editor = editor
        self._viewer = viewer
        self._debounce_timer = QTimer()

    def pause_rendering(self):
        """Stop viewer updates temporarily."""
        self._document.remove_observer(self._viewer)

    def resume_rendering(self):
        """Resume viewer updates."""
        self._document.add_observer(self._viewer)

    def set_throttle_mode(self, enabled: bool, interval_ms: int):
        """Control update frequency."""
        # Throttle logic here
```

**Key**: Controller has references to model and views, coordinates between them

---

## Controller Usage Guidelines: When to Use Controllers

**This is "Pragmatic MVC"** - not strict textbook MVC. We balance simplicity with proper architecture.

### Rule: Views CAN Update Model Directly

**Simple cases** - view updates model directly:
```python
class MarkdownTextEditor(QPlainTextEdit):
    def _on_qt_text_changed(self):
        """User typed - update model directly."""
        if not self._updating_from_model:
            self._document.set_text(self.toPlainText())  # ← Direct model update
```

**Why?** For simple 1:1 interactions, going through a controller adds unnecessary complexity.

### Rule: Use Controllers for Coordination

**Use controllers when you need**:
- **Timing control** - Debouncing, throttling, pausing
- **Multi-view coordination** - Affecting multiple views
- **Complex operations** - Multiple model changes
- **State machines** - Mode switching

**Examples**:

#### Timing Control
```python
# Controller throttles rendering updates
controller.set_throttle_mode(True, interval_ms=200)

# Now even with 100 updates/second, viewer only updates 5 times/second
for chunk in ai_stream:
    document.append_text(chunk)  # Fast!
    # Viewer updates throttled by controller
```

#### Multi-View Coordination
```python
# Pause all rendering during batch update
controller.pause_rendering()

for i in range(1000):
    document.append_text(f"Line {i}\n")

controller.resume_rendering()  # Single update!
```

#### Complex Operations
```python
# Controller coordinates multi-step operation
controller.insert_image_at_cursor(
    image_path="logo.png",
    alt_text="Company Logo"
)
# Internally:
# 1. Gets cursor position from editor
# 2. Updates model at that position
# 3. Scrolls viewer to show image
# 4. Updates TOC if image has caption
```

### Decision Tree

```
Need to update model?
├─ YES
│  └─ Is it a simple 1:1 user action?
│     ├─ YES → View updates model directly
│     └─ NO → Does it involve:
│        ├─ Timing/throttling? → Use controller
│        ├─ Multiple views? → Use controller
│        ├─ Multiple steps? → Use controller
│        └─ Just model logic? → View updates model directly
└─ NO
   └─ Just displaying data? → View observes model
```

### Examples by Scenario

| Scenario | Who Updates Model | Why |
|----------|------------------|-----|
| User types in editor | View → Model | Simple 1:1 action |
| User clicks "Bold" button | View → Model | Simple 1:1 action |
| AI streaming (no throttle) | App → Model | Direct append is fine |
| AI streaming (with throttle) | App → Model, Controller throttles observers | Timing control needed |
| Batch import 1000 lines | Controller → Model | Pause/resume rendering |
| Find/replace | Controller → Model | Complex operation |
| Auto-save timer | Controller → Model | Timing/coordination |
| User scrolls TOC → scroll editor | Controller coordinates views | Multi-view coordination |

### Anti-Pattern: Overusing Controllers

❌ **DON'T** do this:
```python
# Unnecessarily complex
def _on_text_changed(self):
    self.controller.handle_text_change(self.toPlainText())

class Controller:
    def handle_text_change(self, text):
        self.model.set_text(text)  # Just forwarding!
```

✅ **DO** this instead:
```python
# Simple and direct
def _on_text_changed(self):
    self._document.set_text(self.toPlainText())
```

### Summary

**Controllers are for coordination, not gatekeeping.**

- ✅ Use controllers for timing, coordination, complex operations
- ✅ Let views update model directly for simple interactions
- ✅ Controllers operate *on* the model, not *between* view and model
- ❌ Don't make controllers mandatory middlemen for every interaction

---

## Data Flow Examples

### Example 1: User Types in Editor

```
1. User types "Hello" in MarkdownTextEditor
   ↓
2. Editor's textChanged signal fires
   ↓
3. Editor updates model: document.set_text("Hello")
   ↓
4. Model increments version, notifies observers
   ↓
5. All observers receive on_document_changed() call:
   - MarkdownViewer re-renders HTML
   - MarkdownTocView updates TOC list
   - Other MarkdownTextEditor (if exists) updates
   ↓
6. All views now show "Hello"
```

**No manual synchronization needed!**

### Example 2: AI Streaming Response

```
1. AI generates chunk: "# Title"
   ↓
2. App calls: document.append_text("# Title")
   ↓
3. Model emits TextAppendEvent
   ↓
4. Viewers receive event:
   - Editor inserts at end (O(1))
   - Viewer appends to DOM
   - TOC parses and updates
   ↓
5. Next chunk arrives, repeat
```

**Efficient streaming built-in!**

### Example 3: Multiple Editors Stay in Sync

```
           MarkdownDocument
                  │
          ┌───────┼───────┐
          ▼       ▼       ▼
       Editor1 Editor2 Viewer

1. Edit in Editor1: "Test"
   ↓
2. Document updates
   ↓
3. Editor2 and Viewer update automatically
```

**Free synchronization via observer pattern!**

---

## View Coordination Patterns

Sometimes views need to coordinate with each other beyond just displaying model state. Here are the patterns for view-to-view communication.

### Pattern 1: Model Changes (Preferred)

**When**: View action should affect document content

**Example**: User clicks heading in TOC → Should scroll to that heading

```python
class MarkdownTocView(QWidget):
    """TOC view that observes document model."""

    def _on_heading_clicked(self, heading_id: str):
        """User clicked a TOC entry."""
        # Option A: Update model with scroll marker (if part of document state)
        # This is ONLY if scroll position is part of the document model
        # Usually it's NOT - see Pattern 2 below
        pass
```

**Use when**: The action represents a change to document state (content, selection, etc.)

### Pattern 2: Direct View-to-View Signals (UI State)

**When**: View action affects UI state, not document content

**Example**: User clicks heading in TOC → Scroll editor view

```python
class MarkdownTocView(QWidget):
    """TOC view with navigation signals."""

    # Qt signal for scroll requests
    scroll_to_heading = Signal(str)  # heading_id

    def _on_heading_clicked(self, heading_id: str):
        """User clicked a TOC entry - emit signal."""
        self.scroll_to_heading.emit(heading_id)


class MarkdownTextEditor(QPlainTextEdit):
    """Text editor that can scroll to headings."""

    def scroll_to_heading(self, heading_id: str):
        """Scroll to show the given heading."""
        # Find heading in text
        text = self.toPlainText()
        # Search for heading line
        for line_num, line in enumerate(text.split('\n')):
            if self._is_heading_with_id(line, heading_id):
                # Scroll to that line
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, n=line_num)
                self.setTextCursor(cursor)
                break


# Wiring in composite widget or application
toc_view.scroll_to_heading.connect(editor.scroll_to_heading)
```

**Why not through model?** Scroll position is UI state, not document state. The model should not know about UI concerns like scroll positions.

### Pattern 3: Controller-Mediated (Complex Coordination)

**When**: Multiple views need to coordinate in complex ways

**Example**: Find/replace affects both editor and viewer

```python
class MarkdownEditorController:
    """Coordinates editor and viewer."""

    def find_and_replace_all(self, find_text: str, replace_text: str):
        """Find and replace, coordinating views."""
        # 1. Pause viewer rendering
        self._document.remove_observer(self._viewer)

        # 2. Get current text
        text = self._document.get_text()

        # 3. Perform replacements
        new_text = text.replace(find_text, replace_text)

        # 4. Update model
        self._document.set_text(new_text)

        # 5. Highlight changes in editor
        self._editor.highlight_replacements(find_text)

        # 6. Resume viewer rendering (single update)
        self._document.add_observer(self._viewer)

        # 7. Scroll viewer to first change
        self._viewer.scroll_to_first_highlight()
```

**Use when**: Operation involves multiple steps across multiple views

### Pattern 4: Shared State Object (Advanced)

**When**: Multiple views share non-document state (selection, find state, etc.)

**Example**: Shared selection state

```python
@dataclass
class EditorState:
    """Shared UI state (not document content)."""
    selection_start: int = 0
    selection_end: int = 0
    scroll_position: int = 0
    find_query: str = ""
    _observers: list = field(default_factory=list)

    def notify_observers(self):
        for obs in self._observers:
            obs.on_state_changed(self)


# Both editor and viewer observe the same EditorState
editor_state = EditorState()
editor.set_state(editor_state)
viewer.set_state(editor_state)

# Changes to state notify both views
```

**Use when**: You have complex UI state that multiple views need to share

### Decision Matrix

| Type of Action | Pattern | Example |
|----------------|---------|---------|
| Changes document content | Model update | User types, paste, AI append |
| UI state (scroll, cursor) | Direct view signal | TOC click → scroll editor |
| Complex multi-view operation | Controller | Find/replace, batch import |
| Shared UI state | State object | Selection tracking, find state |

### Key Principle

**Document state → Model**
**UI state → View signals or state objects**
**Complex coordination → Controller**

Don't put UI state in the model. Don't make the model aware of views. Keep concerns separated.

---

## Component Relationships

### Model is Independent
```
MarkdownDocument
  - NO dependencies on Qt
  - NO dependencies on views
  - NO dependencies on controllers
  - 100% pure Python
  - Can be imported without QApplication
```

### Views Depend on Model
```
MarkdownTextEditor
  - Depends on: MarkdownDocument
  - Observes: MarkdownDocument
  - Updates when: Model changes
```

### Controllers Coordinate Both
```
MarkdownEditorController
  - Has reference to: MarkdownDocument
  - Has reference to: Views (Editor, Viewer)
  - Coordinates: Model operations
  - Manages: Timing and flow control
```

### Composite Widgets Bundle Everything
```
MarkdownEditorWidget
  - Creates: MarkdownDocument internally
  - Creates: MarkdownTextEditor (view)
  - Creates: MarkdownViewer (view)
  - Creates: MarkdownEditorController
  - Wires: Everything together
  - Exposes: Simple API
```

---

## Design Patterns Used

### 1. Observer Pattern
**Purpose**: Decouple model from views

**Implementation**:
```python
# Model maintains list of observers
self._observers: list[DocumentObserver] = []

# Model notifies on change
def _notify_observers(self, event):
    for observer in self._observers:
        observer.on_document_changed(event)

# Views implement observer protocol
def on_document_changed(self, event):
    # React to change
```

### 2. MVC Pattern
**Purpose**: Separate concerns

**Model**: Business logic and state
**View**: Display and user interaction
**Controller**: Coordination and flow control

### 3. Protocol-Based Design
**Purpose**: Loose coupling

```python
class DocumentObserver(Protocol):
    """Any class implementing this is an observer."""
    def on_document_changed(self, event): ...
```

No inheritance required - duck typing

### 4. Event-Based Communication
**Purpose**: Granular change notifications

Different event types for different changes:
- `TextReplaceEvent` - Full replacement
- `TextAppendEvent` - Efficient append
- `SectionUpdateEvent` - Surgical update

### 5. Composite Pattern
**Purpose**: Hide complexity

`MarkdownEditorWidget` bundles:
- Model
- Views
- Controller
- Layout

User just creates one widget!

---

## Key Architectural Decisions

### Decision 1: Pure Python Model
**Rationale**: Testability, reusability, clarity

**Benefits**:
- Test without Qt/GUI
- Use in CLI tools
- Easy to understand
- No GUI coupling

**Trade-off**: Must use observer pattern for sync

### Decision 2: Observer Pattern for Sync
**Rationale**: Multiple views, loose coupling

**Benefits**:
- Add views without changing model
- Views automatically stay in sync
- No manual wiring needed

**Trade-off**: More complex than direct calls

### Decision 3: Event-Based Changes
**Rationale**: Efficiency, flexibility

**Benefits**:
- Views can optimize based on event type
- Append is O(1) not O(n)
- Future-proof for more event types

**Trade-off**: More event classes to maintain

### Decision 4: Three-Layer Architecture
**Rationale**: Clean separation, scalability

**Benefits**:
- Each layer independently testable
- Clear responsibilities
- Easy to extend

**Trade-off**: More files/classes than flat design

### Decision 5: No Backward Compatibility
**Rationale**: Fresh start, do it right

**Benefits**:
- No legacy baggage
- Clean design
- Modern patterns

**Trade-off**: None - this is new!

---

## Testing Strategy

### Model Tests (No Qt Needed!)
```python
def test_document_append():
    doc = MarkdownDocument()
    doc.append_text("Hello")
    assert doc.get_text() == "Hello"
```

**Run without QApplication** - pure Python tests

### View Tests (With pytest-qt)
```python
def test_editor_observes_model(qtbot):
    document = MarkdownDocument()
    editor = MarkdownTextEditor(document)
    qtbot.addWidget(editor)

    document.set_text("Test")
    assert editor.toPlainText() == "Test"
```

### Controller Tests
```python
def test_pause_resume_rendering():
    document = MarkdownDocument()
    viewer = MarkdownViewer(document)
    controller = MarkdownEditorController(document, editor, viewer)

    controller.pause_rendering()
    document.set_text("New")
    # Viewer should NOT update yet

    controller.resume_rendering()
    # Now viewer updates
```

### Integration Tests
```python
def test_multiple_editors_sync(qtbot):
    document = MarkdownDocument()
    editor1 = MarkdownTextEditor(document)
    editor2 = MarkdownTextEditor(document)

    editor1.setPlainText("Hello")
    assert editor2.toPlainText() == "Hello"
```

---

## Advanced Topics

### Error Handling Strategy

Error handling differs by layer. Here's our strategy:

#### Model Layer Errors

**Philosophy**: Model validates and raises exceptions for invalid operations

```python
class MarkdownDocument:
    def update_section(self, heading_id: str, content: str) -> bool:
        """Update a section, return success status."""
        # Validate input
        if not heading_id:
            raise ValueError("heading_id cannot be empty")

        # Try to find section
        sections = self._parse_sections()
        if heading_id not in sections:
            # Not an error - section doesn't exist
            return False

        # Update section
        # ... implementation ...
        return True
```

**Rules**:
- Raise `ValueError` for invalid arguments
- Raise `TypeError` for wrong types
- Return `False` or `None` for "not found" cases (not errors)
- Document exceptions in docstrings

#### View Layer Errors

**Philosophy**: Views catch and display errors, don't crash

```python
class MarkdownTextEditor(QPlainTextEdit):
    def on_document_changed(self, event):
        """Model changed - update view."""
        try:
            self._updating_from_model = True
            if isinstance(event, TextReplaceEvent):
                self.setPlainText(event.text)
            elif isinstance(event, TextAppendEvent):
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(event.text)
        except Exception as e:
            # Log error but don't crash the app
            logger.error(f"Failed to update editor view: {e}")
            # Optionally: show error in UI
            self.setStyleSheet("border: 2px solid red")
        finally:
            self._updating_from_model = False
```

**Rules**:
- Catch exceptions in observer callbacks
- Log errors with context
- Optionally show user-friendly error message
- Never let view crash propagate to model
- Always clean up (use finally blocks)

#### Controller Layer Errors

**Philosophy**: Controllers validate before operating, handle model/view errors

```python
class MarkdownEditorController:
    def find_and_replace_all(self, find_text: str, replace_text: str) -> tuple[bool, str]:
        """Find and replace, return (success, message)."""
        # Validate input
        if not find_text:
            return False, "Find text cannot be empty"

        try:
            # Pause rendering
            self._document.remove_observer(self._viewer)

            # Perform operation
            text = self._document.get_text()
            new_text = text.replace(find_text, replace_text)
            self._document.set_text(new_text)

            # Resume rendering
            self._document.add_observer(self._viewer)

            return True, f"Replaced {text.count(find_text)} occurrences"

        except Exception as e:
            # Resume rendering on error
            self._document.add_observer(self._viewer)
            logger.error(f"Find/replace failed: {e}")
            return False, f"Error: {str(e)}"
```

**Rules**:
- Validate before operating
- Return success/failure + message
- Clean up on errors (resume observers, etc.)
- Don't crash - return error status

### Threading Model

**Architecture**: Single-threaded by default, with explicit background work

#### Default: Main Thread Only

All operations run on Qt's main thread:
- Model operations
- Observer notifications
- View updates
- Controller operations

**Why?** Qt widgets must be used from the main thread. Keeping everything on main thread is simplest and safest.

#### Background Work Pattern

For expensive operations (parsing large documents, network requests):

```python
class MarkdownDocument:
    def set_text_async(self, text: str, callback: Callable[[bool], None]):
        """Set text with background TOC parsing."""

        # Quick: Update text immediately
        self._content = text
        self._version += 1
        self._notify_observers(TextReplaceEvent(self._version, text))

        # Slow: Parse TOC in background
        def parse_in_background():
            toc = self._parse_toc_expensive(text)
            # Back to main thread for callback
            QTimer.singleShot(0, lambda: self._on_toc_parsed(toc, callback))

        threading.Thread(target=parse_in_background, daemon=True).start()

    def _on_toc_parsed(self, toc: list, callback: Callable):
        """Called on main thread when TOC ready."""
        self._toc_cache = toc
        self._toc_cache_version = self._version
        callback(True)
```

**Rules**:
- Background threads CANNOT touch Qt widgets
- Use `QTimer.singleShot(0, lambda: ...)` to get back to main thread
- Mark background threads as `daemon=True`
- Document async methods clearly

#### Thread Safety

Model is NOT thread-safe by default:

```python
# ❌ DON'T do this (unsafe!)
def worker_thread():
    document.set_text("New text")  # Called from background thread!

# ✅ DO this instead
def worker_thread():
    QTimer.singleShot(0, lambda: document.set_text("New text"))
```

**Why not make model thread-safe?** Would add complexity (locks, mutexes) for a rare use case. Explicit is better.

### View Lifecycle & Memory Management

**Critical**: Observers must be removed when views are destroyed, or you'll leak memory.

#### Pattern: Remove Observer in Destructor

```python
class MarkdownTextEditor(QPlainTextEdit):
    def __init__(self, document: MarkdownDocument):
        super().__init__()
        self._document = document
        self._document.add_observer(self)

    def closeEvent(self, event):
        """View is closing - remove observer."""
        self._document.remove_observer(self)
        super().closeEvent(event)
```

#### Pattern: Context Manager for Temporary Observers

```python
from contextlib import contextmanager

@contextmanager
def observe_document(document: MarkdownDocument, observer):
    """Temporarily observe a document."""
    document.add_observer(observer)
    try:
        yield
    finally:
        document.remove_observer(observer)

# Usage
class TempObserver:
    def on_document_changed(self, event):
        print(f"Changed: {event}")

with observe_document(document, TempObserver()):
    document.set_text("Test")  # Observer notified
# Observer automatically removed
```

#### Memory Leak Detection

If views aren't being garbage collected:

```python
import weakref

class MarkdownDocument:
    def add_observer(self, observer):
        """Add observer with weak reference."""
        # Store weak reference to prevent keeping view alive
        self._observers.append(weakref.ref(observer))

    def _notify_observers(self, event):
        """Notify observers, removing dead references."""
        # Clean up dead references
        self._observers = [
            obs_ref for obs_ref in self._observers
            if obs_ref() is not None
        ]

        # Notify alive observers
        for obs_ref in self._observers:
            obs = obs_ref()
            if obs is not None:
                obs.on_document_changed(event)
```

**Trade-off**: Weak references make cleanup automatic but add complexity. Use only if you have memory leak issues.

---

## Performance Considerations

### Efficient Append
```python
# O(1) - Direct append
document.append_text(chunk)

# NOT O(n) - Full replacement
text = document.get_text()  # O(n)
text += chunk               # O(n)
document.set_text(text)     # O(n)
```

### TOC Caching
```python
self._toc_cache: Optional[list] = None
self._toc_cache_version: int = -1

def get_toc(self):
    if self._toc_cache_version == self._version:
        return self._toc_cache  # Cached!
    # Parse and cache
```

### Throttling for High-Frequency Updates
```python
controller.set_throttle_mode(True, min_interval_ms=200)

# Guarantees max 5 updates/second
# Even with 100 updates/second input
```

### Performance Complexity Reference

Here's the Big-O complexity for all major operations:

#### Model Operations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `get_text()` | O(1) | Returns reference to string |
| `set_text(text)` | O(n) | Copies text, notifies observers |
| `append_text(text)` | O(m) | Where m = len(text), Python string append |
| `get_version()` | O(1) | Returns integer |
| `get_toc()` | O(n) first call, O(1) cached | Where n = document length |
| `update_section(id, content)` | O(n) | Must find section, rebuild text |
| `add_observer()` | O(1) | Appends to list |
| `remove_observer()` | O(k) | Where k = number of observers |
| `_notify_observers()` | O(k) | Where k = number of observers |

#### View Operations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `on_document_changed()` with TextReplaceEvent | O(n) | Qt must re-layout entire text |
| `on_document_changed()` with TextAppendEvent | O(m) | Where m = appended text length |
| Editor: User types single char | O(1) + O(k) notifications | k = observers |
| Viewer: Re-render HTML | O(n) | Markdown parsing + HTML generation |
| TOC: Display update | O(h) | Where h = number of headings |

#### Controller Operations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `pause_rendering()` | O(1) | Just removes observer |
| `resume_rendering()` | O(1) + one render | Re-adds observer + catches up |
| `set_throttle_mode()` | O(1) | Configures timer |

#### Real-World Performance Targets

**Document Size Targets**:
- Small (< 10 KB): All operations < 10ms
- Medium (10-100 KB): Typing < 10ms, render < 50ms
- Large (100 KB - 1 MB): Typing < 10ms, render < 200ms
- Huge (> 1 MB): Use pagination/virtual scrolling

**AI Streaming Targets**:
- Append rate: 1000 chunks/second
- With throttling: 5 renders/second
- Memory growth: < 2x document size

**Observer Count Scaling**:
- 1-5 observers: No noticeable impact
- 5-20 observers: May need throttling
- 20+ observers: Definitely use throttling/batching

---

## Future Extensions

### Easy to Add
- ✅ New view types (minimap, diff view, etc.)
- ✅ Multiple simultaneous editors
- ✅ Undo/redo (command pattern on model)
- ✅ Collaborative editing (sync model state)
- ✅ Export formats (operate on model)

### Architectural Support
The MVC architecture makes these features natural:
- **Undo/Redo**: Command pattern wraps model operations
- **Collaboration**: Sync document state across network
- **Multiple Views**: Already built-in via observer pattern
- **Plugins**: Views observe model, no model changes needed

---

## Quick Reference

### Creating a Simple Editor
```python
# Create model
document = MarkdownDocument()

# Create view
editor = MarkdownTextEditor(document)
editor.show()

# That's it - they're connected!
```

### Multiple Views
```python
document = MarkdownDocument()

editor1 = MarkdownTextEditor(document)
editor2 = MarkdownTextEditor(document)
viewer = MarkdownViewer(document)

# All three stay in sync automatically
```

### Using Composite Widget
```python
# Even simpler - composite creates everything internally
editor_widget = MarkdownEditorWidget()
editor_widget.show()

# Access internals if needed
document = editor_widget.get_document()
```

### AI Streaming
```python
editor_widget = MarkdownEditorWidget()

# Stream AI response
for chunk in ai_response_stream():
    editor_widget.append_text(chunk)
    # Preview updates automatically with throttling
```

---

## Summary

### Architecture in Three Sentences

1. **Model** holds all document state and notifies observers of changes
2. **Views** observe the model and update themselves when notified
3. **Controllers** coordinate model operations and manage timing

### Key Insight

**By making the model observable and having views react to changes, we get automatic synchronization across all views without any manual wiring.**

This is the power of MVC + Observer pattern.

### Critical Patterns to Remember

1. **Dual Pattern Approach** - Python observer (Model→View) + Qt signals (View↔View) for best of both worlds
2. **Update Loop Prevention** - Always use `_updating_from_model` flag in views that can update the model
3. **Pragmatic MVC** - Views can update model directly for simple cases; use controllers for coordination
4. **View Coordination** - Document state → Model, UI state → View signals, Complex → Controller
5. **Error Handling** - Model raises, Views catch, Controllers validate
6. **Threading** - Single-threaded by default, explicit background work with `QTimer.singleShot`
7. **Memory Management** - Remove observers in `closeEvent()` or use weak references
8. **Performance** - Use `append_text()` for O(m) instead of `set_text()` for O(n), cache TOC, throttle high-frequency updates

### Documentation Structure

This architecture document covers:
- ✅ **Philosophy** - Why we're using MVC + Observer
- ✅ **Layer Breakdown** - Model, View, Controller details with code
- ✅ **Critical Patterns** - Update loop prevention (Section added 2025-01-11)
- ✅ **Qt Signals vs Observer Pattern** - Dual approach explained (Section added 2025-01-11)
- ✅ **Controller Guidelines** - When to use controllers vs direct updates (Section added 2025-01-11)
- ✅ **Data Flow Examples** - Real-world scenarios
- ✅ **View Coordination** - How views communicate (Section added 2025-01-11)
- ✅ **Component Relationships** - Dependencies between layers
- ✅ **Design Patterns** - Observer, MVC, Protocol-based, Event-based, Composite
- ✅ **Key Decisions** - Why we made specific architectural choices
- ✅ **Advanced Topics** - Error handling, threading, memory management (Section added 2025-01-11)
- ✅ **Performance** - Complexity analysis and targets (Enhanced 2025-01-11)
- ✅ **Testing Strategy** - How to test each layer
- ✅ **Future Extensions** - What's easy to add later

---

**Status**: ✅ Architecture Complete - Ready for Implementation

**Next**: See `TASKS.md` for sequential implementation tasks starting with TASK-001.
