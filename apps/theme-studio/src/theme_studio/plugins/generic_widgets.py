"""Generic Widgets Plugin - Shows common Qt widgets with theming."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QToolBar,
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
        # Enable auto-fill background so the widget uses the palette background color
        self.setAutoFillBackground(True)
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

        # Menus & Toolbars group
        menus_group = self._create_menus_toolbars_group()
        layout.addWidget(menus_group)

        # Tabs
        tabs = self._create_tabs()
        layout.addWidget(tabs)

        layout.addStretch()

    def _create_collapsible_group(self, title: str, collapsed: bool = False) -> QGroupBox:
        """Create a collapsible group box.

        Args:
            title: Group title
            collapsed: Whether to start collapsed (default False)

        Returns:
            Collapsible QGroupBox
        """
        group = QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(not collapsed)  # Checked means expanded
        return group

    def _create_buttons_group(self) -> QGroupBox:
        """Create buttons demonstration group with state demonstrations."""
        group = self._create_collapsible_group("Buttons & States")
        layout = QVBoxLayout(group)

        # Button states row
        states_label = QLabel("Button States:")
        states_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(states_label)

        states_layout = QHBoxLayout()

        # Normal state
        btn_normal = QPushButton("Normal")
        states_layout.addWidget(btn_normal)

        # Hover state (simulated with property)
        btn_hover = QPushButton("Hover")
        btn_hover.setProperty("state", "hover")
        btn_hover.setStyleSheet("""
            QPushButton[state="hover"] {
                background-color: palette(light);
                border: 1px solid palette(highlight);
            }
        """)
        states_layout.addWidget(btn_hover)

        # Pressed state (simulated with property)
        btn_pressed = QPushButton("Pressed")
        btn_pressed.setProperty("state", "pressed")
        btn_pressed.setStyleSheet("""
            QPushButton[state="pressed"] {
                background-color: palette(dark);
                border: 1px solid palette(highlight);
            }
        """)
        states_layout.addWidget(btn_pressed)

        # Disabled state
        btn_disabled = QPushButton("Disabled")
        btn_disabled.setEnabled(False)
        states_layout.addWidget(btn_disabled)

        states_layout.addStretch()
        layout.addLayout(states_layout)

        # Button variants row
        variants_label = QLabel("Button Variants:")
        variants_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(variants_label)

        variants_layout = QHBoxLayout()

        # Default/Primary button
        btn_primary = QPushButton("Primary Button")
        btn_primary.setDefault(True)
        variants_layout.addWidget(btn_primary)

        # Regular button
        btn_regular = QPushButton("Regular Button")
        variants_layout.addWidget(btn_regular)

        # Flat button
        btn_flat = QPushButton("Flat Button")
        btn_flat.setFlat(True)
        variants_layout.addWidget(btn_flat)

        variants_layout.addStretch()
        layout.addLayout(variants_layout)

        return group

    def _create_inputs_group(self) -> QGroupBox:
        """Create input widgets demonstration group."""
        group = self._create_collapsible_group("Input Widgets")
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
        group = self._create_collapsible_group("Selection Widgets")
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
        group = self._create_collapsible_group("Progress Indicators")
        layout = QVBoxLayout(group)

        # Progress bar (static)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(65)
        layout.addWidget(progress)

        return group

    def _create_menus_toolbars_group(self) -> QGroupBox:
        """Create menus and toolbars demonstration group."""
        group = self._create_collapsible_group("Menus & Toolbars")
        layout = QVBoxLayout(group)

        # MenuBar demonstration
        menubar_label = QLabel("MenuBar:")
        menubar_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(menubar_label)

        menu_bar = QMenuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open...")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")

        layout.addWidget(menu_bar)

        # ToolBar demonstration
        toolbar_label = QLabel("ToolBar:")
        toolbar_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(toolbar_label)

        toolbar = QToolBar()
        toolbar.addAction("New")
        toolbar.addAction("Open")
        toolbar.addAction("Save")
        toolbar.addSeparator()
        toolbar.addAction("Cut")
        toolbar.addAction("Copy")
        toolbar.addAction("Paste")

        layout.addWidget(toolbar)

        # Context Menu demonstration
        menu_label = QLabel("Context Menu (QMenu):")
        menu_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(menu_label)

        menu_layout = QHBoxLayout()
        context_btn = QPushButton("Right-click or Click ▼")

        # Create context menu
        context_menu = QMenu(context_btn)
        context_menu.addAction("Action 1")
        context_menu.addAction("Action 2")
        context_menu.addSeparator()

        # Submenu
        submenu = context_menu.addMenu("Submenu")
        submenu.addAction("Sub Action 1")
        submenu.addAction("Sub Action 2")

        context_menu.addSeparator()
        context_menu.addAction("Delete")

        # Connect button to show menu
        context_btn.setMenu(context_menu)

        menu_layout.addWidget(context_btn)
        menu_layout.addStretch()
        layout.addLayout(menu_layout)

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

