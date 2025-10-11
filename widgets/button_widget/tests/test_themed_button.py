"""Test suite for themed ButtonWidget integration."""

import pytest
from vfwidgets_button import ButtonWidget
from vfwidgets_theme import ThemedApplication, WidgetRole


@pytest.fixture(scope="module")
def app():
    """Create ThemedApplication for tests."""
    app = ThemedApplication([])
    app.set_theme("dark")
    yield app
    app.quit()


def test_button_widget_creation(app):
    """Test basic button creation."""
    btn = ButtonWidget("Test Button")
    assert btn.text() == "Test Button"
    assert btn.theme is not None


def test_button_widget_with_role(app):
    """Test button with semantic role."""
    btn = ButtonWidget("Primary", role=WidgetRole.PRIMARY)
    assert btn.get_role() == WidgetRole.PRIMARY


def test_button_widget_theme_access(app):
    """Test theme token access."""
    btn = ButtonWidget("Test")
    # Should have access to button theme tokens
    assert btn.theme.bg is not None
    assert btn.theme.fg is not None
    assert btn.theme.hover_bg is not None


def test_button_widget_role_change(app):
    """Test changing button role."""
    btn = ButtonWidget("Test")
    assert btn.get_role() is None

    btn.set_role(WidgetRole.SUCCESS)
    assert btn.get_role() == WidgetRole.SUCCESS


def test_button_widget_deprecated_style(app):
    """Test backward compatibility with ButtonStyle."""
    from vfwidgets_button import ButtonStyle

    btn = ButtonWidget("Test", style=ButtonStyle.PRIMARY)
    assert btn.get_role() == WidgetRole.PRIMARY
    assert btn.get_style() == ButtonStyle.PRIMARY


def test_button_widget_customization(app):
    """Test button customization options."""
    btn = ButtonWidget("Custom", rounded=False, shadow=False, animated=False)
    assert btn._rounded is False
    assert btn._shadow_enabled is False
    assert btn._animated is False


def test_button_widget_signals(app):
    """Test button custom signals."""
    btn = ButtonWidget("Test")

    # Button should have custom signals
    assert hasattr(btn, "double_clicked")
    assert hasattr(btn, "long_pressed")
    assert hasattr(btn, "style_changed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
