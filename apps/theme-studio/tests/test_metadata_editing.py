"""Tests for metadata editing functionality (Task 12)."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_theme.core.theme import Theme

from src.theme_studio.controllers.theme_controller import ThemeController
from src.theme_studio.models.theme_document import ThemeDocument
from src.theme_studio.panels.inspector import InspectorPanel
from src.theme_studio.validators.metadata_validator import MetadataValidator
from src.theme_studio.window import ThemeStudioWindow


@pytest.fixture
def app(qtbot):
    """Create QApplication."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def document():
    """Create test document."""
    theme = Theme(
        name="Test Theme",
        version="1.0.0",
        type="dark",
        colors={"button.bg": "#ff0000"},
        metadata={"author": "Test Author", "description": "Test description"},
    )
    return ThemeDocument(theme)


@pytest.fixture
def controller(document):
    """Create controller for document."""
    return ThemeController(document)


@pytest.fixture
def inspector(app, qtbot, controller):
    """Create inspector panel with controller."""
    panel = InspectorPanel()
    panel.set_controller(controller)
    panel.show()
    qtbot.waitExposed(panel)
    return panel


class TestMetadataValidator:
    """Test metadata validation."""

    def test_validate_name_valid(self):
        """Test name validation with valid input."""
        is_valid, error = MetadataValidator.validate_name("My Theme")
        assert is_valid is True
        assert error is None

    def test_validate_name_empty(self):
        """Test name validation with empty input."""
        is_valid, error = MetadataValidator.validate_name("")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_validate_name_whitespace(self):
        """Test name validation with whitespace-only input."""
        is_valid, error = MetadataValidator.validate_name("   ")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_validate_version_valid_simple(self):
        """Test version validation with simple semver."""
        is_valid, error = MetadataValidator.validate_version("1.0.0")
        assert is_valid is True
        assert error is None

    def test_validate_version_valid_prerelease(self):
        """Test version validation with prerelease."""
        is_valid, error = MetadataValidator.validate_version("2.1.5-beta")
        assert is_valid is True
        assert error is None

    def test_validate_version_invalid_short(self):
        """Test version validation with too few parts."""
        is_valid, error = MetadataValidator.validate_version("1.0")
        assert is_valid is False
        assert "semantic version" in error

    def test_validate_version_invalid_prefix(self):
        """Test version validation with 'v' prefix."""
        is_valid, error = MetadataValidator.validate_version("v1.0.0")
        assert is_valid is False
        assert "semantic version" in error

    def test_validate_type_valid(self):
        """Test type validation with valid types."""
        for type_val in ["dark", "light", "high-contrast"]:
            is_valid, error = MetadataValidator.validate_type(type_val)
            assert is_valid is True
            assert error is None

    def test_validate_type_invalid(self):
        """Test type validation with invalid type."""
        is_valid, error = MetadataValidator.validate_type("invalid")
        assert is_valid is False
        assert "must be one of" in error


class TestInspectorMetadataSection:
    """Test inspector panel metadata section."""

    def test_metadata_section_exists(self, inspector):
        """Test that metadata section is present."""
        assert hasattr(inspector, "metadata_group")
        assert inspector.metadata_group.isVisible()

    def test_metadata_section_collapsible(self, inspector):
        """Test that metadata section is collapsible."""
        assert inspector.metadata_group.isCheckable()
        assert inspector.metadata_group.isChecked()  # Expanded by default

    def test_metadata_fields_exist(self, inspector):
        """Test that all metadata input fields exist."""
        assert hasattr(inspector, "name_input")
        assert hasattr(inspector, "version_input")
        assert hasattr(inspector, "type_combo")
        assert hasattr(inspector, "author_input")
        assert hasattr(inspector, "description_input")

    def test_populate_metadata_fields(self, inspector, document):
        """Test populating metadata fields from document."""
        inspector.populate_metadata_fields(document)

        assert inspector.name_input.text() == "Test Theme"
        assert inspector.version_input.text() == "1.0.0"
        assert inspector.type_combo.currentText() == "dark"
        assert inspector.author_input.text() == "Test Author"
        assert inspector.description_input.toPlainText() == "Test description"

    def test_focus_metadata(self, inspector, qtbot):
        """Test Ctrl+I focus functionality."""
        # Collapse section first
        inspector.metadata_group.setChecked(False)
        assert not inspector.metadata_group.isChecked()

        # Focus metadata
        inspector.focus_metadata()

        # Should expand and focus name field
        assert inspector.metadata_group.isChecked()
        qtbot.wait(100)
        assert inspector.name_input.hasFocus()


class TestMetadataEditing:
    """Test metadata editing through controller."""

    def test_edit_name_queues_change(self, inspector, controller, document, qtbot):
        """Test editing name queues controller change."""
        inspector.populate_metadata_fields(document)

        # Edit name
        inspector.name_input.setText("New Theme Name")
        qtbot.wait(100)  # Wait for deferred command

        # Check command was created
        assert document.theme.name == "New Theme Name"

    def test_edit_version_queues_change(self, inspector, controller, document, qtbot):
        """Test editing version queues controller change."""
        inspector.populate_metadata_fields(document)

        # Edit version
        inspector.version_input.setText("2.0.0")
        qtbot.wait(100)

        assert document.theme.version == "2.0.0"

    def test_edit_type_queues_change(self, inspector, controller, document, qtbot):
        """Test editing type queues controller change."""
        inspector.populate_metadata_fields(document)

        # Change type
        inspector.type_combo.setCurrentText("light")
        qtbot.wait(100)

        assert document.theme.type == "light"

    def test_invalid_name_shows_error(self, inspector, document):
        """Test invalid name shows error label."""
        inspector.populate_metadata_fields(document)

        # Set empty name
        inspector.name_input.setText("")

        # Error label should be visible
        assert inspector.name_error_label.isVisible()
        assert "cannot be empty" in inspector.name_error_label.text()

    def test_invalid_version_shows_error(self, inspector, document):
        """Test invalid version shows error label."""
        inspector.populate_metadata_fields(document)

        # Set invalid version
        inspector.version_input.setText("1.0")

        # Error label should be visible
        assert inspector.version_error_label.isVisible()
        assert "semantic version" in inspector.version_error_label.text()


class TestMetadataUndoRedo:
    """Test undo/redo for metadata changes."""

    def test_undo_name_change(self, inspector, controller, document, qtbot):
        """Test undoing name change."""
        inspector.populate_metadata_fields(document)
        old_name = document.theme.name

        # Edit name
        inspector.name_input.setText("New Name")
        qtbot.wait(500)

        # Undo
        document._undo_stack.undo()
        qtbot.wait(100)

        assert document.theme.name == old_name

    def test_redo_name_change(self, inspector, controller, document, qtbot):
        """Test redoing name change."""
        inspector.populate_metadata_fields(document)

        # Edit name
        inspector.name_input.setText("New Name")
        qtbot.wait(500)

        # Undo then redo
        document._undo_stack.undo()
        qtbot.wait(100)
        document._undo_stack.redo()
        qtbot.wait(100)

        assert document.theme.name == "New Name"

    def test_multiple_edits_merge(self, inspector, controller, document, qtbot):
        """Test multiple consecutive edits to same field merge."""
        inspector.populate_metadata_fields(document)

        # Make multiple edits
        inspector.name_input.setText("Name 1")
        qtbot.wait(100)
        inspector.name_input.setText("Name 2")
        qtbot.wait(100)
        inspector.name_input.setText("Name 3")
        qtbot.wait(500)

        # Should have only one undo command (merged)
        assert document._undo_stack.canUndo()
        document._undo_stack.undo()
        qtbot.wait(100)

        # Should undo all the way back to original
        assert document.theme.name == "Test Theme"


class TestWindowTitleIntegration:
    """Test window title updates with metadata."""

    def test_window_title_shows_theme_name(self, app, qtbot):
        """Test window title shows theme name and version."""
        window = ThemeStudioWindow()
        window.show()
        qtbot.waitExposed(window)

        title = window.windowTitle()
        assert "Untitled" in title
        assert "v1.0.0" in title
        assert "VFTheme Studio" in title

        window.close()

    def test_window_title_updates_on_name_change(self, app, qtbot):
        """Test window title updates when name changes."""
        window = ThemeStudioWindow()
        window.show()
        qtbot.waitExposed(window)
        qtbot.wait(100)

        # Edit name
        window.inspector_panel.name_input.setText("My Theme")
        qtbot.wait(500)

        title = window.windowTitle()
        assert "My Theme" in title

        window.close()


class TestSaveLoadPersistence:
    """Test metadata persistence in save/load."""

    def test_save_persists_metadata(self, document, tmp_path):
        """Test saving document persists metadata."""
        import json

        # Modify metadata
        document.set_name("Custom Theme")
        document.set_version("3.2.1")
        document.set_type("light")
        document.set_metadata_field("author", "John Doe")
        document.set_metadata_field("description", "My custom theme")

        # Save to file
        save_path = tmp_path / "test_theme.json"
        document.save(str(save_path))

        # Read file and verify
        with open(save_path) as f:
            data = json.load(f)

        assert data["name"] == "Custom Theme"
        assert data["version"] == "3.2.1"
        assert data["type"] == "light"
        assert data["metadata"]["author"] == "John Doe"
        assert data["metadata"]["description"] == "My custom theme"

    def test_load_restores_metadata(self, tmp_path):
        """Test loading document restores metadata."""
        import json

        # Create test file
        theme_data = {
            "name": "Loaded Theme",
            "version": "2.5.0",
            "type": "high-contrast",
            "colors": {},
            "styles": {},
            "metadata": {
                "author": "Jane Smith",
                "description": "A high contrast theme",
            },
            "tokenColors": [],
        }

        load_path = tmp_path / "load_test.json"
        with open(load_path, "w") as f:
            json.dump(theme_data, f)

        # Load document
        doc = ThemeDocument()
        doc.load(str(load_path))

        # Verify metadata
        assert doc.theme.name == "Loaded Theme"
        assert doc.theme.version == "2.5.0"
        assert doc.theme.type == "high-contrast"
        assert doc.get_metadata_field("author") == "Jane Smith"
        assert doc.get_metadata_field("description") == "A high contrast theme"
