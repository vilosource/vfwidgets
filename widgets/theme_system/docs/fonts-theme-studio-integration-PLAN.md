# Font Support - Theme Studio Integration Plan

**Status**: Planning
**Version**: v2.1.0 (Theme Studio Integration)
**Started**: 2025-10-14
**Dependencies**: Phase 1 (Core Infrastructure) ✅, Phase 2 (Font Token Resolution) ✅

## Overview

This document outlines the phased integration of font support into the Theme Studio visual editor. Phases 1-2 (core infrastructure and token resolution) are complete. This plan covers Phases 3-6: visual editing integration.

**What's Complete**:
- ✅ Phase 1: Theme.fonts field, validation, exceptions
- ✅ Phase 2: FontTokenRegistry with hierarchical resolution
- ✅ 30 passing tests, 2 working demos

**What's Next**:
- 🔄 Phase 3: Font token browsing in Theme Studio
- 🔄 Phase 4: Basic font property editing (size, weight)
- 🔄 Phase 5: Font family list editing with drag-drop
- 🔄 Phase 6: Advanced properties and live preview

## Architecture Context

### Existing Theme Studio Components

**ThemeEditorWidget** (`src/vfwidgets_theme/widgets/theme_editor.py`)
- Main orchestrator for theme editing
- Manages preview debouncing (300ms delay)
- Emits `theme_modified` signal on changes
- Coordinates between token browser and property editors

**TokenBrowserWidget** (`src/vfwidgets_theme/widgets/token_browser.py`)
- Tree view of theme tokens organized by category
- Emits `token_selected(str)` signal
- Currently shows color tokens only
- **Needs**: New "FONT TOKENS" category

**FontEditorWidget** (`src/vfwidgets_theme/widgets/font_editor.py`, 399 lines)
- **Current State**: CSS string-based font editor
- Emits `font_changed(str)` signal with CSS strings
- Has font family combo, size spinbox, weight combo
- **Needs**: Complete refactor to token-based editing

**ColorEditorWidget** (`src/vfwidgets_theme/widgets/color_editor.py`)
- Reference pattern for property editors
- Shows how to emit property changes
- Good model for FontPropertyEditorWidget

### Integration Pattern

```
User clicks token in TokenBrowserWidget
    ↓
ThemeEditorWidget receives token_selected(str) signal
    ↓
ThemeEditorWidget shows appropriate editor widget
    ↓
Editor widget emits property_changed signal
    ↓
ThemeEditorWidget updates Theme.fonts
    ↓
Preview timer debounces (300ms)
    ↓
Live preview updates with new fonts
```

## Phase 3: Font Token Browsing (4-5 hours)

**Goal**: View and select font tokens in Theme Studio's token browser

**Demo**: Open Theme Studio → See "FONT TOKENS" category → Click tokens → Selection works

**Duration**: 4-5 hours

### Tasks

#### Task 3.1: Add Font Token Database to TokenBrowserWidget (1.5 hours)

**File**: `src/vfwidgets_theme/widgets/token_browser.py`

Create font token categories similar to color tokens:

```python
def _build_token_database(self):
    """Build database of all theme tokens organized by category."""
    # ... existing color tokens ...

    # Add font token categories
    self._categories["FONT TOKENS"] = {
        "Base Categories": [
            ("MONO_FONTS", "fonts.mono"),
            ("UI_FONTS", "fonts.ui"),
            ("SERIF_FONTS", "fonts.serif"),
        ],
        "Base Properties": [
            ("DEFAULT_SIZE", "fonts.size"),
            ("DEFAULT_WEIGHT", "fonts.weight"),
            ("LINE_HEIGHT", "fonts.lineHeight"),
            ("LETTER_SPACING", "fonts.letterSpacing"),
        ],
        "Terminal Fonts": [
            ("TERMINAL_FAMILY", "terminal.fontFamily"),
            ("TERMINAL_SIZE", "terminal.fontSize"),
            ("TERMINAL_WEIGHT", "terminal.fontWeight"),
            ("TERMINAL_LINE_HEIGHT", "terminal.lineHeight"),
            ("TERMINAL_LETTER_SPACING", "terminal.letterSpacing"),
        ],
        "Tabs Fonts": [
            ("TABS_FAMILY", "tabs.fontFamily"),
            ("TABS_SIZE", "tabs.fontSize"),
            ("TABS_WEIGHT", "tabs.fontWeight"),
        ],
        "Editor Fonts": [
            ("EDITOR_FAMILY", "editor.fontFamily"),
            ("EDITOR_SIZE", "editor.fontSize"),
            ("EDITOR_WEIGHT", "editor.fontWeight"),
            ("EDITOR_LINE_HEIGHT", "editor.lineHeight"),
        ],
        "UI Fonts": [
            ("UI_FAMILY", "ui.fontFamily"),
            ("UI_SIZE", "ui.fontSize"),
            ("UI_WEIGHT", "ui.fontWeight"),
        ],
    }
```

**Acceptance Criteria**:
- Font tokens appear in token browser tree
- Clicking font token emits `token_selected` signal
- Token path is correct (e.g., "terminal.fontSize")

#### Task 3.2: Display Font Token Values (1.5 hours)

**File**: `src/vfwidgets_theme/widgets/token_browser.py`

Add value preview for font tokens (similar to color preview):

```python
def _get_token_display_value(self, token_path: str, theme: Theme) -> str:
    """Get human-readable display value for token."""
    if token_path in theme.fonts:
        value = theme.fonts[token_path]

        # Font family list
        if "Family" in token_path or token_path in ["fonts.mono", "fonts.ui", "fonts.serif"]:
            if isinstance(value, list):
                return ", ".join(value[:2]) + ("..." if len(value) > 2 else "")
            return str(value)

        # Font size
        if "Size" in token_path or token_path == "fonts.size":
            return f"{value}pt"

        # Font weight
        if "Weight" in token_path or token_path == "fonts.weight":
            return str(value)

        # Line height
        if "lineHeight" in token_path:
            return f"{value}×"

        # Letter spacing
        if "letterSpacing" in token_path:
            return f"{value}px"

    return "(not set)"
```

**Acceptance Criteria**:
- Font family shows first 2 fonts + "..." if more
- Font size shows "14pt" format
- Font weight shows number or name
- Line height shows "1.4×" format
- Letter spacing shows "0.0px" format

#### Task 3.3: Add Hierarchical Resolution Display (1 hour)

**File**: `src/vfwidgets_theme/widgets/token_browser.py`

Show fallback chain when token not explicitly set:

```python
def _get_token_tooltip(self, token_path: str, theme: Theme) -> str:
    """Get detailed tooltip showing resolution chain."""
    from vfwidgets_theme.core.font_tokens import FontTokenRegistry

    tooltip_parts = [f"<b>{token_path}</b><br/>"]

    # Show resolution chain if token uses fallbacks
    chain = FontTokenRegistry.HIERARCHY_MAP.get(token_path, [])
    if chain:
        tooltip_parts.append("<br/><b>Resolution Chain:</b><br/>")
        for i, token in enumerate(chain):
            if token in theme.fonts:
                tooltip_parts.append(f"✓ {token} (defined)<br/>")
                break
            else:
                tooltip_parts.append(f"- {token} (not set)<br/>")

    # Show actual resolved value
    if "Family" in token_path:
        families = FontTokenRegistry.get_font_family(token_path, theme)
        tooltip_parts.append(f"<br/><b>Resolved:</b> {', '.join(families)}")
    elif "Size" in token_path:
        size = FontTokenRegistry.get_font_size(token_path, theme)
        tooltip_parts.append(f"<br/><b>Resolved:</b> {size}pt")

    return "".join(tooltip_parts)
```

**Acceptance Criteria**:
- Tooltip shows resolution chain
- Shows which token in chain is actually used
- Shows final resolved value
- Tooltip appears on hover

#### Task 3.4: Write Tests for Font Token Browsing (1 hour)

**File**: `tests/widgets/test_token_browser_fonts.py` (new file)

```python
def test_font_tokens_appear_in_browser(qtbot):
    """Font tokens should appear in token browser."""
    theme = Theme(name="test", fonts={"fonts.mono": ["Consolas", "monospace"]})
    browser = TokenBrowserWidget(theme=theme)
    qtbot.addWidget(browser)

    # Find FONT TOKENS category
    # Verify terminal.fontFamily token exists
    # Verify fonts.mono token exists
    assert True  # Replace with actual checks

def test_font_token_selection_emits_signal(qtbot):
    """Clicking font token should emit token_selected signal."""
    theme = Theme(name="test", fonts={"terminal.fontSize": 14})
    browser = TokenBrowserWidget(theme=theme)
    qtbot.addWidget(browser)

    with qtbot.waitSignal(browser.token_selected) as blocker:
        # Simulate clicking terminal.fontSize token
        pass

    assert blocker.args[0] == "terminal.fontSize"

def test_font_token_value_display(qtbot):
    """Font token values should display correctly."""
    theme = Theme(
        name="test",
        fonts={
            "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
            "terminal.fontSize": 14,
            "fonts.weight": "bold",
        },
    )
    browser = TokenBrowserWidget(theme=theme)

    # Verify fonts.mono shows "JetBrains Mono, Consolas..."
    # Verify terminal.fontSize shows "14pt"
    # Verify fonts.weight shows "bold"
    assert True  # Replace with actual checks

def test_font_token_tooltip_shows_resolution(qtbot):
    """Font token tooltip should show resolution chain."""
    theme = Theme(name="test", fonts={"fonts.mono": ["Consolas", "monospace"]})
    browser = TokenBrowserWidget(theme=theme)

    # Get tooltip for terminal.fontFamily
    # Should show: terminal.fontFamily → fonts.mono
    # Should indicate fonts.mono is defined
    assert True  # Replace with actual checks
```

**Acceptance Criteria**:
- All tests pass
- Font tokens appear in browser
- Selection signal works
- Value display is correct
- Tooltips show resolution

### Phase 3 Exit Criteria

**Demo Steps**:
1. Run Theme Studio: `python -m vfwidgets_theme.apps.theme_studio`
2. Open theme editor
3. Navigate to "FONT TOKENS" category in token browser
4. Verify all font token categories visible
5. Click "terminal.fontSize" token
6. Verify `token_selected` signal emitted (check logs/debug)
7. Hover over "terminal.fontFamily" token
8. Verify tooltip shows resolution chain

**Success Criteria**:
- ✅ Font tokens visible in TokenBrowserWidget
- ✅ Token selection works
- ✅ Value display shows correct format
- ✅ Tooltips show resolution chains
- ✅ 4 new tests pass
- ✅ No regressions in existing tests

---

## Phase 4: Basic Font Property Editing (5-6 hours)

**Goal**: Edit font.size and fonts.weight properties in Theme Studio UI

**Demo**: Select "terminal.fontSize" → Change value in editor → Preview updates

**Duration**: 5-6 hours

### Tasks

#### Task 4.1: Create FontPropertyEditorWidget (2.5 hours)

**File**: `src/vfwidgets_theme/widgets/font_property_editor.py` (new file)

Create widget for editing individual font properties:

```python
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QComboBox

class FontPropertyEditorWidget(QWidget):
    """Editor for individual font properties (size, weight, line height, etc)."""

    property_changed = Signal(str, object)  # (token_path, new_value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_token = None
        self._setup_ui()

    def _setup_ui(self):
        """Create UI for property editing."""
        layout = QVBoxLayout(self)

        # Token path label
        self._token_label = QLabel()
        layout.addWidget(self._token_label)

        # Editor stack (changes based on property type)
        # - QSpinBox for font size (6-144pt)
        # - QComboBox for font weight (100-900 or names)
        # - QDoubleSpinBox for line height (0.5-3.0)
        # - QDoubleSpinBox for letter spacing (-5.0 to 5.0)
        pass

    def set_token(self, token_path: str, current_value, theme: Theme):
        """Set the token being edited."""
        self._current_token = token_path
        self._token_label.setText(f"Editing: {token_path}")

        # Show appropriate editor based on token type
        if "Size" in token_path or token_path == "fonts.size":
            self._show_size_editor(current_value)
        elif "Weight" in token_path or token_path == "fonts.weight":
            self._show_weight_editor(current_value)
        elif "lineHeight" in token_path:
            self._show_line_height_editor(current_value)
        elif "letterSpacing" in token_path:
            self._show_letter_spacing_editor(current_value)

    def _show_size_editor(self, current_value):
        """Show font size spinbox (6-144pt)."""
        pass

    def _show_weight_editor(self, current_value):
        """Show font weight combo (100-900 or names)."""
        pass

    def _on_value_changed(self):
        """Emit property_changed signal when user changes value."""
        new_value = self._get_current_editor_value()
        self.property_changed.emit(self._current_token, new_value)
```

**Acceptance Criteria**:
- Widget shows appropriate editor for each property type
- Font size: spinbox 6-144pt
- Font weight: combo with 100-900 and names (normal, bold, etc)
- Line height: double spinbox 0.5-3.0
- Letter spacing: double spinbox -5.0 to 5.0
- Emits `property_changed` signal on changes

#### Task 4.2: Integrate FontPropertyEditor into ThemeEditorWidget (1.5 hours)

**File**: `src/vfwidgets_theme/widgets/theme_editor.py`

Connect token selection to property editor:

```python
def __init__(self):
    # ... existing code ...

    # Add font property editor
    from vfwidgets_theme.widgets.font_property_editor import FontPropertyEditorWidget
    self._font_property_editor = FontPropertyEditorWidget()
    self._font_property_editor.property_changed.connect(self._on_font_property_changed)
    # Add to layout (probably in a stacked widget with other editors)

def _on_token_selected(self, token_path: str):
    """Handle token selection from browser."""
    # ... existing color token handling ...

    # Check if it's a font token
    if token_path in self._current_theme.fonts or self._is_font_token(token_path):
        # Get current value (with fallback resolution)
        current_value = self._resolve_font_token_value(token_path)

        # Show font property editor
        self._font_property_editor.set_token(token_path, current_value, self._current_theme)
        self._editor_stack.setCurrentWidget(self._font_property_editor)

def _on_font_property_changed(self, token_path: str, new_value):
    """Handle font property change from editor."""
    # Update theme.fonts
    self._current_theme.fonts[token_path] = new_value

    # Emit theme_modified signal
    self.theme_modified.emit()

    # Trigger preview update (with debouncing)
    self._preview_timer.start()

def _is_font_token(self, token_path: str) -> bool:
    """Check if token is a font token."""
    font_keywords = ["font", "Font", "line", "letter", "spacing"]
    return any(kw in token_path for kw in font_keywords)

def _resolve_font_token_value(self, token_path: str):
    """Get current value of font token with fallback resolution."""
    from vfwidgets_theme.core.font_tokens import FontTokenRegistry

    if "Size" in token_path or token_path == "fonts.size":
        return FontTokenRegistry.get_font_size(token_path, self._current_theme)
    elif "Weight" in token_path or token_path == "fonts.weight":
        return FontTokenRegistry.get_font_weight(token_path, self._current_theme)
    # ... etc for other property types ...
```

**Acceptance Criteria**:
- Selecting font token shows FontPropertyEditor
- Editor displays current resolved value
- Changing value updates Theme.fonts
- `theme_modified` signal emitted
- Preview timer triggered

#### Task 4.3: Add Validation Feedback (1 hour)

**File**: `src/vfwidgets_theme/widgets/font_property_editor.py`

Show validation errors in UI:

```python
def _validate_and_emit(self):
    """Validate new value before emitting."""
    from vfwidgets_theme.errors import FontPropertyError
    from vfwidgets_theme.core.theme import ThemeValidator

    new_value = self._get_current_editor_value()

    try:
        # Validate using ThemeValidator
        ThemeValidator._validate_font_property(self._current_token, new_value)

        # Clear error display
        self._error_label.clear()
        self._error_label.hide()

        # Emit change
        self.property_changed.emit(self._current_token, new_value)

    except FontPropertyError as e:
        # Show error in UI
        self._error_label.setText(f"⚠️ {str(e)}")
        self._error_label.setStyleSheet("color: red;")
        self._error_label.show()
```

**Acceptance Criteria**:
- Invalid values show error message
- Error message appears near editor
- Valid values clear error
- Font size <6 or >144 shows error
- Font weight <100 or >900 shows error

#### Task 4.4: Write Tests for Property Editing (1 hour)

**File**: `tests/widgets/test_font_property_editor.py` (new file)

```python
def test_font_size_editor_displays_value(qtbot):
    """Font size editor should show current value."""
    theme = Theme(name="test", fonts={"terminal.fontSize": 14})
    editor = FontPropertyEditorWidget()
    qtbot.addWidget(editor)

    editor.set_token("terminal.fontSize", 14, theme)

    # Verify spinbox shows 14
    assert True  # Replace with actual check

def test_font_size_change_emits_signal(qtbot):
    """Changing font size should emit property_changed."""
    theme = Theme(name="test", fonts={"terminal.fontSize": 14})
    editor = FontPropertyEditorWidget()
    qtbot.addWidget(editor)

    editor.set_token("terminal.fontSize", 14, theme)

    with qtbot.waitSignal(editor.property_changed) as blocker:
        # Change spinbox to 16
        pass

    assert blocker.args[0] == "terminal.fontSize"
    assert blocker.args[1] == 16

def test_invalid_font_size_shows_error(qtbot):
    """Invalid font size should show error message."""
    theme = Theme(name="test", fonts={"terminal.fontSize": 14})
    editor = FontPropertyEditorWidget()
    qtbot.addWidget(editor)

    editor.set_token("terminal.fontSize", 14, theme)

    # Try to set size to 200 (>144 max)
    # Verify error message shown
    assert True  # Replace with actual check

def test_font_weight_combo_shows_options(qtbot):
    """Font weight combo should show all weight options."""
    theme = Theme(name="test", fonts={"fonts.weight": "normal"})
    editor = FontPropertyEditorWidget()
    qtbot.addWidget(editor)

    editor.set_token("fonts.weight", "normal", theme)

    # Verify combo has: 100, 200, ..., 900, normal, bold, etc
    assert True  # Replace with actual check
```

**Acceptance Criteria**:
- Tests verify editor displays values
- Tests verify signal emission
- Tests verify validation errors
- All tests pass

### Phase 4 Exit Criteria

**Demo Steps**:
1. Run Theme Studio
2. Select "terminal.fontSize" in token browser
3. Verify FontPropertyEditor appears with spinbox showing current value
4. Change font size from 14 to 16
5. Verify `theme_modified` signal emitted
6. Verify preview updates after 300ms debounce
7. Try setting font size to 200
8. Verify error message appears
9. Select "fonts.weight" token
10. Verify combo box appears with weight options
11. Change weight to "bold"
12. Verify preview updates

**Success Criteria**:
- ✅ FontPropertyEditorWidget created
- ✅ Editor integrated into ThemeEditorWidget
- ✅ Font size editing works
- ✅ Font weight editing works
- ✅ Line height editing works
- ✅ Letter spacing editing works
- ✅ Validation errors shown in UI
- ✅ Preview updates on changes
- ✅ 4+ new tests pass
- ✅ No regressions

---

## Phase 5: Font Family List Editing (6-7 hours)

**Goal**: Edit font family lists with drag-drop fallback ordering

**Demo**: Edit "terminal.fontFamily" → Drag fonts to reorder → Add/remove fonts

**Duration**: 6-7 hours

### Tasks

#### Task 5.1: Create FontFamilyListEditor Widget (3 hours)

**File**: `src/vfwidgets_theme/widgets/font_family_editor.py` (new file)

Create drag-drop list for font fallback chains:

```python
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton

class FontFamilyListEditor(QWidget):
    """Editor for font family fallback lists with drag-drop reordering."""

    families_changed = Signal(str, list)  # (token_path, new_family_list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_token = None
        self._setup_ui()

    def _setup_ui(self):
        """Create UI with list, add/remove buttons."""
        layout = QVBoxLayout(self)

        # Token path label
        self._token_label = QLabel()
        layout.addWidget(self._token_label)

        # Font family list (drag-drop enabled)
        self._family_list = QListWidget()
        self._family_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._family_list.model().rowsMoved.connect(self._on_order_changed)
        layout.addWidget(self._family_list)

        # Add button (opens system font picker)
        self._add_button = QPushButton("Add Font...")
        self._add_button.clicked.connect(self._on_add_font)
        layout.addWidget(self._add_button)

        # Remove button
        self._remove_button = QPushButton("Remove Selected")
        self._remove_button.clicked.connect(self._on_remove_font)
        layout.addWidget(self._remove_button)

        # Font availability indicators (✓ available, ✗ not installed)

    def set_token(self, token_path: str, family_list: list[str], theme: Theme):
        """Set the font family list being edited."""
        self._current_token = token_path
        self._token_label.setText(f"Editing: {token_path}")

        # Populate list
        self._family_list.clear()
        for family in family_list:
            item = QListWidgetItem(family)

            # Check if font is available on system
            from vfwidgets_theme.core.font_tokens import FontTokenRegistry
            is_available = FontTokenRegistry.get_available_font((family,)) is not None

            # Set icon based on availability
            if is_available:
                item.setIcon(QIcon("✓"))  # Green checkmark
            else:
                item.setIcon(QIcon("✗"))  # Red X

            self._family_list.addItem(item)

    def _on_add_font(self):
        """Open font picker dialog."""
        from PySide6.QtWidgets import QFontDialog
        from PySide6.QtGui import QFontDatabase

        # Show system font picker
        font_dialog = QFontDialog(self)
        if font_dialog.exec():
            selected_font = font_dialog.selectedFont()
            family = selected_font.family()

            # Add to list if not already present
            if not self._family_list.findItems(family, Qt.MatchExactly):
                self._family_list.addItem(family)
                self._emit_change()

    def _on_remove_font(self):
        """Remove selected font from list."""
        current_item = self._family_list.currentItem()
        if current_item:
            # Don't allow removing last generic family (monospace, sans-serif, serif)
            if self._is_last_generic_family(current_item.text()):
                QMessageBox.warning(
                    self,
                    "Cannot Remove",
                    "Cannot remove the last generic family fallback.",
                )
                return

            self._family_list.takeItem(self._family_list.row(current_item))
            self._emit_change()

    def _on_order_changed(self):
        """Handle drag-drop reordering."""
        self._emit_change()

    def _emit_change(self):
        """Emit families_changed signal with new list."""
        new_list = []
        for i in range(self._family_list.count()):
            new_list.append(self._family_list.item(i).text())

        self.families_changed.emit(self._current_token, new_list)

    def _is_last_generic_family(self, family: str) -> bool:
        """Check if this is the last generic family in the list."""
        generic_families = {"monospace", "sans-serif", "serif", "cursive", "fantasy"}

        # Count generic families in list
        generic_count = 0
        for i in range(self._family_list.count()):
            if self._family_list.item(i).text().lower() in generic_families:
                generic_count += 1

        return generic_count == 1 and family.lower() in generic_families
```

**Acceptance Criteria**:
- List shows current font families
- Drag-drop reordering works
- Add button opens font picker
- Remove button removes selected font
- Can't remove last generic family
- Font availability shown with icons
- Emits `families_changed` on changes

#### Task 5.2: Integrate FontFamilyListEditor into ThemeEditorWidget (1.5 hours)

**File**: `src/vfwidgets_theme/widgets/theme_editor.py`

Show family editor for font family tokens:

```python
def _on_token_selected(self, token_path: str):
    """Handle token selection from browser."""
    # ... existing code ...

    # Check if it's a font family token
    if self._is_font_family_token(token_path):
        from vfwidgets_theme.core.font_tokens import FontTokenRegistry

        # Get current family list
        families = FontTokenRegistry.get_font_family(token_path, self._current_theme)

        # Show font family editor
        self._font_family_editor.set_token(token_path, families, self._current_theme)
        self._editor_stack.setCurrentWidget(self._font_family_editor)

def _on_font_families_changed(self, token_path: str, new_families: list[str]):
    """Handle font family list change."""
    # Update theme.fonts
    self._current_theme.fonts[token_path] = new_families

    # Emit theme_modified
    self.theme_modified.emit()

    # Trigger preview update
    self._preview_timer.start()

def _is_font_family_token(self, token_path: str) -> bool:
    """Check if token is a font family token."""
    return (
        "Family" in token_path
        or token_path in ["fonts.mono", "fonts.ui", "fonts.serif"]
    )
```

**Acceptance Criteria**:
- Selecting font family token shows FontFamilyListEditor
- Editor shows current resolved families
- Changing list updates Theme.fonts
- Preview updates after changes
- Validation runs on list changes

#### Task 5.3: Add Font Family Validation to Editor (1 hour)

**File**: `src/vfwidgets_theme/widgets/font_family_editor.py`

Validate font family lists before emitting:

```python
def _validate_and_emit(self, new_list: list[str]):
    """Validate font family list before emitting."""
    from vfwidgets_theme.errors import FontValidationError
    from vfwidgets_theme.core.theme import ThemeValidator

    try:
        # Create test theme with new list
        test_fonts = {self._current_token: new_list}
        ThemeValidator._validate_fonts(test_fonts)

        # Clear error
        self._error_label.clear()
        self._error_label.hide()

        # Emit change
        self.families_changed.emit(self._current_token, new_list)

    except FontValidationError as e:
        # Show error
        self._error_label.setText(f"⚠️ {str(e)}")
        self._error_label.setStyleSheet("color: red;")
        self._error_label.show()

        # Don't emit change (invalid)
```

**Acceptance Criteria**:
- Removing last generic family shows error
- Empty list shows error
- Valid lists pass validation
- Error appears in UI

#### Task 5.4: Write Tests for Font Family Editing (1.5 hours)

**File**: `tests/widgets/test_font_family_editor.py` (new file)

```python
def test_font_family_list_displays(qtbot):
    """Font family list should display current families."""
    theme = Theme(
        name="test",
        fonts={"fonts.mono": ["JetBrains Mono", "Consolas", "monospace"]},
    )
    editor = FontFamilyListEditor()
    qtbot.addWidget(editor)

    editor.set_token("fonts.mono", ["JetBrains Mono", "Consolas", "monospace"], theme)

    # Verify list has 3 items
    assert editor._family_list.count() == 3
    assert editor._family_list.item(0).text() == "JetBrains Mono"

def test_drag_drop_reordering_emits_signal(qtbot):
    """Reordering fonts should emit families_changed."""
    theme = Theme(name="test", fonts={"fonts.mono": ["Consolas", "monospace"]})
    editor = FontFamilyListEditor()
    qtbot.addWidget(editor)

    editor.set_token("fonts.mono", ["Consolas", "monospace"], theme)

    with qtbot.waitSignal(editor.families_changed) as blocker:
        # Simulate drag-drop (move "monospace" to top)
        pass

    assert blocker.args[0] == "fonts.mono"
    assert blocker.args[1] == ["monospace", "Consolas"]

def test_cannot_remove_last_generic_family(qtbot):
    """Cannot remove last generic family from list."""
    theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
    editor = FontFamilyListEditor()
    qtbot.addWidget(editor)

    editor.set_token("fonts.mono", ["monospace"], theme)

    # Select "monospace" and click remove
    editor._family_list.setCurrentRow(0)
    editor._on_remove_font()

    # Verify still in list
    assert editor._family_list.count() == 1
    assert editor._family_list.item(0).text() == "monospace"

def test_add_font_opens_dialog(qtbot, mocker):
    """Add font button should open font picker."""
    theme = Theme(name="test", fonts={"fonts.mono": ["monospace"]})
    editor = FontFamilyListEditor()
    qtbot.addWidget(editor)

    # Mock QFontDialog
    mock_dialog = mocker.patch("PySide6.QtWidgets.QFontDialog.exec")
    mock_dialog.return_value = True

    editor.set_token("fonts.mono", ["monospace"], theme)
    editor._on_add_font()

    # Verify dialog was shown
    mock_dialog.assert_called_once()
```

**Acceptance Criteria**:
- Tests verify list display
- Tests verify drag-drop reordering
- Tests verify add/remove buttons
- Tests verify validation
- All tests pass

### Phase 5 Exit Criteria

**Demo Steps**:
1. Run Theme Studio
2. Select "terminal.fontFamily" in token browser
3. Verify FontFamilyListEditor appears
4. Verify current font families shown in list
5. Drag "monospace" to top of list
6. Verify preview updates with new order
7. Click "Add Font..." button
8. Select a system font (e.g., "Arial")
9. Verify font added to list
10. Verify availability icon (✓ or ✗)
11. Select "Arial" and click "Remove Selected"
12. Verify font removed
13. Try to remove last "monospace" font
14. Verify error message appears

**Success Criteria**:
- ✅ FontFamilyListEditor created
- ✅ Drag-drop reordering works
- ✅ Add font opens picker
- ✅ Remove font works
- ✅ Can't remove last generic family
- ✅ Font availability indicators work
- ✅ Editor integrated into ThemeEditorWidget
- ✅ Validation works
- ✅ 4+ new tests pass
- ✅ No regressions

---

## Phase 6: Advanced Properties and Live Preview (4-5 hours)

**Goal**: Complete integration with live preview, validation, and save/load

**Demo**: Edit any font property → See changes in preview immediately → Save theme

**Duration**: 4-5 hours

### Tasks

#### Task 6.1: Add Font Preview to ThemeEditorWidget (1.5 hours)

**File**: `src/vfwidgets_theme/widgets/theme_editor.py`

Show font changes in preview panel:

```python
def _update_preview(self):
    """Update preview with current theme."""
    # ... existing color preview ...

    # Add font preview
    from vfwidgets_theme.core.font_tokens import FontTokenRegistry

    # Apply terminal font to preview terminal widget
    if hasattr(self._preview_widget, "terminal"):
        terminal_font = FontTokenRegistry.get_qfont("terminal", self._current_theme)
        self._preview_widget.terminal.setFont(terminal_font)

    # Apply tabs font to preview tabs
    if hasattr(self._preview_widget, "tabs"):
        tabs_font = FontTokenRegistry.get_qfont("tabs", self._current_theme)
        self._preview_widget.tabs.setFont(tabs_font)

    # Apply UI font to preview UI elements
    if hasattr(self._preview_widget, "ui_widget"):
        ui_font = FontTokenRegistry.get_qfont("ui", self._current_theme)
        self._preview_widget.ui_widget.setFont(ui_font)
```

**Acceptance Criteria**:
- Preview updates when font properties change
- Terminal preview uses terminal fonts
- Tabs preview uses tabs fonts
- UI elements use UI fonts
- Changes visible immediately after 300ms debounce

#### Task 6.2: Add Font Validation to Theme Save (1 hour)

**File**: `src/vfwidgets_theme/widgets/theme_editor.py`

Validate fonts when saving theme:

```python
def save_theme(self, file_path: str):
    """Save current theme to file."""
    from vfwidgets_theme.errors import FontValidationError, FontPropertyError

    # Validate theme (including fonts)
    try:
        ThemeValidator.validate_theme(self._current_theme)
    except (FontValidationError, FontPropertyError) as e:
        QMessageBox.critical(
            self,
            "Font Validation Error",
            f"Cannot save theme: {str(e)}",
        )
        return

    # Save theme
    from vfwidgets_theme.core.theme import save_theme_to_file
    save_theme_to_file(self._current_theme, file_path)

    QMessageBox.information(self, "Saved", f"Theme saved to {file_path}")
```

**Acceptance Criteria**:
- Can't save theme with invalid fonts
- Validation errors shown to user
- Valid themes save successfully
- Font tokens included in saved JSON

#### Task 6.3: Add Font Documentation Panel (1 hour)

**File**: `src/vfwidgets_theme/widgets/font_property_editor.py`

Show contextual help for font tokens:

```python
def _show_token_documentation(self, token_path: str):
    """Show help text for current token."""
    docs = {
        "fonts.mono": "Base monospace font for terminal and code editors. Must end with 'monospace'.",
        "fonts.ui": "Base UI font for buttons, tabs, and menus. Must end with 'sans-serif'.",
        "fonts.serif": "Base serif font for documentation. Must end with 'serif'.",
        "fonts.size": "Default font size in points (6-144pt). Used as fallback for all widgets.",
        "fonts.weight": "Default font weight (100-900 or names like 'normal', 'bold').",
        "terminal.fontFamily": "Terminal-specific font. Falls back to fonts.mono if not set.",
        "terminal.fontSize": "Terminal font size in points. Falls back to fonts.size if not set.",
        "terminal.lineHeight": "Line height multiplier for terminal (e.g., 1.4 = 140% of font size).",
        # ... more docs ...
    }

    help_text = docs.get(token_path, "No documentation available.")
    self._help_label.setText(help_text)
    self._help_label.setWordWrap(True)
```

**Acceptance Criteria**:
- Help text appears for each token
- Explains purpose and fallback chain
- Shows validation rules (e.g., "must end with monospace")
- Updates when token selection changes

#### Task 6.4: Write Integration Tests (1.5 hours)

**File**: `tests/widgets/test_theme_studio_fonts_integration.py` (new file)

End-to-end tests for font editing flow:

```python
def test_font_token_selection_to_preview(qtbot):
    """Complete flow: select token → edit → preview updates."""
    from vfwidgets_theme.widgets.theme_editor import ThemeEditorWidget

    theme = Theme(
        name="test",
        fonts={"terminal.fontSize": 14},
    )

    editor = ThemeEditorWidget(base_theme=theme, show_preview=True)
    qtbot.addWidget(editor)

    # Select terminal.fontSize in browser
    # Change size to 16 in property editor
    # Wait for preview timer (300ms)
    # Verify preview terminal font size is 16
    assert True  # Replace with actual checks

def test_font_theme_save_load_roundtrip(qtbot, tmp_path):
    """Saving and loading theme preserves font tokens."""
    from vfwidgets_theme.widgets.theme_editor import ThemeEditorWidget
    from vfwidgets_theme.core.theme import load_theme_from_file

    theme = Theme(
        name="test",
        fonts={
            "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
            "terminal.fontSize": 16,
        },
    )

    editor = ThemeEditorWidget(base_theme=theme)

    # Save theme
    theme_path = tmp_path / "test-theme.json"
    editor.save_theme(str(theme_path))

    # Load theme
    loaded_theme = load_theme_from_file(str(theme_path))

    # Verify fonts preserved
    assert loaded_theme.fonts["fonts.mono"] == ["JetBrains Mono", "Consolas", "monospace"]
    assert loaded_theme.fonts["terminal.fontSize"] == 16

def test_invalid_font_prevents_save(qtbot):
    """Cannot save theme with invalid fonts."""
    from vfwidgets_theme.widgets.theme_editor import ThemeEditorWidget

    theme = Theme(name="test", fonts={"terminal.fontSize": 14})
    editor = ThemeEditorWidget(base_theme=theme)
    qtbot.addWidget(editor)

    # Manually set invalid font (bypass validation)
    editor._current_theme.fonts["terminal.fontSize"] = 200  # >144 max

    # Try to save
    with qtbot.waitSignal(editor.validation_changed) as blocker:
        editor.save_theme("/tmp/test.json")

    # Verify error shown
    # Verify file not created
    assert True  # Replace with actual checks

def test_font_family_reorder_updates_preview(qtbot):
    """Reordering font families updates preview."""
    from vfwidgets_theme.widgets.theme_editor import ThemeEditorWidget

    theme = Theme(
        name="test",
        fonts={"fonts.mono": ["JetBrains Mono", "Consolas", "monospace"]},
    )

    editor = ThemeEditorWidget(base_theme=theme, show_preview=True)
    qtbot.addWidget(editor)

    # Select fonts.mono
    # Drag "Consolas" to top
    # Wait for preview update
    # Verify preview uses Consolas (or next available)
    assert True  # Replace with actual checks
```

**Acceptance Criteria**:
- Integration tests verify complete flow
- Tests verify save/load roundtrip
- Tests verify preview updates
- Tests verify validation prevents invalid saves
- All tests pass

### Phase 6 Exit Criteria

**Demo Steps**:
1. Run Theme Studio
2. Load dark-default theme
3. Select "terminal.fontFamily" token
4. Add "Comic Sans MS" to top of list
5. Verify preview terminal uses Comic Sans MS (if installed)
6. Select "terminal.fontSize" token
7. Change size to 18
8. Wait 300ms
9. Verify preview terminal font size is 18pt
10. Try to save theme with invalid font (e.g., size = 200)
11. Verify error message appears
12. Fix invalid font
13. Save theme to file
14. Close Theme Studio
15. Open Theme Studio again
16. Load saved theme
17. Verify fonts preserved correctly

**Success Criteria**:
- ✅ Font preview works in ThemeEditorWidget
- ✅ Preview updates after 300ms debounce
- ✅ Validation prevents saving invalid themes
- ✅ Font documentation panel implemented
- ✅ Save/load roundtrip preserves fonts
- ✅ 4+ integration tests pass
- ✅ All previous tests still pass
- ✅ No regressions

---

## Overall Success Criteria (Phases 3-6 Complete)

**Feature Completeness**:
- ✅ Font tokens visible in Theme Studio token browser
- ✅ Font properties editable (size, weight, line height, letter spacing)
- ✅ Font family lists editable with drag-drop
- ✅ Live preview shows font changes
- ✅ Validation prevents invalid fonts
- ✅ Save/load preserves font tokens
- ✅ Documentation panel explains tokens

**Testing**:
- ✅ 15+ new widget tests pass
- ✅ 4+ integration tests pass
- ✅ All existing tests still pass
- ✅ No test regressions

**Documentation**:
- ✅ Font editing documented in Theme Studio guide
- ✅ Token documentation shown in UI
- ✅ Examples demonstrate font editing

**Performance**:
- ✅ Preview updates <500ms after edit
- ✅ Font resolution uses LRU cache (<100μs)
- ✅ No UI blocking during font changes

**User Experience**:
- ✅ Intuitive token browsing
- ✅ Clear error messages
- ✅ Responsive preview
- ✅ Font availability indicators
- ✅ Contextual help available

---

## Implementation Notes

### Development Workflow

1. **Start Each Phase**:
   - Read this plan section
   - Create task checklist
   - Run existing tests (ensure no regressions)

2. **During Implementation**:
   - Write tests first (TDD approach)
   - Implement feature
   - Run tests continuously
   - Update this plan if discoveries require changes

3. **End Each Phase**:
   - Run complete demo scenario
   - Verify all exit criteria met
   - Run full test suite
   - Commit changes with descriptive message
   - Update this plan status

### Testing Strategy

**Widget Tests** (pytest-qt):
- Test individual widgets in isolation
- Mock signals and slots
- Verify UI updates correctly

**Integration Tests**:
- Test complete editing flow
- Verify Theme object updates
- Verify save/load roundtrip
- Verify preview updates

**Manual Testing**:
- Run Theme Studio after each phase
- Follow demo steps exactly
- Verify visual appearance
- Test edge cases

### Debugging Tips

**Font Not Appearing**:
- Check font is installed on system
- Verify FontTokenRegistry.get_available_font() returns it
- Check QFontDatabase.families() includes it
- Try generic fallback (monospace, sans-serif)

**Preview Not Updating**:
- Check theme_modified signal emitted
- Verify preview timer started (300ms)
- Check _update_preview() called
- Verify widget has setFont() method

**Validation Errors**:
- Check ThemeValidator._validate_fonts() logic
- Verify generic family fallback present
- Check font size in range (6-144)
- Check font weight in range (100-900)

### Code Style

Follow existing VFWidgets patterns:
- PySide6 (not PyQt)
- Signal/Slot for communication
- ThemedWidget mixin for theme integration
- Protocols for dependency injection
- Type hints for all public APIs
- Docstrings for all public methods

### Git Commit Messages

Use descriptive commit messages:
- `feat(theme-studio): add font token browser integration`
- `feat(theme-studio): implement font property editor widget`
- `feat(theme-studio): add font family drag-drop list editor`
- `test(theme-studio): add integration tests for font editing`
- `docs(theme-studio): update user guide with font editing`

---

## Timeline

**Total Estimated Duration**: 19-23 hours

- Phase 3: Font Token Browsing - 4-5 hours
- Phase 4: Basic Font Property Editing - 5-6 hours
- Phase 5: Font Family List Editing - 6-7 hours
- Phase 6: Advanced Properties and Live Preview - 4-5 hours

**Recommended Schedule**:
- Day 1: Phase 3 (token browsing)
- Day 2: Phase 4 (property editing)
- Day 3: Phase 5 (family lists)
- Day 4: Phase 6 (preview and polish)

---

## Dependencies and Prerequisites

**Required**:
- ✅ Phase 1 complete (Theme.fonts, validation)
- ✅ Phase 2 complete (FontTokenRegistry)
- ✅ Theme Studio existing infrastructure
- ✅ pytest-qt for testing

**Optional**:
- QFontDialog for font picker
- QListWidget drag-drop support
- System font database access

---

## Risks and Mitigation

**Risk**: FontEditorWidget refactor breaks existing code
**Mitigation**: Create new widgets instead of modifying existing

**Risk**: Font availability varies by platform
**Mitigation**: Always include generic fallbacks, show availability indicators

**Risk**: Preview performance degrades with many changes
**Mitigation**: Use 300ms debounce timer, LRU cache for font resolution

**Risk**: Validation too strict, blocks legitimate use cases
**Mitigation**: Follow Phase 1 validation rules exactly, allow all CSS font names

---

## Next Steps After Completion

1. **User Testing**: Get feedback on font editing UX
2. **Documentation**: Complete user guide with screenshots
3. **Examples**: Add Theme Studio font editing examples
4. **Blog Post**: Announce font support in VFWidgets Theme System v2.1.0
5. **Release**: Tag v2.1.0 and publish to PyPI

---

## Questions and Open Issues

**Q1**: Should we support custom font files (TTF/OTF upload)?
**A1**: Not in this phase. Stick to system fonts only. Future enhancement.

**Q2**: Should font families auto-complete from system fonts?
**A2**: Nice to have, but not required. QFontDialog provides picker. Add later if time permits.

**Q3**: How to handle font preview with non-installed fonts?
**A3**: Show availability indicator (✗), use next fallback in preview.

**Q4**: Should line height and letter spacing apply to preview?
**A4**: Yes in Phase 6. Terminal widget needs to support these properties.

**Q5**: What if Theme Studio preview doesn't have terminal widget?
**A5**: Check with hasattr() before applying fonts. Add terminal to preview if missing.

---

## References

- `fonts-implementation-tasks-PLAN.md` - Original font support plan (Phases 1-2)
- `src/vfwidgets_theme/core/font_tokens.py` - FontTokenRegistry implementation
- `src/vfwidgets_theme/core/theme.py` - Theme dataclass and validation
- `src/vfwidgets_theme/widgets/theme_editor.py` - Main theme editor
- `src/vfwidgets_theme/widgets/token_browser.py` - Token browser widget
- `examples/12_font_resolution.py` - Font resolution demo
- VFWidgets Theme System Documentation

---

**End of Plan**

Ready to begin Phase 3 implementation! 🚀
