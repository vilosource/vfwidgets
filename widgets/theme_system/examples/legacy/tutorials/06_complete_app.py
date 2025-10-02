#!/usr/bin/env python3
"""
Tutorial 06: Complete Application
================================

This tutorial puts everything together into a complete themed application.

What you'll learn:
- Building a complete application with themes
- Combining multiple widgets and layouts
- Application-wide theme management
- Settings persistence
- Best practices for themed applications

This is the culmination of all previous tutorials!
"""

import sys

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import custom widgets from previous tutorials
from tutorials.tutorial_05_custom_widget import ThemedGauge, ThemedProgressRing

from vfwidgets_theme import ThemedApplication, ThemedWidget


class ThemedMainWindow(ThemedWidget, QMainWindow):
    """Main application window with complete theming."""

    theme_config = {
        'bg': 'window.background',
        'fg': 'window.foreground',
        'menubar_bg': 'menubar.background',
        'menubar_fg': 'menubar.foreground',
        'statusbar_bg': 'statusbar.background',
        'statusbar_fg': 'statusbar.foreground'
    }

    def __init__(self):
        super().__init__()
        self.settings = QSettings("VFWidgets", "ThemeDemo")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the complete application UI."""
        self.setWindowTitle("Complete Themed Application")
        self.setMinimumSize(1000, 700)

        # Create menu bar
        self.create_menu_bar()

        # Create main content area
        self.create_main_content()

        # Create dock widgets
        self.create_dock_widgets()

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create themed menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        # Theme submenu
        theme_menu = view_menu.addMenu('Theme')

        themes = ['light', 'dark', 'blue', 'purple', 'forest']
        for theme in themes:
            action = QAction(theme.title(), self)
            action.triggered.connect(lambda checked, t=theme: self.switch_theme(t))
            theme_menu.addAction(action)

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        preferences_action = QAction('Preferences', self)
        preferences_action.triggered.connect(self.show_preferences)
        settings_menu.addAction(preferences_action)

    def create_main_content(self):
        """Create main content area with tabs."""
        # Central widget with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Editor tab
        self.create_editor_tab()

        # Dashboard tab
        self.create_dashboard_tab()

        # Data tab
        self.create_data_tab()

    def create_editor_tab(self):
        """Create text editor tab."""
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)

        # Toolbar
        toolbar = QHBoxLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems(['Plain Text', 'Markdown', 'HTML'])
        toolbar.addWidget(QLabel("Format:"))
        toolbar.addWidget(self.format_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.update_editor_font)
        toolbar.addWidget(QLabel("Font Size:"))
        toolbar.addWidget(self.font_size_spin)

        toolbar.addStretch()

        word_count_label = QLabel("Words: 0")
        toolbar.addWidget(word_count_label)

        layout.addLayout(toolbar)

        # Text editor
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Start writing your document here...")
        self.text_editor.textChanged.connect(
            lambda: self.update_word_count(word_count_label)
        )
        layout.addWidget(self.text_editor)

        self.tab_widget.addTab(editor_widget, "Editor")

    def create_dashboard_tab(self):
        """Create dashboard with custom widgets."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)

        # Title
        title = QLabel("System Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Metrics row
        metrics_layout = QHBoxLayout()

        # CPU gauge
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout(cpu_group)

        self.cpu_gauge = ThemedGauge(0, 100)
        self.cpu_gauge.title = "CPU"
        self.cpu_gauge.value = 45
        cpu_layout.addWidget(self.cpu_gauge)

        metrics_layout.addWidget(cpu_group)

        # Memory gauge
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout(memory_group)

        self.memory_gauge = ThemedGauge(0, 100)
        self.memory_gauge.title = "Memory"
        self.memory_gauge.value = 67
        memory_layout.addWidget(self.memory_gauge)

        metrics_layout.addWidget(memory_group)

        # Disk progress
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout(disk_group)

        self.disk_progress = ThemedProgressRing()
        self.disk_progress.progress = 0.34
        disk_layout.addWidget(self.disk_progress)

        metrics_layout.addWidget(disk_group)

        layout.addLayout(metrics_layout)

        # Controls
        controls_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        controls_layout.addWidget(refresh_btn)

        auto_refresh_check = QCheckBox("Auto Refresh")
        auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(auto_refresh_check)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self.tab_widget.addTab(dashboard_widget, "Dashboard")

        # Set up auto refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)

    def create_data_tab(self):
        """Create data management tab."""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)

        # Splitter for data view
        splitter = QSplitter(Qt.Horizontal)

        # File list
        file_group = QGroupBox("Files")
        file_layout = QVBoxLayout(file_group)

        self.file_list = QListWidget()
        sample_files = [
            "document1.txt", "report.pdf", "data.csv",
            "image.jpg", "presentation.pptx", "notes.md"
        ]
        for file in sample_files:
            self.file_list.addItem(file)

        self.file_list.itemClicked.connect(self.on_file_selected)
        file_layout.addWidget(self.file_list)

        splitter.addWidget(file_group)

        # File content preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.file_preview.setPlaceholderText("Select a file to preview...")
        preview_layout.addWidget(self.file_preview)

        splitter.addWidget(preview_group)

        splitter.setSizes([300, 500])
        layout.addWidget(splitter)

        self.tab_widget.addTab(data_widget, "Data")

    def create_dock_widgets(self):
        """Create dockable widgets."""
        # Properties dock
        props_dock = QDockWidget("Properties", self)
        props_widget = QWidget()
        props_layout = QFormLayout(props_widget)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['light', 'dark', 'blue', 'purple', 'forest'])
        self.theme_combo.currentTextChanged.connect(self.switch_theme)
        props_layout.addRow("Theme:", self.theme_combo)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        props_layout.addRow("Zoom:", self.zoom_slider)

        self.auto_save_check = QCheckBox("Auto Save")
        self.auto_save_check.setChecked(True)
        props_layout.addRow("", self.auto_save_check)

        props_dock.setWidget(props_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, props_dock)

        # Console dock
        console_dock = QDockWidget("Console", self)
        self.console = QTextEdit()
        self.console.setMaximumHeight(150)
        self.console.setPlaceholderText("Application console output...")
        console_dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, console_dock)

    def create_status_bar(self):
        """Create themed status bar."""
        status_bar = self.statusBar()

        # Status message
        status_bar.showMessage("Ready")

        # Theme indicator
        self.theme_label = QLabel("Theme: Light")
        status_bar.addPermanentWidget(self.theme_label)

        # Time display
        self.time_label = QLabel()
        status_bar.addPermanentWidget(self.time_label)

        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def on_theme_changed(self):
        """Handle theme changes."""
        self.update_styling()

    def update_styling(self):
        """Apply theme styling to main window."""
        bg = self.theme.get('bg', '#ffffff')
        fg = self.theme.get('fg', '#000000')
        menubar_bg = self.theme.get('menubar_bg', '#f0f0f0')
        menubar_fg = self.theme.get('menubar_fg', '#000000')
        statusbar_bg = self.theme.get('statusbar_bg', '#e0e0e0')
        statusbar_fg = self.theme.get('statusbar_fg', '#000000')

        self.setStyleSheet(f"""
        QMainWindow {{
            background-color: {bg};
            color: {fg};
        }}

        QMenuBar {{
            background-color: {menubar_bg};
            color: {menubar_fg};
            border-bottom: 1px solid #ccc;
        }}

        QStatusBar {{
            background-color: {statusbar_bg};
            color: {statusbar_fg};
            border-top: 1px solid #ccc;
        }}
        """)

    def new_document(self):
        """Create new document."""
        self.text_editor.clear()
        self.log_message("New document created")

    def open_document(self):
        """Open document (simulated)."""
        self.log_message("Document opened")

    def save_document(self):
        """Save document (simulated)."""
        self.log_message("Document saved")

    def switch_theme(self, theme_name):
        """Switch application theme."""
        app = ThemedApplication.instance()
        try:
            app.set_theme(theme_name)
            self.theme_label.setText(f"Theme: {theme_name.title()}")
            self.log_message(f"Switched to {theme_name} theme")

            # Update theme combo if needed
            index = self.theme_combo.findText(theme_name)
            if index >= 0 and self.theme_combo.currentIndex() != index:
                self.theme_combo.setCurrentIndex(index)

        except Exception as e:
            self.log_message(f"Error switching theme: {e}")

    def show_preferences(self):
        """Show preferences dialog."""
        self.log_message("Preferences dialog would open here")

    def update_editor_font(self, size):
        """Update editor font size."""
        font = self.text_editor.font()
        font.setPointSize(size)
        self.text_editor.setFont(font)

    def update_word_count(self, label):
        """Update word count display."""
        text = self.text_editor.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        label.setText(f"Words: {word_count}")

    def refresh_dashboard(self):
        """Refresh dashboard data."""
        import random

        # Simulate new data
        self.cpu_gauge.value = random.randint(20, 90)
        self.memory_gauge.value = random.randint(30, 85)
        self.disk_progress.progress = random.randint(20, 80) / 100.0

        self.log_message("Dashboard data refreshed")

    def toggle_auto_refresh(self, enabled):
        """Toggle auto refresh."""
        if enabled:
            self.refresh_timer.start(5000)  # 5 seconds
            self.log_message("Auto refresh enabled")
        else:
            self.refresh_timer.stop()
            self.log_message("Auto refresh disabled")

    def on_file_selected(self, item):
        """Handle file selection."""
        filename = item.text()
        # Simulate file content
        content = f"Content of {filename}\n\n"
        if filename.endswith('.txt'):
            content += "This is a text file with sample content."
        elif filename.endswith('.csv'):
            content += "Name,Age,City\nJohn,25,New York\nJane,30,London"
        else:
            content += "Binary file - cannot preview"

        self.file_preview.setPlainText(content)
        self.log_message(f"Selected file: {filename}")

    def log_message(self, message):
        """Log message to console."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")

    def update_time(self):
        """Update time display."""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def load_settings(self):
        """Load application settings."""
        theme = self.settings.value("theme", "light")
        font_size = int(self.settings.value("font_size", 12))
        auto_save = self.settings.value("auto_save", True, type=bool)

        # Apply loaded settings
        self.switch_theme(theme)
        self.font_size_spin.setValue(font_size)
        self.auto_save_check.setChecked(auto_save)

        self.log_message("Settings loaded")

    def save_settings(self):
        """Save application settings."""
        current_theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()
        auto_save = self.auto_save_check.isChecked()

        self.settings.setValue("theme", current_theme)
        self.settings.setValue("font_size", font_size)
        self.settings.setValue("auto_save", auto_save)

        self.log_message("Settings saved")

    def closeEvent(self, event):
        """Handle application close."""
        self.save_settings()
        event.accept()


def create_application_themes():
    """Create comprehensive themes for the complete application."""
    themes = {
        'light': {
            'name': 'light',
            'window': {'background': '#ffffff', 'foreground': '#333333'},
            'menubar': {'background': '#f0f0f0', 'foreground': '#000000'},
            'statusbar': {'background': '#e0e0e0', 'foreground': '#333333'},
            'gauge': {
                'background': '#ffffff', 'foreground': '#333333',
                'needle': '#ff0000', 'scale': '#666666',
                'value': {'background': '#f0f0f0', 'foreground': '#000000'},
                'danger': '#ff0000', 'warning': '#ffaa00', 'safe': '#00aa00'
            },
            'progress': {
                'background': '#e0e0e0', 'foreground': '#333333',
                'fill': '#007bff', 'text': '#000000'
            }
        },
        'dark': {
            'name': 'dark',
            'window': {'background': '#2d2d2d', 'foreground': '#ffffff'},
            'menubar': {'background': '#3a3a3a', 'foreground': '#ffffff'},
            'statusbar': {'background': '#1a1a1a', 'foreground': '#ffffff'},
            'gauge': {
                'background': '#2d2d2d', 'foreground': '#ffffff',
                'needle': '#ff6666', 'scale': '#aaaaaa',
                'value': {'background': '#3a3a3a', 'foreground': '#ffffff'},
                'danger': '#ff6666', 'warning': '#ffcc66', 'safe': '#66ff66'
            },
            'progress': {
                'background': '#555555', 'foreground': '#ffffff',
                'fill': '#66aaff', 'text': '#ffffff'
            }
        },
        'blue': {
            'name': 'blue',
            'window': {'background': '#e3f2fd', 'foreground': '#0d47a1'},
            'menubar': {'background': '#bbdefb', 'foreground': '#1565c0'},
            'statusbar': {'background': '#90caf9', 'foreground': '#0d47a1'},
            'gauge': {
                'background': '#e3f2fd', 'foreground': '#0d47a1',
                'needle': '#d32f2f', 'scale': '#1976d2',
                'value': {'background': '#ffffff', 'foreground': '#0d47a1'},
                'danger': '#d32f2f', 'warning': '#f57c00', 'safe': '#388e3c'
            },
            'progress': {
                'background': '#bbdefb', 'foreground': '#0d47a1',
                'fill': '#1976d2', 'text': '#0d47a1'
            }
        },
        'purple': {
            'name': 'purple',
            'window': {'background': '#f3e5f5', 'foreground': '#4a148c'},
            'menubar': {'background': '#e1bee7', 'foreground': '#6a1b9a'},
            'statusbar': {'background': '#ce93d8', 'foreground': '#4a148c'},
            'gauge': {
                'background': '#f3e5f5', 'foreground': '#4a148c',
                'needle': '#d32f2f', 'scale': '#7b1fa2',
                'value': {'background': '#ffffff', 'foreground': '#4a148c'},
                'danger': '#d32f2f', 'warning': '#f57c00', 'safe': '#388e3c'
            },
            'progress': {
                'background': '#e1bee7', 'foreground': '#4a148c',
                'fill': '#7b1fa2', 'text': '#4a148c'
            }
        },
        'forest': {
            'name': 'forest',
            'window': {'background': '#f1f8e9', 'foreground': '#1b5e20'},
            'menubar': {'background': '#c8e6c9', 'foreground': '#2e7d32'},
            'statusbar': {'background': '#a5d6a7', 'foreground': '#1b5e20'},
            'gauge': {
                'background': '#f1f8e9', 'foreground': '#1b5e20',
                'needle': '#d32f2f', 'scale': '#388e3c',
                'value': {'background': '#ffffff', 'foreground': '#1b5e20'},
                'danger': '#d32f2f', 'warning': '#f57c00', 'safe': '#388e3c'
            },
            'progress': {
                'background': '#c8e6c9', 'foreground': '#1b5e20',
                'fill': '#388e3c', 'text': '#1b5e20'
            }
        }
    }
    return themes


def main():
    """Main function for complete application demo."""
    print("Tutorial 06: Complete Application")
    print("=" * 35)

    app = ThemedApplication(sys.argv)

    # Register all themes
    themes = create_application_themes()
    for name, theme in themes.items():
        app.register_theme(name, theme)
        print(f"Registered theme: {name}")

    # Set initial theme
    app.set_theme('light')

    # Create and show main window
    window = ThemedMainWindow()
    window.show()

    print("\nComplete themed application ready!")
    print("Features:")
    print("- Multi-tab interface with editor, dashboard, and data views")
    print("- Dockable property and console panels")
    print("- Custom themed widgets (gauges, progress rings)")
    print("- Full menu system with theme switching")
    print("- Settings persistence")
    print("- Real-time updates and animations")

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
