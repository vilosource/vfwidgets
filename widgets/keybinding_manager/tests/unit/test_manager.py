"""Unit tests for KeybindingManager."""

import pytest
from PySide6.QtWidgets import QMainWindow
from vfwidgets_keybinding.manager import KeybindingManager
from vfwidgets_keybinding.registry import ActionDefinition


class TestKeybindingManager:
    """Test KeybindingManager class."""

    @pytest.fixture
    def manager(self):
        """Create manager with in-memory storage."""
        return KeybindingManager(storage_path=None, auto_save=False)

    @pytest.fixture
    def sample_actions(self):
        """Create sample actions for testing."""
        return [
            ActionDefinition(
                id="file.save", description="Save File", default_shortcut="Ctrl+S", category="File"
            ),
            ActionDefinition(
                id="edit.copy", description="Copy", default_shortcut="Ctrl+C", category="Edit"
            ),
        ]

    def test_register_action(self, manager, sample_actions):
        """Test registering a single action."""
        manager.register_action(sample_actions[0])
        assert manager.get_binding("file.save") == "Ctrl+S"

    def test_register_actions_batch(self, manager, sample_actions):
        """Test registering multiple actions."""
        manager.register_actions(sample_actions)
        assert len(manager.get_all_bindings()) == 2

    def test_load_bindings(self, manager, sample_actions):
        """Test loading bindings merges defaults."""
        manager.register_actions(sample_actions)
        manager.load_bindings()

        assert manager.get_binding("file.save") == "Ctrl+S"
        assert manager.get_binding("edit.copy") == "Ctrl+C"

    def test_set_binding(self, manager, sample_actions):
        """Test changing a keybinding."""
        manager.register_action(sample_actions[0])

        assert manager.set_binding("file.save", "Ctrl+Alt+S") is True
        assert manager.get_binding("file.save") == "Ctrl+Alt+S"

    def test_set_binding_nonexistent_action(self, manager):
        """Test setting binding for unregistered action."""
        assert manager.set_binding("missing.action", "Ctrl+M") is False

    def test_set_binding_to_none(self, manager, sample_actions):
        """Test unbinding an action."""
        manager.register_action(sample_actions[0])

        assert manager.set_binding("file.save", None) is True
        assert manager.get_binding("file.save") is None

    def test_apply_shortcuts(self, qapp, manager, sample_actions):
        """Test applying shortcuts to widget."""
        window = QMainWindow()
        manager.register_actions(sample_actions)

        actions = manager.apply_shortcuts(window)

        assert len(actions) == 2
        assert "file.save" in actions
        assert actions["file.save"].shortcut().toString() == "Ctrl+S"

    def test_apply_shortcuts_specific_actions(self, qapp, manager, sample_actions):
        """Test applying only specific shortcuts."""
        window = QMainWindow()
        manager.register_actions(sample_actions)

        actions = manager.apply_shortcuts(window, action_ids=["file.save"])

        assert len(actions) == 1
        assert "file.save" in actions
        assert "edit.copy" not in actions

    def test_apply_shortcuts_with_callback(self, qapp, manager):
        """Test that callbacks are connected."""
        callback_called = []

        def test_callback():
            callback_called.append(True)

        action = ActionDefinition(id="test.action", description="Test", callback=test_callback)
        manager.register_action(action)

        window = QMainWindow()
        actions = manager.apply_shortcuts(window)

        # Trigger the action
        actions["test.action"].trigger()
        assert callback_called == [True]

    def test_reset_to_defaults(self, manager, sample_actions):
        """Test resetting keybindings to defaults."""
        manager.register_actions(sample_actions)
        manager.set_binding("file.save", "Ctrl+Alt+S")

        assert manager.get_binding("file.save") == "Ctrl+Alt+S"

        manager.reset_to_defaults()

        assert manager.get_binding("file.save") == "Ctrl+S"

    def test_get_actions_by_category(self, manager, sample_actions):
        """Test getting actions by category."""
        manager.register_actions(sample_actions)

        file_actions = manager.get_actions_by_category("File")
        assert len(file_actions) == 1
        assert file_actions[0].id == "file.save"

    def test_get_categories(self, manager, sample_actions):
        """Test getting all categories."""
        manager.register_actions(sample_actions)

        categories = manager.get_categories()
        assert categories == ["Edit", "File"]

    def test_auto_save(self, temp_storage_file, sample_actions):
        """Test auto-save functionality."""
        manager = KeybindingManager(storage_path=str(temp_storage_file), auto_save=True)
        manager.register_action(sample_actions[0])

        # Change binding (should auto-save)
        manager.set_binding("file.save", "Ctrl+Alt+S")

        # Create new manager and load
        manager2 = KeybindingManager(storage_path=str(temp_storage_file))
        manager2.register_action(sample_actions[0])
        manager2.load_bindings()

        assert manager2.get_binding("file.save") == "Ctrl+Alt+S"
