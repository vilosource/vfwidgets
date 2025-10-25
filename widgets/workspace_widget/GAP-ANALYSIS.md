# VFWidgets Workspace Widget - Gap Analysis

**Date:** 2025-10-24
**Status:** Pre-Implementation Review
**Reviewed Documents:** SPECIFICATION.md (3,910 lines), DESIGN.md (1,573 lines)

## Purpose

Systematic analysis of gaps, inconsistencies, and missing information between SPECIFICATION.md and DESIGN.md before starting implementation.

---

## Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Missing Implementation Details | 3 | 5 | 4 | 2 | 14 |
| Inconsistencies | 0 | 2 | 3 | 1 | 6 |
| Missing Specifications | 1 | 3 | 2 | 0 | 6 |
| Clarifications Needed | 0 | 4 | 6 | 3 | 13 |
| **TOTAL** | **4** | **14** | **15** | **6** | **39** |

**Overall Assessment:** Documents are ~85% complete. Most gaps are medium/low priority clarifications. 4 critical items must be addressed before implementation.

---

## Critical Gaps (Must Fix Before Implementation)

### 1. ❌ CRITICAL: `WorkspaceWidget.__init__()` Signature Incomplete in DESIGN

**Issue:** DESIGN.md shows `def __init__(self, ...):` but doesn't specify the complete parameter list with all extension point handlers.

**In SPECIFICATION.md (lines 2652-2676):**
```python
def __init__(
    self,
    file_extensions: Optional[list[str]] = None,
    excluded_folders: Optional[list[str]] = None,
    filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
    config_class: type = WorkspaceConfig,
    config_filename: str = ".workspace.json",
    session_dir: Optional[Path] = None,
    parent: Optional[QWidget] = None
):
```

**Missing in DESIGN.md (lines 127-129):**
- `conflict_handler` parameter
- `error_handler` parameter
- `icon_provider` parameter
- `workspace_validator` parameter
- `context_menu_provider` parameter
- `lifecycle_hooks` parameter

**Impact:** Developers won't know the complete constructor signature.

**Fix Required:** Update DESIGN.md Initialization Sequence section (line 128) with full signature:
```python
def __init__(
    self,
    file_extensions: Optional[list[str]] = None,
    excluded_folders: Optional[list[str]] = None,
    filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None,
    config_class: type = WorkspaceConfig,
    config_filename: str = ".workspace.json",
    session_dir: Optional[Path] = None,
    conflict_handler: Optional[FileConflictHandler] = None,
    error_handler: Optional[ErrorHandler] = None,
    icon_provider: Optional[IconProvider] = None,
    workspace_validator: Optional[WorkspaceValidator] = None,
    context_menu_provider: Optional[ContextMenuProvider] = None,
    lifecycle_hooks: Optional[WorkspaceLifecycleHooks] = None,
    parent: Optional[QWidget] = None
):
```

---

### 2. ❌ CRITICAL: Missing Implementation for `FileExplorerWidget`

**Issue:** DESIGN.md mentions FileExplorerWidget but provides NO implementation details.

**What's Missing:**
- How to integrate ThemedWidget mixin
- How to create and configure QTreeView
- How to handle selection signals
- How to implement context menu
- How to track expanded/collapsed state for icons

**In DESIGN.md:** Only mentions it in architecture diagram and Phase 4 checklist.

**In SPECIFICATION.md:** No internal details (correctly, it's implementation).

**Impact:** Developers won't know how to build the view component.

**Fix Required:** Add new section to DESIGN.md:

```markdown
### FileExplorerWidget Implementation

#### Class Structure
```python
# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

# Conditional base class
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class FileExplorerWidget(_BaseClass):
    # Theme configuration
    theme_config = {
        "background": "sideBar.background",
        "foreground": "sideBar.foreground",
        # ... (from workspace-theme-integration-DESIGN.md)
    }

    # Signals
    file_selected = Signal(str)
    file_double_clicked = Signal(str)
    folder_expanded = Signal(str, str)
    folder_collapsed = Signal(str, str)
    context_menu_requested = Signal(QPoint, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Create tree view
        self._tree_view = QTreeView(self)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setUniformRowHeights(True)
        self._tree_view.setAnimated(False)  # Performance

        # Signals
        self._tree_view.clicked.connect(self._on_clicked)
        self._tree_view.doubleClicked.connect(self._on_double_clicked)
        self._tree_view.expanded.connect(self._on_expanded)
        self._tree_view.collapsed.connect(self._on_collapsed)
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree_view.customContextMenuRequested.connect(self._on_context_menu)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tree_view)

    def set_model(self, model: QAbstractItemModel):
        self._tree_view.setModel(model)

    def _on_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        # Get file path from model
        file_info = index.data(Qt.ItemDataRole.UserRole)
        if file_info and not file_info.is_dir:
            self.file_selected.emit(file_info.absolute_path)

    # ... etc
```
\`\`\`

---

### 3. ❌ CRITICAL: Missing `WorkspaceManager` Implementation Details

**Issue:** DESIGN.md mentions WorkspaceManager in architecture but provides NO implementation.

**What's Missing:**
- How to load/save config JSON
- How to load/save session JSON
- How to manage folder list
- How to compute session hash
- How to handle config versioning
- How to detect config file changes

**In DESIGN.md:** Only Phase 3 checklist items, no implementation guidance.

**Impact:** Developers won't know how to implement config/session persistence.

**Fix Required:** Add section to DESIGN.md after MultiRootFileSystemModel:

```markdown
## WorkspaceManager Implementation

### Responsibilities
- Load/save workspace configuration (`.workspace.json`)
- Load/save UI session state (`~/.config/app/workspaces/sessions/<hash>.json`)
- Manage workspace folder list
- Watch config file for external changes
- Provide workspace lifecycle methods

### Class Structure
```python
class WorkspaceManager(QObject):
    # Signals
    workspace_opened = Signal(list)  # list[WorkspaceFolder]
    workspace_closed = Signal()
    folder_added = Signal(object)  # WorkspaceFolder
    folder_removed = Signal(str)
    config_changed = Signal()  # External config file changed

    def __init__(
        self,
        config_class: type = WorkspaceConfig,
        config_filename: str = ".workspace.json",
        session_dir: Optional[Path] = None,
        error_handler: Optional[ErrorHandler] = None,
        validator: Optional[WorkspaceValidator] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._config_class = config_class
        self._config_filename = config_filename
        self._session_dir = session_dir or self._get_default_session_dir()
        self._error_handler = error_handler
        self._validator = validator

        # State
        self._folders: list[WorkspaceFolder] = []
        self._config: Optional[WorkspaceConfig] = None
        self._workspace_path: Optional[Path] = None

        # Config file watcher
        self._config_watcher = QFileSystemWatcher(self)
        self._config_watcher.fileChanged.connect(self._on_config_changed)

    def open_workspace(self, folder_path: Path) -> list[WorkspaceFolder]:
        """Open workspace and return folders."""
        # Try to load config
        config_path = folder_path / self._config_filename
        if config_path.exists():
            config = self._load_config(config_path)
        else:
            # No config - create single-folder workspace
            config = self._config_class.from_folder(folder_path)

        # Create folders list
        self._folders = config.folders
        self._config = config
        self._workspace_path = folder_path

        # Watch config file
        if config_path.exists():
            self._config_watcher.addPath(str(config_path))

        # Emit signal
        self.workspace_opened.emit(self._folders)
        return self._folders

    def _load_config(self, config_path: Path) -> WorkspaceConfig:
        """Load config from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._config_class.from_dict(data)
        except json.JSONDecodeError as e:
            # Corrupt config
            raise ConfigError(f"Config file corrupt: {e}")

    def save_config(self) -> None:
        """Save current config to file."""
        if not self._workspace_path or not self._config:
            return

        config_path = self._workspace_path / self._config_filename

        # Temporarily remove from watcher (avoid triggering fileChanged)
        if str(config_path) in self._config_watcher.files():
            self._config_watcher.removePath(str(config_path))

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
        finally:
            # Re-add to watcher
            self._config_watcher.addPath(str(config_path))

    def load_session(self, workspace_path: Path) -> Optional[WorkspaceSession]:
        """Load session for workspace."""
        session_hash = self._compute_session_hash(workspace_path)
        session_path = self._session_dir / f"{session_hash}.json"

        if not session_path.exists():
            return None

        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return WorkspaceSession.from_dict(data)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load session: {e}")
            return None

    def save_session(self, session: WorkspaceSession) -> None:
        """Save session to file."""
        if not self._workspace_path:
            return

        session_hash = self._compute_session_hash(self._workspace_path)
        session_path = self._session_dir / f"{session_hash}.json"

        # Ensure directory exists
        session_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save session: {e}")

    @staticmethod
    def _compute_session_hash(workspace_path: Path) -> str:
        """Compute hash for session filename."""
        import hashlib
        return hashlib.md5(str(workspace_path).encode()).hexdigest()[:16]

    @staticmethod
    def _get_default_session_dir() -> Path:
        """Get default session directory."""
        return Path.home() / ".config" / "vfwidgets" / "workspaces" / "sessions"
```
\`\`\`

---

### 4. ❌ CRITICAL: Expanded/Collapsed State Tracking Missing

**Issue:** Icons need to know if folder is expanded/collapsed, but no implementation for tracking this.

**In SPECIFICATION.md (line 1047):**
```python
def get_folder_icon(
    self,
    file_info: FileInfo,
    is_expanded: bool = False  # ← How to get this?
) -> QIcon:
```

**In DESIGN.md (line 416):**
```python
is_expanded = False  # TODO: track expanded state
```

**Impact:** Can't show different icons for open/closed folders.

**Fix Required:** Add to DESIGN.md (FileExplorerWidget section):

```python
class FileExplorerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Track expanded state
        self._expanded_nodes: set[str] = set()  # Set of absolute paths

    def _on_expanded(self, index: QModelIndex):
        """Track when node expanded."""
        node = index.internalPointer()
        if node:
            self._expanded_nodes.add(node.path)
            # Request icon update
            self._tree_view.model().dataChanged.emit(index, index)

    def _on_collapsed(self, index: QModelIndex):
        """Track when node collapsed."""
        node = index.internalPointer()
        if node:
            self._expanded_nodes.discard(node.path)
            # Request icon update
            self._tree_view.model().dataChanged.emit(index, index)

    def is_expanded(self, path: str) -> bool:
        """Check if path is currently expanded."""
        return path in self._expanded_nodes
```

And in Model.data():
```python
elif role == Qt.ItemDataRole.DecorationRole:
    file_info = self._get_file_info(node)

    # Get expanded state from view
    is_expanded = self._view_delegate.is_expanded(node.path) if self._view_delegate else False

    if file_info.is_dir:
        return self._icon_provider.get_folder_icon(file_info, is_expanded)
```

---

## High Priority Gaps (Should Fix Soon)

### 5. ⚠️ HIGH: `WorkspaceSession` Save/Restore Implementation Missing

**Issue:** SPEC defines WorkspaceSession dataclass, but DESIGN doesn't explain how to collect/restore UI state.

**What's Missing:**
- How to collect expanded folder paths from QTreeView
- How to get scroll position from QTreeView
- How to restore expanded state (expand specific paths)
- How to restore scroll position

**Fix Required:** Add to DESIGN.md:

```python
class WorkspaceWidget(QWidget):
    def save_session(self) -> WorkspaceSession:
        """Collect current UI state."""
        # Get expanded folders
        expanded_folders = []
        model = self._explorer._tree_view.model()

        def collect_expanded(parent_index: QModelIndex):
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                if self._explorer._tree_view.isExpanded(index):
                    node = index.internalPointer()
                    if node:
                        expanded_folders.append(node.path)
                    # Recurse
                    collect_expanded(index)

        collect_expanded(QModelIndex())

        # Get scroll position
        scrollbar = self._explorer._tree_view.verticalScrollBar()
        scroll_position = scrollbar.value()

        return WorkspaceSession(
            workspace_name=self._current_workspace_path.name if self._current_workspace_path else "",
            last_opened=datetime.now().isoformat(),
            expanded_folders=expanded_folders,
            scroll_position=scroll_position,
            active_file=self._get_active_file()
        )

    def restore_session(self, session: WorkspaceSession) -> None:
        """Restore UI state from session."""
        model = self._explorer._tree_view.model()

        # Expand folders
        for folder_path in session.expanded_folders:
            # Find index for this path
            index = self._find_index_by_path(folder_path)
            if index.isValid():
                self._explorer._tree_view.expand(index)

        # Restore scroll position
        QTimer.singleShot(100, lambda: self._restore_scroll(session.scroll_position))

        # Restore active file
        if session.active_file:
            self.highlight_file(session.active_file)

    def _find_index_by_path(self, path: str) -> QModelIndex:
        """Find model index for absolute path."""
        # Implementation: recursive search through model
        # ...
```

---

### 6. ⚠️ HIGH: `reveal_file()` and `highlight_file()` Implementation Missing

**Issue:** SPEC defines these methods (lines 1617-1661) but DESIGN doesn't explain algorithm.

**What's Missing:**
- How to find QModelIndex for absolute file path
- How to expand parent folders
- How to scroll to make item visible
- How to select item in tree

**Fix Required:** Add to DESIGN.md:

```python
def reveal_file(self, file_path: str) -> bool:
    """Reveal file in tree (expand parents, scroll, select)."""
    # 1. Find model index for file
    index = self._find_index_by_path(file_path)
    if not index.isValid():
        return False

    # 2. Expand all parent folders
    parent = index.parent()
    while parent.isValid():
        self._explorer._tree_view.expand(parent)
        parent = parent.parent()

    # 3. Scroll to make visible
    self._explorer._tree_view.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)

    # 4. Select item
    self._explorer._tree_view.setCurrentIndex(index)

    # 5. Emit signal
    self.active_file_changed.emit(file_path)

    return True

def _find_index_by_path(self, path: str) -> QModelIndex:
    """Find model index for absolute file path.

    Algorithm:
    1. Determine which workspace folder contains file
    2. Get relative path from workspace root
    3. Walk down tree following path components
    4. Return index of final component
    """
    # Find workspace folder
    workspace_folder = None
    for folder in self._manager.get_folders():
        if path.startswith(folder.path):
            workspace_folder = folder
            break

    if not workspace_folder:
        return QModelIndex()

    # Get relative path
    rel_path = Path(path).relative_to(workspace_folder.path)
    components = rel_path.parts

    # Find root index
    model = self._explorer._tree_view.model()
    current_index = QModelIndex()

    # Find workspace folder root
    for row in range(model.rowCount(current_index)):
        index = model.index(row, 0, current_index)
        node = index.internalPointer()
        if node and node.workspace_folder == workspace_folder:
            current_index = index
            break

    # Walk down path
    for component in components:
        found = False
        for row in range(model.rowCount(current_index)):
            index = model.index(row, 0, current_index)
            if index.data(Qt.ItemDataRole.DisplayRole) == component:
                current_index = index
                found = True
                break

        if not found:
            return QModelIndex()

    return current_index
```

---

### 7. ⚠️ HIGH: `sync_with_tab_widget()` Implementation Missing

**Issue:** SPEC promises auto-sync with tabs (line 2947) but DESIGN doesn't explain how.

**Fix Required:** Add to DESIGN.md:

```python
def sync_with_tab_widget(
    self,
    tab_widget: QTabWidget,
    file_path_attr: str = "file_path",
    auto_sync: bool = True
) -> None:
    """Sync workspace selection with tab widget."""
    self._synced_tab_widget = tab_widget
    self._tab_file_path_attr = file_path_attr

    if auto_sync:
        # Connect tab changed signal
        tab_widget.currentChanged.connect(self._on_tab_changed)

def _on_tab_changed(self, index: int):
    """Handle tab change - highlight file in workspace."""
    if not hasattr(self, '_synced_tab_widget'):
        return

    widget = self._synced_tab_widget.widget(index)
    if not widget:
        return

    # Get file path from widget
    if hasattr(widget, self._tab_file_path_attr):
        file_path = getattr(widget, self._tab_file_path_attr)
        if file_path:
            self.highlight_file(str(file_path))
```

---

### 8. ⚠️ HIGH: `find_file()` Fuzzy Matching Algorithm Missing

**Issue:** SPEC promises fuzzy matching (line 2866) but no algorithm specified.

**Fix Required:** Add to DESIGN.md:

```python
def find_file(self, filename: str, fuzzy: bool = False) -> list[str]:
    """Find files by name."""
    results = []
    all_files = self.get_all_files()

    if fuzzy:
        # Fuzzy matching: allow partial, case-insensitive matches
        filename_lower = filename.lower()
        for file_path in all_files:
            file_name = Path(file_path).name.lower()

            # Simple fuzzy: all characters in search must appear in order
            search_idx = 0
            for char in file_name:
                if search_idx < len(filename_lower) and char == filename_lower[search_idx]:
                    search_idx += 1

            if search_idx == len(filename_lower):
                results.append(file_path)
    else:
        # Exact match (case-insensitive)
        filename_lower = filename.lower()
        for file_path in all_files:
            if Path(file_path).name.lower() == filename_lower:
                results.append(file_path)

    return results
```

---

### 9. ⚠️ HIGH: Missing Recent Workspaces Persistence Implementation

**Issue:** SPEC defines recent workspaces API (lines 1228-1341) but DESIGN doesn't explain how to persist.

**Fix Required:** Add to DESIGN.md WorkspaceManager:

```python
class WorkspaceManager(QObject):
    def __init__(self, ...):
        ...
        self._recent_workspaces_file = Path.home() / ".config" / "vfwidgets" / "workspace" / "recent.json"

    def add_recent_workspace(self, workspace_path: str, name: str, folder_count: int):
        """Add to recent workspaces list."""
        recent = self._load_recent_workspaces()

        # Create entry
        entry = {
            "path": workspace_path,
            "name": name,
            "folder_count": folder_count,
            "last_opened": datetime.now().isoformat()
        }

        # Remove if already exists
        recent = [r for r in recent if r["path"] != workspace_path]

        # Add to front
        recent.insert(0, entry)

        # Limit to 10
        recent = recent[:10]

        # Save
        self._save_recent_workspaces(recent)

    def _load_recent_workspaces(self) -> list[dict]:
        if not self._recent_workspaces_file.exists():
            return []

        try:
            with open(self._recent_workspaces_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_recent_workspaces(self, recent: list[dict]):
        self._recent_workspaces_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self._recent_workspaces_file, 'w') as f:
            json.dump(recent, f, indent=2)
```

---

## Medium Priority Gaps (Good to Have)

### 10. 📝 MEDIUM: Filter Callback Gets WorkspaceFolder - How to Determine It?

**Issue:** Filter callback receives `WorkspaceFolder` parameter, but how does Model determine which folder a file belongs to?

**In SPEC (line 2657):**
```python
filter_callback: Optional[Callable[[FileInfo, WorkspaceFolder], bool]] = None
```

**In DESIGN (line 329):**
```python
# Get workspace folder (walk up to root)
workspace_folder = None  # TODO: determine workspace folder
```

**Fix Required:** Add to TreeNode:

```python
class TreeNode:
    def get_workspace_folder(self) -> Optional[WorkspaceFolder]:
        """Get workspace folder this node belongs to."""
        current = self
        while current.parent is not None:
            current = current.parent
        # current is now a root node
        return current.workspace_folder if current.is_root else None
```

---

### 11. 📝 MEDIUM: `reveal_in_file_manager()` Platform-Specific Implementation

**Issue:** SPEC promises platform-aware file manager reveal (line 2927) but no implementation.

**Fix Required:**

```python
def reveal_in_file_manager(self, file_path: str) -> bool:
    """Open file manager and select file (platform-specific)."""
    import sys
    import subprocess

    path = Path(file_path)
    if not path.exists():
        return False

    try:
        if sys.platform == "win32":
            # Windows: Use explorer.exe /select
            subprocess.run(["explorer", "/select,", str(path)], check=True)

        elif sys.platform == "darwin":
            # macOS: Use open -R
            subprocess.run(["open", "-R", str(path)], check=True)

        else:
            # Linux: Use xdg-open on parent folder
            # (no standard way to select specific file)
            subprocess.run(["xdg-open", str(path.parent)], check=True)

        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
```

---

### 12. 📝 MEDIUM: How Does Model Know About View for Expanded State?

**Issue:** Model needs to ask view if folder is expanded (for icon), but models shouldn't reference views.

**Current Problem (DESIGN line 416):**
```python
# Get expanded state from view
is_expanded = self._view_delegate.is_expanded(node.path)  # ← Model shouldn't know about view!
```

**Better Solution:**

Store expanded state in Model (updated by View):

```python
class MultiRootFileSystemModel(QAbstractItemModel):
    def __init__(self, ...):
        ...
        self._expanded_paths: set[str] = set()

    def set_expanded(self, path: str, expanded: bool):
        """Called by view when node expanded/collapsed."""
        if expanded:
            self._expanded_paths.add(path)
        else:
            self._expanded_paths.discard(path)

        # Refresh icon for this path
        node = self._find_node_by_path(path)
        if node:
            index = self._index_for_node(node)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

# In FileExplorerWidget:
def _on_expanded(self, index: QModelIndex):
    node = index.internalPointer()
    if node:
        self._tree_view.model().set_expanded(node.path, True)

def _on_collapsed(self, index: QModelIndex):
    node = index.internalPointer()
    if node:
        self._tree_view.model().set_expanded(node.path, False)
```

---

### 13. 📝 MEDIUM: Missing `get_all_files()` Implementation

**Issue:** SPEC defines this (line 2878) but DESIGN doesn't explain algorithm.

**Fix Required:**

```python
def get_all_files(self, folder_path: Optional[str] = None) -> list[str]:
    """Get all files in workspace (flat list)."""
    results = []

    model = self._model

    # Determine starting indices
    if folder_path:
        # Find workspace folder with this path
        start_indices = []
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            node = index.internalPointer()
            if node and node.path == folder_path:
                start_indices.append(index)
                break
    else:
        # All workspace folders
        start_indices = [model.index(row, 0) for row in range(model.rowCount())]

    # Recursive collection
    def collect_files(parent_index: QModelIndex):
        for row in range(model.rowCount(parent_index)):
            index = model.index(row, 0, parent_index)
            file_info = index.data(Qt.ItemDataRole.UserRole)

            if file_info:
                if file_info.is_dir:
                    # Recurse into folder
                    collect_files(index)
                else:
                    # Add file
                    results.append(file_info.absolute_path)

    for start_index in start_indices:
        collect_files(start_index)

    return results
```

---

### 14. 📝 MEDIUM: Builder Pattern `build()` Method Missing Some Fields

**Issue:** Builder pattern (SPEC lines 3131-3150) doesn't include all extension points.

**Missing from builder:**
- `context_menu_provider`
- `workspace_validator`

**Fix Required:** Add to SPEC line 3138:

```python
def build(self) -> WorkspaceWidget:
    widget = WorkspaceWidget(
        file_extensions=self._file_extensions,
        excluded_folders=self._excluded_folders,
        config_filename=self._config_filename,
        conflict_handler=self._conflict_handler,
        error_handler=self._error_handler,
        icon_provider=self._icon_provider,
        lifecycle_hooks=self._lifecycle_hooks,
        context_menu_provider=self._context_menu_provider,  # ← ADD
        workspace_validator=self._workspace_validator,      # ← ADD
        parent=self._parent
    )
```

---

### 15. 📝 MEDIUM: Missing Signals in Complete API

**Issue:** Some signals mentioned in design but not in SPEC Complete API.

**Missing Signals:**
- `file_reload_requested` (mentioned in file conflict handling)
- `file_reload_prompt_requested`
- `file_close_requested`
- `file_diff_requested`
- `context_menu_action_triggered`
- `validation_failed`
- `keyboard_shortcut_triggered`
- `recent_workspaces_changed`

**Fix Required:** Add to SPEC WorkspaceWidget class (after line 2650):

```python
# Additional signals from extension points
file_reload_requested = Signal(str)
file_reload_prompt_requested = Signal(str)
file_close_requested = Signal(str)
file_diff_requested = Signal(str)
context_menu_action_triggered = Signal(str, object)
validation_failed = Signal(str, str)  # path, error_message
keyboard_shortcut_triggered = Signal(str)
recent_workspaces_changed = Signal()
```

---

### 16. 📝 MEDIUM: Missing `watch_file()` / `unwatch_file()` in Complete API

**Issue:** File conflict handling requires watching files, but these methods not in Complete API.

**In SPEC (line 849):**
```python
workspace.watch_file(file_path)
```

**But not in Complete API section (lines 2631-2735).**

**Fix Required:** Add to Complete API:

```python
# File watching (for conflict detection)
def watch_file(self, file_path: str) -> None:
    """Add file to conflict watch list."""
    pass

def unwatch_file(self, file_path: str) -> None:
    """Remove file from conflict watch list."""
    pass
```

---

## Inconsistencies

### 17. ⚠️ INCONSISTENCY: Signal Parameter Types

**Issue:** Some signals use different types in different places.

**Example 1 - `folder_expanded`:**

In SPEC Complete API (line 2644):
```python
folder_expanded = Signal(str, str)  # What are the two strings?
```

In FileExplorerWidget (should be):
```python
folder_expanded = Signal(str, str)  # folder_path, workspace_folder_path
```

**Needs clarification in docstring.**

---

### 18. ⚠️ INCONSISTENCY: `context_menu_requested` Signal Parameters

**In SPEC (line 2650):**
```python
context_menu_requested = Signal(QPoint, object)  # QPoint, item
```

**In Context Menu Protocol (line 1357):**
```python
context_menu_requested = Signal(QPoint, object, object)  # position, item, workspace_folder
```

**Fix:** Use 3-parameter version everywhere (more useful).

---

### 19. 📝 INCONSISTENCY: `FileInfo.relative_path` vs `FileInfo.absolute_path`

**Issue:** FileInfo has `relative_path` field, but many examples use `absolute_path` which doesn't exist.

**In SPEC FileInfo (line 332):**
```python
@dataclass
class FileInfo:
    name: str
    relative_path: str  # ← Relative to workspace folder
    is_dir: bool
    size: int
    modified_time: float
```

**But in usage (line 1306):**
```python
self.app.open_in_typora(file_info.absolute_path)  # ← Doesn't exist!
```

**Fix:** Add `absolute_path` property to FileInfo:

```python
@dataclass
class FileInfo:
    name: str
    relative_path: str
    is_dir: bool
    size: int
    modified_time: float
    _absolute_path: str = field(default="", repr=False)  # Internal

    @property
    def absolute_path(self) -> str:
        """Get absolute path (computed or stored)."""
        return self._absolute_path

    @property
    def extension(self) -> str:
        """Get file extension (e.g., '.py')."""
        return Path(self.name).suffix.lower()
```

---

## Missing Specifications

### 20. ⚠️ MISSING SPEC: No Documentation for `WorkspaceRootState`

**Issue:** WorkspaceRootState dataclass exists (SPEC line 462) but never used or explained.

**Current:**
```python
@dataclass
class WorkspaceRootState:
    """State of a workspace root (expanded, etc.)."""
    path: str
    is_expanded: bool = False
```

**Problem:** Where is this used? Is it part of WorkspaceSession? Unclear.

**Fix:** Either remove if unused, or integrate into WorkspaceSession:

```python
@dataclass
class WorkspaceSession:
    workspace_name: str
    last_opened: str  # ISO format timestamp
    expanded_folders: list[str]  # Absolute paths
    scroll_position: int
    active_file: Optional[str] = None
    root_states: list[WorkspaceRootState] = field(default_factory=list)  # ← ADD
```

---

### 21. 📝 MISSING SPEC: No Keyboard Shortcuts Defined

**Issue:** SPEC mentions keyboard navigation (line 1168) but doesn't define specific shortcuts.

**Fix:** Add table to SPEC:

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Navigate up/down |
| `←` / `→` | Collapse/expand folder |
| `Enter` | Open file (double-click equivalent) |
| `Space` | Toggle folder expand/collapse |
| `Home` | Jump to first item |
| `End` | Jump to last item |
| `Ctrl+F` / `Cmd+F` | Focus search (if enabled) |
| Type characters | Type-ahead search |

---

### 22. 📝 MISSING SPEC: Context Menu Default Actions Not Connected

**Issue:** DefaultContextMenuProvider creates actions but doesn't connect them.

**In SPEC (lines 1190-1223):**
```python
# Open action
open_action = QAction("Open", self.parent)
actions.append(open_action)  # ← Not connected to anything!
```

**Fix:** Either connect in default implementation OR emit signals:

```python
# Option 1: Emit signals (better - lets app handle)
open_action = QAction("Open", self.parent)
open_action.triggered.connect(
    lambda: self.action_triggered.emit("open", file_info)
)

# Option 2: Connect to widget methods (tighter coupling)
open_action.triggered.connect(
    lambda: self.parent.file_double_clicked.emit(file_info.absolute_path)
)
```

---

## Clarifications Needed

### 23. 🔍 CLARIFY: What Happens on Open Workspace When One Already Open?

**Issue:** No specification for this scenario.

**Options:**
1. Auto-close current workspace first
2. Error "Workspace already open"
3. Prompt user "Close current workspace?"

**Recommendation:** Option 2 (error), app should explicitly close first.

**Add to SPEC:**
```python
def open_workspace(self, folder_path: Path) -> bool:
    """Open a folder as workspace.

    Returns:
        True if successful, False if failed or workspace already open.

    Note:
        If a workspace is already open, returns False.
        App must call close_workspace() first.
    """
```

---

### 24. 🔍 CLARIFY: Session Auto-Save Timing

**Issue:** When is session auto-saved?

**Options:**
1. On every UI change (expensive)
2. On workspace close only
3. Debounced (e.g., 5 seconds after last change)
4. Manual only (app calls save_session)

**Recommendation:** Option 4 (manual) for V1, Option 3 (debounced) for V2.

**Add to DESIGN:**
```python
# V1: Manual session save
# - App calls workspace.save_session() before closing
# - Simple, predictable

# V2: Auto-save with debouncing
# - Save 5 seconds after last expand/collapse/scroll
# - Requires QTimer in WorkspaceWidget
```

---

### 25. 🔍 CLARIFY: Multi-Folder Config - One File or Multiple?

**Issue:** When workspace has multiple folders, where is config stored?

**Current SPEC:** Suggests config in primary folder (first folder).

**Clarify:** Add to SPEC:

```
**Config File Location:**

For single-folder workspace:
```
/home/user/my-project/.workspace.json
```

For multi-folder workspace:
```
/home/user/folder1/.workspace.json  ← Primary config here
/home/user/folder2/                 ← Referenced in config
/home/user/folder3/                 ← Referenced in config
```

The config is always stored in the FIRST folder's directory.
```

---

### 26. 🔍 CLARIFY: Empty Workspace Behavior

**Issue:** What happens if you open workspace but all folders filtered out?

**Scenario:**
```python
workspace = WorkspaceWidget(file_extensions=[".py"])
workspace.open_workspace("/home/user/docs")  # Folder only has .md files
```

**Result:** Tree is empty. Is this an error or valid state?

**Recommendation:** Valid state, emit warning via ErrorHandler.

---

### 27. 🔍 CLARIFY: Nested Workspace Detection

**Issue:** WorkspaceValidator warns about nested workspaces (SPEC line 1537) but what action is taken?

**Options:**
1. Just warn (allow opening)
2. Block opening
3. Prompt user

**Recommendation:** Option 1 (warn) - let user decide.

---

### 28. 🔍 CLARIFY: Config Version Compatibility

**Issue:** How to handle config version mismatches?

**Scenario:**
```json
{
  "version": 3,  // Widget only supports version 1 & 2
  ...
}
```

**Recommendation:** Add to WorkspaceValidator:

```python
def validate_workspace_config(self, config, config_path):
    if config.version > 2:
        return ValidationResult(
            False,
            f"Config version {config.version} not supported (max: 2)"
        )
```

---

### 29. 🔍 CLARIFY: QFileSystemWatcher Reliability

**Issue:** QFileSystemWatcher can miss changes or have platform limitations.

**Platform Limits:**
- **Linux:** inotify limit (~8,192 watches by default)
- **macOS:** FSEvents generally reliable
- **Windows:** ReadDirectoryChangesW generally reliable

**Recommendation:** Add to DESIGN Performance section:

```markdown
### QFileSystemWatcher Limitations

**Linux (inotify):**
- Default limit: 8,192 watches
- Check: `cat /proc/sys/fs/inotify/max_user_watches`
- Increase: `echo 524288 | sudo tee /proc/sys/fs/inotify/max_user_watches`

**Mitigation:**
- Only watch open files (not entire workspace)
- Use AUTO_ON_OPEN mode (watch when file opened in editor)
- Warn user if watch limit reached
```

---

### 30. 🔍 CLARIFY: Thread Safety for Config/Session File I/O

**Issue:** File I/O can block UI. Should it be async?

**Current:** All I/O synchronous.

**Recommendation:** V1 synchronous (simpler), V2 async if needed.

Config/session files are small (< 1KB typically), blocking is minimal.

---

## Low Priority Gaps

### 31. 📌 LOW: Missing Type Hints in Some Examples

**Issue:** Some code examples lack complete type hints.

**Example (SPEC line 178):**
```python
class MyConflictHandler:  # ← Missing `: FileConflictHandler`
    def handle_file_modified(self, file_path, workspace_folder=None):  # ← Missing types
```

**Fix:** Add type hints to all examples.

---

### 32. 📌 LOW: No Examples of Subclassing Default Implementations

**Issue:** SPEC shows creating custom handlers, but not extending defaults.

**Add Example:**
```python
class MyErrorHandler(DefaultErrorHandler):
    """Custom error handler extending default."""

    def handle_error(self, severity, message, exception=None, context=None):
        # Log to custom logger
        my_app_logger.log(severity, message)

        # Call default behavior (shows UI)
        return super().handle_error(severity, message, exception, context)
```

---

### 33. 📌 LOW: Performance Benchmarks Missing

**Issue:** DESIGN mentions performance targets but no benchmark code.

**Add to DESIGN:**
```python
# Benchmark script
def benchmark_model_performance():
    """Benchmark model operations."""
    import time

    workspace = WorkspaceWidget()
    workspace.open_workspace(Path("/large/workspace"))

    model = workspace._model

    # Benchmark rowCount
    start = time.perf_counter()
    for _ in range(1000):
        model.rowCount(QModelIndex())
    elapsed = time.perf_counter() - start
    print(f"rowCount: {elapsed*1000:.2f}ms for 1000 calls")

    # ... etc
```

---

### 34. 📌 LOW: No Migration Guide from Single-Folder Apps

**Issue:** Apps currently using single-folder pattern need migration guide.

**Add to SPEC:**
```markdown
## Migrating from Single-Folder to Multi-Folder

**Before (single-folder):**
```python
file_tree = QTreeView()
model = QFileSystemModel()
model.setRootPath("/home/user/project")
file_tree.setModel(model)
```

**After (workspace widget):**
```python
workspace = WorkspaceWidget()
workspace.open_workspace(Path("/home/user/project"))
# Handles config, session, multi-folder automatically
```
\`\`\`

---

### 35-39: Additional Low Priority Items

- Missing example of workspace with > 2 folders
- No example of custom WorkspaceConfig with to_dict/from_dict
- Testing guide could include mock examples for handlers
- Troubleshooting could include "clean session data" command
- No discussion of workspace portability (absolute vs relative paths)

---

## Summary & Recommendations

### Critical Path Items (Must Fix Before Implementation)

1. **Fix `WorkspaceWidget.__init__()` signature in DESIGN** → Add all extension point parameters
2. **Add FileExplorerWidget implementation section to DESIGN** → Complete implementation guide
3. **Add WorkspaceManager implementation section to DESIGN** → Config/session loading/saving
4. **Solve expanded/collapsed state tracking** → Design decision on Model vs View storage

### High Priority (Fix in Phase 1-2)

5-9. Implement session save/restore, reveal_file, sync_with_tabs, find_file (fuzzy), recent workspaces

### Medium Priority (Fix During Implementation)

10-16. Clarify filter callback workspace folder resolution, platform-specific implementations, signal additions

### Inconsistencies (Fix Now)

17-19. Resolve signal parameter mismatches, FileInfo absolute_path issue

### Missing Specs (Document During Implementation)

20-22. Document WorkspaceRootState usage, keyboard shortcuts, context menu action connections

### Clarifications (Decide Before Implementation)

23-30. Document behavior for edge cases (open when open, empty workspace, nested workspaces, etc.)

---

## Next Steps

1. **Address 4 critical gaps** (items 1-4) - Required before implementation
2. **Review and approve** high priority items (5-9) - Add to DESIGN
3. **Fix inconsistencies** (17-19) - Update both SPEC and DESIGN
4. **Document decisions** for clarifications (23-30) - Add to DESIGN or SPEC as appropriate
5. **Begin implementation** following updated DESIGN Phase 1

