"""Test theme CSS application in isolation."""

from playwright.sync_api import Page


def test_simple_css_variable_application(page: Page):
    """Test basic CSS variable application without external libraries."""

    # Create minimal HTML with just the structure
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            pre[class*="language-"] {
                background-color: var(--md-code-bg);
                color: var(--md-code-fg);
                padding: 10px;
            }
        </style>
    </head>
    <body>
        <div id="content">
            <pre class="language-python"><code>print("hello")</code></pre>
        </div>
    </body>
    </html>
    """

    page.set_content(html_content)

    # Set CSS variables
    page.evaluate(
        """() => {
        document.documentElement.style.setProperty('--md-code-bg', 'rgb(255, 0, 0)');
        document.documentElement.style.setProperty('--md-code-fg', 'rgb(255, 255, 255)');
    }"""
    )

    # Get computed background
    bg_color = page.evaluate(
        """() => {
        const pre = document.querySelector('pre[class*="language-"]');
        return window.getComputedStyle(pre).backgroundColor;
    }"""
    )

    assert bg_color == "rgb(255, 0, 0)", f"Expected red, got: {bg_color}"


def test_prism_theme_override_specificity(page: Page):
    """Test CSS specificity when overriding Prism's built-in theme."""

    # Simulate Prism's CSS with high specificity
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Prism's default theme (high specificity) */
            code[class*="language-"],
            pre[class*="language-"] {
                background: #2d2d2d !important;
                color: #ccc;
            }

            /* Our override - need to test different approaches */
        </style>
    </head>
    <body>
        <div id="content">
            <pre class="language-python"><code class="language-python">print("hello")</code></pre>
        </div>
    </body>
    </html>
    """

    page.set_content(html_content)

    # Check baseline - Prism's color should apply
    initial_bg = page.evaluate(
        """() => {
        const pre = document.querySelector('pre[class*="language-"]');
        return window.getComputedStyle(pre).backgroundColor;
    }"""
    )

    print(f"\nInitial (Prism) background: {initial_bg}")
    assert initial_bg == "rgb(45, 45, 45)", "Prism default should be active"

    # Now try different override strategies
    strategies = [
        # Strategy 1: Same specificity with !important
        {
            "name": "Same specificity + !important",
            "css": """
                pre[class*="language-"] {
                    background: var(--md-code-bg) !important;
                }
            """,
        },
        # Strategy 2: Higher specificity
        {
            "name": "Higher specificity with body",
            "css": """
                body pre[class*="language-"] {
                    background: var(--md-code-bg) !important;
                }
            """,
        },
        # Strategy 3: Much higher specificity
        {
            "name": "Much higher specificity",
            "css": """
                html body #content pre[class*="language-"] {
                    background: var(--md-code-bg) !important;
                }
            """,
        },
    ]

    results = {}
    for strategy in strategies:
        # Reset page
        page.set_content(html_content)

        # Inject override CSS
        css = strategy["css"]
        page.evaluate(
            f"""() => {{
            const style = document.createElement('style');
            style.textContent = `{css}`;
            document.head.appendChild(style);

            document.documentElement.style.setProperty('--md-code-bg', 'rgb(0, 255, 0)');
        }}"""
        )

        # Get computed background
        bg_color = page.evaluate(
            """() => {
            const pre = document.querySelector('pre[class*="language-"]');
            return window.getComputedStyle(pre).backgroundColor;
        }"""
        )

        results[strategy["name"]] = bg_color
        print(f"{strategy['name']}: {bg_color}")

    # At least one strategy should work
    success = any(color == "rgb(0, 255, 0)" for color in results.values())
    assert success, f"None of the override strategies worked! Results: {results}"


def test_current_theme_bridge_css(page: Page):
    """Test the exact CSS pattern used in ThemeBridge._build_prism_override_css()."""

    # Read the actual Prism CSS file
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="file:///home/kuja/GitHub/vfwidgets/widgets/markdown_widget/src/vfwidgets_markdown/renderers/markdown_it/css/prism-themes/prism.css">
        <style>
            body {
                background: white;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div id="content">
            <pre class="language-python"><code class="language-python">print("hello")</code></pre>
        </div>
    </body>
    </html>
    """

    page.set_content(html_content)

    # Get baseline color from Prism CSS
    baseline_bg = page.evaluate(
        """() => {
        const pre = document.querySelector('pre[class*="language-"]');
        return window.getComputedStyle(pre).backgroundColor;
    }"""
    )

    print(f"\nBaseline (Prism CSS) background: {baseline_bg}")

    # Now inject the EXACT CSS from ThemeBridge
    theme_bridge_css = """
        body #content pre[class*="language-"],
        body #content pre.language-,
        body pre[class*="language-"],
        pre[class*="language-"] {
            background-color: var(--md-code-bg) !important;
            background: var(--md-code-bg) !important;
        }
    """

    page.evaluate(
        f"""() => {{
        const style = document.createElement('style');
        style.id = 'theme-custom-css';
        style.textContent = `{theme_bridge_css}`;
        document.head.appendChild(style);

        document.documentElement.style.setProperty('--md-code-bg', 'rgb(255, 0, 0)');
    }}"""
    )

    # Check if override worked
    override_bg = page.evaluate(
        """() => {
        const pre = document.querySelector('pre[class*="language-"]');
        return window.getComputedStyle(pre).backgroundColor;
    }"""
    )

    print(f"After ThemeBridge override: {override_bg}")

    # Take screenshot
    page.screenshot(path="/tmp/theme_bridge_test.png")
    print("Screenshot saved to: /tmp/theme_bridge_test.png")

    assert (
        override_bg == "rgb(255, 0, 0)"
    ), f"ThemeBridge CSS failed to override Prism! Expected red, got: {override_bg}"
