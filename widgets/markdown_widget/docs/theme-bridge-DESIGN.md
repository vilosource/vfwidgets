# Theme Bridge - Design Specification

## Overview

The `ThemeBridge` is a dedicated component that manages theme communication between Python (Qt/ThemedWidget) and JavaScript (HTML/CSS rendering). It provides a clean, testable abstraction for applying theme tokens to webview content.

**Inspired by**: Terminal widget's theme handling, VS Code's CSS variable injection pattern

---

## Design Goals

1. **Separation of Concerns**: Theme logic separate from widget and renderer
2. **Testability**: Test theme application without QWebEngineView
3. **Debuggability**: Clear logging of token resolution and CSS injection
4. **Reusability**: Pattern for all webview-based widgets
5. **Consistency**: Uniform theme application across all widgets

---

## Current Problems (Identified in Research)

### Problem 1: Theme Logic Scattered Across Widget
**Current**: `markdown_viewer.py` lines 571-710
- Theme token resolution mixed with widget lifecycle
- CSS variable building embedded in `on_theme_changed()`
- Prism.js override CSS hardcoded in widget
- No clear boundaries

### Problem 2: No Diagnostic Visibility
**Current**: CSS variables set but no validation
- Can't tell if CSS is actually applied
- Can't tell if CSS specificity is correct
- Can't tell if JavaScript executed successfully

### Problem 3: Difficult to Test
**Current**: Must run full QWebEngineView to test theming
- Can't test CSS variable generation in isolation
- Can't test Prism override logic without browser
- Can't mock theme application

### Problem 4: Not Reusable
**Current**: Each webview widget reimplements theme injection
- Terminal widget: ~100 lines of theme code
- Markdown widget: ~140 lines of theme code
- Future widgets will duplicate this code

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   MarkdownViewer                        │
│                   (ThemedWidget)                        │
│                                                         │
│  on_theme_changed(theme) ─────────┐                    │
│                                    │                    │
└────────────────────────────────────┼────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────┐
│                    ThemeBridge                          │
│                                                         │
│  Token Resolution ───► CSS Variable Building           │
│                   ───► CSS Injection                   │
│                   ───► Validation & Diagnostics        │
│                                                         │
└────────────────────────────────────┬────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────┐
│                QWebEnginePage                           │
│                                                         │
│  runJavaScript() ───► document.documentElement.style   │
│                   ───► CSS variable injection          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Core Classes

### 1. ThemeBridge

```python
from typing import Optional, Callable
from dataclasses import dataclass
import logging
from PySide6.QtWebEngineCore import QWebEnginePage

logger = logging.getLogger(__name__)


@dataclass
class ThemeTokenMapping:
    """Maps CSS variable names to theme token paths.

    Example:
        ThemeTokenMapping(
            css_var="md-fg",
            token_path="markdown.colors.foreground",
            fallback_paths=["editor.foreground", "colors.foreground"]
        )
    """

    css_var: str  # CSS variable name (without --)
    token_path: str  # Primary theme token path
    fallback_paths: list[str] = None  # Fallback token paths
    default_value: Optional[str] = None  # Hard default if all tokens missing

    def __post_init__(self):
        if self.fallback_paths is None:
            self.fallback_paths = []


@dataclass
class ThemeApplicationResult:
    """Result of applying theme to page."""

    success: bool
    css_variables_set: dict[str, str]  # {"--md-fg": "#c9d1d9", ...}
    missing_tokens: list[str]  # Tokens that had no value
    used_fallbacks: dict[str, str]  # {"md-fg": "editor.foreground", ...}
    errors: list[str]  # Any errors during application


class ThemeBridge:
    """Manages theme communication between Python and JavaScript.

    Responsibilities:
    - Resolve theme tokens with fallback chains
    - Build CSS custom properties (variables)
    - Inject CSS into QWebEnginePage
    - Validate theme application
    - Provide diagnostic logging

    Example:
        bridge = ThemeBridge(
            page=web_page,
            token_mappings=[
                ThemeTokenMapping("md-fg", "markdown.colors.foreground",
                                  fallback_paths=["editor.foreground"]),
                ThemeTokenMapping("md-bg", "markdown.colors.background",
                                  fallback_paths=["editor.background"]),
            ]
        )

        result = bridge.apply_theme(theme)
        if not result.success:
            logger.error(f"Theme application failed: {result.errors}")
    """

    def __init__(
        self,
        page: QWebEnginePage,
        token_mappings: list[ThemeTokenMapping],
        css_injection_callback: Optional[Callable[[dict], str]] = None
    ):
        """Initialize theme bridge.

        Args:
            page: QWebEnginePage where CSS will be injected
            token_mappings: List of CSS variable to theme token mappings
            css_injection_callback: Optional custom CSS builder for special cases
                (e.g., Prism override CSS in markdown widget)
        """
        self._page = page
        self._token_mappings = token_mappings
        self._css_injection_callback = css_injection_callback
        self._last_result: Optional[ThemeApplicationResult] = None

    def apply_theme(self, theme) -> ThemeApplicationResult:
        """Apply theme to page.

        Args:
            theme: Theme object with colors dict

        Returns:
            ThemeApplicationResult with success status and diagnostics
        """
        if not theme:
            return ThemeApplicationResult(
                success=False,
                css_variables_set={},
                missing_tokens=[],
                used_fallbacks={},
                errors=["No theme provided"]
            )

        # Step 1: Resolve theme tokens
        css_vars = {}
        missing_tokens = []
        used_fallbacks = {}

        for mapping in self._token_mappings:
            resolved = self._resolve_token(theme, mapping)

            if resolved.value:
                css_var_name = f"--{mapping.css_var}"
                css_vars[css_var_name] = resolved.value

                if resolved.used_fallback:
                    used_fallbacks[mapping.css_var] = resolved.used_fallback
            else:
                missing_tokens.append(mapping.token_path)

        # Log diagnostics
        logger.debug(f"Theme application: {len(css_vars)} variables resolved")
        if used_fallbacks:
            logger.debug(f"  Used fallbacks: {used_fallbacks}")
        if missing_tokens:
            logger.warning(f"  Missing tokens: {missing_tokens}")

        # Step 2: Build CSS injection code
        css_injection = self._build_css_injection(css_vars)

        # Step 3: Inject CSS into page
        try:
            self._inject_css(css_injection)

            result = ThemeApplicationResult(
                success=True,
                css_variables_set=css_vars,
                missing_tokens=missing_tokens,
                used_fallbacks=used_fallbacks,
                errors=[]
            )

        except Exception as e:
            logger.error(f"Failed to inject CSS: {e}")
            result = ThemeApplicationResult(
                success=False,
                css_variables_set=css_vars,
                missing_tokens=missing_tokens,
                used_fallbacks=used_fallbacks,
                errors=[str(e)]
            )

        self._last_result = result
        return result

    def _resolve_token(self, theme, mapping: ThemeTokenMapping):
        """Resolve theme token with fallback chain.

        Returns:
            ResolvedToken with value and which path was used
        """
        from dataclasses import dataclass

        @dataclass
        class ResolvedToken:
            value: Optional[str]
            used_fallback: Optional[str]

        # Try primary path
        value = self._get_nested_value(theme.colors, mapping.token_path)
        if value:
            return ResolvedToken(value=value, used_fallback=None)

        # Try fallback paths
        for fallback_path in mapping.fallback_paths:
            value = self._get_nested_value(theme.colors, fallback_path)
            if value:
                logger.debug(
                    f"  {mapping.css_var}: using fallback {fallback_path} "
                    f"(primary {mapping.token_path} not found)"
                )
                return ResolvedToken(value=value, used_fallback=fallback_path)

        # Use default value if provided
        if mapping.default_value:
            logger.debug(
                f"  {mapping.css_var}: using default {mapping.default_value} "
                f"(no theme tokens found)"
            )
            return ResolvedToken(value=mapping.default_value, used_fallback="default")

        return ResolvedToken(value=None, used_fallback=None)

    def _get_nested_value(self, colors: dict, path: str) -> Optional[str]:
        """Get value from nested dict using dot notation path.

        Example:
            colors = {"markdown": {"colors": {"foreground": "#fff"}}}
            _get_nested_value(colors, "markdown.colors.foreground") -> "#fff"
        """
        parts = path.split(".")
        current = colors

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current if isinstance(current, str) else None

    def _build_css_injection(self, css_vars: dict[str, str]) -> str:
        """Build JavaScript code to inject CSS variables.

        Args:
            css_vars: CSS variables dict {"--md-fg": "#c9d1d9", ...}

        Returns:
            JavaScript code string
        """
        # Build CSS variable string
        css_vars_string = "; ".join(f"{k}: {v}" for k, v in css_vars.items())

        # Base injection code
        js_code = f"""
        (function() {{
            // Inject CSS variables into document root
            document.documentElement.style.cssText += "{css_vars_string};";

            // Log to console for debugging
            console.log("[ThemeBridge] Applied CSS variables:", {len(css_vars)});

            {self._get_custom_css_injection(css_vars)}

            return true;
        }})();
        """

        return js_code

    def _get_custom_css_injection(self, css_vars: dict) -> str:
        """Get custom CSS injection code (e.g., Prism override).

        Args:
            css_vars: CSS variables that were set

        Returns:
            Additional JavaScript code for custom CSS
        """
        if not self._css_injection_callback:
            return ""

        custom_css = self._css_injection_callback(css_vars)
        if not custom_css:
            return ""

        # Inject custom CSS via <style> tag
        js_code = f"""
        // Inject custom CSS (e.g., Prism overrides)
        let customStyle = document.getElementById('theme-custom-css');
        if (!customStyle) {{
            customStyle = document.createElement('style');
            customStyle.id = 'theme-custom-css';
            document.head.appendChild(customStyle);
        }}
        customStyle.textContent = `{custom_css}`;
        console.log("[ThemeBridge] Injected custom CSS");
        """

        return js_code

    def _inject_css(self, js_code: str) -> None:
        """Execute JavaScript to inject CSS.

        Args:
            js_code: JavaScript code to execute
        """
        self._page.runJavaScript(js_code, lambda result: self._on_injection_complete(result))

    def _on_injection_complete(self, result) -> None:
        """Callback when CSS injection completes.

        Args:
            result: JavaScript return value (True if successful)
        """
        if result is True:
            logger.debug("  CSS injection completed successfully")
        else:
            logger.warning(f"  CSS injection returned: {result}")

    def get_last_result(self) -> Optional[ThemeApplicationResult]:
        """Get result of last theme application."""
        return self._last_result

    def validate_theme(self, theme) -> dict:
        """Validate theme has all required tokens.

        Args:
            theme: Theme object to validate

        Returns:
            Validation report dict with completeness info
        """
        required_tokens = [m.token_path for m in self._token_mappings]
        missing = []
        present = []

        for token_path in required_tokens:
            value = self._get_nested_value(theme.colors, token_path)
            if value:
                present.append(token_path)
            else:
                missing.append(token_path)

        return {
            "complete": len(missing) == 0,
            "completeness_percentage": (len(present) / len(required_tokens)) * 100,
            "missing_tokens": missing,
            "present_tokens": present,
        }
```

---

### 2. Usage in MarkdownViewer

```python
from vfwidgets_markdown.bridges.theme_bridge import ThemeBridge, ThemeTokenMapping


class MarkdownViewer(ThemedWidget, QWebEngineView):
    """Markdown viewer with clean theme bridge integration."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup QWebEnginePage
        page = QWebEnginePage(self)
        self.setPage(page)

        # Create theme bridge with token mappings
        self._theme_bridge = ThemeBridge(
            page=page,
            token_mappings=[
                ThemeTokenMapping(
                    css_var="md-fg",
                    token_path="markdown.colors.foreground",
                    fallback_paths=["editor.foreground", "colors.foreground"],
                    default_value="#c9d1d9"
                ),
                ThemeTokenMapping(
                    css_var="md-bg",
                    token_path="markdown.colors.background",
                    fallback_paths=["editor.background", "colors.background"],
                    default_value="#0d1117"
                ),
                ThemeTokenMapping(
                    css_var="md-code-fg",
                    token_path="markdown.colors.code.foreground",
                    fallback_paths=["editor.foreground"],
                    default_value="#c9d1d9"
                ),
                ThemeTokenMapping(
                    css_var="md-code-bg",
                    token_path="markdown.colors.code.background",
                    fallback_paths=["editor.background"],
                    default_value="#161b22"
                ),
                # ... more mappings
            ],
            css_injection_callback=self._build_prism_override_css
        )

    def on_theme_changed(self, theme=None) -> None:
        """Apply theme via bridge.

        Args:
            theme: Optional theme to apply (uses current theme if None)
        """
        # Get theme (handle pending theme logic)
        theme = self._resolve_theme(theme)
        if not theme:
            return

        # Apply via bridge
        result = self._theme_bridge.apply_theme(theme)

        # Check result
        if not result.success:
            logger.error(f"Theme application failed: {result.errors}")
        else:
            logger.debug(f"Theme applied: {len(result.css_variables_set)} variables")

            # Log diagnostics if in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                if result.used_fallbacks:
                    logger.debug(f"  Fallbacks: {result.used_fallbacks}")
                if result.missing_tokens:
                    logger.debug(f"  Missing: {result.missing_tokens}")

    def _build_prism_override_css(self, css_vars: dict) -> str:
        """Build Prism.js override CSS using theme variables.

        This is a custom CSS injection for markdown-specific needs.

        Args:
            css_vars: CSS variables that were set

        Returns:
            CSS string to inject
        """
        # Only generate if code colors are available
        if "--md-code-bg" not in css_vars:
            return ""

        return """
        /* Override Prism.js hardcoded backgrounds */
        body #content pre[class*="language-"],
        body #content code[class*="language-"],
        pre[class*="language-"],
        code[class*="language-"] {
            background-color: var(--md-code-bg) !important;
            color: var(--md-code-fg) !important;
        }

        /* Inline code */
        body #content code,
        code {
            background-color: var(--md-code-bg) !important;
            color: var(--md-code-fg) !important;
        }
        """

    def _resolve_theme(self, theme):
        """Resolve theme with pending theme logic."""
        # Handle pending theme storage (from summary context)
        if theme is not None:
            self._pending_theme = theme
        elif self._pending_theme is not None:
            theme = self._pending_theme
        else:
            theme = self.get_current_theme()

        return theme
```

---

### 3. Testing ThemeBridge

```python
def test_theme_bridge_token_resolution():
    """Test theme token resolution with fallbacks."""
    from unittest.mock import Mock

    page_mock = Mock(spec=QWebEnginePage)

    bridge = ThemeBridge(
        page=page_mock,
        token_mappings=[
            ThemeTokenMapping(
                css_var="md-fg",
                token_path="markdown.colors.foreground",
                fallback_paths=["editor.foreground"],
                default_value="#ffffff"
            )
        ]
    )

    # Test with primary token present
    theme1 = Mock()
    theme1.colors = {"markdown": {"colors": {"foreground": "#123456"}}}

    result1 = bridge.apply_theme(theme1)
    assert result1.success
    assert result1.css_variables_set["--md-fg"] == "#123456"
    assert len(result1.used_fallbacks) == 0

    # Test with fallback token
    theme2 = Mock()
    theme2.colors = {"editor": {"foreground": "#abcdef"}}

    result2 = bridge.apply_theme(theme2)
    assert result2.success
    assert result2.css_variables_set["--md-fg"] == "#abcdef"
    assert result2.used_fallbacks["md-fg"] == "editor.foreground"

    # Test with default value
    theme3 = Mock()
    theme3.colors = {}

    result3 = bridge.apply_theme(theme3)
    assert result3.success
    assert result3.css_variables_set["--md-fg"] == "#ffffff"
    assert result3.used_fallbacks["md-fg"] == "default"


def test_theme_bridge_custom_css_injection():
    """Test custom CSS injection callback."""
    from unittest.mock import Mock

    page_mock = Mock(spec=QWebEnginePage)

    def prism_override_css(css_vars):
        if "--md-code-bg" in css_vars:
            return "pre { background: var(--md-code-bg); }"
        return ""

    bridge = ThemeBridge(
        page=page_mock,
        token_mappings=[
            ThemeTokenMapping("md-code-bg", "markdown.colors.code.background")
        ],
        css_injection_callback=prism_override_css
    )

    theme = Mock()
    theme.colors = {"markdown": {"colors": {"code": {"background": "#000"}}}}

    result = bridge.apply_theme(theme)
    assert result.success

    # Verify custom CSS was included in injection
    js_code_arg = page_mock.runJavaScript.call_args[0][0]
    assert "pre { background: var(--md-code-bg); }" in js_code_arg
```

---

## Reusability for Other Widgets

### Terminal Widget Integration

```python
# In terminal widget
from vfwidgets_common.bridges import ThemeBridge, ThemeTokenMapping

bridge = ThemeBridge(
    page=terminal_page,
    token_mappings=[
        ThemeTokenMapping("term-bg", "terminal.background",
                          fallback_paths=["editor.background"]),
        ThemeTokenMapping("term-fg", "terminal.foreground",
                          fallback_paths=["editor.foreground"]),
        # ... 16 ANSI color mappings
    ]
)
```

### Future PDF Viewer Widget

```python
# In PDF viewer widget
from vfwidgets_common.bridges import ThemeBridge, ThemeTokenMapping

bridge = ThemeBridge(
    page=pdf_page,
    token_mappings=[
        ThemeTokenMapping("pdf-bg", "pdf.background",
                          fallback_paths=["editor.background"]),
        ThemeTokenMapping("pdf-annotation-color", "pdf.annotation.color",
                          fallback_paths=["editor.selection.background"]),
    ]
)
```

---

## Migration Path

### Phase 1: Extract ThemeBridge Class (Week 1)
1. Create `bridges/theme_bridge.py` module
2. Implement `ThemeBridge` class
3. Add comprehensive unit tests
4. Keep existing code in `markdown_viewer.py` unchanged

### Phase 2: Integrate in MarkdownViewer (Week 1)
1. Refactor `on_theme_changed()` to use `ThemeBridge`
2. Extract token mappings to class-level constant
3. Extract Prism CSS override to callback
4. Maintain backward compatibility

### Phase 3: Move to vfwidgets_common (Week 2)
1. Move `ThemeBridge` to `shared/vfwidgets_common/bridges/`
2. Update imports in markdown widget
3. Document pattern for other widgets
4. Add examples to docs

---

## Benefits

### Immediate
- ✅ **Clean separation**: Theme logic isolated from widget
- ✅ **Testable**: Test theme resolution without QWebEngineView
- ✅ **Debuggable**: Clear logging of token resolution and fallbacks
- ✅ **Maintainable**: ~50 lines in widget vs. 140 lines currently

### Long-term
- ✅ **Reusable**: Pattern for all webview widgets
- ✅ **Consistent**: Uniform theme application across widgets
- ✅ **Extensible**: Easy to add new token mappings
- ✅ **Validated**: Can check theme completeness before application

---

## References

- **Terminal Widget Theme Analysis**: `/home/kuja/GitHub/vfwidgets/widgets/terminal_widget/docs/terminal-theme-improvements-ANALYSIS.md`
- **VS Code CSS Variable Pattern**: https://code.visualstudio.com/api/references/theme-color
- **Renderer Protocol Design**: `./renderer-protocol-DESIGN.md`
- **Webview Patterns Research**: `./webview-patterns-RESEARCH.md`

---

**Status**: Design Complete - Ready for Implementation
**Next Steps**: Finalize directory structure, then implement Phase 1 extraction
