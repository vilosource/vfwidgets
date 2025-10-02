#!/usr/bin/env python3
"""Tutorial 05: Custom Widget.
==========================

This tutorial shows how to build a custom themed widget from scratch.

What you'll learn:
- Creating custom painted widgets
- Implementing theme-aware painting
- Custom properties and signals
- Widget composition
- Performance considerations
"""

import math
import sys

from PySide6.QtCore import QRect, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedGauge(ThemedWidget):
    """A custom gauge widget that demonstrates themed painting.

    This widget shows how to:
    - Create custom painted widgets
    - Use theme colors in painting
    - Implement custom properties
    - Emit custom signals
    """

    # Custom signal
    value_changed = Signal(float)

    theme_config = {
        'bg': 'gauge.background',
        'fg': 'gauge.foreground',
        'needle': 'gauge.needle',
        'scale': 'gauge.scale',
        'value_bg': 'gauge.value.background',
        'value_fg': 'gauge.value.foreground',
        'danger': 'gauge.danger',
        'warning': 'gauge.warning',
        'safe': 'gauge.safe'
    }

    def __init__(self, min_value=0, max_value=100, parent=None):
        super().__init__(parent)
        self._min_value = min_value
        self._max_value = max_value
        self._value = min_value
        self._title = "Gauge"

        self.setMinimumSize(200, 200)

    @property
    def value(self):
        """Get current gauge value."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Set gauge value with bounds checking."""
        new_value = max(self._min_value, min(self._max_value, new_value))
        if new_value != self._value:
            self._value = new_value
            self.value_changed.emit(new_value)
            self.update()  # Trigger repaint

    @property
    def title(self):
        """Get gauge title."""
        return self._title

    @title.setter
    def title(self, new_title):
        """Set gauge title."""
        self._title = new_title
        self.update()

    def on_theme_changed(self):
        """Called when theme changes."""
        self.update()  # Repaint with new theme colors

    def paintEvent(self, event):
        """Custom painting with theme colors."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get theme colors
        bg_color = QColor(self.theme.get('bg', '#ffffff'))
        fg_color = QColor(self.theme.get('fg', '#000000'))
        needle_color = QColor(self.theme.get('needle', '#ff0000'))
        scale_color = QColor(self.theme.get('scale', '#666666'))
        QColor(self.theme.get('value_bg', '#f0f0f0'))
        QColor(self.theme.get('value_fg', '#000000'))
        danger_color = QColor(self.theme.get('danger', '#ff0000'))
        warning_color = QColor(self.theme.get('warning', '#ffaa00'))
        safe_color = QColor(self.theme.get('safe', '#00aa00'))

        # Calculate dimensions
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = size // 2

        # Draw background
        painter.fillRect(rect, bg_color)

        # Draw gauge background arc
        gauge_rect = QRect(center_x - radius, center_y - radius, size, size)
        painter.setPen(QPen(scale_color, 3))
        painter.drawArc(gauge_rect, 30 * 16, 120 * 16)  # 120 degree arc

        # Draw colored zones
        zone_width = 8
        zone_rect = QRect(center_x - radius + zone_width, center_y - radius + zone_width,
                         size - 2 * zone_width, size - 2 * zone_width)

        # Safe zone (green)
        painter.setPen(QPen(safe_color, zone_width))
        painter.drawArc(zone_rect, 30 * 16, 40 * 16)

        # Warning zone (yellow)
        painter.setPen(QPen(warning_color, zone_width))
        painter.drawArc(zone_rect, 70 * 16, 40 * 16)

        # Danger zone (red)
        painter.setPen(QPen(danger_color, zone_width))
        painter.drawArc(zone_rect, 110 * 16, 40 * 16)

        # Draw scale marks
        painter.setPen(QPen(scale_color, 2))
        for i in range(11):  # 0 to 100 in steps of 10
            angle = 30 + (120 * i / 10)  # Map to gauge arc
            angle_rad = math.radians(angle)

            # Outer point
            outer_x = center_x + (radius - 10) * math.cos(angle_rad)
            outer_y = center_y + (radius - 10) * math.sin(angle_rad)

            # Inner point
            inner_x = center_x + (radius - 25) * math.cos(angle_rad)
            inner_y = center_y + (radius - 25) * math.sin(angle_rad)

            painter.drawLine(outer_x, outer_y, inner_x, inner_y)

            # Draw scale numbers
            number_x = center_x + (radius - 35) * math.cos(angle_rad)
            number_y = center_y + (radius - 35) * math.sin(angle_rad)

            painter.setPen(QPen(fg_color))
            painter.setFont(QFont("Arial", 8))
            value_text = str(int(self._min_value + (self._max_value - self._min_value) * i / 10))
            painter.drawText(number_x - 10, number_y + 5, value_text)

        # Draw needle
        value_ratio = (self._value - self._min_value) / (self._max_value - self._min_value)
        needle_angle = 30 + 120 * value_ratio
        needle_angle_rad = math.radians(needle_angle)

        painter.setPen(QPen(needle_color, 4))
        needle_x = center_x + (radius - 30) * math.cos(needle_angle_rad)
        needle_y = center_y + (radius - 30) * math.sin(needle_angle_rad)
        painter.drawLine(center_x, center_y, needle_x, needle_y)

        # Draw center circle
        painter.setBrush(QBrush(needle_color))
        painter.setPen(QPen(needle_color))
        painter.drawEllipse(center_x - 5, center_y - 5, 10, 10)

        # Draw title
        painter.setPen(QPen(fg_color))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        title_rect = QRect(0, center_y + radius - 40, rect.width(), 20)
        painter.drawText(title_rect, Qt.AlignCenter, self._title)

        # Draw value
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        value_rect = QRect(0, center_y + radius - 20, rect.width(), 20)
        painter.drawText(value_rect, Qt.AlignCenter, f"{self._value:.1f}")


class ThemedProgressRing(ThemedWidget):
    """A circular progress ring widget."""

    theme_config = {
        'bg': 'progress.background',
        'fg': 'progress.foreground',
        'fill': 'progress.fill',
        'text': 'progress.text'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0  # 0.0 to 1.0
        self.setMinimumSize(150, 150)

    @property
    def progress(self):
        """Get progress value (0.0 to 1.0)."""
        return self._progress

    @progress.setter
    def progress(self, value):
        """Set progress value."""
        self._progress = max(0.0, min(1.0, value))
        self.update()

    def on_theme_changed(self):
        """Theme change handler."""
        self.update()

    def paintEvent(self, event):
        """Paint the progress ring."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get theme colors
        bg_color = QColor(self.theme.get('bg', '#f0f0f0'))
        QColor(self.theme.get('fg', '#333333'))
        fill_color = QColor(self.theme.get('fill', '#007bff'))
        text_color = QColor(self.theme.get('text', '#000000'))

        # Calculate dimensions
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = size // 2

        # Draw background ring
        painter.setPen(QPen(bg_color, 10))
        ring_rect = QRect(center_x - radius, center_y - radius, size, size)
        painter.drawArc(ring_rect, 0, 360 * 16)

        # Draw progress arc
        painter.setPen(QPen(fill_color, 10))
        span_angle = int(360 * self._progress * 16)
        painter.drawArc(ring_rect, 90 * 16, -span_angle)  # Start from top

        # Draw percentage text
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        percentage = int(self._progress * 100)
        text_rect = QRect(center_x - 30, center_y - 10, 60, 20)
        painter.drawText(text_rect, Qt.AlignCenter, f"{percentage}%")


class CustomWidgetDemo(ThemedWidget):
    """Demo showcasing custom themed widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        """Set up the demo UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Custom Themed Widgets")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Widgets layout
        widgets_layout = QHBoxLayout()

        # Gauge
        gauge_layout = QVBoxLayout()
        gauge_layout.addWidget(QLabel("Themed Gauge"))

        self.gauge = ThemedGauge(0, 100)
        self.gauge.title = "Temperature"
        self.gauge.value = 25
        gauge_layout.addWidget(self.gauge)

        # Gauge controls
        gauge_controls = QHBoxLayout()
        self.gauge_slider = QSlider(Qt.Horizontal)
        self.gauge_slider.setRange(0, 100)
        self.gauge_slider.setValue(25)
        self.gauge_slider.valueChanged.connect(self.gauge.value.fset)
        gauge_controls.addWidget(QLabel("Value:"))
        gauge_controls.addWidget(self.gauge_slider)

        gauge_layout.addLayout(gauge_controls)
        widgets_layout.addLayout(gauge_layout)

        # Progress ring
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("Progress Ring"))

        self.progress_ring = ThemedProgressRing()
        self.progress_ring.progress = 0.65
        progress_layout.addWidget(self.progress_ring)

        # Progress controls
        progress_controls = QHBoxLayout()
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(65)
        self.progress_slider.valueChanged.connect(
            lambda v: setattr(self.progress_ring, 'progress', v / 100.0)
        )
        progress_controls.addWidget(QLabel("Progress:"))
        progress_controls.addWidget(self.progress_slider)

        progress_layout.addLayout(progress_controls)
        widgets_layout.addLayout(progress_layout)

        layout.addLayout(widgets_layout)

        # Animation controls
        anim_layout = QHBoxLayout()

        self.animate_btn = QPushButton("Start Animation")
        self.animate_btn.clicked.connect(self.toggle_animation)
        anim_layout.addWidget(self.animate_btn)

        # Theme controls
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        anim_layout.addWidget(light_btn)

        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        anim_layout.addWidget(dark_btn)

        layout.addLayout(anim_layout)

    def setup_animation(self):
        """Set up animation timer."""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_widgets)
        self.animation_value = 0
        self.animation_direction = 1

    def toggle_animation(self):
        """Toggle widget animation."""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.animate_btn.setText("Start Animation")
        else:
            self.animation_timer.start(50)  # 50ms intervals
            self.animate_btn.setText("Stop Animation")

    def animate_widgets(self):
        """Animate the custom widgets."""
        # Update animation value
        self.animation_value += self.animation_direction * 2

        if self.animation_value >= 100:
            self.animation_direction = -1
        elif self.animation_value <= 0:
            self.animation_direction = 1

        # Update widgets
        self.gauge.value = self.animation_value
        self.gauge_slider.setValue(self.animation_value)

        progress = self.animation_value / 100.0
        self.progress_ring.progress = progress
        self.progress_slider.setValue(self.animation_value)

    def switch_theme(self, theme_name):
        """Switch theme."""
        app = ThemedApplication.instance()
        app.set_theme(theme_name)


def main():
    """Main function for custom widget demo."""
    print("Tutorial 05: Custom Widget")
    print("=" * 30)

    app = ThemedApplication(sys.argv)

    # Define themes with custom widget properties
    light_theme = {
        'name': 'light',
        'gauge': {
            'background': '#ffffff',
            'foreground': '#333333',
            'needle': '#ff0000',
            'scale': '#666666',
            'value': {'background': '#f0f0f0', 'foreground': '#000000'},
            'danger': '#ff0000',
            'warning': '#ffaa00',
            'safe': '#00aa00'
        },
        'progress': {
            'background': '#e0e0e0',
            'foreground': '#333333',
            'fill': '#007bff',
            'text': '#000000'
        }
    }

    dark_theme = {
        'name': 'dark',
        'gauge': {
            'background': '#2d2d2d',
            'foreground': '#ffffff',
            'needle': '#ff6666',
            'scale': '#aaaaaa',
            'value': {'background': '#3a3a3a', 'foreground': '#ffffff'},
            'danger': '#ff6666',
            'warning': '#ffcc66',
            'safe': '#66ff66'
        },
        'progress': {
            'background': '#555555',
            'foreground': '#ffffff',
            'fill': '#66aaff',
            'text': '#ffffff'
        }
    }

    app.register_theme('light', light_theme)
    app.register_theme('dark', dark_theme)
    app.set_theme('light')

    # Create and show demo
    widget = CustomWidgetDemo()
    widget.setWindowTitle("Tutorial 05: Custom Widget")
    widget.setMinimumSize(600, 400)
    widget.show()

    print("\nCustom widget demo ready!")
    print("- Use sliders to control widget values")
    print("- Click 'Start Animation' for automatic animation")
    print("- Switch themes to see color changes")

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
