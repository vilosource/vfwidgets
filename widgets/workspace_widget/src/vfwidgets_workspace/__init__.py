"""VFWidgets Workspace - Multi-folder workspace widget for PySide6.

A VS Code-style workspace widget with multi-folder support, session persistence,
file filtering, and extensive customization options.
"""

__version__ = "0.1.0"

# Core data structures
from .models import (
    FileInfo,
    WorkspaceConfig,
    WorkspaceFolder,
    WorkspaceSession,
)

# Protocols for customization
from .protocols import (
    ContextMenuProvider,
    ErrorHandler,
    ErrorSeverity,
    FileConflictAction,
    FileConflictHandler,
    IconProvider,
    ValidationResult,
    WorkspaceLifecycleHooks,
    WorkspaceValidator,
)

# Main widget
from .workspace_widget import WorkspaceWidget

__all__ = [
    # Version
    "__version__",
    # Data models
    "FileInfo",
    "WorkspaceFolder",
    "WorkspaceConfig",
    "WorkspaceSession",
    # Main widget
    "WorkspaceWidget",
    # Protocols
    "FileConflictHandler",
    "FileConflictAction",
    "ErrorHandler",
    "ErrorSeverity",
    "IconProvider",
    "WorkspaceValidator",
    "ValidationResult",
    "ContextMenuProvider",
    "WorkspaceLifecycleHooks",
]
