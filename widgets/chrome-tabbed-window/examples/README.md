# ChromeTabbedWindow Examples

This directory contains example applications demonstrating various features of ChromeTabbedWindow.

## Running the Examples

All examples can be run directly from the examples directory:

```bash
python 01_basic_usage.py
python 02_frameless_chrome.py
python 03_tab_compression_demo.py
```

## Example Descriptions

### 01_basic_usage.py - Basic QTabWidget Replacement
- **Purpose**: Demonstrates that ChromeTabbedWindow is a drop-in replacement for QTabWidget
- **Features shown**:
  - Adding/removing tabs
  - Tab signals (currentChanged, tabCloseRequested)
  - All standard QTabWidget API methods
  - Embedding in a QMainWindow

### 02_frameless_chrome.py - Chrome Browser Clone
- **Purpose**: Shows frameless window mode that looks exactly like Chrome browser
- **Features shown**:
  - Frameless window (no OS title bar)
  - Custom window controls (minimize, maximize, close)
  - Chrome-style tab rendering
  - Window dragging by tab bar
  - Tab compression as tabs are added

### 03_tab_compression_demo.py - Tab Compression Visualization
- **Purpose**: Interactive demo of Chrome's tab compression behavior
- **Features shown**:
  - Dynamic tab width calculation
  - Real-time width display
  - Color-coded compression states:
    - Green: Maximum width (240px)
    - Orange: Compressed (between min and max)
    - Red: Minimum width (52px)
  - Add/remove multiple tabs at once

## Key Behaviors

### Chrome-Style Tab Compression
Unlike traditional tab widgets that use scroll buttons, ChromeTabbedWindow compresses tabs exactly like Chrome:

- **Few tabs (1-4)**: Tabs expand to maximum width (240px)
- **Medium tabs (5-15)**: Tabs compress proportionally
- **Many tabs (16+)**: Tabs compress to minimum width (52px)
- **All tabs always visible**: No scroll buttons, no hidden tabs

### Implementation Details
The correct implementation uses:
- `tabSizeHint()` override for dynamic width calculation
- `setExpanding(False)` to allow compression
- NO `tabRect()` override (uses Qt's native positioning)

See `docs/chrome-tabs-implementation-GUIDE.md` for complete technical details.

## Common Use Cases

### As a Drop-in QTabWidget Replacement
```python
# Replace this:
tabs = QTabWidget()

# With this:
tabs = ChromeTabbedWindow()
```

### As a Frameless Chrome-Style Window
```python
# Create without parent for frameless mode
chrome = ChromeTabbedWindow()
chrome.show()  # Shows as frameless window with Chrome styling
```

### In an Existing Application
```python
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = ChromeTabbedWindow(self)
        self.setCentralWidget(self.tabs)
```

## Troubleshooting

If tabs appear incorrectly sized or positioned:
1. Ensure you're using the latest version with the correct implementation
2. Check that `setExpanding(False)` is set in ChromeTabBar
3. Verify no `tabRect()` override exists in the code
4. See the implementation guide for correct approach

## Additional Resources

- [Implementation Guide](../docs/chrome-tabs-implementation-GUIDE.md)
- [API Documentation](../README.md)
- [Phase 2 Features](../PHASE2_IMPLEMENTATION_SUMMARY.md)