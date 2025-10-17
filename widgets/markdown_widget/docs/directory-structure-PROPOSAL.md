# Directory Structure Proposal - Refactored Architecture

## Overview

This document proposes a new directory structure for the markdown widget that separates concerns into distinct modules: hosting (Qt integration), bridges (Python↔JS communication), and renderers (HTML/JS/CSS rendering).

**Goals:**
- Clear separation of concerns
- Independent testability of each layer
- Reusable components for other webview widgets
- Maintain backward compatibility

---

## Current Structure (Before Refactoring)

```
markdown_widget/
├── pyproject.toml
├── README.md
├── src/
│   └── vfwidgets_markdown/
│       ├── __init__.py
│       ├── models/
│       │   ├── document.py (190 lines) - Document model
│       │   ├── events.py - Event types
│       │   └── protocols.py - Observer protocol
│       ├── controllers/
│       │   └── editor_controller.py (198 lines) - Editor logic
│       ├── widgets/
│       │   ├── markdown_viewer.py (1222 lines) ⚠️ MONOLITHIC
│       │   ├── editor_widget.py - Editor UI
│       │   ├── text_editor.py - Text input
│       │   └── toc_view.py - Table of contents
│       └── resources/
│           ├── viewer.html - HTML template
│           ├── css/
│           │   ├── viewer.css - Custom styles
│           │   └── prism-themes/ - Syntax highlighting themes
│           └── js/
│               ├── viewer.js (691 lines) - Rendering engine
│               ├── markdown-it.min.js - Parser
│               ├── prism.min.js - Syntax highlighter
│               └── mermaid.min.js - Diagrams
├── tests/
│   ├── test_document.py
│   ├── test_editor_controller.py
│   └── test_markdown_viewer.py
└── examples/
    ├── 01_basic_usage.py
    └── 02_advanced_features.py
```

**Problems:**
- `markdown_viewer.py` has 14 responsibilities (1222 lines)
- `resources/` mixes HTML/JS/CSS with no clear ownership
- No separation between Qt integration and rendering logic
- Can't test HTML/JS without full Qt application
- Can't swap renderer implementations

---

## Proposed Structure (After Refactoring)

```
markdown_widget/
├── pyproject.toml
├── README.md
├── src/
│   └── vfwidgets_markdown/
│       ├── __init__.py (PUBLIC API - unchanged for compatibility)
│       │
│       ├── models/ (UNCHANGED - pure data models)
│       │   ├── document.py
│       │   ├── events.py
│       │   └── protocols.py
│       │
│       ├── controllers/ (UNCHANGED - business logic)
│       │   └── editor_controller.py
│       │
│       ├── widgets/ (REDUCED - only widget logic)
│       │   ├── markdown_viewer.py (~400 lines, down from 1222)
│       │   │   # Responsibilities:
│       │   │   # - QWebEngineView lifecycle
│       │   │   # - ThemedWidget integration
│       │   │   # - Signal/slot connections
│       │   │   # - Coordinate host, bridge, renderer
│       │   ├── editor_widget.py
│       │   ├── text_editor.py
│       │   └── toc_view.py
│       │
│       ├── hosting/ (NEW - Qt/webview integration)
│       │   ├── __init__.py
│       │   ├── webview_host.py (~200 lines)
│       │   │   # Responsibilities:
│       │   │   # - QWebEngineView/Page setup
│       │   │   # - QWebChannel management
│       │   │   # - Resource loading (HTML/CSS/JS)
│       │   │   # - Page lifecycle events
│       │   │   # - Transparency configuration
│       │   └── resource_loader.py (~100 lines)
│       │       # Responsibilities:
│       │       # - Load HTML/CSS/JS from package resources
│       │       # - Generate QUrl for local files
│       │       # - Content Security Policy setup
│       │
│       ├── bridges/ (NEW - Python ↔ JavaScript communication)
│       │   ├── __init__.py
│       │   ├── theme_bridge.py (~300 lines)
│       │   │   # Responsibilities:
│       │   │   # - Theme token resolution with fallbacks
│       │   │   # - CSS variable building
│       │   │   # - CSS injection via JavaScript
│       │   │   # - Theme validation and diagnostics
│       │   └── message_bridge.py (~150 lines)
│       │       # Responsibilities:
│       │       # - General Python → JS message passing
│       │       # - JS → Python callback handling
│       │       # - QWebChannel wrapper
│       │       # - Type-safe communication
│       │
│       ├── renderers/ (NEW - pluggable rendering engines)
│       │   ├── __init__.py
│       │   ├── base.py (~150 lines)
│       │   │   # RendererProtocol (abstract interface)
│       │   │   # RendererCapabilities (feature flags)
│       │   │   # RenderResult (data class)
│       │   │
│       │   ├── markdown_it/ (CURRENT IMPLEMENTATION - refactored)
│       │   │   ├── __init__.py
│       │   │   ├── renderer.py (~300 lines)
│       │   │   │   # MarkdownItRenderer class
│       │   │   │   # Coordinates HTML/JS resources
│       │   │   │   # Implements RendererProtocol
│       │   │   │
│       │   │   ├── html/
│       │   │   │   └── viewer.html (MOVED from resources/)
│       │   │   │       # Clean HTML template
│       │   │   │       # No inline styles/scripts
│       │   │   │
│       │   │   ├── css/
│       │   │   │   ├── viewer.css (MOVED from resources/css/)
│       │   │   │   │   # Base markdown styles
│       │   │   │   │   # Uses CSS variables
│       │   │   │   └── prism-themes/ (MOVED from resources/css/)
│       │   │   │       # Syntax highlighting themes
│       │   │   │
│       │   │   └── js/
│       │   │       ├── viewer.js (MOVED from resources/js/)
│       │   │       │   # Rendering engine (691 lines)
│       │   │       │   # NOW TESTABLE INDEPENDENTLY
│       │   │       │
│       │   │       ├── plugins/
│       │   │       │   # markdown-it plugins (organized)
│       │   │       │
│       │   │       └── lib/
│       │   │           ├── markdown-it.min.js
│       │   │           ├── prism.min.js
│       │   │           └── mermaid.min.js
│       │   │
│       │   └── python_markdown/ (FUTURE - pure Python renderer)
│       │       ├── __init__.py
│       │       └── renderer.py
│       │           # PythonMarkdownRenderer (python-markdown library)
│       │           # No JavaScript required
│       │           # Faster startup
│       │
│       └── utils/ (NEW - shared utilities)
│           ├── __init__.py
│           └── colors.py
│               # Color parsing/blending utilities
│               # Hex → RGB conversion
│               # Luminance calculation
│
├── tests/
│   ├── unit/ (ORGANIZED - fast pure Python tests)
│   │   ├── test_document.py (existing)
│   │   ├── test_editor_controller.py (existing)
│   │   ├── test_theme_bridge.py (NEW - test token resolution)
│   │   ├── test_resource_loader.py (NEW - test resource loading)
│   │   └── test_renderer_protocol.py (NEW - test protocol conformance)
│   │
│   ├── integration/ (NEW - Qt integration tests)
│   │   ├── test_markdown_viewer.py (existing, refactored)
│   │   ├── test_webview_host.py (NEW - test host setup)
│   │   └── test_full_widget.py (NEW - end-to-end tests)
│   │
│   └── html/ (NEW - JavaScript/HTML tests with Playwright)
│       ├── conftest.py (Playwright fixtures)
│       ├── test_markdown_rendering.py
│       │   # Test viewer.js in isolation
│       │   # Test markdown-it rendering
│       │   # Test Prism syntax highlighting
│       │
│       ├── test_theme_application.py
│       │   # Test CSS variable injection
│       │   # Test Prism override CSS
│       │   # Test computed styles
│       │   # ✅ FIX markdown.colors.code.background HERE
│       │
│       ├── test_mermaid_diagrams.py
│       │   # Test diagram rendering
│       │
│       └── fixtures/
│           ├── test_viewer.html (standalone test HTML)
│           └── test_styles.css (test CSS)
│
└── examples/
    ├── 01_basic_usage.py (UNCHANGED)
    ├── 02_advanced_features.py (UNCHANGED)
    ├── 03_custom_renderer.py (NEW - show Python renderer)
    └── 04_theme_validation.py (NEW - show theme diagnostics)
```

---

## Module Responsibilities Breakdown

### Layer 1: Widget (User-Facing Qt Interface)

**File**: `widgets/markdown_viewer.py` (~400 lines, down from 1222)

**Responsibilities:**
- QWebEngineView lifecycle management
- ThemedWidget integration (`on_theme_changed()`)
- Public API (`set_markdown()`, signals, etc.)
- Coordinate host, bridge, renderer components

**Dependencies:**
- `hosting.WebViewHost`
- `bridges.ThemeBridge`
- `renderers.RendererProtocol`

**Example:**
```python
class MarkdownViewer(ThemedWidget, QWebEngineView):
    def __init__(self, renderer: Optional[RendererProtocol] = None):
        self._host = WebViewHost(self)
        self._bridge = ThemeBridge(self._host.page, token_mappings=...)
        self._renderer = renderer or MarkdownItRenderer(self._host.page)
```

---

### Layer 2: Host (Qt/WebView Integration)

**File**: `hosting/webview_host.py` (~200 lines)

**Responsibilities:**
- QWebEngineView/Page setup
- QWebChannel initialization
- Transparency configuration
- Page lifecycle events (`loadFinished`, etc.)
- Content Security Policy

**No Dependencies on:**
- Theme system
- Rendering logic
- Business logic

**Reusable by:**
- Terminal widget
- PDF viewer widget
- Any future webview widget

---

### Layer 3: Bridge (Python ↔ JavaScript Communication)

**File**: `bridges/theme_bridge.py` (~300 lines)

**Responsibilities:**
- Resolve theme tokens with fallback chain
- Build CSS custom properties
- Inject CSS via `runJavaScript()`
- Validate theme completeness
- Diagnostic logging

**No Dependencies on:**
- Widget logic
- Renderer implementation

**Testable:**
- Mock `QWebEnginePage`
- Test token resolution in isolation
- Test CSS generation without browser

---

**File**: `bridges/message_bridge.py` (~150 lines)

**Responsibilities:**
- General Python → JS messaging
- JS → Python callback handling
- QWebChannel wrapper
- Type-safe communication

---

### Layer 4: Renderer (HTML/JS/CSS Rendering)

**File**: `renderers/base.py` (~150 lines)

**Defines:**
- `RendererProtocol` (abstract interface)
- `RendererCapabilities` (feature flags)
- `RenderResult` (data class)

---

**File**: `renderers/markdown_it/renderer.py` (~300 lines)

**Responsibilities:**
- Implement `RendererProtocol`
- Load HTML/CSS/JS resources
- Coordinate markdown-it rendering
- Extract TOC
- Export standalone HTML

**All HTML/JS/CSS files live in `renderers/markdown_it/`:**
- `html/viewer.html` - Template
- `css/viewer.css` - Styles
- `js/viewer.js` - Rendering engine
- `js/lib/` - Third-party libraries

**Benefits:**
- Self-contained renderer
- Can extract to separate package
- Testable with Playwright in isolation

---

## Testing Strategy

### Unit Tests (No Qt Required)

```bash
# Fast pure Python tests
pytest tests/unit/ -v

# Test cases:
# - Theme token resolution (ThemeBridge)
# - Resource loading (ResourceLoader)
# - Protocol conformance (RendererProtocol)
# - Color utilities
```

### Integration Tests (pytest-qt)

```bash
# Qt integration tests
pytest tests/integration/ -v

# Test cases:
# - WebViewHost setup
# - Full MarkdownViewer widget
# - Theme application end-to-end
```

### HTML/JS Tests (Playwright)

```bash
# JavaScript rendering tests
pytest tests/html/ -v

# Test cases:
# - markdown-it rendering in isolation
# - CSS variable injection
# - Prism syntax highlighting
# - Mermaid diagrams
# - ✅ FIX: markdown.colors.code.background visual application
```

**Key Benefit:** Can debug CSS issues in browser DevTools without running full Qt app!

---

## Migration Strategy

### Phase 1: Create New Structure (Week 1)
✅ **No breaking changes** - Old code still works

1. Create `hosting/`, `bridges/`, `renderers/` directories
2. Implement `WebViewHost` class
3. Implement `ThemeBridge` class
4. Implement `RendererProtocol` interface
5. Add unit tests for new modules

### Phase 2: Refactor MarkdownViewer (Week 2)
✅ **Internal refactoring only** - Public API unchanged

1. Refactor `markdown_viewer.py` to use new modules
2. Move theme logic to `ThemeBridge`
3. Move host logic to `WebViewHost`
4. Maintain exact same public API

### Phase 3: Extract Renderer (Week 2-3)
✅ **Backward compatible** - Default renderer unchanged

1. Extract `MarkdownItRenderer` class
2. Move `resources/` to `renderers/markdown_it/`
3. Add Playwright tests for HTML/JS
4. Fix CSS issues in isolated tests

### Phase 4: Polish & Reusability (Week 3-4)
✅ **Enable future widgets** - Reusable components

1. Move `WebViewHost` to `vfwidgets_common`
2. Move `ThemeBridge` to `vfwidgets_common`
3. Document pattern for other widgets
4. Add examples and guides

---

## Backward Compatibility

### Public API (UNCHANGED)

```python
# Users import the same way
from vfwidgets_markdown import MarkdownViewer

# Same constructor signature
viewer = MarkdownViewer(parent=None)

# Same methods
viewer.set_markdown("# Hello")
viewer.export_html()

# Same signals
viewer.toc_updated.connect(...)
```

### Internal Structure (CHANGED)

**Old:**
```python
# Everything in markdown_viewer.py
class MarkdownViewer:
    def on_theme_changed(self):
        # 140 lines of theme logic here
        pass
```

**New:**
```python
# Delegated to specialized modules
class MarkdownViewer:
    def __init__(self):
        self._bridge = ThemeBridge(...)

    def on_theme_changed(self, theme=None):
        self._bridge.apply_theme(theme)  # Clean!
```

---

## File Size Comparison

### Before Refactoring:
- `markdown_viewer.py`: **1222 lines** ⚠️
- `viewer.js`: 691 lines (untestable without Qt)

### After Refactoring:
- `markdown_viewer.py`: **~400 lines** ✅ (67% reduction)
- `hosting/webview_host.py`: ~200 lines (reusable)
- `bridges/theme_bridge.py`: ~300 lines (reusable, testable)
- `renderers/markdown_it/renderer.py`: ~300 lines (pluggable)
- `renderers/markdown_it/js/viewer.js`: 691 lines (testable with Playwright!)

**Total lines:** ~1891 lines (vs. 1913 before)
**BUT:** Organized, separated, testable, reusable!

---

## Benefits

### Immediate
- ✅ Clear separation of concerns
- ✅ Testable modules (unit tests without Qt)
- ✅ Debuggable (browser DevTools for HTML/JS)
- ✅ Maintainable (smaller, focused files)

### Long-term
- ✅ Reusable components (WebViewHost, ThemeBridge)
- ✅ Pluggable renderers (markdown-it, python-markdown, etc.)
- ✅ Pattern for future widgets (terminal, PDF, etc.)
- ✅ Better performance (can optimize layers independently)

---

## Next Steps

1. ✅ Create directory structure
2. ✅ Implement `WebViewHost` class
3. ✅ Implement `ThemeBridge` class
4. ✅ Add unit tests
5. ✅ Refactor `MarkdownViewer` to use new modules
6. ✅ Add Playwright tests
7. ✅ Fix `markdown.colors.code.background` in isolated test
8. ✅ Extract to `vfwidgets_common` for reusability

---

**Status**: Proposal Complete - Ready for Implementation
**Estimated Effort**: 3-4 weeks for complete refactoring
**Risk**: Low - Incremental approach with backward compatibility
