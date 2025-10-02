# VFWidgets Theme System - API Consolidation Plan

**Date:** 2025-10-01
**Status:** APPROVED
**Replaces:** api-refactoring-PLAN.md (outdated)
**Goal:** Align all documentation and examples with progressive disclosure strategy

---

## 🎯 Strategy: Progressive Disclosure

**See:** [API-STRATEGY.md](API-STRATEGY.md) for complete philosophy.

**Core Insight:** We don't have "two competing APIs" - we have a **progressive learning path**.

```
Simple API (Training Wheels)        Advanced API (Full Bicycle)
├─ ThemedMainWindow                 ├─ ThemedWidget mixin
├─ ThemedDialog              →      ├─ Works with ANY Qt base
└─ ThemedQWidget                    └─ Maximum flexibility
```

**Goal:** Make documentation and examples clearly show this progression.

---

## 📊 Current State Analysis

### Documentation Status

| Document | Current State | Needs Update |
|----------|---------------|--------------|
| `quick-start-GUIDE.md` | Shows ThemedQWidget, but also ThemedWidget | ✅ Yes - Show ONLY simple API |
| `api-REFERENCE.md` | Flat organization, no Simple/Advanced split | ✅ Yes - Reorganize by skill level |
| `theme-customization-GUIDE.md` | Good, but missing new features | ✅ Yes - Add Tokens, ThemeProperty |
| `widget-development-GUIDE.md` | **Doesn't exist** | ✅ Yes - Create for Stage 3 users |
| `API-STRATEGY.md` | **Just created** | ✅ No - Already complete |

### Examples Status

| Example Set | Current API | Target State |
|-------------|-------------|--------------|
| `01-06_*.py` (top-level) | 83% new API, 1 mixed | ✅ Needs cleanup - 100% simple API |
| `basic/` | 83% old API | ✅ Needs migration - Introduce ThemedWidget here |
| `user_examples/` | 50/50 mix | ✅ Needs reorganization |
| `tutorials/` | 100% old API | ✅ Needs complete overhaul |
| `layouts/` | 100% old API | ✅ Needs migration |

**From:** [examples-api-audit-REPORT.md](examples-api-audit-REPORT.md)

---

## 🎯 Goals (NOT Breaking Changes)

### What We're Doing

1. **Clarify** the progressive learning path in documentation
2. **Reorganize** examples to show natural progression
3. **Add** developer experience improvements (Tokens, ThemeProperty, WidgetRole)
4. **Communicate** when to use simple API vs advanced API

### What We're NOT Doing

- ❌ Deprecating ThemedWidget (it's the advanced API!)
- ❌ Removing any functionality
- ❌ Breaking existing code
- ❌ Forcing migration

**All changes are backward compatible additions and documentation improvements.**

---

## 📋 Implementation Plan (3 Weeks)

### Week 1: Documentation Alignment

#### Day 1-2: Update quick-start-GUIDE.md

**Current state:** Shows both ThemedQWidget and basic usage

**Target state:** Show ONLY simple API
- Only ThemedMainWindow, ThemedDialog, ThemedQWidget
- Zero mention of ThemedWidget
- Add "Next Steps" section linking to widget-development-GUIDE.md

**Changes:**
```markdown
# Quick Start (30 seconds)

from vfwidgets_theme import ThemedApplication, ThemedMainWindow

class MyApp(ThemedMainWindow):  # ✅ One base class - simple!
    pass

## Next Steps

- [Creating Custom Widgets →](widget-development-GUIDE.md) - When you need QTextEdit, QFrame, etc.
```

---

#### Day 3-4: Create widget-development-GUIDE.md (NEW)

**Audience:** Developers who need custom widgets beyond plain QWidget

**Structure:**
```markdown
# Widget Development Guide

## When You Need This Guide

You've been using ThemedQWidget successfully. Now you need:
- A QTextEdit subclass for code editing
- A QFrame subclass for custom panels
- A QPushButton subclass with special behavior

ThemedQWidget won't work - you need ThemedWidget.

## The Pattern

class MyCustomWidget(ThemedWidget, QtBaseClass):
    """ThemedWidget MUST come first."""

## Why This Works

ThemedQWidget is actually just:
    class ThemedQWidget(ThemedWidget, QWidget):
        pass

Now you understand the full pattern!

## Examples

### Custom Text Editor
class CodeEditor(ThemedWidget, QTextEdit):
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground'
    }

### Custom Button
class IconButton(ThemedWidget, QPushButton):
    pass
```

---

#### Day 5-6: Reorganize api-REFERENCE.md

**Current:** Flat list of all classes

**Target:** Organized by skill level

**Structure:**
```markdown
# API Reference

## Simple API (Start Here)

**For building themed applications quickly.**

### ThemedApplication
[Documentation...]

### ThemedMainWindow
**When to use:** Building a main application window
[Code example...]

### ThemedDialog
**When to use:** Building dialog windows
[Code example...]

### ThemedQWidget
**When to use:** Building simple container widgets
[Code example...]

---

## Advanced API (Custom Widgets)

**For building custom widget classes.**

### ThemedWidget
**When to use:** Need to inherit from QTextEdit, QFrame, QPushButton, or any non-QWidget base

**Pattern:**
```python
class MyWidget(ThemedWidget, QtBaseClass):
    pass
```

**IMPORTANT:** ThemedWidget must come FIRST in inheritance list.

[Detailed documentation...]

---

## Developer Experience Features

### Tokens (NEW - v2.0.0-rc3)
**Token constants for IDE autocomplete**

### ThemeProperty (NEW - v2.0.0-rc3)
**Property descriptors for clean theme access**

### WidgetRole (NEW - v2.0.0-rc3)
**Type-safe widget roles**
```

---

### Week 2: Examples Reorganization

#### Day 7-8: Restructure examples/ directory

**Current structure:**
```
examples/
  01_hello_world.py
  02_buttons_and_layout.py
  ...
  basic/
  user_examples/
  tutorials/
  layouts/
```

**Target structure:**
```
examples/
  README.md                    # Explains progression

  # Stage 1: Simple Apps (ThemedMainWindow/Dialog/QWidget only)
  01_hello_world.py           # Simplest possible
  02_buttons_and_layout.py    # Standard Qt widgets
  03_theme_switching.py       # Switching themes
  04_input_forms.py           # Forms and dialogs

  # Stage 2-3: Custom Widgets (Introduces ThemedWidget)
  05_custom_text_editor.py    # First ThemedWidget usage (QTextEdit)
  06_role_markers.py          # Using roles

  # Advanced examples
  advanced/
    custom_tab_widget.py      # Complex inheritance
    theme_builder.py          # Creating themes
    multi_window.py           # Multiple windows

  # Deprecated (moved for reference)
  legacy/
    (old mixed-API examples)
```

**Migration:**
1. Update 01-04 to use ONLY simple API
2. Rewrite 05 to be the "bridge" example (introduces ThemedWidget)
3. Move complex examples to advanced/
4. Archive old examples to legacy/

---

#### Day 9-10: Update examples to show progression

**Example 01-04: Simple API Only**
```python
# 01_hello_world.py
from vfwidgets_theme import ThemedMainWindow

class HelloApp(ThemedMainWindow):
    """Stage 1: Dead simple - one base class."""
    pass
```

**Example 05: Bridge to Advanced**
```python
# 05_custom_text_editor.py
"""
This example introduces ThemedWidget for the first time.

WHY: We need a QTextEdit subclass, and ThemedQWidget only works with QWidget.

PATTERN: class MyWidget(ThemedWidget, QtBaseClass)
"""

from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """Now you're using the advanced API!

    ThemedWidget works with ANY Qt base class.
    ThemedQWidget was just ThemedWidget + QWidget pre-combined.
    """
    theme_config = {
        'bg': 'editor.background',
        'fg': 'editor.foreground'
    }
```

**Example 06+: Advanced Features**
```python
# Show Tokens, ThemeProperty, WidgetRole
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import ThemeProperty

class ProfessionalWidget(ThemedWidget, QFrame):
    """Stage 4: Master level - using all features."""

    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)
    fg = ThemeProperty(Tokens.WINDOW_FOREGROUND)
```

---

#### Day 11-12: Add examples/README.md

```markdown
# VFWidgets Theme System - Examples

## Learning Path

This directory is organized to teach progressive complexity:

### Stage 1: Simple Apps (Examples 01-04)
**You are here** if you're building a basic themed application.

- `01_hello_world.py` - Simplest possible themed app
- `02_buttons_and_layout.py` - Using standard Qt widgets
- `03_theme_switching.py` - Switching between themes
- `04_input_forms.py` - Forms and dialogs

**API Used:** `ThemedMainWindow`, `ThemedDialog`, `ThemedQWidget`

### Stage 2: Custom Widgets (Example 05+)
**Go here** when you need widgets beyond QWidget (like QTextEdit, QFrame).

- `05_custom_text_editor.py` - **Start here!** Introduces ThemedWidget pattern
- `06_role_markers.py` - Using widget roles

**API Used:** `ThemedWidget` (the full mixin)

### Stage 3: Advanced (advanced/ directory)
**Go here** for complex applications and widget libraries.

**API Used:** Full API with Tokens, ThemeProperty, WidgetRole

## Quick Decision Tree

Q: Building a main window?
→ Use `ThemedMainWindow` (Example 01)

Q: Building a dialog?
→ Use `ThemedDialog` (Example 04)

Q: Building a simple container?
→ Use `ThemedQWidget` (Example 02)

Q: Need QTextEdit/QFrame/QPushButton/etc?
→ Use `ThemedWidget` (Example 05) ⭐ Bridge example

Q: Building a widget library?
→ See `advanced/` directory
```

---

### Week 3: Developer Experience Improvements

#### Day 13-14: Implement Tokens constants

**File:** `src/vfwidgets_theme/core/token_constants.py` (NEW)

```python
"""Token constants for IDE autocomplete.

Usage:
    from vfwidgets_theme import Tokens

    theme_config = {
        'bg': Tokens.WINDOW_BACKGROUND,  # IDE autocomplete!
        'fg': Tokens.WINDOW_FOREGROUND
    }
"""

class Tokens:
    """All 179 theme tokens as constants."""

    # Base Colors (11 tokens)
    COLORS_FOREGROUND = 'colors.foreground'
    COLORS_BACKGROUND = 'colors.background'
    COLORS_PRIMARY = 'colors.primary'
    # ... (generate from ColorTokenRegistry)

    # Window (8 tokens)
    WINDOW_BACKGROUND = 'window.background'
    WINDOW_FOREGROUND = 'window.foreground'
    # ...

    # Buttons (12 tokens)
    BUTTON_BACKGROUND = 'button.background'
    BUTTON_HOVER_BACKGROUND = 'button.hoverBackground'
    # ...

    # Editor (45 tokens)
    EDITOR_BACKGROUND = 'editor.background'
    # ...
```

**Test:**
```python
def test_tokens_match_registry():
    """Verify Tokens class has all registry tokens."""
    from vfwidgets_theme.core.tokens import ColorTokenRegistry

    registry_tokens = set(ColorTokenRegistry.get_all_token_names())
    constant_tokens = set(Tokens.all_tokens())

    assert registry_tokens == constant_tokens
```

**Export:**
```python
# src/vfwidgets_theme/__init__.py
from .core.token_constants import Tokens

__all__ = [
    # ... existing ...
    "Tokens",
]
```

---

#### Day 15: Implement ThemeProperty descriptors

**File:** `src/vfwidgets_theme/widgets/properties.py` (NEW)

```python
"""Property descriptors for clean theme access."""

class ThemeProperty:
    """Descriptor for type-safe theme properties.

    Usage:
        from vfwidgets_theme.widgets.properties import ThemeProperty

        class MyWidget(ThemedWidget, QWidget):
            bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)

            def paintEvent(self, event):
                # Clean access - no getattr!
                painter.fillRect(self.rect(), QColor(self.bg))
    """

    def __init__(self, token: str, default: Optional[str] = None):
        self.token = token
        self.default = default

    def __set_name__(self, owner, name):
        self._attr_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        # Get from theme with fallback
        return getattr(obj.theme, self._attr_name, self.default)

    def __set__(self, obj, value):
        raise AttributeError("Theme properties are read-only")
```

**Export:**
```python
from .widgets.properties import ThemeProperty

__all__ = [
    # ... existing ...
    "ThemeProperty",
]
```

---

#### Day 16: Implement WidgetRole enum

**File:** `src/vfwidgets_theme/widgets/roles.py` (NEW)

```python
"""Type-safe widget roles."""

from enum import Enum

class WidgetRole(Enum):
    """Semantic widget roles for styling."""

    DANGER = "danger"
    SUCCESS = "success"
    WARNING = "warning"
    SECONDARY = "secondary"
    EDITOR = "editor"
    PRIMARY = "primary"
    INFO = "info"

def set_widget_role(widget, role: WidgetRole):
    """Set widget role (type-safe wrapper)."""
    widget.setProperty("role", role.value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
```

**Export:**
```python
from .widgets.roles import WidgetRole, set_widget_role

__all__ = [
    # ... existing ...
    "WidgetRole",
    "set_widget_role",
]
```

---

#### Day 17: Add inheritance order validation

**File:** `src/vfwidgets_theme/widgets/base.py` (MODIFY)

Add to `ThemedWidget.__init__`:

```python
def __init__(self, *args, **kwargs):
    self._validate_inheritance_order()
    # ... existing init ...

def _validate_inheritance_order(self):
    """Validate ThemedWidget comes before Qt base classes."""
    bases = self.__class__.__mro__

    themed_idx = next(
        (i for i, c in enumerate(bases) if c.__name__ == 'ThemedWidget'),
        None
    )

    qt_idx = next(
        (i for i, c in enumerate(bases)
         if c.__name__.startswith('Q') and
            c.__module__.startswith('PySide6')),
        None
    )

    if themed_idx is not None and qt_idx is not None:
        if themed_idx > qt_idx:
            qt_class = bases[qt_idx].__name__
            raise TypeError(
                f"{self.__class__.__name__}: ThemedWidget must come BEFORE {qt_class}.\n"
                f"  ❌ Wrong: class {self.__class__.__name__}({qt_class}, ThemedWidget)\n"
                f"  ✅ Right: class {self.__class__.__name__}(ThemedWidget, {qt_class})\n"
                f"\n"
                f"📖 See: docs/widget-development-GUIDE.md"
            )
```

---

#### Day 18: Update theme-customization-GUIDE.md

Add sections for:
1. Using Tokens constants instead of strings
2. Using ThemeProperty descriptors
3. Using WidgetRole enum

```markdown
## Using Token Constants (Recommended)

Instead of magic strings, use Tokens constants:

```python
# Before
theme_config = {'bg': 'window.background'}  # What tokens exist?

# After
from vfwidgets_theme import Tokens

theme_config = {'bg': Tokens.WINDOW_BACKGROUND}  # IDE autocomplete!
```

## Clean Property Access

Use ThemeProperty descriptors for cleaner code:

```python
from vfwidgets_theme.widgets.properties import ThemeProperty

class MyWidget(ThemedWidget, QWidget):
    bg = ThemeProperty(Tokens.WINDOW_BACKGROUND)

    def paintEvent(self, event):
        # No getattr needed!
        painter.fillRect(self.rect(), QColor(self.bg))
```
```

---

### Week 3: Testing & Validation

#### Day 19: Test all examples

```bash
cd examples
./run_tests.sh

# All examples should:
# - Run without errors
# - Show consistent API usage
# - Follow progression (simple → advanced)
```

---

#### Day 20: Documentation review

**Checklist:**
- [ ] quick-start-GUIDE.md shows ONLY simple API
- [ ] widget-development-GUIDE.md explains ThemedWidget clearly
- [ ] api-REFERENCE.md organized by skill level
- [ ] theme-customization-GUIDE.md shows new features
- [ ] API-STRATEGY.md clearly communicates philosophy
- [ ] ROADMAP.md includes API philosophy section
- [ ] All docs cross-link appropriately

---

#### Day 21: Final polish

1. Update CHANGELOG.md
2. Version bump: 2.0.0-rc2 → 2.0.0-rc3
3. Run full test suite
4. Verify all cross-links work

---

## 🎯 Success Criteria

### Documentation
- [ ] No confusion about "which API to use"
- [ ] Clear progression from simple → advanced
- [ ] ThemedWidget positioned as "advanced, powerful"
- [ ] ThemedQWidget positioned as "simple, common"
- [ ] Decision tree helps users choose

### Examples
- [ ] Examples 01-04: Only simple API
- [ ] Example 05: Bridge to ThemedWidget (clearly explained)
- [ ] Example 06+: Advanced features
- [ ] All examples run successfully
- [ ] Progressive complexity obvious

### Code
- [ ] Tokens class with all 179 tokens
- [ ] ThemeProperty descriptor working
- [ ] WidgetRole enum with helpers
- [ ] Inheritance order validation
- [ ] All tests passing

### Communication
- [ ] API-STRATEGY.md clearly explains progressive disclosure
- [ ] ROADMAP.md includes API philosophy
- [ ] No mention of "competing APIs" or "migration"
- [ ] Positioned as "learning path"

---

## 📊 Measuring Success

### Quantitative
- [ ] 0 examples showing "choose between these two ways"
- [ ] 100% of examples follow progression
- [ ] 4 docs for 4 skill levels (quick start, widget dev, API ref, customization)

### Qualitative
- [ ] Beginner can build app in < 5 minutes
- [ ] Natural "aha moment" when discovering ThemedWidget
- [ ] No questions like "when do I use ThemedWidget vs ThemedQWidget?"
- [ ] Users understand it's a learning path, not competing APIs

---

## 🚫 What We're NOT Doing

This is critical to remember:

- ❌ NOT deprecating ThemedWidget
- ❌ NOT removing any functionality
- ❌ NOT breaking backward compatibility
- ❌ NOT forcing code migration
- ❌ NOT creating "new vs old" narrative

**We're just organizing and clarifying what already exists.**

---

## 📝 Timeline Summary

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Documentation | 4 updated/new docs showing progression |
| 2 | Examples | Reorganized examples with clear stages |
| 3 | Code + Polish | Tokens, ThemeProperty, WidgetRole + validation |

**Total:** 3 weeks, all backward compatible

---

## 🔗 Related Documents

- **API-STRATEGY.md** - Complete philosophy and rationale
- **ROADMAP.md** - Now includes API philosophy section
- **examples-api-audit-REPORT.md** - Evidence of current state
- **api-critical-analysis-HONEST.md** - What we learned (ThemedWidget is powerful, not obsolete)

---

## ✅ Approval Status

- [x] Strategy approved: Progressive disclosure
- [x] No breaking changes: All backward compatible
- [x] Timeline approved: 3 weeks
- [x] Goals clear: Clarify, don't migrate

**Ready to execute.**
