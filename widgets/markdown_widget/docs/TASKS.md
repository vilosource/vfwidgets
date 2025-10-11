# Markdown Widget Implementation Tasks

**Status**: 🏗️ Ready to Build
**Approach**: Sequential execution - each task builds on previous
**Goal**: Working MVC markdown widget with proper architecture

---

## Task Execution Rules

1. **Execute in order** - Don't skip ahead
2. **Validate each task** - Run the validation command
3. **Check off completed** - Mark with ✅ when done
4. **Show evidence** - Paste validation output
5. **No assumptions** - If it doesn't run, it's not done

---

## Task Summary

**Total**: 15 core tasks + 5 demos = 20 items
**Estimated Time**: 2-3 days
**Phases**: 4 main phases

### Phase Breakdown
- **Phase 1**: Model Layer (5 tasks + demo) - 4 hours
- **Phase 2**: View Layer (3 tasks + demo) - 3 hours
- **Phase 3**: Controller Layer (2 tasks + demo) - 2 hours
- **Phase 4**: Integration (5 tasks + 2 demos) - 3 hours

---

## PHASE 1: Model Layer (Foundation)

**Goal**: Pure Python document model with observer pattern

### TASK-001: Create Model Package Files
**Time**: 15 min

**Files to create**:
```
src/vfwidgets_markdown/models/__init__.py
src/vfwidgets_markdown/models/protocols.py
src/vfwidgets_markdown/models/events.py
src/vfwidgets_markdown/models/document.py
```

**Action**: Create empty __init__ files first, then create protocol, events, and document stub

**Validation**:
```bash
cd /home/kuja/GitHub/vfwidgets/widgets/markdown_widget
python -c "from vfwidgets_markdown.models import MarkdownDocument; print('✅ Import works')"
```

Expected: `✅ Import works`

- [ ] Task complete

---

### TASK-002: Implement Core Document Model
**Time**: 45 min

**File**: `src/vfwidgets_markdown/models/document.py`

**What to implement**:
- `__init__(content="")`
- `get_text()` → str
- `set_text(text)` → void
- `append_text(text)` → void
- `get_version()` → int
- `add_observer(observer)`
- `remove_observer(observer)`
- `_notify_observers(event)`

**Validation**:
```bash
python -c "
from vfwidgets_markdown.models import MarkdownDocument
doc = MarkdownDocument('test')
print(f'Text: {doc.get_text()}')
print(f'Version: {doc.get_version()}')
doc.append_text(' more')
print(f'After append: {doc.get_text()}')
print(f'Version: {doc.get_version()}')
print('✅ Core model works')
"
```

Expected:
```
Text: test
Version: 0
After append: test more
Version: 1
✅ Core model works
```

- [ ] Task complete

---

### TASK-003: Implement Observer Pattern
**Time**: 30 min

**Files**:
- `src/vfwidgets_markdown/models/protocols.py` - DocumentObserver protocol
- `src/vfwidgets_markdown/models/events.py` - Event classes

**What to implement**:
- `DocumentObserver` protocol with `on_document_changed(event)`
- `TextReplaceEvent` dataclass
- `TextAppendEvent` dataclass

**Validation**:
```bash
python -c "
from vfwidgets_markdown.models import MarkdownDocument, TextReplaceEvent

doc = MarkdownDocument()
events = []

class TestObserver:
    def on_document_changed(self, event):
        events.append(event)

observer = TestObserver()
doc.add_observer(observer)
doc.set_text('Hello')
doc.append_text(' World')

print(f'Events received: {len(events)}')
print(f'Event 1: {events[0].__class__.__name__}')
print(f'Event 2: {events[1].__class__.__name__}')
print('✅ Observer pattern works')
"
```

Expected:
```
Events received: 2
Event 1: TextReplaceEvent
Event 2: TextAppendEvent
✅ Observer pattern works
```

- [ ] Task complete

---

### TASK-004: Implement TOC Parsing
**Time**: 45 min

**File**: `src/vfwidgets_markdown/models/document.py` (add methods)

**What to implement**:
- `get_toc()` → list[dict]
- `_parse_toc()` → list[dict] (private helper)
- TOC caching with `_toc_cache` and `_toc_cache_version`

**Validation**:
```bash
python -c "
from vfwidgets_markdown.models import MarkdownDocument

doc = MarkdownDocument('''
# Title
## Section 1
### Subsection
## Section 2
''')

toc = doc.get_toc()
print(f'TOC entries: {len(toc)}')
for entry in toc:
    indent = '  ' * (entry['level'] - 1)
    print(f\"{indent}{entry['text']} (id: {entry['id']})\")
print('✅ TOC parsing works')
"
```

Expected:
```
TOC entries: 4
Title (id: title)
  Section 1 (id: section-1)
    Subsection (id: subsection)
  Section 2 (id: section-2)
✅ TOC parsing works
```

- [ ] Task complete

---

### TASK-005: Write Model Tests
**Time**: 30 min

**File**: `tests/models/test_document.py`

**What to test**:
- Core operations (set_text, append_text, get_text)
- Observer pattern (add/remove, notifications)
- TOC parsing (basic structure, GitHub IDs)
- Version tracking

**Validation**:
```bash
cd /home/kuja/GitHub/vfwidgets/widgets/markdown_widget
pytest tests/models/test_document.py -v
```

Expected: All tests pass (green)

- [ ] Task complete

---

### DEMO-1: Model Foundation Demo
**Time**: 15 min

**File**: `examples/demo_model_foundation.py`

**What to demo**:
- Create document
- Set/append text
- Observer notifications
- TOC parsing
- No Qt - pure Python

**Validation**:
```bash
python examples/demo_model_foundation.py
```

Expected: Clean output showing all features work

- [ ] Demo complete

---

## PHASE 2: View Layer (Qt Observers)

**Goal**: Qt widgets that observe the model

### TASK-101: Implement MarkdownTextEditor
**Time**: 45 min

**File**: `src/vfwidgets_markdown/widgets/text_editor.py`

**What to implement**:
- `__init__(document: MarkdownDocument)`
- `on_document_changed(event)` - Python observer method (NOT a Qt slot)
- Handle TextReplaceEvent, TextAppendEvent
- `_updating_from_model` flag to prevent loops
- **Qt Signals** (for UI coordination):
  - `content_modified = Signal()` - Emitted when user edits
  - `cursor_moved = Signal(int, int)` - Emitted on cursor position change
- **Qt Slots** (for view coordination):
  - `@Slot(str) scroll_to_heading(heading_id)` - Scroll to a heading
- Connect `textChanged` signal → `_on_qt_text_changed()` slot

**Validation**:
```bash
python -c "
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.text_editor import MarkdownTextEditor

app = QApplication([])
document = MarkdownDocument('Initial')
editor = MarkdownTextEditor(document)

print(f'Editor shows: {editor.toPlainText()}')
document.append_text(' text')
print(f'After append: {editor.toPlainText()}')
print('✅ Editor observes model')
"
```

Expected:
```
Editor shows: Initial
After append: Initial text
✅ Editor observes model
```

- [ ] Task complete

---

### TASK-102: Implement MarkdownTocView
**Time**: 30 min

**File**: `src/vfwidgets_markdown/widgets/toc_view.py`

**What to implement**:
- `__init__(document: MarkdownDocument)`
- `on_document_changed(event)` - Python observer method (NOT a Qt slot)
- `display_toc(toc: list[dict])` - Update UI with TOC
- **Qt Signals** (for UI coordination):
  - `heading_clicked = Signal(str)` - Emitted when user clicks a heading (heading_id)
  - `heading_hovered = Signal(str)` - Emitted when user hovers over heading
- Connect QListWidget signals → internal slots → emit custom signals

**Validation**:
```bash
python -c "
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.toc_view import MarkdownTocView

app = QApplication([])
document = MarkdownDocument('# Title\n## Section')
toc_view = MarkdownTocView(document)

# Should auto-populate from model
print(f'TOC has items: {toc_view._list.count() > 0}')
print('✅ TOC observes model')
"
```

Expected:
```
TOC has items: True
✅ TOC observes model
```

- [ ] Task complete

---

### TASK-103: Write View Tests
**Time**: 30 min

**File**: `tests/widgets/test_text_editor.py`

**What to test**:
- Editor observes model (Python observer pattern)
- Model changes update editor
- Multiple editors stay in sync
- No update loops (`_updating_from_model` flag works)
- **Qt Signals**: `content_modified` emitted when user types
- **Qt Signals**: Use `qtbot.waitSignal()` to test signal emissions
- **Qt Slots**: `scroll_to_heading()` slot works

**Validation**:
```bash
pytest tests/widgets/test_text_editor.py -v
```

Expected: All tests pass

- [ ] Task complete

---

### DEMO-2: Multiple Views Demo
**Time**: 20 min

**File**: `examples/demo_multiple_views.py`

**What to demo**:
- One document (pure Python model)
- Two editors + one TOC view
- **Python Observer Pattern**: Edit in either editor → all views update via model
- **Qt Signals/Slots**: TOC heading click → editor scrolls (view-to-view)
- Print connection diagram showing both patterns
- Demonstrate `content_modified` signal emission

**Validation**:
```bash
python examples/demo_multiple_views.py
```

Expected:
- Window opens with editors and TOC
- Typing in editor updates all views (observer pattern)
- Clicking TOC scrolls editor (Qt signals)
- Console shows which pattern is being used

- [ ] Demo complete

---

## PHASE 3: Controller Layer (Coordination)

**Goal**: Controllers that coordinate model operations

### TASK-201: Implement MarkdownEditorController
**Time**: 45 min

**File**: `src/vfwidgets_markdown/controllers/editor_controller.py`

**What to implement**:
- `__init__(document, editor, viewer)`
- `pause_rendering()`
- `resume_rendering()`
- `set_throttle_mode(enabled, interval_ms)`
- Debounce timer logic

**Validation**:
```bash
python -c "
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets.text_editor import MarkdownTextEditor
from vfwidgets_markdown.controllers.editor_controller import MarkdownEditorController

app = QApplication([])
document = MarkdownDocument()
editor = MarkdownTextEditor(document)

# Mock viewer for test
class MockViewer:
    updated = False
    def on_document_changed(self, event):
        self.updated = True

viewer = MockViewer()
document.add_observer(viewer)

controller = MarkdownEditorController(document, editor, viewer)
controller.pause_rendering()
document.set_text('Test')
print(f'Viewer updated while paused: {viewer.updated}')

controller.resume_rendering()
print('✅ Controller works')
"
```

Expected:
```
Viewer updated while paused: False
✅ Controller works
```

- [ ] Task complete

---

### TASK-202: Write Controller Tests
**Time**: 30 min

**File**: `tests/controllers/test_editor_controller.py`

**What to test**:
- Pause/resume rendering
- Throttle mode
- Debouncing

**Validation**:
```bash
pytest tests/controllers/ -v
```

Expected: All tests pass

- [ ] Task complete

---

### DEMO-3: Controller Features Demo
**Time**: 15 min

**File**: `examples/demo_controller_features.py`

**What to demo**:
- Pause rendering during batch updates
- Resume rendering
- Throttling for high-frequency updates

**Validation**:
```bash
python examples/demo_controller_features.py
```

Expected: Demonstrates pause/resume and throttling

- [ ] Demo complete

---

## PHASE 4: Integration (Complete System)

**Goal**: Everything working together

### TASK-301: Create pyproject.toml
**Time**: 20 min

**File**: `pyproject.toml`

**What to include**:
- Package metadata
- Dependencies (PySide6)
- Build system
- Entry points

**Validation**:
```bash
pip install -e .
python -c "import vfwidgets_markdown; print('✅ Package installs')"
```

Expected: `✅ Package installs`

- [ ] Task complete

---

### TASK-302: Create MarkdownEditorWidget Composite
**Time**: 45 min

**File**: `src/vfwidgets_markdown/widgets/editor_widget.py`

**What to implement**:
- Creates document internally
- Creates editor + viewer
- Creates controller
- Wires everything together
- Simple API: `set_text()`, `append_text()`, `get_document()`

**Validation**:
```bash
python -c "
from PySide6.QtWidgets import QApplication
from vfwidgets_markdown.widgets.editor_widget import MarkdownEditorWidget

app = QApplication([])
widget = MarkdownEditorWidget()
widget.set_text('# Hello World')
print(f'Text set: {widget.get_document().get_text()[:13]}')
print('✅ Composite widget works')
"
```

Expected:
```
Text set: # Hello World
✅ Composite widget works
```

- [ ] Task complete

---

### TASK-303: Create README.md
**Time**: 30 min

**File**: `README.md`

**What to include**:
- Quick start example
- Installation
- Basic usage
- Architecture overview
- Link to docs/ARCHITECTURE.md

**Validation**: Read the README - does it make sense?

- [ ] Task complete

---

### TASK-304: Copy MarkdownViewer from Old Widget
**Time**: 30 min

**Action**: Copy the WebEngine viewer from old widget (it works!)

**Files to copy**:
- `markdown_widget_OLD_2025-01-11/src/vfwidgets_markdown/markdown_viewer.py`
- `markdown_widget_OLD_2025-01-11/src/vfwidgets_markdown/resources/` (HTML/CSS/JS)

**Then**: Update to support document observation

**Validation**:
```bash
python -c "
from vfwidgets_markdown import MarkdownViewer
from vfwidgets_markdown.models import MarkdownDocument
print('✅ Viewer imports and integrates')
"
```

- [ ] Task complete

---

### TASK-305: Write Integration Tests
**Time**: 45 min

**File**: `tests/integration/test_full_system.py`

**What to test**:
- Complete editor widget
- Model → View → Controller flow
- Multiple views synchronization
- AI streaming scenario

**Validation**:
```bash
pytest tests/integration/ -v
```

Expected: All integration tests pass

- [ ] Task complete

---

### DEMO-4: Complete Editor Demo
**Time**: 30 min

**File**: `examples/demo_complete_editor.py`

**What to demo**:
- Full MarkdownEditorWidget
- Live preview
- TOC navigation
- All features working

**Validation**:
```bash
python examples/demo_complete_editor.py
```

Expected: Professional-looking editor with all features

- [ ] Demo complete

---

### DEMO-5: AI Streaming Demo
**Time**: 30 min

**File**: `examples/demo_ai_streaming.py`

**What to demo**:
- Simulated AI response streaming
- Efficient append operations
- Throttled rendering
- Live preview updates

**Validation**:
```bash
python examples/demo_ai_streaming.py
```

Expected: Smooth streaming demonstration

- [ ] Demo complete

---

## Completion Checklist

### Phase 1: Model ✅
- [ ] Core document operations work
- [ ] Observer pattern implemented
- [ ] TOC parsing works
- [ ] Tests pass
- [ ] Demo runs

### Phase 2: Views ✅
- [ ] Editor observes model
- [ ] TOC view observes model
- [ ] Multiple views sync
- [ ] Tests pass
- [ ] Demo shows multiple views

### Phase 3: Controllers ✅
- [ ] Pause/resume works
- [ ] Throttling works
- [ ] Tests pass
- [ ] Demo shows features

### Phase 4: Integration ✅
- [ ] Package installs
- [ ] Composite widget works
- [ ] Viewer integrated
- [ ] README written
- [ ] All demos work
- [ ] All tests pass

---

## Success Criteria

When all tasks are complete:

✅ Pure Python model with no Qt dependencies
✅ Observer pattern working
✅ Multiple views stay in sync automatically
✅ Controllers coordinate operations
✅ Composite widgets provide simple API
✅ All tests passing
✅ All demos working
✅ Clean, understandable code
✅ Proper MVC architecture
✅ Ready for AI streaming features

---

## Next Steps After Completion

Once all tasks are done:

1. **Performance Testing** - Benchmark append vs replace
2. **AI Streaming Features** - Add advanced streaming APIs
3. **Section Operations** - Implement update_section()
4. **Theme Integration** - Add theme support
5. **More Widgets** - MarkdownViewerWidget, etc.

---

## Notes

### Execution Tips

1. **Start Fresh Each Day** - Review ARCHITECTURE.md
2. **One Task at a Time** - Don't skip ahead
3. **Validate Everything** - Run validation commands
4. **Ask Questions** - If stuck, refer to ARCHITECTURE.md
5. **Keep It Clean** - Follow the patterns

### Common Pitfalls

⚠️ **Update Loops**: Use `_updating_from_model` flag in views
⚠️ **Qt in Model**: Model must be pure Python
⚠️ **Missing Observers**: Remember to add_observer()
⚠️ **Event Types**: Match event type in observer handlers

### Debug Commands

```bash
# Run single test
pytest tests/models/test_document.py::test_append_text -v

# Run with output
pytest tests/ -v -s

# Check imports
python -c "from vfwidgets_markdown.models import MarkdownDocument"

# Interactive testing
python -i examples/demo_model_foundation.py
```

---

**Ready to start? Begin with TASK-001!**
