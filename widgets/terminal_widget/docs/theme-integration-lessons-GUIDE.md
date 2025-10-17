# Theme Integration Lessons Learned: WebView-Based Widgets

**Document Purpose**: Reference guide for integrating the VFWidgets Theme System 2.0 with WebView-based widgets (xterm.js, Monaco Editor, etc.)

**Created From**: Real-world debugging session fixing bidirectional theme switching in TerminalWidget

---

## Table of Contents

1. [Critical Theme System Behaviors](#critical-theme-system-behaviors)
2. [WebView + Theme Integration Patterns](#webview--theme-integration-patterns)
3. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
4. [Best Practices](#best-practices)
5. [Debugging Techniques](#debugging-techniques)
6. [Reference Implementation](#reference-implementation)

---

## Critical Theme System Behaviors

### 1. Theme Property Cache Invalidation Timing

**Issue**: Property cache may not be fully updated when `on_theme_changed()` is called.

**What Happens**:
```python
def _on_global_theme_changed(self, theme_name: str) -> None:
    self._current_theme_name = theme_name              # ✅ Updated immediately
    self._theme_properties.invalidate_cache()          # ✅ Cache cleared
    self._apply_theme_update()                         # Regenerates stylesheet
    self.on_theme_changed()                            # ⚠️ Called here
```

**The Problem**:
- `self._current_theme_name` is reliably updated
- Cache is invalidated
- BUT: Accessing `self.theme.background` may still return stale cached values
- This appears to be a race condition or implementation detail in the property resolution system

**Lesson Learned**: **Never trust `self.theme.property` values in `on_theme_changed()`**

### 2. Built-in Themes Token Coverage

**Reality Check**: Built-in themes (`dark`, `light`, `minimal`) do NOT populate all token namespaces.

**What's Available**:
```python
# ✅ AVAILABLE in built-in themes
"colors.primary"       # "#007acc"
"colors.background"    # "#ffffff" (light) or "#2d2d2d" (dark)
"colors.foreground"    # "#000000" (light) or "#cccccc" (dark)

# ❌ NOT AVAILABLE in built-in themes
"editor.background"    # None (returns None)
"editor.foreground"    # None (returns None)
"terminal.colors.ansiRed"     # None (returns None)
```

**Lesson Learned**: **Always provide comprehensive fallbacks. Don't assume tokens exist.**

### 3. Theme Manager vs Application Current Theme

**Multiple Sources of Truth**:
```python
# ❌ STALE during notification
app = ThemedApplication.instance()
app._current_theme          # Still holds OLD theme object
app.get_current_theme()     # Returns OLD theme object

# ❌ STALE during notification
widget._theme_manager.current_theme  # Not updated yet

# ✅ RELIABLE during notification
widget._current_theme_name  # Correctly updated to new theme name
```

**Lesson Learned**: **In `on_theme_changed()`, use `self._current_theme_name` to query the theme manager by name**

### 4. Correct Way to Get Current Theme Type

**Wrong Way** (returns stale data):
```python
def on_theme_changed(self):
    app = ThemedApplication.instance()
    theme = app.get_current_theme()  # ❌ Returns OLD theme
    theme_type = theme.type           # ❌ Wrong type!
```

**Right Way** (always current):
```python
def _get_current_theme_type(self) -> str:
    """Get current theme type reliably."""
    try:
        if hasattr(self, '_current_theme_name') and self._current_theme_name:
            from vfwidgets_theme import ThemedApplication
            app = ThemedApplication.instance()
            if app and hasattr(app, '_theme_manager') and app._theme_manager:
                # Query by name - this gets the CURRENT theme
                theme = app._theme_manager.get_theme(self._current_theme_name)
                if theme and hasattr(theme, 'type'):
                    return theme.type
    except Exception as e:
        logger.error(f"Error getting theme type: {e}")
    return 'dark'  # Safe default
```

**Lesson Learned**: **Always query theme manager by name using `self._current_theme_name`**

---

## WebView + Theme Integration Patterns

### 1. JavaScript API Requirements

**xterm.js Theme Object Format**:
```javascript
// xterm.js v4+ uses this structure
terminal.setOption('theme', {
    background: '#1e1e1e',
    foreground: '#d4d4d4',
    cursor: '#d4d4d4',
    // ... ANSI colors
});
```

**Key Requirements**:
- JavaScript object with color properties
- Colors must be valid CSS color strings (#rrggbb, rgb(), rgba())
- Invalid/null colors cause fallback to defaults (often wrong theme)
- Must use proper API method (`setOption('theme', {})` not `Object.assign()`)

**Lesson Learned**: **Always validate colors before sending to JavaScript. One null color can break the entire theme.**

### 2. Bridging Qt Theme System to JavaScript

**Pattern: Theme-Aware Fallbacks**

```python
def on_theme_changed(self) -> None:
    # Step 1: Determine current theme type
    theme_type = self._get_current_theme_type()

    # Step 2: Select appropriate fallbacks based on type
    if theme_type == 'light':
        fallbacks = {
            'background': '#ffffff',
            'foreground': '#000000',
        }
    else:  # dark
        fallbacks = {
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
        }

    # Step 3: Use fallbacks directly (don't trust self.theme properties)
    js_theme = {
        'background': fallbacks['background'],
        'foreground': fallbacks['foreground'],
        # ... more colors
    }

    # Step 4: Send to JavaScript
    self._send_theme_to_js(js_theme)
```

**Lesson Learned**: **Use theme-aware fallbacks. Select fallback set based on theme type, not individual property checks.**

### 3. WebView Communication Patterns

**JSON Serialization**:
```python
import json

def set_theme(self, theme_dict: dict) -> None:
    # Convert Python dict to JSON
    js_theme = json.dumps(theme_dict)

    # Inject as JavaScript
    js_code = f"if (window.terminal) {{ window.terminal.setOption('theme', {js_theme}); }}"
    self.inject_javascript(js_code)
```

**Common Issues**:
- Missing `if (window.terminal)` guard → errors before page load
- Using `Object.assign(terminal.options.theme, {})` → doesn't trigger update
- Forgetting to JSON serialize → invalid JavaScript syntax

**Lesson Learned**: **Always guard JavaScript execution with existence checks and use proper API methods.**

### 4. Timing: When to Apply Themes

**Initialization Order**:
```python
1. Widget created
2. WebView created
3. HTML loaded
4. JavaScript initialized
5. ✅ Now safe to call terminal.setOption()
```

**Implementation Pattern**:
```python
def __init__(self):
    super().__init__()
    self._theme_pending = None

    # WebView signals page load completion
    self.web_view.loadFinished.connect(self._on_page_loaded)

def _on_page_loaded(self, success: bool):
    if success and self._theme_pending:
        self.set_theme(self._theme_pending)
        self._theme_pending = None

def set_theme(self, theme_dict: dict):
    if not self.is_ready():
        self._theme_pending = theme_dict  # Queue for later
        return

    # Apply immediately
    self._send_theme_to_js(theme_dict)
```

**Lesson Learned**: **Queue theme updates until JavaScript environment is ready. Don't silently fail.**

---

## Common Pitfalls and Solutions

### Pitfall 1: Using `self.theme.property or fallback`

**The Trap**:
```python
# ❌ BROKEN - self.theme.background may return STALE cached value
xterm_theme = {
    'background': self.theme.background or '#1e1e1e',
    'foreground': self.theme.foreground or '#d4d4d4',
}
```

**Why It Fails**:
- If `self.theme.background` returns `"#ffffff"` (cached from previous light theme)
- The `or` operator sees a truthy value and doesn't use fallback
- Result: Dark theme gets light colors

**The Fix**:
```python
# ✅ CORRECT - Use fallbacks directly
theme_type = self._get_current_theme_type()

if theme_type == 'light':
    fallbacks = {'background': '#ffffff', 'foreground': '#000000'}
else:
    fallbacks = {'background': '#1e1e1e', 'foreground': '#d4d4d4'}

xterm_theme = {
    'background': fallbacks['background'],
    'foreground': fallbacks['foreground'],
}
```

**Lesson Learned**: **In `on_theme_changed()`, bypass `self.theme` entirely and use fallbacks directly.**

### Pitfall 2: Assuming Tokens Exist

**The Trap**:
```python
# ❌ ASSUMES editor.background exists
theme_config = {
    'background': 'editor.background',
}

def on_theme_changed(self):
    # Returns None for built-in themes!
    bg = self.theme.background
```

**The Fix**:
```python
# ✅ Document the assumption and provide fallbacks
# Theme configuration - maps theme tokens to xterm.js properties
# NOTE: Built-in themes don't populate editor.* tokens,
#       so on_theme_changed() uses theme-aware fallbacks
theme_config = {
    'background': 'editor.background',  # Will be None for built-in themes
}

def on_theme_changed(self):
    # Don't use theme tokens - use theme-aware fallbacks instead
    theme_type = self._get_current_theme_type()
    # ... select fallbacks based on type
```

**Lesson Learned**: **Document token assumptions. Always have fallback strategy.**

### Pitfall 3: Forgetting Bidirectional Testing

**The Trap**:
- Test dark → light: ✅ Works!
- Ship it
- User switches light → dark: ❌ Broken!

**The Fix**:
```python
# test_theme_switch.py
def test_bidirectional_switching():
    """Test all theme transition directions."""
    window = ThemedTerminalWindow()
    app = ThemedApplication.instance()

    # Test each direction
    app.set_theme("dark")
    assert_background_is_dark()

    app.set_theme("light")
    assert_background_is_light()

    app.set_theme("dark")  # ← THIS IS CRITICAL
    assert_background_is_dark()

    app.set_theme("light")
    assert_background_is_light()
```

**Lesson Learned**: **Always test theme switching in BOTH directions multiple times.**

### Pitfall 4: Silent Failures

**The Trap**:
```python
def set_theme(self, theme_dict: dict):
    # Silently does nothing if terminal not ready
    if not self.is_ready():
        return  # ❌ Theme change lost forever
```

**The Fix**:
```python
def set_theme(self, theme_dict: dict):
    if not self.is_ready():
        self._pending_theme = theme_dict  # ✅ Queue for later
        logger.debug("Terminal not ready, queueing theme update")
        return

    self._apply_theme_immediately(theme_dict)
```

**Lesson Learned**: **Never silently drop requests. Queue or log them.**

---

## Best Practices

### 1. Theme Integration Checklist

When integrating theme system with a WebView widget:

- [ ] Define `theme_config` dict mapping properties to token paths
- [ ] Implement `_get_current_theme_type()` helper
- [ ] Implement `on_theme_changed()` with theme-aware fallbacks
- [ ] DO NOT use `self.theme.property` in `on_theme_changed()`
- [ ] DO query theme manager by name: `app._theme_manager.get_theme(self._current_theme_name)`
- [ ] Provide fallback colors for EVERY property
- [ ] Make fallbacks theme-aware (different for light vs dark)
- [ ] Guard all JavaScript calls with existence checks
- [ ] Use proper JavaScript API (not direct property assignment)
- [ ] Queue theme updates if WebView not ready
- [ ] Test bidirectional switching (dark↔light, multiple times)
- [ ] Add debug logging for theme changes

### 2. Fallback Strategy Pattern

```python
# Define once, use throughout widget
LIGHT_THEME_FALLBACKS = {
    'background': '#ffffff',
    'foreground': '#000000',
    'cursor': '#000000',
    'cursorAccent': '#ffffff',
    # ... all colors needed
}

DARK_THEME_FALLBACKS = {
    'background': '#1e1e1e',
    'foreground': '#d4d4d4',
    'cursor': '#d4d4d4',
    'cursorAccent': '#1e1e1e',
    # ... all colors needed
}

def on_theme_changed(self):
    theme_type = self._get_current_theme_type()
    fallbacks = LIGHT_THEME_FALLBACKS if theme_type == 'light' else DARK_THEME_FALLBACKS

    # Use fallbacks for everything
    js_theme = {k: fallbacks[k] for k in fallbacks}
    self.set_theme(js_theme)
```

### 3. Debug Logging Pattern

```python
def on_theme_changed(self):
    theme_type = self._get_current_theme_type()
    logger.debug(f"Theme changed: type={theme_type}, name={self._current_theme_name}")

    # Build theme
    fallbacks = self._select_fallbacks(theme_type)
    js_theme = self._build_js_theme(fallbacks)

    # Log what we're sending
    logger.debug(f"Applying theme: bg={js_theme['background']}, fg={js_theme['foreground']}")

    # Apply
    self.set_theme(js_theme)
```

### 4. Error Handling Pattern

```python
def _get_current_theme_type(self) -> str:
    """Get theme type with comprehensive error handling."""
    try:
        if hasattr(self, '_current_theme_name') and self._current_theme_name:
            from vfwidgets_theme import ThemedApplication
            app = ThemedApplication.instance()
            if app and hasattr(app, '_theme_manager') and app._theme_manager:
                theme = app._theme_manager.get_theme(self._current_theme_name)
                if theme and hasattr(theme, 'type'):
                    return theme.type
    except Exception as e:
        logger.error(f"Error getting theme type: {e}", exc_info=True)

    # Always return a valid default
    return 'dark'
```

---

## Debugging Techniques

### 1. Add Comprehensive Debug Output

```python
def on_theme_changed(self):
    # Log theme state
    logger.debug(f"=== THEME CHANGE DEBUG ===")
    logger.debug(f"_current_theme_name: {self._current_theme_name}")

    # Log theme type detection
    theme_type = self._get_current_theme_type()
    logger.debug(f"Detected theme type: {theme_type}")

    # Log fallback selection
    fallbacks = self._select_fallbacks(theme_type)
    logger.debug(f"Selected fallbacks: bg={fallbacks['background']}, fg={fallbacks['foreground']}")

    # Log final theme
    js_theme = self._build_js_theme(fallbacks)
    logger.debug(f"Final JS theme: bg={js_theme['background']}, fg={js_theme['foreground']}")
    logger.debug(f"=== END THEME CHANGE ===")
```

### 2. Verify JavaScript Reception

```python
def set_theme(self, theme_dict: dict):
    js_theme = json.dumps(theme_dict)
    js_code = f"""
    console.log('🎨 Received theme:', {js_theme});
    if (window.terminal) {{
        window.terminal.setOption('theme', {js_theme});
        console.log('✅ Theme applied');
    }} else {{
        console.error('❌ Terminal not available');
    }}
    """
    self.inject_javascript(js_code)
```

### 3. Create Automated Test

```python
# test_theme_switch.py
def test_theme_switching():
    """Automated test for theme switching."""
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")
    window = TestWindow()

    # Auto-test sequence
    QTimer.singleShot(2000, lambda: app.set_theme("light"))
    QTimer.singleShot(4000, lambda: app.set_theme("dark"))
    QTimer.singleShot(6000, lambda: app.set_theme("light"))
    QTimer.singleShot(8000, lambda: app.set_theme("dark"))
    QTimer.singleShot(10000, lambda: verify_success())
```

### 4. Check Browser Console

WebView widgets have a JavaScript console:
```python
# Enable debug output
self.web_view = QWebEngineView()
settings = self.web_view.settings()
settings.setAttribute(QWebEngineSettings.JavascriptConsoleMessages, True)

# View console output
# Look for: js: Color: null is invalid using fallback #ffffff
```

---

## Reference Implementation

Complete working implementation from TerminalWidget:

```python
class TerminalWidget(ThemedWidget, QWidget):
    """Terminal widget with proper theme integration."""

    # Theme configuration
    theme_config = {
        'background': 'editor.background',  # Won't exist in built-in themes
        'foreground': 'editor.foreground',
        # ... more mappings (won't be used in on_theme_changed)
    }

    def _get_current_theme_type(self) -> str:
        """Get current theme type for theme-aware fallbacks.

        Returns:
            'dark', 'light', or 'dark' (default)
        """
        try:
            if hasattr(self, '_current_theme_name') and self._current_theme_name:
                from vfwidgets_theme import ThemedApplication
                app = ThemedApplication.instance()
                if app and hasattr(app, '_theme_manager') and app._theme_manager:
                    # Query by name to get CURRENT theme (not cached)
                    theme = app._theme_manager.get_theme(self._current_theme_name)
                    if theme and hasattr(theme, 'type'):
                        return theme.type
        except Exception as e:
            logger.error(f"Error getting theme type: {e}")

        return 'dark'

    def on_theme_changed(self) -> None:
        """Handle theme change - called by framework."""
        if not THEME_AVAILABLE:
            return

        # Step 1: Get current theme type
        theme_type = self._get_current_theme_type()

        # Step 2: Select theme-aware fallbacks
        if theme_type == 'light':
            main_fallbacks = {
                'background': '#ffffff',
                'foreground': '#000000',
                'cursor': '#000000',
                'cursorAccent': '#ffffff',
                'selectionBackground': '#add6ff',
            }
        else:  # dark or unknown
            main_fallbacks = {
                'background': '#1e1e1e',
                'foreground': '#d4d4d4',
                'cursor': '#d4d4d4',
                'cursorAccent': '#1e1e1e',
                'selectionBackground': '#264f78',
            }

        # ANSI color fallbacks (same for both)
        ansi_fallbacks = {
            'black': '#2e3436',
            'red': '#cc0000',
            # ... etc
        }

        # Step 3: Build theme using fallbacks directly
        # NOTE: Do NOT use self.theme.property - may return stale cached values
        xterm_theme = {
            'background': main_fallbacks['background'],
            'foreground': main_fallbacks['foreground'],
            'cursor': main_fallbacks['cursor'],
            'cursorAccent': main_fallbacks['cursorAccent'],
            'selectionBackground': main_fallbacks['selectionBackground'],
            'black': ansi_fallbacks['black'],
            'red': ansi_fallbacks['red'],
            # ... all colors
        }

        # Step 4: Apply to xterm.js
        self.set_theme(xterm_theme)

    def set_theme(self, theme_dict: dict) -> None:
        """Apply theme to xterm.js terminal."""
        if not self.web_view or not self.is_connected:
            self._pending_theme = theme_dict
            return

        # Convert to JSON and inject
        js_theme = json.dumps(theme_dict)
        js_code = f"if (window.terminal) {{ window.terminal.setOption('theme', {js_theme}); }}"
        self.inject_javascript(js_code)

        logger.debug(f"Theme updated: {len(theme_dict)} colors")
```

---

## Key Takeaways

### For WebView Widget Developers

1. **Never trust `self.theme.property` in `on_theme_changed()`** - cache may be stale
2. **Always use theme-aware fallbacks** - select entire fallback set based on theme type
3. **Query theme manager by name** - `app._theme_manager.get_theme(self._current_theme_name)`
4. **Test bidirectionally** - dark→light AND light→dark, multiple times
5. **Guard JavaScript calls** - `if (window.object)` before calling methods
6. **Use proper APIs** - `terminal.setOption('theme', {})`, not `Object.assign()`

### For Theme System Users

1. **Built-in themes have limited tokens** - most namespaces are empty
2. **Always provide fallbacks** - for every property you use
3. **Theme type is your friend** - use it to select appropriate fallback sets
4. **Property cache timing** - don't rely on it during transition
5. **Debug with logging** - log theme name, type, and final colors

### For Everyone

**The Golden Rule**: In `on_theme_changed()`, treat the theme system as a notification mechanism only. Don't query it for colors - use theme-aware fallbacks instead.

---

## Related Documentation

- Theme System Architecture: `~/GitHub/vfwidgets/widgets/theme_system/docs/ARCHITECTURE.md`
- ThemedWidget API: `~/GitHub/vfwidgets/widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md`
- Terminal Widget Implementation: `~/GitHub/vfwidgets/widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Based On**: Real debugging session fixing TerminalWidget theme switching
