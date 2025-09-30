#!/usr/bin/env python3
"""
VFWidgets Theme System - Validation Framework
Task 24: Runtime validation system for theme integrity

This module provides comprehensive validation capabilities:
- Schema validation for themes and widgets
- Contract validation for protocols
- Runtime assertion system
- Validation decorators for easy integration
- Configurable validation modes (debug, production, strict)
"""

from .framework import (
    ValidationFramework,
    ValidationMode,
    ValidationError,
    ValidationResult,
    ValidationType
)

from .decorators import (
    validate_theme,
    validate_contract,
    validation_decorator,
    require_valid_color,
    require_theme_structure,
    require_widget_state
)

from .schema import (
    ThemeSchema,
    WidgetSchema,
    ColorSchema,
    StyleSchema,
    validate_schema
)

from .contracts import (
    ThemeProtocol,
    WidgetProtocol,
    ContractValidator,
    validate_protocol_implementation
)

from .assertions import (
    RuntimeAssertion,
    AssertionContext,
    theme_assertions,
    widget_assertions,
    performance_assertions
)

__all__ = [
    # Core framework
    'ValidationFramework',
    'ValidationMode',
    'ValidationError',
    'ValidationResult',
    'ValidationType',

    # Decorators
    'validate_theme',
    'validate_contract',
    'validation_decorator',
    'require_valid_color',
    'require_theme_structure',
    'require_widget_state',

    # Schema validation
    'ThemeSchema',
    'WidgetSchema',
    'ColorSchema',
    'StyleSchema',
    'validate_schema',

    # Contract validation
    'ThemeProtocol',
    'WidgetProtocol',
    'ContractValidator',
    'validate_protocol_implementation',

    # Runtime assertions
    'RuntimeAssertion',
    'AssertionContext',
    'theme_assertions',
    'widget_assertions',
    'performance_assertions'
]

# Version information
__version__ = '1.0.0'
__author__ = 'VFWidgets Theme System'
__description__ = 'Runtime validation framework for theme system integrity'