# VFTheme Studio - Phase 1 Implementation Tasks

**Phase:** Foundation (Weeks 1-2)
**Goal:** Basic application structure and navigation
**Status:** ✅ COMPLETE (100%)
**Started:** 2025-10-12
**Completed:** 2025-10-12
**Tasks:** 18/18 complete
**Tests:** 10/10 passing

---

## Phase 1 Overview

### Objectives

Create the foundational structure of VFTheme Studio with:
- Working application window with 3-panel layout
- Basic token browsing (read-only)
- Static preview of generic Qt widgets
- File operations (New, Open, Save)
- Theme document model

### Success Criteria

- ✅ Application launches successfully
- ✅ Three panels visible and resizable
- ✅ Can open existing theme JSON files
- ✅ Token browser displays all 197 tokens in categories
- ✅ Preview canvas shows sample widgets with theme applied
- ✅ Inspector shows selected token information
- ✅ Can save theme (no editing yet)

### Deliverables

1. Main application window (`ThemeStudioWindow`)
2. Token browser panel (read-only tree view)
3. Preview canvas panel (static widget preview)
4. Inspector panel (view-only token properties)
5. File operations (New, Open, Save, Save As)
6. Theme document model with signals

---

## Task Breakdown

### Category 1: Project Foundation

#### Task 1.1: Create Application Entry Point
**Priority:** Critical
**Dependencies:** None
**Estimated Time:** 1 hour

**Description:**
Create the main application entry point that initializes PySide6, sets up theming, and launches the main window.

**Files to Create/Modify:**
- `src/theme_studio/app.py` - ThemedApplication subclass
- `src/theme_studio/__main__.py` - Update with real implementation

**Acceptance Criteria:**
- [ ] Application launches with proper PySide6 initialization
- [ ] ThemedApplication properly configured
- [ ] Window icon set
- [ ] Application metadata (name, version) set correctly
- [ ] Clean shutdown on close

**Implementation Notes:**
```python
# src/theme_studio/app.py
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedApplication

class ThemeStudioApp(ThemedApplication):
    """Main application class."""

    def __init__(self, argv):
        super().__init__(argv)

        # Application metadata
        self.setApplicationName("VFTheme Studio")
        self.setApplicationVersion("0.1.0-dev")
        self.setOrganizationName("Vilosource")

        # Set default theme
        self.set_theme("dark")
```

**Testing:**
```bash
python -m theme_studio
# Should launch and show window
```

**Evidence Required:**
- Screenshot of launched application
- Terminal output showing clean startup
- Exit code 0 on close

---

#### Task 1.2: Create Main Window Structure
**Priority:** Critical
**Dependencies:** Task 1.1
**Estimated Time:** 2-3 hours

**Description:**
Create the main window class based on ViloCodeWindow with menu bar, toolbar, and status bar.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Main window class
- `src/theme_studio/components/menubar.py` - Menu bar builder
- `src/theme_studio/components/toolbar.py` - Toolbar builder
- `src/theme_studio/components/status_bar.py` - Status bar

**Acceptance Criteria:**
- [ ] Window class inherits from ViloCodeWindow and ThemedWidget
- [ ] Default window size: 1600x1000
- [ ] Minimum window size: 1200x800
- [ ] Window title: "VFTheme Studio"
- [ ] Menu bar with all 7 menus (actions can be stubs)
- [ ] Toolbar with file/edit groups (connected to stubs)
- [ ] Status bar with 3 sections

**Implementation Notes:**
```python
# src/theme_studio/window.py
from PySide6.QtWidgets import QMainWindow, QSplitter
from vfwidgets_theme import ThemedWidget

class ThemeStudioWindow(QMainWindow, ThemedWidget):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle("VFTheme Studio")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)

        # Setup UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
```

**Testing:**
- Window appears with correct size
- All menus visible and clickable (even if actions don't work yet)
- Toolbar buttons visible
- Status bar shows placeholder text

**Evidence Required:**
- Screenshot showing complete window structure
- Menu expansion screenshots (all 7 menus)
- Window resize demonstration

---

#### Task 1.3: Create Three-Panel Layout
**Priority:** Critical
**Dependencies:** Task 1.2
**Estimated Time:** 2 hours

**Description:**
Create the central widget with QSplitter containing three resizable panels.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Add central widget layout
- `src/theme_studio/panels/token_browser.py` - Panel placeholder
- `src/theme_studio/panels/preview_canvas.py` - Panel placeholder
- `src/theme_studio/panels/inspector.py` - Panel placeholder

**Acceptance Criteria:**
- [ ] Three panels visible in 25% | 50% | 25% ratio
- [ ] Panels resizable via splitter handles
- [ ] Minimum panel widths enforced (200px | 400px | 200px)
- [ ] Panel sizes persist between sessions (saved to settings)
- [ ] Each panel shows placeholder content with title

**Implementation Notes:**
```python
def _create_central_widget(self):
    """Create three-panel layout."""
    # Main splitter
    self.main_splitter = QSplitter(Qt.Horizontal)

    # Create panels (placeholders for now)
    self.token_browser = TokenBrowserPanel()
    self.preview_canvas = PreviewCanvasPanel()
    self.inspector_panel = InspectorPanel()

    # Add to splitter
    self.main_splitter.addWidget(self.token_browser)
    self.main_splitter.addWidget(self.preview_canvas)
    self.main_splitter.addWidget(self.inspector_panel)

    # Set initial sizes (25% | 50% | 25%)
    self.main_splitter.setSizes([400, 800, 400])

    # Set as central widget
    self.setCentralWidget(self.main_splitter)
```

**Testing:**
- Drag splitter handles to resize panels
- Verify minimum widths enforced
- Close and reopen app (panel sizes should persist)

**Evidence Required:**
- Screenshot showing three panels
- Video/GIF of panel resizing
- Settings file showing saved sizes

---

### Category 2: Theme Document Model

#### Task 2.1: Create Theme Document Model
**Priority:** Critical
**Dependencies:** Task 1.1
**Estimated Time:** 3-4 hours

**Description:**
Create the ThemeDocument model that wraps a Theme object with undo/redo support and change tracking.

**Files to Create/Modify:**
- `src/theme_studio/models/theme_document.py` - Document model
- `src/theme_studio/models/history.py` - Undo/redo stack wrapper
- `tests/test_theme_document.py` - Unit tests

**Acceptance Criteria:**
- [ ] ThemeDocument class wraps vfwidgets_theme.Theme
- [ ] Emits signals on token changes: `token_changed(str, str)`
- [ ] Emits signal on modification: `modified(bool)`
- [ ] Tracks modified state (unsaved changes)
- [ ] Provides get/set methods for tokens
- [ ] QUndoStack integrated (for future undo/redo)
- [ ] File path tracking
- [ ] Can serialize to/from JSON

**Implementation Notes:**
```python
# src/theme_studio/models/theme_document.py
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
from vfwidgets_theme import Theme

class ThemeDocument(QObject):
    """Observable theme document with undo/redo support."""

    # Signals
    token_changed = Signal(str, str)  # token_name, new_value
    modified = Signal(bool)           # is_modified

    def __init__(self, theme: Theme = None):
        super().__init__()
        self._theme = theme or Theme.create_default()
        self._file_path = None
        self._modified = False
        self._undo_stack = QUndoStack(self)

    def get_token(self, name: str) -> str:
        """Get token value."""
        return self._theme.colors.get(name, "")

    def set_token(self, name: str, value: str):
        """Set token value (future: with undo support)."""
        # For Phase 1, direct setting (no undo yet)
        old_value = self._theme.colors.get(name)
        if old_value != value:
            self._theme.colors[name] = value
            self._modified = True
            self.token_changed.emit(name, value)
            self.modified.emit(True)

    def save(self, file_path: str = None):
        """Save theme to file."""
        path = file_path or self._file_path
        if not path:
            raise ValueError("No file path specified")

        self._theme.save(path)
        self._file_path = path
        self._modified = False
        self.modified.emit(False)

    def load(self, file_path: str):
        """Load theme from file."""
        self._theme = Theme.load(file_path)
        self._file_path = file_path
        self._modified = False
        self.modified.emit(False)
```

**Testing:**
```python
def test_theme_document_signals():
    doc = ThemeDocument()

    # Track signals
    token_changes = []
    doc.token_changed.connect(lambda n, v: token_changes.append((n, v)))

    # Change token
    doc.set_token("button.background", "#ff0000")

    # Verify signal emitted
    assert len(token_changes) == 1
    assert token_changes[0] == ("button.background", "#ff0000")
    assert doc.is_modified()
```

**Evidence Required:**
- Test output showing all tests passing
- Code demonstrating signal emission
- Example of save/load round-trip

---

#### Task 2.2: Integrate Theme Document with Window
**Priority:** Critical
**Dependencies:** Task 2.1, Task 1.2
**Estimated Time:** 2 hours

**Description:**
Connect the ThemeDocument to the main window, allowing document changes to update UI.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Add document management

**Acceptance Criteria:**
- [ ] Window has `current_document` property
- [ ] Window title updates with document name and modified state
- [ ] Status bar shows document info
- [ ] Document signals connected to UI updates

**Implementation Notes:**
```python
class ThemeStudioWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._current_document = None
        # ... setup ...

    def set_document(self, document: ThemeDocument):
        """Set current theme document."""
        # Disconnect old document
        if self._current_document:
            self._current_document.modified.disconnect()
            self._current_document.token_changed.disconnect()

        # Set new document
        self._current_document = document

        # Connect signals
        document.modified.connect(self._on_document_modified)
        document.token_changed.connect(self._on_token_changed)

        # Update UI
        self._update_window_title()
        self._update_status_bar()

    def _update_window_title(self):
        """Update window title with document name."""
        if not self._current_document:
            self.setWindowTitle("VFTheme Studio")
            return

        name = self._current_document.file_name or "Untitled"
        modified = "*" if self._current_document.is_modified() else ""
        self.setWindowTitle(f"{name}{modified} - VFTheme Studio")
```

**Testing:**
- Create new document: title shows "Untitled - VFTheme Studio"
- Make change: title shows "Untitled* - VFTheme Studio"
- Save document: title shows "my-theme.json - VFTheme Studio"
- Make change: title shows "my-theme.json* - VFTheme Studio"

**Evidence Required:**
- Screenshots of window title at each state
- Status bar showing correct document info

---

### Category 3: Token Browser Panel

#### Task 3.1: Create Token Tree Model
**Priority:** High
**Dependencies:** Task 2.1
**Estimated Time:** 4-5 hours

**Description:**
Create the QAbstractItemModel that provides hierarchical token data for the tree view.

**Files to Create/Modify:**
- `src/theme_studio/widgets/token_tree_model.py` - Tree model
- `src/theme_studio/widgets/token_tree_node.py` - Tree node data class
- `tests/test_token_tree_model.py` - Unit tests

**Acceptance Criteria:**
- [ ] Model implements QAbstractItemModel
- [ ] Root node contains 14 category nodes
- [ ] Each category contains token nodes
- [ ] All 197 tokens represented
- [ ] Each node has: name, value, category, modified status
- [ ] Model updates when document changes
- [ ] Color preview data provided via Qt.DecorationRole

**Implementation Notes:**
```python
# src/theme_studio/widgets/token_tree_model.py
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from vfwidgets_theme.tokens import ColorTokenRegistry, TokenCategory

class TokenTreeNode:
    """Node in token tree."""
    def __init__(self, name: str, value: str = None, is_category: bool = False):
        self.name = name
        self.value = value
        self.is_category = is_category
        self.children = []
        self.parent = None

class TokenTreeModel(QAbstractItemModel):
    """Hierarchical model for token browser."""

    def __init__(self, document: ThemeDocument):
        super().__init__()
        self._document = document
        self._root = self._build_tree()

        # Connect to document changes
        document.token_changed.connect(self._on_token_changed)

    def _build_tree(self) -> TokenTreeNode:
        """Build hierarchical tree from ColorTokenRegistry."""
        root = TokenTreeNode("Tokens")

        # Iterate through categories
        for category in TokenCategory:
            # Create category node
            category_node = TokenTreeNode(
                name=category.value.title(),
                is_category=True
            )
            category_node.parent = root
            root.children.append(category_node)

            # Get tokens for this category
            tokens = ColorTokenRegistry.get_tokens_by_category(category)

            # Create token nodes
            for token_def in tokens:
                token_node = TokenTreeNode(
                    name=token_def.name,
                    value=self._document.get_token(token_def.name),
                    is_category=False
                )
                token_node.parent = category_node
                category_node.children.append(token_node)

        return root

    def data(self, index: QModelIndex, role: int):
        """Provide data for view."""
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if node.is_category:
                count = len(node.children)
                return f"{node.name} ({count})"
            else:
                return node.name

        elif role == Qt.DecorationRole:
            if not node.is_category and node.value:
                # Return QColor for color preview
                from PySide6.QtGui import QColor
                return QColor(node.value)

        return None
```

**Testing:**
```python
def test_token_tree_structure():
    doc = ThemeDocument()
    model = TokenTreeModel(doc)

    # Root should have 14 categories
    assert model.rowCount(QModelIndex()) == 14

    # First category should have children
    cat_index = model.index(0, 0, QModelIndex())
    assert model.rowCount(cat_index) > 0

    # Check token display
    token_index = model.index(0, 0, cat_index)
    name = model.data(token_index, Qt.DisplayRole)
    assert name  # Should have a name
```

**Evidence Required:**
- Test output showing tree structure validation
- Print statement showing all 197 tokens loaded
- Demonstration of color preview data

---

#### Task 3.2: Create Token Browser UI
**Priority:** High
**Dependencies:** Task 3.1, Task 1.3
**Estimated Time:** 3-4 hours

**Description:**
Create the token browser panel UI with tree view, search bar, and filter controls.

**Files to Create/Modify:**
- `src/theme_studio/panels/token_browser.py` - Complete implementation
- `src/theme_studio/widgets/token_tree_view.py` - Custom tree view

**Acceptance Criteria:**
- [ ] Panel shows search bar at top
- [ ] Tree view displays all categories and tokens
- [ ] Category nodes expandable/collapsible
- [ ] Token nodes show color preview dot
- [ ] Single-click selects token
- [ ] Filter dropdown at bottom (All/Defined/Undefined)
- [ ] Token count label (e.g., "197 tokens")
- [ ] Search bar filters tree in real-time

**Implementation Notes:**
```python
# src/theme_studio/panels/token_browser.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeView, QLabel

class TokenBrowserPanel(QWidget):
    """Token browser panel with search and tree view."""

    token_selected = Signal(str)  # token_name

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("TOKEN BROWSER")
        layout.addWidget(title)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search tokens...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_bar)

        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.clicked.connect(self._on_token_clicked)
        layout.addWidget(self.tree_view)

        # Token count
        self.count_label = QLabel("197 tokens")
        layout.addWidget(self.count_label)

    def set_model(self, model: TokenTreeModel):
        """Set tree model."""
        self.tree_view.setModel(model)
        # Expand all categories by default
        self.tree_view.expandAll()

    def _on_token_clicked(self, index: QModelIndex):
        """Handle token selection."""
        node = index.internalPointer()
        if not node.is_category:
            self.token_selected.emit(node.name)
```

**Testing:**
- Launch app, verify tree shows all categories
- Expand/collapse categories
- Click token, verify signal emitted
- Type in search bar, verify filtering works

**Evidence Required:**
- Screenshot of full token browser
- Screenshot of expanded category showing tokens
- Video of search filtering in action
- Signal connection demonstration

---

#### Task 3.3: Implement Token Search/Filter
**Priority:** Medium
**Dependencies:** Task 3.2
**Estimated Time:** 2-3 hours

**Description:**
Implement real-time search filtering and filter dropdown functionality.

**Files to Create/Modify:**
- `src/theme_studio/panels/token_browser.py` - Add filtering logic
- `src/theme_studio/widgets/token_tree_model.py` - Add filter proxy model

**Acceptance Criteria:**
- [ ] Typing in search filters tree in real-time
- [ ] Search is case-insensitive
- [ ] Search matches token names and descriptions
- [ ] Filter dropdown with options: All, Defined, Undefined
- [ ] Changing filter updates tree view
- [ ] Token count updates with filter

**Implementation Notes:**
```python
from PySide6.QtCore import QSortFilterProxyModel

class TokenFilterProxyModel(QSortFilterProxyModel):
    """Proxy model for filtering tokens."""

    def __init__(self):
        super().__init__()
        self._search_text = ""
        self._filter_mode = "all"  # all, defined, undefined

    def set_search_text(self, text: str):
        self._search_text = text.lower()
        self.invalidateFilter()

    def set_filter_mode(self, mode: str):
        self._filter_mode = mode
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)
        node = index.internalPointer()

        # Always show categories
        if node.is_category:
            return True

        # Apply search filter
        if self._search_text:
            if self._search_text not in node.name.lower():
                return False

        # Apply mode filter
        if self._filter_mode == "defined":
            return bool(node.value)
        elif self._filter_mode == "undefined":
            return not node.value

        return True
```

**Testing:**
- Type "button" in search, verify only button tokens shown
- Select "Defined" filter, verify only tokens with values shown
- Select "Undefined" filter, verify only default tokens shown
- Clear search, verify all tokens shown again

**Evidence Required:**
- Video demonstrating each filter mode
- Screenshots of filtered results
- Token count changing with filters

---

### Category 4: Preview Canvas Panel

#### Task 4.1: Create Preview Canvas Widget
**Priority:** High
**Dependencies:** Task 1.3
**Estimated Time:** 3-4 hours

**Description:**
Create the preview canvas using QGraphicsView that will display themed widgets.

**Files to Create/Modify:**
- `src/theme_studio/panels/preview_canvas.py` - Complete implementation
- `src/theme_studio/widgets/preview_canvas_view.py` - QGraphicsView subclass

**Acceptance Criteria:**
- [ ] Panel shows title "PREVIEW CANVAS"
- [ ] Plugin selector dropdown (stub, shows "Generic Widgets")
- [ ] QGraphicsView with scene
- [ ] Placeholder content (e.g., "Preview will appear here")
- [ ] Basic zoom controls (toolbar integration comes later)

**Implementation Notes:**
```python
# src/theme_studio/panels/preview_canvas.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QGraphicsView, QGraphicsScene

class PreviewCanvasPanel(QWidget):
    """Preview canvas panel."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("PREVIEW CANVAS")
        layout.addWidget(title)

        # Plugin selector
        self.plugin_combo = QComboBox()
        self.plugin_combo.addItem("Generic Widgets")
        layout.addWidget(self.plugin_combo)

        # Canvas view
        self.canvas_view = QGraphicsView()
        self.canvas_scene = QGraphicsScene()
        self.canvas_view.setScene(self.canvas_scene)
        layout.addWidget(self.canvas_view)

        # Add placeholder text
        placeholder = self.canvas_scene.addText("Preview will appear here")
        placeholder.setDefaultTextColor(Qt.gray)
```

**Testing:**
- Canvas area visible and takes up most of panel
- Plugin selector shows "Generic Widgets"
- Placeholder text visible in center

**Evidence Required:**
- Screenshot of preview canvas panel
- Panel properly resizes with splitter

---

#### Task 4.2: Create Generic Widgets Plugin (Static)
**Priority:** High
**Dependencies:** Task 4.1, Task 2.2
**Estimated Time:** 5-6 hours

**Description:**
Create the GenericWidgetsPlugin that displays static sample Qt widgets with theme applied.

**Files to Create/Modify:**
- `src/theme_studio/preview/plugin_system.py` - PreviewPlugin base class
- `src/theme_studio/preview/generic_preview.py` - Generic widgets implementation

**Acceptance Criteria:**
- [ ] PreviewPlugin ABC defined with required methods
- [ ] GenericWidgetsPlugin creates sample widgets:
  - 3 QPushButtons (Primary, Secondary, Danger)
  - 1 QLineEdit
  - 1 QComboBox
  - 2 QRadioButtons
  - 1 QCheckBox
- [ ] Widgets wrapped in QWidget container
- [ ] Theme stylesheet applied to all widgets
- [ ] Container can be added to QGraphicsScene

**Implementation Notes:**
```python
# src/theme_studio/preview/plugin_system.py
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget
from vfwidgets_theme import Theme

class PreviewPlugin(ABC):
    """Base class for preview plugins."""

    @abstractmethod
    def name(self) -> str:
        """Plugin display name."""
        pass

    @abstractmethod
    def create_preview(self, theme: Theme) -> QWidget:
        """Create preview widget with theme applied."""
        pass

    @abstractmethod
    def get_relevant_tokens(self) -> list[str]:
        """Get list of tokens this plugin uses."""
        pass
```

```python
# src/theme_studio/preview/generic_preview.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QComboBox,
                               QCheckBox, QRadioButton, QGroupBox)
from vfwidgets_theme import Theme, StylesheetGenerator

class GenericWidgetsPlugin(PreviewPlugin):
    """Preview generic Qt widgets."""

    def name(self) -> str:
        return "Generic Widgets"

    def create_preview(self, theme: Theme) -> QWidget:
        """Create sample widget collection."""
        container = QWidget()
        layout = QVBoxLayout(container)

        # Buttons group
        btn_group = QGroupBox("Buttons")
        btn_layout = QHBoxLayout(btn_group)

        primary_btn = QPushButton("Primary")
        primary_btn.setProperty("variant", "primary")

        secondary_btn = QPushButton("Secondary")
        secondary_btn.setProperty("variant", "secondary")

        danger_btn = QPushButton("Danger")
        danger_btn.setProperty("variant", "danger")

        btn_layout.addWidget(primary_btn)
        btn_layout.addWidget(secondary_btn)
        btn_layout.addWidget(danger_btn)
        layout.addWidget(btn_group)

        # Inputs group
        input_group = QGroupBox("Inputs")
        input_layout = QVBoxLayout(input_group)

        line_edit = QLineEdit("Sample text input")
        input_layout.addWidget(line_edit)

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        input_layout.addWidget(combo)

        checkbox = QCheckBox("Checkbox option")
        input_layout.addWidget(checkbox)

        radio1 = QRadioButton("Radio option 1")
        radio1.setChecked(True)
        input_layout.addWidget(radio1)

        radio2 = QRadioButton("Radio option 2")
        input_layout.addWidget(radio2)

        layout.addWidget(input_group)

        # Apply theme stylesheet
        stylesheet = StylesheetGenerator.generate(theme)
        container.setStyleSheet(stylesheet)

        return container

    def get_relevant_tokens(self) -> list[str]:
        return [
            "button.background",
            "button.foreground",
            "button.hoverBackground",
            "button.border",
            "input.background",
            "input.foreground",
            "input.border",
            # ... more tokens
        ]
```

**Testing:**
- Create plugin instance
- Generate preview with default theme
- Verify all widgets visible
- Verify theme colors applied

**Evidence Required:**
- Screenshot of preview with default theme
- Screenshot of preview with custom theme
- Code showing stylesheet generation

---

#### Task 4.3: Integrate Plugin with Canvas
**Priority:** High
**Dependencies:** Task 4.2
**Estimated Time:** 2-3 hours

**Description:**
Connect the GenericWidgetsPlugin to the preview canvas, displaying widgets when document loads.

**Files to Create/Modify:**
- `src/theme_studio/panels/preview_canvas.py` - Add plugin integration

**Acceptance Criteria:**
- [ ] Canvas displays plugin preview when document loaded
- [ ] Preview updates when theme changes (document signal)
- [ ] Plugin preview properly sized to fit canvas
- [ ] Preview centered in canvas initially

**Implementation Notes:**
```python
class PreviewCanvasPanel(QWidget):
    def set_document(self, document: ThemeDocument):
        """Set theme document and update preview."""
        self._document = document

        # Connect to document changes
        document.token_changed.connect(self._update_preview)

        # Initial preview
        self._update_preview()

    def _update_preview(self):
        """Update preview with current theme."""
        # Clear scene
        self.canvas_scene.clear()

        # Create plugin preview
        plugin = GenericWidgetsPlugin()
        preview_widget = plugin.create_preview(self._document._theme)

        # Add to scene
        proxy = self.canvas_scene.addWidget(preview_widget)

        # Center in view
        self.canvas_view.centerOn(proxy)
```

**Testing:**
- Open theme file
- Verify preview appears with themed widgets
- (Future: Change token value, verify preview updates)

**Evidence Required:**
- Screenshot of preview displaying themed widgets
- Preview properly centered in canvas
- Different themes showing different colors

---

### Category 5: Inspector Panel

#### Task 5.1: Create Inspector Panel UI (Read-Only)
**Priority:** Medium
**Dependencies:** Task 1.3
**Estimated Time:** 3-4 hours

**Description:**
Create the inspector panel that displays selected token information in read-only mode.

**Files to Create/Modify:**
- `src/theme_studio/panels/inspector.py` - Complete implementation

**Acceptance Criteria:**
- [ ] Panel shows title "INSPECTOR"
- [ ] Shows selected token name
- [ ] Shows token category and type
- [ ] Shows token value (read-only)
- [ ] Shows color preview swatch (for color tokens)
- [ ] Shows RGB/HSL conversions (read-only)
- [ ] Placeholder when no token selected

**Implementation Notes:**
```python
# src/theme_studio/panels/inspector.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QLineEdit
from PySide6.QtCore import Signal

class InspectorPanel(QWidget):
    """Inspector panel for token details."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._show_placeholder()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("INSPECTOR")
        layout.addWidget(title)

        # Token info group
        self.info_group = QGroupBox("Selected Token")
        info_layout = QVBoxLayout(self.info_group)

        self.token_name_label = QLabel("No token selected")
        info_layout.addWidget(self.token_name_label)

        self.category_label = QLabel("")
        info_layout.addWidget(self.category_label)

        self.type_label = QLabel("")
        info_layout.addWidget(self.type_label)

        layout.addWidget(self.info_group)

        # Value group
        self.value_group = QGroupBox("Value")
        value_layout = QVBoxLayout(self.value_group)

        self.value_display = QLineEdit()
        self.value_display.setReadOnly(True)  # Read-only for Phase 1
        value_layout.addWidget(self.value_display)

        # Color preview (will be hidden for non-color tokens)
        self.color_preview = QLabel("Color: ")
        self.color_preview.setStyleSheet("padding: 10px; border: 1px solid gray;")
        value_layout.addWidget(self.color_preview)

        layout.addWidget(self.value_group)

        layout.addStretch()

    def show_token(self, token_name: str, token_value: str):
        """Display token information."""
        self.token_name_label.setText(token_name)

        # Parse category from token name
        parts = token_name.split('.')
        category = parts[0] if parts else "Unknown"
        self.category_label.setText(f"Category: {category.title()}")
        self.type_label.setText("Type: Color")

        # Show value
        self.value_display.setText(token_value or "(using default)")

        # Update color preview
        if token_value:
            self.color_preview.setStyleSheet(
                f"background-color: {token_value}; "
                f"padding: 10px; border: 1px solid gray;"
            )
        else:
            self.color_preview.setStyleSheet("padding: 10px; border: 1px solid gray;")

    def _show_placeholder(self):
        """Show placeholder when no token selected."""
        self.token_name_label.setText("No token selected")
        self.category_label.setText("")
        self.type_label.setText("")
        self.value_display.setText("")
        self.color_preview.setStyleSheet("padding: 10px; border: 1px solid gray;")
```

**Testing:**
- Launch app with no selection: placeholder shown
- Click token in browser: inspector shows token info
- Select color token: color preview swatch displays correct color

**Evidence Required:**
- Screenshot of inspector with no selection
- Screenshot of inspector showing selected token
- Color preview swatch demonstration

---

#### Task 5.2: Connect Inspector to Token Browser
**Priority:** Medium
**Dependencies:** Task 5.1, Task 3.2
**Estimated Time:** 1-2 hours

**Description:**
Connect token browser selection to inspector display.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Connect signals

**Acceptance Criteria:**
- [ ] Clicking token in browser updates inspector
- [ ] Inspector shows correct token name, category, value
- [ ] Color preview updates with token color
- [ ] No errors when clicking category nodes

**Implementation Notes:**
```python
class ThemeStudioWindow(QMainWindow):
    def _connect_signals(self):
        """Connect panel signals."""
        # Token browser -> Inspector
        self.token_browser.token_selected.connect(self._on_token_selected)

    def _on_token_selected(self, token_name: str):
        """Handle token selection."""
        if not self._current_document:
            return

        # Get token value
        token_value = self._current_document.get_token(token_name)

        # Update inspector
        self.inspector_panel.show_token(token_name, token_value)
```

**Testing:**
- Click various tokens in browser
- Verify inspector updates each time
- Test with tokens that have values and defaults

**Evidence Required:**
- Video showing click -> inspector update
- Multiple tokens selected showing different values

---

### Category 6: File Operations

#### Task 6.1: Implement File > New
**Priority:** High
**Dependencies:** Task 2.2
**Estimated Time:** 2-3 hours

**Description:**
Implement New Theme action that creates a blank theme document.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Add new_theme() method
- `src/theme_studio/components/menubar.py` - Connect action

**Acceptance Criteria:**
- [ ] File > New creates new ThemeDocument
- [ ] New document has default theme
- [ ] Window title shows "Untitled - VFTheme Studio"
- [ ] Token browser updates with new document
- [ ] Preview updates with default theme
- [ ] If current document modified, prompt to save first

**Implementation Notes:**
```python
def new_theme(self):
    """Create new theme."""
    # Check if current document needs saving
    if self._current_document and self._current_document.is_modified():
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "Save changes to current theme?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_theme()
        elif reply == QMessageBox.Cancel:
            return

    # Create new document
    theme = Theme.create_default()
    document = ThemeDocument(theme)

    # Set as current
    self.set_document(document)

    self.statusBar().showMessage("New theme created", 3000)
```

**Testing:**
- Click File > New
- Verify new document created
- Verify token browser shows default tokens
- Verify preview shows default colors
- Test "unsaved changes" prompt

**Evidence Required:**
- Screenshot of new theme
- Video of unsaved changes prompt
- Window title showing "Untitled"

---

#### Task 6.2: Implement File > Open
**Priority:** High
**Dependencies:** Task 2.2
**Estimated Time:** 3-4 hours

**Description:**
Implement Open Theme action with file dialog.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Add open_theme() method

**Acceptance Criteria:**
- [ ] File > Open shows file dialog
- [ ] Dialog filters for .json files
- [ ] Can browse to theme file
- [ ] Opens and loads theme successfully
- [ ] Window title shows filename
- [ ] Token browser updates with loaded tokens
- [ ] Preview updates with loaded theme
- [ ] Status bar shows "Theme loaded" message
- [ ] If current document modified, prompt to save first

**Implementation Notes:**
```python
def open_theme(self):
    """Open existing theme."""
    # Check if current document needs saving
    if self._current_document and self._current_document.is_modified():
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "Save changes to current theme?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_theme()
        elif reply == QMessageBox.Cancel:
            return

    # Show file dialog
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Open Theme",
        "",
        "VFWidgets Theme (*.json);;All Files (*)"
    )

    if not file_path:
        return

    try:
        # Load theme
        document = ThemeDocument()
        document.load(file_path)

        # Set as current
        self.set_document(document)

        self.statusBar().showMessage(f"Loaded: {file_path}", 3000)

    except Exception as e:
        QMessageBox.critical(
            self,
            "Error Loading Theme",
            f"Failed to load theme:\n{str(e)}"
        )
```

**Testing:**
- Click File > Open
- Browse to existing theme JSON
- Verify theme loads successfully
- Check token browser shows loaded values
- Check preview shows loaded colors
- Test error handling with invalid file

**Evidence Required:**
- Video of open process
- Screenshot of loaded theme
- Screenshot of error dialog for invalid file

---

#### Task 6.3: Implement File > Save / Save As
**Priority:** High
**Dependencies:** Task 2.2
**Estimated Time:** 3-4 hours

**Description:**
Implement Save and Save As actions.

**Files to Create/Modify:**
- `src/theme_studio/window.py` - Add save_theme() and save_theme_as() methods

**Acceptance Criteria:**
- [ ] File > Save saves to current file path
- [ ] If no file path, prompts for Save As
- [ ] File > Save As always prompts for path
- [ ] Save dialog defaults to .json extension
- [ ] Theme saved successfully
- [ ] Window title removes "*" (modified indicator)
- [ ] Status bar shows "Theme saved" message
- [ ] Error handling for save failures

**Implementation Notes:**
```python
def save_theme(self):
    """Save current theme."""
    if not self._current_document:
        return

    # If no file path, do Save As
    if not self._current_document.file_path:
        return self.save_theme_as()

    try:
        self._current_document.save()
        self.statusBar().showMessage("Theme saved", 3000)
    except Exception as e:
        QMessageBox.critical(
            self,
            "Error Saving Theme",
            f"Failed to save theme:\n{str(e)}"
        )

def save_theme_as(self):
    """Save theme with new filename."""
    if not self._current_document:
        return

    # Show save dialog
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Theme As",
        "",
        "VFWidgets Theme (*.json);;All Files (*)"
    )

    if not file_path:
        return

    # Ensure .json extension
    if not file_path.endswith('.json'):
        file_path += '.json'

    try:
        self._current_document.save(file_path)
        self.statusBar().showMessage(f"Saved: {file_path}", 3000)
    except Exception as e:
        QMessageBox.critical(
            self,
            "Error Saving Theme",
            f"Failed to save theme:\n{str(e)}"
        )
```

**Testing:**
- Create new theme
- Click File > Save (should prompt for path)
- Save as "test-theme.json"
- Verify file created on disk
- Verify window title shows "test-theme.json"
- Make change, save again (no prompt)
- Test Save As with existing theme

**Evidence Required:**
- Video of save process
- Terminal output showing file created
- Window title update demonstration
- Saved JSON file contents

---

### Category 7: Integration & Testing

#### Task 7.1: End-to-End Integration Test
**Priority:** Critical
**Dependencies:** All previous tasks
**Estimated Time:** 2-3 hours

**Description:**
Test complete workflow from launch to save.

**Acceptance Criteria:**
- [ ] Launch application successfully
- [ ] Create new theme
- [ ] Browse all token categories
- [ ] Select various tokens, inspector updates
- [ ] Preview shows widgets with theme
- [ ] Save theme to file
- [ ] Close application
- [ ] Reopen application
- [ ] Open saved theme
- [ ] Verify all data preserved

**Test Script:**
```bash
# 1. Launch
python -m theme_studio

# 2. Create new theme
# Click File > New

# 3. Browse tokens
# Expand "colors" category
# Expand "button" category
# Click "button.background" token

# 4. Verify inspector
# Should show: button.background, Category: Button, Type: Color

# 5. Verify preview
# Should show buttons, inputs with default theme

# 6. Save theme
# Click File > Save As
# Save as "test-phase1.json"

# 7. Close app
# Click File > Exit

# 8. Reopen app
python -m theme_studio

# 9. Open theme
# Click File > Open
# Open "test-phase1.json"

# 10. Verify loaded
# Token browser shows tokens
# Preview shows widgets
```

**Evidence Required:**
- Video of complete workflow
- Screenshots at each major step
- Saved theme JSON file
- Terminal output showing clean execution

---

#### Task 7.2: Create Phase 1 Demo
**Priority:** Medium
**Dependencies:** Task 7.1
**Estimated Time:** 1-2 hours

**Description:**
Create demo script and documentation showing Phase 1 capabilities.

**Files to Create:**
- `apps/theme-studio/wip/phase1-demo-SCRIPT.md` - Demo walkthrough
- `apps/theme-studio/wip/phase1-COMPLETE.md` - Completion report

**Acceptance Criteria:**
- [ ] Demo script covers all Phase 1 features
- [ ] Screenshots of each feature included
- [ ] Known limitations documented
- [ ] Phase 2 preview included

**Demo Script Outline:**
```markdown
# Phase 1 Demo Script

## 1. Application Launch
- Show clean startup
- Show window with three panels

## 2. Token Browser
- Show 14 categories
- Expand categories
- Show 197 total tokens
- Demonstrate search

## 3. Preview Canvas
- Show generic widgets preview
- Show theme colors applied

## 4. Inspector
- Select token
- Show token details
- Show color preview

## 5. File Operations
- New theme
- Save theme
- Close and reopen
- Open saved theme

## Known Limitations
- Tokens are read-only (editing in Phase 2)
- Single plugin only (more in Phase 3)
- No undo/redo yet (Phase 2)
- No accessibility validation (Phase 7)
```

**Evidence Required:**
- Complete demo script document
- All screenshots captured
- Phase 1 completion report

---

## Task Summary

### Critical Path Tasks (Must Complete)
1. Task 1.1: Application Entry Point
2. Task 1.2: Main Window Structure
3. Task 1.3: Three-Panel Layout
4. Task 2.1: Theme Document Model
5. Task 2.2: Integrate Document with Window
6. Task 3.1: Token Tree Model
7. Task 3.2: Token Browser UI
8. Task 4.2: Generic Widgets Plugin
9. Task 4.3: Integrate Plugin with Canvas
10. Task 6.1: File > New
11. Task 6.2: File > Open
12. Task 6.3: File > Save/Save As
13. Task 7.1: End-to-End Integration Test

### Total Estimated Time
- Critical tasks: ~40-50 hours
- Medium priority: ~10-15 hours
- **Total: 50-65 hours (~1.5-2 weeks with full-time work)**

### Success Metrics
- ✅ Application launches without errors
- ✅ All 197 tokens visible in browser
- ✅ Preview shows themed widgets
- ✅ Can save/load theme files
- ✅ No crashes during normal operation

---

## Next Steps After Phase 1

### Phase 2 Preview (Interactive Editing)
Once Phase 1 is complete, Phase 2 will add:
- Token editing (color picker, value input)
- Live preview updates on change
- Undo/redo system
- Modified token tracking

### Handoff to Phase 2
Upon completion, create:
- `phase1-COMPLETE.md` - Completion report
- `phase2-tasks-IMPLEMENTATION.md` - Next phase tasks
- Update main SPECIFICATION.md with any design changes discovered

---

**Document Status:** Ready for Implementation
**Last Updated:** October 2025
**Next Review:** After Task 1.3 completion
