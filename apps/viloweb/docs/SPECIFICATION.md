# ViloWeb Browser - Technical Specification

**Version:** 0.1.0-dev
**Status:** Design Phase
**Target Release:** Q1 2026
**Project Type:** Educational Browser & VFWidgets Showcase

---

## Executive Summary

**ViloWeb** is an educational web browser and comprehensive showcase for the VFWidgets ecosystem, designed to teach developers how to control QWebEngineView with Python while demonstrating professional Qt/PySide6 application development. Built on QtWebEngine (Chromium), ViloWeb serves as both a learning platform for browser automation and a living demonstration of VFWidgets' capabilities.

**Primary Purpose:** Educational platform for learning Python-based web automation, browser extension development, and showcasing VFWidgets components in a real-world application.

**Key Differentiators:**
1. **Python-First Extensions**: Write browser extensions in Python, not JavaScript
2. **VFWidgets Showcase**: Every major VFWidgets component demonstrated
3. **Learning Platform**: Extensively commented code, tutorials, examples
4. **Developer Experience**: Built for developers learning QtWebEngine
5. **Web Automation**: Python scripts to control and modify web pages

**Technology Foundation:**
- **Rendering**: QtWebEngine (Chromium-based, standards-compliant)
- **UI Framework**: ChromeTabbedWindow + ViloCodeWindow (showcase)
- **Theme System**: vfwidgets-theme (demonstrates theming)
- **Extensions**: Python-based (unique approach)
- **Platform**: Cross-platform (Linux, Windows, macOS, WSL)

---

## 1. Vision & Goals

### 1.1 Vision Statement

Create an educational web browser that teaches developers how to programmatically control web content with Python while serving as a comprehensive showcase for VFWidgets components and professional Qt application architecture.

ViloWeb aims to be:
- **Educational**: Learn QWebEngineView, JavaScript bridges, DOM manipulation
- **Showcase**: Demonstrate all major VFWidgets in real-world use
- **Extensible**: Python-based extensions that modify web pages
- **Well-Documented**: Every feature explained with tutorials
- **Developer-Friendly**: Code designed for learning, not just functionality

### 1.2 Primary Goals (In Priority Order)

1. **Developer Experience & Learning**:
   - Teach QtWebEngine programming patterns
   - Demonstrate Python-to-JavaScript bridges
   - Show DOM manipulation from Python
   - Provide extensive code documentation
   - Include step-by-step tutorials

2. **VFWidgets Showcase**:
   - ChromeTabbedWindow (tab management)
   - ViloCodeWindow (sidebar panels, activity bar)
   - vfwidgets-theme (theming integration)
   - vfwidgets-multisplit (optional: split screen browsing)

3. **Python Extension System**:
   - Write extensions in Python (not JavaScript)
   - Python scripts can modify web pages
   - Access to Qt and PySide6 APIs
   - Direct DOM manipulation via JavaScript bridge
   - Examples: ad blocker, page modifier, automation scripts

4. **Browser Automation**:
   - Python API for controlling browser
   - Scriptable navigation and interaction
   - Form filling and data extraction
   - Screenshot and PDF generation
   - Testing framework for web apps

5. **Security Testing (Defensive)**:
   - HTTP security headers analysis
   - TLS/certificate inspection
   - Cookie and session security audit
   - CSP analyzer
   - Form security checker
   - Security scanner extension
   - Educational security tutorials
   - **DEFENSIVE ONLY**: Test your own applications

6. **Modern Browser Features**:
   - Multi-tab browsing
   - Bookmarks and history
   - Downloads manager
   - Developer tools
   - (But with educational focus)

### 1.3 Success Metrics

**Phase 1 (MVP - Month 1):**
- Multi-tab browsing with <50ms tab switching
- Full navigation controls (back/forward/refresh/stop)
- Basic bookmarks management
- HTTPS security indicators
- 100% theme system integration

**Phase 2 (Core Features - Month 3):**
- Full history tracking with search
- Downloads manager with pause/resume
- Context menus (page, link, image, selection)
- Find in page functionality
- Zoom controls (25%-500%)

**Phase 3 (Power User - Month 6):**
- Extension system with Chrome Web Store compatibility
- Session management (save/restore windows)
- Private browsing mode
- Developer tools integration
- Password manager with encryption

**Phase 4 (Advanced - Month 12):**
- Multi-profile support
- Cloud sync (bookmarks, history, passwords)
- Tab groups and workspaces
- Advanced privacy controls
- Custom search engines

---

## 2. User Personas

### Persona 1: Python Developer Learning QtWebEngine (PRIMARY)
**Background**: Python developer wanting to learn browser automation and web scraping
**Technical Level**: Intermediate Python, new to Qt/PySide6
**Goal**: Learn how to control web browsers programmatically with Python
**Pain Points**: QtWebEngine documentation is sparse, few Python examples, hard to bridge Python and JavaScript
**Needs**:
- Clear code examples
- Tutorials on JavaScript bridge
- DOM manipulation patterns
- Real working code to study
- Step-by-step guides

**Key Features for This Persona:**
- Extensively commented codebase
- Python extension examples (ad blocker, page modifier)
- JavaScript bridge demonstrations
- DOM manipulation tutorials
- Browser automation API
- Built-in Python console for live experimentation

**Learning Objectives:**
1. Understand QWebEngineView architecture
2. Master JavaScript bridge (QWebChannel)
3. Learn DOM manipulation from Python
4. Build Python-based browser extensions
5. Automate web tasks with Python

### Persona 2: VFWidgets Developer (SECONDARY)
**Background**: Qt/PySide6 developer evaluating VFWidgets for their project
**Technical Level**: Advanced Qt knowledge
**Goal**: See VFWidgets components in action before using them
**Pain Points**: Need to see real-world usage, not just examples
**Needs**:
- Professional application demonstrating all widgets
- Best practices for widget integration
- Theme system usage patterns
- Performance characteristics
- Real-world architecture

**Key Features for This Persona:**
- Every VFWidgets component showcased
- ChromeTabbedWindow in complex use case
- ViloCodeWindow with multiple panels
- Theme system integration examples
- Professional code architecture

### Persona 3: Web Automation Engineer (TERTIARY)
**Background**: Test engineer or data scientist needing browser automation
**Technical Level**: Intermediate Python, familiar with Selenium
**Goal**: Automate web tasks, scrape data, test web applications
**Pain Points**: Selenium is slow, Playwright is JavaScript-focused, need Python solution
**Needs**:
- Python API for browser control
- Scriptable web interactions
- Data extraction tools
- Screenshot/PDF capabilities
- Headless mode support

**Key Features for This Persona:**
- Python automation API
- Script recording/playback
- Element selection helpers
- Form filling utilities
- Data extraction patterns
- Testing framework integration

### Persona 4: Security Tester / Developer (QUATERNARY)
**Background**: Developer or security professional testing web application security
**Technical Level**: Intermediate to advanced in web security concepts
**Goal**: Learn web security, test own applications for vulnerabilities, understand secure coding practices
**Pain Points**: Most security tools are complex, expensive, or designed for pentesters, not developers. Hard to learn security concepts with practical tools.
**Needs**:
- Educational security testing tools
- Clear explanations of security concepts
- Safe environment to learn about vulnerabilities
- Automated security scanning
- Reports to improve application security

**Key Features for This Persona:**
- Security testing panel with header analysis
- TLS/certificate inspection
- Cookie and session security auditing
- CSP (Content Security Policy) analyzer
- Form security checker
- Security scanner extension (Python)
- Educational security tutorials
- Security report generation

**Learning Objectives:**
1. Understand HTTP security headers (CSP, HSTS, X-Frame-Options)
2. Learn TLS/certificate validation
3. Identify common security misconfigurations
4. Test own web applications for vulnerabilities
5. Generate security reports for remediation
6. Learn secure coding practices

**Ethical Guidelines:**
- ✓ Test YOUR OWN applications only
- ✓ Learn security concepts
- ✓ Security research with permission
- ✗ Never test without authorization
- ✗ Never use for malicious purposes

---

## 3. Core Architecture

### 3.1 Technology Stack

```
Foundation Layer:
├── PySide6 6.9+              # Qt framework
├── QtWebEngine 6.9+          # Chromium rendering engine
└── Python 3.9+               # Language

VFWidgets Layer:
├── chrome-tabbed-window      # Tab bar with Chrome styling
├── vfwidgets-vilocode-window # VS Code-style window layout
├── vfwidgets-theme           # Unified theme system
└── vfwidgets-common          # Platform utilities, webview helpers

Storage Layer:
├── SQLite 3.x               # History, downloads, passwords
├── JSON                     # Bookmarks, settings, session state
└── QSettings                # Qt native preferences

Security Layer:
├── QtWebEngine Security     # Sandboxing, process isolation
├── Cryptography Library     # Password encryption
└── Certificate Management   # SSL/TLS validation
```

### 3.2 Process Architecture

ViloWeb uses a multi-process architecture similar to Chrome:

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Process                       │
│  (Main Python app, UI, bookmarks, history, settings)   │
└────────┬─────────────────────────────────────┬──────────┘
         │                                     │
    ┌────▼─────────────────┐        ┌─────────▼──────────┐
    │  Renderer Process 1  │        │ Renderer Process 2  │
    │  (Tab 1 web content) │        │ (Tab 2 web content) │
    └──────────────────────┘        └─────────────────────┘
         │                                     │
    ┌────▼─────────────────┐        ┌─────────▼──────────┐
    │    GPU Process       │        │   Plugin Process    │
    │  (Hardware accel)    │        │  (Extensions)       │
    └──────────────────────┘        └─────────────────────┘
```

**Key Benefits:**
- **Isolation**: One tab crash doesn't affect others
- **Security**: Renderer processes are sandboxed
- **Performance**: Parallel processing of multiple tabs
- **Memory**: Per-tab resource limits and suspension

### 3.3 Component Hierarchy

```
ViloWebWindow (extends ViloCodeWindow)
├── MenuBar
│   ├── File Menu (New Tab, New Window, Close Tab, Exit)
│   ├── Edit Menu (Cut, Copy, Paste, Find)
│   ├── View Menu (Zoom, Full Screen, Developer Tools)
│   ├── History Menu (Recent, Clear History)
│   ├── Bookmarks Menu (Add, Manage, Show All)
│   └── Tools Menu (Downloads, Extensions, Settings)
│
├── ChromeTabbedWindow (main_pane)
│   ├── TabBar (Chrome-style tabs)
│   │   ├── Tab 1 (title, favicon, close button)
│   │   ├── Tab 2 (title, favicon, close button)
│   │   └── New Tab Button (+)
│   │
│   └── Tab Content Stack
│       ├── BrowserTab 1
│       │   ├── NavigationBar
│       │   │   ├── Back Button
│       │   │   ├── Forward Button
│       │   │   ├── Refresh/Stop Button
│       │   │   ├── Home Button
│       │   │   ├── AddressBar (URL + search)
│       │   │   │   ├── Security Icon (HTTPS lock)
│       │   │   │   ├── URL Text Input
│       │   │   │   ├── Bookmark Star
│       │   │   │   └── Extension Icons
│       │   │   └── Menu Button (⋮)
│       │   │
│       │   └── QWebEngineView (web content)
│       │       └── QWebEnginePage (JavaScript, DOM)
│       │
│       └── BrowserTab 2...
│
├── Sidebar (ViloCodeWindow panels)
│   ├── Home Panel
│   │   ├── Frequently Visited
│   │   ├── Recent Bookmarks
│   │   └── Quick Links
│   │
│   ├── Bookmarks Panel
│   │   ├── Search Bar
│   │   ├── Folder Tree
│   │   └── Bookmark List (title, URL, favicon)
│   │
│   ├── History Panel
│   │   ├── Search Bar
│   │   ├── Date Groups (Today, Yesterday, Last 7 Days)
│   │   └── History Items (time, title, URL)
│   │
│   ├── Downloads Panel
│   │   ├── Active Downloads (progress, speed, pause/resume)
│   │   └── Completed Downloads (open, show in folder)
│   │
│   └── Extensions Panel
│       ├── Installed Extensions
│       ├── Extension Settings
│       └── Chrome Web Store Link
│
├── ActivityBar (ViloCodeWindow sidebar selector)
│   ├── Home Icon
│   ├── Bookmarks Icon
│   ├── History Icon
│   ├── Downloads Icon
│   └── Extensions Icon
│
└── StatusBar
    ├── Page Load Progress
    ├── Security Status (HTTPS/HTTP)
    ├── Zoom Level (100%)
    ├── Extension Status Icons
    └── Status Messages (Hover links, loading status)
```

### 3.4 Data Models

#### 3.4.1 Tab Model

```python
@dataclass
class Tab:
    """Represents a browser tab."""
    tab_id: str                      # Unique identifier
    url: str                         # Current URL
    title: str                       # Page title
    favicon: QIcon | None            # Page favicon
    loading: bool                    # Is page loading?
    progress: int                    # Load progress (0-100)
    secure: bool                     # HTTPS connection?
    can_go_back: bool                # Has history to go back?
    can_go_forward: bool             # Has history to go forward?
    pinned: bool                     # Is tab pinned?
    muted: bool                      # Is audio muted?
    last_accessed: datetime          # For tab sorting
    web_view: QWebEngineView         # The actual web view
```

#### 3.4.2 Bookmark Model

```python
@dataclass
class Bookmark:
    """Represents a bookmark entry."""
    id: str                          # Unique identifier
    title: str                       # Bookmark title
    url: str                         # Bookmark URL
    folder: str                      # Parent folder path
    added: datetime                  # When added
    modified: datetime               # Last modification
    tags: list[str]                  # Tags for organization
    favicon: bytes | None            # Cached favicon data
    description: str                 # Optional description
```

#### 3.4.3 History Model

```python
@dataclass
class HistoryEntry:
    """Represents a history entry."""
    id: int                          # Auto-increment ID
    url: str                         # Visited URL
    title: str                       # Page title
    visit_time: datetime             # When visited
    visit_count: int                 # Number of visits
    typed_count: int                 # Times typed manually
    last_visit: datetime             # Most recent visit
    duration: int                    # Time spent (seconds)
```

#### 3.4.4 Download Model

```python
@dataclass
class Download:
    """Represents a download."""
    id: str                          # Unique identifier
    url: str                         # Download URL
    path: str                        # Save path
    filename: str                    # File name
    size: int                        # Total size (bytes)
    downloaded: int                  # Downloaded bytes
    state: DownloadState             # PENDING/ACTIVE/PAUSED/COMPLETE/FAILED
    speed: int                       # Download speed (bytes/sec)
    start_time: datetime             # When started
    end_time: datetime | None        # When completed
    error: str | None                # Error message if failed
    mime_type: str                   # Content type
```

---

## 4. Feature Specifications

### Phase 1: Foundation (MVP) - Weeks 1-2

**Goal**: Basic multi-tab browser with bookmarks

#### 4.1.1 Multi-Tab Browsing
- ✅ ChromeTabbedWindow integration
- ✅ Add new tab button (+)
- ✅ Close tab button (x) on each tab
- ✅ Tab title updates with page title
- ✅ Tab favicon updates with page icon
- ✅ Tab switching via clicking or Ctrl+Tab
- ✅ Tab reordering via drag & drop
- ✅ Tab context menu (Reload, Close, Close Others, Pin)

**Technical Implementation:**
```python
class BrowserTab(QWidget):
    """Individual browser tab with web view."""

    # Signals
    titleChanged = Signal(str)
    urlChanged = Signal(str)
    loadProgressChanged = Signal(int)
    secureChanged = Signal(bool)

    def __init__(self):
        self.web_view = QWebEngineView()
        self.nav_bar = NavigationBar()
        # Layout: nav_bar on top, web_view below
```

#### 4.1.2 Navigation Controls
- ✅ Back button (← with keyboard Alt+Left)
- ✅ Forward button (→ with keyboard Alt+Right)
- ✅ Refresh button (⟳ with keyboard F5 or Ctrl+R)
- ✅ Stop button (✕ shown during loading)
- ✅ Home button (🏠 navigates to home page)
- ✅ Navigation state updates (disabled when no history)

#### 4.1.3 Address Bar
- ✅ URL text input with editing
- ✅ Security indicator (🔒 for HTTPS, ⚠️ for HTTP)
- ✅ Bookmark star button (☆/★ toggle)
- ✅ Enter to navigate
- ✅ Ctrl+L to focus address bar
- ✅ URL validation and correction
- ✅ Protocol auto-addition (https://)

#### 4.1.4 Basic Bookmarks
- ✅ Add bookmark (Ctrl+D or star button)
- ✅ Remove bookmark (click star again)
- ✅ Bookmarks panel in sidebar
- ✅ Bookmark list with icons
- ✅ Double-click to open bookmark
- ✅ Right-click context menu (Open, Delete, Edit)
- ✅ JSON persistence (~/.viloweb/bookmarks.json)

#### 4.1.5 Theme Integration
- ✅ Automatic theme color adaptation
- ✅ Dark/Light mode support
- ✅ Chrome tab styling from theme
- ✅ Consistent with other VFWidgets apps

**Success Criteria:**
- Can browse any website with multiple tabs
- Tabs switch in <50ms
- Bookmarks persist across sessions
- No crashes or memory leaks after 1 hour use
- Looks professional with default theme

---

### Phase 2: Core Features - Weeks 3-4

**Goal**: History, downloads, context menus, find in page

#### 4.2.1 History Tracking
- SQLite database storage
- Automatic history recording on page load
- Visit count and last visit time
- History panel in sidebar
- Search history by title/URL
- Date grouping (Today, Yesterday, Last 7 Days, Older)
- Clear history (all, range, specific sites)
- Privacy: Incognito mode doesn't save history

**Database Schema:**
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visit_count INTEGER DEFAULT 1,
    typed_count INTEGER DEFAULT 0,
    last_visit TIMESTAMP,
    duration INTEGER DEFAULT 0,
    UNIQUE(url, DATE(visit_time))
);

CREATE INDEX idx_history_url ON history(url);
CREATE INDEX idx_history_time ON history(visit_time DESC);
```

#### 4.2.2 Downloads Manager
- QWebEngineDownloadRequest handling
- Downloads panel in sidebar
- Active downloads with progress bars
- Pause/Resume/Cancel buttons
- Download speed indicator
- Completed downloads list
- Open file or show in folder
- Download history in database
- Configurable download directory

**UI Components:**
```
Downloads Panel
├── Active Downloads
│   ├── File 1 (progress: 45%, speed: 2.5 MB/s)
│   │   [Pause] [Cancel]
│   └── File 2 (progress: 90%, speed: 1.2 MB/s)
│       [Pause] [Cancel]
│
└── Completed Downloads
    ├── File 3 (today, 3.2 MB)
    │   [Open] [Show in Folder] [Delete]
    └── File 4 (yesterday, 15 MB)
        [Open] [Show in Folder] [Delete]
```

#### 4.2.3 Context Menus
All context menus follow Qt style with icons and keyboard shortcuts.

**Page Context Menu** (right-click on page):
- Back
- Forward
- Reload
- ---
- Save Page As...
- Print...
- ---
- View Page Source
- Inspect Element (DevTools)

**Link Context Menu** (right-click on link):
- Open Link in New Tab
- Open Link in New Window
- Open Link in Incognito Window
- ---
- Copy Link Address
- Save Link As...
- ---
- Bookmark This Link

**Image Context Menu** (right-click on image):
- Open Image in New Tab
- Save Image As...
- Copy Image
- Copy Image Address
- ---
- Search Image with Google

**Text Selection Context Menu**:
- Cut (Ctrl+X)
- Copy (Ctrl+C)
- Paste (Ctrl+V)
- ---
- Search with Google
- ---
- Inspect Element

#### 4.2.4 Find in Page
- Find bar (Ctrl+F)
- Search input with match count (e.g., "3 of 25")
- Previous/Next buttons
- Match case toggle
- Highlight all matches
- Close with Escape
- Keyboard navigation (F3/Shift+F3)

**UI Design:**
```
┌─────────────────────────────────────────────────────┐
│ Find in page: [search text     ] ⌃ ⌄ [3 of 25]  ✕  │
│               [Match case] [Highlight all]          │
└─────────────────────────────────────────────────────┘
```

#### 4.2.5 Zoom Controls
- Zoom in (Ctrl++ or Ctrl+Scroll Up)
- Zoom out (Ctrl+- or Ctrl+Scroll Down)
- Reset zoom (Ctrl+0)
- Zoom range: 25% to 500%
- Per-tab zoom level
- Zoom indicator in status bar
- Zoom menu in View menu

---

### Phase 3: Advanced Features - Weeks 5-8

**Goal**: Session management, private mode, DevTools, passwords

#### 4.3.1 Session Management
- Save window state on close
- Restore tabs on startup (configurable)
- Session JSON format
- Named sessions (save/load)
- Recent sessions list
- Crash recovery

**Session Data Model:**
```python
@dataclass
class Session:
    """Browser session state."""
    session_id: str
    name: str
    created: datetime
    windows: list[WindowState]

@dataclass
class WindowState:
    """Window state in session."""
    window_id: str
    geometry: QRect
    active_tab_index: int
    tabs: list[TabState]

@dataclass
class TabState:
    """Tab state in session."""
    url: str
    title: str
    scroll_position: int
    zoom_level: float
    history: list[str]  # Navigation history
```

#### 4.3.2 Private Browsing Mode
- Incognito window (Ctrl+Shift+N)
- No history recording
- No cookie persistence
- Isolated web storage
- Session-only data
- Visual indicator (dark theme, spy icon)
- Separate process group

#### 4.3.3 Developer Tools Integration
- Chrome DevTools embedded (F12)
- Inspect element from context menu
- Console access
- Network tab with requests
- Elements tree
- Sources with debugger
- Application storage viewer
- Dock position (bottom, right, separate window)

**Implementation:**
```python
def show_dev_tools(self):
    """Show Chrome DevTools for current tab."""
    dev_tools = QWebEngineView()
    current_page = self.current_tab.web_view.page()
    current_page.setDevToolsPage(dev_tools.page())

    # Show in dialog or dock
    self.dev_tools_dialog.setCentralWidget(dev_tools)
    self.dev_tools_dialog.show()
```

#### 4.3.4 Password Manager
- Detect login forms
- Offer to save passwords
- Encrypted password storage (AES-256)
- Auto-fill saved credentials
- Password generator
- Master password protection
- Import/export passwords
- Breach detection warnings

**Database Schema:**
```sql
CREATE TABLE passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    username TEXT NOT NULL,
    password BLOB NOT NULL,  -- Encrypted
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP,
    UNIQUE(url, username)
);
```

#### 4.3.5 Settings Dialog
Comprehensive settings organized in tabs:

**General:**
- Default page (home, new tab, blank)
- Download location
- Default zoom level
- Restore tabs on startup

**Appearance:**
- Theme selection (VFWidgets themes)
- Font size
- Show/hide bookmarks bar
- Tab bar position

**Privacy & Security:**
- Clear browsing data
- Cookie settings
- Site permissions (camera, mic, location)
- HTTPS-only mode
- Do Not Track

**Search:**
- Default search engine
- Search engine management
- Address bar suggestions

**Advanced:**
- Hardware acceleration
- Proxy settings
- Content settings
- Language preferences

---

### Phase 4: Power Features - Weeks 9-12

**Goal**: Extensions, profiles, sync, tab groups

#### 4.4.1 Extension System
**Architecture:**
```
Extensions Directory: ~/.viloweb/extensions/
├── extension_id_1/
│   ├── manifest.json       # Extension metadata
│   ├── background.js       # Background script
│   ├── content.js          # Content scripts
│   ├── popup.html          # Popup UI
│   └── icons/              # Extension icons
└── extension_id_2/
    └── ...
```

**Chrome Extension API Compatibility:**
- chrome.tabs API (create, update, close, query)
- chrome.windows API (create, update, remove)
- chrome.bookmarks API (CRUD operations)
- chrome.history API (search, delete)
- chrome.storage API (sync, local)
- chrome.runtime API (messaging, events)
- chrome.contextMenus API (custom menus)
- chrome.webRequest API (intercept requests)

**Extension Manager UI:**
- Installed extensions list
- Enable/disable toggle
- Extension settings/options
- Remove extension
- Chrome Web Store link
- Developer mode (load unpacked)

#### 4.4.2 Multi-Profile Support
- Profile creation/deletion
- Profile switching without restart
- Isolated data (bookmarks, history, passwords, extensions)
- Profile icons and names
- Guest profile (temporary)
- Profile management dialog

**Profile Directory Structure:**
```
~/.viloweb/
├── profiles/
│   ├── default/
│   │   ├── bookmarks.json
│   │   ├── history.db
│   │   ├── passwords.db
│   │   ├── settings.json
│   │   └── extensions/
│   ├── work/
│   │   └── ...
│   └── personal/
│       └── ...
└── profile_manager.json
```

#### 4.4.3 Cloud Sync (Optional)
- Sync bookmarks across devices
- Sync history (last 30 days)
- Sync passwords (encrypted)
- Sync extensions and settings
- Conflict resolution
- Self-hosted sync server option
- Privacy-first approach (end-to-end encryption)

#### 4.4.4 Tab Groups & Workspaces
**Tab Groups:**
- Create named groups
- Color-coded groups
- Collapse/expand groups
- Group context menu
- Save groups as workspace

**Workspaces:**
- Named collections of tab groups
- Quick switching (Ctrl+Shift+W)
- Workspace manager dialog
- Save/load workspaces
- Workspace templates

**UI Design:**
```
Tab Bar with Groups:
[Group: Work ▼] Tab1 Tab2 Tab3  [Group: Personal ▼] Tab4 Tab5  [+]
```

#### 4.4.5 Advanced Search
**Omnibox (Smart Address Bar):**
- Search history by keyword
- Search bookmarks by title/URL
- Search open tabs by title
- Calculator (type "5+3")
- Unit converter (type "10 km to miles")
- Direct answers (weather, time, etc.)
- Custom search engines with keywords
  - Example: "g python tutorial" → Google search
  - Example: "w browser" → Wikipedia search

**History Search:**
- Full-text search
- Filter by date range
- Filter by domain
- Most visited sites
- Recently closed tabs

**Bookmark Search:**
- Full-text search
- Filter by folder
- Filter by tags
- Sort options (date, name, URL)

---

## 5. Python Extensions & Learning Features (UNIQUE TO VILOWEB)

This section describes ViloWeb's **primary differentiator**: Python-based extensions and educational focus.

### 5.1 Python Extension System Architecture

Unlike Chrome's JavaScript-only extensions, ViloWeb extensions are written in **pure Python**, giving full access to:
- Python standard library
- Qt/PySide6 APIs
- Direct DOM manipulation via JavaScript bridge
- File system and network access
- Native UI creation

**Extension Directory Structure:**
```
~/.viloweb/extensions/
├── ad_blocker/
│   ├── extension.py          # Main extension class
│   ├── manifest.json         # Metadata
│   ├── rules.txt             # Ad blocking rules
│   └── ui/
│       └── settings.py       # Settings dialog (Qt)
│
├── page_modifier/
│   ├── extension.py
│   ├── scripts/
│   │   ├── reddit_dark.py    # Reddit dark mode
│   │   └── youtube_clean.py  # YouTube cleaner
│   └── manifest.json
│
└── web_scraper/
    ├── extension.py
    ├── extractors/
    │   ├── amazon.py
    │   └── wikipedia.py
    └── manifest.json
```

### 5.2 Extension API

**Base Extension Class:**
```python
from PySide6.QtCore import QObject, Signal, Slot
from viloweb.api import ExtensionAPI

class ViloWebExtension(QObject):
    """Base class for all ViloWeb extensions."""

    # Extension metadata
    name: str = "My Extension"
    version: str = "1.0.0"
    description: str = "Extension description"
    author: str = "Your Name"

    # Lifecycle signals
    enabled = Signal()
    disabled = Signal()
    page_loaded = Signal(str)  # URL

    def __init__(self, api: ExtensionAPI):
        super().__init__()
        self.api = api  # Access to browser APIs

    def on_activate(self):
        """Called when extension is enabled."""
        pass

    def on_deactivate(self):
        """Called when extension is disabled."""
        pass

    def on_page_load(self, url: str, page: QWebEnginePage):
        """Called after each page loads."""
        pass

    def on_before_navigate(self, url: str) -> bool:
        """Called before navigation. Return False to block."""
        return True

    def on_context_menu(self, menu: QMenu, hit_test: QWebEngineContextMenuData):
        """Add items to context menu."""
        pass
```

### 5.3 Example Extensions (Included)

#### 5.3.1 Ad Blocker Extension

**Purpose**: Block ads and trackers, demonstrate URL filtering

**Features:**
- Block requests matching patterns
- Element hiding via CSS injection
- Custom block rules
- Statistics panel

**Code Example** (`extensions/ad_blocker/extension.py`):
```python
class AdBlockerExtension(ViloWebExtension):
    name = "Ad Blocker"
    version = "1.0.0"

    def __init__(self, api):
        super().__init__(api)
        self.rules = self.load_rules("rules.txt")
        self.blocked_count = 0

    def on_before_navigate(self, url: str) -> bool:
        """Block URLs matching ad patterns."""
        for pattern in self.rules:
            if pattern in url:
                self.blocked_count += 1
                self.api.show_notification(f"Blocked ad: {url}")
                return False  # Block navigation
        return True  # Allow

    def on_page_load(self, url: str, page: QWebEnginePage):
        """Hide ad elements with CSS."""
        css = """
        .ad, .advertisement, [class*='ad-'], [id*='ad-'] {
            display: none !important;
        }
        """
        self.api.inject_css(page, css)

    def load_rules(self, filename: str) -> list[str]:
        """Load blocking rules from file."""
        with open(self.extension_dir / filename) as f:
            return [line.strip() for line in f if line and not line.startswith('#')]
```

#### 5.3.2 Page Modifier Extension

**Purpose**: Modify page appearance and behavior, demonstrate DOM manipulation

**Features:**
- Dark mode for any site
- Font size adjustment
- Element removal
- Custom CSS per domain

**Code Example:**
```python
class PageModifierExtension(ViloWebExtension):
    name = "Page Modifier"
    version = "1.0.0"

    def __init__(self, api):
        super().__init__(api)
        self.custom_styles = {}  # domain -> CSS

    def on_page_load(self, url: str, page: QWebEnginePage):
        """Apply custom styles based on domain."""
        domain = self.api.get_domain(url)

        if domain in self.custom_styles:
            self.api.inject_css(page, self.custom_styles[domain])

        # Universal dark mode toggle
        if self.api.get_setting("dark_mode_enabled"):
            self.apply_dark_mode(page)

    def apply_dark_mode(self, page: QWebEnginePage):
        """Inject dark mode CSS."""
        dark_css = """
        html {
            filter: invert(1) hue-rotate(180deg);
        }
        img, video {
            filter: invert(1) hue-rotate(180deg);
        }
        """
        self.api.inject_css(page, dark_css)

    def on_context_menu(self, menu: QMenu, hit_test):
        """Add 'Toggle Dark Mode' to context menu."""
        action = menu.addAction("Toggle Dark Mode")
        action.triggered.connect(self.toggle_dark_mode)
```

#### 5.3.3 Web Scraper Extension

**Purpose**: Extract data from web pages, demonstrate Python's data processing power

**Features:**
- Extract structured data
- Export to JSON/CSV
- Custom extractors per site
- Batch scraping

**Code Example:**
```python
import json
from bs4 import BeautifulSoup  # Python library!

class WebScraperExtension(ViloWebExtension):
    name = "Web Scraper"
    version = "1.0.0"

    def on_page_load(self, url: str, page: QWebEnginePage):
        """Extract data when page loads."""
        if "amazon.com" in url:
            self.extract_amazon_product(page)
        elif "wikipedia.org" in url:
            self.extract_wikipedia_article(page)

    def extract_amazon_product(self, page: QWebEnginePage):
        """Extract product details from Amazon."""
        # Get page HTML from JavaScript
        page.toHtml(lambda html: self._process_amazon_html(html))

    def _process_amazon_html(self, html: str):
        """Process HTML with Beautiful Soup."""
        soup = BeautifulSoup(html, 'html.parser')

        product = {
            "title": soup.find(id="productTitle").text.strip(),
            "price": soup.find(class_="a-price-whole").text.strip(),
            "rating": soup.find(class_="a-star-rating").text.strip(),
            "reviews": soup.find(id="acrCustomerReviewText").text.strip(),
        }

        # Save to file or display
        self.api.show_notification(f"Extracted: {product['title']}")
        self.save_to_json(product)

    def on_context_menu(self, menu: QMenu, hit_test):
        """Add 'Scrape Page' to context menu."""
        action = menu.addAction("Scrape Current Page")
        action.triggered.connect(self.scrape_current_page)
```

### 5.4 Extension API Methods

**Browser Control:**
```python
# Navigation
api.navigate(url: str)
api.back()
api.forward()
api.reload()

# Tabs
api.new_tab(url: str = None) -> Tab
api.close_tab(tab: Tab)
api.get_current_tab() -> Tab
api.get_all_tabs() -> list[Tab]

# DOM Manipulation
api.inject_javascript(page: QWebEnginePage, js_code: str)
api.inject_css(page: QWebEnginePage, css_code: str)
api.execute_js(page: QWebEnginePage, js_code: str) -> Any  # Returns result

# Element Selection
api.get_element_by_id(page: QWebEnginePage, element_id: str) -> dict
api.get_elements_by_class(page: QWebEnginePage, class_name: str) -> list[dict]
api.query_selector(page: QWebEnginePage, selector: str) -> dict

# Form Interaction
api.fill_form(page: QWebEnginePage, form_data: dict)
api.click_element(page: QWebEnginePage, selector: str)
api.type_text(page: QWebEnginePage, selector: str, text: str)

# Data Extraction
api.get_page_html(page: QWebEnginePage) -> str
api.get_page_text(page: QWebEnginePage) -> str
api.screenshot(page: QWebEnginePage, path: str)
api.pdf_export(page: QWebEnginePage, path: str)

# Storage
api.set_setting(key: str, value: Any)
api.get_setting(key: str, default: Any = None) -> Any
api.store_data(key: str, data: dict)  # JSON storage
api.load_data(key: str) -> dict

# UI
api.show_notification(message: str, duration: int = 3000)
api.show_dialog(title: str, message: str) -> bool
api.add_toolbar_button(icon: QIcon, tooltip: str, callback: Callable)

# Network
api.block_request(url_pattern: str)
api.intercept_request(url_pattern: str, handler: Callable)
api.modify_headers(url_pattern: str, headers: dict)
```

### 5.5 Learning Features & Documentation

#### 5.5.1 Built-in Python Console Panel

**Purpose**: Live experimentation with browser APIs

```
Console Panel (in sidebar):
┌──────────────────────────────────────────────────────────┐
│ Python Console                                   [Clear] │
├──────────────────────────────────────────────────────────┤
│ >>> tab = browser.current_tab                            │
│ <BrowserTab url='https://example.com'>                   │
│                                                           │
│ >>> tab.execute_js("document.title")                     │
│ 'Example Domain'                                         │
│                                                           │
│ >>> tab.inject_css("body { background: red; }")         │
│ True                                                      │
│                                                           │
│ >>> elements = tab.query_selector_all(".link")          │
│ [<Element id='link1'>, <Element id='link2'>]            │
│                                                           │
│ >>> _                                                     │
│                                                           │
└──────────────────────────────────────────────────────────┘

Features:
- Full Python REPL
- Access to current tab: `browser.current_tab`
- Access to all tabs: `browser.tabs`
- Access to extension API: `browser.api`
- Code completion
- Syntax highlighting
- History (up/down arrows)
```

#### 5.5.2 Extension Template Generator

**Purpose**: Quick start for new extensions

```bash
$ viloweb create-extension my_extension
Creating extension: my_extension
✓ Created directory: ~/.viloweb/extensions/my_extension/
✓ Created extension.py from template
✓ Created manifest.json
✓ Created README.md
✓ Created tests/test_my_extension.py

Next steps:
1. Edit extension.py to add your logic
2. Test with: viloweb test-extension my_extension
3. Enable in browser: Extensions > Enable 'my_extension'
```

**Generated Template:**
```python
# ~/.viloweb/extensions/my_extension/extension.py
from viloweb.api import ViloWebExtension

class MyExtension(ViloWebExtension):
    """TODO: Describe your extension."""

    name = "My Extension"
    version = "1.0.0"
    description = "TODO: What does this extension do?"
    author = "Your Name"

    def on_activate(self):
        """
        Called when extension is enabled.

        Use this to:
        - Load settings
        - Set up UI elements
        - Register event handlers
        """
        self.api.show_notification(f"{self.name} activated!")

    def on_page_load(self, url: str, page):
        """
        Called after each page loads.

        Args:
            url: The loaded URL
            page: QWebEnginePage object

        Example: Change page background
        """
        # self.api.inject_css(page, "body { background: #f0f0f0; }")
        pass

    def on_before_navigate(self, url: str) -> bool:
        """
        Called before navigating to URL.

        Args:
            url: URL about to be loaded

        Returns:
            True to allow, False to block

        Example: Block social media
        """
        # if "facebook.com" in url:
        #     return False  # Block
        return True  # Allow

    def on_context_menu(self, menu, hit_test):
        """
        Add items to right-click context menu.

        Args:
            menu: QMenu object
            hit_test: QWebEngineContextMenuData with click info

        Example: Add custom menu item
        """
        # action = menu.addAction("My Action")
        # action.triggered.connect(self.my_handler)
        pass
```

#### 5.5.3 Interactive Tutorials

**Built-in tutorial system in Help menu:**

1. **Tutorial 1: Your First Extension**
   - Create a "Hello World" extension
   - Show notification on page load
   - Test in browser

2. **Tutorial 2: DOM Manipulation**
   - Select elements with CSS selectors
   - Modify element content
   - Inject custom CSS

3. **Tutorial 3: JavaScript Bridge**
   - Execute JavaScript from Python
   - Get return values
   - Handle async operations

4. **Tutorial 4: Form Automation**
   - Fill form fields
   - Submit forms
   - Handle page navigation

5. **Tutorial 5: Web Scraping**
   - Extract data from pages
   - Parse HTML with BeautifulSoup
   - Export to JSON/CSV

6. **Tutorial 6: Ad Blocker**
   - Pattern matching
   - Request blocking
   - Element hiding

**Tutorial Format:**
```
Tutorial Panel:
┌──────────────────────────────────────────────────────────┐
│ Tutorial 1: Your First Extension          [← Prev] [Next →]│
├──────────────────────────────────────────────────────────┤
│ # Creating Your First Extension                          │
│                                                           │
│ In this tutorial, you'll create a simple extension that  │
│ shows a notification when a page loads.                  │
│                                                           │
│ ## Step 1: Create Extension Directory                    │
│                                                           │
│ Run this command:                                        │
│ ```bash                                                  │
│ viloweb create-extension hello_world                     │
│ ```                                                      │
│                                                           │
│ [Run Command]  <- Interactive button                     │
│                                                           │
│ ## Step 2: Edit extension.py                            │
│                                                           │
│ ```python                                                │
│ def on_page_load(self, url, page):                      │
│     self.api.show_notification(f"Loaded: {url}")        │
│ ```                                                      │
│                                                           │
│ [Try It Now]  <- Opens editor with code                  │
│                                                           │
│ ## Step 3: Test Your Extension                          │
│                                                           │
│ 1. Go to Extensions panel                               │
│ 2. Enable "Hello World"                                 │
│ 3. Navigate to any website                              │
│ 4. See notification appear!                             │
│                                                           │
│ [Complete Tutorial] [Skip to Next Tutorial]              │
└──────────────────────────────────────────────────────────┘
```

### 5.6 VFWidgets Showcase Features

#### 5.6.1 Split Screen Browsing (vfwidgets-multisplit) - OPTIONAL

**Purpose**: Compare pages side-by-side

```
Split View:
┌────────────────────┬────────────────────┐
│ Page 1             │ Page 2             │
│ example.com        │ reference.com      │
│                    │                    │
│ Content...         │ Content...         │
│                    │                    │
└────────────────────┴────────────────────┘

Features:
- Drag to resize splits
- 2, 3, or 4 panes
- Independent navigation
- Synchronized scrolling (optional)
```

### 5.7 Code Organization for Learning

**Principle**: Every file is a teaching tool

#### 5.7.1 Extensive Comments

```python
# browser/tab.py - HEAVILY COMMENTED FOR LEARNING

class BrowserTab(QWidget):
    """Individual browser tab with web view.

    This class demonstrates:
    1. QWebEngineView setup and configuration
    2. JavaScript-Python communication via QWebChannel
    3. Signal/slot connections for reactive UI
    4. Proper memory management for web views

    Learning Objectives:
    - Understand QWebEngineView lifecycle
    - Master JavaScript bridge patterns
    - Handle asynchronous page loading
    - Implement custom context menus
    """

    # === SIGNALS ===
    # Qt signals notify other components about state changes
    # Learn more: https://doc.qt.io/qt-6/signalsandslots.html

    titleChanged = Signal(str)  # Emitted when page title changes
    urlChanged = Signal(str)    # Emitted when URL changes
    loadProgressChanged = Signal(int)  # Emitted during loading (0-100)
    secureChanged = Signal(bool)  # Emitted when HTTPS status changes

    def __init__(self):
        """Initialize browser tab.

        LEARNING NOTE:
        This setup shows the recommended pattern for QWebEngineView:
        1. Create QWebEnginePage (represents the web page)
        2. Create QWebEngineView (displays the page)
        3. Create QWebChannel (Python-JavaScript bridge)
        4. Connect signals (reactive updates)
        """
        super().__init__()

        # === STEP 1: Create the web page ===
        # QWebEnginePage represents the actual web page
        # It handles JavaScript execution, DOM, network requests
        self.page = QWebEnginePage()

        # === STEP 2: Create the web view ===
        # QWebEngineView is the Qt widget that displays the page
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.page)

        # === STEP 3: Set up JavaScript bridge ===
        # This allows Python to call JavaScript and vice versa
        self._setup_javascript_bridge()

        # === STEP 4: Connect signals ===
        # Connect web page signals to our custom signals
        # This pattern is called "signal forwarding"
        self.page.titleChanged.connect(self.titleChanged.emit)
        self.page.urlChanged.connect(lambda url: self.urlChanged.emit(url.toString()))
        self.page.loadProgress.connect(self.loadProgressChanged.emit)

        # ... rest of implementation
```

#### 5.7.2 Tutorial-Style READMEs

Each module has a `README.md`:

```markdown
# Browser Tab Module

## What You'll Learn

1. How to create and configure QWebEngineView
2. How to set up JavaScript-Python communication
3. How to handle page loading events
4. How to inject CSS and JavaScript

## Key Concepts

### QWebEnginePage vs QWebEngineView

- **QWebEnginePage**: The actual web page (DOM, JavaScript, network)
- **QWebEngineView**: The visual widget that displays the page

Think of it like:
- Page = Document
- View = Window showing the document

### JavaScript Bridge Pattern

```python
# Python side
channel = QWebChannel()
bridge = BrowserBridge()
channel.registerObject("python", bridge)
page.setWebChannel(channel)

# JavaScript side (in web page)
new QWebChannel(qt.webChannelTransport, function(channel) {
    var python = channel.objects.python;
    python.callPythonFunction("hello");
});
```

## Try It Yourself

Run the examples:
```bash
python examples/01_basic_webview.py
python examples/02_javascript_bridge.py
python examples/03_dom_manipulation.py
```
```

### 5.8 Python Package for External Use

ViloWeb is also usable as a **library** for automation:

```python
# Install as package
pip install viloweb

# Use in your scripts
from viloweb import Browser

# Create browser instance
browser = Browser(headless=True)  # No GUI

# Navigate and interact
browser.navigate("https://example.com")
browser.wait_for_load()

# Extract data
title = browser.execute_js("return document.title")
print(f"Page title: {title}")

# Fill form
browser.fill_form({
    "username": "test@example.com",
    "password": "secret123"
})
browser.click("#login-button")

# Take screenshot
browser.screenshot("result.png")

# Export PDF
browser.pdf_export("page.pdf")

# Close
browser.close()
```

### 5.8 Security Testing Features (DEFENSIVE SECURITY)

ViloWeb includes specialized features for **defensive security testing** and learning security concepts. These tools help developers understand web security, test their own applications, and learn secure coding practices.

**IMPORTANT**: ViloWeb is designed for **defensive security only** - testing your own applications and learning security concepts. All security features are educational and meant to improve security awareness.

#### 5.8.1 Security Testing Panel

Dedicated panel for security analysis and testing:

```
┌───────────────────────────────────────────────────────────┐
│ 🔒 Security Testing                         [Analyze]     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ Current Page: https://example.com                         │
│                                                           │
│ Security Headers                                          │
│ ─────────────────────────────────────────────────────    │
│ ✓ HTTPS (TLS 1.3)                                         │
│ ✓ Strict-Transport-Security: max-age=31536000            │
│ ⚠ Missing: Content-Security-Policy                       │
│ ⚠ Missing: X-Frame-Options                               │
│ ✓ X-Content-Type-Options: nosniff                        │
│                                                           │
│ [View All Headers] [Export Report]                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Key Features:**

1. **HTTP Security Headers Analysis**
   - Detect missing security headers (CSP, HSTS, X-Frame-Options)
   - Validate header configurations
   - Explain each header's purpose (educational)
   - Suggest improvements

2. **TLS/SSL Certificate Inspection**
   - Certificate chain validation
   - Expiration warnings
   - Cipher suite information
   - Educational explanations of certificate fields

3. **Content Security Policy (CSP) Analyzer**
   - Parse and explain CSP directives
   - Identify unsafe configurations (unsafe-inline, unsafe-eval)
   - Test CSP violations
   - Suggest improvements

4. **Cookie Security Audit**
   - Check for HttpOnly flag
   - Check for Secure flag
   - Check for SameSite attribute
   - Identify session token risks

5. **Form Security Checker**
   - Detect forms without CSRF tokens
   - Check password field security attributes
   - Validate autocomplete settings
   - Identify mixed content issues

#### 5.8.2 Security Testing Extensions

Python extensions for automated security testing:

**Example: Security Scanner Extension**

```python
from viloweb.extensions import ViloWebExtension

class SecurityScannerExtension(ViloWebExtension):
    """Automated security scanner for web applications.

    This extension demonstrates defensive security testing:
    - Analyzes HTTP headers
    - Checks for common misconfigurations
    - Identifies potential vulnerabilities
    - Generates security reports

    Educational Purpose: Learn to identify security issues
    """

    name = "Security Scanner"
    version = "1.0.0"
    description = "Automated security analysis tool"
    author = "VFWidgets Security Team"

    def __init__(self, api):
        super().__init__(api)
        self.scan_results = {}

    def on_page_load(self, url: str, page):
        """Analyze page security after loading."""
        print(f"\\n🔒 Security Scan: {url}")
        print("=" * 60)

        # 1. Check HTTPS
        self._check_https(url)

        # 2. Analyze headers
        self._analyze_headers(page)

        # 3. Check cookies
        self._check_cookies(page)

        # 4. Analyze forms
        self._analyze_forms(page)

        # 5. Check for mixed content
        self._check_mixed_content(page)

        # 6. Generate report
        self._generate_report()

    def _check_https(self, url: str):
        """Verify HTTPS usage."""
        if not url.startswith("https://"):
            self.scan_results["https"] = {
                "status": "FAIL",
                "message": "Site not using HTTPS",
                "risk": "HIGH",
                "recommendation": "Enable HTTPS with valid certificate"
            }
        else:
            self.scan_results["https"] = {
                "status": "PASS",
                "message": "Site using HTTPS"
            }

    def _analyze_headers(self, page):
        """Analyze HTTP security headers."""
        # Get response headers via JavaScript bridge
        js_code = """
        (function() {
            // Note: In real implementation, headers come from QNetworkReply
            return {
                'strict-transport-security': document.securityPolicy?.hsts,
                'content-security-policy': document.securityPolicy?.csp,
                'x-frame-options': document.securityPolicy?.xfo,
                'x-content-type-options': document.securityPolicy?.xcto
            };
        })();
        """

        def handle_headers(headers):
            results = {}

            # Check HSTS
            if not headers.get('strict-transport-security'):
                results['hsts'] = {
                    "status": "FAIL",
                    "message": "Missing Strict-Transport-Security header",
                    "risk": "MEDIUM",
                    "recommendation": "Add HSTS header with long max-age"
                }

            # Check CSP
            if not headers.get('content-security-policy'):
                results['csp'] = {
                    "status": "FAIL",
                    "message": "Missing Content-Security-Policy header",
                    "risk": "HIGH",
                    "recommendation": "Implement strict CSP to prevent XSS"
                }

            # Check X-Frame-Options
            if not headers.get('x-frame-options'):
                results['xfo'] = {
                    "status": "WARN",
                    "message": "Missing X-Frame-Options header",
                    "risk": "MEDIUM",
                    "recommendation": "Add X-Frame-Options: DENY or SAMEORIGIN"
                }

            self.scan_results['headers'] = results

        page.runJavaScript(js_code, handle_headers)

    def _check_cookies(self, page):
        """Audit cookie security."""
        js_code = """
        document.cookie.split(';').map(c => {
            let [name, value] = c.trim().split('=');
            return {
                name: name,
                hasHttpOnly: false,  // JavaScript can't detect HttpOnly
                hasSecure: document.location.protocol === 'https:',
                hasSameSite: false   // Would need to check Set-Cookie header
            };
        });
        """

        def handle_cookies(cookies):
            issues = []
            for cookie in cookies:
                if not cookie.get('hasHttpOnly'):
                    issues.append({
                        "cookie": cookie['name'],
                        "issue": "Missing HttpOnly flag",
                        "risk": "MEDIUM",
                        "impact": "Cookie accessible to JavaScript (XSS risk)"
                    })

                if not cookie.get('hasSecure'):
                    issues.append({
                        "cookie": cookie['name'],
                        "issue": "Missing Secure flag",
                        "risk": "HIGH",
                        "impact": "Cookie can be sent over HTTP"
                    })

            self.scan_results['cookies'] = issues

        page.runJavaScript(js_code, handle_cookies)

    def _analyze_forms(self, page):
        """Check form security."""
        js_code = """
        Array.from(document.forms).map(form => {
            let passwordFields = Array.from(form.elements).filter(
                el => el.type === 'password'
            );

            return {
                action: form.action,
                method: form.method,
                hasHttpsAction: form.action.startsWith('https://'),
                hasPasswordField: passwordFields.length > 0,
                passwordAutocomplete: passwordFields.some(
                    f => f.autocomplete === 'on' || !f.autocomplete
                ),
                hasCsrfToken: Array.from(form.elements).some(
                    el => el.name.toLowerCase().includes('csrf') ||
                          el.name.toLowerCase().includes('token')
                )
            };
        });
        """

        def handle_forms(forms):
            issues = []
            for form in forms:
                if form['hasPasswordField']:
                    if not form['hasHttpsAction']:
                        issues.append({
                            "form": form['action'],
                            "issue": "Password form submits to HTTP",
                            "risk": "CRITICAL",
                            "impact": "Credentials sent in plaintext"
                        })

                    if form['passwordAutocomplete']:
                        issues.append({
                            "form": form['action'],
                            "issue": "Password autocomplete enabled",
                            "risk": "LOW",
                            "recommendation": "Set autocomplete='new-password'"
                        })

                if form['method'].upper() == 'POST' and not form['hasCsrfToken']:
                    issues.append({
                        "form": form['action'],
                        "issue": "Possible missing CSRF token",
                        "risk": "HIGH",
                        "impact": "Vulnerable to CSRF attacks"
                    })

            self.scan_results['forms'] = issues

        page.runJavaScript(js_code, handle_forms)

    def _check_mixed_content(self, page):
        """Detect mixed HTTP/HTTPS content."""
        js_code = """
        let httpResources = [];

        // Check images
        document.querySelectorAll('img').forEach(img => {
            if (img.src.startsWith('http://')) {
                httpResources.push({type: 'image', url: img.src});
            }
        });

        // Check scripts
        document.querySelectorAll('script[src]').forEach(script => {
            if (script.src.startsWith('http://')) {
                httpResources.push({type: 'script', url: script.src});
            }
        });

        // Check stylesheets
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            if (link.href.startsWith('http://')) {
                httpResources.push({type: 'stylesheet', url: link.href});
            }
        });

        return httpResources;
        """

        def handle_mixed_content(resources):
            if resources:
                self.scan_results['mixed_content'] = {
                    "status": "FAIL",
                    "count": len(resources),
                    "resources": resources,
                    "risk": "MEDIUM",
                    "impact": "Insecure resources loaded over HTTP"
                }

        page.runJavaScript(js_code, handle_mixed_content)

    def _generate_report(self):
        """Generate and display security report."""
        print("\\n📊 Security Scan Results:")
        print("-" * 60)

        # Count issues by severity
        critical = sum(1 for r in self.scan_results.values()
                      if isinstance(r, dict) and r.get('risk') == 'CRITICAL')
        high = sum(1 for r in self.scan_results.values()
                  if isinstance(r, dict) and r.get('risk') == 'HIGH')
        medium = sum(1 for r in self.scan_results.values()
                    if isinstance(r, dict) and r.get('risk') == 'MEDIUM')

        print(f"\\n🔴 Critical: {critical}")
        print(f"🟠 High:     {high}")
        print(f"🟡 Medium:   {medium}")

        # Show detailed findings
        for category, result in self.scan_results.items():
            if isinstance(result, dict) and result.get('status') == 'FAIL':
                print(f"\\n❌ {category.upper()}")
                print(f"   Issue: {result['message']}")
                print(f"   Risk: {result['risk']}")
                if 'recommendation' in result:
                    print(f"   Fix: {result['recommendation']}")

        # Notification
        total_issues = critical + high + medium
        if total_issues > 0:
            self.api.show_notification(
                f"⚠️  Security Scan: Found {total_issues} issues"
            )
        else:
            self.api.show_notification("✅ Security Scan: No issues found")
```

#### 5.8.3 Additional Security Testing Tools

**1. HTTP Request/Response Inspector**
```python
class RequestInterceptor(ViloWebExtension):
    """Intercept and analyze HTTP requests/responses.

    Educational features:
    - View all request headers
    - Inspect response headers
    - Analyze authentication methods
    - Check for sensitive data in URLs/headers
    """

    def on_request(self, request):
        """Analyze outgoing request."""
        # Check for sensitive data in URL
        if any(param in request.url.lower() for param in
               ['password', 'token', 'apikey', 'secret']):
            self.api.show_notification(
                "⚠️  Sensitive data in URL query parameters!"
            )

        # Log authentication headers
        if 'Authorization' in request.headers:
            auth_type = request.headers['Authorization'].split()[0]
            print(f"🔐 Authentication: {auth_type}")
```

**2. Cookie/Session Manager**
```python
class SessionAnalyzer(ViloWebExtension):
    """Analyze session management security.

    Features:
    - Track session cookies
    - Detect session fixation risks
    - Check cookie attributes
    - Monitor session timeout
    """

    def analyze_session_cookie(self, cookie):
        """Analyze session cookie security."""
        issues = []

        if not cookie.secure:
            issues.append("Cookie lacks Secure flag")

        if not cookie.httpOnly:
            issues.append("Cookie lacks HttpOnly flag")

        if cookie.sameSite == 'None':
            issues.append("Cookie has SameSite=None (CSRF risk)")

        return issues
```

**3. TLS/Certificate Inspector**
```python
class TLSInspector(ViloWebExtension):
    """Inspect TLS configuration and certificates.

    Educational features:
    - View certificate details
    - Check certificate chain
    - Analyze cipher suites
    - Detect weak encryption
    """

    def inspect_certificate(self, url: str, page):
        """Show certificate information."""
        # Access via QWebEngineCertificateError
        cert_info = page.certificate()

        print(f"📜 Certificate for {url}")
        print(f"   Issuer: {cert_info.issuer}")
        print(f"   Valid: {cert_info.valid_from} to {cert_info.valid_to}")
        print(f"   Subject: {cert_info.subject}")
        print(f"   Fingerprint: {cert_info.fingerprint}")
```

**4. XSS Testing Helper**
```python
class XSSTestHelper(ViloWebExtension):
    """Helper for testing XSS vulnerabilities (own applications only).

    DEFENSIVE SECURITY ONLY:
    - Test your own web applications
    - Learn about XSS prevention
    - Understand output encoding
    """

    # Common XSS test payloads (for educational purposes)
    TEST_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
    ]

    def test_input_field(self, page, selector: str):
        """Test input field for XSS (educational demo)."""
        print(f"\\n🧪 Testing input field: {selector}")
        print("⚠️  Only test your own applications!")

        for payload in self.TEST_PAYLOADS:
            js = f"""
            let el = document.querySelector({repr(selector)});
            if (el) {{
                el.value = {repr(payload)};
                console.log('Testing payload: {payload}');
            }}
            """
            page.runJavaScript(js)
```

#### 5.8.4 Security Learning Resources

**Built-in Security Tutorials:**

1. **"Understanding HTTPS and TLS"**
   - How TLS works
   - Certificate validation
   - Man-in-the-middle attacks
   - Best practices

2. **"Web Application Security Headers"**
   - CSP (Content-Security-Policy)
   - HSTS (Strict-Transport-Security)
   - X-Frame-Options
   - X-Content-Type-Options
   - Referrer-Policy

3. **"Cookie Security"**
   - HttpOnly flag
   - Secure flag
   - SameSite attribute
   - Session management

4. **"Testing Your Web Application"**
   - Security testing methodology
   - Common vulnerabilities (OWASP Top 10)
   - How to use ViloWeb security tools
   - Responsible disclosure

5. **"Python Security Extensions"**
   - Writing security scanner extensions
   - Automating security tests
   - Generating security reports
   - Best practices

#### 5.8.5 Security Report Generator

```python
class SecurityReportGenerator:
    """Generate comprehensive security reports.

    Features:
    - HTML report with findings
    - JSON export for CI/CD integration
    - PDF report generation
    - Markdown summary
    """

    def generate_report(self, scan_results: dict, url: str) -> str:
        """Generate HTML security report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Report - {url}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #689f38; }}
                .pass {{ color: #388e3c; }}
            </style>
        </head>
        <body>
            <h1>🔒 Security Scan Report</h1>
            <p><strong>URL:</strong> {url}</p>
            <p><strong>Scan Date:</strong> {datetime.now()}</p>

            <h2>Summary</h2>
            <!-- Risk summary -->

            <h2>Detailed Findings</h2>
            <!-- Detailed results -->

            <h2>Recommendations</h2>
            <!-- Prioritized fixes -->
        </body>
        </html>
        """
        return html
```

#### 5.8.6 Ethical Guidelines & Disclaimers

**Displayed prominently in Security Testing panel:**

```
╔═══════════════════════════════════════════════════════════╗
║           SECURITY TESTING - ETHICAL USE ONLY             ║
╟───────────────────────────────────────────────────────────╢
║                                                           ║
║  ViloWeb security tools are for DEFENSIVE security:      ║
║                                                           ║
║  ✓ Testing YOUR OWN web applications                     ║
║  ✓ Learning security concepts                            ║
║  ✓ Security research with permission                     ║
║  ✓ Educational demonstrations                            ║
║                                                           ║
║  ✗ DO NOT test applications without permission           ║
║  ✗ DO NOT use for malicious purposes                     ║
║  ✗ DO NOT attack systems you don't own                   ║
║                                                           ║
║  Unauthorized security testing may be illegal.            ║
║  Always obtain written permission before testing.         ║
║                                                           ║
║  [I Understand - Enable Security Tools]                  ║
╚═══════════════════════════════════════════════════════════╝
```

**Code of Conduct for Security Features:**

1. **Permission Required**: Only test systems you own or have written permission to test
2. **Responsible Disclosure**: Report vulnerabilities responsibly to application owners
3. **Educational Purpose**: Use tools to learn and improve security, not exploit
4. **Privacy Respect**: Don't access or collect data without authorization
5. **Legal Compliance**: Follow all applicable laws and regulations

---

## 6. Technical Implementation Details

### 5.1 QtWebEngine Configuration

```python
class ViloWebApp(ViloCodeWindow):
    """Main browser application."""

    def __init__(self):
        super().__init__()

        # Configure QtWebEngine before creating views
        self._configure_webengine()

    def _configure_webengine(self):
        """Configure QtWebEngine settings."""
        from PySide6.QtWebEngineCore import (
            QWebEngineSettings,
            QWebEngineProfile,
        )

        # Get default profile
        profile = QWebEngineProfile.defaultProfile()

        # Set storage paths
        profile.setPersistentStoragePath(self.data_dir / "storage")
        profile.setCachePath(self.data_dir / "cache")

        # Enable features
        settings = QWebEngineSettings.defaultSettings()
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.WebGLEnabled, True
        )

        # Security settings
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
            False,  # Security: prevent local file access to remote
        )
```

### 5.2 JavaScript Bridge

For custom functionality not provided by QtWebEngine:

```python
class BrowserBridge(QObject):
    """JavaScript bridge for custom browser features."""

    @Slot(str, result=str)
    def getPassword(self, url: str) -> str:
        """Get saved password for URL."""
        password = self.password_manager.get_password(url)
        return password or ""

    @Slot(str, str)
    def savePassword(self, url: str, password: str):
        """Save password for URL."""
        self.password_manager.save_password(url, password)

    @Slot(str)
    def addToHistory(self, url: str):
        """Manually add to history."""
        self.history_manager.add_entry(url)
```

Register with web page:
```python
from PySide6.QtWebChannel import QWebChannel

channel = QWebChannel()
bridge = BrowserBridge()
channel.registerObject("browser", bridge)
page.setWebChannel(channel)
```

Access from JavaScript:
```javascript
// In web page
new QWebChannel(qt.webChannelTransport, function(channel) {
    var browser = channel.objects.browser;

    // Get saved password
    browser.getPassword(window.location.href, function(password) {
        document.getElementById('password').value = password;
    });
});
```

### 5.3 Storage Architecture

**SQLite Databases:**

1. **History** (`~/.viloweb/profiles/default/history.db`):
   - Main table: history entries
   - Indexes: url, visit_time
   - Full-text search on title/URL
   - Automatic cleanup (delete >90 days)

2. **Downloads** (`~/.viloweb/profiles/default/downloads.db`):
   - Active and completed downloads
   - Resume information
   - File metadata

3. **Passwords** (`~/.viloweb/profiles/default/passwords.db`):
   - Encrypted with master password
   - AES-256-GCM encryption
   - Salt per entry

**JSON Files:**

1. **Bookmarks** (`bookmarks.json`):
   - Tree structure with folders
   - Quick read/write
   - Human-readable for debugging

2. **Settings** (`settings.json`):
   - All user preferences
   - Theme selection
   - Window geometry

3. **Sessions** (`sessions/session_*.json`):
   - Window and tab state
   - Navigation history per tab
   - Scroll positions

### 5.4 Performance Targets

**Tab Operations:**
- New tab creation: <100ms
- Tab switching: <50ms
- Tab close: <30ms
- Tab drag & drop: 60 FPS

**Page Loading:**
- Address bar to first paint: <200ms (cached)
- Address bar to first paint: <800ms (network)
- Back button navigation: <100ms (from cache)

**Memory Management:**
- Base browser process: <100 MB
- Per active tab: <150 MB average
- Per suspended tab: <10 MB
- Maximum tabs before warning: 50
- Automatic tab suspension: after 30 minutes inactive

**Startup Time:**
- Cold start (no cache): <2 seconds
- Warm start (cached): <500ms
- Session restore: <3 seconds for 10 tabs

### 5.5 Security Considerations

**Process Isolation:**
- Renderer processes run sandboxed
- No direct file system access from renderers
- IPC communication only through defined channels

**Content Security:**
- HTTPS-only mode (optional)
- Mixed content blocking
- XSS protection
- Certificate validation
- Automatic updates for QtWebEngine

**User Data Protection:**
- Encrypted password storage
- Secure deletion of private data
- No telemetry or tracking
- Optional master password
- Automatic security updates

---

## 6. Development Roadmap

### Phase 1: Foundation (Weeks 1-2) ✅
**Status**: Skeleton exists, needs full implementation

**Tasks:**
1. Set up ChromeTabbedWindow integration
2. Create BrowserTab with QWebEngineView
3. Implement NavigationBar with controls
4. Build address bar with security indicators
5. Add basic bookmark management
6. Integrate with ViloCodeWindow sidebar
7. Implement keyboard shortcuts
8. Add theme system integration

**Deliverables:**
- Working multi-tab browser
- Basic navigation and bookmarks
- Theme-aware UI
- No crashes during normal use

**Success Criteria:**
- Can browse any website
- Tabs work smoothly
- Bookmarks persist
- Looks professional

---

### Phase 2: Core Features (Weeks 3-4)

**Tasks:**
1. Set up SQLite history database
2. Create HistoryManager with CRUD
3. Build HistoryPanel UI with search
4. Implement QWebEngineDownloadRequest handling
5. Create DownloadsPanel with progress
6. Add all context menus (page, link, image, text)
7. Implement Find in Page bar
8. Add zoom controls

**Deliverables:**
- Full history tracking
- Downloads manager
- All context menus
- Find in page
- Zoom controls

**Success Criteria:**
- History searchable
- Downloads work reliably
- Context menus feel native
- Find highlights matches
- Zoom persists per tab

---

### Phase 3: Advanced Features (Weeks 5-8)

**Tasks:**
1. Implement session save/restore
2. Create Session management dialog
3. Add incognito window mode
4. Integrate Chrome DevTools
5. Set up encrypted password database
6. Build password manager UI
7. Create comprehensive settings dialog
8. Add auto-fill functionality

**Deliverables:**
- Session management
- Private browsing
- DevTools integration
- Password manager
- Settings dialog

**Success Criteria:**
- Sessions restore correctly
- Incognito mode isolated
- DevTools fully functional
- Passwords encrypted
- All settings accessible

---

### Phase 4: Power Features (Weeks 9-12)

**Tasks:**
1. Design extension API
2. Implement Chrome extension compatibility layer
3. Create ExtensionManager
4. Build profile system
5. Add profile switching UI
6. Implement tab groups
7. Create workspace management
8. Build smart omnibox with search

**Deliverables:**
- Extension system
- Multi-profile support
- Tab groups
- Workspaces
- Smart search

**Success Criteria:**
- Can load Chrome extensions
- Profiles fully isolated
- Tab groups intuitive
- Omnibox helpful
- All features stable

---

### Phase 5: Polish & Release (Weeks 13-16)

**Tasks:**
1. Performance profiling and optimization
2. Memory leak detection and fixes
3. Security audit
4. Accessibility improvements (WCAG AA)
5. Comprehensive testing
6. Documentation completion
7. Package for distribution
8. Create website and marketing materials

**Deliverables:**
- Optimized performance
- Security hardening
- Full accessibility
- Complete documentation
- Release packages
- Marketing site

**Success Criteria:**
- Performance targets met
- No security vulnerabilities
- Passes accessibility audit
- Documentation complete
- Ready for public release

---

## 7. Platform Considerations

### 7.1 Linux
- Native Wayland support via QtWebEngine
- X11 fallback for older systems
- AppImage packaging for distribution
- Desktop file integration
- System tray notifications

### 7.2 Windows
- Native Windows API integration
- Windows 10/11 styling
- MSI installer
- Windows Defender SmartScreen signing
- Start menu integration

### 7.3 macOS
- Native macOS window management
- Touch Bar support (if available)
- DMG packaging
- Code signing and notarization
- App Store distribution (optional)

### 7.4 WSL/WSLg
- Automatic detection via vfwidgets-common
- Software rendering fallback
- X11 forwarding support
- Native Linux paths

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Core component testing (pytest)
- Data model validation
- Manager classes (bookmarks, history, downloads)
- Settings persistence

### 8.2 Integration Tests
- Tab creation/switching/closing
- Navigation flow
- Bookmark operations
- History recording
- Download handling

### 8.3 UI Tests
- pytest-qt for widget testing
- Keyboard shortcut verification
- Context menu functionality
- Dialog interactions

### 8.4 Browser Tests
- Playwright for web content testing
- JavaScript execution
- Form interactions
- Page load performance

### 8.5 Performance Tests
- Tab switching latency
- Memory usage monitoring
- Startup time measurement
- CPU usage profiling

### 8.6 Security Tests
- SQL injection prevention
- XSS protection verification
- Password encryption validation
- Process isolation testing

---

## 9. Documentation Requirements

### 9.1 User Documentation
- Quick start guide
- Feature tutorials
- Keyboard shortcuts reference
- Troubleshooting guide
- FAQ

### 9.2 Developer Documentation
- Architecture overview
- API reference
- Extension development guide
- Contributing guidelines
- Code style guide

### 9.3 Administrator Documentation
- Installation guide
- Configuration options
- Enterprise deployment
- Policy management

---

## 10. Success Metrics

### 10.1 Performance Metrics
- Tab switching: <50ms (target: <30ms)
- Startup time: <2s cold, <500ms warm
- Memory per tab: <150MB average
- Page load: <800ms first paint

### 10.2 Quality Metrics
- Zero crashes during 1-hour browsing session
- <5 critical bugs in production
- 90%+ code coverage for core components
- WCAG AA accessibility compliance

### 10.3 Feature Metrics
- 100% of Phase 1 features complete
- 80%+ of Phase 2 features complete within month 1
- Extension API compatible with top 20 Chrome extensions
- Settings cover 50+ configuration options

### 10.4 User Metrics
- <1 minute to install and launch
- <5 minutes to learn basic features
- Positive feedback from 80%+ of testers
- Daily active usage by development team

---

## 11. Future Enhancements (Beyond Phase 4)

### 11.1 Advanced Privacy
- Built-in VPN integration
- Tor browser mode
- Fingerprinting protection
- Cookie isolation
- DNS-over-HTTPS

### 11.2 AI Integration
- Smart suggestions in address bar
- Content summarization
- Translation integration
- Accessibility improvements (read aloud)
- Image description for screen readers

### 11.3 Developer Features
- REST client (like Postman)
- JSON formatter
- Code editor integration
- Git repository viewer

### 11.4 Productivity
- Split screen browsing
- Picture-in-picture for all videos
- Reading mode with customization
- Note-taking sidebar
- Task manager with website blockers

### 11.5 Customization
- Custom CSS per site
- JavaScript injection
- URL rewriting rules
- Gesture controls
- Mouse button customization

---

## 12. Known Risks & Mitigations

### Risk 1: QtWebEngine Compatibility
**Risk**: QtWebEngine may not support all Chrome features
**Mitigation**: Focus on core features first, document limitations, contribute to Qt if needed

### Risk 2: Performance with Many Tabs
**Risk**: Memory usage may become problematic with 50+ tabs
**Mitigation**: Implement tab suspension, process limits, memory warnings

### Risk 3: Extension API Compatibility
**Risk**: Chrome extension API is complex and evolving
**Mitigation**: Start with most common APIs, phase in advanced features, document incompatibilities

### Risk 4: Security Vulnerabilities
**Risk**: Browser security is critical and complex
**Mitigation**: Regular security audits, follow QtWebEngine updates, encrypted storage, sandboxing

### Risk 5: Cross-Platform Issues
**Risk**: Behavior may differ on Windows/Mac/Linux
**Mitigation**: Platform-specific testing, CI/CD on all platforms, use vfwidgets-common

---

## 13. Appendix

### 13.1 Keyboard Shortcuts Reference

**Navigation:**
- `Ctrl+T` - New tab
- `Ctrl+W` - Close tab
- `Ctrl+Shift+T` - Reopen closed tab
- `Ctrl+Tab` - Next tab
- `Ctrl+Shift+Tab` - Previous tab
- `Ctrl+1` to `Ctrl+8` - Switch to tab 1-8
- `Ctrl+9` - Switch to last tab
- `Alt+Left` - Back
- `Alt+Right` - Forward
- `F5` or `Ctrl+R` - Reload
- `Ctrl+Shift+R` - Hard reload
- `Ctrl+L` - Focus address bar
- `Ctrl+D` - Bookmark current page

**Browsing:**
- `Ctrl+F` - Find in page
- `F3` - Find next
- `Shift+F3` - Find previous
- `Ctrl++` - Zoom in
- `Ctrl+-` - Zoom out
- `Ctrl+0` - Reset zoom
- `Ctrl+H` - History
- `Ctrl+Shift+Delete` - Clear browsing data
- `Ctrl+Shift+B` - Show bookmarks bar

**Window:**
- `Ctrl+N` - New window
- `Ctrl+Shift+N` - New incognito window
- `F11` - Full screen
- `Ctrl+Shift+M` - Toggle mobile view

**Developer:**
- `F12` or `Ctrl+Shift+I` - Developer tools
- `Ctrl+U` - View page source
- `Ctrl+Shift+J` - JavaScript console

### 13.2 File Structure

```
apps/viloweb/
├── docs/
│   ├── SPECIFICATION.md        # This file
│   ├── ARCHITECTURE.md         # Detailed architecture
│   └── UI-MOCKUPS.md           # UI designs
│
├── src/viloweb/
│   ├── __init__.py             # Package init
│   ├── __main__.py             # Entry point
│   ├── app.py                  # ViloWebWindow main class
│   │
│   ├── browser/                # Browser components
│   │   ├── __init__.py
│   │   ├── tab.py              # BrowserTab
│   │   ├── navigation.py       # NavigationBar
│   │   ├── address_bar.py      # AddressBar
│   │   └── web_view.py         # Custom QWebEngineView
│   │
│   ├── managers/               # Data management
│   │   ├── __init__.py
│   │   ├── bookmarks.py        # BookmarkManager
│   │   ├── history.py          # HistoryManager
│   │   ├── downloads.py        # DownloadManager
│   │   ├── passwords.py        # PasswordManager
│   │   ├── sessions.py         # SessionManager
│   │   └── extensions.py       # ExtensionManager
│   │
│   ├── panels/                 # Sidebar panels
│   │   ├── __init__.py
│   │   ├── home.py             # HomePanel
│   │   ├── bookmarks.py        # BookmarksPanel
│   │   ├── history.py          # HistoryPanel
│   │   ├── downloads.py        # DownloadsPanel
│   │   └── extensions.py       # ExtensionsPanel
│   │
│   ├── dialogs/                # Dialogs
│   │   ├── __init__.py
│   │   ├── settings.py         # SettingsDialog
│   │   ├── bookmark_edit.py    # BookmarkEditDialog
│   │   ├── clear_data.py       # ClearDataDialog
│   │   └── dev_tools.py        # DevToolsDialog
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── tab.py              # Tab model
│   │   ├── bookmark.py         # Bookmark model
│   │   ├── history.py          # HistoryEntry model
│   │   ├── download.py         # Download model
│   │   └── session.py          # Session models
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── database.py         # Database helpers
│       ├── encryption.py       # Password encryption
│       └── favicon.py          # Favicon fetching
│
├── tests/                      # Tests
│   ├── test_bookmarks.py
│   ├── test_history.py
│   ├── test_downloads.py
│   └── test_browser_tab.py
│
├── pyproject.toml              # Package configuration
├── Makefile                    # Build automation
└── README.md                   # User documentation
```

---

## Conclusion

ViloWeb is **not just another browser** – it's an educational platform for learning QtWebEngine, a showcase for VFWidgets components, and a unique environment for Python-based web automation and extension development.

### What Makes ViloWeb Special

1. **Educational First**: Every file extensively commented, tutorials built-in, learning as primary goal
2. **Python Extensions**: Write browser extensions in Python with full Qt/PySide6 API access
3. **VFWidgets Showcase**: Demonstrates every major widget in real-world context
4. **Web Automation**: Full Python API for controlling browsers programmatically
5. **Developer Experience**: Built for developers learning QtWebEngine, not end users

### For Developers Learning QtWebEngine

ViloWeb provides:
- **Clear Examples**: Real working code demonstrating JavaScript bridges, DOM manipulation, form automation
- **Interactive Console**: Live Python REPL to experiment with browser APIs
- **Comprehensive Tutorials**: Step-by-step guides from "Hello World" to advanced scraping
- **Template Generator**: Quick-start new extensions with best practices built-in
- **Well-Documented Code**: Every pattern explained, learning notes throughout

### For VFWidgets Evaluators

ViloWeb demonstrates:
- **ChromeTabbedWindow**: Complex multi-tab management with Chrome styling
- **ViloCodeWindow**: Professional sidebar layout with multiple panels
- **vfwidgets-theme**: Seamless theme integration and switching
- **vfwidgets-multisplit**: Split-screen browsing (optional)

### For Web Automation Engineers

ViloWeb provides:
- **Python API**: Control browser from scripts, no JavaScript required
- **Element Selection**: CSS selectors, XPath, BeautifulSoup integration
- **Form Automation**: Fill forms, click buttons, navigate pages
- **Data Extraction**: HTML parsing, structured data export
- **Screenshots/PDFs**: Capture pages programmatically

### Development Philosophy

**Code as Teaching Material:**
- Extensive comments explaining "why" not just "what"
- Tutorial-style READMEs in each module
- Learning objectives documented
- Examples progress from simple to complex
- Best practices demonstrated throughout

**Python-First Approach:**
- Extensions written in Python, not JavaScript
- Full Python ecosystem available (BeautifulSoup, requests, pandas, etc.)
- Qt/PySide6 APIs accessible from extensions
- Native UI creation with Qt widgets

**Real-World Application:**
- Not a toy or demo – fully functional browser
- Professional architecture suitable for study
- Production-quality code with tests
- Deployable and embeddable

### Next Steps

**Phase 1 (Weeks 1-2): Foundation + Learning Features**
1. Basic browser functionality (tabs, navigation, bookmarks)
2. Integrated Python console panel
3. First tutorial ("Your First Extension")
4. Ad blocker example extension
5. Comprehensive code comments

**Phase 2 (Weeks 3-4): VFWidgets Showcase**
1. All sidebar panels (bookmarks, history, downloads)
2. Theme system demonstration
3. More tutorial content
4. vfwidgets-multisplit integration (optional)

**Phase 3 (Weeks 5-8): Extension System**
1. Complete extension API
2. Page modifier extension example
3. Web scraper extension example
4. Extension template generator
5. Interactive tutorial system

**Phase 4 (Weeks 9-12): Advanced Features + Polish**
1. Advanced automation examples
2. Testing framework integration
3. Headless mode for scripts
4. Package for external use (`pip install viloweb`)
5. Comprehensive documentation site

### Success Criteria (Revised for Educational Focus)

**Developer Learning:**
- ✅ Can learn QWebEngineView from code examples
- ✅ Can write first Python extension in <30 minutes
- ✅ Can understand JavaScript bridge after reading docs
- ✅ Can automate web tasks after tutorials

**VFWidgets Showcase:**
- ✅ All major widgets demonstrated
- ✅ Professional application architecture
- ✅ Theme integration exemplified
- ✅ Reusable patterns documented

**Unique Value:**
- ✅ Python extensions work reliably
- ✅ Automation API is intuitive
- ✅ Code quality suitable for learning
- ✅ Documentation comprehensive

---

**Target Audience**: Python developers learning QtWebEngine, VFWidgets evaluators, web automation engineers

**Primary Goal**: Education and showcasing, not end-user browser competition

**Unique Selling Point**: Only browser teaching QtWebEngine with Python-first extensions

---

**Document Version:** 2.0
**Last Updated:** 2025-10-17 (Revised for Educational Focus)
**Author:** VFWidgets Team
**Status:** Ready for Educational Implementation
