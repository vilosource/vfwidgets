#!/usr/bin/env python3
"""Example 05: Custom Widgets - ThemedWidget Mixin
===================================================

⭐ BRIDGE TO ADVANCED API ⭐

This example introduces ThemedWidget for the first time and explains
when and how to use it for custom widget development.

What you'll learn:
- When to use ThemedWidget (custom Qt base classes)
- How to use ThemedWidget (inheritance order matters!)
- The relationship between ThemedQWidget and ThemedWidget
- Creating themed versions of ANY Qt widget

THE PROBLEM:
Examples 01-04 used ThemedMainWindow and ThemedQWidget. But what if
you need to subclass QTextEdit, QTabWidget, or other Qt classes?

THE SOLUTION: ThemedWidget Mixin
ThemedWidget can combine with ANY Qt base class using multiple
inheritance.

INHERITANCE PATTERN:
    class MyWidget(ThemedWidget, QtBaseClass):
                   ^^^^^^^^^^^^^^^^ ThemedWidget MUST come first!

Run:
    python examples/05_custom_widgets.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import (
    ThemedApplication,
    ThemedMainWindow,
    ThemedQWidget,
    ThemedWidget,
    WidgetRole,
    set_widget_role,
)


class CodeEditor(ThemedWidget, QTextEdit):
    """Custom themed text editor.

    ⭐ FIRST USAGE OF ThemedWidget! ⭐

    WHY: We need QTextEdit's text editing capabilities, but ThemedQWidget
         only inherits from QWidget. Solution: Use ThemedWidget mixin!

    PATTERN:
        class CodeEditor(ThemedWidget, QTextEdit)
                        ^^^^^^^^^^^^ Must be first!

    WRONG:  class CodeEditor(QTextEdit, ThemedWidget)  # ❌ Won't work!
    RIGHT:  class CodeEditor(ThemedWidget, QTextEdit)  # ✅ Correct!

    This gives us:
    - QTextEdit functionality (text editing, selection, undo/redo)
    - Automatic theming from ThemedWidget
    - Access to all theme system features
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set editor role for monospace font
        set_widget_role(self, WidgetRole.EDITOR)

        # Configure editor
        self.setPlaceholderText("Type your code here...")

        # Add sample code
        self.setPlainText(
            "# This text editor is themed!\n"
            "# It uses:\n"
            "# - Monospace font (role='editor')\n"
            "# - Editor background color\n"
            "# - Editor text color\n"
            "# - Selection colors from theme\n"
            "\n"
            "def example():\n"
            "    return 'ThemedWidget + QTextEdit = Magic!'"
        )


class DocumentTabs(ThemedWidget, QTabWidget):
    """Custom themed tab widget.

    ⭐ SECOND USAGE OF ThemedWidget! ⭐

    WHY: We need QTabWidget's tab management, but again ThemedQWidget
         won't work. Use ThemedWidget mixin!

    PATTERN:
        class DocumentTabs(ThemedWidget, QTabWidget)
                          ^^^^^^^^^^^^ Same pattern!

    Once you understand this pattern, you can create themed versions of:
    - QFrame, QSplitter, QToolBar, QDockWidget
    - QListWidget, QTreeWidget, QTableWidget
    - QLineEdit, QSpinBox, QComboBox
    - ANY Qt widget class!
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configure tabs
        self.setTabsClosable(True)
        self.setMovable(True)

        # Add some demo tabs
        self.add_demo_tab("README.md", "# Welcome\n\nThis is a demo document.")
        self.add_demo_tab("main.py", "# Python file\n\nimport sys")
        self.add_demo_tab("styles.css", "/* CSS file */\nbody { margin: 0; }")

    def add_demo_tab(self, title: str, content: str):
        """Add a demo tab with an editor."""
        editor = CodeEditor()
        editor.setPlainText(content)
        self.addTab(editor, title)


class CustomWidgetsWindow(ThemedMainWindow):
    """Main window showcasing custom themed widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Widgets - ThemedWidget Mixin")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        central = ThemedQWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 Custom Widgets with ThemedWidget Mixin")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Explanation
        explanation = QGroupBox("Why ThemedWidget?")
        exp_layout = QVBoxLayout(explanation)

        exp_text = QLabel(
            "ThemedQWidget only works with QWidget base class.\n\n"
            "When you need to subclass other Qt widgets (QTextEdit, QTabWidget, etc.),\n"
            "use ThemedWidget mixin with multiple inheritance:\n\n"
            "  class MyWidget(ThemedWidget, QTextEdit):\n"
            "      ^^^^^^^^^^^^ ThemedWidget MUST come first!\n\n"
            "This is the 'advanced API' - but it's still simple!"
        )
        exp_text.setWordWrap(True)
        exp_layout.addWidget(exp_text)

        layout.addWidget(explanation)

        # Custom tab widget example
        tabs_group = QGroupBox("Example: Themed QTabWidget")
        tabs_layout = QVBoxLayout(tabs_group)

        tabs_layout.addWidget(QLabel("This QTabWidget subclass uses ThemedWidget:"))

        self.tabs = DocumentTabs()
        tabs_layout.addWidget(self.tabs)

        layout.addWidget(tabs_group)

        # Footer
        footer = QLabel(
            "💡 Key Insight:\n"
            "ThemedQWidget is just: class ThemedQWidget(ThemedWidget, QWidget)\n"
            "Now you know the full pattern and can theme ANY Qt widget!"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet("font-size: 11px; color: #888; padding: 10px;")
        layout.addWidget(footer)


def main():
    """Main entry point."""
    app = ThemedApplication(sys.argv)

    window = CustomWidgetsWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
