# vfwidgets-webview Implementation Roadmap

**Goal**: Create clean, reusable browser widget with theme integration
**MVP Target**: Single-page browser (like old-school browsers)
**Timeline**: 2 weeks

---

## Overview

We're following **Option C** approach:
- **vfwidgets-webview**: Lightweight, reusable widget (this)
- **ViloWeb**: Advanced features built on top (extensions, security, automation)

---

## Phase 0.1: Core Components (Days 1-4)

### Day 1-2: WebPage & WebView

**Files to Create**:
```
src/vfwidgets_webview/
├── webpage.py         # Custom QWebEnginePage
└── webview.py         # QWebEngineView wrapper
```

**WebPage (webpage.py)**:
```python
class WebPage(QWebEnginePage):
    """Custom web page with educational features."""

    # Features:
    - JavaScript console message handling
    - Certificate error handling
    - User agent customization
    - Educational comments explaining each method
```

**WebView (webview.py)**:
```python
class WebView(QWidget):
    """Wrapper around QWebEngineView."""

    # Features:
    - Clean API (load, back, forward, reload)
    - Signal forwarding
    - Theme integration hooks
    - Hides QWebEngine complexity
```

**Test**: Can load https://example.com

---

### Day 3-4: NavigationBar

**File to Create**:
```
src/vfwidgets_webview/
└── navigation_bar.py
```

**NavigationBar**:
```python
class NavigationBar(QWidget):
    """Navigation controls and URL bar."""

    Components:
    - BackButton (◄)
    - ForwardButton (►)
    - ReloadButton (⟲)
    - HomeButton (🏠)
    - URLBar (QLineEdit)
    - ProgressBar (loading indicator)

    Signals:
    - back_clicked
    - forward_clicked
    - reload_clicked
    - home_clicked
    - url_submitted(str)
```

**Layout**:
```
┌────────────────────────────────────────────┐
│ [◄] [►] [⟲] [🏠]  https://example.com     │
├────────────────────────────────────────────┤
│ ████████────────── 45%                     │
└────────────────────────────────────────────┘
```

**Test**: Buttons clickable, URL bar functional

---

### Day 4: BrowserWidget Integration

**File to Create**:
```
src/vfwidgets_webview/
└── browser_widget.py
```

**BrowserWidget**:
```python
class BrowserWidget(QWidget):
    """Complete browser: NavigationBar + WebView."""

    Responsibilities:
    - Compose NavigationBar + WebView
    - Wire signals between components
    - Provide public API
    - Forward important signals
```

**Signal Flow**:
```
User clicks Back button
  → NavigationBar.back_clicked
  → BrowserWidget._on_back_clicked()
  → WebView.back()
  → QWebEngineView.back()
```

**Test**: Can navigate, go back, go forward

---

## Phase 0.2: Theme Integration (Days 5-6)

### Theme System Integration

**Update Files**:
- `browser_widget.py` - Add ThemedWidget mixin
- `navigation_bar.py` - Add theme_config
- All components - Apply theme colors

**Theme Configuration**:
```python
theme_config = {
    "navbar.background": "editor.background",
    "navbar.foreground": "editor.foreground",
    "urlbar.background": "input.background",
    "urlbar.foreground": "input.foreground",
    "urlbar.border": "input.border",
    "urlbar.border_focus": "focusBorder",
    "button.background": "button.background",
    "button.hover": "button.hoverBackground",
    "progress.background": "progressBar.background",
    "progress.foreground": "progressBar.foreground",
}
```

**Test Cases**:
- Widget looks good in dark theme
- Widget looks good in light theme
- Theme switching works live
- All text readable in both themes
- Focus indicators visible

---

## Phase 0.3: Polish & Examples (Days 7-10)

### Day 7-8: Polish

**Features to Add**:
1. URL autocomplete (simple history-based)
2. Loading indicators (spinner + progress)
3. Favicon display
4. Error pages (for failed loads)
5. Keyboard shortcuts (Ctrl+L for URL bar, etc.)

**File Updates**:
- `navigation_bar.py` - Add autocomplete
- `webview.py` - Add error handling
- `browser_widget.py` - Add shortcuts

### Day 9-10: Progressive Examples

**Create Examples**:
```
examples/
├── 01_minimal_browser.py           # ~20 lines
├── 02_themed_browser.py            # ~40 lines
├── 03_navigation_signals.py        # ~50 lines
├── 04_custom_styling.py            # ~60 lines
├── 05_single_page_browser.py       # ~70 lines (MVP!)
├── 06_standalone_components.py     # ~40 lines
└── 07_embedding_in_app.py          # ~80 lines
```

**Example Progression**:
1. Minimal - Show simplest usage
2. Themed - Add theme system
3. Signals - Handle events
4. Styling - Custom colors
5. **MVP - Complete single-page browser** ⭐
6. Components - Use NavigationBar alone
7. Embedding - In larger application

---

## Phase 0.4: Documentation (Days 11-14)

### Documentation Files to Create

**API Documentation**:
```
docs/
├── SPECIFICATION.md               ✅ Done
├── IMPLEMENTATION-ROADMAP.md      ✅ This file
├── API.md                         # Public API reference
├── THEME-INTEGRATION.md           # Theme system guide
├── THEME-STUDIO.md                # Using in theme-studio
└── DEVELOPMENT.md                 # Contributing guide
```

### Testing Documentation

**Create**:
```
tests/
├── test_webpage.py                # WebPage tests
├── test_webview.py                # WebView tests
├── test_navigation_bar.py         # NavigationBar tests
├── test_browser_widget.py         # BrowserWidget tests
└── test_theme_integration.py      # Theme tests
```

---

## Implementation Order

### Week 1: Core Widget

**Monday-Tuesday**: WebPage + WebView
- Create `webpage.py`
- Create `webview.py`
- Can load web pages
- Educational comments

**Wednesday-Thursday**: NavigationBar
- Create `navigation_bar.py`
- All buttons working
- URL bar functional
- Progress indicator

**Friday**: BrowserWidget
- Create `browser_widget.py`
- Integrate components
- Wire signals
- Public API

**Weekend**: Theme Integration
- Add ThemedWidget mixin
- Define theme_config
- Test dark/light themes

### Week 2: Polish & Examples

**Monday**: Polish Features
- URL autocomplete
- Loading indicators
- Error handling

**Tuesday-Wednesday**: Progressive Examples
- Create all 7 examples
- Test each one
- Add inline comments

**Thursday**: Documentation
- API.md
- THEME-INTEGRATION.md
- THEME-STUDIO.md

**Friday**: Testing & Release
- Write unit tests
- Integration tests
- Tag v0.1.0

---

## Design Patterns Used

### 1. Composite Pattern
```python
BrowserWidget
├── NavigationBar (component)
└── WebView (component)
```

### 2. Wrapper Pattern
```python
WebView wraps QWebEngineView
# Provides cleaner API, hides Qt complexity
```

### 3. Signal/Slot Communication
```python
# Components communicate via signals
navbar.url_submitted.connect(webview.load)
webview.title_changed.connect(navbar.set_title)
```

### 4. Theme Mixin Pattern
```python
class BrowserWidget(ThemedWidget):
    theme_config = {...}
```

### 5. Delegation Pattern
```python
# BrowserWidget delegates to components
def back(self):
    self._webview.back()
```

---

## API Design Philosophy

### Hide Complexity
```python
# GOOD: Simple
browser.navigate("https://example.com")

# BAD: Exposing internals
browser._webview._engine_view.page().setUrl(...)
```

### Minimal Surface
Only expose what users need:
- ✅ `navigate()`, `back()`, `forward()`, `reload()`
- ✅ `url()`, `title()`
- ✅ Essential signals
- ❌ QWebEngine internals

### Educational Code
```python
def navigate(self, url: str) -> None:
    """Navigate to URL.

    This method demonstrates:
    1. URL validation
    2. Scheme detection (add https:// if missing)
    3. Signal emission
    4. QWebEngineView interaction

    Args:
        url: URL to navigate to

    Example:
        >>> browser.navigate("example.com")  # Auto-adds https://
        >>> browser.navigate("https://example.com")  # Direct
    """
```

---

## Success Criteria

### MVP Complete When:
- ✅ Can load web pages
- ✅ Full navigation (back, forward, reload, home)
- ✅ URL bar with basic autocomplete
- ✅ Loading indicators visible
- ✅ Theme integration working (dark/light)
- ✅ Example 05 runs (single-page browser)
- ✅ Works in theme-studio
- ✅ Documentation complete
- ✅ Tests passing

### Quality Gates:
- All examples run without errors
- Dark theme: all elements visible
- Light theme: all elements visible
- Can browse 10+ real websites
- No crashes or freezes
- Code fully commented
- API documented

---

## After MVP: Future Enhancements

**Not in MVP, but can add later**:
- URL history persistence
- Bookmark support
- Download handling UI
- Print support
- Find in page
- Zoom controls
- Custom context menus

**These belong in applications built on this widget**:
- Tab management → Use ChromeTabbedWindow
- Extensions → ViloWeb
- Security testing → ViloWeb
- Automation API → ViloWeb

---

## Getting Started

### For Developers:

1. **Start with WebPage**:
   ```bash
   cd widgets/webview_widget/src/vfwidgets_webview
   # Create webpage.py
   ```

2. **Then WebView**:
   ```bash
   # Create webview.py
   ```

3. **Test Early**:
   ```bash
   cd widgets/webview_widget
   python -c "from vfwidgets_webview import WebView; print('Success!')"
   ```

4. **Follow Roadmap**: Day by day as outlined above

### For Users (After Release):

1. **Install**:
   ```bash
   pip install vfwidgets-webview
   ```

2. **Try Examples**:
   ```bash
   python examples/01_minimal_browser.py
   python examples/05_single_page_browser.py
   ```

3. **Read Docs**:
   - `docs/SPECIFICATION.md` - Complete spec
   - `docs/API.md` - API reference
   - `docs/THEME-INTEGRATION.md` - Theming guide

---

## Questions?

- **Scope question**: See SPECIFICATION.md section 1.3 (Non-Goals)
- **API question**: See docs/API.md (after it's created)
- **Theme question**: See docs/THEME-INTEGRATION.md (after it's created)
- **Implementation question**: Follow this roadmap day by day

Ready to build! 🚀
