# VFWidgets KeybindingManager

Configurable keyboard shortcuts for PySide6/PyQt6 applications.

## Features

- **Simple API**: Register actions and apply shortcuts in 3 lines of code
- **Persistent Storage**: Save and load user-customized keybindings
- **Action Registry**: Centralized command pattern for application actions
- **Type-Safe**: 100% type hints with mypy --strict compliance
- **Well-Tested**: 89% test coverage with comprehensive unit tests
- **Category Support**: Organize actions into logical groups
- **Auto-Save**: Automatically persist keybinding changes
- **Qt Integration**: Seamless integration with QAction and QWidget

## Installation

```bash
pip install -e /path/to/vfwidgets/widgets/keybinding_manager
```

## Quick Start

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_keybinding import KeybindingManager, ActionDefinition

app = QApplication([])
window = QMainWindow()

# Create manager
manager = KeybindingManager()

# Register action
manager.register_action(ActionDefinition(
    id="file.save",
    description="Save File",
    default_shortcut="Ctrl+S",
    category="File",
    callback=save_file  # Your function
))

# Apply shortcuts to window
manager.apply_shortcuts(window)

window.show()
app.exec()
```

## Examples

- **[01_minimal_usage.py](examples/01_minimal_usage.py)** - Minimal example (< 20 lines)
- **[02_full_application.py](examples/02_full_application.py)** - Complete text editor with menus

Run examples:
```bash
python examples/01_minimal_usage.py
python examples/02_full_application.py
```

## Core Concepts

### ActionDefinition

Defines an action that can be triggered:

```python
action = ActionDefinition(
    id="edit.copy",           # Unique dot-separated ID
    description="Copy",       # Human-readable description
    default_shortcut="Ctrl+C",  # Default keyboard shortcut
    category="Edit",          # Category for grouping
    callback=copy_function    # Optional callback function
)
```

### KeybindingManager

Central manager for registering actions and applying shortcuts:

```python
manager = KeybindingManager(
    storage_path="~/.config/myapp/keybindings.json",  # Optional persistent storage
    auto_save=True  # Auto-save changes
)

# Register actions
manager.register_action(action)

# Load saved bindings
manager.load_bindings()

# Apply shortcuts to widget
manager.apply_shortcuts(main_window)

# Query bindings
shortcut = manager.get_binding("edit.copy")

# Change binding
manager.set_binding("edit.copy", "Ctrl+Shift+C")

# Reset to defaults
manager.reset_to_defaults()
```

## Documentation

- **[Architecture Design](docs/architecture-DESIGN.md)** - System design and components
- **[Developer Experience Plan](docs/developer-experience-PLAN.md)** - DX requirements and goals
- **[Implementation Roadmap](docs/implementation-roadmap-PLAN.md)** - Phased development plan
- **[Implementation Tasks](docs/tasks-IMPLEMENTATION.md)** - Step-by-step task checklist

## Development

### Running Tests

```bash
# Run tests
pytest tests/unit/ -v

# Check coverage
pytest tests/unit/ --cov=src/vfwidgets_keybinding --cov-report=term-missing

# Type checking
mypy --strict src/vfwidgets_keybinding
```

### Current Status

**Phase 1 (MVP + Core DX)**: ✅ Complete

- ✅ ActionDefinition and ActionRegistry
- ✅ KeybindingStorage with JSON persistence
- ✅ KeybindingManager orchestrator
- ✅ Unit tests (89% coverage)
- ✅ Type hints (mypy --strict passing)
- ✅ Comprehensive docstrings
- ✅ Minimal and full application examples
- ✅ Documentation

**Phase 2 (UI + Polish)**: 📅 Planned
- KeybindingDialog for user customization
- KeySequenceEdit widget
- Theme integration
- Additional documentation guides

**Phase 3 (Advanced Features)**: 📅 Planned
- Context-aware bindings
- Import/export profiles
- Performance optimizations

## Requirements

- Python >= 3.9
- PySide6 >= 6.5.0

## License

MIT

## Part of VFWidgets

This widget is part of the VFWidgets collection - reusable Qt widgets for Python applications.
