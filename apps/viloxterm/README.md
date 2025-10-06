# ViloxTerm

A modern terminal emulator application showcasing the integration of multiple VFWidgets components. ViloxTerm combines Chrome-style tabbed windows, dynamic split panes, and xterm.js-based terminals with a powerful theme system for a fully customizable terminal experience.

## Architecture

ViloxTerm demonstrates a layered architecture combining four key VFWidgets components:

```
┌─────────────────────────────────────────────────────────────┐
│  ChromeTabbedWindow (Main Window)                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Tab 1                    Tab 2          Tab 3  [+]    │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ MultisplitWidget (Dynamic Split Panes)               │  │
│  │ ┌───────────────────┬───────────────────────────────┐ │  │
│  │ │ TerminalWidget    │ TerminalWidget                │ │  │
│  │ │ (xterm.js)        │ (xterm.js)                    │ │  │
│  │ │                   │                               │ │  │
│  │ │ $ vim main.py     │ $ python main.py              │ │  │
│  │ │                   ├───────────────────────────────┤ │  │
│  │ │                   │ TerminalWidget                │ │  │
│  │ │                   │ (xterm.js)                    │ │  │
│  │ │                   │                               │ │  │
│  │ │                   │ $ npm run build               │ │  │
│  │ └───────────────────┴───────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│  Theme System: Unified theming across all components       │
└─────────────────────────────────────────────────────────────┘
```

**Layer 1: ChromeTabbedWindow** - Chrome-style tabs with modern UI
**Layer 2: MultisplitWidget** - Dynamic runtime splitting of panes
**Layer 3: TerminalWidget** - Full-featured xterm.js terminals
**Layer 4: Theme System** - VSCode-compatible theme management

## Integrated Widgets

### 1. ChromeTabbedWindow (Main Window)

Provides the Chrome-style tabbed interface with modern window controls.

**Key Features:**
- Chrome-style tab rendering with compression
- Drag-and-drop tab reordering
- Native window controls integration
- Automatic theme system integration

**Reference Examples:**
- [`../../widgets/chrome-tabbed-window/examples/04_themed_chrome_tabs.py`](../../widgets/chrome-tabbed-window/examples/04_themed_chrome_tabs.py)
  Basic ChromeTabbedWindow with ThemedApplication integration

- [`../../widgets/chrome-tabbed-window/examples/05_themed_chrome_embedded.py`](../../widgets/chrome-tabbed-window/examples/05_themed_chrome_embedded.py)
  ChromeTabbedWindow embedded in ThemedMainWindow

**Documentation:**
- [`../../widgets/chrome-tabbed-window/README.md`](../../widgets/chrome-tabbed-window/README.md)
- [`../../widgets/chrome-tabbed-window/docs/theme-integration-GUIDE.md`](../../widgets/chrome-tabbed-window/docs/theme-integration-GUIDE.md)

### 2. MultisplitWidget (Tab Content)

Enables dynamic runtime splitting of terminal panes within each tab.

**ViloxTerm uses MultisplitWidget v0.2.0:**
- **Fixed Container Architecture** - Eliminates flashing during splits
- **Widget Lifecycle Hooks** - Automatic session cleanup via `widget_closing()`
- **Focus Tracking** - Visual indicators show active terminal pane
- **Widget Lookup APIs** - Direct access to terminal widgets

Each tab contains a `MultisplitWidget` that can be dynamically split into multiple terminal panes. Terminal sessions are managed by a shared `MultiSessionTerminalServer` for memory efficiency.

**Implementation:**
- Provider: `src/viloxterm/providers/terminal_provider.py`
- Integration: `src/viloxterm/app.py`

**Key Features:**
- Vim-inspired split commands (Ctrl+Shift+H/V)
- Dynamic horizontal/vertical splitting
- Keyboard-driven pane navigation
- Focus management with visual borders
- Automatic terminal session cleanup

**Reference Examples:**
- [`../../widgets/multisplit_widget/examples/01_basic_text_editor.py`](../../widgets/multisplit_widget/examples/01_basic_text_editor.py)
  Multi-document editor demonstrating runtime splitting and focus management

- [`../../widgets/multisplit_widget/examples/03_keyboard_driven_splitting.py`](../../widgets/multisplit_widget/examples/03_keyboard_driven_splitting.py)
  Advanced keyboard control with vim-like navigation

**Documentation:**
- [`../../widgets/multisplit_widget/docs/QUICKSTART.md`](../../widgets/multisplit_widget/docs/QUICKSTART.md) - Get started in 5 minutes
- [`../../widgets/multisplit_widget/docs/API.md`](../../widgets/multisplit_widget/docs/API.md) - Complete API reference
- [`../../widgets/multisplit_widget/docs/GUIDE.md`](../../widgets/multisplit_widget/docs/GUIDE.md) - Best practices & patterns

### 3. TerminalWidget (Pane Content)

Full-featured terminal emulator based on xterm.js with WebView integration.

**Key Features:**
- xterm.js-powered terminal emulation
- WebView + Qt theme system bridge
- Real PTY integration
- Modern terminal features (true color, unicode, etc.)
- Theme-aware color schemes

**Reference Examples:**
- [`../../widgets/terminal_widget/examples/themed_terminal.py`](../../widgets/terminal_widget/examples/themed_terminal.py)
  Terminal with 80/20 theming pattern (ThemedMainWindow + theme customization)

- [`../../widgets/terminal_widget/examples/advanced_features.py`](../../widgets/terminal_widget/examples/advanced_features.py)
  Advanced terminal capabilities and event handling

**Documentation:**
- [`../../widgets/terminal_widget/README.md`](../../widgets/terminal_widget/README.md)
- [`../../widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md`](../../widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md)
  Critical lessons for WebView + theme system integration

### 4. Theme System (Application Theming)

Provides VSCode-compatible theme management across all widgets.

**Key Features:**
- VSCode theme import/export
- Dynamic theme switching
- WebView theme bridging
- Token-based color system
- ThemedWidget base classes

**Reference Documentation:**
- [`../../widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md`](../../widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md)
  Official theming guide with 80/20 pattern

- [`../../widgets/theme_system/docs/quick-start-GUIDE.md`](../../widgets/theme_system/docs/quick-start-GUIDE.md)
  Quick start for theme system integration

- [`../../widgets/theme_system/docs/widget-development-GUIDE.md`](../../widgets/theme_system/docs/widget-development-GUIDE.md)
  Complete guide for developing themed widgets

## Development Status

**Current Version:** 1.0
**Status:** Production-ready
**Architecture Documentation:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Implementation Complete ✅

All planned phases have been successfully implemented:

**Phase 1: Core Window** ✅
- ChromeTabbedWindow as frameless top-level window
- ThemedApplication integration
- Basic tab creation and management
- Theme switching via menu icon + modal dialog

**Phase 2: Terminal Server** ✅
- MultiSessionTerminalServer implementation
- Memory-efficient shared server (63% reduction: 300MB → 110MB for 20 terminals)
- TerminalWidget integration
- Session lifecycle management

**Phase 3: MultisplitWidget Integration** ✅
- TerminalProvider implementation (WidgetProvider pattern)
- MultisplitWidget in each tab
- Provider integration (constructor pattern)
- Terminal displays in panes
- Pane focus management
- Split commands (Ctrl+Shift+H horizontal, Ctrl+Shift+V vertical)

**Phase 4: Theme Menu** ✅
- ThemeDialog implementation
- MenuButton for window controls
- Theme switching integration (dark, light, default, minimal)
- Menu button in window controls

**Phase 5: Keyboard Shortcuts** ✅
- KeybindingManager integration
- User-customizable shortcuts via JSON (`~/.config/viloxterm/keybindings.json`)
- Pane split commands (Ctrl+Shift+H/V)
- Pane close (Ctrl+W)
- Tab close (Ctrl+Shift+W)
- Menu integration (shortcuts appear in context menu)

### Current Features

✅ Chrome-style tabbed interface with frameless window
✅ Dynamic split panes (horizontal/vertical)
✅ Multiple terminals sharing one server (memory efficient)
✅ VSCode-compatible theme system (4 built-in themes)
✅ Terminal color & font customization (Ctrl+Shift+,)
✅ Terminal behavior preferences with presets (Ctrl+,)
✅ User-customizable keyboard shortcuts
✅ Auto-save settings (keybindings, terminal preferences, terminal themes persist)
✅ Clean shutdown (no zombie processes)

### Terminal Customization

**Terminal Colors & Fonts (Ctrl+Shift+,)**:
- 18 customizable colors (background, foreground, cursor, 16 ANSI colors)
- Font family and size selection
- Live preview of changes
- Save custom themes
- Set default theme for new terminals
- Themes stored in `~/.config/viloxterm/terminal_themes/`

**Terminal Preferences (Ctrl+,)**:
- Scrollback buffer (100-200k lines)
- Cursor style (block/underline/bar) and blinking
- Scroll sensitivity and fast scroll settings
- Tab width configuration
- Bell style (none/visual/sound)
- Right-click behavior
- 7 built-in presets: default, developer, power_user, minimal, accessible, log_viewer, remote
- Preferences stored in `~/.config/viloxterm/terminal_preferences.json`

### Known Limitations

- No session persistence (terminals don't survive app restart)
- No tab rename functionality
- No remote server support (local terminals only)

## Key Integration Patterns

### Pattern 1: ChromeTabbedWindow as Frameless Window

**Reference:** `chrome-tabbed-window/examples/04_themed_chrome_tabs.py`

```python
from vfwidgets_theme import ThemedApplication
from chrome_tabbed_window import ChromeTabbedWindow

# Create themed application
app = ThemedApplication(sys.argv)
app.set_theme("dark")

# Create ChromeTabbedWindow (no parent = frameless mode)
window = ChromeTabbedWindow()
window.setWindowTitle("ViloxTerm")
window.resize(1200, 800)

# Add tabs
window.addTab(content_widget, "Tab 1")

window.show()
sys.exit(app.exec())
```

**Key Points:**
- ChromeTabbedWindow with no parent = automatic frameless mode
- ThemedApplication provides theme support
- Window controls (min/max/close) added automatically

### Pattern 2: MultisplitWidget + WidgetProvider

**Reference:** `multisplit_widget/examples/01_basic_text_editor.py`

```python
from vfwidgets_multisplit import MultisplitWidget
from vfwidgets_multisplit.view.container import WidgetProvider
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

class TerminalProvider(WidgetProvider):
    def __init__(self, server: MultiSessionTerminalServer):
        self.server = server

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        # Create session
        session_id = self.server.create_session(command="bash")
        session_url = self.server.get_session_url(session_id)

        # Create terminal
        terminal = TerminalWidget(server_url=session_url)
        return terminal

# Use with MultisplitWidget
multisplit = MultisplitWidget()
multisplit.set_widget_provider(TerminalProvider(server))
```

**Key Points:**
- WidgetProvider creates widgets on demand
- Shared server for memory efficiency
- Each pane gets unique terminal session

### Pattern 3: MultiSessionTerminalServer Integration

**Reference:** `terminal_widget/docs/lessons-learned-GUIDE.md`

```python
from vfwidgets_terminal import TerminalWidget, MultiSessionTerminalServer

# Create shared server once
server = MultiSessionTerminalServer(port=0)  # Auto-allocate port
server.start()

# Create multiple terminals sharing the server
session_id = server.create_session(command="bash")
session_url = server.get_session_url(session_id)
terminal = TerminalWidget(server_url=session_url)

# Cleanup on exit
server.shutdown()
```

**Key Points:**
- Shared server for memory efficiency (63% reduction)
- Each terminal gets unique session
- Auto-allocated port with `port=0`

### Pattern 4: Theme System Integration (WebView Widgets)

**Reference:** `terminal_widget/docs/theme-integration-lessons-GUIDE.md`

```python
from vfwidgets_theme import ThemedWidget
from vfwidgets_terminal import TerminalWidget

class ThemedTerminal(ThemedWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.terminal = TerminalWidget()

    def on_theme_changed(self):
        # Bridge Qt theme to xterm.js colors
        theme = get_current_theme()
        # Apply theme to terminal...
```

See: [`terminal_widget/examples/themed_terminal.py`](../../widgets/terminal_widget/examples/themed_terminal.py)

## Documentation

### Primary Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system architecture and component integration
- **[docs/lessons-learned-GUIDE.md](docs/lessons-learned-GUIDE.md)** - Critical integration lessons and pitfalls
- **[docs/README.md](docs/README.md)** - Documentation index

### Historical Documentation

Planning and design documents have been archived in `docs/archive/` for reference.

## Critical Lessons Learned

This application demonstrates integration of five VFWidgets components. Key lessons from implementation:

### Multi-Widget Integration Lessons

**[Complete Lessons Learned Guide](docs/lessons-learned-GUIDE.md)** - Essential reading for multi-widget applications

**Top 6 Critical Lessons**:
1. **Provider MUST be in MultisplitWidget constructor** - `MultisplitWidget(provider=...)` not `set_widget_provider()`
2. **Don't override `_setup_ui()` in ChromeTabbedWindow** - Customize in `__init__` after `super().__init__()`
3. **Always check widget examples first** - They show the correct minimal pattern (saved us twice!)
4. **WidgetProvider creates widgets lazily** - Share resources via provider constructor
5. **Window controls only exist in frameless mode** - Check `_window_mode` before accessing
6. **ThemedApplication integration is automatic** - ChromeTabbedWindow is already a ThemedWidget

### Component-Specific Lessons

**WebView + Theme Integration** ([Terminal Widget Guide](../../widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md)):
- Theme property cache timing issues in `on_theme_changed()`
- Always test theme switches bidirectionally (dark→light AND light→dark)

**Theme Token Coverage**:
Built-in themes may not populate all token namespaces. Always provide theme-aware fallbacks:

```python
def _get_fallback_colors(self):
    theme_type = self._get_current_theme_type()
    if theme_type == 'light':
        return LIGHT_FALLBACKS
    return DARK_FALLBACKS
```

## Usage

*To be implemented*

```bash
# Install dependencies
pip install -e widgets/chrome-tabbed-window
pip install -e widgets/multisplit_widget
pip install -e widgets/terminal_widget
pip install -e widgets/theme_system

# Run ViloxTerm
cd apps/viloxterm
python -m viloxterm
```

## Building Binary Distribution

ViloxTerm can be packaged as a single executable binary for distribution using **pyside6-deploy**, Qt's official deployment tool.

### Quick Build

```bash
cd apps/viloxterm
./build.sh
```

This creates a standalone binary:
- **Linux**: `ViloXTerm` or `ViloXTerm.bin`
- **Windows**: `ViloXTerm.exe`
- **macOS**: `ViloXTerm.app`

### Manual Build

```bash
# Install in development mode
pip install -e .

# Build with pyside6-deploy
pyside6-deploy -c pysidedeploy.spec -f
```

### Build Configuration

The build is configured via `pysidedeploy.spec`:

```ini
[nuitka]
mode = onefile        # Single executable
jobs = 4             # Parallel compilation

[qt]
modules = Core,Gui,Widgets,WebEngineWidgets,WebEngineCore,WebChannel,Network
```

### Distribution

**Expected Binary Size:** 150-300 MB (includes Qt WebEngine)

**Distribution Options:**
- **Linux**: AppImage, tar.gz, or native package
- **Windows**: Installer (Inno Setup, NSIS) or portable ZIP
- **macOS**: DMG or notarized .app bundle

### Documentation

See [`docs/building-binary-GUIDE.md`](docs/building-binary-GUIDE.md) for:
- Platform-specific requirements
- Size optimization tips
- Troubleshooting
- CI/CD integration examples

## Configuration

ViloxTerm stores user preferences in `~/.config/viloxterm/`:

```
~/.config/viloxterm/
├── keybindings.json              # Keyboard shortcut customizations
├── terminal_preferences.json     # Terminal behavior settings
└── terminal_themes/              # Custom terminal color themes
    ├── my-theme.json
    └── viloxterm.json
```

### Keyboard Shortcuts

Customizable via the KeybindingManager. Default shortcuts:

**Tabs**:
- New Tab: `Ctrl+T`
- Close Tab: `Ctrl+Shift+W`
- Next Tab: `Ctrl+Tab`
- Previous Tab: `Ctrl+Shift+Tab`
- Jump to Tab 1-9: `Alt+1` through `Alt+9`

**Panes**:
- Split Vertical: `Ctrl+Shift+\`
- Split Horizontal: `Ctrl+Shift+-`
- Close Pane: `Ctrl+W`

**Appearance**:
- Terminal Preferences: `Ctrl+,`
- Terminal Colors & Fonts: `Ctrl+Shift+,`

Shortcuts are stored in `~/.config/viloxterm/keybindings.json` and persist across sessions.

### Terminal Preferences

Access via `Ctrl+,` or hamburger menu → "Terminal Preferences"

**Available Presets**:
- `default` - Standard settings (1k scrollback, block cursor)
- `developer` - Developer-optimized (10k scrollback, bar cursor, visual bell)
- `power_user` - Power user (50k scrollback, fast scrolling)
- `minimal` - Minimal resources (500 lines, basic features)
- `accessible` - Accessibility focused (visual bell, high visibility)
- `log_viewer` - Log viewing (100k scrollback, very fast scrolling)
- `remote` - Remote connections (balanced settings for SSH)

**Configurable Options**:
- Scrollback buffer size (0-200k lines)
- Cursor style and blinking
- Scroll sensitivity (normal and fast)
- Tab width
- Bell style
- Right-click behavior
- Line ending conversion

Settings are stored in `~/.config/viloxterm/terminal_preferences.json`

### Terminal Themes

Access via `Ctrl+Shift+,` or hamburger menu → "Terminal Colors & Fonts"

**Bundled Themes**:
- Default Dark
- Default Light

**Custom Themes**:
- Create custom color schemes
- Configure all 16 ANSI colors
- Set background, foreground, cursor colors
- Choose font family and size
- Save and load custom themes
- Set default theme for new terminals

Themes are stored as JSON files in `~/.config/viloxterm/terminal_themes/`

## License

See root LICENSE file.
