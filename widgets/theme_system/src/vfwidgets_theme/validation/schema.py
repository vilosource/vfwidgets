#!/usr/bin/env python3
"""VFWidgets Theme System - Schema Validation
Task 24: Schema validation for themes and widgets

This module provides comprehensive schema validation capabilities
for theme system data structures.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Union

from .framework import ValidationResult, ValidationType


class SchemaType(Enum):
    """Schema validation types."""

    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DICT = auto()
    LIST = auto()
    COLOR = auto()
    CSS_UNIT = auto()
    ENUM = auto()
    OPTIONAL = auto()


@dataclass
class SchemaField:
    """Schema field definition."""

    name: str
    schema_type: SchemaType
    required: bool = True
    default: Any = None
    validators: List[Callable] = field(default_factory=list)
    enum_values: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    nested_schema: Optional["Schema"] = None

    def validate(self, value: Any, result: ValidationResult):
        """Validate a value against this field schema."""
        # Handle optional fields
        if value is None:
            if self.required:
                result.add_error(f"Required field '{self.name}' is missing")
            return

        # Type validation
        if not self._validate_type(value):
            result.add_error(
                f"Field '{self.name}' has invalid type: expected {self.schema_type.name}, got {type(value).__name__}"
            )
            return

        # Value constraints
        self._validate_constraints(value, result)

        # Custom validators
        for validator in self.validators:
            try:
                validator(value, result, self.name)
            except Exception as e:
                result.add_error(f"Custom validator failed for field '{self.name}': {e}")

    def _validate_type(self, value: Any) -> bool:
        """Validate the basic type of a value."""
        if self.schema_type == SchemaType.STRING:
            return isinstance(value, str)
        elif self.schema_type == SchemaType.INTEGER:
            return isinstance(value, int)
        elif self.schema_type == SchemaType.FLOAT:
            return isinstance(value, (int, float))
        elif self.schema_type == SchemaType.BOOLEAN:
            return isinstance(value, bool)
        elif self.schema_type == SchemaType.DICT:
            return isinstance(value, dict)
        elif self.schema_type == SchemaType.LIST:
            return isinstance(value, list)
        elif self.schema_type == SchemaType.COLOR:
            return self._is_valid_color(value)
        elif self.schema_type == SchemaType.CSS_UNIT:
            return self._is_valid_css_unit(value)
        elif self.schema_type == SchemaType.ENUM:
            return value in self.enum_values if self.enum_values else True
        elif self.schema_type == SchemaType.OPTIONAL:
            return True  # Optional fields accept any type or None
        else:
            return True

    def _validate_constraints(self, value: Any, result: ValidationResult):
        """Validate value constraints."""
        # Numeric constraints
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                result.add_error(
                    f"Field '{self.name}' value {value} is below minimum {self.min_value}"
                )
            if self.max_value is not None and value > self.max_value:
                result.add_error(
                    f"Field '{self.name}' value {value} is above maximum {self.max_value}"
                )

        # String constraints
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                result.add_error(
                    f"Field '{self.name}' length {len(value)} is below minimum {self.min_length}"
                )
            if self.max_length is not None and len(value) > self.max_length:
                result.add_error(
                    f"Field '{self.name}' length {len(value)} is above maximum {self.max_length}"
                )
            if self.pattern and not re.match(self.pattern, value):
                result.add_error(f"Field '{self.name}' does not match pattern {self.pattern}")

        # Enum constraints
        if self.schema_type == SchemaType.ENUM and self.enum_values:
            if value not in self.enum_values:
                result.add_error(
                    f"Field '{self.name}' value '{value}' not in allowed values {self.enum_values}"
                )

        # Nested schema validation
        if self.nested_schema and isinstance(value, dict):
            nested_result = self.nested_schema.validate(value)
            result.errors.extend(nested_result.errors)
            result.warnings.extend(nested_result.warnings)

    def _is_valid_color(self, value: Any) -> bool:
        """Validate color values."""
        if not isinstance(value, str):
            return False

        # Hex colors
        if value.startswith("#"):
            hex_part = value[1:]
            if len(hex_part) in (3, 4, 6, 8):  # #RGB, #RGBA, #RRGGBB, #RRGGBBAA
                try:
                    int(hex_part, 16)
                    return True
                except ValueError:
                    pass

        # RGB/RGBA functions
        rgb_pattern = r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$"
        rgba_pattern = r"^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-1]?\.?\d*)\s*\)$"
        if re.match(rgb_pattern, value) or re.match(rgba_pattern, value):
            return True

        # Named colors (basic set)
        named_colors = {
            "red",
            "green",
            "blue",
            "white",
            "black",
            "transparent",
            "gray",
            "grey",
            "yellow",
            "cyan",
            "magenta",
            "orange",
            "purple",
            "pink",
            "brown",
        }
        return value.lower() in named_colors

    def _is_valid_css_unit(self, value: Any) -> bool:
        """Validate CSS unit values."""
        if not isinstance(value, str):
            return False

        # CSS unit pattern: number followed by optional unit
        pattern = r"^-?\d*\.?\d+(px|em|rem|%|vh|vw|pt|pc|in|cm|mm|ex|ch)?$"
        return re.match(pattern, value) is not None


class Schema:
    """Schema definition for data validation."""

    def __init__(self, name: str, fields: List[SchemaField] = None):
        self.name = name
        self.fields = fields or []
        self._field_map = {field.name: field for field in self.fields}

    def add_field(self, field: SchemaField):
        """Add a field to the schema."""
        self.fields.append(field)
        self._field_map[field.name] = field

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against this schema."""
        result = ValidationResult(
            passed=True,
            validation_type=ValidationType.SCHEMA,
            message=f"Schema validation for {self.name}",
        )

        if not isinstance(data, dict):
            result.add_error(f"Expected dictionary for {self.name}, got {type(data).__name__}")
            return result

        # Validate each field
        for field in self.fields:
            value = data.get(field.name)
            field.validate(value, result)

        # Check for unexpected fields (warnings only)
        expected_fields = set(self._field_map.keys())
        actual_fields = set(data.keys())
        unexpected_fields = actual_fields - expected_fields
        for field in unexpected_fields:
            result.add_warning(f"Unexpected field '{field}' in {self.name}")

        # Final validation result
        if not result.errors:
            result.message = f"Schema validation passed for {self.name}"

        return result

    def get_default_data(self) -> Dict[str, Any]:
        """Get default data structure based on schema."""
        data = {}
        for field in self.fields:
            if field.default is not None:
                data[field.name] = field.default
            elif not field.required:
                data[field.name] = None

        return data


# Common validator functions
def validate_hex_color(value: Any, result: ValidationResult, field_name: str):
    """Validate hex color format."""
    if isinstance(value, str) and value.startswith("#"):
        hex_part = value[1:]
        if len(hex_part) not in (3, 6, 8):
            result.add_error(f"Invalid hex color length in {field_name}: {value}")
        try:
            int(hex_part, 16)
        except ValueError:
            result.add_error(f"Invalid hex color format in {field_name}: {value}")


def validate_positive_number(value: Any, result: ValidationResult, field_name: str):
    """Validate positive number."""
    if isinstance(value, (int, float)) and value <= 0:
        result.add_error(f"Value must be positive in {field_name}: {value}")


def validate_css_size(value: Any, result: ValidationResult, field_name: str):
    """Validate CSS size units."""
    if isinstance(value, str):
        pattern = r"^\d+(\.\d+)?(px|em|rem|%|pt|pc|in|cm|mm|vh|vw)$"
        if not re.match(pattern, value):
            result.add_error(f"Invalid CSS size format in {field_name}: {value}")


# Predefined schemas
def create_color_schema() -> Schema:
    """Create schema for color definitions."""
    return Schema(
        "Color",
        [
            SchemaField("value", SchemaType.COLOR, required=True),
            SchemaField("alpha", SchemaType.FLOAT, required=False, min_value=0.0, max_value=1.0),
            SchemaField("name", SchemaType.STRING, required=False, max_length=50),
        ],
    )


def create_style_schema() -> Schema:
    """Create schema for style definitions."""
    return Schema(
        "Style",
        [
            SchemaField("font_family", SchemaType.STRING, required=False, max_length=100),
            SchemaField(
                "font_size", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
            ),
            SchemaField(
                "font_weight",
                SchemaType.ENUM,
                required=False,
                enum_values=[
                    "normal",
                    "bold",
                    "lighter",
                    "bolder",
                    "100",
                    "200",
                    "300",
                    "400",
                    "500",
                    "600",
                    "700",
                    "800",
                    "900",
                ],
            ),
            SchemaField("color", SchemaType.COLOR, required=False),
            SchemaField("background_color", SchemaType.COLOR, required=False),
            SchemaField(
                "border_width", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
            ),
            SchemaField(
                "border_radius", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
            ),
            SchemaField(
                "padding", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
            ),
            SchemaField(
                "margin", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
            ),
        ],
    )


class ThemeSchema(Schema):
    """Schema for theme validation."""

    def __init__(self):
        super().__init__(
            "Theme",
            [
                SchemaField(
                    "name",
                    SchemaType.STRING,
                    required=True,
                    min_length=1,
                    max_length=100,
                    pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
                ),
                SchemaField(
                    "version", SchemaType.STRING, required=False, pattern=r"^\d+\.\d+\.\d+$"
                ),
                SchemaField("description", SchemaType.STRING, required=False, max_length=500),
                SchemaField("colors", SchemaType.DICT, required=True),
                SchemaField("styles", SchemaType.DICT, required=True),
                SchemaField("metadata", SchemaType.DICT, required=False),
            ],
        )


class WidgetSchema(Schema):
    """Schema for widget validation."""

    def __init__(self):
        super().__init__(
            "Widget",
            [
                SchemaField("name", SchemaType.STRING, required=True, min_length=1, max_length=100),
                SchemaField(
                    "type",
                    SchemaType.STRING,
                    required=True,
                    enum_values=[
                        "button",
                        "label",
                        "input",
                        "textarea",
                        "select",
                        "checkbox",
                        "radio",
                    ],
                ),
                SchemaField("theme", SchemaType.STRING, required=False),
                SchemaField("styles", SchemaType.DICT, required=False),
                SchemaField("enabled", SchemaType.BOOLEAN, required=False, default=True),
                SchemaField("visible", SchemaType.BOOLEAN, required=False, default=True),
            ],
        )


class ColorSchema(Schema):
    """Schema for color validation."""

    def __init__(self):
        super().__init__(
            "Color",
            [
                SchemaField("primary", SchemaType.COLOR, required=True),
                SchemaField("secondary", SchemaType.COLOR, required=False),
                SchemaField("background", SchemaType.COLOR, required=False),
                SchemaField("foreground", SchemaType.COLOR, required=False),
                SchemaField("accent", SchemaType.COLOR, required=False),
                SchemaField("error", SchemaType.COLOR, required=False),
                SchemaField("warning", SchemaType.COLOR, required=False),
                SchemaField("success", SchemaType.COLOR, required=False),
                SchemaField("info", SchemaType.COLOR, required=False),
            ],
        )


class StyleSchema(Schema):
    """Schema for style validation."""

    def __init__(self):
        super().__init__(
            "Style",
            [
                SchemaField("font_family", SchemaType.STRING, required=False),
                SchemaField(
                    "font_size", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
                ),
                SchemaField("font_weight", SchemaType.STRING, required=False),
                SchemaField("line_height", SchemaType.CSS_UNIT, required=False),
                SchemaField(
                    "border_radius",
                    SchemaType.CSS_UNIT,
                    required=False,
                    validators=[validate_css_size],
                ),
                SchemaField(
                    "padding", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
                ),
                SchemaField(
                    "margin", SchemaType.CSS_UNIT, required=False, validators=[validate_css_size]
                ),
                SchemaField(
                    "border_width",
                    SchemaType.CSS_UNIT,
                    required=False,
                    validators=[validate_css_size],
                ),
            ],
        )


def validate_schema(data: Dict[str, Any], schema: Schema) -> ValidationResult:
    """Validate data against a schema.

    Args:
        data: Data to validate
        schema: Schema to validate against

    Returns:
        ValidationResult: Result of validation

    """
    return schema.validate(data)


# Schema registry for dynamic schema lookup
_SCHEMA_REGISTRY: Dict[str, Schema] = {
    "theme": ThemeSchema(),
    "widget": WidgetSchema(),
    "color": ColorSchema(),
    "style": StyleSchema(),
}


def get_schema(schema_name: str) -> Optional[Schema]:
    """Get a schema by name from the registry."""
    return _SCHEMA_REGISTRY.get(schema_name)


def register_schema(name: str, schema: Schema):
    """Register a custom schema."""
    _SCHEMA_REGISTRY[name] = schema


def get_available_schemas() -> List[str]:
    """Get list of available schema names."""
    return list(_SCHEMA_REGISTRY.keys())
