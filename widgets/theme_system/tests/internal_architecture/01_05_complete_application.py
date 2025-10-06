#!/usr/bin/env python3
"""
Complete Application Example

This example demonstrates a complete, real-world application built using
ThemedApplication and ThemedWidget, showcasing the full power of the theme
system in a practical context.

Features demonstrated:
- Complete themed application with multiple windows
- Real-world widget composition and layouts
- Theme persistence and system integration
- VSCode theme importing
- Performance monitoring dashboard
- Memory usage tracking
- Thread-safe background operations
- Plugin-style architecture with theming

Run this example:
    python complete_application.py
"""

import json
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

# Add the source directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from PySide6.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PySide6.QtGui import QAction, QColor, QFont, QPainter
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMenuBar,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    print(
        "PySide6 not available. This example will demonstrate the architecture without full Qt functionality."
    )
    QT_AVAILABLE = False

    # Fallback implementations for architectural demonstration
    class QMainWindow:
        pass

    class QWidget:
        pass

    class QVBoxLayout:
        pass

    class QHBoxLayout:
        pass

    class QGridLayout:
        pass

    class QPushButton:
        def __init__(self, text=""):
            self.text = text

    class QLabel:
        def __init__(self, text=""):
            self.text = text

    class QTextEdit:
        pass

    class QSlider:
        pass

    class QProgressBar:
        pass

    class QMenuBar:
        pass

    class QMenu:
        pass

    class QStatusBar:
        pass

    class QTabWidget:
        pass

    class QGroupBox:
        pass

    class QCheckBox:
        pass

    class QComboBox:
        pass

    class QSpinBox:
        pass

    class QLineEdit:
        pass

    class QTableWidget:
        pass

    class QTableWidgetItem:
        pass

    class QSplitter:
        pass

    class QFrame:
        pass

    class QScrollArea:
        pass

    class QTimer:
        pass

    class QThread:
        pass

    class QAction:
        pass

    class QPainter:
        pass

    class QColor:
        pass

    class QFont:
        pass

    def pyqtSignal(*args):
        pass

    class Qt:
        pass


from vfwidgets_theme.core.theme import ThemeBuilder
from vfwidgets_theme.testing import MemoryProfiler
from vfwidgets_theme.widgets.application import ThemedApplication
from vfwidgets_theme.widgets.base import ThemedWidget
from vfwidgets_theme.widgets.mixins import ThemeableMixin


@dataclass
class ApplicationStats:
    """Application statistics for monitoring."""

    widgets_created: int = 0
    theme_switches: int = 0
    memory_usage: float = 0.0
    uptime: float = 0.0
    active_threads: int = 0


class ThemedMenuBar(QMenuBar, ThemeableMixin):
    """Themed menu bar for the application."""

    def __init__(self):
        super().__init__()
        self.setup_theming(
            {
                "background": "menubar.background",
                "color": "menubar.foreground",
                "selection": "menubar.selection",
            }
        )

    def on_theme_changed(self):
        """Handle theme changes for menu bar."""
        print("🎨 Menu bar theme updated")


class ThemedStatusBar(QStatusBar, ThemeableMixin):
    """Themed status bar showing application status."""

    def __init__(self):
        super().__init__()
        self.setup_theming(
            {
                "background": "statusbar.background",
                "color": "statusbar.foreground",
                "border": "statusbar.border",
            }
        )

        self._status_labels = {}
        self._setup_status_widgets()

    def _setup_status_widgets(self):
        """Set up status widgets."""
        # Create status indicators
        self.showMessage("Application ready")

    def on_theme_changed(self):
        """Handle theme changes for status bar."""
        print("🎨 Status bar theme updated")

    def update_stats(self, stats: ApplicationStats):
        """Update status bar with application statistics."""
        status_text = (
            f"Widgets: {stats.widgets_created} | "
            f"Memory: {stats.memory_usage:.1f}KB | "
            f"Uptime: {stats.uptime:.1f}s"
        )
        self.showMessage(status_text)


class PerformanceMonitorWidget(ThemedWidget):
    """Widget for monitoring application performance."""

    theme_config = {
        "panel_bg": "panel.background",
        "panel_border": "panel.border",
        "text_color": "panel.foreground",
        "success_color": "status.success",
        "warning_color": "status.warning",
        "error_color": "status.error",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._stats_history = []
        self._update_timer = QTimer() if QT_AVAILABLE else None
        self._setup_ui()

        if self._update_timer:
            self._update_timer.timeout.connect(self._update_stats)
            self._update_timer.start(1000)  # Update every second

        print("📊 Performance monitor widget created")

    def _setup_ui(self):
        """Set up the performance monitor UI."""
        if not QT_AVAILABLE:
            return

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Performance Monitor")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Statistics display
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(200)
        layout.addWidget(self.stats_display)

        # Performance charts (simulated)
        self.chart_widget = QLabel("Performance Chart Area")
        self.chart_widget.setMinimumHeight(150)
        self.chart_widget.setStyleSheet("border: 1px solid #ccc; background: #f9f9f9;")
        layout.addWidget(self.chart_widget)

    def on_theme_changed(self):
        """Handle theme changes for performance monitor."""
        print("🎨 Performance monitor theme updated")
        self._update_styling()

    def _update_styling(self):
        """Update widget styling based on current theme."""
        if not QT_AVAILABLE:
            return

        bg = self.theme.get("panel_bg", "#ffffff")
        border = self.theme.get("panel_border", "#cccccc")
        text_color = self.theme.get("text_color", "#000000")

        style = f"""
        QTextEdit {{
            background-color: {bg};
            border: 1px solid {border};
            color: {text_color};
        }}
        """
        if hasattr(self, "stats_display"):
            self.stats_display.setStyleSheet(style)

    def _update_stats(self):
        """Update performance statistics."""
        # Get current application stats
        app = ThemedApplication.instance()
        if app:
            try:
                stats = app.get_performance_statistics()
                self._display_stats(stats)
            except Exception as e:
                print(f"Error updating performance stats: {e}")

    def _display_stats(self, stats: Dict[str, Any]):
        """Display performance statistics."""
        if not QT_AVAILABLE or not hasattr(self, "stats_display"):
            return

        # Format statistics for display
        formatted_stats = "=== APPLICATION PERFORMANCE ===\n\n"
        formatted_stats += f"Themes Available: {stats.get('total_themes', 'N/A')}\n"
        formatted_stats += f"Widgets Registered: {stats.get('total_widgets', 'N/A')}\n"
        formatted_stats += f"Theme Switches: {stats.get('theme_switches', 'N/A')}\n"
        formatted_stats += f"Average Switch Time: {stats.get('average_switch_time', 0):.3f}s\n"
        formatted_stats += f"Widgets Updated: {stats.get('widgets_updated', 'N/A')}\n"
        formatted_stats += f"Cache Hit Rate: {stats.get('hit_rate', 0):.1%}\n"

        # Add timestamp
        formatted_stats += f"\nLast Updated: {time.strftime('%H:%M:%S')}\n"

        self.stats_display.setText(formatted_stats)


class ThemeGalleryWidget(ThemedWidget):
    """Widget showing available themes with preview."""

    theme_config = {
        "gallery_bg": "gallery.background",
        "card_bg": "gallery.card.background",
        "card_border": "gallery.card.border",
        "card_hover": "gallery.card.hover",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._theme_cards = []
        self._setup_ui()
        self._populate_themes()

        print("🖼️ Theme gallery widget created")

    def _setup_ui(self):
        """Set up the theme gallery UI."""
        if not QT_AVAILABLE:
            return

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Theme Gallery")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Scroll area for theme cards
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.grid_layout = QGridLayout(scroll_widget)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

    def _populate_themes(self):
        """Populate the gallery with available themes."""
        app = ThemedApplication.instance()
        if not app:
            return

        try:
            themes = app.get_available_themes()
            current_theme = app.get_current_theme()

            for i, theme in enumerate(themes):
                card = self._create_theme_card(theme, theme == current_theme)
                if QT_AVAILABLE and hasattr(self, "grid_layout"):
                    row = i // 3
                    col = i % 3
                    self.grid_layout.addWidget(card, row, col)

                self._theme_cards.append(card)

        except Exception as e:
            print(f"Error populating theme gallery: {e}")

    def _create_theme_card(self, theme, is_current=False):
        """Create a theme preview card."""
        if not QT_AVAILABLE:
            return QWidget()

        card = QGroupBox()
        if hasattr(theme, "name"):
            title = f"{theme.name} {'(Current)' if is_current else ''}"
        else:
            title = f"{str(theme)} {'(Current)' if is_current else ''}"

        card.setTitle(title)
        card.setMaximumSize(200, 150)

        layout = QVBoxLayout(card)

        # Theme preview (simplified)
        preview = QLabel("Theme Preview")
        preview.setMinimumHeight(80)
        preview.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        layout.addWidget(preview)

        # Apply button
        apply_btn = QPushButton("Apply Theme")
        if hasattr(theme, "name"):
            apply_btn.clicked.connect(lambda: self._apply_theme(theme.name))
        layout.addWidget(apply_btn)

        return card

    def _apply_theme(self, theme_name):
        """Apply selected theme."""
        app = ThemedApplication.instance()
        if app:
            success = app.set_theme(theme_name)
            print(f"🎨 Applied theme '{theme_name}': {success}")

            if success:
                self._refresh_gallery()

    def _refresh_gallery(self):
        """Refresh the theme gallery."""
        # Clear existing cards
        for card in self._theme_cards:
            if hasattr(card, "deleteLater"):
                card.deleteLater()

        self._theme_cards.clear()

        # Repopulate
        self._populate_themes()

    def on_theme_changed(self):
        """Handle theme changes for gallery."""
        print("🎨 Theme gallery updated")
        # Refresh gallery to show current theme indicator
        # self._refresh_gallery()  # Commented to avoid infinite loops


class ContentWidget(ThemedWidget):
    """Main content widget with multiple tabs."""

    theme_config = {
        "content_bg": "content.background",
        "tab_bg": "tab.background",
        "tab_active": "tab.active",
        "text_color": "content.foreground",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()
        print("📄 Content widget created")

    def _setup_ui(self):
        """Set up the content UI with tabs."""
        if not QT_AVAILABLE:
            return

        layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Performance tab
        self.performance_widget = PerformanceMonitorWidget()
        self.tab_widget.addTab(self.performance_widget, "Performance")

        # Theme gallery tab
        self.gallery_widget = ThemeGalleryWidget()
        self.tab_widget.addTab(self.gallery_widget, "Themes")

        # Demo content tab
        demo_widget = self._create_demo_widget()
        self.tab_widget.addTab(demo_widget, "Demo")

        layout.addWidget(self.tab_widget)

    def _create_demo_widget(self):
        """Create a demo widget with various themed controls."""
        if not QT_AVAILABLE:
            return QWidget()

        demo = ThemedWidget()
        layout = QGridLayout(demo)

        # Various themed controls
        controls = [
            ("Button", QPushButton("Themed Button")),
            ("Label", QLabel("Themed Label")),
            ("Line Edit", QLineEdit("Themed text input")),
            ("Combo Box", QComboBox()),
            ("Spin Box", QSpinBox()),
            ("Check Box", QCheckBox("Themed checkbox")),
            ("Slider", QSlider(Qt.Horizontal)),
            ("Progress Bar", QProgressBar()),
        ]

        for i, (label_text, control) in enumerate(controls):
            label = QLabel(label_text + ":")
            layout.addWidget(label, i, 0)
            layout.addWidget(control, i, 1)

        return demo

    def on_theme_changed(self):
        """Handle theme changes for content."""
        print("🎨 Content widget theme updated")


class MainWindow(QMainWindow, ThemeableMixin):
    """Main application window with complete theming."""

    def __init__(self):
        super().__init__()
        self.setup_theming({"window_bg": "window.background", "window_fg": "window.foreground"})

        self._stats = ApplicationStats()
        self._start_time = time.time()

        self._setup_ui()
        self._setup_menu()
        self._start_background_tasks()

        print("🏠 Main window created with theming")

    def _setup_ui(self):
        """Set up the main window UI."""
        if not QT_AVAILABLE:
            return

        self.setWindowTitle("Complete Themed Application")
        self.setMinimumSize(800, 600)

        # Central widget
        self.content_widget = ContentWidget()
        self.setCentralWidget(self.content_widget)

        # Status bar
        self.status_bar = ThemedStatusBar()
        self.setStatusBar(self.status_bar)

        # Update stats
        self._stats.widgets_created = 3  # content, menu, status

    def _setup_menu(self):
        """Set up the application menu."""
        if not QT_AVAILABLE:
            return

        menubar = ThemedMenuBar()
        self.setMenuBar(menubar)

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Theme menu
        theme_menu = menubar.addMenu("Themes")

        # Add theme switching actions
        app = ThemedApplication.instance()
        if app:
            themes = app.get_available_themes()
            for theme in themes[:5]:  # Limit menu items
                theme_name = theme.name if hasattr(theme, "name") else str(theme)
                action = QAction(theme_name, self)
                action.triggered.connect(lambda checked, name=theme_name: self._switch_theme(name))
                theme_menu.addAction(action)

        theme_menu.addSeparator()

        import_vscode_action = QAction("Import VSCode Theme...", self)
        import_vscode_action.triggered.connect(self._import_vscode_theme)
        theme_menu.addAction(import_vscode_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _switch_theme(self, theme_name):
        """Switch to specified theme."""
        app = ThemedApplication.instance()
        if app:
            success = app.set_theme(theme_name)
            print(f"🎨 Switched to theme '{theme_name}': {success}")
            if success:
                self._stats.theme_switches += 1

    def _import_vscode_theme(self):
        """Import a VSCode theme (simplified for demo)."""
        # In a real application, this would open a file dialog
        print("📥 VSCode theme import requested (demo mode)")

        # Create a sample VSCode theme for demonstration
        sample_vscode_theme = {
            "name": "Demo VSCode Theme",
            "type": "dark",
            "colors": {
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "activityBar.background": "#333333",
            },
        }

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_vscode_theme, f)
            temp_file = f.name

        try:
            app = ThemedApplication.instance()
            if app:
                success = app.import_vscode_theme(temp_file)
                print(f"✅ VSCode theme import: {success}")
        finally:
            # Clean up temp file
            Path(temp_file).unlink(missing_ok=True)

    def _show_about(self):
        """Show about dialog (simplified for demo)."""
        print("ℹ️ About: Complete Themed Application Demo")
        print("   Demonstrates ThemedWidget and ThemedApplication")

    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        if QT_AVAILABLE:
            # Stats update timer
            self._stats_timer = QTimer()
            self._stats_timer.timeout.connect(self._update_stats)
            self._stats_timer.start(1000)  # Update every second

            print("⏰ Background monitoring started")

    def _update_stats(self):
        """Update application statistics."""
        self._stats.uptime = time.time() - self._start_time

        # Update memory usage
        profiler = MemoryProfiler()
        self._stats.memory_usage = profiler.get_memory_usage() / 1024  # KB

        # Update status bar
        if hasattr(self, "status_bar"):
            self.status_bar.update_stats(self._stats)

    def on_theme_changed(self):
        """Handle theme changes for main window."""
        print("🎨 Main window theme updated")
        self._stats.theme_switches += 1

    def closeEvent(self, event):
        """Handle window close event."""
        print("🚪 Application closing...")

        # Clean up theming
        if hasattr(self, "cleanup_theming"):
            self.cleanup_theming()

        event.accept()


class CompleteApplication:
    """Complete application demonstration."""

    def __init__(self):
        """Initialize the complete application."""
        print("🚀 Starting Complete Themed Application")
        print("=" * 60)

        # Initialize themed application with full configuration
        self.app = ThemedApplication(
            [],  # Command line args
            theme_config={
                "default_theme": "default",
                "auto_detect_system": True,
                "persist_theme": True,
                "vscode_integration": True,
                "performance_monitoring": True,
            },
        )

        # Enable system theme monitoring
        self.app.enable_system_theme_monitoring()

        # Create main window
        self.main_window = MainWindow()

        # Set up additional features
        self._setup_custom_themes()
        self._demonstrate_features()

        print("✅ Complete application initialized")

    def _setup_custom_themes(self):
        """Set up custom themes for the application."""
        print("\n🎨 Setting up custom themes...")

        # Create application-specific theme
        builder = ThemeBuilder()

        app_theme = (
            builder.set_name("application_theme")
            .set_description("Custom theme for complete application")
            # Window colors
            .add_color("window_bg", "#f8f9fa")
            .add_color("window_fg", "#212529")
            # UI component colors
            .add_color("panel_bg", "#ffffff")
            .add_color("panel_border", "#dee2e6")
            .add_color("button_primary", "#007bff")
            .add_color("button_success", "#28a745")
            # Status colors
            .add_color("status_success", "#28a745")
            .add_color("status_warning", "#ffc107")
            .add_color("status_error", "#dc3545")
            # Component styles
            .add_style(
                "window", {"background-color": "@colors.window_bg", "color": "@colors.window_fg"}
            )
            .add_style(
                "panel",
                {
                    "background-color": "@colors.panel_bg",
                    "border": "1px solid @colors.panel_border",
                },
            )
            .add_style(
                "menubar",
                {
                    "background-color": "@colors.panel_bg",
                    "color": "@colors.window_fg",
                    "selection": "@colors.button_primary",
                },
            )
            .add_style(
                "statusbar",
                {
                    "background-color": "@colors.panel_bg",
                    "color": "@colors.window_fg",
                    "border": "1px solid @colors.panel_border",
                },
            )
            .build()
        )

        # Apply the custom theme
        success = self.app.set_theme(app_theme)
        print(f"✅ Custom application theme applied: {success}")

    def _demonstrate_features(self):
        """Demonstrate application features."""
        print("\n🔧 Demonstrating application features...")

        # Show available themes
        themes = self.app.get_available_themes()
        print(f"📋 Available themes: {len(themes)}")
        for theme in themes:
            name = theme.name if hasattr(theme, "name") else str(theme)
            print(f"   - {name}")

        # Show performance stats
        stats = self.app.get_performance_statistics()
        print(f"📊 Performance stats: {len(stats)} metrics tracked")

        # Demonstrate theme switching
        print("🔄 Demonstrating theme switching...")
        test_themes = ["dark", "light", "application_theme"]
        for theme_name in test_themes:
            if any(getattr(t, "name", str(t)) == theme_name for t in themes):
                success = self.app.set_theme(theme_name)
                print(f"   - Switched to '{theme_name}': {success}")
                time.sleep(0.1)  # Brief pause

    def run(self):
        """Run the complete application."""
        try:
            print("\n🎯 Running complete application...")

            if QT_AVAILABLE:
                # Show main window
                self.main_window.show()
                print("🖼️ Main window displayed")

                # In a real Qt application, this would be:
                # return self.app.exec()

                # For demo, simulate running
                print("⚙️ Application running (demo mode)")
                time.sleep(2)  # Simulate runtime

            else:
                print("💡 Application architecture demonstrated without Qt")

            print("\n🎉 Complete Application Demo Successful!")
            print("=" * 50)
            print("\nApplication Features Demonstrated:")
            print("1. Complete themed application with ThemedApplication")
            print("2. Multiple themed windows and widgets")
            print("3. Menu and status bar theming")
            print("4. Performance monitoring dashboard")
            print("5. Theme gallery with live preview")
            print("6. Custom theme creation and application")
            print("7. VSCode theme import capability")
            print("8. System theme integration")
            print("9. Background monitoring and statistics")
            print("10. Proper cleanup and memory management")

            return 0

        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback

            traceback.print_exc()
            return 1

        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up application resources."""
        print("\n🧹 Cleaning up application...")

        # Cleanup main window
        if hasattr(self.main_window, "cleanup_theming"):
            self.main_window.cleanup_theming()

        # Cleanup application
        self.app.cleanup()

        print("✅ Application cleanup completed")


def main():
    """Main entry point."""
    try:
        app = CompleteApplication()
        return app.run()

    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
        return 1

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n👋 Application exited with code: {exit_code}")
    sys.exit(exit_code)
