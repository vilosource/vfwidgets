"""Activity Bar Demo - Demonstrates activity bar functionality.

Shows how to add items to the activity bar and handle clicks.
"""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QTextEdit

from vfwidgets_vilocode_window import ViloCodeWindow


def main():
    """Run the activity bar demo."""
    app = QApplication(sys.argv)

    # Create window
    window = ViloCodeWindow()
    window.setWindowTitle("Activity Bar Demo")
    window.resize(1000, 700)

    # Add some content
    editor = QTextEdit()
    editor.setPlainText(
        """# Activity Bar Demo

The activity bar on the left shows clickable icons.

Try clicking on the different icons to see the signals being emitted.

Features demonstrated:
- add_activity_item() - Add items with icons and tooltips
- activity_item_clicked signal - Handle clicks
- set_active_activity_item() - Highlight active item
- Icons from theme (fallback to Unicode symbols)
"""
    )
    window.set_main_content(editor)

    # Status label to show click events
    def on_item_clicked(item_id: str):
        window.set_status_message(f"📍 Activity item clicked: {item_id}")
        print(f"Activity item clicked: {item_id}")

    # Connect signal
    window.activity_item_clicked.connect(on_item_clicked)

    # Helper function to create icons from Unicode symbols
    def create_icon_from_text(text: str, size: int = 24) -> QIcon:
        """Create an icon from text/unicode symbol."""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor, QFont, QPixmap

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        from PySide6.QtGui import QPainter

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw text centered
        font = QFont("Segoe UI Symbol", int(size * 0.6))  # 60% of icon size
        painter.setFont(font)
        painter.setPen(QColor("#cccccc"))  # Light gray

        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

        return QIcon(pixmap)

    # Add activity items with Unicode symbol icons
    # These will always be visible regardless of system theme
    explorer_icon = create_icon_from_text("📁")  # Folder
    search_icon = create_icon_from_text("🔍")  # Magnifying glass
    source_control_icon = create_icon_from_text("⎇")  # Git branch symbol
    debug_icon = create_icon_from_text("▶")  # Play/run
    extensions_icon = create_icon_from_text("⊞")  # Box/extensions

    window.add_activity_item("explorer", explorer_icon, "Explorer (Ctrl+Shift+E)")
    window.add_activity_item("search", search_icon, "Search (Ctrl+Shift+F)")
    window.add_activity_item("source_control", source_control_icon, "Source Control (Ctrl+Shift+G)")
    window.add_activity_item("debug", debug_icon, "Run and Debug (Ctrl+Shift+D)")
    window.add_activity_item("extensions", extensions_icon, "Extensions (Ctrl+Shift+X)")

    # Set first item as active
    window.set_active_activity_item("explorer")

    # Set initial status
    window.set_status_message("Click on activity bar items to see them highlighted")

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
