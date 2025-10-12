# VFTheme Studio - User Guide (MVP)

**Version:** 0.1.0-dev (Phase 2 Complete)
**Date:** 2025-10-12
**Status:** MVP Production-Ready

---

## Quick Start: Create Your First Theme in 10 Minutes

This guide walks you through creating a custom theme using VFTheme Studio MVP.

---

## Table of Contents

1. [Launching the Application](#1-launching-the-application)
2. [Understanding the Interface](#2-understanding-the-interface)
3. [Creating a New Theme](#3-creating-a-new-theme)
4. [Editing Color Tokens](#4-editing-color-tokens)
5. [Using the Color Picker](#5-using-the-color-picker)
6. [Real-Time Preview](#6-real-time-preview)
7. [Undo/Redo](#7-undoredo)
8. [Saving Your Theme](#8-saving-your-theme)
9. [Loading Existing Themes](#9-loading-existing-themes)
10. [Tips & Best Practices](#10-tips--best-practices)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Launching the Application

### From Command Line
```bash
# If installed via pip
vftheme-studio

# Or via Python module
python -m theme_studio
```

### From Source (Development)
```bash
cd /path/to/vfwidgets/apps/theme-studio
python -m theme_studio
```

**Expected Result:** A window appears with three panels:
- **Left:** Token Browser (tree view of all tokens)
- **Center:** Preview Canvas (sample widgets)
- **Right:** Inspector Panel (token details)

---

## 2. Understanding the Interface

### The Three-Panel Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  Theme  View  Tools  Window  Help                    │
├──────────┬────────────────────────────────┬─────────────────────┤
│          │                                │                     │
│  Token   │        Preview Canvas          │     Inspector       │
│  Browser │                                │     Panel           │
│          │  [Sample Widgets Preview]      │                     │
│  📁 Base │                                │  Token: (none)      │
│  📁 Button│  Buttons  Inputs  etc.        │                     │
│  📁 Editor│                                │  [Token details]    │
│  📁 Input│                                │                     │
│          │                                │  [Edit] button      │
│          │                                │                     │
│          │  Plugin: Generic Widgets ▼     │                     │
│          │                                │                     │
└──────────┴────────────────────────────────┴─────────────────────┘
```

### Key UI Elements

**Token Browser (Left Panel):**
- 🔍 **Search Box** at top - Filter tokens by name
- **Tree View** - Tokens organized by category:
  - Base (core colors)
  - Button
  - Editor
  - Input
  - List
  - Menu
  - etc.
- **Click any token** to see details in Inspector

**Preview Canvas (Center Panel):**
- **Plugin Selector** dropdown at top
- **Sample Widgets** showing current theme
- Updates **in real-time** as you edit tokens

**Inspector Panel (Right Panel):**
- **Token Name** - Currently selected token
- **Token Value** - Current color value
- **Category** - Token category
- **Description** - What this token controls
- **Color Swatch** - Visual preview (for color tokens)
- **Color Details** - RGB, HSL, Hex values
- **Edit Button** - Click to edit the token

---

## 3. Creating a New Theme

### Step-by-Step: New Theme from Scratch

**Step 1:** Launch VFTheme Studio
- Application starts with default "Untitled" theme

**Step 2:** Start Fresh (Optional)
- Go to **File → New Theme**
- If current theme has changes, you'll be asked to save
- Click **Discard** (we'll save later)

**Step 3:** Verify Clean State
- Window title shows: `Untitled - VFTheme Studio`
- Status bar shows: `Theme: Untitled (Modified: No)`
- Token count: `Defined: 0 / Total: 197`

**You now have a blank canvas to create your theme!**

---

## 4. Editing Color Tokens

Let's create a simple blue theme by editing key tokens.

### Example: Editing Button Background Color

**Step 1: Find the Token**
1. In **Token Browser** (left panel):
   - Expand **📁 Button** category
   - Click on **button.background**

**Step 2: Inspect Current Value**
- **Inspector Panel** (right) shows:
  - Name: `button.background`
  - Value: `(using default)` (empty = uses built-in default)
  - Category: `button`
  - Description: "Button background color"

**Step 3: Enter Edit Mode**
1. Click the **Edit** button in Inspector
2. UI changes:
   - Label becomes editable text field
   - **Save** and **Cancel** buttons appear
   - 🎨 **Color Picker** button appears (if color token)

**Step 4: Enter a Color Value**
Type any of these formats:
- **Hex:** `#2196f3` (6-digit hex)
- **Short Hex:** `#21f` (3-digit hex)
- **Hex with Alpha:** `#2196f3ff` (8-digit with transparency)
- **Color Name:** `blue`, `red`, `green`, etc.
- **RGB:** `rgb(33, 150, 243)`
- **RGBA:** `rgba(33, 150, 243, 255)`

**Example:** Type `#2196f3` (Material Blue)

**Step 5: Validate**
- As you type, validation runs in real-time
- ✅ **Valid:** Save button enabled, no error message
- ❌ **Invalid:** Save button disabled, error message appears:
  - `"Invalid hex color: '#12'. Use #RGB, #RRGGBB, or #RRGGBBAA format."`

**Step 6: Save Changes**
1. Click **Save** button
2. Inspector exits edit mode
3. **Preview Canvas updates instantly!**
4. Status bar shows: `Updated button.background`
5. Window title shows: `Untitled* - VFTheme Studio` (asterisk = modified)

**You just edited your first token!** 🎉

---

## 5. Using the Color Picker

For visual color selection instead of typing hex codes.

### Step-by-Step: Visual Color Selection

**Step 1: Enter Edit Mode**
1. Select a color token (e.g., `button.foreground`)
2. Click **Edit** button
3. Notice the **🎨 button** appears

**Step 2: Open Color Picker**
1. Click the **🎨** button
2. Qt Color Dialog opens with:
   - **Color wheel** or grid
   - **RGB sliders**
   - **HSV sliders**
   - **Alpha channel** slider
   - **Hex input** field
   - **OK** and **Cancel** buttons

**Step 3: Pick Your Color**
- **Option 1:** Click on color wheel/grid
- **Option 2:** Adjust RGB sliders (0-255)
- **Option 3:** Adjust HSV sliders
- **Option 4:** Type hex directly in dialog
- **Option 5:** Adjust alpha (transparency) if needed

**Example:** Select a white color:
- Move to top-left of color wheel
- Or set RGB: R=255, G=255, B=255

**Step 4: Apply Color**
1. Click **OK** in color dialog
2. Color value updates in edit field: `#ffffff`
3. Click **Save** in Inspector

**Step 5: See Results**
- Preview Canvas updates instantly
- Button text turns white (if you edited `button.foreground`)

**Tip:** The color picker remembers your last used color!

---

## 6. Real-Time Preview

Watch your changes come to life instantly.

### What Updates in Preview?

The **Preview Canvas** shows sample widgets affected by your tokens:

**Generic Widgets Plugin** includes:
- **Buttons:** Normal, Primary, Disabled
- **Text Inputs:** Line edit, Text edit
- **Combo Boxes**
- **Spin Boxes**
- **Check Boxes**
- **Radio Buttons**
- **Sliders**
- **Progress Bars**
- **Tabs**

### Seeing Your Changes

**Example Workflow:**
1. Edit `button.background` → `#2196f3` → Save
   - **Preview:** All buttons turn blue instantly!

2. Edit `button.foreground` → `#ffffff` → Save
   - **Preview:** Button text turns white instantly!

3. Edit `button.hover` → `#1976d2` → Save
   - **Preview:** Hover state would update (currently static preview)

4. Edit `input.background` → `#f5f5f5` → Save
   - **Preview:** Text inputs change to light gray!

**No manual refresh needed - changes apply instantly!** ⚡

---

## 7. Undo/Redo

Made a mistake? No problem!

### Keyboard Shortcuts

- **Undo:** `Ctrl+Z` (Windows/Linux) or `Cmd+Z` (Mac)
- **Redo:** `Ctrl+Shift+Z` or `Ctrl+Y`

### Menu Options

**Edit Menu:**
- **Edit → Undo** (Ctrl+Z)
- **Edit → Redo** (Ctrl+Shift+Z)

**Menu items are smart:**
- Grayed out when no undo/redo available
- Enabled when actions are available

### Example Undo Workflow

**Scenario:** You accidentally made a button red instead of blue

1. Edit `button.background` → `#ff0000` → Save
   - Preview shows red buttons (oops!)

2. Press **Ctrl+Z** (Undo)
   - Token reverts to previous value
   - Preview updates back to blue
   - Status bar: `Undo`

3. Edit `button.background` → `#2196f3` → Save
   - Correct blue color applied

4. Press **Ctrl+Z** if you change your mind
   - Or **Ctrl+Shift+Z** to redo

**Undo history persists until you:**
- Close the application
- Create a new theme
- Load a different theme

---

## 8. Saving Your Theme

### Save vs Save As

**Save (Ctrl+S):**
- If theme has a file path: Overwrites existing file
- If theme is new ("Untitled"): Opens "Save As" dialog

**Save As (Ctrl+Shift+S):**
- Always opens dialog to choose new location/name
- Use this to:
  - Save new themes
  - Create variants of existing themes
  - Save to different location

### Step-by-Step: Save Your Theme

**Step 1: Choose Save Action**
- **File → Save** (or `Ctrl+S`)
- Or **File → Save As** (or `Ctrl+Shift+S`)

**Step 2: Choose Location**
Save dialog appears:
1. Navigate to desired folder
2. Enter filename: `my-blue-theme.json`
3. Click **Save**

**Expected format:** `.json` extension is automatic

**Step 3: Verify Saved**
- Window title: `my-blue-theme.json - VFTheme Studio` (no asterisk)
- Status bar: `Saved: my-blue-theme.json`
- Modified indicator: `Modified: No`

### Theme File Format

Your theme is saved as JSON:

```json
{
  "name": "My Blue Theme",
  "version": "1.0.0",
  "type": "dark",
  "colors": {
    "button.background": "#2196f3",
    "button.foreground": "#ffffff",
    "button.hover": "#1976d2",
    "input.background": "#f5f5f5",
    "editor.background": "#1e1e1e"
  },
  "metadata": {
    "created_with": "VFTheme Studio",
    "author": "",
    "description": ""
  }
}
```

**Only defined tokens are saved** - undefined tokens use defaults.

---

## 9. Loading Existing Themes

Open and edit themes you or others created.

### Step-by-Step: Open a Theme

**Step 1: Open Dialog**
- **File → Open Theme** (or `Ctrl+O`)
- If current theme is modified, you'll be prompted to save

**Step 2: Choose File**
1. Navigate to theme file location
2. Select a `.json` theme file
3. Click **Open**

**Step 3: Theme Loads**
- All tokens from file populate the inspector
- Preview Canvas updates to show the theme
- Window title: `theme-name.json - VFTheme Studio`
- Token count updates: `Defined: X / Total: 197`

**Step 4: Explore the Theme**
- Browse tokens in Token Browser
- Click tokens to see their values
- Preview Canvas shows theme applied
- Edit tokens as needed
- Save changes with `Ctrl+S`

### Built-in Themes

VFTheme Studio includes several built-in themes:
- **dark** - Default dark theme (VS Code Dark+)
- **light** - Light theme
- **nord** - Nord color scheme
- **dracula** - Dracula theme
- **monokai** - Monokai theme
- **solarized-dark** / **solarized-light** - Solarized themes

**To try built-in themes:**
They're part of the theme system, but currently you'd need to find their JSON files in the vfwidgets-theme package.

---

## 10. Tips & Best Practices

### Theme Creation Tips

**Start with Key Tokens:**
Focus on these high-impact tokens first:
1. `editor.background` - Main background color
2. `editor.foreground` - Main text color
3. `button.background` - Button color
4. `button.foreground` - Button text
5. `input.background` - Input fields
6. `input.foreground` - Input text

**Use Search:**
- Type in search box to filter tokens
- Example: Search "background" to see all background colors
- Search "button" to see all button-related tokens

**Color Consistency:**
- Use the same base colors throughout
- Example: Blue buttons, blue highlights, blue selection
- Use color picker to ensure exact color matches

**Test Contrast:**
- Make sure text is readable on backgrounds
- Light text on dark backgrounds (or vice versa)
- Currently no automatic validation (coming in Phase 4)

**Save Often:**
- Press `Ctrl+S` frequently
- Theme Studio has undo, but saving prevents loss

**Use Descriptive Names:**
- `my-blue-corporate-theme.json`
- `dark-purple-accent.json`
- `light-minimal-theme.json`

### Keyboard Shortcuts Reference

| Action | Shortcut |
|--------|----------|
| **New Theme** | `Ctrl+N` |
| **Open Theme** | `Ctrl+O` |
| **Save** | `Ctrl+S` |
| **Save As** | `Ctrl+Shift+S` |
| **Undo** | `Ctrl+Z` |
| **Redo** | `Ctrl+Shift+Z` or `Ctrl+Y` |
| **Find Token** | `Ctrl+F` (planned) |
| **Fullscreen** | `F11` |
| **Quit** | `Ctrl+Q` |

### Common Workflows

**Workflow 1: Create Corporate Theme**
```
1. File → New Theme
2. Edit editor.background → Company background color
3. Edit editor.foreground → Company text color
4. Edit button.background → Company accent color
5. Edit button.foreground → White
6. Edit input.background → Slightly lighter/darker than editor
7. Save → company-theme.json
```

**Workflow 2: Dark → Light Conversion**
```
1. File → Open → dark-theme.json
2. File → Save As → light-theme.json
3. Edit editor.background → #ffffff (white)
4. Edit editor.foreground → #000000 (black)
5. Edit all "background" tokens → light colors
6. Edit all "foreground" tokens → dark colors
7. Save
```

**Workflow 3: Accent Color Change**
```
1. File → Open → existing-theme.json
2. Search: "button"
3. Edit button.background → New accent color
4. Edit button.hover → Darker/lighter variant
5. Edit button.active → Even darker/lighter
6. File → Save As → theme-blue-accent.json
```

---

## 11. Troubleshooting

### Common Issues

**Issue: Color Picker Button Doesn't Appear**
- **Cause:** Not in edit mode
- **Solution:** Click "Edit" button first, then 🎨 appears

**Issue: Save Button is Disabled**
- **Cause:** Invalid color value entered
- **Solution:** Check validation error message below input field
- **Fix:** Enter valid hex (#123456) or color name (blue)

**Issue: Preview Doesn't Update**
- **Cause:** Need to save changes first
- **Solution:** Click "Save" button in Inspector after editing
- **Expected:** Preview updates immediately after save

**Issue: Changes Lost When Switching Tokens**
- **Cause:** Forgot to click Save
- **Solution:** Always click Save before selecting another token
- **Or:** Click Cancel to discard and start over

**Issue: "Unsaved Changes" Dialog Appears**
- **Cause:** Theme has unsaved edits
- **Options:**
  - **Save:** Save changes before continuing
  - **Discard:** Lose changes and continue
  - **Cancel:** Go back and keep editing

**Issue: Application Crashes**
- **Rare:** Should not happen in MVP
- **Report:** File an issue at https://github.com/viloforge/vfwidgets/issues
- **Workaround:** Restart application, theme should auto-save

### Validation Errors

**"Invalid hex color: '#12'. Use #RGB, #RRGGBB, or #RRGGBBAA format."**
- Your hex color has wrong length
- Valid: `#abc`, `#aabbcc`, `#aabbccdd`
- Invalid: `#ab`, `#abcde`

**"Invalid hex color: '#gggggg'. Check that all characters are valid hex digits."**
- Your hex contains non-hex characters
- Valid characters: 0-9, a-f, A-F
- Example: `#gggggg` has 'g' (invalid)

**"Invalid color: 'bleu'. Use hex (#RRGGBB), rgb(r,g,b), or color name."**
- Color name not recognized
- Valid names: red, blue, green, white, black, etc.
- Check spelling: "bleu" vs "blue"

### Getting Help

**Documentation:**
- This guide: `docs/USER-GUIDE-MVP.md`
- Known issues: `KNOWN-ISSUES.md`
- Technical docs: `docs/SPECIFICATION.md`
- Phase completion: `PHASE2-COMPLETE.md`

**Support:**
- GitHub Issues: https://github.com/viloforge/vfwidgets/issues
- Search existing issues first
- Include: OS, Python version, error messages

**Known Issues:**
- ⚠️ Segfault on exit (harmless, doesn't affect functionality)
- See `KNOWN-ISSUES.md` for full list

**Known Limitations (MVP):**
- No font editing yet (Phase 3+)
- No bulk editing (Phase 3+)
- No templates (Phase 3+)
- No accessibility validation (Phase 4+)
- No export formats besides JSON (Phase 4+)

---

## Complete Example: Creating a "Ocean Blue" Theme

Let's create a complete theme from start to finish.

### Step 1: Create New Theme
```
File → New Theme
```

### Step 2: Set Editor Colors (Background)
```
1. Token Browser → Expand "Editor" → Click "editor.background"
2. Inspector → Click "Edit"
3. Type: #0d1117 (dark ocean blue)
4. Click "Save"
→ Preview background becomes dark blue
```

### Step 3: Set Editor Text Color (Foreground)
```
1. Click "editor.foreground" in Token Browser
2. Inspector → Click "Edit"
3. Type: #e6edf3 (light blue-white)
4. Click "Save"
→ Preview text becomes light
```

### Step 4: Set Button Colors
```
1. Click "button.background"
2. Edit → Type: #1f6feb (bright blue)
3. Save → Preview buttons turn bright blue

4. Click "button.foreground"
5. Edit → Type: #ffffff (white)
6. Save → Button text turns white

7. Click "button.hover"
8. Edit → Type: #388bfd (lighter blue)
9. Save → Hover state defined
```

### Step 5: Set Input Colors
```
1. Click "input.background"
2. Edit → Type: #161b22 (slightly lighter than editor)
3. Save

4. Click "input.foreground"
5. Edit → Type: #e6edf3 (same as editor text)
6. Save

→ Input fields now ocean-themed!
```

### Step 6: Set Selection Colors
```
1. Click "selection.background"
2. Edit → Click 🎨 color picker
3. Choose medium blue: #1f6feb with 40% opacity
4. OK → Save

→ Selected text highlighted in blue
```

### Step 7: Save Theme
```
File → Save As → ocean-blue.json
→ Status: "Saved: ocean-blue.json"
```

### Step 8: Test Undo
```
1. Edit "button.background" → Type: #ff0000 (red)
2. Save → Buttons turn red (oops!)
3. Press Ctrl+Z → Buttons back to blue ✓
```

### Step 9: Verify Theme File
```bash
# Look at your saved theme
cat ocean-blue.json
```

```json
{
  "name": "Ocean Blue",
  "version": "1.0.0",
  "type": "dark",
  "colors": {
    "editor.background": "#0d1117",
    "editor.foreground": "#e6edf3",
    "button.background": "#1f6feb",
    "button.foreground": "#ffffff",
    "button.hover": "#388bfd",
    "input.background": "#161b22",
    "input.foreground": "#e6edf3",
    "selection.background": "#1f6feb66"
  },
  "metadata": {
    "created_with": "VFTheme Studio"
  }
}
```

**Congratulations! You created a complete theme!** 🎉

---

## Using Your Theme in Applications

### Apply Theme to VFWidgets App

```python
# In your application code
from vfwidgets_theme import ThemedApplication

app = ThemedApplication(sys.argv)

# Load your custom theme
app.set_theme("/path/to/ocean-blue.json")

# Or set as default theme
app.set_theme("ocean-blue")  # If installed in theme system
```

### Share Your Theme

**Option 1: Direct File Sharing**
- Send `.json` file to others
- They can load it with "File → Open"

**Option 2: Theme Repository** (Future)
- Submit to VFWidgets theme gallery
- Others can browse and download
- Coming in Phase 5+

---

## Next Steps

Now that you've mastered the MVP basics:

**Experiment:**
- Create themes for different moods (professional, playful, minimal)
- Try different color schemes (monochrome, complementary, analogous)
- Edit more token categories (list, menu, tabs)

**Learn More:**
- Explore all 197 tokens
- Understand token categories
- Plan for Phase 3 features (fonts, templates)

**Give Feedback:**
- Report issues: https://github.com/viloforge/vfwidgets/issues
- Suggest features
- Share your themes!

---

## Summary

**You learned:**
- ✅ How to create a new theme from scratch
- ✅ How to edit color tokens visually
- ✅ How to use the color picker
- ✅ How to see real-time preview updates
- ✅ How to undo/redo changes
- ✅ How to save and load themes
- ✅ Best practices for theme creation

**You can now:**
- Create custom themes for your VFWidgets applications
- Modify existing themes
- Share themes with others
- Build consistent visual experiences

**Ready to create beautiful themes!** 🎨✨

---

*VFTheme Studio MVP User Guide - Phase 2 Complete*
*Last Updated: 2025-10-12*
