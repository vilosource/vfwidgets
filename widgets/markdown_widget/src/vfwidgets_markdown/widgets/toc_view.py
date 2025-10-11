"""Table of Contents view that observes the document model."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from vfwidgets_markdown.models import MarkdownDocument


class MarkdownTocView(QWidget):
    """Table of Contents view that observes a MarkdownDocument model.

    This widget uses an auto-wrapping pattern:
    - If no document is provided, creates an internal document (simple mode)
    - If document is provided, uses external document (architecture mode)

    This widget demonstrates the dual pattern approach:
    - Uses Python observer pattern to react to model changes
    - Uses Qt signals/slots for UI coordination with other views
    """

    # Qt Signals for UI coordination (view-to-view communication)
    heading_clicked = Signal(str)  # heading_id
    heading_hovered = Signal(str)  # heading_id

    def __init__(
        self, document: Optional[MarkdownDocument] = None, parent: Optional[QWidget] = None
    ):
        """Initialize the TOC view.

        The TOC view uses an auto-wrapping pattern:
        - If no document is provided, creates an internal document (simple mode)
        - If document is provided, uses external document (architecture mode)

        Args:
            document: Optional document model to observe. If None, creates internal document.
            parent: Optional parent widget
        """
        super().__init__(parent)

        # Auto-wrapping: Always use a document (internal or external)
        if document:
            # Advanced mode - use external document
            self._document = document
            self._owns_document = False
        else:
            # Simple mode - create internal document
            self._document = MarkdownDocument()
            self._owns_document = True

        # Add this view as an observer (Python observer pattern)
        self._document.add_observer(self)

        # Create UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget()
        layout.addWidget(self._list)

        # Connect Qt signals from list widget to our slots
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemEntered.connect(self._on_item_hovered)

        # Enable mouse tracking for hover events
        self._list.setMouseTracking(True)

        # Initial TOC display from model
        toc = self._document.get_toc()
        self.display_toc(toc)

    def on_document_changed(self, event):
        """Observer callback - called when model changes.

        This is a Python observer method, NOT a Qt slot.
        It's called directly by the model's _notify_observers().

        Args:
            event: TextReplaceEvent, TextAppendEvent, or SectionUpdateEvent
        """
        # Update TOC from model
        toc = self._document.get_toc()
        self.display_toc(toc)

    def display_toc(self, toc: list[dict]):
        """Update the UI with TOC entries.

        Args:
            toc: List of TOC entries with 'level', 'text', and 'id' keys
        """
        # Save current selection
        current_item = self._list.currentItem()
        current_id = current_item.data(Qt.UserRole) if current_item else None

        # Clear and rebuild list
        self._list.clear()

        for entry in toc:
            level = entry["level"]
            text = entry["text"]
            heading_id = entry["id"]

            # Create list item
            item = QListWidgetItem()

            # Indent based on level
            indent = "  " * (level - 1)
            item.setText(f"{indent}{text}")

            # Store heading ID for later retrieval
            item.setData(Qt.UserRole, heading_id)

            self._list.addItem(item)

            # Restore selection if this was the selected item
            if heading_id == current_id:
                self._list.setCurrentItem(item)

    @Slot(QListWidgetItem)
    def _on_item_clicked(self, item: QListWidgetItem):
        """Qt slot - responds to item clicked signal.

        Args:
            item: The clicked list widget item
        """
        heading_id = item.data(Qt.UserRole)
        if heading_id:
            # Emit our custom Qt signal (view-to-view coordination)
            self.heading_clicked.emit(heading_id)

    @Slot(QListWidgetItem)
    def _on_item_hovered(self, item: QListWidgetItem):
        """Qt slot - responds to item hover signal.

        Args:
            item: The hovered list widget item
        """
        heading_id = item.data(Qt.UserRole)
        if heading_id:
            # Emit our custom Qt signal (view-to-view coordination)
            self.heading_hovered.emit(heading_id)

    def set_text(self, text: str) -> None:
        """Set the document text (convenience method for simple mode).

        Args:
            text: The markdown content
        """
        self._document.set_text(text)

    def get_document(self) -> MarkdownDocument:
        """Get the underlying document model (for advanced usage).

        Returns:
            The MarkdownDocument instance
        """
        return self._document

    def closeEvent(self, event):
        """Handle widget closing - remove observer to prevent memory leaks."""
        self._document.remove_observer(self)
        super().closeEvent(event)
