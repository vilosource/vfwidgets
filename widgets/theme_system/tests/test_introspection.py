"""Tests for widget introspection API.

Tests cover:
- PluginAvailability enum
- WidgetMetadata dataclass and validation
- Helper functions (extract_theme_tokens, validate_metadata)
"""

from vfwidgets_theme import (
    PluginAvailability,
    WidgetMetadata,
    extract_theme_tokens,
    validate_metadata,
)
from vfwidgets_theme.widgets import ThemedWidget


class TestPluginAvailability:
    """Test PluginAvailability enum."""

    def test_enum_values(self):
        """Test all enum values exist."""
        assert PluginAvailability.AVAILABLE
        assert PluginAvailability.MISSING_DEPENDENCIES
        assert PluginAvailability.IMPORT_ERROR
        assert PluginAvailability.INVALID_METADATA
        assert PluginAvailability.DISABLED

    def test_is_available_property(self):
        """Test is_available property."""
        assert PluginAvailability.AVAILABLE.is_available is True
        assert PluginAvailability.MISSING_DEPENDENCIES.is_available is False
        assert PluginAvailability.IMPORT_ERROR.is_available is False
        assert PluginAvailability.INVALID_METADATA.is_available is False
        assert PluginAvailability.DISABLED.is_available is False


class TestWidgetMetadata:
    """Test WidgetMetadata dataclass."""

    def test_minimal_metadata_creation(self):
        """Test creating minimal valid metadata."""
        metadata = WidgetMetadata(
            name="Test Widget",
            widget_class_name="TestWidget",
            package_name="test_package",
            version="1.0.0",
            theme_tokens={"background": "editor.background"},
        )

        assert metadata.name == "Test Widget"
        assert metadata.widget_class_name == "TestWidget"
        assert metadata.package_name == "test_package"
        assert metadata.version == "1.0.0"
        assert metadata.theme_tokens == {"background": "editor.background"}

    def test_full_metadata_creation(self):
        """Test creating metadata with all fields."""

        def factory(parent):
            return ThemedWidget(parent)

        metadata = WidgetMetadata(
            name="Full Widget",
            widget_class_name="FullWidget",
            package_name="full_package",
            version="2.0.0",
            theme_tokens={
                "background": "editor.background",
                "foreground": "editor.foreground",
            },
            required_tokens=["editor.background", "editor.foreground"],
            optional_tokens=["editor.border"],
            preview_description="A full featured widget",
            preview_factory=factory,
            preview_config={"read_only": True},
            dependencies=["PySide6>=6.5.0"],
            availability=PluginAvailability.AVAILABLE,
            error_message=None,
        )

        assert metadata.name == "Full Widget"
        assert metadata.token_count == 2
        assert len(metadata.required_tokens) == 2
        assert metadata.preview_factory is factory
        assert metadata.is_available is True

    def test_is_available_property(self):
        """Test is_available property based on status."""
        available = WidgetMetadata(
            name="Available",
            widget_class_name="Available",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
            availability=PluginAvailability.AVAILABLE,
        )
        assert available.is_available is True

        unavailable = WidgetMetadata(
            name="Unavailable",
            widget_class_name="Unavailable",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
            availability=PluginAvailability.IMPORT_ERROR,
            error_message="Failed to import",
        )
        assert unavailable.is_available is False

    def test_unique_token_paths(self):
        """Test unique_token_paths property."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={
                "bg": "editor.background",
                "fg": "editor.foreground",
                "bg2": "editor.background",  # Duplicate
            },
        )

        paths = metadata.unique_token_paths
        assert len(paths) == 2  # Duplicates removed
        assert "editor.background" in paths
        assert "editor.foreground" in paths

    def test_token_categories(self):
        """Test token_categories property."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={
                "bg": "editor.background",
                "fg": "editor.foreground",
                "black": "terminal.colors.ansiBlack",
                "red": "terminal.colors.ansiRed",
            },
        )

        categories = metadata.token_categories
        assert len(categories) == 2
        assert "editor" in categories
        assert "terminal" in categories

    def test_token_count(self):
        """Test token_count property."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={
                "bg": "editor.background",
                "fg": "editor.foreground",
                "border": "editor.border",
            },
        )

        assert metadata.token_count == 3

    def test_validate_success(self):
        """Test successful validation."""
        metadata = WidgetMetadata(
            name="Valid Widget",
            widget_class_name="ValidWidget",
            package_name="valid_pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
        )

        is_valid, error = metadata.validate()
        assert is_valid is True
        assert error is None

    def test_validate_missing_name(self):
        """Test validation fails with missing name."""
        metadata = WidgetMetadata(
            name="",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
        )

        is_valid, error = metadata.validate()
        assert is_valid is False
        assert "name is required" in error

    def test_validate_missing_widget_class_name(self):
        """Test validation fails with missing widget_class_name."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
        )

        is_valid, error = metadata.validate()
        assert is_valid is False
        assert "widget_class_name is required" in error

    def test_validate_empty_theme_tokens(self):
        """Test validation fails with empty theme_tokens."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={},
        )

        is_valid, error = metadata.validate()
        assert is_valid is False
        assert "theme_tokens is required" in error

    def test_validate_invalid_token_path(self):
        """Test validation fails with invalid token path."""
        metadata = WidgetMetadata(
            name="Widget",
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "invalid.nonexistent.token"},
        )

        is_valid, error = metadata.validate()
        assert is_valid is False
        assert "Invalid token path" in error
        assert "invalid.nonexistent.token" in error


class TestExtractThemeTokens:
    """Test extract_theme_tokens helper function."""

    def test_extract_from_themed_widget(self):
        """Test extracting tokens from ThemedWidget subclass."""

        class TestWidget(ThemedWidget):
            theme_config = {
                "background": "editor.background",
                "foreground": "editor.foreground",
            }

        tokens = extract_theme_tokens(TestWidget)
        assert tokens == {
            "background": "editor.background",
            "foreground": "editor.foreground",
        }

    def test_extract_from_widget_without_theme_config(self):
        """Test extracting from widget without theme_config returns empty dict."""

        class PlainWidget:
            pass

        tokens = extract_theme_tokens(PlainWidget)
        assert tokens == {}

    def test_extract_from_widget_with_non_dict_theme_config(self):
        """Test extracting from widget with invalid theme_config returns empty dict."""

        class BadWidget:
            theme_config = "not a dict"

        tokens = extract_theme_tokens(BadWidget)
        assert tokens == {}


class TestValidateMetadataFunction:
    """Test validate_metadata helper function."""

    def test_validates_successfully(self):
        """Test validation succeeds for valid metadata."""
        metadata = WidgetMetadata(
            name="Valid Widget",
            widget_class_name="ValidWidget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
        )

        is_valid, error = validate_metadata(metadata)
        assert is_valid is True
        assert error is None

    def test_detects_validation_errors(self):
        """Test validation detects errors."""
        metadata = WidgetMetadata(
            name="",  # Invalid: empty name
            widget_class_name="Widget",
            package_name="pkg",
            version="1.0.0",
            theme_tokens={"bg": "editor.background"},
        )

        is_valid, error = validate_metadata(metadata)
        assert is_valid is False
        assert error is not None
        assert "name is required" in error
