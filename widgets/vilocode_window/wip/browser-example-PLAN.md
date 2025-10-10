# Browser Application Plan (Based on IDE Example)

**Status**: 📝 Planning
**Target**: `examples/06_browser.py`
**Based On**: `examples/05_advanced_ide.py`

---

## Overview

Create a full-featured web browser application using ViloCodeWindow that mirrors the structure of the advanced IDE example but adapted for web browsing. This will be example #6, demonstrating the most advanced real-world application of ViloCodeWindow.

---

## Architecture

### Main Components

**1. Tab Widget (Main Pane)**
- Use `ChromeTabbedWindow` if available (preferred), fallback to `QTabWidget`
- Multiple browser tabs (like Chrome/Firefox)
- Each tab contains a `QWebEngineView` for web content
- New tab button (+) functionality
- Close tab functionality (X)
- Tab reordering support

**2. Activity Bar (Left Side)**
- 🏠 **Home** - Show homepage/favorites
- 📚 **Bookmarks** - Bookmarks panel
- 📜 **History** - Browsing history panel
- ⚙️ **Settings** - Browser settings

**3. Sidebar Panels**
- **Home Panel**: Quick access links, favorites grid
- **Bookmarks Panel**: Tree view of bookmark folders
- **History Panel**: List of recent browsing history with search
- **Settings Panel**: Browser preferences (homepage, default search engine)

**4. Auxiliary Bar (Optional)**
- Developer tools preview
- Page outline/table of contents
- Reading mode sidebar

**5. Navigation Bar (Custom Widget in Main Pane)**
- Back/Forward/Refresh buttons
- URL address bar with autocomplete
- Bookmark current page button (⭐)
- Page loading progress indicator
- HTTPS indicator (🔒)

---

## Implementation Details

### File Structure

```
examples/06_browser.py
├── NavigationBar class      - URL bar + back/forward/refresh controls
├── BrowserTab class          - QWebEngineView wrapper with navigation
├── BookmarkManager class     - JSON persistence for bookmarks
├── HistoryManager class      - SQLite persistence for history
├── BookmarksPanel class      - Tree view of bookmarks with folders
├── HistoryPanel class        - List view of browsing history
├── HomePanel class           - Quick links grid + recent/frequent sites
├── SettingsPanel class       - Browser configuration options
└── main() function           - Application initialization
```

### Key Classes

#### 1. NavigationBar Widget
```python
class NavigationBar(QWidget):
    """Navigation controls and URL bar."""

    # Widgets:
    - Back button (←) - QToolButton
    - Forward button (→) - QToolButton
    - Refresh button (⟳) - QToolButton
    - Home button (🏠) - QToolButton
    - URL bar (QLineEdit) - with autocomplete
    - Bookmark button (⭐) - QToolButton
    - Progress bar (QProgressBar) - shows loading
    - HTTPS indicator (🔒) - QLabel

    # Signals:
    - navigate_to_url(str) - when user enters URL
    - bookmark_requested() - when bookmark button clicked
    - home_requested() - when home button clicked
```

#### 2. BrowserTab Widget
```python
class BrowserTab(QWidget):
    """Single browser tab with web view and navigation."""

    # Widgets:
    - NavigationBar (top)
    - QWebEngineView (main content)

    # Properties:
    - current_url: str
    - current_title: str
    - favicon: QIcon
    - loading_progress: int (0-100)

    # Methods:
    - navigate_to(url: str)
    - go_back()
    - go_forward()
    - refresh()
    - stop_loading()

    # Signals:
    - title_changed(str)
    - url_changed(str)
    - favicon_changed(QIcon)
    - loading_progress_changed(int)
    - load_finished(bool)
```

#### 3. BookmarkManager
```python
class BookmarkManager:
    """Manage bookmarks with JSON persistence."""

    # Storage: ~/.vilocode_browser/bookmarks.json

    # Data Structure:
    {
        "bookmarks": [
            {
                "title": "GitHub",
                "url": "https://github.com",
                "folder": "Development",
                "added": "2025-10-10T12:00:00",
                "tags": ["code", "git"]
            }
        ],
        "folders": ["Development", "News", "Social"]
    }

    # Methods:
    - load_bookmarks() -> List[Dict]
    - save_bookmarks()
    - add_bookmark(url, title, folder)
    - remove_bookmark(url)
    - get_bookmarks_by_folder(folder) -> List[Dict]
    - import_bookmarks(file_path)
    - export_bookmarks(file_path)
```

#### 4. HistoryManager
```python
class HistoryManager:
    """Manage browsing history with SQLite persistence."""

    # Storage: ~/.vilocode_browser/history.db

    # Schema:
    CREATE TABLE history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        title TEXT,
        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        visit_count INTEGER DEFAULT 1
    );

    # Methods:
    - add_visit(url, title)
    - get_history(limit=100) -> List[Dict]
    - search_history(query) -> List[Dict]
    - clear_history(time_range: str)  # "hour", "today", "all"
    - get_most_visited(limit=10) -> List[Dict]
    - cleanup_old_entries(days=30)
```

#### 5. BookmarksPanel
```python
class BookmarksPanel(QWidget):
    """Sidebar panel showing bookmarks in tree view."""

    # Widgets:
    - QTreeWidget (bookmarks organized by folder)
    - Search bar (QLineEdit)
    - Add folder button
    - Import/Export buttons

    # Context Menu:
    - Open in current tab
    - Open in new tab
    - Edit bookmark
    - Delete bookmark
    - Move to folder

    # Signals:
    - bookmark_clicked(url: str, new_tab: bool)
```

#### 6. HistoryPanel
```python
class HistoryPanel(QWidget):
    """Sidebar panel showing browsing history."""

    # Widgets:
    - Search bar (QLineEdit)
    - QListWidget (history entries)
    - Clear history button
    - Time range filter (dropdown)

    # Context Menu:
    - Open in current tab
    - Open in new tab
    - Delete from history
    - Copy URL

    # Signals:
    - history_clicked(url: str, new_tab: bool)
```

#### 7. HomePanel
```python
class HomePanel(QWidget):
    """Homepage with quick access links."""

    # Sections:
    - Quick Links grid (customizable tiles)
    - Recently Visited (last 10 sites)
    - Most Visited (top 10 sites)

    # Widgets:
    - QScrollArea with grid layout
    - Tile widgets (clickable with icon + title)

    # Signals:
    - site_clicked(url: str)
```

#### 8. SettingsPanel
```python
class SettingsPanel(QWidget):
    """Browser settings and preferences."""

    # Settings:
    - Homepage URL (QLineEdit)
    - Default search engine (QComboBox: Google, DuckDuckGo, Bing)
    - Download directory (QLineEdit + browse button)
    - Clear cache on exit (QCheckBox)
    - Enable JavaScript (QCheckBox)
    - Block pop-ups (QCheckBox)
    - User agent (QComboBox: Default, Mobile, Custom)
    - Theme preference (QComboBox: Auto, Light, Dark)

    # Storage: ~/.vilocode_browser/settings.json
```

---

## Feature Set

### Phase 1: Browsing Basics & Bookmarks (MVP - First Working Version)
**Goal**: Get a functional browser with basic navigation and bookmarking

- ✅ Single tab with QWebEngineView
- ✅ Basic navigation (back/forward/refresh/stop)
- ✅ URL address bar (enter URL to navigate)
- ✅ Loading progress indicator
- ✅ Page title in window title
- ✅ Bookmark current page (⭐ button)
- ✅ Bookmarks panel with list view
- ✅ Add/remove bookmarks
- ✅ Open bookmark in current tab
- ✅ Bookmark persistence (JSON)
- ✅ Home button (go to default homepage)
- ✅ Activity bar + sidebar integration
- ✅ Basic theme styling

### Phase 2: Multiple Tabs & Tab Management
**Goal**: Support multiple tabs like a real browser

- ✅ Multiple tabs (ChromeTabbedWindow or QTabWidget)
- ✅ New tab (Ctrl+T)
- ✅ Close tab (Ctrl+W, X button)
- ✅ Switch between tabs (Ctrl+Tab, Ctrl+Shift+Tab)
- ✅ Tab title from page title
- ✅ Tab favicon from page icon
- ✅ Welcome tab on launch
- ✅ Duplicate tab
- ✅ Tab context menu (right-click)
- ✅ Pin tabs (compact, stay left)
- ✅ Mute tabs (audio indicator 🔊)
- ✅ Reopen closed tab (Ctrl+Shift+T with stack)
- ✅ Close tabs to the right

### Phase 3: History & Search
**Goal**: Track history and enable searching

- ✅ History tracking (SQLite persistence)
- ✅ History panel with list view
- ✅ Search history
- ✅ Clear history (time ranges)
- ✅ Open history item in current/new tab
- ✅ Most visited sites
- ✅ Recently visited sites
- ✅ Search from URL bar (detect query vs URL)
- ✅ Search engine selection (Google/DuckDuckGo/Bing)
- ✅ URL bar autocomplete from history

### Phase 4: Advanced Navigation & Page Actions
**Goal**: Full page interaction capabilities

- ✅ Zoom controls (Ctrl+Plus/Minus/0, 25%-500%)
- ✅ Zoom indicator in status bar (e.g., "100%")
- ✅ Full screen mode (F11)
- ✅ Print page (Ctrl+P)
- ✅ Save page (Ctrl+S)
- ✅ View page source (Ctrl+U)
- ✅ Find in page (Ctrl+F with highlight)
- ✅ HTTPS indicator in URL bar (🔒)
- ✅ Site identity dialog (click lock icon for cert info)

### Phase 5: Context Menus & Link Handling
**Goal**: Rich interaction with page content

- ✅ Link context menu (open in new tab, copy link, save link)
- ✅ Image context menu (save image, copy image, open in new tab)
- ✅ Text context menu (copy, select all, search selection)
- ✅ Page context menu (back, forward, reload, view source, inspect)
- ✅ Ctrl+Click link → open in new tab
- ✅ Middle-click link → open in new tab
- ✅ Drag link to tab bar → new tab

### Phase 6: Downloads
**Goal**: Download files and manage downloads

- ✅ Download manager (auxiliary bar or panel)
- ✅ Download progress indicator
- ✅ Pause/Resume downloads
- ✅ Open downloaded file
- ✅ Open download folder
- ✅ Download history persistence (SQLite)
- ✅ Downloads button in toolbar (📥 with badge)
- ✅ Download notifications

### Phase 7: Bookmarks Enhancement
**Goal**: Advanced bookmark management

- ✅ Bookmark folders (tree view)
- ✅ Bookmark organization (drag and drop)
- ✅ Edit bookmark (title, URL, folder, tags)
- ✅ Bookmark search
- ✅ Bookmark import (HTML format)
- ✅ Bookmark export (HTML format)
- ✅ Bookmark tags
- ✅ Bookmark favicon storage

### Phase 8: Security & Privacy
**Goal**: User control over security and privacy

- ✅ Cookie manager (view/delete per site)
- ✅ Site permissions (camera, mic, location, notifications)
- ✅ Clear browsing data dialog (cache, cookies, history, downloads)
- ✅ HTTPS-only mode option
- ✅ Do Not Track header
- ✅ Incognito/Private mode (separate profile)
- ✅ Block pop-ups option

### Phase 9: Session Management
**Goal**: Remember state across sessions

- ✅ Save current session (all tabs)
- ✅ Restore last session on startup
- ✅ Continue where you left off option
- ✅ Recently closed tabs menu (Ctrl+Shift+T list)
- ✅ Manual session save/restore
- ✅ Remember window size/position
- ✅ Crash recovery (restore tabs after crash)

### Phase 10: Home & Settings
**Goal**: Customizable homepage and preferences

- ✅ Homepage with quick links grid
- ✅ Recently visited section (last 10)
- ✅ Most visited section (top 10)
- ✅ Customizable quick links (add/edit/remove)
- ✅ Settings panel with all preferences
- ✅ Homepage URL setting
- ✅ Default search engine setting
- ✅ Download directory setting
- ✅ Theme preference (auto/light/dark)
- ✅ Restore defaults button

### Phase 11: Developer Tools
**Goal**: Web development support

- ✅ Built-in developer console (F12)
- ✅ Web inspector (right-click → Inspect)
- ✅ JavaScript console
- ✅ Network inspector
- ✅ Elements inspector
- ✅ Console in auxiliary bar

### Phase 12: Polish & Advanced Features (Nice-to-Have)
**Goal**: Production-quality polish

- 🎨 Reading mode (clean article view)
- 🎨 Auto-fill forms (basic)
- 🎨 Password manager (simple vault)
- 🎨 Multiple profiles (separate user profiles)
- 🎨 Tab groups (color-coded organization)
- 🎨 QR code generator (for current URL)
- 🎨 Screenshot tool (full page or selection)
- 🎨 Picture-in-Picture (video popout)
- 🎨 Translate page (if API available)
- 🎨 Dark mode for all sites (force dark theme)
- 🎨 Ad blocker (basic domain blocking)
- 🎨 Extensions API (for future plugins)

---

## Implementation Steps

### Phase 1: Basic Structure ✅
1. Create `examples/06_browser.py` with file header and imports
2. Set up main window with ViloCodeWindow
3. Create basic tab widget (Chrome tabs if available)
4. Add placeholder panels for all sidebar sections
5. Set up menu bar with File/Edit/View/Bookmarks/History/Help
6. Add status bar

### Phase 2: Web Engine Integration 🚧
1. Create `BrowserTab` class with `QWebEngineView`
2. Create `NavigationBar` widget with URL bar and buttons
3. Connect web engine signals (loadProgress, urlChanged, titleChanged, iconChanged)
4. Implement new tab functionality (opens blank page)
5. Implement close tab functionality
6. Add keyboard shortcuts (Ctrl+T, Ctrl+W, Ctrl+L, Ctrl+R)
7. Show loading progress in navigation bar
8. Update tab title from page title
9. Update tab favicon from page icon

### Phase 3: Navigation & Controls ⏳
1. Implement back button (QWebEngineView.back())
2. Implement forward button (QWebEngineView.forward())
3. Implement refresh button (QWebEngineView.reload())
4. Implement home button (navigate to homepage URL)
5. Implement URL bar navigation (press Enter to load)
6. Add URL autocomplete from history
7. Add HTTPS indicator (🔒 for https://)
8. Show page load progress bar
9. Handle URL validation and correction
10. Add stop loading button (while loading)

### Phase 4: Bookmarks System ⏳
1. Create `BookmarkManager` class with JSON persistence
2. Implement save/load from `~/.vilocode_browser/bookmarks.json`
3. Create `BookmarksPanel` with QTreeWidget
4. Implement add bookmark button (⭐ in navigation bar)
5. Implement bookmark dialog (title, URL, folder)
6. Implement bookmark folders in tree view
7. Add context menu (open, edit, delete, new folder)
8. Implement drag-and-drop to organize bookmarks
9. Add bookmark search in panel
10. Implement import/export bookmarks (HTML format)

### Phase 5: History System ⏳
1. Create `HistoryManager` class with SQLite
2. Set up database at `~/.vilocode_browser/history.db`
3. Create history table schema
4. Track visited URLs automatically on page load
5. Create `HistoryPanel` with QListWidget
6. Implement search functionality in panel
7. Add time range filter (Last hour, Today, Last 7 days, All time)
8. Add clear history button with confirmation
9. Add context menu (open, delete, copy URL)
10. Implement "most visited" query for homepage

### Phase 6: Home & Settings ⏳
1. Create `HomePanel` with quick links grid
2. Add default quick links (Google, YouTube, GitHub, etc.)
3. Implement "recently visited" section (from history)
4. Implement "most visited" section (from history)
5. Make quick links customizable (add/edit/remove)
6. Create `SettingsPanel` with preferences
7. Add homepage URL setting (text field)
8. Add default search engine setting (dropdown)
9. Add download directory setting (file picker)
10. Implement settings persistence (JSON)
11. Add "Restore defaults" button

### Phase 7: Theme Integration 🎨
1. Get theme colors using `get_theme_manager()`
2. Style navigation bar with theme colors
3. Style sidebar panels with theme colors
4. Style URL bar with theme colors (focus state)
5. Style buttons with theme hover colors
6. Style QWebEngineView background
7. Add theme switching in settings panel
8. Test with "Dark Default" and "Light Default" themes

### Phase 8: Keyboard Shortcuts ⌨️
1. Implement Ctrl+T (new tab)
2. Implement Ctrl+W (close current tab)
3. Implement Ctrl+L (focus URL bar)
4. Implement Ctrl+D (bookmark current page)
5. Implement Ctrl+H (toggle history panel)
6. Implement Ctrl+Shift+B (toggle bookmarks panel)
7. Implement Ctrl+Tab (next tab)
8. Implement Ctrl+Shift+Tab (previous tab)
9. Implement Ctrl+R / F5 (refresh page)
10. Implement Alt+Left (back)
11. Implement Alt+Right (forward)
12. Implement Ctrl+F (find in page)
13. Document all shortcuts in menu bar

### Phase 9: Polish & Documentation 📝
1. Add comprehensive docstrings to all classes
2. Add example header with features list
3. Add "What you'll learn" section
4. Add usage instructions
5. Test all keyboard shortcuts
6. Test on Windows/macOS/Linux
7. Add error handling (network errors, invalid URLs)
8. Add loading indicators
9. Test tab closing edge cases (close last tab)
10. Add status bar messages (page loaded, bookmark added, etc.)

### Phase 10: Advanced Features (Optional) ✨
1. Add download manager (show in status bar)
2. Implement find in page (Ctrl+F dialog)
3. Add session restore (save open tabs on exit)
4. Implement zoom controls (Ctrl+Plus/Minus/0)
5. Add print preview (Ctrl+P)
6. Implement context menu in web view (back, forward, reload, save image)
7. Add developer tools toggle (F12)
8. Implement private/incognito mode

---

## Keyboard Shortcuts

| Shortcut | Action | Priority |
|----------|--------|----------|
| `Ctrl+T` | New tab | MVP |
| `Ctrl+W` | Close current tab | MVP |
| `Ctrl+L` | Focus address bar | MVP |
| `Ctrl+D` | Bookmark current page | MVP |
| `Ctrl+H` | Show history | MVP |
| `Ctrl+Shift+B` | Toggle bookmarks bar | Enhanced |
| `Ctrl+Tab` | Next tab | Enhanced |
| `Ctrl+Shift+Tab` | Previous tab | Enhanced |
| `Ctrl+R` / `F5` | Refresh page | MVP |
| `Alt+Left` | Back | MVP |
| `Alt+Right` | Forward | MVP |
| `Ctrl+F` | Find in page | Enhanced |
| `Ctrl+Plus` | Zoom in | Nice-to-have |
| `Ctrl+Minus` | Zoom out | Nice-to-have |
| `Ctrl+0` | Reset zoom | Nice-to-have |
| `Ctrl+P` | Print | Nice-to-have |
| `F12` | Toggle developer tools | Nice-to-have |

---

## Storage & Persistence

### Bookmarks
**File**: `~/.vilocode_browser/bookmarks.json`

```json
{
  "version": 1,
  "bookmarks": [
    {
      "title": "GitHub",
      "url": "https://github.com",
      "folder": "Development",
      "added": "2025-10-10T12:00:00Z",
      "tags": ["code", "git"],
      "favicon": "data:image/png;base64,..."
    }
  ],
  "folders": [
    {
      "name": "Development",
      "parent": null
    },
    {
      "name": "Python",
      "parent": "Development"
    }
  ]
}
```

### History
**File**: `~/.vilocode_browser/history.db` (SQLite)

```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visit_count INTEGER DEFAULT 1,
    UNIQUE(url, date(visit_time))
);

CREATE INDEX idx_visit_time ON history(visit_time DESC);
CREATE INDEX idx_url ON history(url);
```

### Settings
**File**: `~/.vilocode_browser/settings.json`

```json
{
  "version": 1,
  "homepage": "vilobrowser://home",
  "search_engine": "google",
  "download_directory": "~/Downloads",
  "clear_cache_on_exit": false,
  "enable_javascript": true,
  "block_popups": true,
  "user_agent": "default",
  "theme": "auto",
  "restore_session": true,
  "last_tabs": [
    "https://github.com",
    "https://python.org"
  ]
}
```

---

## Code Structure Template

```python
#!/usr/bin/env python3
"""Browser Example - Full-Featured Web Browser

This example demonstrates a complete web browser built with ViloCodeWindow:
- Multiple tabs with QWebEngineView
- Navigation controls (back/forward/refresh/home)
- URL address bar with autocomplete
- Bookmark manager with folders
- Browsing history with search
- Theme-based styling
- Full keyboard shortcut support

What you'll learn:
- QWebEngineView integration for web rendering
- Tab management for multiple web views
- Persistent storage (bookmarks JSON, history SQLite)
- Navigation bar with custom controls
- Activity bar → Sidebar patterns
- Production browser architecture
- Theme system integration for custom widgets

Features:
✓ Multiple tabs (Chrome-style if available)
✓ Back/Forward/Refresh/Home navigation
✓ URL bar with autocomplete from history
✓ Bookmark management with folders
✓ Browsing history with search
✓ Homepage with quick links
✓ Settings panel with preferences
✓ Theme integration (Dark/Light modes)
✓ Full keyboard shortcuts (Ctrl+T, Ctrl+W, Ctrl+L, etc.)
✓ HTTPS indicator in URL bar
✓ Page loading progress
✓ Favicon display in tabs

Run this example:
    python examples/06_browser.py

Requirements:
    pip install PySide6 PySide6-WebEngine
"""

import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import Qt, QUrl, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_vilocode_window import ViloCodeWindow

# Check for optional widgets
try:
    from chrome_tabbed_window import ChromeTabbedWindow
    CHROME_TABS_AVAILABLE = True
except ImportError:
    CHROME_TABS_AVAILABLE = False


# ============================================================================
# Helper Functions
# ============================================================================

def create_icon_from_text(text: str, size: int = 24) -> QIcon:
    """Create an icon from Unicode text/emoji."""
    # ... (same as IDE example)


def get_browser_data_dir() -> Path:
    """Get browser data directory, create if not exists."""
    data_dir = Path.home() / ".vilocode_browser"
    data_dir.mkdir(exist_ok=True)
    return data_dir


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Bookmark:
    """Bookmark data model."""
    title: str
    url: str
    folder: str = ""
    added: str = ""
    tags: List[str] = None
    favicon: Optional[str] = None


@dataclass
class HistoryEntry:
    """History entry data model."""
    id: int
    url: str
    title: str
    visit_time: str
    visit_count: int


# ============================================================================
# Storage Managers
# ============================================================================

class BookmarkManager:
    """Manage bookmarks with JSON persistence."""
    # ... implementation


class HistoryManager:
    """Manage browsing history with SQLite persistence."""
    # ... implementation


# ============================================================================
# Browser Components
# ============================================================================

class NavigationBar(QWidget):
    """Navigation controls and URL bar."""
    # ... implementation


class BrowserTab(QWidget):
    """Single browser tab with web view and navigation."""
    # ... implementation


# ============================================================================
# Sidebar Panels
# ============================================================================

class BookmarksPanel(QWidget):
    """Bookmarks panel with tree view."""
    # ... implementation


class HistoryPanel(QWidget):
    """History panel with search."""
    # ... implementation


class HomePanel(QWidget):
    """Homepage with quick links."""
    # ... implementation


class SettingsPanel(QWidget):
    """Browser settings panel."""
    # ... implementation


# ============================================================================
# Main Application
# ============================================================================

def main() -> None:
    """Create browser application."""
    app = QApplication(sys.argv)

    # Apply theme
    try:
        from vfwidgets_theme import get_theme_manager
        theme_manager = get_theme_manager()
        theme_manager.apply_theme("Dark Default")
    except ImportError:
        pass

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("ViloBrowser - Web Browser")
    window.resize(1400, 900)

    # ... rest of setup

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## Testing Plan

### Manual Testing Checklist

1. **Launch & UI**
   - ✅ Browser launches with welcome page
   - ✅ All UI elements visible (navigation bar, sidebar, tabs)
   - ✅ Theme colors applied correctly

2. **Navigation**
   - ✅ Navigate to https://www.google.com
   - ✅ Back button works
   - ✅ Forward button works
   - ✅ Refresh button works
   - ✅ Home button returns to homepage
   - ✅ URL bar accepts input and navigates
   - ✅ HTTPS indicator shows for secure sites

3. **Tabs**
   - ✅ Open new tab (Ctrl+T)
   - ✅ Switch between tabs
   - ✅ Close tab (X button and Ctrl+W)
   - ✅ Tab title updates with page title
   - ✅ Tab favicon updates with page icon
   - ✅ Loading progress shows in tab

4. **Bookmarks**
   - ✅ Bookmark current page (⭐ button)
   - ✅ Bookmark appears in bookmarks panel
   - ✅ Create bookmark folder
   - ✅ Move bookmark to folder
   - ✅ Edit bookmark (title, URL)
   - ✅ Delete bookmark
   - ✅ Open bookmark in current tab
   - ✅ Open bookmark in new tab
   - ✅ Bookmarks persist after restart

5. **History**
   - ✅ Visited URLs appear in history
   - ✅ Search history works
   - ✅ Clear history (last hour)
   - ✅ Clear history (all time)
   - ✅ Most visited sites shown on homepage
   - ✅ History persists after restart

6. **Settings**
   - ✅ Change homepage URL
   - ✅ Change search engine
   - ✅ Settings persist after restart

7. **Keyboard Shortcuts**
   - ✅ Ctrl+T (new tab)
   - ✅ Ctrl+W (close tab)
   - ✅ Ctrl+L (focus URL bar)
   - ✅ Ctrl+D (bookmark page)
   - ✅ Ctrl+H (show history)
   - ✅ Ctrl+R (refresh)
   - ✅ Alt+Left (back)
   - ✅ Alt+Right (forward)

8. **Edge Cases**
   - ✅ Close last tab (should open new blank tab)
   - ✅ Navigate to invalid URL (show error)
   - ✅ Network error handling
   - ✅ Very long URL in address bar
   - ✅ Special URLs (about:blank, file://)

---

## Estimated Effort

- **Lines of Code**: ~800-1200 lines
- **Development Time**: 6-8 hours (with testing)
- **Complexity**: Medium-High (similar to IDE example, plus web engine)
- **Dependencies**: PySide6, PySide6-WebEngine

---

## Benefits of This Example

1. **Real-World Application** - Fully functional web browser
2. **QWebEngineView Showcase** - Modern web rendering in Qt
3. **Persistent Storage** - JSON + SQLite patterns
4. **Advanced Tab Management** - Multiple web views in tabs
5. **Complex UI Integration** - Navigation bar, panels, overlays
6. **Production Patterns** - Manager classes, separation of concerns
7. **Theme System Usage** - Extensive styling with theme colors
8. **ViloCodeWindow API** - Uses all major APIs (activity bar, sidebar, main pane, auxiliary bar)
9. **Keyboard Shortcuts** - Full shortcut support with VS Code style
10. **Cross-Platform** - Works on Windows, macOS, Linux

This example will demonstrate ViloCodeWindow's capability to build professional, production-ready applications!

---

## Next Steps

1. ✅ Create this WIP document
2. ⏳ Get approval on architecture and features
3. ⏳ Implement Phase 1 (basic structure)
4. ⏳ Implement Phase 2 (web engine)
5. ⏳ Continue through all phases
6. ⏳ Test thoroughly
7. ⏳ Document and polish
8. ✅ Ship example #6!
