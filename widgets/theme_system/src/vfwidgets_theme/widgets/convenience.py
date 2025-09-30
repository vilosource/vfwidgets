"""Convenience themed widget classes.

This module provides ready-to-use themed widget classes that combine ThemedWidget
with common Qt base classes, eliminating the need for multiple inheritance.

These classes simplify the API for users who want a single-inheritance approach:
- ThemedQWidget: Themed QWidget (most common use case)
- ThemedMainWindow: Themed QMainWindow for applications
- ThemedDialog: Themed QDialog for dialogs

Old API (multiple inheritance - still supported):
    class MyWidget(ThemedWidget, QWidget):
        pass

New API (single inheritance - easier):
    class MyWidget(ThemedQWidget):
        pass

Both approaches work identically and provide full theming capabilities.
"""

from typing import Optional

try:
    from PySide6.QtWidgets import QWidget, QMainWindow, QDialog
    QT_AVAILABLE = True
except ImportError:
    # Fallback for testing without Qt
    QT_AVAILABLE = False

    class QWidget:
        """Fallback QWidget for testing."""
        def __init__(self, parent=None):
            pass

    class QMainWindow:
        """Fallback QMainWindow for testing."""
        def __init__(self, parent=None):
            pass

    class QDialog:
        """Fallback QDialog for testing."""
        def __init__(self, parent=None):
            pass

from .base import ThemedWidget


class ThemedQWidget(ThemedWidget, QWidget):
    """A QWidget with built-in theming support.

    This is a convenience class that combines ThemedWidget and QWidget
    in the correct order, eliminating the need for multiple inheritance.

    Usage:
        # Simple way - single inheritance
        class MyWidget(ThemedQWidget):
            def __init__(self):
                super().__init__()
                # Your widget code here

        # Old way - still works but more complex
        class MyWidget(ThemedWidget, QWidget):
            def __init__(self):
                super().__init__()
                # Your widget code here

    Both approaches are equivalent and provide full theming capabilities.
    ThemedQWidget is simply more convenient and less error-prone.

    All ThemedWidget features are available:
    - self.theme property for accessing theme values
    - Automatic theme updates
    - Smart defaults for colors, fonts, etc.
    - Theme property caching
    """

    def __init__(self, parent: Optional[QWidget] = None, **kwargs):
        """Initialize themed QWidget.

        Args:
            parent: Parent widget (optional)
            **kwargs: Additional arguments passed to parent classes

        """
        super().__init__(parent=parent, **kwargs)


class ThemedMainWindow(ThemedWidget, QMainWindow):
    """A QMainWindow with built-in theming support.

    This is a convenience class that combines ThemedWidget and QMainWindow
    in the correct order, perfect for application main windows.

    Usage:
        class MyMainWindow(ThemedMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("My App")
                # Your main window code here

    All ThemedWidget features are available:
    - self.theme property for accessing theme values
    - Automatic theme updates
    - Smart defaults for colors, fonts, etc.
    - Theme property caching

    Plus all QMainWindow features:
    - setCentralWidget, setMenuBar, setStatusBar, etc.
    - Dock widgets, toolbars, etc.
    """

    def __init__(self, parent: Optional[QWidget] = None, **kwargs):
        """Initialize themed QMainWindow.

        Args:
            parent: Parent widget (optional)
            **kwargs: Additional arguments passed to parent classes

        """
        super().__init__(parent=parent, **kwargs)


class ThemedDialog(ThemedWidget, QDialog):
    """A QDialog with built-in theming support.

    This is a convenience class that combines ThemedWidget and QDialog
    in the correct order, perfect for dialog windows.

    Usage:
        class MyDialog(ThemedDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("My Dialog")
                # Your dialog code here

    All ThemedWidget features are available:
    - self.theme property for accessing theme values
    - Automatic theme updates
    - Smart defaults for colors, fonts, etc.
    - Theme property caching

    Plus all QDialog features:
    - exec(), accept(), reject()
    - Modal/modeless operation
    - Dialog button boxes, etc.
    """

    def __init__(self, parent: Optional[QWidget] = None, **kwargs):
        """Initialize themed QDialog.

        Args:
            parent: Parent widget (optional)
            **kwargs: Additional arguments passed to parent classes

        """
        super().__init__(parent=parent, **kwargs)


__all__ = [
    "ThemedQWidget",
    "ThemedMainWindow",
    "ThemedDialog",
]