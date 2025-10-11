"""Demo: Controller Features - Pause/Resume and Throttling

This demo showcases the MarkdownEditorController's performance features:
1. Pause/Resume - Batch multiple updates into a single render
2. Throttling - Debounce rapid updates for smooth typing performance

These features are critical for:
- Loading large files (pause during load, resume for single render)
- High-frequency typing (throttle to prevent UI lag)
- Bulk operations (paste, find/replace, etc.)
"""

import sys
import time

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from vfwidgets_markdown.controllers import MarkdownEditorController
from vfwidgets_markdown.models import MarkdownDocument
from vfwidgets_markdown.widgets import MarkdownTextEditor


class MockHTMLViewer(QTextEdit):
    """Mock HTML viewer that tracks render count.

    In a real application, this would be a markdown-to-HTML renderer
    (e.g., using markdown-it or mistune). For this demo, we just
    track how many times it's asked to update.
    """

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.render_count = 0
        self._render_label = None

    def set_render_label(self, label: QLabel):
        """Set label to display render count."""
        self._render_label = label
        self._update_label()

    def on_document_changed(self, event):
        """Observer callback - simulates expensive rendering."""
        # Simulate rendering delay
        time.sleep(0.05)  # 50ms render time

        self.render_count += 1
        text = event.text if hasattr(event, "text") else "[update]"

        # Display render info
        self.setPlainText(
            f"Render #{self.render_count}\n─────────────────\nContent preview:\n{text[:200]}..."
        )

        self._update_label()
        print(f"[VIEWER] Render #{self.render_count} (50ms simulated delay)")

    def _update_label(self):
        """Update the render count label."""
        if self._render_label:
            self._render_label.setText(f"Renders: {self.render_count}")

    def reset_count(self):
        """Reset render counter."""
        self.render_count = 0
        self._update_label()


class ControllerFeaturesDemo(QWidget):
    """Demo window showing controller features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Controller Features Demo")
        self.resize(1200, 700)

        # Create MVC components
        self.document = MarkdownDocument(
            "# Controller Features Demo\n\n"
            "Try the buttons below to see how the controller "
            "optimizes rendering performance."
        )
        self.editor = MarkdownTextEditor(self.document)
        self.viewer = MockHTMLViewer()

        # Create controller
        self.document.add_observer(self.viewer)
        self.controller = MarkdownEditorController(self.document, self.editor, self.viewer)

        self._setup_ui()

        print("\n" + "=" * 70)
        print("CONTROLLER FEATURES DEMO")
        print("=" * 70)
        print("Watch the 'Renders' counter to see controller optimizations:")
        print("- Pause/Resume: 100 updates → 1 render")
        print("- Throttling: Rapid updates → 1 render after delay")
        print("=" * 70 + "\n")

    def _setup_ui(self):
        """Create the UI layout."""
        layout = QHBoxLayout(self)

        # Left panel: Editor
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        editor_label = QLabel("Editor (Source)")
        editor_label.setStyleSheet("font-weight: bold; padding: 5px;")
        left_layout.addWidget(editor_label)

        left_layout.addWidget(self.editor)

        # Right panel: Viewer + Controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        viewer_label = QLabel("Viewer (Rendered)")
        viewer_label.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(viewer_label)

        right_layout.addWidget(self.viewer)

        # Controls
        controls = self._create_controls()
        right_layout.addWidget(controls)

        # Add panels to main layout
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(right_panel, stretch=1)

    def _create_controls(self):
        """Create control panel."""
        controls = QWidget()
        layout = QVBoxLayout(controls)
        layout.setContentsMargins(0, 10, 0, 0)

        # Title
        title = QLabel("Controller Features")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Render counter
        self.render_label = QLabel("Renders: 0")
        self.render_label.setStyleSheet("font-size: 12px; color: #0066cc;")
        layout.addWidget(self.render_label)
        self.viewer.set_render_label(self.render_label)

        # Section 1: Pause/Resume
        pause_section = QLabel("1. Pause/Resume (Batch Updates)")
        pause_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(pause_section)

        pause_desc = QLabel(
            "Without pause: 100 updates = 100 renders (5 seconds)\n"
            "With pause: 100 updates = 1 render (instant)"
        )
        pause_desc.setWordWrap(True)
        pause_desc.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(pause_desc)

        pause_buttons = QHBoxLayout()

        btn_no_pause = QPushButton("100 Updates (No Pause)")
        btn_no_pause.clicked.connect(self._demo_without_pause)
        pause_buttons.addWidget(btn_no_pause)

        btn_with_pause = QPushButton("100 Updates (With Pause)")
        btn_with_pause.clicked.connect(self._demo_with_pause)
        pause_buttons.addWidget(btn_with_pause)

        layout.addLayout(pause_buttons)

        # Section 2: Throttling
        throttle_section = QLabel("2. Throttling (Debounce)")
        throttle_section.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(throttle_section)

        throttle_desc = QLabel(
            "Debounces rapid updates to prevent lag during typing.\n"
            "Multiple updates → Single render after delay."
        )
        throttle_desc.setWordWrap(True)
        throttle_desc.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(throttle_desc)

        throttle_controls = QHBoxLayout()

        throttle_controls.addWidget(QLabel("Interval (ms):"))

        self.throttle_spin = QSpinBox()
        self.throttle_spin.setRange(100, 1000)
        self.throttle_spin.setValue(300)
        self.throttle_spin.setSingleStep(100)
        throttle_controls.addWidget(self.throttle_spin)

        btn_enable_throttle = QPushButton("Enable")
        btn_enable_throttle.clicked.connect(self._enable_throttle)
        throttle_controls.addWidget(btn_enable_throttle)

        btn_disable_throttle = QPushButton("Disable")
        btn_disable_throttle.clicked.connect(self._disable_throttle)
        throttle_controls.addWidget(btn_disable_throttle)

        layout.addLayout(throttle_controls)

        self.throttle_status = QLabel("Status: Disabled")
        self.throttle_status.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.throttle_status)

        # Section 3: Reset
        btn_reset = QPushButton("Reset Demo")
        btn_reset.clicked.connect(self._reset_demo)
        layout.addWidget(btn_reset)

        # Spacer
        layout.addStretch()

        return controls

    def _demo_without_pause(self):
        """Demo batch updates WITHOUT pause - slow!"""
        print("\n[DEMO] 100 updates WITHOUT pause...")
        self.viewer.reset_count()

        start = time.time()
        for i in range(100):
            self.document.append_text(f"\nUpdate {i + 1}")
            QApplication.processEvents()  # Process each update immediately

        elapsed = time.time() - start
        print(f"[DEMO] Completed in {elapsed:.2f}s with {self.viewer.render_count} renders")
        print("[DEMO] ⚠️ Slow! Each update triggered a 50ms render")

    def _demo_with_pause(self):
        """Demo batch updates WITH pause - fast!"""
        print("\n[DEMO] 100 updates WITH pause...")
        self.viewer.reset_count()

        start = time.time()

        # Pause rendering
        self.controller.pause_rendering()
        print("[CONTROLLER] Rendering paused")

        for i in range(100):
            self.document.append_text(f"\nUpdate {i + 1}")

        # Resume rendering - triggers single update
        self.controller.resume_rendering()
        print("[CONTROLLER] Rendering resumed")

        elapsed = time.time() - start
        print(f"[DEMO] Completed in {elapsed:.2f}s with {self.viewer.render_count} renders")
        print("[DEMO] ✅ Fast! Only 1 render for 100 updates")

    def _enable_throttle(self):
        """Enable throttling."""
        interval = self.throttle_spin.value()
        self.controller.set_throttle_mode(True, interval)
        self.throttle_status.setText(f"Status: Enabled ({interval}ms)")
        self.throttle_status.setStyleSheet("font-size: 11px; color: #00aa00;")
        print(f"\n[CONTROLLER] Throttling enabled ({interval}ms debounce)")
        print("[CONTROLLER] Try typing rapidly - viewer updates will be debounced")

    def _disable_throttle(self):
        """Disable throttling."""
        self.controller.set_throttle_mode(False)
        self.throttle_status.setText("Status: Disabled")
        self.throttle_status.setStyleSheet("font-size: 11px; color: #666;")
        print("\n[CONTROLLER] Throttling disabled")
        print("[CONTROLLER] Viewer updates immediately on each change")

    def _reset_demo(self):
        """Reset the demo."""
        self.document.set_text(
            "# Controller Features Demo\n\n"
            "Try the buttons below to see how the controller "
            "optimizes rendering performance."
        )
        self.viewer.reset_count()
        self._disable_throttle()
        print("\n[DEMO] Reset")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)

    print(
        """
╔══════════════════════════════════════════════════════════════════╗
║               MARKDOWN CONTROLLER FEATURES DEMO                  ║
╚══════════════════════════════════════════════════════════════════╝

This demo shows how MarkdownEditorController optimizes performance:

┌─ Feature 1: Pause/Resume ─────────────────────────────────────┐
│ Problem: Loading a large file triggers hundreds of renders    │
│ Solution: Pause rendering, load file, resume (1 render)       │
│                                                                │
│ Try: Click "100 Updates (No Pause)" vs "100 Updates (Pause)"  │
└────────────────────────────────────────────────────────────────┘

┌─ Feature 2: Throttling ───────────────────────────────────────┐
│ Problem: Rapid typing causes lag from constant re-rendering   │
│ Solution: Debounce updates - render once after typing pauses  │
│                                                                │
│ Try: Enable throttling, then type rapidly in the editor       │
└────────────────────────────────────────────────────────────────┘

Watch the "Renders" counter to see the optimizations in action!
"""
    )

    window = ControllerFeaturesDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
