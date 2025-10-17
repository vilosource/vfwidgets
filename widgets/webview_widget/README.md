# vfwidgets-webview

Clean, reusable web browser widget with navigation bar for PySide6/Qt applications.

## Features

- 🌐 **Simple Browser Widget**: Complete browser functionality in one widget
- 🎨 **Theme System Integration**: Full vfwidgets-theme support with dark/light modes
- 🧩 **Reusable Components**: Use NavigationBar, WebView, or complete BrowserWidget
- 📦 **Minimal Dependencies**: Just PySide6 + vfwidgets-theme
- 🎓 **Educational**: Heavily commented code showing QtWebEngine patterns
- 🔧 **Extensible**: Clean API for building advanced browsers (see ViloWeb)

## Installation

```bash
pip install vfwidgets-webview
```

Or for development:

```bash
cd widgets/webview_widget
pip install -e ".[dev]"
```

## Quick Start

### Basic Browser Widget (Single Page Browser)

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_webview import BrowserWidget

app = QApplication([])

# Create browser widget
browser = BrowserWidget()
browser.navigate("https://example.com")
browser.show()

app.exec()
```

### With Theme System

```python
from PySide6.QtWidgets import QApplication
from vfwidgets_theme import ThemedApplication
from vfwidgets_webview import BrowserWidget

app = QApplication([])
themed_app = ThemedApplication()

# Browser automatically inherits theme
browser = BrowserWidget()
browser.navigate("https://example.com")
browser.show()

# Switch themes
themed_app.set_theme("dark")

app.exec()
```

## Components

### BrowserWidget

Complete browser with navigation bar and web view.

```python
from vfwidgets_webview import BrowserWidget

browser = BrowserWidget()

# Navigate
browser.navigate("https://example.com")
browser.back()
browser.forward()
browser.reload()

# Connect to signals
browser.title_changed.connect(lambda title: print(f"Title: {title}"))
browser.url_changed.connect(lambda url: print(f"URL: {url}"))
browser.load_progress.connect(lambda progress: print(f"Loading: {progress}%"))
```

### NavigationBar

Standalone navigation bar for custom browser UIs.

```python
from vfwidgets_webview import NavigationBar

navbar = NavigationBar()
navbar.back_clicked.connect(my_back_handler)
navbar.forward_clicked.connect(my_forward_handler)
navbar.url_submitted.connect(my_navigate_handler)
```

### WebView

Simple wrapper around QWebEngineView with theme integration.

```python
from vfwidgets_webview import WebView

webview = WebView()
webview.load("https://example.com")
```

## Progressive Examples

Learn by following numbered examples:

- `examples/01_minimal_browser.py` - Simplest possible browser
- `examples/02_themed_browser.py` - With theme system integration
- `examples/03_navigation_signals.py` - Handling navigation events
- `examples/04_custom_navigation.py` - Custom navigation bar styling
- `examples/05_single_page_browser.py` - Complete MVP: old-school single-page browser

## Documentation

See `docs/` directory:

- `SPECIFICATION.md` - Complete technical specification
- `API.md` - Public API reference
- `THEME-INTEGRATION.md` - Theme system integration guide
- `THEME-STUDIO.md` - Using in theme-studio for testing

## Architecture

```
BrowserWidget
├── NavigationBar
│   ├── BackButton
│   ├── ForwardButton
│   ├── ReloadButton
│   ├── HomeButton
│   └── URLBar (QLineEdit)
└── WebView (QWebEngineView wrapper)
    └── WebPage (QWebEnginePage)
```

## Theme System Integration

The widget uses vfwidgets-theme for consistent theming:

```python
# Widget automatically themed
browser = BrowserWidget()

# Theme configuration
browser.theme_config = {
    "navbar_background": "editor.background",
    "navbar_foreground": "editor.foreground",
    "urlbar_background": "input.background",
    "urlbar_foreground": "input.foreground",
    "urlbar_border": "input.border",
}
```

## Building Advanced Browsers

This widget is designed as a foundation. For advanced features (extensions, security testing, automation), see:

- **ViloWeb**: Educational browser built on vfwidgets-webview
- **Your Browser**: Build your own with custom features!

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/

# Type check
mypy src/
```

## Contributing

Follow VFWidgets contribution guidelines. Key points:

- Code must be heavily commented (educational focus)
- All public APIs need docstrings with examples
- Add progressive examples for new features
- Maintain theme system integration

## License

MIT License - see LICENSE file

## Related Projects

- **vfwidgets-theme**: Theme system (required dependency)
- **chrome-tabbed-window**: Chrome-style tabs (for multi-tab browsers)
- **ViloWeb**: Educational browser built on this widget
