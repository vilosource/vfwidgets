"""Theme Editor Widget - Main Editor Component.

This module provides the ThemeEditorWidget and ThemeEditorDialog for visual theme editing.

Phase 1: Core Infrastructure
"""

from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import QSize, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..core.theme import Theme, ThemeBuilder
from ..factory.builder import ThemeComposer
from ..logging import get_debug_logger
from ..validation.framework import ValidationResult
from .base import ThemedWidget
from .color_editor import ColorEditorWidget
from .convenience import ThemedDialog
from .font_editor import FontEditorWidget
from .import_export import ThemeExportDialog, ThemeImportDialog
from .preview_samples import ThemePreviewWidget
from .token_browser import TokenBrowserWidget
from .validation_panel import ValidationPanel

logger = get_debug_logger(__name__)


class ThemeEditorWidget(ThemedWidget, QWidget):
    """Embeddable theme editor widget.

    Main editor widget that can be embedded in dialogs or settings pages.
    Provides visual editing of all 200 theme tokens.

    Phase 1: Core infrastructure with token browser
    Future phases will add: color editor, preview, validation, etc.

    Signals:
        theme_modified(): Emitted when theme is modified
        validation_changed(ValidationResult): Emitted when validation status changes
        token_selected(str): Emitted when a token is selected
    """

    # Signals
    theme_modified = Signal()
    validation_changed = Signal(ValidationResult)
    token_selected = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        base_theme: Union[str, Theme] = "dark",
        show_preview: bool = True,
        show_validation: bool = True,
        compact_mode: bool = False,
    ):
        """Initialize theme editor widget.

        Args:
            parent: Parent widget
            base_theme: Theme name or Theme instance to start from
            show_preview: Show live preview panel (Phase 3)
            show_validation: Show accessibility validation (Phase 4)
            compact_mode: Use compact layout for embedding
        """
        super().__init__(parent)

        # Configuration
        self._show_preview = show_preview
        self._show_validation = show_validation
        self._compact_mode = compact_mode

        # Theme management
        self._current_theme: Optional[Theme] = None
        self._theme_builder: Optional[ThemeBuilder] = None
        self._base_theme_name: str = ""

        # Preview debouncing (300ms delay)
        self._preview_timer: Optional[QTimer] = None
        if show_preview:
            self._preview_timer = QTimer()
            self._preview_timer.setSingleShot(True)
            self._preview_timer.setInterval(300)  # 300ms debounce
            self._preview_timer.timeout.connect(self._update_preview)

        # Setup UI
        self._setup_ui()

        # Load base theme
        self.set_theme(base_theme)

        logger.info(f"ThemeEditorWidget initialized (base: {base_theme}, compact: {compact_mode})")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Header with toolbar
        header_layout = QHBoxLayout()
        self._theme_label = QLabel("Editing Theme: ")
        self._theme_name_label = QLabel("(not loaded)")
        self._theme_name_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self._theme_label)
        header_layout.addWidget(self._theme_name_label)
        header_layout.addStretch()

        # Toolbar buttons
        self._import_btn = QPushButton("Import...")
        self._import_btn.clicked.connect(self._on_import)
        header_layout.addWidget(self._import_btn)

        self._export_btn = QPushButton("Export...")
        self._export_btn.clicked.connect(self._on_export)
        header_layout.addWidget(self._export_btn)

        layout.addLayout(header_layout)

        # Main content area - use splitter for resizable panels
        self._splitter = QSplitter()
        layout.addWidget(self._splitter)

        # Left panel: Token browser
        self._token_browser = TokenBrowserWidget()
        self._token_browser.token_selected.connect(self._on_token_selected)
        self._splitter.addWidget(self._token_browser)

        # Middle panel: Token editors
        self._editor_panel = QWidget()
        editor_layout = QVBoxLayout(self._editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Color editor
        self._color_editor = ColorEditorWidget()
        self._color_editor.color_changed.connect(self._on_color_changed)
        editor_layout.addWidget(self._color_editor)

        # Font editor
        self._font_editor = FontEditorWidget()
        self._font_editor.font_changed.connect(self._on_font_changed)
        editor_layout.addWidget(self._font_editor)

        # Initially hide font editor (show based on token type)
        self._font_editor.hide()

        editor_layout.addStretch()
        self._splitter.addWidget(self._editor_panel)

        # Right panel: Live Preview (if enabled)
        if self._show_preview:
            self._preview_widget = ThemePreviewWidget()
            self._splitter.addWidget(self._preview_widget)

        # Set splitter stretch factors to allow preview to expand
        # Token browser: fixed size, Editor: compact, Preview: expands to fill
        self._splitter.setStretchFactor(0, 0)  # Token browser - don't stretch
        self._splitter.setStretchFactor(1, 0)  # Editor panel - don't stretch
        if self._show_preview:
            self._splitter.setStretchFactor(2, 1)  # Preview - stretch to fill available space
            self._splitter.setSizes([300, 400, 600])  # Initial sizes (preview gets more space)
        else:
            self._splitter.setSizes([400, 600])

        # Validation panel (if enabled)
        if self._show_validation:
            self._validation_panel = ValidationPanel()
            self._validation_panel.fix_requested.connect(self._on_fix_requested)
            self._validation_panel.token_highlight_requested.connect(self._on_token_highlight)
            layout.addWidget(self._validation_panel)

    def _on_token_selected(self, token_path: str) -> None:
        """Handle token selection from browser.

        Args:
            token_path: Selected token path
        """
        logger.debug(f"Token selected in editor: {token_path}")
        self.token_selected.emit(token_path)

        # Get token value from current theme
        token_value = self._get_token_value(token_path)

        # Determine token type and show appropriate editor
        if self._is_font_token(token_path):
            # Show font editor
            self._color_editor.hide()
            self._font_editor.show()
            self._font_editor.set_token(token_path, token_value)
        else:
            # Show color editor (default)
            self._font_editor.hide()
            self._color_editor.show()
            self._color_editor.set_token(token_path, token_value)

        # TODO Phase 3: Highlight token in preview

    def _on_color_changed(self, color_value: str) -> None:
        """Handle color editor changes.

        Args:
            color_value: New color value
        """
        token_path = self._token_browser.get_selected_token()
        if token_path and self._theme_builder:
            # Update theme
            self._theme_builder.add_color(token_path, color_value)
            self._current_theme = self._theme_builder.build()

            # Emit modified signal
            self.theme_modified.emit()

            # Schedule preview update (debounced)
            self._schedule_preview_update()

            # Update validation
            self._update_validation()

            logger.debug(f"Token updated: {token_path} = {color_value}")

    def _on_font_changed(self, font_value: str) -> None:
        """Handle font editor changes.

        Args:
            font_value: New font value (CSS string)
        """
        token_path = self._token_browser.get_selected_token()
        if token_path and self._theme_builder:
            # Update theme (fonts are stored in styles)
            self._theme_builder.add_style(token_path, {"font": font_value})
            self._current_theme = self._theme_builder.build()

            # Emit modified signal
            self.theme_modified.emit()

            # Schedule preview update (debounced)
            self._schedule_preview_update()

            # Update validation (font changes don't affect contrast, but keep consistent)
            self._update_validation()

            logger.debug(f"Token updated: {token_path} = {font_value}")

    def _get_token_value(self, token_path: str) -> str:
        """Get current value of a token.

        Args:
            token_path: Token path

        Returns:
            Token value as string
        """
        if not self._current_theme:
            return ""

        # Try colors first
        if token_path in self._current_theme.colors:
            return self._current_theme.colors[token_path]

        # Try styles
        if token_path in self._current_theme.styles:
            style = self._current_theme.styles[token_path]
            if isinstance(style, dict) and "font" in style:
                return style["font"]

        return ""

    def _is_font_token(self, token_path: str) -> bool:
        """Check if token is a font token.

        Args:
            token_path: Token path

        Returns:
            True if font token
        """
        # Font tokens typically contain "font" in the path
        font_keywords = ["font", "fontFamily", "fontSize", "fontWeight"]
        return any(keyword in token_path for keyword in font_keywords)

    def set_theme(self, theme: Union[str, Theme]) -> None:
        """Set theme to edit.

        Args:
            theme: Theme name or Theme instance
        """
        if isinstance(theme, str):
            # Load theme by name
            # TODO: Use ThemeManager to load theme
            self._base_theme_name = theme
            logger.info(f"Loading theme: {theme}")

            # For now, create a new theme from scratch
            self._theme_builder = ThemeBuilder(theme)
            self._current_theme = self._theme_builder.build()

        elif isinstance(theme, Theme):
            # Use existing theme
            self._base_theme_name = theme.name
            self._current_theme = theme

            # Create builder from existing theme (copy-on-write)
            self._theme_builder = ThemeBuilder.from_theme(theme)

        # Update UI
        self._theme_name_label.setText(self._base_theme_name)

        # Initial validation
        self._update_validation()

        logger.info(f"Theme loaded: {self._base_theme_name}")

    def get_theme(self) -> Theme:
        """Get the edited theme.

        Returns:
            Current theme with all modifications
        """
        if self._theme_builder:
            return self._theme_builder.build()
        return self._current_theme

    def validate_theme(self) -> ValidationResult:
        """Validate current theme.

        Returns:
            Validation result with accessibility checks
        """
        # TODO Phase 4: Implement full validation
        # For now, return a placeholder
        from ..validation.framework import ValidationResult

        return ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            metadata={"phase": "Phase 4 - Not yet implemented"}
        )

    def reset_theme(self) -> None:
        """Reset theme to original base theme."""
        if self._base_theme_name:
            self.set_theme(self._base_theme_name)
            self.theme_modified.emit()

    def get_modified_tokens(self) -> dict[str, str]:
        """Get tokens that have been modified from base theme.

        Returns:
            Dict of token_path -> value for modified tokens
        """
        # TODO Phase 7: Track modifications for undo/redo
        return {}

    def _schedule_preview_update(self) -> None:
        """Schedule a debounced preview update."""
        if self._preview_timer:
            # Restart timer (debounce)
            self._preview_timer.start()
            logger.debug("Preview update scheduled (300ms)")

    def _update_preview(self) -> None:
        """Update preview with current theme."""
        if not self._show_preview or not self._current_theme:
            return

        # Apply theme to preview widget (ThemedWidget handles this automatically)
        # We just need to trigger a refresh
        if hasattr(self, '_preview_widget'):
            self._preview_widget.refresh()

        logger.debug(f"Preview updated with theme: {self._current_theme.name}")

    def _update_validation(self) -> None:
        """Update validation panel with current theme colors."""
        if not self._show_validation or not self._current_theme:
            return

        if hasattr(self, '_validation_panel'):
            # Extract color values from theme
            theme_colors = self._current_theme.colors.copy()
            self._validation_panel.validate_theme(theme_colors)

        logger.debug("Validation updated")

    def _on_fix_requested(self, token_path: str, suggested_value: str) -> None:
        """Handle auto-fix request from validation panel.

        Args:
            token_path: Token to fix
            suggested_value: Suggested value
        """
        if self._theme_builder:
            # Apply suggested fix
            self._theme_builder.add_color(token_path, suggested_value)
            self._current_theme = self._theme_builder.build()

            # Update UI
            self.theme_modified.emit()
            self._schedule_preview_update()
            self._update_validation()

            # Select token in browser to show what was fixed
            if hasattr(self, '_token_browser'):
                self._token_browser.select_token(token_path)

            logger.info(f"Auto-fix applied: {token_path} = {suggested_value}")

    def _on_token_highlight(self, token_path: str) -> None:
        """Handle token highlight request from validation panel.

        Args:
            token_path: Token to highlight
        """
        # Select token in browser
        if hasattr(self, '_token_browser'):
            self._token_browser.select_token(token_path)

        logger.debug(f"Token highlighted: {token_path}")

    def _on_import(self) -> None:
        """Handle import button click."""
        dialog = ThemeImportDialog(self)

        def on_imported(theme: Theme):
            # Load imported theme
            self.set_theme(theme)
            self.theme_modified.emit()
            logger.info(f"Theme imported: {theme.name}")

        dialog.theme_imported.connect(on_imported)
        dialog.exec()

    def _on_export(self) -> None:
        """Handle export button click."""
        if not self._current_theme:
            QMessageBox.warning(self, "No Theme", "No theme to export.")
            return

        dialog = ThemeExportDialog(self._current_theme, self)
        dialog.exec()


class ThemeEditorDialog(ThemedDialog):
    """Modal theme editor dialog.

    Standalone dialog for creating or editing themes.

    Signals:
        theme_changed(Theme): Emitted when theme changes (live preview)
        theme_saved(Theme): Emitted when theme is saved
        validation_failed(ValidationResult): Emitted when validation fails
    """

    # Signals
    theme_changed = Signal(Theme)
    theme_saved = Signal(Theme)
    validation_failed = Signal(ValidationResult)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        base_theme: Union[str, Theme] = "dark",
        mode: str = "create",  # "create", "edit", "clone"
        size: QSize = QSize(1200, 800),
    ):
        """Initialize theme editor dialog.

        Args:
            parent: Parent widget
            base_theme: Theme name or Theme instance to start from
            mode: Editor mode ("create", "edit", or "clone")
            size: Initial dialog size
        """
        super().__init__(parent)

        self._mode = mode
        self._original_theme: Optional[Theme] = None

        # Configure dialog
        self.setWindowTitle(f"Theme Editor - {mode.title()}")
        self.resize(size)

        # Setup UI
        self._setup_ui(base_theme)

        logger.info(f"ThemeEditorDialog opened (mode: {mode}, base: {base_theme})")

    def _setup_ui(self, base_theme: Union[str, Theme]) -> None:
        """Setup dialog UI.

        Args:
            base_theme: Base theme to edit
        """
        layout = QVBoxLayout(self)

        # Editor widget (embeddable)
        self._editor = ThemeEditorWidget(
            parent=self,
            base_theme=base_theme,
            show_preview=True,
            show_validation=True,
            compact_mode=False,
        )
        self._editor.theme_modified.connect(self._on_theme_modified)
        layout.addWidget(self._editor)

        # Dialog buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._on_apply
        )
        layout.addWidget(self._button_box)

        # Store original theme for revert on cancel
        self._original_theme = self._editor.get_theme()

    def _on_theme_modified(self) -> None:
        """Handle theme modifications."""
        theme = self._editor.get_theme()
        self.theme_changed.emit(theme)

    def _on_apply(self) -> None:
        """Handle Apply button click."""
        theme = self._editor.get_theme()

        # Validate theme
        validation_result = self._editor.validate_theme()
        if not validation_result.valid:
            self.validation_failed.emit(validation_result)
            return

        # Emit saved signal
        self.theme_saved.emit(theme)
        logger.info(f"Theme applied: {theme.name}")

    def accept(self) -> None:
        """Handle dialog acceptance (OK button)."""
        # Apply changes first
        self._on_apply()

        # Close dialog
        super().accept()

    def reject(self) -> None:
        """Handle dialog rejection (Cancel button)."""
        # Revert to original theme
        if self._original_theme:
            self._editor.set_theme(self._original_theme)
            logger.info("Theme changes reverted")

        super().reject()

    def get_theme(self) -> Theme:
        """Get the edited theme.

        Returns:
            Theme instance with all modifications
        """
        return self._editor.get_theme()

    def export_theme(self, filepath: Optional[Path] = None) -> bool:
        """Export theme to JSON file.

        Args:
            filepath: Optional path to save theme (opens dialog if None)

        Returns:
            True if successful
        """
        theme = self._editor.get_theme()

        if filepath:
            # Direct export to specified path
            try:
                from ..persistence.storage import ThemePersistence

                persistence = ThemePersistence()
                persistence.save_theme(theme, filename=filepath.name)
                logger.info(f"Theme exported to: {filepath}")
                return True
            except Exception as e:
                logger.error(f"Export failed: {e}")
                return False
        else:
            # Open export dialog
            dialog = ThemeExportDialog(theme, self)
            dialog.exec()
            return True

    def import_theme(self, filepath: Optional[Path] = None) -> bool:
        """Import theme from JSON file.

        Args:
            filepath: Optional path to theme file (opens dialog if None)

        Returns:
            True if successful
        """
        if filepath:
            # Direct import from specified path
            try:
                from ..persistence.storage import ThemePersistence

                persistence = ThemePersistence()
                theme = persistence.load_theme(filepath, validate=True)
                self._editor.set_theme(theme)
                logger.info(f"Theme imported from: {filepath}")
                return True
            except Exception as e:
                logger.error(f"Import failed: {e}")
                return False
        else:
            # Open import dialog
            dialog = ThemeImportDialog(self)

            def on_imported(theme: Theme):
                self._editor.set_theme(theme)

            dialog.theme_imported.connect(on_imported)
            dialog.exec()
            return True
