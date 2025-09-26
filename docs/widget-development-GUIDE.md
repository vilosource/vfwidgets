# VFWidgets Development Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Widget Development Standards](#widget-development-standards)
3. [Architecture Patterns](#architecture-patterns)
4. [Testing Guidelines](#testing-guidelines)
5. [Documentation Standards](#documentation-standards)
6. [Publishing Widgets](#publishing-widgets)

## Getting Started

### Prerequisites

- Python 3.9+
- PySide6 6.9.0+
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setting Up Development Environment

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/vfwidgets.git
cd vfwidgets
```

2. **Set up direnv (recommended):**
```bash
# Install direnv if not already installed
# On Ubuntu/Debian: sudo apt-get install direnv
# On macOS: brew install direnv

# Allow direnv in this directory
direnv allow
```

The `.envrc` file will automatically:
- Create and activate a virtual environment
- Set up Python paths
- Configure Qt environment variables

3. **Manual setup (if not using direnv):**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -U pip setuptools wheel
pip install pytest pytest-qt black ruff mypy
```

### Creating a New Widget

Use the widget generator to create a new widget from the template:

```bash
python tools/create_widget.py my_custom_widget --author "Your Name" --email "your.email@example.com"
```

This creates a complete widget structure in `widgets/my_custom_widget_widget/`.

## Widget Development Standards

### Naming Conventions

- **Widget directory:** `{name}_widget` (snake_case with _widget suffix)
- **Package name:** `vfwidgets_{name}` (snake_case with vfwidgets_ prefix)
- **Class name:** `{Name}Widget` (PascalCase with Widget suffix)
- **PyPI package:** `vfwidgets-{name}` (kebab-case with vfwidgets- prefix)

### File Structure

Every widget MUST follow this structure:

```
widgets/my_widget/
├── pyproject.toml          # Package configuration (REQUIRED)
├── README.md              # Widget documentation (REQUIRED)
├── LICENSE                # License file (REQUIRED)
├── src/
│   └── vfwidgets_my_widget/
│       ├── __init__.py    # Package initialization (REQUIRED)
│       ├── my_widget.py   # Main widget implementation (REQUIRED)
│       ├── py.typed       # Type hint marker (REQUIRED)
│       └── resources/     # Optional resources
│           ├── icons/
│           └── styles/
├── tests/
│   ├── __init__.py
│   └── test_my_widget.py  # Unit tests (REQUIRED)
├── examples/
│   └── basic_usage.py     # Usage example (REQUIRED)
└── docs/
    └── api.md             # API documentation (RECOMMENDED)
```

### Code Style Guidelines

#### Python Standards

- **Formatting:** Black with line length 100
- **Linting:** Ruff with configuration in root pyproject.toml
- **Type hints:** Required for all public APIs
- **Docstrings:** Google style for all public classes and methods

#### PySide6/Qt Guidelines

1. **Inheritance:** Inherit from appropriate Qt widget or VFBaseWidget
2. **Signals:** Define custom signals at class level
3. **Properties:** Use Qt properties for configurable attributes
4. **Events:** Override event handlers carefully, always call super()
5. **Threading:** Use QThread for long-running operations
6. **Resources:** Use Qt resource system for embedded files

Example widget structure:

```python
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, Property

class MyCustomWidget(QWidget):
    """Brief description of widget.

    Longer description explaining purpose and usage.

    Signals:
        value_changed: Emitted when value changes
    """

    # Signals
    value_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._value = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Implementation

    @Property(object, notify=value_changed)
    def value(self) -> object:
        """Get the current value."""
        return self._value

    @value.setter
    def value(self, new_value: object) -> None:
        """Set the value."""
        if self._value != new_value:
            self._value = new_value
            self.value_changed.emit(new_value)
```

## Architecture Patterns

### Using VFBaseWidget

For widgets that need common functionality, inherit from VFBaseWidget:

```python
from vfwidgets_common import VFBaseWidget

class MyWidget(VFBaseWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def _setup_widget(self):
        super()._setup_widget()
        # Your initialization
```

### State Management

- Use properties for public state
- Emit signals when state changes
- Validate input in setters
- Provide sensible defaults

### Resource Management

```python
from pathlib import Path
import importlib.resources

def get_icon_path(icon_name: str) -> Path:
    """Get path to icon resource."""
    if hasattr(importlib.resources, 'files'):
        # Python 3.9+
        return importlib.resources.files('vfwidgets_my_widget') / 'resources' / 'icons' / icon_name
    else:
        # Fallback
        import pkg_resources
        return Path(pkg_resources.resource_filename(
            'vfwidgets_my_widget', f'resources/icons/{icon_name}'
        ))
```

## Testing Guidelines

### Test Structure

Every widget MUST have tests covering:

1. **Creation:** Widget can be instantiated
2. **Properties:** Getters and setters work correctly
3. **Signals:** Signals are emitted properly
4. **UI Interaction:** User interactions work as expected
5. **Edge Cases:** Handle invalid input gracefully

### Testing with pytest-qt

```python
import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_my_widget import MyWidget

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def widget(qapp, qtbot):
    """Create widget instance for testing."""
    widget = MyWidget()
    qtbot.addWidget(widget)
    return widget

def test_widget_creation(widget):
    """Test widget can be created."""
    assert widget is not None
    assert isinstance(widget, MyWidget)

def test_signal_emission(widget, qtbot):
    """Test signal is emitted on value change."""
    with qtbot.waitSignal(widget.value_changed, timeout=1000):
        widget.set_value("test")

def test_mouse_interaction(widget, qtbot):
    """Test mouse click interaction."""
    qtbot.mouseClick(widget, Qt.LeftButton)
    # Assert expected behavior
```

### Running Tests

```bash
# Test single widget
cd widgets/my_widget
pytest

# Test all widgets
./tools/test_all.sh

# With coverage
pytest --cov --cov-report=html
```

## Documentation Standards

### README Requirements

Each widget README must include:

1. **Description:** What the widget does
2. **Installation:** How to install
3. **Basic Usage:** Simple code example
4. **Features:** Key features list
5. **API Reference:** Link to detailed docs
6. **Examples:** Link to example scripts

### Docstring Standards

Use Google style docstrings:

```python
def complex_method(self, param1: str, param2: int = 0) -> bool:
    """Brief description of method.

    Longer description if needed, explaining behavior,
    side effects, and usage patterns.

    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 0

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails

    Example:
        >>> widget.complex_method("test", 42)
        True
    """
```

### API Documentation

Create `docs/api.md` with:

- Class hierarchy
- Signal descriptions
- Method signatures
- Property descriptions
- Usage examples
- Styling options

## Publishing Widgets

### Version Management

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR:** Breaking API changes
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes

Update version in:
1. `pyproject.toml`
2. `src/vfwidgets_name/__init__.py`

### Pre-publish Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code formatted (`black src/`)
- [ ] Linting passes (`ruff check src/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Documentation updated
- [ ] Examples work
- [ ] Version bumped
- [ ] CHANGELOG updated

### Publishing to PyPI

1. **Build the package:**
```bash
cd widgets/my_widget
python -m build
```

2. **Test with TestPyPI (optional):**
```bash
python -m twine upload --repository testpypi dist/*
```

3. **Publish to PyPI:**
```bash
python -m twine upload dist/*
```

Or use GitHub Actions:
- Go to Actions → Release Widget
- Select widget, version bump type
- Enable PyPI publishing
- Run workflow

### Post-publish

1. Create GitHub release
2. Update main README with widget status
3. Announce in project channels
4. Monitor for issues

## Best Practices

### DO

- ✅ Follow the established structure exactly
- ✅ Write comprehensive tests
- ✅ Document all public APIs
- ✅ Use type hints everywhere
- ✅ Handle errors gracefully
- ✅ Emit appropriate signals
- ✅ Provide sensible defaults
- ✅ Include working examples
- ✅ Support theme changes
- ✅ Clean up resources properly

### DON'T

- ❌ Break backward compatibility without major version bump
- ❌ Use global state
- ❌ Block the UI thread
- ❌ Ignore Qt best practices
- ❌ Skip tests
- ❌ Leave debug print statements
- ❌ Hardcode paths or values
- ❌ Ignore type checking warnings
- ❌ Create circular dependencies
- ❌ Mix business logic with UI

## Getting Help

- **Issues:** Open an issue on GitHub
- **Discussions:** Use GitHub Discussions
- **Contributing:** See CONTRIBUTING.md
- **Code of Conduct:** See CODE_OF_CONDUCT.md

## Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt Widget Gallery](https://doc.qt.io/qt-6/gallery.html)
- [Python Packaging Guide](https://packaging.python.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)