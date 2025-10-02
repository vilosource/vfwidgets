#!/usr/bin/env python3
"""Example 03: Custom Themed Widgets.
==================================

Shows how to create custom widgets with sophisticated theming.
Demonstrates property mapping, theme inheritance, and custom painting.

What this demonstrates:
- Creating custom widgets with theme support
- Mapping theme properties to widget attributes
- Custom painting with theme colors
- Responding to theme changes with animations
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedProgressBar(ThemedWidget, QWidget):
    """A custom progress bar that uses theme colors."""

    theme_config = {
        'bar_bg': 'colors.background',
        'bar_fg': 'colors.primary',
        'bar_accent': 'colors.accent',
        'text_color': 'colors.foreground'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self._animated_progress = 0
        self.animation = QPropertyAnimation(self, b"animated_progress")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.setMinimumHeight(30)

    def get_animated_progress(self):
        return self._animated_progress

    def set_animated_progress(self, value):
        self._animated_progress = value
        self.update()

    animated_progress = Property(int, get_animated_progress, set_animated_progress)

    def set_progress(self, value):
        """Set progress with animation."""
        value = max(0, min(100, value))
        self.animation.setStartValue(self._progress)
        self.animation.setEndValue(value)
        self.animation.start()
        self._progress = value

    def paintEvent(self, event):
        """Custom painting using theme colors."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get theme colors
        bg = QColor(getattr(self.theme, 'bar_bg', '#f0f0f0'))
        fg = QColor(getattr(self.theme, 'bar_fg', '#0066cc'))
        accent = QColor(getattr(self.theme, 'bar_accent', '#00aa00'))
        text_color = QColor(getattr(self.theme, 'text_color', '#000000'))

        # Draw background
        painter.fillRect(self.rect(), QBrush(bg))

        # Draw progress bar
        if self._animated_progress > 0:
            progress_width = int(self.width() * self._animated_progress / 100)
            progress_rect = QRect(0, 0, progress_width, self.height())

            # Gradient effect
            gradient_color = fg if self._animated_progress < 100 else accent
            painter.fillRect(progress_rect, QBrush(gradient_color))

        # Draw text
        painter.setPen(QPen(text_color))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self._progress}%")


class ThemedCard(ThemedWidget, QWidget):
    """A card widget with shadow and hover effects."""

    theme_config = {
        'card_bg': 'colors.background',
        'card_border': 'colors.border',
        'card_shadow': 'colors.primary',
        'title_color': 'colors.primary',
        'content_color': 'colors.foreground'
    }

    def __init__(self, title="Card Title", content="Card content", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.content_text = content
        self.hovered = False
        self.setup_ui()
        self.setMouseTracking(True)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.title = QLabel(self.title_text)
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title)

        self.content = QLabel(self.content_text)
        self.content.setWordWrap(True)
        layout.addWidget(self.content)

        layout.addStretch()

    def on_theme_changed(self):
        """Update card styling when theme changes."""
        bg = getattr(self.theme, 'card_bg', '#ffffff')
        border = getattr(self.theme, 'card_border', '#cccccc')
        shadow = getattr(self.theme, 'card_shadow', '#888888')
        title_color = getattr(self.theme, 'title_color', '#0066cc')
        content_color = getattr(self.theme, 'content_color', '#333333')

        # Apply card style with shadow
        self.setStyleSheet(f"""
            ThemedCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            ThemedCard:hover {{
                border: 2px solid {shadow};
            }}
        """)

        self.title.setStyleSheet(f"color: {title_color}; font-size: 16px; font-weight: bold;")
        self.content.setStyleSheet(f"color: {content_color}; font-size: 14px;")

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()


class CustomWidgetShowcase(ThemedWidget, QWidget):
    """Main widget showcasing custom themed widgets."""

    theme_config = {
        'main_bg': 'colors.background',
        'main_fg': 'colors.foreground'
    }

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Custom Themed Widgets")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Progress bars
        progress_label = QLabel("Themed Progress Bars:")
        layout.addWidget(progress_label)

        self.progress1 = ThemedProgressBar()
        self.progress1.set_progress(30)
        layout.addWidget(self.progress1)

        self.progress2 = ThemedProgressBar()
        self.progress2.set_progress(75)
        layout.addWidget(self.progress2)

        self.progress3 = ThemedProgressBar()
        self.progress3.set_progress(100)
        layout.addWidget(self.progress3)

        # Control buttons
        button_layout = QHBoxLayout()

        increase_btn = QPushButton("Increase Progress")
        increase_btn.clicked.connect(self.increase_progress)
        button_layout.addWidget(increase_btn)

        decrease_btn = QPushButton("Decrease Progress")
        decrease_btn.clicked.connect(self.decrease_progress)
        button_layout.addWidget(decrease_btn)

        layout.addLayout(button_layout)

        # Cards
        cards_label = QLabel("Themed Cards:")
        layout.addWidget(cards_label)

        cards_layout = QHBoxLayout()

        card1 = ThemedCard(
            "Features",
            "• Automatic theming\n• Custom painting\n• Property mapping"
        )
        cards_layout.addWidget(card1)

        card2 = ThemedCard(
            "Benefits",
            "• Consistent look\n• Easy maintenance\n• Theme switching"
        )
        cards_layout.addWidget(card2)

        card3 = ThemedCard(
            "Usage",
            "• Inherit ThemedWidget\n• Define theme_config\n• Handle on_theme_changed"
        )
        cards_layout.addWidget(card3)

        layout.addLayout(cards_layout)

        # Set minimum size
        self.setMinimumSize(600, 500)

    def increase_progress(self):
        """Increase all progress bars."""
        for progress in [self.progress1, self.progress2, self.progress3]:
            progress.set_progress(min(100, progress._progress + 10))

    def decrease_progress(self):
        """Decrease all progress bars."""
        for progress in [self.progress1, self.progress2, self.progress3]:
            progress.set_progress(max(0, progress._progress - 10))

    def on_theme_changed(self):
        """Update main widget styling."""
        bg = getattr(self.theme, 'main_bg', '#ffffff')
        fg = getattr(self.theme, 'main_fg', '#000000')

        self.setStyleSheet(f"""
            CustomWidgetShowcase {{
                background-color: {bg};
                color: {fg};
            }}
            QLabel {{
                color: {fg};
            }}
            QPushButton {{
                padding: 8px 15px;
                background-color: {fg};
                color: {bg};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)


def main():
    app = ThemedApplication(sys.argv)

    # Use dark theme to show off the custom widgets
    app.set_theme('dark')

    showcase = CustomWidgetShowcase()
    showcase.setWindowTitle("Custom Themed Widgets")
    showcase.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
