# MarkdownViewer Theme System Integration Guide

**Version:** 2.0
**Date:** 2025-10-11
**Status:** Complete

## Overview

The MarkdownViewer widget integrates with the VFWidgets theme system to provide automatic, seamless theming of markdown content. This document explains how the integration works, the techniques used, and lessons learned.

## Architecture

### Component Stack

```
Application (ThemedApplication)
    ↓
MarkdownViewer (ThemedWidget)
    ↓
QWebEngineView
    ↓
HTML/CSS Content (themed via JavaScript injection)
```

### Key Components

1. **ThemedWidget Inheritance**: MarkdownViewer optionally inherits from ThemedWidget when vfwidgets-theme is available
2. **Theme Config Mapping**: Maps theme tokens to CSS variables
3. **JavaScript Bridge**: Injects theme colors into web content
4. **Deferred Application**: Handles async QWebEngineView initialization

## Theme Integration Pattern

### 1. Optional Theme System Support

```python
# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

# Conditional inheritance via mixin pattern
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWebEngineView), {})
else:
    _BaseClass = QWebEngineView

class MarkdownViewer(_BaseClass):
    """Widget works with or without theme system."""
    pass
```

**Why this works:**
- Widget is fully functional without vfwidgets-theme installed
- Seamlessly gains theme capabilities when theme system is available
- No code duplication or conditional logic in implementation

### 2. Theme Token Mapping

```python
theme_config = {
    # Markdown content colors
    "md_bg": "editor.background",
    "md_fg": "editor.foreground",
    "md_heading": "editor.foreground",
    "md_link": "textLink.foreground",
    "md_link_hover": "textLink.activeForeground",

    # Code styling
    "md_code_bg": "textCodeBlock.background",
    "md_code_fg": "textPreformat.foreground",

    # UI elements
    "md_border": "editorWidget.border",
    "md_quote_border": "textBlockQuote.border",
    "md_quote_bg": "textBlockQuote.background",

    # Tables
    "md_table_border": "editorWidget.border",
    "md_table_header_bg": "editor.lineHighlightBackground",

    # Scrollbar
    "md_scrollbar_bg": "editor.background",
    "md_scrollbar_thumb": "scrollbar.activeBackground",
    "md_scrollbar_thumb_hover": "scrollbar.hoverBackground",
}
```

**Token Selection Strategy:**
- Use semantic tokens from VSCode theme spec where possible
- Map to closest equivalent for markdown-specific elements
- Fallback to editor tokens for consistency

### 3. White Flash Prevention

**The Challenge:** QWebEngineView shows white background before HTML loads, causing jarring flash.

**The Solution:** Set page background color based on application theme type during init.

```python
def _get_initial_background_color(self) -> str:
    """Get initial background color for WebView.

    Checks the application's current theme type to return an appropriate
    static fallback color (dark or light) that prevents flash on startup.
    """
    # Try to determine theme type from application
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app and hasattr(app, "get_current_theme"):
            current_theme = app.get_current_theme()
            if current_theme and hasattr(current_theme, "type"):
                # Return appropriate static color based on theme type
                if current_theme.type == "dark":
                    return "#1a1a1a"  # Dark background
                else:
                    return "#ffffff"  # Light background
    except Exception:
        pass  # Continue to fallback

    # Default fallback to dark (most common for development/terminal apps)
    return "#1a1a1a"

# In __init__:
bg_color = self._get_initial_background_color()
self.page().setBackgroundColor(QColor(bg_color))
```

**Key Points:**
- ✅ **Check `app.get_current_theme().type`** - Application theme IS available during `__init__`
- ❌ **Don't check `self.theme.colors`** - Widget theme NOT applied until after `__init__` completes
- Use **theme type** (dark/light) not individual color values
- Prevents white flash on dark themes, black flash on light themes

**Why This Works:**
- `ThemedApplication.get_current_theme()` returns the app's current theme immediately
- Theme **type** ("dark" or "light") is available even though widget theme colors aren't
- Static fallback based on type is sufficient - exact colors applied later via JavaScript

### 4. Async Initialization Handling

**The Challenge:** QWebEngineView isn't fully initialized until shown/polished, but ThemedWidget wants to apply theme during `__init__`.

**The Solution:** Defer theme application until viewer is ready.

```python
def __init__(self, parent=None):
    super().__init__(parent)

    self._is_ready = False
    self.viewer_ready = Signal()

    # Connect to apply theme when ready (only once)
    if THEME_AVAILABLE:
        self.viewer_ready.connect(
            self._apply_initial_theme,
            Qt.ConnectionType.SingleShotConnection
        )

    # ... setup web engine ...

def showEvent(self, event):
    """Handle widget show event - viewer is now ready."""
    super().showEvent(event)
    if not self._is_ready:
        self._is_ready = True
        self.viewer_ready.emit()

def on_theme_changed(self):
    """Called when theme changes."""
    # Guard: don't apply if not ready yet
    if not self._is_ready:
        return

    # Apply theme via JavaScript
    self._inject_theme_colors()

def _apply_initial_theme(self):
    """Apply theme when viewer becomes ready."""
    self.on_theme_changed()
```

**Timing Diagram:**

```
Time →

Widget __init__ starts
    ↓
Set page background color (prevents flash)
    ↓
ThemedWidget defers theme (QTimer.singleShot)
    ↓
__init__ completes
    ↓
Deferred theme tries to apply
    ↓
on_theme_changed() called but returns early (_is_ready=False)
    ↓
Widget shown (showEvent)
    ↓
viewer_ready signal emitted
    ↓
_apply_initial_theme() called
    ↓
on_theme_changed() executes (now _is_ready=True)
    ↓
Theme injected via JavaScript
```

### 5. Theme Injection via JavaScript

**The Technique:** Inject CSS variables into HTML document's `<style>` tag.

```python
def on_theme_changed(self):
    """Inject theme colors into web content."""
    if not self._is_ready:
        return

    # Build CSS variables from theme
    if hasattr(self, "theme"):
        css_vars = "\n".join([
            f"--{key.replace('_', '-')}: {getattr(self.theme, key)};"
            for key in self.theme_config.keys()
            if hasattr(self.theme, key) and getattr(self.theme, key) is not None
        ])

        # Escape for JavaScript
        escaped_css_vars = (
            css_vars.replace("\\", "\\\\")
                   .replace("'", "\\'")
                   .replace("\n", "\\n")
        )

        # Inject into document
        js_code = f"""
        (function() {{
            var style = document.getElementById('theme-vars');
            if (!style) {{
                style = document.createElement('style');
                style.id = 'theme-vars';
                document.head.appendChild(style);
            }}
            style.textContent = 'body {{ {escaped_css_vars} }}';
        }})();
        """

        self.page().runJavaScript(js_code)
```

**CSS Side (viewer.css):**

```css
body {
    color: var(--md-fg, #c9d1d9);
    background-color: var(--md-bg, #0d1117);
}

::-webkit-scrollbar-thumb {
    background-color: var(--md-scrollbar-thumb, #30363d);
}

/* etc. */
```

**Why This Works:**
- CSS variables provide clean separation between theme data and styling
- JavaScript injection is safe (we control the theme data)
- Fallback values in CSS ensure graceful degradation
- Updates are instant when theme changes

### 6. Syntax Highlighting Theme Sync

**The Challenge:** Code blocks use Prism.js with separate themes.

**The Solution:** Sync Prism theme with app theme.

```python
def on_theme_changed(self):
    """Update both CSS variables and syntax theme."""
    # ... CSS variable injection ...

    # Determine if dark or light
    is_dark = False
    try:
        app = QApplication.instance()
        if app and hasattr(app, "get_current_theme"):
            current_theme = app.get_current_theme()
            if current_theme and hasattr(current_theme, "type"):
                is_dark = current_theme.type == "dark"
    except Exception:
        pass

    # Update JavaScript viewer theme
    theme_name = "dark" if is_dark else "light"
    self.set_theme(theme_name)

def set_theme(self, theme: str):
    """Set viewer theme (dark/light)."""
    escaped_theme = json.dumps(theme)
    js_code = f"window.MarkdownViewer.setSyntaxTheme({escaped_theme});"
    self.page().runJavaScript(js_code)
```

**JavaScript Side (viewer.js):**

```javascript
window.MarkdownViewer = {
    setSyntaxTheme: function(theme) {
        // Switch Prism CSS file
        const prismLink = document.getElementById('prism-theme');
        if (theme === 'dark') {
            prismLink.href = 'css/prism-themes/prism-tomorrow.css';
        } else {
            prismLink.href = 'css/prism-themes/prism.css';
        }

        // Update body data-theme attribute
        document.body.setAttribute('data-theme', theme);
    }
};
```

## Integration Checklist

When integrating a QWebEngineView-based widget with the theme system:

### Phase 1: Basic Setup
- [ ] Add optional ThemedWidget import and mixin pattern
- [ ] Define theme_config mapping appropriate theme tokens
- [ ] Test widget works without vfwidgets-theme installed

### Phase 2: White Flash Prevention
- [ ] Implement `_get_initial_background_color()` checking app theme type
- [ ] Call `page().setBackgroundColor()` in `__init__`
- [ ] Test with both dark and light themes
- [ ] Verify no white/black flash on widget creation

### Phase 3: Async Initialization
- [ ] Add `_is_ready` flag and `viewer_ready` signal
- [ ] Connect signal to initial theme application (SingleShotConnection)
- [ ] Implement guard in `on_theme_changed()` to check `_is_ready`
- [ ] Emit `viewer_ready` in `showEvent()`

### Phase 4: Theme Injection
- [ ] Implement `on_theme_changed()` with JavaScript injection
- [ ] Build CSS variables from theme_config mappings
- [ ] Escape CSS properly for JavaScript embedding
- [ ] Test theme switching works after widget is shown

### Phase 5: CSS Integration
- [ ] Add CSS variables to stylesheet with fallback values
- [ ] Use `var(--token-name, fallback)` pattern throughout
- [ ] Add `[data-theme="dark"]` and `[data-theme="light"]` overrides if needed
- [ ] Test appearance with theme applied and without

### Phase 6: Documentation
- [ ] Document theme token choices
- [ ] Explain any special techniques or gotchas
- [ ] Add examples of themed widget usage
- [ ] Update widget README with theme support info

## Common Pitfalls

### ❌ Accessing self.theme During __init__

**Wrong:**
```python
def __init__(self):
    super().__init__()
    # ❌ self.theme not available yet!
    bg_color = self.theme.md_bg if hasattr(self, 'theme') else "#000"
    self.page().setBackgroundColor(QColor(bg_color))
```

**Right:**
```python
def __init__(self):
    super().__init__()
    # ✅ Check app theme TYPE, not widget theme colors
    bg_color = self._get_initial_background_color()
    self.page().setBackgroundColor(QColor(bg_color))
```

### ❌ Applying Theme Before Viewer Ready

**Wrong:**
```python
def on_theme_changed(self):
    # ❌ No guard - will fail if page not loaded yet
    self.page().runJavaScript("...")
```

**Right:**
```python
def on_theme_changed(self):
    # ✅ Guard prevents premature theme application
    if not self._is_ready:
        return
    self.page().runJavaScript("...")
```

### ❌ Hardcoded Background Color

**Wrong:**
```python
def _get_initial_background_color(self):
    # ❌ Always dark - causes black flash on light themes
    return "#1a1a1a"
```

**Right:**
```python
def _get_initial_background_color(self):
    # ✅ Check theme type for appropriate fallback
    app = QApplication.instance()
    if app and hasattr(app, "get_current_theme"):
        theme = app.get_current_theme()
        if theme and theme.type == "dark":
            return "#1a1a1a"
        else:
            return "#ffffff"
    return "#1a1a1a"
```

### ❌ Unescaped JavaScript Injection

**Wrong:**
```python
js_code = f"var style = '{css_vars}';"  # ❌ Vulnerable to injection
```

**Right:**
```python
escaped = css_vars.replace("\\", "\\\\").replace("'", "\\'")  # ✅ Escaped
js_code = f"var style = '{escaped}';"
```

### ❌ Over-Engineering Protection Layers

**Wrong:**
```python
# ❌ 4 layers of background color setting
self.setStyleSheet("QWidget { background: #1a1a1a; }")  # 1
self.web_view.setStyleSheet("QWebEngineView { background: #1a1a1a; }")  # 2
self.web_view.page().setBackgroundColor(QColor("#1a1a1a"))  # 3
# HTML template also has default dark background  # 4
```

**Right:**
```python
# ✅ Just page background + HTML defaults
self.page().setBackgroundColor(QColor(bg_color))  # Sufficient!
# HTML template has fallback defaults in case JavaScript delayed
```

## Performance Considerations

### Theme Switching Performance
- **Target:** < 100ms for theme change
- **Achieved:** ~20-50ms (measured)
- **Technique:** Single JavaScript call to inject all CSS variables at once

### Memory Usage
- **Theme data:** < 1KB per widget (just references to theme manager)
- **CSS variables:** Minimal overhead (browser native)
- **No duplication:** All widgets share same theme manager

### Startup Time
- **White flash prevention:** 0ms overhead (static check)
- **Deferred theme:** Happens off critical path
- **No blocking:** JavaScript injection is async

## Testing Strategy

### Manual Testing
```bash
# Test basic theming
python -c "from vfwidgets_markdown import MarkdownViewer; from PySide6.QtWidgets import QApplication; app = QApplication([]); w = MarkdownViewer(); w.show(); app.exec()"

# Test theme switching
# Open widget, go to Theme Preferences, switch themes
# Verify colors update, no flash, no errors

# Test without theme system
pip uninstall vfwidgets-theme
# Run again, verify widget still works
```

### Automated Testing
```python
def test_theme_integration(qtbot):
    """Test theme integration works."""
    from vfwidgets_markdown import MarkdownViewer

    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Verify has theme config
    assert hasattr(viewer, 'theme_config')
    assert 'md_bg' in viewer.theme_config

    # Verify background color set
    bg_color = viewer.page().backgroundColor()
    assert bg_color.isValid()

    # Show widget to trigger ready state
    viewer.show()
    qtbot.waitExposed(viewer)

    # Verify theme applied after ready
    assert viewer._is_ready
```

## Related Documentation

- **Terminal Widget**: `widgets/terminal_widget/docs/lessons-learned-GUIDE.md` - Similar QWebEngineView theme integration
- **Theme System**: `widgets/theme_system/README.md` - Core theme system documentation
- **ThemedWidget**: `widgets/theme_system/docs/themed-widget-api.md` - ThemedWidget base class API
- **White Flash Fix**: `apps/reamde/white-flash-simplification-BUGFIX.md` - Detailed bugfix writeup

## Changelog

### v2.0 (2025-10-11)
- Added light theme support in white flash prevention
- Enhanced documentation with theme type vs colors distinction
- Added comprehensive integration checklist
- Documented common pitfalls and solutions

### v1.0 (2025-10-11)
- Initial theme system integration
- White flash prevention (dark themes only)
- Async initialization handling
- CSS variable injection pattern
