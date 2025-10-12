"""ReamdeWindow - Main application window using ViloCodeWindow."""

from pathlib import Path
from typing import Optional

from chrome_tabbed_window import ChromeTabbedWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from vfwidgets_markdown import MarkdownViewer
from vfwidgets_vilocode_window import ViloCodeWindow


class MarkdownViewerTab(QWidget):
    """Wrapper for MarkdownViewer with file path tracking."""

    def __init__(self, file_path: Optional[Path] = None, parent: Optional[QWidget] = None):
        """Initialize the markdown viewer tab.

        Args:
            file_path: Path to markdown file to load
            parent: Parent widget
        """
        print(f"[reamde] MarkdownViewerTab.__init__() called, file_path={file_path}")
        super().__init__(parent)

        self.file_path = file_path

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

        # Load file if provided - MarkdownViewer handles queueing automatically
        if file_path:
            print("[reamde] Loading file (will be queued if viewer not ready yet)...")
            self.load_file(file_path)

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
        else:
            print("[reamde] Failed to load file")

        return success

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

        # Setup tabbed content area
        self._setup_tabbed_content()

        # Setup file menu
        self._setup_file_menu()

    # showEvent workaround removed - no longer needed with fluent API's automatic theme integration!

    def _setup_tabbed_content(self) -> None:
        """Setup ChromeTabbedWindow in main content area."""
        # Create tabbed window as embedded widget (pass self as parent)
        self._tabs = ChromeTabbedWindow(parent=self)
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.setDocumentMode(True)

        # Connect signals
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tabs.currentChanged.connect(self._on_current_tab_changed)

        # Set as main content
        self.set_main_content(self._tabs)

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
        # Create new tab
        tab = MarkdownViewerTab(file_path)
        tab_title = file_path.name
        print(f"[reamde] Adding tab '{tab_title}'...")
        tab_index = self._tabs.addTab(tab, tab_title)
        print(f"[reamde] Tab added at index {tab_index}")

        # Set tooltip to full path
        self._tabs.setTabToolTip(tab_index, str(file_path))

        # Track open file
        self._open_files[file_str] = tab_index

        # Focus new tab
        if focus:
            print(f"[reamde] Setting current tab to {tab_index}")
            self._tabs.setCurrentIndex(tab_index)

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

        # Theme Preferences (if available)
        try:
            from vfwidgets_theme.widgets.dialogs import ThemePickerDialog

            file_menu.add_action(
                "Theme &Preferences...",
                lambda: ThemePickerDialog(self).exec(),
                tooltip="Configure application theme",
            )
        except ImportError:
            pass

        file_menu.add_separator()

        file_menu.add_action(
            "E&xit",
            self.close,
            "Ctrl+Q",
            tooltip="Exit the application",
        )

    def _on_open_file(self) -> None:
        """Handle File > Open action."""
        from PySide6.QtWidgets import QFileDialog

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

    # _on_theme_preferences removed - simplified to lambda in menu setup
