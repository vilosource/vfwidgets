"""Plugin System for Pattern Matching

This module provides a plugin system for extending pattern matching
capabilities with custom pattern types.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..widgets.base import ThemedWidget

from .matcher import MatchResult


class PatternPlugin(ABC):
    """Base class for pattern matching plugins.

    Plugins can implement custom pattern matching logic that integrates
    seamlessly with the PatternMatcher system.
    """

    def __init__(self, name: str, description: str = ""):
        """Initialize plugin.

        Args:
            name: Unique plugin name
            description: Plugin description

        """
        self.name = name
        self.description = description

    @abstractmethod
    def match(self, pattern: str, target: str, widget: 'ThemedWidget',
              context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """Check if target matches the pattern.

        Args:
            pattern: Pattern string specific to this plugin
            target: String to match against
            widget: Widget instance for context
            context: Additional context for matching

        Returns:
            MatchResult indicating match status and quality

        """
        pass

    @abstractmethod
    def validate_pattern(self, pattern: str) -> bool:
        """Validate a pattern string for this plugin.

        Args:
            pattern: Pattern string to validate

        Returns:
            True if pattern is valid, False otherwise

        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            'name': self.name,
            'description': self.description,
            'type': 'pattern_plugin',
        }


class PluginManager:
    """Manages pattern matching plugins.

    This class handles plugin registration, validation, and lifecycle
    management for the pattern matching system.
    """

    def __init__(self):
        self._plugins: Dict[str, PatternPlugin] = {}

    def register_plugin(self, plugin: PatternPlugin) -> bool:
        """Register a pattern plugin.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registered successfully, False if name conflict

        """
        if plugin.name in self._plugins:
            return False

        self._plugins[plugin.name] = plugin
        return True

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a pattern plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistered successfully, False if not found

        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            return True
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PatternPlugin]:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> Dict[str, PatternPlugin]:
        """Get all registered plugins."""
        return self._plugins.copy()

    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all plugins."""
        return {name: plugin.get_info() for name, plugin in self._plugins.items()}


# Built-in plugins

class HierarchyPlugin(PatternPlugin):
    """Plugin for matching widget hierarchy patterns."""

    def __init__(self):
        super().__init__(
            name="hierarchy",
            description="Match patterns based on widget parent-child relationships"
        )

    def match(self, pattern: str, target: str, widget: 'ThemedWidget',
              context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """Match hierarchy patterns like "Dialog.Button" or "Window>Panel>Button".

        Pattern format:
        - "Parent.Child" - direct parent-child relationship
        - "Ancestor>Descendant" - ancestor-descendant relationship
        - "Widget~Sibling" - sibling relationship
        """
        try:
            # Simple implementation - this would need actual widget hierarchy traversal
            if "." in pattern:
                # Direct parent-child
                parent_type, child_type = pattern.split(".", 1)
                # Would check if widget's parent is of parent_type
                # For now, just check if target contains both
                if parent_type in target and child_type in target:
                    return MatchResult(True, 0.8)

            elif ">" in pattern:
                # Ancestor-descendant
                parts = pattern.split(">")
                # Would traverse widget hierarchy
                # For now, simplified check
                if all(part.strip() in target for part in parts):
                    return MatchResult(True, 0.7)

            elif "~" in pattern:
                # Sibling relationship
                # Would check actual sibling widgets
                return MatchResult(False, 0.0)

            return MatchResult(False, 0.0)

        except Exception:
            return MatchResult(False, 0.0)

    def validate_pattern(self, pattern: str) -> bool:
        """Validate hierarchy pattern syntax."""
        return any(sep in pattern for sep in [".", ">", "~"])


class StatePlugin(PatternPlugin):
    """Plugin for matching widget state patterns."""

    def __init__(self):
        super().__init__(
            name="state",
            description="Match patterns based on widget state (enabled, visible, etc.)"
        )

    def match(self, pattern: str, target: str, widget: 'ThemedWidget',
              context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """Match state patterns like "enabled", "visible", "focused".

        Pattern format:
        - "enabled" - widget is enabled
        - "disabled" - widget is disabled
        - "visible" - widget is visible
        - "hidden" - widget is hidden
        - "focused" - widget has focus
        """
        try:
            if pattern == "enabled":
                enabled = getattr(widget, 'isEnabled', lambda: True)()
                return MatchResult(enabled, 1.0 if enabled else 0.0)

            elif pattern == "disabled":
                enabled = getattr(widget, 'isEnabled', lambda: True)()
                disabled = not enabled
                return MatchResult(disabled, 1.0 if disabled else 0.0)

            elif pattern == "visible":
                visible = getattr(widget, 'isVisible', lambda: True)()
                return MatchResult(visible, 1.0 if visible else 0.0)

            elif pattern == "hidden":
                visible = getattr(widget, 'isVisible', lambda: True)()
                hidden = not visible
                return MatchResult(hidden, 1.0 if hidden else 0.0)

            elif pattern == "focused":
                focused = getattr(widget, 'hasFocus', lambda: False)()
                return MatchResult(focused, 1.0 if focused else 0.0)

            return MatchResult(False, 0.0)

        except Exception:
            return MatchResult(False, 0.0)

    def validate_pattern(self, pattern: str) -> bool:
        """Validate state pattern."""
        valid_states = {"enabled", "disabled", "visible", "hidden", "focused"}
        return pattern in valid_states


class GeometryPlugin(PatternPlugin):
    """Plugin for matching widget geometry patterns."""

    def __init__(self):
        super().__init__(
            name="geometry",
            description="Match patterns based on widget geometry (size, position)"
        )

    def match(self, pattern: str, target: str, widget: 'ThemedWidget',
              context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """Match geometry patterns like "width>100", "height<50", "x=0".

        Pattern format:
        - "width>100" - width greater than 100
        - "height<50" - height less than 50
        - "x=0" - x position equals 0
        - "large" - predefined size category
        """
        try:
            # This would need actual widget geometry access
            # For now, return false for all geometry patterns
            return MatchResult(False, 0.0)

        except Exception:
            return MatchResult(False, 0.0)

    def validate_pattern(self, pattern: str) -> bool:
        """Validate geometry pattern."""
        # Simple validation for demonstration
        return any(op in pattern for op in [">", "<", "=", ">=", "<="])


# Create default plugin manager instance
default_plugin_manager = PluginManager()

# Register built-in plugins
default_plugin_manager.register_plugin(HierarchyPlugin())
default_plugin_manager.register_plugin(StatePlugin())
default_plugin_manager.register_plugin(GeometryPlugin())


__all__ = [
    "PatternPlugin",
    "PluginManager",
    "HierarchyPlugin",
    "StatePlugin",
    "GeometryPlugin",
    "default_plugin_manager",
]
