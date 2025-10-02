#!/usr/bin/env python3
"""Example 05: Complete Application with Advanced Theming.
=======================================================

A sophisticated application demonstrating all theme system features:
- Custom theme creation and loading
- Theme persistence
- Live theme editing
- Complex widget hierarchies
- Animation with theme transitions
- Theme export/import

This represents a production-ready application using the theme system.

What this demonstrates:
- Complete application architecture
- Theme management UI
- Custom theme creation
- Theme persistence
- Advanced widget integration
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemeEditor(ThemedWidget, QWidget):
    """Advanced theme editor with live preview."""

    theme_changed_signal = Signal()

    theme_config = {
        'editor_bg': 'colors.background',
        'editor_fg': 'colors.foreground',
        'editor_border': 'colors.border',
        'editor_accent': 'colors.accent'
    }

    def __init__(self):
        super().__init__()
        self.custom_theme = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Theme name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Theme Name:"))
        self.name_edit = QLineEdit("Custom Theme")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Color editor
        color_group = QGroupBox("Theme Colors")
        color_layout = QGridLayout(color_group)

        self.color_editors = {}
        colors = [
            ('Background', 'background', '#ffffff'),
            ('Foreground', 'foreground', '#000000'),
            ('Primary', 'primary', '#0066cc'),
            ('Accent', 'accent', '#00aa00'),
            ('Border', 'border', '#cccccc'),
            ('Error', 'error', '#ff0000'),
            ('Warning', 'warning', '#ffaa00'),
            ('Success', 'success', '#00aa00'),
        ]

        for i, (label, key, default) in enumerate(colors):
            color_layout.addWidget(QLabel(f"{label}:"), i, 0)

            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {default};")
            color_btn.clicked.connect(lambda checked, k=key, b=color_btn: self.pick_color(k, b))
            color_layout.addWidget(color_btn, i, 1)

            color_input = QLineEdit(default)
            color_input.textChanged.connect(lambda text, k=key, b=color_btn: self.update_color(k, text, b))
            color_layout.addWidget(color_input, i, 2)

            self.color_editors[key] = (color_btn, color_input)

        layout.addWidget(color_group)

        # Theme type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Theme Type:"))
        self.light_check = QCheckBox("Light")
        self.light_check.setChecked(True)
        type_layout.addWidget(self.light_check)
        self.dark_check = QCheckBox("Dark")
        self.dark_check.toggled.connect(lambda checked: self.light_check.setChecked(not checked))
        self.light_check.toggled.connect(lambda checked: self.dark_check.setChecked(not checked))
        type_layout.addWidget(self.dark_check)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self.apply_theme)
        button_layout.addWidget(apply_btn)

        save_btn = QPushButton("Save Theme")
        save_btn.clicked.connect(self.save_theme)
        button_layout.addWidget(save_btn)

        load_btn = QPushButton("Load Theme")
        load_btn.clicked.connect(self.load_theme)
        button_layout.addWidget(load_btn)

        layout.addLayout(button_layout)

    def pick_color(self, key, button):
        """Open color picker dialog."""
        current = button.styleSheet().split(":")[1].strip().rstrip(";")
        color = QColorDialog.getColor(QColor(current), self, f"Choose {key} color")
        if color.isValid():
            hex_color = color.name()
            button.setStyleSheet(f"background-color: {hex_color};")
            self.color_editors[key][1].setText(hex_color)

    def update_color(self, key, value, button):
        """Update color button when text changes."""
        if value.startswith('#') and len(value) == 7:
            button.setStyleSheet(f"background-color: {value};")
            self.custom_theme[key] = value

    def apply_theme(self):
        """Apply the custom theme to the application."""
        # Build theme colors
        colors = {}
        for key, (_button, input) in self.color_editors.items():
            colors[key] = input.text()

        # Create theme data
        theme_data = {
            'name': self.name_edit.text(),
            'type': 'dark' if self.dark_check.isChecked() else 'light',
            'colors': colors,
            'styles': {
                'window': {
                    'background-color': colors['background'],
                    'color': colors['foreground']
                }
            }
        }

        # Save to temp file and load
        temp_path = Path('/tmp/custom_theme.json')
        with open(temp_path, 'w') as f:
            json.dump(theme_data, f)

        app = ThemedApplication.instance()
        if app:
            app.load_theme_file(temp_path)
            app.set_theme(theme_data['name'])

    def save_theme(self):
        """Save theme to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Theme", "", "Theme Files (*.json)"
        )
        if file_path:
            colors = {}
            for key, (_button, input) in self.color_editors.items():
                colors[key] = input.text()

            theme_data = {
                'name': self.name_edit.text(),
                'type': 'dark' if self.dark_check.isChecked() else 'light',
                'colors': colors,
                'styles': {
                    'window': {
                        'background-color': colors['background'],
                        'color': colors['foreground']
                    }
                }
            }

            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)

            QMessageBox.information(self, "Success", f"Theme saved to {file_path}")

    def load_theme(self):
        """Load theme from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Theme", "", "Theme Files (*.json)"
        )
        if file_path:
            app = ThemedApplication.instance()
            if app and app.load_theme_file(file_path):
                QMessageBox.information(self, "Success", "Theme loaded successfully!")


class AnimatedWidget(ThemedWidget, QWidget):
    """Widget with animated theme transitions."""

    theme_config = {
        'widget_bg': 'colors.background',
        'widget_fg': 'colors.foreground',
        'widget_accent': 'colors.accent'
    }

    def __init__(self):
        super().__init__()
        self._animation_progress = 0
        self.old_colors = {}
        self.new_colors = {}
        self.animation = QPropertyAnimation(self, b"animation_progress")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.setup_ui()

    def get_animation_progress(self):
        return self._animation_progress

    def set_animation_progress(self, value):
        self._animation_progress = value
        self.update_animated_style()

    animation_progress = Property(int, get_animation_progress, set_animation_progress)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.content = QLabel("Animated Theme Transitions")
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(self.content)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(50)
        layout.addWidget(self.progress)

    def on_theme_changed(self):
        """Animate theme transition."""
        # Store old colors
        self.old_colors = dict(self.new_colors) if self.new_colors else {
            'bg': '#ffffff',
            'fg': '#000000',
            'accent': '#0066cc'
        }

        # Get new colors
        self.new_colors = {
            'bg': getattr(self.theme, 'widget_bg', '#ffffff'),
            'fg': getattr(self.theme, 'widget_fg', '#000000'),
            'accent': getattr(self.theme, 'widget_accent', '#0066cc')
        }

        # Start animation
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.start()

    def update_animated_style(self):
        """Update style based on animation progress."""
        if not self.old_colors or not self.new_colors:
            return

        # Interpolate colors
        progress = self._animation_progress / 100.0

        def interpolate_color(old, new, progress):
            old_color = QColor(old)
            new_color = QColor(new)
            r = int(old_color.red() + (new_color.red() - old_color.red()) * progress)
            g = int(old_color.green() + (new_color.green() - old_color.green()) * progress)
            b = int(old_color.blue() + (new_color.blue() - old_color.blue()) * progress)
            return QColor(r, g, b).name()

        bg = interpolate_color(self.old_colors['bg'], self.new_colors['bg'], progress)
        fg = interpolate_color(self.old_colors['fg'], self.new_colors['fg'], progress)
        accent = interpolate_color(self.old_colors['accent'], self.new_colors['accent'], progress)

        self.setStyleSheet(f"""
            AnimatedWidget {{
                background-color: {bg};
                border: 2px solid {accent};
                border-radius: 8px;
            }}
            QLabel {{
                color: {fg};
            }}
            QProgressBar {{
                background-color: {bg};
                border: 1px solid {accent};
            }}
            QProgressBar::chunk {{
                background-color: {accent};
            }}
        """)


class CompleteApplication(ThemedWidget, QMainWindow):
    """Complete application demonstrating all features."""

    theme_config = {
        'app_bg': 'colors.background',
        'app_fg': 'colors.foreground'
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Complete Themed Application")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Theme management
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(400)

        # Theme list
        theme_list_widget = QWidget()
        theme_list_layout = QVBoxLayout(theme_list_widget)

        theme_list_layout.addWidget(QLabel("Available Themes:"))
        self.theme_list = QListWidget()
        self.update_theme_list()
        self.theme_list.itemClicked.connect(self.switch_theme)
        theme_list_layout.addWidget(self.theme_list)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_theme_list)
        theme_list_layout.addWidget(refresh_btn)

        left_panel.addTab(theme_list_widget, "Themes")

        # Theme editor
        self.theme_editor = ThemeEditor()
        left_panel.addTab(self.theme_editor, "Editor")

        splitter.addWidget(left_panel)

        # Right panel - Content
        right_panel = QTabWidget()

        # Dashboard
        dashboard = self.create_dashboard()
        right_panel.addTab(dashboard, "Dashboard")

        # Animated widget
        self.animated_widget = AnimatedWidget()
        right_panel.addTab(self.animated_widget, "Animations")

        # Data table
        table = self.create_data_table()
        right_panel.addTab(table, "Data")

        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        # Status bar
        self.status = self.statusBar()
        self.update_status()

        # Auto-update status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    def create_dashboard(self):
        """Create a dashboard with various widgets."""
        dashboard = QWidget()
        layout = QGridLayout(dashboard)

        # Stats cards
        for i in range(4):
            card = QGroupBox(f"Metric {i+1}")
            card_layout = QVBoxLayout(card)

            value = QLabel(f"{(i+1)*25}%")
            value.setAlignment(Qt.AlignCenter)
            value.setStyleSheet("font-size: 24px; font-weight: bold;")
            card_layout.addWidget(value)

            label = QLabel(f"Performance metric {i+1}")
            label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(label)

            layout.addWidget(card, i // 2, i % 2)

        # Chart placeholder
        chart = QTextEdit()
        chart.setPlainText("Chart visualization would go here.\nTheme colors are applied automatically.")
        chart.setReadOnly(True)
        layout.addWidget(chart, 2, 0, 1, 2)

        return dashboard

    def create_data_table(self):
        """Create a themed data table."""
        table = QTableWidget(10, 5)
        table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Value", "Action"])

        # Sample data
        for i in range(10):
            table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            table.setItem(i, 1, QTableWidgetItem(f"Item {i+1}"))
            table.setItem(i, 2, QTableWidgetItem("Active" if i % 2 else "Inactive"))
            table.setItem(i, 3, QTableWidgetItem(f"{(i+1)*10}"))

            btn = QPushButton("Edit")
            table.setCellWidget(i, 4, btn)

        table.horizontalHeader().setStretchLastSection(True)
        return table

    def update_theme_list(self):
        """Update the list of available themes."""
        self.theme_list.clear()
        app = ThemedApplication.instance()
        if app:
            for theme in app.available_themes:
                self.theme_list.addItem(theme)

    def switch_theme(self, item):
        """Switch to selected theme."""
        theme_name = item.text()
        app = ThemedApplication.instance()
        if app:
            app.set_theme(theme_name)

    def update_status(self):
        """Update status bar."""
        app = ThemedApplication.instance()
        if app:
            theme = app.current_theme_name
            theme_type = app.theme_type
            self.status.showMessage(f"Current Theme: {theme} | Type: {theme_type} | Widgets: Multiple")

    def on_theme_changed(self):
        """Update application styling."""
        bg = getattr(self.theme, 'app_bg', '#ffffff')
        fg = getattr(self.theme, 'app_fg', '#000000')

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg};
            }}
            QTabWidget {{
                background-color: {bg};
            }}
            QTabBar::tab {{
                background-color: {bg};
                color: {fg};
                padding: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {fg};
                color: {bg};
            }}
            QGroupBox {{
                border: 1px solid {fg};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {fg};
            }}
            QTableWidget {{
                background-color: {bg};
                color: {fg};
                gridline-color: {fg};
            }}
            QHeaderView::section {{
                background-color: {fg};
                color: {bg};
                padding: 5px;
            }}
        """)


def main():
    app = ThemedApplication(sys.argv)

    # Start with default theme
    app.set_theme('default')

    window = CompleteApplication()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
