"""Import/Export Widget - Theme Editor Component.

This module provides UI for importing and exporting themes.

Phase 5: Import/Export UI
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.theme import Theme
from ..logging import get_debug_logger
from ..persistence.storage import ThemePersistence, ThemeValidationResult
from .base import ThemedWidget

logger = get_debug_logger(__name__)


class ThemeMetadataEditor(ThemedWidget, QWidget):
    """Widget for editing theme metadata.

    Features:
    - Name, version, type editing
    - Author and description fields
    - Validation feedback
    """

    metadata_changed = Signal(dict)  # Emitted when metadata changes

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize metadata editor.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current metadata
        self._metadata: dict = {}

        # Setup UI
        self._setup_ui()

        logger.debug("ThemeMetadataEditor initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Theme information
        info_group = QGroupBox("Theme Information")
        info_layout = QVBoxLayout(info_group)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("My Custom Theme")
        self._name_input.textChanged.connect(self._on_metadata_changed)
        name_layout.addWidget(self._name_input)
        info_layout.addLayout(name_layout)

        # Version
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self._version_input = QLineEdit()
        self._version_input.setPlaceholderText("1.0.0")
        self._version_input.textChanged.connect(self._on_metadata_changed)
        version_layout.addWidget(self._version_input)
        info_layout.addLayout(version_layout)

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self._type_input = QLineEdit()
        self._type_input.setPlaceholderText("dark, light, or high-contrast")
        self._type_input.textChanged.connect(self._on_metadata_changed)
        type_layout.addWidget(self._type_input)
        info_layout.addLayout(type_layout)

        layout.addWidget(info_group)

        # Author information
        author_group = QGroupBox("Author Information")
        author_layout = QVBoxLayout(author_group)

        # Author
        author_name_layout = QHBoxLayout()
        author_name_layout.addWidget(QLabel("Author:"))
        self._author_input = QLineEdit()
        self._author_input.setPlaceholderText("Your Name")
        self._author_input.textChanged.connect(self._on_metadata_changed)
        author_name_layout.addWidget(self._author_input)
        author_layout.addLayout(author_name_layout)

        # Description
        desc_label = QLabel("Description:")
        author_layout.addWidget(desc_label)
        self._description_input = QTextEdit()
        self._description_input.setPlaceholderText("Theme description...")
        self._description_input.setMaximumHeight(80)
        self._description_input.textChanged.connect(self._on_metadata_changed)
        author_layout.addWidget(self._description_input)

        layout.addWidget(author_group)

    def _on_metadata_changed(self) -> None:
        """Handle metadata changes."""
        metadata = self.get_metadata()
        self._metadata = metadata
        self.metadata_changed.emit(metadata)

    def set_metadata(self, metadata: dict) -> None:
        """Set metadata values.

        Args:
            metadata: Metadata dictionary
        """
        self._metadata = metadata

        # Block signals during update
        self._name_input.blockSignals(True)
        self._version_input.blockSignals(True)
        self._type_input.blockSignals(True)
        self._author_input.blockSignals(True)
        self._description_input.blockSignals(True)

        # Update fields
        self._name_input.setText(metadata.get("name", ""))
        self._version_input.setText(metadata.get("version", "1.0.0"))
        self._type_input.setText(metadata.get("type", "dark"))
        self._author_input.setText(metadata.get("author", ""))
        self._description_input.setPlainText(metadata.get("description", ""))

        # Unblock signals
        self._name_input.blockSignals(False)
        self._version_input.blockSignals(False)
        self._type_input.blockSignals(False)
        self._author_input.blockSignals(False)
        self._description_input.blockSignals(False)

    def get_metadata(self) -> dict:
        """Get current metadata.

        Returns:
            Metadata dictionary
        """
        return {
            "name": self._name_input.text().strip() or "Untitled Theme",
            "version": self._version_input.text().strip() or "1.0.0",
            "type": self._type_input.text().strip() or "dark",
            "author": self._author_input.text().strip(),
            "description": self._description_input.toPlainText().strip(),
        }


class ThemeImportDialog(ThemedWidget, QDialog):
    """Dialog for importing themes from files.

    Features:
    - File picker for .json/.json.gz files
    - Validation error display
    - Preview of theme metadata
    """

    theme_imported = Signal(Theme)  # Emitted when theme is successfully imported

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize import dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._imported_theme: Optional[Theme] = None
        self._persistence = ThemePersistence()

        # Configure dialog
        self.setWindowTitle("Import Theme")
        self.resize(500, 400)

        # Setup UI
        self._setup_ui()

        logger.debug("ThemeImportDialog initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("Select Theme File")
        file_layout = QHBoxLayout(file_group)

        self._file_path_input = QLineEdit()
        self._file_path_input.setReadOnly(True)
        self._file_path_input.setPlaceholderText("No file selected...")
        file_layout.addWidget(self._file_path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(browse_btn)

        layout.addWidget(file_group)

        # Validation results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout(validation_group)

        self._validation_output = QTextEdit()
        self._validation_output.setReadOnly(True)
        self._validation_output.setMaximumHeight(150)
        validation_layout.addWidget(self._validation_output)

        layout.addWidget(validation_group)

        # Dialog buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        layout.addWidget(self._button_box)

    def _on_browse(self) -> None:
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Theme File",
            str(Path.home()),
            "Theme Files (*.json *.json.gz);;All Files (*)",
        )

        if file_path:
            self._load_and_validate(Path(file_path))

    def _load_and_validate(self, file_path: Path) -> None:
        """Load and validate theme file.

        Args:
            file_path: Path to theme file
        """
        self._file_path_input.setText(str(file_path))
        self._validation_output.clear()

        try:
            # Load theme
            theme = self._persistence.load_theme(file_path, validate=True)
            self._imported_theme = theme

            # Show success
            self._validation_output.setPlainText(
                f"✅ Theme loaded successfully!\n\n"
                f"Name: {theme.name}\n"
                f"Version: {theme.version}\n"
                f"Type: {theme.type}\n"
                f"Colors: {len(theme.colors)} tokens\n"
                f"Styles: {len(theme.styles)} properties"
            )
            self._validation_output.setStyleSheet("color: #4caf50;")

            # Enable OK button
            self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

            logger.info(f"Theme imported: {theme.name}")

        except Exception as e:
            # Show error
            self._validation_output.setPlainText(f"❌ Import failed:\n\n{str(e)}")
            self._validation_output.setStyleSheet("color: #f44336;")

            # Disable OK button
            self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

            logger.error(f"Import failed: {e}")

    def _on_accept(self) -> None:
        """Handle OK button click."""
        if self._imported_theme:
            self.theme_imported.emit(self._imported_theme)
            self.accept()

    def get_theme(self) -> Optional[Theme]:
        """Get the imported theme.

        Returns:
            Imported theme or None
        """
        return self._imported_theme


class ThemeExportDialog(ThemedWidget, QDialog):
    """Dialog for exporting themes to files.

    Features:
    - File picker for save location
    - Metadata editing
    - Compression option
    - Export format selection
    """

    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        """Initialize export dialog.

        Args:
            theme: Theme to export
            parent: Parent widget
        """
        super().__init__(parent)

        self._theme = theme
        self._persistence = ThemePersistence()

        # Configure dialog
        self.setWindowTitle(f"Export Theme: {theme.name}")
        self.resize(500, 500)

        # Setup UI
        self._setup_ui()

        # Load theme metadata
        self._metadata_editor.set_metadata({
            "name": theme.name,
            "version": theme.version,
            "type": theme.type,
            "author": theme.metadata.get("author", ""),
            "description": theme.metadata.get("description", ""),
        })

        logger.debug(f"ThemeExportDialog initialized for: {theme.name}")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Metadata editor
        self._metadata_editor = ThemeMetadataEditor()
        layout.addWidget(self._metadata_editor)

        # Export location
        file_group = QGroupBox("Export Location")
        file_layout = QHBoxLayout(file_group)

        self._file_path_input = QLineEdit()
        self._file_path_input.setPlaceholderText("Select export location...")
        file_layout.addWidget(self._file_path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(browse_btn)

        layout.addWidget(file_group)

        # Status
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).clicked.connect(
            self._on_save
        )
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_browse(self) -> None:
        """Handle browse button click."""
        # Suggest filename based on theme name
        suggested_name = f"{self._theme.name.replace(' ', '_').lower()}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme",
            str(Path.home() / suggested_name),
            "Theme Files (*.json);;Compressed Theme (*.json.gz)",
        )

        if file_path:
            self._file_path_input.setText(file_path)

    def _on_save(self) -> None:
        """Handle save button click."""
        file_path = self._file_path_input.text().strip()

        if not file_path:
            QMessageBox.warning(self, "No File Selected", "Please select an export location.")
            return

        # Get updated metadata
        metadata = self._metadata_editor.get_metadata()

        try:
            # Create new theme with updated metadata
            from ..core.theme import ThemeBuilder

            builder = ThemeBuilder.from_theme(self._theme)
            builder._name = metadata["name"]
            builder._version = metadata["version"]
            builder._type = metadata["type"]
            builder._metadata = {
                "author": metadata["author"],
                "description": metadata["description"],
            }
            updated_theme = builder.build()

            # Save theme
            compress = file_path.endswith(".gz")
            saved_path = self._persistence.save_theme(
                updated_theme, filename=Path(file_path).name, compress=compress
            )

            # Show success
            self._status_label.setText(f"✅ Theme exported to: {saved_path}")
            self._status_label.setStyleSheet("color: #4caf50;")

            logger.info(f"Theme exported to: {saved_path}")

            # Close dialog after short delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, self.accept)

        except Exception as e:
            # Show error
            QMessageBox.critical(self, "Export Failed", f"Failed to export theme:\n\n{str(e)}")
            logger.error(f"Export failed: {e}")
