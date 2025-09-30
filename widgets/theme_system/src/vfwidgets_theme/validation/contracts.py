#!/usr/bin/env python3
"""
VFWidgets Theme System - Contract Validation
Task 24: Contract validation for protocols and interfaces

This module provides contract validation capabilities to ensure
objects implement required protocols correctly.
"""

from typing import Any, Dict, List, Optional, Protocol, Type, runtime_checkable
from abc import ABC, abstractmethod
from .framework import ValidationResult, ValidationType


@runtime_checkable
class ThemeProtocol(Protocol):
    """Protocol for theme objects."""

    name: str
    colors: Dict[str, Any]
    styles: Dict[str, Any]

    def get_color(self, color_name: str) -> str:
        """Get a color value by name."""
        ...

    def get_style(self, style_name: str) -> Any:
        """Get a style value by name."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary representation."""
        ...


@runtime_checkable
class WidgetProtocol(Protocol):
    """Protocol for themeable widgets."""

    def apply_theme(self, theme: Any) -> None:
        """Apply a theme to the widget."""
        ...

    def get_current_theme(self) -> Optional[Any]:
        """Get the currently applied theme."""
        ...

    def supports_theme_property(self, property_name: str) -> bool:
        """Check if widget supports a theme property."""
        ...


@runtime_checkable
class ThemeProviderProtocol(Protocol):
    """Protocol for theme providers."""

    def get_theme(self, theme_name: str) -> Optional[Any]:
        """Get a theme by name."""
        ...

    def list_themes(self) -> List[str]:
        """List available theme names."""
        ...

    def add_theme(self, theme: Any) -> None:
        """Add a new theme."""
        ...

    def remove_theme(self, theme_name: str) -> bool:
        """Remove a theme."""
        ...


@runtime_checkable
class ThemeApplicatorProtocol(Protocol):
    """Protocol for theme applicators."""

    def apply_theme_to_widget(self, widget: Any, theme: Any) -> bool:
        """Apply theme to a specific widget."""
        ...

    def apply_theme_to_application(self, theme: Any) -> bool:
        """Apply theme to entire application."""
        ...

    def can_apply_theme(self, widget: Any, theme: Any) -> bool:
        """Check if theme can be applied to widget."""
        ...


class ContractValidator:
    """Validator for protocol contracts."""

    def __init__(self):
        self._protocol_validators: Dict[Type, List[callable]] = {}

    def register_protocol_validator(self, protocol: Type, validator: callable):
        """Register a custom validator for a protocol."""
        if protocol not in self._protocol_validators:
            self._protocol_validators[protocol] = []
        self._protocol_validators[protocol].append(validator)

    def validate_protocol_implementation(self, obj: Any, protocol: Type) -> ValidationResult:
        """
        Validate that an object implements a protocol correctly.

        Args:
            obj: Object to validate
            protocol: Protocol to validate against

        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(
            passed=True,
            validation_type=ValidationType.CONTRACT,
            message=f"Contract validation for {protocol.__name__}",
            context={
                'object_type': type(obj).__name__,
                'protocol': protocol.__name__
            }
        )

        # Basic isinstance check using Protocol
        if hasattr(protocol, '__protocols__') or hasattr(protocol, '_is_protocol'):
            if not isinstance(obj, protocol):
                result.add_error(f"Object does not implement {protocol.__name__} protocol")
                return result

        # Validate required attributes
        required_attrs = self._get_protocol_attributes(protocol)
        for attr_name, attr_type in required_attrs.items():
            if not hasattr(obj, attr_name):
                result.add_error(f"Missing required attribute: {attr_name}")
                continue

            attr_value = getattr(obj, attr_name)

            # Check if attribute is callable when expected
            if callable(attr_type) and not callable(attr_value):
                result.add_error(f"Attribute {attr_name} should be callable")
            elif not callable(attr_type) and callable(attr_value):
                result.add_error(f"Attribute {attr_name} should not be callable")

        # Validate required methods
        required_methods = self._get_protocol_methods(protocol)
        for method_name, method_signature in required_methods.items():
            if not hasattr(obj, method_name):
                result.add_error(f"Missing required method: {method_name}")
                continue

            method = getattr(obj, method_name)
            if not callable(method):
                result.add_error(f"Method {method_name} is not callable")
                continue

            # Validate method signature (basic check)
            try:
                import inspect
                sig = inspect.signature(method)
                expected_params = len(method_signature.get('params', []))
                actual_params = len([p for p in sig.parameters.values()
                                   if p.default == p.empty])

                if actual_params > expected_params:
                    result.add_warning(f"Method {method_name} has more parameters than expected")
            except Exception:
                # Signature validation failed, but method exists
                pass

        # Run custom validators
        if protocol in self._protocol_validators:
            for validator in self._protocol_validators[protocol]:
                try:
                    validator(obj, result)
                except Exception as e:
                    result.add_error(f"Custom validator failed: {e}")

        # Protocol-specific validations
        if protocol == ThemeProtocol:
            self._validate_theme_protocol(obj, result)
        elif protocol == WidgetProtocol:
            self._validate_widget_protocol(obj, result)
        elif protocol == ThemeProviderProtocol:
            self._validate_theme_provider_protocol(obj, result)
        elif protocol == ThemeApplicatorProtocol:
            self._validate_theme_applicator_protocol(obj, result)

        if not result.errors:
            result.message = f"Contract validation passed for {protocol.__name__}"

        return result

    def _get_protocol_attributes(self, protocol: Type) -> Dict[str, Any]:
        """Extract required attributes from protocol."""
        attrs = {}
        if hasattr(protocol, '__annotations__'):
            attrs.update(protocol.__annotations__)
        return attrs

    def _get_protocol_methods(self, protocol: Type) -> Dict[str, Dict[str, Any]]:
        """Extract required methods from protocol."""
        methods = {}
        for name in dir(protocol):
            if not name.startswith('_'):
                attr = getattr(protocol, name, None)
                if callable(attr):
                    methods[name] = {'params': []}  # Simplified signature
        return methods

    def _validate_theme_protocol(self, obj: Any, result: ValidationResult):
        """Validate theme-specific contract requirements."""
        # Check that colors and styles are accessible
        if hasattr(obj, 'colors'):
            if not isinstance(obj.colors, dict):
                result.add_error("Theme.colors must be a dictionary")

        if hasattr(obj, 'styles'):
            if not isinstance(obj.styles, dict):
                result.add_error("Theme.styles must be a dictionary")

        # Test method functionality
        if hasattr(obj, 'get_color'):
            try:
                # Test with a known color if possible
                if hasattr(obj, 'colors') and obj.colors:
                    first_color = next(iter(obj.colors.keys()))
                    color_value = obj.get_color(first_color)
                    if color_value is None:
                        result.add_warning(f"get_color returned None for existing color: {first_color}")
            except Exception as e:
                result.add_error(f"get_color method failed: {e}")

        if hasattr(obj, 'get_style'):
            try:
                # Test with a known style if possible
                if hasattr(obj, 'styles') and obj.styles:
                    first_style = next(iter(obj.styles.keys()))
                    style_value = obj.get_style(first_style)
                    if style_value is None:
                        result.add_warning(f"get_style returned None for existing style: {first_style}")
            except Exception as e:
                result.add_error(f"get_style method failed: {e}")

    def _validate_widget_protocol(self, obj: Any, result: ValidationResult):
        """Validate widget-specific contract requirements."""
        # Test apply_theme method
        if hasattr(obj, 'apply_theme'):
            # Can't easily test without a real theme, but check it's callable
            if not callable(obj.apply_theme):
                result.add_error("apply_theme is not callable")

        # Test get_current_theme method
        if hasattr(obj, 'get_current_theme'):
            try:
                current_theme = obj.get_current_theme()
                # Should return None or a theme object
                if current_theme is not None and not hasattr(current_theme, 'name'):
                    result.add_warning("get_current_theme returned object without 'name' attribute")
            except Exception as e:
                result.add_error(f"get_current_theme method failed: {e}")

        # Test supports_theme_property method
        if hasattr(obj, 'supports_theme_property'):
            try:
                # Test with common property names
                test_props = ['color', 'background', 'font_size']
                for prop in test_props:
                    supports = obj.supports_theme_property(prop)
                    if not isinstance(supports, bool):
                        result.add_error(f"supports_theme_property should return bool, got {type(supports)}")
                        break
            except Exception as e:
                result.add_error(f"supports_theme_property method failed: {e}")

    def _validate_theme_provider_protocol(self, obj: Any, result: ValidationResult):
        """Validate theme provider-specific contract requirements."""
        if hasattr(obj, 'list_themes'):
            try:
                themes = obj.list_themes()
                if not isinstance(themes, list):
                    result.add_error(f"list_themes should return list, got {type(themes)}")
                elif themes and not all(isinstance(name, str) for name in themes):
                    result.add_error("list_themes should return list of strings")
            except Exception as e:
                result.add_error(f"list_themes method failed: {e}")

        if hasattr(obj, 'get_theme'):
            try:
                # Test with invalid theme name should return None
                nonexistent_theme = obj.get_theme("__nonexistent_theme__")
                if nonexistent_theme is not None:
                    result.add_warning("get_theme should return None for nonexistent themes")
            except Exception as e:
                result.add_error(f"get_theme method failed: {e}")

    def _validate_theme_applicator_protocol(self, obj: Any, result: ValidationResult):
        """Validate theme applicator-specific contract requirements."""
        # Test can_apply_theme method
        if hasattr(obj, 'can_apply_theme'):
            try:
                # Test with None arguments should not crash
                can_apply = obj.can_apply_theme(None, None)
                if not isinstance(can_apply, bool):
                    result.add_error(f"can_apply_theme should return bool, got {type(can_apply)}")
            except Exception as e:
                result.add_error(f"can_apply_theme method failed: {e}")


# Global contract validator instance
_contract_validator = ContractValidator()


def validate_protocol_implementation(obj: Any, protocol: Type) -> ValidationResult:
    """
    Validate that an object implements a protocol correctly.

    Args:
        obj: Object to validate
        protocol: Protocol to validate against

    Returns:
        ValidationResult: Result of validation
    """
    return _contract_validator.validate_protocol_implementation(obj, protocol)


def register_protocol_validator(protocol: Type, validator: callable):
    """
    Register a custom validator for a protocol.

    Args:
        protocol: Protocol to register validator for
        validator: Validator function that takes (obj, result) and modifies result
    """
    _contract_validator.register_protocol_validator(protocol, validator)


# Convenience validation functions
def validate_theme_contract(theme: Any) -> ValidationResult:
    """Validate a theme implements ThemeProtocol."""
    return validate_protocol_implementation(theme, ThemeProtocol)


def validate_widget_contract(widget: Any) -> ValidationResult:
    """Validate a widget implements WidgetProtocol."""
    return validate_protocol_implementation(widget, WidgetProtocol)


def validate_theme_provider_contract(provider: Any) -> ValidationResult:
    """Validate a provider implements ThemeProviderProtocol."""
    return validate_protocol_implementation(provider, ThemeProviderProtocol)


def validate_theme_applicator_contract(applicator: Any) -> ValidationResult:
    """Validate an applicator implements ThemeApplicatorProtocol."""
    return validate_protocol_implementation(applicator, ThemeApplicatorProtocol)


# Additional contract validation utilities
class ContractEnforcer:
    """Enforces contracts at runtime."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def enforce_contract(self, obj: Any, protocol: Type):
        """Enforce that an object meets contract requirements."""
        result = validate_protocol_implementation(obj, protocol)

        if result.has_errors:
            error_msg = f"Contract violation for {protocol.__name__}: {result.errors}"
            if self.strict:
                raise ContractViolationError(error_msg)
            else:
                import logging
                logging.warning(error_msg)

        return result


class ContractViolationError(Exception):
    """Exception raised when contract validation fails."""
    pass


# Testing utilities for contracts
def create_mock_theme() -> Any:
    """Create a mock theme for testing."""
    class MockTheme:
        def __init__(self):
            self.name = "mock_theme"
            self.colors = {"primary": "#007acc", "secondary": "#6f6f6f"}
            self.styles = {"font_size": "12px", "padding": "4px"}

        def get_color(self, color_name: str) -> str:
            return self.colors.get(color_name)

        def get_style(self, style_name: str) -> Any:
            return self.styles.get(style_name)

        def to_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "colors": self.colors,
                "styles": self.styles
            }

    return MockTheme()


def create_mock_widget() -> Any:
    """Create a mock widget for testing."""
    class MockWidget:
        def __init__(self):
            self._current_theme = None
            self._supported_properties = {"color", "background", "font_size"}

        def apply_theme(self, theme: Any) -> None:
            self._current_theme = theme

        def get_current_theme(self) -> Optional[Any]:
            return self._current_theme

        def supports_theme_property(self, property_name: str) -> bool:
            return property_name in self._supported_properties

    return MockWidget()