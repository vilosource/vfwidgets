#!/usr/bin/env python3
"""
grid_layout.py - Themed grid layout with themed cells

Shows how to create grid layouts that respond to theme changes with
consistent cell styling, spacing, and responsive behavior.

Key Concepts:
- Grid layout theming
- Cell styling
- Responsive design
- Dynamic content
- Layout spacing

Example usage:
    python grid_layout.py
"""

import random
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedGridCell(ThemedWidget, QFrame):
    """A themed cell for grid layouts."""

    theme_config = {
        "bg": "grid.cell.background",
        "fg": "grid.cell.foreground",
        "border": "grid.cell.border",
        "hover_bg": "grid.cell.hover.background",
        "selected_bg": "grid.cell.selected.background",
        "selected_fg": "grid.cell.selected.foreground",
        "font": "grid.cell.font",
    }

    def __init__(self, content="", cell_type="normal", parent=None):
        super().__init__(parent)
        self._cell_type = cell_type
        self._is_selected = False
        self._is_hovered = False

        # Set up the cell
        self.setFrameStyle(QFrame.Box)
        self.setMinimumSize(80, 60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Content label
        self.content_label = QLabel(content)
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)
        layout.addWidget(self.content_label)

        # Type indicator
        if cell_type != "normal":
            type_label = QLabel(f"[{cell_type.title()}]")
            type_label.setAlignment(Qt.AlignCenter)
            type_label.setStyleSheet("font-size: 9px; font-style: italic;")
            layout.addWidget(type_label)

        # Apply initial styling
        self.update_styling()

    def on_theme_changed(self):
        """Called automatically when theme changes."""
        self.update_styling()

    def set_selected(self, selected):
        """Set the selection state."""
        self._is_selected = selected
        self.update_styling()

    def set_content(self, content):
        """Set the cell content."""
        self.content_label.setText(content)

    def set_cell_type(self, cell_type):
        """Set the cell type."""
        self._cell_type = cell_type
        self.update_styling()

    def update_styling(self):
        """Update cell styling based on theme and state."""
        # Get base theme colors
        bg_color = self.theme.get("bg", "#ffffff")
        fg_color = self.theme.get("fg", "#000000")
        border_color = self.theme.get("border", "#cccccc")
        hover_bg = self.theme.get("hover_bg", "#f0f0f0")
        selected_bg = self.theme.get("selected_bg", "#0066cc")
        selected_fg = self.theme.get("selected_fg", "#ffffff")
        font = self.theme.get("font", "Arial, sans-serif")

        # Determine colors based on state and type
        if self._is_selected:
            current_bg = selected_bg
            current_fg = selected_fg
        elif self._is_hovered:
            current_bg = hover_bg
            current_fg = fg_color
        else:
            current_bg = bg_color
            current_fg = fg_color

        # Modify colors based on cell type
        if self._cell_type == "header":
            current_bg = self.theme.get("grid.header.background", "#e0e0e0")
            current_fg = self.theme.get("grid.header.foreground", "#000000")
        elif self._cell_type == "important":
            border_color = self.theme.get("accent.primary", "#ff6600")
        elif self._cell_type == "disabled":
            current_bg = self.theme.get("surface.disabled", "#f5f5f5")
            current_fg = self.theme.get("text.disabled", "#999999")

        # Generate stylesheet
        stylesheet = f"""
        QFrame {{
            background-color: {current_bg};
            color: {current_fg};
            border: 2px solid {border_color};
            border-radius: 6px;
            font-family: {font};
        }}

        QLabel {{
            background-color: transparent;
            color: {current_fg};
            border: none;
        }}
        """

        self.setStyleSheet(stylesheet)

    def enterEvent(self, event):
        """Handle mouse enter event."""
        self._is_hovered = True
        self.update_styling()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self._is_hovered = False
        self.update_styling()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            self.set_selected(not self._is_selected)
        super().mousePressEvent(event)


class DynamicGrid(ThemedWidget):
    """A dynamic grid that can add/remove cells."""

    def __init__(self, rows=3, cols=4, parent=None):
        super().__init__(parent)
        self._rows = rows
        self._cols = cols
        self._cells = []

        self.setup_ui()
        self.populate_grid()

    def setup_ui(self):
        """Set up the grid UI."""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        add_btn = QPushButton("Add Cell")
        add_btn.clicked.connect(self.add_random_cell)
        controls_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_cells)
        controls_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_grid)
        controls_layout.addWidget(clear_btn)

        randomize_btn = QPushButton("Randomize")
        randomize_btn.clicked.connect(self.randomize_content)
        controls_layout.addWidget(randomize_btn)

        layout.addLayout(controls_layout)

        # Scroll area for grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Grid widget
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)

        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)

        # Status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def populate_grid(self):
        """Populate the grid with initial cells."""
        self.clear_grid()

        cell_contents = [
            "Header",
            "Data 1",
            "Data 2",
            "Data 3",
            "Row 2",
            "Value A",
            "Value B",
            "Value C",
            "Row 3",
            "Item X",
            "Item Y",
            "Item Z",
        ]

        cell_types = [
            "header",
            "normal",
            "normal",
            "normal",
            "header",
            "normal",
            "important",
            "normal",
            "header",
            "normal",
            "normal",
            "disabled",
        ]

        for row in range(self._rows):
            for col in range(self._cols):
                index = row * self._cols + col
                if index < len(cell_contents):
                    content = cell_contents[index]
                    cell_type = cell_types[index] if index < len(cell_types) else "normal"
                else:
                    content = f"Cell {row},{col}"
                    cell_type = "normal"

                cell = ThemedGridCell(content, cell_type)
                self._cells.append(cell)
                self.grid_layout.addWidget(cell, row, col)

        self.update_status()

    def add_random_cell(self):
        """Add a new cell at a random position."""
        # Find empty position or expand grid
        max_row = max_col = 0
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item:
                pos = self.grid_layout.getItemPosition(i)
                max_row = max(max_row, pos[0])
                max_col = max(max_col, pos[1])

        # Add to next available position
        row = max_row if max_col >= self._cols - 1 else max_row
        col = (max_col + 1) % self._cols
        if col == 0 and max_col >= self._cols - 1:
            row += 1

        contents = ["New Cell", "Added", "Dynamic", "Content", "Random"]
        types = ["normal", "important", "header"]

        content = random.choice(contents)
        cell_type = random.choice(types)

        cell = ThemedGridCell(f"{content} {len(self._cells) + 1}", cell_type)
        self._cells.append(cell)
        self.grid_layout.addWidget(cell, row, col)

        self.update_status()

    def remove_selected_cells(self):
        """Remove all selected cells."""
        cells_to_remove = [cell for cell in self._cells if cell._is_selected]

        for cell in cells_to_remove:
            self.grid_layout.removeWidget(cell)
            self._cells.remove(cell)
            cell.deleteLater()

        self.update_status()

    def clear_grid(self):
        """Clear all cells from the grid."""
        for cell in self._cells:
            self.grid_layout.removeWidget(cell)
            cell.deleteLater()

        self._cells.clear()
        self.update_status()

    def randomize_content(self):
        """Randomize the content of all cells."""
        contents = [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Data",
            "Info",
            "Value",
            "Item",
            "Element",
            "Content",
        ]
        types = ["normal", "important", "header", "disabled"]

        for cell in self._cells:
            content = random.choice(contents)
            cell_type = random.choice(types)

            cell.set_content(f"{content} {random.randint(1, 100)}")
            cell.set_cell_type(cell_type)

        self.update_status()

    def update_status(self):
        """Update the status label."""
        total = len(self._cells)
        selected = len([cell for cell in self._cells if cell._is_selected])
        self.status_label.setText(f"Grid: {total} cells, {selected} selected")


class GridLayoutDemo(ThemedWidget):
    """Demo window showing themed grid layouts."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Grid Layout Demo")
        self.setMinimumSize(900, 700)

        self.setup_ui()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Themed Grid Layout Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Create horizontal layout for two grids
        grids_layout = QHBoxLayout()

        # Static grid
        self.create_static_grid(grids_layout)

        # Dynamic grid
        self.create_dynamic_grid(grids_layout)

        layout.addLayout(grids_layout)

        # Theme controls
        self.create_theme_controls(layout)

    def create_static_grid(self, layout):
        """Create a static grid example."""
        static_layout = QVBoxLayout()

        # Title
        title = QLabel("Static Grid")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        static_layout.addWidget(title)

        # Static grid widget
        static_widget = QWidget()
        grid_layout = QGridLayout(static_widget)
        grid_layout.setSpacing(6)

        # Create a 4x4 grid with different cell types
        grid_data = [
            ("Name", "header"),
            ("Age", "header"),
            ("City", "header"),
            ("Status", "header"),
            ("Alice", "normal"),
            ("25", "normal"),
            ("New York", "normal"),
            ("Active", "important"),
            ("Bob", "normal"),
            ("30", "normal"),
            ("London", "normal"),
            ("Inactive", "disabled"),
            ("Carol", "normal"),
            ("28", "normal"),
            ("Tokyo", "normal"),
            ("Active", "important"),
        ]

        for i, (content, cell_type) in enumerate(grid_data):
            row = i // 4
            col = i % 4
            cell = ThemedGridCell(content, cell_type)
            grid_layout.addWidget(cell, row, col)

        static_layout.addWidget(static_widget)
        layout.addLayout(static_layout)

    def create_dynamic_grid(self, layout):
        """Create a dynamic grid example."""
        dynamic_layout = QVBoxLayout()

        # Title
        title = QLabel("Dynamic Grid")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        dynamic_layout.addWidget(title)

        # Dynamic grid
        self.dynamic_grid = DynamicGrid(4, 5)
        dynamic_layout.addWidget(self.dynamic_grid)

        layout.addLayout(dynamic_layout)

    def create_theme_controls(self, layout):
        """Create theme switching controls."""
        controls_layout = QHBoxLayout()

        # Theme buttons
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme("light"))
        controls_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme("dark"))
        controls_layout.addWidget(dark_btn)

        colorful_btn = QPushButton("Colorful Theme")
        colorful_btn.clicked.connect(lambda: self.switch_theme("colorful"))
        controls_layout.addWidget(colorful_btn)

        layout.addLayout(controls_layout)

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
    """Run the themed grid layout demo."""
    # Create themed application
    app = ThemedApplication(sys.argv)

    # Define themes with grid styling
    light_theme = {
        "name": "light",
        "grid": {
            "cell": {
                "background": "#ffffff",
                "foreground": "#333333",
                "border": "#cccccc",
                "hover": {"background": "#f0f0f0"},
                "selected": {"background": "#0066cc", "foreground": "#ffffff"},
                "font": "Arial, sans-serif",
            },
            "header": {"background": "#e6e6e6", "foreground": "#000000"},
        },
        "surface": {"disabled": "#f8f8f8"},
        "text": {"disabled": "#999999"},
        "accent": {"primary": "#ff6600"},
    }

    dark_theme = {
        "name": "dark",
        "grid": {
            "cell": {
                "background": "#3a3a3a",
                "foreground": "#ffffff",
                "border": "#555555",
                "hover": {"background": "#4a4a4a"},
                "selected": {"background": "#66aaff", "foreground": "#000000"},
                "font": "Arial, sans-serif",
            },
            "header": {"background": "#2a2a2a", "foreground": "#ffffff"},
        },
        "surface": {"disabled": "#2d2d2d"},
        "text": {"disabled": "#777777"},
        "accent": {"primary": "#ff8833"},
    }

    colorful_theme = {
        "name": "colorful",
        "grid": {
            "cell": {
                "background": "#fff5f0",
                "foreground": "#2d1810",
                "border": "#ffb380",
                "hover": {"background": "#ffe6d9"},
                "selected": {"background": "#ff6b35", "foreground": "#ffffff"},
                "font": "Arial, sans-serif",
            },
            "header": {"background": "#ff8c50", "foreground": "#ffffff"},
        },
        "surface": {"disabled": "#f0e6e0"},
        "text": {"disabled": "#b38060"},
        "accent": {"primary": "#ff3300"},
    }

    # Register themes
    app.register_theme("light", light_theme)
    app.register_theme("dark", dark_theme)
    app.register_theme("colorful", colorful_theme)

    # Set initial theme
    app.set_theme("light")

    # Create and show demo
    demo = GridLayoutDemo()
    demo.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
