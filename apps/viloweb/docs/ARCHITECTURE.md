# ViloWeb Architecture

**Version**: 1.0
**Last Updated**: 2025-10-17
**Status**: Design Phase

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Hierarchy](#2-component-hierarchy)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Module Structure](#4-module-structure)
5. [JavaScript Bridge Pattern](#5-javascript-bridge-pattern)
6. [Extension System Architecture](#6-extension-system-architecture)
7. [Signal/Slot Connections](#7-signalslot-connections)
8. [Storage Layer](#8-storage-layer)
9. [Thread Architecture](#9-thread-architecture)
10. [Security Model](#10-security-model)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ViloWeb Application                       │
│                     (Educational Browser)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
      ┌─────────▼─────────┐       ┌────────▼────────┐
      │   VFWidgets       │       │   Qt/PySide6    │
      │   Components      │       │   Framework     │
      └─────────┬─────────┘       └────────┬────────┘
                │                           │
    ┌───────────┼───────────┬───────────────┼──────────┐
    │           │           │               │          │
┌───▼───┐  ┌───▼───┐  ┌────▼────┐  ┌──────▼──────┐  │
│Chrome │  │Vilo   │  │vfwidgets│  │QWebEngine   │  │
│Tabbed │  │Code   │  │ theme   │  │QWebChannel  │  │
│Window │  │Window │  │         │  │             │  │
└───┬───┘  └───┬───┘  └────┬────┘  └──────┬──────┘  │
    │          │            │               │         │
    └──────────┴────────────┴───────────────┴─────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
    ┌───────▼────────┐              ┌──────────▼──────────┐
    │  Browser Core  │              │  Extension System   │
    │  - Tabs        │              │  - Python API       │
    │  - Navigation  │              │  - JS Bridge        │
    │  - History     │              │  - Lifecycle Hooks  │
    │  - Bookmarks   │              │  - DOM Manipulation │
    └───────┬────────┘              └──────────┬──────────┘
            │                                   │
            └───────────────┬───────────────────┘
                            │
                ┌───────────▼───────────┐
                │   Storage Layer       │
                │   - SQLite (history)  │
                │   - JSON (bookmarks)  │
                │   - JSON (settings)   │
                └───────────────────────┘
```

### 1.2 Design Principles

**Educational First:**
- Every component designed as teaching material
- Extensive inline documentation
- Clear separation of concerns
- Standard Qt patterns demonstrated

**VFWidgets Showcase:**
- Real-world integration of ChromeTabbedWindow
- ViloCodeWindow with multiple panels
- Theme system throughout UI
- Optional multisplit for advanced layouts

**Python-Centric Extensions:**
- Extensions written in Python, not JavaScript
- Full access to Python ecosystem (BeautifulSoup, requests, etc.)
- Qt/PySide6 APIs available to extensions
- QWebChannel bridge for DOM manipulation

**Clean Architecture:**
- Separation between UI and business logic
- Protocol-based interfaces for flexibility
- Dependency injection where appropriate
- Testable components

---

## 2. Component Hierarchy

### 2.1 Main Window Structure

```
ViloWebWindow (ViloCodeWindow)
├── Activity Bar (left sidebar)
│   ├── Browser Icon (home view)
│   ├── Bookmarks Icon
│   ├── History Icon
│   ├── Downloads Icon
│   ├── Extensions Icon
│   ├── Console Icon (Python REPL)
│   └── Settings Icon
│
├── Sidebar Panel (collapsible)
│   ├── BookmarksPanel
│   ├── HistoryPanel
│   ├── DownloadsPanel
│   ├── ExtensionsPanel
│   ├── ConsolePanel (Python REPL)
│   └── SettingsPanel
│
└── Main Content Area
    └── BrowserArea (ChromeTabbedWindow)
        ├── Tab 1 (BrowserTab)
        │   ├── NavigationBar
        │   │   ├── BackButton
        │   │   ├── ForwardButton
        │   │   ├── ReloadButton
        │   │   ├── HomeButton
        │   │   ├── URLBar (with autocomplete)
        │   │   └── BookmarkButton
        │   └── WebView (QWebEngineView)
        │       └── WebPage (QWebEnginePage)
        │           ├── QWebChannel (JS Bridge)
        │           └── Profile (QWebEngineProfile)
        ├── Tab 2 (BrowserTab)
        └── Tab N (BrowserTab)
```

### 2.2 Component Responsibilities

| Component | Responsibility | Key APIs |
|-----------|---------------|----------|
| **ViloWebWindow** | Main application window, coordinates all panels | show_panel(), current_tab(), theme_changed() |
| **BrowserArea** | Manages browser tabs using ChromeTabbedWindow | new_tab(), close_tab(), get_current_tab() |
| **BrowserTab** | Single browser tab with navigation and web view | navigate(), back(), forward(), reload() |
| **NavigationBar** | URL input and navigation controls | set_url(), update_progress(), update_state() |
| **WebView** | Displays web content (QWebEngineView wrapper) | load(), inject_js(), inject_css() |
| **BookmarksPanel** | Displays and manages bookmarks | add_bookmark(), remove_bookmark(), organize() |
| **HistoryPanel** | Displays browsing history | load_history(), search(), clear() |
| **ConsolePanel** | Python REPL for browser automation | execute_code(), access to browser object |
| **ExtensionsPanel** | Manages installed extensions | load_extension(), enable(), disable(), configure() |
| **ExtensionManager** | Extension lifecycle and API injection | register_extension(), notify_page_load() |

---

## 3. Data Flow Diagrams

### 3.1 Page Navigation Flow

```
User enters URL
       │
       ▼
  URLBar.returnPressed
       │
       ▼
  BrowserTab.navigate(url)
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
ExtensionManager                    WebPage.setUrl(url)
.on_before_navigate()                     │
       │                                  ▼
       ├─ False: Block              WebPage.loadStarted
       │         navigation               │
       │                                  ▼
       └─ True: Allow              NavigationBar
                │                  .update_progress(0)
                │                        │
                │                        ▼
                │                  WebPage.loadProgress
                │                        │
                │                        ▼
                │                  NavigationBar
                │                  .update_progress(percent)
                │                        │
                │                        ▼
                └──────────────────> WebPage.loadFinished
                                         │
                                         ▼
                                   ExtensionManager
                                   .on_page_load(url, page)
                                         │
                                         ├──> Extension 1.on_page_load()
                                         ├──> Extension 2.on_page_load()
                                         └──> Extension N.on_page_load()
                                         │
                                         ▼
                                   History.add_entry(url, title)
                                         │
                                         ▼
                                   Navigation Complete
```

### 3.2 Extension Execution Flow

```
User installs extension.py
       │
       ▼
ExtensionManager.load_extension("extension.py")
       │
       ▼
Import extension module
       │
       ▼
Instantiate extension class
extension = MyExtension(api)
       │
       ▼
ExtensionManager.register(extension)
       │
       ▼
Extension activated
       │
       │
       │  [Page loads]
       │        │
       ▼        ▼
ExtensionManager.on_before_navigate(url)
       │
       ├──> extension.on_before_navigate(url)
       │         │
       │         ├──> Return False: Block navigation
       │         └──> Return True: Allow navigation
       │
       └──> [If allowed]
                 │
                 ▼
            Page loads
                 │
                 ▼
ExtensionManager.on_page_load(url, page)
       │
       ├──> extension.on_page_load(url, page)
       │         │
       │         ├──> api.inject_css(page, "...")
       │         ├──> api.inject_javascript(page, "...")
       │         ├──> api.execute_js(page, "...")
       │         └──> api.show_notification("...")
       │
       └──> Extension processing complete
```

### 3.3 JavaScript Bridge Flow (Python ↔ JavaScript)

```
Python Side                          JavaScript Side
─────────────                        ────────────────

Extension wants to modify DOM
       │
       ▼
api.execute_js(page, "document.title")
       │
       ▼
WebPage.runJavaScript(                     │
    code="document.title",                 │
    callback=handle_result                 │
)                                          │
       │                                   │
       ├───────────── IPC ─────────────────▶
       │                                   │
       │                              Chromium
       │                              executes JS
       │                                   │
       │                              return "Example"
       │                                   │
       ◀───────────── IPC ─────────────────┤
       │                                   │
       ▼
handle_result("Example")
       │
       ▼
Extension receives result


JavaScript Side                      Python Side
────────────────                     ─────────────

JavaScript calls Python function
       │
       ▼
qwebchannel.objects.pyBridge.notify(
    "linkClicked",
    "https://example.com"
)
       │
       ├───────────── IPC ─────────────────▶
       │                                   │
       │                            WebChannel
       │                            routes to object
       │                                   │
       │                            pyBridge.notify()
       │                                   │
       │                            Signal emitted
       │                                   │
       │                            Slot receives data
       │                                   │
       │                            Process in Python
       │                                   │
       ◀───────────── IPC ─────────────────┤
       │                              (optional response)
       ▼
JavaScript receives response
```

---

## 4. Module Structure

### 4.1 Directory Layout

```
viloweb/
├── src/
│   └── viloweb/
│       ├── __init__.py                    # Public API exports
│       │
│       ├── app.py                         # Application entry point
│       ├── window.py                      # Main window (ViloCodeWindow)
│       │
│       ├── browser/                       # Browser core components
│       │   ├── __init__.py
│       │   ├── tab.py                    # BrowserTab widget
│       │   ├── navigation.py             # NavigationBar widget
│       │   ├── webview.py                # WebView wrapper
│       │   ├── webpage.py                # WebPage with custom behaviors
│       │   └── profile.py                # Profile manager
│       │
│       ├── extensions/                    # Extension system
│       │   ├── __init__.py
│       │   ├── base.py                   # ViloWebExtension base class
│       │   ├── manager.py                # ExtensionManager
│       │   ├── api.py                    # ExtensionAPI implementation
│       │   ├── loader.py                 # Extension loading/importing
│       │   └── examples/                 # Example extensions
│       │       ├── ad_blocker.py
│       │       ├── page_modifier.py
│       │       └── web_scraper.py
│       │
│       ├── panels/                        # Sidebar panels
│       │   ├── __init__.py
│       │   ├── bookmarks.py              # BookmarksPanel
│       │   ├── history.py                # HistoryPanel
│       │   ├── downloads.py              # DownloadsPanel
│       │   ├── extensions_panel.py       # ExtensionsPanel
│       │   ├── console.py                # ConsolePanel (Python REPL)
│       │   └── settings.py               # SettingsPanel
│       │
│       ├── storage/                       # Data persistence
│       │   ├── __init__.py
│       │   ├── history_db.py             # SQLite history storage
│       │   ├── bookmarks.py              # JSON bookmarks storage
│       │   ├── downloads_db.py           # SQLite downloads tracking
│       │   └── settings.py               # JSON settings storage
│       │
│       ├── bridge/                        # JavaScript bridge
│       │   ├── __init__.py
│       │   ├── channel.py                # QWebChannel setup
│       │   ├── bridge_object.py          # Python object exposed to JS
│       │   └── bridge.js                 # JavaScript side code
│       │
│       └── utils/                         # Utilities
│           ├── __init__.py
│           ├── url_utils.py              # URL parsing/validation
│           ├── autocomplete.py           # URL autocomplete
│           └── icon_provider.py          # Favicon handling
│
├── tests/                                 # Test suite
│   ├── test_browser/
│   ├── test_extensions/
│   └── test_storage/
│
├── examples/                              # Usage examples
│   ├── 01_basic_browser.py
│   ├── 02_custom_extension.py
│   └── 03_automation.py
│
├── tutorials/                             # Interactive tutorials
│   ├── 01_hello_world.md
│   ├── 02_ad_blocker.md
│   └── ...
│
└── pyproject.toml                        # Package configuration
```

### 4.2 Key Classes by Module

**browser/tab.py:**
```python
class BrowserTab(QWidget):
    """Individual browser tab with web view and navigation."""

    # Signals
    titleChanged = Signal(str)
    urlChanged = Signal(str)
    loadProgressChanged = Signal(int)
    loadFinished = Signal(bool)

    # Methods
    def navigate(self, url: str) -> None
    def back(self) -> None
    def forward(self) -> None
    def reload(self) -> None
    def stop(self) -> None
    def execute_js(self, code: str, callback: Callable = None) -> None
    def inject_css(self, css: str) -> None
```

**extensions/base.py:**
```python
class ViloWebExtension(QObject):
    """Base class for all ViloWeb extensions."""

    # Metadata
    name: str
    version: str
    description: str
    author: str

    # Lifecycle hooks
    def on_page_load(self, url: str, page: QWebEnginePage) -> None
    def on_before_navigate(self, url: str) -> bool
    def on_navigation_finished(self, url: str, success: bool) -> None
    def on_download_requested(self, download: QWebEngineDownloadRequest) -> bool
```

**extensions/api.py:**
```python
class ExtensionAPI:
    """API provided to extensions for browser control."""

    def navigate(self, url: str) -> None
    def new_tab(self, url: str = None) -> Tab
    def close_tab(self, tab: Tab) -> None
    def get_current_tab(self) -> Tab
    def inject_javascript(self, page: QWebEnginePage, js: str) -> None
    def inject_css(self, page: QWebEnginePage, css: str) -> None
    def execute_js(self, page: QWebEnginePage, js: str) -> Any
    def show_notification(self, message: str) -> None
    def get_page_html(self, page: QWebEnginePage) -> str
    def screenshot(self, page: QWebEnginePage, path: str) -> None
```

**panels/console.py:**
```python
class ConsolePanel(QWidget):
    """Python REPL panel for browser automation."""

    def __init__(self, browser_area: BrowserArea):
        self.browser = browser_area  # Access to browser object
        self.interpreter = code.InteractiveInterpreter(locals={
            'browser': browser_area,
            'tab': browser_area.current_tab,
        })

    def execute_code(self, code: str) -> str
    def clear(self) -> None
    def update_context(self) -> None  # Update 'tab' variable
```

---

## 5. JavaScript Bridge Pattern

### 5.1 QWebChannel Setup

**Python Side (bridge/channel.py):**

```python
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage

class BridgeSetup:
    """Sets up QWebChannel for Python-JavaScript communication."""

    @staticmethod
    def setup_channel(page: QWebEnginePage, bridge_object: QObject):
        """
        Initialize QWebChannel on a page.

        This demonstrates:
        1. Creating QWebChannel
        2. Registering Python objects
        3. Injecting channel JS library
        4. Making object available to page

        Args:
            page: The QWebEnginePage to setup
            bridge_object: Python object to expose to JavaScript
        """
        # Create channel
        channel = QWebChannel(page)

        # Register Python object with name "pyBridge"
        # JavaScript can access as: qwebchannel.objects.pyBridge
        channel.registerObject("pyBridge", bridge_object)

        # Set channel on page
        page.setWebChannel(channel)

        # Inject qwebchannel.js library
        # This provides the JavaScript API for QWebChannel
        with open(":/qtwebchannel/qwebchannel.js", "r") as f:
            qwebchannel_js = f.read()

        page.runJavaScript(qwebchannel_js)
```

**Python Bridge Object (bridge/bridge_object.py):**

```python
from PySide6.QtCore import QObject, Signal, Slot

class BridgeObject(QObject):
    """Python object exposed to JavaScript via QWebChannel."""

    # Signals JavaScript can connect to
    themeChanged = Signal(str)  # Notify JS of theme changes
    extensionMessage = Signal(str, dict)  # Extension to JS communication

    def __init__(self, browser_tab):
        super().__init__()
        self.tab = browser_tab

    @Slot(str, str)
    def notify(self, event: str, data: str):
        """
        JavaScript calls this to notify Python of events.

        Example from JS:
            qwebchannel.objects.pyBridge.notify("linkClicked", url);
        """
        if event == "linkClicked":
            print(f"Link clicked: {data}")
        elif event == "formSubmitted":
            print(f"Form submitted: {data}")

    @Slot(str, result=str)
    def execute_extension(self, extension_name: str) -> str:
        """JavaScript calls this to trigger extension functionality."""
        # Extension manager processes this
        return self.tab.extension_manager.execute(extension_name)

    @Slot(str, str)
    def log_to_python(self, level: str, message: str):
        """JavaScript console messages forwarded to Python."""
        print(f"JS [{level}]: {message}")
```

**JavaScript Side (bridge/bridge.js):**

```javascript
// This file is injected into every page
(function() {
    'use strict';

    // Initialize QWebChannel when document loads
    new QWebChannel(qt.webChannelTransport, function(channel) {
        // Access the Python bridge object
        window.pyBridge = channel.objects.pyBridge;

        // Example: Notify Python when links are clicked
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                pyBridge.notify('linkClicked', e.target.href);
            }
        });

        // Example: Forward console messages to Python
        const oldLog = console.log;
        console.log = function(...args) {
            oldLog.apply(console, args);
            pyBridge.log_to_python('info', args.join(' '));
        };

        // Listen for theme changes from Python
        pyBridge.themeChanged.connect(function(themeName) {
            console.log('Theme changed to:', themeName);
            applyTheme(themeName);
        });

        // Notify Python that bridge is ready
        pyBridge.notify('bridgeReady', 'initialized');
    });

    function applyTheme(themeName) {
        // Apply theme CSS to page
        // This is called when Python emits themeChanged signal
    }
})();
```

### 5.2 Extension DOM Manipulation

**How extensions manipulate DOM from Python:**

```python
class PageModifierExtension(ViloWebExtension):
    """Example: Modify page content from Python."""

    def on_page_load(self, url: str, page: QWebEnginePage):
        # Method 1: Execute JavaScript directly
        page.runJavaScript("""
            document.body.style.backgroundColor = 'darkgray';
        """)

        # Method 2: Use ExtensionAPI wrapper
        self.api.execute_js(page, """
            let links = document.querySelectorAll('a');
            links.forEach(link => link.style.color = 'blue');
        """)

        # Method 3: Inject CSS
        css = """
        body {
            filter: invert(1) hue-rotate(180deg);
        }
        img, video {
            filter: invert(1) hue-rotate(180deg);
        }
        """
        self.api.inject_css(page, css)

        # Method 4: Get data from page to Python
        def handle_title(title):
            print(f"Page title: {title}")
            self.api.show_notification(f"Loaded: {title}")

        page.runJavaScript("document.title", handle_title)
```

---

## 6. Extension System Architecture

### 6.1 Extension Lifecycle

```
┌───────────────────────────────────────────────────────────────┐
│                    Extension Lifecycle                         │
└───────────────────────────────────────────────────────────────┘

1. Discovery
   └─> ExtensionManager scans ~/.viloweb/extensions/
       └─> Finds extension.py files

2. Loading
   └─> ExtensionLoader.load("extension.py")
       ├─> Import module dynamically
       ├─> Find ViloWebExtension subclass
       ├─> Validate metadata (name, version, etc.)
       └─> Return extension class

3. Instantiation
   └─> extension = ExtensionClass(api)
       ├─> Pass ExtensionAPI instance
       └─> Extension initializes

4. Registration
   └─> ExtensionManager.register(extension)
       ├─> Add to active extensions list
       ├─> Connect to lifecycle signals
       └─> Call extension.on_enable() if defined

5. Activation
   └─> Extension receives lifecycle callbacks:
       ├─> on_before_navigate(url) → bool
       ├─> on_page_load(url, page) → None
       ├─> on_navigation_finished(url, success) → None
       └─> on_download_requested(download) → bool

6. Deactivation (optional)
   └─> ExtensionManager.disable(extension)
       └─> Call extension.on_disable() if defined

7. Unloading (optional)
   └─> ExtensionManager.unload(extension)
       ├─> Remove from active list
       ├─> Disconnect signals
       └─> Cleanup resources
```

### 6.2 Extension Manager Implementation

**extensions/manager.py:**

```python
from typing import Dict, List, Type
from PySide6.QtCore import QObject, Signal
from .base import ViloWebExtension
from .api import ExtensionAPI
from .loader import ExtensionLoader

class ExtensionManager(QObject):
    """
    Manages extension lifecycle and coordinates callbacks.

    This class demonstrates:
    1. Dynamic extension loading
    2. Lifecycle hook coordination
    3. Extension isolation
    4. Error handling
    """

    # Signals
    extensionLoaded = Signal(str)  # extension_name
    extensionEnabled = Signal(str)
    extensionDisabled = Signal(str)
    extensionError = Signal(str, str)  # extension_name, error_message

    def __init__(self, browser_window):
        super().__init__()
        self.browser_window = browser_window
        self.api = ExtensionAPI(browser_window)
        self.extensions: Dict[str, ViloWebExtension] = {}
        self.loader = ExtensionLoader()

    def load_extension(self, path: str) -> bool:
        """
        Load extension from file.

        Args:
            path: Path to extension.py file

        Returns:
            True if loaded successfully
        """
        try:
            # Load extension class
            extension_class = self.loader.load(path)

            # Instantiate with API
            extension = extension_class(self.api)

            # Validate
            if not hasattr(extension, 'name'):
                raise ValueError("Extension must define 'name' attribute")

            # Register
            self.extensions[extension.name] = extension
            self.extensionLoaded.emit(extension.name)

            print(f"Loaded extension: {extension.name} v{extension.version}")
            return True

        except Exception as e:
            self.extensionError.emit(path, str(e))
            print(f"Failed to load extension {path}: {e}")
            return False

    def on_before_navigate(self, url: str) -> bool:
        """
        Call all extensions' on_before_navigate hooks.

        Returns False if any extension blocks navigation.
        """
        for name, extension in self.extensions.items():
            if hasattr(extension, 'on_before_navigate'):
                try:
                    # If any extension returns False, block navigation
                    if not extension.on_before_navigate(url):
                        print(f"Navigation blocked by {name}")
                        return False
                except Exception as e:
                    self.extensionError.emit(name, str(e))
                    print(f"Error in {name}.on_before_navigate: {e}")

        return True  # Allow navigation

    def on_page_load(self, url: str, page):
        """
        Call all extensions' on_page_load hooks.
        """
        for name, extension in self.extensions.items():
            if hasattr(extension, 'on_page_load'):
                try:
                    extension.on_page_load(url, page)
                except Exception as e:
                    self.extensionError.emit(name, str(e))
                    print(f"Error in {name}.on_page_load: {e}")
```

### 6.3 Extension API Implementation

**extensions/api.py:**

```python
from typing import Optional, Callable, Any
from PySide6.QtCore import QObject
from PySide6.QtWebEngineCore import QWebEnginePage

class ExtensionAPI:
    """
    API provided to extensions for browser control.

    This class wraps browser functionality in a safe, stable API
    that extensions can use without accessing internal implementation.
    """

    def __init__(self, browser_window):
        self.window = browser_window
        self.browser = browser_window.browser_area

    # ===== Browser Control =====

    def navigate(self, url: str) -> None:
        """Navigate current tab to URL."""
        tab = self.browser.current_tab()
        if tab:
            tab.navigate(url)

    def back(self) -> None:
        """Navigate back in current tab."""
        tab = self.browser.current_tab()
        if tab:
            tab.back()

    def forward(self) -> None:
        """Navigate forward in current tab."""
        tab = self.browser.current_tab()
        if tab:
            tab.forward()

    # ===== Tab Management =====

    def new_tab(self, url: Optional[str] = None):
        """Create new tab, optionally navigating to URL."""
        return self.browser.new_tab(url)

    def close_tab(self, tab) -> None:
        """Close specified tab."""
        self.browser.close_tab(tab)

    def get_current_tab(self):
        """Get currently active tab."""
        return self.browser.current_tab()

    def get_all_tabs(self) -> list:
        """Get list of all open tabs."""
        return self.browser.get_all_tabs()

    # ===== DOM Manipulation =====

    def inject_javascript(self, page: QWebEnginePage, js_code: str) -> None:
        """
        Inject JavaScript into page.

        The code runs in the page context and has access to the DOM.
        """
        page.runJavaScript(js_code)

    def inject_css(self, page: QWebEnginePage, css_code: str) -> None:
        """
        Inject CSS into page.

        Creates a <style> element with the provided CSS.
        """
        js = f"""
        (function() {{
            let style = document.createElement('style');
            style.textContent = {repr(css_code)};
            document.head.appendChild(style);
        }})();
        """
        page.runJavaScript(js)

    def execute_js(self, page: QWebEnginePage, js_code: str,
                   callback: Optional[Callable] = None) -> None:
        """
        Execute JavaScript and optionally get result via callback.

        Example:
            def handle_title(title):
                print(f"Title: {title}")

            api.execute_js(page, "document.title", handle_title)
        """
        if callback:
            page.runJavaScript(js_code, callback)
        else:
            page.runJavaScript(js_code)

    # ===== Element Interaction =====

    def click_element(self, page: QWebEnginePage, selector: str) -> None:
        """Click element matching CSS selector."""
        js = f"""
        (function() {{
            let element = document.querySelector({repr(selector)});
            if (element) {{
                element.click();
            }}
        }})();
        """
        page.runJavaScript(js)

    def fill_form(self, page: QWebEnginePage, form_data: dict) -> None:
        """
        Fill form fields.

        Args:
            form_data: Dict of {selector: value} pairs
        """
        for selector, value in form_data.items():
            js = f"""
            (function() {{
                let element = document.querySelector({repr(selector)});
                if (element) {{
                    element.value = {repr(value)};
                }}
            }})();
            """
            page.runJavaScript(js)

    # ===== Data Extraction =====

    def get_page_html(self, page: QWebEnginePage,
                      callback: Callable[[str], None]) -> None:
        """Get page HTML asynchronously."""
        page.toHtml(callback)

    def screenshot(self, page: QWebEnginePage, path: str) -> None:
        """Save page screenshot to file."""
        # Implementation using QWebEngineView.grab()
        pass

    # ===== UI Interaction =====

    def show_notification(self, message: str, duration: int = 3000) -> None:
        """Show notification to user."""
        # Use Qt notification or status bar
        self.window.statusBar().showMessage(message, duration)
```

---

## 7. Signal/Slot Connections

### 7.1 Navigation Flow Signals

```python
# browser/tab.py
class BrowserTab(QWidget):
    # Signals emitted by BrowserTab
    titleChanged = Signal(str)          # Page title changed
    urlChanged = Signal(str)            # URL changed
    loadProgressChanged = Signal(int)   # Load progress (0-100)
    loadStarted = Signal()              # Navigation started
    loadFinished = Signal(bool)         # Navigation finished (success)
    iconChanged = Signal(QIcon)         # Favicon changed

# window.py - Main window connects to tab signals
class ViloWebWindow(ViloCodeWindow):
    def _setup_signals(self):
        # Connect browser area signals
        self.browser_area.currentChanged.connect(self._on_tab_changed)

        # When tab changes, update window title
        self._on_tab_changed(self.browser_area.currentIndex())

    def _on_tab_changed(self, index: int):
        tab = self.browser_area.widget(index)
        if tab:
            # Connect new tab's signals
            tab.titleChanged.connect(self._on_title_changed)
            tab.urlChanged.connect(self._on_url_changed)
            tab.loadProgressChanged.connect(self._on_progress_changed)

            # Update window title with current tab title
            self._on_title_changed(tab.title())

    def _on_title_changed(self, title: str):
        self.setWindowTitle(f"{title} - ViloWeb")

    def _on_url_changed(self, url: str):
        # Update URL bar in navigation bar
        current_tab = self.browser_area.currentWidget()
        if current_tab:
            current_tab.navigation_bar.set_url(url)

    def _on_progress_changed(self, progress: int):
        # Update progress in status bar
        if progress < 100:
            self.statusBar().showMessage(f"Loading... {progress}%")
        else:
            self.statusBar().clearMessage()
```

### 7.2 Extension System Signals

```python
# extensions/manager.py
class ExtensionManager(QObject):
    # Signals emitted by ExtensionManager
    extensionLoaded = Signal(str)       # Extension loaded successfully
    extensionEnabled = Signal(str)      # Extension enabled
    extensionDisabled = Signal(str)     # Extension disabled
    extensionError = Signal(str, str)   # Error occurred (name, message)

# panels/extensions_panel.py
class ExtensionsPanel(QWidget):
    def __init__(self, extension_manager: ExtensionManager):
        super().__init__()
        self.extension_manager = extension_manager

        # Connect to manager signals
        self.extension_manager.extensionLoaded.connect(
            self._on_extension_loaded
        )
        self.extension_manager.extensionError.connect(
            self._on_extension_error
        )

    def _on_extension_loaded(self, name: str):
        # Add extension to list widget
        self.extension_list.addItem(name)

    def _on_extension_error(self, name: str, error: str):
        # Show error dialog
        QMessageBox.warning(
            self,
            f"Extension Error: {name}",
            error
        )
```

---

## 8. Storage Layer

### 8.1 History Database (SQLite)

**storage/history_db.py:**

```python
import sqlite3
from datetime import datetime
from typing import List, Optional

class HistoryDatabase:
    """
    SQLite database for browsing history.

    This demonstrates:
    1. SQLite integration with Qt
    2. Efficient history queries
    3. Full-text search
    4. Privacy considerations (clear history)
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create history table if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visit_count INTEGER DEFAULT 1
                )
            """)

            # Index for fast URL lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_url
                ON history(url)
            """)

            # Index for date range queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_visit_time
                ON history(visit_time DESC)
            """)

    def add_visit(self, url: str, title: str) -> None:
        """Add or update history entry."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if URL already exists
            cursor = conn.execute(
                "SELECT id, visit_count FROM history WHERE url = ?",
                (url,)
            )
            row = cursor.fetchone()

            if row:
                # Update existing entry
                conn.execute("""
                    UPDATE history
                    SET title = ?,
                        visit_time = CURRENT_TIMESTAMP,
                        visit_count = visit_count + 1
                    WHERE id = ?
                """, (title, row[0]))
            else:
                # Insert new entry
                conn.execute("""
                    INSERT INTO history (url, title)
                    VALUES (?, ?)
                """, (url, title))

    def search(self, query: str, limit: int = 100) -> List[dict]:
        """Search history by URL or title."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT url, title, visit_time, visit_count
                FROM history
                WHERE url LIKE ? OR title LIKE ?
                ORDER BY visit_time DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 100) -> List[dict]:
        """Get recent history entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT url, title, visit_time, visit_count
                FROM history
                ORDER BY visit_time DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def clear_all(self) -> None:
        """Clear all history (privacy feature)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history")
```

### 8.2 Bookmarks Storage (JSON)

**storage/bookmarks.py:**

```python
import json
from pathlib import Path
from typing import List, Dict, Optional

class BookmarksStorage:
    """
    JSON-based bookmarks storage.

    Structure:
    {
        "bookmarks": [
            {
                "id": "uuid",
                "title": "Example",
                "url": "https://example.com",
                "folder": "Work",
                "tags": ["important", "docs"],
                "created": "2025-10-17T10:30:00",
                "notes": "Optional notes"
            }
        ],
        "folders": ["Work", "Personal", "Reading List"]
    }
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = self._load()

    def _load(self) -> dict:
        """Load bookmarks from file."""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {"bookmarks": [], "folders": []}

    def _save(self) -> None:
        """Save bookmarks to file."""
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_bookmark(self, title: str, url: str,
                    folder: Optional[str] = None,
                    tags: List[str] = None) -> str:
        """Add new bookmark."""
        import uuid
        from datetime import datetime

        bookmark = {
            "id": str(uuid.uuid4()),
            "title": title,
            "url": url,
            "folder": folder,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "notes": ""
        }

        self.data["bookmarks"].append(bookmark)
        self._save()
        return bookmark["id"]

    def get_all(self) -> List[dict]:
        """Get all bookmarks."""
        return self.data["bookmarks"]

    def search(self, query: str) -> List[dict]:
        """Search bookmarks."""
        query = query.lower()
        return [
            b for b in self.data["bookmarks"]
            if query in b["title"].lower()
            or query in b["url"].lower()
            or any(query in tag.lower() for tag in b["tags"])
        ]
```

---

## 9. Thread Architecture

### 9.1 Threading Model

```
Main Thread (Qt GUI Thread)
├── UI Components
│   ├── ViloWebWindow
│   ├── BrowserArea (ChromeTabbedWindow)
│   ├── Sidebar Panels
│   └── All QWidget-derived components
│
├── QWebEngineView (runs in main thread)
│   └── Communicates with Renderer Process
│
└── Extension Manager (runs in main thread)
    └── Extension callbacks (Python code)

Chromium Renderer Process (separate process)
├── HTML/CSS rendering
├── JavaScript execution
├── DOM manipulation
└── IPC with Main Process via QWebChannel

Background Workers (QThread or QRunnable)
├── Database queries (history search)
├── File I/O (bookmark loading)
├── Network requests (extension downloads)
└── Heavy computation (thumbnail generation)
```

**Key Principles:**
- All UI operations must be on main thread
- QWebEngine handles multi-process architecture internally
- Extensions run on main thread (keep callbacks fast!)
- Use QThread for heavy operations in extensions

### 9.2 Thread-Safe Extension Operations

```python
from PySide6.QtCore import QThread, Signal, QRunnable, QThreadPool

class WebScraperExtension(ViloWebExtension):
    """Example: Scraping data in background thread."""

    def on_page_load(self, url: str, page: QWebEnginePage):
        # Get HTML asynchronously
        page.toHtml(lambda html: self._process_html(html, url))

    def _process_html(self, html: str, url: str):
        """This runs on main thread - delegate to worker."""
        # Create worker
        worker = ScraperWorker(html, url)
        worker.signals.finished.connect(self._on_scrape_complete)

        # Run in thread pool
        QThreadPool.globalInstance().start(worker)

    def _on_scrape_complete(self, data: dict):
        """Back on main thread - can update UI."""
        self.api.show_notification(f"Scraped {len(data)} items")

class ScraperWorker(QRunnable):
    """Worker for background scraping."""

    class Signals(QObject):
        finished = Signal(dict)

    def __init__(self, html: str, url: str):
        super().__init__()
        self.html = html
        self.url = url
        self.signals = self.Signals()

    def run(self):
        """This runs in background thread."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.html, 'html.parser')

        # Heavy processing here
        data = {
            "title": soup.title.string if soup.title else "",
            "links": [a['href'] for a in soup.find_all('a', href=True)],
            "images": [img['src'] for img in soup.find_all('img', src=True)],
        }

        # Emit result (Qt will deliver to main thread)
        self.signals.finished.emit(data)
```

---

## 10. Security Model

### 10.1 Web Security Features

**Content Security Policy (CSP):**
- ViloWeb does not modify page CSP by default
- Extensions can inject scripts (user explicitly installs extensions)
- No remote code execution without user consent

**Same-Origin Policy:**
- Enforced by Chromium/QWebEngine
- Extensions use QWebChannel for cross-origin communication
- No direct DOM access from Python without JavaScript bridge

**Download Security:**
```python
def _on_download_requested(self, download: QWebEngineDownloadRequest):
    """Prompt user for download confirmation."""

    # Ask extensions first
    if not self.extension_manager.on_download_requested(download):
        download.cancel()
        return

    # Prompt user
    reply = QMessageBox.question(
        self,
        "Download File",
        f"Download {download.suggestedFileName()}?\\n"
        f"From: {download.url().host()}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        download.accept()
    else:
        download.cancel()
```

### 10.2 Extension Security

**Sandboxing:**
- Extensions are Python code - have full system access (by design for learning)
- User must explicitly install extensions from filesystem
- No automatic extension installation from web

**Extension Isolation:**
- Each extension is a separate Python object
- Extensions cannot directly access each other
- Communication via ExtensionAPI only

**Best Practices:**
```python
# Good: Safe API usage
self.api.inject_css(page, "body { background: red; }")

# Bad: Direct page manipulation (works but bypasses API)
page.runJavaScript("dangerous_code()")  # Still possible for learning

# Good: User notification
self.api.show_notification("Ad blocked")

# Bad: Silent modification
# (nothing stops this - educational tool prioritizes learning)
```

**Future Enhancements:**
- Extension permissions system
- Extension manifest with declared permissions
- Sandboxed extension execution (restricted Python)

---

## 11. Security Testing Architecture

### 11.1 Overview

ViloWeb includes a comprehensive security testing system designed for **defensive security only** - teaching developers how to test their own applications and understand security concepts.

**Key Principles:**
- Educational first - explain security concepts clearly
- Defensive only - test your own applications
- Automated scanning - reduce manual effort
- Report generation - actionable security findings
- Ethical guidelines - prominent warnings and disclaimers

### 11.2 Security Testing Components

```
┌─────────────────────────────────────────────────────────────┐
│                Security Testing System                       │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
  ┌─────▼──────┐   ┌─────▼──────┐   ┌─────▼──────┐
  │  Security  │   │  Security  │   │   Report   │
  │   Panel    │   │ Extensions │   │ Generator  │
  │   (UI)     │   │  (Python)  │   │            │
  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
  ┌─────▼──────┐                    ┌──────▼─────┐
  │  Security  │                    │  Security  │
  │  Scanners  │                    │  Database  │
  │            │                    │  (Rules)   │
  └────────────┘                    └────────────┘
```

### 11.3 Security Panel Architecture

**panels/security.py:**

```python
from PySide6.QtWidgets import QWidget
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SecurityIssue:
    """Represents a single security finding."""
    category: str  # "headers", "cookies", "forms", "tls", "content"
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    recommendation: str
    fix_code: Optional[str] = None  # Code to copy for fixing
    learn_more_url: Optional[str] = None

@dataclass
class SecurityScanResult:
    """Complete security scan results."""
    url: str
    scan_time: datetime
    score: int  # 0-100
    issues: List[SecurityIssue]
    passed_checks: List[str]

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "high")

class SecurityPanel(QWidget):
    """Security testing panel.

    Coordinates security scanning and displays results.
    """

    def __init__(self, browser_area):
        super().__init__()
        self.browser = browser_area
        self.scanner = SecurityScanner()
        self.report_gen = SecurityReportGenerator()
        self._setup_ui()

    def scan_current_page(self):
        """Scan the currently active page."""
        tab = self.browser.current_tab()
        if not tab:
            return

        url = tab.url()
        page = tab.page

        # Run all security checks
        self.scanner.scan(url, page, callback=self._on_scan_complete)

    def _on_scan_complete(self, result: SecurityScanResult):
        """Handle scan completion."""
        # Update UI with results
        self._display_results(result)

        # Show notification
        if result.critical_count > 0:
            self._show_notification(
                f"⚠️  {result.critical_count} critical security issues found!"
            )
```

### 11.4 Security Scanner Architecture

**security/scanner.py:**

```python
from PySide6.QtCore import QObject, Signal
from typing import Callable, List

class SecurityScanner(QObject):
    """Coordinates all security checks.

    Architecture:
    - Modular checkers (headers, cookies, forms, TLS)
    - Asynchronous scanning
    - Extensible rule system
    - Progress reporting
    """

    scan_started = Signal(str)  # url
    scan_progress = Signal(int)  # percentage
    scan_completed = Signal(SecurityScanResult)

    def __init__(self):
        super().__init__()
        # Initialize checkers
        self.checkers = {
            "headers": SecurityHeadersChecker(),
            "cookies": CookieSecurityChecker(),
            "forms": FormSecurityChecker(),
            "tls": TLSChecker(),
            "content": ContentSecurityChecker(),
        }

    def scan(self, url: str, page, callback: Callable):
        """Run all security checks on page."""
        self.scan_started.emit(url)

        issues = []
        passed = []

        # Run each checker
        total = len(self.checkers)
        for idx, (name, checker) in enumerate(self.checkers.items()):
            # Update progress
            progress = int((idx / total) * 100)
            self.scan_progress.emit(progress)

            # Run checker
            checker_issues, checker_passed = checker.check(url, page)
            issues.extend(checker_issues)
            passed.extend(checker_passed)

        # Calculate security score
        score = self._calculate_score(issues, passed)

        # Create result
        result = SecurityScanResult(
            url=url,
            scan_time=datetime.now(),
            score=score,
            issues=issues,
            passed_checks=passed
        )

        # Notify
        self.scan_completed.emit(result)
        callback(result)

    def _calculate_score(self, issues: List, passed: List) -> int:
        """Calculate security score (0-100)."""
        total_checks = len(issues) + len(passed)
        if total_checks == 0:
            return 100

        # Weight by severity
        deductions = sum(
            {"critical": 25, "high": 15, "medium": 5, "low": 2}.get(
                issue.severity, 0
            )
            for issue in issues
        )

        score = max(0, 100 - deductions)
        return score
```

### 11.5 Security Checkers

**security/checkers/headers.py:**

```python
class SecurityHeadersChecker:
    """Check HTTP security headers."""

    # Security header rules
    REQUIRED_HEADERS = {
        "strict-transport-security": {
            "severity": "high",
            "description": "HSTS forces HTTPS connections",
            "recommendation": "Add HSTS: max-age=31536000; includeSubDomains",
        },
        "content-security-policy": {
            "severity": "high",
            "description": "CSP prevents XSS attacks",
            "recommendation": "Implement strict CSP policy",
        },
        "x-content-type-options": {
            "severity": "medium",
            "description": "Prevents MIME sniffing attacks",
            "recommendation": "Add X-Content-Type-Options: nosniff",
        },
        "x-frame-options": {
            "severity": "medium",
            "description": "Prevents clickjacking attacks",
            "recommendation": "Add X-Frame-Options: DENY or SAMEORIGIN",
        },
    }

    def check(self, url: str, page) -> Tuple[List[SecurityIssue], List[str]]:
        """Check security headers."""
        issues = []
        passed = []

        # Get response headers (via QNetworkReply)
        headers = self._get_headers(page)

        for header_name, rule in self.REQUIRED_HEADERS.items():
            if header_name not in headers:
                issues.append(
                    SecurityIssue(
                        category="headers",
                        severity=rule["severity"],
                        title=f"Missing {header_name}",
                        description=rule["description"],
                        recommendation=rule["recommendation"],
                        fix_code=self._generate_fix_code(header_name),
                    )
                )
            else:
                passed.append(f"{header_name} present")

        return issues, passed
```

**security/checkers/cookies.py:**

```python
class CookieSecurityChecker:
    """Audit cookie security attributes."""

    def check(self, url: str, page) -> Tuple[List, List]:
        """Check cookies for security attributes."""
        issues = []
        passed = []

        # Get cookies from QWebEngineCookieStore
        cookies = self._get_cookies(page)

        for cookie in cookies:
            # Check each security attribute
            if not cookie.isSecure():
                issues.append(
                    SecurityIssue(
                        category="cookies",
                        severity="high",
                        title=f"Cookie '{cookie.name()}' missing Secure flag",
                        description="Cookie can be sent over HTTP",
                        recommendation="Set Secure flag on all cookies",
                        fix_code=f"Set-Cookie: {cookie.name()}=...; Secure",
                    )
                )

            if not cookie.isHttpOnly():
                issues.append(
                    SecurityIssue(
                        category="cookies",
                        severity="medium",
                        title=f"Cookie '{cookie.name()}' missing HttpOnly",
                        description="Cookie accessible to JavaScript (XSS risk)",
                        recommendation="Set HttpOnly flag",
                        fix_code=f"Set-Cookie: {cookie.name()}=...; HttpOnly",
                    )
                )

            # Check SameSite attribute
            if cookie.sameSitePolicy() == QWebEngineCookie.SameSiteNone:
                issues.append(
                    SecurityIssue(
                        category="cookies",
                        severity="medium",
                        title=f"Cookie '{cookie.name()}' has SameSite=None",
                        description="Vulnerable to CSRF attacks",
                        recommendation="Set SameSite=Lax or Strict",
                    )
                )

        return issues, passed
```

### 11.6 Security Report Generator

**security/report_generator.py:**

```python
class SecurityReportGenerator:
    """Generate security reports in multiple formats."""

    def generate_html(self, result: SecurityScanResult) -> str:
        """Generate HTML report."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Report - {url}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .critical {{ color: #d32f2f; font-weight: bold; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #689f38; }}
                .pass {{ color: #388e3c; }}
                .score {{ font-size: 48px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>🔒 Security Scan Report</h1>
            <p><strong>URL:</strong> {url}</p>
            <p><strong>Scan Date:</strong> {scan_time}</p>

            <h2>Security Score</h2>
            <div class="score" style="color: {score_color};">{score}/100</div>

            <h2>Summary</h2>
            <ul>
                <li class="critical">Critical: {critical_count}</li>
                <li class="high">High: {high_count}</li>
                <li class="medium">Medium: {medium_count}</li>
                <li class="low">Low: {low_count}</li>
                <li class="pass">Passed: {passed_count}</li>
            </ul>

            <h2>Detailed Findings</h2>
            {issues_html}

            <h2>Recommendations</h2>
            {recommendations_html}
        </body>
        </html>
        """

        return template.format(
            url=result.url,
            scan_time=result.scan_time,
            score=result.score,
            score_color=self._score_color(result.score),
            critical_count=result.critical_count,
            high_count=result.high_count,
            # ... etc
        )

    def generate_json(self, result: SecurityScanResult) -> str:
        """Generate JSON report for CI/CD integration."""
        return json.dumps({
            "url": result.url,
            "scan_time": result.scan_time.isoformat(),
            "score": result.score,
            "issues": [
                {
                    "category": issue.category,
                    "severity": issue.severity,
                    "title": issue.title,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                }
                for issue in result.issues
            ],
            "passed_checks": result.passed_checks,
        }, indent=2)

    def generate_pdf(self, result: SecurityScanResult, output_path: str):
        """Generate PDF report using QPrinter."""
        # Convert HTML to PDF using Qt's printing
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtWebEngineWidgets import QWebEngineView

        html = self.generate_html(result)
        # ... PDF generation logic
```

### 11.7 Ethical Use Enforcement

**security/ethical_guardian.py:**

```python
class EthicalGuardian:
    """Enforce ethical use of security tools.

    - Show disclaimer on first use
    - Log all security scans
    - Require explicit consent
    - Provide educational context
    """

    def __init__(self):
        self.settings = QSettings("VFWidgets", "ViloWeb")
        self.consent_given = self.settings.value("security/consent", False, bool)

    def check_consent(self) -> bool:
        """Check if user has given ethical use consent."""
        if not self.consent_given:
            # Show ethical use dialog
            dialog = EthicalUseDialog()
            if dialog.exec() == QDialog.Accepted:
                self.consent_given = True
                self.settings.setValue("security/consent", True)
                return True
            return False
        return True

    def log_scan(self, url: str, scan_type: str):
        """Log security scan for accountability."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "scan_type": scan_type,
        }
        # Append to local log file
        with open(self._get_log_path(), "a") as f:
            f.write(json.dumps(log_entry) + "\n")

class EthicalUseDialog(QDialog):
    """Dialog showing ethical use agreement."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Testing - Ethical Use")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Warning text (from SPECIFICATION.md)
        warning = QLabel("""
        SECURITY TESTING - ETHICAL USE ONLY

        ViloWeb security tools are for DEFENSIVE security:

        ✓ Testing YOUR OWN web applications
        ✓ Learning security concepts
        ✓ Security research with permission
        ✓ Educational demonstrations

        ✗ DO NOT test applications without permission
        ✗ DO NOT use for malicious purposes
        ✗ DO NOT attack systems you don't own

        Unauthorized security testing may be illegal.
        Always obtain written permission before testing.
        """)
        layout.addWidget(warning)

        # Checkbox
        self.checkbox = QCheckBox(
            "I understand and agree to use security tools ethically"
        )
        layout.addWidget(self.checkbox)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept(self):
        if not self.checkbox.isChecked():
            QMessageBox.warning(
                self,
                "Agreement Required",
                "You must agree to ethical use to enable security tools."
            )
            return
        super().accept()
```

### 11.8 Security Testing Data Flow

```
User clicks "Scan" button
       │
       ▼
SecurityPanel.scan_current_page()
       │
       ▼
EthicalGuardian.check_consent()
       │
       ├─ No consent: Show ethical use dialog
       │               User must agree
       │
       └─ Consent given
           │
           ▼
       SecurityScanner.scan(url, page)
           │
           ├──> HeadersChecker.check()
           │        │
           │        └─> Returns issues + passed checks
           │
           ├──> CookieChecker.check()
           ├──> FormChecker.check()
           ├──> TLSChecker.check()
           └──> ContentChecker.check()
           │
           ▼
       Calculate security score
           │
           ▼
       Create SecurityScanResult
           │
           ▼
       Display results in SecurityPanel
           │
           ├──> Update UI (score, issues list)
           ├──> Show notification
           └──> Enable report export
```

---

## Architecture Summary

**ViloWeb** is architected as an educational platform demonstrating:

1. **VFWidgets Integration**: Real-world use of ChromeTabbedWindow, ViloCodeWindow, and theme system
2. **Qt/PySide6 Patterns**: Signals/slots, model/view, threading, and inter-process communication
3. **Web Technologies**: QWebEngine, JavaScript bridge via QWebChannel, DOM manipulation
4. **Python Extensibility**: Unique extension system using Python instead of JavaScript
5. **Clean Architecture**: Separation of concerns, protocol-based design, testable components

**Key Learning Objectives:**
- Master QWebEngineView and QWebEnginePage APIs
- Understand JavaScript-Python bridge patterns
- Build browser automation tools with Python
- Create browser extensions in Python
- Integrate VFWidgets components professionally

**Next Steps:**
1. Review SPECIFICATION.md for feature details
2. Review UI-MOCKUPS.md for interface designs
3. Begin Phase 1 implementation (foundation + console)
4. Build example extensions as learning material

---

**Questions?** See SPECIFICATION.md for detailed requirements or README.md for quick start guide.
