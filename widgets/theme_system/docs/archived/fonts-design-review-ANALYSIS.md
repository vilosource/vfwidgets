# Font Support Design Review - Soundness Analysis

**Status: 🔍 Design Review Phase**

This document critically examines the font support design to identify potential issues, edge cases, and areas that need clarification before implementation.

---

## Critical Questions to Answer

### 1. Token Hierarchy & Resolution

**Question**: How do we handle conflicting resolution paths?

**Example Conflict**:
```json
{
  "fonts": {
    "fonts.mono": ["JetBrains Mono", "monospace"],
    "terminal.fontFamily": ["Cascadia Code", "monospace"],
    "editor.fontFamily": ["Fira Code", "monospace"],

    // What if someone also sets:
    "fonts.fontFamily": ["Comic Sans", "sans-serif"]  // ❌ Conflicts with fonts.mono!
  }
}
```

**Current Design**:
```python
HIERARCHY_MAP = {
    "terminal.fontFamily": ["terminal.fontFamily", "fonts.mono"],
    "editor.fontFamily": ["editor.fontFamily", "fonts.mono"],
}
```

**Issue**: What if theme has both `fonts.mono` and `fonts.fontFamily`? Which wins?

**Proposed Solution**:
- `fonts.mono`, `fonts.ui`, `fonts.serif` are **category-specific** (higher priority)
- `fonts.fontFamily` would be a **global fallback** (lowest priority)
- Resolution: `terminal.fontFamily → fonts.mono → fonts.fontFamily → system default`

**Decision Needed**: ✅ Should we allow `fonts.fontFamily` or only category-specific ones?

---

### 2. Font Property Bundles vs Individual Properties

**Question**: Should widgets request complete font bundles or individual properties?

**Approach A - Individual Properties** (current design):
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
    "font": "terminal.font",  # Returns complete font specification
}
```

**Trade-offs**:
| Approach | Pros | Cons |
|----------|------|------|
| Individual | Granular control, can mix properties | Verbose, more tokens to manage |
| Bundles | Simple, fewer tokens | Less flexible, all-or-nothing |

**Current Design Choice**: Individual properties for maximum flexibility

**Issue**: Widget needs to know ALL property names (`fontFamily`, `fontSize`, `fontWeight`, etc.)

**Proposed Solution**: Provide BOTH approaches:
```python
# Approach A: Simple bundle (most widgets)
theme_config = {
    "font": "terminal.font",  # Auto-resolves all properties
}

# Approach B: Individual (for fine control)
theme_config = {
    "fontFamily": "terminal.fontFamily",
    "fontSize": "ui.fontSize",  # Mix and match!
}
```

**Decision Needed**: ✅ Support both approaches?

---

### 3. Theme Validation & Errors

**Question**: What happens when font tokens are malformed?

**Error Cases**:

**Case 1: Missing Required Tokens**
```json
{
  "fonts": {
    "terminal.fontSize": 14
    // Missing terminal.fontFamily!
  }
}
```

**Current Behavior**: Falls back to `fonts.mono` then system default
**Question**: Should this be a warning? An error?

**Case 2: Invalid Font Family**
```json
{
  "fonts": {
    "fonts.mono": "not-a-list"  // Should be array!
  }
}
```

**Current Design**: Validation in `Theme.__post_init__()` raises error
**Question**: Should we auto-fix (wrap in list) or fail hard?

**Case 3: Non-Existent Fonts**
```json
{
  "fonts": {
    "fonts.mono": ["TotallyFakeFont", "AlsoFake"]  // None exist on system
  }
}
```

**Current Behavior**: Falls back to generic "monospace"
**Question**: Should we warn theme author during development?

**Proposed Solution Levels**:
1. **Hard Errors**: Type mismatches (string instead of list)
2. **Warnings**: Missing optional tokens
3. **Silent Fallback**: Non-existent fonts (use next in chain)

**Decision Needed**: ✅ What error level for each case?

---

### 4. Font Availability & Platform Differences

**Question**: How do we handle fonts that exist on some platforms but not others?

**Example**:
```json
{
  "fonts": {
    "fonts.mono": ["Cascadia Code", "SF Mono", "Consolas", "monospace"]
  }
}
```

- **Windows**: Has Cascadia Code (if installed), Consolas ✅
- **macOS**: Has SF Mono ✅, no Cascadia Code ❌
- **Linux**: Might have none, falls back to "monospace" ❌

**Current Design**: `get_available_font()` checks `QFontDatabase.families()`

**Issues**:

1. **Font name variations**: "SF Mono" vs "SFMono-Regular" vs "San Francisco Mono"
2. **Case sensitivity**: "Consolas" vs "consolas"
3. **Font styles as families**: "Segoe UI Semibold" vs "Segoe UI" + weight=600

**Current Solution**: Case-insensitive matching

**Additional Issues**:

**Issue A: Font Style in Family Name**
```json
"tabs.fontFamily": ["Segoe UI Semibold", "Ubuntu Bold", "sans-serif"]
```

This is **wrong** - should be:
```json
"tabs.fontFamily": ["Segoe UI", "Ubuntu", "sans-serif"],
"tabs.fontWeight": "semibold"
```

**Question**: Should we detect and warn about this anti-pattern?

**Issue B: Font Installation**
- User creates theme with "JetBrains Mono" on their system
- Another user opens theme but doesn't have JetBrains Mono
- Theme looks different!

**Question**: Should Theme Studio warn "Font X not available on this system"?

**Proposed Solutions**:
1. ✅ Normalize font names (case-insensitive, strip variations)
2. ✅ Validate against Qt's font database during theme editing
3. ✅ Theme Studio shows availability status per platform
4. ⚠️ Document best practices (always include generic fallback)

**Decision Needed**: ✅ How aggressive should font normalization be?

---

### 5. Font Size Units & Scaling

**Question**: What units for font sizes? How to handle DPI scaling?

**Current Design**: Point sizes (integer)
```json
"terminal.fontSize": 14  // 14pt
```

**Issues**:

**Issue A: DPI Scaling**
- 14pt looks different at 96 DPI vs 192 DPI (HiDPI)
- Qt handles this automatically with point sizes ✅
- BUT: Users might expect pixel-perfect sizes

**Issue B: Relative Sizing**
```json
"ui.fontSize": 13,
"heading.fontSize": 18,  // 1.38x bigger
```

**Question**: Should we support relative sizes?
```json
"heading.fontSize": "1.5x"  // 1.5x the base size
"small.fontSize": "-2"      // 2pt smaller than base
```

**Issue C: Fractional Sizes**
```json
"terminal.fontSize": 13.5  // Valid?
```

Qt QFont.setPointSize() takes int, but QFont.setPointSizeF() takes float.

**Current Design**: Accepts int or float, converts to int
**Question**: Should we support fractional sizes with setPointSizeF()?

**Proposed Solution**:
1. ✅ Use point sizes (Qt's default, DPI-aware)
2. ✅ Support both int and float
3. ⚠️ Relative sizing is future enhancement (v2.2.0)
4. ✅ Document that Qt auto-scales for HiDPI

**Decision Needed**: ✅ Float or int for font sizes?

---

### 6. Line Height & Letter Spacing

**Question**: How to apply line height and letter spacing to Qt widgets?

**Current Design**:
```json
"terminal.lineHeight": 1.2,      // Multiplier
"terminal.letterSpacing": 0.5    // Pixels
```

**Issue**: Qt doesn't have built-in line-height for QFont!

**Qt Reality**:
- `QFont` has no `setLineHeight()` method
- Line height is controlled by `QFontMetrics.lineSpacing()`
- For QTextEdit/QTextBrowser: Use `QTextBlockFormat.setLineHeight()`
- For custom widgets: Manual calculation

**Terminal Widget Case**:
- xterm.js has `lineHeight` option ✅
- Passes directly to JavaScript ✅
- Works perfectly!

**Tab Bar Case**:
- QTabBar has no line height control ❌
- Line height is determined by font + internal padding ❌
- Can't apply line height!

**Letter Spacing**:
- `QFont.setLetterSpacing()` exists ✅
- Works for all widgets ✅

**Proposed Solutions**:

**For Line Height**:
1. **Terminal widgets**: Pass to xterm.js ✅
2. **Text widgets** (QTextEdit): Use QTextBlockFormat ✅
3. **UI widgets** (QTabBar, QPushButton): **Ignore** (not supported) ⚠️
4. Document which widgets support line height

**Alternative**: Use CSS stylesheets for line-height?
```python
widget.setStyleSheet(f"QWidget {{ line-height: {line_height}; }}")
```

**Question**: Is CSS line-height reliable across Qt widgets?

**Decision Needed**:
- ✅ Which widgets support line height?
- ✅ Should we warn if widget can't apply line height?
- ✅ Use CSS or native Qt methods?

---

### 7. ThemedWidget Integration

**Question**: How does ThemedWidget automatically apply fonts?

**Current Design Sketch**:
```python
class ThemedWidget:
    theme_config = {
        "fontFamily": "terminal.fontFamily",
        "fontSize": "terminal.fontSize",
    }

    def on_theme_changed(self, theme):
        # Auto-apply fonts
        self._apply_fonts(theme)
```

**Issues**:

**Issue A: Which Widget Gets the Font?**
```python
class MyWidget(ThemedWidget, QWidget):
    # QWidget with children: QLabel, QPushButton, QTextEdit
    # When we call self.setFont(), which widgets get it?
    # Answer: Only self, not children (unless they inherit)
```

**Question**: Should fonts cascade to children automatically?

**Issue B: Font Property Names**
What if widget uses different property names?
```python
# Terminal uses "fontFamily"
theme_config = {"fontFamily": "terminal.fontFamily"}

# But what if another widget uses "font_family"?
theme_config = {"font_family": "terminal.fontFamily"}  # Different key!
```

**Current Design**: Standardize on camelCase
**Question**: Should we support both snake_case and camelCase?

**Issue C: Partial Font Specs**
```python
theme_config = {
    "fontSize": "terminal.fontSize",
    # No fontFamily specified - what happens?
}
```

**Current Behavior**: Only size is applied, family uses widget default
**Question**: Is this intuitive?

**Proposed Solutions**:
1. ✅ Standardize property names: `fontFamily`, `fontSize`, `fontWeight`
2. ✅ Document that fonts don't cascade (by design)
3. ✅ Partial specs are allowed (apply only specified properties)
4. ⚠️ Consider adding `font` bundle property for simplicity

**Decision Needed**: ✅ Should we support font cascading to children?

---

### 8. Terminal Widget Specifics

**Question**: How does TerminalWidget apply fonts to xterm.js?

**Current Design**:
```python
def _apply_theme(self, theme):
    families = FontTokenRegistry.get_font_family("terminal.fontFamily", theme)
    size = FontTokenRegistry.get_font_size("terminal.fontSize", theme)

    # Convert to xterm.js format
    font_family_str = ", ".join(f'"{f}"' for f in families)

    xterm_config = {
        "fontFamily": font_family_str,
        "fontSize": size,
    }
```

**Issues**:

**Issue A: Font Family String Format**
```python
# Qt format: ["JetBrains Mono", "Consolas", "monospace"]
# xterm.js format: '"JetBrains Mono", Consolas, monospace'
```

**Current Code**:
```python
font_family_str = ", ".join(f'"{f}"' for f in families)
# Result: '"JetBrains Mono", "Consolas", "monospace"'
```

**Question**: Should we quote ALL names or only ones with spaces?

**Better Approach**:
```python
def quote_if_needed(name):
    return f'"{name}"' if " " in name else name

font_family_str = ", ".join(quote_if_needed(f) for f in families)
# Result: '"JetBrains Mono", Consolas, monospace' ✅
```

**Issue B: Font Weight Conversion**
```python
# Qt: QFont.Weight enum (100-900)
# xterm.js: "normal", "bold", or 100-900
```

**Question**: Should we convert numeric weights to strings for xterm.js?

**Issue C: Line Height Format**
```python
# Qt: Multiplier (1.2)
# xterm.js: Multiplier (1.2) ✅
# Same format! No conversion needed
```

**Issue D: Letter Spacing Format**
```python
# Qt: QFont.setLetterSpacing(spacing, QFont.AbsoluteSpacing) - pixels
# xterm.js: letterSpacing (pixels) ✅
# Same format! No conversion needed
```

**Proposed Solutions**:
1. ✅ Quote font names only if they contain spaces
2. ✅ Keep numeric weight values (xterm.js accepts both)
3. ✅ Pass line height and letter spacing directly (same units)

**Decision Needed**: ✅ Finalize conversion logic

---

### 9. Performance & Caching

**Question**: Is LRU caching the right approach?

**Current Design**:
```python
@lru_cache(maxsize=256)
def get_font_family(token: str, theme: Theme) -> Optional[list[str]]:
    ...
```

**Issues**:

**Issue A: Cache Key**
```python
# LRU cache uses (token, theme) as key
# BUT: theme is a dataclass with _hash cached
# If theme is modified, hash changes, cache miss!
```

**Question**: Are themes truly immutable? What about theme editing in Theme Studio?

**Issue B: Cache Size**
- 256 entries for font_family
- 256 entries for font_size
- 256 entries for font_weight
- Total: ~768 entries

**Question**: Is this too much? Too little?

**Issue C: Cache Invalidation**
When theme changes, caches should be cleared:
```python
FontTokenRegistry.clear_cache()
```

**Question**: Who calls this? ThemedApplication? Automatically?

**Issue D: Theme Object as Cache Key**
```python
@lru_cache(maxsize=256)
def get_font_family(token: str, theme: Theme):
    # theme is hashed for cache key
    # BUT: If Theme is large (many tokens), hashing is expensive
```

**Alternative**: Use theme ID instead?
```python
@lru_cache(maxsize=256)
def get_font_family(token: str, theme_id: str):
    # Faster hashing, but need to pass theme separately
```

**Proposed Solutions**:
1. ✅ Keep LRU cache (proven pattern from ColorTokenRegistry)
2. ✅ Cache size 256 is reasonable (covers most use cases)
3. ✅ Clear cache on theme change (via ThemeManager)
4. ⚠️ Profile actual performance before optimizing

**Decision Needed**: ✅ Current caching approach is sound

---

### 10. Theme Studio Font Editor UX

**Question**: How should font editing work in Theme Studio?

**Current Design**: `FontPropertyEditor` widget

**UX Questions**:

**Q1: Font Family List Editor**
How to edit fallback chains?
```
[JetBrains Mono] [Fira Code] [Consolas] [monospace]
  ^Remove         ^Reorder     ^Add
```

**Options**:
- A: QListWidget with drag-drop reordering
- B: QLineEdit with comma-separated values
- C: Multiple QComboBox for each fallback level

**Proposed**: Option A (most user-friendly)

**Q2: Font Availability Indicator**
Show which fonts exist on current system?
```
✅ JetBrains Mono (Installed)
❌ Fira Code (Not found)
✅ Consolas (System default)
```

**Q3: Font Preview**
Live preview of selected font?
```
[Font Preview Box]
The quick brown fox jumps over the lazy dog
0123456789 {} [] () <> /\ |
```

**Q4: Category vs Widget Tokens**
Should editor show both?
```
Base Categories:
  fonts.mono: [...]
  fonts.ui: [...]

Widget Overrides:
  terminal.fontFamily: [...]  (overrides fonts.mono)
  tabs.fontFamily: [...]      (inherits fonts.ui)
```

**Or only show widget tokens?**

**Proposed UX**:
1. ✅ List editor with drag-drop
2. ✅ Availability indicators
3. ✅ Live preview
4. ✅ Show both categories and widget tokens (with inheritance arrows)

**Decision Needed**: ✅ Finalize Theme Studio UI design

---

## Edge Cases & Corner Cases

### Edge Case 1: Empty Font Family List
```json
"fonts.mono": []  // Empty array!
```

**Behavior**: Falls back to system default "monospace"
**Question**: Should this be an error?

### Edge Case 2: Circular References
```json
"terminal.fontFamily": "editor.fontFamily",
"editor.fontFamily": "terminal.fontFamily"
```

**Current Design**: No support for token references (only static values)
**Behavior**: This would be a validation error
**Question**: Should we detect this during validation?

### Edge Case 3: Very Large Font Sizes
```json
"heading.fontSize": 999
```

**Behavior**: Qt will render it (badly)
**Question**: Should we enforce max size (e.g., 72pt)?

### Edge Case 4: Negative Values
```json
"terminal.fontSize": -5,
"terminal.letterSpacing": -10
```

**Behavior**:
- Negative size: Validation error ✅
- Negative letter spacing: Valid (tighter spacing) ✅

**Question**: Are negative values ever valid?

### Edge Case 5: Mixed Units
```json
"terminal.fontSize": "14pt",  // String with unit?
```

**Current Design**: Expects number, not string
**Behavior**: Validation error
**Question**: Should we support string parsing?

---

## Security Considerations

### Issue: Font Injection

**Question**: Can malicious themes exploit font loading?

**Scenario**:
```json
"fonts.mono": ["../../../etc/passwd", "monospace"]
```

**Current Design**: Qt's QFontDatabase only loads system fonts
**Safety**: Qt handles font loading safely ✅

**No injection risk** - fonts are loaded from system font directories only.

---

## Compatibility & Migration

### Question: What happens to old themes without font tokens?

**Old Theme**:
```json
{
  "name": "Dark",
  "colors": {...},
  // No "fonts" section
}
```

**Current Design**: Falls back to system defaults
**Behavior**: Theme still works, uses default fonts ✅

**Question**: Should we auto-generate font tokens for old themes?

**Proposed Migration**:
```python
def migrate_theme(old_theme):
    if "fonts" not in old_theme:
        old_theme["fonts"] = {
            "fonts.mono": ["Consolas", "Monaco", "monospace"],
            "fonts.ui": ["Segoe UI", "Ubuntu", "sans-serif"],
            "fonts.size": 13,
        }
    return old_theme
```

**Decision Needed**: ✅ Auto-migration or leave as-is?

---

## Open Questions Summary

Priority questions that need answers before implementation:

### High Priority (Blockers)
1. ✅ Should we support `fonts.fontFamily` as global fallback?
2. ✅ Support both font bundles AND individual properties?
3. ✅ Error levels: hard errors vs warnings vs silent fallback?
4. ✅ Float or int for font sizes?
5. ✅ Which widgets support line height? Document limitations?
6. ✅ Font cascading to children - yes or no?

### Medium Priority (Important)
7. ✅ Font name normalization - how aggressive?
8. ✅ Quote all font names or only ones with spaces?
9. ✅ Max font size limit?
10. ✅ Auto-migration for old themes?

### Low Priority (Nice to Have)
11. ⚠️ Theme Studio shows font availability per platform?
12. ⚠️ Detect font style in family name anti-pattern?
13. ⚠️ Support relative font sizes ("1.5x", "-2")?

---

## Recommendations

### Before Implementation Starts:

1. **Answer all High Priority questions** - These are blockers
2. **Create a minimal prototype** - Test core assumptions
3. **Validate with real fonts** - Test on Windows/Linux/macOS
4. **Review with team** - Get feedback on design decisions

### During Implementation:

1. **Start with Phase 1** - Core infrastructure only
2. **Write tests first** - TDD approach
3. **Test on multiple platforms** - Don't assume fonts exist
4. **Document limitations** - Line height not supported on all widgets

### After Implementation:

1. **Performance testing** - Verify cache performance
2. **User testing** - Theme Studio UX validation
3. **Documentation** - Complete API docs and examples
4. **Migration guide** - Help users update themes

---

## Conclusion

The overall design is **sound** but has several areas needing clarification:

**Strengths**: ✅
- Hierarchical resolution (proven pattern from colors)
- Category guarantees (mono/ui/serif)
- Platform-aware font availability
- LRU caching for performance
- Comprehensive testing strategy

**Concerns**: ⚠️
- Line height not supported on all Qt widgets
- Font cascading behavior needs clarification
- Theme Studio UX needs detailed design
- Platform differences need careful handling

**Blockers**: 🚫
- None! All issues are resolvable with design decisions

**Recommendation**: ✅ **Proceed with implementation** after answering High Priority questions.
