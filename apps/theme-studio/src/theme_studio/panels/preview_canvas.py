"""Preview Canvas Panel - Center panel for widget preview."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class PreviewCanvasPanel(QWidget):
    """Preview canvas panel - displays themed widget previews.

    Phase 1: Basic canvas with plugin selector and scroll area
    Phase 2: Add zoom controls and state simulation

    The canvas will host widgets from selected plugins that demonstrate
    the current theme's appearance.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_plugin = None
        self._current_plugin_ref = None  # Store plugin reference for metadata access
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with toolbar and canvas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar at top
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scroll area for preview content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Content widget (will be set by plugins in Task 4.2-4.3)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Placeholder label (will be removed when plugin sets content)
        self.placeholder_label = QLabel(
            "No plugin selected\n\n"
            "Select a widget plugin from the dropdown above\n"
            "to preview themed widgets."
        )
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: gray; font-size: 12px;")
        self.content_layout.addWidget(self.placeholder_label)
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def _create_toolbar(self):
        """Create toolbar with plugin selector.

        Returns:
            QWidget: Toolbar widget
        """
        toolbar = QWidget()
        toolbar.setFixedHeight(36)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)

        # Plugin selector
        plugin_label = QLabel("Plugin:")
        toolbar_layout.addWidget(plugin_label)

        self.plugin_selector = QComboBox()
        self.plugin_selector.setMinimumWidth(200)
        self.plugin_selector.addItem("(None)")
        # Plugins will be added in Task 4.3
        self.plugin_selector.currentTextChanged.connect(self._on_plugin_changed)
        toolbar_layout.addWidget(self.plugin_selector)

        toolbar_layout.addStretch()

        # Zoom controls (placeholder for Phase 2)
        zoom_label = QLabel("Zoom: 100%")
        zoom_label.setStyleSheet("color: gray;")
        toolbar_layout.addWidget(zoom_label)

        return toolbar

    def _on_plugin_changed(self, plugin_name: str):
        """Handle plugin selection change.

        Args:
            plugin_name: Selected plugin name
        """
        # Will be implemented in Task 4.3 when plugins are integrated
        pass

    def set_plugin_content(self, content_widget: QWidget, plugin_ref=None):
        """Set content widget from plugin.

        This method will be called by the plugin system (Task 4.3) to
        display the plugin's widget preview.

        Args:
            content_widget: Widget to display in canvas
            plugin_ref: Optional plugin reference for metadata access
        """
        # Remove placeholder if present
        if self.placeholder_label:
            self.placeholder_label.hide()
            self.content_layout.removeWidget(self.placeholder_label)
            self.placeholder_label = None

        # Remove current plugin widget if any
        if self._current_plugin:
            try:
                self.content_layout.removeWidget(self._current_plugin)
                self._current_plugin.hide()
                self._current_plugin.setParent(None)
                self._current_plugin.deleteLater()
            except RuntimeError:
                # Widget already deleted
                pass
            finally:
                self._current_plugin = None

        # Clear the layout completely (removes stretch items too)
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new plugin widget - it will expand to fill available space
        self._current_plugin = content_widget
        self._current_plugin_ref = plugin_ref  # Store plugin reference for metadata access
        self.content_layout.addWidget(content_widget)

    def clear_content(self):
        """Clear canvas content."""
        if self._current_plugin:
            try:
                # Remove from layout first
                self.content_layout.removeWidget(self._current_plugin)
                # Hide immediately to prevent further access
                self._current_plugin.hide()
                # Set parent to None to break parent-child relationship
                self._current_plugin.setParent(None)
                # Schedule for deletion
                self._current_plugin.deleteLater()
            except RuntimeError:
                # Widget already deleted
                pass
            finally:
                # Clear references immediately
                self._current_plugin = None
                self._current_plugin_ref = None

        # Show placeholder
        if not self.placeholder_label:
            self.placeholder_label = QLabel(
                "No plugin selected\n\n"
                "Select a widget plugin from the dropdown above\n"
                "to preview themed widgets."
            )
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.placeholder_label.setStyleSheet("color: gray; font-size: 12px;")
            self.content_layout.addWidget(self.placeholder_label)

    def apply_canvas_theme(self, background_color: str, foreground_color: str):
        """Apply theme colors to the canvas background.

        This makes the entire preview pane visually reflect the theme,
        not just the plugin widget.

        Args:
            background_color: Background color hex string (e.g., "#1e1e1e")
            foreground_color: Foreground color hex string (e.g., "#d4d4d4")
        """
        # Apply to scroll area viewport (the visible area)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {background_color};
                border: none;
            }}
        """)

        # Apply to content widget (the container)
        self.content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {foreground_color};
            }}
        """)
