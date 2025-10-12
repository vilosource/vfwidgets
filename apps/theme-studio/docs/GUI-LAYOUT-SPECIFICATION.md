# VFTheme Studio - GUI Layout Specification

**Version:** 0.1.0-dev
**Status:** Design Phase
**Last Updated:** October 2025

---

## Table of Contents

1. [Overview](#1-overview)
2. [Application Window Structure](#2-application-window-structure)
3. [Menu Bar Specification](#3-menu-bar-specification)
4. [Toolbar Specification](#4-toolbar-specification)
5. [Left Panel: Token Browser](#5-left-panel-token-browser)
6. [Center Panel: Preview Canvas](#6-center-panel-preview-canvas)
7. [Right Panel: Inspector](#7-right-panel-inspector)
8. [Status Bar Specification](#8-status-bar-specification)
9. [Dialogs and Modal Windows](#9-dialogs-and-modal-windows)
10. [Responsive Behavior](#10-responsive-behavior)
11. [Keyboard Shortcuts](#11-keyboard-shortcuts)
12. [Accessibility Features](#12-accessibility-features)

---

## 1. Overview

### 1.1 Design Philosophy

VFTheme Studio follows a **three-panel workspace layout** inspired by professional creative tools:
- **Left**: Navigation and browsing (Token Browser)
- **Center**: Primary work area (Preview Canvas)
- **Right**: Properties and details (Inspector)

This layout maximizes:
- **Visual hierarchy**: Most important content in center
- **Workflow efficiency**: Related actions grouped together
- **Screen real estate**: Resizable panels adapt to user needs
- **Familiarity**: Similar to Qt Designer, VS Code, Figma

### 1.2 Base Technology

- **Framework**: PySide6 6.9+
- **Base Window**: `ViloCodeWindow` (VS Code-style layout from vfwidgets-vilocode-window)
- **Theme Integration**: `ThemedApplication` and `ThemedWidget` mixins
- **Layout Manager**: `QSplitter` for resizable panels

---

## 2. Application Window Structure

### 2.1 Complete Layout Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ VFTheme Studio                                                    [_] [□] [X]    │  ← Title Bar
├─────────────────────────────────────────────────────────────────────────────────┤
│ File  Edit  Theme  View  Tools  Window  Help                                    │  ← Menu Bar
├─────────────────────────────────────────────────────────────────────────────────┤
│ [New] [Open] [Save] │ [Undo] [Redo] │ [Validate] [Export] │ Zoom: [100%] [▼]  │  ← Toolbar
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────┬──────────────────────────────────────┬───────────────────┐ │
│  │                │                                      │                   │ │
│  │ TOKEN BROWSER  │        PREVIEW CANVAS                │    INSPECTOR      │ │
│  │                │                                      │                   │ │
│  │  (25% width)   │         (50% width)                  │    (25% width)    │ │  ← Main Content
│  │   Resizable    │          Resizable                   │     Resizable     │ │
│  │                │                                      │                   │ │
│  │  [See §5]      │         [See §6]                     │     [See §7]      │ │
│  │                │                                      │                   │ │
│  └────────────────┴──────────────────────────────────────┴───────────────────┘ │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ⓘ Theme: my-custom-theme.json (modified) │ Tokens: 45/197 defined │ Ready      │  ← Status Bar
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Window Properties

```python
class ThemeStudioWindow(ViloCodeWindow, ThemedWidget):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle("VFTheme Studio")
        self.setMinimumSize(1200, 800)  # Minimum usable size
        self.resize(1600, 1000)         # Default size

        # Window icon
        self.setWindowIcon(QIcon(":/icons/theme-studio.png"))
```

**Default Window Size**: 1600x1000 pixels
**Minimum Window Size**: 1200x800 pixels
**Default Panel Ratio**: 25% | 50% | 25% (adjustable)

### 2.3 Layout Hierarchy

```
ThemeStudioWindow (QMainWindow)
├── MenuBar (QMenuBar)
├── Toolbar (QToolBar)
├── CentralWidget (QWidget)
│   └── MainSplitter (QSplitter - Horizontal)
│       ├── TokenBrowserPanel (QWidget) - 25%
│       ├── PreviewCanvasPanel (QWidget) - 50%
│       └── InspectorPanel (QWidget) - 25%
└── StatusBar (QStatusBar)
```

---

## 3. Menu Bar Specification

### 3.1 Complete Menu Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  Theme  View  Tools  Window  Help                    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 File Menu

```
File
├── New Theme                    Ctrl+N
├── New from Template...         Ctrl+Shift+N
├── ──────────────────
├── Open Theme...                Ctrl+O
├── Open Recent                  →
│   ├── my-theme.json
│   ├── dark-custom.json
│   ├── ──────────────
│   └── Clear Recent Files
├── ──────────────────
├── Save                         Ctrl+S
├── Save As...                   Ctrl+Shift+S
├── Save All                     Ctrl+Alt+S
├── ──────────────────
├── Import                       →
│   ├── From VS Code Theme...
│   ├── From CSS Variables...
│   ├── From Qt Stylesheet...
│   └── From Image Palette...
├── Export                       →
│   ├── As VFWidgets JSON...     Ctrl+E
│   ├── As VS Code Theme...
│   ├── As CSS Variables...
│   ├── As Qt Stylesheet...
│   ├── As Python Dict...
│   └── Export Preview Image...  Ctrl+Shift+E
├── ──────────────────
├── Theme Properties...          Ctrl+I
├── ──────────────────
├── Close Theme                  Ctrl+W
├── Exit                         Ctrl+Q
```

### 3.3 Edit Menu

```
Edit
├── Undo                         Ctrl+Z
├── Redo                         Ctrl+Shift+Z (or Ctrl+Y)
├── ──────────────────
├── Copy Token Value             Ctrl+C
├── Paste Token Value            Ctrl+V
├── Reset Token to Default       Ctrl+R
├── ──────────────────
├── Find Token...                Ctrl+F
├── Find Next                    F3
├── Find Previous                Shift+F3
├── ──────────────────
├── Select All Tokens            Ctrl+A
├── Select Modified Tokens       Ctrl+Shift+M
├── Select Tokens with Issues    Ctrl+Shift+I
├── ──────────────────
├── Preferences...               Ctrl+,
```

### 3.4 Theme Menu

```
Theme
├── New from Template...         Ctrl+Shift+N
├── Clone Current Theme...
├── ──────────────────
├── Rename Theme...
├── Edit Metadata...             Ctrl+I
├── ──────────────────
├── Validate Accessibility       F7
├── Generate Validation Report...
├── Auto-Fix Issues...
├── ──────────────────
├── Compare with Another Theme...
├── Show Theme Diff...
```

### 3.5 View Menu

```
View
├── Zoom In                      Ctrl++
├── Zoom Out                     Ctrl+-
├── Reset Zoom                   Ctrl+0
├── Zoom to Fit                  Ctrl+Shift+F
├── ──────────────────
├── Show Token Browser           Ctrl+1
├── Show Preview Canvas          Ctrl+2
├── Show Inspector               Ctrl+3
├── ──────────────────
├── Show Widget Library          Ctrl+L
├── Show State Simulator         Ctrl+Shift+S
├── Show Grid                    Ctrl+G
├── ──────────────────
├── Fullscreen                   F11
├── Reset Layout                 Ctrl+Shift+R
```

### 3.6 Tools Menu

```
Tools
├── Palette Extractor...         Ctrl+Shift+P
├── Color Harmonizer...          Ctrl+H
├── Bulk Edit Tokens...          Ctrl+B
├── ──────────────────
├── Compare Themes...            Ctrl+D
├── Theme Diff Viewer...
├── ──────────────────
├── Colorblind Simulation        →
│   ├── Normal Vision            ✓
│   ├── Protanopia (Red-Blind)
│   ├── Deuteranopia (Green-Blind)
│   └── Tritanopia (Blue-Blind)
├── ──────────────────
├── Export Preview Card...
├── Generate Documentation...
```

### 3.7 Window Menu

```
Window
├── Minimize                     Ctrl+M
├── Zoom (macOS)
├── ──────────────────
├── Reset Panel Sizes
├── Reset Layout                 Ctrl+Shift+R
├── ──────────────────
├── Bring All to Front
```

### 3.8 Help Menu

```
Help
├── Documentation                F1
├── Keyboard Shortcuts           Ctrl+/
├── Tutorial Videos...
├── ──────────────────
├── Report Issue...
├── View Changelog...
├── Check for Updates...
├── ──────────────────
├── About VFTheme Studio...
```

---

## 4. Toolbar Specification

### 4.1 Toolbar Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ [New] [Open] [Save] │ [Undo] [Redo] │ [Validate] [Export] │ Zoom: [100%] [▼]  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Toolbar Groups

**Group 1: File Operations**
```
[New]  - New theme (Ctrl+N)
[Open] - Open theme (Ctrl+O)
[Save] - Save theme (Ctrl+S)
```
- Icons: Standard file icons (new document, folder, floppy disk)
- Tooltips: Show full action name + shortcut

**Group 2: Edit Operations**
```
[Undo] - Undo last change (Ctrl+Z)
[Redo] - Redo change (Ctrl+Shift+Z)
```
- Icons: Curved arrows (left for undo, right for redo)
- Tooltips: Show action description (e.g., "Undo: Set button.background")
- Disabled state: Grayed out when undo/redo stack empty

**Group 3: Theme Operations**
```
[Validate] - Validate accessibility (F7)
[Export]   - Export theme (Ctrl+E)
```
- Icons: Checkmark for validate, export/share icon for export
- Tooltips: Show validation status or export format

**Group 4: View Controls**
```
Zoom: [100%] [▼]
```
- Combo box with preset zoom levels: 25%, 50%, 75%, 100%, 125%, 150%, 200%, 400%
- Editable: User can type custom percentage
- Shows current zoom level of preview canvas

### 4.3 Toolbar Implementation

```python
class ThemeStudioToolbar(QToolBar):
    """Main application toolbar."""

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        # Toolbar properties
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(24, 24))

        # Group 1: File
        self.new_action = self.addAction(QIcon(":/icons/new.svg"), "New")
        self.open_action = self.addAction(QIcon(":/icons/open.svg"), "Open")
        self.save_action = self.addAction(QIcon(":/icons/save.svg"), "Save")

        self.addSeparator()

        # Group 2: Edit
        self.undo_action = self.addAction(QIcon(":/icons/undo.svg"), "Undo")
        self.redo_action = self.addAction(QIcon(":/icons/redo.svg"), "Redo")

        self.addSeparator()

        # Group 3: Theme
        self.validate_action = self.addAction(QIcon(":/icons/check.svg"), "Validate")
        self.export_action = self.addAction(QIcon(":/icons/export.svg"), "Export")

        self.addSeparator()

        # Group 4: Zoom
        zoom_label = QLabel("Zoom:")
        self.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%",
                                  "150%", "200%", "400%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setEditable(True)
        self.addWidget(self.zoom_combo)
```

---

## 5. Left Panel: Token Browser

### 5.1 Panel Layout

```
┌────────────────┐
│ TOKEN BROWSER  │
├────────────────┤
│ [🔍 Search...] │  ← Search/filter bar
├────────────────┤
│                │
│ ▼ colors       │  ← Category (expanded)
│   ● foreground │  ← Token (color preview dot)
│   ● background │     Click to select/edit
│   ● primary    │
│   ○ secondary  │  ← Unmodified (empty dot)
│                │
│ ▼ button       │  ← Category (expanded)
│   ● background │
│   ⚠ hover...   │  ← Has validation issue (warning)
│   ● border     │
│                │
│ ▶ input        │  ← Category (collapsed)
│                │
│ ▶ list         │
│ ▶ editor       │
│ ▶ sidebar      │
│ ▶ panel        │
│ ▶ tab          │
│ ▶ activityBar  │
│ ▶ statusBar    │
│ ▶ titleBar     │
│ ▶ menu         │
│ ▶ scrollbar    │
│ ▶ terminal     │
│                │
├────────────────┤
│ Filter Options │
├────────────────┤
│ [All      ▼]   │  ← Filter dropdown
│ ☑ Modified     │  ← Show only modified
│ ☐ Issues Only  │  ← Show only with issues
├────────────────┤
│ 45/197 tokens  │  ← Token count
└────────────────┘
```

### 5.2 Search Bar

**Features**:
- Instant search (filters as you type)
- Searches token names and descriptions
- Case-insensitive
- Clear button (X) to reset search
- Keyboard focus: Ctrl+F

**Implementation**:
```python
class TokenSearchBar(QLineEdit):
    search_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setPlaceholderText("🔍 Search tokens...")
        self.setClearButtonEnabled(True)
        self.textChanged.connect(self.search_changed)
```

### 5.3 Token Tree View

**Visual Indicators**:
- **Color Preview**: Colored dot (●) showing current token value
- **Modified Indicator**: Filled dot (●) vs empty dot (○)
- **Validation Issues**:
  - ⚠ Warning icon (yellow) - WCAG AA fail
  - ✗ Error icon (red) - WCAG minimum fail
- **Font Tokens**: 'Aa' icon instead of color dot

**Interaction**:
- **Single Click**: Select token (shows in inspector)
- **Double Click**: Open color picker / font selector
- **Right Click**: Context menu (Copy, Reset, etc.)
- **Drag**: Drag token value to another token

**Tree Structure**:
```python
class TokenTreeView(QTreeView):
    """Hierarchical token browser."""

    token_selected = Signal(str)  # token name

    def __init__(self):
        super().__init__()

        # View properties
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.setAlternatingRowColors(True)

        # Enable drag-drop
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
```

### 5.4 Filter Options

**Filter Dropdown Values**:
- **All**: Show all 197 tokens
- **Defined**: Show only tokens with custom values
- **Undefined**: Show only tokens using defaults
- **Modified**: Show tokens changed in this session
- **Issues**: Show tokens with validation issues

**Checkboxes**:
- **Modified**: Toggle to show/hide modified tokens
- **Issues Only**: Toggle to show/hide tokens with issues

### 5.5 Context Menu

**Right-click on token**:
```
Token: button.background
├── Edit Value...               Enter
├── Copy Value                  Ctrl+C
├── Paste Value                 Ctrl+V
├── ──────────────────
├── Reset to Default            Ctrl+R
├── Set from Color Picker...    Ctrl+Shift+C
├── ──────────────────
├── Show in Preview             Ctrl+Shift+V
├── Find Usage...
├── ──────────────────
├── Copy Token Name
```

---

## 6. Center Panel: Preview Canvas

### 6.1 Panel Layout

```
┌────────────────────────────────────┐
│ PREVIEW CANVAS                     │
├────────────────────────────────────┤
│ Plugin: [Generic Widgets    ▼]     │  ← Plugin selector
│ [Zoom: 100%]  [Grid: Off]          │  ← Canvas controls
├────────────────────────────────────┤
│                                    │
│   Widget Library Palette           │  ← Draggable widget palette
│   ┌────────────────────────────┐  │
│   │[BTN][INP][LST][TAB][MNU]   │  │
│   │[TXT][TBL][TRE][SCR][PGB]   │  │
│   └────────────────────────────┘  │
│                                    │
├────────────────────────────────────┤
│                                    │
│ ┌────────────────────────────────┐│
│ │                                ││
│ │      Live Preview Area         ││  ← Zoomable canvas
│ │                                ││     Shows actual widgets
│ │   [Primary Button]             ││     with theme applied
│ │   [Secondary] [Danger]         ││
│ │                                ││
│ │   [Text Input Field___]        ││
│ │                                ││
│ │   [Dropdown ▼]                 ││
│ │                                ││
│ │   ☐ Checkbox                   ││
│ │   ⦿ Radio Selected             ││
│ │   ○ Radio Unselected           ││
│ │                                ││
│ │   ─────────────                ││  ← Horizontal line
│ │                                ││
│ │   Item 1                       ││
│ │   Item 2 (selected)            ││
│ │   Item 3                       ││
│ │                                ││
│ └────────────────────────────────┘│
│                                    │
├────────────────────────────────────┤
│ State Simulation Panel             │  ← Force widget states
│ ┌────────────────────────────────┐│
│ │ [●Normal] [Hover] [Pressed]    ││
│ │ [Disabled] [Focus]             ││
│ └────────────────────────────────┘│
└────────────────────────────────────┘
```

### 6.2 Plugin Selector

**Dropdown Options**:
```
Plugin: [Generic Widgets ▼]
├── Generic Widgets          (always available)
├── Terminal Widget          (if installed)
├── Multisplit Widget        (if installed)
├── Chrome Tabbed Window     (if installed)
├── ──────────────
├── Custom Plugins           →
│   └── (user plugins from ~/.theme-studio/plugins/)
```

**Behavior**:
- Changing plugin replaces preview content
- Plugin selection persisted per session
- Shows "(not installed)" for unavailable plugins

### 6.3 Canvas Controls

**Control Bar**:
```
┌────────────────────────────────────────────────────────┐
│ [Zoom: 100% ▼] [Grid: Off] [Snap: Off] [Export Image] │
└────────────────────────────────────────────────────────┘
```

**Zoom Combo**:
- Values: 25%, 50%, 75%, 100%, 125%, 150%, 200%, 400%
- Editable (custom values)
- Synced with toolbar zoom

**Grid Toggle**:
- On/Off button
- Grid size: 20px (configurable in preferences)
- Grid color: Subtle, based on theme

**Snap Toggle**:
- On/Off button
- Snap to grid when dragging widgets
- Only visible when grid is on

**Export Image**:
- Button to export preview as PNG/SVG
- Opens save dialog

### 6.4 Widget Library Palette

**Palette Layout**:
```
┌────────────────────────────────────┐
│ Widget Library                     │
├────────────────────────────────────┤
│ [BTN] [INP] [LST] [TAB] [MNU]     │  ← Row 1
│ [TXT] [TBL] [TRE] [SCR] [PGB]     │  ← Row 2
│ [SLD] [SPB] [CMB] [CHK] [RAD]     │  ← Row 3
└────────────────────────────────────┘
```

**Widget Icons**:
- BTN: Button
- INP: Input (line edit)
- LST: List view
- TAB: Tab widget
- MNU: Menu
- TXT: Text edit
- TBL: Table
- TRE: Tree view
- SCR: Scrollbar
- PGB: Progress bar
- SLD: Slider
- SPB: Spin box
- CMB: Combo box
- CHK: Checkbox
- RAD: Radio button

**Interaction**:
- Click to add widget to canvas
- Drag to position on canvas
- Tooltips show widget name

### 6.5 Preview Canvas Area

**Canvas Implementation**:
```python
class PreviewCanvas(QGraphicsView):
    """Zoomable preview canvas for widgets."""

    def __init__(self):
        super().__init__()

        # Scene setup
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Canvas properties
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Zoom
        self._zoom_factor = 1.0
        self._zoom_range = (0.25, 4.0)

    def wheelEvent(self, event):
        """Zoom with Ctrl+Wheel."""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            zoom_in = delta > 0
            self.zoom(1.1 if zoom_in else 0.9)
```

**Features**:
- Zoomable (Ctrl+Wheel or toolbar)
- Pannable (drag with scroll hand)
- Grid overlay (optional)
- Snap-to-grid (optional)
- Widget selection (click)
- Widget repositioning (drag)

### 6.6 State Simulation Panel

**Panel Layout**:
```
┌────────────────────────────────────┐
│ State Simulation                   │
├────────────────────────────────────┤
│ [●Normal] [Hover] [Pressed]        │
│ [Disabled] [Focus]                 │
└────────────────────────────────────┘
```

**States**:
- **Normal**: Default state (radio button selected by default)
- **Hover**: Simulates mouse hover
- **Pressed**: Simulates mouse press
- **Disabled**: Disables widget
- **Focus**: Sets keyboard focus

**Behavior**:
- Radio button group (mutually exclusive)
- Applies to all widgets in canvas
- Visual feedback on selected state

---

## 7. Right Panel: Inspector

### 7.1 Panel Layout

```
┌───────────────────┐
│ INSPECTOR         │
├───────────────────┤
│ Selected Token    │
│ ┌───────────────┐ │
│ │ button.       │ │
│ │ background    │ │
│ └───────────────┘ │
│                   │
│ Category: Button  │
│ Type: Color       │
│                   │
├───────────────────┤
│ Value             │
│ ┌───────────────┐ │
│ │ #0e639c       │ │  ← Hex input
│ │ ┌───────────┐ │ │
│ │ │ [🎨 Pick] │ │ │  ← Color picker
│ │ └───────────┘ │ │
│ │               │ │
│ │ rgb(14,99,156)│ │  ← RGB display
│ │ hsl(205,83,33)│ │  ← HSL display
│ └───────────────┘ │
│                   │
│ Format:           │
│ [Hex ▼]           │  ← Format selector
│                   │
├───────────────────┤
│ Accessibility     │
│ ┌───────────────┐ │
│ │ Contrast:     │ │
│ │   4.8:1       │ │  ← Ratio with background
│ │               │ │
│ │ WCAG AA:  ✓   │ │  ← AA compliance
│ │ WCAG AAA: ✗   │ │  ← AAA compliance
│ │               │ │
│ │ [Auto-Fix]    │ │  ← Fix button
│ └───────────────┘ │
│                   │
├───────────────────┤
│ Usage             │
│ ┌───────────────┐ │
│ │ Used by:      │ │
│ │ • QPushButton │ │
│ │ • QToolButton │ │
│ │ • QPushBtn... │ │
│ │               │ │
│ │ [Show All...] │ │
│ └───────────────┘ │
│                   │
├───────────────────┤
│ Related Tokens    │
│ ┌───────────────┐ │
│ │→button.hover  │ │  ← Click to navigate
│ │→button.border │ │
│ │→button.fg     │ │
│ └───────────────┘ │
│                   │
├───────────────────┤
│ Actions           │
│ [Reset] [Copy]    │
└───────────────────┘
```

### 7.2 Token Information Section

**Selected Token Display**:
```python
class TokenInfoWidget(QWidget):
    """Displays selected token information."""

    def show_token(self, token_name: str):
        self.name_label.setText(token_name)

        # Parse token name
        parts = token_name.split('.')
        category = parts[0] if parts else "Unknown"

        self.category_label.setText(f"Category: {category.title()}")
        self.type_label.setText(f"Type: Color")  # or "Font"
```

**Fields**:
- **Token Name**: Full token path (e.g., `button.background`)
- **Category**: Category name (e.g., "Button")
- **Type**: "Color" or "Font"
- **Description**: Human-readable description (from registry)

### 7.3 Value Editor Section

#### 7.3.1 Color Token Editor

```
┌───────────────┐
│ Value         │
├───────────────┤
│ #0e639c       │  ← Hex input (editable)
│ ┌───────────┐ │
│ │ [🎨 Pick] │ │  ← Opens QColorDialog
│ └───────────┘ │
│               │
│ Preview: ███  │  ← Color swatch
│               │
│ rgb(14,99,156)│  ← RGB display (read-only)
│ hsl(205,83,33)│  ← HSL display (read-only)
└───────────────┘

Format: [Hex ▼]
├── Hex (#rrggbb)
├── RGB (r,g,b)
├── RGBA (r,g,b,a)
└── HSL (h,s,l)
```

**Color Picker Button**:
- Opens `QColorDialog`
- Shows current color as default
- Updates value on selection

**Format Selector**:
- Changes display format (not stored format)
- All formats stored as hex internally
- Converts on display

#### 7.3.2 Font Token Editor

```
┌───────────────┐
│ Value         │
├───────────────┤
│ Family:       │
│ [Consolas ▼]  │  ← Font family combo
│               │
│ Size:         │
│ [14] px       │  ← Size spin box
│               │
│ Weight:       │
│ [400      ▼]  │  ← Weight combo (100-900)
│               │
│ Style:        │
│ [Normal   ▼]  │  ← Style combo (Normal/Italic)
│               │
│ Preview:      │
│ ┌───────────┐ │
│ │ AaBbCc123 │ │  ← Font preview
│ └───────────┘ │
└───────────────┘
```

### 7.4 Accessibility Section

**Contrast Checker**:
```python
class AccessibilityWidget(QWidget):
    """WCAG compliance checker."""

    def update_contrast(self, foreground: str, background: str):
        ratio = self._calculate_contrast(foreground, background)

        self.ratio_label.setText(f"{ratio:.1f}:1")

        # WCAG AA: 4.5:1 for normal text
        aa_pass = ratio >= 4.5
        self.aa_label.setText("✓" if aa_pass else "✗")

        # WCAG AAA: 7:1 for normal text
        aaa_pass = ratio >= 7.0
        self.aaa_label.setText("✓" if aaa_pass else "✗")
```

**Auto-Fix Button**:
- Suggests color adjustments to meet WCAG AA
- Shows preview of suggested color
- Click to apply suggestion

**Validation Display**:
- **Green checkmark (✓)**: Passes standard
- **Red X (✗)**: Fails standard
- **Ratio display**: Shows exact contrast ratio

### 7.5 Usage Section

**Usage Tree**:
```
Used by:
├── QPushButton
├── QToolButton
├── QDialogButtonBox
└── Custom widgets...
    ├── MyCustomButton
    └── ThemedButton
```

**Features**:
- Lists all Qt widgets using this token
- Shows custom widgets if known
- Click to highlight in preview (if widget present)
- "Show All..." button for long lists

### 7.6 Related Tokens Section

**Related Token Links**:
```
Related Tokens:
├── → button.hoverBackground    (related state)
├── → button.border             (same category)
├── → button.foreground         (complementary)
└── → colors.primary            (base token)
```

**Features**:
- Clickable links (arrows →)
- Click to navigate to that token
- Grouped by relationship type
- Shows token value preview

### 7.7 Actions Section

**Action Buttons**:
```
┌───────────────────────┐
│ [Reset]  [Copy]       │
│ [Apply to All...]     │
└───────────────────────┘
```

**Buttons**:
- **Reset**: Reset token to registry default
- **Copy**: Copy token value to clipboard
- **Apply to All...**: Apply color to multiple tokens (bulk edit)

---

## 8. Status Bar Specification

### 8.1 Status Bar Layout

```
┌────────────────────────────────────────────────────────────────┐
│ ⓘ Theme: my-theme.json (modified) │ Tokens: 45/197 │ Ready    │
└────────────────────────────────────────────────────────────────┘
```

### 8.2 Status Bar Sections

**Section 1: Theme Info (Left, 50%)**
```
ⓘ Theme: my-custom-theme.json (modified)
```
- Info icon (ⓘ)
- Theme filename
- Modified indicator (if unsaved changes)

**Section 2: Token Status (Center, 30%)**
```
Tokens: 45/197 defined (23%)
```
- Defined count / Total count
- Percentage in parentheses
- Progress bar (optional)

**Section 3: Status Message (Right, 20%)**
```
Ready
Saving...
Validating accessibility...
[Progress: ████████░░] 80%
```
- Status messages
- Progress bar for long operations
- Idle message: "Ready"

### 8.3 Status Messages

**Message Types**:
- **Idle**: "Ready"
- **File Operation**: "Saving...", "Loading theme...", "Exporting..."
- **Validation**: "Validating accessibility...", "45 issues found"
- **Edit Operation**: "Token updated", "Undo: Set button.background"
- **Error**: "Error: Failed to save theme"

**Message Duration**:
- Info messages: 3 seconds
- Error messages: 10 seconds (or until dismissed)
- Progress operations: Until complete

---

## 9. Dialogs and Modal Windows

### 9.1 New Theme Dialog

**Purpose**: Create new theme from template or blank

```
┌──────────────────────────────────────────────┐
│ New Theme                                [X] │
├──────────────────────────────────────────────┤
│                                              │
│ Theme Name:                                  │
│ ┌──────────────────────────────────────────┐│
│ │ My Custom Theme                          ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Base Theme:                                  │
│ ┌──────────────────────────────────────────┐│
│ │ [Blank (Empty)]               ▼          ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Type:                                        │
│ ⦿ Dark   ○ Light   ○ High Contrast          │
│                                              │
│ Template Gallery:                            │
│ ┌──────────────────────────────────────────┐│
│ │ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐      ││
│ │ │Dark│ │Lite│ │Nord│ │Drac│ │Mate│      ││
│ │ │Min │ │Min │ │    │ │ula │ │rial│      ││
│ │ └────┘ └────┘ └────┘ └────┘ └────┘      ││
│ │ ┌────┐ ┌────┐ ┌────┐ ┌────┐             ││
│ │ │Solr│ │Solr│ │One │ │Git │             ││
│ │ │Dark│ │Lite│ │Dark│ │Hub │             ││
│ │ └────┘ └────┘ └────┘ └────┘             ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Preview:                                     │
│ ┌──────────────────────────────────────────┐│
│ │ [Button]  [Input___]  [Tab]              ││
│ │                                          ││
│ └──────────────────────────────────────────┘│
│                                              │
│              [Cancel]  [Create Theme]        │
└──────────────────────────────────────────────┘
```

### 9.2 Export Dialog

**Purpose**: Export theme to various formats

```
┌──────────────────────────────────────────────┐
│ Export Theme                             [X] │
├──────────────────────────────────────────────┤
│                                              │
│ Format:                                      │
│ ⦿ VFWidgets JSON (.json)                     │
│ ○ VS Code Theme (.jsonc)                     │
│ ○ CSS Variables (.css)                       │
│ ○ Qt Stylesheet (.qss)                       │
│ ○ Python Dict (.py)                          │
│                                              │
│ Export Location:                             │
│ ┌──────────────────────────────────────────┐│
│ │ /home/user/themes/my-theme.json    [...]││
│ └──────────────────────────────────────────┘│
│                                              │
│ Options:                                     │
│ ☑ Include metadata                           │
│ ☑ Include comments                           │
│ ☑ Generate preview card                      │
│ ☑ Generate documentation                     │
│ ☐ Minify output                              │
│                                              │
│ Validation:                                  │
│ ⚠ 3 accessibility issues found               │
│ [View Report...]                             │
│                                              │
│              [Cancel]  [Export]              │
└──────────────────────────────────────────────┘
```

### 9.3 Color Picker Dialog

**Purpose**: Select color with advanced options

```
┌──────────────────────────────────────────────┐
│ Color Picker - button.background        [X] │
├──────────────────────────────────────────────┤
│                                              │
│ ┌────────────────┐  ┌────────────────────┐  │
│ │                │  │ H: [205 ] Hue      │  │
│ │   Color        │  │ S: [ 83 ] Sat      │  │
│ │   Square       │  │ L: [ 33 ] Light    │  │
│ │   Selector     │  │                    │  │
│ │                │  │ R: [ 14 ] Red      │  │
│ │                │  │ G: [ 99 ] Green    │  │
│ │                │  │ B: [156 ] Blue     │  │
│ └────────────────┘  └────────────────────┘  │
│                                              │
│ Hex: #0e639c                                 │
│                                              │
│ Recent Colors:                               │
│ ┌──────────────────────────────────────────┐│
│ │ ███ ███ ███ ███ ███ ███ ███ ███ ███      ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Theme Palette:                               │
│ ┌──────────────────────────────────────────┐│
│ │ ███ ███ ███ ███ ███ ███ ███ ███ ███      ││
│ └──────────────────────────────────────────┘│
│                                              │
│              [Cancel]  [OK]                  │
└──────────────────────────────────────────────┘
```

### 9.4 Preferences Dialog

**Purpose**: Application settings

```
┌──────────────────────────────────────────────────────────────┐
│ Preferences                                              [X] │
├────────────────┬─────────────────────────────────────────────┤
│                │                                             │
│ ▼ General      │ General Settings                            │
│   • Interface  │                                             │
│   • Theme      │ Language:                                   │
│                │ [English           ▼]                       │
│ ▼ Editor       │                                             │
│   • Preview    │ Auto-save:                                  │
│   • Canvas     │ ☑ Enable (every [5] minutes)                │
│                │                                             │
│ ▼ Accessibility│ Recent files:                               │
│   • Validation │ Keep [10] recent files                      │
│                │                                             │
│ ▼ Export       │ ───────────────────────────────────────     │
│   • Formats    │                                             │
│   • Templates  │ Interface Settings                          │
│                │                                             │
│ ▼ Advanced     │ UI Scale:                                   │
│   • Performance│ [100%] (requires restart)                   │
│   • Plugins    │                                             │
│                │ Font Size:                                  │
│                │ [Medium      ▼]                             │
│                │                                             │
│                │ ───────────────────────────────────────     │
│                │                                             │
│                │ Theme                                       │
│                │                                             │
│                │ Application Theme:                          │
│                │ [Dark (System)          ▼]                  │
│                │                                             │
│                │                                             │
│                │              [Cancel]  [Apply]  [OK]        │
│                │                                             │
└────────────────┴─────────────────────────────────────────────┘
```

### 9.5 Validation Report Dialog

**Purpose**: Show accessibility validation results

```
┌──────────────────────────────────────────────┐
│ Accessibility Validation Report          [X] │
├──────────────────────────────────────────────┤
│                                              │
│ Summary:                                     │
│ ┌──────────────────────────────────────────┐│
│ │ ✓ 147 tokens pass WCAG AA                ││
│ │ ⚠  8 tokens below AA threshold           ││
│ │ ✗  3 tokens fail minimum contrast        ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Issues:                                      │
│ ┌──────────────────────────────────────────┐│
│ │ ✗ button.secondary.foreground            ││
│ │   Contrast: 2.8:1 (needs 4.5:1)          ││
│ │   Against: button.secondary.background   ││
│ │   Suggestion: Use #4a4a4a                ││
│ │   [Auto-Fix] [Ignore]                    ││
│ │                                          ││
│ │ ⚠ input.placeholderForeground            ││
│ │   Contrast: 3.2:1 (needs 4.5:1)          ││
│ │   Against: input.background              ││
│ │   Suggestion: Use #5a5a5a                ││
│ │   [Auto-Fix] [Ignore]                    ││
│ │                                          ││
│ │ ✗ list.inactiveSelectionForeground       ││
│ │   Contrast: 2.1:1 (needs 4.5:1)          ││
│ │   [Auto-Fix] [Ignore]                    ││
│ └──────────────────────────────────────────┘│
│                                              │
│ [Export Report...] [Fix All]  [Close]       │
└──────────────────────────────────────────────┘
```

---

## 10. Responsive Behavior

### 10.1 Panel Resizing

**Minimum Panel Widths**:
- Token Browser: 200px
- Preview Canvas: 400px
- Inspector: 200px

**Collapsing Behavior**:
- When window width < 1000px: Auto-collapse Inspector
- When window width < 800px: Auto-collapse Token Browser
- User can manually expand collapsed panels

**Splitter Behavior**:
```python
class MainContentSplitter(QSplitter):
    """Three-panel splitter with constraints."""

    def __init__(self):
        super().__init__(Qt.Horizontal)

        # Add panels
        self.addWidget(token_browser_panel)
        self.addWidget(preview_canvas_panel)
        self.addWidget(inspector_panel)

        # Set initial sizes (25% | 50% | 25%)
        total_width = 1600
        self.setSizes([400, 800, 400])

        # Set minimum sizes
        self.setStretchFactor(0, 1)  # Token browser
        self.setStretchFactor(1, 2)  # Preview (stretches more)
        self.setStretchFactor(2, 1)  # Inspector
```

### 10.2 Window Size Adaptations

**Large Displays (1920px+)**:
- Full three-panel layout
- Widget library always visible
- State simulator always visible

**Medium Displays (1200-1920px)**:
- Full three-panel layout
- Widget library collapsible
- State simulator collapsible

**Small Displays (< 1200px)**:
- Two-panel layout (canvas + one side panel)
- Toggle between Token Browser and Inspector
- Compact toolbar (text labels hidden)

### 10.3 Toolbar Responsive Behavior

**Full Mode (> 1400px)**:
```
[New] [Open] [Save] │ [Undo] [Redo] │ [Validate] [Export] │ Zoom: [100%]
```

**Compact Mode (< 1400px)**:
```
[⎙] [📁] [💾] │ [↶] [↷] │ [✓] [↗] │ [100%]
```
- Icons only, no text labels
- Tooltips show full action names

**Minimal Mode (< 1000px)**:
```
[☰] Menu  [Zoom: 100%]
```
- Hamburger menu with all actions
- Essential controls only

---

## 11. Keyboard Shortcuts

### 11.1 File Operations

| Action | Shortcut |
|--------|----------|
| New Theme | Ctrl+N |
| New from Template | Ctrl+Shift+N |
| Open Theme | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Export | Ctrl+E |
| Close Theme | Ctrl+W |
| Quit | Ctrl+Q |

### 11.2 Edit Operations

| Action | Shortcut |
|--------|----------|
| Undo | Ctrl+Z |
| Redo | Ctrl+Shift+Z or Ctrl+Y |
| Copy Token Value | Ctrl+C |
| Paste Token Value | Ctrl+V |
| Reset Token | Ctrl+R |
| Find Token | Ctrl+F |
| Select All Tokens | Ctrl+A |

### 11.3 View Operations

| Action | Shortcut |
|--------|----------|
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Reset Zoom | Ctrl+0 |
| Toggle Token Browser | Ctrl+1 |
| Toggle Preview Canvas | Ctrl+2 |
| Toggle Inspector | Ctrl+3 |
| Toggle Grid | Ctrl+G |
| Fullscreen | F11 |

### 11.4 Theme Operations

| Action | Shortcut |
|--------|----------|
| Validate Accessibility | F7 |
| Theme Properties | Ctrl+I |

### 11.5 Tools

| Action | Shortcut |
|--------|----------|
| Palette Extractor | Ctrl+Shift+P |
| Color Harmonizer | Ctrl+H |
| Bulk Edit | Ctrl+B |
| Compare Themes | Ctrl+D |

### 11.6 Navigation

| Action | Shortcut |
|--------|----------|
| Focus Token Browser | Alt+1 |
| Focus Preview Canvas | Alt+2 |
| Focus Inspector | Alt+3 |
| Focus Search | Ctrl+F |
| Next Token | Down or Tab |
| Previous Token | Up or Shift+Tab |

### 11.7 Help

| Action | Shortcut |
|--------|----------|
| Documentation | F1 |
| Keyboard Shortcuts | Ctrl+/ |

---

## 12. Accessibility Features

### 12.1 Screen Reader Support

**ARIA Labels**:
- All interactive elements have descriptive labels
- Button labels describe action, not just icon
- Panel headings marked as landmarks

**Example**:
```python
button.setAccessibleName("New Theme")
button.setAccessibleDescription("Create a new theme from scratch or template")
```

### 12.2 Keyboard Navigation

**Tab Order**:
1. Menu bar
2. Toolbar buttons (left to right)
3. Token browser search
4. Token tree (arrow keys to navigate)
5. Preview canvas
6. Inspector fields

**Focus Indicators**:
- Visible focus ring on all focusable elements
- High contrast focus indicator (2px border)
- Focus follows keyboard navigation

### 12.3 High Contrast Support

**High Contrast Mode**:
- Detects system high contrast setting
- Adjusts UI colors accordingly
- Increases border thickness
- Ensures 7:1 contrast minimum (WCAG AAA)

### 12.4 Text Scaling

**Font Size Options**:
- Small (90%)
- Medium (100%) - Default
- Large (125%)
- Extra Large (150%)

**Zoom**:
- UI scales with system display scaling
- Canvas zoom independent (25%-400%)
- Text remains legible at all zoom levels

### 12.5 Color Indicators

**Not Color-Only**:
- Modified tokens: Dot (●) + asterisk (*) in tree
- Validation issues: Icon (⚠/✗) + text description
- Active state: Radio button + bold text

**Colorblind-Friendly**:
- Issues use icons, not just colors
- Success/warning/error icons distinct shapes
- Optional colorblind simulation mode

---

## Implementation Notes

### Technology Stack
- **Base Window**: `ViloCodeWindow` from `vfwidgets-vilocode-window`
- **Theme System**: `ThemedApplication`, `ThemedWidget` from `vfwidgets-theme`
- **Splitters**: `QSplitter` for resizable panels
- **Tree View**: `QTreeView` with custom model
- **Canvas**: `QGraphicsView` + `QGraphicsScene`

### File Structure
```
src/theme_studio/
├── window.py                    # Main window (this spec)
├── panels/
│   ├── token_browser.py         # Section 5
│   ├── preview_canvas.py        # Section 6
│   └── inspector.py             # Section 7
├── widgets/
│   ├── token_tree_view.py       # Token browser tree
│   ├── color_picker.py          # Color selector
│   └── state_simulator.py       # State simulation panel
├── dialogs/
│   ├── new_theme.py             # Section 9.1
│   ├── export.py                # Section 9.2
│   └── preferences.py           # Section 9.4
└── resources/
    ├── icons/                   # UI icons
    └── styles/                  # Stylesheets
```

---

**Document Status:** Living document
**Next Steps**: Begin Phase 1 implementation (Foundation)
**Related Documents**:
- `SPECIFICATION.md` - Overall application specification
- `ARCHITECTURE.md` - System architecture (TBD)
