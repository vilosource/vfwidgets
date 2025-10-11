#!/usr/bin/env python3
"""Themed Terminal Widget Example.

This example demonstrates integration of the TerminalWidget with the VFWidgets
Theme System 2.0, following the official 80/20 theming pattern:

- 80% Case: Use ThemedMainWindow for automatic window chrome theming
- 20% Case: Use get_current_theme() to customize terminal appearance

For more on theming patterns, see:
    ~/GitHub/vfwidgets/widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md
"""

import sys
from pathlib import Path

# Add paths for both widgets
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
theme_path = Path(__file__).parent.parent.parent / "theme_system" / "src"
sys.path.insert(0, str(theme_path))

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Import terminal widget
from vfwidgets_terminal import TerminalWidget

# Import theme system (80% case - automatic theming)
from vfwidgets_theme import ThemedApplication, ThemedMainWindow


# Example terminal theme configurations demonstrating lineHeight and letterSpacing
COMPACT_THEME = {
    "name": "Compact Dark",
    "terminal": {
        "fontFamily": "Monaco, Consolas, 'Courier New', monospace",
        "fontSize": 13,
        "lineHeight": 1.0,  # Tight line spacing for maximum content
        "letterSpacing": 0,  # No extra character spacing
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "cursor": "#ffcc00",
        "cursorAccent": "#1e1e1e",
        "selectionBackground": "rgba(38, 79, 120, 0.3)",
        # ANSI colors
        "black": "#000000",
        "red": "#cd3131",
        "green": "#0dbc79",
        "yellow": "#e5e510",
        "blue": "#2472c8",
        "magenta": "#bc3fbc",
        "cyan": "#11a8cd",
        "white": "#e5e5e5",
        "brightBlack": "#555753",
        "brightRed": "#f14c4c",
        "brightGreen": "#23d18b",
        "brightYellow": "#f5f543",
        "brightBlue": "#3b8eea",
        "brightMagenta": "#d670d6",
        "brightCyan": "#29b8db",
        "brightWhite": "#f5f5f5",
    },
}

RELAXED_THEME = {
    "name": "Relaxed Dark",
    "terminal": {
        "fontFamily": "Monaco, Consolas, 'Courier New', monospace",
        "fontSize": 14,
        "lineHeight": 1.5,  # Generous line spacing for readability
        "letterSpacing": 1,  # 1px between characters for clarity
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "cursor": "#ffcc00",
        "cursorAccent": "#1e1e1e",
        "selectionBackground": "rgba(38, 79, 120, 0.3)",
        # ANSI colors
        "black": "#000000",
        "red": "#cd3131",
        "green": "#0dbc79",
        "yellow": "#e5e510",
        "blue": "#2472c8",
        "magenta": "#bc3fbc",
        "cyan": "#11a8cd",
        "white": "#e5e5e5",
        "brightBlack": "#555753",
        "brightRed": "#f14c4c",
        "brightGreen": "#23d18b",
        "brightYellow": "#f5f543",
        "brightBlue": "#3b8eea",
        "brightMagenta": "#d670d6",
        "brightCyan": "#29b8db",
        "brightWhite": "#f5f5f5",
    },
}

ACCESSIBLE_THEME = {
    "name": "Accessible High Contrast",
    "terminal": {
        "fontFamily": "Monaco, Consolas, 'Courier New', monospace",
        "fontSize": 15,
        "lineHeight": 1.6,  # Extra generous spacing for accessibility
        "letterSpacing": 1.5,  # Clear character separation
        "background": "#000000",
        "foreground": "#ffffff",
        "cursor": "#00ff00",
        "cursorAccent": "#000000",
        "selectionBackground": "rgba(255, 255, 0, 0.3)",
        # ANSI colors (high contrast)
        "black": "#000000",
        "red": "#ff0000",
        "green": "#00ff00",
        "yellow": "#ffff00",
        "blue": "#0000ff",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "white": "#ffffff",
        "brightBlack": "#808080",
        "brightRed": "#ff8080",
        "brightGreen": "#80ff80",
        "brightYellow": "#ffff80",
        "brightBlue": "#8080ff",
        "brightMagenta": "#ff80ff",
        "brightCyan": "#80ffff",
        "brightWhite": "#ffffff",
    },
}


class ThemedTerminalWindow(ThemedMainWindow):
    """Terminal window with automatic theme integration.

    This demonstrates the 80/20 theming pattern:
    - ThemedMainWindow provides automatic window chrome theming (80%)
    - get_current_theme() provides Theme object for customization (20%)
    """

    def __init__(self):
        """Initialize themed terminal window."""
        super().__init__()

        self.setWindowTitle("VFWidgets Themed Terminal")
        self.setGeometry(100, 100, 1000, 700)

        # ========== 80% CASE: Automatic Theming ==========
        # By inheriting from ThemedMainWindow, the window chrome
        # (title bar, borders, buttons) automatically follow the theme.
        # All Qt widgets added here are automatically themed!

        # Create central widget (also themed automatically)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar with theme controls
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar, 0)  # 0 = no stretch, toolbar uses minimum height

        # Create terminal widget
        # Terminal uses xterm.js which has its own theming
        # (we'll demonstrate passing theme colors in the 20% case below)
        self.terminal = TerminalWidget(debug=False)
        layout.addWidget(
            self.terminal, 1
        )  # 1 = stretch, terminal takes remaining space

        # Connect terminal events
        self.terminal.terminal_ready.connect(self._on_terminal_ready)
        self.terminal.terminal_closed.connect(self._on_terminal_closed)

        # Store toolbar widgets for access
        self._setup_complete = False

    def _create_toolbar(self) -> QWidget:
        """Create themed toolbar with controls.

        Returns:
            Themed toolbar widget (automatically styled)
        """
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # Title label (automatically themed)
        title = QLabel("🎨 Themed Terminal")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        toolbar_layout.addWidget(title)

        toolbar_layout.addStretch()

        # ========== 80% CASE: Theme Selector ==========
        # Theme selector uses automatic theming from parent
        toolbar_layout.addWidget(QLabel("Theme:"))
        self.theme_selector = QComboBox()

        # Get available themes from ThemedApplication
        app = ThemedApplication.instance()
        if app:
            self.theme_selector.addItems(app.available_themes)
            current_theme = app.get_current_theme()
            if current_theme:
                self.theme_selector.setCurrentText(current_theme.name)

        self.theme_selector.currentTextChanged.connect(self._on_theme_changed)
        toolbar_layout.addWidget(self.theme_selector)

        # ========== 80% CASE: Action Buttons ==========
        # Buttons automatically get theme styling
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.terminal.clear())
        toolbar_layout.addWidget(clear_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: self.terminal.reset())
        toolbar_layout.addWidget(reset_btn)

        # Danger button with role marker (semantic theming)
        close_btn = QPushButton("Close Terminal")
        close_btn.setProperty("role", "danger")  # Red styling
        close_btn.clicked.connect(lambda: self.terminal.close_terminal())
        toolbar_layout.addWidget(close_btn)

        # Separator
        toolbar_layout.addWidget(QLabel(" | "))

        # Terminal theme buttons (demonstrate lineHeight/letterSpacing)
        toolbar_layout.addWidget(QLabel("Terminal Theme:"))

        compact_btn = QPushButton("Compact")
        compact_btn.clicked.connect(
            lambda: self.terminal.set_terminal_theme(COMPACT_THEME)
        )
        compact_btn.setToolTip("Tight spacing (lineHeight: 1.0)")
        toolbar_layout.addWidget(compact_btn)

        relaxed_btn = QPushButton("Relaxed")
        relaxed_btn.clicked.connect(
            lambda: self.terminal.set_terminal_theme(RELAXED_THEME)
        )
        relaxed_btn.setToolTip("Generous spacing (lineHeight: 1.5, letterSpacing: 1)")
        toolbar_layout.addWidget(relaxed_btn)

        accessible_btn = QPushButton("Accessible")
        accessible_btn.clicked.connect(
            lambda: self.terminal.set_terminal_theme(ACCESSIBLE_THEME)
        )
        accessible_btn.setToolTip(
            "High contrast with extra spacing (lineHeight: 1.6, letterSpacing: 1.5)"
        )
        toolbar_layout.addWidget(accessible_btn)

        return toolbar

    def _on_theme_changed(self, theme_name: str):
        """Handle theme selection change.

        This demonstrates both the 80% and 20% cases:
        - 80%: Window chrome updates automatically
        - 20%: We could pass theme colors to terminal if needed
        """
        app = ThemedApplication.instance()
        if app:
            # Change application theme (80% case - automatic)
            app.set_theme(theme_name)

            # ========== 20% CASE: Custom Theme Integration ==========
            # If we wanted to sync terminal colors with Qt theme,
            # we would use get_current_theme() here:
            #
            # theme = self.get_current_theme()
            # if theme:
            #     bg_color = theme.colors.get('editor.background', '#1e1e1e')
            #     fg_color = theme.colors.get('editor.foreground', '#d4d4d4')
            #     # Apply to terminal (implementation would depend on terminal API)
            #
            # For this example, we just demonstrate the pattern.
            # The terminal widget uses xterm.js with its own theming.

    def _on_terminal_ready(self):
        """Handle terminal ready event."""
        print("✅ Terminal is ready!")

        # ========== 20% CASE EXAMPLE: Access Theme for Customization ==========
        # This demonstrates getting the Theme object to customize child components
        theme = self.get_current_theme()
        if theme:
            print(f"📝 Current theme: {theme.name}")
            print(f"   - Background: {theme.colors.get('editor.background', 'N/A')}")
            print(f"   - Foreground: {theme.colors.get('editor.foreground', 'N/A')}")
            print(
                f"   - Selection: {theme.colors.get('editor.selectionBackground', 'N/A')}"
            )

            # In a real integration, you might pass these to terminal:
            # self.terminal.set_theme({
            #     'background': theme.colors.get('editor.background'),
            #     'foreground': theme.colors.get('editor.foreground'),
            #     # ... more color mappings
            # })

    def _on_terminal_closed(self, exit_code: int):
        """Handle terminal closed event."""
        print(f"🔚 Terminal closed with code: {exit_code}")

    def on_theme_changed(self):
        """Hook called when application theme changes (from ThemedMainWindow).

        This is part of the 80% case - framework calls this automatically.
        Use this for additional logic when theme changes.

        Note: self.update() is already called by the framework before this.
        """
        # Example: Could update terminal theme here if needed
        theme = self.get_current_theme()
        if theme:
            print(f"🎨 Theme changed to: {theme.name}")


def main():
    """Run the themed terminal example."""
    # ========== 80% CASE: ThemedApplication ==========
    # Use ThemedApplication instead of QApplication
    # This enables automatic theming for the entire app
    app = ThemedApplication(sys.argv)
    app.setApplicationName("VFWidgets Themed Terminal")

    # Set initial theme (optional)
    app.set_theme("dark")

    # ========== 80% CASE: ThemedMainWindow ==========
    # Create themed window - inherits from ThemedMainWindow
    # All child widgets automatically get themed
    window = ThemedTerminalWindow()
    window.show()

    print("\n" + "=" * 60)
    print("🎨 VFWIDGETS THEMED TERMINAL EXAMPLE")
    print("=" * 60)
    print("📖 This example demonstrates theme system integration:")
    print()
    print("🎯 80% Case (Automatic Theming):")
    print("   • ThemedApplication + ThemedMainWindow")
    print("   • Window chrome automatically themed")
    print("   • All Qt widgets automatically themed")
    print("   • Theme selector updates entire UI")
    print()
    print("🎯 20% Case (Custom Integration):")
    print("   • Use get_current_theme() to get Theme object")
    print("   • Pass theme colors to child components")
    print("   • Demonstrated in _on_terminal_ready()")
    print()
    print("📏 Terminal Spacing Customization:")
    print("   • Compact: lineHeight 1.0 (tight)")
    print("   • Relaxed: lineHeight 1.5 + letterSpacing 1px")
    print("   • Accessible: lineHeight 1.6 + letterSpacing 1.5px")
    print()
    print("💡 Try changing themes with the dropdown!")
    print("💡 Try terminal spacing with the theme buttons!")
    print("=" * 60)
    print()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
