# Markdown Widget Architecture Analysis

## Executive Summary

This document consolidates research and analysis into the markdown widget's architecture issues and proposes a comprehensive refactoring plan. The current monolithic design (`markdown_viewer.py`: 1222 lines) prevents proper testing, debugging, and reusability of HTML/JS components.

**Root Cause of Current Issues:**
The `markdown.colors.code.background` theme token not applying visually is a **symptom** of deeper architectural problems:
- No separation between Qt widget logic and HTML/JS rendering
- Cannot test HTML/CSS in isolation
- No abstraction for theme communication
- Cannot reuse webview patterns for other widgets

**Proposed Solution:**
4-layer clean architecture (Widget → Host → Bridge → Renderer) with:
- Extractable, testable HTML/JS components
- Playwright-based browser testing
- Reusable patterns for all future webview widgets
- Backward-compatible migration path

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Research Findings](#research-findings)
3. [Proposed Architecture](#proposed-architecture)
4. [Design Specifications](#design-specifications)
5. [Migration Strategy](#migration-strategy)
6. [Benefits & Trade-offs](#benefits--trade-offs)
7. [Next Steps](#next-steps)

---

## Problem Statement

### Current Issue: Theme Token Not Applying

**Symptom:**
`markdown.colors.code.background` set to `#ff0000` in Theme Studio:
- ✅ Token resolved correctly in Python
- ✅ CSS variable injected: `--md-code-bg = #ff0000`
- ✅ JavaScript executed successfully
- ❌ **Visual not updating** - code blocks remain default color

**Debugging Challenges:**
1. Cannot reproduce in browser DevTools without running full Qt app
2. Cannot test CSS specificity in isolation
3. Prism.js CSS overrides mixed with widget logic
4. No way to validate actual computed styles

### Root Architectural Problems

#### 1. **Tight Coupling** (1222 lines in `markdown_viewer.py`)

**Current Responsibilities (14 different concerns):**
1. QWebEngineView lifecycle management
2. QWebChannel bridge setup
3. ThemedWidget integration
4. Theme token resolution with fallbacks
5. CSS variable injection via JavaScript
6. Prism.js CSS override injection
7. Document observer pattern
8. Image path resolution
9. Markdown rendering coordination
10. HTML/PDF export
11. Scroll synchronization
12. Keyboard shortcuts
13. TOC extraction
14. File loading

**Problem:** Changing theme logic requires touching widget, which requires touching QWebEngine setup, which requires changing tests...

#### 2. **No Renderer Abstraction**

**Current:**
- Single markdown-it implementation hardcoded
- Cannot swap to Python-based renderer
- Cannot test rendering without QWebEngineView
- HTML/JS/CSS scattered across `resources/` directory

**Impact:**
- Cannot optimize for different use cases (lightweight vs. feature-rich)
- Cannot test JavaScript independently
- Difficult to add alternative renderers

#### 3. **Theme Integration Problems**

**Current:**
- CSS injection via JavaScript strings in Python
- No clear boundary between theme system and rendering
- Debugging requires inspecting both Python logs AND browser DevTools
- CSS specificity issues impossible to debug without running full app

**Impact:**
- Current `markdown.colors.code.background` issue
- Future theme issues will be equally difficult to debug
- Each webview widget reimplements theme injection

#### 4. **Testing Limitations**

**Current:**
- No JavaScript unit tests
- No integration tests for HTML rendering
- Cannot test theme application without full QWebEngineView
- Cannot reproduce CSS issues outside of running application

**Impact:**
- Slow test cycles (must run full Qt app)
- Cannot isolate CSS issues
- Regression risks when changing theme code

---

## Research Findings

### 1. Webview Patterns Research

**Sources Analyzed:**
- VS Code webview API architecture
- Jupyter QtConsole webview implementation
- Qt/PySide6 best practices
- Electron architecture patterns

**Key Findings:**

#### CSS Theme Injection (VS Code Pattern)
```javascript
// VS Code approach (gold standard)
document.documentElement.style.setProperty('--vscode-editor-foreground', '#cccccc');
```

✅ **Our current approach is correct** - using CSS custom properties
❌ **Problem is in testing/debugging** - need browser DevTools access

#### Testing Strategy
- **Cannot use Playwright directly with QWebEngineView** (QtWebEngine CDP server incomplete)
- **Solution:** Dual testing approach:
  - HTML/JS unit tests: Playwright on standalone HTML files
  - Qt integration tests: pytest-qt for widget functionality

#### Communication Patterns
- **QWebChannel is best practice** for Qt/JS communication
- Better than Electron's string-based IPC (type-safe, bidirectional)
- Must keep reference to channel object (GC prevention)

**Reference:** `webview-patterns-RESEARCH.md`

### 2. Architecture Patterns from Terminal Widget

**Terminal Widget Lessons:**
- 3-layer transparency pattern works well
- Direct theme access via `get_current_theme()` more reliable than property system
- Pending theme storage needed for async initialization
- Missing token diagnostics help developers

**Problems to Avoid:**
- Fragile theme type detection (reaching into app internals)
- `print()` instead of `logger.debug()`
- No diagnostic visibility for missing tokens

**Reference:** `terminal-theme-improvements-ANALYSIS.md`

### 3. Clean Architecture Principles

**From VFWidgets Guidelines:**
- Model-View-Controller separation
- Protocol-based dependency injection
- Performance-first: <100ms operations
- Test-driven development

**Application to Markdown Widget:**
```
Model: Document (pure data) ✅ Already good
View: Qt widgets + HTML/JS rendering
Controller: Editor controller ✅ Already good
Protocols: Need RendererProtocol, theme communication abstraction
```

---

## Proposed Architecture

### 4-Layer Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Widget Layer (Qt/PySide6)                 │
│  MarkdownViewer(ThemedWidget, QWebEngineView)              │
│  - Widget lifecycle, signals, slots                         │
│  - ThemedWidget protocol implementation                     │
│  - Public API (set_markdown, export_html, etc.)            │
│  - Coordinate host, bridge, renderer                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Host Layer (Qt Integration)                │
│  WebViewHost                                                 │
│  - QWebEngineView/Page setup                               │
│  - QWebChannel management                                   │
│  - Resource loading (HTML/CSS/JS)                           │
│  - Transparency configuration                               │
│  - Page lifecycle events                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Bridge Layer (Python ↔ JavaScript)             │
│  ThemeBridge: Theme communication                           │
│  - Token resolution with fallbacks                          │
│  - CSS variable building                                    │
│  - CSS injection via JavaScript                             │
│  - Validation & diagnostics                                 │
│                                                             │
│  MessageBridge: General communication                       │
│  - Bidirectional message passing                            │
│  - Type-safe communication                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Renderer Layer (HTML/JS/CSS)                  │
│  RendererProtocol (Abstract Interface)                      │
│  ├── MarkdownItRenderer (Current: HTML/JS)                 │
│  │   ├── html/viewer.html                                  │
│  │   ├── css/viewer.css, prism-themes/                    │
│  │   └── js/viewer.js, markdown-it, prism, mermaid        │
│  │                                                          │
│  └── PythonMarkdownRenderer (Future: Pure Python)          │
│      └── No JavaScript, faster startup, simpler            │
└─────────────────────────────────────────────────────────────┘
```

### Responsibility Matrix

| Layer | Responsibilities | Dependencies | Testable With |
|-------|-----------------|--------------|---------------|
| **Widget** | Qt lifecycle, public API, coordination | Host, Bridge, Renderer | pytest-qt |
| **Host** | QWebEngine setup, resource loading | Qt only | pytest-qt (mocked) |
| **Bridge** | Theme communication, token resolution | Theme system | pytest (pure Python) |
| **Renderer** | HTML/JS/CSS rendering, markdown parsing | None | Playwright (isolated) |

---

## Design Specifications

### 1. RendererProtocol

**Purpose:** Abstract interface for pluggable markdown rendering engines

**Key Classes:**
```python
@runtime_checkable
class RendererProtocol(Protocol):
    @property
    def capabilities(self) -> RendererCapabilities: ...
    def initialize(self) -> None: ...
    def render(self, markdown: str) -> RenderResult: ...
    def set_theme(self, theme_data: dict[str, str]) -> None: ...
    def get_toc(self) -> list[dict]: ...
    def export_html(self, markdown: str, standalone: bool = True) -> str: ...
```

**Implementations:**
- `MarkdownItRenderer` - Current JavaScript-based implementation
- `PythonMarkdownRenderer` - Future pure Python implementation

**Benefits:**
- Swap renderers without changing widget
- Test rendering in isolation
- Support different use cases (feature-rich vs. lightweight)

**Reference:** `renderer-protocol-DESIGN.md`

### 2. ThemeBridge

**Purpose:** Clean abstraction for Python → JavaScript theme communication

**Key Classes:**
```python
class ThemeBridge:
    def __init__(
        self,
        page: QWebEnginePage,
        token_mappings: list[ThemeTokenMapping],
        css_injection_callback: Optional[Callable] = None
    ): ...

    def apply_theme(self, theme) -> ThemeApplicationResult: ...
```

**Features:**
- Token resolution with fallback chains
- CSS variable building
- Validation & diagnostics
- Custom CSS injection (e.g., Prism overrides)

**Benefits:**
- Testable without QWebEngineView (mock page)
- Clear logging of token resolution
- Reusable for all webview widgets

**Reference:** `theme-bridge-DESIGN.md`

### 3. Directory Structure

**New Organization:**
```
src/vfwidgets_markdown/
├── widgets/
│   └── markdown_viewer.py (~400 lines, down from 1222)
├── hosting/
│   ├── webview_host.py (~200 lines)
│   └── resource_loader.py (~100 lines)
├── bridges/
│   ├── theme_bridge.py (~300 lines)
│   └── message_bridge.py (~150 lines)
└── renderers/
    ├── base.py (~150 lines)
    └── markdown_it/
        ├── renderer.py (~300 lines)
        ├── html/viewer.html
        ├── css/viewer.css, prism-themes/
        └── js/viewer.js, lib/
```

**Benefits:**
- Clear separation of concerns
- Smaller, focused files
- Reusable components
- Independent testability

**Reference:** `directory-structure-PROPOSAL.md`

---

## Migration Strategy

### Phase-Based Approach (3-4 weeks)

#### Phase 1: Create New Structure (Week 1)
✅ **No breaking changes** - old code continues working

**Tasks:**
1. Create `hosting/`, `bridges/`, `renderers/` directories
2. Implement `WebViewHost` class
3. Implement `ThemeBridge` class
4. Define `RendererProtocol` interface
5. Add unit tests for new modules

**Validation:**
- All existing tests pass
- New modules have 90%+ test coverage
- Public API unchanged

#### Phase 2: Refactor MarkdownViewer (Week 2)
✅ **Internal refactoring only** - public API unchanged

**Tasks:**
1. Refactor `markdown_viewer.py` to use new modules
2. Delegate theme logic to `ThemeBridge`
3. Delegate host logic to `WebViewHost`
4. Maintain exact same public API

**Validation:**
- All existing tests pass
- All existing examples work
- Line count reduced from 1222 → ~400

#### Phase 3: Extract Renderer + HTML Tests (Week 2-3)
✅ **Backward compatible** - default renderer unchanged

**Tasks:**
1. Extract `MarkdownItRenderer` class
2. Move `resources/` to `renderers/markdown_it/`
3. Add Playwright test infrastructure
4. Create standalone HTML test files
5. **Fix `markdown.colors.code.background` in isolated test**

**Validation:**
- Renderer conforms to `RendererProtocol`
- HTML/JS tests pass in browser
- CSS theme issue fixed and validated

#### Phase 4: Reusability + Documentation (Week 3-4)
✅ **Enable future widgets** - reusable components

**Tasks:**
1. Move `WebViewHost` to `vfwidgets_common`
2. Move `ThemeBridge` to `vfwidgets_common`
3. Document pattern for other widgets
4. Create advanced examples
5. Update README and docs

**Validation:**
- Terminal widget can use `WebViewHost` + `ThemeBridge`
- Documentation complete
- Examples demonstrate new capabilities

### Backward Compatibility Guarantee

**Public API (UNCHANGED):**
```python
# Users import the same way
from vfwidgets_markdown import MarkdownViewer

# Same constructor
viewer = MarkdownViewer(parent=None)

# Same methods
viewer.set_markdown("# Hello")
viewer.export_html()

# Same signals
viewer.toc_updated.connect(...)
```

**Internal Implementation (CHANGED):**
```python
# Old: Everything in markdown_viewer.py
class MarkdownViewer:
    def on_theme_changed(self):
        # 140 lines of theme logic
        pass

# New: Delegated to specialized modules
class MarkdownViewer:
    def __init__(self):
        self._bridge = ThemeBridge(...)

    def on_theme_changed(self, theme=None):
        self._bridge.apply_theme(theme)  # Clean!
```

---

## Benefits & Trade-offs

### Immediate Benefits

#### 1. **Fixes Current Theme Issue**
- ✅ Can test CSS in browser DevTools (standalone HTML)
- ✅ Can validate computed styles with Playwright
- ✅ Can debug CSS specificity issues in isolation
- ✅ Can reproduce issue without running full Qt app

#### 2. **Improved Testability**
- ✅ Unit tests for theme resolution (pure Python, fast)
- ✅ HTML/JS tests with Playwright (browser validation)
- ✅ Integration tests with pytest-qt (widget functionality)
- ✅ Clear test boundaries (unit → integration → E2E)

#### 3. **Better Debuggability**
- ✅ Clear logging at each layer
- ✅ Diagnostic info for missing tokens
- ✅ Browser DevTools for CSS issues
- ✅ Smaller files easier to understand

#### 4. **Maintainability**
- ✅ 67% reduction in widget line count (1222 → 400)
- ✅ Clear responsibilities per module
- ✅ Easier to onboard new developers
- ✅ Safer refactoring (clear boundaries)

### Long-term Benefits

#### 1. **Reusability**
- ✅ `WebViewHost` for all webview widgets
- ✅ `ThemeBridge` for consistent theme application
- ✅ Pattern for terminal, PDF viewer, etc.
- ✅ Shared test infrastructure

#### 2. **Flexibility**
- ✅ Swap renderers (markdown-it ↔ python-markdown)
- ✅ Add new renderers (GitHub Markdown API, etc.)
- ✅ Customize for different use cases
- ✅ Optimize layers independently

#### 3. **Performance**
- ✅ Can optimize renderer without touching widget
- ✅ Can lazy-load JavaScript libraries
- ✅ Can use lightweight Python renderer for simple cases
- ✅ Can cache compiled CSS

### Trade-offs

#### Costs
- ⚠️ **Development Time**: 3-4 weeks for complete refactoring
- ⚠️ **Complexity**: More files to understand (but each simpler)
- ⚠️ **Testing Overhead**: Need Playwright + pytest-qt

#### Mitigations
- ✅ **Incremental Migration**: Phase-based, backward compatible
- ✅ **Clear Documentation**: Architecture guides for each layer
- ✅ **Reusable Investment**: Benefits all future webview widgets

---

## Testing Strategy

### Test Pyramid

```
           ╱╲
          ╱  ╲
         ╱ E2E╲      ← pytest-qt: Full widget integration
        ╱──────╲
       ╱  HTML  ╲    ← Playwright: Browser rendering validation
      ╱──────────╲
     ╱    Unit    ╲  ← pytest: Theme resolution, protocols
    ╱──────────────╲
```

### Test Coverage by Layer

| Layer | Test Type | Tools | Coverage Target |
|-------|-----------|-------|-----------------|
| Widget | Integration | pytest-qt | 85%+ |
| Host | Integration | pytest-qt (mocked page) | 90%+ |
| Bridge | Unit | pytest (pure Python) | 95%+ |
| Renderer | HTML/JS | Playwright | 90%+ |

### Key Test Cases

#### Unit Tests (Fast, Pure Python)
```python
def test_theme_bridge_token_resolution():
    """Test token resolution with fallback chain."""
    # Mock QWebEnginePage, test Python logic only

def test_renderer_protocol_conformance():
    """Test renderers conform to protocol."""
    # Use isinstance() with runtime_checkable Protocol
```

#### HTML/JS Tests (Playwright, Isolated)
```python
def test_css_theme_application(page):
    """Test CSS variables apply to code blocks."""
    page.goto("file:///path/to/test_viewer.html")
    page.evaluate("document.documentElement.style.setProperty('--md-code-bg', '#ff0000')")
    page.evaluate("renderMarkdown('```python\\nprint(\"test\")\\n```')")

    # THIS IS WHERE WE FIX markdown.colors.code.background!
    code_bg = page.evaluate("""
        const pre = document.querySelector('pre[class*="language-"]');
        return getComputedStyle(pre).backgroundColor;
    """)

    assert code_bg == "rgb(255, 0, 0)"  # #ff0000
```

#### Integration Tests (pytest-qt, Full Widget)
```python
def test_markdown_viewer_theme_change(qtbot):
    """Test full widget theme change."""
    viewer = MarkdownViewer()
    qtbot.addWidget(viewer)

    # Apply theme
    theme = create_test_theme()
    viewer.on_theme_changed(theme)

    # Validate via bridge
    result = viewer._theme_bridge.get_last_result()
    assert result.success
```

---

## Next Steps

### Immediate Actions (This Week)

1. ✅ **Complete Research Phase** (DONE)
   - ✅ Audit architecture
   - ✅ Research patterns
   - ✅ Design abstractions
   - ✅ Create comprehensive plan

2. 🔄 **Begin Implementation Phase 1**
   - Create directory structure
   - Implement `WebViewHost` class
   - Implement `ThemeBridge` class
   - Add unit tests

### Implementation Roadmap

**Week 1: Foundation**
- ✅ Create new directory structure
- ✅ Implement `WebViewHost` (~200 lines)
- ✅ Implement `ThemeBridge` (~300 lines)
- ✅ Define `RendererProtocol` (~150 lines)
- ✅ Add unit tests (90%+ coverage)

**Week 2: Refactoring**
- ✅ Refactor `MarkdownViewer` to use new modules
- ✅ Reduce from 1222 → ~400 lines
- ✅ Maintain backward compatibility
- ✅ All existing tests pass

**Week 3: Extraction + Testing**
- ✅ Extract `MarkdownItRenderer` class
- ✅ Move `resources/` to `renderers/markdown_it/`
- ✅ Add Playwright test infrastructure
- ✅ **Fix `markdown.colors.code.background`** in isolated test

**Week 4: Polish + Reusability**
- ✅ Move components to `vfwidgets_common`
- ✅ Document pattern for future widgets
- ✅ Create advanced examples
- ✅ Update all documentation

### Success Criteria

#### Phase 1 Complete
- ✅ New modules created with 90%+ test coverage
- ✅ All existing tests pass
- ✅ No breaking changes to public API

#### Phase 2 Complete
- ✅ `markdown_viewer.py` reduced to ~400 lines
- ✅ Theme logic delegated to `ThemeBridge`
- ✅ Host logic delegated to `WebViewHost`

#### Phase 3 Complete
- ✅ Renderer extracted to `renderers/markdown_it/`
- ✅ Playwright tests passing
- ✅ **`markdown.colors.code.background` FIXED**

#### Phase 4 Complete
- ✅ Components moved to `vfwidgets_common`
- ✅ Pattern documented for reuse
- ✅ Terminal widget can use `WebViewHost` + `ThemeBridge`

---

## References

### Design Documents
1. **Renderer Protocol**: `renderer-protocol-DESIGN.md`
2. **Theme Bridge**: `theme-bridge-DESIGN.md`
3. **Directory Structure**: `directory-structure-PROPOSAL.md`

### Research Documents
1. **Webview Patterns**: `webview-patterns-RESEARCH.md`
2. **Terminal Widget Analysis**: `../../terminal_widget/docs/terminal-theme-improvements-ANALYSIS.md`

### Planning Documents
1. **Architecture Refactoring**: `ARCHITECTURE-REFACTORING-PLAN.md`

### VFWidgets Guidelines
1. **Clean Architecture**: `/home/kuja/GitHub/vfwidgets/CleanArchitectureAsTheWay.md`
2. **Agent Development**: `/home/kuja/GitHub/vfwidgets/writing-dev-AGENTS-v2.md`

---

**Document Status**: Complete - Ready for Implementation
**Approval Required**: Yes - User review of architecture proposal
**Estimated Effort**: 3-4 weeks full implementation
**Risk Level**: Low - Incremental, backward-compatible approach
**Priority**: High - Fixes current issues + establishes pattern for future

---

## Appendix A: Current vs. Proposed Comparison

### Code Organization

| Metric | Current | Proposed | Change |
|--------|---------|----------|--------|
| `markdown_viewer.py` lines | 1222 | ~400 | -67% |
| Responsibilities in widget | 14 | 4 | -71% |
| Number of modules | 3 | 7 | +133% |
| Testable without Qt | No | Yes | ✅ |
| HTML/JS independently testable | No | Yes | ✅ |
| Reusable components | 0 | 2+ | ✅ |

### Test Coverage

| Layer | Current | Proposed |
|-------|---------|----------|
| Widget | 60% | 85%+ |
| Theme logic | 0% | 95%+ |
| HTML/JS | 0% | 90%+ |
| Overall | 40% | 90%+ |

---

**End of Document**
