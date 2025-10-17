"""Theme bridge for Python ↔ JavaScript theme communication.

This module provides clean abstraction for applying theme tokens to
webview content via CSS variable injection.
"""

import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

from PySide6.QtWebEngineCore import QWebEnginePage

logger = logging.getLogger(__name__)


@dataclass
class ThemeTokenMapping:
    """Maps CSS variable names to theme token paths with fallback chain.

    Example:
        ThemeTokenMapping(
            css_var="md-fg",
            token_path="markdown.colors.foreground",
            fallback_paths=["editor.foreground", "colors.foreground"],
            default_value="#c9d1d9"
        )

    This will try to resolve in order:
    1. markdown.colors.foreground
    2. editor.foreground (if #1 missing)
    3. colors.foreground (if #2 missing)
    4. #c9d1d9 (if all missing)
    """

    css_var: str  # CSS variable name (without -- prefix)
    token_path: str  # Primary theme token path (dot notation)
    fallback_paths: list[str] = field(default_factory=list)  # Fallback token paths
    default_value: Optional[str] = None  # Hard default if all tokens missing


@dataclass
class ThemeApplicationResult:
    """Result of applying theme to page.

    Provides comprehensive diagnostics about what was applied,
    what tokens were missing, and any errors that occurred.
    """

    success: bool
    css_variables_set: dict[str, str]  # {"--md-fg": "#c9d1d9", ...}
    missing_tokens: list[str]  # Token paths that had no value
    used_fallbacks: dict[str, str]  # {"md-fg": "editor.foreground", ...}
    errors: list[str]  # Any errors during application


class ThemeBridge:
    """Manages theme communication between Python and JavaScript.

    Responsibilities:
    - Resolve theme tokens with fallback chains
    - Build CSS custom properties (variables)
    - Inject CSS into QWebEnginePage via JavaScript
    - Validate theme application
    - Provide diagnostic logging

    Example:
        bridge = ThemeBridge(
            page=web_page,
            token_mappings=[
                ThemeTokenMapping(
                    css_var="md-fg",
                    token_path="markdown.colors.foreground",
                    fallback_paths=["editor.foreground"],
                    default_value="#c9d1d9"
                ),
                ThemeTokenMapping(
                    css_var="md-bg",
                    token_path="markdown.colors.background",
                    fallback_paths=["editor.background"],
                    default_value="#0d1117"
                ),
            ],
            css_injection_callback=lambda vars: custom_css_builder(vars)
        )

        result = bridge.apply_theme(theme)
        if not result.success:
            logger.error(f"Theme application failed: {result.errors}")
        elif result.missing_tokens:
            logger.warning(f"Missing tokens: {result.missing_tokens}")
    """

    def __init__(
        self,
        page: QWebEnginePage,
        token_mappings: list[ThemeTokenMapping],
        css_injection_callback: Optional[Callable[[dict], str]] = None,
    ):
        """Initialize theme bridge.

        Args:
            page: QWebEnginePage where CSS will be injected
            token_mappings: List of CSS variable to theme token mappings
            css_injection_callback: Optional custom CSS builder
                Signature: (css_vars: dict) -> str (CSS string)
                Used for special cases like Prism.js overrides
        """
        self._page = page
        self._token_mappings = token_mappings
        self._css_injection_callback = css_injection_callback
        self._last_result: Optional[ThemeApplicationResult] = None

    def apply_theme(self, theme) -> ThemeApplicationResult:
        """Apply theme to page by injecting CSS variables.

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
                errors=["No theme provided"],
            )

        logger.debug(f"Applying theme '{theme.name}' to page")

        # Step 1: Resolve theme tokens with fallback chains
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
                logger.warning(
                    f"  Token '{mapping.token_path}' not found " f"(no fallbacks or default)"
                )

        # Log resolution summary
        logger.debug(f"  Resolved {len(css_vars)} CSS variables")
        if used_fallbacks:
            logger.debug(f"  Used fallbacks for {len(used_fallbacks)} variables:")
            for css_var, fallback_path in used_fallbacks.items():
                logger.debug(f"    {css_var} → {fallback_path}")

        # Step 2: Build JavaScript injection code
        css_injection = self._build_css_injection(css_vars)

        # Step 3: Inject CSS into page
        try:
            self._inject_css(css_injection)

            result = ThemeApplicationResult(
                success=True,
                css_variables_set=css_vars,
                missing_tokens=missing_tokens,
                used_fallbacks=used_fallbacks,
                errors=[],
            )

        except Exception as e:
            logger.error(f"Failed to inject CSS: {e}", exc_info=True)
            result = ThemeApplicationResult(
                success=False,
                css_variables_set=css_vars,
                missing_tokens=missing_tokens,
                used_fallbacks=used_fallbacks,
                errors=[str(e)],
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
            logger.debug(f"  {mapping.css_var}: {value} (from {mapping.token_path})")
            return ResolvedToken(value=value, used_fallback=None)

        # Try fallback paths
        for fallback_path in mapping.fallback_paths:
            value = self._get_nested_value(theme.colors, fallback_path)
            if value:
                logger.debug(
                    f"  {mapping.css_var}: {value} (fallback: {fallback_path}, "
                    f"primary '{mapping.token_path}' not found)"
                )
                return ResolvedToken(value=value, used_fallback=fallback_path)

        # Use default value if provided
        if mapping.default_value:
            logger.debug(
                f"  {mapping.css_var}: {mapping.default_value} (default, " f"no theme tokens found)"
            )
            return ResolvedToken(value=mapping.default_value, used_fallback="default")

        # No value found
        logger.warning(
            f"  {mapping.css_var}: No value (tried {mapping.token_path}, "
            f"{mapping.fallback_paths}, no default)"
        )
        return ResolvedToken(value=None, used_fallback=None)

    def _get_nested_value(self, colors: dict, path: str) -> Optional[str]:
        """Get value from nested dict using dot notation path.

        Supports both flat and nested structures:
        - Flat: {"markdown.colors.foreground": "#fff"}
        - Nested: {"markdown": {"colors": {"foreground": "#fff"}}}

        Args:
            colors: Dictionary (theme.colors) - flat or nested
            path: Dot-notation path (e.g., "markdown.colors.foreground")

        Returns:
            String value if found, None otherwise
        """
        # Try direct lookup first (flat structure from Theme Studio)
        if path in colors:
            value = colors[path]
            return value if isinstance(value, str) else None

        # Fall back to nested traversal (nested structure from JSON files)
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
            JavaScript code string to execute
        """
        # Build CSS variable string
        css_vars_string = "; ".join(f"{k}: {v}" for k, v in css_vars.items())

        # Escape for JavaScript string
        css_vars_string = css_vars_string.replace("\\", "\\\\").replace('"', '\\"')

        # Base injection code
        # Inject on body element to override body[data-theme] specificity in viewer.css
        js_code = f"""
(function() {{
    // Inject CSS variables into body element (overrides body[data-theme] in viewer.css)
    document.body.style.cssText += "{css_vars_string};";

    // Log to console for debugging
    console.log("[ThemeBridge] Applied {len(css_vars)} CSS variables");

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
            Additional JavaScript code for custom CSS, or empty string
        """
        if not self._css_injection_callback:
            return ""

        try:
            custom_css = self._css_injection_callback(css_vars)
            if not custom_css:
                return ""

            # Escape CSS for JavaScript
            custom_css = custom_css.replace("\\", "\\\\").replace("`", "\\`")

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

        except Exception as e:
            logger.error(f"Custom CSS injection callback failed: {e}", exc_info=True)
            return ""

    def _inject_css(self, js_code: str) -> None:
        """Execute JavaScript to inject CSS.

        Args:
            js_code: JavaScript code to execute

        Raises:
            RuntimeError: If page is None or injection fails
        """
        if not self._page:
            raise RuntimeError("QWebEnginePage is None, cannot inject CSS")

        self._page.runJavaScript(js_code, lambda result: self._on_injection_complete(result))

    def _on_injection_complete(self, result) -> None:
        """Callback when CSS injection completes.

        Args:
            result: JavaScript return value (True if successful)
        """
        if result is True:
            logger.debug("  CSS injection completed successfully")
        elif result is False:
            logger.warning("  CSS injection returned False")
        elif result is None:
            # JavaScript returned undefined - this is normal
            logger.debug("  CSS injection executed (no return value)")
        else:
            logger.warning(f"  CSS injection returned unexpected value: {result}")

    def get_last_result(self) -> Optional[ThemeApplicationResult]:
        """Get result of last theme application.

        Returns:
            ThemeApplicationResult from last apply_theme() call, or None
        """
        return self._last_result

    def validate_theme(self, theme) -> dict:
        """Validate theme has all required tokens.

        This can be used by Theme Studio to show warnings about
        missing tokens before applying the theme.

        Args:
            theme: Theme object to validate

        Returns:
            Validation report dict: {
                "complete": bool,
                "completeness_percentage": float (0-100),
                "missing_tokens": list[str],
                "present_tokens": list[str]
            }
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
            "completeness_percentage": (
                (len(present) / len(required_tokens) * 100) if required_tokens else 100.0
            ),
            "missing_tokens": missing,
            "present_tokens": present,
        }
