"""Auxiliary Bar Demo - Demonstrates right sidebar (auxiliary panel).

Shows how to use the auxiliary bar to display secondary content.
Includes toggle functionality and practical examples.
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
)

from vfwidgets_vilocode_window import ViloCodeWindow


def main() -> None:
    """Run the auxiliary bar demo."""
    app = QApplication(sys.argv)

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("Auxiliary Bar Demo - Right Sidebar")
    window.resize(1200, 700)

    # Add main content
    editor = QTextEdit()
    editor.setPlainText(
        """# Auxiliary Bar Demo

The auxiliary bar is a right sidebar for secondary content.

Features demonstrated:
- set_auxiliary_content() - Set the auxiliary bar content widget
- toggle_auxiliary_bar() - Toggle visibility
- set_auxiliary_bar_visible() - Show/hide programmatically
- Resizable - Drag the left edge of auxiliary bar to resize

Try:
1. The auxiliary bar shows an outline tree on the right
2. Drag the left edge of the auxiliary bar to resize it
3. Press Alt+O to toggle auxiliary bar visibility
4. Click outline items to select them

Difference from Sidebar:
- Auxiliary bar: Single content widget, no header, right side
- Sidebar: Multiple stackable panels, with header, left side
- Both: Independently collapsible and resizable
"""
    )
    window.set_main_content(editor)

    # Create outline panel for auxiliary bar
    outline = QTreeWidget()
    outline.setHeaderLabel("OUTLINE")
    outline.setStyleSheet(
        """
        QTreeWidget {
            background-color: #252526;
            color: #cccccc;
            border: none;
            outline: none;
        }
        QTreeWidget::item {
            padding: 4px;
        }
        QTreeWidget::item:selected {
            background-color: #094771;
        }
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
    """
    )

    # Populate outline with document structure
    def populate_outline() -> None:
        """Populate outline tree with document structure."""
        outline.clear()

        # Root
        root = QTreeWidgetItem(outline)
        root.setText(0, "📄 Document")
        root.setExpanded(True)

        # Heading 1
        h1 = QTreeWidgetItem(root)
        h1.setText(0, "# Auxiliary Bar Demo")
        h1.setExpanded(True)

        # Features section
        features = QTreeWidgetItem(h1)
        features.setText(0, "📋 Features demonstrated")
        features.setExpanded(True)

        feature_items = [
            "set_auxiliary_content()",
            "toggle_auxiliary_bar()",
            "set_auxiliary_bar_visible()",
            "Resizable",
        ]
        for item_text in feature_items:
            item = QTreeWidgetItem(features)
            item.setText(0, f"  • {item_text}")

        # Try section
        try_section = QTreeWidgetItem(h1)
        try_section.setText(0, "✓ Try")
        try_section.setExpanded(True)

        try_items = [
            "The auxiliary bar shows an outline tree on the right",
            "Drag the left edge of the auxiliary bar to resize it",
            "Press Alt+O to toggle auxiliary bar visibility",
            "Click outline items to select them",
        ]
        for idx, item_text in enumerate(try_items, 1):
            item = QTreeWidgetItem(try_section)
            item.setText(0, f"  {idx}. {item_text}")

        # Difference section
        diff = QTreeWidgetItem(h1)
        diff.setText(0, "📊 Difference from Sidebar")
        diff.setExpanded(True)

        diff_items = [
            "Auxiliary bar: Single content widget, no header, right side",
            "Sidebar: Multiple stackable panels, with header, left side",
            "Both: Independently collapsible and resizable",
        ]
        for item_text in diff_items:
            item = QTreeWidgetItem(diff)
            item.setText(0, f"  • {item_text}")

    populate_outline()

    # Handle outline item clicks
    def on_outline_item_clicked(item: QTreeWidgetItem, column: int) -> None:
        """Handle outline item click.

        Args:
            item: Clicked tree item
            column: Column index
        """
        item_text = item.text(0).strip()
        window.set_status_message(f"📝 Selected: {item_text}")

    outline.itemClicked.connect(on_outline_item_clicked)

    # Set auxiliary bar content
    window.set_auxiliary_content(outline)

    # Show auxiliary bar by default
    window.set_auxiliary_bar_visible(True)

    # Show visibility change notifications
    def on_visibility_changed(is_visible: bool) -> None:
        """Handle auxiliary bar visibility change.

        Args:
            is_visible: True if visible, False if hidden
        """
        status = "visible" if is_visible else "hidden"
        window.set_status_message(f"👁 Auxiliary bar is now {status} (press Alt+O to toggle)")
        print(f"Auxiliary bar visibility: {is_visible}")

    window.auxiliary_bar_visibility_changed.connect(on_visibility_changed)

    # Register custom shortcut for toggling auxiliary bar
    window.register_custom_shortcut(
        "toggle_auxiliary_bar",
        "Alt+O",
        window.toggle_auxiliary_bar,
        "Toggle Auxiliary Bar",
    )

    # Set initial status
    window.set_status_message(
        "Auxiliary bar shows document outline | "
        "Drag left edge to resize | "
        "Press Alt+O to toggle visibility"
    )

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
