#!/usr/bin/env python3
"""splitter.py - Themed splitter with styled handles.

Shows how to create splitters that respond to theme changes with
consistent handle styling and responsive layouts.

Key Concepts:
- Splitter theming
- Handle styling
- Responsive layouts
- Nested splitters

Example usage:
    python splitter.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedSplitter(ThemedWidget, QSplitter):
    """A themed splitter with styled handles."""

    theme_config = {
        "bg": "splitter.background",
        "handle_bg": "splitter.handle.background",
        "handle_hover": "splitter.handle.hover",
        "handle_pressed": "splitter.handle.pressed",
    }

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setChildrenCollapsible(False)
        self.setHandleWidth(8)
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update splitter styling based on current theme."""
        bg_color = self.theme.get("bg", "#f0f0f0")
        handle_bg = self.theme.get("handle_bg", "#cccccc")
        handle_hover = self.theme.get("handle_hover", "#bbbbbb")
        handle_pressed = self.theme.get("handle_pressed", "#aaaaaa")

        stylesheet = f"""
        QSplitter {{
            background-color: {bg_color};
        }}

        QSplitter::handle {{
            background-color: {handle_bg};
            border: 1px solid {handle_bg};
        }}

        QSplitter::handle:horizontal {{
            width: 6px;
            margin: 2px 0px;
        }}

        QSplitter::handle:vertical {{
            height: 6px;
            margin: 0px 2px;
        }}

        QSplitter::handle:hover {{
            background-color: {handle_hover};
        }}

        QSplitter::handle:pressed {{
            background-color: {handle_pressed};
        }}
        """

        self.setStyleSheet(stylesheet)


class SplitterPane(ThemedWidget, QFrame):
    """A themed pane for use in splitters."""

    theme_config = {
        "bg": "splitter.pane.background",
        "fg": "splitter.pane.foreground",
        "border": "splitter.pane.border",
    }

    def __init__(self, title="Pane", content_type="text", parent=None):
        super().__init__(parent)
        self._title = title
        self._content_type = content_type
        self.setFrameStyle(QFrame.Box)
        self.setMinimumSize(100, 100)
        self.setup_ui()
        self.update_styling()

    def setup_ui(self):
        """Set up the pane UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)

        # Content based on type
        if self._content_type == "text":
            self.content_widget = QTextEdit()
            self.content_widget.setPlaceholderText(f"Content for {self._title}")
        elif self._content_type == "list":
            self.content_widget = QListWidget()
            for i in range(5):
                self.content_widget.addItem(f"{self._title} Item {i+1}")
        else:
            self.content_widget = QLabel(f"Content for {self._title}")
            self.content_widget.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.content_widget)

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def update_styling(self):
        """Update pane styling."""
        bg_color = self.theme.get("bg", "#ffffff")
        fg_color = self.theme.get("fg", "#000000")
        border_color = self.theme.get("border", "#cccccc")

        self.setStyleSheet(
            f"""
        QFrame {{
            background-color: {bg_color};
            color: {fg_color};
            border: 1px solid {border_color};
            border-radius: 4px;
        }}
        """
        )


class SplitterDemo(ThemedWidget):
    """Demo window showing themed splitters."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Splitter Demo")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Splitter Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Main splitter (vertical)
        main_splitter = ThemedSplitter(Qt.Vertical)

        # Top section with horizontal splitter
        top_splitter = ThemedSplitter(Qt.Horizontal)

        # Add panes to top splitter
        left_pane = SplitterPane("File Explorer", "list")
        center_pane = SplitterPane("Editor", "text")
        right_pane = SplitterPane("Properties", "text")

        top_splitter.addWidget(left_pane)
        top_splitter.addWidget(center_pane)
        top_splitter.addWidget(right_pane)
        top_splitter.setSizes([200, 400, 200])

        # Bottom section
        bottom_pane = SplitterPane("Console", "text")

        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_pane)
        main_splitter.setSizes([400, 200])

        layout.addWidget(main_splitter)

        # Controls
        self.create_controls(layout)

    def create_controls(self, layout):
        """Create control buttons."""
        controls_layout = QHBoxLayout()

        # Reset layout button
        reset_btn = QPushButton("Reset Layout")
        reset_btn.clicked.connect(self.reset_layout)
        controls_layout.addWidget(reset_btn)

        # Theme controls
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme("light"))
        controls_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        controls_layout.addWidget(dark_btn)

        layout.addLayout(controls_layout)

    def reset_layout(self):
        """Reset splitter sizes to defaults."""
        # This would reset the splitter sizes
        print("Layout reset")

    def switch_theme(self, theme_name):
        """Switch to a different theme."""
        app = ThemedApplication.instance()
        if app:
            try:
                app.set_theme(theme_name)
                print(f"Switched to {theme_name} theme")
            except Exception as e:
                print(f"Could not switch to {theme_name} theme: {e}")


def main():
    """Run the themed splitter demo."""
    app = ThemedApplication(sys.argv)

    # Define themes
    light_theme = {
        "name": "light",
        "splitter": {
            "background": "#f5f5f5",
            "handle": {"background": "#cccccc", "hover": "#bbbbbb", "pressed": "#aaaaaa"},
            "pane": {"background": "#ffffff", "foreground": "#000000", "border": "#dddddd"},
        },
    }

    dark_theme = {
        "name": "dark",
        "splitter": {
            "background": "#2d2d2d",
            "handle": {"background": "#555555", "hover": "#666666", "pressed": "#444444"},
            "pane": {"background": "#3a3a3a", "foreground": "#ffffff", "border": "#555555"},
        },
    }

    app.register_theme("light", light_theme)
    app.register_theme("dark", dark_theme)
    app.set_theme("light")

    demo = SplitterDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
