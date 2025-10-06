"""Debug script to test ThemeComboBox."""

import sys

from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.widgets import ThemeComboBox


class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThemeComboBox Debug")
        self.resize(500, 300)

        self.app = ThemedApplication.instance()

        central = QWidget()
        layout = QVBoxLayout(central)

        # Status label
        self.status_label = QLabel()
        self.update_status()
        layout.addWidget(self.status_label)

        # Combo
        self.combo = ThemeComboBox()
        layout.addWidget(self.combo)

        # Monitor combo changes
        self.combo.currentTextChanged.connect(self.on_combo_changed)

        # Monitor app theme changes
        self.app.theme_changed.connect(self.on_app_theme_changed)

        # Manual test button
        btn = QPushButton("Manually set theme to 'light'")
        btn.clicked.connect(lambda: self.app.set_theme("light"))
        layout.addWidget(btn)

        self.setCentralWidget(central)

    def on_combo_changed(self, text):
        print(f"[COMBO CHANGED] Text: '{text}'")
        self.update_status()

    def on_app_theme_changed(self, theme_name):
        print(f"[APP THEME CHANGED] Theme: '{theme_name}'")
        self.update_status()

    def update_status(self):
        current = self.app.current_theme_name
        combo_text = self.combo.currentText() if hasattr(self, "combo") else "N/A"
        self.status_label.setText(
            f"App theme: {current}\n"
            f"Combo shows: {combo_text}\n"
            f"Syncing: {getattr(self.combo, '_syncing', False) if hasattr(self, 'combo') else False}"
        )


def main():
    app = ThemedApplication(sys.argv)
    app.set_theme("dark")

    window = DebugWindow()
    window.show()

    print("\n=== INITIAL STATE ===")
    print(f"App theme: {app.current_theme_name}")
    print(f"Combo shows: {window.combo.currentText()}")
    print(f"Available themes: {[t.name for t in app.get_available_themes()]}")
    print("\nTry changing the combo selection and watch the output...\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
