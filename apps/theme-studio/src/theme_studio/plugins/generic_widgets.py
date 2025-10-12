"""Generic Widgets Plugin - Shows common Qt widgets with theming."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .plugin_base import PreviewPlugin


class GenericWidgetsPreview(QWidget):
    """Preview widget for generic widgets.

    This is a plain QWidget. Theme Studio applies edited themes to this widget
    manually via direct stylesheet application, not through the global theme system.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with themed widgets."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Generic Qt Widgets Preview")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Buttons group
        buttons_group = self._create_buttons_group()
        layout.addWidget(buttons_group)

        # Inputs group
        inputs_group = self._create_inputs_group()
        layout.addWidget(inputs_group)

        # Selection group
        selection_group = self._create_selection_group()
        layout.addWidget(selection_group)

        # Progress group
        progress_group = self._create_progress_group()
        layout.addWidget(progress_group)

        # Tabs
        tabs = self._create_tabs()
        layout.addWidget(tabs)

        layout.addStretch()

    def _create_buttons_group(self) -> QGroupBox:
        """Create buttons demonstration group."""
        group = QGroupBox("Buttons")
        layout = QHBoxLayout(group)

        # Normal button
        btn_normal = QPushButton("Normal Button")
        layout.addWidget(btn_normal)

        # Primary button (styled differently)
        btn_primary = QPushButton("Primary Button")
        btn_primary.setDefault(True)
        layout.addWidget(btn_primary)

        # Disabled button
        btn_disabled = QPushButton("Disabled Button")
        btn_disabled.setEnabled(False)
        layout.addWidget(btn_disabled)

        layout.addStretch()

        return group

    def _create_inputs_group(self) -> QGroupBox:
        """Create input widgets demonstration group."""
        group = QGroupBox("Input Widgets")
        layout = QVBoxLayout(group)

        # Line edit
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Text input...")
        layout.addWidget(line_edit)

        # Text edit
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Multi-line text input...")
        text_edit.setMaximumHeight(80)
        layout.addWidget(text_edit)

        # Horizontal layout for smaller inputs
        h_layout = QHBoxLayout()

        # Combo box
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        h_layout.addWidget(QLabel("ComboBox:"))
        h_layout.addWidget(combo)

        # Spin box
        spin = QSpinBox()
        spin.setRange(0, 100)
        spin.setValue(50)
        h_layout.addWidget(QLabel("SpinBox:"))
        h_layout.addWidget(spin)

        h_layout.addStretch()
        layout.addLayout(h_layout)

        return group

    def _create_selection_group(self) -> QGroupBox:
        """Create selection widgets demonstration group."""
        group = QGroupBox("Selection Widgets")
        layout = QVBoxLayout(group)

        # Checkboxes
        cb_layout = QHBoxLayout()
        cb_layout.addWidget(QLabel("CheckBoxes:"))
        cb1 = QCheckBox("Option 1")
        cb1.setChecked(True)
        cb_layout.addWidget(cb1)
        cb_layout.addWidget(QCheckBox("Option 2"))
        cb3 = QCheckBox("Disabled")
        cb3.setEnabled(False)
        cb_layout.addWidget(cb3)
        cb_layout.addStretch()
        layout.addLayout(cb_layout)

        # Radio buttons
        rb_layout = QHBoxLayout()
        rb_layout.addWidget(QLabel("RadioButtons:"))
        rb1 = QRadioButton("Choice A")
        rb1.setChecked(True)
        rb_layout.addWidget(rb1)
        rb_layout.addWidget(QRadioButton("Choice B"))
        rb_layout.addWidget(QRadioButton("Choice C"))
        rb_layout.addStretch()
        layout.addLayout(rb_layout)

        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Slider:"))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(60)
        slider_layout.addWidget(slider)
        layout.addLayout(slider_layout)

        return group

    def _create_progress_group(self) -> QGroupBox:
        """Create progress widgets demonstration group."""
        group = QGroupBox("Progress Indicators")
        layout = QVBoxLayout(group)

        # Progress bar (static)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(65)
        layout.addWidget(progress)

        return group

    def _create_tabs(self) -> QTabWidget:
        """Create tabbed widget demonstration."""
        tabs = QTabWidget()

        # Tab 1
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("This is tab 1 content"))
        tab1_layout.addWidget(QLineEdit("Edit this text..."))
        tab1_layout.addStretch()
        tabs.addTab(tab1, "Tab 1")

        # Tab 2
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("This is tab 2 content"))
        tab2_layout.addWidget(QPushButton("Button in Tab 2"))
        tab2_layout.addStretch()
        tabs.addTab(tab2, "Tab 2")

        # Tab 3
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("This is tab 3 content"))
        tab3_layout.addStretch()
        tabs.addTab(tab3, "Tab 3")

        return tabs



class GenericWidgetsPlugin(PreviewPlugin):
    """Plugin that displays common Qt widgets.

    Shows buttons, inputs, checkboxes, sliders, and other
    standard Qt widgets with the current theme applied.
    """

    def get_name(self) -> str:
        """Get plugin name."""
        return "Generic Widgets"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Common Qt widgets (buttons, inputs, sliders, etc.)"

    def create_preview_widget(self, parent=None) -> QWidget:
        """Create preview widget with themed Qt widgets."""
        return GenericWidgetsPreview(parent)

