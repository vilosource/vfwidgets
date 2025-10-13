# VFWidgets Theme System - Font Support Design

**Status: 🚧 Work In Progress - Design Phase**

This document is a design specification for adding font support to the VFWidgets theme system. Implementation has not yet started.

## Overview

Add comprehensive font configuration support to the VFWidgets theme system, allowing themes to define typography settings including font families, sizes, weights, and styles.

## Goals

1. **Theme-defined fonts**: Allow themes to specify font families, sizes, weights, and styles
2. **Semantic font tokens**: Support semantic tokens like `editor.font`, `terminal.font`, `ui.font`
3. **Fallback chains**: Define fallback font families for cross-platform compatibility
4. **Font metrics**: Include line height, letter spacing, and other typography metrics
5. **Widget integration**: Automatically apply fonts to ThemedWidget instances
6. **Platform awareness**: Handle platform-specific font availability
7. **Performance**: Minimal overhead for font application

## Non-Goals

- Font file bundling/distribution (use system fonts)
- Custom font rendering (use Qt's QFont system)
- Web font loading (terminal uses xterm.js fonts separately)

---

## Design

### 1. Font Token Schema

Add a new `fonts` section to theme JSON files with hierarchical structure:

```json
{
  "name": "Dark Default",
  "type": "dark",
  "version": "1.0.0",
  "colors": { ... },
  "fonts": {
    // Base font categories (required)
    "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "Monaco", "monospace"],
    "fonts.ui": ["Segoe UI", "Inter", "Ubuntu", "Roboto", "sans-serif"],
    "fonts.serif": ["Georgia", "Times New Roman", "serif"],

    "fonts.size": 13,
    "fonts.weight": "normal",
    "fonts.lineHeight": 1.4,
    "fonts.letterSpacing": 0,

    // Editor fonts (inherits from fonts.mono)
    "editor.fontFamily": ["JetBrains Mono", "Consolas", "Monaco", "monospace"],
    "editor.fontSize": 14,
    "editor.fontWeight": "normal",
    "editor.lineHeight": 1.5,
    "editor.letterSpacing": 0,

    // Terminal fonts (inherits from fonts.mono)
    "terminal.fontFamily": ["Cascadia Code", "Fira Code", "Consolas", "monospace"],
    "terminal.fontSize": 13,
    "terminal.fontWeight": "normal",
    "terminal.lineHeight": 1.2,
    "terminal.letterSpacing": 0.5,

    // UI fonts (inherits from fonts.ui)
    "ui.fontFamily": ["Segoe UI", "Ubuntu", "Roboto", "sans-serif"],
    "ui.fontSize": 13,
    "ui.fontWeight": "normal",
    "ui.lineHeight": 1.4,

    // Widget-specific fonts (can override base)
    "tabs.fontFamily": ["Segoe UI Semibold", "Ubuntu", "Roboto", "sans-serif"],
    "tabs.fontSize": 12,
    "tabs.fontWeight": "semibold",

    "menu.fontFamily": ["Segoe UI", "Ubuntu", "sans-serif"],
    "menu.fontSize": 13,

    "button.fontFamily": ["Segoe UI", "Ubuntu", "sans-serif"],
    "button.fontSize": 13,
    "button.fontWeight": "normal",

    "heading.fontFamily": ["Segoe UI", "Ubuntu", "sans-serif"],
    "heading.fontSize": 18,
    "heading.fontWeight": "semibold"
  },
  "styles": { ... },
  "metadata": { ... }
}
```

### 2. Font Token Hierarchy (Like Color Overrides)

Support hierarchical font resolution similar to color tokens:

#### Hierarchy Pattern
```
specific → widget → category → base → system default
```

#### Examples

**Terminal Widget Font Resolution:**
```
terminal.fontFamily → fonts.mono → system monospace
terminal.fontSize → fonts.size → 13
terminal.lineHeight → fonts.lineHeight → 1.4
```

**Tab Widget Font Resolution:**
```
tabs.fontFamily → ui.fontFamily → fonts.ui → system sans-serif
tabs.fontSize → ui.fontSize → fonts.size → 13
tabs.fontWeight → ui.fontWeight → fonts.weight → "normal"
```

**MultisplitWidget Tab Bar Example:**
```python
class MultisplitWidget(ThemedWidget):
    theme_config = {
        # Colors
        "background": "widget.background",
        "foreground": "widget.foreground",
        # Tabs use UI fonts
        "tab.fontFamily": "tabs.fontFamily",  # → ui.fontFamily → fonts.ui
        "tab.fontSize": "tabs.fontSize",       # → ui.fontSize → fonts.size
        "tab.fontWeight": "tabs.fontWeight",   # → ui.fontWeight → fonts.weight
    }
```

**TerminalWidget Font Resolution:**
```python
class TerminalWidget(ThemedWidget):
    theme_config = {
        # Colors with hierarchy
        "background": "terminal.colors.background",  # → colors.background
        "foreground": "terminal.colors.foreground",  # → colors.foreground

        # Fonts with hierarchy - MUST be monospace
        "fontFamily": "terminal.fontFamily",      # → fonts.mono (NOT fonts.ui!)
        "fontSize": "terminal.fontSize",          # → fonts.size
        "fontWeight": "terminal.fontWeight",      # → fonts.weight
        "lineHeight": "terminal.lineHeight",      # → fonts.lineHeight
        "letterSpacing": "terminal.letterSpacing", # → fonts.letterSpacing
    }
```

#### Font Category Guarantees

**Important**: Base font categories provide semantic guarantees:

- `fonts.mono`: **Always** monospace fonts (for code/terminal)
- `fonts.ui`: **Always** sans-serif fonts (for UI elements)
- `fonts.serif`: **Always** serif fonts (for documents)

This ensures:
- Terminals always get monospace fonts
- UI elements always get readable sans-serif fonts
- Documents can use serif fonts for better readability

### 3. Font Data Model

Add to `Theme` dataclass in `core/theme.py`:

```python
from typing import TypedDict, Union

# Font type definitions
FontFamily = Union[str, list[str]]  # Single font or fallback chain
FontSize = Union[int, float]  # Point size
FontWeight = Union[int, str]  # 100-900 or "normal", "bold", "semibold", etc.
LineHeight = float  # Multiplier (1.0 = 100%)
LetterSpacing = Union[int, float]  # Pixels

class FontProperties(TypedDict, total=False):
    """Font property bundle."""
    family: FontFamily
    size: FontSize
    weight: FontWeight
    style: str  # "normal", "italic", "oblique"
    lineHeight: LineHeight
    letterSpacing: LetterSpacing

FontPalette = dict[str, Union[FontFamily, FontSize, FontWeight, str, float]]

@dataclass(frozen=True)
class Theme:
    name: str
    version: str = "1.0.0"
    colors: ColorPalette = field(default_factory=dict)
    fonts: FontPalette = field(default_factory=dict)  # NEW
    styles: StyleProperties = field(default_factory=dict)
    metadata: ThemeMetadata = field(default_factory=dict)
    token_colors: TokenColors = field(default_factory=list)
    type: str = "light"
```

### 4. Font Token Registry (With Hierarchical Resolution)

Create `core/font_tokens.py`:

```python
"""Font token registry and resolution.

Provides fast, cached font token lookup with hierarchical resolution
similar to ColorTokenRegistry.

Resolution follows the pattern:
    specific.property → widget.property → category.property → fonts.property → default

Examples:
    terminal.fontFamily → fonts.mono → ["Consolas", "monospace"]
    tabs.fontSize → ui.fontSize → fonts.size → 13
"""

from typing import Optional, Union
from functools import lru_cache
from PySide6.QtGui import QFont, QFontDatabase

class FontTokenRegistry:
    """Central registry for font token resolution with hierarchy."""

    # Hierarchical resolution chains (like colors)
    HIERARCHY_MAP = {
        "terminal.fontFamily": ["terminal.fontFamily", "fonts.mono"],
        "terminal.fontSize": ["terminal.fontSize", "fonts.size"],
        "terminal.fontWeight": ["terminal.fontWeight", "fonts.weight"],
        "terminal.lineHeight": ["terminal.lineHeight", "fonts.lineHeight"],
        "terminal.letterSpacing": ["terminal.letterSpacing", "fonts.letterSpacing"],

        "editor.fontFamily": ["editor.fontFamily", "fonts.mono"],
        "editor.fontSize": ["editor.fontSize", "fonts.size"],
        "editor.fontWeight": ["editor.fontWeight", "fonts.weight"],

        "tabs.fontFamily": ["tabs.fontFamily", "ui.fontFamily", "fonts.ui"],
        "tabs.fontSize": ["tabs.fontSize", "ui.fontSize", "fonts.size"],
        "tabs.fontWeight": ["tabs.fontWeight", "ui.fontWeight", "fonts.weight"],

        "ui.fontFamily": ["ui.fontFamily", "fonts.ui"],
        "ui.fontSize": ["ui.fontSize", "fonts.size"],
        "ui.fontWeight": ["ui.fontWeight", "fonts.weight"],

        "button.fontFamily": ["button.fontFamily", "ui.fontFamily", "fonts.ui"],
        "menu.fontFamily": ["menu.fontFamily", "ui.fontFamily", "fonts.ui"],
    }

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_family(token: str, theme: Theme) -> Optional[list[str]]:
        """Get font family with hierarchical fallback resolution.

        Example:
            get_font_family("terminal.fontFamily", theme)
            → Tries: terminal.fontFamily → fonts.mono → default
        """
        # Get resolution chain
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        # Try each token in chain
        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                # Normalize to list
                if isinstance(value, str):
                    return [value]
                elif isinstance(value, list):
                    return value

        # System defaults based on category
        if "mono" in token or "terminal" in token or "editor" in token:
            return ["Consolas", "Monaco", "monospace"]
        elif "serif" in token:
            return ["Georgia", "Times New Roman", "serif"]
        else:
            return ["Segoe UI", "Ubuntu", "Roboto", "sans-serif"]

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_size(token: str, theme: Theme) -> Optional[int]:
        """Get font size with hierarchical resolution.

        Example:
            get_font_size("tabs.fontSize", theme)
            → Tries: tabs.fontSize → ui.fontSize → fonts.size → 13
        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return int(value)

        # Default size
        return 13

    @staticmethod
    @lru_cache(maxsize=256)
    def get_font_weight(token: str, theme: Theme) -> Optional[int]:
        """Get font weight (100-900) with hierarchical resolution.

        Converts string weights to Qt values:
        - "thin" → 100, "light" → 300, "normal" → 400
        - "medium" → 500, "semibold" → 600, "bold" → 700
        - "black" → 900
        """
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        weight_map = {
            "thin": 100, "light": 300, "normal": 400,
            "medium": 500, "semibold": 600, "bold": 700,
            "black": 900
        }

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, int):
                    return value
                elif isinstance(value, str):
                    return weight_map.get(value.lower(), 400)

        return 400  # Normal

    @staticmethod
    @lru_cache(maxsize=256)
    def get_line_height(token: str, theme: Theme) -> Optional[float]:
        """Get line height multiplier with hierarchical resolution."""
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return float(value)

        return 1.4  # Default

    @staticmethod
    @lru_cache(maxsize=256)
    def get_letter_spacing(token: str, theme: Theme) -> Optional[float]:
        """Get letter spacing in pixels with hierarchical resolution."""
        chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

        for candidate_token in chain:
            if candidate_token in theme.fonts:
                value = theme.fonts[candidate_token]
                if isinstance(value, (int, float)):
                    return float(value)

        return 0.0  # Default

    @staticmethod
    def get_qfont(token: str, theme: Theme) -> Optional[QFont]:
        """Get complete QFont instance with all properties resolved.

        Example:
            font = FontTokenRegistry.get_qfont("terminal.fontFamily", theme)
            # Returns QFont with:
            # - Family: First available from terminal.fontFamily chain
            # - Size: From terminal.fontSize chain
            # - Weight: From terminal.fontWeight chain
        """
        # Get base token (family)
        base_token = token.replace(".fontFamily", "")

        # Resolve all properties
        families = FontTokenRegistry.get_font_family(f"{base_token}.fontFamily", theme)
        size = FontTokenRegistry.get_font_size(f"{base_token}.fontSize", theme)
        weight = FontTokenRegistry.get_font_weight(f"{base_token}.fontWeight", theme)

        # Create QFont with first available family
        available_family = FontTokenRegistry.get_available_font(families)
        if not available_family:
            available_family = families[-1]  # Use last fallback

        font = QFont(available_family, size)
        font.setWeight(QFont.Weight(weight))

        return font

    @staticmethod
    @lru_cache(maxsize=64)
    def get_available_font(families: tuple[str, ...]) -> Optional[str]:
        """Get first available font from fallback chain.

        Args:
            families: Tuple of font family names (tuple for caching)

        Returns:
            First available font family, or None if none found
        """
        db = QFontDatabase()
        available_families = set(db.families())

        for family in families:
            # Exact match
            if family in available_families:
                return family

            # Case-insensitive match
            for available in available_families:
                if available.lower() == family.lower():
                    return available

        return None

    @staticmethod
    def clear_cache():
        """Clear LRU caches (useful for testing or theme reload)."""
        FontTokenRegistry.get_font_family.cache_clear()
        FontTokenRegistry.get_font_size.cache_clear()
        FontTokenRegistry.get_font_weight.cache_clear()
        FontTokenRegistry.get_line_height.cache_clear()
        FontTokenRegistry.get_letter_spacing.cache_clear()
        FontTokenRegistry.get_available_font.cache_clear()
```

### 5. ThemedWidget Font Integration

Update `widgets/base.py` to support font properties:

```python
class ThemedWidget:
    """Base class for themed widgets with font support."""

    # Widget declares font token mapping
    theme_config = {
        # Colors
        "background": "editor.background",
        "foreground": "editor.foreground",
        # Fonts (NEW)
        "font": "editor.font",  # Complete font bundle
        "fontFamily": "editor.fontFamily",
        "fontSize": "editor.fontSize",
    }

    def on_theme_changed(self, theme: Optional[Theme] = None) -> None:
        """Apply theme including fonts."""
        # ... existing color logic ...

        # Apply fonts
        self._apply_fonts(theme)

    def _apply_fonts(self, theme: Theme) -> None:
        """Apply font configuration from theme."""
        if "font" in self.theme_config:
            # Get complete QFont
            qfont = FontTokenRegistry.get_qfont(self.theme_config["font"], theme)
            if qfont:
                self.setFont(qfont)

        elif "fontFamily" in self.theme_config:
            # Apply individual font properties
            font = self.font()

            family_token = self.theme_config.get("fontFamily")
            if family_token:
                families = FontTokenRegistry.get_font_family(family_token, theme)
                if families:
                    available = FontTokenRegistry.get_available_font(families)
                    if available:
                        font.setFamily(available)

            size_token = self.theme_config.get("fontSize")
            if size_token:
                size = FontTokenRegistry.get_font_size(size_token, theme)
                if size:
                    font.setPointSize(size)

            self.setFont(font)
```

### 6. Font Validation

Add validation in `Theme.__post_init__()`:

```python
def __post_init__(self) -> None:
    """Validate theme data after creation."""
    # ... existing validation ...

    # Validate fonts
    for key, value in self.fonts.items():
        if not self._is_valid_font_property(key, value):
            raise InvalidThemeFormatError(f"Invalid font property '{key}': {value}")

def _is_valid_font_property(self, key: str, value: Any) -> bool:
    """Validate font property."""
    # fontFamily: string or list of strings
    if "fontFamily" in key or "family" in key.lower():
        if isinstance(value, str):
            return True
        if isinstance(value, list):
            return all(isinstance(f, str) for f in value)
        return False

    # fontSize: number
    if "fontSize" in key or "size" in key.lower():
        return isinstance(value, (int, float)) and value > 0

    # fontWeight: number (100-900) or string
    if "fontWeight" in key or "weight" in key.lower():
        if isinstance(value, int):
            return 100 <= value <= 900
        if isinstance(value, str):
            return value in ["normal", "bold", "semibold", "light", "thin", "medium", "black"]
        return False

    # lineHeight: number >= 1.0
    if "lineHeight" in key or "line" in key.lower():
        return isinstance(value, (int, float)) and value >= 0.5

    # letterSpacing: number
    if "letterSpacing" in key or "spacing" in key.lower():
        return isinstance(value, (int, float))

    return True
```

### 7. Terminal Font Integration

Update `TerminalWidget` to use theme fonts:

```python
class TerminalWidget(ThemedWidget):
    """Terminal widget with font support."""

    theme_config = {
        # Colors
        "background": "terminal.colors.background",
        "foreground": "terminal.colors.foreground",
        # Fonts
        "fontFamily": "terminal.fontFamily",
        "fontSize": "terminal.fontSize",
        "lineHeight": "terminal.lineHeight",
        "letterSpacing": "terminal.letterSpacing",
    }

    def _apply_theme(self, theme_config: dict) -> None:
        """Apply theme to xterm.js."""
        # Extract font configuration
        font_family = theme_config.get("fontFamily", ["monospace"])
        font_size = theme_config.get("fontSize", 14)
        line_height = theme_config.get("lineHeight", 1.2)
        letter_spacing = theme_config.get("letterSpacing", 0)

        # Convert to xterm.js font family string
        if isinstance(font_family, list):
            font_family_str = ", ".join(f'"{f}"' if " " in f else f for f in font_family)
        else:
            font_family_str = font_family

        # Build xterm.js config
        xterm_config = {
            "fontFamily": font_family_str,
            "fontSize": font_size,
            "lineHeight": line_height,
            "letterSpacing": letter_spacing,
            # ... colors ...
        }

        # Apply to xterm.js
        self._send_theme_to_terminal(xterm_config)
```

### 8. Theme Studio Integration

Add font editor to Theme Studio:

```python
# New widget: FontPropertyEditor
class FontPropertyEditor(QWidget):
    """Editor for font properties."""

    def __init__(self):
        # Font family combo box (with available fonts)
        # Font size spin box
        # Font weight combo box
        # Line height spin box
        # Letter spacing spin box
        # Preview label
```

---

## Testing Strategy

### 1. Unit Tests (pytest)

**File**: `tests/unit/test_font_tokens.py`

```python
"""Unit tests for FontTokenRegistry."""

def test_font_family_resolution():
    """Test hierarchical font family resolution."""
    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
            "terminal.fontFamily": ["Cascadia Code", "Fira Code", "monospace"],
        }
    )

    # Terminal uses specific override
    families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    assert families == ["Cascadia Code", "Fira Code", "monospace"]

    # Editor falls back to fonts.mono
    families = FontTokenRegistry.get_font_family("editor.fontFamily", theme)
    assert families == ["JetBrains Mono", "Consolas", "monospace"]

def test_font_size_fallback():
    """Test font size resolution with fallbacks."""
    theme = Theme(
        name="Test",
        fonts={
            "fonts.size": 13,
            "terminal.fontSize": 14,
        }
    )

    assert FontTokenRegistry.get_font_size("terminal.fontSize", theme) == 14
    assert FontTokenRegistry.get_font_size("editor.fontSize", theme) == 13  # Fallback
    assert FontTokenRegistry.get_font_size("tabs.fontSize", theme) == 13    # Fallback

def test_font_category_guarantees():
    """Test that categories provide correct font types."""
    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "sans-serif"],
        }
    )

    # Terminal MUST get monospace
    mono_fonts = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    assert "monospace" in mono_fonts

    # Tabs MUST get sans-serif
    ui_fonts = FontTokenRegistry.get_font_family("tabs.fontFamily", theme)
    assert "sans-serif" in ui_fonts

def test_font_weight_conversion():
    """Test string to numeric weight conversion."""
    theme = Theme(
        name="Test",
        fonts={
            "fonts.weight": "semibold",
            "terminal.fontWeight": 700,
        }
    )

    assert FontTokenRegistry.get_font_weight("fonts.weight", theme) == 600
    assert FontTokenRegistry.get_font_weight("terminal.fontWeight", theme) == 700

def test_available_font_detection():
    """Test platform font availability checking."""
    # Platform-specific test
    available = FontTokenRegistry.get_available_font(
        ["NonexistentFont", "Consolas", "monospace"]
    )
    assert available in ["Consolas", "monospace"]  # One should exist
```

### 2. Integration Tests (pytest-qt)

**File**: `tests/integration/test_themed_fonts.py`

```python
"""Integration tests for font application to widgets."""

def test_terminal_receives_monospace(qtbot):
    """Test that TerminalWidget receives monospace fonts."""
    app = ThemedApplication()

    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "sans-serif"],
        }
    )
    app.set_theme(theme)

    terminal = TerminalWidget()
    qtbot.addWidget(terminal)

    # Verify terminal got monospace (via internal config)
    # This would check the xterm.js config sent to JS
    assert "monospace" in terminal._last_xterm_config["fontFamily"].lower()

def test_tab_bar_receives_ui_fonts(qtbot):
    """Test that tab bars receive UI fonts, not monospace."""
    app = ThemedApplication()

    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["Consolas", "monospace"],
            "fonts.ui": ["Segoe UI", "sans-serif"],
            "tabs.fontSize": 12,
        }
    )
    app.set_theme(theme)

    multisplit = MultisplitWidget()
    qtbot.addWidget(multisplit)

    # Verify tab bar got UI fonts
    tab_bar = multisplit.findChild(QTabBar)
    font = tab_bar.font()
    assert font.family() in ["Segoe UI", "Ubuntu", "Roboto"]  # Platform-specific
    assert font.pointSize() == 12

def test_theme_change_updates_fonts(qtbot):
    """Test that changing theme updates widget fonts."""
    app = ThemedApplication()
    terminal = TerminalWidget()
    qtbot.addWidget(terminal)

    # Apply first theme
    theme1 = Theme(name="Small", fonts={"terminal.fontSize": 12})
    app.set_theme(theme1)
    assert terminal._last_xterm_config["fontSize"] == 12

    # Apply second theme
    theme2 = Theme(name="Large", fonts={"terminal.fontSize": 16})
    app.set_theme(theme2)
    assert terminal._last_xterm_config["fontSize"] == 16
```

### 3. Visual Tests (Example Applications)

**File**: `examples/font_showcase.py`

```python
"""Visual test application showing all font tokens."""

class FontShowcaseWindow(QMainWindow, ThemedWidget):
    """Window displaying all font categories and their rendering."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VFWidgets Font Showcase")

        central = QWidget()
        layout = QVBoxLayout(central)

        # Show each font category
        self._add_font_sample(layout, "Monospace Fonts", "fonts.mono",
                             "The quick brown fox jumps over the lazy dog 0123456789")
        self._add_font_sample(layout, "UI Fonts", "fonts.ui",
                             "The quick brown fox jumps over the lazy dog")
        self._add_font_sample(layout, "Terminal Font", "terminal.fontFamily",
                             "$ npm install @types/node\n> Success!")
        self._add_font_sample(layout, "Tab Font", "tabs.fontFamily",
                             "Terminal 1  Terminal 2  Terminal 3")

        # Add theme selector
        theme_selector = QComboBox()
        theme_selector.addItems(["Dark Default", "Light Default", "High Contrast"])
        theme_selector.currentTextChanged.connect(self._on_theme_selected)
        layout.addWidget(theme_selector)

        self.setCentralWidget(central)

    def _add_font_sample(self, layout, title, token, sample_text):
        """Add a font sample widget."""
        group = QGroupBox(title)
        group_layout = QVBoxLayout()

        # Font info label
        info = QLabel()
        group_layout.addWidget(info)

        # Sample text
        sample = QTextEdit()
        sample.setPlainText(sample_text)
        sample.setReadOnly(True)
        group_layout.addWidget(sample)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Store for theme updates
        sample.setProperty("font_token", token)
        info.setProperty("font_info_for", token)

    def on_theme_changed(self, theme):
        """Update all font samples when theme changes."""
        for widget in self.findChildren(QTextEdit):
            token = widget.property("font_token")
            if token:
                font = FontTokenRegistry.get_qfont(token, theme)
                widget.setFont(font)

                # Update info label
                info_label = self.findChild(QLabel, f"info_{token}")
                families = FontTokenRegistry.get_font_family(token, theme)
                size = FontTokenRegistry.get_font_size(f"{token.split('.')[0]}.fontSize", theme)
                info_label.setText(f"Family: {families[0]}, Size: {size}pt")

if __name__ == "__main__":
    app = ThemedApplication()
    window = FontShowcaseWindow()
    window.show()
    sys.exit(app.exec())
```

**File**: `examples/font_comparison.py`

```python
"""Side-by-side comparison of themes with different fonts."""

class FontComparisonWindow(QMainWindow):
    """Split window showing two themes side-by-side."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Font Theme Comparison")

        splitter = QSplitter()

        # Left: Small monospace terminal
        left_terminal = TerminalWidget()
        splitter.addWidget(left_terminal)

        # Right: Large monospace terminal
        right_terminal = TerminalWidget()
        splitter.addWidget(right_terminal)

        self.setCentralWidget(splitter)

        # Apply different font sizes
        theme_small = Theme(name="Small", fonts={"terminal.fontSize": 11})
        theme_large = Theme(name="Large", fonts={"terminal.fontSize": 16})

        left_terminal.on_theme_changed(theme_small)
        right_terminal.on_theme_changed(theme_large)
```

### 4. Theme Studio Integration Tests

**File**: `apps/theme-studio/tests/test_font_editor.py`

```python
"""Tests for font editing in Theme Studio."""

def test_font_property_editor(qtbot):
    """Test FontPropertyEditor widget."""
    editor = FontPropertyEditor()
    qtbot.addWidget(editor)

    # Set initial font
    editor.set_font_family(["JetBrains Mono", "Consolas"])
    editor.set_font_size(14)
    editor.set_font_weight("semibold")

    # Verify values
    assert editor.get_font_family() == ["JetBrains Mono", "Consolas"]
    assert editor.get_font_size() == 14
    assert editor.get_font_weight() == "semibold"

def test_font_preview_updates(qtbot):
    """Test that font preview updates when properties change."""
    editor = FontPropertyEditor()
    qtbot.addWidget(editor)

    # Change font size
    editor.set_font_size(18)

    # Verify preview updated
    preview = editor.findChild(QLabel, "preview")
    assert preview.font().pointSize() == 18

def test_theme_save_includes_fonts(qtbot, tmp_path):
    """Test that saving theme includes font data."""
    studio = ThemeStudioWindow()
    qtbot.addWidget(studio)

    # Edit fonts
    studio.set_font_token("terminal.fontFamily", ["Cascadia Code", "monospace"])
    studio.set_font_token("terminal.fontSize", 14)

    # Save theme
    theme_file = tmp_path / "test-theme.json"
    studio.save_theme(str(theme_file))

    # Verify saved data
    with open(theme_file) as f:
        data = json.load(f)

    assert "fonts" in data
    assert data["fonts"]["terminal.fontFamily"] == ["Cascadia Code", "monospace"]
    assert data["fonts"]["terminal.fontSize"] == 14
```

### 5. Performance Tests

**File**: `tests/performance/test_font_performance.py`

```python
"""Performance tests for font token resolution."""

def test_font_resolution_performance():
    """Test that font resolution is fast (<1ms per lookup)."""
    theme = Theme(
        name="Test",
        fonts={
            "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
            "terminal.fontFamily": ["Cascadia Code", "Fira Code", "monospace"],
            "terminal.fontSize": 14,
        }
    )

    import time

    # Warm up cache
    FontTokenRegistry.get_font_family("terminal.fontFamily", theme)

    # Measure cached performance
    start = time.perf_counter()
    for _ in range(10000):
        FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    elapsed = time.perf_counter() - start

    # Should be < 1ms per lookup (with caching)
    assert elapsed / 10000 < 0.001

def test_qfont_creation_performance():
    """Test QFont creation performance."""
    theme = Theme(
        name="Test",
        fonts={
            "terminal.fontFamily": ["Consolas", "monospace"],
            "terminal.fontSize": 14,
        }
    )

    import time
    start = time.perf_counter()

    for _ in range(1000):
        font = FontTokenRegistry.get_qfont("terminal.fontFamily", theme)

    elapsed = time.perf_counter() - start

    # Should be < 1ms per QFont creation
    assert elapsed / 1000 < 0.001
```

### 6. Cross-Platform Tests

**File**: `tests/platform/test_font_availability.py`

```python
"""Tests for font availability across platforms."""

def test_monospace_fonts_available():
    """Test that monospace fallbacks work on all platforms."""
    # Every platform should have at least one of these
    common_mono = ["Consolas", "Monaco", "Courier New", "monospace"]

    available = FontTokenRegistry.get_available_font(tuple(common_mono))
    assert available is not None

def test_ui_fonts_available():
    """Test that UI fonts work on all platforms."""
    # Every platform should have at least one of these
    common_ui = ["Segoe UI", "Ubuntu", "Roboto", "Arial", "sans-serif"]

    available = FontTokenRegistry.get_available_font(tuple(common_ui))
    assert available is not None

@pytest.mark.parametrize("platform,expected_fonts", [
    ("Windows", ["Consolas", "Segoe UI"]),
    ("Linux", ["Ubuntu Mono", "Ubuntu"]),
    ("Darwin", ["Monaco", "San Francisco"]),
])
def test_platform_specific_fonts(platform, expected_fonts):
    """Test that platform-specific fonts are detected."""
    if sys.platform.startswith(platform.lower()):
        for font in expected_fonts:
            families = QFontDatabase().families()
            assert any(font.lower() in f.lower() for f in families)
```

---

## Implementation Plan (Updated with Testing)

### Phase 1: Core Infrastructure (Week 1)
1. Add `fonts` field to `Theme` dataclass
2. Add font validation in `Theme.__post_init__()`
3. Create `FontTokenRegistry` class
4. Update theme JSON schema
5. Add font tokens to package themes (dark-default, light-default, high-contrast)
6. **Write unit tests** (`test_font_tokens.py`)

### Phase 2: Widget Integration (Week 2)
1. Add font support to `ThemedWidget.on_theme_changed()`
2. Update `TerminalWidget` to use theme fonts
3. Test font application and fallback chains
4. Add font property introspection
5. **Write integration tests** (`test_themed_fonts.py`)
6. **Create example apps** (`font_showcase.py`, `font_comparison.py`)

### Phase 3: Theme Studio (Week 3)
1. Create `FontPropertyEditor` widget
2. Add font section to Theme Studio UI
3. Add font preview functionality
4. Test font editing and saving
5. **Write Theme Studio tests** (`test_font_editor.py`)

### Phase 4: Documentation & Polish (Week 4)
1. Update theme documentation with font examples
2. Add migration guide for existing themes
3. **Performance testing** and optimization (`test_font_performance.py`)
4. **Cross-platform testing** (`test_font_availability.py`)
5. Release as theme system v2.1.0

---

## Example Theme with Fonts

```json
{
  "$schema": "https://vfwidgets.org/schemas/theme-v2.json",
  "name": "Dark Professional",
  "type": "dark",
  "version": "2.0.0",
  "metadata": {
    "author": "VFWidgets Team",
    "description": "Professional dark theme with custom fonts"
  },
  "colors": {
    "colors.background": "#1e1e1e",
    "colors.foreground": "#d4d4d4",
    "..."
  },
  "fonts": {
    // Base font categories (REQUIRED - provide defaults)
    "fonts.mono": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
    "fonts.ui": ["Inter", "Segoe UI", "Ubuntu", "Roboto", "sans-serif"],
    "fonts.serif": ["Georgia", "Times New Roman", "serif"],
    "fonts.size": 13,
    "fonts.weight": "normal",
    "fonts.lineHeight": 1.4,
    "fonts.letterSpacing": 0,

    // Terminal fonts (overrides fonts.mono)
    "terminal.fontFamily": ["Cascadia Code", "Fira Code", "Consolas", "monospace"],
    "terminal.fontSize": 13,
    "terminal.lineHeight": 1.2,
    "terminal.letterSpacing": 0.5,

    // Editor fonts (overrides fonts.mono)
    "editor.fontFamily": ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
    "editor.fontSize": 14,
    "editor.lineHeight": 1.5,

    // UI fonts (overrides fonts.ui)
    "ui.fontSize": 13,
    "ui.fontWeight": "normal",

    // Tab fonts (inherits from ui)
    "tabs.fontSize": 12,
    "tabs.fontWeight": "semibold",

    // Button/Menu fonts (inherits from ui)
    "button.fontSize": 13,
    "menu.fontSize": 13,

    // Heading fonts
    "heading.fontSize": 18,
    "heading.fontWeight": "semibold"
  }
}
```

## Real-World Widget Examples

### MultisplitWidget with Tabs

```python
class MultisplitWidget(ThemedWidget):
    """Split pane container with themed tab bar."""

    theme_config = {
        # Splitter colors
        "handle_bg": "widget.background",
        "handle_hover_bg": "list.hoverBackground",
        "handle_border": "widget.border",

        # Tab bar fonts (uses UI fonts, NOT mono)
        "tab.fontFamily": "tabs.fontFamily",  # → ui.fontFamily → fonts.ui
        "tab.fontSize": "tabs.fontSize",       # → ui.fontSize → fonts.size
        "tab.fontWeight": "tabs.fontWeight",   # → ui.fontWeight → fonts.weight
    }

    def _create_tab_bar(self):
        """Create tab bar with themed fonts."""
        tab_bar = QTabBar()

        # Get font from theme (automatically resolved)
        # Result: Inter/Segoe UI, 12pt, semibold
        font = FontTokenRegistry.get_qfont("tabs.fontFamily", self._current_theme)
        if font:
            tab_bar.setFont(font)

        return tab_bar
```

### TerminalWidget (MUST use monospace)

```python
class TerminalWidget(ThemedWidget):
    """Terminal widget - ALWAYS uses monospace fonts."""

    theme_config = {
        # Colors with hierarchy
        "background": "terminal.colors.background",
        "foreground": "terminal.colors.foreground",

        # Fonts with hierarchy - resolves to fonts.mono
        "fontFamily": "terminal.fontFamily",      # → fonts.mono
        "fontSize": "terminal.fontSize",          # → fonts.size
        "lineHeight": "terminal.lineHeight",      # → fonts.lineHeight
        "letterSpacing": "terminal.letterSpacing", # → fonts.letterSpacing
    }

    def _apply_theme(self, theme: Theme):
        """Apply theme to xterm.js."""
        # Get font properties with fallbacks
        families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
        # Result: ["Cascadia Code", "Fira Code", "Consolas", "monospace"]

        size = FontTokenRegistry.get_font_size("terminal.fontSize", theme)
        # Result: 13 (from terminal.fontSize or fonts.size)

        line_height = FontTokenRegistry.get_line_height("terminal.lineHeight", theme)
        # Result: 1.2 (from terminal.lineHeight or fonts.lineHeight)

        letter_spacing = FontTokenRegistry.get_letter_spacing("terminal.letterSpacing", theme)
        # Result: 0.5 (from terminal.letterSpacing or fonts.letterSpacing)

        # Convert to xterm.js format
        font_family_str = ", ".join(f'"{f}"' for f in families)

        xterm_config = {
            "fontFamily": font_family_str,
            "fontSize": size,
            "lineHeight": line_height,
            "letterSpacing": letter_spacing,
            # ... colors ...
        }

        self._send_to_js("applyTheme", xterm_config)
```

### Button Widget (UI fonts)

```python
class ThemedButton(ThemedWidget, QPushButton):
    """Button with themed UI fonts."""

    theme_config = {
        "background": "button.background",
        "foreground": "button.foreground",
        "fontFamily": "button.fontFamily",  # → ui.fontFamily → fonts.ui
        "fontSize": "button.fontSize",       # → ui.fontSize → fonts.size
    }

    # ThemedWidget automatically applies fonts via on_theme_changed()
```

---

## Benefits

1. **Consistent typography**: Single source of truth for fonts across application
2. **Theme completeness**: Fonts are as important as colors for visual identity
3. **Cross-platform**: Fallback chains ensure good experience on all platforms
4. **Easy customization**: Users can customize fonts without code changes
5. **Widget simplicity**: Widgets automatically get fonts from theme
6. **Professional results**: Better typography = better UX

---

## Migration Strategy

### For Theme Authors
1. Add `fonts` section to existing themes (optional, has defaults)
2. Test font rendering on target platforms
3. Update theme version to 2.0.0

### For Widget Developers
1. Add font tokens to `theme_config` if custom fonts needed
2. Widget automatically gets system default fonts if not specified
3. No breaking changes - fonts are optional enhancement

### For Applications
1. Update theme system to v2.1.0
2. Existing themes continue to work (backward compatible)
3. New themes can use font tokens

---

## Open Questions

1. **Font licensing**: How to handle licensed fonts? (Answer: Document in theme metadata)
2. **Font loading time**: Any performance impact? (Answer: Qt caches fonts)
3. **Variable fonts**: Support OpenType features? (Future enhancement)
4. **Font smoothing**: Platform-specific rendering? (Use Qt defaults)
5. **Font metrics**: Need more than family/size/weight? (Start minimal, extend later)

---

## Future Enhancements

1. **Font presets**: Named combinations like "Coding Dark", "Professional Light"
2. **Font scaling**: Relative sizing (small, medium, large)
3. **Per-widget overrides**: Allow widgets to override specific font properties
4. **Font bundles**: Package fonts with themes (complex, needs careful design)
5. **OpenType features**: Ligatures, stylistic sets, etc.
6. **Accessibility**: High contrast fonts, dyslexia-friendly options

---

## References

- VSCode font settings: `editor.fontFamily`, `terminal.integrated.fontFamily`
- Qt font system: `QFont`, `QFontDatabase`, `QFontMetrics`
- CSS font properties: `font-family`, `font-size`, `font-weight`, `line-height`
- Material Design typography: Size/weight scale system
- Apple Human Interface Guidelines: Typography best practices
