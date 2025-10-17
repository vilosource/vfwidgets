# ViloWeb Documentation

Welcome to the ViloWeb documentation directory!

## What is ViloWeb?

ViloWeb is **not a typical web browser**. It's a unique educational platform and showcase application with three primary purposes:

1. **Learning Platform**: Teach Python developers how to control QWebEngineView and build browser automation tools
2. **VFWidgets Showcase**: Demonstrate every major VFWidgets component in a real-world application
3. **Python Extensions**: First browser where extensions are written in **Python**, not JavaScript

## Target Audience

- **Python developers** learning QtWebEngine and Qt/PySide6
- **VFWidgets evaluators** wanting to see components in action
- **Web automation engineers** seeking Python-based browser control
- **Educators** teaching web automation and Qt programming

## Documentation Files

### 📋 [SPECIFICATION.md](SPECIFICATION.md) (2,322 lines)
**Complete technical specification covering:**

**Section 1-2: Vision & Goals**
- Educational first approach
- Python developer learning objectives
- VFWidgets showcase requirements
- Three user personas (learner, evaluator, automation engineer)

**Section 3-4: Architecture & Features**
- Multi-process browser architecture
- Component hierarchy (ChromeTabbedWindow, ViloCodeWindow)
- 4-phase development roadmap
- Core browser features (tabs, bookmarks, history, downloads)

**Section 5: Python Extensions (★ UNIQUE)**
- Python-based extension system (not JavaScript!)
- Extension API reference (40+ methods)
- 3 example extensions included:
  - Ad Blocker (URL filtering, element hiding)
  - Page Modifier (dark mode, CSS injection)
  - Web Scraper (Beautiful Soup integration, data extraction)
- Extension template generator
- Interactive tutorial system

**Section 5.5-5.8: Learning Features**
- Built-in Python console panel
- 6 interactive tutorials (Hello World to Ad Blocker)
- VFWidgets showcase (terminal, markdown viewer, split view)
- Extensively commented codebase
- Tutorial-style READMEs

**Section 6-13: Technical Details**
- QtWebEngine configuration
- JavaScript bridge patterns
- Storage architecture (SQLite + JSON)
- Performance targets
- Testing strategy
- Complete keyboard shortcuts reference

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) *(Coming Soon)*
**Detailed technical architecture document:**
- Component diagrams and data flow
- Class hierarchy and relationships
- Signal/slot connection patterns
- Module responsibilities
- JavaScript bridge implementation details

### 🎨 [UI-MOCKUPS.md](UI-MOCKUPS.md) *(Coming Soon)*
**UI designs and mockups:**
- Main window layout (ASCII art)
- Sidebar panel designs
- Python console interface
- Extension manager UI
- Tutorial viewer mockups

## Quick Start

### For Learners

1. Read [SPECIFICATION.md](SPECIFICATION.md) sections 1-2 for goals
2. Read section 5 for Python extension system
3. Look at section 5.5 for learning features
4. Check section 5.7 for code organization principles

### For VFWidgets Evaluators

1. Read sections 1-2 for project vision
2. Read section 3 for architecture overview
3. Read section 5.6 for VFWidgets showcase features
4. See "For VFWidgets Evaluators" in conclusion

### For Automation Engineers

1. Read section 5.2 for Extension API
2. Read section 5.3 for example extensions
3. Read section 5.8 for using ViloWeb as library
4. See "For Web Automation Engineers" in conclusion

## Key Features

### Python Extensions (Unique!)
```python
class MyExtension(ViloWebExtension):
    def on_page_load(self, url, page):
        # Full Python + Qt APIs available!
        if "ad" in url:
            self.api.show_notification("Blocked ad!")
            return False  # Block
        return True
```

### Web Automation
```python
from viloweb import Browser

browser = Browser(headless=True)
browser.navigate("https://example.com")
title = browser.execute_js("return document.title")
browser.screenshot("page.png")
```

### Built-in Learning
- Interactive Python console
- 6 step-by-step tutorials
- Extension template generator
- Heavily commented code

### VFWidgets Showcase
- ChromeTabbedWindow (tab management)
- ViloCodeWindow (sidebar panels)
- vfwidgets-terminal (Python REPL)
- vfwidgets-markdown (docs viewer)
- vfwidgets-theme (theming)

## Development Phases

**Phase 1 (Weeks 1-2)**: Foundation + Python console + first tutorial
**Phase 2 (Weeks 3-4)**: All panels + VFWidgets integration
**Phase 3 (Weeks 5-8)**: Complete extension system + examples
**Phase 4 (Weeks 9-12)**: Advanced features + packaging

## Contributing

ViloWeb is part of the VFWidgets monorepo. When contributing:

1. **Code Quality**: Every file is a teaching tool – extensive comments required
2. **Learning Focus**: Explain "why" not just "what"
3. **Examples**: Provide working examples for every feature
4. **Documentation**: Update tutorials when adding features

## Philosophy

**"Code as Teaching Material"**

Every line of code in ViloWeb should teach something:
- Why this pattern, not alternatives?
- What Qt concept does this demonstrate?
- How can developers use this in their projects?

**"Python First"**

Everything extensible uses Python:
- Extensions written in Python
- Automation API is Python
- Console is Python REPL
- Scripts are Python files

**"Real World, Real Learning"**

ViloWeb is not a toy:
- Production-quality architecture
- Professional code standards
- Actually useful as a browser
- Deployable and embeddable

## Resources

- **VFWidgets Docs**: https://github.com/your-repo/vfwidgets
- **QtWebEngine Docs**: https://doc.qt.io/qt-6/qtwebengine-index.html
- **PySide6 Docs**: https://doc.qt.io/qtforpython/
- **Extension Examples**: `~/.viloweb/extensions/` (after installation)

## Status

**Current**: Design phase, specification complete
**Next**: Begin Phase 1 implementation
**Goal**: Educational browser showcasing VFWidgets + Python extensions

---

**Questions?** Read [SPECIFICATION.md](SPECIFICATION.md) for comprehensive details.

**Want to contribute?** Start with Phase 1 tasks in section 6 of SPECIFICATION.md.

**Need help?** Create an issue on GitHub with `[viloweb]` tag.
