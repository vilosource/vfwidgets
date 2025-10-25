"""ReamdeWindow - Main application window using ViloCodeWindow."""

from enum import Enum
from pathlib import Path
from typing import Optional

from chrome_tabbed_window import ChromeTabbedWindow
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QSplitter,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from vfwidgets_markdown import MarkdownDocument, MarkdownTextEditor, MarkdownViewer
from vfwidgets_vilocode_window import ViloCodeWindow

from .controllers import WindowController
from .utils.logging_setup import get_logger
from .workspace_manager import ReamdeWorkspaceManager

logger = get_logger(__name__)


class ViewMode(Enum):
    """View mode for markdown tabs."""

    PREVIEW_ONLY = "preview"
    EDITOR_ONLY = "editor"
    SPLIT_VIEW = "split"


class ReamdeTabbedWindow(ChromeTabbedWindow):
    """Custom ChromeTabbedWindow that opens file dialog when '+' button is clicked."""

    # Signal emitted when user requests to open a file via '+' button
    open_file_requested = Signal()

    def _on_new_tab_requested(self) -> None:
        """Handle new tab button ('+') click - emit signal to open file dialog.

        This overrides ChromeTabbedWindow's default behavior to provide
        a file picker instead of creating a blank "New Tab" widget.
        """
        self.open_file_requested.emit()


class MarkdownViewerTab(QWidget):
    """Wrapper for MarkdownViewer with file path tracking and split editing support.

    Supports:
    - Lazy loading - content loaded when ensure_loaded() is called
    - Split editing - toggle between preview-only, editor-only, and split views
    - Auto-save - changes saved automatically after 1.5 seconds
    - View mode persistence - each tab remembers its view mode
    """

    # Signals
    view_mode_changed = Signal(object)  # ViewMode
    content_modified = Signal()  # Emitted when content changes (for unsaved indicator)
    content_saved = Signal()  # Emitted when content is auto-saved

    def __init__(
        self,
        file_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
        load_content: bool = True,
        view_mode: ViewMode = ViewMode.PREVIEW_ONLY,
        show_view_toolbar: bool = False,
    ):
        """Initialize the markdown viewer tab.

        Args:
            file_path: Path to markdown file to load
            parent: Parent widget
            load_content: If False, defer loading until ensure_loaded() is called
            view_mode: Initial view mode (default: preview-only)
            show_view_toolbar: Whether to show view mode toolbar (default: False/hidden)
        """
        print(f"[reamde] MarkdownViewerTab.__init__() called, file_path={file_path}")
        super().__init__(parent)

        self.file_path = file_path
        self._content_loaded = False  # Track if content has been loaded
        self._view_mode = view_mode
        self._has_unsaved_changes = False
        self._show_view_toolbar = show_view_toolbar  # Store toolbar visibility preference

        # Create shared MarkdownDocument (MVC architecture)
        print("[reamde] Creating shared MarkdownDocument...")
        self.document = MarkdownDocument()

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create toolbar for view mode controls (conditionally shown)
        self._toolbar = self._create_toolbar()
        main_layout.addWidget(self._toolbar)
        self._toolbar.setVisible(self._show_view_toolbar)  # Apply visibility preference

        # Create splitter for preview/editor
        print("[reamde] Creating QSplitter...")
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)

        # Create MarkdownViewer with shared document
        print("[reamde] Creating MarkdownViewer with shared document...")
        self.viewer = MarkdownViewer(document=self.document, parent=self.splitter)
        self.splitter.addWidget(self.viewer)

        # Create MarkdownTextEditor with shared document
        print("[reamde] Creating MarkdownTextEditor with shared document...")
        self.editor = MarkdownTextEditor(self.document, parent=self.splitter)
        self.editor.setVisible(False)  # Initially hidden
        self.splitter.addWidget(self.editor)

        # Set initial splitter sizes (50/50 split)
        self.splitter.setSizes([500, 500])

        main_layout.addWidget(self.splitter)
        print("[reamde] Splitter and widgets added to layout")

        # Set dark background on tab container to prevent white flash
        self.setStyleSheet("QWidget { background-color: #1a1a1a; }")

        # Setup auto-save timer
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.setInterval(1500)  # 1.5 seconds
        self._auto_save_timer.timeout.connect(self._auto_save)

        # Connect editor content changes to auto-save trigger
        self.editor.content_modified.connect(self._on_content_modified)

        # Apply initial view mode
        self.set_view_mode(view_mode)

        # Load file if provided and load_content=True
        if file_path and load_content:
            print("[reamde] Loading file immediately...")
            self.load_file(file_path)
        elif file_path:
            print("[reamde] Deferring file load (lazy loading enabled)")

    def _create_toolbar(self) -> QToolBar:
        """Create toolbar with view mode controls.

        Returns:
            QToolBar with preview/split/editor buttons
        """
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border: none; spacing: 2px; }")

        # Preview-only button
        self._preview_btn = QToolButton()
        self._preview_btn.setText("👁")
        self._preview_btn.setToolTip("Preview Only (Ctrl+Shift+P)")
        self._preview_btn.setCheckable(True)
        self._preview_btn.clicked.connect(lambda: self.set_view_mode(ViewMode.PREVIEW_ONLY))
        toolbar.addWidget(self._preview_btn)

        # Split view button
        self._split_btn = QToolButton()
        self._split_btn.setText("⬌")
        self._split_btn.setToolTip("Split View (Ctrl+Shift+S)")
        self._split_btn.setCheckable(True)
        self._split_btn.clicked.connect(lambda: self.set_view_mode(ViewMode.SPLIT_VIEW))
        toolbar.addWidget(self._split_btn)

        # Editor-only button
        self._editor_btn = QToolButton()
        self._editor_btn.setText("📝")
        self._editor_btn.setToolTip("Editor Only (Ctrl+Shift+E)")
        self._editor_btn.setCheckable(True)
        self._editor_btn.clicked.connect(lambda: self.set_view_mode(ViewMode.EDITOR_ONLY))
        toolbar.addWidget(self._editor_btn)

        return toolbar

    def load_file(self, file_path: Path) -> bool:
        """Load markdown file into shared document.

        Args:
            file_path: Path to markdown file

        Returns:
            True if loaded successfully, False otherwise
        """
        print(f"[reamde] Loading file: {file_path}")
        self.file_path = file_path

        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Set content in shared document (will update both viewer and editor)
            self.document.set_text(content)

            # Set base path for relative images in viewer
            self.viewer.set_base_path(str(file_path.parent))

            print("[reamde] File loaded successfully")
            self._content_loaded = True
            self._has_unsaved_changes = False
            return True

        except Exception as e:
            print(f"[reamde] Failed to load file: {e}")
            logger.error(f"Failed to load file {file_path}: {e}")
            return False

    def ensure_loaded(self) -> bool:
        """Ensure content is loaded (lazy loading support).

        If content hasn't been loaded yet and file_path is set, load it now.
        This is called when tab becomes visible for the first time.

        Returns:
            True if content is now loaded, False if no file or load failed
        """
        if self._content_loaded:
            # Already loaded
            return True

        if not self.file_path:
            # No file to load
            return False

        print(f"[reamde] Lazy loading content for: {self.file_path.name}")
        return self.load_file(self.file_path)

    def reload(self) -> bool:
        """Reload file from disk.

        Returns:
            True if reloaded successfully, False otherwise
        """
        if self.file_path:
            return self.load_file(self.file_path)
        return False

    def set_view_mode(self, mode: ViewMode) -> None:
        """Set the view mode (preview-only, editor-only, or split).

        Args:
            mode: ViewMode to apply
        """
        print(f"[reamde] Setting view mode to: {mode.value}")
        self._view_mode = mode

        # Update button states
        self._preview_btn.setChecked(mode == ViewMode.PREVIEW_ONLY)
        self._split_btn.setChecked(mode == ViewMode.SPLIT_VIEW)
        self._editor_btn.setChecked(mode == ViewMode.EDITOR_ONLY)

        # Show/hide widgets based on mode
        if mode == ViewMode.PREVIEW_ONLY:
            self.viewer.setVisible(True)
            self.editor.setVisible(False)
            # Resume file watching (no editing conflicts)
            self._start_file_watching()
        elif mode == ViewMode.EDITOR_ONLY:
            self.viewer.setVisible(False)
            self.editor.setVisible(True)
            # Pause file watching (prevent conflicts with auto-save)
            self._stop_file_watching()
        elif mode == ViewMode.SPLIT_VIEW:
            self.viewer.setVisible(True)
            self.editor.setVisible(True)
            # Pause file watching (prevent conflicts with auto-save)
            self._stop_file_watching()

        # Emit signal
        self.view_mode_changed.emit(mode)

        logger.info(f"View mode changed to: {mode.value}")

    def toggle_edit_mode(self) -> None:
        """Toggle between preview-only and split-view modes.

        This is a convenience method for the Edit action.
        """
        if self._view_mode == ViewMode.PREVIEW_ONLY:
            self.set_view_mode(ViewMode.SPLIT_VIEW)
        else:
            self.set_view_mode(ViewMode.PREVIEW_ONLY)

    def get_view_mode(self) -> ViewMode:
        """Get current view mode.

        Returns:
            Current ViewMode
        """
        return self._view_mode

    def set_toolbar_visible(self, visible: bool) -> None:
        """Set toolbar visibility.

        Args:
            visible: Whether toolbar should be visible
        """
        self._show_view_toolbar = visible
        if self._toolbar:
            self._toolbar.setVisible(visible)

    def _on_content_modified(self) -> None:
        """Handle content modification in editor.

        Triggered when user types in editor. Starts auto-save timer.
        """
        self._has_unsaved_changes = True
        self.content_modified.emit()

        # Restart auto-save timer (debounce)
        self._auto_save_timer.stop()
        self._auto_save_timer.start()

    def _auto_save(self) -> None:
        """Auto-save content to file.

        Called by timer after user stops typing for 1.5 seconds.
        """
        if not self._has_unsaved_changes or not self.file_path:
            return

        try:
            # Get current content from document
            content = self.document.get_text()

            # Write to file
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self._has_unsaved_changes = False
            self.content_saved.emit()
            logger.info(f"Auto-saved: {self.file_path.name}")

        except Exception as e:
            logger.error(f"Auto-save failed for {self.file_path}: {e}")

    def has_unsaved_changes(self) -> bool:
        """Check if tab has unsaved changes.

        Returns:
            True if there are unsaved changes
        """
        return self._has_unsaved_changes

    def _start_file_watching(self) -> None:
        """Start watching file for external changes (used in preview-only mode)."""
        if not self.file_path:
            return

        # Get controller from parent window
        parent_window = self.window()
        if hasattr(parent_window, "controller"):
            controller = parent_window.controller
            if hasattr(controller, "file_watcher"):
                controller.file_watcher.watch_file(str(self.file_path))
                logger.debug(f"Started watching file: {self.file_path.name}")

    def _stop_file_watching(self) -> None:
        """Stop watching file for external changes (used during editing to prevent conflicts)."""
        if not self.file_path:
            return

        # Get controller from parent window
        parent_window = self.window()
        if hasattr(parent_window, "controller"):
            controller = parent_window.controller
            if hasattr(controller, "file_watcher"):
                controller.file_watcher.unwatch_file(str(self.file_path))
                logger.debug(f"Stopped watching file: {self.file_path.name}")


class ReamdeWindow(ViloCodeWindow):
    """Main application window for Reamde.

    Uses ViloCodeWindow for VS Code-style layout with ChromeTabbedWindow
    in the main content area for tabbed document viewing.

    Signals:
        file_opened: Emitted when a file is opened (file_path)
        tab_closed: Emitted when a tab is closed (file_path)
    """

    # Signals
    file_opened = Signal(str)  # file_path
    tab_closed = Signal(str)  # file_path

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the ReamdeWindow."""
        super().__init__(
            parent,
            enable_default_shortcuts=True,
            show_activity_bar=True,  # Enable for workspace explorer
            show_sidebar=True,  # Enable for file tree
            show_auxiliary_bar=False,
        )

        # Set window title
        self.setWindowTitle("Reamde - Markdown Viewer")
        self.resize(1200, 800)

        # Track open files to prevent duplicates
        self._open_files: dict[str, int] = {}  # file_path -> tab_index

        # Track view modes from session (used during restore)
        self._session_view_modes: dict[str, str] = {}  # file_path -> view_mode

        # Initialize controller for session management and file operations
        self.controller = WindowController(parent=self)
        logger.info("WindowController initialized")

        # Initialize workspace manager
        self.workspace_manager = ReamdeWorkspaceManager(self)
        logger.info("WorkspaceManager initialized")

        # Setup workspace in sidebar (if available)
        if self.workspace_manager.workspace_widget:
            self.add_sidebar_panel("files", self.workspace_manager.workspace_widget, "Files")
            logger.info("Workspace widget added to sidebar")

            # Add Files activity bar item
            from PySide6.QtGui import QIcon

            files_icon = QIcon.fromTheme("folder", QIcon())  # Use system folder icon
            self.add_activity_item("files", files_icon, "File Explorer (Ctrl+Shift+E)")
            logger.info("Files activity bar item added")

            # Connect activity item click to show sidebar panel
            self.activity_item_clicked.connect(self._on_activity_item_clicked)

            # Initially hide sidebar (shown when workspace opens)
            self.set_sidebar_visible(False)

            # Connect workspace lifecycle signals
            self.workspace_manager.workspace_widget.workspace_opened.connect(
                self._on_workspace_opened
            )
            self.workspace_manager.workspace_widget.workspace_closed.connect(
                self._on_workspace_closed
            )

        # Load and apply preferences
        from .preferences_manager import PreferencesManager

        self.prefs_manager = PreferencesManager()
        self.preferences = self.prefs_manager.load_preferences()
        self._apply_startup_preferences()

        # Setup tabbed content area
        self._setup_tabbed_content()

        # Store action references for enabling/disabling (before menu setup)
        self._undo_action = None
        self._redo_action = None

        # Setup file menu
        self._setup_file_menu()

        # Setup edit menu
        self._setup_edit_menu()

        # Setup help menu
        self._setup_help_menu()

        # Restore previous session (open files from last run)
        logger.info("Restoring session...")
        self.controller.restore_session()

    # showEvent workaround removed - no longer needed with fluent API's automatic theme integration!

    def _setup_tabbed_content(self) -> None:
        """Setup ChromeTabbedWindow in main content area."""
        # Create tabbed window as embedded widget (pass self as parent)
        self._tabs = ReamdeTabbedWindow(parent=self)
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.setTabsEditable(True)  # Enable tab renaming via double-click

        # Connect tab signals
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tabs.currentChanged.connect(self._on_current_tab_changed)
        self._tabs.open_file_requested.connect(
            self._on_open_file
        )  # Connect '+' button to file dialog

        # Connect tab rename signals
        self._tabs.tabRenameFinished.connect(self._on_tab_renamed)

        # Connect controller signals to UI updates
        self.controller.file_opened.connect(self._on_controller_file_opened)
        self.controller.file_closed.connect(self._on_controller_file_closed)
        self.controller.session_restored.connect(self._on_session_restored)

        # Set as main content
        self.set_main_content(self._tabs)

        # Apply topbar preferences (now that self._tabs exists)
        self._apply_topbar_preferences()

    def _apply_topbar_preferences(self) -> None:
        """Apply topbar appearance preferences on startup."""
        # Apply accent line settings (for ChromeTabbedWindow tabs)
        self._tabs.set_accent_line_visible(self.preferences.appearance.show_accent_line)
        if self.preferences.appearance.accent_line_color:
            self._tabs.set_accent_line_color(self.preferences.appearance.accent_line_color)
            logger.info(
                f"Applied accent line color: {self.preferences.appearance.accent_line_color}"
            )

        # Apply title bar background color via user layer (like ViloxTerm)
        if self.preferences.appearance.top_bar_background_color:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if hasattr(app, "customize_color"):
                app.customize_color(
                    "titleBar.activeBackground",
                    self.preferences.appearance.top_bar_background_color,
                    persist=True,
                )
                logger.info(
                    f"Applied title bar background color on startup: {self.preferences.appearance.top_bar_background_color}"
                )

    def open_file(self, file_path: str | Path, focus: bool = True) -> bool:
        """Open a markdown file in a new tab or focus existing tab.

        Args:
            file_path: Path to markdown file
            focus: Whether to focus the tab after opening

        Returns:
            True if opened/focused successfully, False otherwise
        """
        file_path = Path(file_path).resolve()
        print(f"[reamde] ReamdeWindow.open_file() called with: {file_path}")

        # Check if file already open
        file_str = str(file_path)
        if file_str in self._open_files:
            # File already open - just focus it
            print(f"[reamde] File already open at tab {self._open_files[file_str]}")
            tab_index = self._open_files[file_str]
            if focus:
                self._tabs.setCurrentIndex(tab_index)
            return True

        # Check if file exists
        if not file_path.exists():
            print(f"[reamde] Error: File not found: {file_path}")
            return False

        print("[reamde] Creating new MarkdownViewerTab...")
        # Create new tab - only load content immediately if this tab will be focused
        # This prevents multiple tabs from loading simultaneously during session restore
        tab = MarkdownViewerTab(
            file_path,
            load_content=focus,
            show_view_toolbar=self.preferences.markdown.show_view_mode_toolbar,
        )
        tab_title = file_path.name
        print(f"[reamde] Adding tab '{tab_title}'...")
        tab_index = self._tabs.addTab(tab, tab_title)
        print(f"[reamde] Tab added at index {tab_index}")

        # Set tooltip to full path
        self._tabs.setTabToolTip(tab_index, str(file_path))

        # Connect tab signals for unsaved indicator
        tab.content_modified.connect(lambda: self._on_tab_content_modified(tab))
        tab.content_saved.connect(lambda: self._on_tab_content_saved(tab))

        # Connect editor's undo/redo availability signals
        tab.editor.undoAvailable.connect(self._update_undo_action_state)
        tab.editor.redoAvailable.connect(self._update_redo_action_state)

        # Track open file
        self._open_files[file_str] = tab_index

        # Register file with controller (without triggering UI update to avoid recursion)
        # Controller needs to know about the file for session persistence
        logger.info(f"Registering file with controller: {file_str}")
        self.controller.open_file(file_str, set_active=False)

        # Focus new tab
        if focus:
            print(f"[reamde] Setting current tab to {tab_index}")
            self._tabs.setCurrentIndex(tab_index)
            # Update controller's active document
            self.controller.set_active_file(file_str)

        # Update window title
        self._update_window_title()

        # Emit signal
        self.file_opened.emit(file_str)

        print("[reamde] File opened successfully")
        return True

    def _on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request.

        Args:
            index: Index of tab to close
        """
        # Get file path before removing
        widget = self._tabs.widget(index)
        if isinstance(widget, MarkdownViewerTab) and widget.file_path:
            file_str = str(widget.file_path)

            # Notify controller to unregister file (don't check for modifications - user already closed)
            logger.info(f"Unregistering file from controller: {file_str}")
            self.controller.close_file(file_str, check_modified=False)

            # Remove from tracking
            if file_str in self._open_files:
                del self._open_files[file_str]

            # Emit signal
            self.tab_closed.emit(file_str)

        # Remove tab
        self._tabs.removeTab(index)

        # Update window title
        self._update_window_title()

        # Rebuild index mapping (indices change after removal)
        self._rebuild_file_index()

    def _rebuild_file_index(self) -> None:
        """Rebuild the file path to tab index mapping."""
        self._open_files.clear()

        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, MarkdownViewerTab) and widget.file_path:
                file_str = str(widget.file_path)
                self._open_files[file_str] = i

    def _on_current_tab_changed(self, index: int) -> None:
        """Handle current tab change.

        Args:
            index: New current tab index
        """
        # Trigger lazy loading for this tab if not already loaded
        if index >= 0:
            widget = self._tabs.widget(index)
            if isinstance(widget, MarkdownViewerTab):
                widget.ensure_loaded()
                # Update undo/redo action states for current tab
                self._update_undo_redo_states(widget)

        self._update_window_title()

    def _update_undo_action_state(self, available: bool) -> None:
        """Update undo action enabled state.

        Args:
            available: True if undo is available
        """
        if self._undo_action:
            self._undo_action.setEnabled(available)

    def _update_redo_action_state(self, available: bool) -> None:
        """Update redo action enabled state.

        Args:
            available: True if redo is available
        """
        if self._redo_action:
            self._redo_action.setEnabled(available)

    def _update_undo_redo_states(self, tab: MarkdownViewerTab) -> None:
        """Update undo/redo action states for given tab.

        Args:
            tab: The MarkdownViewerTab to check
        """
        if self._undo_action:
            self._undo_action.setEnabled(tab.editor.document().isUndoAvailable())
        if self._redo_action:
            self._redo_action.setEnabled(tab.editor.document().isRedoAvailable())

    def _on_tab_content_modified(self, tab: MarkdownViewerTab) -> None:
        """Handle tab content modification - add unsaved indicator to title.

        Args:
            tab: The MarkdownViewerTab that has unsaved changes
        """
        # Find tab index
        for i in range(self._tabs.count()):
            if self._tabs.widget(i) is tab:
                # Get current title
                current_title = self._tabs.tabText(i)
                # Add asterisk if not already present
                if not current_title.endswith(" *"):
                    self._tabs.setTabText(i, current_title + " *")
                break

    def _on_tab_content_saved(self, tab: MarkdownViewerTab) -> None:
        """Handle tab content saved - remove unsaved indicator from title.

        Args:
            tab: The MarkdownViewerTab that was saved
        """
        # Find tab index
        for i in range(self._tabs.count()):
            if self._tabs.widget(i) is tab:
                # Get current title
                current_title = self._tabs.tabText(i)
                # Remove asterisk if present
                if current_title.endswith(" *"):
                    self._tabs.setTabText(i, current_title[:-2])
                break

    def _on_tab_renamed(self, index: int, new_text: str) -> None:
        """Handle tab rename completion.

        Args:
            index: Tab index
            new_text: New tab title text
        """
        logger.info(f"Tab {index} renamed to: '{new_text}'")
        # The tab text has already been updated by ChromeTabbedWindow
        # We just log it for now. In the future, we could update file metadata, etc.

    def _update_window_title(self) -> None:
        """Update window title based on current tab."""
        current_index = self._tabs.currentIndex()

        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab) and widget.file_path:
                file_name = widget.file_path.name
                self.setWindowTitle(f"Reamde - {file_name}")
                return

        # No file open or no current tab
        self.setWindowTitle("Reamde - Markdown Viewer")

    def bring_to_front(self) -> None:
        """Activate and raise window to front."""
        # Show window if minimized
        if self.isMinimized():
            self.showNormal()

        # Activate and raise
        self.activateWindow()
        self.raise_()
        self.setFocus()

    def get_open_files(self) -> list[str]:
        """Get list of currently open file paths.

        Returns:
            List of file paths as strings
        """
        return list(self._open_files.keys())

    def close_file(self, file_path: str | Path) -> bool:
        """Close a file by path.

        Args:
            file_path: Path to file to close

        Returns:
            True if closed, False if not found
        """
        file_str = str(Path(file_path).resolve())

        if file_str in self._open_files:
            tab_index = self._open_files[file_str]
            self._tabs.removeTab(tab_index)
            self._rebuild_file_index()
            self._update_window_title()
            return True

        return False

    def _setup_file_menu(self) -> None:
        """Setup File menu using fluent API - clean and simple!"""
        file_menu = self.add_menu("&File")

        file_menu.add_action(
            "&Open...",
            self._on_open_file,
            "Ctrl+O",
            tooltip="Open a markdown file",
        )

        file_menu.add_action(
            "&Close",
            self._on_close_current_tab,
            "Ctrl+W",
            tooltip="Close the current tab",
        )

        file_menu.add_separator()

        # Workspace actions
        file_menu.add_action(
            "Open &Workspace Folder...",
            self._on_open_workspace_folder,
            "Ctrl+K,Ctrl+O",
            tooltip="Open a folder as workspace",
        )

        file_menu.add_action(
            "&Add Folder to Workspace...",
            self._on_add_folder_to_workspace,
            tooltip="Add a folder to workspace (creates new workspace if none exists)",
        )

        file_menu.add_separator()

        # Workspace file operations
        file_menu.add_action(
            "Open Workspace &File...",
            self._on_open_workspace_file,
            tooltip="Open a portable .reamde workspace file",
        )

        file_menu.add_action(
            "&Save Workspace File...",
            self._on_save_workspace_file,
            "Ctrl+K,S",
            tooltip="Save current workspace to .reamde file",
            enabled=False,  # Initially disabled
        )

        file_menu.add_separator()

        file_menu.add_action(
            "Close Workspace",
            self._on_close_workspace,
            tooltip="Close the current workspace",
            enabled=False,  # Initially disabled (enabled when workspace opens)
        )

        file_menu.add_separator()

        # Preferences
        file_menu.add_action(
            "&Preferences...",
            self._show_preferences_dialog,
            "Ctrl+,",
            tooltip="Configure application preferences",
        )

        file_menu.add_separator()

        file_menu.add_action(
            "E&xit",
            self.close,
            "Ctrl+Q",
            tooltip="Exit the application",
        )

        # WORKAROUND: Get references to workspace actions for enabling/disabling
        # This is a temporary solution until MenuBuilder V2 is implemented
        # (see docs/TODO-menubuilder-enhancement.md and menubuilder-api-v2-PROPOSAL.md)
        #
        # Future API will be:
        #   self._close_workspace_action = file_menu.add_action(
        #       "Close Workspace",
        #       callback,
        #       enabled=False,
        #       return_action=True  # Returns QAction instead of MenuBuilder
        #   )
        #
        # Current workaround: Find actions by text in menu.actions()
        menu_actions = file_menu._menu.actions()
        for action in menu_actions:
            if action.text() == "Close Workspace":
                self._close_workspace_action = action
            elif action.text() == "Save Workspace File...":
                self._save_workspace_file_action = action

    def _setup_edit_menu(self) -> None:
        """Setup Edit menu with undo/redo and view mode controls."""
        edit_menu = self.add_menu("&Edit")

        # Undo/Redo actions - disabled by default
        edit_menu.add_action(
            "&Undo",
            self._on_undo,
            "Ctrl+Z",
            tooltip="Undo last change",
            enabled=False,
        )

        edit_menu.add_action(
            "&Redo",
            self._on_redo,
            "Ctrl+Shift+Z",
            tooltip="Redo last undone change",
            enabled=False,
        )

        # Get QAction references from menu for dynamic enabling/disabling
        menu_actions = edit_menu._menu.actions()
        self._undo_action = menu_actions[0]  # First action
        self._redo_action = menu_actions[1]  # Second action

        edit_menu.add_separator()

        # View mode toggle
        edit_menu.add_action(
            "&Toggle Edit Mode",
            self._on_toggle_edit_mode,
            "Ctrl+E",
            tooltip="Toggle between preview and split editing view",
        )

        edit_menu.add_separator()

        edit_menu.add_action(
            "&Preview Only",
            self._on_preview_only,
            "Ctrl+Shift+P",
            tooltip="Show preview only",
        )

        edit_menu.add_action(
            "&Split View",
            self._on_split_view,
            "Ctrl+Shift+S",
            tooltip="Show preview and editor side-by-side",
        )

        edit_menu.add_action(
            "&Editor Only",
            self._on_editor_only,
            "Ctrl+Shift+E",
            tooltip="Show editor only",
        )

    def _setup_help_menu(self) -> None:
        """Setup Help menu with About action."""
        help_menu = self.add_menu("&Help")

        help_menu.add_action(
            "&About Reamde",
            self._show_about_dialog,
            tooltip="Show application information and version",
        )

    def _show_about_dialog(self) -> None:
        """Show About Reamde dialog."""
        from .components.about_dialog import AboutDialog

        dialog = AboutDialog(self)
        dialog.exec()
        logger.info("About dialog closed")

    def _on_undo(self) -> None:
        """Handle Edit > Undo action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                # Undo in the text editor
                widget.editor.undo()

    def _on_redo(self) -> None:
        """Handle Edit > Redo action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                # Redo in the text editor
                widget.editor.redo()

    def _on_toggle_edit_mode(self) -> None:
        """Handle Edit > Toggle Edit Mode action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                widget.toggle_edit_mode()

    def _on_preview_only(self) -> None:
        """Handle Edit > Preview Only action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                widget.set_view_mode(ViewMode.PREVIEW_ONLY)

    def _on_split_view(self) -> None:
        """Handle Edit > Split View action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                widget.set_view_mode(ViewMode.SPLIT_VIEW)

    def _on_editor_only(self) -> None:
        """Handle Edit > Editor Only action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                widget.set_view_mode(ViewMode.EDITOR_ONLY)

    def _on_open_file(self) -> None:
        """Handle File > Open action."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown *.mdown *.mkd);;All Files (*)",
        )

        if file_path:
            self.open_file(file_path)

    def _on_close_current_tab(self) -> None:
        """Handle File > Close action."""
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            self._on_tab_close_requested(current_index)

    def _on_open_workspace_folder(self) -> None:
        """Handle File > Open Workspace Folder action."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Open Workspace Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if folder_path:
            success = self.workspace_manager.open_folder(Path(folder_path))
            if success:
                logger.info(f"Opened workspace folder: {folder_path}")
                # Enable Close Workspace action
                if hasattr(self, "_close_workspace_action"):
                    self._close_workspace_action.setEnabled(True)
            else:
                logger.error(f"Failed to open workspace folder: {folder_path}")

    def _on_add_folder_to_workspace(self) -> None:
        """Handle File > Add Folder to Workspace action."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Add Folder to Workspace",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if folder_path:
            success = self.workspace_manager.add_folder(Path(folder_path))
            if success:
                logger.info(f"Added folder to workspace: {folder_path}")
            else:
                logger.error(f"Failed to add folder to workspace: {folder_path}")

    def _on_close_workspace(self) -> None:
        """Handle File > Close Workspace action."""
        self.workspace_manager.close_workspace()
        logger.info("Closed workspace")
        # Disable workspace actions
        if hasattr(self, "_close_workspace_action"):
            self._close_workspace_action.setEnabled(False)
        if hasattr(self, "_save_workspace_file_action"):
            self._save_workspace_file_action.setEnabled(False)

    def _on_open_workspace_file(self) -> None:
        """Handle File > Open Workspace File action."""
        from PySide6.QtWidgets import QFileDialog

        # Get file dialog filter from workspace manager
        file_filter = self.workspace_manager.workspace_widget._manager.get_file_dialog_filter()

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Workspace File", str(Path.home()), file_filter
        )

        if file_path:
            success = self.workspace_manager.load_workspace_file(Path(file_path))
            if success:
                logger.info(f"Opened workspace file: {file_path}")
                # Enable workspace actions
                if hasattr(self, "_close_workspace_action"):
                    self._close_workspace_action.setEnabled(True)
                if hasattr(self, "_save_workspace_file_action"):
                    self._save_workspace_file_action.setEnabled(True)
            else:
                logger.error(f"Failed to open workspace file: {file_path}")

    def _on_save_workspace_file(self) -> None:
        """Handle File > Save Workspace File action."""
        from PySide6.QtWidgets import QFileDialog

        # Check if workspace file path already known
        manager = self.workspace_manager.workspace_widget._manager
        current_file = manager.get_workspace_file_path()

        if current_file:
            # Save to current file
            success = self.workspace_manager.save_workspace_file(current_file)
            if success:
                logger.info(f"Saved workspace to: {current_file}")
        else:
            # Save As dialog
            file_filter = manager.get_file_dialog_filter()
            extension = manager.get_workspace_file_extension()
            default_name = f"workspace{extension}"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Workspace File", str(Path.home() / default_name), file_filter
            )

            if file_path:
                success = self.workspace_manager.save_workspace_file(Path(file_path))
                if success:
                    logger.info(f"Saved workspace to: {file_path}")
                else:
                    logger.error(f"Failed to save workspace file: {file_path}")

    def _show_preferences_dialog(self) -> None:
        """Show preferences dialog."""
        from .components.preferences_dialog import PreferencesDialog

        dialog = PreferencesDialog(self)
        dialog.preferences_applied.connect(self._apply_preferences)
        dialog.exec()

    def _apply_preferences(self, preferences) -> None:
        """Apply preferences to running application.

        Args:
            preferences: PreferencesModel with new settings
        """

        logger.info("Applying preferences to application")

        # Apply window opacity
        opacity = preferences.appearance.window_opacity / 100.0
        self.setWindowOpacity(opacity)
        logger.debug(f"Set window opacity to {opacity}")

        # Apply accent line settings (for ChromeTabbedWindow tabs)
        self._tabs.set_accent_line_visible(preferences.appearance.show_accent_line)
        if preferences.appearance.accent_line_color:
            self._tabs.set_accent_line_color(preferences.appearance.accent_line_color)
            logger.info(f"Applied accent line color: {preferences.appearance.accent_line_color}")

        # Apply title bar background color via user layer (like ViloxTerm)
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        theme_name = preferences.appearance.application_theme

        if preferences.appearance.top_bar_background_color:
            # Use customize_color to set "user" layer override
            if hasattr(app, "customize_color"):
                app.customize_color(
                    "titleBar.activeBackground",
                    preferences.appearance.top_bar_background_color,
                    persist=True,
                )
                logger.info(
                    f"Applied title bar background color: {preferences.appearance.top_bar_background_color}"
                )
        else:
            # Clear the override if color is empty
            if hasattr(app, "reset_color"):
                app.reset_color("titleBar.activeBackground", persist=True)
                logger.info("Cleared title bar background color override")

        # Apply theme with markdown overrides (title bar override is in user layer)
        from vfwidgets_common import apply_theme_with_overrides

        markdown_overrides = preferences.markdown.theme_overrides
        success = apply_theme_with_overrides(theme_name, markdown_overrides)
        if success:
            logger.info(f"Applied theme '{theme_name}' with markdown and title bar overrides")
        else:
            logger.warning(f"Failed to apply theme '{theme_name}' with overrides")

        # Apply markdown preferences to all open tabs
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, MarkdownViewerTab):
                # Apply toolbar visibility preference
                widget.set_toolbar_visible(preferences.markdown.show_view_mode_toolbar)
                # Future: widget.viewer.apply_preferences(preferences.markdown)

        logger.info("Preferences applied successfully")

    def _on_controller_file_opened(self, file_path: str) -> None:
        """Handle controller file_opened signal - open file in UI.

        Args:
            file_path: Path to file that was opened by controller
        """
        logger.info(f"Controller opened file, creating tab: {file_path}")
        # Use existing open_file method to create tab
        # This is called when controller.restore_session() opens files
        self.open_file(file_path, focus=False)

    def _on_controller_file_closed(self, file_path: str) -> None:
        """Handle controller file_closed signal - close file in UI.

        Args:
            file_path: Path to file that was closed by controller
        """
        logger.info(f"Controller closed file, removing tab: {file_path}")
        # Close the tab (without asking for confirmation as controller already handled it)
        self.close_file(file_path)

    def _on_session_restored(self) -> None:
        """Handle session_restored signal - load view modes and ensure active tab loads content.

        After session restoration, all tabs are created but content is not loaded
        (lazy loading). This triggers content load for the currently active tab
        and applies saved view modes to all tabs.
        """
        logger.info("Session restored, applying view modes and loading active tab content")

        # Load session state to get view modes
        session_state = self.controller.session_manager.load_session()
        if session_state and session_state.view_modes:
            # Apply view modes to existing tabs
            for file_path, view_mode_str in session_state.view_modes.items():
                if file_path in self._open_files:
                    tab_index = self._open_files[file_path]
                    widget = self._tabs.widget(tab_index)
                    if isinstance(widget, MarkdownViewerTab):
                        try:
                            # Convert string to ViewMode enum
                            view_mode = ViewMode(view_mode_str)
                            widget.set_view_mode(view_mode)
                            logger.info(f"Restored view mode '{view_mode_str}' for {file_path}")
                        except ValueError:
                            logger.warning(f"Invalid view mode '{view_mode_str}' for {file_path}")

        # Ensure active tab content is loaded
        current_index = self._tabs.currentIndex()
        if current_index >= 0:
            widget = self._tabs.widget(current_index)
            if isinstance(widget, MarkdownViewerTab):
                widget.ensure_loaded()

    def _apply_startup_preferences(self) -> None:
        """Apply preferences on application startup."""
        logger.info("Applying startup preferences")

        # Apply window opacity
        opacity = self.preferences.appearance.window_opacity / 100.0
        self.setWindowOpacity(opacity)
        logger.debug(f"Set window opacity to {opacity}")

        # Note: Topbar colors will be applied after _setup_tabbed_content() creates self._tabs
        # They are applied in _apply_topbar_preferences() called after tab setup

        # Apply theme with markdown color overrides
        from vfwidgets_common import apply_theme_with_overrides

        theme_name = self.preferences.appearance.application_theme
        markdown_overrides = self.preferences.markdown.theme_overrides

        success = apply_theme_with_overrides(theme_name, markdown_overrides)
        if success:
            logger.info(f"Applied startup theme '{theme_name}' with markdown overrides")
        else:
            logger.warning(f"Failed to apply startup theme '{theme_name}' with overrides")

        # Session restoration is already handled by controller
        # (uses its own SessionManager)

        logger.info("Startup preferences applied")

    def _on_workspace_opened(self, folders: list) -> None:
        """Handle workspace opened event.

        Args:
            folders: List of workspace folder objects
        """
        logger.info(f"Workspace opened with {len(folders)} folders")

        # Enable workspace actions
        if hasattr(self, "_close_workspace_action"):
            self._close_workspace_action.setEnabled(True)
        if hasattr(self, "_save_workspace_file_action"):
            self._save_workspace_file_action.setEnabled(True)

        # Update window title to show workspace context
        self._update_window_title()

    def _on_workspace_closed(self) -> None:
        """Handle workspace closed event."""
        logger.info("Workspace closed")

        # Disable Close Workspace action
        if hasattr(self, "_close_workspace_action"):
            self._close_workspace_action.setEnabled(False)

        # Update window title to remove workspace context
        self._update_window_title()

    def _on_activity_item_clicked(self, item_id: str) -> None:
        """Handle activity bar item click.

        Args:
            item_id: ID of clicked activity item
        """
        # Show the corresponding sidebar panel
        if item_id == "files":
            self.show_sidebar_panel("files")
            logger.debug("Showed files sidebar panel")

    def closeEvent(self, event) -> None:
        """Handle window close event - save session with view modes before closing.

        Args:
            event: QCloseEvent
        """
        logger.info("Window closing, collecting view modes and saving session...")

        # Collect view modes from all tabs
        view_modes = {}
        for file_path, tab_index in self._open_files.items():
            widget = self._tabs.widget(tab_index)
            if isinstance(widget, MarkdownViewerTab):
                view_mode = widget.get_view_mode()
                view_modes[file_path] = view_mode.value
                logger.debug(f"Saving view mode '{view_mode.value}' for {file_path}")

        # Save current session (collects fresh workspace state, open files, etc.)
        self.controller.save_session()

        # Now update with view modes if needed
        if view_modes:
            session_state = self.controller.session_manager.load_session()
            if session_state:
                session_state.view_modes = view_modes
                self.controller.session_manager.save_session(session_state)
                logger.info(f"Session saved with {len(view_modes)} view modes and workspace state")

        # Accept close event
        super().closeEvent(event)
