"""Playwright tests for terminal theme application.

These tests validate that xterm.js correctly applies theme colors in a real browser environment.
"""

import pytest


@pytest.mark.asyncio
async def test_xterm_background_color(xterm_page, sample_themes):
    """Test xterm.js background color application from theme.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme background color
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{
            background: '{dark_theme['background']}'
        }};
    }}"""
    )

    # Get computed background color from terminal element
    bg_color = await xterm_page.evaluate(
        """() => {
        const terminal = document.querySelector('.xterm-screen');
        return window.getComputedStyle(terminal).backgroundColor;
    }"""
    )

    # #1e1e1e = rgb(30, 30, 30)
    assert bg_color == "rgb(30, 30, 30)", f"Expected dark background, got {bg_color}"


@pytest.mark.asyncio
async def test_xterm_foreground_color(xterm_page, sample_themes):
    """Test xterm.js foreground color application from theme.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme foreground color
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{
            foreground: '{dark_theme['foreground']}'
        }};
    }}"""
    )

    # Write text and check its color
    await xterm_page.evaluate(
        """() => {
        window.term.write('Test text');
    }"""
    )

    # Get computed foreground color
    fg_color = await xterm_page.evaluate(
        """() => {
        const textElement = document.querySelector('.xterm-rows span');
        return window.getComputedStyle(textElement).color;
    }"""
    )

    # #d4d4d4 = rgb(212, 212, 212)
    assert fg_color == "rgb(212, 212, 212)", f"Expected light foreground, got {fg_color}"


@pytest.mark.asyncio
async def test_xterm_cursor_color(xterm_page, sample_themes):
    """Test xterm.js cursor color application from theme.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    light_theme = sample_themes["light"]

    # Apply theme with cursor color
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{
            cursor: '{light_theme['cursor']}'
        }};
    }}"""
    )

    # Get computed cursor color
    cursor_color = await xterm_page.evaluate(
        """() => {
        const cursor = document.querySelector('.xterm-cursor');
        return window.getComputedStyle(cursor).backgroundColor;
    }"""
    )

    # #000000 = rgb(0, 0, 0)
    assert cursor_color == "rgb(0, 0, 0)", f"Expected black cursor, got {cursor_color}"


@pytest.mark.asyncio
async def test_theme_switching(xterm_page, sample_themes):
    """Test switching between light and dark themes.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]
    light_theme = sample_themes["light"]

    # Apply dark theme
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{
            background: '{dark_theme['background']}',
            foreground: '{dark_theme['foreground']}'
        }};
    }}"""
    )

    # Verify dark theme applied
    bg_dark = await xterm_page.evaluate(
        """() => {
        const terminal = document.querySelector('.xterm-screen');
        return window.getComputedStyle(terminal).backgroundColor;
    }"""
    )
    assert bg_dark == "rgb(30, 30, 30)", "Dark theme not applied"

    # Switch to light theme
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{
            background: '{light_theme['background']}',
            foreground: '{light_theme['foreground']}'
        }};
    }}"""
    )

    # Verify light theme applied
    bg_light = await xterm_page.evaluate(
        """() => {
        const terminal = document.querySelector('.xterm-screen');
        return window.getComputedStyle(terminal).backgroundColor;
    }"""
    )
    assert bg_light == "rgb(255, 255, 255)", "Light theme not applied"


@pytest.mark.asyncio
async def test_all_theme_colors_apply(xterm_page, sample_themes):
    """Test that all theme color properties apply correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply complete theme
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(
        f"""() => {{
        window.term.options.theme = {{ {theme_js} }};
    }}"""
    )

    # Verify theme is set
    applied_theme = await xterm_page.evaluate(
        """() => {
        return window.term.options.theme;
    }"""
    )

    # Check that all color properties are present
    for key, expected_color in dark_theme.items():
        assert key in applied_theme, f"Theme property '{key}' missing"
        assert applied_theme[key] == expected_color, f"Theme property '{key}' has wrong value"


@pytest.mark.asyncio
async def test_partial_theme_application(xterm_page):
    """Test applying partial theme (only some colors).

    Args:
        xterm_page: Playwright page with xterm.js loaded
    """
    # Apply only background and foreground
    await xterm_page.evaluate(
        """() => {
        window.term.options.theme = {
            background: '#ff0000',  // Red background for visibility
            foreground: '#00ff00'   // Green foreground
        };
    }"""
    )

    # Verify partial theme applied
    bg_color = await xterm_page.evaluate(
        """() => {
        const terminal = document.querySelector('.xterm-screen');
        return window.getComputedStyle(terminal).backgroundColor;
    }"""
    )

    assert bg_color == "rgb(255, 0, 0)", f"Red background not applied, got {bg_color}"
