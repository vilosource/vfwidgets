#!/usr/bin/env python3
"""Quick test for bidirectional theme switching."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
theme_path = Path(__file__).parent.parent / "theme_system" / "src"
sys.path.insert(0, str(theme_path))

from PySide6.QtCore import QTimer
from vfwidgets_theme import ThemedApplication, ThemedMainWindow
from vfwidgets_terminal import TerminalWidget


class TestWindow(ThemedMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Switch Test")
        self.setGeometry(100, 100, 800, 600)

        self.terminal = TerminalWidget(debug=True)
        self.setCentralWidget(self.terminal)

        # Auto-test theme switching
        self.terminal.terminal_ready.connect(self.test_theme_switching)

    def test_theme_switching(self):
        """Automatically test theme switching: dark -> light -> dark -> light"""
        app = ThemedApplication.instance()

        print("\n" + "="*60)
        print("AUTOMATIC THEME SWITCHING TEST")
        print("="*60)

        # Start with dark (already set in main)
        QTimer.singleShot(2000, lambda: self.switch_and_log(app, "light"))
        QTimer.singleShot(4000, lambda: self.switch_and_log(app, "dark"))
        QTimer.singleShot(6000, lambda: self.switch_and_log(app, "light"))
        QTimer.singleShot(8000, lambda: self.switch_and_log(app, "dark"))
        QTimer.singleShot(10000, lambda: print("\n✅ Test complete! Check if terminal colors changed each time."))

    def switch_and_log(self, app, theme_name):
        print(f"\n🔄 Switching to: {theme_name}")
        app.set_theme(theme_name)


app = ThemedApplication(sys.argv)
app.set_theme("dark")
window = TestWindow()
window.show()
sys.exit(app.exec())
