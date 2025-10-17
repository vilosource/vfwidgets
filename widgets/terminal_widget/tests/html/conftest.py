"""Pytest configuration for Playwright HTML/browser tests."""

import pytest


@pytest.fixture(scope="session")
def xterm_resources():
    """Provide xterm.js resource URLs for tests.

    Returns:
        dict: URLs for xterm.js library and CSS
    """
    # Using CDN for xterm.js in tests
    return {
        "js_url": "https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js",
        "css_url": "https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css",
    }


@pytest.fixture
def xterm_html_template(xterm_resources):
    """Generate base HTML template for xterm.js tests.

    Args:
        xterm_resources: Fixture providing xterm.js URLs

    Returns:
        str: HTML template with xterm.js loaded
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Xterm.js Test</title>
    <link rel="stylesheet" href="{xterm_resources['css_url']}" />
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
        }}
        #terminal {{
            width: 800px;
            height: 600px;
        }}
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script src="{xterm_resources['js_url']}"></script>
    <script>
        // Create terminal instance
        const term = new Terminal({{
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'monospace',
        }});

        // Mount to DOM
        term.open(document.getElementById('terminal'));

        // Make terminal globally accessible for tests
        window.term = term;

        // Signal that terminal is ready
        window.terminalReady = true;
    </script>
</body>
</html>"""


@pytest.fixture
async def xterm_page(page, xterm_html_template):
    """Create a page with xterm.js loaded and ready.

    Args:
        page: Playwright page fixture
        xterm_html_template: HTML template fixture

    Returns:
        Page: Playwright page with xterm.js ready
    """
    # Set content
    await page.set_content(xterm_html_template)

    # Wait for terminal to be ready
    await page.wait_for_function("window.terminalReady === true")

    return page


@pytest.fixture
def sample_themes():
    """Provide sample theme dictionaries for testing.

    Returns:
        dict: Sample light and dark themes
    """
    return {
        "dark": {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "cursor": "#ffffff",
            "black": "#000000",
            "red": "#cd3131",
            "green": "#0dbc79",
            "yellow": "#e5e510",
            "blue": "#2472c8",
            "magenta": "#bc3fbc",
            "cyan": "#11a8cd",
            "white": "#e5e5e5",
            "brightBlack": "#666666",
            "brightRed": "#f14c4c",
            "brightGreen": "#23d18b",
            "brightYellow": "#f5f543",
            "brightBlue": "#3b8eea",
            "brightMagenta": "#d670d6",
            "brightCyan": "#29b8db",
            "brightWhite": "#ffffff",
        },
        "light": {
            "background": "#ffffff",
            "foreground": "#000000",
            "cursor": "#000000",
            "black": "#000000",
            "red": "#cd3131",
            "green": "#00bc00",
            "yellow": "#949800",
            "blue": "#0451a5",
            "magenta": "#bc05bc",
            "cyan": "#0598bc",
            "white": "#555555",
            "brightBlack": "#666666",
            "brightRed": "#cd3131",
            "brightGreen": "#14ce14",
            "brightYellow": "#b5ba00",
            "brightBlue": "#0451a5",
            "brightMagenta": "#bc05bc",
            "brightCyan": "#0598bc",
            "brightWhite": "#a5a5a5",
        },
    }
