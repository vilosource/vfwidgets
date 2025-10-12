"""Toolbar builder for VFTheme Studio."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QComboBox, QLabel, QToolBar


def create_toolbar(parent) -> QToolBar:
    """Create and configure the main toolbar.

    Args:
        parent: Parent window

    Returns:
        Configured QToolBar
    """
    toolbar = QToolBar("Main Toolbar", parent)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
    toolbar.setIconSize(QSize(24, 24))

    # Group 1: File operations
    toolbar.addAction("New", lambda: parent.new_theme())
    toolbar.addAction("Open", lambda: parent.open_theme())
    toolbar.addAction("Save", lambda: parent.save_theme())

    toolbar.addSeparator()

    # Group 2: Edit operations
    toolbar.addAction("Undo", lambda: print("Undo (stub)"))
    toolbar.addAction("Redo", lambda: print("Redo (stub)"))

    toolbar.addSeparator()

    # Group 3: Theme operations
    toolbar.addAction("Validate", lambda: print("Validate (stub)"))
    toolbar.addAction("Export", lambda: print("Export (stub)"))

    toolbar.addSeparator()

    # Group 4: Zoom control
    zoom_label = QLabel("Zoom:")
    toolbar.addWidget(zoom_label)

    zoom_combo = QComboBox()
    zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%", "150%", "200%", "400%"])
    zoom_combo.setCurrentText("100%")
    zoom_combo.setEditable(True)
    zoom_combo.currentTextChanged.connect(lambda text: print(f"Zoom: {text} (stub)"))
    toolbar.addWidget(zoom_combo)

    # Store zoom combo for later access
    parent._zoom_combo = zoom_combo

    return toolbar
