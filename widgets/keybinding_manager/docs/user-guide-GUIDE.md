# KeybindingManager User Guide

**Document Type**: GUIDE
**Audience**: End Users
**Purpose**: How to customize keyboard shortcuts

---

## Table of Contents

1. [Introduction](#introduction)
2. [Finding Your Keybindings File](#finding-your-keybindings-file)
3. [Editing Keybindings](#editing-keybindings)
4. [Shortcut Syntax](#shortcut-syntax)
5. [Common Customizations](#common-customizations)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

Applications built with KeybindingManager allow you to customize keyboard shortcuts by editing a simple text file. No special software is needed - just a text editor!

### What You Can Do

- **Change** any keyboard shortcut
- **Unbind** actions you don't use
- **Share** your customizations with others
- **Backup** your shortcuts

---

## Finding Your Keybindings File

### File Location

The keybindings file is stored in a standard configuration directory:

**Linux/macOS**:
```
~/.config/<appname>/keybindings.json
```

**Windows**:
```
C:\Users\<username>\AppData\Local\<appname>\keybindings.json
```

### Example Locations

- ViloxTerm: `~/.config/viloxterm/keybindings.json`
- Text Editor: `~/.config/texteditor/keybindings.json`

### Finding the File

**Method 1: Check Application Help/About**
Most applications display the file path in:
- Help → Keyboard Shortcuts
- About dialog
- Preferences

**Method 2: Use Find Command (Linux/macOS)**
```bash
find ~/.config -name "keybindings.json"
```

**Method 3: Run Application Once**
The file is created automatically after:
1. Running the application
2. Making any shortcut change
3. Closing the application

---

## Editing Keybindings

### File Format

The keybindings file is JSON (JavaScript Object Notation):

```json
{
  "file.save": "Ctrl+S",
  "file.open": "Ctrl+O",
  "edit.copy": "Ctrl+C",
  "edit.paste": "Ctrl+V",
  "app.quit": "Ctrl+Q"
}
```

### Editing Steps

1. **Close the application** (important!)
2. **Open the file** in any text editor:
   - VS Code
   - Notepad (Windows)
   - TextEdit (macOS)
   - nano/vim (Linux)
3. **Edit shortcuts** (see examples below)
4. **Save the file**
5. **Restart the application**

**⚠️ Important**: Always close the application before editing! Changes made while the app is running will be overwritten.

### Basic Editing Examples

**Change a shortcut:**
```json
{
  "file.save": "Ctrl+Alt+S"
}
```
Changes Save from `Ctrl+S` to `Ctrl+Alt+S`

**Unbind an action:**
```json
{
  "app.quit": null
}
```
Removes the Quit shortcut (menu/button still works)

**Add modifier keys:**
```json
{
  "edit.copy": "Ctrl+Shift+C"
}
```
Adds Shift to the Copy shortcut

---

## Shortcut Syntax

### Modifier Keys

| Modifier | Symbol | Example |
|----------|--------|---------|
| Control | `Ctrl` | `Ctrl+S` |
| Shift | `Shift` | `Shift+F3` |
| Alt | `Alt` | `Alt+F4` |
| Meta/Win/Cmd | `Meta` | `Meta+Tab` |

### Special Keys

| Key | Syntax |
|-----|--------|
| Function keys | `F1`, `F2`, ..., `F12` |
| Arrow keys | `Up`, `Down`, `Left`, `Right` |
| Page keys | `PageUp`, `PageDown`, `Home`, `End` |
| Edit keys | `Insert`, `Delete`, `Backspace` |
| Special | `Esc`, `Tab`, `Return`, `Space` |

### Combining Keys

Combine modifiers with `+`:
```
Ctrl+S              # Control + S
Ctrl+Shift+T        # Control + Shift + T
Alt+F4              # Alt + F4
Meta+Shift+Q        # Meta/Win/Cmd + Shift + Q
```

### Valid Examples

```json
{
  "file.new": "Ctrl+N",
  "file.open": "Ctrl+O",
  "edit.find": "Ctrl+F",
  "edit.replace": "Ctrl+H",
  "view.fullscreen": "F11",
  "help.shortcuts": "F1",
  "window.close": "Ctrl+W"
}
```

### Platform Differences

**macOS**: Use `Meta` for Command key:
```json
{
  "file.save": "Meta+S",      # Cmd+S
  "file.quit": "Meta+Q"       # Cmd+Q
}
```

**Linux/Windows**: Use `Ctrl`:
```json
{
  "file.save": "Ctrl+S",
  "file.quit": "Ctrl+Q"
}
```

---

## Common Customizations

### Emacs-Style Shortcuts

```json
{
  "file.save": "Ctrl+X, Ctrl+S",
  "file.open": "Ctrl+X, Ctrl+F",
  "edit.copy": "Meta+W",
  "edit.paste": "Ctrl+Y"
}
```

### Vim-Style Navigation

```json
{
  "cursor.up": "Ctrl+K",
  "cursor.down": "Ctrl+J",
  "cursor.left": "Ctrl+H",
  "cursor.right": "Ctrl+L"
}
```

### Gaming-Style (WASD)

```json
{
  "move.forward": "W",
  "move.left": "A",
  "move.back": "S",
  "move.right": "D",
  "action.primary": "Space"
}
```

### Ergonomic (Avoiding Pinky Strain)

```json
{
  "file.save": "Ctrl+K, S",
  "file.open": "Ctrl+K, O",
  "edit.find": "Ctrl+K, F"
}
```

---

## Troubleshooting

### Shortcut Not Working

**Problem**: Changed shortcut but it doesn't work

**Solutions**:
1. ✅ Check the file syntax is valid JSON (commas, quotes)
2. ✅ Ensure application was closed before editing
3. ✅ Restart the application after saving
4. ✅ Check for typos in shortcut syntax (`Crtl` → `Ctrl`)
5. ✅ Verify action ID matches application's actions

### Shortcut Conflicts

**Problem**: Shortcut triggers multiple actions

**Solutions**:
- Remove duplicate shortcuts in the file
- Check system-wide shortcuts (OS may capture the key)
- Use different modifier combinations

### File Not Loading

**Problem**: Changes not applied after restart

**Solutions**:
1. Check file location is correct
2. Verify JSON syntax with a validator (jsonlint.com)
3. Look for application error messages in console
4. Reset to defaults and try again

### Invalid JSON Syntax

**Common Mistakes**:

❌ **Missing comma:**
```json
{
  "file.save": "Ctrl+S"
  "file.open": "Ctrl+O"
}
```

✅ **Correct:**
```json
{
  "file.save": "Ctrl+S",
  "file.open": "Ctrl+O"
}
```

❌ **Trailing comma:**
```json
{
  "file.save": "Ctrl+S",
}
```

✅ **Correct:**
```json
{
  "file.save": "Ctrl+S"
}
```

❌ **Wrong quotes:**
```json
{
  'file.save': 'Ctrl+S'
}
```

✅ **Correct (use double quotes):**
```json
{
  "file.save": "Ctrl+S"
}
```

### Resetting to Defaults

**Option 1: Delete the file**
```bash
rm ~/.config/myapp/keybindings.json
```
Application will recreate with defaults on next run.

**Option 2: In-application reset**
Most applications provide: Help → Reset Keyboard Shortcuts

**Option 3: Empty the file**
```json
{}
```
All actions will use their default shortcuts.

---

## Tips & Best Practices

### 1. Backup Before Editing

```bash
cp ~/.config/myapp/keybindings.json ~/.config/myapp/keybindings.backup.json
```

### 2. Use JSON Validator

Before saving, validate at: https://jsonlint.com

### 3. Document Your Changes

Add comments by using a separate file:
```
keybindings.json       # Your customizations
keybindings.notes.txt  # Why you made changes
```

### 4. Share Configurations

Share your keybindings file with team members:
```bash
# Export
cp ~/.config/myapp/keybindings.json ~/Documents/my-shortcuts.json

# Import (on another machine)
cp ~/Documents/my-shortcuts.json ~/.config/myapp/keybindings.json
```

### 5. Start Small

Don't change everything at once:
1. Change 2-3 most-used shortcuts
2. Use for a week
3. Adjust if needed
4. Repeat

---

## Example Configurations

### Complete Configuration Example

```json
{
  "file.new": "Ctrl+N",
  "file.open": "Ctrl+O",
  "file.save": "Ctrl+S",
  "file.saveas": "Ctrl+Shift+S",
  "file.close": "Ctrl+W",
  "file.quit": "Ctrl+Q",

  "edit.undo": "Ctrl+Z",
  "edit.redo": "Ctrl+Shift+Z",
  "edit.cut": "Ctrl+X",
  "edit.copy": "Ctrl+C",
  "edit.paste": "Ctrl+V",
  "edit.selectall": "Ctrl+A",

  "search.find": "Ctrl+F",
  "search.replace": "Ctrl+H",
  "search.findnext": "F3",
  "search.findprev": "Shift+F3",

  "view.fullscreen": "F11",
  "view.zoom.in": "Ctrl++",
  "view.zoom.out": "Ctrl+-",
  "view.zoom.reset": "Ctrl+0",

  "help.shortcuts": "F1",
  "help.about": null
}
```

### Minimal Configuration (Unbind Unused)

```json
{
  "file.print": null,
  "file.export": null,
  "help.tutorial": null
}
```
Only unbound actions are listed; everything else uses defaults.

---

## Getting Help

If you encounter issues:

1. **Check application documentation**: README or help menu
2. **Application logs**: Look for error messages
3. **Community forums**: Search for similar issues
4. **Report bugs**: Include your keybindings.json file

---

## Summary

✅ **Edit** `~/.config/<appname>/keybindings.json`
✅ **Close** application before editing
✅ **Use** valid JSON syntax
✅ **Test** changes after restart
✅ **Backup** before major changes

Happy customizing! 🎹
