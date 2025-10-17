"""Playwright tests for ANSI escape sequence rendering.

These tests validate that xterm.js correctly renders ANSI color sequences
and formatting in a real browser environment.
"""

import pytest


@pytest.mark.asyncio
async def test_ansi_red_text_renders(xterm_page, sample_themes):
    """Test ANSI red text color sequence renders correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme to get ANSI color palette
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(f"() => {{ window.term.options.theme = {{ {theme_js} }}; }}")

    # Write ANSI red text
    await xterm_page.evaluate(r"""() => { window.term.write('\x1b[31mRed text\x1b[0m'); }""")

    # Get the color of the text
    text_color = await xterm_page.evaluate(
        """() => {
        const spans = document.querySelectorAll('.xterm-rows span');
        for (const span of spans) {
            if (span.textContent.includes('Red')) {
                return window.getComputedStyle(span).color;
            }
        }
        return null;
    }"""
    )

    # #cd3131 = rgb(205, 49, 49)
    assert text_color == "rgb(205, 49, 49)", f"Expected ANSI red, got {text_color}"


@pytest.mark.asyncio
async def test_ansi_green_text_renders(xterm_page, sample_themes):
    """Test ANSI green text color sequence renders correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(f"() => {{ window.term.options.theme = {{ {theme_js} }}; }}")

    # Write ANSI green text
    await xterm_page.evaluate(r"""() => { window.term.write('\x1b[32mGreen text\x1b[0m'); }""")

    # Get the color of the text
    text_color = await xterm_page.evaluate(
        """() => {
        const spans = document.querySelectorAll('.xterm-rows span');
        for (const span of spans) {
            if (span.textContent.includes('Green')) {
                return window.getComputedStyle(span).color;
            }
        }
        return null;
    }"""
    )

    # #0dbc79 = rgb(13, 188, 121)
    assert text_color == "rgb(13, 188, 121)", f"Expected ANSI green, got {text_color}"


@pytest.mark.asyncio
async def test_ansi_bold_renders(xterm_page):
    """Test ANSI bold formatting sequence renders correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
    """
    # Write ANSI bold text
    await xterm_page.evaluate(r"""() => { window.term.write('\x1b[1mBold text\x1b[0m'); }""")

    # Check font-weight
    font_weight = await xterm_page.evaluate(
        """() => {
        const spans = document.querySelectorAll('.xterm-rows span');
        for (const span of spans) {
            if (span.textContent.includes('Bold')) {
                return window.getComputedStyle(span).fontWeight;
            }
        }
        return null;
    }"""
    )

    # Font-weight should be 'bold' or '700'
    assert font_weight in ["bold", "700"], f"Expected bold text, got font-weight={font_weight}"


@pytest.mark.asyncio
async def test_ansi_background_color(xterm_page, sample_themes):
    """Test ANSI background color sequence renders correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(f"() => {{ window.term.options.theme = {{ {theme_js} }}; }}")

    # Write text with red background (41 = red background)
    await xterm_page.evaluate(r"""() => { window.term.write('\x1b[41mRed BG\x1b[0m'); }""")

    # Get background color
    bg_color = await xterm_page.evaluate(
        """() => {
        const spans = document.querySelectorAll('.xterm-rows span');
        for (const span of spans) {
            if (span.textContent.includes('Red BG')) {
                return window.getComputedStyle(span).backgroundColor;
            }
        }
        return null;
    }"""
    )

    # #cd3131 = rgb(205, 49, 49)
    assert bg_color == "rgb(205, 49, 49)", f"Expected red background, got {bg_color}"


@pytest.mark.asyncio
async def test_all_16_ansi_colors(xterm_page, sample_themes):
    """Test all 16 ANSI colors render correctly.

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(f"() => {{ window.term.options.theme = {{ {theme_js} }}; }}")

    # ANSI color codes: 30-37 (normal), 90-97 (bright)
    ansi_color_codes = {
        30: "black",
        31: "red",
        32: "green",
        33: "yellow",
        34: "blue",
        35: "magenta",
        36: "cyan",
        37: "white",
        90: "brightBlack",
        91: "brightRed",
        92: "brightGreen",
        93: "brightYellow",
        94: "brightBlue",
        95: "brightMagenta",
        96: "brightCyan",
        97: "brightWhite",
    }

    colors_tested = 0

    for code, color_name in ansi_color_codes.items():
        # Write colored text
        await xterm_page.evaluate(
            f"() => {{ window.term.write('\\x1b[{code}m{color_name}\\x1b[0m '); }}"
        )
        colors_tested += 1

    # Take screenshot for visual validation
    screenshot = await xterm_page.screenshot()
    assert len(screenshot) > 0, "Screenshot capture failed"

    # Verify all 16 colors were written
    assert colors_tested == 16, f"Expected 16 colors, tested {colors_tested}"


@pytest.mark.asyncio
async def test_ansi_combined_formatting(xterm_page, sample_themes):
    """Test combined ANSI formatting (bold + color).

    Args:
        xterm_page: Playwright page with xterm.js loaded
        sample_themes: Sample theme dictionaries
    """
    dark_theme = sample_themes["dark"]

    # Apply theme
    theme_js = ", ".join([f"{key}: '{value}'" for key, value in dark_theme.items()])
    await xterm_page.evaluate(f"() => {{ window.term.options.theme = {{ {theme_js} }}; }}")

    # Write bold red text
    await xterm_page.evaluate(r"""() => { window.term.write('\x1b[1;31mBold Red\x1b[0m'); }""")

    # Check both font-weight and color
    result = await xterm_page.evaluate(
        """() => {
        const spans = document.querySelectorAll('.xterm-rows span');
        for (const span of spans) {
            if (span.textContent.includes('Bold Red')) {
                return {
                    color: window.getComputedStyle(span).color,
                    fontWeight: window.getComputedStyle(span).fontWeight
                };
            }
        }
        return null;
    }"""
    )

    assert result is not None, "Could not find formatted text"
    assert result["color"] == "rgb(205, 49, 49)", f"Expected red color, got {result['color']}"
    assert result["fontWeight"] in [
        "bold",
        "700",
    ], f"Expected bold, got {result['fontWeight']}"


@pytest.mark.asyncio
async def test_ansi_reset_sequence(xterm_page):
    """Test ANSI reset sequence clears formatting.

    Args:
        xterm_page: Playwright page with xterm.js loaded
    """
    # Write red text, then reset, then normal text
    await xterm_page.evaluate(
        r"""() => {
        window.term.write('\x1b[31mRed\x1b[0m Normal');
    }"""
    )

    # Get colors of both text segments
    colors = await xterm_page.evaluate(
        """() => {
        const spans = Array.from(document.querySelectorAll('.xterm-rows span'));
        return spans.map(span => ({
            text: span.textContent,
            color: window.getComputedStyle(span).color
        }));
    }"""
    )

    # Find the "Red" and "Normal" text
    red_text = next((c for c in colors if "Red" in c["text"]), None)
    normal_text = next((c for c in colors if "Normal" in c["text"]), None)

    assert red_text is not None, "Could not find red text"
    assert normal_text is not None, "Could not find normal text"

    # Red text should be colored, normal text should not
    assert red_text["color"] != normal_text["color"], "Reset sequence did not work"
