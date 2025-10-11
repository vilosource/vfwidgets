#!/usr/bin/env python3
"""Quick test script for the terminal widget."""

import sys
from pathlib import Path

# Add the src directory to path so we can import the widget
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and test
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow
from vfwidgets_terminal import TerminalWidget


def test_basic_terminal(debug=False):
    """Test basic terminal functionality."""
    print("Testing VFWidgets Terminal...")
    print("-" * 50)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Terminal Widget Test")

    # Create main window
    window = QMainWindow()
    title = "Terminal Widget Test"
    if debug:
        title += " - DEBUG MODE (Right-click to test!)"
    window.setWindowTitle(title)
    window.setGeometry(100, 100, 800, 600)

    # Create terminal widget with debug flag
    print("Creating terminal widget...")
    terminal = TerminalWidget(debug=debug)

    # Connect signals to verify they work
    terminal.terminal_ready.connect(lambda: print("✅ Signal: Terminal is ready!"))

    terminal.server_started.connect(
        lambda url: print(f"✅ Signal: Server started at {url}")
    )

    terminal.command_started.connect(
        lambda cmd: print(f"✅ Signal: Command started: {cmd}")
    )

    terminal.output_received.connect(
        lambda data: print(f"📤 Output received: {len(data)} chars")
    )

    terminal.terminal_closed.connect(
        lambda code: print(f"✅ Signal: Terminal closed with code {code}")
    )

    # Add new signal connections for testing enhanced features (Phase 1-4)
    if debug:
        print("🔌 Connecting enhanced event signals for testing...")
        terminal.focus_received.connect(
            lambda: print("🎯 FOCUS: Terminal received focus!")
        )
        terminal.focus_lost.connect(lambda: print("❌ FOCUS: Terminal lost focus!"))
        terminal.selection_changed.connect(
            lambda text: print(
                f"📝 SELECTION: '{text[:50]}{'...' if len(text) > 50 else ''}'"
            )
        )
        terminal.context_menu_requested.connect(
            lambda pos, text: print(
                f"🖱️  CONTEXT MENU: Requested at ({pos.x()}, {pos.y()}) with text: '{text[:30]}{'...' if len(text) > 30 else ''}'"
            )
        )
        terminal.bell_rang.connect(lambda: print("🔔 BELL: Terminal bell rang!"))
        terminal.key_pressed.connect(
            lambda key, code, ctrl, alt, shift: (
                print(f"⌨️  KEY: {key} (ctrl:{ctrl}, alt:{alt}, shift:{shift})")
                if ctrl or alt or len(key) > 1
                else None
            )
        )

    # Set as central widget
    window.setCentralWidget(terminal)

    # Show window
    window.show()

    # Auto-test some features after terminal loads
    def run_auto_tests():
        print("\nRunning automated tests...")

        # Test 1: Send a simple command
        print("Test 1: Sending 'echo Hello World' command...")
        terminal.send_command("echo 'Hello from Terminal Widget!'")

        # Test 2: Get process info
        QTimer.singleShot(1000, lambda: test_process_info())

        # Test 3: Clear terminal
        QTimer.singleShot(2000, lambda: test_clear())

        # Test 4: Send another command
        QTimer.singleShot(3000, lambda: test_pwd())

    def test_process_info():
        info = terminal.get_process_info()
        print(
            f"Test 2: Process info: PID={info.get('pid')}, Command={info.get('command')}"
        )

    def test_clear():
        print("Test 3: Clearing terminal...")
        terminal.clear()

    def test_pwd():
        print("Test 4: Sending 'pwd' command...")
        terminal.send_command("pwd")

    # Start auto tests after terminal is ready
    terminal.terminal_ready.connect(run_auto_tests)

    print("\nStarting application...")
    if debug:
        print("🚀 DEBUG MODE ACTIVE - Enhanced event logging enabled!")
        print("🖱️  Right-click anywhere on the terminal to test context menu")
        print("📝 Select text first, then right-click to see selection handling")
        print("🎯 Click on/off the terminal to see focus events")
    print("You should see a terminal window with bash prompt.")
    print("Try typing commands like 'ls', 'echo hello', etc.")
    print("-" * 50)

    # Run the application
    return app.exec()


def test_python_terminal():
    """Test with Python REPL."""
    print("\nTesting Python REPL mode...")

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Python Terminal Test")
    window.setGeometry(100, 100, 800, 600)

    # Create Python terminal
    terminal = TerminalWidget(command="python", args=["-i"], debug=True)

    window.setCentralWidget(terminal)
    window.show()

    # Send some Python commands after ready
    def send_python_commands():
        print("Sending Python commands...")
        terminal.send_command("print('Hello from Python!')")
        QTimer.singleShot(500, lambda: terminal.send_command("2 + 2"))
        QTimer.singleShot(
            1000, lambda: terminal.send_command("import sys; print(sys.version)")
        )

    terminal.terminal_ready.connect(send_python_commands)

    return app.exec()


def test_with_capture():
    """Test output capture functionality."""
    print("\nTesting output capture...")

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Terminal with Output Capture")
    window.setGeometry(100, 100, 800, 600)

    # Create terminal with output capture
    terminal = TerminalWidget(capture_output=True, debug=True)

    # Capture output
    captured_output = []
    terminal.output_received.connect(lambda data: captured_output.append(data))

    window.setCentralWidget(terminal)
    window.show()

    def test_capture():
        terminal.send_command("echo 'Testing output capture'")
        terminal.send_command("ls -la")

        # Check captured output after delay
        QTimer.singleShot(2000, lambda: show_captured())

    def show_captured():
        output = terminal.get_output()
        print(f"\nCaptured output ({len(output)} chars):")
        print("-" * 40)
        print(output[-500:] if len(output) > 500 else output)  # Last 500 chars
        print("-" * 40)

        # Save to file
        terminal.save_output("test_output.txt")
        print("Output saved to test_output.txt")

    terminal.terminal_ready.connect(test_capture)

    return app.exec()


def main():
    """Run tests based on command line argument."""
    import argparse

    parser = argparse.ArgumentParser(description="Test VFWidgets Terminal")
    parser.add_argument(
        "--mode",
        choices=["basic", "python", "capture", "all"],
        default="basic",
        help="Test mode to run",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging for enhanced event testing",
    )

    args = parser.parse_args()

    # Print instructions for right-click testing if debug is enabled
    if args.debug:
        print("\n" + "=" * 60)
        print("🖱️  DEBUG MODE: Right-click Context Menu Testing")
        print("=" * 60)
        print("🎯 Right-click anywhere on the terminal to see:")
        print("   • Focus event detection logs")
        print("   • Context menu creation logs")
        print("   • Selection tracking")
        print("   • Menu action logs")
        print("=" * 60)
        print()

    # Modify test functions to use debug flag

    if args.mode == "basic":
        return test_basic_terminal(debug=args.debug)
    elif args.mode == "python":
        return test_python_terminal()
    elif args.mode == "capture":
        return test_with_capture()
    elif args.mode == "all":
        # Run all tests sequentially (not recommended for GUI)
        print("Run individual tests with --mode flag instead")
        print("Options: basic, python, capture")
        return test_basic_terminal(debug=args.debug)

    return 0


if __name__ == "__main__":
    sys.exit(main())
