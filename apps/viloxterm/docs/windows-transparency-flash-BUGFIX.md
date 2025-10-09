# Windows Transparency Flash Bug Fix

**Status**: Implementation Ready
**Date**: 2025-10-09
**Issue**: Brief transparency flash when switching panes on Windows (desktop shows through)

---

## Root Cause Analysis

### The Problem
When switching panes on Windows, there's a brief flash where you can see through the app to the desktop.

### Why It Happens
1. ChromeTabbedWindow uses `WA_TranslucentBackground` for frameless design
2. When removing focus, code calls `setAutoFillBackground(False)` on the old terminal
3. This makes the widget temporarily transparent
4. On Windows, during the repaint, the desktop shows through the transparent widget
5. This creates a visible flash

### Additional Issues Found
- **Multiple hardcoded colors** throughout app.py (`#1e1e1e`, `#3a3a3a`, `#007ACC`)
- **Not theme-aware** - doesn't respond to light themes or user customizations
- **No update batching** - each style change triggers a repaint
- **Wrong operation order** - clears old focus before setting new (creates empty state)

---

## Solution: Theme-Aware Background Management

### Core Principle
**Never toggle `setAutoFillBackground()`** - always keep it `True` and change the background **color** instead.

### Implementation Strategy

1. **Add helper method** for centralized theme color resolution
2. **Fix focus change logic** - batch updates, reverse order, no transparency toggle
3. **Remove all hardcoded colors** - use theme tokens everywhere
4. **Initialize terminals properly** - opaque from creation
5. **Optimize for Windows** - use `WA_OpaquePaintEvent` attribute

---

## Part 1: Add Helper Method for Theme-Aware Colors

**File**: `apps/viloxterm/src/viloxterm/app.py`

**Location**: Add as new method in `ViloxTermApp` class (after `__init__`, before event handlers)

```python
def _get_theme_color(self, token_name: str, fallback_token: str = None) -> str:
    """Get color from theme system with fallback chain.

    Resolves colors from VSCode-compatible theme tokens with multiple fallback levels:
    1. Primary theme token from vfwidgets_theme
    2. Fallback theme token (if provided)
    3. Terminal theme (for background colors)
    4. Light/dark default based on theme type

    Args:
        token_name: Primary theme token (e.g., "editor.background")
        fallback_token: Secondary token if primary not found

    Returns:
        Hex color string (#RRGGBB format)

    Examples:
        >>> self._get_theme_color("editor.background")
        "#1e1e1e"
        >>> self._get_theme_color("focusBorder", "input.focusBorder")
        "#007ACC"
    """
    try:
        from vfwidgets_theme.core.tokens import ColorTokenRegistry
        from vfwidgets_theme.core.manager import ThemeManager

        theme_mgr = ThemeManager.get_instance()
        current_theme = theme_mgr.current_theme

        # Try primary token
        try:
            return ColorTokenRegistry.get(token_name, current_theme)
        except (KeyError, AttributeError):
            # Try fallback token
            if fallback_token:
                try:
                    return ColorTokenRegistry.get(fallback_token, current_theme)
                except (KeyError, AttributeError):
                    pass

            # Use terminal theme as fallback for background colors
            if token_name == "editor.background":
                terminal_theme = self.terminal_theme_manager.get_default_theme()
                if "background" in terminal_theme:
                    return terminal_theme["background"]

            # Final fallback based on theme type (dark vs light)
            if token_name == "editor.background":
                return "#1e1e1e" if current_theme.type == "dark" else "#f3f3f3"
            elif token_name in ("focusBorder", "input.focusBorder"):
                return "#007ACC" if current_theme.type == "dark" else "#0078d4"
            elif token_name in ("widget.border", "panel.border"):
                return "#3a3a3a" if current_theme.type == "dark" else "#d4d4d4"
            elif token_name in ("list.hoverBackground", "list.activeSelectionBackground"):
                return "#505050" if current_theme.type == "dark" else "#e8e8e8"
            else:
                return "#1e1e1e" if current_theme.type == "dark" else "#f3f3f3"

    except Exception:
        # Fallback to terminal theme, then emergency hardcoded
        try:
            if token_name == "editor.background":
                terminal_theme = self.terminal_theme_manager.get_default_theme()
                if "background" in terminal_theme:
                    return terminal_theme["background"]
        except Exception:
            pass

        # Emergency fallback (should rarely be reached)
        return "#1e1e1e"
```

---

## Part 2: Fix Transparency Flash in `_on_focus_changed()`

**File**: `apps/viloxterm/src/viloxterm/app.py`

**Location**: Lines 892-964 (replace entire method)

**Key Changes**:
- ✅ Never toggle `setAutoFillBackground` - always `True`
- ✅ Batch updates with `setUpdatesEnabled(False/True)`
- ✅ Set new focus FIRST, clear old SECOND (reversed order)
- ✅ Use theme-aware colors from helper method
- ✅ Change background color instead of toggling transparency

```python
def _on_focus_changed(self, old_pane_id: str, new_pane_id: str) -> None:
    """Handle focus changes with theme-aware backgrounds.

    Adds a prominent border to the focused terminal pane by modifying
    the layout margins and setting a background color on the container.

    CRITICAL: Always keeps setAutoFillBackground(True) and changes the
    background COLOR instead of toggling transparency. This prevents
    the transparency flash bug on Windows.

    Args:
        old_pane_id: Pane that lost focus (empty string if none)
        new_pane_id: Pane that gained focus (empty string if none)
    """
    multisplit = self.currentWidget()
    if not isinstance(multisplit, MultisplitWidget):
        return

    from PySide6.QtGui import QPalette, QColor

    # Get theme-aware colors (no hardcoded values)
    focus_color = self._get_theme_color("focusBorder", "input.focusBorder")
    bg_color = self._get_theme_color("editor.background")

    border_width = 3

    # IMPORTANT: Set new focus FIRST to avoid empty state during transition
    # This ensures there's always a focused pane with proper styling
    if new_pane_id:
        new_terminal = multisplit.get_widget(new_pane_id)
        if new_terminal and isinstance(new_terminal, TerminalWidget):
            # Batch updates to prevent multiple repaints (Windows optimization)
            new_terminal.setUpdatesEnabled(False)

            # Set layout margins to create space for border
            new_terminal.layout().setContentsMargins(
                border_width, border_width, border_width, border_width
            )

            # Set focus border color using QPalette (more reliable than stylesheet)
            palette = new_terminal.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(focus_color))
            new_terminal.setPalette(palette)
            new_terminal.setAutoFillBackground(True)  # ALWAYS TRUE

            # Re-enable updates (triggers single repaint)
            new_terminal.setUpdatesEnabled(True)

    # THEN clear old focus (order matters - prevents visual gaps)
    if old_pane_id:
        old_terminal = multisplit.get_widget(old_pane_id)
        if old_terminal and isinstance(old_terminal, TerminalWidget):
            # Batch updates
            old_terminal.setUpdatesEnabled(False)

            # Remove border margins
            old_terminal.layout().setContentsMargins(0, 0, 0, 0)

            # Change to background color (NOT transparent)
            palette = old_terminal.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
            old_terminal.setPalette(palette)
            old_terminal.setAutoFillBackground(True)  # KEEP TRUE - change color only

            # Re-enable updates
            old_terminal.setUpdatesEnabled(True)

    logger.debug(
        f"Focus changed: "
        f"{old_pane_id[:8] if old_pane_id else 'None'} -> "
        f"{new_pane_id[:8] if new_pane_id else 'None'}"
    )
```

---

## Part 3: Fix Hardcoded Colors in `add_new_terminal_tab()`

**File**: `apps/viloxterm/src/viloxterm/app.py`

**Location**: Lines 413-433 (update splitter style and MultisplitWidget initialization)

**Replace**:
```python
# OLD - Hardcoded colors
dark_splitter_style = SplitterStyle(
    handle_bg="#3a3a3a",  # ← HARDCODED
    handle_hover_bg="#505050",  # ← HARDCODED
    ...
)
multisplit.setStyleSheet("background-color: #1e1e1e;")  # ← HARDCODED
```

**With**:
```python
# Get theme-aware colors for splitter and background
splitter_bg = self._get_theme_color("widget.border", "panel.border")
splitter_hover = self._get_theme_color("list.hoverBackground", "list.activeSelectionBackground")
multisplit_bg = self._get_theme_color("editor.background")

# Create splitter style with theme-aware colors
dark_splitter_style = SplitterStyle(
    handle_width=1,
    handle_margin_horizontal=0,
    handle_margin_vertical=0,
    handle_bg=splitter_bg,  # Theme-aware
    handle_hover_bg=splitter_hover,  # Theme-aware
    border_width=0,
    show_hover_effect=True,
    cursor_on_hover=True,
    hit_area_padding=3,
)

multisplit = MultisplitWidget(
    provider=self.terminal_provider, splitter_style=dark_splitter_style
)

# Install event filter to intercept keyboard shortcuts
multisplit.installEventFilter(self)

# Set theme-aware background using QPalette (more reliable than stylesheet)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

palette = multisplit.palette()
palette.setColor(QPalette.ColorRole.Window, QColor(multisplit_bg))
multisplit.setPalette(palette)
multisplit.setAutoFillBackground(True)

# Mark as opaque for better Windows repaint performance
multisplit.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)

# Connect to pane_added signal for auto-focus on split
multisplit.pane_added.connect(self._on_pane_added)

# Connect to focus_changed signal for visual indicators
multisplit.focus_changed.connect(self._on_focus_changed)
```

---

## Part 4: Initialize Terminals with Opaque Background

**File**: `apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

**Location**: In `provide_widget()` method, after line 63 (after creating terminal widget)

**Add after**:
```python
terminal = TerminalWidget(
    server_url=session_url,
    terminal_config=self._default_config,
)
```

**Insert this code**:
```python
# Initialize with theme-aware opaque background
# This prevents any transparency flash on first render
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# Get background color from terminal theme
bg_color = "#1e1e1e"  # Default fallback
if self._default_theme and "background" in self._default_theme:
    bg_color = self._default_theme["background"]

# Set opaque background immediately
palette = terminal.palette()
palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
terminal.setPalette(palette)
terminal.setAutoFillBackground(True)

# Mark as opaque for better repaint performance (especially on Windows)
terminal.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)

logger.debug(f"Initialized terminal {widget_id} with opaque background: {bg_color}")
```

**Then continue with existing code**:
```python
# Apply default theme if set (theme is applied after config in _configure_terminal)
if self._default_theme:
    terminal.set_terminal_theme(self._default_theme)
    logger.debug(f"Applied default theme to terminal: {widget_id}")
```

---

## Theme Tokens Reference

| Purpose | Primary Token | Fallback Token | Emergency Fallback (Dark/Light) |
|---------|--------------|----------------|--------------------------------|
| Unfocused pane background | `editor.background` | terminal theme | `#1e1e1e` / `#f3f3f3` |
| Focused pane border | `focusBorder` | `input.focusBorder` | `#007ACC` / `#0078d4` |
| Splitter handle | `widget.border` | `panel.border` | `#3a3a3a` / `#d4d4d4` |
| Splitter hover | `list.hoverBackground` | `list.activeSelectionBackground` | `#505050` / `#e8e8e8` |

**VSCode Theme Token Documentation**: https://code.visualstudio.com/api/references/theme-color

---

## Implementation Checklist

- [ ] Add `_get_theme_color()` helper method to `ViloxTermApp`
- [ ] Replace `_on_focus_changed()` method with new implementation
- [ ] Update `add_new_terminal_tab()` to use theme-aware colors
- [ ] Initialize terminals with opaque background in `terminal_provider.py`
- [ ] Test on Windows (no transparency flash)
- [ ] Test with light theme (correct colors)
- [ ] Test with custom terminal themes
- [ ] Verify focus borders work correctly
- [ ] Check splitter handle colors match theme
- [ ] Commit changes with comprehensive message

---

## Expected Results

### After Implementation

✅ **No transparency flash** on Windows (or any platform)
✅ **Zero hardcoded colors** - fully theme-aware
✅ **Works with light themes** - automatically adapts colors
✅ **Performance optimized** - batched updates, `WA_OpaquePaintEvent`
✅ **Consistent behavior** - all terminals initialized properly from creation
✅ **Future-proof** - responds to theme changes dynamically

### Visual Behavior

1. **Unfocused panes**: Match `editor.background` from theme (or terminal theme background)
2. **Focused pane**: Has colored border using `focusBorder` token
3. **Splitter handles**: Use `widget.border` color, hover uses `list.hoverBackground`
4. **Theme changes**: All colors update automatically when user changes themes
5. **Light themes**: Everything works correctly with light backgrounds

---

## Testing Instructions

### Test on Windows
1. Build ViloxTerm on Windows: `.\build.ps1`
2. Run the binary: `.\ViloXTerm.exe`
3. Create multiple panes (Ctrl+Shift+H, Ctrl+Shift+V)
4. Switch between panes with Ctrl+Shift+Arrow keys
5. Verify: No flash/transparency visible during switches

### Test Theme Integration
1. Open terminal theme dialog (Ctrl+Shift+,)
2. Switch to light theme (e.g., "Light+")
3. Verify: All colors adapt (background, borders, splitters)
4. Switch back to dark theme
5. Verify: Returns to dark colors

### Test Custom Terminal Themes
1. Load custom terminal theme with unusual background color
2. Create new terminal
3. Verify: Unfocused panes match terminal background color
4. Verify: Focus border still visible and contrasts with background

---

## Files Modified Summary

1. **`apps/viloxterm/src/viloxterm/app.py`** (3 changes)
   - Add `_get_theme_color()` helper method
   - Replace `_on_focus_changed()` implementation
   - Update `add_new_terminal_tab()` splitter and background initialization

2. **`apps/viloxterm/src/viloxterm/providers/terminal_provider.py`** (1 change)
   - Initialize terminals with opaque background in `provide_widget()`

---

## Performance Optimizations

### Windows-Specific
- `WA_OpaquePaintEvent` attribute tells Qt the widget always paints its entire area
- Reduces compositor overhead on Windows
- Faster repaints, especially during rapid focus changes

### All Platforms
- `setUpdatesEnabled(False/True)` batches multiple style changes into single repaint
- Reversed operation order (set new → clear old) prevents empty visual state
- QPalette changes are faster than stylesheet parsing

---

## Version History

- **v1.0** (2025-10-09): Initial bugfix document
