#!/usr/bin/env python3
"""VFWidgets Theme System - Validation Framework
Task 24: Runtime validation system for theme integrity

This module provides comprehensive validation capabilities:
- Schema validation for themes and widgets
- Contract validation for protocols
- Runtime assertion system
- Validation decorators for easy integration
- Configurable validation modes (debug, production, strict)
"""

from .assertions import (
    AssertionContext,
    RuntimeAssertion,
    performance_assertions,
    theme_assertions,
    widget_assertions,
)
from .contracts import (
    ContractValidator,
    ThemeProtocol,
    WidgetProtocol,
    validate_protocol_implementation,
)
from .decorators import (
    require_theme_structure,
    require_valid_color,
    require_widget_state,
    validate_contract,
    validate_theme,
    validation_decorator,
)
from .framework import (
    ValidationError,
    ValidationFramework,
    ValidationMode,
    ValidationResult,
    ValidationType,
)
from .schema import ColorSchema, StyleSchema, ThemeSchema, WidgetSchema, validate_schema

__all__ = [
    # Core framework
    "ValidationFramework",
    "ValidationMode",
    "ValidationError",
    "ValidationResult",
    "ValidationType",
    # Decorators
    "validate_theme",
    "validate_contract",
    "validation_decorator",
    "require_valid_color",
    "require_theme_structure",
    "require_widget_state",
    # Schema validation
    "ThemeSchema",
    "WidgetSchema",
    "ColorSchema",
    "StyleSchema",
    "validate_schema",
    # Contract validation
    "ThemeProtocol",
    "WidgetProtocol",
    "ContractValidator",
    "validate_protocol_implementation",
    # Runtime assertions
    "RuntimeAssertion",
    "AssertionContext",
    "theme_assertions",
    "widget_assertions",
    "performance_assertions",
]

# Version information
__version__ = "1.0.0"
__author__ = "VFWidgets Theme System"
__description__ = "Runtime validation framework for theme system integrity"
