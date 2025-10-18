# GUI Theme Editor Design Document

**Status**: Design Phase
**Last Updated**: 2025-10-04
**Target**: VFWidgets Theme System 2.0
**Location**: `vfwidgets_theme.widgets.ThemeEditorDialog`

---

## Executive Summary

This document describes the design for a **reusable GUI Theme Editor** that will be integrated into the VFWidgets Theme System. The editor provides a visual interface for creating, editing, and managing themes with live preview, accessibility validation, and JSON import/export capabilities.

### Key Features

- 🎨 **Visual Token Editor** - Edit all 197 theme tokens with color pickers
- 👁️ **Live Preview** - Real-time preview with sample widgets
- 📊 **Category Organization** - Tokens grouped by component (Button, Input, Editor, etc.)
- ✅ **Accessibility Validation** - WCAG contrast ratio checking
- 📁 **Import/Export** - JSON theme files
- 🔄 **Theme Inheritance** - Extend built-in themes
- 🎯 **Reusable** - Available to all VFWidgets applications

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Specifications](#component-specifications)
3. [User Interface Design](#user-interface-design)
4. [Token Management](#token-management)
5. [Live Preview System](#live-preview-system)
6. [Accessibility Validation](#accessibility-validation)
7. [Import/Export](#importexport)
8. [Integration Patterns](#integration-patterns)
9. [Implementation Phases](#implementation-phases)
10. [API Reference](#api-reference)

---

## Architecture Overview

### Component Hierarchy

```
ThemeEditorDialog (QDialog)
└── ThemeEditorWidget (QWidget) - Embeddable widget
    ├── TokenBrowserWidget - Tree view of tokens by category
    ├── ColorEditorWidget - Color picker and value editor
    ├── ThemePreviewWidget - Live preview panel
    ├── ValidationPanel - Accessibility feedback
    └── ToolbarWidget - Save/Load/Reset/Export buttons
```

### Design Principles

1. **Reusability**: Part of `vfwidgets_theme` package, not ViloxTerm-specific
2. **Modularity**: Each component is independent and testable
3. **Extensibility**: Easy to add new token categories or validation rules
4. **Performance**: Efficient updates using signals/slots pattern
5. **Accessibility**: Built-in WCAG validation and contrast checking

### Dependencies

```python
# Existing VFWidgets Theme System Components
from vfwidgets_theme.core.theme import Theme, ThemeBuilder, ThemeValidator
from vfwidgets_theme.core.tokens import Tokens
from vfwidgets_theme.widgets.base import ThemedWidget
from vfwidgets_theme.widgets.dialogs import ThemePickerDialog
from vfwidgets_theme.widgets.helpers import ThemePreview

# Qt Components
from PySide6.QtWidgets import (
    QDialog, QWidget, QTreeWidget, QColorDialog,
    QSplitter, QToolBar, QFileDialog
)
from PySide6.QtCore import Signal, Slot
```

---

## Component Specifications

### 1. ThemeEditorDialog

**Purpose**: Modal dialog for theme editing
**File**: `src/vfwidgets_theme/widgets/theme_editor.py`

```python
class ThemeEditorDialog(QDialog):
    """Modal dialog for creating and editing themes.

    Features:
    - Full-screen or configurable size
    - OK/Cancel/Apply buttons
    - Auto-save on Apply
    - Revert on Cancel

    Example:
        >>> dialog = ThemeEditorDialog(base_theme="dark")
        >>> if dialog.exec():
        ...     custom_theme = dialog.get_theme()
        ...     app.load_custom_theme(custom_theme)
    """

    # Signals
    theme_changed = Signal(Theme)  # Emitted when theme is modified
    theme_saved = Signal(Theme)    # Emitted when theme is saved

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        base_theme: Union[str, Theme] = "dark",
        mode: str = "create"  # "create", "edit", "clone"
    ):
        """Initialize theme editor dialog."""

    def get_theme(self) -> Theme:
        """Get the current theme being edited."""

    def set_theme(self, theme: Union[str, Theme]) -> None:
        """Load a theme for editing."""

    def validate_theme(self) -> ValidationResult:
        """Validate current theme for accessibility."""
```

### 2. ThemeEditorWidget

**Purpose**: Embeddable theme editor (for settings panels)
**File**: Same as ThemeEditorDialog

```python
class ThemeEditorWidget(ThemedWidget, QWidget):
    """Embeddable theme editor widget.

    Can be embedded in:
    - Settings/Preferences dialogs
    - Tabbed settings panels
    - Custom theme management UIs

    Example:
        >>> settings_dialog = QDialog()
        >>> layout = QVBoxLayout(settings_dialog)
        >>>
        >>> theme_editor = ThemeEditorWidget()
        >>> layout.addWidget(theme_editor)
        >>>
        >>> settings_dialog.show()
    """

    # Signals
    theme_modified = Signal()      # Theme was changed
    validation_changed = Signal(ValidationResult)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        show_preview: bool = True,
        show_validation: bool = True
    ):
        """Initialize theme editor widget."""
```

### 3. TokenBrowserWidget

**Purpose**: Tree view for navigating theme tokens
**File**: `src/vfwidgets_theme/widgets/token_browser.py`

```python
class TokenBrowserWidget(ThemedWidget, QWidget):
    """Hierarchical browser for theme tokens.

    Organization:
    ├── 🎨 Base Colors (11 tokens)
    │   ├── colors.foreground
    │   ├── colors.background
    │   └── colors.primary
    ├── 🔘 Buttons (18 tokens)
    │   ├── Default
    │   │   ├── button.background
    │   │   └── button.foreground
    │   ├── States
    │   │   ├── button.hoverBackground
    │   │   └── button.pressedBackground
    │   └── Roles
    │       ├── button.danger.background
    │       └── button.success.background
    ├── 📝 Inputs (18 tokens)
    ├── 📄 Editor (35 tokens)
    ├── 📋 Lists/Trees (22 tokens)
    └── ... (10 more categories)
    """

    # Signals
    token_selected = Signal(str)  # Token ID selected
    token_modified = Signal(str, str)  # token_id, new_value

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize token browser."""

    def set_theme(self, theme: Theme) -> None:
        """Update browser with theme data."""

    def get_selected_token(self) -> Optional[str]:
        """Get currently selected token ID."""

    def filter_tokens(self, search: str) -> None:
        """Filter tokens by search string."""
```

**Token Categories**:

```python
TOKEN_CATEGORIES = {
    "Base Colors": {
        "icon": "🎨",
        "tokens": Tokens.COLORS_*,
        "count": 11
    },
    "Buttons": {
        "icon": "🔘",
        "subcategories": {
            "Default": ["background", "foreground", "border"],
            "States": ["hover", "pressed", "disabled"],
            "Roles": ["danger", "success", "warning", "secondary"]
        },
        "count": 18
    },
    "Inputs": {
        "icon": "📝",
        "tokens": Tokens.INPUT_*,
        "count": 18
    },
    # ... etc
}
```

### 4. ColorEditorWidget

**Purpose**: Edit token values with color and font pickers
**File**: `src/vfwidgets_theme/widgets/color_editor.py`

```python
class ColorEditorWidget(ThemedWidget, QWidget):
    """Color value editor with picker integration.

    Features:
    - QColorDialog integration
    - Hex color input (#RRGGBB)
    - RGBA support with alpha channel
    - Named color support (red, blue, etc.)
    - Real-time validation
    - Color preview swatch

    Layout:
    ┌─────────────────────────────────────┐
    │ Token: button.background            │
    │                                     │
    │ ┌─────┐  #0e639c         [Pick...] │
    │ │ ███ │  ──────────────             │
    │ └─────┘                             │
    │                                     │
    │ ✅ Valid hex color                  │
    │ ⚠️  Contrast ratio: 4.2:1 (Warning) │
    └─────────────────────────────────────┘
    """

    # Signals
    color_changed = Signal(str, str)  # token_id, color_value

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize color editor."""

    def set_token(self, token_id: str, current_value: str) -> None:
        """Set the token being edited."""

    def open_color_picker(self) -> None:
        """Open Qt color picker dialog."""

    def validate_color(self, color_str: str) -> bool:
        """Validate color format."""

class FontEditorWidget(ThemedWidget, QWidget):
    """Font value editor with font picker integration.

    Features:
    - QFontDialog integration
    - Font family dropdown with preview
    - Font size spinbox (6pt - 72pt)
    - Font weight selector
    - Real-time preview
    - Common font suggestions

    Layout:
    ┌─────────────────────────────────────┐
    │ Token: font.editor.family           │
    │                                     │
    │ Family: [Courier New ▼]  [Pick...] │
    │ Size:   [11pt      ▲▼]             │
    │ Weight: [Normal    ▼]               │
    │                                     │
    │ Preview:                            │
    │ ┌─────────────────────────────────┐ │
    │ │ The quick brown fox             │ │
    │ │ jumps over the lazy dog         │ │
    │ └─────────────────────────────────┘ │
    └─────────────────────────────────────┘
    """

    # Signals
    font_changed = Signal(str, str)  # token_id, font_value

    def set_token(self, token_id: str, current_value: str) -> None:
        """Set the font token being edited."""

    def open_font_picker(self) -> None:
        """Open Qt font picker dialog."""
```

### 5. ThemePreviewWidget

**Purpose**: Live preview of theme with sample widgets
**File**: `src/vfwidgets_theme/widgets/theme_preview.py` (extend existing)

```python
class ThemePreviewWidget(ThemedWidget, QWidget):
    """Live preview panel showing theme applied to widgets.

    Preview includes:
    - Buttons (default, primary, danger, success, disabled)
    - Text inputs (normal, focused, disabled)
    - Lists with selection
    - Tabs
    - Menus
    - Text editor
    - Scrollbars

    Layout:
    ┌──────────────────────────────────────┐
    │ Preview: my_custom_theme             │
    ├──────────────────────────────────────┤
    │ Buttons:                             │
    │ [Default] [Primary] [Danger] [Disabled] │
    │                                      │
    │ Inputs:                              │
    │ ┌──────────────┐ ┌──────────────┐   │
    │ │ Normal input │ │ Focused input│   │
    │ └──────────────┘ └──────────────┘   │
    │                                      │
    │ Editor:                              │
    │ ┌──────────────────────────────────┐ │
    │ │ 1  function example() {          │ │
    │ │ 2      return "syntax colors";   │ │
    │ │ 3  }                              │ │
    │ └──────────────────────────────────┘ │
    └──────────────────────────────────────┘
    """

    def update_preview(self, theme: Theme) -> None:
        """Update all preview widgets with new theme."""

    def add_sample_widget(self, widget: QWidget, label: str) -> None:
        """Add custom widget to preview."""
```

### 6. ValidationPanel

**Purpose**: Display accessibility validation results
**File**: `src/vfwidgets_theme/widgets/validation_panel.py`

```python
class ValidationPanel(ThemedWidget, QWidget):
    """Accessibility validation feedback panel.

    Features:
    - WCAG AA/AAA compliance checking
    - Contrast ratio calculations
    - Color blindness simulation warnings
    - Real-time validation as tokens change

    Layout:
    ┌─────────────────────────────────────┐
    │ Accessibility Validation            │
    ├─────────────────────────────────────┤
    │ ✅ WCAG AA Compliant                │
    │                                     │
    │ Checks:                             │
    │ ✅ Text contrast: 7.2:1 (AAA)       │
    │ ✅ Button contrast: 5.1:1 (AA)      │
    │ ⚠️  Input border: 2.8:1 (Warning)   │
    │ ❌ Disabled text: 2.1:1 (Fail)      │
    │                                     │
    │ [View Details] [Ignore Warnings]    │
    └─────────────────────────────────────┘
    """

    # Signals
    validation_updated = Signal(ValidationResult)

    def validate_theme(self, theme: Theme) -> ValidationResult:
        """Run full validation on theme."""

    def show_validation_details(self, issue: str) -> None:
        """Show detailed info about validation issue."""
```

---

## User Interface Design

### Main Dialog Layout

```
┌────────────────────────────────────────────────────────────────┐
│ Theme Editor - Editing: my_custom_theme                        │
├────────────────────────────────────────────────────────────────┤
│ ┌──────────────┬─────────────────┬───────────────────────────┐ │
│ │ Token        │ Editor          │ Preview                   │ │
│ │ Browser      │                 │                           │ │
│ │ ─────────    │ ─────────       │ ──────────                │ │
│ │              │                 │                           │ │
│ │ 🎨 Base      │ Token:          │ Buttons:                  │ │
│ │   Colors     │ button.bg       │ [Default] [Primary]       │ │
│ │   ├ fg       │                 │                           │ │
│ │   ├ bg       │ ┌───┐ #0e639c  │ Inputs:                   │ │
│ │   └ primary  │ │███│ ────────  │ ┌─────────┐              │ │
│ │              │ └───┘ [Pick...] │ │ Sample  │              │ │
│ │ 🔘 Buttons   │                 │ └─────────┘              │ │
│ │   ├ Default  │ Validation:     │                           │ │
│ │   ├ States   │ ✅ Valid color  │ Editor:                   │ │
│ │   └ Roles    │ ⚠️  Contrast:   │ ┌────────────┐           │ │
│ │      ├ danger│    4.2:1 (Low)  │ │ 1  code()  │           │ │
│ │      ├ success│                │ │ 2  {       │           │ │
│ │      └ warning│                │ └────────────┘           │ │
│ │              │                 │                           │ │
│ │ 📝 Inputs    │                 │                           │ │
│ │ ...          │                 │                           │ │
│ └──────────────┴─────────────────┴───────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│ Accessibility: ✅ WCAG AA   [View Report]                     │
├────────────────────────────────────────────────────────────────┤
│                    [Save] [Export JSON] [Reset] [Cancel] [OK]  │
└────────────────────────────────────────────────────────────────┘
```

### Compact Mode (Embeddable)

```
┌─────────────────────────────────────────┐
│ Theme Editor                            │
├─────────────────────────────────────────┤
│ ┌─────────────┬──────────────────────┐  │
│ │ Tokens      │ Editor & Preview     │  │
│ │ ──────      │ ───────────────      │  │
│ │             │                      │  │
│ │ 🎨 Base     │ Token: colors.bg     │  │
│ │ 🔘 Buttons  │ ┌─┐ #1e1e1e [Pick]  │  │
│ │ 📝 Inputs   │ └─┘                  │  │
│ │             │                      │  │
│ │             │ Preview:             │  │
│ │             │ [Button] [Input]     │  │
│ │             │                      │  │
│ └─────────────┴──────────────────────┘  │
├─────────────────────────────────────────┤
│ ✅ Valid   [Save] [Export] [Reset]      │
└─────────────────────────────────────────┘
```

---

## Token Management

### Token Organization Strategy

**Group by Visual Component** (not technical structure):

```python
COMPONENT_CATEGORIES = {
    "Base Colors": {
        "description": "Fundamental colors used throughout the theme",
        "tokens": [
            "colors.foreground",
            "colors.background",
            "colors.primary",
            "colors.secondary",
            "colors.focusBorder",
            # ... 11 total
        ],
        "icon": "🎨"
    },

    "Buttons": {
        "description": "Button appearances and states",
        "subcategories": {
            "Default State": [
                "button.background",
                "button.foreground",
                "button.border"
            ],
            "Interactive States": [
                "button.hoverBackground",
                "button.pressedBackground",
                "button.disabledBackground"
            ],
            "Semantic Roles": [
                "button.danger.background",
                "button.success.background",
                "button.warning.background",
                "button.secondary.background"
            ]
        },
        "icon": "🔘"
    },

    # ... more categories
}
```

### Token Search and Filtering

```python
class TokenSearchEngine:
    """Search and filter tokens by various criteria."""

    def search(self, query: str) -> List[str]:
        """Search by token name, category, or description."""
        # "button" → all button.* tokens
        # "danger" → all *.danger.* tokens
        # "background" → all *background* tokens

    def filter_by_category(self, category: str) -> List[str]:
        """Get all tokens in a category."""

    def filter_by_validation_status(
        self,
        status: str  # "valid", "warning", "error"
    ) -> List[str]:
        """Get tokens with validation issues."""
```

---

## Live Preview System

### Preview Widget Generator

Auto-generate sample widgets for each token category:

```python
class PreviewGenerator:
    """Generate preview widgets for token categories."""

    def generate_button_preview(self, theme: Theme) -> QWidget:
        """Generate button preview panel."""
        # Creates: Default, Primary, Danger, Success, Disabled buttons

    def generate_input_preview(self, theme: Theme) -> QWidget:
        """Generate input field preview."""
        # Creates: Normal, Focused, Disabled inputs

    def generate_editor_preview(self, theme: Theme) -> QWidget:
        """Generate text editor preview with syntax highlighting."""

    def generate_list_preview(self, theme: Theme) -> QWidget:
        """Generate list/tree preview with selections."""
```

### Real-time Update Strategy

```python
class LivePreviewController:
    """Manages real-time preview updates."""

    def __init__(self, preview_widget: ThemePreviewWidget):
        self._preview = preview_widget
        self._update_timer = QTimer()
        self._update_timer.setInterval(300)  # 300ms debounce
        self._update_timer.timeout.connect(self._apply_preview)

    def token_changed(self, token_id: str, value: str) -> None:
        """Handle token value change."""
        # Debounce updates to avoid flicker
        self._pending_changes[token_id] = value
        self._update_timer.start()

    def _apply_preview(self) -> None:
        """Apply pending changes to preview."""
        # Build temporary theme
        # Apply to preview widgets
        # Clear pending changes
```

---

## Accessibility Validation

### WCAG Compliance Checking

```python
class AccessibilityValidator:
    """Validate theme accessibility compliance."""

    WCAG_AA_TEXT = 4.5  # Minimum contrast ratio
    WCAG_AA_LARGE_TEXT = 3.0
    WCAG_AAA_TEXT = 7.0

    def validate_contrast_ratio(
        self,
        foreground: str,
        background: str,
        wcag_level: str = "AA"
    ) -> ValidationResult:
        """Calculate and validate contrast ratio."""

    def validate_theme(self, theme: Theme) -> ValidationReport:
        """Full theme accessibility validation."""
        return ValidationReport(
            level="AA",  # or "AAA"
            passed=[
                "Text contrast: 7.2:1 (AAA)",
                "Button contrast: 5.1:1 (AA)"
            ],
            warnings=[
                "Input border: 2.8:1 (Below AA)"
            ],
            errors=[
                "Disabled text: 2.1:1 (Fail)"
            ]
        )

    def suggest_fix(self, token_id: str, issue: str) -> List[str]:
        """Suggest color adjustments to fix issue."""
        # Returns list of suggested color values
```

### Color Contrast Calculation

```python
def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Formula:
        ratio = (L1 + 0.05) / (L2 + 0.05)
        where L1 is lighter, L2 is darker

    Returns:
        Float from 1.0 (no contrast) to 21.0 (maximum)
    """

def relative_luminance(color: str) -> float:
    """Calculate relative luminance of a color.

    Formula from WCAG 2.1:
        L = 0.2126 * R + 0.7152 * G + 0.0722 * B
        (where R, G, B are linearized)
    """
```

---

## Import/Export

### JSON Theme Format

```json
{
  "name": "my_custom_theme",
  "version": "1.0.0",
  "type": "dark",
  "metadata": {
    "description": "My custom theme",
    "author": "User Name",
    "created": "2025-10-04T18:00:00Z"
  },
  "colors": {
    "colors.foreground": "#e0e0e0",
    "colors.background": "#1e1e1e",
    "button.background": "#0e639c",
    "button.foreground": "#ffffff"
  }
}
```

### Import/Export Implementation

```python
class ThemeImportExport:
    """Handle theme import/export operations."""

    def export_theme(
        self,
        theme: Theme,
        filepath: Path,
        format: str = "json"  # Future: "yaml", "toml"
    ) -> bool:
        """Export theme to file."""

    def import_theme(
        self,
        filepath: Path,
        validate: bool = True
    ) -> Theme:
        """Import theme from file."""

    def export_partial(
        self,
        theme: Theme,
        tokens: List[str]
    ) -> str:
        """Export only specified tokens (for sharing color palettes)."""
```

---

## Integration Patterns

### Pattern 1: Standalone Dialog (ViloxTerm)

```python
from vfwidgets_theme.widgets import ThemeEditorDialog

# Open theme editor from menu
def on_edit_theme_action():
    dialog = ThemeEditorDialog(
        parent=main_window,
        base_theme="dark",  # Current theme
        mode="edit"
    )

    if dialog.exec():
        custom_theme = dialog.get_theme()
        app.load_custom_theme(custom_theme)
        app.set_theme(custom_theme.name)
```

### Pattern 2: Embedded in Settings

```python
from vfwidgets_theme.widgets import ThemeEditorWidget

# Add to settings dialog
settings_dialog = QDialog()
tabs = QTabWidget()

# Appearance tab
appearance_tab = QWidget()
layout = QVBoxLayout(appearance_tab)

theme_editor = ThemeEditorWidget(
    show_preview=True,
    show_validation=True
)
layout.addWidget(theme_editor)

tabs.addTab(appearance_tab, "Appearance")
```

### Pattern 3: Quick Theme Customization

```python
# Minimal editor for quick color tweaks
from vfwidgets_theme.widgets import QuickThemeEditor

editor = QuickThemeEditor(
    tokens_to_edit=[
        "colors.primary",
        "button.background",
        "input.background"
    ]
)

if editor.exec():
    app.apply_custom_colors(editor.get_colors())
```

---

## Undo/Redo System

### Command Pattern Implementation

```python
from dataclasses import dataclass
from typing import Any, List

@dataclass
class ThemeEditCommand:
    """Represents a single theme edit operation."""
    token_id: str
    old_value: Any
    new_value: Any
    timestamp: float

class UndoRedoManager:
    """Manages undo/redo history for theme edits."""

    def __init__(self, max_history: int = 100):
        self._undo_stack: List[ThemeEditCommand] = []
        self._redo_stack: List[ThemeEditCommand] = []
        self._max_history = max_history

    def execute_command(self, command: ThemeEditCommand) -> None:
        """Execute a command and add to undo stack."""
        self._undo_stack.append(command)
        self._redo_stack.clear()  # Clear redo on new edit

        # Limit stack size
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self) -> Optional[ThemeEditCommand]:
        """Undo last command."""
        if not self._undo_stack:
            return None

        command = self._undo_stack.pop()
        self._redo_stack.append(command)
        return command

    def redo(self) -> Optional[ThemeEditCommand]:
        """Redo last undone command."""
        if not self._redo_stack:
            return None

        command = self._redo_stack.pop()
        self._undo_stack.append(command)
        return command

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def get_undo_history(self) -> List[str]:
        """Get list of undoable actions."""
        return [f"Change {cmd.token_id}" for cmd in self._undo_stack]
```

### Keyboard Shortcuts

```python
# Standard shortcuts
Ctrl+Z - Undo
Ctrl+Shift+Z - Redo (or Ctrl+Y)
Ctrl+S - Save theme
Ctrl+E - Export theme
Ctrl+O - Open/Import theme
Ctrl+N - New theme (from current)
Ctrl+F - Search tokens
Esc - Cancel/Close dialog
```

---

## Theme Comparison View

### Side-by-Side Comparison Widget

```python
class ThemeComparisonWidget(ThemedWidget, QWidget):
    """Compare two themes side-by-side.

    Use Cases:
    - See changes when extending a theme
    - Compare custom theme with built-in
    - Review before/after edits

    Layout:
    ┌─────────────────────────────────────────────────┐
    │ Compare Themes                                  │
    ├─────────────────────────────────────────────────┤
    │ Theme A: [dark      ▼]  Theme B: [my_custom ▼] │
    ├────────────────────┬────────────────────────────┤
    │ Token             │ Theme A    │ Theme B       │
    ├────────────────────┼────────────┼───────────────┤
    │ colors.background │ #1e1e1e    │ #2a1438  ⚠️  │
    │ button.background │ #0e639c    │ #7b2cbf  ✓   │
    │ input.background  │ #2d2d2d    │ #2d2d2d       │
    └────────────────────┴────────────┴───────────────┘

    Legend:
    ⚠️  - Value differs
    ✓  - Changed from Theme A
    """

    def set_themes(self, theme_a: Theme, theme_b: Theme) -> None:
        """Set themes to compare."""

    def highlight_differences(self) -> List[str]:
        """Get list of tokens with different values."""

    def export_diff(self) -> Dict[str, Tuple[str, str]]:
        """Export differences as dict."""
```

---

## Batch Token Editing

### Multi-Token Operations

```python
class BatchTokenEditor(ThemedWidget, QWidget):
    """Edit multiple related tokens at once.

    Features:
    - Select tokens by pattern (e.g., all *.hover*)
    - Apply color transformation to selected tokens
    - Bulk find/replace
    - Copy values between token groups

    Example Operations:
    - "Make all hover states 10% lighter"
    - "Set all disabled foregrounds to gray"
    - "Copy button.* colors to input.*"
    """

    def select_tokens_by_pattern(self, pattern: str) -> List[str]:
        """Select tokens matching pattern.

        Examples:
            *.hover* - All hover states
            button.* - All button tokens
            *.background - All background colors
        """

    def apply_transformation(
        self,
        tokens: List[str],
        transformation: str  # "lighten(10%)", "darken(20%)", "opacity(50%)"
    ) -> None:
        """Apply color transformation to selected tokens."""

    def batch_replace(
        self,
        tokens: List[str],
        find: str,
        replace: str
    ) -> int:
        """Replace value in selected tokens."""
```

---

## Color Palette Management

### Palette-Based Theming

```python
class ThemePaletteManager:
    """Manage color palettes and aliases.

    Benefits:
    - Define base palette once
    - Reference palette colors in tokens
    - Change palette color updates all references
    - Ensures color consistency

    Example:
        palette = {
            "$primary": "#007acc",
            "$danger": "#dc3545",
            "$success": "#28a745"
        }

        theme = ThemeBuilder("my_theme")
            .set_palette(palette)
            .add_color("button.background", "$primary")
            .add_color("button.danger.background", "$danger")
            .build()
    """

    def define_palette(self, palette: Dict[str, str]) -> None:
        """Define base color palette."""

    def resolve_aliases(self, theme: Theme) -> Theme:
        """Resolve $alias references to actual colors."""

    def extract_palette(self, theme: Theme) -> Dict[str, str]:
        """Extract commonly used colors as palette."""

    def suggest_palette(self, primary_color: str) -> Dict[str, str]:
        """Generate complementary palette from primary color."""
```

### Palette Generation Tools

```python
class PaletteGenerator:
    """Generate color palettes using color theory."""

    def generate_analogous(self, base: str) -> List[str]:
        """Generate analogous colors (adjacent on color wheel)."""

    def generate_complementary(self, base: str) -> List[str]:
        """Generate complementary colors (opposite on wheel)."""

    def generate_triadic(self, base: str) -> List[str]:
        """Generate triadic colors (evenly spaced on wheel)."""

    def generate_monochromatic(
        self,
        base: str,
        steps: int = 5
    ) -> List[str]:
        """Generate monochromatic palette (tints/shades)."""

    def extract_from_image(self, image_path: Path) -> Dict[str, str]:
        """Extract color palette from image (future)."""
```

---

## Keyboard Shortcuts & KeybindingManager Integration

### Editor Shortcuts

```python
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

class ThemeEditorKeyBindings:
    """Theme editor keyboard shortcuts."""

    def setup_keybindings(self, manager: KeybindingManager) -> None:
        """Register theme editor shortcuts."""
        manager.register_actions([
            # File operations
            ActionDefinition(
                id="theme.save",
                description="Save Theme",
                default_shortcut="Ctrl+S",
                category="Theme Editor",
                callback=self.save_theme
            ),
            ActionDefinition(
                id="theme.export",
                description="Export Theme",
                default_shortcut="Ctrl+E",
                category="Theme Editor"
            ),
            ActionDefinition(
                id="theme.import",
                description="Import Theme",
                default_shortcut="Ctrl+O",
                category="Theme Editor"
            ),

            # Edit operations
            ActionDefinition(
                id="theme.undo",
                description="Undo",
                default_shortcut="Ctrl+Z",
                category="Theme Editor",
                callback=self.undo_manager.undo
            ),
            ActionDefinition(
                id="theme.redo",
                description="Redo",
                default_shortcut="Ctrl+Shift+Z",
                category="Theme Editor",
                callback=self.undo_manager.redo
            ),

            # Navigation
            ActionDefinition(
                id="theme.search_tokens",
                description="Search Tokens",
                default_shortcut="Ctrl+F",
                category="Theme Editor",
                callback=self.focus_search
            ),
            ActionDefinition(
                id="theme.next_token",
                description="Next Token",
                default_shortcut="Ctrl+Down",
                category="Theme Editor"
            ),
            ActionDefinition(
                id="theme.prev_token",
                description="Previous Token",
                default_shortcut="Ctrl+Up",
                category="Theme Editor"
            ),

            # Preview
            ActionDefinition(
                id="theme.toggle_preview",
                description="Toggle Preview",
                default_shortcut="Ctrl+P",
                category="Theme Editor"
            ),

            # Quick actions
            ActionDefinition(
                id="theme.pick_color",
                description="Open Color Picker",
                default_shortcut="Ctrl+K",
                category="Theme Editor"
            ),
            ActionDefinition(
                id="theme.reset_token",
                description="Reset Token to Default",
                default_shortcut="Ctrl+R",
                category="Theme Editor"
            ),
        ])
```

---

## Token Documentation & Tooltips

### Interactive Token Help

```python
class TokenDocumentationProvider:
    """Provide documentation and help for theme tokens."""

    TOKEN_DOCS = {
        "colors.foreground": {
            "description": "Default text color throughout the application",
            "affects": ["All text elements", "Menu items", "Labels"],
            "related": ["colors.background", "editor.foreground"],
            "example_widgets": ["QLabel", "QMenu", "QPushButton text"],
            "wcag_pair": "colors.background"
        },
        "button.background": {
            "description": "Background color for buttons in default state",
            "affects": ["QPushButton", "QToolButton"],
            "related": [
                "button.foreground",
                "button.hoverBackground",
                "button.pressedBackground"
            ],
            "example_widgets": ["QPushButton"],
            "wcag_pair": "button.foreground"
        },
        # ... all 197 tokens documented
    }

    def get_tooltip(self, token_id: str) -> str:
        """Get tooltip text for token."""
        doc = self.TOKEN_DOCS.get(token_id, {})
        return f"""
        {token_id}

        {doc.get('description', 'No description available')}

        Affects:
        {chr(10).join('  • ' + a for a in doc.get('affects', []))}

        Related tokens:
        {', '.join(doc.get('related', []))}
        """

    def highlight_in_preview(self, token_id: str) -> None:
        """Highlight preview widgets affected by this token."""
        # Flash/animate widgets using this token

    def show_affected_widgets(self, token_id: str) -> List[str]:
        """Get list of widget types affected by token."""
        return self.TOKEN_DOCS.get(token_id, {}).get("example_widgets", [])
```

### "Show Me" Feature

```python
class TokenPreviewHighlighter:
    """Highlight where tokens are used in preview."""

    def highlight_token_usage(self, token_id: str) -> None:
        """Highlight all widgets using this token in preview.

        Visual feedback:
        - Flash affected widgets
        - Draw border around them
        - Show tooltip with token name
        """

    def create_visual_map(self) -> None:
        """Create interactive map of token usage.

        Click on any preview widget to see which tokens affect it.
        """
```

---

## Theme Migration & Versioning

### Version Migration System

```python
class ThemeMigration:
    """Handle theme migrations between schema versions."""

    MIGRATIONS = {
        "1.0.0 -> 2.0.0": {
            "renamed_tokens": {
                "button.color": "button.foreground",
                "input.color": "input.foreground"
            },
            "removed_tokens": ["deprecated.token"],
            "added_tokens": {
                "button.success.background": "#28a745"
            }
        }
    }

    def migrate_theme(
        self,
        theme: Theme,
        target_version: str
    ) -> Theme:
        """Migrate theme to target version."""

    def check_compatibility(
        self,
        theme: Theme,
        current_version: str
    ) -> CompatibilityReport:
        """Check if theme needs migration."""
        return CompatibilityReport(
            compatible=True,
            missing_tokens=["new.token.added"],
            deprecated_tokens=["old.token.removed"],
            migration_needed=False
        )

    def auto_upgrade(self, theme: Theme) -> Theme:
        """Automatically upgrade theme to latest version."""
```

---

## Error Handling & Recovery

### Robust Error Management

```python
class ThemeEditorErrorHandler:
    """Handle errors and provide recovery options."""

    def handle_corrupted_file(self, filepath: Path) -> Theme:
        """Attempt to recover corrupted theme file.

        Strategies:
        1. Try to parse as JSON and recover partial data
        2. Offer to load from backup
        3. Create new theme with recovered tokens
        """

    def enable_autosave(self, interval: int = 60) -> None:
        """Enable autosave every N seconds."""
        self._autosave_timer = QTimer()
        self._autosave_timer.setInterval(interval * 1000)
        self._autosave_timer.timeout.connect(self._autosave)

    def _autosave(self) -> None:
        """Autosave current theme to temp file."""
        temp_file = Path.home() / ".vfwidgets" / "autosave" / "theme.json"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        self.export_theme(temp_file)

    def recover_from_crash(self) -> Optional[Theme]:
        """Check for autosave and offer recovery."""
        autosave_file = Path.home() / ".vfwidgets" / "autosave" / "theme.json"
        if autosave_file.exists():
            # Show recovery dialog
            return self.import_theme(autosave_file)
        return None

    def validate_before_save(self, theme: Theme) -> ValidationResult:
        """Comprehensive validation before saving."""
        errors = []

        # Check required tokens
        if not theme.get("colors.background"):
            errors.append("Missing required token: colors.background")

        # Check color format
        for token_id, value in theme.colors.items():
            if not self._is_valid_color(value):
                errors.append(f"Invalid color format: {token_id} = {value}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
```

---

## ViloxTerm Integration

### Menu Integration

```python
# In ViloxTerm's menu button
from vfwidgets_theme.widgets import ThemeEditorDialog

class ViloxTermMenuButton:
    """Menu button with theme editor integration."""

    def create_theme_menu(self) -> QMenu:
        """Create theme submenu."""
        theme_menu = QMenu("Theme")

        # Theme selection
        select_action = theme_menu.addAction("Select Theme...")
        select_action.triggered.connect(self._on_select_theme)

        theme_menu.addSeparator()

        # Theme editor - NEW
        edit_action = theme_menu.addAction("Edit Current Theme...")
        edit_action.setShortcut("Ctrl+Shift+T")
        edit_action.triggered.connect(self._on_edit_theme)

        create_action = theme_menu.addAction("Create New Theme...")
        create_action.triggered.connect(self._on_create_theme)

        theme_menu.addSeparator()

        # Import/Export
        import_action = theme_menu.addAction("Import Theme...")
        import_action.triggered.connect(self._on_import_theme)

        export_action = theme_menu.addAction("Export Theme...")
        export_action.triggered.connect(self._on_export_theme)

        return theme_menu

    def _on_edit_theme(self) -> None:
        """Open theme editor for current theme."""
        app = ThemedApplication.instance()
        current_theme = app.get_current_theme()

        editor = ThemeEditorDialog(
            parent=self.parent(),
            base_theme=current_theme,
            mode="edit"
        )

        if editor.exec():
            custom_theme = editor.get_theme()
            app.load_custom_theme(custom_theme)
            app.set_theme(custom_theme.name)

    def _on_create_theme(self) -> None:
        """Create new theme from scratch."""
        editor = ThemeEditorDialog(
            parent=self.parent(),
            base_theme="dark",
            mode="create"
        )

        if editor.exec():
            custom_theme = editor.get_theme()
            # Save to user themes directory
            self._save_user_theme(custom_theme)
```

---

## Developer Experience (DX) Features

### 1. Code Generation

```python
class ThemeCodeGenerator:
    """Generate code from visual theme editor.

    Features:
    - Export theme as Python code (ThemeBuilder)
    - Generate TypeScript definitions
    - Create CSS variables
    - Export as QSS stylesheet
    """

    def generate_python_code(self, theme: Theme) -> str:
        """Generate Python ThemeBuilder code."""
        return f'''
from vfwidgets_theme import ThemeBuilder, Tokens

{theme.name}_theme = (ThemeBuilder("{theme.name}")
    .set_type("{theme.type}")
    .add_metadata("description", "{theme.metadata.get('description', '')}")

    # Base colors
    .add_color(Tokens.COLORS_FOREGROUND, "{theme.get('colors.foreground')}")
    .add_color(Tokens.COLORS_BACKGROUND, "{theme.get('colors.background')}")
    # ... more tokens ...

    .build())
'''

    def generate_typescript_types(self, theme: Theme) -> str:
        """Generate TypeScript type definitions."""
        return f'''
export interface {theme.name.title()}Theme {{
    colors: {{
        foreground: string;
        background: string;
        // ... more tokens ...
    }};
}}
'''

    def generate_css_variables(self, theme: Theme) -> str:
        """Generate CSS custom properties."""
        return f'''
:root {{
    --color-foreground: {theme.get('colors.foreground')};
    --color-background: {theme.get('colors.background')};
    /* ... more tokens ... */
}}
'''
```

### 2. Theme Template System

```python
class ThemeTemplateLibrary:
    """Pre-built theme templates for quick start.

    Templates:
    - Material Design (Light/Dark)
    - Flat Design
    - Solarized (Light/Dark)
    - Nord
    - Dracula
    - One Dark
    - GitHub (Light/Dark)
    """

    def get_template(self, name: str) -> Theme:
        """Get theme template by name."""

    def list_templates(self) -> List[str]:
        """List available templates."""

    def create_from_template(
        self,
        template: str,
        customizations: Dict[str, str]
    ) -> Theme:
        """Create theme from template with customizations."""
```

### 3. Interactive Tutorials

```python
class ThemeEditorTutorial:
    """Interactive tutorial system for theme editor.

    Tutorials:
    1. "Your First Custom Theme" (5 min)
    2. "Understanding Token Categories" (10 min)
    3. "Accessibility Best Practices" (10 min)
    4. "Advanced: Palette Management" (15 min)
    """

    def start_tutorial(self, tutorial_id: str) -> None:
        """Start interactive tutorial with step-by-step guidance."""

    def show_quick_tips(self) -> None:
        """Show context-sensitive quick tips."""
```

### 4. Theme Validation & Linting

```python
class ThemeLinter:
    """Lint themes for best practices and common issues.

    Checks:
    - Accessibility (contrast ratios)
    - Consistency (similar tokens should have similar values)
    - Completeness (all essential tokens defined)
    - Naming conventions (for custom tokens)
    - Performance (no duplicate color definitions)
    """

    def lint_theme(self, theme: Theme) -> LintReport:
        """Run all lint checks on theme."""
        return LintReport(
            errors=[
                "Missing required token: editor.background"
            ],
            warnings=[
                "Inconsistent hover states: some are 10% lighter, some 20%"
            ],
            suggestions=[
                "Consider using palette aliases for repeated colors"
            ],
            score=85  # Overall quality score
        )
```

### 5. Developer Documentation Generator

```python
class ThemeDocGenerator:
    """Generate documentation from theme.

    Outputs:
    - README.md with theme overview
    - Token reference table
    - Preview screenshots
    - Usage examples
    """

    def generate_readme(self, theme: Theme) -> str:
        """Generate README.md for theme."""

    def generate_preview_images(self, theme: Theme) -> List[Path]:
        """Generate preview screenshots of theme."""

    def generate_usage_examples(self, theme: Theme) -> str:
        """Generate code examples using theme."""
```

### 6. Hot Reload Support

```python
class ThemeHotReload:
    """Watch theme file and auto-reload on changes.

    Useful for development:
    1. Edit theme in external editor
    2. Save file
    3. Theme auto-reloads in running app
    """

    def enable_hot_reload(self, theme_file: Path) -> None:
        """Enable hot reload for theme file."""
        self._watcher = QFileSystemWatcher([str(theme_file)])
        self._watcher.fileChanged.connect(self._on_file_changed)

    def _on_file_changed(self, path: str) -> None:
        """Reload theme when file changes."""
        try:
            new_theme = self.import_theme(Path(path))
            ThemedApplication.instance().set_theme(new_theme.name)
        except Exception as e:
            logger.error(f"Hot reload failed: {e}")
```

### 7. Theme Testing Framework

```python
class ThemeTestSuite:
    """Automated testing for themes.

    Tests:
    - All widgets render correctly
    - No visual regressions
    - Accessibility compliance
    - Cross-platform consistency
    """

    def test_all_widgets(self, theme: Theme) -> TestReport:
        """Test theme with all Qt widgets."""

    def visual_regression_test(
        self,
        theme: Theme,
        baseline: Theme
    ) -> DiffReport:
        """Compare visual rendering with baseline."""

    def screenshot_test(self, theme: Theme) -> List[Path]:
        """Generate screenshots for all widget types."""
```

---

## Implementation Phases

**Implementation Strategy**: Build new UI components while leveraging existing theme system infrastructure. Phases 3-5 are accelerated by reusing validation, preview, and persistence systems already in place.

### Quick Reference: What Exists vs What to Build

**Already Implemented (Leverage)** ✅:
- `ThemeBuilder` - Fluent theme construction API
- `Theme` - Immutable, validated theme model
- `ThemeValidator` - Color/schema validation
- `ThemePreview` - Preview with commit/cancel
- `ValidationFramework` - Runtime validation
- `persistence/storage.py` - Theme file management
- `development/hot_reload.py` - Hot reload system
- `ThemedWidget/Application` - Widget theming
- `ColorProperty/FontProperty` - Property descriptors
- `KeybindingManager` - Keyboard shortcuts

**New Components to Build** 🔨:
- `ThemeEditorDialog` - Main dialog wrapper
- `ThemeEditorWidget` - Embeddable editor
- `TokenBrowserWidget` - Token tree view (197 tokens)
- `ColorEditorWidget` - Visual color picker
- `FontEditorWidget` - Font selection UI
- `ValidationPanel` - WCAG compliance display
- Sample widget generator - Preview samples
- UndoRedoManager - Command pattern undo/redo
- Batch editor - Multi-token operations
- Palette manager - Color palette system
- Code generator - Export Python/TS/CSS

---

### Phase 1: Core Infrastructure (Week 1)

**Goals**: Basic framework and token browser

**Build New** 🔨:
1. Create `ThemeEditorWidget` base structure
2. Implement `TokenBrowserWidget` with tree view (197 tokens organized by category)
3. Add token selection and navigation signals
4. Build token search/filter UI

**Leverage Existing** ✅:
- `ThemeBuilder` - Fluent API for theme construction
- `Theme` - Immutable theme model with validation
- Token constants from `core/token_constants.py`
- `ThemedWidget` base class for editor UI

**Deliverables**:
- ✅ Working token browser with categories (colors, button, input, editor, etc.)
- ✅ Token selection signals (token_selected, category_changed)
- ✅ Search/filter functionality
- ✅ Integration with ThemeBuilder API

---

### Phase 2: Visual Editors (Week 1-2)

**Goals**: Color and font editing widgets

**Build New** 🔨:
1. Create `ColorEditorWidget` with Qt color picker
2. Create `FontEditorWidget` with font selection
3. Build hex/rgb/rgba input fields with validation UI
4. Implement color preview swatches
5. Connect editors to token browser selection

**Leverage Existing** ✅:
- `ThemeValidator` - Color format validation (hex, rgb, rgba, hsl)
- `ColorProperty` descriptor - Type-safe color properties
- `FontProperty` descriptor - Type-safe font properties
- `QColorDialog`, `QFontDialog` - Qt's native pickers

**Deliverables**:
- ✅ Visual color picker with format validation
- ✅ Font selection with preview
- ✅ Live token updates
- ✅ Format conversion (hex ↔ rgb ↔ rgba)

---

### Phase 3: Live Preview (Week 2) ⚡ ACCELERATED

**Goals**: Real-time theme preview with sample widgets

**Build New** 🔨:
1. Create sample widget generator (buttons, inputs, tabs, editor, menus)
2. Build preview panel layout
3. Implement preview update debouncing (300ms)
4. Add sample code editor with syntax highlighting

**Leverage Existing** ✅:
- `ThemePreview` class - Commit/cancel preview system (widgets/helpers.py)
- `ThemedWidget` - Automatic theme application to widgets
- `ThemedApplication.set_theme()` - Real-time theme switching
- Hot reload system (`development/hot_reload.py`)

**Deliverables**:
- ✅ Live preview panel with sample widgets
- ✅ Real-time updates (< 300ms)
- ✅ Preview shows: buttons, inputs, tabs, lists, editor
- ✅ Debounced updates for performance

**Why Faster**: Preview infrastructure already exists - just need to generate sample widgets and connect signals!

---

### Phase 4: Validation UI (Week 2-3) ⚡ ACCELERATED

**Goals**: Accessibility validation display

**Build New** 🔨:
1. Create `ValidationPanel` UI widget
2. Build WCAG compliance display (AA/AAA badges)
3. Design validation error/warning list
4. Add auto-fix suggestions UI
5. Implement "Show Me" feature (highlight problematic tokens)

**Leverage Existing** ✅:
- `ThemeValidator` - Schema and color validation (core/theme.py)
- `ValidationFramework` - Runtime validation system (validation/)
- `ValidationResult` - Error/warning data structures
- Color contrast validation patterns (already implemented)

**Deliverables**:
- ✅ Visual validation panel with error/warning list
- ✅ WCAG AA/AAA compliance badges
- ✅ Contrast ratio calculations displayed
- ✅ Auto-fix suggestions (clickable)

**Why Faster**: Validation logic exists - just need UI to display results!

---

### Phase 5: Import/Export UI (Week 3) ⚡ ACCELERATED

**Goals**: Theme file management

**Build New** 🔨:
1. Add file dialog integration (QFileDialog)
2. Create import wizard with error display
3. Build export options dialog (JSON, Python, CSS)
4. Design theme library browser UI
5. Add "Save as..." and "Load" toolbar buttons

**Leverage Existing** ✅:
- `Theme.from_json()` / `to_json()` - Serialization (core/theme.py)
- `ThemeValidator.validate()` - Import validation
- `persistence/storage.py` - Theme file management
- `ThemeRepository` - Theme discovery and loading

**Deliverables**:
- ✅ Import/Export file dialogs
- ✅ Validation error display on import
- ✅ Theme library browser
- ✅ Multi-format export (JSON, Python code)

**Why Faster**: Serialization and persistence already implemented - just add file dialog UI!

---

### Phase 6: Dialog Integration (Week 3-4)

**Goals**: Complete dialog wrapper and app integration

**Build New** 🔨:
1. Create `ThemeEditorDialog` wrapper class
2. Implement OK/Cancel/Apply button logic
3. Add theme revert on cancel (restore original)
4. Build ViloxTerm menu integration ("Edit Theme...")
5. Create integration examples (standalone, embedded, quick-edit)

**Leverage Existing** ✅:
- `ThemedDialog` - Base dialog class
- `ThemePreview.commit()/cancel()` - Preview state management
- `KeybindingManager` - Keyboard shortcuts (Ctrl+S, Ctrl+Z)
- Signal/slot system for theme changes

**Deliverables**:
- ✅ Complete `ThemeEditorDialog` (modal)
- ✅ Embeddable `ThemeEditorWidget` (for settings pages)
- ✅ ViloxTerm integration (menu item, keyboard shortcuts)
- ✅ Working examples (12_*.py, 13_*.py, 14_*.py)

---

### Phase 7: Advanced Features (Week 4)

**Goals**: Power-user features and developer tools

**Build New** 🔨:
1. **Undo/Redo System**:
   - Command pattern implementation
   - UndoRedoManager with history (50 actions)
   - Ctrl+Z / Ctrl+Shift+Z integration

2. **Batch Token Editing**:
   - Multi-token selection
   - Pattern-based editing (*.hover.background)
   - Batch color adjustments (lighten/darken)

3. **Palette Management**:
   - Color palette aliases ($primary, $accent)
   - Palette generation tools
   - Palette-wide adjustments

4. **Code Generation** (DX Feature):
   - Export as Python ThemeBuilder code
   - Generate TypeScript type definitions
   - Generate CSS custom properties
   - Export as QSS stylesheet

5. **Testing & Polish**:
   - Unit tests for all components
   - Performance optimization
   - Accessibility testing
   - UI refinement

**Leverage Existing** ✅:
- `KeybindingManager` - Keyboard shortcuts
- `ThemeComposer` - Theme merging for palette management
- Hot reload (`development/hot_reload.py`)
- Property descriptors for type safety

**Deliverables**:
- ✅ Undo/Redo with 50-action history
- ✅ Batch editing (pattern-based, multi-select)
- ✅ Palette management system
- ✅ Code generator (Python, TypeScript, CSS, QSS)
- ✅ 90%+ test coverage
- ✅ Complete documentation

---

## Phase Summary & Time Allocation

| Phase | Duration | Complexity | Acceleration Factor |
|-------|----------|------------|-------------------|
| Phase 1 | Week 1 | Medium | Baseline |
| Phase 2 | Week 1-2 | Medium | Baseline |
| Phase 3 | Week 2 | **Low** ⚡ | 50% faster (preview exists) |
| Phase 4 | Week 2-3 | **Low** ⚡ | 50% faster (validation exists) |
| Phase 5 | Week 3 | **Low** ⚡ | 50% faster (persistence exists) |
| Phase 6 | Week 3-4 | Medium | Baseline |
| Phase 7 | Week 4 | **High** | Extended scope (extra time from 3-5) |

**Key Insight**: Time saved in Phases 3-5 (by leveraging existing systems) is reallocated to Phase 7 for advanced features (undo/redo, batch editing, palette management, code generation).

---

## API Reference

### ThemeEditorDialog

```python
class ThemeEditorDialog(QDialog):
    """Modal theme editor dialog."""

    # Signals
    theme_changed = Signal(Theme)
    theme_saved = Signal(Theme)
    validation_failed = Signal(ValidationResult)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        base_theme: Union[str, Theme] = "dark",
        mode: str = "create",  # "create", "edit", "clone"
        size: QSize = QSize(1200, 800)
    ):
        """Initialize theme editor dialog.

        Args:
            parent: Parent widget
            base_theme: Theme name or Theme instance to start from
            mode: Editor mode
            size: Initial dialog size
        """

    def get_theme(self) -> Theme:
        """Get the edited theme.

        Returns:
            Theme instance with all modifications
        """

    def set_theme(self, theme: Union[str, Theme]) -> None:
        """Set theme to edit.

        Args:
            theme: Theme name or Theme instance
        """

    def validate_theme(self) -> ValidationResult:
        """Validate current theme.

        Returns:
            ValidationResult with accessibility checks
        """

    def export_theme(self, filepath: Path) -> bool:
        """Export theme to JSON file.

        Args:
            filepath: Path to save theme

        Returns:
            True if successful
        """

    def import_theme(self, filepath: Path) -> bool:
        """Import theme from JSON file.

        Args:
            filepath: Path to theme file

        Returns:
            True if successful
        """
```

### ThemeEditorWidget

```python
class ThemeEditorWidget(ThemedWidget, QWidget):
    """Embeddable theme editor widget."""

    # Signals
    theme_modified = Signal()
    validation_changed = Signal(ValidationResult)
    token_selected = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        show_preview: bool = True,
        show_validation: bool = True,
        compact_mode: bool = False
    ):
        """Initialize theme editor widget.

        Args:
            parent: Parent widget
            show_preview: Show live preview panel
            show_validation: Show accessibility validation
            compact_mode: Use compact layout for embedding
        """
```

---

## File Structure

```
widgets/theme_system/
├── src/vfwidgets_theme/
│   └── widgets/
│       ├── theme_editor.py           # NEW - ThemeEditorDialog/Widget
│       ├── token_browser.py          # NEW - Token tree browser
│       ├── color_editor.py           # NEW - Color picker widget
│       ├── validation_panel.py       # NEW - Accessibility validation
│       └── theme_preview.py          # EXTENDED - Add more samples
│
├── docs/
│   ├── theme-editor-DESIGN.md       # This document
│   └── theme-editor-GUIDE.md        # User guide (to be created)
│
└── examples/
    ├── 10_theme_editor_standalone.py    # Standalone dialog example
    ├── 11_theme_editor_embedded.py      # Embedded widget example
    └── 12_theme_editor_quick_edit.py    # Quick customization example
```

---

## Success Criteria

### Functional Requirements ✅

- [ ] Edit all 197 theme tokens visually
- [ ] Live preview updates in real-time (< 300ms)
- [ ] Color picker integration with hex/rgb/rgba support
- [ ] WCAG AA/AAA accessibility validation
- [ ] Import/Export JSON themes
- [ ] Extend built-in themes
- [ ] Save custom themes to disk
- [ ] Undo/Redo support
- [ ] Search and filter tokens
- [ ] Validation error reporting

### Non-Functional Requirements ✅

- [ ] Reusable across all VFWidgets apps
- [ ] < 100ms response time for color changes
- [ ] < 1s initial load time
- [ ] Works with themes 10+ MB
- [ ] Keyboard navigation support
- [ ] Screen reader compatible
- [ ] 90%+ test coverage
- [ ] Comprehensive documentation

---

## Future Enhancements

### Post-MVP Features

1. **Theme Templates**
   - Material Design template
   - Flat Design template
   - Solarized template
   - High Contrast template

2. **Color Palette Tools**
   - Generate complementary colors
   - Color harmony suggestions
   - Palette extraction from images
   - Gradient generator

3. **Advanced Validation**
   - Color blindness simulation
   - Photosensitivity warnings
   - Animation timing checks

4. **Collaboration Features**
   - Share themes via URL
   - Theme marketplace
   - Version control integration
   - Collaborative editing

5. **AI-Assisted Features**
   - Auto-generate themes from description
   - Smart color suggestions
   - Accessibility auto-fix

---

## References

- **VFWidgets Theme System**: `widgets/theme_system/README.md`
- **Theme Customization Guide**: `docs/theme-customization-GUIDE.md`
- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **Qt Color Dialog**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QColorDialog.html
- **Material Design Color**: https://m3.material.io/styles/color/overview

---

## Developer Examples & Templates

The following example files demonstrate how to use the theme editor and DX features:

### Example Files Created

**12_theme_editor_standalone.py**
- Standalone theme editor dialog
- Create, edit, and clone themes
- Three usage modes: create, edit, clone
- Theme saved/changed signal handling

**13_theme_editor_embedded.py**
- Embed theme editor in settings page
- Settings integration pattern
- Live preview in application UI
- Import/export from embedded widget

**14_theme_editor_quick_edit.py**
- Quick color customization UI
- Simplified "Change App Color" feature
- Real-time preview with minimal UI
- Perfect for simple theme tweaks

**15_theme_code_generation.py**
- Theme code generation demo
- Export to Python, TypeScript, CSS, QSS, JSON
- Developer workflow integration
- Copy/save generated code

These examples serve as:
1. **API documentation** - Show intended usage patterns
2. **Implementation templates** - Reference during development
3. **User tutorials** - Help developers integrate theme editor
4. **Test cases** - Verify API design decisions

All examples are marked as **TEMPLATE** status and include TODO comments for actual implementation.

---

## Changelog

- **2025-10-04**: Initial design document created
- **2025-10-04**: Added missing requirements (undo/redo, comparison, batch editing, palette management, shortcuts, docs, migration, error handling, integration)
- **2025-10-04**: Added comprehensive Developer Experience (DX) section with 7 features
- **2025-10-04**: Created 4 developer example templates (examples 12-15)
- **2025-10-04**: **Revised implementation phases** - Clarified "Build New" vs "Leverage Existing" for each phase. Identified Phases 3-5 as accelerated (50% faster) by reusing existing preview, validation, and persistence systems. Reallocated saved time to Phase 7 for advanced features (undo/redo, batch editing, palette management, code generation).
