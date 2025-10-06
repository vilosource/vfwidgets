# ViloxTerm Keyboard Shortcuts Specification

**Status**: Living Document
**Last Updated**: 2025-10-04

This document tracks all keyboard shortcuts in ViloxTerm, both implemented and planned.

---

## Legend

- ✅ **Implemented** - Working in current version
- 🔧 **Planned** - Designed but not yet implemented
- 💡 **Proposed** - Idea for future consideration

---

## Tab Management

| Action | Shortcut | Status | Category | Notes |
|--------|----------|--------|----------|-------|
| New Tab | `Ctrl+Shift+T` | ✅ Implemented | Tab | Standard across terminals/browsers |
| Close Tab | `Ctrl+Shift+W` | ✅ Implemented | Tab | Matches VSCode/Chrome |
| Next Tab | `Ctrl+PgDn` | ✅ Implemented | Tab | VSCode standard, wraps around |
| Previous Tab | `Ctrl+PgUp` | ✅ Implemented | Tab | VSCode standard, wraps around |
| Jump to Tab 1 | `Alt+1` | ✅ Implemented | Tab | Quick access to first tab |
| Jump to Tab 2 | `Alt+2` | ✅ Implemented | Tab | Quick access to second tab |
| Jump to Tab 3 | `Alt+3` | ✅ Implemented | Tab | Quick access to third tab |
| Jump to Tab 4 | `Alt+4` | ✅ Implemented | Tab | Quick access to fourth tab |
| Jump to Tab 5 | `Alt+5` | ✅ Implemented | Tab | Quick access to fifth tab |
| Jump to Tab 6 | `Alt+6` | ✅ Implemented | Tab | Quick access to sixth tab |
| Jump to Tab 7 | `Alt+7` | ✅ Implemented | Tab | Quick access to seventh tab |
| Jump to Tab 8 | `Alt+8` | ✅ Implemented | Tab | Quick access to eighth tab |
| Jump to Tab 9 | `Alt+9` | ✅ Implemented | Tab | Quick access to ninth tab |

---

## Pane Management

| Action | Shortcut | Status | Category | Notes |
|--------|----------|--------|----------|-------|
| Split Horizontal | `Ctrl+Shift+H` | ✅ Implemented | Pane | Creates vertical divider (side-by-side panes) |
| Split Vertical | `Ctrl+Shift+V` | ✅ Implemented | Pane | Creates horizontal divider (stacked panes) |
| Close Pane | `Ctrl+W` | ✅ Implemented | Pane | Closes focused pane (closes tab if last pane) |
| Navigate Left | 💡 Proposed | Pane | Vim-like navigation between panes |
| Navigate Right | 💡 Proposed | Pane | Vim-like navigation between panes |
| Navigate Up | 💡 Proposed | Pane | Vim-like navigation between panes |
| Navigate Down | 💡 Proposed | Pane | Vim-like navigation between panes |

---

## Application

| Action | Shortcut | Status | Category | Notes |
|--------|----------|--------|----------|-------|
| Quit Application | `Ctrl+Q` | 💡 Proposed | App | Standard quit shortcut |
| Settings/Preferences | `Ctrl+,` | 💡 Proposed | App | VSCode standard |

---

## Theme & Appearance

| Action | Shortcut | Status | Category | Notes |
|--------|----------|--------|----------|-------|
| Theme Menu | Via Menu Button | ✅ Implemented | Theme | Click menu button in window controls |
| Toggle Theme | 💡 Proposed | Theme | Quick dark/light toggle |

---

## Terminal Operations

| Action | Shortcut | Status | Category | Notes |
|--------|----------|--------|----------|-------|
| Copy | `Ctrl+Shift+C` | ✅ Implemented | Terminal | Handled by TerminalWidget (xterm.js) |
| Paste | `Ctrl+Shift+V` | ✅ Implemented | Terminal | Handled by TerminalWidget (xterm.js) |
| Clear Terminal | `Ctrl+L` | ✅ Implemented | Terminal | Handled by TerminalWidget (xterm.js) |
| Search | `Ctrl+Shift+F` | ✅ Implemented | Terminal | Handled by TerminalWidget (xterm.js) |

---

## Shortcut Design Principles

### 1. Industry Standard Compliance
- **Terminal Emulators**: Follow Gnome Terminal, Windows Terminal, iTerm2 conventions
- **IDEs**: Match VSCode shortcuts where applicable
- **Browsers**: Match Chrome tab shortcuts for familiarity

### 2. Avoid Conflicts
- Don't override essential terminal shortcuts (Ctrl+C, Ctrl+D, etc.)
- Use `Shift` modifier for app-level actions vs terminal actions
- Example: `Ctrl+W` closes pane, `Ctrl+Shift+W` closes tab

### 3. Muscle Memory
- Prioritize shortcuts users already know from other tools
- Maintain consistency within the app (similar actions use similar patterns)

### 4. Accessibility
- All actions should be accessible via keyboard
- Shortcuts should be displayed in menus/tooltips
- Support customization via KeybindingManager

---

## Implementation Status

### Current Version (v1.1)
- ✅ 15 shortcuts implemented (3 pane, 12 tab)
- ✅ KeybindingManager integration with JSON persistence
- ✅ User-customizable shortcuts via `~/.config/viloxterm/keybindings.json`
- ✅ Menu integration (shortcuts appear in context menu)
- ✅ Tab navigation (new, next, prev, jump 1-9)

### Future Enhancements
- 💡 Vim-like pane navigation
- 💡 Application-level shortcuts
- 💡 Theme toggle
- 💡 Search in all panes
- 💡 Zoom in/out (font size)

---

## Customization

Users can customize shortcuts by editing:
```
~/.config/viloxterm/keybindings.json
```

Example:
```json
{
  "pane.split_horizontal": "Ctrl+Shift+H",
  "pane.split_vertical": "Ctrl+Shift+V",
  "pane.close": "Ctrl+W",
  "tab.close": "Ctrl+Shift+W"
}
```

After editing, restart ViloxTerm for changes to take effect.

---

## Cross-Reference

- **ChromeTabbedWindow**: Provides tab bar and window controls
- **MultisplitWidget**: Provides pane splitting and navigation
- **TerminalWidget**: Provides terminal-specific shortcuts (copy/paste/search)
- **KeybindingManager**: Manages shortcut registration and persistence

---

## Conflict Resolution

### Current Conflicts to Resolve

1. **Ctrl+Shift+V**
   - Current: Split Vertical (pane)
   - Standard: Paste in terminals
   - **Resolution**: Terminal paste handled by xterm.js layer, app-level Ctrl+Shift+V for split is acceptable

2. **Ctrl+W**
   - Current: Close Pane
   - Alternative: Close Tab (more common in browsers/IDEs)
   - **Resolution**: Keep Ctrl+W for pane, use Ctrl+Shift+W for tab

3. **Ctrl+PgDn (Fixed)**
   - Issue: QWebEngineView (terminal) was capturing Ctrl+PgDn before app-level shortcut
   - **Resolution**: Added event filter to ViloxTermApp that intercepts keyboard events
   - Implementation: `eventFilter()` method checks shortcuts and triggers actions before propagation
   - All shortcuts now work consistently even when terminal has focus

No conflicts detected with current implementation.

---

## References

- [VSCode Keyboard Shortcuts](https://code.visualstudio.com/docs/configure/keybindings)
- [Gnome Terminal Shortcuts](https://help.gnome.org/users/gnome-terminal/stable/adv-keyboard-shortcuts.html)
- [Windows Terminal Actions](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions)
- [Chrome Keyboard Shortcuts](https://support.google.com/chrome/answer/157179)
