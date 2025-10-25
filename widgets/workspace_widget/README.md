# WorkspaceWidget

Multi-folder workspace widget with VS Code-like file explorer for PySide6.

## Features

- **Multi-Folder Workspaces** - Open multiple root folders in one workspace
- **VS Code Compatibility** - `.workspace.json` config format
- **File Filtering** - Filter by extension or custom callback
- **Session Persistence** - Save/restore UI state (expanded folders, scroll position)
- **File Navigation** - `reveal_file()`, `find_file()` with fuzzy matching
- **Tab Integration** - Auto-sync with QTabWidget
- **Theme Support** - Automatic integration with vfwidgets-theme (optional)
- **Extension Points** - Protocol-based customization (icons, context menu, error handling)

## Installation

```bash
pip install vfwidgets-workspace
```

### Optional Theme Support

```bash
pip install vfwidgets-workspace[theme]
```

## Quick Start

```python
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_workspace import WorkspaceWidget

app = QApplication([])

# Create workspace widget
workspace = WorkspaceWidget()

# Handle file selection
workspace.file_selected.connect(lambda path: print(f"Selected: {path}"))

# Open workspace
workspace.open_workspace(Path("/path/to/project"))

window = QMainWindow()
window.setCentralWidget(workspace)
window.show()
app.exec()
```

## Examples

See `examples/` directory for progressive examples:

- `01_basic_single_folder.py` - Basic usage
- `02_multi_folder_workspace.py` - Multi-folder config
- `03_file_filtering.py` - File filtering
- `04_session_persistence.py` - Session save/restore
- `05_file_navigation.py` - File navigation and search
- `06_tab_integration.py` - Tab widget integration

## Documentation

- [Specification](SPECIFICATION.md) - Complete feature specification
- [Design](DESIGN.md) - Implementation design document
- [API Reference](docs/api.md) - API documentation

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run examples
python examples/01_basic_single_folder.py
```

## License

MIT License - see [LICENSE](LICENSE) file
