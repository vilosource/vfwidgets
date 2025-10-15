# Testing Terminal Font Settings via Preferences GUI

## Overview

You can now change terminal font settings (size, family, line height, letter spacing) through the Preferences dialog! These settings apply to **all terminals** in ViloxTerm.

## Quick Test (2 minutes)

```bash
cd /home/kuja/GitHub/vfwidgets/apps/viloxterm
python -m src.viloxterm
```

### Test Terminal Font Size

1. **Open Preferences**: Press `Ctrl+,`
2. **Go to Terminal tab**
3. **Find "Font" section** (should be the second group)
4. **Change "Font size"**: Set to **20 px** (default is 14 px)
5. **Click "Apply"**
6. **Look at your terminal** - text should get bigger immediately!
7. **Try different sizes**: 10 px (small), 24 px (large), 16 px (medium)

### Test Line Height

1. Still in **Terminal tab → Font section**
2. **Change "Line height"**: Set to **1.5** (default is 1.2)
3. **Click "Apply"**
4. **Look at your terminal** - lines should have more spacing!
5. **Try**: 1.0 (tight), 2.0 (very spacious), 1.2 (default)

### Test Font Family

1. Still in **Terminal tab → Font section**
2. **Change "Font family"**: Enter **"JetBrains Mono"** or **"Courier New"**
3. **Click "Apply"**
4. **Look at your terminal** - font style changes!
5. **Try different fonts**:
   - `"JetBrains Mono, monospace"`
   - `"Fira Code, Consolas, monospace"`
   - `"Monaco, Courier New, monospace"`

### Test Letter Spacing

1. Still in **Terminal tab → Font section**
2. **Change "Letter spacing"**: Set to **2 px** (default is 0)
3. **Click "Apply"**
4. **Look at your terminal** - letters are spaced wider!
5. **Try**: -1 (tighter), 5 (very wide), 0 (default)

## What You'll See

### Font Settings in Preferences Dialog

```
┌─────────────────────────────────────┐
│ Terminal Tab                        │
├─────────────────────────────────────┤
│ General                             │
│   Scrollback buffer: [1000] lines   │
│   Tab width: [4] spaces             │
│   Terminal type: [xterm-256color]   │
│                                     │
│ Font                     ← NEW!     │
│   Font family: [________________]   │
│   Font size: [14] px                │
│   Line height: [1.2]                │
│   Letter spacing: [0] px            │
│                                     │
│ Cursor                              │
│   ...                               │
└─────────────────────────────────────┘
```

### Expected Behavior

**When you click "Apply"**:
- Changes apply to **all open terminals** immediately
- No need to close and reopen terminals
- Settings save to `~/.config/viloxterm/terminal_preferences.json`

**When you restart ViloxTerm**:
- Font settings are remembered
- New terminals use the saved font settings

## Complete Test Scenarios

### Scenario 1: Make Text Bigger

**Goal**: Increase terminal font size for better readability

1. Open Preferences (`Ctrl+,`)
2. Terminal tab → Font section
3. Change "Font size" to **18 px**
4. Change "Line height" to **1.4**
5. Click "Apply"
6. Terminal text is now bigger and more readable!
7. Click "OK" to save

**Result**: All terminals now use 18px font with 1.4 line height. Settings persist across restarts.

### Scenario 2: Use Custom Font

**Goal**: Switch to JetBrains Mono with ligatures

1. Open Preferences (`Ctrl+,`)
2. Terminal tab → Font section
3. Font family: `"JetBrains Mono, Fira Code, monospace"`
4. Font size: **14 px**
5. Letter spacing: **0 px**
6. Click "Apply"
7. Terminal now uses JetBrains Mono!

**Result**: All terminals use JetBrains Mono. If font has ligatures (like arrows `->` or `=>`), they'll render as single glyphs.

### Scenario 3: Compact Terminal Layout

**Goal**: Fit more lines on screen

1. Open Preferences (`Ctrl+,`)
2. Terminal tab → Font section
3. Font size: **12 px** (smaller)
4. Line height: **1.0** (tighter)
5. Letter spacing: **-1 px** (tighter)
6. Click "Apply"
7. Terminal is now more compact!

**Result**: More lines visible, good for logs and debugging.

### Scenario 4: Spacious Code Editor Style

**Goal**: Comfortable reading for long coding sessions

1. Open Preferences (`Ctrl+,`)
2. Terminal tab → Font section
3. Font family: `"Fira Code, Consolas, monospace"`
4. Font size: **16 px**
5. Line height: **1.6**
6. Letter spacing: **1 px**
7. Click "Apply"
8. Terminal feels like a code editor!

**Result**: Easy-to-read layout with breathing room.

## Settings Details

### Font Family

**Format**: CSS font-family string (comma-separated list)

**Examples**:
- `"JetBrains Mono, monospace"`
- `"Fira Code, Consolas, Monaco, monospace"`
- `"Monaco, Courier New, monospace"`
- Leave **empty** to use system default

**Fallback**: If first font not available, tries next in list.

### Font Size

**Range**: 6-72 pixels
**Default**: 14 px
**Recommended**: 12-18 px for most displays

**Guidelines**:
- **Small** (10-12 px): Compact, fits more text
- **Medium** (13-16 px): Comfortable reading
- **Large** (18-24 px): Presentations, accessibility

### Line Height

**Range**: 0.5-3.0 (multiplier)
**Default**: 1.2
**Recommended**: 1.0-1.6

**Meaning**: Line height = font size × line height value

**Examples**:
- **1.0**: Tight spacing (no extra space)
- **1.2**: Default (20% extra space)
- **1.5**: Comfortable (50% extra space)
- **2.0**: Very spacious (double spacing)

### Letter Spacing

**Range**: -10 to +20 pixels
**Default**: 0 px
**Recommended**: -2 to +3 px

**Meaning**:
- **Negative**: Letters closer together (tighter)
- **0**: Normal spacing
- **Positive**: Letters farther apart (wider)

**Use cases**:
- **-1**: Slightly more compact
- **0**: Normal (recommended)
- **1-2**: Slight breathing room
- **5+**: Extreme spacing (accessibility)

## Where Settings Are Saved

**File**: `~/.config/viloxterm/terminal_preferences.json`

**Example**:
```json
{
  "scrollback": 1000,
  "tabStopWidth": 4,
  "termType": "xterm-256color",
  "fontFamily": "JetBrains Mono, monospace",
  "fontSize": 16,
  "lineHeight": 1.4,
  "letterSpacing": 0,
  "cursorStyle": "block",
  "cursorBlink": true,
  "scrollSensitivity": 1,
  "fastScrollSensitivity": 5,
  "fastScrollModifier": "shift",
  "bellStyle": "none",
  "rightClickSelectsWord": false,
  "convertEol": false
}
```

## How It Works Internally

### Signal Flow

```
User changes font setting in Preferences Dialog
  ↓
Terminal tab save_preferences() collects values
  ↓
PreferencesDialog saves to terminal_preferences.json
  ↓
PreferencesDialog emits terminal_preferences_applied signal
  ↓
ViloxTermApp._apply_terminal_preferences_to_all()
  ↓
Iterates all tabs and panes
  ↓
For each TerminalWidget:
  widget.set_terminal_config(config)
    ↓
  Terminal applies font settings to xterm.js
    ↓
  JavaScript executes:
    term.setOption('fontFamily', 'JetBrains Mono')
    term.setOption('fontSize', 16)
    term.setOption('lineHeight', 1.4)
    term.setOption('letterSpacing', 0)
      ↓
    xterm.js re-renders terminal with new font
      ↓
    USER SEES UPDATED TERMINAL! ✨
```

### Key Methods

**Terminal widget** (`terminal.py`):
- `_get_font_with_fallback()` - Reads font from config with fallback
- `set_theme()` - Applies font properties to xterm.js individually
- Font properties: fontFamily, fontSize, lineHeight, letterSpacing

**Preferences** (`terminal_prefs_tab.py`):
- `_create_font_group()` - Creates font UI controls
- `load_preferences()` - Loads font settings from config
- `save_preferences()` - Saves font settings to config

## Troubleshooting

### Problem: Font doesn't change

**Possible causes**:
1. Font family name misspelled
2. Font not installed on system
3. Settings not applied (forgot to click Apply)

**Solution**:
- Use common fonts: `"Consolas, Monaco, monospace"`
- Click "Apply" button
- Check console for errors

### Problem: Font too small/large

**Solution**:
- Use font size range 12-18 px for normal use
- Adjust line height proportionally (1.2-1.5)

### Problem: Terminal looks cramped

**Solution**:
- Increase line height to 1.4 or 1.5
- Add letter spacing (1-2 px)
- Increase font size slightly

### Problem: Settings don't persist

**Solution**:
- Click "OK" (not just "Apply")
- Check `~/.config/viloxterm/terminal_preferences.json` exists
- Check file has write permissions

## Summary

**Total Font Settings**: 4
- Font family (text field)
- Font size (6-72 px)
- Line height (0.5-3.0)
- Letter spacing (-10 to +20 px)

**How to Access**: `Ctrl+,` → Terminal tab → Font section

**Application**: Immediate (all terminals update when you click Apply)

**Persistence**: Saved to `~/.config/viloxterm/terminal_preferences.json`

**Best Quick Test**: Change font size to 20 px and click Apply!

---

**Enjoy customizing your terminal font!** ✨
