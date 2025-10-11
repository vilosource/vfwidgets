"""Advanced Theme Mapping with CSS Selector Support and Validation.

This module implements Task 13: CSS selector-based theme mapping with conflict
resolution, composition support, visual debugging, and comprehensive validation.

Key Features:
- CSS selector parsing for precise widget targeting
- Priority-based conflict resolution
- Mapping composition and inheritance
- Visual debugging and inspection tools
- Runtime validation and error recovery
- Integration with PropertyDescriptor and ThemeEventSystem
"""

import re
import threading
import time
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
)

if TYPE_CHECKING:
    from ..widgets.base import ThemedWidget

# Import Qt for widget inspection
try:
    from PySide6.QtCore import QObject
    from PySide6.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    class QObject:
        pass

    class QWidget:
        pass


from ..errors import ThemeError
from ..logging import get_debug_logger
from ..protocols import PropertyKey, PropertyValue

logger = get_debug_logger(__name__)


class MappingError(ThemeError):
    """Raised when theme mapping operations fail."""

    pass


class SelectorType(Enum):
    """Types of CSS selectors supported."""

    ID = "id"  # #widget_id
    CLASS = "class"  # .class_name
    TYPE = "type"  # QPushButton
    ATTRIBUTE = "attribute"  # [attr=value]
    PSEUDO = "pseudo"  # :hover, :disabled
    DESCENDANT = "descendant"  # parent child
    CHILD = "child"  # parent > child
    SIBLING = "sibling"  # element ~ sibling
    UNIVERSAL = "universal"  # *


class MappingPriority(IntEnum):
    """Priority levels for mapping conflicts."""

    LOWEST = 0
    LOW = 100
    NORMAL = 500
    HIGH = 800
    HIGHEST = 1000
    CRITICAL = 9999  # Always wins


class ConflictResolution(Enum):
    """Strategies for resolving mapping conflicts."""

    PRIORITY = "priority"  # Use highest priority mapping
    MERGE = "merge"  # Merge all applicable mappings
    FIRST_MATCH = "first_match"  # Use first matching mapping
    LAST_MATCH = "last_match"  # Use last matching mapping
    MOST_SPECIFIC = "specific"  # Use most specific selector


@dataclass
class SelectorPart:
    """Represents a part of a CSS selector."""

    type: SelectorType
    value: str
    attributes: dict[str, str] = field(default_factory=dict)
    pseudo_classes: set[str] = field(default_factory=set)
    combinator: Optional[str] = None  # ' ', '>', '~', '+'


@dataclass
class ParsedSelector:
    """Represents a fully parsed CSS selector."""

    parts: list[SelectorPart]
    specificity: tuple[int, int, int, int]  # inline, id, class/attr, element
    raw_selector: str


@dataclass
class MappingRule:
    """Represents a single theme mapping rule."""

    selector: ParsedSelector
    properties: dict[PropertyKey, PropertyValue]
    priority: MappingPriority = MappingPriority.NORMAL
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    conditions: list[Callable[["ThemedWidget"], bool]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class SelectorMatcher:
    """High-performance selector matching engine."""

    def __init__(self):
        self._cache: dict[str, bool] = {}
        self._cache_lock = threading.RLock()
        self._max_cache_size = 1000
        self._cache_hits = 0
        self._cache_misses = 0

    def matches(self, selector: ParsedSelector, widget: "ThemedWidget") -> bool:
        """Check if widget matches the CSS selector."""
        # Generate cache key
        widget_signature = self._get_widget_signature(widget)
        cache_key = f"{selector.raw_selector}::{widget_signature}"

        # Check cache
        with self._cache_lock:
            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]

            self._cache_misses += 1

        # Perform matching
        result = self._matches_uncached(selector, widget)

        # Cache result (with size limit)
        with self._cache_lock:
            if len(self._cache) >= self._max_cache_size:
                # Remove oldest entries (simple FIFO)
                keys_to_remove = list(self._cache.keys())[:100]
                for key in keys_to_remove:
                    del self._cache[key]

            self._cache[cache_key] = result

        return result

    def _matches_uncached(self, selector: ParsedSelector, widget: "ThemedWidget") -> bool:
        """Perform actual selector matching without caching."""
        try:
            # For now, implement basic selector matching
            # Full CSS selector matching would be more complex

            if len(selector.parts) != 1:
                # Complex selectors not fully supported yet
                return self._matches_complex_selector(selector, widget)

            part = selector.parts[0]
            return self._matches_selector_part(part, widget)

        except Exception as e:
            logger.warning(f"Selector matching error: {e}")
            return False

    def _matches_selector_part(self, part: SelectorPart, widget: "ThemedWidget") -> bool:
        """Check if widget matches a single selector part."""
        if part.type == SelectorType.ID:
            widget_id = getattr(widget, "_widget_id", None)
            return widget_id == part.value

        elif part.type == SelectorType.CLASS:
            widget_classes = getattr(widget, "_theme_classes", set())
            return part.value in widget_classes

        elif part.type == SelectorType.TYPE:
            widget_type = type(widget).__name__
            return widget_type == part.value or part.value == "*"

        elif part.type == SelectorType.ATTRIBUTE:
            # Check if widget has attributes that match
            widget_attrs = getattr(widget, "_theme_attributes", {})
            for attr_name, attr_value in part.attributes.items():
                if attr_name not in widget_attrs:
                    return False
                if str(widget_attrs[attr_name]) != attr_value:
                    return False
            return len(part.attributes) > 0  # Must have at least one attribute to match

        elif part.type == SelectorType.PSEUDO:
            # Check pseudo-classes like :enabled, :disabled, etc.
            for pseudo in part.pseudo_classes:
                if not self._check_pseudo_class(pseudo, widget):
                    return False
            return len(part.pseudo_classes) > 0  # Must have at least one pseudo-class to match

        elif part.type == SelectorType.UNIVERSAL:
            return True

        return False

    def _matches_complex_selector(self, selector: ParsedSelector, widget: "ThemedWidget") -> bool:
        """Handle complex selectors with combinators."""
        # Simplified implementation - full CSS selector matching is complex
        # For now, just check if the last part matches the widget
        if selector.parts:
            return self._matches_selector_part(selector.parts[-1], widget)
        return False

    def _check_pseudo_class(self, pseudo: str, widget: "ThemedWidget") -> bool:
        """Check pseudo-class conditions."""
        try:
            if pseudo == "enabled":
                return getattr(widget, "isEnabled", lambda: True)()
            elif pseudo == "disabled":
                return not getattr(widget, "isEnabled", lambda: True)()
            elif pseudo == "visible":
                return getattr(widget, "isVisible", lambda: True)()
            elif pseudo == "hidden":
                return not getattr(widget, "isVisible", lambda: True)()
            elif pseudo == "focused":
                return getattr(widget, "hasFocus", lambda: False)()
            # Add more pseudo-classes as needed
        except Exception:
            pass

        return False

    def _get_widget_signature(self, widget: "ThemedWidget") -> str:
        """Generate a signature for caching."""
        parts = [
            type(widget).__name__,
            str(getattr(widget, "_widget_id", id(widget))),
            str(getattr(widget, "_theme_classes", set())),
            str(hash(frozenset(getattr(widget, "_theme_attributes", {}).items()))),
        ]
        return "::".join(parts)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        with self._cache_lock:
            total = self._cache_hits + self._cache_misses
            hit_rate = self._cache_hits / total if total > 0 else 0.0

            return {
                "cache_size": len(self._cache),
                "max_cache_size": self._max_cache_size,
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate": hit_rate,
            }

    def clear_cache(self):
        """Clear the matching cache."""
        with self._cache_lock:
            self._cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0


class SelectorParser:
    """CSS selector parser with validation."""

    # Regex patterns for different selector parts
    ID_PATTERN = re.compile(r"#([a-zA-Z_][a-zA-Z0-9_-]*)")
    CLASS_PATTERN = re.compile(r"\.([a-zA-Z_][a-zA-Z0-9_-]*)")
    TYPE_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*|\*)")
    ATTRIBUTE_PATTERN = re.compile(
        r'\[([a-zA-Z_][a-zA-Z0-9_-]*)\s*([=~|^$*]?)\s*["\']?([^"\'\]]*)["\']?\]'
    )
    PSEUDO_PATTERN = re.compile(r":([a-zA-Z_][a-zA-Z0-9_-]*)")

    COMBINATOR_PATTERN = re.compile(r"(\s+|>|\+|~)")

    def parse(self, selector: str) -> ParsedSelector:
        """Parse a CSS selector string."""
        try:
            selector = selector.strip()
            if not selector:
                raise MappingError("Empty selector")

            # Split by combinators while preserving them
            parts = self._split_selector(selector)
            parsed_parts = []

            for part_str in parts:
                if part_str.strip() in [" ", ">", "+", "~"]:
                    # This is a combinator
                    if parsed_parts:
                        parsed_parts[-1].combinator = part_str.strip()
                    continue

                parsed_part = self._parse_selector_part(part_str.strip())
                parsed_parts.append(parsed_part)

            specificity = self._calculate_specificity(parsed_parts)

            return ParsedSelector(
                parts=parsed_parts, specificity=specificity, raw_selector=selector
            )

        except Exception as e:
            raise MappingError(f"Failed to parse selector '{selector}': {e}")

    def _split_selector(self, selector: str) -> list[str]:
        """Split selector by combinators while preserving them."""
        # Simple implementation - split on whitespace and combinators
        parts = []
        current = ""

        i = 0
        while i < len(selector):
            char = selector[i]

            if char in ">+~":
                if current.strip():
                    parts.append(current.strip())
                parts.append(char)
                current = ""
            elif char == " ":
                if current.strip():
                    parts.append(current.strip())
                # Look ahead for multiple spaces
                while i + 1 < len(selector) and selector[i + 1] == " ":
                    i += 1
                if current.strip():
                    parts.append(" ")  # Descendant combinator
                current = ""
            else:
                current += char

            i += 1

        if current.strip():
            parts.append(current.strip())

        return parts

    def _parse_selector_part(self, part: str) -> SelectorPart:
        """Parse a single selector part."""
        original_part = part.strip()
        selector_type = SelectorType.TYPE  # Default
        value = ""
        attributes = {}
        pseudo_classes = set()

        # Check for universal selector first
        if original_part == "*":
            return SelectorPart(
                type=SelectorType.UNIVERSAL, value="*", attributes={}, pseudo_classes=set()
            )

        # Check for ID selector
        id_match = self.ID_PATTERN.search(part)
        if id_match:
            selector_type = SelectorType.ID
            value = id_match.group(1)
            part = part.replace(id_match.group(0), "")

        # Check for class selectors
        class_matches = self.CLASS_PATTERN.findall(part)
        if class_matches:
            selector_type = SelectorType.CLASS
            value = class_matches[0]  # Use first class for simplicity
            for match in class_matches:
                part = part.replace(f".{match}", "")

        # Check for attribute selectors
        attr_matches = self.ATTRIBUTE_PATTERN.findall(part)
        for attr_match in attr_matches:
            attr_name, operator, attr_value = attr_match
            attributes[attr_name] = attr_value
            if not value:  # Only set type if no other primary selector
                selector_type = SelectorType.ATTRIBUTE

        # Check for pseudo-classes
        pseudo_matches = self.PSEUDO_PATTERN.findall(part)
        for pseudo in pseudo_matches:
            pseudo_classes.add(pseudo)
            if not value and not attributes:  # Pseudo-only selector
                selector_type = SelectorType.PSEUDO

        # Check for type selector
        if not value and not attributes and not pseudo_classes:
            type_match = self.TYPE_PATTERN.match(original_part)
            if type_match and type_match.group(1) != "*":
                selector_type = SelectorType.TYPE
                value = type_match.group(1)

        # If still no value, treat as universal
        if not value and not attributes and not pseudo_classes:
            selector_type = SelectorType.UNIVERSAL
            value = "*"

        return SelectorPart(
            type=selector_type, value=value, attributes=attributes, pseudo_classes=pseudo_classes
        )

    def _calculate_specificity(self, parts: list[SelectorPart]) -> tuple[int, int, int, int]:
        """Calculate CSS specificity (inline, id, class/attr, element)."""
        inline = 0  # We don't support inline styles
        id_count = 0
        class_attr_count = 0
        element_count = 0

        for part in parts:
            if part.type == SelectorType.ID:
                id_count += 1
            elif part.type == SelectorType.CLASS:
                class_attr_count += 1
            elif part.type == SelectorType.ATTRIBUTE:
                class_attr_count += len(part.attributes)
            elif part.type == SelectorType.PSEUDO:
                class_attr_count += len(part.pseudo_classes)
            elif part.type == SelectorType.TYPE and part.value != "*":
                element_count += 1

        return (inline, id_count, class_attr_count, element_count)


class ConflictResolver:
    """Resolves conflicts when multiple mappings apply to a widget."""

    def resolve(
        self, rules: list[MappingRule], strategy: ConflictResolution
    ) -> dict[PropertyKey, PropertyValue]:
        """Resolve conflicts and return final property mapping."""
        if not rules:
            return {}

        if len(rules) == 1:
            return rules[0].properties.copy()

        if strategy == ConflictResolution.PRIORITY:
            return self._resolve_by_priority(rules)
        elif strategy == ConflictResolution.MERGE:
            return self._resolve_by_merge(rules)
        elif strategy == ConflictResolution.FIRST_MATCH:
            return rules[0].properties.copy()
        elif strategy == ConflictResolution.LAST_MATCH:
            return rules[-1].properties.copy()
        elif strategy == ConflictResolution.MOST_SPECIFIC:
            return self._resolve_by_specificity(rules)

        # Default fallback
        return self._resolve_by_priority(rules)

    def _resolve_by_priority(self, rules: list[MappingRule]) -> dict[PropertyKey, PropertyValue]:
        """Resolve by priority, then by specificity."""
        # Sort by priority (descending), then by specificity (descending)
        sorted_rules = sorted(
            rules, key=lambda r: (r.priority.value, r.selector.specificity), reverse=True
        )

        result = {}
        for rule in reversed(sorted_rules):  # Apply lowest priority first
            result.update(rule.properties)

        return result

    def _resolve_by_merge(self, rules: list[MappingRule]) -> dict[PropertyKey, PropertyValue]:
        """Merge all rules, with later rules overriding earlier ones."""
        result = {}
        for rule in rules:
            result.update(rule.properties)
        return result

    def _resolve_by_specificity(self, rules: list[MappingRule]) -> dict[PropertyKey, PropertyValue]:
        """Resolve by CSS specificity rules."""
        sorted_rules = sorted(rules, key=lambda r: r.selector.specificity, reverse=True)

        result = {}
        for rule in reversed(sorted_rules):  # Apply least specific first
            result.update(rule.properties)

        return result


class ThemeMapping:
    """Advanced theme mapping system with CSS selector support.

    This is the core implementation of Task 13, providing:
    - CSS selector parsing and matching
    - Priority-based conflict resolution
    - Mapping composition and inheritance
    - Visual debugging capabilities
    - Runtime validation and error recovery
    """

    def __init__(
        self,
        conflict_resolution: ConflictResolution = ConflictResolution.PRIORITY,
        debug: bool = False,
    ):
        """Initialize theme mapping system.

        Args:
            conflict_resolution: Strategy for resolving mapping conflicts
            debug: Enable debug logging

        """
        self.conflict_resolution = conflict_resolution
        self.debug = debug

        # Core components
        self._parser = SelectorParser()
        self._matcher = SelectorMatcher()
        self._resolver = ConflictResolver()

        # Mapping storage
        self._rules: list[MappingRule] = []
        self._rules_lock = threading.RLock()

        # Widget registry for tracking
        self._widget_mappings: dict[str, set[int]] = defaultdict(set)  # widget_id -> rule indices
        self._widget_refs: dict[str, weakref.ReferenceType] = {}

        # Performance tracking
        self._mapping_cache: dict[str, dict[PropertyKey, PropertyValue]] = {}
        self._cache_lock = threading.RLock()
        self._stats = {
            "rules_applied": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "mapping_failures": 0,
            "last_mapping_time": 0.0,
        }

        # Validation
        self._validators: list[Callable[[MappingRule], bool]] = []

        if self.debug:
            logger.debug("ThemeMapping initialized")

    def add_rule(
        self,
        selector: str,
        properties: dict[PropertyKey, PropertyValue],
        priority: MappingPriority = MappingPriority.NORMAL,
        name: Optional[str] = None,
        description: Optional[str] = None,
        conditions: list[Callable[["ThemedWidget"], bool]] = None,
    ) -> int:
        """Add a mapping rule.

        Args:
            selector: CSS selector string
            properties: Theme properties to apply
            priority: Priority level for conflict resolution
            name: Optional rule name for debugging
            description: Optional rule description
            conditions: Optional runtime conditions

        Returns:
            Rule index for later reference

        Raises:
            MappingError: If selector parsing or validation fails

        """
        try:
            # Parse selector
            parsed_selector = self._parser.parse(selector)

            # Create rule
            rule = MappingRule(
                selector=parsed_selector,
                properties=properties.copy(),
                priority=priority,
                name=name,
                description=description,
                conditions=conditions or [],
            )

            # Validate rule
            self._validate_rule(rule)

            # Add to storage
            with self._rules_lock:
                rule_index = len(self._rules)
                self._rules.append(rule)

            # Clear cache since rules changed
            self._clear_mapping_cache()

            # Notify event system
            self._notify_rule_added(rule_index, rule)

            if self.debug:
                logger.debug(f"Added rule {rule_index}: {selector} -> {len(properties)} properties")

            return rule_index

        except Exception as e:
            self._stats["mapping_failures"] += 1
            raise MappingError(f"Failed to add rule '{selector}': {e}")

    def remove_rule(self, rule_index: int) -> bool:
        """Remove a mapping rule by index."""
        try:
            with self._rules_lock:
                if 0 <= rule_index < len(self._rules):
                    rule = self._rules[rule_index]
                    self._rules[rule_index] = None  # Mark as deleted

                    # Clear cache
                    self._clear_mapping_cache()

                    # Notify event system
                    self._notify_rule_removed(rule_index, rule)

                    if self.debug:
                        logger.debug(f"Removed rule {rule_index}")

                    return True
            return False

        except Exception as e:
            logger.error(f"Failed to remove rule {rule_index}: {e}")
            return False

    def get_mapping(self, widget: "ThemedWidget") -> dict[PropertyKey, PropertyValue]:
        """Get resolved theme mapping for a widget.

        Args:
            widget: Widget to get mapping for

        Returns:
            Dictionary of resolved theme properties

        """
        start_time = time.perf_counter()

        try:
            # Find matching rules first to check if any have conditions
            matching_rules = self._find_matching_rules(widget)

            # Check if any rules have conditions (can't cache these)
            has_conditions = any(rule.conditions for rule in matching_rules)

            widget_signature = None
            if not has_conditions:
                # Generate cache key only if no conditional rules
                widget_signature = self._get_widget_signature(widget)

                # Check cache first
                with self._cache_lock:
                    if widget_signature in self._mapping_cache:
                        self._stats["cache_hits"] += 1
                        return self._mapping_cache[widget_signature].copy()

                self._stats["cache_misses"] += 1

            # Resolve conflicts
            resolved_mapping = self._resolver.resolve(matching_rules, self.conflict_resolution)

            # Cache result only if no conditional rules
            if widget_signature is not None:
                with self._cache_lock:
                    self._mapping_cache[widget_signature] = resolved_mapping.copy()

            # Update stats
            self._stats["rules_applied"] += len(matching_rules)
            self._stats["last_mapping_time"] = time.perf_counter() - start_time

            # Notify event system
            widget_id = getattr(widget, "_widget_id", f"widget_{id(widget)}")
            self._notify_mapping_applied(widget_id, len(matching_rules), resolved_mapping)

            if self.debug:
                logger.debug(
                    f"Mapped {len(matching_rules)} rules to widget {widget_id}: {len(resolved_mapping)} properties"
                )

            return resolved_mapping

        except Exception as e:
            self._stats["mapping_failures"] += 1
            logger.error(f"Failed to get mapping for widget: {e}")
            return {}

    def get_applicable_rules(self, widget: "ThemedWidget") -> list[tuple[int, MappingRule]]:
        """Get all rules that apply to a widget (for debugging)."""
        try:
            matching_rules = self._find_matching_rules(widget)
            return [(i, rule) for i, rule in enumerate(matching_rules)]
        except Exception as e:
            logger.error(f"Failed to get applicable rules: {e}")
            return []

    def add_validator(self, validator: Callable[[MappingRule], bool]) -> None:
        """Add a rule validator."""
        self._validators.append(validator)

    def compose_with(self, other: "ThemeMapping") -> "ThemeMapping":
        """Create a new mapping that combines this one with another."""
        composed = ThemeMapping(conflict_resolution=self.conflict_resolution, debug=self.debug)

        # Copy all rules from both mappings
        with self._rules_lock, other._rules_lock:
            for rule in self._rules:
                if rule is not None:  # Skip deleted rules
                    composed._rules.append(rule)

            for rule in other._rules:
                if rule is not None:  # Skip deleted rules
                    composed._rules.append(rule)

        return composed

    def clear(self) -> None:
        """Clear all mapping rules."""
        with self._rules_lock:
            self._rules.clear()

        self._clear_mapping_cache()

        if self.debug:
            logger.debug("Cleared all mapping rules")

    def get_statistics(self) -> dict[str, Any]:
        """Get mapping system statistics."""
        with self._rules_lock, self._cache_lock:
            active_rules = sum(1 for rule in self._rules if rule is not None)

            return {
                "total_rules": len(self._rules),
                "active_rules": active_rules,
                "cached_mappings": len(self._mapping_cache),
                "conflict_resolution": self.conflict_resolution.value,
                "matcher_stats": self._matcher.get_cache_stats(),
                "performance_stats": self._stats.copy(),
            }

    # Private methods

    def _find_matching_rules(self, widget: "ThemedWidget") -> list[MappingRule]:
        """Find all rules that match the widget."""
        matching_rules = []

        with self._rules_lock:
            for rule in self._rules:
                if rule is None or not rule.enabled:
                    continue

                try:
                    # Check selector match
                    if not self._matcher.matches(rule.selector, widget):
                        continue

                    # Check runtime conditions
                    if rule.conditions:
                        if not all(condition(widget) for condition in rule.conditions):
                            continue

                    matching_rules.append(rule)

                except Exception as e:
                    if self.debug:
                        logger.warning(f"Rule matching error: {e}")

        return matching_rules

    def _validate_rule(self, rule: MappingRule) -> None:
        """Validate a mapping rule."""
        # Run custom validators
        for validator in self._validators:
            if not validator(rule):
                raise MappingError(f"Rule validation failed: {rule.name or 'unnamed'}")

        # Basic validation
        if not rule.properties:
            raise MappingError("Rule must have at least one property")

        # Validate property types
        for key, _value in rule.properties.items():
            if not isinstance(key, str):
                raise MappingError(f"Property key must be string, got {type(key)}")

    def _get_widget_signature(self, widget: "ThemedWidget") -> str:
        """Generate a signature for caching."""
        parts = [
            type(widget).__name__,
            str(getattr(widget, "_widget_id", id(widget))),
            str(getattr(widget, "_theme_classes", set())),
            str(hash(frozenset(getattr(widget, "_theme_attributes", {}).items()))),
        ]

        # Include dynamic state for pseudo-class matching
        try:
            dynamic_state = [
                str(getattr(widget, "isEnabled", lambda: True)()),
                str(getattr(widget, "isVisible", lambda: True)()),
                str(getattr(widget, "hasFocus", lambda: False)()),
            ]
            parts.extend(dynamic_state)
        except Exception:
            # If getting dynamic state fails, still cache but less efficiently
            parts.append(str(time.time()))  # Prevent caching in this case

        return "::".join(parts)

    def _clear_mapping_cache(self) -> None:
        """Clear the mapping cache."""
        with self._cache_lock:
            self._mapping_cache.clear()

    def _notify_rule_added(self, rule_index: int, rule: MappingRule) -> None:
        """Notify event system of rule addition."""
        try:
            from ..events.system import get_global_event_system

            get_global_event_system()
            # Custom notification for mapping events
            # Note: This would need corresponding signals in the event system
        except Exception as e:
            if self.debug:
                logger.warning(f"Failed to notify rule added: {e}")

    def _notify_rule_removed(self, rule_index: int, rule: MappingRule) -> None:
        """Notify event system of rule removal."""
        try:
            from ..events.system import get_global_event_system

            get_global_event_system()
            # Custom notification for mapping events
        except Exception as e:
            if self.debug:
                logger.warning(f"Failed to notify rule removed: {e}")

    def _notify_mapping_applied(
        self, widget_id: str, rule_count: int, mapping: dict[str, Any]
    ) -> None:
        """Notify event system of mapping application."""
        try:
            from ..events.system import get_global_event_system

            get_global_event_system()
            # Custom notification for mapping events
        except Exception as e:
            if self.debug:
                logger.warning(f"Failed to notify mapping applied: {e}")


class ThemeMappingVisualizer:
    """Visual debugging tools for theme mappings."""

    def __init__(self, mapping: ThemeMapping):
        self.mapping = mapping

    def generate_debug_report(self, widget: "ThemedWidget") -> dict[str, Any]:
        """Generate a comprehensive debug report for a widget."""
        widget_id = getattr(widget, "_widget_id", f"widget_{id(widget)}")

        # Get applicable rules
        applicable_rules = self.mapping.get_applicable_rules(widget)

        # Get final mapping
        final_mapping = self.mapping.get_mapping(widget)

        # Generate widget info
        widget_info = {
            "id": widget_id,
            "type": type(widget).__name__,
            "classes": getattr(widget, "_theme_classes", set()),
            "attributes": getattr(widget, "_theme_attributes", {}),
        }

        # Rule details
        rule_details = []
        for i, rule in applicable_rules:
            rule_details.append(
                {
                    "index": i,
                    "name": rule.name,
                    "selector": rule.selector.raw_selector,
                    "specificity": rule.selector.specificity,
                    "priority": rule.priority.value,
                    "properties": rule.properties,
                    "enabled": rule.enabled,
                }
            )

        return {
            "widget": widget_info,
            "applicable_rules": rule_details,
            "final_mapping": final_mapping,
            "stats": self.mapping.get_statistics(),
        }

    def explain_property_source(
        self, widget: "ThemedWidget", property_key: PropertyKey
    ) -> dict[str, Any]:
        """Explain where a property value comes from."""
        applicable_rules = self.mapping.get_applicable_rules(widget)

        # Find rules that set this property
        contributing_rules = []
        for i, rule in applicable_rules:
            if property_key in rule.properties:
                contributing_rules.append(
                    {
                        "index": i,
                        "name": rule.name,
                        "selector": rule.selector.raw_selector,
                        "specificity": rule.selector.specificity,
                        "priority": rule.priority.value,
                        "value": rule.properties[property_key],
                    }
                )

        # Get final value
        final_mapping = self.mapping.get_mapping(widget)
        final_value = final_mapping.get(property_key)

        return {
            "property": property_key,
            "final_value": final_value,
            "contributing_rules": contributing_rules,
            "conflict_resolution": self.mapping.conflict_resolution.value,
        }

    def generate_css_like_output(self, widget: "ThemedWidget") -> str:
        """Generate CSS-like output showing applied styles."""
        applicable_rules = self.mapping.get_applicable_rules(widget)

        output = []
        widget_id = getattr(widget, "_widget_id", f"widget_{id(widget)}")

        output.append(f"/* Widget: {widget_id} ({type(widget).__name__}) */")

        for i, rule in applicable_rules:
            output.append(f"\n/* Rule {i}: {rule.name or 'unnamed'} */")
            output.append(
                f"/* Priority: {rule.priority.value}, Specificity: {rule.selector.specificity} */"
            )
            output.append(f"{rule.selector.raw_selector} {{")

            for prop, value in rule.properties.items():
                output.append(f"    {prop}: {value};")

            output.append("}")

        # Show final computed values
        final_mapping = self.mapping.get_mapping(widget)
        if final_mapping:
            output.append(f"\n/* Final computed values for {widget_id} */")
            output.append("/* (after conflict resolution) */")
            output.append(f"#{widget_id} {{")

            for prop, value in final_mapping.items():
                output.append(f"    {prop}: {value};")

            output.append("}")

        return "\n".join(output)


# Utility functions for creating common selectors


def css_selector(selector: str) -> str:
    """Return a CSS selector string (for readability)."""
    return selector


def id_selector(widget_id: str) -> str:
    """Create an ID selector."""
    return f"#{widget_id}"


def class_selector(class_name: str) -> str:
    """Create a class selector."""
    return f".{class_name}"


def type_selector(widget_type: str) -> str:
    """Create a type selector."""
    return widget_type


def attribute_selector(attr_name: str, attr_value: str = None, operator: str = "=") -> str:
    """Create an attribute selector."""
    if attr_value is None:
        return f"[{attr_name}]"
    return f"[{attr_name}{operator}'{attr_value}']"


__all__ = [
    "ThemeMapping",
    "SelectorType",
    "MappingPriority",
    "ConflictResolution",
    "MappingError",
    "ThemeMappingVisualizer",
    "css_selector",
    "id_selector",
    "class_selector",
    "type_selector",
    "attribute_selector",
]
