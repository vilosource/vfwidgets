# Theme-Studio Font Editing Integration Plan (CORRECTED)

## Overview
Add font token editing to Theme-Studio using **proper MVC architecture** that **exactly mirrors** the color token implementation. This plan has been corrected after a comprehensive architectural audit to ensure true 1:1 parity with the color system.

## Design Philosophy

**No shortcuts. No compromises. Perfect architectural symmetry.**

The font token system MUST match the color token system in EVERY architectural aspect:
- FontTokenMetadataRegistry with full metadata (like ColorTokenRegistry)
- FontTreeModel using QAbstractItemModel (like TokenTreeModel)
- FontFilterProxyModel for search/filtering (like TokenFilterProxyModel)
- Font visual indicators (like color swatches)
- Widget filtering feature (show only current widget's fonts)
- Complete status bar integration
- Hierarchical category organization

## Architectural Audit Results

**Audit Findings:** The original plan had 5 critical gaps:
1. ❌ Missing QSortFilterProxyModel layer (colors use 3-layer architecture)
2. ❌ Wrong column count (colors use 1 column, plan had 2)
3. ❌ Missing helper methods (get_token_path, get_token_value)
4. ❌ Missing widget filter feature (checkbox to filter by current widget)
5. ⚠️ Registry naming conflict (FontTokenRegistry already exists for runtime resolution)

**All issues have been corrected in this revised plan.**

## Architecture Summary

### Current State
- Theme-Studio has `TokenBrowserPanel` showing 197 color tokens
- Colors use **3-layer architecture**: TokenTreeModel → TokenFilterProxyModel → QTreeView
- `ColorTokenRegistry` provides metadata (descriptions, defaults, validation)
- Widget library has `FontTokenRegistry` for **runtime resolution** (not metadata!)
- JSON themes already support fonts (lines 126-137 in dark-default.json)
- Inspector panel only handles color editing

### Target State
- **Left panel**: `QTabWidget` with "Colors" and "Fonts" tabs
- **Font browser**: Uses **3-layer architecture**: FontTreeModel → FontFilterProxyModel → QTreeView
- **Font metadata**: `FontTokenMetadataRegistry` (separate from runtime FontTokenRegistry)
- **Font filtering**: Search + widget filter (show only current widget's fonts)
- **Inspector**: Automatically shows appropriate editor (color/font)
- **Status bar**: Shows both color AND font token counts
- **Full round-trip**: load JSON → edit fonts → save JSON

### Architecture Diagram

```
Color Tokens:                          Font Tokens (MUST MATCH):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ColorTokenRegistry                     FontTokenMetadataRegistry
(metadata for editing)                 (metadata for editing)
         ↓                                      ↓
TokenTreeModel                         FontTreeModel
(QAbstractItemModel)                   (QAbstractItemModel)
         ↓                                      ↓
TokenFilterProxyModel                  FontFilterProxyModel
(QSortFilterProxyModel)                (QSortFilterProxyModel)
         ↓                                      ↓
TokenBrowserPanel                      FontBrowserPanel
(QTreeView + search + filter)          (QTreeView + search + filter)
```

## Implementation Phases

See the full plan in the file for all 10 phases with complete code examples.

### Summary of Changes Required:

**NEW FILES (5):**
1. Phase 0: `metadata/font_token_metadata.py` (~450 lines) - Metadata registry
2. Phase 1: `widgets/font_tree_model.py` (~400 lines) - QAbstractItemModel
3. Phase 2: `widgets/font_filter_proxy_model.py` (~100 lines) - QSortFilterProxyModel
4. Phase 3: `panels/font_browser.py` (~280 lines) - View with search/filter
5. Phase 4: `commands/font_commands.py` (~50 lines) - Undo/redo command

**MODIFIED FILES (4):**
1. Phase 8: `components/status_bar.py` (+30 lines) - Add font count
2. Phase 9: `window.py` (+40 lines) - Tab integration + widget filtering
3. Phases 5-7: Already complete (ThemeDocument, ThemeController, Inspector)

**Total:** ~1,350 new lines across 13 files

## Architectural Guarantees - 100% Parity

| Aspect | Colors | Fonts | Status |
|--------|--------|-------|--------|
| Metadata Registry | ColorTokenRegistry | FontTokenMetadataRegistry | ✅ |
| Model | TokenTreeModel | FontTreeModel | ✅ |
| Proxy Model | TokenFilterProxyModel | FontFilterProxyModel | ✅ |
| View | TokenBrowserPanel | FontBrowserPanel | ✅ |
| Column Count | 1 | 1 | ✅ |
| Helper Methods | get_token_name, get_token_value | get_token_path, get_token_value | ✅ |
| Search filtering | ✅ | ✅ | ✅ |
| Widget filtering | set_current_widget_tokens | set_current_widget_tokens | ✅ |
| Status bar | update_token_count | update_font_count | ✅ |
| Visual indicators | Color swatches | Font icons | ✅ |
| Tooltips | From ColorToken | From FontTokenInfo | ✅ |
| Validation | validate_color | validate_value | ✅ |

---

# DETAILED IMPLEMENTATION

## Phase 0: Create Metadata Registry (NEW FILE)

**File**: `apps/theme-studio/src/theme_studio/metadata/font_token_metadata.py`
**Lines**: ~450 lines
**Priority**: CRITICAL - Foundation

```python
"""Font Token Metadata Registry - Metadata System for Theme-Studio Font Editing.

This registry provides METADATA for font tokens (descriptions, defaults, validation)
for use by theme-studio's editing interface.

This is SEPARATE from vfwidgets_theme.core.font_tokens.FontTokenRegistry, which
provides RUNTIME RESOLUTION (hierarchical fallback chains) for widgets.

Two registries, two purposes:
- FontTokenMetadataRegistry (here): Editing metadata for theme-studio
- FontTokenRegistry (widget lib): Runtime resolution for widgets
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union


class FontTokenCategory(Enum):
    """Font token categories for organization."""
    BASE_FONTS = "base_fonts"
    TERMINAL = "terminal"
    EDITOR = "editor"
    TABS = "tabs"
    UI = "ui"


@dataclass(frozen=True)
class FontTokenInfo:
    """Metadata about a single font token.

    Exactly mirrors ColorToken structure.
    """
    path: str
    category: FontTokenCategory
    description: str
    default_value: Union[list[str], int, float, None]
    value_type: type
    required: bool = False
    unit: str = ""
    min_value: Union[int, float, None] = None
    max_value: Union[int, float, None] = None


class FontTokenMetadataRegistry:
    """Registry of font token metadata for theme-studio editing."""

    BASE_FONTS: list[FontTokenInfo] = [
        FontTokenInfo(
            path="fonts.mono",
            category=FontTokenCategory.BASE_FONTS,
            description="Monospace font family list (fallback chain for code/terminal)",
            default_value=["'Cascadia Code'", "Consolas", "'Courier New'", "monospace"],
            value_type=list,
        ),
        # ... (7 tokens total, see full code in plan)
    ]

    TERMINAL_FONTS: list[FontTokenInfo] = [...]  # 5 tokens
    EDITOR_FONTS: list[FontTokenInfo] = [...]    # 4 tokens
    TABS_FONTS: list[FontTokenInfo] = [...]      # 3 tokens
    UI_FONTS: list[FontTokenInfo] = [...]        # 3 tokens

    _all_tokens: list[FontTokenInfo] = (
        BASE_FONTS + TERMINAL_FONTS + EDITOR_FONTS + TABS_FONTS + UI_FONTS
    )

    @classmethod
    def get_all_tokens(cls) -> list[FontTokenInfo]:
        """Get all 22 font tokens."""
        return cls._all_tokens.copy()

    @classmethod
    def get_tokens_by_category(cls, category: FontTokenCategory) -> list[FontTokenInfo]:
        """Get tokens in specific category."""
        return [t for t in cls._all_tokens if t.category == category]

    @classmethod
    def get_token(cls, path: str) -> FontTokenInfo | None:
        """Get token metadata by path."""
        for token in cls._all_tokens:
            if token.path == path:
                return token
        return None

    @classmethod
    def validate_value(cls, path: str, value) -> tuple[bool, str]:
        """Validate font token value."""
        # Returns (is_valid, error_message)
        # See full implementation in plan

    @classmethod
    def get_display_name(cls, path: str) -> str:
        """Get human-readable name (e.g., 'terminal.fontSize' → 'Font Size')."""
        # See full implementation in plan
```

---

## Phase 1: Create Font Tree Model (NEW FILE)

**File**: `apps/theme-studio/src/theme_studio/widgets/font_tree_model.py`
**Lines**: ~400 lines
**Priority**: CRITICAL

**Key Points:**
- **Single column** (columnCount returns 1)
- Has helper methods: `get_token_path()`, `get_token_value()`
- Uses FontTokenMetadataRegistry
- Mirrors TokenTreeModel exactly

```python
"""Font Tree Model - QAbstractItemModel for hierarchical font token display."""

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QIcon

from ..metadata.font_token_metadata import FontTokenMetadataRegistry, FontTokenCategory
from ..models import ThemeDocument


class FontTreeNode:
    """Node in font tree (mirrors TokenTreeNode)."""
    def __init__(self, name: str, path: str = None, value = None,
                 is_category: bool = False, category: FontTokenCategory = None):
        self.name = name
        self.path = path
        self.value = value
        self.is_category = is_category
        self.category = category
        self.children = []
        self.parent = None


class FontTreeModel(QAbstractItemModel):
    """Hierarchical model for font tokens."""

    def __init__(self, document: ThemeDocument, parent=None):
        super().__init__(parent)
        self._document = document
        self._root = self._build_tree()
        document.font_changed.connect(self._on_font_changed)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1  # CRITICAL: Single column!

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if node.is_category:
                return f"{node.name} ({len(node.children)})"
            else:
                return node.name  # Just name, no value column

        elif role == Qt.DecorationRole:
            # Font icons (like color swatches)
            if node.is_category:
                return QIcon.fromTheme("folder")
            elif "Family" in node.path:
                return QIcon.fromTheme("font")
            elif "Size" in node.path:
                return QIcon.fromTheme("format-font-size-more")
            # ... more icons

        elif role == Qt.ToolTipRole:
            # Show metadata in tooltip
            # See full implementation

    # CRITICAL: Helper methods
    def get_token_path(self, index: QModelIndex) -> str | None:
        """Get token path from index."""
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.path if not node.is_category else None

    def get_token_value(self, index: QModelIndex):
        """Get token value from index."""
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.value if not node.is_category else None

    # ... (standard QAbstractItemModel methods)
```

---

## Phase 2: Create Font Filter Proxy Model (NEW FILE)

**File**: `apps/theme-studio/src/theme_studio/widgets/font_filter_proxy_model.py`
**Lines**: ~100 lines
**Priority**: CRITICAL - Enables search/filtering

```python
"""Font Filter Proxy Model - Filtering for font token tree."""

from PySide6.QtCore import QModelIndex, QSortFilterProxyModel


class FontFilterProxyModel(QSortFilterProxyModel):
    """Custom proxy for search and widget filtering.

    Mirrors TokenFilterProxyModel exactly.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._allowed_token_paths = None  # None = show all
        self._source_model = None

    def setSourceModel(self, model):
        self._source_model = model
        super().setSourceModel(model)

    def set_allowed_token_paths(self, token_paths: set[str] | None):
        """Set which tokens to show (for widget filtering)."""
        self._allowed_token_paths = token_paths
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Filter by token paths and search text."""
        if not self._source_model:
            return True

        index = self._source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        token_path = self._source_model.get_token_path(index)

        if not token_path:
            # Category - use recursive filtering
            return super().filterAcceptsRow(source_row, source_parent)

        # Token node - check allowed paths
        if self._allowed_token_paths is not None:
            if token_path not in self._allowed_token_paths:
                return False

        # Apply text filter
        return super().filterAcceptsRow(source_row, source_parent)
```

---

## Phase 3: Create Font Browser Panel (NEW FILE)

**File**: `apps/theme-studio/src/theme_studio/panels/font_browser.py`
**Lines**: ~280 lines
**Priority**: HIGH

```python
"""Font Browser Panel - View with search and widget filtering."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QLineEdit, QTreeView, QVBoxLayout, QWidget

from ..models import ThemeDocument
from ..widgets.font_tree_model import FontTreeModel
from ..widgets.font_filter_proxy_model import FontFilterProxyModel


class FontBrowserPanel(QWidget):
    """Font token browser (mirrors TokenBrowserPanel)."""

    font_token_selected = Signal(str)
    font_token_edit_requested = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._proxy_model = None  # CRITICAL
        self._current_widget_tokens = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search font tokens...")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # Widget filter checkbox (CRITICAL - was missing!)
        self.widget_filter_checkbox = QCheckBox("Show only current widget fonts")
        self.widget_filter_checkbox.stateChanged.connect(self._on_widget_filter_changed)
        self.widget_filter_checkbox.setEnabled(False)
        layout.addWidget(self.widget_filter_checkbox)

        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)  # Single column
        self.tree_view.setAlternatingRowColors(True)
        layout.addWidget(self.tree_view)

    def set_document(self, document: ThemeDocument):
        # Create model
        self._model = FontTreeModel(document, self)

        # Create proxy (CRITICAL - 3-layer architecture!)
        self._proxy_model = FontFilterProxyModel()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setRecursiveFilteringEnabled(True)
        self._proxy_model.setFilterRole(Qt.DisplayRole)

        # Set proxy on view
        self.tree_view.setModel(self._proxy_model)
        self.tree_view.expandAll()

        # Connect signals
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.tree_view.doubleClicked.connect(self._on_double_clicked)

    def set_current_widget_tokens(self, token_paths: set[str] | None):
        """Enable widget filtering (CRITICAL - was missing!)."""
        self._current_widget_tokens = token_paths
        self.widget_filter_checkbox.setEnabled(token_paths is not None)

        if token_paths:
            count = len(token_paths)
            self.widget_filter_checkbox.setText(f"Show only current widget fonts ({count})")
        else:
            self.widget_filter_checkbox.setText("Show only current widget fonts")
            self.widget_filter_checkbox.setChecked(False)

    def _on_search_changed(self, text: str):
        if self._proxy_model:
            self._proxy_model.setFilterWildcard(f"*{text}*")
            if text:
                self.tree_view.expandAll()

    def _on_widget_filter_changed(self, state: int):
        if not self._proxy_model:
            return

        if self.widget_filter_checkbox.isChecked() and self._current_widget_tokens:
            self._proxy_model.set_allowed_token_paths(self._current_widget_tokens)
            self.tree_view.expandAll()
        else:
            self._proxy_model.set_allowed_token_paths(None)
            self.tree_view.expandAll()

    # ... (signal handlers)
```

---

## Phases 4-10: Summary

**Phase 4**: SetFontCommand (undo/redo) - 50 lines
**Phases 5-7**: Already complete (ThemeDocument, Controller, Inspector)
**Phase 8**: Status bar (+30 lines) - Add font count display
**Phase 9**: Window integration (+40 lines) - Wire up tabs + widget filtering
**Phase 10**: Module exports - Update __init__.py files

---

## Critical Corrections Summary

✅ **Fixed 5 critical issues:**

1. Added FontFilterProxyModel (Phase 2) - 3-layer architecture
2. Changed FontTreeModel to 1 column (not 2)
3. Added helper methods: get_token_path(), get_token_value()
4. Added widget filter checkbox + set_current_widget_tokens()
5. Renamed to FontTokenMetadataRegistry (avoid naming conflict)

**Result**: 100% architectural parity with color token system.

---

## This Is The Way

**No shortcuts. No compromises. Perfect architectural symmetry.**

Every aspect of the font system now **exactly matches** the color system:
- ✅ 3-layer architecture (model → proxy → view)
- ✅ Single column display
- ✅ Helper methods
- ✅ Widget filtering
- ✅ Complete metadata
- ✅ Proper naming

**The codebase will be professional, maintainable, and architecturally pure.**
