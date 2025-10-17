# ViloWeb Installation Guide

## Quick Install (VFWidgets Monorepo)

Since ViloWeb is part of the VFWidgets monorepo, you need to install its dependencies first.

### Step 1: Install vfwidgets-webview

```bash
cd widgets/webview_widget
pip install -e .
```

This installs the browser widget that ViloWeb uses.

### Step 2: Install ViloWeb

```bash
cd ../../apps/viloweb
pip install -e .
```

### Step 3: Verify Installation

```bash
# Check that viloweb command is available
which viloweb

# Verify imports work
python -c "from viloweb import main; print('✓ ViloWeb installed successfully')"
```

## Development Installation

If you want to run tests and contribute:

```bash
cd apps/viloweb
pip install -e ".[dev]"
```

This adds development dependencies:
- pytest (testing framework)
- pytest-qt (Qt testing plugin)
- black (code formatter)
- ruff (linter)
- mypy (type checker)

## Dependencies

ViloWeb requires:

**Required**:
- Python 3.9+
- PySide6 >= 6.9.0
- vfwidgets-webview >= 0.2.0
- vfwidgets-common

**Optional**:
- vfwidgets-theme-system (for theme support)

All dependencies are automatically installed by pip.

## Running ViloWeb

After installation, you can run ViloWeb in three ways:

### 1. Via Entry Point Command

```bash
viloweb
```

### 2. As Python Module

```bash
python -m viloweb
```

### 3. Via Examples

```bash
cd apps/viloweb
python examples/01_basic_browser.py
```

## Troubleshooting

### Error: "No matching distribution found for vfwidgets-webview"

**Solution**: Install vfwidgets-webview first (Step 1 above).

```bash
cd widgets/webview_widget
pip install -e .
```

### Error: "Segmentation fault" on launch

**Solution**: This is due to Qt WebEngine sandboxing. ViloWeb automatically disables sandboxing for development, but if you still see this:

```bash
export QTWEBENGINE_DISABLE_SANDBOX=1
viloweb
```

### Error: "Could not parse application stylesheet"

**Solution**: This is a warning from theme system, not an error. ViloWeb will continue with system theme. To fix:

1. Ensure vfwidgets-theme-system is installed
2. The theme system will automatically be detected and used

### Module not found errors

**Solution**: Ensure you're in the VFWidgets monorepo root and dependencies are installed:

```bash
# Check you're in the right place
pwd  # Should end with /vfwidgets

# Reinstall dependencies
cd widgets/webview_widget && pip install -e .
cd ../../apps/viloweb && pip install -e .
```

## Uninstallation

```bash
pip uninstall viloweb vfwidgets-webview
```

## Testing Installation

Run the test suite to verify everything works:

```bash
cd apps/viloweb
pytest
```

Expected output:
```
============================== 46 passed in 0.53s ==============================
```

Run example to verify GUI works:

```bash
python examples/03_bookmark_management.py
```

Expected: All demos pass successfully.

## Platform-Specific Notes

### Linux

No special requirements. Qt WebEngine sandboxing is automatically disabled for development.

### WSL (Windows Subsystem for Linux)

WSL is detected automatically by vfwidgets-common. Software rendering is enabled automatically.

### macOS

Standard installation should work. Qt WebEngine sandboxing may require additional configuration.

### Windows

Native Windows installation should work with standard Python + PySide6.

## Next Steps

After installation:

1. Read the [README.md](README.md) for usage guide
2. Try examples in `examples/` directory
3. Read code comments (highly educational)
4. Check [IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md) for architecture details
