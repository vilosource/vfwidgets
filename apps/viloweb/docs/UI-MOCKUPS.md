# ViloWeb UI Design Mockups

**Version**: 1.0
**Last Updated**: 2025-10-17
**Status**: Design Phase

---

## Table of Contents

1. [Main Window Layout](#1-main-window-layout)
2. [Browser Area](#2-browser-area)
3. [Sidebar Panels](#3-sidebar-panels)
4. [Python Console Panel](#4-python-console-panel)
5. [Extension Manager UI](#5-extension-manager-ui)
6. [Dev Tools Panel](#6-dev-tools-panel)
7. [Tutorial Viewer](#7-tutorial-viewer)
8. [Settings Interface](#8-settings-interface)
9. [Context Menus](#9-context-menus)
10. [Theme Variations](#10-theme-variations)

---

## 1. Main Window Layout

### 1.1 Overview with VS Code-style Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ViloWeb - Example Domain                                                [_][□][X]   │
├───┬─────────────────────────────────────────────────────────────────────────────────┤
│   │                                                                                 │
│ ⌂ │  ◄  ►  ⟲  🏠   https://example.com                           🔖  ⋯  👤        │
│ 🔖│                                                                                 │
│ 🕒│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│ ⬇ │  │ Welcome to Example Domain                               [Tab 1]  [+]     │ │
│ 🧩│  ├──────────────────────────────────────────────────────────────────────────┤ │
│ 🖥 │  │                                                                          │ │
│ ⚙ │  │  Example Domain                                                          │ │
│   │  │  ═══════════════                                                         │ │
│   │  │                                                                          │ │
│   │  │  This domain is for use in illustrative examples in documents.          │ │
│   │  │  You may use this domain in literature without prior coordination       │ │
│   │  │  or asking for permission.                                              │ │
│   │  │                                                                          │ │
│   │  │  More information...                                                     │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  │                                                                          │ │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │
├───┴─────────────────────────────────────────────────────────────────────────────────┤
│ ⚡ Python Console | 3 extensions loaded | Dark Theme                                │
└─────────────────────────────────────────────────────────────────────────────────────┘

Legend:
├─ Left: Activity Bar (icons for panels)
├─ Top: Navigation Bar (back, forward, refresh, URL bar)
├─ Main: Browser Content Area (ChromeTabbedWindow)
└─ Bottom: Status Bar
```

### 1.2 Component Breakdown

**Activity Bar (Left - 50px wide):**
- ⌂ Browser (home view)
- 🔖 Bookmarks
- 🕒 History
- ⬇ Downloads
- 🧩 Extensions
- 🖥 Console (Python REPL)
- 🔧 Dev Tools
- 🔒 Security (NEW - defensive testing)
- ⚙ Settings

**Main Content:**
- Navigation Bar (compact, 40px height)
- Browser Area (ChromeTabbedWindow)
- Collapsible Sidebar (300px default, expandable)

---

## 2. Browser Area

### 2.1 Navigation Bar (Compact Mode)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ◄  ►  ⟲  🏠   https://example.com/page?query=test#section        🔖  ⋯  👤     │
└─────────────────────────────────────────────────────────────────────────────────┘
 ▲  ▲  ▲  ▲                                                          ▲  ▲  ▲
 │  │  │  │                                                          │  │  │
 │  │  │  │                                                          │  │  └─ Profile
 │  │  │  │                                                          │  └─── More
 │  │  │  │                                                          └────── Bookmark
 │  │  │  └────────────────────────────────────────────────────────────────── Home
 │  │  └───────────────────────────────────────────────────────────────────── Reload
 │  └──────────────────────────────────────────────────────────────────────── Forward
 └─────────────────────────────────────────────────────────────────────────── Back

URL Bar Features:
- Smart autocomplete from history/bookmarks
- HTTPS indicator
- Site permissions indicator
- Extension actions on right
```

### 2.2 Tab Bar (Chrome-style)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌐 Example Domain        ✕  │ 📄 Documentation        ✕  │ 🔍 Search    ✕  │ + │
└──────────────────────────────────────────────────────────────────────────────┘
   ▲                           ▲                           ▲                  ▲
   │                           │                           │                  │
   └─ Active Tab               └─ Inactive Tab             └─ Inactive Tab    └─ New Tab

Tab Features:
- Favicon + Title
- Close button (✕)
- Drag to reorder
- Middle-click to close
- Ctrl+Click to open in new tab
- Tab overflow: scrollable or dropdown
```

### 2.3 Web Content Area with Loading State

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Loading... ████████████████────────────── 72%                                │
│                                                                               │
│  [Page content renders here as it loads]                                     │
│                                                                               │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sidebar Panels

### 3.1 Bookmarks Panel

```
┌───────────────────────────────────┐
│ 🔖 Bookmarks            [+] [⚙]  │
├───────────────────────────────────┤
│ 🔍 Search bookmarks...            │
├───────────────────────────────────┤
│                                   │
│ 📁 Work                        ▼  │
│    🌐 GitHub                      │
│    🌐 Stack Overflow              │
│    🌐 Qt Documentation            │
│                                   │
│ 📁 Learning                    ▼  │
│    🌐 Python Tutorial             │
│    🌐 QtWebEngine Docs            │
│    🌐 VFWidgets Examples          │
│                                   │
│ 📁 Reading List                ▶  │
│                                   │
│ 📌 Unsorted                       │
│    🌐 Example Site 1              │
│    🌐 Example Site 2              │
│                                   │
│ [Import] [Export] [Organize]      │
│                                   │
└───────────────────────────────────┘

Interactions:
- Right-click: Edit, Delete, Move to folder
- Drag & drop: Reorder and organize
- Double-click: Open in current tab
- Ctrl+Click: Open in new tab
- Star icon in URL bar: Quick add bookmark
```

### 3.2 History Panel

```
┌───────────────────────────────────┐
│ 🕒 History              [🗑] [⚙]  │
├───────────────────────────────────┤
│ 🔍 Search history...              │
├───────────────────────────────────┤
│ 📅 Filter: [Today ▼] [All Sites ▼]│
├───────────────────────────────────┤
│                                   │
│ Today                             │
│ ───────────────────────────       │
│ 14:32  🌐 Example Domain          │
│        https://example.com        │
│                                   │
│ 13:45  📄 Qt Documentation        │
│        https://doc.qt.io/...      │
│                                   │
│ 12:20  🐍 Python.org              │
│        https://python.org         │
│                                   │
│ Yesterday                         │
│ ───────────────────────────       │
│ 18:45  🌐 GitHub                  │
│ 16:30  📚 Stack Overflow          │
│                                   │
│ This Week                         │
│ ───────────────────────────       │
│ Oct 15  🔧 VFWidgets Docs         │
│ Oct 14  🖥  Terminal Tutorial     │
│                                   │
└───────────────────────────────────┘

Features:
- Grouped by date
- Search with filters
- Right-click: Delete, Open, Copy URL
- Clear history button (with date range)
```

### 3.3 Downloads Panel

```
┌───────────────────────────────────┐
│ ⬇ Downloads            [📂] [⚙]  │
├───────────────────────────────────┤
│                                   │
│ In Progress                       │
│ ───────────────────────────       │
│ 📄 document.pdf                   │
│ ████████████────── 67% (2.1 MB)  │
│ ⏸ Pause | ✕ Cancel                │
│                                   │
│ Completed                         │
│ ───────────────────────────       │
│ ✓ image.png             [📂] [⋯] │
│   234 KB • Just now               │
│                                   │
│ ✓ archive.zip           [📂] [⋯] │
│   15.3 MB • 5 min ago             │
│                                   │
│ ✓ video.mp4             [📂] [⋯] │
│   128 MB • Yesterday              │
│                                   │
│ Failed                            │
│ ───────────────────────────       │
│ ✕ large_file.iso        [⟲] [⋯] │
│   Network error                   │
│                                   │
│ [Clear Completed] [Show Folder]   │
│                                   │
└───────────────────────────────────┘

Features:
- Real-time progress
- Pause/resume
- Open file location
- Retry failed downloads
- Clear completed items
```

---

## 4. Python Console Panel

### 4.1 Interactive Python REPL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🖥 Python Console                                [Clear] [Help] [Settings]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Python 3.11.5 | PySide6 6.9.0 | QtWebEngine 6.9.0                          │
│ ViloWeb Educational Browser Console                                        │
│                                                                             │
│ Available objects:                                                         │
│   browser - Browser area controller                                        │
│   tab     - Current active tab                                             │
│   api     - Extension API                                                  │
│                                                                             │
│ Try:                                                                       │
│   tab.navigate("https://example.com")                                      │
│   tab.execute_js("document.title")                                         │
│   browser.new_tab("https://python.org")                                    │
│                                                                             │
│ ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│ >>> tab.navigate("https://example.com")                                    │
│                                                                             │
│ >>> tab.execute_js("document.title")                                       │
│ 'Example Domain'                                                            │
│                                                                             │
│ >>> tab.execute_js("document.body.style.background = 'red'")               │
│ (Page background changes to red)                                           │
│                                                                             │
│ >>> browser.new_tab("https://python.org")                                  │
│ <BrowserTab url='https://python.org'>                                      │
│                                                                             │
│ >>> # List all open tabs                                                   │
│ >>> for i, t in enumerate(browser.get_all_tabs()):                         │
│ ...     print(f"{i}: {t.url()}")                                           │
│ ...                                                                         │
│ 0: https://example.com                                                      │
│ 1: https://python.org                                                       │
│                                                                             │
│ >>> _                                                                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ >>> |                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
    ▲
    └─ Input cursor (with syntax highlighting and autocomplete)

Features:
- Full Python REPL
- Syntax highlighting (Pygments)
- Autocomplete with Tab
- Multi-line input support
- Access to browser, tab, api objects
- Command history (↑ ↓)
- Clear output button
- Save session to file
- Load and execute Python scripts
```

### 4.2 Console Autocomplete Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ >>> tab.exe|                                                                │
│             ┌───────────────────────────────┐                               │
│             │ execute_js(code, callback)    │ ← Highlighted selection       │
│             │ execute_script(...)           │                               │
│             ├───────────────────────────────┤                               │
│             │ Execute JavaScript in page    │ ← Docstring preview           │
│             └───────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘

Autocomplete triggered by:
- Tab key
- Ctrl+Space
- Automatic after "."
```

---

## 5. Extension Manager UI

### 5.1 Extensions Panel

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🧩 Extensions                              [Install] [Browse] [Settings]  │
├───────────────────────────────────────────────────────────────────────────┤
│ 🔍 Search extensions...                                                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Installed (3)                                                             │
│ ────────────────────────────────────────────────────────                  │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ 🛡️ Ad Blocker                                        [⚙] [✓] [✕] │  │
│ │ Version 1.2.0 by Community                                          │  │
│ │                                                                     │  │
│ │ Blocks ads and tracking scripts. Uses filter lists to remove       │  │
│ │ advertisements from web pages.                                      │  │
│ │                                                                     │  │
│ │ 🔵 Active • Blocked 247 requests today                              │  │
│ │                                                                     │  │
│ │ [Configure] [View Code] [Disable]                                   │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ 🎨 Dark Mode                                         [⚙] [✓] [✕] │  │
│ │ Version 1.0.3 by VFWidgets Team                                     │  │
│ │                                                                     │  │
│ │ Applies dark mode to all websites using CSS injection. Inverts     │  │
│ │ colors intelligently while preserving images.                       │  │
│ │                                                                     │  │
│ │ 🔵 Active • Applied to 42 pages                                     │  │
│ │                                                                     │  │
│ │ [Configure] [View Code] [Disable]                                   │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ 📊 Web Scraper                                       [⚙] [✓] [✕] │  │
│ │ Version 2.1.0 by Data Team                                          │  │
│ │                                                                     │  │
│ │ Extract structured data from web pages using BeautifulSoup and     │  │
│ │ CSS selectors. Export to JSON, CSV, or Excel.                      │  │
│ │                                                                     │  │
│ │ 🔴 Inactive                                                          │  │
│ │                                                                     │  │
│ │ [Configure] [View Code] [Enable]                                    │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ Available Extensions (Browse)                                             │
│ ────────────────────────────────────────────────────────                  │
│ • Screenshot Tool                                                         │
│ • Link Checker                                                            │
│ • Markdown Converter                                                      │
│ • Form Filler                                                             │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- Enable/disable extensions
- Configure extension settings
- View Python source code
- Install from file or URL
- Browse extension templates
- Usage statistics
```

### 5.2 Extension Configuration Dialog

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Configure: Ad Blocker Extension                                   [✕]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Basic Settings                                                            │
│ ──────────────────────────────────────────────────                        │
│                                                                           │
│ ☑ Enable ad blocking                                                     │
│ ☑ Block tracking scripts                                                 │
│ ☑ Hide ad placeholders                                                   │
│ ☐ Block social media widgets                                             │
│                                                                           │
│ Filter Lists                                                              │
│ ──────────────────────────────────────────────────────                    │
│                                                                           │
│ ☑ EasyList (recommended)                                                 │
│ ☑ EasyPrivacy                                                            │
│ ☐ Fanboy's Annoyances                                                    │
│ ☐ Custom list...                   [Add Custom List]                     │
│                                                                           │
│ Whitelist (Allow ads on these sites)                                     │
│ ──────────────────────────────────────────────────────                    │
│                                                                           │
│ ┌───────────────────────────────────────────────────────────────┐        │
│ │ github.com                                           [Remove]  │        │
│ │ stackoverflow.com                                    [Remove]  │        │
│ │ python.org                                           [Remove]  │        │
│ └───────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ [Add Site to Whitelist...]                                               │
│                                                                           │
│ Statistics                                                                │
│ ──────────────────────────────────────────────────────                    │
│                                                                           │
│ Total blocked: 1,234 requests                                            │
│ Today: 247 requests                                                       │
│ This week: 1,891 requests                                                 │
│                                                                           │
│                                                                           │
│                                        [Reset Stats] [Cancel] [Apply]     │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Dev Tools Panel

### 6.1 Developer Tools Overview

This is a **unique educational feature** that teaches web development concepts while browsing.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools                                                [_][□][✕]│
├───────────────────────────────────────────────────────────────────────────┤
│ [Elements] [Console] [Network] [Sources] [Performance] [Application]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ [Main content area - varies by tab selected]                             │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Elements Inspector

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - Elements                                             │
├────────────────────────────────────────────────────────────┬──────────────┤
│ DOM Tree                                                   │ Styles       │
│ ────────────────────────────────────────                   │              │
│                                                            │ element.style│
│ ▼ <!DOCTYPE html>                                          │              │
│   ▼ <html lang="en">                                       │ color:       │
│     ▼ <head>                                               │   #333333    │
│         <meta charset="UTF-8">                             │ font-size:   │
│         <title>Example Domain</title>                      │   16px       │
│     ▼ <body>                                               │              │
│       ▼ <div class="container">                            │ Computed     │
│           ► <h1>Example Domain</h1> ← Selected             │              │
│           ▼ <p class="description">                        │ Box Model    │
│               This domain is for use in...                 │ ┌──────────┐ │
│           ► <a href="...">More information...</a>          │ │ margin   │ │
│       ► <footer>                                           │ │ ┌──────┐ │ │
│                                                            │ │ │border│ │ │
│ 🔍 Search DOM...                                           │ │ │┌────┐│ │ │
│                                                            │ │ ││pad ││ │ │
│ [Inspect Element Mode] [Copy HTML] [Edit HTML]            │ │ └└────┘┘ │ │
│                                                            │ └──────────┘ │
│                                                            │              │
│                                                            │ Layout       │
│                                                            │   width:     │
│                                                            │   height:    │
│                                                            │              │
└────────────────────────────────────────────────────────────┴──────────────┘

Features:
- Click elements to inspect
- Edit HTML in place
- Modify CSS live
- View computed styles
- Box model visualization
- Copy selectors (for scraping extensions!)
```

### 6.3 Console Tab (JavaScript Console)

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - Console                                              │
├───────────────────────────────────────────────────────────────────────────┤
│ [Top ▼] [Default levels ▼] [🚫] Clear                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ ℹ️  example.com loaded                                                    │
│                                                                           │
│ ⚠️ [Warning] Resource interpreted as Stylesheet but transferred with MIME│
│    type text/html: "https://example.com/styles.css"                      │
│                                                                           │
│ ℹ️  3 extensions active: Ad Blocker, Dark Mode, Web Scraper              │
│                                                                           │
│ > console.log("Hello from JavaScript")                                    │
│ Hello from JavaScript                                                     │
│                                                                           │
│ > document.querySelectorAll('a')                                          │
│ ► NodeList(5) [a, a, a, a, a]                                            │
│                                                                           │
│ > $0                                                                      │
│ ► <h1>Example Domain</h1>                                                │
│                                                                           │
│ 💡 Educational Tip:                                                       │
│    Try: document.querySelector('h1').textContent                          │
│    This selects the first h1 and gets its text!                          │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│ > |                                                                       │
└───────────────────────────────────────────────────────────────────────────┘
    ▲
    └─ JavaScript REPL (different from Python Console!)

Features:
- JavaScript execution in page context
- Console.log output capture
- Error/warning filtering
- Object inspection
- $0 = selected element from Elements tab
- Educational tips and hints
```

### 6.4 Network Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - Network                                              │
├───────────────────────────────────────────────────────────────────────────┤
│ ☑ Preserve log  ☑ Disable cache  [⚪] Record  [🚫] Clear  [⬇] Export HAR │
│                                                                           │
│ Filter: [All ▼] [XHR ▼] [JS ▼] [CSS ▼] [Img ▼] [Media ▼]  🔍 Search     │
├───────────────────────────────────────────────────────────────────────────┤
│ Name              Method  Status  Type       Size     Time    Waterfall  │
│ ───────────────────────────────────────────────────────────────────────  │
│ example.com       GET     200     document   1.2 KB   124ms   ████──────│
│ styles.css        GET     200     stylesheet 4.5 KB   45ms    ──██──────│
│ script.js         GET     200     script     12 KB    78ms    ────███───│
│ logo.png          GET     200     image      8.3 KB   156ms   ──────████│
│ tracking.js       GET     blocked script     -        -       ✕ BLOCKED │
│ ad-banner.jpg     GET     blocked image      -        -       ✕ BLOCKED │
│ api/data          XHR     200     json       234 B    892ms   ────────██│
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│ 7 requests  |  26.2 KB transferred  |  1.35s load time  |  2 blocked     │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│ Request Details (selected: example.com)                                  │
│ ──────────────────────────────────────────────────────────────           │
│                                                                           │
│ [Headers] [Preview] [Response] [Timing]                                  │
│                                                                           │
│ General:                                                                  │
│   Request URL:    https://example.com/                                   │
│   Request Method: GET                                                     │
│   Status Code:    200 OK                                                  │
│   Remote Address: 93.184.216.34:443                                      │
│                                                                           │
│ Response Headers:                                                         │
│   Content-Type:   text/html; charset=utf-8                               │
│   Content-Length: 1256                                                    │
│   Date:           Fri, 17 Oct 2025 10:30:00 GMT                          │
│   Server:         nginx/1.20.1                                           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- All network requests logged
- Filter by type (XHR, JS, CSS, images)
- View request/response headers
- Preview JSON responses
- Timing breakdown
- Show blocked requests (by extensions!)
- Export HAR for analysis
- Educational tooltips explaining HTTP concepts
```

### 6.5 Performance Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - Performance                                          │
├───────────────────────────────────────────────────────────────────────────┤
│ [⚪ Record] [↻ Reload and Record] [🗑️ Clear] [⬇ Export] [Screenshots ▼] │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Page Load Timeline                                                        │
│ ────────────────────────────────────────────────────────────────────────  │
│                                                                           │
│ 0ms              500ms             1000ms            1500ms       2000ms │
│ │────────────────│────────────────│────────────────│───────────│─────   │
│ │                                                                         │
│ │█ HTML Parse                                                             │
│ │  ██ CSS Load                                                            │
│ │    ███ JS Load                                                          │
│ │      █████ JS Execution                                                 │
│ │           ██ First Paint                                                │
│ │             ████ DOM Content Loaded                                     │
│ │                  ███████ Images Load                                    │
│ │                          ██ Fully Loaded                                │
│ │                                                                         │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ Metrics:                                                                  │
│   First Paint:           423ms                                            │
│   First Contentful Paint: 456ms                                           │
│   DOM Content Loaded:    892ms                                            │
│   Load Complete:         1,345ms                                          │
│                                                                           │
│ Breakdown:                                                                │
│   HTML Parsing:          45ms                                             │
│   CSS Processing:        123ms                                            │
│   JavaScript Execution:  234ms                                            │
│   Image Decoding:        189ms                                            │
│   Layout:                67ms                                             │
│   Paint:                 34ms                                             │
│                                                                           │
│ 💡 Performance Tips:                                                      │
│    • Consider lazy-loading images below the fold                         │
│    • JavaScript execution time is high - check for blocking scripts      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- Visual timeline of page load
- Key performance metrics
- JavaScript profiling
- Memory usage tracking
- FPS (frames per second) monitoring
- Performance recommendations
- Educational explanations of metrics
```

### 6.6 Application Tab (Storage Inspector)

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - Application                                          │
├─────────────────────────┬─────────────────────────────────────────────────┤
│ Storage                 │ Local Storage (https://example.com)             │
│                         │ ──────────────────────────────────────          │
│ ▼ Local Storage         │                                                 │
│   • https://example.com │ Key                     Value                   │
│   • https://python.org  │ ───────────────────────────────────────────    │
│                         │ user_preference        "dark_mode"              │
│ ▼ Session Storage       │ last_visit             "2025-10-17T10:30:00Z"  │
│   • https://example.com │ page_views             "42"                     │
│                         │                                                 │
│ ▼ Cookies               │ [➕ Add] [✏️ Edit] [🗑️ Delete] [🗑️ Clear All]  │
│   • https://example.com │                                                 │
│   • https://python.org  │ ─────────────────────────────────────────────  │
│                         │                                                 │
│ ▼ IndexedDB             │ 💡 Educational Note:                            │
│   • example_db          │    Local Storage stores key-value pairs in the │
│                         │    browser. Data persists across sessions but  │
│ Cache Storage           │    is limited to ~5-10 MB per domain.          │
│                         │                                                 │
│                         │    Use Cases:                                   │
│                         │    • User preferences                           │
│                         │    • Temporary data                             │
│                         │    • Caching API responses                      │
│                         │                                                 │
├─────────────────────────┼─────────────────────────────────────────────────┤
│ Cookies                 │ Cookies for https://example.com                 │
│                         │ ──────────────────────────────────────          │
│                         │                                                 │
│                         │ Name        Value      Domain      Path  Expires│
│                         │ ──────────────────────────────────────────────  │
│                         │ session_id  xyz123... .example.com /     Session│
│                         │ theme       dark       example.com /     1 year │
│                         │                                                 │
│                         │ [🗑️ Delete All Cookies]                         │
│                         │                                                 │
└─────────────────────────┴─────────────────────────────────────────────────┘

Features:
- Browse all storage types
- Edit localStorage/sessionStorage
- View and delete cookies
- Inspect IndexedDB databases
- View service workers
- Clear storage by type
- Educational explanations
```

### 6.7 REST Client (Postman-like)

This is a **unique addition** not typically found in browsers!

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - REST Client                                          │
├───────────────────────────────────────────────────────────────────────────┤
│ [GET ▼] https://api.example.com/users/123                         [Send]  │
├───────────────────────────────────────────────────────────────────────────┤
│ [Params] [Headers] [Body] [Auth] [Scripts]                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Query Parameters                                                          │
│ ─────────────────────────────────────────────────────────────────         │
│                                                                           │
│ ☑ Key                    Value                         [✕]               │
│ ☑ format                 json                          [✕]               │
│ ☑ include                profile,posts                 [✕]               │
│ ☐ debug                  true                          [✕]               │
│                                                                           │
│ [+ Add Parameter]                                                         │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│ Response (Status: 200 OK, Time: 234ms, Size: 1.2 KB)                     │
│ ──────────────────────────────────────────────────────────────────────   │
│ [Body] [Headers] [Cookies]                                               │
│                                                                           │
│ {                                                                         │
│   "id": 123,                                                              │
│   "name": "John Doe",                                                     │
│   "email": "john@example.com",                                            │
│   "profile": {                                                            │
│     "bio": "Software developer",                                          │
│     "avatar": "https://example.com/avatar.jpg"                            │
│   },                                                                      │
│   "posts": [                                                              │
│     {"id": 1, "title": "First post"},                                     │
│     {"id": 2, "title": "Second post"}                                     │
│   ]                                                                       │
│ }                                                                         │
│                                                                           │
│ [Copy] [Download] [Format JSON] [Copy as Python Code]                    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- All HTTP methods (GET, POST, PUT, DELETE, etc.)
- Query parameters with checkboxes
- Request headers editor
- JSON/XML/Form body editor
- Authentication helpers (Basic, Bearer, OAuth)
- Response formatting
- Save requests to history
- **Generate Python code** (unique feature!)
- Environment variables support

Example Python Code Generation:
```python
import requests

url = "https://api.example.com/users/123"
params = {
    "format": "json",
    "include": "profile,posts"
}
headers = {
    "Authorization": "Bearer token123"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
print(data)
```
```

### 6.8 JSON Formatter/Viewer

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔧 Developer Tools - JSON Formatter                                       │
├───────────────────────────────────────────────────────────────────────────┤
│ [📋 Paste JSON] [📂 Load File] [Tree View] [Raw View] [Format] [Minify]  │
├─────────────────────────────────────────────┬─────────────────────────────┤
│ JSON Tree                                   │ Details                     │
│                                             │                             │
│ ▼ Object (root)                             │ Type: Object                │
│   ├─ id: 123                                │ Size: 456 bytes             │
│   ├─ name: "John Doe"                       │ Keys: 5                     │
│   ├─ email: "john@example.com"              │                             │
│   ├─▼ profile: Object                       │ Selected: profile           │
│   │   ├─ bio: "Software developer"          │                             │
│   │   └─ avatar: "https://..."              │ Type: Object                │
│   └─▼ posts: Array[2]                       │ Keys: 2                     │
│       ├─▼ [0]: Object                       │   • bio (string)            │
│       │   ├─ id: 1                          │   • avatar (string)         │
│       │   └─ title: "First post"            │                             │
│       └─▼ [1]: Object                       │ Copy Value                  │
│           ├─ id: 2                          │ Copy Path                   │
│           └─ title: "Second post"           │ Copy as Python Dict         │
│                                             │                             │
│ 🔍 Search JSON...                           │ JSONPath:                   │
│                                             │ $.profile.bio               │
│ [Expand All] [Collapse All]                 │                             │
│                                             │                             │
└─────────────────────────────────────────────┴─────────────────────────────┘

Features:
- Interactive tree view
- Syntax highlighting
- Search and filter
- JSONPath evaluation
- Type information
- Copy values/paths
- Generate Python code
- Validate JSON
- Diff two JSON objects
```

### 6.9 Security Testing Panel (NEW!)

This is a **unique educational feature** for learning web security and testing your own applications.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔒 Security Testing                                [Scan] [Report] [Help] │
├───────────────────────────────────────────────────────────────────────────┤
│ ⚠️  DEFENSIVE SECURITY ONLY - Test your own applications only             │
├───────────────────────────────────────────────────────────────────────────┤
│ Current Page: https://example.com                                         │
│ Last Scan: 2 minutes ago                                [🔄 Refresh Scan] │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ [Overview] [Headers] [Cookies] [Forms] [TLS] [Content]                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Security Score: 72/100                                                    │
│ ████████████████████────────── 72%                                       │
│                                                                           │
│ 🔴 Critical Issues: 0                                                     │
│ 🟠 High Risk:       2                                                     │
│ 🟡 Medium Risk:     4                                                     │
│ 🟢 Low Risk:        1                                                     │
│ ✅ Passed:          8                                                     │
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ HTTPS & Transport Security                                               │
│ ─────────────────────────────────────────────────────────────────────    │
│ ✅ HTTPS Enabled (TLS 1.3)                                                │
│ ✅ Valid Certificate (Expires: 2026-12-31)                                │
│ ⚠️  Missing Strict-Transport-Security (HSTS)                             │
│    Recommendation: Add HSTS header with long max-age                     │
│    [Learn More] [Copy Fix]                                               │
│                                                                           │
│ Content Security                                                          │
│ ─────────────────────────────────────────────────────────────────────    │
│ ⚠️  Missing Content-Security-Policy (CSP)                                │
│    Risk: XSS attacks possible                                            │
│    Recommendation: Implement strict CSP policy                           │
│    [Learn More] [Generate CSP]                                           │
│                                                                           │
│ ✅ X-Content-Type-Options: nosniff                                        │
│ 🟡 X-Frame-Options: Missing (Clickjacking risk)                          │
│    [Learn More] [Copy Fix]                                               │
│                                                                           │
│ [View Full Report] [Export PDF] [Export JSON]                            │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- Real-time security scanning
- Educational explanations
- One-click fixes (copy code)
- OWASP Top 10 coverage
- Export reports (PDF/JSON)
```

#### Security Headers Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔒 Security Testing - Headers                                             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Response Headers                                                          │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ✅ Strict-Transport-Security                                              │
│    max-age=31536000; includeSubDomains; preload                          │
│    📘 Forces HTTPS for 1 year, includes subdomains                       │
│    [View Documentation]                                                   │
│                                                                           │
│ ⚠️  Content-Security-Policy: MISSING                                      │
│    📘 CSP prevents XSS by controlling resource loading                   │
│    Suggested policy:                                                     │
│    ┌──────────────────────────────────────────────────────┐             │
│    │ Content-Security-Policy:                             │             │
│    │   default-src 'self';                                │             │
│    │   script-src 'self' 'unsafe-inline';                 │             │
│    │   style-src 'self' 'unsafe-inline';                  │             │
│    │   img-src 'self' data: https:;                       │             │
│    │   font-src 'self';                                   │             │
│    └──────────────────────────────────────────────────────┘             │
│    [Copy to Clipboard] [Test This CSP] [Learn More]                      │
│                                                                           │
│ ✅ X-Content-Type-Options: nosniff                                        │
│    📘 Prevents MIME type sniffing attacks                                │
│                                                                           │
│ ⚠️  X-Frame-Options: MISSING                                              │
│    📘 Prevents clickjacking by controlling iframe embedding              │
│    Recommended:                                                          │
│    ┌──────────────────────────────────────────────────────┐             │
│    │ X-Frame-Options: DENY                                │             │
│    │ or                                                   │             │
│    │ X-Frame-Options: SAMEORIGIN                          │             │
│    └──────────────────────────────────────────────────────┘             │
│    [Copy to Clipboard] [Learn More]                                      │
│                                                                           │
│ ✅ Referrer-Policy: strict-origin-when-cross-origin                       │
│    📘 Controls referrer information in requests                          │
│                                                                           │
│ ⚠️  Permissions-Policy: MISSING                                           │
│    📘 Controls browser features (camera, microphone, geolocation)        │
│    [Generate Policy] [Learn More]                                        │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Cookies Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔒 Security Testing - Cookies                                             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Cookie Security Audit (3 cookies found)                                  │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ 🟡 session_id                                          [Details] [✕]│  │
│ │ Value: abc123xyz... (truncated)                                     │  │
│ │                                                                     │  │
│ │ Security Attributes:                                                │  │
│ │ ✅ Secure:    Yes (HTTPS only)                                      │  │
│ │ ⚠️  HttpOnly:  No  ← Accessible to JavaScript (XSS risk)           │  │
│ │ ⚠️  SameSite:  None ← CSRF vulnerable                               │  │
│ │ • Domain:     .example.com                                          │  │
│ │ • Path:       /                                                     │  │
│ │ • Expires:    Session                                               │  │
│ │                                                                     │  │
│ │ 🛡️  Recommendations:                                                 │  │
│ │   1. Add HttpOnly flag to prevent JavaScript access                │  │
│ │   2. Set SameSite=Lax or SameSite=Strict for CSRF protection       │  │
│ │                                                                     │  │
│ │   Set-Cookie: session_id=value; Secure; HttpOnly; SameSite=Lax    │  │
│ │   [Copy Fix] [Learn More]                                           │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ ✅ preferences                                         [Details] [✕]│  │
│ │ Value: theme=dark&lang=en                                           │  │
│ │                                                                     │  │
│ │ Security Attributes:                                                │  │
│ │ ✅ Secure:    Yes                                                   │  │
│ │ ✅ HttpOnly:  Yes                                                   │  │
│ │ ✅ SameSite:  Strict                                                │  │
│ │ • Domain:     example.com                                           │  │
│ │ • Path:       /                                                     │  │
│ │ • Expires:    2026-10-17                                            │  │
│ │                                                                     │  │
│ │ ✅ All security attributes properly configured                       │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ 💡 Educational Note:                                                      │
│    Cookie Security Flags:                                                │
│    • Secure:   Only sent over HTTPS                                      │
│    • HttpOnly: Not accessible to JavaScript (prevents XSS)              │
│    • SameSite: Restricts cross-site requests (prevents CSRF)            │
│                                                                           │
│ [Export Cookie Report] [Delete All Cookies]                              │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Forms Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔒 Security Testing - Forms                                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Form Security Analysis (2 forms found)                                   │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ 🔴 Login Form                                          [Inspect]     │  │
│ │ Action: /login                                                      │  │
│ │ Method: POST                                                        │  │
│ │                                                                     │  │
│ │ 🔴 CRITICAL: Password form submitting to HTTP                       │  │
│ │    Form action: http://example.com/login                           │  │
│ │    Impact: Credentials sent in plaintext!                          │  │
│ │    Fix: Change to https://example.com/login                        │  │
│ │                                                                     │  │
│ │ ⚠️  Missing CSRF Token                                              │  │
│ │    Impact: Vulnerable to Cross-Site Request Forgery                │  │
│ │    Fix: Add hidden CSRF token field                                │  │
│ │    <input type="hidden" name="csrf_token" value="...">             │  │
│ │    [Learn About CSRF]                                               │  │
│ │                                                                     │  │
│ │ 🟡 Password Autocomplete Enabled                                    │  │
│ │    Recommendation: Set autocomplete="new-password" for new logins  │  │
│ │    [Learn More]                                                     │  │
│ │                                                                     │  │
│ │ Fields:                                                             │  │
│ │ • username (text)                                                   │  │
│ │ • password (password) - autocomplete: on                           │  │
│ │                                                                     │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐  │
│ │ ✅ Contact Form                                        [Inspect]     │  │
│ │ Action: https://example.com/contact                                 │  │
│ │ Method: POST                                                        │  │
│ │                                                                     │  │
│ │ ✅ HTTPS Action URL                                                  │  │
│ │ ✅ CSRF Token Present (name="csrf_token")                            │  │
│ │ ✅ No sensitive fields                                               │  │
│ │                                                                     │  │
│ │ Fields:                                                             │  │
│ │ • name (text)                                                       │  │
│ │ • email (email)                                                     │  │
│ │ • message (textarea)                                                │  │
│ │ • csrf_token (hidden)                                               │  │
│ │                                                                     │  │
│ └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ 💡 Tutorial: [Testing Form Security in Your Applications]                │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

#### TLS/Certificate Tab

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 🔒 Security Testing - TLS/Certificate                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Certificate Information                                                   │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ✅ Valid Certificate (Issued by Let's Encrypt)                            │
│                                                                           │
│ Subject:                                                                  │
│   Common Name (CN):  example.com                                          │
│   Organization (O):  Example Corp                                         │
│   Country (C):       US                                                   │
│                                                                           │
│ Issuer:                                                                   │
│   CN: Let's Encrypt Authority X3                                          │
│   O:  Let's Encrypt                                                       │
│                                                                           │
│ Validity:                                                                 │
│   Not Before: 2025-07-01 00:00:00 UTC                                     │
│   Not After:  2026-09-30 23:59:59 UTC                                     │
│   ⏱  Valid for 315 more days                                             │
│                                                                           │
│ Public Key:                                                               │
│   Algorithm:  RSA 2048 bits                                               │
│   Fingerprint (SHA-256):                                                  │
│   A1:B2:C3:D4:E5:F6:A7:B8:C9:D0:E1:F2:A3:B4:C5:D6                        │
│                                                                           │
│ Subject Alternative Names (SANs):                                         │
│   • example.com                                                           │
│   • www.example.com                                                       │
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ TLS Connection                                                            │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ✅ Protocol:      TLS 1.3                                                 │
│ ✅ Cipher Suite:  TLS_AES_128_GCM_SHA256                                  │
│ ✅ Key Exchange:  X25519                                                  │
│ ✅ Perfect Forward Secrecy (PFS): Enabled                                 │
│                                                                           │
│ 💡 What this means:                                                       │
│    • TLS 1.3 is the latest, most secure protocol                         │
│    • AES-128-GCM provides strong encryption                              │
│    • PFS ensures past communications remain secure if key is compromised │
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ Certificate Chain                                                         │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ ✅ [0] example.com                                                        │
│    ↓ Issued by                                                            │
│ ✅ [1] Let's Encrypt Authority X3 (Intermediate)                          │
│    ↓ Issued by                                                            │
│ ✅ [2] DST Root CA X3 (Root)                                              │
│                                                                           │
│ ✅ Chain validation: Success                                              │
│                                                                           │
│ [View Full Chain] [Export Certificate] [Test Certificate]                │
│                                                                           │
│ 📘 Tutorial: [Understanding TLS and Certificates]                         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Ethical Use Warning Dialog

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Security Testing - First Time Setup                               [✕]    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ╔═══════════════════════════════════════════════════════════════╗      │
│   ║       SECURITY TESTING - ETHICAL USE ONLY                     ║      │
│   ╟───────────────────────────────────────────────────────────────╢      │
│   ║                                                               ║      │
│   ║  ViloWeb security tools are for DEFENSIVE security:          ║      │
│   ║                                                               ║      │
│   ║  ✓ Testing YOUR OWN web applications                         ║      │
│   ║  ✓ Learning security concepts                                ║      │
│   ║  ✓ Security research with permission                         ║      │
│   ║  ✓ Educational demonstrations                                ║      │
│   ║                                                               ║      │
│   ║  ✗ DO NOT test applications without permission               ║      │
│   ║  ✗ DO NOT use for malicious purposes                         ║      │
│   ║  ✗ DO NOT attack systems you don't own                       ║      │
│   ║                                                               ║      │
│   ║  Unauthorized security testing may be illegal.                ║      │
│   ║  Always obtain written permission before testing.             ║      │
│   ║                                                               ║      │
│   ║  By clicking "I Understand", you agree to use these tools     ║      │
│   ║  ethically and in accordance with applicable laws.            ║      │
│   ║                                                               ║      │
│   ╚═══════════════════════════════════════════════════════════════╝      │
│                                                                           │
│   ☑ I understand and agree to use security tools ethically               │
│   ☑ Don't show this again                                                │
│                                                                           │
│                          [Cancel] [I Understand - Enable Tools]          │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Tutorial Viewer

### 7.1 Interactive Tutorial Panel

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 📚 Tutorial: Your First Extension                  [Prev] [Next] [Index]  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ # Creating Your First Extension                                          │
│                                                                           │
│ In this tutorial, you'll create a simple extension that shows a          │
│ notification when a page loads. This introduces you to:                  │
│                                                                           │
│ • Extension base class (ViloWebExtension)                                │
│ • Lifecycle hooks (on_page_load)                                         │
│ • Extension API (show_notification)                                      │
│                                                                           │
│ ## Step 1: Create Extension Directory                                    │
│                                                                           │
│ Create a new directory for your extension:                               │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────┐      │
│ │ $ mkdir ~/.viloweb/extensions/hello_world                       │      │
│ │ $ cd ~/.viloweb/extensions/hello_world                          │      │
│ └─────────────────────────────────────────────────────────────────┘      │
│                                                                           │
│ ## Step 2: Write the Extension                                           │
│                                                                           │
│ Create `hello_world.py`:                                                 │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────┐      │
│ │ from viloweb.extensions import ViloWebExtension                 │      │
│ │                                                                  │      │
│ │ class HelloWorldExtension(ViloWebExtension):                    │      │
│ │     name = "Hello World"                                        │      │
│ │     version = "1.0.0"                                           │      │
│ │     description = "Shows a greeting on page load"               │      │
│ │     author = "Your Name"                                        │      │
│ │                                                                  │      │
│ │     def on_page_load(self, url: str, page):                     │      │
│ │         self.api.show_notification(                             │      │
│ │             f"Hello! You loaded {url}"                          │      │
│ │         )                                                        │      │
│ └─────────────────────────────────────────────────────────────────┘      │
│                                                                           │
│ [Copy Code]                                                               │
│                                                                           │
│ ## Step 3: Load the Extension                                            │
│                                                                           │
│ 1. Open ViloWeb                                                          │
│ 2. Click Extensions icon (🧩) in activity bar                            │
│ 3. Click "Install" button                                                │
│ 4. Select `hello_world.py`                                               │
│ 5. Extension is now active!                                              │
│                                                                           │
│ ## Try It Out                                                             │
│                                                                           │
│ Navigate to any website - you should see a notification!                 │
│                                                                           │
│ [⚡ Load Example] [▶️ Run Code] [💬 Ask Question]                         │
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│                                                                           │
│ Progress: Tutorial 1 of 6                                                │
│ ████████────────────────────── 33%                                       │
│                                                                           │
│                                    [Skip Tutorial] [Mark as Complete]    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

Features:
- Markdown rendering with syntax highlighting
- Interactive code examples
- Copy code buttons
- Step-by-step guidance
- Progress tracking
- Quick actions (load example, run code)
- Navigation (prev/next/index)
- Ask questions (opens docs or forum)
```

### 7.2 Tutorial Index

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 📚 Tutorials - Index                                              [✕]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Getting Started                                                           │
│ ─────────────────────────────────────────────────────────────────         │
│                                                                           │
│ ✓ 1. Your First Extension              [View] ← Completed               │
│   Learn the basics of extension development                              │
│   Duration: 15 minutes                                                    │
│                                                                           │
│ ⏳ 2. Understanding QWebEngineView      [Start] ← In Progress            │
│   Deep dive into Qt web rendering                                        │
│   Duration: 30 minutes                                                    │
│                                                                           │
│   3. JavaScript Bridge Patterns        [Start]                           │
│   Master Python-JavaScript communication                                 │
│   Duration: 25 minutes                                                    │
│                                                                           │
│ Extension Development                                                     │
│ ─────────────────────────────────────────────────────────────────         │
│                                                                           │
│   4. Building an Ad Blocker            [Start]                           │
│   Pattern matching and request blocking                                  │
│   Duration: 45 minutes                                                    │
│                                                                           │
│   5. Page Modification Extension       [Start]                           │
│   CSS injection and DOM manipulation                                     │
│   Duration: 40 minutes                                                    │
│                                                                           │
│   6. Web Scraping with Python          [Start]                           │
│   Beautiful Soup integration                                             │
│   Duration: 1 hour                                                        │
│                                                                           │
│ Advanced Topics                                                           │
│ ─────────────────────────────────────────────────────────────────         │
│                                                                           │
│   7. Browser Automation API            [Start]                           │
│   Headless browsing and scripting                                        │
│   Duration: 45 minutes                                                    │
│                                                                           │
│   8. Extension Publishing              [Start]                           │
│   Share your extensions                                                  │
│   Duration: 20 minutes                                                    │
│                                                                           │
│ ─────────────────────────────────────────────────────────────────────    │
│ Overall Progress: 1 of 8 tutorials completed (12%)                       │
│ ██───────────────────────────────────── 12%                              │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Settings Interface

### 8.1 Settings Panel

```
┌───────────────────────────────────────────────────────────────────────────┐
│ ⚙ Settings                                                        [✕]     │
├─────────────────────┬─────────────────────────────────────────────────────┤
│ General             │ General Settings                                    │
│ Appearance          │ ──────────────────────────────────────              │
│ Privacy             │                                                     │
│ Extensions          │ Startup                                             │
│ Developer Tools     │                                                     │
│ Advanced            │ ⚪ Open new tab                                      │
│ About               │ ⚪ Restore last session                              │
│                     │ ⚫ Open homepage                                     │
│                     │                                                     │
│                     │ Homepage: [https://example.com    ] [Set Current]  │
│                     │                                                     │
│                     │ New Tab Behavior                                    │
│                     │                                                     │
│                     │ [Blank page ▼]                                      │
│                     │   • Blank page                                      │
│                     │   • Homepage                                        │
│                     │   • Most visited sites                              │
│                     │                                                     │
│                     │ Downloads                                           │
│                     │                                                     │
│                     │ Download location:                                  │
│                     │ [/home/user/Downloads            ] [Browse...]      │
│                     │                                                     │
│                     │ ☑ Ask where to save each file                       │
│                     │                                                     │
│                     │ Search Engine                                       │
│                     │                                                     │
│                     │ [DuckDuckGo ▼]                                      │
│                     │   • DuckDuckGo                                      │
│                     │   • Google                                          │
│                     │   • Bing                                            │
│                     │   • Custom...                                       │
│                     │                                                     │
└─────────────────────┴─────────────────────────────────────────────────────┘
```

### 8.2 Appearance Settings

```
┌───────────────────────────────────────────────────────────────────────────┐
│ ⚙ Settings > Appearance                                          [✕]     │
├─────────────────────┬─────────────────────────────────────────────────────┤
│ General             │ Appearance                                          │
│ Appearance     ◄    │ ──────────────────────────────────────              │
│ Privacy             │                                                     │
│ Extensions          │ Theme                                               │
│ Developer Tools     │                                                     │
│ Advanced            │ ⚫ Dark                                              │
│ About               │ ⚪ Light                                             │
│                     │ ⚪ System (follow OS)                                │
│                     │                                                     │
│                     │ [Preview: Dark Theme] ──────────────────────┐       │
│                     │ │                                           │       │
│                     │ │  Example of dark theme                    │       │
│                     │ │  • Reduced eye strain                     │       │
│                     │ │  • Better for low-light                   │       │
│                     │ │                                           │       │
│                     │ └───────────────────────────────────────────┘       │
│                     │                                                     │
│                     │ Font                                                │
│                     │                                                     │
│                     │ Font family: [System Default ▼]                     │
│                     │ Font size:   [Medium ▼]                             │
│                     │                                                     │
│                     │ Zoom                                                │
│                     │                                                     │
│                     │ Page zoom:    [──●───────] 100%                     │
│                     │ Minimum font: [──●───────] 12px                     │
│                     │                                                     │
│                     │ UI Density                                          │
│                     │                                                     │
│                     │ ⚪ Compact                                           │
│                     │ ⚫ Normal                                            │
│                     │ ⚪ Comfortable                                       │
│                     │                                                     │
│                     │ Activity Bar                                        │
│                     │                                                     │
│                     │ ☑ Show activity bar                                 │
│                     │ ☑ Show icon labels                                  │
│                     │                                                     │
└─────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 9. Context Menus

### 9.1 Page Context Menu (Right-click on page)

```
┌──────────────────────────────────┐
│ Back                        Alt+← │
│ Forward                     Alt+→ │
│ Reload                      Ctrl+R│
│ ──────────────────────────────── │
│ Save As...             Ctrl+S     │
│ Print...               Ctrl+P     │
│ ──────────────────────────────── │
│ View Page Source       Ctrl+U     │
│ Inspect Element        Ctrl+Shift+I│
│ ──────────────────────────────── │
│ Extension Actions          ▶      │──┬───────────────────────────┐
│ ──────────────────────────────── │  │ Screenshot Page           │
│ Take Screenshot                   │  │ Save to PDF               │
│ Generate QR Code                  │  │ Check Links               │
│ ──────────────────────────────── │  │ Extract Images            │
│ Python Console             ▶      │  └───────────────────────────┘
│ Dev Tools                  ▶      │
└──────────────────────────────────┘
```

### 9.2 Link Context Menu (Right-click on link)

```
┌──────────────────────────────────┐
│ Open Link                         │
│ Open Link in New Tab        Ctrl+│
│ Open Link in New Window           │
│ ──────────────────────────────── │
│ Save Link As...                   │
│ Copy Link Address                 │
│ ──────────────────────────────── │
│ Extension Actions          ▶      │
│ ──────────────────────────────── │
│ Inspect Element                   │
└──────────────────────────────────┘
```

### 9.3 Image Context Menu

```
┌──────────────────────────────────┐
│ Open Image in New Tab             │
│ Save Image As...                  │
│ Copy Image                        │
│ Copy Image Address                │
│ ──────────────────────────────── │
│ Search Image with Google          │
│ ──────────────────────────────── │
│ Extension Actions          ▶      │──┬───────────────────────────┐
│ ──────────────────────────────── │  │ Download All Images       │
│ Inspect Element                   │  │ Reverse Image Search      │
└──────────────────────────────────┘  │ OCR Extract Text          │
                                       └───────────────────────────┘
```

---

## 10. Theme Variations

### 10.1 Dark Theme (Default)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ #2D2D30 ViloWeb - Example Domain                            [_][□][X]      │
├───┬─────────────────────────────────────────────────────────────────────────┤
│   │ #1E1E1E                                                                 │
│ ⌂ │  ◄  ►  ⟲  🏠   https://example.com                      🔖  ⋯  👤     │
│   │                                                                         │
│   │  ┌──────────────────────────────────────────────────────────────────┐  │
│   │  │ #252526 Tab 1                                          [+]        │  │
│   │  ├──────────────────────────────────────────────────────────────────┤  │
│   │  │ #1E1E1E                                                          │  │
│   │  │ #CCCCCC text                                                     │  │
│   │  │                                                                  │  │
│   │  └──────────────────────────────────────────────────────────────────┘  │
├───┴─────────────────────────────────────────────────────────────────────────┤
│ #007ACC Accent  | #252526 Status Bar                                       │
└─────────────────────────────────────────────────────────────────────────────┘

Colors:
- Background: #1E1E1E
- Secondary: #252526
- Text: #CCCCCC
- Accent: #007ACC (blue)
- Border: #3E3E42
```

### 10.2 Light Theme

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ #E8E8E8 ViloWeb - Example Domain                            [_][□][X]      │
├───┬─────────────────────────────────────────────────────────────────────────┤
│   │ #F3F3F3                                                                 │
│ ⌂ │  ◄  ►  ⟲  🏠   https://example.com                      🔖  ⋯  👤     │
│   │                                                                         │
│   │  ┌──────────────────────────────────────────────────────────────────┐  │
│   │  │ #FFFFFF Tab 1                                          [+]        │  │
│   │  ├──────────────────────────────────────────────────────────────────┤  │
│   │  │ #FFFFFF                                                          │  │
│   │  │ #333333 text                                                     │  │
│   │  │                                                                  │  │
│   │  └──────────────────────────────────────────────────────────────────┘  │
├───┴─────────────────────────────────────────────────────────────────────────┤
│ #0066CC Accent  | #FFFFFF Status Bar                                       │
└─────────────────────────────────────────────────────────────────────────────┘

Colors:
- Background: #F3F3F3
- Secondary: #FFFFFF
- Text: #333333
- Accent: #0066CC (blue)
- Border: #CCCCCC
```

---

## UI Design Philosophy

### Educational Focus
- **Clear Visual Hierarchy**: Important learning elements prominently displayed
- **Tooltips Everywhere**: Hover any UI element for educational explanations
- **Contextual Help**: "?" icons link to relevant tutorials
- **Progressive Disclosure**: Advanced features hidden until user is ready

### Developer Experience
- **Fast Access to Tools**: Console and Dev Tools always one click away
- **Code-First Design**: Code examples in every tutorial and help dialog
- **Copy-Paste Friendly**: All code samples have copy buttons
- **Keyboard Shortcuts**: Every action has a keyboard shortcut

### VFWidgets Showcase
- **Chrome-Quality Tabs**: ChromeTabbedWindow provides smooth tab experience
- **VS Code-Style Layout**: ViloCodeWindow demonstrates professional UI patterns
- **Consistent Theming**: vfwidgets-theme ensures coherent appearance
- **Real-World Integration**: Not a toy - production-quality components

### Accessibility
- **Keyboard Navigation**: Full app usable without mouse
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **High Contrast Mode**: Optional high-contrast theme
- **Zoom Support**: UI scales cleanly at all zoom levels

---

## Next Steps

1. **Review SPECIFICATION.md** for complete feature details
2. **Review ARCHITECTURE.md** for technical implementation
3. **Begin Phase 1 Implementation**:
   - Main window with ViloCodeWindow
   - Basic browser tab with navigation
   - Python console panel
   - First tutorial
4. **Iterate on UI based on user feedback**

---

**Questions?** See README.md for overview or SPECIFICATION.md for detailed requirements.
