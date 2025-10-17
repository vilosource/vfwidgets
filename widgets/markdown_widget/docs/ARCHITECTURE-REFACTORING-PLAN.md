# Markdown Widget Architecture Refactoring - Research & Analysis Plan

## Current Architecture Issues Identified

### 1. **Tight Coupling (1222 lines in markdown_viewer.py)**
   - QWebEngineView setup mixed with business logic
   - Theme handling embedded in widget code
   - JavaScript bridge hardcoded
   - HTML/JS rendering logic scattered across Python and JavaScript

### 2. **No Renderer Abstraction**
   - Single markdown-it based renderer hardcoded
   - Cannot swap renderers (Python markdown, mistune, etc.)
   - Difficult to test JavaScript rendering in isolation

### 3. **Theme Integration Problems** (Current Issue)
   - CSS injection happens via JavaScript strings in Python
   - No clear boundary between theme system and rendering
   - Debugging requires inspecting both Python logs and browser DevTools
   - CSS specificity issues difficult to debug without browser tools

### 4. **Testing Limitations**
   - No JavaScript unit tests
   - No integration tests for HTML rendering
   - Cannot test theme application without full QWebEngineView
   - Cannot reproduce CSS issues outside of running application

## Current Architecture Map

### File Structure
```
markdown_widget/
├── src/vfwidgets_markdown/
│   ├── models/
│   │   ├── document.py (190 lines) - Pure data model
│   │   ├── events.py - Event types
│   │   └── protocols.py - Observer protocol
│   ├── controllers/
│   │   └── editor_controller.py (198 lines) - Editor logic
│   ├── widgets/
│   │   ├── markdown_viewer.py (1222 lines) ⚠️ MONOLITHIC
│   │   ├── editor_widget.py - Editor UI
│   │   ├── text_editor.py - Text input
│   │   └── toc_view.py - Table of contents
│   └── resources/
│       ├── viewer.html - HTML template
│       ├── css/
│       │   ├── viewer.css - Custom styles
│       │   └── prism-themes/ - Syntax highlighting themes
│       └── js/
│           ├── viewer.js (691 lines) - Rendering engine
│           ├── markdown-it.min.js - Parser
│           ├── prism.min.js - Syntax highlighter
│           └── mermaid.min.js - Diagrams
```

### Responsibilities Analysis

**markdown_viewer.py (1222 lines) - TOO MANY RESPONSIBILITIES**
1. QWebEngineView lifecycle management
2. QWebChannel bridge setup
3. Theme system integration (ThemedWidget)
4. Theme token resolution and fallback logic
5. CSS variable injection via JavaScript
6. Prism.js CSS override injection
7. Document observer pattern
8. Image path resolution
9. Markdown rendering coordination
10. HTML/PDF export
11. Scroll sync
12. Keyboard shortcuts
13. TOC extraction
14. File loading

**viewer.js (691 lines) - JavaScript Rendering Engine**
1. markdown-it initialization and plugin configuration
2. Prism.js syntax highlighting
3. Mermaid diagram rendering
4. Theme switching (light/dark)
5. QWebChannel communication
6. Scroll position management
7. Keyboard shortcuts
8. HTML export
9. TOC extraction

## Proposed Solution: Clean Architecture for WebView Widgets

### Core Principles
1. **Separation of Concerns**: Rendering logic separate from Qt widget logic
2. **Testability**: HTML/JS components testable in isolation
3. **Flexibility**: Support multiple renderer implementations
4. **Reusability**: Pattern applicable to all webview-based widgets
5. **Debuggability**: Clear boundaries make issues easier to isolate

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Widget Layer (Qt/PySide6)                 │
│  MarkdownViewer(ThemedWidget, QWebEngineView)              │
│  - Widget lifecycle, signals, slots                         │
│  - Theme integration (ThemedWidget protocol)                │
│  - User interaction handling                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Host Layer (Abstraction)                   │
│  WebViewHost                                                 │
│  - QWebEngineView wrapper                                   │
│  - Bridge management                                         │
│  - Resource loading                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Bridge Layer (Communication)                │
│  ThemeBridge: Python ↔ JavaScript theme communication       │
│  MessageBridge: Bidirectional messaging                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Renderer Layer (HTML/JS/CSS)                  │
│  RendererProtocol (ABC)                                     │
│  ├── MarkdownItRenderer (HTML/JS implementation)            │
│  └── PythonMarkdownRenderer (Server-side rendering)         │
└─────────────────────────────────────────────────────────────┘
```

### Proposed Directory Structure

```
markdown_widget/
├── src/vfwidgets_markdown/
│   ├── models/                    # Data models (unchanged)
│   │   └── document.py
│   ├── controllers/               # Business logic (unchanged)
│   │   └── editor_controller.py
│   ├── widgets/
│   │   └── markdown_viewer.py    # ⬇️ REDUCED to ~400 lines
│   ├── hosting/                   # 🆕 WebView host abstraction
│   │   ├── webview_host.py       # QWebEngineView wrapper
│   │   └── resource_loader.py    # Resource management
│   ├── bridges/                   # 🆕 Python ↔ JS communication
│   │   ├── theme_bridge.py       # Theme communication protocol
│   │   └── message_bridge.py     # General messaging
│   ├── renderers/                 # 🆕 Pluggable rendering engines
│   │   ├── base.py               # RendererProtocol (ABC)
│   │   ├── markdown_it/          # HTML/JS renderer (current)
│   │   │   ├── renderer.py       # Python coordinator
│   │   │   ├── html/
│   │   │   │   └── viewer.html   # Template
│   │   │   ├── js/
│   │   │   │   ├── viewer.js     # Rendering engine
│   │   │   │   ├── plugins/      # markdown-it plugins
│   │   │   │   └── lib/          # 3rd party libs
│   │   │   └── css/
│   │   │       ├── viewer.css    # Base styles
│   │   │       └── themes/       # Prism themes
│   │   └── python_markdown/      # 🔮 Future: Server-side
│   │       └── renderer.py
│   └── tests/                     # 🆕 Enhanced testing
│       ├── unit/
│       │   ├── test_bridges.py
│       │   └── test_renderers.py
│       ├── integration/
│       │   └── test_full_widget.py
│       └── html/                  # 🆕 Playwright tests
│           ├── test_markdown_it_renderer.py
│           └── test_theme_application.py
```

## Phase 1: Research & Documentation

### Tasks
1. ✅ **Audit current architecture** - COMPLETED
2. **Document current responsibilities** - IN PROGRESS
3. **Research webview patterns** from:
   - VS Code's webview API architecture
   - Jupyter QtConsole webview implementation
   - QWebEngineView best practices in PySide6 projects
4. **Design abstractions**:
   - `RendererProtocol` - Abstract markdown rendering interface
   - `ThemeBridge` - Clean Python↔JavaScript theme communication
   - `WebViewHost` - Reusable QWebEngineView wrapper
5. **Research Playwright integration** for HTML/JS testing
6. **Create detailed migration plan**

### Research Questions
- How do other projects handle CSS injection for theming?
- What's the best way to test QWebEngineView components?
- How to structure bidirectional Python ↔ JavaScript communication?
- Can we use Playwright with QWebEngineView or need separate HTML testing?

## Phase 2: Interface Design

### RendererProtocol (ABC)
```python
from abc import ABC, abstractmethod
from typing import Protocol

class RendererProtocol(Protocol):
    """Abstract interface for markdown renderers."""

    @abstractmethod
    def render(self, markdown: str) -> str:
        """Render markdown to HTML."""
        pass

    @abstractmethod
    def set_theme(self, theme_data: dict) -> None:
        """Apply theme to renderer."""
        pass

    @abstractmethod
    def get_toc(self) -> list[dict]:
        """Extract table of contents."""
        pass

    @abstractmethod
    def export_html(self, markdown: str) -> str:
        """Export standalone HTML."""
        pass
```

### ThemeBridge
```python
class ThemeBridge:
    """Manages theme communication between Python and JavaScript."""

    def __init__(self, page: QWebEnginePage):
        self.page = page

    def apply_theme(self, theme: Theme) -> None:
        """Apply theme to web content."""
        css_vars = self._build_css_variables(theme)
        self._inject_css(css_vars)

    def _build_css_variables(self, theme: Theme) -> dict:
        """Build CSS variables from theme tokens."""
        pass

    def _inject_css(self, css_vars: dict) -> None:
        """Inject CSS variables into page."""
        pass
```

## Phase 3: Extraction & Refactoring

### Step 1: Extract HTML/JS Renderer
1. Move `resources/` to `renderers/markdown_it/`
2. Create `MarkdownItRenderer` class
3. Extract JavaScript rendering logic
4. Make renderer independently testable

### Step 2: Extract Theme Bridge
1. Create `ThemeBridge` class
2. Move CSS variable injection logic
3. Move Prism override logic
4. Add comprehensive logging

### Step 3: Extract WebView Host
1. Create `WebViewHost` wrapper
2. Move QWebEngineView setup
3. Move bridge management
4. Make host reusable

### Step 4: Refactor MarkdownViewer
1. Use `WebViewHost` for web rendering
2. Use `ThemeBridge` for theming
3. Use `RendererProtocol` for markdown rendering
4. Reduce to ~400 lines (widget logic only)

## Phase 4: Testing Infrastructure

### Unit Tests
- Test `ThemeBridge` CSS variable generation
- Test `RendererProtocol` implementations
- Test theme token resolution logic

### Integration Tests
- Test `WebViewHost` with mock page
- Test full widget with mock renderer
- Test theme application end-to-end

### HTML/JS Tests (Playwright)
- Test markdown-it rendering in isolation
- Test Prism syntax highlighting
- Test CSS theme application
- Test Mermaid diagram rendering
- **Fix current theme.colors.code.background issue in isolation!**

## Phase 5: Migration Plan

### Backward Compatibility
- Keep existing `MarkdownViewer` API unchanged
- Internal refactoring only
- All tests must pass
- No breaking changes for users

### Incremental Steps
1. Create new architecture in parallel
2. Migrate functionality piece by piece
3. Add comprehensive tests for each piece
4. Switch `MarkdownViewer` to use new architecture
5. Deprecate old internal code

## Benefits

### Immediate
- ✅ **Fix current theme issue**: Isolated testing will reveal CSS problem
- ✅ **Testability**: Test HTML/JS separately with Playwright
- ✅ **Debuggability**: Clear separation makes issues easier to isolate

### Long-term
- ✅ **Flexibility**: Swap renderers (markdown-it, Python markdown, etc.)
- ✅ **Reusability**: Pattern for all future webview widgets (terminal, PDF viewer, etc.)
- ✅ **Maintainability**: Smaller, focused modules easier to maintain
- ✅ **Performance**: Can optimize renderers independently

## Pattern for Future WebView Widgets

This architecture becomes the **standard pattern** for:
- Terminal widget (already using webview + xterm.js)
- Future PDF viewer widget
- Future diagram widget
- Any widget using HTML/JS rendering

### Standard Components
1. `WebViewHost` - Reusable host for any webview content
2. `ThemeBridge` - Standard theme communication
3. `MessageBridge` - Standard Python ↔ JS messaging
4. Playwright test infrastructure

## Current Theme Issue Resolution

With this architecture, the `markdown.colors.code.background` issue will be:

1. **Reproducible** in isolated HTML test
2. **Debuggable** in browser DevTools without running full app
3. **Testable** with automated Playwright tests
4. **Fixable** once in ThemeBridge, applies to all future widgets

## Next Steps

1. ✅ Document current architecture (this file)
2. Research webview patterns in other projects
3. Design detailed `RendererProtocol` interface
4. Design detailed `ThemeBridge` interface
5. Create proof-of-concept: Extract markdown-it renderer
6. Test POC with Playwright
7. Fix theme.colors.code.background in isolated test
8. Gradually migrate full architecture

---

**Status**: Research & Planning Phase
**Priority**: High - Fixes current theme issues + establishes pattern for future
**Estimated Effort**: 2-3 weeks for complete refactoring
**Risk**: Low - Incremental approach with backward compatibility
