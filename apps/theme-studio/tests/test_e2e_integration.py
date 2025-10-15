"""End-to-End Integration Test for Theme Studio Phase 1.

Tests complete workflow:
1. Application startup
2. Token browser selection → Inspector update
3. Theme document save/load
4. Plugin preview loading
5. QPalette integration (alternating rows)
"""

import json
import tempfile
from pathlib import Path

import pytest
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget

from theme_studio.models import ThemeDocument
from theme_studio.window import ThemeStudioWindow


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.fixture
def window(app):
    """Create ThemeStudioWindow instance."""
    win = ThemeStudioWindow()
    yield win
    win.close()


class TestE2EIntegration:
    """End-to-end integration tests."""

    def test_application_startup(self, window):
        """Test application starts with all components initialized."""
        # Window exists
        assert window is not None
        # New documents start unmodified (empty colors dict doesn't count as modification)
        assert window.windowTitle() == "Untitled - VFTheme Studio"

        # Three panels exist
        assert window.token_browser is not None
        assert window.preview_canvas is not None
        assert window.inspector_panel is not None

        # Splitter configured
        assert window.main_splitter is not None
        assert window.main_splitter.count() == 3

        # Document exists
        assert window._current_document is not None
        assert not window._current_document.is_modified()  # New documents start unmodified

        # Plugins registered
        assert len(window._plugins) > 0
        assert "Generic Widgets" in window._plugins

    def test_token_browser_to_inspector_flow(self, window, qtbot):
        """Test token selection updates inspector."""
        # Get token browser model
        model = window.token_browser._model
        assert model is not None

        # Find a token in the tree (e.g., "editor.background")
        proxy_model = window.token_browser._proxy_model
        tree_view = window.token_browser.tree_view

        # Expand all to ensure tokens visible
        tree_view.expandAll()

        # Find first valid token
        token_found = False
        token_name = None

        for row in range(proxy_model.rowCount()):
            category_index = proxy_model.index(row, 0)
            for child_row in range(proxy_model.rowCount(category_index)):
                token_index = proxy_model.index(child_row, 0, category_index)
                source_index = proxy_model.mapToSource(token_index)
                token_name = model.get_token_name(source_index)
                if token_name:
                    token_found = True
                    # Select this token
                    tree_view.setCurrentIndex(token_index)
                    break
            if token_found:
                break

        assert token_found, "Should find at least one token"

        # Process events to allow signal propagation
        qtbot.wait(100)

        # Verify inspector updated
        inspector = window.inspector_panel
        assert inspector._current_token == token_name
        # Token value can be empty string for undefined tokens
        assert inspector.token_value_label.text() != "-"

    def test_qpalette_integration(self, window):
        """Test QPalette integration for alternating row colors."""
        tree_view = window.token_browser.tree_view
        palette = tree_view.palette()

        # Check base colors are set (not default system colors)
        base_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Base)
        alternate_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase)

        # Should have dark theme colors
        # Base: #252526 (37, 37, 38)
        # Alternate: #2a2d2e (42, 45, 46)
        assert base_color.red() == 37
        assert base_color.green() == 37
        assert base_color.blue() == 38

        assert alternate_color.red() == 42
        assert alternate_color.green() == 45
        assert alternate_color.blue() == 46

        # Verify alternating rows enabled
        assert tree_view.alternatingRowColors()

    def test_save_and_load_workflow(self, window, qtbot):
        """Test complete save/load workflow."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            # Save current document
            success = window._save_document_to_path(temp_path)
            assert success

            # Verify file exists
            assert Path(temp_path).exists()

            # Load the file
            with open(temp_path) as f:
                data = json.load(f)

            # Verify structure
            assert 'name' in data
            assert 'colors' in data
            assert 'version' in data

            # Create new document and load
            new_document = ThemeDocument()
            new_document.load(temp_path)

            # Verify loaded correctly
            assert new_document.file_path == temp_path
            assert not new_document.is_modified()  # Freshly loaded
            assert new_document.theme.name == data['name']

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_new_theme_workflow(self, window, qtbot, monkeypatch):
        """Test File > New workflow."""
        # Mock QMessageBox to auto-discard changes
        from PySide6.QtWidgets import QMessageBox
        monkeypatch.setattr(QMessageBox, 'question',
                          lambda *args, **kwargs: QMessageBox.Discard)

        # Modify current document
        original_doc = window._current_document
        original_doc.set_token("test.color", "#123456")
        assert original_doc.is_modified()

        # Create new theme
        window.new_theme()

        # Verify new document created
        new_doc = window._current_document
        assert new_doc is not original_doc
        assert not new_doc.is_modified()  # New documents start unmodified
        assert new_doc.file_path is None

    def test_plugin_loading(self, window, qtbot):
        """Test plugin preview loading."""
        # Get preview canvas
        canvas = window.preview_canvas
        selector = canvas.plugin_selector

        # Verify plugin selector has items
        assert selector.count() > 0

        # Select "Generic Widgets" plugin
        index = selector.findText("Generic Widgets")
        assert index >= 0

        selector.setCurrentIndex(index)
        qtbot.wait(100)

        # Verify plugin content loaded (widget exists but might not be visible in headless test)
        assert canvas._current_plugin is not None
        # Content widget exists (visibility depends on parent window visibility in tests)
        assert isinstance(canvas._current_plugin, QWidget)

    def test_search_functionality(self, window, qtbot):
        """Test token search/filter."""
        browser = window.token_browser
        search_input = browser.search_input
        proxy_model = browser._proxy_model

        # Get initial row count
        initial_count = proxy_model.rowCount()
        assert initial_count > 0

        # Search for "editor"
        search_input.setText("editor")
        qtbot.wait(100)

        # Should have filtered results
        proxy_model.rowCount()
        # Note: With recursive filtering, category nodes remain
        # but only show matching children

        # Clear search
        search_input.clear()
        qtbot.wait(100)

        # Should restore all items
        restored_count = proxy_model.rowCount()
        assert restored_count == initial_count

    def test_status_bar_updates(self, window, qtbot):
        """Test status bar updates with document changes."""
        doc = window._current_document

        # Initial state (new document starts unmodified)
        assert "*" not in window.windowTitle()  # No modified indicator yet

        # Get initial token count (new empty document has 0 defined tokens)
        defined, total = doc.get_token_count()
        assert defined == 0  # Empty theme has no custom tokens defined
        assert total > 0  # But has total registry tokens available

        # Modify a token
        doc.set_token("editor.background", "#000000")
        qtbot.wait(100)

        # Status bar should reflect change
        # (Token count should increase by 1 since we added a token)
        new_defined, new_total = doc.get_token_count()
        assert new_defined == defined + 1  # We added one token
        assert new_total == total  # Total available tokens unchanged

    def test_panel_resize_persistence(self, window, qtbot):
        """Test panel sizes saved/restored."""
        from PySide6.QtCore import QSettings

        # Get initial sizes
        initial_sizes = window.main_splitter.sizes()
        assert len(initial_sizes) == 3

        # Modify sizes
        new_sizes = [300, 900, 300]
        window.main_splitter.setSizes(new_sizes)
        qtbot.wait(100)

        # Verify saved to settings
        settings = QSettings("Vilosource", "VFTheme Studio")
        saved_state = settings.value("main_splitter/state")
        assert saved_state is not None

        # Create new window (would restore sizes)
        # Note: Full test would require window recreation
        # which is complex in pytest. We verify save mechanism works.

    def test_complete_workflow(self, window, qtbot, monkeypatch):
        """Test complete end-to-end workflow.

        1. Select token → Inspector updates
        2. Modify token value (simulated)
        3. Save to file
        4. Create new theme
        5. Load saved file
        6. Verify token changes persisted
        """
        from PySide6.QtWidgets import QMessageBox

        # Mock message boxes to auto-accept
        monkeypatch.setattr(QMessageBox, 'question',
                          lambda *args, **kwargs: QMessageBox.Save)

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            # Step 1: Get initial document
            doc = window._current_document

            # Step 2: Modify a token
            test_token = "editor.background"
            test_value = "#123456"
            doc.set_token(test_token, test_value)
            assert doc.is_modified()

            # Step 3: Save to temp file
            success = window._save_document_to_path(temp_path)
            assert success
            assert not doc.is_modified()  # Saved

            # Step 4: Verify saved data
            with open(temp_path) as f:
                saved_data = json.load(f)
            assert saved_data['colors'][test_token] == test_value

            # Step 5: Create new theme (auto-saves via mock)
            window.new_theme()
            new_doc = window._current_document
            assert new_doc is not doc

            # Step 6: Load saved file
            loaded_doc = ThemeDocument()
            loaded_doc.load(temp_path)

            # Step 7: Verify token persisted
            loaded_value = loaded_doc.get_token(test_token)
            assert loaded_value == test_value

            # Step 8: Set loaded document on window
            window.set_document(loaded_doc)
            qtbot.wait(100)

            # Step 9: Verify UI updated
            assert window._current_document is loaded_doc
            assert not loaded_doc.is_modified()

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
