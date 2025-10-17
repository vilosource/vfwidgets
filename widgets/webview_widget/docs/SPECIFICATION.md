# vfwidgets-webview - Technical Specification

**Version**: 0.1.0
**Status**: Design Phase
**Target**: MVP - Single Page Browser Widget

---

## Table of Contents

1. [Vision & Goals](#1-vision--goals)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Specifications](#3-component-specifications)
4. [Theme System Integration](#4-theme-system-integration)
5. [Public API Design](#5-public-api-design)
6. [Implementation Phases](#6-implementation-phases)
7. [Examples Progression](#7-examples-progression)
8. [Theme Studio Integration](#8-theme-studio-integration)
9. [Testing Strategy](#9-testing-strategy)

---

## 1. Vision & Goals

### 1.1 Vision

Create a **clean, reusable browser widget** that any PySide6 developer can embed in their applications. The widget should be:

- **Simple**: Easy to use with minimal code
- **Professional**: Production-quality implementation
- **Themed**: Full vfwidgets-theme integration
- **Educational**: Code serves as learning material
- **Extensible**: Foundation for advanced browsers (like ViloWeb)

### 1.2 Primary Goals

1. **Reusable Widget**: Can be embedded in any Qt application
2. **Minimal Scope**: Just browsing - no extensions, no security testing
3. **Theme Integration**: Seamless vfwidgets-theme support
4. **Clean API**: Hide QWebEngine complexity behind simple interface
5. **Educational Code**: Heavily commented, teaches QtWebEngine patterns
6. **Progressive Examples**: Learn by following 01_, 02_, 03_ examples
7. **MVP Target**: Single-page browser (like old-school browsers)

### 1.3 Non-Goals (Out of Scope)

These belong in ViloWeb or other applications built on this widget:

- ❌ Extension system
- ❌ Security testing features
- ❌ Browser automation API
- ❌ Tab management (use ChromeTabbedWindow separately)
- ❌ Bookmarks/History management
- ❌ Downloads manager
- ❌ Developer tools

**Philosophy**: This widget is a **foundation**. Build advanced features on top of it.

### 1.4 Success Metrics

**MVP Success** (Version 0.1.0):
- ✅ Can load and display web pages
- ✅ Full navigation (back, forward, reload, home)
- ✅ URL bar with autocomplete
- ✅ Loading indicators
- ✅ Theme system integration working
- ✅ 5 progressive examples completed
- ✅ Works in theme-studio for theme testing
- ✅ Single-page browser example (MVP demo)

---

## 2. Architecture Overview

### 2.1 Component Hierarchy

```
BrowserWidget (QWidget)
├── NavigationBar (QWidget)
│   ├── BackButton (QPushButton)
│   ├── ForwardButton (QPushButton)
│   ├── ReloadButton (QPushButton)
│   ├── HomeButton (QPushButton)
│   ├── URLBar (QLineEdit with QCompleter)
│   └── LoadingIndicator (QProgressBar)
└── WebView (QWidget wrapper)
    ├── QWebEngineView (actual web rendering)
    └── WebPage (QWebEnginePage)
```

### 2.2 Design Patterns

**1. Composite Pattern**
- `BrowserWidget` composes `NavigationBar` + `WebView`
- Can use components separately or together

**2. Wrapper Pattern**
- `WebView` wraps `QWebEngineView` to provide cleaner API
- `WebPage` extends `QWebEnginePage` for customization

**3. Signal/Slot Communication**
- Components communicate via Qt signals
- Loose coupling between NavigationBar and WebView

**4. Theme Mixin Pattern**
- Optional `ThemedWidget` mixin for theme integration
- Widget works with or without theme system

**5. Dependency Injection**
- Can provide custom WebPage implementation
- Can provide custom NavigationBar styling

### 2.3 Key Design Decisions

**Decision 1: Wrapper, Not Extension**
```python
# GOOD: Composition
class WebView(QWidget):
    def __init__(self):
        self._engine_view = QWebEngineView()

# NOT: Direct inheritance
class WebView(QWebEngineView):  # ❌ Less flexible
```

**Why**: Composition allows us to add features without fighting Qt's class hierarchy.

**Decision 2: Minimal Public API**
```python
# Public API (what users see)
browser.navigate(url)
browser.back()
browser.forward()

# Internal implementation hidden
browser._webview._engine_view.page().setUrl(...)  # ❌ Don't expose
```

**Why**: Users don't need to know about QWebEngineView, QWebEnginePage, etc.

**Decision 3: Theme System Optional**
```python
# Works without theme system
browser = BrowserWidget()

# Works with theme system
from vfwidgets_theme import ThemedApplication
themed_app = ThemedApplication()
browser = BrowserWidget()  # Automatically themed
```

**Why**: Widget is usable even if users don't want theming.

---

## 3. Component Specifications

### 3.1 BrowserWidget

**Purpose**: Complete browser widget combining navigation and web view.

**Public API**:
```python
class BrowserWidget(QWidget):
    """Complete browser widget with navigation and web view.

    This is the main widget you'll use. It combines a navigation bar
    with a web view to provide complete browsing functionality.

    Example:
        >>> browser = BrowserWidget()
        >>> browser.navigate("https://example.com")
        >>> browser.show()
    """

    # Signals
    title_changed = Signal(str)          # Page title changed
    url_changed = Signal(str)            # URL changed
    load_started = Signal()              # Page load started
    load_progress = Signal(int)          # Loading progress (0-100)
    load_finished = Signal(bool)         # Load finished (success/failure)
    icon_changed = Signal(QIcon)         # Favicon changed

    # Public Methods
    def __init__(self, parent=None):
        """Initialize browser widget."""

    def navigate(self, url: str) -> None:
        """Navigate to URL.

        Args:
            url: URL to navigate to (e.g., "https://example.com")
        """

    def back(self) -> None:
        """Navigate back in history."""

    def forward(self) -> None:
        """Navigate forward in history."""

    def reload(self) -> None:
        """Reload current page."""

    def stop(self) -> None:
        """Stop loading current page."""

    def set_home_url(self, url: str) -> None:
        """Set home page URL."""

    def home(self) -> None:
        """Navigate to home page."""

    def url(self) -> str:
        """Get current URL."""

    def title(self) -> str:
        """Get current page title."""

    def can_go_back(self) -> bool:
        """Check if can navigate back."""

    def can_go_forward(self) -> bool:
        """Check if can navigate forward."""
```

**Theme Integration**:
```python
class BrowserWidget(ThemedWidget):
    """Browser with theme support."""

    theme_config = {
        # Navigation bar colors
        "navbar.background": "editor.background",
        "navbar.foreground": "editor.foreground",
        "navbar.border": "panel.border",

        # URL bar colors
        "urlbar.background": "input.background",
        "urlbar.foreground": "input.foreground",
        "urlbar.border": "input.border",
        "urlbar.border_focus": "focusBorder",

        # Button colors
        "button.background": "button.background",
        "button.foreground": "button.foreground",
        "button.hover_background": "button.hoverBackground",

        # Loading indicator
        "progress.background": "progressBar.background",
        "progress.foreground": "progressBar.foreground",
    }
```

### 3.2 NavigationBar

**Purpose**: Navigation controls and URL bar.

**Components**:
- Back button (◄)
- Forward button (►)
- Reload button (⟲)
- Home button (🏠)
- URL bar (text input with autocomplete)
- Loading progress bar

**Public API**:
```python
class NavigationBar(QWidget):
    """Navigation bar with URL input and navigation buttons.

    Can be used standalone or as part of BrowserWidget.

    Example:
        >>> navbar = NavigationBar()
        >>> navbar.url_submitted.connect(my_navigate_handler)
        >>> navbar.back_clicked.connect(my_back_handler)
    """

    # Signals
    back_clicked = Signal()
    forward_clicked = Signal()
    reload_clicked = Signal()
    home_clicked = Signal()
    stop_clicked = Signal()
    url_submitted = Signal(str)  # User pressed Enter in URL bar

    # Public Methods
    def set_url(self, url: str) -> None:
        """Set URL in URL bar (doesn't navigate)."""

    def set_progress(self, progress: int) -> None:
        """Set loading progress (0-100)."""

    def set_back_enabled(self, enabled: bool) -> None:
        """Enable/disable back button."""

    def set_forward_enabled(self, enabled: bool) -> None:
        """Enable/disable forward button."""

    def set_loading(self, loading: bool) -> None:
        """Switch between reload/stop button."""
```

**Layout**:
```
┌──────────────────────────────────────────────────────────┐
│ [◄] [►] [⟲] [🏠]  https://example.com            [⋯]   │
├──────────────────────────────────────────────────────────┤
│ ████████████────────────── 65%                           │
└──────────────────────────────────────────────────────────┘
```

### 3.3 WebView

**Purpose**: Wrapper around QWebEngineView with cleaner API.

**Public API**:
```python
class WebView(QWidget):
    """Wrapper around QWebEngineView.

    Provides cleaner API and hides QWebEngine complexity.

    Example:
        >>> webview = WebView()
        >>> webview.load("https://example.com")
    """

    # Signals (forwarded from QWebEngineView)
    load_started = Signal()
    load_progress = Signal(int)
    load_finished = Signal(bool)
    title_changed = Signal(str)
    url_changed = Signal(QUrl)
    icon_changed = Signal(QIcon)

    # Public Methods
    def load(self, url: str) -> None:
        """Load URL."""

    def url(self) -> str:
        """Get current URL."""

    def title(self) -> str:
        """Get page title."""

    def back(self) -> None:
        """Go back."""

    def forward(self) -> None:
        """Go forward."""

    def reload(self) -> None:
        """Reload page."""

    def stop(self) -> None:
        """Stop loading."""
```

### 3.4 WebPage

**Purpose**: Custom QWebEnginePage with extra features.

**Customizations**:
```python
class WebPage(QWebEnginePage):
    """Custom web page with enhanced features.

    Demonstrates:
    - JavaScript console message handling
    - Certificate error handling
    - User agent customization
    """

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Handle JavaScript console messages.

        This demonstrates how to capture console.log() from web pages.
        Useful for debugging and educational purposes.
        """

    def certificateError(self, error):
        """Handle certificate errors.

        Shows users a warning for invalid certificates.
        Educational: teaches about TLS/SSL validation.
        """
```

---

## 4. Theme System Integration

### 4.1 Theme Configuration

The widget uses vfwidgets-theme token system:

```python
# Theme configuration mapping
theme_config = {
    # Map widget elements to theme tokens
    "navbar.background": "editor.background",
    "navbar.foreground": "editor.foreground",
    "urlbar.background": "input.background",
    "urlbar.foreground": "input.foreground",
    "button.background": "button.background",
    "button.hover": "button.hoverBackground",
}
```

### 4.2 Theme Application

**Automatic Theme Application**:
```python
from vfwidgets_theme import ThemedApplication
from vfwidgets_webview import BrowserWidget

# Setup themed application
app = QApplication([])
themed_app = ThemedApplication()

# Browser automatically inherits theme
browser = BrowserWidget()  # Already themed!

# Switch themes
themed_app.set_theme("dark")   # Browser updates automatically
themed_app.set_theme("light")  # Browser updates automatically
```

**Manual Theme Override**:
```python
browser = BrowserWidget()

# Override specific colors
browser.set_theme_override("urlbar.background", "#2D2D30")
browser.set_theme_override("urlbar.foreground", "#CCCCCC")
```

### 4.3 Theme-Independent Mode

Widget works without theme system:

```python
# No theme system - uses Qt defaults
browser = BrowserWidget()
browser.navigate("https://example.com")
# Works fine with system colors!
```

### 4.4 Dark/Light Mode Support

Widget automatically adjusts to theme:

```python
# Dark theme
themed_app.set_theme("dark")
# - Navigation bar: dark background, light text
# - URL bar: dark input field
# - Buttons: dark style

# Light theme
themed_app.set_theme("light")
# - Navigation bar: light background, dark text
# - URL bar: light input field
# - Buttons: light style
```

---

## 5. Public API Design

### 5.1 Design Principles

**1. Simple is Better**
```python
# GOOD: Simple API
browser.navigate("https://example.com")

# BAD: Exposing complexity
browser.webview().page().setUrl(QUrl("https://example.com"))
```

**2. Pythonic Naming**
```python
# GOOD: Python conventions
browser.can_go_back()

# BAD: Qt C++ style
browser.canGoBack()  # We keep this for Qt compatibility
```

**3. Signal-Based Communication**
```python
# GOOD: Signals for events
browser.title_changed.connect(on_title_changed)
browser.load_progress.connect(on_progress)

# BAD: Callbacks
browser.set_title_callback(on_title_changed)  # ❌ Not Qt style
```

### 5.2 Minimal API Surface

**What we expose**:
- ✅ `navigate()`, `back()`, `forward()`, `reload()`
- ✅ `url()`, `title()`
- ✅ Signals for events

**What we hide**:
- ❌ `QWebEngineView` internals
- ❌ `QWebEnginePage` internals
- ❌ `QWebEngineSettings` configuration
- ❌ Internal implementation details

**Why**: Users don't need to understand QtWebEngine to use the widget.

### 5.3 API Examples

**Basic Usage**:
```python
from vfwidgets_webview import BrowserWidget

browser = BrowserWidget()
browser.navigate("https://example.com")
browser.show()
```

**With Signals**:
```python
def on_title_changed(title):
    print(f"Page title: {title}")

def on_load_progress(progress):
    print(f"Loading: {progress}%")

browser.title_changed.connect(on_title_changed)
browser.load_progress.connect(on_load_progress)
browser.navigate("https://example.com")
```

**Navigation Control**:
```python
# Navigate
browser.navigate("https://example.com")

# Check navigation state
if browser.can_go_back():
    browser.back()

if browser.can_go_forward():
    browser.forward()

# Reload
browser.reload()

# Home
browser.set_home_url("https://start.duckduckgo.com")
browser.home()
```

---

## 6. Implementation Phases

### Phase 0.1 - Core Components (Week 1)

**Goal**: Basic working browser widget

**Tasks**:
1. Create `WebPage` (custom QWebEnginePage)
   - JavaScript console message handling
   - Certificate error handling
   - Basic user agent

2. Create `WebView` (QWebEngineView wrapper)
   - Wrap QWebEngineView
   - Forward essential signals
   - Clean API methods

3. Create `NavigationBar`
   - Back/Forward/Reload buttons
   - URL bar (QLineEdit)
   - Progress bar
   - Signal connections

4. Create `BrowserWidget`
   - Compose NavigationBar + WebView
   - Wire signals between components
   - Public API implementation

**Deliverable**: Can load web pages with navigation

### Phase 0.2 - Theme Integration (Week 1)

**Goal**: Full theme system integration

**Tasks**:
1. Add `ThemedWidget` mixin to `BrowserWidget`
2. Define `theme_config` mapping
3. Apply theme to NavigationBar
4. Apply theme to URL bar
5. Apply theme to buttons
6. Test dark/light theme switching

**Deliverable**: Widget looks good in dark and light themes

### Phase 0.3 - Polish & Examples (Week 2)

**Goal**: Production-ready widget with examples

**Tasks**:
1. URL autocomplete (simple history-based)
2. Loading indicators (spinner, progress)
3. Icon handling (favicon display)
4. Error pages (for failed loads)
5. Progressive examples (01_ through 05_)
6. Documentation completion

**Deliverable**: Complete MVP with examples

---

## 7. Examples Progression

### 7.1 Example Structure

All examples numbered sequentially:

```
examples/
├── 01_minimal_browser.py          # Simplest possible
├── 02_themed_browser.py           # Add theme system
├── 03_navigation_signals.py       # Handle events
├── 04_custom_styling.py           # Custom colors
├── 05_single_page_browser.py      # MVP: Complete browser
├── 06_standalone_components.py    # Use NavigationBar alone
└── 07_embedding_in_app.py         # Embed in larger app
```

### 7.2 Example 01: Minimal Browser

**Goal**: Show simplest possible usage

```python
"""01_minimal_browser.py

The absolute minimum code to create a working browser.
"""

from PySide6.QtWidgets import QApplication
from vfwidgets_webview import BrowserWidget

app = QApplication([])

# Create and show browser
browser = BrowserWidget()
browser.navigate("https://example.com")
browser.resize(1024, 768)
browser.show()

app.exec()
```

**What it teaches**: Basic usage, minimal setup

### 7.3 Example 02: Themed Browser

**Goal**: Show theme system integration

```python
"""02_themed_browser.py

Browser with theme system integration.
Shows automatic dark/light theme support.
"""

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton
from vfwidgets_theme import ThemedApplication
from vfwidgets_webview import BrowserWidget

app = QApplication([])
themed_app = ThemedApplication()

# Create window
window = QWidget()
layout = QVBoxLayout()

# Theme switcher
dark_btn = QPushButton("Dark Theme")
dark_btn.clicked.connect(lambda: themed_app.set_theme("dark"))
layout.addWidget(dark_btn)

light_btn = QPushButton("Light Theme")
light_btn.clicked.connect(lambda: themed_app.set_theme("light"))
layout.addWidget(light_btn)

# Browser (automatically themed)
browser = BrowserWidget()
browser.navigate("https://example.com")
layout.addWidget(browser)

window.setLayout(layout)
window.resize(1024, 768)
window.show()

app.exec()
```

**What it teaches**: Theme system, automatic theming

### 7.4 Example 03: Navigation Signals

**Goal**: Show event handling

```python
"""03_navigation_signals.py

Demonstrates handling navigation events and page state.
"""

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from vfwidgets_webview import BrowserWidget

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()

# Status label
status = QLabel("Ready")
layout.addWidget(status)

# Browser
browser = BrowserWidget()

# Connect signals
browser.title_changed.connect(
    lambda title: status.setText(f"Title: {title}")
)

browser.load_progress.connect(
    lambda progress: status.setText(f"Loading: {progress}%")
)

browser.load_finished.connect(
    lambda success: status.setText("Loaded!" if success else "Failed!")
)

browser.url_changed.connect(
    lambda url: print(f"URL changed: {url}")
)

browser.navigate("https://example.com")
layout.addWidget(browser)

window.setLayout(layout)
window.resize(1024, 768)
window.show()

app.exec()
```

**What it teaches**: Signals, event handling, page state

### 7.5 Example 05: Single Page Browser (MVP)

**Goal**: Complete old-school single-page browser

```python
"""05_single_page_browser.py

Complete single-page browser - the MVP target.
This is like old-school browsers before tabs existed.

Features:
- Full navigation (back, forward, reload, home)
- URL bar with autocomplete
- Loading indicators
- Themed UI
- Window title updates
"""

from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_theme import ThemedApplication
from vfwidgets_webview import BrowserWidget

app = QApplication([])
themed_app = ThemedApplication()

# Create main window
window = QMainWindow()
window.setWindowTitle("Simple Browser")

# Create browser widget
browser = BrowserWidget()
browser.set_home_url("https://start.duckduckgo.com")

# Update window title with page title
browser.title_changed.connect(
    lambda title: window.setWindowTitle(f"{title} - Simple Browser")
)

# Set as central widget
window.setCentralWidget(browser)

# Navigate to home
browser.home()

# Show window
window.resize(1200, 800)
window.show()

app.exec()
```

**What it teaches**: Complete browser, real-world usage, MVP achieved

---

## 8. Theme Studio Integration

### 8.1 Purpose

The widget should work in theme-studio for:
- Testing themes with real browser content
- Previewing URL bar styling
- Testing button hover states
- Demonstrating theme tokens in action

### 8.2 Theme Studio Example

**Location**: `widgets/webview_widget/docs/THEME-STUDIO.md`

**Integration**:
```python
# In theme-studio preview panel
from vfwidgets_webview import BrowserWidget

class WebviewPreview(QWidget):
    """Preview webview widget with current theme."""

    def __init__(self):
        super().__init__()
        self.browser = BrowserWidget()
        self.browser.navigate("https://example.com")

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)
```

### 8.3 Token Demonstration

Show which tokens affect which parts:

```
Theme Token                    | Affects
-------------------------------|----------------------------------
editor.background              | Navigation bar background
editor.foreground              | Navigation bar text
input.background               | URL bar background
input.foreground               | URL bar text
input.border                   | URL bar border
focusBorder                    | URL bar focus border
button.background              | Navigation buttons
button.hoverBackground         | Navigation buttons on hover
progressBar.background         | Loading progress background
progressBar.foreground         | Loading progress bar
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Test WebPage**:
- JavaScript console message capture
- Certificate error handling
- User agent setting

**Test WebView**:
- URL loading
- Signal forwarding
- Navigation methods

**Test NavigationBar**:
- Button clicks
- URL submission
- State updates (enabled/disabled)

**Test BrowserWidget**:
- Component integration
- Signal propagation
- Public API methods

### 9.2 Integration Tests

**Theme Integration**:
- Widget applies theme correctly
- Theme switching works
- Dark/light mode both work

**Navigation Flow**:
- Forward navigation works
- Back navigation works
- Reload works
- Home button works

### 9.3 Manual Tests

**Browser Functionality**:
- Load various websites
- Test with slow connections
- Test certificate errors
- Test JavaScript-heavy sites

**Theme Testing**:
- All buttons visible in dark theme
- All buttons visible in light theme
- Focus indicators clear
- Loading indicators visible

---

## Conclusion

This specification defines a **clean, reusable browser widget** that:

✅ Provides complete browsing functionality
✅ Integrates seamlessly with vfwidgets-theme
✅ Has a simple, well-documented public API
✅ Serves as foundation for advanced browsers (ViloWeb)
✅ Teaches QtWebEngine patterns through progressive examples
✅ Achieves MVP: single-page browser

**Next Steps**:
1. Implement Phase 0.1 (Core Components)
2. Create progressive examples
3. Document theme integration
4. Build MVP: single-page browser

**Target Users**:
- Developers embedding browsers in Qt apps
- Students learning QtWebEngine
- Builders of advanced browsers (like ViloWeb)
