# ViloxTerm Terminal Customization - Implementation Plan

**Status:** Planning Phase
**Created:** 2025-10-04
**Goal:** Enable users to customize terminal colors, fonts, and appearance with live preview and theme management

---

## Table of Contents

1. [Current State](#current-state)
2. [Requirements](#requirements)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Implementation Phases](#implementation-phases)
6. [File Structure](#file-structure)
7. [API Design](#api-design)
8. [User Workflow](#user-workflow)

---

## Current State

### What ViloxTerm Has Now

- **ThemeDialog**: Simple modal for switching between 4 built-in themes (dark, light, default, minimal)
- **Application-level theming**: Changes Qt widget appearance only
- **No terminal-specific customization**: Terminal colors/fonts are hardcoded

### What TerminalWidget Provides

- **theme_config** (terminal.py:255): Maps terminal properties to theme tokens
- **Terminal color mapping**:
  - Editor tokens: `editor.background`, `editor.foreground`, `editor.selectionBackground`
  - ANSI colors: `terminal.ansiBlack`, `terminal.ansiRed`, etc.
- **_apply_theme() method** (terminal.py:1024): Currently a stub (does nothing!)
- **xterm.js configuration**: Hardcoded in terminal.html (lines 86-117)

### The Gap

1. **Terminal colors are hardcoded** in `terminal.html` CONFIG object
2. **Application theme changes don't update terminal appearance**
3. **No JavaScript injection** to update xterm.js theme dynamically
4. **No terminal-specific customization UI**

---

## Requirements

### Core Features (User-Requested)

✅ **Set terminal colors** - Background, foreground, cursor, selection, 16 ANSI colors
✅ **Set terminal font** - Font family selection (monospace fonts only)
✅ **Set font size** - Adjustable font size (8-24pt recommended)
✅ **Live preview** - See changes in real-time before saving
✅ **Save as new theme** - Create and name custom terminal themes
✅ **Set default theme** - Configure which theme new terminals use

### Additional Features (Best Practices)

✅ **Import/Export** - Share terminal themes as JSON files
✅ **Reset to defaults** - Revert to original theme
✅ **WCAG validation** - Check contrast ratios for readability
✅ **Apply to all terminals** - Update all open terminals at once vs. just current
✅ **Independent from app themes** - Terminal themes separate from application themes

### Why Terminal Themes Should Be Independent

- Users may want **dark app UI with light terminal** (or vice versa)
- Terminal colors are **very specific** (16 ANSI colors + cursor + selection)
- Font preferences **differ** (terminal needs monospace, app uses UI fonts)
- Separate storage allows **theme sharing** in community

---

## Architecture Overview

### Component Hierarchy

```
ViloxTermApp
├── TerminalThemeManager (NEW)
│   ├── Theme storage/loading
│   ├── Default theme tracking
│   └── JSON import/export
│
├── TerminalThemeDialog (NEW)
│   ├── Left Panel: Color/Font selectors
│   ├── Middle Panel: Visual editors
│   └── Right Panel: Live preview
│
└── TerminalWidget (MODIFIED)
    ├── _apply_theme() - JavaScript injection
    ├── set_terminal_theme() - Public API
    └── get_terminal_theme() - Export current config
```

### Design Principles

1. **Separation of Concerns**: Terminal themes independent from app themes
2. **Live Preview**: All changes preview in real-time before saving
3. **Non-Destructive**: Original themes preserved, custom themes saved separately
4. **Persistence**: Themes stored in user config directory
5. **Simplicity**: Focused UI for 18 color pickers + font settings (not 200 tokens)

---

## Component Specifications

### Component 1: TerminalThemeManager

**File:** `apps/viloxterm/src/viloxterm/terminal_theme_manager.py`

**Responsibilities:**
- Store custom terminal themes
- Load/save terminal themes to JSON
- Apply terminal themes via JavaScript injection to TerminalWidget
- Track default terminal theme preference
- Validate themes (WCAG contrast checking)

**Storage Location:**
```
~/.config/viloxterm/terminal_themes/
├── custom-dark.json
├── custom-light.json
├── monokai.json
└── config.json  # Stores default theme preference
```

**Theme JSON Format:**
```json
{
  "name": "My Custom Dark",
  "version": "1.0.0",
  "author": "User Name",
  "description": "Custom dark theme with purple accents",
  "terminal": {
    "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
    "fontSize": 14,
    "lineHeight": 1.2,
    "letterSpacing": 0,
    "cursorBlink": true,
    "cursorStyle": "block",
    "background": "#1e1e1e",
    "foreground": "#d4d4d4",
    "cursor": "#ffcc00",
    "cursorAccent": "#1e1e1e",
    "selectionBackground": "rgba(38, 79, 120, 0.3)",
    "black": "#000000",
    "red": "#cd3131",
    "green": "#0dbc79",
    "yellow": "#e5e510",
    "blue": "#2472c8",
    "magenta": "#bc3fbc",
    "cyan": "#11a8cd",
    "white": "#e5e5e5",
    "brightBlack": "#555753",
    "brightRed": "#f14c4c",
    "brightGreen": "#23d18b",
    "brightYellow": "#f5f543",
    "brightBlue": "#3b8eea",
    "brightMagenta": "#d670d6",
    "brightCyan": "#29b8db",
    "brightWhite": "#f5f5f5"
  }
}
```

**API:**
```python
class TerminalThemeManager:
    def __init__(self, config_dir: Path = None):
        """Initialize theme manager."""

    def get_default_theme(self) -> dict:
        """Get the default terminal theme."""

    def set_default_theme(self, theme_name: str) -> None:
        """Set the default theme for new terminals."""

    def save_theme(self, theme: dict, name: str) -> None:
        """Save custom theme to JSON file."""

    def load_theme(self, name: str) -> dict:
        """Load theme from JSON file."""

    def list_themes(self) -> list[str]:
        """List all available theme names."""

    def delete_theme(self, name: str) -> None:
        """Delete a custom theme."""

    def export_theme(self, name: str, path: Path) -> None:
        """Export theme to external JSON file."""

    def import_theme(self, path: Path) -> str:
        """Import theme from JSON file, returns theme name."""

    def validate_theme(self, theme: dict) -> list[str]:
        """Validate theme for WCAG compliance, returns warnings."""
```

---

### Component 2: TerminalThemeDialog

**File:** `apps/viloxterm/src/viloxterm/components/terminal_theme_dialog.py`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Terminal Theme Customization                               │
├─────────────────┬───────────────────┬───────────────────────┤
│ Color Tokens    │ Editors           │ Live Preview          │
│                 │                   │                       │
│ □ Background    │ ┌─────────────┐   │ ┌───────────────────┐ │
│ □ Foreground    │ │ Color:      │   │ │ user@host:~$      │ │
│ □ Cursor        │ │ [#1e1e1e] 🎨│   │ │ Sample text       │ │
│ □ Selection     │ └─────────────┘   │ │ \e[31mRed text    │ │
│                 │                   │ │ \e[32mGreen text  │ │
│ ANSI Colors     │ ┌─────────────┐   │ │ \e[34mBlue text   │ │
│ □ Black         │ │ Font:       │   │ │                   │ │
│ □ Red           │ │ [Consolas ▼]│   │ │ Cursor here█      │ │
│ □ Green         │ │             │   │ │                   │ │
│ □ Yellow        │ │ Size: 14 pt │   │ └───────────────────┘ │
│ □ Blue          │ │ [────●────] │   │                       │
│ □ Magenta       │ └─────────────┘   │ Contrast: ✅ AA       │
│ □ Cyan          │                   │           ✅ AAA      │
│ □ White         │                   │                       │
│ □ Bright Black  │                   │                       │
│ □ Bright Red    │                   │                       │
│ ... (8 more)    │                   │                       │
├─────────────────┴───────────────────┴───────────────────────┤
│ Theme: [My Custom Dark        ▼] [Save As...] [Set Default] │
│                                                               │
│       [Preview] [Apply to All] [Reset] [Cancel] [OK]         │
└─────────────────────────────────────────────────────────────┘
```

**Features:**

**Left Panel - Token Selection:**
- Tree/list of customizable properties
- Categories: Basic Colors, ANSI Colors, Fonts, Cursor
- Click to select property for editing

**Middle Panel - Visual Editors:**
- Color picker widget (reuse from theme system if possible)
- Font dropdown (filtered to monospace fonts)
- Font size slider (8-24pt range)
- Updates preview in real-time

**Right Panel - Live Preview:**
- Embedded mini xterm.js terminal (400x300px)
- Shows sample text demonstrating all colors
- Sample text includes:
  ```
  user@host:~$ echo "Testing colors"
  Normal text in foreground color
  \e[31mRed text \e[32mGreen text \e[34mBlue text
  \e[1;33mBright Yellow \e[1;35mBright Magenta
  Selected text highlighted
  Cursor blinks here█
  ```

**Bottom Controls:**
- **Theme dropdown**: Select from saved themes
- **Save As**: Save current config as new theme (prompts for name)
- **Set Default**: Make current theme the default for new terminals
- **Preview**: Apply to current terminal only (temporary)
- **Apply to All**: Apply to all open terminals (temporary)
- **Reset**: Revert to theme at dialog open
- **Cancel** / **OK**: Discard or save changes

**API:**
```python
class TerminalThemeDialog(QDialog):
    def __init__(self, parent=None, current_theme: dict = None):
        """Initialize dialog with optional current theme."""

    def get_theme(self) -> dict:
        """Get the configured theme."""

    def set_theme(self, theme: dict) -> None:
        """Set the theme being edited."""
```

---

### Component 3: TerminalWidget Modifications

**File:** `widgets/terminal_widget/src/vfwidgets_terminal/terminal.py`

**Changes:**

1. **Implement _apply_theme() method** (currently stub at line 1024):
```python
def _apply_theme(self, theme_config: dict) -> None:
    """Apply terminal theme by injecting JavaScript to xterm.js.

    Args:
        theme_config: Dictionary with terminal configuration
    """
    if not self.webview:
        logger.warning("Cannot apply theme - webview not initialized")
        return

    # Build JavaScript to update xterm.js configuration
    js_code = f"""
    if (typeof term !== 'undefined') {{
        term.options.fontFamily = '{theme_config.get("fontFamily", "monospace")}';
        term.options.fontSize = {theme_config.get("fontSize", 14)};
        term.options.lineHeight = {theme_config.get("lineHeight", 1.2)};
        term.options.letterSpacing = {theme_config.get("letterSpacing", 0)};
        term.options.cursorBlink = {str(theme_config.get("cursorBlink", True)).lower()};
        term.options.cursorStyle = '{theme_config.get("cursorStyle", "block")}';

        term.options.theme = {{
            background: '{theme_config.get("background", "#1e1e1e")}',
            foreground: '{theme_config.get("foreground", "#d4d4d4")}',
            cursor: '{theme_config.get("cursor", "#ffcc00")}',
            cursorAccent: '{theme_config.get("cursorAccent", "#1e1e1e")}',
            selectionBackground: '{theme_config.get("selectionBackground", "rgba(38,79,120,0.3)")}',
            black: '{theme_config.get("black", "#000000")}',
            red: '{theme_config.get("red", "#cd3131")}',
            green: '{theme_config.get("green", "#0dbc79")}',
            yellow: '{theme_config.get("yellow", "#e5e510")}',
            blue: '{theme_config.get("blue", "#2472c8")}',
            magenta: '{theme_config.get("magenta", "#bc3fbc")}',
            cyan: '{theme_config.get("cyan", "#11a8cd")}',
            white: '{theme_config.get("white", "#e5e5e5")}',
            brightBlack: '{theme_config.get("brightBlack", "#555753")}',
            brightRed: '{theme_config.get("brightRed", "#f14c4c")}',
            brightGreen: '{theme_config.get("brightGreen", "#23d18b")}',
            brightYellow: '{theme_config.get("brightYellow", "#f5f543")}',
            brightBlue: '{theme_config.get("brightBlue", "#3b8eea")}',
            brightMagenta: '{theme_config.get("brightMagenta", "#d670d6")}',
            brightCyan: '{theme_config.get("brightCyan", "#29b8db")}',
            brightWhite: '{theme_config.get("brightWhite", "#f5f5f5")}'
        }};

        console.log('Terminal theme applied');
    }} else {{
        console.error('Terminal not initialized');
    }}
    """

    self.webview.page().runJavaScript(js_code)
    logger.info(f"Applied terminal theme: {theme_config.get('name', 'custom')}")
```

2. **Add public API methods**:
```python
def set_terminal_theme(self, theme: dict) -> None:
    """Set terminal-specific theme.

    Args:
        theme: Terminal theme dictionary with colors, fonts, etc.
    """
    self._current_terminal_theme = theme
    self._apply_theme(theme)

def get_terminal_theme(self) -> dict:
    """Get current terminal theme configuration.

    Returns:
        Dictionary with current terminal theme settings
    """
    return self._current_terminal_theme.copy() if self._current_terminal_theme else {}
```

3. **Store current theme**:
```python
# Add to __init__:
self._current_terminal_theme: Optional[dict] = None
```

---

### Component 4: ViloxTermApp Integration

**File:** `apps/viloxterm/src/viloxterm/app.py`

**Changes:**

1. **Initialize TerminalThemeManager**:
```python
def __init__(self):
    # ... existing code ...

    # Initialize terminal theme manager
    self.terminal_theme_manager = TerminalThemeManager()
    self.current_terminal_theme = self.terminal_theme_manager.get_default_theme()

    logger.info(f"Using terminal theme: {self.current_terminal_theme.get('name', 'default')}")
```

2. **Add menu action** (in _setup_keybinding_manager):
```python
ActionDefinition(
    id="terminal.customize_theme",
    description="Customize Terminal Theme...",
    default_shortcut="Ctrl+Shift+,",
    category="Terminal",
    callback=self._on_customize_terminal_theme,
)
```

3. **Implement customize callback**:
```python
def _on_customize_terminal_theme(self) -> None:
    """Open terminal theme customization dialog."""
    from .components import TerminalThemeDialog

    dialog = TerminalThemeDialog(
        parent=self,
        current_theme=self.current_terminal_theme
    )

    if dialog.exec():
        new_theme = dialog.get_theme()
        self.current_terminal_theme = new_theme

        # Apply to all open terminals if requested
        if dialog.apply_to_all_requested:
            self.apply_terminal_theme_to_all(new_theme)

        logger.info(f"Terminal theme updated: {new_theme.get('name')}")
```

4. **Apply theme when creating terminals** (in _create_terminal):
```python
def _create_terminal(self, title: str) -> TerminalWidget:
    """Create a terminal widget with current theme.

    Args:
        title: Terminal title

    Returns:
        Configured TerminalWidget instance
    """
    terminal = TerminalWidget(
        server_url=f"http://localhost:{self.terminal_server.port}",
        auto_start=False,
        rows=24,
        cols=80,
        title=title,
    )

    # Apply terminal theme
    terminal.set_terminal_theme(self.current_terminal_theme)

    return terminal
```

5. **Apply to all terminals helper**:
```python
def apply_terminal_theme_to_all(self, theme: dict) -> None:
    """Apply terminal theme to all open terminals.

    Args:
        theme: Terminal theme to apply
    """
    count = 0
    for tab_idx in range(self.count()):
        multisplit = self.widget(tab_idx)
        if isinstance(multisplit, MultisplitWidget):
            for pane_id in multisplit.get_pane_ids():
                terminal = multisplit.get_pane_widget(pane_id)
                if isinstance(terminal, TerminalWidget):
                    terminal.set_terminal_theme(theme)
                    count += 1

    logger.info(f"Applied terminal theme to {count} terminals")
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Get basic theme application working

**Tasks:**
1. Create `TerminalThemeManager` class
   - Implement theme storage/loading
   - JSON serialization
   - Default theme tracking

2. Implement `TerminalWidget._apply_theme()`
   - JavaScript injection to xterm.js
   - Test theme changes work

3. Add `set_terminal_theme()` / `get_terminal_theme()` API

4. Integration test: Manually apply theme via Python code

**Success Criteria:**
- Can programmatically set terminal colors/fonts
- Changes visible in running terminal
- Theme persists across terminal creation

---

### Phase 2: Dialog UI (Week 2)

**Goal:** Build basic customization dialog

**Tasks:**
1. Create `TerminalThemeDialog` skeleton
   - Basic layout with 3 panels
   - QListWidget for token selection

2. Add color pickers for 18 color properties
   - Reuse ColorEditorWidget from theme system if compatible
   - Otherwise create simple QColorDialog wrapper

3. Add font selectors
   - Font family dropdown (monospace only)
   - Font size slider (8-24pt)

4. Wire up to TerminalThemeManager
   - Load/save themes
   - Apply to current terminal

**Success Criteria:**
- Dialog opens and shows all 18 color options
- Can select font and size
- Changes apply to current terminal
- Can save as named theme

---

### Phase 3: Live Preview (Week 3)

**Goal:** Add real-time preview panel

**Tasks:**
1. Embed mini xterm.js terminal in preview panel
   - 400x300px size
   - Same setup as main terminal but smaller

2. Generate sample text showing all features
   - ANSI colors demo
   - Cursor visibility
   - Selection highlight

3. Implement real-time updates
   - Debounced (300ms) to avoid lag
   - Updates as user changes colors

4. Add WCAG validation display
   - Show AA/AAA compliance badges
   - Highlight contrast issues

**Success Criteria:**
- Preview updates within 300ms of change
- All 16 ANSI colors visible in preview
- Validation shows readability status

---

### Phase 4: Persistence & Polish (Week 4)

**Goal:** Complete feature set

**Tasks:**
1. Implement "Set as Default" functionality
   - Save default theme preference
   - New terminals use default theme

2. Add "Apply to All Terminals" feature
   - Iterate all tabs/panes
   - Apply theme to each terminal

3. Implement import/export
   - Export theme to JSON file
   - Import theme from JSON file
   - Validate imported themes

4. Add "Reset" button
   - Revert to theme at dialog open
   - Clear unsaved changes

**Success Criteria:**
- Default theme persists across app restarts
- Can share themes via JSON files
- Reset works correctly
- All buttons functional

---

### Phase 5: Testing & Documentation

**Goal:** Production-ready quality

**Tasks:**
1. Unit tests
   - TerminalThemeManager methods
   - Theme validation
   - JSON import/export

2. Integration tests
   - Dialog workflow
   - Apply to all terminals
   - Theme persistence

3. User documentation
   - How to customize terminal themes
   - Theme sharing guide
   - Keyboard shortcuts

4. Example themes
   - Create 3-5 popular themes (Monokai, Solarized, etc.)
   - Include in distribution

**Success Criteria:**
- >80% test coverage on new code
- Documentation complete
- 5 example themes included
- No known bugs

---

## File Structure

```
apps/viloxterm/
├── docs/
│   ├── terminal-customization-PLAN.md        # This file
│   └── terminal-themes-USER_GUIDE.md         # NEW: User documentation
│
├── src/viloxterm/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── terminal_theme_dialog.py          # NEW: Main customization UI
│   │   ├── terminal_color_picker.py          # NEW: Color picker widget (optional)
│   │   ├── terminal_preview.py               # NEW: Live preview panel (optional)
│   │   ├── theme_dialog.py                   # EXISTING: App theme selector
│   │   └── menu_button.py                    # EXISTING
│   │
│   ├── terminal_theme_manager.py             # NEW: Theme storage/management
│   ├── app.py                                # MODIFIED: Add menu item + integration
│   └── providers.py                          # EXISTING
│
├── themes/                                   # NEW: Bundled terminal themes
│   ├── default-dark.json
│   ├── default-light.json
│   ├── monokai.json
│   ├── solarized-dark.json
│   └── solarized-light.json
│
└── tests/
    ├── test_terminal_theme_manager.py        # NEW: Theme manager tests
    └── test_terminal_theme_dialog.py         # NEW: Dialog tests

widgets/terminal_widget/
└── src/vfwidgets_terminal/
    └── terminal.py                           # MODIFIED: Implement _apply_theme()

~/.config/viloxterm/                          # User config directory
├── terminal_themes/                          # User custom themes
│   ├── my-theme-1.json
│   └── my-theme-2.json
└── config.json                               # App config with default theme
```

---

## API Design

### TerminalThemeManager

```python
from pathlib import Path
from typing import Optional

class TerminalThemeManager:
    """Manages terminal theme storage, loading, and application."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize theme manager.

        Args:
            config_dir: Directory for storing themes (default: ~/.config/viloxterm)
        """
        self.config_dir = config_dir or Path.home() / ".config" / "viloxterm"
        self.themes_dir = self.config_dir / "terminal_themes"
        self.themes_dir.mkdir(parents=True, exist_ok=True)

        # Load bundled themes
        self._load_bundled_themes()

    def get_default_theme(self) -> dict:
        """Get the default terminal theme."""

    def set_default_theme(self, theme_name: str) -> None:
        """Set the default theme for new terminals."""

    def save_theme(self, theme: dict, name: str) -> None:
        """Save custom theme to JSON file."""

    def load_theme(self, name: str) -> dict:
        """Load theme from JSON file."""

    def list_themes(self) -> list[str]:
        """List all available theme names."""

    def delete_theme(self, name: str) -> bool:
        """Delete a custom theme. Returns True if successful."""

    def export_theme(self, name: str, path: Path) -> None:
        """Export theme to external JSON file."""

    def import_theme(self, path: Path) -> str:
        """Import theme from JSON file. Returns theme name."""

    def validate_theme(self, theme: dict) -> list[str]:
        """Validate theme for WCAG compliance. Returns list of warnings."""
```

### TerminalWidget

```python
class TerminalWidget(ThemedWidget, QWidget):
    """Terminal widget with theme support."""

    def set_terminal_theme(self, theme: dict) -> None:
        """Set terminal-specific theme.

        Args:
            theme: Terminal theme dictionary with colors, fonts, etc.
        """

    def get_terminal_theme(self) -> dict:
        """Get current terminal theme configuration.

        Returns:
            Dictionary with current terminal theme settings
        """

    def _apply_theme(self, theme_config: dict) -> None:
        """Apply terminal theme by injecting JavaScript to xterm.js.

        Args:
            theme_config: Dictionary with terminal configuration
        """
```

### TerminalThemeDialog

```python
from PySide6.QtWidgets import QDialog

class TerminalThemeDialog(QDialog):
    """Dialog for customizing terminal themes."""

    def __init__(self, parent=None, current_theme: Optional[dict] = None):
        """Initialize dialog.

        Args:
            parent: Parent widget
            current_theme: Current theme to edit (optional)
        """

    def get_theme(self) -> dict:
        """Get the configured theme.

        Returns:
            Terminal theme dictionary
        """

    def set_theme(self, theme: dict) -> None:
        """Set the theme being edited.

        Args:
            theme: Terminal theme to load into editor
        """

    @property
    def apply_to_all_requested(self) -> bool:
        """Check if user clicked 'Apply to All' button."""
```

---

## User Workflow

### Workflow 1: Quick Theme Change

1. User clicks **Menu** → **Customize Terminal...**
2. Dialog opens with current terminal theme loaded
3. User clicks **Theme dropdown** → selects "Monokai"
4. Preview panel updates instantly
5. User clicks **OK**
6. Current terminal updates with new theme

**Time:** ~5 seconds

---

### Workflow 2: Create Custom Theme

1. User clicks **Menu** → **Customize Terminal...**
2. User clicks **Theme dropdown** → selects "Dark" as base
3. User clicks **Background** in left panel
4. Color picker opens, user selects darker blue (#0a0e27)
5. Preview updates instantly
6. User clicks **Foreground** → changes to light cyan (#e0ffff)
7. User clicks **ANSI Red** → changes to softer red (#ff6b6b)
8. Preview shows new colors in sample text
9. User clicks **Save As...** → names theme "My Dark Blue"
10. Theme saved to `~/.config/viloxterm/terminal_themes/my-dark-blue.json`
11. User clicks **Set Default** → new terminals will use this theme
12. User clicks **OK**

**Time:** ~2 minutes

---

### Workflow 3: Apply to All Terminals

1. User has 5 tabs open with different terminals
2. User opens **Customize Terminal...**
3. User selects "Light" theme
4. User clicks **Apply to All**
5. All 5 terminal tabs instantly switch to light theme
6. User clicks **OK** to confirm

**Time:** ~10 seconds

---

### Workflow 4: Share Theme with Team

1. User has created custom theme "Company Branded"
2. User opens **Customize Terminal...**
3. User selects "Company Branded" from dropdown
4. User clicks **Export** button (future feature)
5. Saves to `~/Downloads/company-branded.json`
6. User shares file with team
7. Teammates click **Import** → select file
8. Theme appears in their theme list

**Time:** ~30 seconds

---

## Technical Notes

### JavaScript Injection Strategy

Terminal themes are applied by injecting JavaScript into the QWebEngineView:

```javascript
// Update xterm.js configuration
term.options.fontFamily = 'Consolas, monospace';
term.options.fontSize = 14;
term.options.theme = {
    background: '#1e1e1e',
    foreground: '#d4d4d4',
    // ... all colors
};
```

**Why this approach:**
- ✅ No need to modify terminal.html
- ✅ Works with existing xterm.js setup
- ✅ Changes apply immediately
- ✅ No terminal restart needed

**Limitations:**
- Changes don't persist across page reload (fixed by storing theme and re-applying)
- Requires terminal to be fully loaded (check `window.terminal` exists)

---

### WCAG Contrast Validation

Validate foreground/background contrast ratios:

```python
def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Returns:
        Contrast ratio (1.0 to 21.0)
    """
    # Convert hex to RGB
    # Calculate relative luminance
    # Return ratio
    pass

def validate_theme_wcag(theme: dict) -> dict:
    """Validate theme meets WCAG standards.

    Returns:
        {
            "aa_pass": bool,  # 4.5:1 for normal text
            "aaa_pass": bool, # 7:1 for normal text
            "warnings": [...]
        }
    """
    fg = theme["foreground"]
    bg = theme["background"]
    ratio = calculate_contrast_ratio(fg, bg)

    return {
        "aa_pass": ratio >= 4.5,
        "aaa_pass": ratio >= 7.0,
        "ratio": ratio,
        "warnings": [] if ratio >= 4.5 else ["Low contrast - may be hard to read"]
    }
```

**AA Standard:** 4.5:1 contrast ratio (minimum)
**AAA Standard:** 7.0:1 contrast ratio (enhanced)

---

## Success Metrics

### Phase Completion

- ✅ Phase 1: Terminal theme application works programmatically
- ✅ Phase 2: Dialog UI complete with all 18 color pickers
- ✅ Phase 3: Live preview updates in real-time
- ✅ Phase 4: Save/load/import/export all functional
- ✅ Phase 5: Tests pass, documentation complete

### User Experience

- ⏱️ **Time to change theme:** <5 seconds
- ⏱️ **Time to create custom theme:** <2 minutes
- ⏱️ **Preview update latency:** <300ms
- 📊 **User satisfaction:** Intuitive, no confusion
- 🐛 **Bug count:** <3 known issues at release

---

## Future Enhancements (Post-MVP)

1. **Theme marketplace** - Share themes online
2. **Auto-detect system theme** - Sync with OS dark/light mode
3. **Per-pane themes** - Different colors per terminal pane
4. **Theme animations** - Smooth transitions between themes
5. **Color scheme generator** - AI-generated complementary colors
6. **Import from popular formats** - iTerm2, Windows Terminal, etc.

---

## Questions & Decisions

### Q1: Should terminal themes be completely independent or derive from app themes?

**Decision:** **Independent but with sync option**

- By default, terminal themes are separate
- Add checkbox: "Sync with application theme" (future feature)
- Most users want separate control (dark app, light terminal)

### Q2: How many bundled themes should we include?

**Decision:** **Start with 5 popular themes**

1. Default Dark (VS Code inspired)
2. Default Light (clean, high contrast)
3. Monokai (popular developer theme)
4. Solarized Dark (widely loved)
5. Solarized Light (for outdoor coding)

Users can add more via import.

### Q3: Should we allow partial theme customization?

**Decision:** **Yes, themes can extend base themes**

- Theme JSON can have `"extends": "default-dark"`
- Only override specific colors
- Makes creating variants easier

### Q4: What happens to terminals when theme changes?

**Decision:** **User chooses behavior**

- **Default:** Apply to current terminal only
- **Option:** "Apply to All Terminals" button
- **Option:** "Set as Default" (new terminals only)

This gives users full control.

---

## Risks & Mitigations

### Risk 1: JavaScript injection fails silently

**Mitigation:**
- Add error handling in JavaScript
- Log to console for debugging
- Show error dialog if theme application fails

### Risk 2: Theme files become corrupted

**Mitigation:**
- Validate JSON on load
- Keep backup of last working theme
- Provide "Reset to Default" escape hatch

### Risk 3: Performance issues with many terminals

**Mitigation:**
- Debounce preview updates (300ms)
- Cache theme JavaScript code
- Apply themes on-demand, not proactively

### Risk 4: Users create unreadable themes (low contrast)

**Mitigation:**
- Show WCAG warnings prominently
- Block saving if contrast < 3:1 (optional)
- Provide "Fix Contrast" auto-adjustment button

---

## Appendix: Example Theme Files

### default-dark.json
```json
{
  "name": "Default Dark",
  "version": "1.0.0",
  "author": "ViloxTerm",
  "description": "Default dark theme inspired by VS Code",
  "terminal": {
    "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
    "fontSize": 14,
    "lineHeight": 1.2,
    "letterSpacing": 0,
    "cursorBlink": true,
    "cursorStyle": "block",
    "background": "#1e1e1e",
    "foreground": "#d4d4d4",
    "cursor": "#ffcc00",
    "cursorAccent": "#1e1e1e",
    "selectionBackground": "rgba(38, 79, 120, 0.3)",
    "black": "#000000",
    "red": "#cd3131",
    "green": "#0dbc79",
    "yellow": "#e5e510",
    "blue": "#2472c8",
    "magenta": "#bc3fbc",
    "cyan": "#11a8cd",
    "white": "#e5e5e5",
    "brightBlack": "#555753",
    "brightRed": "#f14c4c",
    "brightGreen": "#23d18b",
    "brightYellow": "#f5f543",
    "brightBlue": "#3b8eea",
    "brightMagenta": "#d670d6",
    "brightCyan": "#29b8db",
    "brightWhite": "#f5f5f5"
  }
}
```

### monokai.json
```json
{
  "name": "Monokai",
  "version": "1.0.0",
  "author": "ViloxTerm",
  "description": "Monokai color scheme",
  "extends": "default-dark",
  "terminal": {
    "background": "#272822",
    "foreground": "#f8f8f2",
    "cursor": "#f8f8f0",
    "cursorAccent": "#272822",
    "selectionBackground": "rgba(73, 72, 62, 0.5)",
    "black": "#272822",
    "red": "#f92672",
    "green": "#a6e22e",
    "yellow": "#f4bf75",
    "blue": "#66d9ef",
    "magenta": "#ae81ff",
    "cyan": "#a1efe4",
    "white": "#f8f8f2",
    "brightBlack": "#75715e",
    "brightRed": "#f92672",
    "brightGreen": "#a6e22e",
    "brightYellow": "#f4bf75",
    "brightBlue": "#66d9ef",
    "brightMagenta": "#ae81ff",
    "brightCyan": "#a1efe4",
    "brightWhite": "#f9f8f5"
  }
}
```

---

**End of Plan**
