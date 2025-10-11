"""Tests for abstract signal system."""

import unittest

from vfwidgets_multisplit.bridge.signal_bridge import SignalBridge
from vfwidgets_multisplit.core.signals import AbstractSignal


class TestAbstractSignal(unittest.TestCase):
    """Test abstract signal implementation."""

    def test_connect_and_emit(self):
        """Test connecting handlers and emitting signals."""
        signal = AbstractSignal()
        results = []

        def handler(value):
            results.append(value)

        signal.connect(handler)
        signal.emit(42)

        self.assertEqual(results, [42])

    def test_multiple_handlers(self):
        """Test multiple handlers on same signal."""
        signal = AbstractSignal()
        results = []

        def handler1(value):
            results.append(f"h1:{value}")

        def handler2(value):
            results.append(f"h2:{value}")

        signal.connect(handler1)
        signal.connect(handler2)
        signal.emit("test")

        self.assertIn("h1:test", results)
        self.assertIn("h2:test", results)

    def test_disconnect(self):
        """Test disconnecting handlers."""
        signal = AbstractSignal()
        results = []

        def handler(value):
            results.append(value)

        signal.connect(handler)
        signal.emit(1)

        signal.disconnect(handler)
        signal.emit(2)

        self.assertEqual(results, [1])  # 2 should not be added

    def test_weak_references(self):
        """Test that weak references don't prevent garbage collection."""
        signal = AbstractSignal()

        def create_handler():
            results = []

            def handler(value):
                results.append(value)

            signal.connect(handler)
            return handler

        handler = create_handler()
        self.assertEqual(signal.handler_count(), 1)

        # Delete handler - weak ref should be cleaned up
        del handler
        signal.emit("test")  # This triggers cleanup
        self.assertEqual(signal.handler_count(), 0)

    def test_handler_error_isolation(self):
        """Test that handler errors don't break signal emission."""
        signal = AbstractSignal()
        results = []

        def bad_handler(value):
            raise ValueError("Test error")

        def good_handler(value):
            results.append(value)

        signal.connect(bad_handler)
        signal.connect(good_handler)

        # Should not raise despite bad_handler error
        signal.emit("test")

        # Good handler should still be called
        self.assertEqual(results, ["test"])


class MockQtSignal:
    """Mock Qt signal for testing bridge."""

    def __init__(self):
        self.emitted_values = []
        self.handlers = []

    def emit(self, *args):
        self.emitted_values.append(args)
        for handler in self.handlers:
            handler(*args)

    def connect(self, slot):
        self.handlers.append(slot)

    def disconnect(self, slot):
        if slot in self.handlers:
            self.handlers.remove(slot)


class TestSignalBridge(unittest.TestCase):
    """Test signal bridge functionality."""

    def test_bridge_to_qt(self):
        """Test bridging from abstract signal to Qt signal."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()

        bridge.bridge_to_qt(abstract_signal, qt_signal)

        # Emit on abstract signal should trigger Qt signal
        abstract_signal.emit("test", 42)

        self.assertEqual(qt_signal.emitted_values, [("test", 42)])

    def test_bridge_from_qt(self):
        """Test bridging from Qt signal to abstract signal."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()
        results = []

        def handler(value):
            results.append(value)

        abstract_signal.connect(handler)
        bridge.bridge_from_qt(qt_signal, abstract_signal)

        # Emit on Qt signal should trigger abstract signal
        qt_signal.emit("test")

        self.assertEqual(results, ["test"])

    def test_bridge_cleanup(self):
        """Test bridge cleanup removes connections."""
        abstract_signal = AbstractSignal()
        qt_signal = MockQtSignal()
        bridge = SignalBridge()

        bridge.bridge_to_qt(abstract_signal, qt_signal)
        bridge.cleanup()

        # After cleanup, signals should not be connected
        abstract_signal.emit("test")
        self.assertEqual(qt_signal.emitted_values, [])


if __name__ == "__main__":
    unittest.main()
