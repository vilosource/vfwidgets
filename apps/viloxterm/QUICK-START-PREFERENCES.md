# ViloxTerm Preferences - Quick Start Guide

## Open Preferences

```bash
# Method 1: Keyboard shortcut (fastest)
Ctrl+,

# Method 2: Menu button
Click ☰ → Preferences

# Method 3: From command line
python -m src.viloxterm
# Then press Ctrl+,
```

## 4 Tabs, 54 Settings

### 📋 General (11 settings)
- Tabs on startup
- Default shell
- Starting directory
- Window behavior
- Session management

### 🎨 Appearance (13 settings)
- **Window opacity** ← Try this first!
- Application theme
- UI customization
- Focus indicators

### 🖥️ Terminal (11 settings)
- Scrollback buffer
- Cursor style
- Scrolling behavior
- Bell style

### ⚙️ Advanced (10 settings)
- Hardware acceleration
- Performance tuning
- Experimental features

## Best Demo

1. Press `Ctrl+,`
2. Go to **Appearance** tab
3. Move "Window opacity" slider to **50%**
4. Click **Apply**
5. **Watch the magic!** ✨

ViloxTerm becomes transparent in real-time!

## Where Settings Are Saved

```
~/.config/viloxterm/
├── app_preferences.json      (General, Appearance, Advanced)
└── terminal_preferences.json (Terminal settings)
```

## All Changes Persist!

Close ViloxTerm and restart - all your settings are remembered.

## That's It!

Press `Ctrl+,` and start customizing! 🚀
