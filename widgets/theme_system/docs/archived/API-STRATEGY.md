# VFWidgets Theme System - API Strategy

**Date:** 2025-10-01
**Version:** 2.0.0-rc3
**Status:** Approved

---

## 🎯 Core Philosophy

**"Make theming trivially easy for app developers, while preserving power for widget library authors."**

### Design Principle: Progressive Disclosure

Users should start simple and naturally graduate to advanced features only when needed.

```
Level 1: App Developer (90% of users)
   ↓ Builds simple apps with standard Qt widgets
   ↓ Uses: ThemedMainWindow, ThemedDialog, ThemedQWidget
   ↓
Level 2: Custom Widget Developer (needs custom widgets)
   ↓ Needs widgets beyond plain QWidget
   ↓ Discovers: ThemedWidget mixin pattern
   ↓
Level 3: Widget Library Author (advanced)
   ↓ Building reusable widget libraries
   ↓ Masters: ThemedWidget with any Qt base class
```

---

## 📊 User Personas

### Persona 1: App Developer (Primary, 90%)

**Goals:**
- Build themed applications quickly
- Use standard Qt widgets (QPushButton, QLabel, QLineEdit, etc.)
- Don't want to think deeply about theming internals

**Needs:**
- Simple API
- Automatic theming
- Minimal boilerplate

**Journey:**
```python
# Day 1: First app
class MyApp(ThemedMainWindow):  # ✅ Simple!
    def __init__(self):
        super().__init__()
        # Add standard Qt widgets - they just work!
```

**API Used:** `ThemedMainWindow`, `ThemedDialog`, `ThemedQWidget`

---

### Persona 2: Custom Widget Developer (Secondary, 9%)

**Goals:**
- Build custom widgets for their specific app needs
- Create widgets that inherit from QTextEdit, QFrame, etc.
- Make custom widgets follow the theme

**Needs:**
- Flexibility to use any Qt base class
- Clear pattern to follow
- Understanding of inheritance order

**Journey:**
```python
# Week 1: Simple container widget
class StatusBar(ThemedQWidget):  # Still simple
    pass

# Week 4: Need QTextEdit functionality
class CodeEditor(ThemedWidget, QTextEdit):  # Learned the pattern
    """Now I understand the mixin approach."""
    pass
```

**API Used:** `ThemedQWidget` → `ThemedWidget + Any Qt Class`

---

### Persona 3: Widget Library Author (Advanced, 1%)

**Goals:**
- Build reusable widget libraries
- Support theming in all widgets
- Maximum flexibility and control

**Needs:**
- Full understanding of theme system internals
- Access to all features
- Ability to customize everything

**Journey:**
```python
# Building a widget library
class ChromeTab(ThemedWidget, QFrame):
    """Professional widget with full theme support."""

    # Using advanced features
    bg = ThemeProperty(Tokens.TAB_BACKGROUND)
    fg = ThemeProperty(Tokens.TAB_FOREGROUND)

    def before_theme_change(self, old, new):
        # Advanced lifecycle hooks
        return True
```

**API Used:** Full `ThemedWidget` API + all advanced features

---

## 🏗️ API Architecture

### Two-Tier System

```
┌─────────────────────────────────────────────────────┐
│  Simple API (For App Developers)                   │
├─────────────────────────────────────────────────────┤
│  ThemedMainWindow  - For main application windows   │
│  ThemedDialog      - For dialog windows             │
│  ThemedQWidget     - For simple container widgets   │
└─────────────────────────────────────────────────────┘
                        ↓
                When you need more...
                        ↓
┌─────────────────────────────────────────────────────┐
│  Advanced API (For Custom Widgets)                  │
├─────────────────────────────────────────────────────┤
│  ThemedWidget      - Mixin for ANY Qt base class    │
│  + Tokens          - Token constants                │
│  + ThemeProperty   - Property descriptors           │
│  + WidgetRole      - Type-safe roles                │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Progressive Learning Path

### Stage 1: "Just Make It Work" (Day 1)

**What they learn:**
- How to create a themed application
- How to use ThemedMainWindow/ThemedDialog
- Themes just work automatically

**API Surface:**
```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow

class MyApp(ThemedMainWindow):
    pass
```

**Complexity:** Minimal - 2 imports, 1 base class

---

### Stage 2: "I Need Simple Custom Widgets" (Week 2-4)

**What they learn:**
- How to create custom container widgets
- ThemedQWidget for plain QWidget subclasses
- Basic theme_config usage

**API Surface:**
```python
from vfwidgets_theme import ThemedQWidget

class StatusPanel(ThemedQWidget):
    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground'
    }
```

**Complexity:** Low - Still single inheritance

---

### Stage 3: "I Need Non-QWidget Base Classes" (Week 4-8)

**What they learn:**
- ThemedWidget mixin pattern
- Multiple inheritance basics
- Inheritance order rules (ThemedWidget first)

**API Surface:**
```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """ThemedWidget must come FIRST."""
    pass
```

**Complexity:** Medium - Multiple inheritance

**Critical insight:** "Oh! ThemedQWidget was just `ThemedWidget + QWidget` all along!"

---

### Stage 4: "I'm Building Reusable Widgets" (Month 2+)

**What they learn:**
- Tokens constants for discoverability
- ThemeProperty descriptors for clean code
- WidgetRole enum for type safety
- Lifecycle hooks

**API Surface:**
```python
from vfwidgets_theme import ThemedWidget, Tokens, WidgetRole
from vfwidgets_theme.widgets.properties import ThemeProperty

class ProfessionalButton(ThemedWidget, QPushButton):
    # Clean property access
    bg = ThemeProperty(Tokens.BUTTON_BACKGROUND)
    fg = ThemeProperty(Tokens.BUTTON_FOREGROUND)

    def __init__(self):
        super().__init__()
        set_widget_role(self, WidgetRole.PRIMARY)
```

**Complexity:** Advanced - Full API mastery

---

## 📖 Documentation Strategy

### Quick Start Guide (quick-start-GUIDE.md)

**Audience:** Persona 1 (App Developers)

**Shows:**
- Only ThemedMainWindow/ThemedDialog/ThemedQWidget
- 30-second "Hello World"
- How to switch themes

**Does NOT show:**
- ThemedWidget mixin
- Multiple inheritance
- Advanced features

**Links to:** "Next Steps: Creating Custom Widgets →"

---

### Widget Development Guide (widget-development-GUIDE.md)

**Audience:** Persona 2 (Custom Widget Developers)

**Shows:**
- When you need ThemedWidget
- Inheritance order rules
- Common patterns (QTextEdit, QFrame, QPushButton subclasses)
- Runtime validation errors explained

**Progressive transition:**
```
"You've been using ThemedQWidget successfully. Now you need
a QTextEdit subclass. Here's how to use ThemedWidget..."
```

---

### API Reference (api-REFERENCE.md)

**Structure:**
```markdown
# Simple API (Start Here)
- ThemedApplication
- ThemedMainWindow
- ThemedDialog
- ThemedQWidget

# Advanced API (Custom Widgets)
- ThemedWidget
- Tokens
- ThemeProperty
- WidgetRole

# Widget Library Authors
- Advanced lifecycle hooks
- Custom theme applicators
- Theme inheritance
```

---

### Theme Customization Guide (theme-customization-GUIDE.md)

**Audience:** All levels

**Shows:**
- Creating themes (all levels)
- Using Tokens constants (Stage 3+)
- ThemeProperty descriptors (Stage 4)
- Role markers (Stage 2+)

---

## 🚦 Decision Tree: Which API to Use?

```
Are you building a main application window?
  YES → Use ThemedMainWindow
  NO  ↓

Are you building a dialog?
  YES → Use ThemedDialog
  NO  ↓

Are you building a simple container widget (QWidget)?
  YES → Use ThemedQWidget
  NO  ↓

Are you building a custom widget with different base (QTextEdit, QFrame, etc.)?
  YES → Use ThemedWidget mixin
        Pattern: class MyWidget(ThemedWidget, QtBaseClass)
        IMPORTANT: ThemedWidget must come FIRST
```

---

## 🔧 Implementation Details

### What Is Each Class?

```python
# Convenience classes (pre-combined for simplicity)
class ThemedMainWindow(ThemedWidget, QMainWindow):
    """ThemedWidget + QMainWindow in one."""
    pass

class ThemedDialog(ThemedWidget, QDialog):
    """ThemedWidget + QDialog in one."""
    pass

class ThemedQWidget(ThemedWidget, QWidget):
    """ThemedWidget + QWidget in one."""
    pass

# The actual mixin (what everything is built on)
class ThemedWidget(metaclass=ThemedWidgetMeta):
    """The powerful mixin that works with ANY Qt base class."""
    pass
```

**Key insight:** The convenience classes are just shortcuts. ThemedWidget is the real API underneath.

---

## 🎯 Example Progression

### Example 01: Hello World (Stage 1)
```python
from vfwidgets_theme import ThemedMainWindow

class HelloApp(ThemedMainWindow):
    """Dead simple."""
    pass
```

**Teaches:** Basic application structure

---

### Example 02: Buttons and Layout (Stage 1)
```python
from vfwidgets_theme import ThemedMainWindow

class ButtonDemo(ThemedMainWindow):
    """Using standard Qt widgets."""
    def __init__(self):
        super().__init__()
        # QPushButton, QLabel, etc. - all themed automatically
```

**Teaches:** Standard widgets work automatically

---

### Example 03: Custom Container (Stage 2)
```python
from vfwidgets_theme import ThemedQWidget

class StatusPanel(ThemedQWidget):
    """First custom widget - still simple."""
    pass
```

**Teaches:** ThemedQWidget for simple customs

---

### Example 04: Text Editor Widget (Stage 3)
```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QTextEdit

class CodeEditor(ThemedWidget, QTextEdit):
    """Now we need ThemedWidget mixin."""
    pass
```

**Teaches:** ThemedWidget for non-QWidget bases
**Critical learning moment:** Understanding the pattern

---

### Example 05: Professional Widget (Stage 4)
```python
from vfwidgets_theme import ThemedWidget, Tokens
from vfwidgets_theme.widgets.properties import ThemeProperty

class ChromeTab(ThemedWidget, QFrame):
    """Professional widget with all features."""

    bg = ThemeProperty(Tokens.TAB_BACKGROUND)
    fg = ThemeProperty(Tokens.TAB_FOREGROUND)
```

**Teaches:** Advanced features, clean code

---

## 📋 Communication Strategy

### In Documentation

**✅ DO:**
- Show ThemedMainWindow/ThemedDialog/ThemedQWidget first
- Explain "when you need more flexibility"
- Natural progression from simple to advanced
- Clear decision tree

**❌ DON'T:**
- Show both APIs as "equivalent options"
- Confuse beginners with multiple inheritance upfront
- Present ThemedWidget in Quick Start

---

### In Examples

**✅ DO:**
- Order examples from simple → advanced
- Add comments explaining API choices
- Show natural progression
- Examples 01-03: Convenience classes only
- Examples 04+: Introduce ThemedWidget naturally

**❌ DON'T:**
- Mix APIs randomly
- Show ThemedWidget before ThemedQWidget
- Use advanced features in basic examples

---

### In Error Messages

**✅ DO:**
```python
# Runtime validation
TypeError: MyWidget: ThemedWidget must come BEFORE Qt base class.
  ❌ Wrong: class MyWidget(QTextEdit, ThemedWidget)
  ✅ Right: class MyWidget(ThemedWidget, QTextEdit)

📖 See: docs/widget-development-GUIDE.md
```

**❌ DON'T:**
- Generic MRO errors
- No guidance on fix
- Assume user knows inheritance rules

---

## ✅ Success Metrics

### For App Developers (Persona 1)
- [ ] Can build themed app in < 5 minutes
- [ ] Never needs to see "ThemedWidget" in Quick Start
- [ ] Understands when to use ThemedMainWindow vs ThemedDialog

### For Custom Widget Developers (Persona 2)
- [ ] Natural transition from ThemedQWidget → ThemedWidget
- [ ] Understands inheritance order clearly
- [ ] Can debug inheritance errors from validation messages

### For Widget Library Authors (Persona 3)
- [ ] Has access to all advanced features
- [ ] Clear documentation on lifecycle hooks
- [ ] Can build professional widget libraries

### Overall
- [ ] No confusion about "which API to use"
- [ ] Clear progression from beginner → advanced
- [ ] Documentation supports all three personas

---

## 🎓 Key Principles

1. **Progressive Disclosure**
   - Don't overwhelm beginners with power features
   - Reveal complexity only when needed

2. **Natural Learning Path**
   - Each stage builds on previous knowledge
   - "Aha moments" lead to deeper understanding

3. **Two-Tier Simplicity**
   - Simple API: One base class, done
   - Advanced API: Full power when needed

4. **Consistent Pattern**
   - All convenience classes follow same pattern
   - ThemedWidget mixin works everywhere

5. **Clear Transitions**
   - Documentation guides users naturally
   - Examples show progression clearly

---

## 🔄 Evolution Strategy

### Current State (v2.0.0-rc3)
- Both APIs exist
- Documentation being aligned
- Examples being reorganized

### Next Steps
1. Complete documentation alignment
2. Migrate examples to show progression
3. Add DX improvements (Tokens, ThemeProperty, WidgetRole)
4. Add runtime validation for inheritance order

### Future (v2.1+)
- Consider additional convenience classes (ThemedTextEdit?)
- Enhance Tokens with categorization
- Visual theme editor
- Hot-reload for theme development

---

## 📚 Related Documents

- **ROADMAP.md** - Overall project roadmap with API philosophy
- **ARCHITECTURE.md** - Technical implementation details
- **quick-start-GUIDE.md** - For Persona 1 (App Developers)
- **widget-development-GUIDE.md** - For Persona 2 (Custom Widget Developers)
- **api-REFERENCE.md** - Complete API documentation
- **theme-customization-GUIDE.md** - Creating and customizing themes

---

## 💡 Final Thoughts

**The API isn't fragmented - it's progressive.**

- **ThemedMainWindow/ThemedDialog/ThemedQWidget** = Training wheels (great for learning)
- **ThemedWidget** = The real bicycle (what everything is built on)

Users start with training wheels, then naturally graduate to the full bike when ready.

This isn't API confusion - **it's thoughtful API design for different skill levels.**
