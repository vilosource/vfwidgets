# Reamde - Single-Instance Markdown Viewer

A modern, single-instance markdown document viewer with VS Code-style interface and tabbed navigation.

## Features

- ✨ **Single-instance behavior** - Multiple invocations open in the same window
- 📑 **Tabbed interface** - Multiple documents in one window
- 🎨 **VS Code-style layout** - Professional ViloCodeWindow interface
- 🔥 **Live rendering** - See your markdown as beautiful HTML
- 🎯 **Syntax highlighting** - Prism.js support for 300+ languages
- 📊 **Diagrams** - Mermaid.js support (flowcharts, sequence, gantt, etc.)
- 🧮 **Math** - KaTeX for LaTeX equations
- 🌈 **Theme support** - Automatic integration with VFWidgets theme system
- ⚡ **Fast** - Efficient Qt-based rendering

## Installation

### From Source (Development)

```bash
# Install in editable mode
pip install -e /path/to/vfwidgets/apps/reamde

# Or install with pip from the directory
cd /path/to/vfwidgets/apps/reamde
pip install -e .
```

### Dependencies

Reamde requires the following VFWidgets packages:
- `vfwidgets-common` - Common utilities and SingleInstanceApplication
- `vfwidgets-vilocode-window` - VS Code-style window layout
- `chrome-tabbed-window` - Chrome-style tabbed interface
- `vfwidgets-markdown` - Markdown rendering widget
- `vfwidgets-theme-system` - Theme support (optional but recommended)

## Usage

### Basic Usage

```bash
# Open a markdown file
reamde README.md

# If reamde is already running, the file opens in a new tab
reamde DOCS.md
```

### Single-Instance Behavior

Reamde uses IPC (Inter-Process Communication) to ensure only one instance runs at a time:

1. **First launch**: Creates window and opens file
   ```bash
   $ reamde README.md
   # Window opens with README.md
   ```

2. **Subsequent launches**: Opens file in existing window
   ```bash
   $ reamde CONTRIBUTING.md
   # New tab opens in the same window
   ```

3. **Cross-directory support**: Works from any directory
   ```bash
   $ cd ~/projects/app1
   $ reamde README.md      # Opens in window

   $ cd ~/projects/app2
   $ reamde README.md      # Opens in same window, new tab
   ```

### Features in the UI

#### Window Layout

```
┌─ Reamde ────────────────────────────────────────┐
│ File  Edit  View  Help                      ⚫🟡🟢│ Title bar
├──────────────────────────────────────────────────┤
│A│S│┌──────────────────────────────────────────┐ │
│c│i││ [README.md] [DOCS.md] [+]                │ │ Tab bar
│t│d│├──────────────────────────────────────────┤ │
│i│e││                                          │ │
│v│b││     Markdown Content                     │ │ Content
│i│a││     (HTML rendered)                      │ │
│t│r││                                          │ │
│y│ │                                          │ │
│ │ │                                          │ │
│B│ │                                          │ │
│a│ │                                          │ │
│r│ └──────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│ Status: Ready                                    │ Status bar
└──────────────────────────────────────────────────┘
```

#### Keyboard Shortcuts

- **Ctrl+W** - Close current tab
- **Ctrl+Tab** - Next tab
- **Ctrl+Shift+Tab** - Previous tab
- **Ctrl+Q** - Quit application

#### Tab Management

- Click **×** on tab to close
- Drag tabs to reorder
- Right-click tab for context menu (future)
- Tab tooltip shows full file path

## Architecture

### Single-Instance Implementation

Reamde uses `SingleInstanceApplication` from `vfwidgets_common`:

```python
from vfwidgets_common import SingleInstanceApplication

class ReamdeApp(SingleInstanceApplication):
    def __init__(self, argv):
        super().__init__(argv, app_id="reamde")

    def handle_message(self, message: dict):
        # Handle messages from other instances
        if message["action"] == "open":
            self.window.open_file(message["file"])
```

**How it works**:

1. **Primary instance**: Creates QLocalServer listening on `/tmp/vfwidgets-reamde-{user}`
2. **Secondary instance**: Connects via QLocalSocket, sends message, exits
3. **IPC protocol**: JSON messages over local socket
   ```json
   {"action": "open", "file": "/absolute/path/to/file.md"}
   ```

### Component Stack

```
ReamdeApp (SingleInstanceApplication)
  └─ ReamdeWindow (ViloCodeWindow)
      └─ ChromeTabbedWindow
          └─ MarkdownViewerTab (QWidget)
              └─ MarkdownViewer (QWebEngineView)
```

### Key Classes

#### ReamdeApp
- Extends `SingleInstanceApplication`
- Manages single-instance logic
- Handles IPC messages
- Creates and manages window

#### ReamdeWindow
- Extends `ViloCodeWindow`
- Contains `ChromeTabbedWindow` for tabs
- Manages file loading and tab lifecycle
- Updates window title based on current tab

#### MarkdownViewerTab
- Wraps `MarkdownViewer` widget
- Tracks file path
- Handles file loading and reloading

## Development

### Project Structure

```
apps/reamde/
├── pyproject.toml              # Package configuration
├── README.md                   # This file
├── reamde.py                   # Development launcher
└── src/reamde/
    ├── __init__.py             # Package exports
    ├── __main__.py             # CLI entry point
    ├── app.py                  # ReamdeApp class
    └── window.py               # ReamdeWindow + MarkdownViewerTab
```

### Running in Development

```bash
# Direct execution
python apps/reamde/reamde.py README.md

# Or use the installed command
reamde README.md
```

### Testing

```bash
# Test single-instance behavior
Terminal 1: $ reamde file1.md
Terminal 2: $ reamde file2.md  # Should open in Terminal 1's window

# Test with different directories
$ cd ~/docs && reamde README.md
$ cd ~/projects && reamde TODO.md  # Opens in same window
```

## Supported Markdown Features

Powered by `vfwidgets-markdown` v2.0:

### Basic Markdown
- **Headings** - H1 through H6
- **Lists** - Ordered and unordered
- **Emphasis** - Bold, italic, strikethrough
- **Links** - HTTP and relative
- **Images** - Inline and reference-style
- **Code** - Inline and fenced code blocks
- **Blockquotes** - Nested support
- **Tables** - GitHub-flavored
- **Horizontal rules**

### Extended Features
- **Syntax highlighting** - 300+ languages via Prism.js
- **Mermaid diagrams** - Flowchart, sequence, class, gantt, state, ER, etc.
- **Math equations** - Inline and block LaTeX via KaTeX
- **Task lists** - `- [ ]` and `- [x]`
- **Footnotes** - Reference-style notes
- **Definition lists**
- **Table of contents** - Auto-generated from headings

## Troubleshooting

### "Could not connect to running instance"

If you see this error, it means:
1. The primary instance crashed without cleaning up
2. Solution: Remove stale socket file

```bash
# Linux/macOS
rm /tmp/vfwidgets-reamde-$USER

# Then relaunch
reamde file.md
```

### Window doesn't come to front

On some Linux desktop environments (especially Wayland), window focus/raise
may have limited support due to compositor restrictions. This is a platform
limitation, not a reamde bug.

### Slow rendering

If markdown rendering is slow:
1. Check file size (very large files may be slow)
2. Disable complex diagrams temporarily
3. Check CPU usage (WebEngine rendering is CPU-intensive)

## Future Enhancements

- [ ] File watching and auto-reload
- [ ] Export to PDF
- [ ] Export to HTML
- [ ] Recent files menu
- [ ] Search within document
- [ ] Bookmarks / navigation
- [ ] Custom CSS themes
- [ ] Plugin system
- [ ] Presentation mode

## License

MIT License - see LICENSE file for details

## Credits

Built with VFWidgets components:
- **SingleInstanceApplication** - Reusable single-instance pattern
- **ViloCodeWindow** - VS Code-style layout
- **ChromeTabbedWindow** - Chrome-style tabs
- **MarkdownViewer** - Full-featured markdown renderer
- **Theme System** - VSCode-compatible theming

Powered by:
- **PySide6** - Qt for Python
- **markdown-it-py** - Markdown parser
- **Prism.js** - Syntax highlighting
- **Mermaid.js** - Diagram rendering
- **KaTeX** - Math typesetting
