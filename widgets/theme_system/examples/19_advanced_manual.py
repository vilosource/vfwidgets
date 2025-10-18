#!/usr/bin/env python3
"""Example 19: Advanced Manual Overrides - Direct ThemeManager API

This example demonstrates advanced overlay system features:
- Direct ThemeManager API usage (without VFThemedApplication)
- Bulk override operations
- Layer priority manipulation (app vs user)
- Override introspection and debugging
- Manual persistence control

This pattern is for advanced users who need fine-grained control
over the overlay system.

Usage:
    python examples/19_advanced_manual.py
"""

import sys

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_theme import ThemedApplication, ThemedWidget
from vfwidgets_theme.core.manager import ThemeManager


class AdvancedManualDemo(ThemedWidget):
    """Demo showing advanced manual override manipulation."""

    theme_config = {
        "background": "editor.background",
        "foreground": "editor.foreground",
    }

    def __init__(self):
        super().__init__()
        self.manager = ThemeManager.get_instance()
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Advanced Manual Overrides")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        desc = QLabel(
            "This example demonstrates direct ThemeManager API usage for advanced scenarios.\n"
            "Explore app vs user layer priorities, bulk operations, and introspection."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px;")
        layout.addWidget(desc)

        # Tabbed interface
        tabs = QTabWidget()
        tabs.addTab(self.create_priority_tab(), "Layer Priority")
        tabs.addTab(self.create_bulk_ops_tab(), "Bulk Operations")
        tabs.addTab(self.create_introspection_tab(), "Introspection")
        layout.addWidget(tabs)

        # Status bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet("padding: 5px; background: #2d2d2d;")
        layout.addWidget(self.status_bar)

    def create_priority_tab(self):
        """Create layer priority demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Description
        desc = QLabel(
            "Override Resolution Priority: user > app > base theme\n\n"
            "Set overrides in both layers for the same token and see which wins."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Demo editor
        self.priority_editor = QTextEdit()
        self.priority_editor.setPlainText(
            "# Watch the background color change based on layer priority\n"
            "# User layer always wins over app layer\n"
        )
        self.priority_editor.setMinimumHeight(150)
        layout.addWidget(self.priority_editor)

        # Controls
        controls = QGroupBox("Layer Controls")
        controls_layout = QVBoxLayout(controls)

        # App layer controls
        app_layout = QHBoxLayout()
        app_layout.addWidget(QLabel("App Layer:"))
        btn_app_red = QPushButton("Set Red")
        btn_app_red.clicked.connect(
            lambda: self.set_layer_override("app", "editor.background", "#4a1515")
        )
        app_layout.addWidget(btn_app_red)
        btn_app_clear = QPushButton("Clear")
        btn_app_clear.clicked.connect(lambda: self.clear_layer_override("app", "editor.background"))
        app_layout.addWidget(btn_app_clear)
        controls_layout.addLayout(app_layout)

        # User layer controls
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("User Layer:"))
        btn_user_blue = QPushButton("Set Blue")
        btn_user_blue.clicked.connect(
            lambda: self.set_layer_override("user", "editor.background", "#15154a")
        )
        user_layout.addWidget(btn_user_blue)
        btn_user_clear = QPushButton("Clear")
        btn_user_clear.clicked.connect(
            lambda: self.clear_layer_override("user", "editor.background")
        )
        user_layout.addWidget(btn_user_clear)
        controls_layout.addLayout(user_layout)

        # Resolution info
        self.resolution_label = QLabel()
        self.update_resolution_info()
        controls_layout.addWidget(self.resolution_label)

        layout.addWidget(controls)
        layout.addStretch()

        return widget

    def create_bulk_ops_tab(self):
        """Create bulk operations demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Bulk operations allow setting multiple overrides efficiently.\n"
            "Useful for theme presets or importing user configurations."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Demo editor
        self.bulk_editor = QTextEdit()
        self.bulk_editor.setPlainText(
            "# Bulk override demo\n# Click buttons below to apply preset configurations"
        )
        self.bulk_editor.setMinimumHeight(150)
        layout.addWidget(self.bulk_editor)

        # Preset buttons
        presets_group = QGroupBox("Color Presets")
        presets_layout = QVBoxLayout(presets_group)

        btn_preset1 = QPushButton("Apply 'Midnight' Preset (5 colors)")
        btn_preset1.clicked.connect(self.apply_midnight_preset)
        presets_layout.addWidget(btn_preset1)

        btn_preset2 = QPushButton("Apply 'Ocean' Preset (5 colors)")
        btn_preset2.clicked.connect(self.apply_ocean_preset)
        presets_layout.addWidget(btn_preset2)

        btn_clear_all = QPushButton("Clear All App Overrides")
        btn_clear_all.clicked.connect(self.clear_all_app_overrides)
        presets_layout.addWidget(btn_clear_all)

        layout.addWidget(presets_group)

        # Bulk operation stats
        self.bulk_stats = QLabel()
        self.update_bulk_stats()
        layout.addWidget(self.bulk_stats)

        layout.addStretch()

        return widget

    def create_introspection_tab(self):
        """Create introspection/debugging tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        desc = QLabel(
            "Inspect all active overrides across both layers.\n"
            "Useful for debugging and understanding the current state."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Override table
        self.override_table = QTableWidget()
        self.override_table.setColumnCount(3)
        self.override_table.setHorizontalHeaderLabels(["Token", "Layer", "Color"])
        self.override_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.override_table)

        # Refresh button
        btn_refresh = QPushButton("Refresh Override List")
        btn_refresh.clicked.connect(self.refresh_override_table)
        layout.addWidget(btn_refresh)

        # Initial population
        self.refresh_override_table()

        return widget

    # ========================================================================
    # Layer Priority Methods
    # ========================================================================

    def set_layer_override(self, layer: str, token: str, color: str):
        """Set override in specific layer."""
        if layer == "app":
            self.manager.set_app_override(token, color)
        elif layer == "user":
            self.manager.set_user_override(token, color)
        self.update_resolution_info()
        self.update_bulk_stats()
        self.refresh_override_table()
        self.status_bar.setText(f"Set {layer} override: {token} = {color}")

    def clear_layer_override(self, layer: str, token: str):
        """Clear override from specific layer."""
        if layer == "app":
            self.manager.remove_app_override(token)
        elif layer == "user":
            self.manager.remove_user_override(token)
        self.update_resolution_info()
        self.update_bulk_stats()
        self.refresh_override_table()
        self.status_bar.setText(f"Cleared {layer} override for {token}")

    def update_resolution_info(self):
        """Update resolution information."""
        token = "editor.background"
        app_color = self.manager.get_app_overrides().get(token, "none")
        user_color = self.manager.get_user_overrides().get(token, "none")
        effective = self.manager.get_effective_color(token, "theme default")

        text = (
            f"Current State for editor.background:\n"
            f"  App Layer: {app_color}\n"
            f"  User Layer: {user_color}\n"
            f"  Effective (resolved): {effective}"
        )
        self.resolution_label.setText(text)
        self.resolution_label.setStyleSheet(
            "padding: 10px; background: #2d2d2d; font-family: monospace;"
        )

    # ========================================================================
    # Bulk Operations Methods
    # ========================================================================

    def apply_midnight_preset(self):
        """Apply midnight color preset."""
        midnight = {
            "editor.background": "#0a0e27",
            "editor.foreground": "#a0a8cd",
            "tab.activeBackground": "#1a1e37",
            "button.background": "#1e2238",
            "statusBar.background": "#050810",
        }
        self.manager.set_app_overrides_bulk(midnight)
        self.update_bulk_stats()
        self.refresh_override_table()
        self.status_bar.setText(f"Applied Midnight preset ({len(midnight)} colors)")

    def apply_ocean_preset(self):
        """Apply ocean color preset."""
        ocean = {
            "editor.background": "#001a33",
            "editor.foreground": "#b3d9ff",
            "tab.activeBackground": "#003366",
            "button.background": "#004d99",
            "statusBar.background": "#003d7a",
        }
        self.manager.set_app_overrides_bulk(ocean)
        self.update_bulk_stats()
        self.refresh_override_table()
        self.status_bar.setText(f"Applied Ocean preset ({len(ocean)} colors)")

    def clear_all_app_overrides(self):
        """Clear all app layer overrides."""
        count = self.manager.clear_app_overrides()
        self.update_bulk_stats()
        self.refresh_override_table()
        self.status_bar.setText(f"Cleared {count} app overrides")

    def update_bulk_stats(self):
        """Update bulk operation statistics."""
        app_count = len(self.manager.get_app_overrides())
        user_count = len(self.manager.get_user_overrides())
        effective = self.manager.get_all_effective_overrides()

        text = (
            f"Override Statistics:\n"
            f"  App Layer: {app_count} overrides\n"
            f"  User Layer: {user_count} overrides\n"
            f"  Total Effective: {len(effective)} tokens affected"
        )
        self.bulk_stats.setText(text)
        self.bulk_stats.setStyleSheet("padding: 10px; background: #2d2d2d; font-family: monospace;")

    # ========================================================================
    # Introspection Methods
    # ========================================================================

    def refresh_override_table(self):
        """Refresh the override introspection table."""
        self.override_table.setRowCount(0)

        # Get all overrides
        app_overrides = self.manager.get_app_overrides()
        user_overrides = self.manager.get_user_overrides()

        # Combine all tokens
        all_tokens = set(app_overrides.keys()) | set(user_overrides.keys())

        # Populate table
        for token in sorted(all_tokens):
            # Add app layer row if exists
            if token in app_overrides:
                row = self.override_table.rowCount()
                self.override_table.insertRow(row)
                self.override_table.setItem(row, 0, QTableWidgetItem(token))
                self.override_table.setItem(row, 1, QTableWidgetItem("app"))
                self.override_table.setItem(row, 2, QTableWidgetItem(app_overrides[token]))

            # Add user layer row if exists
            if token in user_overrides:
                row = self.override_table.rowCount()
                self.override_table.insertRow(row)
                self.override_table.setItem(row, 0, QTableWidgetItem(token))
                self.override_table.setItem(row, 1, QTableWidgetItem("user (wins)"))
                self.override_table.setItem(row, 2, QTableWidgetItem(user_overrides[token]))


def main():
    """Main entry point."""
    # Create application
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    # Create and show main window
    window = AdvancedManualDemo()
    window.setWindowTitle("Example 19: Advanced Manual Overrides")
    window.resize(800, 600)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
