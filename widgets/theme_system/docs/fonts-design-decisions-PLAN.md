# Font Support Design Decisions

**Status: 🎯 Decision Phase - Research & Recommendations**

This document provides researched recommendations for the High Priority design questions.

---

## 1. Token Conflicts - Resolution Strategy

### The Problem

What if a theme has both category-specific and generic tokens?

```json
{
  "fonts": {
    "fonts.mono": ["JetBrains Mono", "monospace"],     // Category-specific
    "fonts.fontFamily": ["Arial", "sans-serif"],       // Generic? ❓

    "terminal.fontFamily": ["Cascadia Code", "monospace"],  // Widget-specific
  }
}
```

**Question**: If `terminal.fontFamily` is missing, should it fall back to `fonts.mono` or `fonts.fontFamily`?

### Research: Industry Standards

#### VSCode Approach
```json
{
  "editor.fontFamily": "JetBrains Mono",           // Specific
  "terminal.integrated.fontFamily": "Cascadia Code", // Specific
  // NO generic "fontFamily" - only category-specific!
}
```

**VSCode Pattern**: ✅ **No generic fallback** - each context has its own token

#### CSS Approach
```css
/* Generic (low specificity) */
* { font-family: Arial, sans-serif; }

/* Category-specific (medium specificity) */
code, pre { font-family: "Courier New", monospace; }

/* Widget-specific (high specificity) */
.terminal { font-family: "Cascadia Code", monospace; }
```

**CSS Pattern**: ✅ **Specificity cascade** - more specific overrides generic

#### Qt Approach
```cpp
// QApplication default font (affects all widgets)
QApplication::setFont(QFont("Arial", 12));

// Widget-specific font (overrides default)
myWidget->setFont(QFont("Consolas", 14));
```

**Qt Pattern**: ✅ **Application default + widget override**

### Recommendation: Hierarchical Categories (No Generic)

**Decision**: ❌ **DON'T support generic `fonts.fontFamily`**

**Rationale**:
1. **Semantic clarity**: `fonts.mono` means "monospace", `fonts.ui` means "sans-serif"
2. **Type safety**: Prevents accidentally using sans-serif for terminal
3. **Explicit is better**: Theme author must think about font purpose
4. **Follows VSCode**: Industry-proven pattern

**Resolution Hierarchy**:
```
specific → category → system default

Examples:
terminal.fontFamily → fonts.mono → ["Consolas", "monospace"] (system)
tabs.fontFamily → ui.fontFamily → fonts.ui → ["Arial", "sans-serif"] (system)
```

**Schema**:
```json
{
  "fonts": {
    // Base categories (REQUIRED)
    "fonts.mono": ["JetBrains Mono", "Consolas", "monospace"],
    "fonts.ui": ["Segoe UI", "Inter", "Ubuntu", "sans-serif"],
    "fonts.serif": ["Georgia", "Times New Roman", "serif"],

    // Base properties (apply to all unless overridden)
    "fonts.size": 13,
    "fonts.weight": "normal",
    "fonts.lineHeight": 1.4,
    "fonts.letterSpacing": 0,

    // Widget/category overrides
    "terminal.fontFamily": [...],  // Overrides fonts.mono
    "terminal.fontSize": 14,       // Overrides fonts.size

    "ui.fontSize": 13,             // Used by tabs, buttons, etc.
    "tabs.fontWeight": "semibold", // Overrides ui.fontWeight → fonts.weight
  }
}
```

**Validation Rules**:
1. ✅ `fonts.mono`, `fonts.ui`, `fonts.serif` are **required** (or have system defaults)
2. ✅ All font families in `fonts.mono` MUST include "monospace" as final fallback
3. ✅ All font families in `fonts.ui` MUST include "sans-serif" or "serif" as final fallback
4. ❌ `fonts.fontFamily` is **not allowed** (validation error)

---

## 2. Bundle vs Individual Properties

### The Problem

Should widgets specify fonts as bundles or individual properties?

**Approach A - Individual Properties** (current):
```python
theme_config = {
    "fontFamily": "terminal.fontFamily",
    "fontSize": "terminal.fontSize",
    "fontWeight": "terminal.fontWeight",
    "lineHeight": "terminal.lineHeight",
}
```

**Approach B - Font Bundles**:
```python
theme_config = {
    "font": "terminal",  # Auto-resolves all properties
}
```

### Research: Industry Patterns

#### CSS Approach
```css
/* Individual (longhand) */
font-family: "Consolas";
font-size: 14px;
font-weight: 700;
line-height: 1.5;

/* Bundle (shorthand) */
font: 700 14px/1.5 "Consolas", monospace;
```

**CSS Pattern**: ✅ **Supports BOTH** - shorthand for convenience, longhand for control

#### Qt Approach
```cpp
// Individual
QFont font;
font.setFamily("Consolas");
font.setPointSize(14);
font.setWeight(QFont::Bold);

// Bundle
QFont font("Consolas", 14, QFont::Bold);
```

**Qt Pattern**: ✅ **Supports BOTH** - constructor for convenience, setters for control

#### React/CSS-in-JS Approach
```jsx
// Individual
<div style={{
  fontFamily: "Consolas",
  fontSize: 14,
  fontWeight: 700,
}} />

// Bundle (not standard, but possible)
<div style={{ font: "700 14px/1.5 Consolas" }} />
```

**React Pattern**: ⚠️ **Mostly individual** - bundles are rare in component APIs

### Recommendation: Support Both (Bundle Primary, Individual Optional)

**Decision**: ✅ **Support BOTH approaches**

**Primary Pattern** (90% of use cases):
```python
class TerminalWidget(ThemedWidget):
    theme_config = {
        # Colors
        "background": "terminal.colors.background",
        "foreground": "terminal.colors.foreground",

        # Font bundle (simple!)
        "font": "terminal",  # Resolves terminal.* → fonts.mono → defaults
    }
```

**Advanced Pattern** (10% of use cases):
```python
class CustomWidget(ThemedWidget):
    theme_config = {
        # Mix and match from different categories!
        "fontFamily": "terminal.fontFamily",  # Mono from terminal
        "fontSize": "ui.fontSize",            # Size from UI
        "fontWeight": "heading.fontWeight",   # Weight from heading
    }
```

**Implementation**:
```python
class ThemedWidget:
    def _apply_fonts(self, theme: Theme):
        """Apply font configuration from theme."""

        # Approach 1: Font bundle (simple)
        if "font" in self.theme_config:
            token_prefix = self.theme_config["font"]
            qfont = FontTokenRegistry.get_qfont(token_prefix, theme)
            if qfont:
                self.setFont(qfont)

        # Approach 2: Individual properties (advanced)
        else:
            font = self.font()  # Start with current font

            if "fontFamily" in self.theme_config:
                families = FontTokenRegistry.get_font_family(
                    self.theme_config["fontFamily"], theme
                )
                available = FontTokenRegistry.get_available_font(tuple(families))
                if available:
                    font.setFamily(available)

            if "fontSize" in self.theme_config:
                size = FontTokenRegistry.get_font_size(
                    self.theme_config["fontSize"], theme
                )
                if size:
                    font.setPointSize(size)

            if "fontWeight" in self.theme_config:
                weight = FontTokenRegistry.get_font_weight(
                    self.theme_config["fontWeight"], theme
                )
                if weight:
                    font.setWeight(QFont.Weight(weight))

            self.setFont(font)
```

**FontTokenRegistry.get_qfont()**:
```python
@staticmethod
def get_qfont(token_prefix: str, theme: Theme) -> QFont:
    """Get complete QFont from token prefix.

    Args:
        token_prefix: Base token like "terminal", "tabs", "ui"
        theme: Theme instance

    Returns:
        Configured QFont with all properties resolved

    Example:
        get_qfont("terminal", theme)
        → Resolves terminal.fontFamily, terminal.fontSize, etc.
    """
    # Resolve all properties with hierarchy
    families = FontTokenRegistry.get_font_family(f"{token_prefix}.fontFamily", theme)
    size = FontTokenRegistry.get_font_size(f"{token_prefix}.fontSize", theme)
    weight = FontTokenRegistry.get_font_weight(f"{token_prefix}.fontWeight", theme)

    # Create QFont
    available = FontTokenRegistry.get_available_font(tuple(families))
    family = available or families[-1]  # Use last as fallback

    font = QFont(family, size)
    font.setWeight(QFont.Weight(weight))

    return font
```

**Benefits**:
- ✅ Simple case is simple: `"font": "terminal"`
- ✅ Advanced case is possible: mix properties from different categories
- ✅ Follows industry patterns (CSS, Qt)
- ✅ Backward compatible (can add bundle later without breaking individual)

---

## 3. Error Handling - Custom Exception

### The Problem

How to handle missing fonts, invalid values, etc.?

### Recommendation: Custom Exception Hierarchy + Hard Fail

**Decision**: ✅ **Custom exceptions, hard fail by default**

**Exception Hierarchy**:
```python
# Core font exceptions
class FontError(Exception):
    """Base exception for font-related errors."""
    pass

class FontValidationError(FontError):
    """Theme font configuration is invalid."""
    pass

class FontTokenNotFoundError(FontError):
    """Requested font token doesn't exist in theme."""
    pass

class FontNotAvailableError(FontError):
    """No fonts in fallback chain are available on this system."""
    pass

class FontPropertyError(FontError):
    """Font property has invalid value."""
    pass
```

**Usage in Theme Validation**:
```python
class Theme:
    def __post_init__(self):
        """Validate theme including fonts."""
        # ... existing validation ...

        # Validate fonts
        for key, value in self.fonts.items():
            # Type validation
            if "fontFamily" in key or "Family" in key:
                if not isinstance(value, (str, list)):
                    raise FontPropertyError(
                        f"Font family must be string or list, got {type(value).__name__}: {key}={value}"
                    )
                if isinstance(value, list) and not all(isinstance(f, str) for f in value):
                    raise FontPropertyError(
                        f"Font family list must contain only strings: {key}={value}"
                    )

            elif "fontSize" in key or "Size" in key:
                if not isinstance(value, (int, float)) or value <= 0:
                    raise FontPropertyError(
                        f"Font size must be positive number, got: {key}={value}"
                    )

            elif "fontWeight" in key or "Weight" in key:
                if isinstance(value, int):
                    if not (100 <= value <= 900):
                        raise FontPropertyError(
                            f"Font weight must be 100-900, got: {key}={value}"
                        )
                elif isinstance(value, str):
                    valid_weights = ["thin", "light", "normal", "medium", "semibold", "bold", "black"]
                    if value.lower() not in valid_weights:
                        raise FontPropertyError(
                            f"Font weight must be one of {valid_weights}, got: {key}={value}"
                        )
                else:
                    raise FontPropertyError(
                        f"Font weight must be int or string, got {type(value).__name__}: {key}={value}"
                    )

        # Validate required categories
        if "fonts.mono" not in self.fonts:
            logger.warning("Theme missing 'fonts.mono', will use system default")

        # Validate mono fonts end with "monospace"
        if "fonts.mono" in self.fonts:
            mono_fonts = self.fonts["fonts.mono"]
            if isinstance(mono_fonts, list) and mono_fonts[-1] != "monospace":
                raise FontValidationError(
                    f"fonts.mono must end with 'monospace' fallback, got: {mono_fonts}"
                )
```

**Usage in FontTokenRegistry**:
```python
@staticmethod
def get_font_family(token: str, theme: Theme) -> list[str]:
    """Get font family with hierarchical resolution.

    Raises:
        FontTokenNotFoundError: If token not found and no fallback exists
    """
    chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

    for candidate_token in chain:
        if candidate_token in theme.fonts:
            value = theme.fonts[candidate_token]
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

    # Note: We ALWAYS return something (system defaults)
    # This prevents FontTokenNotFoundError in normal cases

@staticmethod
def get_available_font(families: tuple[str, ...]) -> Optional[str]:
    """Get first available font from fallback chain.

    Returns:
        First available font family, or None if NONE found

    Raises:
        FontNotAvailableError: If no fonts available (developer error)
    """
    db = QFontDatabase()
    available_families = set(db.families())

    for family in families:
        if family in available_families:
            return family
        # Case-insensitive match
        for available in available_families:
            if available.lower() == family.lower():
                return available

    # Generic fallbacks should ALWAYS exist
    if families[-1] in ["monospace", "sans-serif", "serif"]:
        # Qt guarantees these exist, so just return the generic
        return families[-1]

    # This should never happen if themes are validated properly
    raise FontNotAvailableError(
        f"No fonts available from fallback chain: {families}. "
        f"Available fonts: {sorted(available_families)[:10]}..."
    )
```

**Future: Graceful Degradation** (v2.2.0):
```python
class FontTokenRegistry:
    # Class-level error handling mode
    ERROR_MODE = "strict"  # "strict" | "warn" | "silent"

    @staticmethod
    def set_error_mode(mode: str):
        """Set error handling mode.

        Args:
            mode: "strict" (raise), "warn" (log), "silent" (ignore)
        """
        FontTokenRegistry.ERROR_MODE = mode

    @staticmethod
    def get_font_family(token: str, theme: Theme) -> list[str]:
        """Get font family with configurable error handling."""
        try:
            # ... resolution logic ...
            pass
        except FontTokenNotFoundError as e:
            if FontTokenRegistry.ERROR_MODE == "strict":
                raise
            elif FontTokenRegistry.ERROR_MODE == "warn":
                logger.warning(f"Font token not found: {token}, using default")
                return ["Arial", "sans-serif"]
            else:  # silent
                return ["Arial", "sans-serif"]
```

**Benefits**:
- ✅ Clear error messages for theme developers
- ✅ Type safety enforced
- ✅ Future-proof (can add graceful degradation later)
- ✅ Follows Python best practices (custom exception hierarchy)

---

## 4. Font Sizes - Int vs Float? DPI Scaling?

### Research: Qt Font Size Handling

Let me research Qt's approach to font sizes and DPI scaling...

#### Qt Documentation Research

**QFont Size Methods**:
```cpp
// Integer point size
void QFont::setPointSize(int pointSize)
int QFont::pointSize() const

// Float point size (added in Qt 4.8)
void QFont::setPointSizeF(qreal pointSize)
qreal QFont::pointSizeF() const

// Pixel size (absolute, not DPI-aware)
void QFont::setPixelSize(int pixelSize)
int QFont::pixelSize() const
```

**Qt DPI Scaling**:
- Point sizes are **automatically scaled** by Qt based on screen DPI
- 1 point = 1/72 inch (physical measurement)
- On 96 DPI screen: 12pt = 16px
- On 192 DPI screen (HiDPI): 12pt = 32px
- Qt handles this automatically! ✅

**Qt High-DPI Support** (Qt 5.6+):
```python
# Enable automatic HiDPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
```

VFWidgets already uses this in `vfwidgets_common.desktop.configure_desktop()`!

#### Industry Patterns

**VSCode**:
```json
{
  "editor.fontSize": 14,           // Integer, interpreted as pt
  "terminal.integrated.fontSize": 13  // Integer, interpreted as pt
}
```
Uses integers, interprets as points.

**CSS**:
```css
font-size: 14px;   /* Pixels (not DPI-aware) */
font-size: 14pt;   /* Points (DPI-aware, 1pt = 1/72 inch) */
font-size: 1.2em;  /* Relative (multiplier) */
```
Supports both, but web typically uses pixels.

**macOS/iOS**:
```swift
let font = UIFont.systemFont(ofSize: 14.0)  // Float, interpreted as points
```
Uses floats for sub-pixel accuracy.

### Recommendation: Float Point Sizes (DPI-Aware)

**Decision**: ✅ **Use float point sizes (DPI-aware)**

**Rationale**:
1. **DPI-aware**: Point sizes automatically scale with screen DPI ✅
2. **Sub-pixel accuracy**: 13.5pt is valid and useful for fine-tuning
3. **Qt native**: Qt uses `qreal` (float) internally for font sizes
4. **Future-proof**: Allows fractional sizes without breaking change

**Schema**:
```json
{
  "fonts": {
    "fonts.size": 13,        // Int is OK (converted to float)
    "terminal.fontSize": 13.5, // Float is OK (sub-pixel)
    "heading.fontSize": 18.0   // Explicit float
  }
}
```

**Validation**:
```python
def _validate_font_size(key: str, value: Any) -> float:
    """Validate and normalize font size.

    Args:
        key: Font property key (e.g., "terminal.fontSize")
        value: Size value (int or float)

    Returns:
        Normalized float size

    Raises:
        FontPropertyError: If size is invalid
    """
    if not isinstance(value, (int, float)):
        raise FontPropertyError(
            f"Font size must be number, got {type(value).__name__}: {key}={value}"
        )

    if value <= 0:
        raise FontPropertyError(
            f"Font size must be positive, got: {key}={value}"
        )

    if value > 144:  # 2 inches at 72 DPI
        raise FontPropertyError(
            f"Font size too large (max 144pt), got: {key}={value}"
        )

    return float(value)
```

**Implementation**:
```python
@staticmethod
def get_font_size(token: str, theme: Theme) -> float:
    """Get font size in points (DPI-aware).

    Returns:
        Font size as float (e.g., 13.5)
    """
    chain = FontTokenRegistry.HIERARCHY_MAP.get(token, [token])

    for candidate_token in chain:
        if candidate_token in theme.fonts:
            value = theme.fonts[candidate_token]
            if isinstance(value, (int, float)):
                return float(value)  # Always return float

    return 13.0  # Default size

# Apply to QFont
font = QFont()
size = FontTokenRegistry.get_font_size("terminal.fontSize", theme)
font.setPointSizeF(size)  # Use float method! ✅
```

**DPI Scaling Behavior**:
```python
# Theme specifies 14pt
"terminal.fontSize": 14

# Qt automatically scales:
# - 96 DPI screen:  14pt → ~19px
# - 144 DPI screen: 14pt → ~28px
# - 192 DPI screen: 14pt → ~37px (HiDPI/Retina)

# Developer doesn't need to do anything! Qt handles it ✅
```

**Benefits**:
- ✅ Automatic DPI scaling (cross-platform, HiDPI ready)
- ✅ Sub-pixel accuracy for fine typography
- ✅ Accepts both int and float in theme JSON
- ✅ Future-proof (no breaking change for fractional sizes)
- ✅ Follows Qt best practices

---

## 5. Line Height - Documentation Required

### Recommendation: Document Limitations

**Decision**: ✅ **Document which widgets support line height**

**Supported Widgets**:
- ✅ **TerminalWidget**: xterm.js `lineHeight` option
- ✅ **QTextEdit**: Via `QTextBlockFormat.setLineHeight()`
- ✅ **QTextBrowser**: Via `QTextBlockFormat.setLineHeight()`
- ✅ **QLabel** (with rich text): Via CSS in HTML

**NOT Supported Widgets**:
- ❌ **QTabBar**: No line height control
- ❌ **QPushButton**: No line height control
- ❌ **QMenuBar**: No line height control
- ⚠️ **QComboBox**: Limited (internal QListView only)

**Implementation Strategy**:

```python
class ThemedWidget:
    """Base class for themed widgets with font support."""

    # Widget declares supported font properties
    supported_font_properties = ["fontFamily", "fontSize", "fontWeight"]

    def _apply_fonts(self, theme: Theme):
        """Apply font configuration from theme."""
        # ... apply fontFamily, fontSize, fontWeight ...

        # Line height (only if supported)
        if "lineHeight" in self.theme_config:
            if "lineHeight" not in self.supported_font_properties:
                logger.debug(
                    f"{self.__class__.__name__} does not support lineHeight, ignoring"
                )
            else:
                self._apply_line_height(theme)

    def _apply_line_height(self, theme: Theme):
        """Apply line height (override in subclass if supported)."""
        logger.warning(
            f"{self.__class__.__name__} does not implement _apply_line_height()"
        )

class TerminalWidget(ThemedWidget):
    """Terminal with line height support."""

    supported_font_properties = ["fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing"]

    def _apply_line_height(self, theme: Theme):
        """Apply line height to xterm.js."""
        line_height = FontTokenRegistry.get_line_height(
            self.theme_config["lineHeight"], theme
        )
        self._send_to_js("setLineHeight", line_height)

class CustomTextEdit(ThemedWidget, QTextEdit):
    """Text editor with line height support."""

    supported_font_properties = ["fontFamily", "fontSize", "fontWeight", "lineHeight"]

    def _apply_line_height(self, theme: Theme):
        """Apply line height via QTextBlockFormat."""
        line_height = FontTokenRegistry.get_line_height(
            self.theme_config["lineHeight"], theme
        )

        # Apply to all blocks
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(line_height * 100, QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)
```

**Documentation**:

Create `docs/font-support-matrix.md`:
```markdown
# Font Property Support Matrix

| Widget | fontFamily | fontSize | fontWeight | lineHeight | letterSpacing |
|--------|-----------|----------|------------|------------|---------------|
| TerminalWidget | ✅ | ✅ | ✅ | ✅ | ✅ |
| QTextEdit | ✅ | ✅ | ✅ | ✅ | ✅ |
| QLabel (rich text) | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| QTabBar | ✅ | ✅ | ✅ | ❌ | ✅ |
| QPushButton | ✅ | ✅ | ✅ | ❌ | ✅ |
| QMenuBar | ✅ | ✅ | ✅ | ❌ | ✅ |

## Notes

- ✅ Fully supported
- ⚠️ Partially supported (limitations apply)
- ❌ Not supported by Qt

### Line Height Limitations

Line height is a text layout property that Qt only supports for text widgets (QTextEdit, QTextBrowser). UI widgets like buttons and tabs calculate their height based on font metrics and internal padding.

**Workaround**: Adjust widget padding instead:
```python
button.setStyleSheet("QPushButton { padding: 8px 16px; }")  # Increases effective line height
```
```

**Benefits**:
- ✅ Clear expectations for widget developers
- ✅ Graceful degradation (unsupported properties ignored)
- ✅ Future-proof (can add support to more widgets later)
- ✅ Well-documented limitations

---

## 6. Font Cascading - Best Practice

### Research: Cascading Patterns

#### CSS Approach
```css
/* Parent sets font */
.parent {
  font-family: "Arial", sans-serif;
  font-size: 14px;
}

/* Children inherit automatically */
.child {
  /* Inherits Arial, 14px from parent */
}

/* Child can override */
.child-custom {
  font-size: 16px;  /* Overrides, but still inherits Arial */
}
```

**CSS Pattern**: ✅ **Automatic inheritance** (default behavior)

#### Qt Approach
```cpp
// Parent widget sets font
parentWidget->setFont(QFont("Arial", 14));

// Children DO NOT inherit automatically by default!
// Each widget has its own font (system default)

// To cascade: explicitly propagate
for (QWidget *child : parentWidget->findChildren<QWidget*>()) {
    child->setFont(parentWidget->font());
}
```

**Qt Pattern**: ❌ **No automatic inheritance** (by design for flexibility)

#### React/Component Approach
```jsx
// Parent sets font
<div style={{ fontFamily: "Arial", fontSize: 14 }}>
  {/* Children inherit via CSS cascade */}
  <span>Inherits Arial, 14px</span>

  {/* Can override */}
  <span style={{ fontSize: 16 }}>Override size only</span>
</div>
```

**React Pattern**: ✅ **Automatic inheritance via CSS**

### Recommendation: No Automatic Cascading (Explicit Control)

**Decision**: ❌ **Don't auto-cascade fonts to children**

**Rationale**:
1. **Qt's design**: Qt doesn't cascade fonts by default (intentional)
2. **Widget independence**: Each widget knows its own theme needs
3. **Explicit is better**: Theme author controls each widget's font
4. **Avoids conflicts**: Child widget might need different font category

**Pattern**: Each widget declares its own font needs
```python
class ParentWidget(ThemedWidget):
    theme_config = {
        "font": "ui",  # Uses UI fonts
    }

class TerminalChild(ThemedWidget):
    theme_config = {
        "font": "terminal",  # Uses monospace fonts (different from parent!)
    }

# Parent is sans-serif, child is monospace ✅
# No cascading = each widget gets correct font
```

**Alternative**: Explicit Cascading (Opt-In)

If cascading is needed, widget can explicitly propagate:
```python
class CascadingWidget(ThemedWidget):
    """Widget that cascades fonts to children."""

    cascade_fonts = True  # Opt-in flag

    def on_theme_changed(self, theme):
        super().on_theme_changed(theme)

        if self.cascade_fonts:
            # Explicitly propagate to children
            for child in self.findChildren(QWidget):
                if not isinstance(child, ThemedWidget):
                    # Only cascade to non-themed children
                    child.setFont(self.font())
```

**Best Practice Documentation**:
```markdown
# Font Cascading Best Practices

## Default Behavior: No Cascading

Fonts do NOT automatically cascade to child widgets. Each `ThemedWidget` declares its own font requirements via `theme_config`.

### Why No Cascading?

1. **Widget Independence**: A terminal widget needs monospace fonts even if its parent uses sans-serif
2. **Qt Design**: Qt doesn't cascade fonts by default
3. **Explicit Control**: Theme author knows exactly which font each widget uses

### Example: Parent & Child

```python
class TextEditor(ThemedWidget):
    theme_config = {
        "font": "editor",  # Monospace font
    }

class LineNumberBar(ThemedWidget):
    theme_config = {
        "font": "editor",  # Also monospace (explicit)
    }

class StatusBar(ThemedWidget):
    theme_config = {
        "font": "ui",  # Sans-serif font (different!)
    }
```

## When to Use Cascading

Use explicit cascading for:
- Rich text content (QTextEdit with formatted text)
- Dynamically created child widgets
- Non-themed widgets that should inherit parent font

### Opt-In Cascading

```python
class MyContainer(ThemedWidget):
    cascade_fonts = True  # Opt-in
```

## Anti-Patterns

❌ DON'T: Expect fonts to cascade automatically
❌ DON'T: Set font on parent and assume children inherit
✅ DO: Declare font needs for each ThemedWidget
✅ DO: Use explicit cascading only when needed
```

**Benefits**:
- ✅ Follows Qt's design philosophy
- ✅ Each widget has correct font category (mono vs ui vs serif)
- ✅ No unexpected inheritance issues
- ✅ Opt-in cascading available for special cases
- ✅ Clear, documented behavior

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| **1. Token Conflicts** | ❌ No generic `fonts.fontFamily`, only categories | Semantic clarity, type safety, follows VSCode |
| **2. Bundle vs Individual** | ✅ Support BOTH | Simple case simple, advanced case possible |
| **3. Error Handling** | ✅ Custom exceptions, hard fail | Clear errors, future graceful degradation |
| **4. Font Sizes** | ✅ Float point sizes (DPI-aware) | Qt native, sub-pixel accuracy, HiDPI ready |
| **5. Line Height** | ✅ Document limitations | Not all widgets support, clear expectations |
| **6. Font Cascading** | ❌ No auto-cascade | Qt design, explicit control, widget independence |

---

## Next Steps

1. ✅ Review and approve these decisions
2. ✅ Update fonts-DESIGN.md with approved decisions
3. ✅ Create implementation tasks based on decisions
4. ✅ Begin Phase 1 implementation (core infrastructure)

All High Priority questions now have researched recommendations! 🎉
