"""Document models for Reamde.

This module provides data structures for managing open markdown documents
and the collection of all documents.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


@dataclass
class DocumentModel:
    """Represents a single markdown document.

    Pure data model with no Qt dependencies (except for type hints).
    Following clean architecture principles.

    Attributes:
        file_path: Absolute path to the document file
        title: Display title (usually filename)
        content: Markdown content as string
        is_modified: Whether document has unsaved changes
        last_saved: Timestamp of last save
        scroll_position: Current scroll position (0-100)
        cursor_position: Current cursor position (line, column)

    Example:
        >>> doc = DocumentModel(
        ...     file_path="/home/user/README.md",
        ...     title="README.md",
        ...     content="# Hello World"
        ... )
        >>> doc.title
        'README.md'
    """

    file_path: str
    title: str
    content: str = ""
    is_modified: bool = False
    last_saved: Optional[datetime] = None
    scroll_position: int = 0
    cursor_position: tuple[int, int] = (0, 0)

    @classmethod
    def from_file(cls, file_path: Path) -> "DocumentModel":
        """Create DocumentModel from a file path.

        Args:
            file_path: Path to markdown file

        Returns:
            DocumentModel instance with content loaded

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read

        Example:
            >>> doc = DocumentModel.from_file(Path("/tmp/test.md"))
            >>> doc.title
            'test.md'
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

        # Create model
        return cls(
            file_path=str(file_path.resolve()),
            title=file_path.name,
            content=content,
            is_modified=False,
            last_saved=datetime.now(),
        )

    def save_to_file(self) -> None:
        """Save document content to file.

        Updates last_saved timestamp and clears is_modified flag.

        Raises:
            PermissionError: If file can't be written
            OSError: If disk is full or other I/O error

        Example:
            >>> doc.content = "# New Content"
            >>> doc.save_to_file()
            >>> doc.is_modified
            False
        """
        try:
            path = Path(self.file_path)
            path.write_text(self.content, encoding="utf-8")

            self.is_modified = False
            self.last_saved = datetime.now()

            logger.info(f"Saved document: {self.file_path}")

        except Exception as e:
            logger.error(f"Error saving file {self.file_path}: {e}")
            raise


class DocumentCollection(QObject):
    """Manages the collection of open documents.

    This class uses Qt signals for state changes but keeps the data
    models pure (DocumentModel has no Qt dependencies).

    Signals:
        document_added: Emitted when document is added (file_path: str)
        document_removed: Emitted when document is removed (file_path: str)
        document_modified: Emitted when document content changes (file_path: str)
        active_changed: Emitted when active document changes (file_path: str or None)

    Example:
        >>> collection = DocumentCollection()
        >>> collection.add_document("/tmp/test.md")
        >>> collection.get_active_document()
        DocumentModel(file_path='/tmp/test.md', ...)
    """

    # Signals
    document_added = Signal(str)  # file_path
    document_removed = Signal(str)  # file_path
    document_modified = Signal(str)  # file_path
    active_changed = Signal(object)  # file_path (str or None)

    def __init__(self):
        """Initialize empty document collection."""
        super().__init__()
        self._documents: dict[str, DocumentModel] = {}
        self._active_path: Optional[str] = None
        logger.info("DocumentCollection initialized")

    def add_document(self, file_path: str) -> DocumentModel:
        """Add or return existing document.

        Args:
            file_path: Absolute path to document

        Returns:
            DocumentModel instance

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read

        Example:
            >>> doc = collection.add_document("/tmp/test.md")
            >>> doc.title
            'test.md'
        """
        # Normalize path
        path = Path(file_path).resolve()
        path_str = str(path)

        # Return existing if already open
        if path_str in self._documents:
            logger.info(f"Document already open: {path_str}")
            return self._documents[path_str]

        # Load document
        doc = DocumentModel.from_file(path)
        self._documents[path_str] = doc

        # Set as active if it's the first document
        if len(self._documents) == 1:
            self._active_path = path_str
            self.active_changed.emit(path_str)

        self.document_added.emit(path_str)
        logger.info(f"Document added: {path_str}")

        return doc

    def remove_document(self, file_path: str) -> bool:
        """Remove document from collection.

        Args:
            file_path: Path to document to remove

        Returns:
            True if document was removed, False if not found

        Example:
            >>> collection.remove_document("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        path_str = str(path)

        if path_str not in self._documents:
            logger.warning(f"Document not found in collection: {path_str}")
            return False

        # Remove document
        del self._documents[path_str]
        self.document_removed.emit(path_str)

        # Update active if needed
        if self._active_path == path_str:
            if self._documents:
                # Set first document as active
                self._active_path = next(iter(self._documents.keys()))
                self.active_changed.emit(self._active_path)
            else:
                # No documents left
                self._active_path = None
                self.active_changed.emit(None)

        logger.info(f"Document removed: {path_str}")
        return True

    def get_document(self, file_path: str) -> Optional[DocumentModel]:
        """Get document by file path.

        Args:
            file_path: Path to document

        Returns:
            DocumentModel if found, None otherwise

        Example:
            >>> doc = collection.get_document("/tmp/test.md")
            >>> doc.title if doc else "Not found"
            'test.md'
        """
        path = Path(file_path).resolve()
        return self._documents.get(str(path))

    def get_active_document(self) -> Optional[DocumentModel]:
        """Get currently active document.

        Returns:
            Active DocumentModel or None if no documents

        Example:
            >>> doc = collection.get_active_document()
            >>> doc.title if doc else "No active document"
            'test.md'
        """
        if self._active_path:
            return self._documents.get(self._active_path)
        return None

    def set_active_document(self, file_path: str) -> bool:
        """Set active document by file path.

        Args:
            file_path: Path to document to make active

        Returns:
            True if successful, False if document not found

        Example:
            >>> collection.set_active_document("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        path_str = str(path)

        if path_str not in self._documents:
            logger.warning(f"Cannot set active - document not found: {path_str}")
            return False

        if self._active_path != path_str:
            self._active_path = path_str
            self.active_changed.emit(path_str)
            logger.info(f"Active document changed: {path_str}")

        return True

    def is_file_open(self, file_path: str) -> bool:
        """Check if file is currently open.

        Args:
            file_path: Path to check

        Returns:
            True if file is open in collection

        Example:
            >>> collection.is_file_open("/tmp/test.md")
            True
        """
        path = Path(file_path).resolve()
        return str(path) in self._documents

    def get_all_documents(self) -> list[DocumentModel]:
        """Get all documents in collection.

        Returns:
            List of all DocumentModel instances

        Example:
            >>> docs = collection.get_all_documents()
            >>> len(docs)
            3
        """
        return list(self._documents.values())

    def get_open_file_paths(self) -> list[str]:
        """Get list of all open file paths.

        Returns:
            List of absolute file paths

        Example:
            >>> paths = collection.get_open_file_paths()
            >>> paths
            ['/tmp/file1.md', '/tmp/file2.md']
        """
        return list(self._documents.keys())

    def mark_modified(self, file_path: str) -> None:
        """Mark document as modified.

        Args:
            file_path: Path to document

        Example:
            >>> collection.mark_modified("/tmp/test.md")
        """
        doc = self.get_document(file_path)
        if doc:
            doc.is_modified = True
            self.document_modified.emit(file_path)
            logger.debug(f"Document marked modified: {file_path}")

    def has_unsaved_changes(self) -> bool:
        """Check if any document has unsaved changes.

        Returns:
            True if any document is modified

        Example:
            >>> collection.has_unsaved_changes()
            False
        """
        return any(doc.is_modified for doc in self._documents.values())

    def count(self) -> int:
        """Get number of open documents.

        Returns:
            Number of documents in collection

        Example:
            >>> collection.count()
            3
        """
        return len(self._documents)
