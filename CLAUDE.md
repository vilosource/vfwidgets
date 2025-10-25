# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

VFWidgets is a monorepo of independently installable PySide6/Qt widgets. Each widget is a separate package with its own tests, examples, and documentation. The repository also includes shared utilities and a full terminal application (ViloxTerm).

**Key principle**: Each widget can be installed and used independently via pip, but shares common development standards.

## Common Development Commands

### Installing a Widget for Development
```bash
# Install in editable mode with dev dependencies
pip install -e "./widgets/button_widget[dev]"
pip install -e "./widgets/theme_system[dev]"
pip install -e "./widgets/multisplit_widget[dev]"
```

### Running Tests
```bash
# Test specific widget
cd widgets/button_widget
pytest

# Test all widgets (from root)
pytest

# Test with coverage
cd widgets/theme_system
pytest --cov=vfwidgets_theme --cov-report=html

# Run single test file
pytest tests/test_specific.py -v
```

### Code Quality Checks
```bash
# Format code (line length: 100)
black --check src/

# Lint with Ruff
ruff check src/

# Type checking with MyPy
mypy src/
```

## Architecture Patterns

### Monorepo Structure
```
vfwidgets/
├── widgets/                    # Independent widget packages
│   ├── button_widget/         # Simple widget example
│   ├── theme_system/          # Theme management system
│   ├── multisplit_widget/     # Complex widget with MVC
│   ├── chrome-tabbed-window/  # QTabWidget-compatible with Chrome styling
│   ├── terminal_widget/       # Terminal emulator widget
│   ├── markdown_widget/       # Markdown editor/viewer with MVC
│   ├── vilocode_window/       # VS Code-style application window
│   ├── webview_widget/        # Web browser widget with QWebChannel
│   ├── keybinding_manager/    # Keyboard shortcut manager
│   └── workspace_widget/      # Multi-folder workspace explorer
├── shared/                     # Shared utilities
│   └── vfwidgets_common/      # Base classes, platform detection, desktop integration
├── apps/                       # Full applications
│   ├── viloxterm/             # Terminal emulator application
│   ├── reamde/                # Markdown viewer application
│   ├── theme-studio/          # Theme editor application
│   └── viloweb/               # Educational web browser
└── tools/                      # Development scripts
    └── create_widget.py       # Widget generator
```

### Widget Package Structure
Each widget follows this structure:
```
widgets/my_widget/
├── pyproject.toml          # Package config with dependencies
├── README.md              # Widget-specific docs
├── src/
│   └── vfwidgets_my_widget/
│       ├── __init__.py    # Public API exports
│       └── widget.py      # Implementation
├── tests/
│   └── test_widget.py     # pytest-qt tests
└── examples/
    └── basic_usage.py     # Runnable examples
```

### Major Widgets Architecture

**theme_system** - Clean architecture with dependency injection:
- `ThemedWidget` - Primary user API (mixin for theming capabilities)
- `ThemedApplication` - Application-level theme management
- Protocol-based design with clear separation of concerns
- Performance-first: <100ms theme switching, <1KB per widget
- Package: `vfwidgets_theme`

**multisplit_widget** - MVC architecture for complex split panes:
- Model: Pure data (nodes.py, model.py) - no Qt dependencies
- View: Qt widgets (container.py, visual_renderer.py)
- Controller: Commands with undo/redo (controller.py, commands.py)
- Bridge: Signal translation between layers (signal_bridge.py)
- Package: `vfwidgets_multisplit`

**chrome-tabbed-window** - 100% QTabWidget-compatible with Chrome styling:
- Drop-in replacement for QTabWidget with identical API
- Platform-specific optimizations (Windows/macOS/Linux)
- Built-in "+" button for new tabs
- Automatic theme integration when vfwidgets-theme installed
- Package: `chrome_tabbed_window`

**terminal_widget** - Full-featured terminal emulator:
- Backend abstraction for Unix/Windows PTY
- Multi-session support with embedded server
- Theme system integration
- Package: `vfwidgets_terminal`

**markdown_widget** - MVC markdown editor with live preview:
- Model: MarkdownDocument (pure data, no Qt)
- View: MarkdownViewer (QWebEngineView-based HTML renderer)
- Controller: Commands for document manipulation
- Features: Syntax highlighting (Prism.js), diagrams (Mermaid.js), math (KaTeX)
- Theme-aware rendering with automatic color injection
- Package: `vfwidgets_markdown`

**vilocode_window** - VS Code-style application window:
- Activity bar (vertical icon bar on left)
- Collapsible sidebar with multiple panels
- Auxiliary bar (optional right sidebar)
- Frameless window with custom title bar
- Automatic theme integration when vfwidgets-theme installed
- Package: `vfwidgets_vilocode_window`

**webview_widget** - Clean web browser widget with QWebChannel:
- BrowserWidget: Complete browser with navigation bar
- NavigationBar: Reusable navigation controls
- WebView: Theme-integrated QWebEngineView wrapper
- CSP-safe QWebChannel bridge for Python↔JavaScript communication
- Educational code with extensive comments
- Package: `vfwidgets_webview`

### Shared Utilities (vfwidgets_common)

**vfwidgets_common** is the foundational package providing cross-platform utilities and base classes:

**Platform Detection**:
- `is_wsl()` - Detect Windows Subsystem for Linux
- `is_wayland()` - Detect Wayland display server
- `is_remote_desktop()` - Detect RDP/VNC sessions
- `get_desktop_environment()` - Identify GNOME/KDE/XFCE
- Automatic platform quirks application

**Desktop Integration API** (RECOMMENDED):
```python
from vfwidgets_common.desktop import configure_desktop

# Single call handles everything
app = configure_desktop(
    app_name="myapp",
    app_display_name="My Application",
    icon_name="myapp",
    desktop_categories="Utility;",
)
```
- Automatically detects platform (WSL, Wayland, X11, Remote Desktop)
- Applies platform-specific quirks (software rendering, scaling fixes)
- Checks/installs desktop integration (icons, .desktop files on Linux)
- Creates QApplication with proper metadata
- Integrates with ThemedApplication when vfwidgets-theme is installed

**Single Instance Applications**:
```python
from vfwidgets_common import SingleInstanceApplication

class MyApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="myapp")

    def handle_message(self, message: dict):
        # Handle IPC messages from other instances
        if message["action"] == "open":
            self.window.open_file(message["file"])
```
- IPC via QLocalSocket/QLocalServer
- Automatic primary/secondary instance detection
- JSON message protocol
- Optional ThemedApplication integration

**Base Classes**:
- Abstract protocols for dependency injection
- Common signal definitions
- Utility functions for Qt applications

Package: `vfwidgets_common` (required by most widgets and all applications)

### Applications

The repository includes four production applications demonstrating VFWidgets integration:

**ViloxTerm** - Modern terminal emulator:
- Chrome-style tabs with split panes (using chrome-tabbed-window + multisplit_widget)
- Multi-session terminal server with xterm.js (using terminal_widget)
- VSCode-compatible themes with live switching (using theme_system)
- Comprehensive preferences: 58 settings across 4 tabs
- User-customizable keyboard shortcuts (using keybinding_manager)
- Cross-platform desktop integration (using vfwidgets_common.desktop)
- Installation: `cd apps/viloxterm && make local-release`

**Reamde** - Single-instance markdown viewer:
- VS Code-style interface (using vilocode_window)
- Tabbed navigation (using chrome-tabbed-window)
- Single-instance behavior via IPC (using vfwidgets_common.SingleInstanceApplication)
- Live markdown rendering with syntax highlighting, diagrams, math (using markdown_widget)
- Theme system integration with auto-propagation
- Command-line file opening with cross-directory support
- Installation: `cd apps/reamde && pip install -e .`

**Theme Studio** - Visual theme editor:
- Interactive theme token editing (color and font properties)
- Real-time preview of theme changes
- VSCode-compatible JSON theme export
- Font/color token browsers with hierarchical organization
- Undo/redo support for all edits
- System font detection and preview
- Installation: `cd apps/theme-studio && pip install -e .`

**ViloWeb** - Educational web browser:
- Chrome-style frameless window (using chrome-tabbed-window)
- Multi-tab browsing with unified title bar
- JSON-based bookmark system with search
- QWebChannel bridge for Python↔JavaScript communication (using webview_widget)
- Dark theme by default with automatic theme integration
- Educational codebase with extensive comments
- Installation: `cd apps/viloweb && pip install -e .`

### Theme System Integration Pattern
Widgets can optionally integrate with vfwidgets-theme:

```python
# Check if theme system available
try:
    from vfwidgets_theme import ThemedWidget
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    ThemedWidget = object

# Use mixin pattern if available
if THEME_AVAILABLE:
    _BaseClass = type("_BaseClass", (ThemedWidget, QWidget), {})
else:
    _BaseClass = QWidget

class MyWidget(_BaseClass):
    # Define theme_config mapping
    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }
```

## Development Practices

### PySide6 Framework (NOT PyQt)
This project uses **PySide6**, not PyQt5 or PyQt6:
- Import Signal from `PySide6.QtCore` (NOT `pyqtSignal`)
- Use `PySide6.QtWidgets`, `PySide6.QtCore`, `PySide6.QtGui`
- Test with `pytest-qt` plugin

### Task-Based Development with Agents
This codebase uses systematic task-based implementation:
- Phase-based task files in `wip/` directories (e.g., `phase0-tasks-IMPLEMENTATION.md`)
- **Evidence-based completion**: All task execution must show actual output
- Reality checks every 3 tasks to validate integration
- See `writing-dev-AGENTS-v2.md` for detailed agent development philosophy

### Clean Architecture Principles
Complex widgets follow clean architecture:
- **Model**: Pure business logic, no Qt dependencies
- **View**: Qt widgets, visual rendering only
- **Controller**: Command pattern with undo/redo
- **Protocols**: Dependency injection via abstract protocols

Examples: multisplit_widget and markdown_widget both use MVC architecture

### Creating New Widgets
```bash
# Use the widget generator
python tools/create_widget.py my_new_widget

# This creates the standard structure with:
# - pyproject.toml with standard dependencies
# - src/vfwidgets_my_new_widget/ package
# - tests/ with pytest setup
# - examples/ for usage demonstrations
```

### Code Quality Standards
- **Formatting**: Black with 100-character line length
- **Linting**: Ruff (see pyproject.toml for rules)
- **Type Hints**: MyPy with strict settings
- **Testing**: pytest-qt for GUI testing
- **Docstrings**: Required for public APIs

### Package Naming Convention
- Package names: `vfwidgets_<widget_name>` (underscores)
- PyPI distribution: `vfwidgets-<widget-name>` (hyphens)
- Import path: `from vfwidgets_widget_name import Widget`

## Important Files

- `pyproject.toml` (root) - Workspace-wide tool configuration
- `README.md` - User-facing documentation
- `writing-dev-AGENTS-v2.md` - Agent development philosophy (execution evidence required)
- `tools/create_widget.py` - Widget template generator
- `docs/` - Documentation and guides (widget development, task-driven development, theme integration, etc.)

## Testing Philosophy

### Running Examples as Tests
Examples should be executable and serve as integration tests:
```bash
# Examples must run successfully
python examples/01_basic_usage.py
python examples/02_advanced_features.py
```

### Evidence-Based Validation
Following the agent development guide:
- Show actual terminal output, not descriptions
- Verify imports work: `python -c "from package import Class"`
- Display exit codes: always show execution results
- No "successfully executed" without proof

### Test Coverage Expectations
- Unit tests for all public APIs
- Integration tests for widget interaction
- Examples that demonstrate real usage
- pytest-qt for GUI component testing

## Common Patterns

### Signal/Slot Pattern
```python
from PySide6.QtCore import Signal, Slot

class MyWidget(QWidget):
    # Define signals
    value_changed = Signal(int)

    @Slot()
    def on_button_clicked(self):
        self.value_changed.emit(42)
```

### Widget Provider Pattern (multisplit_widget)
```python
from vfwidgets_multisplit import MultisplitWidget, WidgetProvider

class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        return QTextEdit()

    def widget_closing(self, widget_id: str, pane_id: str, widget: QWidget) -> None:
        # Optional cleanup
        pass

multisplit = MultisplitWidget(provider=MyProvider())
```

### Themed Widget Pattern
```python
from vfwidgets_theme import ThemedWidget

class MyThemedWidget(ThemedWidget):
    theme_config = {
        "bg": "editor.background",
        "fg": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        # Theming automatically applied
```

## Version Information

Widgets maintain independent semantic versioning. Current versions:
- `vfwidgets-theme-system`: 2.0.0-rc4 (Beta, mature and stable)
- `vfwidgets-multisplit`: 1.0.0 (Alpha, stable)
- `vfwidgets-terminal`: 1.0.0 (Alpha, production-ready)
- `vfwidgets-markdown`: 2.0.0 (Beta, production-ready)
- `chrome-tabbed-window`: 1.1.1 (Beta, production-ready with tab renaming)
- `vfwidgets-vilocode-window`: 0.1.0 (Alpha, development)
- `vfwidgets-webview`: 0.2.0 (Alpha, educational/development)
- `vfwidgets-common`: 0.1.0 (Beta, foundational utilities)
- `vfwidgets-keybinding-manager`: (version TBD)

## Dependencies

Core dependencies across all widgets:
- Python 3.9+
- **PySide6 >= 6.9.0** (recommended for all widgets)
  - theme_system and chrome-tabbed-window support 6.5.0+ for broader compatibility
  - Most widgets (multisplit, terminal, markdown, vfwidgets_common) require 6.9.0+
  - WebEngine-based widgets (terminal, markdown, webview) specifically need QtWebEngine
- typing-extensions >= 4.0.0 (for Python 3.9 compatibility)

Development dependencies (standardized):
- pytest >= 7.0
- pytest-qt >= 4.0
- black >= 23.0
- ruff >= 0.1.0
- mypy >= 1.0

**Note**: vfwidgets_common is required by most widgets and all applications. Install it first:
```bash
pip install -e ./shared/vfwidgets_common
```

## Running in WSL (Windows Subsystem for Linux)

### Automatic WSL Detection and Configuration

**VFWidgets automatically detects WSL and configures Qt WebEngine** for software rendering. No manual configuration is required!

When you run ViloxTerm or any application using terminal_widget in WSL, you'll see:
```
[INFO] WSL detected: Using software rendering for Qt WebEngine
[INFO] Auto-configured environment for LIBGL_ALWAYS_SOFTWARE, QT_QUICK_BACKEND, QTWEBENGINE_CHROMIUM_FLAGS
```

The platform detection module (`vfwidgets_common.platform`) automatically:
- Detects WSL by checking `/proc/version` for "microsoft" or "wsl"
- Sets `LIBGL_ALWAYS_SOFTWARE=1` for software OpenGL rendering
- Sets `QT_QUICK_BACKEND=software` for Qt Quick software backend
- Configures `QTWEBENGINE_CHROMIUM_FLAGS` with WSL-compatible flags

### Manual Override (if needed)

If you need to customize the environment variables, set them **before** running the application:
```bash
export QTWEBENGINE_CHROMIUM_FLAGS="--your-custom-flags"
viloxterm  # Will append (not replace) your custom flags
```

### Building VFWidgets Applications (RECOMMENDED)

**Use the unified desktop integration API for all VFWidgets applications:**

```python
# In your main entry point, BEFORE importing Qt modules:
from vfwidgets_common.desktop import configure_desktop

# Single call handles everything
app = configure_desktop(
    app_name="myapp",
    app_display_name="My Application",
    icon_name="myapp",
    desktop_categories="Utility;",
)

# Create your main window
from myapp import MyMainWindow
window = MyMainWindow()
window.show()

sys.exit(app.exec())
```

**This automatically:**
- Detects platform (WSL, Wayland, X11, Remote Desktop)
- Applies platform quirks (software rendering, scaling fixes)
- Checks/installs desktop integration (icons, .desktop files)
- Creates QApplication with proper metadata

### Legacy Platform Detection API

**Note:** The following functions are still available but `configure_desktop()` is now recommended for applications.

```python
from vfwidgets_common import (
    is_wsl,                      # Detect WSL environment (DEPRECATED - use configure_desktop)
    is_remote_desktop,           # Detect remote desktop (DEPRECATED - use configure_desktop)
    configure_all_for_webengine, # Configure environment (DEPRECATED - use configure_desktop)
)

# Old way (still works, but not recommended for new code)
configure_all_for_webengine()

# New way (recommended)
from vfwidgets_common.desktop import configure_desktop
app = configure_desktop(app_name="myapp", ...)
```

### X Server Display (if using WSL1 or older WSL2)

For WSLg (WSL2 on Windows 11), DISPLAY is auto-configured. For older WSL:
```bash
export DISPLAY=:0
```
