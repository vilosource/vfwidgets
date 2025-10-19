"""ReamdeWindow - Main application window using ViloCodeWindow."""

from pathlib import Path
from typing import Optional

from chrome_tabbed_window import ChromeTabbedWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QWidget
from vfwidgets_markdown import MarkdownViewer
from vfwidgets_vilocode_window import ViloCodeWindow

from .controllers import WindowController
from .utils.logging_setup import get_logger

logger = get_logger(__name__)


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
    """Wrapper for MarkdownViewer with file path tracking.

    Supports lazy loading - content is only loaded when ensure_loaded() is called,
    allowing tabs to be created without immediately rendering content.
    """

    def __init__(
        self,
        file_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
        load_content: bool = True,
    ):
        """Initialize the markdown viewer tab.

        Args:
            file_path: Path to markdown file to load
            parent: Parent widget
            load_content: If False, defer loading until ensure_loaded() is called
        """
        print(f"[reamde] MarkdownViewerTab.__init__() called, file_path={file_path}")
        super().__init__(parent)

        self.file_path = file_path
        self._content_loaded = False  # Track if content has been loaded

        print("[reamde] Creating MarkdownViewer widget...")
        self.viewer = MarkdownViewer(parent=self)
        print(f"[reamde] MarkdownViewer created: {self.viewer}")

        # Layout
        from PySide6.QtWidgets import QVBoxLayout

        print("[reamde] Setting up layout...")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.viewer)
        print("[reamde] Layout complete, viewer added to layout")

        # Set dark background on tab container to prevent white flash
        # (matches approach in ViloxTerm)
        self.setStyleSheet("QWidget { background-color: #1a1a1a; }")

        # Load file if provided and load_content=True
        # Otherwise content is loaded lazily when tab becomes visible
        if file_path and load_content:
            print("[reamde] Loading file immediately...")
            self.load_file(file_path)
        elif file_path:
            print("[reamde] Deferring file load (lazy loading enabled)")

    def load_file(self, file_path: Path) -> bool:
        """Load markdown file into viewer.

        Args:
            file_path: Path to markdown file

        Returns:
            True if loaded successfully, False otherwise
        """
        print(f"[reamde] Loading file: {file_path}")
        self.file_path = file_path

        # Use MarkdownViewer's built-in load_file which handles:
        # - Reading the file
        # - Setting content
        # - Setting base path for relative images
        # - Queueing if viewer not ready yet
        success = self.viewer.load_file(file_path)

        if success:
            print("[reamde] File loaded successfully")
            self._content_loaded = True
        else:
            print("[reamde] Failed to load file")

        return success

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
            show_activity_bar=False,
            show_sidebar=False,
            show_auxiliary_bar=False,
        )

        # Set window title
        self.setWindowTitle("Reamde - Markdown Viewer")
        self.resize(1200, 800)

        # Track open files to prevent duplicates
        self._open_files: dict[str, int] = {}  # file_path -> tab_index

        # Initialize controller for session management and file operations
        self.controller = WindowController(parent=self)
        logger.info("WindowController initialized")

        # Load and apply preferences
        from .preferences_manager import PreferencesManager

        self.prefs_manager = PreferencesManager()
        self.preferences = self.prefs_manager.load_preferences()
        self._apply_startup_preferences()

        # Setup tabbed content area
        self._setup_tabbed_content()

        # Setup file menu
        self._setup_file_menu()

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

        # Connect tab signals
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tabs.currentChanged.connect(self._on_current_tab_changed)
        self._tabs.open_file_requested.connect(
            self._on_open_file
        )  # Connect '+' button to file dialog

        # Connect controller signals to UI updates
        self.controller.file_opened.connect(self._on_controller_file_opened)
        self.controller.file_closed.connect(self._on_controller_file_closed)
        self.controller.session_restored.connect(self._on_session_restored)

        # Set as main content
        self.set_main_content(self._tabs)

        # Apply topbar preferences (now that self._tabs exists)
        self._apply_topbar_preferences()

    def _apply_topbar_preferences(self) -> None:
        """Apply topbar appearance preferences to the tabbed window."""
        # Apply top bar background color (if set)
        if self.preferences.appearance.top_bar_background_color:
            self._tabs.set_tab_bar_background_color(
                self.preferences.appearance.top_bar_background_color
            )
            logger.info(
                f"Applied top bar color: {self.preferences.appearance.top_bar_background_color}"
            )

        # Apply accent line settings
        self._tabs.set_accent_line_visible(self.preferences.appearance.show_accent_line)
        if self.preferences.appearance.accent_line_color:
            self._tabs.set_accent_line_color(self.preferences.appearance.accent_line_color)
            logger.info(
                f"Applied accent line color: {self.preferences.appearance.accent_line_color}"
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
        tab = MarkdownViewerTab(file_path, load_content=focus)
        tab_title = file_path.name
        print(f"[reamde] Adding tab '{tab_title}'...")
        tab_index = self._tabs.addTab(tab, tab_title)
        print(f"[reamde] Tab added at index {tab_index}")

        # Set tooltip to full path
        self._tabs.setTabToolTip(tab_index, str(file_path))

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

        self._update_window_title()

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

        # Apply topbar background color (if set)
        if preferences.appearance.top_bar_background_color:
            self._tabs.set_tab_bar_background_color(preferences.appearance.top_bar_background_color)
            logger.info(f"Applied top bar color: {preferences.appearance.top_bar_background_color}")

        # Apply accent line settings
        self._tabs.set_accent_line_visible(preferences.appearance.show_accent_line)
        if preferences.appearance.accent_line_color:
            self._tabs.set_accent_line_color(preferences.appearance.accent_line_color)
            logger.info(f"Applied accent line color: {preferences.appearance.accent_line_color}")

        # Apply theme with markdown color overrides
        from vfwidgets_common import apply_theme_with_overrides

        theme_name = preferences.appearance.application_theme
        markdown_overrides = preferences.markdown.theme_overrides

        success = apply_theme_with_overrides(theme_name, markdown_overrides)
        if success:
            logger.info(f"Applied theme '{theme_name}' with markdown overrides")
        else:
            logger.warning(f"Failed to apply theme '{theme_name}' with overrides")

        # TODO: Apply markdown preferences to all open tabs
        # This would require MarkdownViewer.apply_preferences() method
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, MarkdownViewerTab):
                # Future: widget.viewer.apply_preferences(preferences.markdown)
                pass

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
        """Handle session_restored signal - ensure active tab loads content.

        After session restoration, all tabs are created but content is not loaded
        (lazy loading). This triggers content load for the currently active tab.
        """
        logger.info("Session restored, loading active tab content")
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

    def closeEvent(self, event) -> None:
        """Handle window close event - save session before closing.

        Args:
            event: QCloseEvent
        """
        logger.info("Window closing, saving session...")
        # Save current session (open files, active tab)
        self.controller.save_session()
        # Accept close event
        super().closeEvent(event)
