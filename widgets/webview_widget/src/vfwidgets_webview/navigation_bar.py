"""Navigation bar with URL input and navigation buttons.

This module provides a complete navigation bar for web browsing, including:
- Back/Forward/Reload/Home buttons
- URL bar with autocomplete
- Loading progress indicator

Educational Focus:
    This code demonstrates:
    - Creating custom toolbars in Qt
    - QLineEdit for URL input
    - QPushButton styling and icons
    - QProgressBar for loading indicators
    - Signal/slot communication patterns
    - Layout management (QHBoxLayout)
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class NavigationBar(QWidget):
    """Navigation bar with URL input and control buttons.

    This widget provides a complete navigation interface including:
    - Back button (◄)
    - Forward button (►)
    - Reload/Stop button (⟲/✕)
    - Home button (🏠)
    - URL bar (text input)
    - Loading progress bar

    Educational Note:
        This demonstrates how to build a custom toolbar widget by:
        1. Composing multiple Qt widgets (buttons, line edit, progress bar)
        2. Using layouts to arrange them (QHBoxLayout, QVBoxLayout)
        3. Emitting signals when user interacts
        4. Managing widget state (enabled/disabled buttons)

        Think of this as a "control panel" for the web view.

    Example:
        >>> navbar = NavigationBar()
        >>> navbar.url_submitted.connect(on_navigate)
        >>> navbar.back_clicked.connect(on_back)
        >>> navbar.set_url("https://example.com")

    Signals:
        back_clicked: User clicked back button
        forward_clicked: User clicked forward button
        reload_clicked: User clicked reload button
        stop_clicked: User clicked stop button
        home_clicked: User clicked home button
        url_submitted(str): User pressed Enter in URL bar

    Layout:
        ┌────────────────────────────────────────────┐
        │ [◄] [►] [⟲] [🏠]  https://example.com     │
        ├────────────────────────────────────────────┤
        │ ████████████────── 67%                     │
        └────────────────────────────────────────────┘
    """

    # Signals emitted when user interacts with navigation controls
    back_clicked = Signal()
    forward_clicked = Signal()
    reload_clicked = Signal()
    stop_clicked = Signal()
    home_clicked = Signal()
    url_submitted = Signal(str)  # Emitted with the URL when Enter is pressed

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize navigation bar.

        Educational Note:
            Widget initialization order:
            1. Call super().__init__()
            2. Create child widgets (buttons, line edit, etc.)
            3. Setup layout
            4. Connect signals
            5. Set initial state

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Track loading state (determines if we show reload or stop button)
        self._is_loading = False

        # Create UI components
        self._create_buttons()
        self._create_url_bar()
        self._create_progress_bar()

        # Setup layout
        self._setup_layout()

        # Connect internal signals
        self._connect_signals()

        # Set size policy: expand horizontally, fixed vertically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        logger.debug("NavigationBar initialized")

    def _create_buttons(self) -> None:
        """Create navigation buttons.

        Educational Note:
            QPushButton is the standard Qt button widget.
            We create multiple buttons and will arrange them in a layout.

            Button text can be:
            - Plain text: "Back"
            - Unicode symbols: "◄", "►", "⟲"
            - Icons: QIcon (more professional)

            For this educational widget, we use unicode symbols for simplicity.
            Production browsers typically use icon files.
        """
        # Back button
        self.back_button = QPushButton("◄", self)
        self.back_button.setToolTip("Go back (Alt+Left)")
        self.back_button.setEnabled(False)  # Disabled until we have history
        self.back_button.setFixedSize(40, 32)  # Fixed width and height

        # Forward button
        self.forward_button = QPushButton("►", self)
        self.forward_button.setToolTip("Go forward (Alt+Right)")
        self.forward_button.setEnabled(False)
        self.forward_button.setFixedSize(40, 32)

        # Reload/Stop button (changes based on loading state)
        self.reload_button = QPushButton("⟲", self)
        self.reload_button.setToolTip("Reload page (Ctrl+R)")
        self.reload_button.setFixedSize(40, 32)

        # Home button
        self.home_button = QPushButton("🏠", self)
        self.home_button.setToolTip("Go to home page")
        self.home_button.setFixedSize(40, 32)

        logger.debug("Navigation buttons created")

    def _create_url_bar(self) -> None:
        """Create URL input field.

        Educational Note:
            QLineEdit is a single-line text input widget.
            Perfect for URL entry because:
            - Supports text selection
            - Supports copy/paste
            - Can show placeholder text
            - Emits signals when user presses Enter

            In a production browser, you'd add:
            - Autocomplete (QCompleter)
            - URL validation
            - Search engine integration
            - Security indicators (HTTPS padlock)
        """
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter URL or search...")
        self.url_bar.setFixedHeight(32)  # Match button height

        # Make URL bar expand horizontally to fill available space
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Clear focus outline for cleaner look
        self.url_bar.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #0066cc;
            }
        """
        )

        logger.debug("URL bar created")

    def _create_progress_bar(self) -> None:
        """Create loading progress indicator.

        Educational Note:
            QProgressBar shows progress from 0-100%.
            We use it to show page loading progress.

            We hide it when not loading to save space.
            This is common in modern browsers (progress shown in address bar).
        """
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Don't show "67%" text
        self.progress_bar.setFixedHeight(3)  # Thin progress bar

        # Hide initially
        self.progress_bar.setVisible(False)

        logger.debug("Progress bar created")

    def _setup_layout(self) -> None:
        """Arrange widgets in layout.

        Educational Note:
            Qt layouts automatically position and size widgets.

            QHBoxLayout: Horizontal arrangement (left to right)
            QVBoxLayout: Vertical arrangement (top to bottom)

            Our layout:
            - Top row: buttons + URL bar (QHBoxLayout)
            - Bottom row: progress bar (below everything)
            - Container: QVBoxLayout to stack them vertically
        """
        # Main vertical layout (stacks navigation + progress)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 0)  # Minimal padding, no bottom margin
        main_layout.setSpacing(0)  # No space between rows

        # Navigation row (horizontal: buttons + URL bar)
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)  # Space between buttons
        nav_layout.setContentsMargins(0, 0, 0, 0)  # No margins on nav row
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.reload_button)
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.url_bar)  # Expands to fill space

        # Add layouts to main layout
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.progress_bar)

        logger.debug("Layout configured")

    def _connect_signals(self) -> None:
        """Connect button clicks to signals.

        Educational Note:
            Signal/slot connection pattern:
            widget.signal.connect(handler)

            When button is clicked:
            1. QPushButton emits clicked signal
            2. Our handler receives it
            3. We emit our own signal for parent to handle

            Why forward signals?
            - Keeps implementation details hidden
            - Parent doesn't need to know about our buttons
            - We can add logic before emitting (e.g., validation)
        """
        # Connect buttons to our signal handlers
        self.back_button.clicked.connect(self._on_back_clicked)
        self.forward_button.clicked.connect(self._on_forward_clicked)
        self.reload_button.clicked.connect(self._on_reload_stop_clicked)
        self.home_button.clicked.connect(self._on_home_clicked)

        # Connect URL bar Enter key to submission
        self.url_bar.returnPressed.connect(self._on_url_submitted)

        logger.debug("Signals connected")

    # ===== Signal Handlers =====
    # These methods are called when user interacts with the navigation bar

    @Slot()
    def _on_back_clicked(self) -> None:
        """Handle back button click."""
        logger.debug("Back button clicked")
        self.back_clicked.emit()

    @Slot()
    def _on_forward_clicked(self) -> None:
        """Handle forward button click."""
        logger.debug("Forward button clicked")
        self.forward_clicked.emit()

    @Slot()
    def _on_reload_stop_clicked(self) -> None:
        """Handle reload/stop button click.

        Educational Note:
            This button has dual purpose:
            - When NOT loading: Shows ⟲ (reload)
            - When loading: Shows ✕ (stop)

            We check our internal state to determine which signal to emit.
        """
        if self._is_loading:
            logger.debug("Stop button clicked")
            self.stop_clicked.emit()
        else:
            logger.debug("Reload button clicked")
            self.reload_clicked.emit()

    @Slot()
    def _on_home_clicked(self) -> None:
        """Handle home button click."""
        logger.debug("Home button clicked")
        self.home_clicked.emit()

    @Slot()
    def _on_url_submitted(self) -> None:
        """Handle URL submission (Enter key pressed).

        Educational Note:
            QLineEdit emits returnPressed when user presses Enter.
            We get the text, emit it in our signal, and clear focus.

            Clearing focus returns focus to the web view, so user can
            immediately interact with the page without clicking.
        """
        url = self.url_bar.text().strip()

        if not url:
            logger.debug("Empty URL submitted, ignoring")
            return

        logger.info(f"URL submitted: {url}")
        self.url_submitted.emit(url)

        # Clear focus from URL bar (return focus to page)
        self.url_bar.clearFocus()

    # ===== Public API =====
    # These methods are called by the parent widget (BrowserWidget)

    def set_url(self, url: str) -> None:
        """Set URL in URL bar (doesn't trigger navigation).

        This is called when the page URL changes (e.g., after clicking a link).
        We update the URL bar to reflect the current page.

        Educational Note:
            We block signals temporarily to avoid infinite loops:
            1. Page navigates → URL changes
            2. We update URL bar
            3. Without blocking, this would emit url_submitted
            4. Which would navigate again → infinite loop!

        Args:
            url: URL to display
        """
        # Block signals while updating to avoid triggering navigation
        self.url_bar.blockSignals(True)
        self.url_bar.setText(url)
        self.url_bar.blockSignals(False)

        logger.debug(f"URL bar updated: {url}")

    def set_progress(self, progress: int) -> None:
        """Set loading progress (0-100).

        Args:
            progress: Loading progress percentage
        """
        progress = max(0, min(100, progress))  # Clamp to 0-100

        self.progress_bar.setValue(progress)

        # Show progress bar when loading
        if progress > 0 and progress < 100:
            self.progress_bar.setVisible(True)
        elif progress == 100:
            # Hide progress bar after short delay when done
            # (gives user time to see completion)
            self.progress_bar.setVisible(False)

        logger.debug(f"Progress updated: {progress}%")

    def set_loading(self, loading: bool) -> None:
        """Set loading state (changes reload button to stop button).

        Educational Note:
            When loading:
            - Show stop button (✕) to cancel loading
            - Show progress bar
            - Disable some buttons to prevent confusion

            When not loading:
            - Show reload button (⟲) to refresh page
            - Hide progress bar
            - Enable buttons

        Args:
            loading: True if page is loading
        """
        self._is_loading = loading

        if loading:
            # Change to stop button
            self.reload_button.setText("✕")
            self.reload_button.setToolTip("Stop loading (Esc)")
            self.progress_bar.setVisible(True)
            logger.debug("Navigation bar switched to loading state")
        else:
            # Change to reload button
            self.reload_button.setText("⟲")
            self.reload_button.setToolTip("Reload page (Ctrl+R)")
            self.progress_bar.setVisible(False)
            logger.debug("Navigation bar switched to idle state")

    def set_back_enabled(self, enabled: bool) -> None:
        """Enable/disable back button.

        Args:
            enabled: True if back navigation is possible
        """
        self.back_button.setEnabled(enabled)
        logger.debug(f"Back button {'enabled' if enabled else 'disabled'}")

    def set_forward_enabled(self, enabled: bool) -> None:
        """Enable/disable forward button.

        Args:
            enabled: True if forward navigation is possible
        """
        self.forward_button.setEnabled(enabled)
        logger.debug(f"Forward button {'enabled' if enabled else 'disabled'}")

    def focus_url_bar(self) -> None:
        """Give focus to URL bar and select all text.

        Educational Note:
            This is useful for keyboard shortcuts like Ctrl+L
            (focus URL bar in most browsers).

            Selecting all text allows user to immediately start typing
            without having to manually select/delete the old URL.
        """
        self.url_bar.setFocus()
        self.url_bar.selectAll()
        logger.debug("URL bar focused")

    def get_url(self) -> str:
        """Get current text in URL bar.

        Returns:
            Current URL bar text
        """
        return self.url_bar.text()

    # ===== Keyboard Shortcuts =====

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle keyboard shortcuts.

        Educational Note:
            keyPressEvent is called when user presses a key while
            this widget (or a child) has focus.

            Common browser shortcuts:
            - Ctrl+L: Focus URL bar
            - Alt+Left: Back
            - Alt+Right: Forward
            - Ctrl+R: Reload
            - Esc: Stop loading

        Args:
            event: Key event
        """
        # Ctrl+L: Focus URL bar
        if event.key() == Qt.Key.Key_L and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.focus_url_bar()
            event.accept()
            return

        # Let parent handle other shortcuts
        super().keyPressEvent(event)
