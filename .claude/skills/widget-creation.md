---
name: widget-creation
description: Guide for creating new VFWidgets packages following monorepo standards. Use when creating new widget packages, widget templates, or widget generators.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Widget Creation Skill

When the user asks to create a new widget, follow these steps systematically to ensure compliance with VFWidgets monorepo standards.

## 1. Review Widget Checklist

First, read the complete widget creation checklist:

```
Read: docs/new-widget-checklist.md
```

This checklist contains:
- Required directory structure
- Must-have files
- Must-NOT-have files (no .gitignore, no .github/)
- Common mistakes to avoid

## 2. Verify Widget Name

Ensure the widget name follows conventions:

- **Widget directory**: `lowercase_with_underscores` (e.g., `progress_bar_widget`)
- **Python package**: `vfwidgets_<name>` (e.g., `vfwidgets_progress_bar`)
- **PyPI distribution**: `vfwidgets-<name>` (e.g., `vfwidgets-progress-bar`)

## 3. Create Directory Structure

Create the standard widget structure:

```bash
widgets/<widget_name>/
├── docs/                           # Widget-specific documentation
│   ├── <WIDGET>-SPECIFICATION.md
│   └── api.md
├── src/
│   └── vfwidgets_<name>/          # Python package (underscores)
│       ├── __init__.py
│       └── widget.py              # Main widget implementation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── __init__.py
├── examples/
│   ├── 01_basic_usage.py
│   └── 02_advanced_features.py
├── pyproject.toml                 # Package configuration
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development dependencies
├── README.md                      # User documentation
├── LICENSE                        # MIT License
└── CHANGELOG.md                   # Version history
```

## 4. Create pyproject.toml

Use this template, replacing placeholders with widget-specific values:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vfwidgets-<widget-name>"
version = "0.1.0"
description = "<Brief widget description>"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "VFWidgets Team"},
]
maintainers = [
    {name = "VFWidgets Team"},
]
keywords = [
    "qt",
    "pyside6",
    "widgets",
    "<widget-specific-keywords>",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: User Interfaces",
]
dependencies = [
    "PySide6>=6.5.0",
    "vfwidgets-common>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.0.0",
    "pytest-xvfb>=2.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/vilosource/vfwidgets"
Repository = "https://github.com/vilosource/vfwidgets/tree/main/widgets/<widget-name>"
Issues = "https://github.com/vilosource/vfwidgets/issues"

[tool.setuptools.packages.find]
where = ["src"]
include = ["vfwidgets_<name>*"]

[tool.setuptools.package-data]
vfwidgets_<name> = ["py.typed"]

[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by black)
    "N802",  # Qt event handlers use mixedCase
    "N803",  # Qt method parameters use mixedCase
]

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=vfwidgets_<name>",
    "--cov-report=term-missing",
]
```

## 5. Create Package __init__.py

Create `src/vfwidgets_<name>/__init__.py` with:

```python
"""<Widget description>

This package provides <brief description of functionality>.
"""

from .widget import <WidgetClassName>

__version__ = "0.1.0"
__all__ = ["<WidgetClassName>"]
```

## 6. Create Basic Widget Implementation

Create `src/vfwidgets_<name>/widget.py` with a minimal implementation:

```python
"""<Widget> implementation."""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class <WidgetClassName>(QWidget):
    """<Brief widget description>.

    This widget provides <functionality description>.

    Signals:
        <signal_name>: Description of when this signal is emitted
    """

    # Define signals
    # <signal_name> = Signal(...)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        # TODO: Implement UI setup
        pass
```

## 7. Create Basic Example

Create `examples/01_basic_usage.py`:

```python
"""Basic usage example for <Widget>."""

import sys
from PySide6.QtWidgets import QApplication
from vfwidgets_<name> import <WidgetClassName>


def main():
    """Run basic widget example."""
    app = QApplication(sys.argv)

    # Create and configure widget
    widget = <WidgetClassName>()
    widget.setWindowTitle("<Widget> - Basic Example")
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

## 8. Create Basic Test

Create `tests/test_basic.py`:

```python
"""Basic tests for <Widget>."""

import pytest
from PySide6.QtWidgets import QApplication
from vfwidgets_<name> import <WidgetClassName>


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


def test_widget_creation(app):
    """Test widget can be created."""
    widget = <WidgetClassName>()
    assert widget is not None


def test_widget_is_qwidget(app):
    """Test widget is a QWidget."""
    from PySide6.QtWidgets import QWidget
    widget = <WidgetClassName>()
    assert isinstance(widget, QWidget)
```

## 9. Create README.md

Create a comprehensive README with:

```markdown
# <Widget Name>

<Brief description>

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install vfwidgets-<widget-name>
```

## Quick Start

```python
from vfwidgets_<name> import <WidgetClassName>

# Create widget
widget = <WidgetClassName>()
widget.show()
```

## Documentation

See [docs/api.md](docs/api.md) for complete API documentation.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run example
python examples/01_basic_usage.py
```

## License

MIT License - See LICENSE file for details.
```

## 10. Copy LICENSE File

Copy the MIT license from an existing widget:

```bash
cp widgets/button_widget/LICENSE widgets/<widget_name>/LICENSE
```

## 11. Create CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial widget implementation
- Basic examples
- Unit tests
```

## 12. Verify Installation

Test that the widget can be installed and imported:

```bash
# From widget directory
pip install -e .

# Verify import works
python -c "from vfwidgets_<name> import <WidgetClassName>; print('✅ Import successful')"
```

## 13. Run Tests

Ensure tests pass:

```bash
pytest tests/ -v
```

## 14. Run Example

Verify the example runs:

```bash
python examples/01_basic_usage.py
```

## Common Mistakes to Avoid

❌ **DO NOT**:
- Create `.gitignore` in widget directory (use root monorepo `.gitignore`)
- Create `.github/` folder in widget directory (use root workflows)
- Use absolute paths in code or documentation
- Hardcode widget-specific tool configs (use root `pyproject.toml`)
- Use hyphens in Python package names (use underscores)

✅ **DO**:
- Use relative imports within the widget package
- Follow naming conventions strictly
- Create comprehensive examples
- Write unit tests for all public APIs
- Document all public classes and methods

## Reference Examples

For reference implementations, see:

- **Simple widget**: `widgets/button_widget/`
- **Complex widget with MVC**: `widgets/multisplit_widget/`
- **Theme-integrated widget**: `widgets/chrome-tabbed-window/`

## Checklist Before Completion

Before marking widget creation as complete, verify:

- [ ] Widget follows naming convention
- [ ] Package is importable: `from vfwidgets_<name> import <WidgetClassName>`
- [ ] No `.gitignore` or `.github/` in widget directory
- [ ] `pyproject.toml` has correct package name and paths
- [ ] At least one working example in `examples/`
- [ ] Basic unit tests pass
- [ ] README has usage example
- [ ] No absolute paths in code or docs
- [ ] CHANGELOG.md exists with initial entry
- [ ] LICENSE file copied from template
