"""Centralized error handling for Reamde."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMessageBox, QWidget

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling with user-friendly feedback."""

    @staticmethod
    def handle_file_error(
        parent: Optional[QWidget], file_path: Path, error: Exception, context: str = "opening"
    ) -> None:
        """Show user-friendly error message for file operations.

        Args:
            parent: Parent widget for dialog (None for standalone)
            file_path: Path that caused the error
            error: The exception that was raised
            context: What we were trying to do ("opening", "saving", "loading")

        Example:
            >>> try:
            ...     path.read_text()
            ... except Exception as e:
            ...     ErrorHandler.handle_file_error(window, path, e, "reading")
        """
        logger.error(f"Error {context} {file_path}: {error}", exc_info=True)

        if isinstance(error, FileNotFoundError):
            QMessageBox.critical(
                parent,
                "File Not Found",
                f"Cannot find file:\n\n{file_path}\n\nThe file may have been moved or deleted.",
            )

        elif isinstance(error, PermissionError):
            QMessageBox.critical(
                parent,
                "Permission Denied",
                f"Cannot access file:\n\n{file_path}\n\n"
                f"Check file permissions or try running as administrator.",
            )

        elif isinstance(error, IsADirectoryError):
            QMessageBox.warning(
                parent,
                "Cannot Open Directory",
                f"Cannot open directory as file:\n\n{file_path}\n\n"
                f"Please select a markdown file (.md).",
            )

        elif isinstance(error, OSError):
            QMessageBox.critical(
                parent,
                "I/O Error",
                f"Error {context} file:\n\n{file_path}\n\n"
                f"Error: {error}\n\n"
                f"The disk may be full, the network may be down, "
                f"or the file may be locked by another program.",
            )

        else:
            # Generic error
            QMessageBox.critical(
                parent,
                f"Error {context.capitalize()} File",
                f"Unexpected error {context} file:\n\n{file_path}\n\n"
                f"{type(error).__name__}: {error}",
            )

    @staticmethod
    def handle_session_error(parent: Optional[QWidget], error: Exception) -> None:
        """Handle session load/save errors.

        Args:
            parent: Parent widget for dialog
            error: The exception that was raised

        Example:
            >>> try:
            ...     load_session()
            ... except Exception as e:
            ...     ErrorHandler.handle_session_error(window, e)
        """
        logger.error(f"Session error: {error}", exc_info=True)

        QMessageBox.warning(
            parent,
            "Session Error",
            f"Could not load previous session:\n\n{error}\n\nStarting with a fresh session.",
        )

    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str) -> None:
        """Show non-critical warning.

        Args:
            parent: Parent widget for dialog
            title: Dialog title
            message: Warning message

        Example:
            >>> ErrorHandler.show_warning(window, "Large File", "File is 50 MB")
        """
        logger.warning(f"{title}: {message}")
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_info(parent: Optional[QWidget], title: str, message: str) -> None:
        """Show informational message.

        Args:
            parent: Parent widget for dialog
            title: Dialog title
            message: Info message

        Example:
            >>> ErrorHandler.show_info(window, "Success", "File opened")
        """
        logger.info(f"{title}: {message}")
        QMessageBox.information(parent, title, message)

    @staticmethod
    def confirm_action(
        parent: Optional[QWidget], title: str, message: str, default_yes: bool = False
    ) -> bool:
        """Show confirmation dialog.

        Args:
            parent: Parent widget for dialog
            title: Dialog title
            message: Confirmation message
            default_yes: If True, default button is Yes

        Returns:
            True if user clicked Yes, False otherwise

        Example:
            >>> if ErrorHandler.confirm_action(window, "Delete", "Delete file?"):
            ...     delete_file()
        """
        default_button = QMessageBox.Yes if default_yes else QMessageBox.No
        reply = QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No, default_button
        )
        return reply == QMessageBox.Yes
