"""Abstract signal system for Model layer.

Pure Python implementation with no Qt dependencies.
Provides signal/slot mechanism for the Model layer.
"""

import weakref
from typing import Callable


class AbstractSignal:
    """Pure Python signal implementation with no Qt dependencies."""

    def __init__(self):
        """Initialize signal with empty handler list."""
        # Use weak references to prevent memory leaks
        # Note: We store both weak refs and a special handling for bound methods
        self._handlers: list[weakref.ref] = []
        self._method_refs: list[tuple] = []  # (obj_ref, method_name)

    def connect(self, handler: Callable) -> None:
        """Connect a handler to this signal.

        Args:
            handler: Callable to invoke when signal is emitted
        """
        # Check if it's a bound method
        if hasattr(handler, '__self__') and hasattr(handler, '__name__'):
            # Store weak ref to object and method name
            obj_ref = weakref.ref(handler.__self__)
            method_name = handler.__name__
            # Check if already connected
            for existing_obj_ref, existing_method in self._method_refs:
                if existing_obj_ref() is handler.__self__ and existing_method == method_name:
                    return  # Already connected
            self._method_refs.append((obj_ref, method_name))
        else:
            # Regular function, use weak ref
            ref = weakref.ref(handler)
            if ref not in self._handlers:
                self._handlers.append(ref)

    def disconnect(self, handler: Callable) -> None:
        """Disconnect a handler from this signal.

        Args:
            handler: Handler to remove
        """
        weakref.ref(handler)
        self._handlers = [h for h in self._handlers if h() != handler]

    def emit(self, *args, **kwargs) -> None:
        """Emit signal to all connected handlers.

        Args:
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        # Clean up dead references
        self._cleanup_handlers()

        # Call regular handlers
        for ref in self._handlers:
            handler = ref()
            if handler is not None:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    # Don't let handler errors break signal emission
                    print(f"Signal handler error: {e}")

        # Call bound method handlers
        for obj_ref, method_name in self._method_refs:
            obj = obj_ref()
            if obj is not None:
                try:
                    method = getattr(obj, method_name)
                    method(*args, **kwargs)
                except Exception as e:
                    print(f"Signal handler error: {e}")

    def _cleanup_handlers(self) -> None:
        """Remove dead weak references."""
        self._handlers = [ref for ref in self._handlers if ref() is not None]
        self._method_refs = [(obj_ref, method) for obj_ref, method in self._method_refs if obj_ref() is not None]

    def handler_count(self) -> int:
        """Get count of connected handlers.

        Returns:
            Number of live handlers
        """
        self._cleanup_handlers()
        return len(self._handlers)

    def clear(self) -> None:
        """Disconnect all handlers."""
        self._handlers.clear()


class ModelSignals:
    """Collection of signals for the Model layer."""

    def __init__(self):
        """Initialize all model signals."""
        # Structure signals
        self.about_to_change = AbstractSignal()
        self.changed = AbstractSignal()
        self.structure_changed = AbstractSignal()

        # Focus signals
        self.focus_changed = AbstractSignal()

        # Pane signals
        self.pane_added = AbstractSignal()
        self.pane_removed = AbstractSignal()

        # Error signals
        self.validation_failed = AbstractSignal()

        # Command signals
        self.command_executed = AbstractSignal()
        self.command_undone = AbstractSignal()
