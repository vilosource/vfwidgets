#!/usr/bin/env python3
"""Example demonstrating keyboard shortcuts in ViloCodeWindow.

This example shows:
- Default VS Code-compatible shortcuts
- Customizing existing shortcuts
- Registering custom shortcuts
- Enabling/disabling shortcuts
- Querying shortcut information
- Interactive help display in main pane
"""

import sys

from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget

from vfwidgets_vilocode_window import ViloCodeWindow


def create_help_text(window):
    """Create formatted help text showing all shortcuts."""
    shortcuts = window.get_all_shortcuts()

    text = """<html>
<head>
<style>
body {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 20px;
}
h1 {
    color: #4ec9b0;
    border-bottom: 2px solid #007acc;
    padding-bottom: 10px;
}
h2 {
    color: #569cd6;
    margin-top: 20px;
}
.shortcut-table {
    width: 100%;
    margin: 15px 0;
    border-collapse: collapse;
}
.shortcut-table th {
    background-color: #2d2d30;
    color: #cccccc;
    text-align: left;
    padding: 8px;
    border: 1px solid #3e3e42;
}
.shortcut-table td {
    padding: 8px;
    border: 1px solid #3e3e42;
}
.key {
    background-color: #3c3c3c;
    color: #ce9178;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: monospace;
    font-weight: bold;
}
.category {
    color: #4ec9b0;
    font-weight: bold;
}
.description {
    color: #d4d4d4;
}
.custom {
    color: #c586c0;
}
.instruction {
    background-color: #264f78;
    color: #ffffff;
    padding: 12px;
    border-radius: 5px;
    margin: 15px 0;
}
.tip {
    background-color: #1e3a1e;
    color: #4ec9b0;
    padding: 10px;
    border-left: 4px solid #4ec9b0;
    margin: 10px 0;
}
</style>
</head>
<body>

<h1>⌨️ Keyboard Shortcuts Reference</h1>

<div class="instruction">
📌 <strong>Try the shortcuts below!</strong> Watch the status bar and console for feedback.
</div>

<h2>🎯 View Shortcuts</h2>
<table class="shortcut-table">
<tr>
    <th>Shortcut</th>
    <th>Action</th>
    <th>Description</th>
</tr>
"""

    # Group shortcuts by category
    categories = {"view": [], "window": [], "panel": [], "custom": []}

    for action_name, shortcut_def in shortcuts.items():
        categories[shortcut_def.category].append((action_name, shortcut_def))

    # Add view shortcuts
    for action_name, shortcut_def in sorted(categories["view"]):
        text += f"""<tr>
    <td><span class="key">{shortcut_def.key_sequence}</span></td>
    <td><strong>{action_name}</strong></td>
    <td class="description">{shortcut_def.description}</td>
</tr>
"""

    text += """</table>

<h2>🪟 Window Shortcuts</h2>
<table class="shortcut-table">
<tr>
    <th>Shortcut</th>
    <th>Action</th>
    <th>Description</th>
</tr>
"""

    # Add window shortcuts
    for action_name, shortcut_def in sorted(categories["window"]):
        text += f"""<tr>
    <td><span class="key">{shortcut_def.key_sequence}</span></td>
    <td><strong>{action_name}</strong></td>
    <td class="description">{shortcut_def.description}</td>
</tr>
"""

    text += """</table>

<h2>🎨 Custom Shortcuts</h2>
<table class="shortcut-table">
<tr>
    <th>Shortcut</th>
    <th>Action</th>
    <th>Description</th>
</tr>
"""

    # Add custom shortcuts
    for action_name, shortcut_def in sorted(categories["custom"]):
        text += f"""<tr>
    <td><span class="key">{shortcut_def.key_sequence}</span></td>
    <td class="custom"><strong>{action_name}</strong></td>
    <td class="description">{shortcut_def.description}</td>
</tr>
"""

    text += """</table>

<div class="tip">
💡 <strong>Tips:</strong>
<ul>
<li>Press <span class="key">Ctrl+Shift+S</span> to toggle the status bar on/off</li>
<li>Press <span class="key">F11</span> to toggle fullscreen mode</li>
<li>Press <span class="key">Ctrl+K</span> or <span class="key">Ctrl+Shift+K</span> to trigger custom actions</li>
<li>Watch the status bar at the bottom for feedback on your actions</li>
<li>Check the console output for detailed event logging</li>
</ul>
</div>

<div class="instruction">
🔧 <strong>Customization:</strong> This example demonstrates how to customize shortcuts:
<ul>
<li>TOGGLE_SIDEBAR was changed from <span class="key">Ctrl+B</span> to <span class="key">Ctrl+Shift+E</span></li>
<li>Two custom shortcuts were registered (<span class="key">Ctrl+K</span>, <span class="key">Ctrl+Shift+K</span>)</li>
</ul>
</div>

<h2>📚 About This Demo</h2>
<p>
This window demonstrates the complete keyboard shortcuts system for ViloCodeWindow:
</p>
<ul>
<li><strong>9 default VS Code-compatible shortcuts</strong> loaded automatically</li>
<li><strong>Custom shortcut registration</strong> with callbacks</li>
<li><strong>Shortcut customization</strong> (change key sequences)</li>
<li><strong>Enable/disable shortcuts</strong> dynamically</li>
<li><strong>Query shortcut information</strong> programmatically</li>
</ul>

</body>
</html>
"""

    return text


def main():
    """Demonstrate keyboard shortcut functionality."""
    app = QApplication(sys.argv)

    # Create window with default shortcuts enabled
    window = ViloCodeWindow()
    window.setWindowTitle("ViloCodeWindow - Keyboard Shortcuts Demo")
    window.resize(1400, 900)

    print("=" * 70)
    print("ViloCodeWindow - Keyboard Shortcuts Demo")
    print("=" * 70)
    print()

    # Customize an existing shortcut
    print("Customizations Applied:")
    print("-" * 70)
    window.set_shortcut("TOGGLE_SIDEBAR", "Ctrl+Shift+E")
    print("  • Changed TOGGLE_SIDEBAR from Ctrl+B to Ctrl+Shift+E")

    # Register custom shortcuts
    def custom_action_1():
        window.set_status_message("✓ Custom Action 1 triggered! (Ctrl+K)", 3000)
        print("  [Event] Custom Action 1 triggered (Ctrl+K)")
        # Update help text to show action was triggered
        help_editor.append(
            "<p style='color: #4ec9b0; background-color: #1e3a1e; padding: 5px;'>✓ Custom Action 1 triggered!</p>"
        )

    def custom_action_2():
        window.set_status_message("✓ Custom Action 2 triggered! (Ctrl+Shift+K)", 3000)
        print("  [Event] Custom Action 2 triggered (Ctrl+Shift+K)")
        # Update help text to show action was triggered
        help_editor.append(
            "<p style='color: #4ec9b0; background-color: #1e3a1e; padding: 5px;'>✓ Custom Action 2 triggered!</p>"
        )

    window.register_custom_shortcut(
        "CUSTOM_ACTION_1", "Ctrl+K", custom_action_1, "Trigger custom action 1"
    )
    window.register_custom_shortcut(
        "CUSTOM_ACTION_2", "Ctrl+Shift+K", custom_action_2, "Trigger custom action 2"
    )
    print("  • Registered CUSTOM_ACTION_1: Ctrl+K")
    print("  • Registered CUSTOM_ACTION_2: Ctrl+Shift+K")
    print()

    # Create help text editor and add to window
    help_editor = QTextEdit()
    help_editor.setReadOnly(True)
    help_editor.setHtml(create_help_text(window))

    # Remove border and set background to match VS Code theme
    help_editor.setStyleSheet(
        """
        QTextEdit {
            border: none;
            background-color: #1e1e1e;
            padding: 0px;
            margin: 0px;
        }
    """
    )

    # Access the window's internal layout to replace the main pane placeholder
    # We need to find the main layout and replace the center widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(help_editor)

    # Find the main content area in the window's layout and replace it
    # The ViloCodeWindow has a QHBoxLayout with placeholders
    # We'll find the main pane (the one with stretch=1) and replace it
    main_layout = window.layout()
    if main_layout and main_layout.count() > 1:
        # Second item should be the horizontal content layout
        content_item = main_layout.itemAt(1)
        if content_item and hasattr(content_item, "layout"):
            content_layout = content_item.layout()
            if content_layout:
                # Find and replace the main pane (index 2, the one with stretch)
                for i in range(content_layout.count()):
                    item = content_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        # The main pane is the one with "Main Pane" text
                        if hasattr(widget, "text") and "Main Pane" in widget.text():
                            # Remove old widget
                            content_layout.removeWidget(widget)
                            widget.deleteLater()
                            # Insert help editor
                            content_layout.insertWidget(i, help_editor, 1)
                            break

    # Set initial status message
    window.set_status_message(
        "⌨️ Try the keyboard shortcuts shown above! Watch this status bar for feedback."
    )

    # Show instructions in console
    print("Instructions:")
    print("-" * 70)
    print("  The window now displays an interactive shortcuts reference!")
    print("  Try pressing the keyboard shortcuts listed in the window.")
    print("  Watch the status bar and console for feedback.")
    print()
    print("Quick Test Shortcuts:")
    print("  • Ctrl+Shift+S      - Toggle status bar visibility")
    print("  • F11               - Toggle fullscreen mode")
    print("  • Ctrl+K            - Trigger custom action 1")
    print("  • Ctrl+Shift+K      - Trigger custom action 2")
    print("=" * 70)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
