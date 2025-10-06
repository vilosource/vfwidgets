"""Unit tests for ActionRegistry and ActionDefinition."""

import pytest
from vfwidgets_keybinding.registry import ActionDefinition, ActionRegistry


class TestActionDefinition:
    """Test ActionDefinition dataclass."""

    def test_create_minimal_action(self):
        """Test creating action with minimal fields."""
        action = ActionDefinition(id="test.action", description="Test Action")
        assert action.id == "test.action"
        assert action.description == "Test Action"
        assert action.default_shortcut is None
        assert action.category is None
        assert action.callback is None

    def test_create_full_action(self):
        """Test creating action with all fields."""

        def callback():
            return None

        action = ActionDefinition(
            id="file.save",
            description="Save File",
            default_shortcut="Ctrl+S",
            category="File",
            callback=callback,
        )
        assert action.id == "file.save"
        assert action.description == "Save File"
        assert action.default_shortcut == "Ctrl+S"
        assert action.category == "File"
        assert action.callback is callback

    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Action ID cannot be empty"):
            ActionDefinition(id="", description="Test")

    def test_empty_description_raises_error(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Action description cannot be empty"):
            ActionDefinition(id="test.action", description="")

    def test_invalid_id_format_raises_error(self):
        """Test that non-dot-separated ID raises ValueError."""
        with pytest.raises(ValueError, match="must be dot-separated"):
            ActionDefinition(id="invalid", description="Test")

    def test_action_is_immutable(self):
        """Test that ActionDefinition is frozen."""
        action = ActionDefinition(id="test.action", description="Test")
        with pytest.raises(AttributeError):
            action.id = "new.id"  # type: ignore


class TestActionRegistry:
    """Test ActionRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test."""
        return ActionRegistry()

    @pytest.fixture
    def sample_action(self):
        """Create sample action for tests."""
        return ActionDefinition(
            id="file.save", description="Save File", default_shortcut="Ctrl+S", category="File"
        )

    def test_register_action(self, registry, sample_action):
        """Test registering an action."""
        registry.register(sample_action)
        assert registry.get("file.save") == sample_action

    def test_register_duplicate_raises_error(self, registry, sample_action):
        """Test that registering duplicate ID raises ValueError."""
        registry.register(sample_action)

        duplicate = ActionDefinition(id="file.save", description="Different Description")

        with pytest.raises(ValueError, match="already registered"):
            registry.register(duplicate)

    def test_unregister_action(self, registry, sample_action):
        """Test unregistering an action."""
        registry.register(sample_action)
        registry.unregister("file.save")
        assert registry.get("file.save") is None

    def test_unregister_nonexistent_raises_error(self, registry):
        """Test that unregistering missing action raises KeyError."""
        with pytest.raises(KeyError, match="not registered"):
            registry.unregister("nonexistent.action")

    def test_get_returns_none_for_missing(self, registry):
        """Test that get() returns None for missing actions."""
        assert registry.get("missing.action") is None

    def test_get_all(self, registry):
        """Test getting all actions."""
        action1 = ActionDefinition(id="file.save", description="Save")
        action2 = ActionDefinition(id="edit.copy", description="Copy")

        registry.register(action1)
        registry.register(action2)

        all_actions = registry.get_all()
        assert len(all_actions) == 2
        assert action1 in all_actions
        assert action2 in all_actions

    def test_get_by_category(self, registry):
        """Test filtering actions by category."""
        file_action = ActionDefinition(id="file.save", description="Save", category="File")
        edit_action = ActionDefinition(id="edit.copy", description="Copy", category="Edit")
        no_category = ActionDefinition(id="other.action", description="Other")

        registry.register(file_action)
        registry.register(edit_action)
        registry.register(no_category)

        file_actions = registry.get_by_category("File")
        assert len(file_actions) == 1
        assert file_actions[0] == file_action

    def test_get_categories(self, registry):
        """Test getting unique categories."""
        registry.register(ActionDefinition(id="file.save", description="Save", category="File"))
        registry.register(ActionDefinition(id="file.open", description="Open", category="File"))
        registry.register(ActionDefinition(id="edit.copy", description="Copy", category="Edit"))
        registry.register(ActionDefinition(id="other.action", description="Other"))

        categories = registry.get_categories()
        assert categories == ["Edit", "File"]  # Sorted, excludes None

    def test_clear(self, registry, sample_action):
        """Test clearing all actions."""
        registry.register(sample_action)
        registry.clear()
        assert len(registry.get_all()) == 0
