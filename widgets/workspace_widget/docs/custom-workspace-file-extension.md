# Custom Workspace File Extensions

WorkspaceWidget allows applications to configure their own workspace file extension, making workspace files app-specific and easily recognizable.

## Overview

By default, WorkspaceWidget uses `.workspace` for portable workspace files. However, applications can override this to use their own extension (e.g., `.reamde`, `.viloxterm`, `.myapp`).

## API

### WorkspaceWidget Configuration

```python
from vfwidgets_workspace import WorkspaceWidget

# Configure custom extension when creating WorkspaceWidget
workspace = WorkspaceWidget(
    workspace_file_extension=".reamde",           # File extension
    workspace_file_type_name="Reamde Workspace Files",  # Human-readable name
    parent=window
)
```

### WorkspaceManager Methods

Once configured, the workspace manager provides convenient methods for file dialogs:

```python
manager = workspace._manager

# Get configured extension
extension = manager.get_workspace_file_extension()
# Returns: ".reamde"

# Get human-readable type name
type_name = manager.get_workspace_file_type_name()
# Returns: "Reamde Workspace Files"

# Get complete file dialog filter string
file_filter = manager.get_file_dialog_filter()
# Returns: "Reamde Workspace Files (*.reamde);;All Files (*)"
```

## Complete Example: Reamde

Here's how Reamde (a markdown viewer app) uses custom workspace file extensions:

```python
from pathlib import Path
from PySide6.QtWidgets import QFileDialog
from vfwidgets_workspace import WorkspaceWidget

class ReamdeWorkspaceManager:
    def __init__(self, window):
        # Configure WorkspaceWidget with .reamde extension
        self.workspace_widget = WorkspaceWidget(
            file_extensions=[".md", ".markdown"],  # Filter markdown files
            workspace_file_extension=".reamde",    # Custom extension
            workspace_file_type_name="Reamde Workspace Files",
            parent=window
        )

    def save_workspace_file(self):
        """Save workspace with custom extension."""
        manager = self.workspace_widget._manager

        # Get file dialog filter from manager
        file_filter = manager.get_file_dialog_filter()
        extension = manager.get_workspace_file_extension()

        # Show Save dialog with correct extension
        file_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Workspace File",
            str(Path.home() / f"workspace{extension}"),
            file_filter
        )

        if file_path:
            manager.save_workspace_file(Path(file_path))

    def load_workspace_file(self):
        """Load workspace with custom extension."""
        manager = self.workspace_widget._manager

        # Get file dialog filter from manager
        file_filter = manager.get_file_dialog_filter()

        # Show Open dialog with correct extension filter
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open Workspace File",
            str(Path.home()),
            file_filter
        )

        if file_path:
            manager.load_workspace_file(Path(file_path))
```

## File Dialog Integration

The `get_file_dialog_filter()` method returns a properly formatted Qt file dialog filter string:

```python
# Default (.workspace)
"Workspace Files (*.workspace);;All Files (*)"

# Reamde (.reamde)
"Reamde Workspace Files (*.reamde);;All Files (*)"

# ViloxTerm (.viloxterm)
"ViloxTerm Workspace Files (*.viloxterm);;All Files (*)"
```

This ensures:
- File dialogs show the correct extension in the filter dropdown
- Default filenames use the correct extension
- Users can easily identify which app a workspace file belongs to

## Benefits

1. **App Identity**: Workspace files are clearly associated with your app
2. **File Organization**: Users can organize `.reamde` files separately from `.viloxterm` files
3. **Git Integration**: Different extensions allow different `.gitignore` rules
4. **Sharing**: Workspace files can be shared with clear app association

## Best Practices

1. **Use app name in extension**: `.reamde`, `.viloxterm` (not `.ws` or `.workspace`)
2. **Include app name in type name**: "Reamde Workspace Files" (not "Workspace Files")
3. **Always use lowercase**: `.reamde` (not `.Reamde` or `.REAMDE`)
4. **Keep it short**: 5-10 characters is ideal

## Migration from Generic `.workspace`

If your app previously used the default `.workspace` extension:

1. Update `WorkspaceWidget` initialization with new parameters
2. Update all file dialogs to use `get_file_dialog_filter()`
3. Update tooltips/documentation to mention the new extension
4. Consider supporting both extensions during a transition period

Example transition code:

```python
# Support both .myapp and .workspace during migration
file_filter = (
    "MyApp Workspace Files (*.myapp *.workspace);;"
    "All Files (*)"
)
```

## See Also

- [Portable Workspace Files](portable-workspace-files.md)
- [WorkspaceWidget API Reference](api-reference.md)
- [Example: Reamde Integration](../../../apps/reamde/src/reamde/workspace_manager.py)
