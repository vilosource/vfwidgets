"""Terminal Theme Dialog - UI for customizing terminal colors and fonts."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedDialog, ThemedQWidget

from ..terminal_theme_manager import TerminalThemeManager

logger = logging.getLogger(__name__)


class ColorPickerRow(ThemedQWidget):
    """Row with label and color picker button."""

    colorChanged = Signal(str, str)  # (property_name, color_value)

    def __init__(self, label: str, property_name: str, initial_color: str = "#000000", parent=None):
        super().__init__(parent)
        self.property_name = property_name
        self.current_color = initial_color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Label
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(150)
        layout.addWidget(label_widget)

        # Color preview button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(60, 30)
        self.color_button.clicked.connect(self._pick_color)
        self._update_button_color(initial_color)
        layout.addWidget(self.color_button)

        # Hex value display
        self.hex_input = QLineEdit(initial_color)
        self.hex_input.setMaximumWidth(100)
        self.hex_input.textChanged.connect(self._on_hex_changed)
        layout.addWidget(self.hex_input)

        layout.addStretch()

    def _update_button_color(self, color: str):
        """Update button background color."""
        self.current_color = color
        self.color_button.setStyleSheet(f"background-color: {color}; border: 1px solid #555;")

    def _pick_color(self):
        """Open color picker dialog."""
        initial = QColor(self.current_color)
        color = QColorDialog.getColor(initial, self, f"Pick {self.property_name}")

        if color.isValid():
            hex_color = color.name()
            self.set_color(hex_color)

    def _on_hex_changed(self, text: str):
        """Handle manual hex input changes."""
        if QColor(text).isValid():
            self._update_button_color(text)
            self.colorChanged.emit(self.property_name, text)

    def set_color(self, color: str):
        """Set color programmatically."""
        self._update_button_color(color)
        self.hex_input.setText(color)
        self.colorChanged.emit(self.property_name, color)

    def get_color(self) -> str:
        """Get current color value."""
        return self.current_color


class TerminalThemeDialog(ThemedDialog):
    """Dialog for customizing terminal theme colors and fonts."""

    themeApplied = Signal(dict)  # Emitted when user applies theme

    def __init__(self, theme_manager: TerminalThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.color_pickers = {}  # property_name -> ColorPickerRow
        self.current_theme = self.theme_manager.get_default_theme().copy()

        self.setWindowTitle("Terminal Theme Customization")
        self.setMinimumSize(900, 700)
        self.setup_ui()
        self.load_current_theme()

    def setup_ui(self):
        """Setup UI layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Reduce spacing between elements

        # Top bar: Theme selector and actions
        top_bar = self._create_top_bar()
        layout.addWidget(top_bar, 0)  # 0 = don't stretch

        # Main content: Splitter with editor and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Editor panel
        editor_panel = self._create_editor_panel()
        splitter.addWidget(editor_panel)

        # Right: Preview placeholder (Phase 3)
        preview_panel = self._create_preview_panel()
        splitter.addWidget(preview_panel)

        splitter.setStretchFactor(0, 2)  # Editor gets more space
        splitter.setStretchFactor(1, 1)  # Preview gets less

        layout.addWidget(splitter, 1)  # 1 = stretch to fill available space

        # Bottom: Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.on_apply)
        layout.addWidget(button_box, 0)  # 0 = don't stretch

    def _create_top_bar(self) -> ThemedQWidget:
        """Create top bar with theme selector and actions."""
        widget = ThemedQWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(6)  # Reduce spacing between buttons

        # Theme selector
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        self.theme_combo.addItems(self.theme_manager.list_themes())
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        layout.addWidget(self.theme_combo)

        layout.addStretch()

        # Save current theme
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setToolTip("Save changes to current theme")
        self.save_btn.setMaximumWidth(80)
        self.save_btn.clicked.connect(self.on_save)
        layout.addWidget(self.save_btn)

        # Save as new theme
        save_as_btn = QPushButton("Save As...")
        save_as_btn.setToolTip("Save as a new theme")
        save_as_btn.setMaximumWidth(90)
        save_as_btn.clicked.connect(self.on_save_as)
        layout.addWidget(save_as_btn)

        # Set as default
        default_btn = QPushButton("⭐ Default")
        default_btn.setToolTip("Set this theme as default for new terminals")
        default_btn.setMaximumWidth(90)
        default_btn.clicked.connect(self.on_set_default)
        layout.addWidget(default_btn)

        # Reset to original
        reset_btn = QPushButton("↺ Reset")
        reset_btn.setToolTip("Reset to original theme values")
        reset_btn.setMaximumWidth(80)
        reset_btn.clicked.connect(self.load_current_theme)
        layout.addWidget(reset_btn)

        return widget

    def _create_editor_panel(self) -> ThemedQWidget:
        """Create editor panel with color pickers and font selectors."""
        # Outer themed widget container
        outer = ThemedQWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)  # Remove frame for cleaner look

        # Make scroll area background transparent to show parent theme
        scroll.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """
        )

        # Inner container for the form
        container = ThemedQWidget()
        layout = QVBoxLayout(container)

        # Font settings group
        font_group = self._create_font_settings()
        layout.addWidget(font_group)

        # Basic colors group
        basic_group = self._create_basic_colors_group()
        layout.addWidget(basic_group)

        # ANSI colors group
        ansi_group = self._create_ansi_colors_group()
        layout.addWidget(ansi_group)

        # Bright ANSI colors group
        bright_group = self._create_bright_ansi_colors_group()
        layout.addWidget(bright_group)

        layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

        return outer

    def _create_font_settings(self) -> QGroupBox:
        """Create font settings group."""
        group = QGroupBox("Font Settings")
        layout = QFormLayout(group)

        # Font family
        self.font_combo = QFontComboBox()
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        layout.addRow("Font Family:", self.font_combo)

        # Font size
        size_layout = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(8, 24)
        self.font_size_slider.setValue(14)
        self.font_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.valueChanged.connect(self.on_font_size_changed)
        size_layout.addWidget(self.font_size_slider)

        self.font_size_label = QLabel("14 pt")
        self.font_size_label.setMinimumWidth(50)
        size_layout.addWidget(self.font_size_label)

        layout.addRow("Font Size:", size_layout)

        return group

    def _create_basic_colors_group(self) -> QGroupBox:
        """Create basic colors group."""
        group = QGroupBox("Basic Colors")
        layout = QVBoxLayout(group)

        colors = [
            ("Background", "background"),
            ("Foreground", "foreground"),
            ("Cursor", "cursor"),
            ("Cursor Accent", "cursorAccent"),
            ("Selection Background", "selectionBackground"),
        ]

        for label, prop in colors:
            picker = ColorPickerRow(label, prop)
            picker.colorChanged.connect(self.on_color_changed)
            self.color_pickers[prop] = picker
            layout.addWidget(picker)

        return group

    def _create_ansi_colors_group(self) -> QGroupBox:
        """Create ANSI colors group."""
        group = QGroupBox("ANSI Colors")
        layout = QVBoxLayout(group)

        colors = [
            ("Black", "black"),
            ("Red", "red"),
            ("Green", "green"),
            ("Yellow", "yellow"),
            ("Blue", "blue"),
            ("Magenta", "magenta"),
            ("Cyan", "cyan"),
            ("White", "white"),
        ]

        for label, prop in colors:
            picker = ColorPickerRow(label, prop)
            picker.colorChanged.connect(self.on_color_changed)
            self.color_pickers[prop] = picker
            layout.addWidget(picker)

        return group

    def _create_bright_ansi_colors_group(self) -> QGroupBox:
        """Create bright ANSI colors group."""
        group = QGroupBox("Bright ANSI Colors")
        layout = QVBoxLayout(group)

        colors = [
            ("Bright Black", "brightBlack"),
            ("Bright Red", "brightRed"),
            ("Bright Green", "brightGreen"),
            ("Bright Yellow", "brightYellow"),
            ("Bright Blue", "brightBlue"),
            ("Bright Magenta", "brightMagenta"),
            ("Bright Cyan", "brightCyan"),
            ("Bright White", "brightWhite"),
        ]

        for label, prop in colors:
            picker = ColorPickerRow(label, prop)
            picker.colorChanged.connect(self.on_color_changed)
            self.color_pickers[prop] = picker
            layout.addWidget(picker)

        return group

    def _create_preview_panel(self) -> ThemedQWidget:
        """Create preview panel (placeholder for Phase 3)."""
        widget = ThemedQWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Live Preview\n(Phase 3)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(label)

        return widget

    def load_current_theme(self):
        """Load current theme into UI."""
        terminal = self.current_theme.get("terminal", {})

        # Load fonts
        font_family = terminal.get("fontFamily", "Consolas, Monaco, 'Courier New', monospace")
        # Extract first font from comma-separated list
        first_font = font_family.split(",")[0].strip().strip("'\"")
        self.font_combo.setCurrentText(first_font)

        font_size = terminal.get("fontSize", 14)
        self.font_size_slider.setValue(font_size)

        # Load colors
        for prop, picker in self.color_pickers.items():
            color = terminal.get(prop, "#000000")
            picker.set_color(color)

    def on_theme_selected(self, theme_name: str):
        """Handle theme selection from combo box."""
        if not theme_name:
            return

        try:
            self.current_theme = self.theme_manager.load_theme(theme_name)
            self.load_current_theme()

            # Disable Save button for bundled themes
            bundled_themes = ["Default Dark", "Default Light"]
            self.save_btn.setEnabled(theme_name not in bundled_themes)

            logger.info(f"Loaded theme: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to load theme '{theme_name}': {e}")

    def on_color_changed(self, property_name: str, color: str):
        """Handle color picker changes."""
        if "terminal" not in self.current_theme:
            self.current_theme["terminal"] = {}

        self.current_theme["terminal"][property_name] = color
        logger.debug(f"Color changed: {property_name} = {color}")

        # TODO Phase 3: Update preview

    def on_font_changed(self, font_family: str):
        """Handle font family changes."""
        if "terminal" not in self.current_theme:
            self.current_theme["terminal"] = {}

        self.current_theme["terminal"]["fontFamily"] = font_family
        logger.debug(f"Font changed: {font_family}")

        # TODO Phase 3: Update preview

    def on_font_size_changed(self, size: int):
        """Handle font size changes."""
        if "terminal" not in self.current_theme:
            self.current_theme["terminal"] = {}

        self.current_theme["terminal"]["fontSize"] = size
        self.font_size_label.setText(f"{size} pt")
        logger.debug(f"Font size changed: {size}")

        # TODO Phase 3: Update preview

    def on_save(self):
        """Save changes to the current theme."""
        theme_name = self.current_theme.get("name", "Unnamed")

        # Don't allow saving bundled themes
        bundled_themes = ["Default Dark", "Default Light"]  # Add more as needed
        if theme_name in bundled_themes:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                "Cannot Save",
                f"'{theme_name}' is a bundled theme and cannot be modified.\n"
                "Use 'Save As...' to create a new theme.",
            )
            return

        try:
            # Save theme with current name
            self.theme_manager.save_theme(self.current_theme, theme_name)

            logger.info(f"Saved changes to theme: {theme_name}")

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(self, "Success", f"Theme '{theme_name}' saved successfully!")

        except Exception as e:
            logger.error(f"Failed to save theme: {e}")

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Error", f"Failed to save theme: {e}")

    def on_save_as(self):
        """Save current theme as new theme."""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self, "Save Theme As", "Enter theme name:", QLineEdit.EchoMode.Normal, ""
        )

        if ok and name:
            try:
                # Update theme metadata
                self.current_theme["name"] = name
                self.current_theme["version"] = "1.0.0"
                self.current_theme["author"] = "User"
                self.current_theme["description"] = f"Custom theme: {name}"

                # Save theme
                self.theme_manager.save_theme(self.current_theme, name)

                # Update combo box
                self.theme_combo.clear()
                self.theme_combo.addItems(self.theme_manager.list_themes())
                self.theme_combo.setCurrentText(name)

                logger.info(f"Saved theme as: {name}")

                from PySide6.QtWidgets import QMessageBox

                QMessageBox.information(self, "Success", f"Theme '{name}' saved successfully!")

            except Exception as e:
                logger.error(f"Failed to save theme: {e}")

                from PySide6.QtWidgets import QMessageBox

                QMessageBox.critical(self, "Error", f"Failed to save theme: {e}")

    def on_set_default(self):
        """Set current theme as default."""
        theme_name = self.current_theme.get("name", "custom")

        try:
            self.theme_manager.set_default_theme(theme_name)
            logger.info(f"Set default theme: {theme_name}")

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self, "Success", f"Theme '{theme_name}' is now the default for new terminals!"
            )

        except Exception as e:
            logger.error(f"Failed to set default theme: {e}")

    def on_apply(self):
        """Apply theme without closing dialog."""
        # Auto-save changes for user themes (not bundled themes)
        theme_name = self.current_theme.get("name", "Unnamed")
        bundled_themes = ["Default Dark", "Default Light"]

        if theme_name not in bundled_themes:
            try:
                self.theme_manager.save_theme(self.current_theme, theme_name)
                logger.info(f"Auto-saved theme on Apply: {theme_name}")
            except Exception as e:
                logger.error(f"Failed to auto-save theme: {e}")

        # Validate theme
        warnings = self.theme_manager.validate_theme(self.current_theme)
        if warnings:
            logger.warning(f"Theme validation warnings: {warnings}")
            # TODO: Display warnings in UI

        # Emit signal to apply to all terminals
        self.themeApplied.emit(self.current_theme)
        logger.info(f"Applied theme: {self.current_theme.get('name', 'custom')}")

    def on_accept(self):
        """OK button clicked - save, apply and close."""
        # on_apply() already auto-saves and applies the theme
        self.on_apply()
        self.accept()

    def get_theme(self) -> dict:
        """Get current theme configuration."""
        return self.current_theme.copy()
