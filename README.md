# VFWidgets - PySide6 Qt Widgets Collection

A monorepo collection of reusable PySide6 Qt widgets, each independently installable and maintainable.

## Repository Structure

```
vfwidgets/
├── widgets/           # Individual widget packages
├── shared/           # Shared utilities and base classes
├── tools/            # Development tools and scripts
├── docs/             # Documentation and guidelines
└── .github/          # CI/CD workflows
```

## Quick Start

### Installing a Widget

Each widget can be installed independently:

```bash
# Install from local path
pip install ./widgets/button_widget

# Install in editable mode for development
pip install -e ./widgets/button_widget

# Install with development dependencies
pip install -e "./widgets/button_widget[dev]"
```

### Creating a New Widget

Use the widget generator script to create a new widget from the template:

```bash
python tools/create_widget.py my_new_widget
```

This will create a new widget package in `widgets/my_new_widget/` with the standard structure.

## Available Widgets

| Widget | Description | Status | Documentation |
|--------|-------------|--------|---------------|
| button_widget | Enhanced button with animations and styles | 🟢 Ready | [Docs](widgets/button_widget/README.md) |
| *More widgets coming soon* | | | |

## Development

### Prerequisites

- Python 3.9+
- PySide6 6.9.0+
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vfwidgets.git
cd vfwidgets
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development tools:
```bash
pip install -U pip setuptools wheel
pip install pytest pytest-qt black ruff mypy
```

4. Install a widget in development mode:
```bash
pip install -e "./widgets/button_widget[dev]"
```

### Running Tests

```bash
# Test a specific widget
cd widgets/button_widget
pytest

# Test all widgets
./tools/test_all.sh
```

### Code Quality

All widgets should follow these standards:

- **Formatting**: Black (line length 100)
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Testing**: Pytest with pytest-qt

Run checks:
```bash
black --check src/
ruff check src/
mypy src/
```

## Widget Development Guidelines

Each widget should:

1. **Be Self-Contained**: Minimal external dependencies beyond PySide6
2. **Follow Naming Convention**: `vfwidgets_<name>` for package namespace
3. **Include Documentation**: README, docstrings, and usage examples
4. **Have Tests**: Unit tests using pytest-qt
5. **Provide Examples**: Runnable example scripts in `examples/`

### Standard Widget Structure

```
widgets/my_widget/
├── pyproject.toml          # Package configuration
├── README.md              # Widget documentation
├── src/
│   └── vfwidgets_my_widget/
│       ├── __init__.py
│       ├── widget.py      # Main widget implementation
│       └── resources/     # Icons, styles, etc.
├── tests/
│   └── test_widget.py
└── examples/
    └── basic_usage.py
```

## Publishing Widgets

Widgets can be published to PyPI independently:

```bash
cd widgets/button_widget
python -m build
python -m twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

Each widget may have its own license. Check the individual widget directories for specific licensing information.

## Support

For issues, questions, or contributions, please open an issue on GitHub.