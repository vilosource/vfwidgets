"""
Tab content area for ChromeTabbedWindow.

Manages the stacked widget area that displays tab content.
Pure view component that wraps QStackedWidget for content display.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QStackedWidget, QWidget

from ..model import TabModel


class TabContentArea(QStackedWidget):
    """
    Content area that displays tab widgets.

    This is a pure view component that wraps QStackedWidget to display
    the current tab's content. It observes the TabModel for changes
    and automatically switches to the correct widget.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the tab content area."""
        super().__init__(parent)

        # Internal state
        self._model: Optional[TabModel] = None

        # Configure stacked widget
        self.setFrameStyle(QStackedWidget.Shape.NoFrame)

        # Set size policy for proper layout
        from PySide6.QtWidgets import QSizePolicy

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_model(self, model: TabModel) -> None:
        """
        Connect to the tab model.

        The content area observes the model and automatically updates
        when tabs are added, removed, or the current tab changes.
        """
        self._model = model

        # Connect to model signals
        model._tabAdded.connect(self._on_tab_added)
        model._tabRemoved.connect(self._on_tab_removed)
        model.currentChanged.connect(self._on_current_changed)

        # Sync with current model state
        self._sync_with_model()

    def _sync_with_model(self) -> None:
        """Synchronize content area with current model state."""
        if not self._model:
            return

        # Clear existing widgets
        while self.count() > 0:
            widget = self.widget(0)
            self.removeWidget(widget)

        # Add all widgets from model
        for i in range(self._model.count()):
            widget = self._model.widget(i)
            if widget:
                self._add_widget_to_stack(widget, i)

        # Set current widget
        current_index = self._model.current_index()
        if current_index >= 0 and current_index < self.count():
            self.setCurrentIndex(current_index)

    def _add_widget_to_stack(self, widget: QWidget, index: int) -> None:
        """
        Add a widget to the stacked widget.

        Handles proper parenting and ensures the widget is set up correctly
        for display in the content area.
        """
        if not widget:
            return

        # Set parent - critical for Qt ownership
        widget.setParent(self)

        # Insert at the correct position
        if index >= self.count():
            self.addWidget(widget)
        else:
            self.insertWidget(index, widget)

        # Ensure widget is visible when added
        widget.show()

    def _on_tab_added(self, index: int) -> None:
        """Handle tab addition from model."""
        if not self._model:
            return

        widget = self._model.widget(index)
        if widget:
            self._add_widget_to_stack(widget, index)

    def _on_tab_removed(self, index: int) -> None:
        """Handle tab removal from model."""
        if index < self.count():
            widget = self.widget(index)
            if widget:
                # Remove from stacked widget
                self.removeWidget(widget)

                # Clear parent but don't delete (QTabWidget behavior)
                widget.setParent(None)

    def _on_current_changed(self, index: int) -> None:
        """Handle current tab change from model."""
        if index >= 0 and index < self.count():
            self.setCurrentIndex(index)
        elif index == -1:
            # No current tab - QStackedWidget behavior is to show nothing
            # This happens when all tabs are removed
            pass

    # ==================== QStackedWidget Interface ====================

    def insertWidget(self, index: int, widget: QWidget) -> int:
        """Insert widget at index with proper setup."""
        if not widget:
            return -1

        # Ensure proper parent
        widget.setParent(self)

        # Insert into stack
        actual_index = super().insertWidget(index, widget)

        return actual_index

    def addWidget(self, widget: QWidget) -> int:
        """Add widget with proper setup."""
        return self.insertWidget(self.count(), widget)

    def removeWidget(self, widget: QWidget) -> None:
        """Remove widget from stack."""
        if widget:
            super().removeWidget(widget)
            # Note: We don't clear parent here - that's handled by caller

    def sizeHint(self) -> QSize:
        """Return size hint for the content area."""
        # If we have a current widget, use its size hint
        current = self.currentWidget()
        if current:
            return current.sizeHint()

        # Otherwise, return a reasonable default
        return QSize(400, 300)

    def minimumSizeHint(self) -> QSize:
        """Return minimum size hint for the content area."""
        # If we have a current widget, use its minimum size hint
        current = self.currentWidget()
        if current:
            return current.minimumSizeHint()

        # Otherwise, return a minimal default
        return QSize(200, 150)

    def hasHeightForWidth(self) -> bool:
        """Check if content area has height for width."""
        current = self.currentWidget()
        if current:
            return current.hasHeightForWidth()
        return False

    def heightForWidth(self, width: int) -> int:
        """Calculate height for given width."""
        current = self.currentWidget()
        if current and current.hasHeightForWidth():
            return current.heightForWidth(width)
        return -1
