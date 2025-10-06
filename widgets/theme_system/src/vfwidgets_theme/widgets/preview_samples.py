"""Preview Sample Widget Generator - Theme Editor Component.

This module generates sample widgets for theme preview.

Phase 3: Live Preview
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..logging import get_debug_logger
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class PreviewSampleGenerator(ThemedWidget, QWidget):
    """Generate sample widgets for theme preview.

    Creates a comprehensive preview showing:
    - Buttons (default, primary, danger, success, disabled)
    - Inputs (line edit, text edit, spin box)
    - Lists and trees
    - Tabs
    - Progress bars and sliders
    - Checkboxes and radio buttons

    All widgets are themed and update in real-time.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize preview sample generator.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Setup UI
        self._setup_ui()

        logger.debug("PreviewSampleGenerator initialized")

    def _setup_ui(self) -> None:
        """Setup user interface with sample widgets."""
        # Use scroll area for all samples
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for samples
        container = QWidget()
        layout = QVBoxLayout(container)

        # Add sample groups
        layout.addWidget(self._create_button_samples())
        layout.addWidget(self._create_input_samples())
        layout.addWidget(self._create_list_samples())
        layout.addWidget(self._create_tab_samples())
        layout.addWidget(self._create_control_samples())
        layout.addWidget(self._create_editor_sample())

        layout.addStretch()

        scroll.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_button_samples(self) -> QWidget:
        """Create button samples.

        Returns:
            Widget with button samples

        """
        group = QGroupBox("Buttons")
        layout = QHBoxLayout(group)

        # Default button
        default_btn = QPushButton("Default")
        layout.addWidget(default_btn)

        # Primary button
        primary_btn = QPushButton("Primary")
        primary_btn.setProperty("role", "primary")
        layout.addWidget(primary_btn)

        # Danger button
        danger_btn = QPushButton("Danger")
        danger_btn.setProperty("role", "danger")
        layout.addWidget(danger_btn)

        # Success button
        success_btn = QPushButton("Success")
        success_btn.setProperty("role", "success")
        layout.addWidget(success_btn)

        # Disabled button
        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)
        layout.addWidget(disabled_btn)

        layout.addStretch()

        return group

    def _create_input_samples(self) -> QWidget:
        """Create input samples.

        Returns:
            Widget with input samples

        """
        group = QGroupBox("Inputs")
        layout = QGridLayout(group)

        # Line edit
        layout.addWidget(QLabel("Line Edit:"), 0, 0)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter text...")
        layout.addWidget(line_edit, 0, 1)

        # Line edit (focused simulation)
        layout.addWidget(QLabel("Focused:"), 1, 0)
        focused_edit = QLineEdit("Focused input")
        focused_edit.setFocus()
        layout.addWidget(focused_edit, 1, 1)

        # Disabled line edit
        layout.addWidget(QLabel("Disabled:"), 2, 0)
        disabled_edit = QLineEdit("Disabled input")
        disabled_edit.setEnabled(False)
        layout.addWidget(disabled_edit, 2, 1)

        # Spin box
        layout.addWidget(QLabel("Spin Box:"), 3, 0)
        spin = QSpinBox()
        spin.setValue(42)
        layout.addWidget(spin, 3, 1)

        # Combo box
        layout.addWidget(QLabel("Combo Box:"), 4, 0)
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(combo, 4, 1)

        return group

    def _create_list_samples(self) -> QWidget:
        """Create list samples.

        Returns:
            Widget with list samples

        """
        group = QGroupBox("Lists")
        layout = QVBoxLayout(group)

        list_widget = QListWidget()
        list_widget.addItems(
            [
                "List Item 1",
                "List Item 2 (Selected)",
                "List Item 3",
                "List Item 4",
                "List Item 5",
            ]
        )
        list_widget.setCurrentRow(1)  # Select second item
        list_widget.setMaximumHeight(120)
        layout.addWidget(list_widget)

        return group

    def _create_tab_samples(self) -> QWidget:
        """Create tab samples.

        Returns:
            Widget with tab samples

        """
        group = QGroupBox("Tabs")
        layout = QVBoxLayout(group)

        tabs = QTabWidget()

        # Tab 1
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("Content of Tab 1"))
        tabs.addTab(tab1, "Tab 1")

        # Tab 2
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Content of Tab 2"))
        tabs.addTab(tab2, "Tab 2")

        # Tab 3
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("Content of Tab 3"))
        tabs.addTab(tab3, "Tab 3")

        layout.addWidget(tabs)

        return group

    def _create_control_samples(self) -> QWidget:
        """Create control samples (checkboxes, radio, sliders).

        Returns:
            Widget with control samples

        """
        group = QGroupBox("Controls")
        layout = QVBoxLayout(group)

        # Checkboxes
        cb_layout = QHBoxLayout()
        cb_layout.addWidget(QLabel("Checkboxes:"))
        cb1 = QCheckBox("Option 1")
        cb1.setChecked(True)
        cb_layout.addWidget(cb1)
        cb2 = QCheckBox("Option 2")
        cb_layout.addWidget(cb2)
        cb3 = QCheckBox("Disabled")
        cb3.setEnabled(False)
        cb_layout.addWidget(cb3)
        cb_layout.addStretch()
        layout.addLayout(cb_layout)

        # Radio buttons
        rb_layout = QHBoxLayout()
        rb_layout.addWidget(QLabel("Radio Buttons:"))
        rb1 = QRadioButton("Option A")
        rb1.setChecked(True)
        rb_layout.addWidget(rb1)
        rb2 = QRadioButton("Option B")
        rb_layout.addWidget(rb2)
        rb_layout.addStretch()
        layout.addLayout(rb_layout)

        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Slider:"))
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(50)
        slider_layout.addWidget(slider)
        layout.addLayout(slider_layout)

        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        progress = QProgressBar()
        progress.setValue(65)
        progress_layout.addWidget(progress)
        layout.addLayout(progress_layout)

        return group

    def _create_editor_sample(self) -> QWidget:
        """Create text editor sample.

        Returns:
            Widget with editor sample

        """
        group = QGroupBox("Text Editor")
        layout = QVBoxLayout(group)

        editor = QTextEdit()
        editor.setPlainText(
            "# Sample Code\n"
            "def hello_world():\n"
            "    print('Hello, World!')\n"
            "    return 42\n"
            "\n"
            "# Theme preview\n"
            "The quick brown fox jumps over the lazy dog.\n"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "0123456789"
        )
        editor.setProperty("role", "editor")
        editor.setMaximumHeight(150)
        layout.addWidget(editor)

        return group


class ThemePreviewWidget(ThemedWidget, QWidget):
    """Theme preview panel with sample widgets.

    Displays sample widgets that update in real-time as theme changes.
    Uses PreviewSampleGenerator to create comprehensive widget samples.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize theme preview widget.

        Args:
            parent: Parent widget

        """
        super().__init__(parent)

        # Setup UI
        self._setup_ui()

        logger.debug("ThemePreviewWidget initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("Live Preview")
        header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        layout.addWidget(header)

        # Sample generator
        self._samples = PreviewSampleGenerator()
        layout.addWidget(self._samples)

    def refresh(self) -> None:
        """Refresh preview (force update)."""
        # The ThemedWidget system automatically updates when theme changes
        # This method is here for explicit refresh if needed
        self.update()
        logger.debug("Preview refreshed")
