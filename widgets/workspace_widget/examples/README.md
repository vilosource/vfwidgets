# WorkspaceWidget Examples

Progressive examples demonstrating the WorkspaceWidget API.

## Quick Start

Run any example:
```bash
python examples/01_basic_single_folder.py
```

## Example Index

| # | File | Demonstrates | Complexity |
|---|------|--------------|------------|
| 01 | `01_basic_single_folder.py` | Open folder, handle selection | ⭐ Basic |
| 02 | `02_multi_folder_workspace.py` | Multi-folder config | ⭐ Basic |
| 03 | `03_file_filtering.py` | Extension/callback filters | ⭐⭐ Intermediate |
| 04 | `04_session_persistence.py` | Save/restore UI state | ⭐⭐ Intermediate |
| 05 | `05_file_navigation.py` | reveal, highlight, find | ⭐⭐ Intermediate |
| 06 | `06_tab_integration.py` | Tab widget sync | ⭐⭐ Intermediate |

## Learning Path

**Beginners:** Start with 01-03
**Intermediate:** Continue with 04-06

## Requirements

```bash
# Install workspace widget in development mode
cd ..
pip install -e .
```

## Running Examples

From the widget root directory:
```bash
python examples/01_basic_single_folder.py
python examples/02_multi_folder_workspace.py
python examples/03_file_filtering.py
python examples/04_session_persistence.py
python examples/05_file_navigation.py
python examples/06_tab_integration.py
```

## API Documentation

See `../SPECIFICATION.md` and `../DESIGN.md` for complete documentation.
