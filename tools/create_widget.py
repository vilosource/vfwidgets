#!/usr/bin/env python3
"""Widget template generator for VFWidgets."""

import argparse
import sys
from pathlib import Path
from typing import Any


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    components = snake_str.split("_")
    return "".join(x.title() for x in components)


def create_widget_structure(
    widget_name: str, author: str = "VFWidgets Team", email: str = "vfwidgets@example.com"
) -> None:
    """Create a new widget from the template.

    Args:
        widget_name: Name of the widget (snake_case)
        author: Author name for pyproject.toml
        email: Email for pyproject.toml
    """
    # Validate widget name
    if not widget_name.replace("_", "").isalnum():
        print(
            f"Error: Widget name '{widget_name}' should only contain letters, numbers, and underscores."
        )
        sys.exit(1)

    # Get paths
    root_dir = Path(__file__).parent.parent
    widget_dir = root_dir / "widgets" / f"{widget_name}_widget"
    package_name = f"vfwidgets_{widget_name}"
    class_name = to_camel_case(widget_name) + "Widget"

    # Check if widget already exists
    if widget_dir.exists():
        print(f"Error: Widget '{widget_name}_widget' already exists at {widget_dir}")
        sys.exit(1)

    print(f"Creating widget: {widget_name}_widget")
    print(f"Package name: {package_name}")
    print(f"Class name: {class_name}")

    # Create directory structure
    dirs = [
        widget_dir,
        widget_dir / "src" / package_name,
        widget_dir / "src" / package_name / "resources",
        widget_dir / "src" / package_name / "resources" / "icons",
        widget_dir / "src" / package_name / "resources" / "styles",
        widget_dir / "tests",
        widget_dir / "examples",
        widget_dir / "docs",
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path.relative_to(root_dir)}")

    # Template variables
    template_vars: dict[str, Any] = {
        "widget_name": widget_name,
        "package_name": package_name,
        "class_name": class_name,
        "author": author,
        "email": email,
    }

    # Create pyproject.toml
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vfwidgets-{widget_name}"
version = "0.1.0"
description = "PySide6 {widget_name} widget for VFWidgets collection"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [
    {{name = "{author}", email = "{email}"}}
]
dependencies = [
    "PySide6>=6.9.0",
    # Uncomment to use shared utilities:
    # "vfwidgets-common @ file://../../shared/vfwidgets_common"
]
keywords = ["pyside6", "qt", "widget", "gui", "{widget_name}"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-qt>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
{package_name} = [
    "py.typed",
    "resources/icons/*",
    "resources/styles/*",
]

[tool.pyside6-project]
files = [
    "src/{package_name}/*.py",
]
""".format(**template_vars)

    (widget_dir / "pyproject.toml").write_text(pyproject_content)

    # Create README.md
    readme_content = """# VFWidgets {class_name}

A custom PySide6 {widget_name} widget for the VFWidgets collection.

## Installation

```bash
# Install from local path
pip install ./widgets/{widget_name}_widget

# Install in editable mode for development
pip install -e ./widgets/{widget_name}_widget

# Install with development dependencies
pip install -e "./widgets/{widget_name}_widget[dev]"
```

## Usage

```python
from PySide6.QtWidgets import QApplication
from {package_name} import {class_name}

app = QApplication([])

widget = {class_name}()
widget.show()

app.exec()
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Development

```bash
# Run tests
cd widgets/{widget_name}_widget
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## API Documentation

See [API documentation](docs/api.md) for detailed usage.

## Examples

Check the `examples/` directory for usage examples:
- `basic_usage.py` - Simple usage example
- `advanced_features.py` - Advanced features demonstration

## License

MIT License - See LICENSE file for details.
""".format(**template_vars)

    (widget_dir / "README.md").write_text(readme_content)

    # Create LICENSE
    license_content = """MIT License

Copyright (c) 2025 {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".format(**template_vars)

    (widget_dir / "LICENSE").write_text(license_content)

    # Create requirements.txt
    requirements_content = """# Core dependencies for vfwidgets-{widget_name}
PySide6>=6.9.0
# Add widget-specific dependencies here
""".format(**template_vars)

    (widget_dir / "requirements.txt").write_text(requirements_content)

    # Create requirements-dev.txt
    requirements_dev_content = """# Development dependencies for vfwidgets-{widget_name}
-r requirements.txt

# Testing
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-cov>=4.0.0

# Code quality
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
""".format(**template_vars)

    (widget_dir / "requirements-dev.txt").write_text(requirements_dev_content)

    # Create __init__.py
    init_content = '''"""{class_name} - A custom PySide6 widget."""

__version__ = "0.1.0"

from .{widget_name} import {class_name}

__all__ = ["{class_name}"]
'''.format(**template_vars)

    (widget_dir / "src" / package_name / "__init__.py").write_text(init_content)

    # Create main widget file
    widget_content = '''"""Implementation of {class_name}."""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

# Uncomment to use base class:
# from vfwidgets_common import VFBaseWidget


class {class_name}(QWidget):  # or VFBaseWidget if using common
    """Custom {widget_name} widget.

    Signals:
        value_changed: Emitted when the widget value changes
    """

    # Define custom signals
    value_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the {class_name}.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)

        # Example content
        self.label = QLabel("{class_name} Widget")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Set some default styling
        self.setStyleSheet("""
            QLabel {{
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)

    def set_value(self, value: object) -> None:
        """Set the widget value.

        Args:
            value: The new value
        """
        # Implementation here
        self.value_changed.emit(value)

    def get_value(self) -> object:
        """Get the current widget value.

        Returns:
            The current value
        """
        # Implementation here
        return None
'''.format(**template_vars)

    (widget_dir / "src" / package_name / f"{widget_name}.py").write_text(widget_content)

    # Create py.typed marker
    (widget_dir / "src" / package_name / "py.typed").write_text("")

    # Create test file
    test_content = '''"""Tests for {class_name}."""

import pytest
from PySide6.QtWidgets import QApplication
from {package_name} import {class_name}


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
    widget = {class_name}()
    qtbot.addWidget(widget)
    return widget


def test_widget_creation(widget):
    """Test widget can be created."""
    assert widget is not None
    assert isinstance(widget, {class_name})


def test_widget_signals(widget, qtbot):
    """Test widget signals."""
    with qtbot.waitSignal(widget.value_changed, timeout=100):
        widget.set_value("test")


def test_widget_value(widget):
    """Test widget value get/set."""
    test_value = "test_value"
    widget.set_value(test_value)
    # Implement actual value checking based on widget logic
    # assert widget.get_value() == test_value
'''.format(**template_vars)

    (widget_dir / "tests" / f"test_{widget_name}.py").write_text(test_content)
    (widget_dir / "tests" / "__init__.py").write_text("")

    # Create basic example
    example_content = '''#!/usr/bin/env python3
"""Basic usage example for {class_name}."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from {package_name} import {class_name}


def main():
    """Run the example application."""
    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("{class_name} Example")
    window.resize(400, 300)

    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Create layout
    layout = QVBoxLayout(central_widget)

    # Create and add our custom widget
    custom_widget = {class_name}()
    layout.addWidget(custom_widget)

    # Connect signals
    custom_widget.value_changed.connect(lambda v: print(f"Value changed: {{v}}"))

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''.format(**template_vars)

    (widget_dir / "examples" / "basic_usage.py").write_text(example_content)

    # Create advanced example
    advanced_content = '''#!/usr/bin/env python3
"""Advanced features example for {class_name}."""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QHBoxLayout, QWidget, QPushButton, QLabel
)
from {package_name} import {class_name}


class ExampleWindow(QMainWindow):
    """Example window demonstrating advanced features."""

    def __init__(self):
        """Initialize the example window."""
        super().__init__()
        self.setWindowTitle("{class_name} - Advanced Example")
        self.resize(600, 400)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Add custom widget
        self.custom_widget = {class_name}()
        layout.addWidget(self.custom_widget)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Add controls
        self.status_label = QLabel("Status: Ready")
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        update_btn = QPushButton("Update Widget")
        update_btn.clicked.connect(self.update_widget)
        control_layout.addWidget(update_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_widget)
        control_layout.addWidget(reset_btn)

        layout.addWidget(control_panel)

        # Connect signals
        self.custom_widget.value_changed.connect(self.on_value_changed)

    def update_widget(self):
        """Update the widget with new data."""
        self.custom_widget.set_value("Updated Value")
        self.status_label.setText("Status: Updated")

    def reset_widget(self):
        """Reset the widget to default state."""
        self.custom_widget.set_value(None)
        self.status_label.setText("Status: Reset")

    def on_value_changed(self, value):
        """Handle value changed signal."""
        print(f"Widget value changed to: {{value}}")
        self.status_label.setText(f"Status: Value = {{value}}")


def main():
    """Run the example application."""
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''.format(**template_vars)

    (widget_dir / "examples" / "advanced_features.py").write_text(advanced_content)

    # Create API documentation
    api_doc = '''# {class_name} API Documentation

## Class: `{class_name}`

### Description
Custom PySide6 widget for [describe purpose].

### Inheritance
- `QWidget` (or `VFBaseWidget` if using common utilities)

### Signals

#### `value_changed(value: object)`
Emitted when the widget value changes.

**Parameters:**
- `value`: The new value of the widget

### Methods

#### `__init__(parent: Optional[QWidget] = None)`
Initialize the widget.

**Parameters:**
- `parent`: Parent widget (optional)

#### `set_value(value: object) -> None`
Set the widget value.

**Parameters:**
- `value`: The value to set

#### `get_value() -> object`
Get the current widget value.

**Returns:**
- The current value of the widget

### Usage Example

```python
from {package_name} import {class_name}

widget = {class_name}()
widget.set_value("Hello")
current_value = widget.get_value()

# Connect to signal
widget.value_changed.connect(on_value_changed)
```

### Styling

The widget can be styled using Qt stylesheets:

```python
widget.setStyleSheet("""
    {class_name} {{
        background-color: #f0f0f0;
        border: 1px solid #ccc;
    }}
""")
```

### Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| value | object | The widget value | None |

### Events

The widget responds to standard Qt events and can be subclassed to handle custom events.
'''.format(**template_vars)

    (widget_dir / "docs" / "api.md").write_text(api_doc)

    # Create usage documentation
    usage_doc = '''# {class_name} Usage Guide

## Installation

```bash
pip install vfwidgets-{widget_name}
```

## Basic Usage

### Simple Example

```python
from PySide6.QtWidgets import QApplication
from {package_name} import {class_name}

app = QApplication([])

widget = {class_name}()
widget.show()

app.exec()
```

### Integration with Existing UI

```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from {package_name} import {class_name}

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Add our custom widget
        custom_widget = {class_name}()
        layout.addWidget(custom_widget)
```

## Advanced Usage

### Customizing Appearance

```python
widget = {class_name}()
widget.setStyleSheet("""
    /* Custom styles here */
""")
```

### Handling Signals

```python
def on_value_changed(value):
    print(f"New value: {{value}}")

widget = {class_name}()
widget.value_changed.connect(on_value_changed)
```

## Common Patterns

### Pattern 1: Data Binding

```python
# Bind widget to data model
widget.value_changed.connect(model.update_data)
model.data_changed.connect(widget.set_value)
```

### Pattern 2: Validation

```python
def validate_and_set(value):
    if is_valid(value):
        widget.set_value(value)
    else:
        show_error("Invalid value")
```

## Troubleshooting

### Issue: Widget not displaying
- Ensure QApplication is created before widget
- Check parent widget and layout

### Issue: Signals not connecting
- Verify signal signature matches slot
- Check for typos in signal names

## Best Practices

1. Always handle widget cleanup in parent destructors
2. Use type hints for better IDE support
3. Connect to signals before setting initial values
4. Test widget in isolation before integration
'''.format(**template_vars)

    (widget_dir / "docs" / "usage.md").write_text(usage_doc)

    print(f"\n✅ Widget '{widget_name}_widget' created successfully!")
    print("\nNext steps:")
    print(f"1. cd widgets/{widget_name}_widget")
    print("2. pip install -e .[dev]")
    print(f"3. Implement your widget logic in src/{package_name}/{widget_name}.py")
    print("4. Run tests: pytest")
    print("5. Try the example: python examples/basic_usage.py")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create a new VFWidget from template")
    parser.add_argument(
        "widget_name", help="Name of the widget (snake_case, e.g., 'button' or 'custom_dialog')"
    )
    parser.add_argument("--author", default="VFWidgets Team", help="Author name for pyproject.toml")
    parser.add_argument("--email", default="vfwidgets@example.com", help="Email for pyproject.toml")

    args = parser.parse_args()

    # Remove _widget suffix if provided
    widget_name = args.widget_name
    if widget_name.endswith("_widget"):
        widget_name = widget_name[:-7]

    create_widget_structure(widget_name, args.author, args.email)


if __name__ == "__main__":
    main()
