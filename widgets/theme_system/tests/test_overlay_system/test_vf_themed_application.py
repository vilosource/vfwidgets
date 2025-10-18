"""Tests for VFThemedApplication - Declarative theme configuration."""

import pytest
from PySide6.QtCore import QSettings

from vfwidgets_theme.widgets.vf_themed_application import VFThemedApplication

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def clean_qsettings(tmp_path, monkeypatch):
    """Mock QSettings to use temporary storage."""
    settings_file = tmp_path / "test_settings.ini"

    original_init = QSettings.__init__

    def mock_init(self, *args, **kwargs):
        # Always use temp file
        original_init(self, str(settings_file), QSettings.Format.IniFormat)

    monkeypatch.setattr(QSettings, "__init__", mock_init)

    yield str(settings_file)

    if settings_file.exists():
        settings_file.unlink()


@pytest.fixture
def sample_theme_config():
    """Sample theme configuration for testing."""
    return {
        "base_theme": "dark",
        "app_overrides": {
            "editor.background": "#1e1e2e",
            "tab.activeBackground": "#89b4fa",
            "button.background": "#313244",
        },
        "allow_user_customization": True,
        "customizable_tokens": [
            "editor.background",
            "editor.foreground",
        ],
        "persist_base_theme": True,
        "persist_user_overrides": True,
        "settings_key_prefix": "theme/",
    }


# ============================================================================
# Test Basic Functionality
# ============================================================================


class TestVFThemedApplicationImport:
    """Test VFThemedApplication can be imported."""

    def test_import_vf_themed_application(self):
        """Test that VFThemedApplication can be imported."""
        from vfwidgets_theme.widgets.vf_themed_application import VFThemedApplication

        assert VFThemedApplication is not None

    def test_import_from_widgets_module(self):
        """Test that VFThemedApplication is available from widgets module."""
        from vfwidgets_theme.widgets import VFThemedApplication

        assert VFThemedApplication is not None


class TestVFThemedApplicationBasics:
    """Test basic VFThemedApplication functionality."""

    def test_has_default_theme_config(self):
        """Test that VFThemedApplication has default theme_config."""
        assert hasattr(VFThemedApplication, "theme_config")
        assert isinstance(VFThemedApplication.theme_config, dict)

    def test_default_theme_config_structure(self):
        """Test default theme_config has expected keys."""
        config = VFThemedApplication.theme_config
        assert "base_theme" in config
        assert "app_overrides" in config
        assert "allow_user_customization" in config
        assert "customizable_tokens" in config
        assert "persist_base_theme" in config
        assert "persist_user_overrides" in config
        assert "settings_key_prefix" in config

    def test_default_theme_config_values(self):
        """Test default theme_config values are sensible."""
        config = VFThemedApplication.theme_config
        assert config["base_theme"] == "dark"
        assert config["app_overrides"] == {}
        assert config["allow_user_customization"] is True
        assert config["customizable_tokens"] == []
        assert config["persist_base_theme"] is True
        assert config["persist_user_overrides"] is True
        assert config["settings_key_prefix"] == "theme/"


# ============================================================================
# Test Declarative Configuration
# ============================================================================


class TestVFThemedApplicationDeclarativeConfig:
    """Test declarative theme_config pattern."""

    def test_subclass_can_override_theme_config(self, qapp):
        """Test that subclasses can override theme_config."""

        class CustomApp(VFThemedApplication):
            theme_config = {
                "base_theme": "light",
                "app_overrides": {
                    "editor.background": "#ffffff",
                },
                "allow_user_customization": False,
            }

        # Verify class attribute is set (without instantiating)
        assert CustomApp.theme_config["base_theme"] == "light"
        assert CustomApp.theme_config["allow_user_customization"] is False

    def test_app_overrides_structure(self, qapp):
        """Test that theme_config supports app_overrides."""

        class BrandedApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "app_overrides": {
                    "editor.background": "#1e1e2e",
                    "tab.activeBackground": "#89b4fa",
                },
            }

        # Verify structure (without instantiation)
        assert "app_overrides" in BrandedApp.theme_config
        assert len(BrandedApp.theme_config["app_overrides"]) == 2
        assert BrandedApp.theme_config["app_overrides"]["editor.background"] == "#1e1e2e"

    def test_base_theme_config_structure(self, qapp):
        """Test that base_theme configuration is supported."""

        class LightApp(VFThemedApplication):
            theme_config = {
                "base_theme": "light",
                "app_overrides": {},
            }

        # Verify structure (without instantiation)
        assert LightApp.theme_config["base_theme"] == "light"


# ============================================================================
# Test Persistence (QSettings)
# ============================================================================


class TestVFThemedApplicationPersistence:
    """Test QSettings persistence functionality."""

    def test_theme_config_has_persistence_options(self, qapp):
        """Test that theme_config supports persistence options."""
        config = VFThemedApplication.theme_config

        assert "persist_base_theme" in config
        assert "persist_user_overrides" in config
        assert "settings_key_prefix" in config
        assert config["settings_key_prefix"] == "theme/"

    def test_persistence_can_be_disabled(self, qapp):
        """Test that persistence can be disabled in theme_config."""

        class NoPersistApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "persist_base_theme": False,
                "persist_user_overrides": False,
            }

        # Verify config (without instantiation)
        assert NoPersistApp.theme_config["persist_base_theme"] is False
        assert NoPersistApp.theme_config["persist_user_overrides"] is False

    def test_custom_settings_prefix(self, qapp):
        """Test that QSettings prefix can be customized."""

        class CustomPrefixApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "settings_key_prefix": "myapp/themes/",
            }

        # Verify config (without instantiation)
        assert CustomPrefixApp.theme_config["settings_key_prefix"] == "myapp/themes/"


# ============================================================================
# Test Customization Methods
# ============================================================================


class TestVFThemedApplicationCustomization:
    """Test color customization methods."""

    def test_customization_config_structure(self, qapp):
        """Test that theme_config supports customization options."""
        config = VFThemedApplication.theme_config

        assert "allow_user_customization" in config
        assert "customizable_tokens" in config

    def test_customization_can_be_disabled(self, qapp):
        """Test that customization can be disabled."""

        class NoCustomizeApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "allow_user_customization": False,
            }

        # Verify config (without instantiation)
        assert NoCustomizeApp.theme_config["allow_user_customization"] is False

    def test_customizable_tokens_can_be_restricted(self, qapp):
        """Test that customizable tokens can be restricted."""

        class RestrictedApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "allow_user_customization": True,
                "customizable_tokens": [
                    "editor.background",
                    "editor.foreground",
                ],
            }

        # Verify config (without instantiation)
        tokens = RestrictedApp.theme_config["customizable_tokens"]
        assert len(tokens) == 2
        assert "editor.background" in tokens
        assert "editor.foreground" in tokens

    def test_empty_customizable_tokens_means_all_allowed(self, qapp):
        """Test that empty customizable_tokens list means all tokens are allowed."""

        class AllAllowedApp(VFThemedApplication):
            theme_config = {
                "base_theme": "dark",
                "allow_user_customization": True,
                "customizable_tokens": [],  # Empty = all allowed
            }

        # Verify config (without instantiation)
        assert AllAllowedApp.theme_config["customizable_tokens"] == []


# ============================================================================
# Test Integration with ThemeManager
# ============================================================================


class TestVFThemedApplicationIntegration:
    """Test integration with ThemeManager overlay system."""

    def test_extends_themed_application(self, qapp):
        """Test that VFThemedApplication extends ThemedApplication."""
        from vfwidgets_theme.widgets.application import ThemedApplication

        assert issubclass(VFThemedApplication, ThemedApplication)

    def test_inherits_themed_application_methods(self, qapp):
        """Test that VFThemedApplication inherits ThemedApplication methods."""
        # Verify key methods exist (from ThemedApplication)
        assert hasattr(VFThemedApplication, "set_theme")
        assert hasattr(VFThemedApplication, "get_available_themes")

    def test_adds_overlay_specific_methods(self, qapp):
        """Test that VFThemedApplication adds overlay-specific methods."""
        # Verify new methods exist
        assert hasattr(VFThemedApplication, "customize_color")
        assert hasattr(VFThemedApplication, "reset_color")
        assert hasattr(VFThemedApplication, "get_customizable_tokens")
        assert hasattr(VFThemedApplication, "is_token_customizable")
        assert hasattr(VFThemedApplication, "load_user_preferences")
        assert hasattr(VFThemedApplication, "save_user_preferences")
        assert hasattr(VFThemedApplication, "clear_user_preferences")


# ============================================================================
# Test Documentation and API
# ============================================================================


class TestVFThemedApplicationDocumentation:
    """Test that VFThemedApplication is well-documented."""

    def test_has_docstring(self, qapp):
        """Test that VFThemedApplication has a docstring."""
        assert VFThemedApplication.__doc__ is not None
        assert len(VFThemedApplication.__doc__) > 50

    def test_methods_have_docstrings(self, qapp):
        """Test that key methods have docstrings."""
        assert VFThemedApplication.customize_color.__doc__ is not None
        assert VFThemedApplication.reset_color.__doc__ is not None
        assert VFThemedApplication.load_user_preferences.__doc__ is not None
        assert VFThemedApplication.save_user_preferences.__doc__ is not None

    def test_has_repr(self, qapp):
        """Test that VFThemedApplication has a repr method."""
        assert hasattr(VFThemedApplication, "__repr__")
