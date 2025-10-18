# VFWidgets Theme System - Documentation Index

**Complete guide to the VFWidgets theme system for PySide6/Qt applications**

Version: 2.1.0 (with Unified Token Resolution API)

---

## 📚 Documentation Navigator

### 🚀 Getting Started (Read First!)

**New to the theme system?** Start here:

1. **[../README.md](../README.md)** - Project overview and quick start
2. **[QUICK-START.md](QUICK-START.md)** - 5-minute tutorial for building themed apps
3. **[theme-customization-GUIDE.md](theme-customization-GUIDE.md)** - Creating custom themes

### 🎯 Core Concepts

**Understanding how the theme system works:**

1. **[THEME-SYSTEM.md](THEME-SYSTEM.md)** - Theme system overview and philosophy
2. **[tokens-GUIDE.md](tokens-GUIDE.md)** - Complete token system guide (197 tokens)
3. **[TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md)** - **⭐ NEW** How tokens are resolved (critical!)
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns

### 🔧 Developer Guides

**Building themed applications and widgets:**

1. **[widget-development-GUIDE.md](widget-development-GUIDE.md)** - Using ThemedWidget for custom widgets
2. **[THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md)** - **⭐ NEW** ThemedWidget + Override System
3. **[api-REFERENCE.md](api-REFERENCE.md)** - Complete API reference
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - **⭐ NEW** Common issues and solutions

### 🎨 Advanced Topics

**Customization and theming:**

1. **[OVERLAY-QUICK-START.md](OVERLAY-QUICK-START.md)** - Runtime color customization (v2.0.0)
2. **[OVERLAY-MIGRATION-GUIDE.md](OVERLAY-MIGRATION-GUIDE.md)** - Migrating to overlay system
3. **[fonts-DESIGN.md](fonts-DESIGN.md)** - Font system design and usage
4. **[BREAKING-CHANGES.md](../BREAKING-CHANGES.md)** - Breaking changes by version

---

## 🎓 Learning Paths

### Path 1: Application Developer

**Goal**: Build a themed Qt application

```
1. Read: ../README.md (Quick Start section)
2. Read: QUICK-START.md
3. Read: theme-customization-GUIDE.md (to customize colors)
4. Reference: api-REFERENCE.md (when needed)
```

**Time**: 30 minutes to productive

### Path 2: Widget Developer

**Goal**: Create custom themed widgets

```
1. Complete: Path 1 (Application Developer)
2. Read: widget-development-GUIDE.md
3. Read: TOKEN-RESOLUTION.md ⚠️ CRITICAL - understand resolution!
4. Read: THEMED-WIDGET-INTEGRATION.md ⚠️ CRITICAL - avoid common bugs!
5. Reference: tokens-GUIDE.md (for available tokens)
```

**Time**: 2 hours to expert

### Path 3: Theme System Contributor

**Goal**: Understand and modify the theme system

```
1. Complete: Path 2 (Widget Developer)
2. Read: ARCHITECTURE.md
3. Read: TOKEN-RESOLUTION.md (deep dive into internals)
4. Study: ../wip/resolve-token-api-DESIGN.md (implementation design)
```

**Time**: 4 hours to full understanding

---

## 🔥 Critical Concepts (Don't Skip!)

### 1. Token Resolution System (v2.1.0)

**⚠️ IMPORTANT**: The theme system uses a **unified token resolution API** that integrates with the overlay system.

**Why This Matters**:
- User color customizations work automatically
- App-level branding is preserved across theme changes
- Widget-specific token namespaces are respected
- Fallbacks work correctly

**How It Works**:
```python
# Unified resolution API (v2.1.0)
ThemeManager.resolve_token(token, token_type, fallback, check_overrides)

# Convenience methods
ThemeManager.resolve_color(token, fallback)  # For colors
ThemeManager.resolve_font(token, fallback)   # For fonts
ThemeManager.resolve_size(token, fallback)   # For sizes
```

**Resolution Priority** (from highest to lowest):
```
1. User Override    (app.customize_color() - highest priority)
   ↓
2. App Override     (app_overrides in theme_config)
   ↓
3. Base Theme       (theme.colors dictionary)
   ↓
4. Fallback Value   (provided or default)
```

**📖 Learn More**: [TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md)

### 2. ThemedWidget Integration (v2.1.0)

**⚠️ IMPORTANT**: `ThemedWidget` automatically uses the unified resolution API for all `theme_config` properties.

**What This Means**:
```python
class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'editor.background',  # ✅ Automatically checks overrides!
    }

    def paintEvent(self, event):
        bg = self.theme.bg  # ✅ Returns user override if set
```

**Common Mistake**:
```python
# ❌ DON'T DO THIS - bypasses override system!
theme = self.get_current_theme()
bg = theme.colors.get('editor.background')  # Ignores overrides!

# ✅ DO THIS - uses override system
bg = self.theme.bg  # From theme_config
```

**📖 Learn More**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md)

### 3. Token Namespaces

**⚠️ IMPORTANT**: Tokens use a hierarchical namespace for widget-specific customization.

**Examples**:
```
colors.background              # Global background
editor.background              # Editor-specific (overrides global)
terminal.colors.background     # Terminal-specific (overrides both)
```

**Why This Matters**:
- Terminal can have different colors than the editor
- Tab bars can have different colors than windows
- Widget-specific tokens take precedence

**📖 Learn More**: [tokens-GUIDE.md](tokens-GUIDE.md)

---

## 📖 Documentation Reference

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](../README.md) | Project overview, quick start | Everyone |
| [THEME-SYSTEM.md](THEME-SYSTEM.md) | System overview | App developers |
| [tokens-GUIDE.md](tokens-GUIDE.md) | Token system (197 tokens) | Theme authors |
| [TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md) | **How tokens are resolved** ⭐ | Widget developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture | Contributors |

### Developer Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| [QUICK-START.md](QUICK-START.md) | 5-minute tutorial | New users |
| [widget-development-GUIDE.md](widget-development-GUIDE.md) | Custom widget development | Widget developers |
| [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) | **ThemedWidget + Overrides** ⭐ | Widget developers |
| [theme-customization-GUIDE.md](theme-customization-GUIDE.md) | Create custom themes | Theme authors |
| [api-REFERENCE.md](api-REFERENCE.md) | Complete API reference | All developers |

### Advanced Topics

| Document | Purpose | Audience |
|----------|---------|----------|
| [OVERLAY-QUICK-START.md](OVERLAY-QUICK-START.md) | Runtime customization | App developers |
| [OVERLAY-MIGRATION-GUIDE.md](OVERLAY-MIGRATION-GUIDE.md) | Overlay system migration | Upgrading users |
| [fonts-DESIGN.md](fonts-DESIGN.md) | Font system | Advanced users |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | **Common issues** ⭐ | Everyone |

### Release Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [../CHANGELOG.md](../CHANGELOG.md) | Version history | Everyone |
| [../BREAKING-CHANGES.md](../BREAKING-CHANGES.md) | Breaking changes | Upgrading users |
| [../RELEASE-v2.0.0-OVERLAY-SYSTEM.md](../RELEASE-v2.0.0-OVERLAY-SYSTEM.md) | Overlay system release | v2.0.0 users |

---

## 🚨 Common Pitfalls (Read This!)

### Pitfall 1: Bypassing the Override System

**❌ WRONG**:
```python
# Directly accessing theme.colors bypasses overrides!
theme = widget.get_current_theme()
bg = theme.colors.get('editor.background')  # Ignores user customizations!
```

**✅ CORRECT**:
```python
# Use theme_config or resolve_color()
bg = widget.theme.bg  # From theme_config - checks overrides ✅

# Or use ThemeManager directly
manager = ThemeManager.get_instance()
bg = manager.resolve_color('editor.background')  # Checks overrides ✅
```

**📖 Learn More**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md)

### Pitfall 2: Wrong Token for Top Bar Background

**❌ WRONG**:
```python
# ViloxTerm-specific token (doesn't exist!)
"viloxterm.topBarBackground": "#ff0000"

# Individual tab background (wrong widget!)
"tab.inactiveBackground": "#ff0000"
```

**✅ CORRECT**:
```python
# Generic top bar background (works for all apps)
"editorGroupHeader.tabsBackground": "#ff0000"
```

**Why**: Use generic tokens, not app-specific ones. The top bar is `editorGroupHeader.tabsBackground`, not `tab.*` tokens.

**📖 Learn More**: [tokens-GUIDE.md](tokens-GUIDE.md) - Token Hierarchy section

### Pitfall 3: Inheritance Order for ThemedWidget

**❌ WRONG**:
```python
class MyWidget(QTextEdit, ThemedWidget):  # Wrong order!
    pass
```

**✅ CORRECT**:
```python
class MyWidget(ThemedWidget, QTextEdit):  # ThemedWidget FIRST!
    pass
```

**Why**: Python's Method Resolution Order (MRO) requires ThemedWidget to come first.

**📖 Learn More**: [widget-development-GUIDE.md](widget-development-GUIDE.md) - Inheritance Order section

### Pitfall 4: Accessing Theme Properties in `on_theme_changed()`

**❌ RISKY**:
```python
def on_theme_changed(self):
    # May return stale cached values during theme transition!
    bg = self.theme.bg or '#ffffff'
```

**✅ SAFE**:
```python
def on_theme_changed(self):
    # Query ThemeManager directly for current values
    manager = ThemeManager.get_instance()
    bg = manager.resolve_color('colors.background', fallback='#ffffff')
```

**Why**: Property cache may contain old values during theme transition.

**📖 Learn More**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Theme Properties section

---

## 🔄 Recent Changes

### v2.1.0 (2025-10-18) - Unified Token Resolution API

**Added**:
- ✅ Unified token resolution API (`resolve_token()`, `resolve_color()`, etc.)
- ✅ TokenType enum and type-specific resolvers
- ✅ ThemedWidget integration with override system
- ✅ Comprehensive tests (24/25 passing)

**Impact**:
- User color customizations now work with ThemedWidget
- App-level branding preserved across theme changes
- All widgets automatically respect overrides

**📖 Migration**: [THEMED-WIDGET-INTEGRATION.md](THEMED-WIDGET-INTEGRATION.md) - No code changes required!

### v2.0.0 (2025-10-18) - Theme Overlay System

**Added**:
- ✅ Runtime color customization (customize_color())
- ✅ Two-layer override system (user > app > base)
- ✅ VFThemedApplication with declarative config
- ✅ Automatic persistence to QSettings

**📖 Learn More**: [OVERLAY-QUICK-START.md](OVERLAY-QUICK-START.md)

---

## 🛠️ Quick Reference

### Most Common Tasks

**1. Build a themed app**:
```python
from vfwidgets_theme import ThemedApplication, ThemedMainWindow

app = ThemedApplication(sys.argv)
window = ThemedMainWindow()
window.show()
app.exec()
```

**2. Create a custom widget**:
```python
from vfwidgets_theme import ThemedWidget
from PySide6.QtWidgets import QWidget

class MyWidget(ThemedWidget, QWidget):
    theme_config = {
        'bg': 'colors.background',
        'fg': 'colors.foreground',
    }
```

**3. Customize a color**:
```python
app.customize_color('editor.background', '#ff0000', persist=True)
```

**4. Get effective color**:
```python
from vfwidgets_theme.core.manager import ThemeManager

manager = ThemeManager.get_instance()
color = manager.resolve_color('editor.background', fallback='#1e1e1e')
```

---

## 📞 Getting Help

### Documentation Not Clear?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Search [tokens-GUIDE.md](tokens-GUIDE.md) for token questions
3. Read [TOKEN-RESOLUTION.md](TOKEN-RESOLUTION.md) for resolution questions
4. Review examples in `../examples/`

### Found a Bug?

1. Check if it's a known issue in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify you're using the correct API (not bypassing override system)
3. Check token names against [tokens-GUIDE.md](tokens-GUIDE.md)
4. Report with minimal reproduction case

---

## 📝 Contributing to Documentation

If you find gaps in the documentation:

1. Check if the topic is covered in [../wip/](../wip/) (work in progress docs)
2. Consider adding examples to illustrate the concept
3. Update this index if you add new documentation
4. Follow the naming convention: `<topic>-<PURPOSE>.md`

---

## 🎯 Next Steps

**Choose your path**:

- **New to theming?** → Start with [../README.md](../README.md)
- **Building an app?** → Read [QUICK-START.md](QUICK-START.md)
- **Creating a widget?** → Read [widget-development-GUIDE.md](widget-development-GUIDE.md)
- **Having issues?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Last Updated**: 2025-10-18
**Version**: 2.1.0
**Contributors**: VFWidgets Team
