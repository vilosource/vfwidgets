# VFTheme Studio - Technical Specification

**Version:** 0.1.0-dev
**Status:** Design Phase
**Target Release:** Q2 2026

---

## Executive Summary

**VFTheme Studio** is a standalone professional application for visual theme design and editing in the VFWidgets ecosystem. Inspired by Qt Designer's workflow, it enables theme creators to design comprehensive themes without writing code, with real-time preview across 200+ tokens and support for custom widget rendering.

**Key Differentiator:** First visual theme designer specifically for Qt/PySide6 applications with plugin architecture for custom widget previews.

---

## 1. Vision & Goals

### 1.1 Vision Statement
Enable designers and developers to create professional, accessible themes for VFWidgets applications through an intuitive visual interface, reducing theme creation time from hours to minutes.

### 1.2 Primary Goals
- **Zero-Code Theme Creation**: Non-programmers can create themes
- **Real-Time Preview**: Instant visual feedback on token changes
- **Custom Widget Support**: Preview actual VFWidgets (Terminal, Multisplit, etc.)
- **Accessibility First**: Built-in WCAG compliance validation
- **Professional Export**: Multi-format export (JSON, VS Code, CSS, QSS)

### 1.3 Success Metrics
- Reduce theme creation time from 2+ hours → 15-30 minutes
- 100% coverage of 200+ theme tokens
- WCAG AA compliance validation before export
- Support 5+ export formats
- 10+ built-in professional templates

---

## 2. User Personas

### Persona 1: UI/UX Designer (Primary)
**Background**: Graphic designer with limited programming knowledge
**Goal**: Create brand-consistent themes for company applications
**Pain Points**: Can't code, needs visual tools, requires color harmony
**Needs**: Color picker, palette extractor, preview all widget states

### Persona 2: Application Developer (Secondary)
**Background**: Python developer building PySide6 apps
**Goal**: Quickly customize themes for specific applications
**Pain Points**: Theme JSON is tedious, wants quick iterations
**Needs**: Fast editing, export to multiple formats, template starting points

### Persona 3: Theme Creator (Tertiary)
**Background**: Community contributor creating theme packs
**Goal**: Create and share high-quality themes
**Pain Points**: Needs validation, documentation generation, preview cards
**Needs**: Accessibility validation, export documentation, sharing tools

---

## 3. Architecture Overview

### 3.1 Technology Stack

```
Foundation:
- PySide6 6.9+           # Qt framework
- Python 3.9+            # Language

VFWidgets Integration:
- vfwidgets-theme        # Theme system
- vfwidgets-vilocode-window  # Main window layout
- chrome-tabbed-window   # Optional: tabbed projects

Custom Widget Plugins (Optional):
- vfwidgets-terminal     # Terminal preview
- vfwidgets-multisplit   # Splitter preview
- chrome-tabbed-window   # Tab preview
```

### 3.2 Application Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    VFTheme Studio                          │
│                  (ThemedApplication)                        │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│                   ThemeStudioWindow                        │
│                 (ViloCodeWindow Base)                      │
│  ┌──────────────┬──────────────────┬───────────────────┐  │
│  │ Token        │  Preview         │  Inspector        │  │
│  │ Browser      │  Canvas          │  Panel            │  │
│  │ Panel        │                  │                   │  │
│  │              │  ┌────────────┐  │                   │  │
│  │ ▼ colors     │  │  Widget    │  │  Token Properties │  │
│  │   • fg       │  │  Library   │  │  ┌─────────────┐  │  │
│  │   • bg       │  │  Palette   │  │  │ Name: btn.bg│  │  │
│  │ ▼ button     │  └────────────┘  │  │ Value:#0e63 │  │  │
│  │   • bg       │                  │  │ [Picker]    │  │  │
│  │   • hover    │  ┌────────────┐  │  └─────────────┘  │  │
│  │              │  │  Preview   │  │                   │  │
│  │ [Search]     │  │  [Widgets] │  │  Accessibility    │  │
│  │ [Filter]     │  │            │  │  Contrast: 4.8:1  │  │
│  │              │  └────────────┘  │  WCAG AA: ✓       │  │
│  └──────────────┴──────────────────┴───────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │    ThemeDocument Model        │
          │    (Observable, Undo/Redo)    │
          └───────────────────────────────┘
```

### 3.3 Module Structure

```
apps/theme-studio/
├── src/theme_studio/
│   ├── __init__.py                 # Package initialization
│   ├── __main__.py                 # Entry point (CLI)
│   ├── app.py                      # ThemedApplication subclass
│   ├── window.py                   # Main window (3-panel layout)
│   │
│   ├── models/                     # Data models
│   │   ├── theme_document.py       # Theme as document (undo/redo)
│   │   ├── project.py              # Multi-theme project container
│   │   ├── history.py              # Change history tracking
│   │   └── token.py                # Token data model
│   │
│   ├── panels/                     # UI panels
│   │   ├── token_browser.py        # Left: Token tree browser
│   │   ├── preview_canvas.py       # Center: Preview area
│   │   └── inspector.py            # Right: Property inspector
│   │
│   ├── widgets/                    # Custom widgets
│   │   ├── color_picker.py         # Enhanced color picker
│   │   ├── token_editor.py         # Token value editor
│   │   ├── widget_library.py       # Draggable widget palette
│   │   ├── preview_samples.py      # Sample widget generator
│   │   └── contrast_checker.py     # WCAG validation widget
│   │
│   ├── preview/                    # Preview system
│   │   ├── plugin_system.py        # Plugin base classes
│   │   ├── generic_preview.py      # Generic Qt widgets
│   │   ├── terminal_plugin.py      # Terminal widget preview
│   │   ├── multisplit_plugin.py    # Multisplit widget preview
│   │   └── chrome_tabs_plugin.py   # Chrome tabs preview
│   │
│   ├── tools/                      # Design tools
│   │   ├── palette_extractor.py    # Extract colors from images
│   │   ├── harmonizer.py           # Color harmony generator
│   │   ├── bulk_operations.py      # Mass token editing
│   │   └── diff_viewer.py          # Theme comparison
│   │
│   ├── io/                         # Import/Export
│   │   ├── formats/
│   │   │   ├── vfwidgets_json.py   # Native format
│   │   │   ├── vscode_theme.py     # VS Code import/export
│   │   │   ├── css_variables.py    # CSS custom properties
│   │   │   └── qt_stylesheet.py    # QSS export
│   │   └── converters.py           # Format conversion utils
│   │
│   ├── dialogs/                    # Application dialogs
│   │   ├── new_project.py          # New theme wizard
│   │   ├── preferences.py          # App settings
│   │   ├── export.py               # Export dialog
│   │   └── templates.py            # Template gallery
│   │
│   ├── components/                 # Reusable UI components
│   │   ├── toolbar.py              # Main toolbar
│   │   ├── status_bar.py           # Status messages
│   │   └── menubar.py              # Menu bar builder
│   │
│   └── resources/                  # Embedded resources
│       ├── templates/              # Built-in themes
│       ├── icons/                  # UI icons
│       └── styles/                 # App stylesheets
```

---

## 4. Core Features

### 4.1 Three-Panel Layout

**Left Panel: Token Browser**
- Hierarchical tree view (15 categories, 200+ tokens)
- Search/filter functionality
- Recently edited tokens
- Favorite tokens
- Show only modified tokens
- Show tokens with validation issues
- Token usage indicators

**Center Panel: Preview Canvas**
- Widget library palette (drag-drop)
- Zoomable canvas (25% - 400%)
- Preview mode selector:
  - Generic Widgets (buttons, inputs, lists, etc.)
  - Custom Widget Plugins (terminal, multisplit, etc.)
- State simulation (hover, focus, pressed, disabled)
- Grid/snap-to-grid
- Export preview as PNG/SVG

**Right Panel: Inspector**
- Selected token properties
- Color picker with formats (hex, rgb, rgba, hsl)
- Font selector (family, size, weight, style)
- Token usage tree ("Used by: QPushButton, QToolButton...")
- Live accessibility validation
- Related tokens suggestions
- Quick actions (copy, paste, reset)

### 4.2 Plugin-Based Preview System

**Abstract Plugin Interface:**
```python
class PreviewPlugin(ABC):
    @abstractmethod
    def name(self) -> str:
        """Plugin display name."""

    @abstractmethod
    def create_preview(self, theme: Theme) -> QWidget:
        """Create widget instance with theme applied."""

    @abstractmethod
    def get_relevant_tokens(self) -> list[str]:
        """List of tokens this widget uses."""

    @abstractmethod
    def update_theme(self, widget: QWidget, theme: Theme):
        """Update existing widget with new theme."""
```

**Built-in Plugins:**
1. **GenericWidgetsPlugin** - Standard Qt widgets (always available)
2. **TerminalWidgetPlugin** - Live terminal preview (if vfwidgets-terminal installed)
3. **MultisplitWidgetPlugin** - Split pane preview (if vfwidgets-multisplit installed)
4. **ChromeTabbedWindowPlugin** - Tab preview (if chrome-tabbed-window installed)

**Plugin Discovery:**
- Auto-detect installed VFWidgets packages
- Load plugins from `~/.theme-studio/plugins/`
- Third-party plugins via Python packages

**Token Filtering:**
When plugin is active:
- Token browser highlights relevant tokens
- Inspector shows "Used by [Plugin Name]"
- Search defaults to plugin tokens

### 4.3 Token Management System

**Token Data Model:**
```python
@dataclass
class TokenData:
    name: str                    # "button.background"
    category: TokenCategory      # BUTTON
    value: str                   # "#0e639c"
    default_light: str          # Registry default for light
    default_dark: str           # Registry default for dark
    required: bool              # Whether token must be defined
    description: str            # Human-readable description
    usage: list[str]            # Widgets that use this token
    modified: bool              # Changed from default?
    validation_issues: list[str] # WCAG warnings/errors
```

**Token Operations:**
- Get/Set with undo/redo support
- Bulk selection and editing
- Copy/paste token values
- Reset to default
- Search by name, category, or usage
- Filter by validation status

### 4.4 Theme Document Model

**Observable Document:**
```python
class ThemeDocument(QObject):
    # Signals
    modified = Signal()
    token_changed = Signal(str, str)  # name, new_value
    validation_changed = Signal()

    def __init__(self, theme: Theme):
        self._theme = theme
        self._undo_stack = QUndoStack()
        self._modified = False
        self._observers: list[Observer] = []

    def set_token(self, name: str, value: str):
        """Set token with undo support."""
        command = SetTokenCommand(self._theme, name, value)
        self._undo_stack.push(command)
        self.token_changed.emit(name, value)

    def undo(self):
        self._undo_stack.undo()

    def redo(self):
        self._undo_stack.redo()
```

**Undo/Redo System:**
- Command pattern for all token changes
- Unlimited undo/redo (configurable limit)
- Undo stack visualization
- Checkpoint/restore

### 4.5 Accessibility Validation

**WCAG Compliance:**
- Level AA (minimum 4.5:1 for normal text, 3:1 for large text)
- Level AAA (minimum 7:1 for normal text, 4.5:1 for large text)
- Real-time contrast ratio calculation
- Color blindness simulation (Protanopia, Deuteranopia, Tritanopia)

**Validation Display:**
```
┌────────────────────────────────────┐
│ Accessibility Validation           │
├────────────────────────────────────┤
│ ✓ 147 tokens pass WCAG AA         │
│ ⚠ 8 tokens below AA threshold     │
│ ✗ 3 tokens fail AA                │
│                                    │
│ Issues:                            │
│ • button.secondary.foreground      │
│   Contrast 2.8:1 (needs 4.5:1)    │
│   Suggestion: Use #4a4a4a          │
│   [Auto-Fix]                       │
│                                    │
│ • input.placeholderForeground      │
│   Contrast 3.2:1 (needs 4.5:1)    │
│   [Auto-Fix]                       │
└────────────────────────────────────┘
```

### 4.6 Import/Export System

**Supported Formats:**

1. **VFWidgets JSON** (Native)
   ```json
   {
     "name": "My Theme",
     "type": "dark",
     "version": "1.0.0",
     "colors": {
       "button.background": "#0e639c",
       ...
     }
   }
   ```

2. **VS Code Theme** (.jsonc)
   ```json
   {
     "name": "My Theme",
     "type": "dark",
     "colors": {
       "editor.background": "#1e1e1e",
       ...
     },
     "tokenColors": [...]
   }
   ```

3. **CSS Variables** (.css)
   ```css
   :root {
     --button-background: #0e639c;
     --button-hover-background: #1177bb;
     ...
   }
   ```

4. **Qt Stylesheet** (.qss)
   ```css
   QPushButton {
     background-color: #0e639c;
     color: #ffffff;
     border-radius: 2px;
   }
   ```

5. **Python Dict** (.py)
   ```python
   THEME = {
       "name": "My Theme",
       "colors": {
           "button.background": "#0e639c",
       }
   }
   ```

**Export Options:**
- Single file or directory structure
- Include metadata (author, license, description)
- Generate preview card (PNG/SVG)
- Generate documentation (Markdown/HTML/PDF)
- Validation report

### 4.7 Built-in Templates

**Professional Theme Templates:**
1. **Dark Minimal** - Minimal dark theme (13 base tokens)
2. **Light Minimal** - Minimal light theme (13 base tokens)
3. **Material Dark** - Material Design dark
4. **Material Light** - Material Design light
5. **Nord** - Nord color palette
6. **Dracula** - Dracula color scheme
7. **Solarized Dark** - Solarized dark variant
8. **Solarized Light** - Solarized light variant
9. **One Dark** - Atom One Dark
10. **GitHub Dark** - GitHub's dark theme

**Template Wizard:**
- Preview all templates
- Filter by type (dark/light/high-contrast)
- Filter by tag (professional, playful, minimal, vibrant)
- Start from template or blank

---

## 5. User Workflows

### 5.1 Create Theme from Scratch

**Steps:**
1. File → New Theme from Template
2. Select "Dark Minimal" template
3. Theme loads with 13 base tokens defined
4. Click "button.background" in token browser
5. Use color picker to choose new color
6. Preview updates in real-time (all buttons)
7. Inspector shows contrast ratio: 4.8:1 ✓ WCAG AA
8. Continue editing tokens
9. File → Export → VFWidgets JSON
10. Theme saved as `my-theme.json`

**Time Estimate:** 15-30 minutes for comprehensive theme

### 5.2 Edit Existing Theme

**Steps:**
1. File → Open Theme
2. Select `dark-default.json`
3. Theme loads (all 200 tokens visible)
4. Use search to find "button" tokens
5. Select multiple button tokens (Ctrl+Click)
6. Right-click → Bulk Edit → Adjust Brightness +10%
7. Preview updates for all buttons
8. Validate accessibility (toolbar button)
9. File → Save (overwrites original)

**Time Estimate:** 5-10 minutes for focused edits

### 5.3 Extract Palette from Image

**Steps:**
1. Tools → Palette Extractor
2. Drag screenshot/design mockup to dialog
3. Extractor finds 8 dominant colors
4. AI suggests token mappings:
   - #1e1e1e → colors.background
   - #007acc → colors.primary
   - #d4d4d4 → colors.foreground
   - etc.
5. Click "Apply Mappings"
6. Theme updates with extracted colors
7. Fine-tune individual tokens
8. Export theme

**Time Estimate:** 10-15 minutes

### 5.4 Preview Custom Widget (Terminal)

**Steps:**
1. Preview dropdown → Select "Terminal Widget"
2. Live terminal instance appears in canvas
3. Shows sample terminal output with ANSI colors
4. Click "terminal.colors.ansiRed" in token browser
5. Change color from #cd3131 to #ff0000
6. Terminal updates instantly (red text changes)
7. Type in terminal to test interactively
8. See selection background color update

**Key Benefit:** See exact rendering as end-users will see it

---

## 6. Widget Preview Strategies

### 6.1 Overview

VFTheme Studio provides **real-time preview** of themes across different widget types. Unlike mockups or screenshots, all previews use **actual Qt widget instances** with themes applied, ensuring 100% accurate representation of how themes will appear in production applications.

**Design Principle**: Every widget preview is a real, interactive instance—not a static image or approximation.

### 6.2 Preview Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Preview Canvas                          │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Plugin Selector:  [Generic Widgets ▼]           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │                                                   │    │
│  │    [Live Widget Instance]                        │    │
│  │                                                   │    │
│  │    • Real Qt widgets                             │    │
│  │    • Theme applied via stylesheet + API          │    │
│  │    • Fully interactive (hover, focus, etc.)      │    │
│  │    • Updates on token change (<100ms)            │    │
│  │                                                   │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  State Simulation Panel                           │    │
│  │  [Normal] [Hover] [Pressed] [Disabled]           │    │
│  └──────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### 6.3 Standard Qt Widgets

**Strategy**: Direct instantiation of Qt widgets with stylesheet application.

**Supported Widgets**:
- `QPushButton` - Primary, secondary, danger variants
- `QLineEdit` - Normal, focus, error states
- `QTextEdit` / `QPlainTextEdit` - Multi-line text
- `QComboBox` - Dropdown selector
- `QCheckBox` / `QRadioButton` - Boolean inputs
- `QListWidget` / `QListView` - List views with selection
- `QTableWidget` / `QTableView` - Tabular data
- `QTreeWidget` / `QTreeView` - Hierarchical data
- `QScrollBar` - Horizontal and vertical
- `QSlider` / `QDial` - Range inputs
- `QProgressBar` - Progress indication
- `QToolBar` / `QToolButton` - Toolbar widgets
- `QMenuBar` / `QMenu` - Menu system
- `QStatusBar` - Status messages
- `QGroupBox` - Grouped controls
- `QTabWidget` / `QTabBar` - Tab containers

**Implementation Example**:
```python
class GenericWidgetsPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Generic Qt Widgets"

    def create_preview(self, theme: Theme) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        # Button showcase
        btn_group = QGroupBox("Buttons")
        btn_layout = QHBoxLayout(btn_group)

        primary_btn = QPushButton("Primary")
        primary_btn.setProperty("variant", "primary")

        secondary_btn = QPushButton("Secondary")
        secondary_btn.setProperty("variant", "secondary")

        danger_btn = QPushButton("Danger")
        danger_btn.setProperty("variant", "danger")

        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)

        btn_layout.addWidget(primary_btn)
        btn_layout.addWidget(secondary_btn)
        btn_layout.addWidget(danger_btn)
        btn_layout.addWidget(disabled_btn)
        layout.addWidget(btn_group)

        # Input showcase
        input_group = QGroupBox("Inputs")
        input_layout = QVBoxLayout(input_group)

        line_edit = QLineEdit("Sample text input")
        input_layout.addWidget(line_edit)

        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        input_layout.addWidget(combo)

        layout.addWidget(input_group)

        # Apply theme stylesheet
        stylesheet = StylesheetGenerator.generate(theme)
        container.setStyleSheet(stylesheet)

        return container

    def get_relevant_tokens(self) -> list[str]:
        return [
            "button.background", "button.foreground",
            "button.hoverBackground", "button.border",
            "input.background", "input.foreground",
            "input.border", "input.focusBorder",
            # ... all relevant tokens
        ]

    def update_theme(self, widget: QWidget, theme: Theme):
        stylesheet = StylesheetGenerator.generate(theme)
        widget.setStyleSheet(stylesheet)
```

**Token Coverage**: ~80 tokens
**Update Speed**: Instant (<50ms)
**Interactivity**: Full (hover, focus, click work naturally)

### 6.4 Tab Widgets

**Strategy**: Both standard and custom tab widget previews.

**Variant 1: QTabWidget (Standard)**
```python
class TabWidgetPreview(PreviewPlugin):
    def name(self) -> str:
        return "Tab Widget (Standard)"

    def create_preview(self, theme: Theme) -> QWidget:
        tabs = QTabWidget()

        # Add sample tabs with content
        tabs.addTab(QTextEdit("Content 1"), "Editor")
        tabs.addTab(QListWidget(), "Files")
        tabs.addTab(QTreeWidget(), "Outline")
        tabs.addTab(QTextEdit("Terminal"), "Terminal")

        # Demonstrate closable tabs
        tabs.setTabsClosable(True)
        tabs.setMovable(True)

        # Apply theme
        stylesheet = StylesheetGenerator.generate(theme)
        tabs.setStyleSheet(stylesheet)

        return tabs

    def get_relevant_tokens(self) -> list[str]:
        return [
            "tab.activeBackground",
            "tab.inactiveBackground",
            "tab.activeForeground",
            "tab.inactiveForeground",
            "tab.border",
            "tab.activeBorder",
            "tab.activeBorderTop",
            "tab.hoverBackground",
            "tab.unfocusedActiveBorder",
        ]
```

**Variant 2: ChromeTabbedWindow (Custom)**
```python
class ChromeTabsPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Chrome Tabs"

    def create_preview(self, theme: Theme) -> QWidget:
        # Non-frameless mode for preview
        chrome_tabs = ChromeTabbedWindow(frameless=False)

        # Add sample tabs
        chrome_tabs.addTab(QTextEdit("Content 1"), "Tab 1")
        chrome_tabs.addTab(QTextEdit("Content 2"), "Tab 2")
        chrome_tabs.addTab(QTextEdit("Content 3"), "Tab 3")

        # Theme is auto-applied via ThemedWidget mixin
        # when vfwidgets-theme is available

        return chrome_tabs

    def get_relevant_tokens(self) -> list[str]:
        return [
            "tab.activeBackground",
            "tab.inactiveBackground",
            "tab.activeForeground",
            "tab.border",
            "titleBar.activeBackground",  # Uses title bar tokens
        ]
```

**Token Coverage**: ~10 tab-specific tokens
**Update Speed**: Instant
**Interactivity**: Full (click tabs, close, drag to reorder)

### 6.5 Terminal Widget (WebView-Based)

**Strategy**: Embed actual `TerminalWidget` instance with xterm.js rendering.

**Implementation**:
```python
class TerminalWidgetPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Terminal Widget"

    def create_preview(self, theme: Theme) -> QWidget:
        from vfwidgets_terminal import TerminalWidget

        # Create live terminal instance
        terminal = TerminalWidget()

        # Write sample content showing all ANSI colors
        terminal.write_to_terminal(self._get_sample_content())

        return terminal

    def _get_sample_content(self) -> str:
        """Generate sample terminal output with all colors."""
        return """
\033[0;30mBlack text\033[0m   (terminal.colors.ansiBlack)
\033[0;31mRed text\033[0m     (terminal.colors.ansiRed)
\033[0;32mGreen text\033[0m   (terminal.colors.ansiGreen)
\033[0;33mYellow text\033[0m  (terminal.colors.ansiYellow)
\033[0;34mBlue text\033[0m    (terminal.colors.ansiBlue)
\033[0;35mMagenta text\033[0m (terminal.colors.ansiMagenta)
\033[0;36mCyan text\033[0m    (terminal.colors.ansiCyan)
\033[0;37mWhite text\033[0m   (terminal.colors.ansiWhite)

\033[1;31mBright Red\033[0m   (terminal.colors.ansiBrightRed)
\033[1;32mBright Green\033[0m (terminal.colors.ansiBrightGreen)
\033[1;34mBright Blue\033[0m  (terminal.colors.ansiBrightBlue)

\033[7mSelection background\033[0m (terminal.selectionBackground)
\033[4mCursor\033[0m (terminal.cursor)

$ ls -la
$ echo "Interactive terminal - try typing!"
"""

    def get_relevant_tokens(self) -> list[str]:
        return [
            "terminal.colors.background",
            "terminal.colors.foreground",
            "terminal.cursor",
            "terminal.cursorAccent",
            "terminal.selectionBackground",
            "terminal.colors.ansiBlack",
            "terminal.colors.ansiRed",
            "terminal.colors.ansiGreen",
            "terminal.colors.ansiYellow",
            "terminal.colors.ansiBlue",
            "terminal.colors.ansiMagenta",
            "terminal.colors.ansiCyan",
            "terminal.colors.ansiWhite",
            "terminal.colors.ansiBrightBlack",
            "terminal.colors.ansiBrightRed",
            "terminal.colors.ansiBrightGreen",
            "terminal.colors.ansiBrightYellow",
            "terminal.colors.ansiBrightBlue",
            "terminal.colors.ansiBrightMagenta",
            "terminal.colors.ansiBrightCyan",
            "terminal.colors.ansiBrightWhite",
        ]

    def update_theme(self, widget: QWidget, theme: Theme):
        """Update terminal with new theme."""
        terminal = widget  # TerminalWidget instance

        # Terminal widget has theme update API
        terminal.apply_theme(theme)
```

**Token Coverage**: 21 terminal-specific tokens
**Update Speed**: ~50ms (web rendering delay)
**Interactivity**: Full (can type commands, select text)
**Rendering**: xterm.js in QWebEngineView

### 6.6 Text Editor Widgets

**Strategy**: Dual approach for plain text vs code editors.

**Variant 1: Plain Text Editor (QTextEdit)**
```python
class TextEditorPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Text Editor (Plain)"

    def create_preview(self, theme: Theme) -> QWidget:
        editor = QTextEdit()

        # Sample content
        editor.setPlainText("""
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

This is a sample text editor showing:
- Line wrapping
- Text selection (select this text!)
- Scrollbar styling
- Background and foreground colors

Try clicking inside to see focus border!
""")

        # Apply theme stylesheet
        stylesheet = StylesheetGenerator.generate(theme)
        editor.setStyleSheet(stylesheet)

        return editor

    def get_relevant_tokens(self) -> list[str]:
        return [
            "editor.background",
            "editor.foreground",
            "editor.lineHighlightBackground",
            "editor.selectionBackground",
            "editor.selectionForeground",
            "editor.findMatchBackground",
            "editor.findMatchHighlightBackground",
            "editorCursor.foreground",
            "editorLineNumber.foreground",
            "editorLineNumber.activeForeground",
        ]
```

**Variant 2: Code Editor (QScintilla)**
```python
class CodeEditorPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Code Editor (Syntax Highlighting)"

    def create_preview(self, theme: Theme) -> QWidget:
        from PyQt6.Qsci import QsciScintilla, QsciLexerPython

        editor = QsciScintilla()
        lexer = QsciLexerPython(editor)
        editor.setLexer(lexer)

        # Sample Python code showing syntax highlighting
        editor.setText('''
def calculate_fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Usage example
result = calculate_fibonacci(10)
print(f"Result: {result}")  # Output: Result: 55
''')

        # Apply theme to lexer colors
        self._apply_lexer_theme(lexer, theme)

        return editor

    def _apply_lexer_theme(self, lexer: QsciLexerPython, theme: Theme):
        """Map theme tokens to lexer syntax colors."""
        lexer.setDefaultColor(QColor(theme.get("editor.foreground")))
        lexer.setColor(QColor(theme.get("editorSyntax.keyword")), QsciLexerPython.Keyword)
        lexer.setColor(QColor(theme.get("editorSyntax.string")), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor(theme.get("editorSyntax.comment")), QsciLexerPython.Comment)
        lexer.setColor(QColor(theme.get("editorSyntax.function")), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor(theme.get("editorSyntax.number")), QsciLexerPython.Number)
        # ... additional syntax element mappings

    def get_relevant_tokens(self) -> list[str]:
        return [
            "editor.background",
            "editor.foreground",
            "editorSyntax.keyword",
            "editorSyntax.string",
            "editorSyntax.comment",
            "editorSyntax.function",
            "editorSyntax.number",
            "editorSyntax.operator",
            "editorSyntax.variable",
            "editorSyntax.type",
        ]
```

**Token Coverage**:
- Plain: ~10 editor tokens
- Code: ~20+ syntax tokens

**Update Speed**: Instant
**Interactivity**: Full (edit text, syntax highlighting updates)

### 6.7 Multisplit Widget

**Strategy**: Embed actual `MultisplitWidget` instance with sample panes.

**Implementation**:
```python
class MultisplitWidgetPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Multisplit Widget"

    def create_preview(self, theme: Theme) -> QWidget:
        from vfwidgets_multisplit import MultisplitWidget

        # Simple widget provider for preview
        class PreviewWidgetProvider:
            def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
                if "editor" in widget_id:
                    return QTextEdit(f"Editor {pane_id[:8]}")
                elif "terminal" in widget_id:
                    return QTextEdit(f"Terminal {pane_id[:8]}")
                else:
                    return QWidget()

        # Create multisplit with sample layout
        multisplit = MultisplitWidget(provider=PreviewWidgetProvider())

        # Build sample split layout:
        # +-------------+-------+
        # |   Editor 1  |  Ter  |
        # +-------------+       |
        # |   Editor 2  |  min  |
        # +-------------+-------+

        # Split horizontally
        pane1 = multisplit.get_root_pane_id()
        pane2 = multisplit.split(pane1, "horizontal", 0.7)

        # Split left pane vertically
        pane3 = multisplit.split(pane1, "vertical", 0.5)

        # Add widgets
        multisplit.set_widget(pane1, "editor-1")
        multisplit.set_widget(pane3, "editor-2")
        multisplit.set_widget(pane2, "terminal-1")

        return multisplit

    def get_relevant_tokens(self) -> list[str]:
        return [
            "panel.background",
            "panel.border",
            "sash.hoverBorder",  # Splitter handle
            "editor.background",
        ]
```

**Token Coverage**: ~5 layout-specific tokens
**Update Speed**: Instant
**Interactivity**: Full (resize splitters, drag to adjust)

### 6.8 Other WebView-Based Widgets

**Strategy**: QWebEngineView with HTML/CSS theme injection.

**Generic Web Widget Preview**:
```python
class WebViewWidgetPlugin(PreviewPlugin):
    def name(self) -> str:
        return "Web Widget (Generic)"

    def create_preview(self, theme: Theme) -> QWidget:
        from PySide6.QtWebEngineWidgets import QWebEngineView

        web_view = QWebEngineView()

        # Generate HTML with theme-injected CSS
        html = self._generate_themed_html(theme)
        web_view.setHtml(html)

        return web_view

    def _generate_themed_html(self, theme: Theme) -> str:
        """Generate HTML with CSS variables from theme."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        :root {{
            --bg: {theme.get('editor.background')};
            --fg: {theme.get('editor.foreground')};
            --accent: {theme.get('button.background')};
            --border: {theme.get('panel.border')};
        }}

        body {{
            background-color: var(--bg);
            color: var(--fg);
            font-family: 'Segoe UI', Tahoma, sans-serif;
            padding: 20px;
            margin: 0;
        }}

        .card {{
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 16px;
            margin: 10px 0;
        }}

        button {{
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }}

        button:hover {{
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <h1>Web Widget Preview</h1>
    <div class="card">
        <p>This demonstrates theme integration in web-based widgets.</p>
        <button>Sample Button</button>
    </div>
    <div class="card">
        <p>Colors update when theme tokens change.</p>
    </div>
</body>
</html>
"""

    def get_relevant_tokens(self) -> list[str]:
        return [
            "editor.background",
            "editor.foreground",
            "button.background",
            "panel.border",
        ]

    def update_theme(self, widget: QWidget, theme: Theme):
        """Regenerate HTML with new theme."""
        web_view = widget  # QWebEngineView
        html = self._generate_themed_html(theme)
        web_view.setHtml(html)
```

**Token Coverage**: Varies by widget (10-30 tokens)
**Update Speed**: ~100ms (HTML regeneration + render)
**Interactivity**: Full (JavaScript works normally)

### 6.9 State Simulation Panel

**Purpose**: Force widgets into specific states for theme preview.

**Implementation**:
```python
class StateSimulationPanel(QWidget):
    """Panel to force widget states for preview."""

    state_changed = Signal(str)  # "normal", "hover", "pressed", "disabled"

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        # State buttons
        self.normal_btn = QPushButton("Normal")
        self.hover_btn = QPushButton("Hover")
        self.pressed_btn = QPushButton("Pressed")
        self.disabled_btn = QPushButton("Disabled")
        self.focus_btn = QPushButton("Focus")

        # Make exclusive (radio-like behavior)
        self.btn_group = QButtonGroup()
        for btn in [self.normal_btn, self.hover_btn, self.pressed_btn,
                    self.disabled_btn, self.focus_btn]:
            self.btn_group.addButton(btn)
            btn.setCheckable(True)
            layout.addWidget(btn)

        self.normal_btn.setChecked(True)

        # Connect signals
        self.btn_group.buttonClicked.connect(self._on_state_selected)

    def _on_state_selected(self, button: QPushButton):
        state = button.text().lower()
        self.state_changed.emit(state)
```

**State Application**:
```python
def apply_state(widget: QWidget, state: str):
    """Apply simulated state to widget."""

    if state == "normal":
        widget.setEnabled(True)
        widget.clearFocus()
        # Remove property overrides
        widget.setProperty("force_state", None)

    elif state == "hover":
        widget.setEnabled(True)
        # Set property that stylesheet can target
        widget.setProperty("force_state", "hover")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    elif state == "pressed":
        widget.setProperty("force_state", "pressed")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    elif state == "disabled":
        widget.setEnabled(False)

    elif state == "focus":
        widget.setEnabled(True)
        widget.setFocus()
```

**Stylesheet Support**:
```css
/* In generated stylesheet */
QPushButton[force_state="hover"] {
    background-color: #1177bb;  /* button.hoverBackground */
}

QPushButton[force_state="pressed"] {
    background-color: #0d5a99;  /* button.pressedBackground */
}
```

### 6.10 Preview Comparison Table

| Widget Type | Preview Method | Instance Type | Interactive | Update Speed | Token Count |
|-------------|---------------|---------------|-------------|--------------|-------------|
| **Standard Widgets** |
| Buttons | Direct Qt | QPushButton | Yes | <50ms | ~10 |
| Inputs | Direct Qt | QLineEdit | Yes | <50ms | ~8 |
| Lists | Direct Qt | QListWidget | Yes | <50ms | ~12 |
| Tables | Direct Qt | QTableWidget | Yes | <50ms | ~15 |
| Trees | Direct Qt | QTreeWidget | Yes | <50ms | ~12 |
| Scrollbars | Direct Qt | QScrollBar | Yes | <50ms | ~6 |
| Menus | Direct Qt | QMenu | Yes | <50ms | ~8 |
| **Tab Widgets** |
| Standard Tabs | Direct Qt | QTabWidget | Yes | <50ms | ~10 |
| Chrome Tabs | Embedded | ChromeTabbedWindow | Yes | <50ms | ~10 |
| **WebView Widgets** |
| Terminal | Embedded | TerminalWidget | Yes | ~50ms | 21 |
| Generic Web | Web embed | QWebEngineView | Yes | ~100ms | 10-30 |
| **Text Editors** |
| Plain Text | Direct Qt | QTextEdit | Yes | <50ms | ~10 |
| Code Editor | Direct Qt | QScintilla | Yes | <50ms | ~20 |
| **Complex Widgets** |
| Multisplit | Embedded | MultisplitWidget | Yes | <50ms | ~5 |
| Activity Bar | Custom | QWidget+Layout | Yes | <50ms | ~8 |
| Status Bar | Direct Qt | QStatusBar | Yes | <50ms | ~6 |
| Toolbar | Direct Qt | QToolBar | Yes | <50ms | ~8 |

**Total Token Coverage**: 200+ tokens across all widget types

### 6.11 Plugin Development Guide

**Creating Custom Preview Plugins**:

1. **Subclass PreviewPlugin**:
```python
from theme_studio.preview.plugin_system import PreviewPlugin
from vfwidgets_theme import Theme
from PySide6.QtWidgets import QWidget

class MyCustomPlugin(PreviewPlugin):
    def name(self) -> str:
        return "My Custom Widget"

    def create_preview(self, theme: Theme) -> QWidget:
        # Return your widget instance
        widget = MyCustomWidget()
        # Apply theme...
        return widget

    def get_relevant_tokens(self) -> list[str]:
        return ["list", "of", "token", "names"]

    def update_theme(self, widget: QWidget, theme: Theme):
        # Update widget with new theme
        widget.apply_new_theme(theme)
```

2. **Install Plugin**:
```bash
# Place in plugin directory
mkdir -p ~/.theme-studio/plugins/
cp my_plugin.py ~/.theme-studio/plugins/
```

3. **Plugin Discovery**:
VFTheme Studio automatically discovers plugins on startup from:
- Built-in plugins (always available)
- Installed VFWidgets packages (via import checks)
- `~/.theme-studio/plugins/*.py` (user plugins)

4. **Best Practices**:
- Use real widget instances (not mockups)
- Implement fast `update_theme()` (<100ms)
- List all tokens your widget uses
- Handle missing tokens gracefully
- Provide sample data that exercises all theme tokens

---

## 7. Technical Implementation

### 7.1 Preview Canvas Implementation

**Canvas Architecture:**
```python
class PreviewCanvas(QGraphicsView):
    """Zoomable, interactive preview canvas."""

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Zoom controls
        self._zoom_factor = 1.0
        self._zoom_min = 0.25
        self._zoom_max = 4.0

        # Grid
        self._show_grid = True
        self._grid_size = 20

        # Widget library
        self._widget_library = WidgetLibraryPalette()

    def wheelEvent(self, event):
        """Zoom with mouse wheel."""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.1 if delta > 0 else 0.9
            self.zoom(factor)

    def zoom(self, factor: float):
        """Zoom view by factor."""
        new_zoom = self._zoom_factor * factor
        if self._zoom_min <= new_zoom <= self._zoom_max:
            self._zoom_factor = new_zoom
            self.scale(factor, factor)
```

### 7.2 Token Browser Implementation

**Tree Model:**
```python
class TokenBrowserModel(QAbstractItemModel):
    """Tree model for token browser."""

    def __init__(self, theme: Theme):
        super().__init__()
        self._theme = theme
        self._root = self._build_tree()

    def _build_tree(self):
        """Build hierarchical token tree."""
        root = TokenTreeNode("Tokens (200)")

        # Category nodes
        for category in TokenCategory:
            category_node = TokenTreeNode(
                f"{category.value} ({len(tokens)})"
            )
            root.add_child(category_node)

            # Token nodes
            tokens = ColorTokenRegistry.get_tokens_by_category(category)
            for token in tokens:
                token_node = TokenTreeNode(
                    name=token.name,
                    value=self._theme.get(token.name),
                    modified=self._is_modified(token.name)
                )
                category_node.add_child(token_node)

        return root
```

### 7.3 Plugin System Implementation

**Plugin Discovery:**
```python
class PluginManager:
    """Manages preview plugins."""

    def __init__(self):
        self._plugins: dict[str, PreviewPlugin] = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Auto-discover and register plugins."""
        # Built-in plugin (always available)
        self.register(GenericWidgetsPlugin())

        # Optional VFWidgets plugins
        try:
            from vfwidgets_terminal import __version__
            self.register(TerminalWidgetPlugin())
        except ImportError:
            pass

        try:
            from vfwidgets_multisplit import __version__
            self.register(MultisplitWidgetPlugin())
        except ImportError:
            pass

        try:
            from chrome_tabbed_window import __version__
            self.register(ChromeTabbedWindowPlugin())
        except ImportError:
            pass

        # Third-party plugins from plugin directory
        plugin_dir = Path.home() / ".theme-studio" / "plugins"
        if plugin_dir.exists():
            self._load_external_plugins(plugin_dir)
```

---

## 8. Development Timeline

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Basic application structure and navigation

**Deliverables:**
- [ ] Project structure created
- [ ] Main window with 3-panel layout
- [ ] Token browser (read-only tree view)
- [ ] Preview canvas (static generic widgets)
- [ ] Inspector panel (view token properties)
- [ ] File operations (New, Open, Save, Save As)
- [ ] Theme document model

**Milestone:** Can open theme JSON, browse tokens, see static preview

### Phase 2: Interactive Editing (Weeks 3-4)
**Goal:** Enable token editing with real-time preview

**Deliverables:**
- [ ] Color picker widget
- [ ] Font selector widget
- [ ] Token editor in inspector
- [ ] Live preview updates on token change
- [ ] Undo/redo system
- [ ] Search/filter tokens
- [ ] Modified token indicators

**Milestone:** Can edit tokens and see live preview updates

### Phase 3: Plugin System (Weeks 5-6)
**Goal:** Support custom widget previews

**Deliverables:**
- [ ] Plugin base classes (PreviewPlugin ABC)
- [ ] Plugin discovery mechanism
- [ ] Generic widgets plugin
- [ ] Terminal widget plugin
- [ ] Multisplit widget plugin
- [ ] Chrome tabbed window plugin
- [ ] Plugin selector in preview panel
- [ ] Token filtering by active plugin

**Milestone:** Can preview terminal widget with live theme updates

### Phase 4: Advanced Preview (Weeks 7-8)
**Goal:** Professional preview capabilities

**Deliverables:**
- [ ] Zoomable canvas (25%-400%)
- [ ] Widget library palette
- [ ] Drag-drop widgets to canvas
- [ ] State simulation (hover, focus, pressed, disabled)
- [ ] Grid and snap-to-grid
- [ ] Preview export (PNG/SVG)
- [ ] Complete widget coverage (20+ types)

**Milestone:** Professional-grade preview with zoom and interaction

### Phase 5: Design Tools (Weeks 9-10)
**Goal:** Advanced token manipulation tools

**Deliverables:**
- [ ] Palette extractor (from images)
- [ ] Color harmonizer
- [ ] Bulk token operations
- [ ] Token diff viewer
- [ ] Theme comparison (side-by-side)
- [ ] Smart suggestions
- [ ] Copy/paste tokens

**Milestone:** Can extract palette from image and use design tools

### Phase 6: Export & Templates (Weeks 11-12)
**Goal:** Multi-format export and professional templates

**Deliverables:**
- [ ] Export to VFWidgets JSON
- [ ] Export to VS Code theme
- [ ] Export to CSS variables
- [ ] Export to Qt stylesheet
- [ ] Export to Python dict
- [ ] 10 built-in templates
- [ ] Template wizard
- [ ] Preview card generator
- [ ] Documentation generator

**Milestone:** Can export to 5+ formats and use templates

### Phase 7: Accessibility (Weeks 13-14)
**Goal:** WCAG validation and accessibility

**Deliverables:**
- [ ] Live contrast ratio calculation
- [ ] WCAG AA/AAA validation
- [ ] Accessibility report generation
- [ ] Auto-fix suggestions
- [ ] Colorblind simulation
- [ ] Validation panel
- [ ] Issue highlighting in token browser

**Milestone:** Full accessibility validation integrated

### Phase 8: Polish & Release (Weeks 15-16)
**Goal:** Production-ready release

**Deliverables:**
- [ ] Desktop integration (`.desktop`, icons)
- [ ] Build scripts (Linux, Windows, macOS)
- [ ] Installation scripts
- [ ] User documentation
- [ ] Developer documentation
- [ ] Tutorial videos
- [ ] Example themes
- [ ] Package for PyPI
- [ ] GitHub release

**Milestone:** v1.0.0 released on GitHub and PyPI

---

## 9. Non-Functional Requirements

### 9.1 Performance
- Theme loading: < 500ms for 200 tokens
- Preview update: < 100ms after token change
- Undo/redo: < 50ms
- Canvas zoom: 60 FPS
- Plugin loading: < 2s on startup

### 9.2 Usability
- Keyboard shortcuts for all major actions
- Tooltips on all UI elements
- Contextual help (F1 key)
- Responsive UI (no freezing)
- Auto-save (every 5 minutes)
- Crash recovery

### 9.3 Compatibility
- Python 3.9+
- PySide6 6.9+
- Linux (Ubuntu 20.04+, Fedora 35+)
- Windows 10/11
- macOS 11+

### 9.4 Extensibility
- Plugin API for custom widget previews
- Export format plugins
- Tool plugins
- Theme template packs

---

## 10. Future Enhancements (Post-v1.0)

### 10.1 Collaboration (v1.1)
- Multi-user editing (WebSocket sync)
- Comments on tokens
- Change approval workflow
- Team sharing

### 10.2 Theme Marketplace (v1.2)
- Browse community themes
- Upload/share themes
- Rating and reviews
- Theme collections

### 10.3 AI-Powered Features (v1.3)
- "Generate theme from description" (GPT integration)
- Automatic color harmony suggestions
- Accessibility auto-fix
- Theme naming suggestions

### 10.4 Integration (v1.4)
- Figma plugin (sync colors)
- Adobe XD integration
- VS Code extension
- CI/CD validation

---

## 11. Open Questions

1. **Theme Versioning**: How to handle theme format evolution?
2. **Plugin Security**: Sandboxing for third-party plugins?
3. **Large Themes**: Performance with custom tokens beyond 200?
4. **Offline Operation**: Should app work without internet?
5. **Localization**: Support for multiple languages?

---

## 12. References

- VFWidgets Theme System Documentation: `vfwidgets/widgets/theme_system/docs/`
- Qt Designer UX: https://doc.qt.io/qt-6/qtdesigner-manual.html
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- VS Code Theme Format: https://code.visualstudio.com/api/extension-guides/color-theme

---

**Document Status:** Living document, updated as design evolves
**Last Updated:** October 2025
**Next Review:** Start of Phase 1 implementation
