# VFTheme Studio

**Visual Theme Designer for VFWidgets Applications**

[![Version](https://img.shields.io/badge/version-0.1.0--dev-orange.svg)](https://github.com/viloforge/vfwidgets)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.9+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Phase%202%20Complete-brightgreen.svg)]()
[![Production](https://img.shields.io/badge/production--ready-MVP%20YES-brightgreen.svg)]()

---

## What is VFTheme Studio?

**VFTheme Studio** is a professional standalone application for creating and editing themes for VFWidgets-based applications. Inspired by Qt Designer's workflow, it enables designers and developers to create comprehensive themes **without writing a single line of code**.

Think of it as **"Photoshop for Qt Themes"** - a visual design tool where you see exactly how your theme looks in real-time across all widgets.

---

## ✨ Key Features

### 🎨 **Visual Theme Design**
- **Zero-Code Creation**: Design themes visually with color pickers and live preview
- **200+ Theme Tokens**: Complete coverage of all UI elements
- **Real-Time Preview**: See changes instantly across all widgets
- **3-Panel Layout**: Token browser, preview canvas, and property inspector

### 🔌 **Plugin-Based Preview System**
- **Generic Qt Widgets**: Standard buttons, inputs, lists, tables, tabs
- **Custom VFWidgets**: Live preview of Terminal, Multisplit, Chrome Tabs
- **Extensible**: Third-party developers can create preview plugins

### ♿ **Accessibility First**
- **WCAG Validation**: Built-in contrast checker for AA/AAA compliance
- **Auto-Fix Suggestions**: Automatic suggestions for accessibility issues
- **Colorblind Simulation**: Preview themes as colorblind users see them

### 📦 **Multi-Format Export**
- VFWidgets JSON (native format)
- VS Code Theme (.jsonc)
- CSS Variables (--token-name)
- Qt Stylesheet (.qss)
- Python Dict (.py)

### 🎯 **Professional Tools**
- **Palette Extractor**: Extract colors from images/screenshots
- **Color Harmonizer**: Generate complementary color schemes
- **Bulk Operations**: Edit multiple tokens simultaneously
- **Theme Templates**: 10+ built-in professional templates (Material, Nord, Dracula, etc.)

---

## 🚀 Quick Start (When Released)

### Installation

```bash
# From PyPI (coming soon)
pip install vftheme-studio

# From source (development)
cd /path/to/vfwidgets/apps/theme-studio
pip install -e .
```

### Launch Application

```bash
# Command-line launch
vftheme-studio

# Or via Python module
python -m theme_studio
```

### Create Your First Theme

1. **File → New Theme from Template**
2. Choose "Dark Minimal" template
3. Edit tokens with color picker
4. See live preview updates
5. **File → Export → VFWidgets JSON**
6. Theme ready to use!

**Time to create professional theme:** 15-30 minutes (down from 2+ hours manually!)

---

## ⌨️ Keyboard Shortcuts

VFTheme Studio includes comprehensive keyboard shortcuts with **user customization** support (powered by vfwidgets-keybinding).

### File Operations
- `Ctrl+N` - New Theme
- `Ctrl+Shift+N` - New from Template
- `Ctrl+O` - Open Theme
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save As
- `Ctrl+E` - Export
- `Ctrl+Q` - Exit

### Editing
- `Ctrl+Z` - Undo
- `Ctrl+Shift+Z` - Redo
- `Ctrl+F` - Find Token
- `Ctrl+,` - Preferences

### View
- `Ctrl++` - Zoom In
- `Ctrl+-` - Zoom Out
- `Ctrl+0` - Reset Zoom
- `F11` - Fullscreen

### Tools
- `Ctrl+Shift+P` - Palette Extractor
- `Ctrl+H` - Color Harmonizer
- `Ctrl+B` - Bulk Edit

### Other
- `F7` - Validate Accessibility
- `Ctrl+D` - Compare Themes
- `F1` - Documentation

**Customize Shortcuts:** All shortcuts can be customized via Edit → Preferences → Keyboard Shortcuts. Custom bindings are saved to `~/.config/vftheme-studio/keybindings.json`.

---

## 📸 Screenshots

*Coming soon - application in design phase*

**Preview of planned UI:**

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  Theme  View  Tools  Window  Help                    │
├──────────┬────────────────────────────────┬─────────────────────┤
│ TOKEN    │        PREVIEW CANVAS          │    INSPECTOR        │
│ BROWSER  │                                │                     │
│          │  ┌──────────────────────┐      │  Token Properties   │
│ ▼ colors │  │   Widget Library     │      │  ┌───────────────┐ │
│   • fg   │  │  [BTN] [INPUT] [TAB] │      │  │ button.bg     │ │
│   • bg   │  └──────────────────────┘      │  │ #0e639c       │ │
│ ▼ button │                                │  │ [Color Picker]│ │
│   • bg   │  ┌──────────────────────┐      │  │               │ │
│   • hover│  │                      │      │  │ Contrast: 4.8 │ │
│          │  │   Live Preview       │      │  │ WCAG AA: ✓    │ │
│ [Search] │  │   ┌────┐  ┌────┐     │      │  └───────────────┘ │
│          │  │   │BTN │  │BTN │     │      │                     │
└──────────┴────────────────────────────────┴─────────────────────┘
```

---

## 🎯 Use Cases

### For UI/UX Designers
- Create brand-consistent themes without coding
- Extract palettes from design mockups
- Ensure WCAG accessibility compliance
- Generate theme documentation automatically

### For Application Developers
- Quickly customize themes for specific apps
- Preview themes on actual custom widgets (Terminal, etc.)
- Export to multiple formats (JSON, CSS, QSS)
- Use professional templates as starting points

### For Theme Creators
- Create high-quality theme packs
- Validate accessibility before sharing
- Generate preview cards for marketing
- Export comprehensive documentation

---

## 🏗️ Architecture

**Technology Stack:**
- **Framework**: PySide6 6.9+
- **Base Window**: ViloCodeWindow (VS Code-style layout)
- **Theme System**: vfwidgets-theme (200+ tokens)
- **Preview Plugins**: Modular architecture for custom widgets

**Core Components:**
- **Token Browser Panel**: Hierarchical tree of 200+ tokens
- **Preview Canvas Panel**: Zoomable, interactive widget preview
- **Inspector Panel**: Token editor with accessibility validation
- **Plugin System**: Extensible preview for custom widgets

See [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) for detailed technical architecture.

---

## 📚 Documentation

- **[SPECIFICATION.md](docs/SPECIFICATION.md)** - Complete technical specification
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture (coming soon)
- **[USER-GUIDE.md](docs/USER-GUIDE.md)** - End-user documentation (coming soon)
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer setup guide (coming soon)

---

## 🗺️ Development Status & Roadmap

### Current Status: **Phase 1 Complete - NOT Production-Ready**

**Build Status:**
- [![Phase 1](https://img.shields.io/badge/Phase%201-Complete%20(100%25)-green.svg)]()
- [![Phase 2](https://img.shields.io/badge/Phase%202-Not%20Started-red.svg)]()
- [![Production](https://img.shields.io/badge/Production%20Ready-NO-red.svg)]()

**What Works Now (Phase 1 - Read-Only Viewer):**
- ✅ 3-panel layout (token browser | preview | inspector)
- ✅ Token browser with 197 tokens organized in categories
- ✅ Token search/filter functionality
- ✅ Read-only inspector showing token details
- ✅ Preview canvas with Generic Widgets plugin
- ✅ File operations (New, Open, Save, Save As)
- ✅ 10/10 E2E tests passing

**What DOESN'T Work (Not Yet Implemented):**
- ❌ Cannot edit token values (Inspector is read-only)
- ❌ No color picker (editing required first)
- ❌ No font picker (editing required first)
- ❌ No undo/redo (not needed without editing)
- ❌ No real-time preview updates (no changes to preview)
- ❌ Cannot create usable themes

**Bottom Line:** Phase 1 is a foundation/proof-of-concept. You can browse and inspect themes, but you cannot edit them. **Not suitable for real theme development work yet.**

---

### Roadmap to Production-Ready

**Phase 1: Foundation ✅ COMPLETE** (October 2025)
- ✅ Basic application structure
- ✅ 3-panel layout
- ✅ Token browser (read-only)
- ✅ Static preview with plugins
- ✅ File operations (New, Open, Save)
- ✅ QPalette integration improvement (bonus)
- **Status:** Complete but read-only

**Phase 2: Editing Capabilities ⏳ REQUIRED FOR MVP** (Weeks 3-4)
- [ ] Token value editing in Inspector
- [ ] Color picker integration
- [ ] Font picker integration
- [ ] Token validation (prevent broken themes)
- [ ] Undo/redo system
- [ ] Real-time preview updates
- **Status:** Not started
- **Goal:** Make app actually useful for theme development

**Phase 3: Enhancement & Polish** (Weeks 5-6)
- [ ] Additional preview plugins
- [ ] Theme metadata editor
- [ ] Export to multiple formats
- [ ] Keyboard shortcuts
- [ ] Recent files menu
- [ ] Preferences dialog
- **Status:** Not started
- **Goal:** Production-ready MVP

**Phase 4-8: Advanced Features** (Weeks 7-16)
- [ ] Theme templates
- [ ] Palette extraction from images
- [ ] Color harmonizer
- [ ] Accessibility validation (WCAG)
- [ ] Zoomable canvas
- [ ] Bulk token editing
- [ ] Desktop integration
- **Status:** Future
- **Goal:** Professional-grade tool

---

### Production-Ready Timeline

**Minimum Viable Product (MVP):**
- Requires: Phase 1 ✅ + Phase 2 ❌ + Phase 3 (partial)
- Estimate: 2-3 more weeks of development
- Target: Q1 2026

**Full v1.0 Release:**
- Requires: Phases 1-8 complete
- Estimate: 3-4 months of development
- Target: Q2 2026

**Current Reality Check:**
- Phase 1 took ~2 weeks
- Application exists but cannot edit themes
- Need Phase 2 before this is usable
- Realistic MVP: 4-6 weeks total (2 weeks done, 2-4 weeks remaining)

See [PHASE1-COMPLETE.md](PHASE1-COMPLETE.md) for detailed Phase 1 summary and production-readiness assessment.

---

## 🤝 Contributing

VFTheme Studio is part of the VFWidgets ecosystem. Contributions are welcome!

**Ways to contribute:**
- **Preview Plugins**: Create plugins for your custom widgets
- **Export Formats**: Add new export format converters
- **Templates**: Design professional theme templates
- **Documentation**: Improve user guides and tutorials
- **Testing**: Test on different platforms and report issues

**Development Setup:**

```bash
# Clone repository
git clone https://github.com/viloforge/vfwidgets.git
cd vfwidgets/apps/theme-studio

# Install in development mode
pip install -e ".[dev]"

# Run application
python -m theme_studio
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qt/PySide6 Team** - Excellent framework
- **VS Code Team** - Inspiration for theme format and UI
- **VFWidgets Team** - Foundation theme system
- **Qt Designer** - Inspiration for visual design workflow

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/viloforge/vfwidgets/issues)
- **Discussions**: [GitHub Discussions](https://github.com/viloforge/vfwidgets/discussions)
- **Email**: vilosource@viloforge.com

---

## 🌟 Why VFTheme Studio?

**Problem**: Creating comprehensive Qt themes requires:
- Writing hundreds of lines of CSS-like stylesheets
- Testing across dozens of widget types and states
- Manually checking accessibility compliance
- Converting between different format specifications
- Hours of trial-and-error iteration

**Solution**: VFTheme Studio provides:
- ✅ Visual color picking instead of hex codes
- ✅ Live preview across all widget types
- ✅ Automatic accessibility validation
- ✅ One-click export to multiple formats
- ✅ 15-30 minute theme creation time

**The first visual theme designer built specifically for Qt/PySide6 applications!**

---

**Ready to create beautiful themes?** Watch this space for the v1.0 release!
