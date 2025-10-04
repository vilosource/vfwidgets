"""Theme selection dialog for ViloxTerm."""

from typing import Optional

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication, QWidget


class ThemeDialog(QDialog):
    """Modal dialog for theme selection.

    Provides buttons for selecting from available themes:
    - Dark theme
    - Light theme
    - Default theme
    - Minimal theme
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize theme selection dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Theme")
        self.setModal(True)
        self.resize(300, 200)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Theme buttons
        themes = ["dark", "light", "default", "minimal"]
        for theme in themes:
            btn = QPushButton(f"{theme.capitalize()} Theme")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, t=theme: self.select_theme(t))
            layout.addWidget(btn)

    def select_theme(self, theme_name: str) -> None:
        """Apply selected theme and close dialog.

        Args:
            theme_name: Name of theme to apply
        """
        app = QApplication.instance()
        if hasattr(app, "set_theme"):
            app.set_theme(theme_name)
        self.accept()
