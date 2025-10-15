"""VFTheme Studio - Main Window.

Main application window with three-panel layout.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSplitter, QTabWidget
from vfwidgets_keybinding import KeybindingManager

from .actions import get_action_definitions
from .commands import SetTokenCommand
from .components import StatusBarWidget, create_menu_bar, create_toolbar
from .controllers import PluginRegistry, ThemeController
from .models import ThemeDocument
from .panels import FontBrowserPanel, InspectorPanel, PreviewCanvasPanel, TokenBrowserPanel
from .plugins import DiscoveredWidgetPlugin, GenericWidgetsPlugin
from .widgets import TokenTreeModel

logger = logging.getLogger(__name__)


class ThemeStudioWindow(QMainWindow):
    """Main application window.

    Note: This window does NOT use ThemedWidget. Theme Studio maintains a fixed
    appearance and only applies edited themes to preview widgets.
    """

    def __init__(self):
        super().__init__()

        # Current document (will be set in Task 2.2)
        self._current_document = None

        # Theme controller (MVC controller layer)
        self._theme_controller = None

        # Plugin registry (Task 4.3 + Introspection System)
        self._plugins = {}  # Manual plugins (e.g., GenericWidgetsPlugin)
        self._plugin_registry = PluginRegistry(self)  # Dynamic discovery via entry points

        # Keyboard shortcut manager (Task 11)
        self._setup_keybinding_manager()

        # Window properties
        self.setWindowTitle("VFTheme Studio")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)

        # Apply keyboard shortcuts to window (before UI setup)
        # This creates QActions that the menu bar will reference
        self.actions_by_id = self.keybinding_manager.apply_shortcuts(self)

        # Setup UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()

        # Restore panel sizes from settings
        self._restore_panel_sizes()

        # Register plugins (Task 4.3)
        self._register_plugins()

        # Create initial document
        self._create_new_document()

        # Show status
        self.status_bar.show_status("Ready")

    def closeEvent(self, event):
        """Handle window close event with proper cleanup.

        Args:
            event: QCloseEvent
        """
        # Disconnect document signals before cleanup to prevent signal firing during destruction
        if self._current_document:
            try:
                self._current_document.modified.disconnect(self._on_document_modified)
                self._current_document.token_changed.disconnect(self._on_token_changed)
                self._current_document.file_path_changed.disconnect(self._on_file_path_changed)
            except (RuntimeError, TypeError):
                # Already disconnected or object deleted
                pass

        # Clear preview canvas to properly clean up plugin widget
        if hasattr(self, "preview_canvas") and self.preview_canvas:
            try:
                self.preview_canvas.clear_content()
            except RuntimeError:
                # Widget already deleted
                pass

        # Save panel sizes
        self._save_panel_sizes()

        # Accept the close event
        event.accept()

    def _setup_keybinding_manager(self):
        """Setup keyboard shortcut manager with all action definitions."""
        # Storage path for user-customized keybindings
        config_dir = Path.home() / ".config" / "vftheme-studio"
        config_dir.mkdir(parents=True, exist_ok=True)
        storage_path = config_dir / "keybindings.json"

        # Create keybinding manager with persistent storage
        self.keybinding_manager = KeybindingManager(storage_path=str(storage_path), auto_save=True)

        # Get all action definitions and update with callbacks
        from vfwidgets_keybinding import ActionDefinition

        actions = []
        for base_action in get_action_definitions():
            # Get callback for this action
            callback = self._get_action_callback(base_action.id)

            # Create new ActionDefinition with callback
            action_with_callback = ActionDefinition(
                id=base_action.id,
                description=base_action.description,
                default_shortcut=base_action.default_shortcut,
                category=base_action.category,
                callback=callback,
            )
            actions.append(action_with_callback)

        # Register all actions at once
        self.keybinding_manager.register_actions(actions)

        # Load saved keybindings from storage
        self.keybinding_manager.load_bindings()

    def _get_action_callback(self, action_id: str):
        """Get the callback function for an action ID.

        Args:
            action_id: Action identifier (e.g., "file.save")

        Returns:
            Callback function or None
        """
        # File actions
        if action_id == "file.new":
            return self.new_theme
        elif action_id == "file.new_from_template":
            return lambda: print("New from template (stub)")
        elif action_id == "file.open":
            return self.open_theme
        elif action_id == "file.save":
            return self.save_theme
        elif action_id == "file.save_as":
            return self.save_theme_as
        elif action_id == "file.export":
            return lambda: print("Export (stub)")
        elif action_id == "file.exit":
            return self.close
        # Edit actions
        elif action_id == "edit.undo":
            return self.undo
        elif action_id == "edit.redo":
            return self.redo
        elif action_id == "edit.find":
            return lambda: print("Find token (stub)")
        elif action_id == "edit.preferences":
            return lambda: print("Preferences (stub)")
        # Theme actions
        elif action_id == "theme.validate_accessibility":
            return lambda: print("Validate accessibility (stub)")
        elif action_id == "theme.compare":
            return lambda: print("Compare themes (stub)")
        # View actions
        elif action_id == "view.zoom_in":
            return lambda: print("Zoom in (stub)")
        elif action_id == "view.zoom_out":
            return lambda: print("Zoom out (stub)")
        elif action_id == "view.reset_zoom":
            return lambda: print("Reset zoom (stub)")
        elif action_id == "view.fullscreen":
            return self.toggle_fullscreen
        elif action_id == "view.focus_metadata":
            return self.focus_metadata
        # Tools actions
        elif action_id == "tools.palette_extractor":
            return lambda: print("Palette extractor (stub)")
        elif action_id == "tools.color_harmonizer":
            return lambda: print("Color harmonizer (stub)")
        elif action_id == "tools.bulk_edit":
            return lambda: print("Bulk edit (stub)")
        # Window actions
        elif action_id == "window.reset_layout":
            return lambda: print("Reset layout (stub)")
        # Help actions
        elif action_id == "help.documentation":
            return lambda: print("Documentation (stub)")
        elif action_id == "help.about":
            return self.show_about
        return None

    def _create_menu_bar(self):
        """Create menu bar."""
        create_menu_bar(self)

    def _create_toolbar(self):
        """Create toolbar."""
        self.toolbar = create_toolbar(self)
        self.addToolBar(self.toolbar)

    def _create_central_widget(self):
        """Create three-panel layout with tabbed token browser."""
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL: Tabbed token browser
        self.token_tabs = QTabWidget()

        # Colors tab (existing token browser)
        self.color_browser = TokenBrowserPanel()
        self.token_tabs.addTab(self.color_browser, "Colors")

        # Fonts tab (new font browser)
        self.font_browser = FontBrowserPanel()
        self.token_tabs.addTab(self.font_browser, "Fonts")

        # MIDDLE PANEL: Preview canvas
        self.preview_canvas = PreviewCanvasPanel()

        # RIGHT PANEL: Inspector
        self.inspector_panel = InspectorPanel()

        # Connect color browser to inspector
        self.color_browser.token_selected.connect(self._on_token_selected_for_inspector)
        self.color_browser.token_edit_requested.connect(self._on_token_edit_requested)

        # Connect font browser to inspector
        self.font_browser.font_token_selected.connect(self._on_font_token_selected_for_inspector)
        self.font_browser.font_token_edit_requested.connect(self._on_font_token_edit_requested)

        # NOTE: Inspector no longer emits signals - uses controller pattern
        # Controller will be injected when document is created

        # Add panels to splitter
        self.main_splitter.addWidget(self.token_tabs)  # Tabs instead of single browser
        self.main_splitter.addWidget(self.preview_canvas)
        self.main_splitter.addWidget(self.inspector_panel)

        # Set initial sizes (25% | 50% | 25% of 1600px = 400 | 800 | 400)
        self.main_splitter.setSizes([400, 800, 400])

        # Set stretch factors (preview canvas stretches more)
        self.main_splitter.setStretchFactor(0, 1)  # Token browser
        self.main_splitter.setStretchFactor(1, 2)  # Preview canvas (double)
        self.main_splitter.setStretchFactor(2, 1)  # Inspector

        # Save splitter state when changed
        self.main_splitter.splitterMoved.connect(self._save_panel_sizes)

        # Set as central widget
        self.setCentralWidget(self.main_splitter)

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = StatusBarWidget(self)
        self.setStatusBar(self.status_bar)

    def _restore_panel_sizes(self):
        """Restore panel sizes from settings."""
        settings = QSettings("Vilosource", "VFTheme Studio")
        splitter_state = settings.value("main_splitter/state")
        if splitter_state:
            self.main_splitter.restoreState(splitter_state)

    def _save_panel_sizes(self):
        """Save panel sizes to settings."""
        settings = QSettings("Vilosource", "VFTheme Studio")
        settings.setValue("main_splitter/state", self.main_splitter.saveState())

    # Plugin Management Methods (Task 4.3 + Introspection System)

    def _register_plugins(self):
        """Register available preview plugins (manual + discovered)."""
        # Connect plugin registry signals for observability
        self._plugin_registry.discovery_started.connect(self._on_plugin_discovery_started)
        self._plugin_registry.plugin_discovered.connect(self._on_plugin_discovered)
        self._plugin_registry.plugin_failed.connect(self._on_plugin_failed)
        self._plugin_registry.discovery_completed.connect(self._on_plugin_discovery_completed)
        self._plugin_registry.error_occurred.connect(self._on_plugin_error)

        # Register manual plugins first
        generic_plugin = GenericWidgetsPlugin()
        self._plugins[generic_plugin.get_name()] = generic_plugin
        logger.info(f"Registered manual plugin: {generic_plugin.get_name()}")

        # Discover plugins via entry points
        discovered_metadata = self._plugin_registry.discover_plugins()
        logger.info(f"Plugin discovery completed: {len(discovered_metadata)} plugins found")

        # Create adapters for discovered plugins
        for name, metadata in discovered_metadata.items():
            plugin = DiscoveredWidgetPlugin(metadata)
            self._plugins[name] = plugin
            logger.info(f"Registered discovered plugin: {name} (available={metadata.is_available})")

        # Add all plugins to preview canvas selector
        for plugin_name in self._plugins.keys():
            self.preview_canvas.plugin_selector.addItem(plugin_name)

        # Connect plugin selection change
        self.preview_canvas.plugin_selector.currentTextChanged.connect(self._on_plugin_selected)

        # Load first plugin by default
        if self._plugins:
            first_plugin = list(self._plugins.keys())[0]
            self.preview_canvas.plugin_selector.setCurrentText(first_plugin)

    def _on_plugin_discovery_started(self):
        """Handle plugin discovery started."""
        logger.debug("Plugin discovery started")
        self.status_bar.show_status("Discovering plugins...", 1000)

    def _on_plugin_discovered(self, name: str, metadata):
        """Handle plugin discovered.

        Args:
            name: Plugin name
            metadata: WidgetMetadata object
        """
        logger.info(f"Discovered plugin: {name} v{metadata.version}")

    def _on_plugin_failed(self, name: str, error_message: str):
        """Handle plugin load failure.

        Args:
            name: Plugin name
            error_message: Error message
        """
        logger.warning(f"Plugin '{name}' failed to load: {error_message}")

    def _on_plugin_discovery_completed(self, count: int):
        """Handle plugin discovery completed.

        Args:
            count: Number of successfully discovered plugins
        """
        logger.info(f"Plugin discovery completed: {count} plugins available")
        if count > 0:
            self.status_bar.show_status(f"Discovered {count} plugin(s)", 2000)

    def _on_plugin_error(self, context: str, message: str, exception: Exception):
        """Handle plugin system error.

        Args:
            context: Error context
            message: Error message
            exception: Exception that occurred
        """
        logger.error(f"Plugin error in {context}: {message}", exc_info=exception)

    def _on_plugin_selected(self, plugin_name: str):
        """Handle plugin selection change.

        Args:
            plugin_name: Selected plugin name
        """
        if plugin_name == "(None)" or not plugin_name:
            # Clear canvas
            self.preview_canvas.clear_content()
            # Clear token filter
            self.color_browser.set_current_widget_tokens(None)
            return

        # Get plugin
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return

        # Create and set preview widget
        preview_widget = plugin.create_preview_widget()
        self.preview_canvas.set_plugin_content(preview_widget)

        # Update token browser with widget's tokens (for filtering)
        from .plugins.discovered_plugin import DiscoveredWidgetPlugin

        if isinstance(plugin, DiscoveredWidgetPlugin):
            # Get unique token paths from the plugin's metadata
            token_paths = set(plugin.metadata.unique_token_paths)
            self.color_browser.set_current_widget_tokens(token_paths)
        else:
            # Manual plugins don't have metadata, show all tokens
            self.color_browser.set_current_widget_tokens(None)

        # Apply current theme to the newly loaded widget
        # This ensures the widget gets the theme on initial load (not just on changes)
        if self._current_document:
            self._update_preview_theme(self._current_document.theme)

        # Show status
        self.status_bar.show_status(f"Loaded plugin: {plugin_name}", 2000)

    # Inspector Connection (Task 5.2 & 8.1)

    def _on_token_selected_for_inspector(self, token_name: str):
        """Handle token selection for inspector display.

        Args:
            token_name: Selected token name
        """
        if not self._current_document:
            return

        # Get token value from document
        token_value = self._current_document.get_token(token_name)

        # Update inspector
        self.inspector_panel.set_token(token_name, token_value)

    def _on_font_token_selected_for_inspector(self, token_path: str):
        """Handle font token selection for inspector display.

        Args:
            token_path: Selected font token path (e.g., "terminal.fontSize")
        """
        if not self._current_document:
            return

        # Get font token value from document
        token_value = self._current_document.get_font(token_path)

        # Update inspector with font token
        self.inspector_panel.set_font_token(token_path, token_value, self._current_document.theme)

    def _on_font_token_edit_requested(self, token_path: str, current_value):
        """Handle double-click on font token - show editor in inspector.

        Args:
            token_path: Font token path to edit
            current_value: Current token value (may be None)
        """
        if not self._current_document:
            return

        # Same as single-click - show the font editor in inspector
        self.inspector_panel.set_font_token(token_path, current_value, self._current_document.theme)

    def _on_token_edit_requested(self, token_name: str, current_value: str):
        """Handle double-click on token - open color editor directly.

        Args:
            token_name: Token name to edit
            current_value: Current token value (may be empty)
        """
        if not self._current_document or not self._theme_controller:
            return

        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog

        # Get initial color
        initial_color = QColor(current_value) if current_value else QColor("#ffffff")

        # Open color picker using Qt's static method
        selected_color = QColorDialog.getColor(
            initial_color,
            self,
            f"Edit Color: {token_name}",
            QColorDialog.ShowAlphaChannel | QColorDialog.DontUseNativeDialog,
        )

        # If user selected a color, apply it
        if selected_color.isValid():
            hex_color = selected_color.name()

            # Update via controller (uses same pattern as inspector)
            self._theme_controller.queue_token_change(token_name, hex_color)

            # Also update inspector if it's showing this token
            self.inspector_panel.set_token(token_name, hex_color)

    # DEPRECATED: InspectorPanel now uses ThemeController directly
    # This method is kept for reference but is no longer called
    def _on_token_value_changed_DEPRECATED(self, token_name: str, new_value: str):
        """[DEPRECATED] Handle token value change from inspector.

        NOTE: This method is no longer used. InspectorPanel now uses
        ThemeController.queue_token_change() which directly updates the document.

        Args:
            token_name: Token name that was changed
            new_value: New token value
        """
        if not self._current_document:
            return

        # Get old value for undo
        old_value = self._current_document.get_token(token_name)

        # Create and push undo command
        command = SetTokenCommand(self._current_document, token_name, new_value, old_value)
        self._current_document._undo_stack.push(command)

        # Show status
        self.status_bar.show_status(f"Updated {token_name}", 2000)

    # Document Management Methods

    def _create_new_document(self):
        """Create a new document."""
        document = ThemeDocument()
        self.set_document(document)

    def set_document(self, document: ThemeDocument):
        """Set current theme document.

        Args:
            document: ThemeDocument to set as current
        """
        # Disconnect old document signals
        if self._current_document:
            self._current_document.modified.disconnect(self._on_document_modified)
            self._current_document.token_changed.disconnect(self._on_token_changed)
            self._current_document.font_changed.disconnect(self._on_font_changed)
            self._current_document.metadata_changed.disconnect(self._on_metadata_changed)
            self._current_document.file_path_changed.disconnect(self._on_file_path_changed)

        # Set new document
        self._current_document = document

        # Create controller for this document (MVC pattern)
        self._theme_controller = ThemeController(document)

        # Inject controller into inspector panel
        self.inspector_panel.set_controller(self._theme_controller)

        # Populate inspector metadata fields from document
        self.inspector_panel.populate_metadata_fields(document)

        # Connect document signals to window
        document.modified.connect(self._on_document_modified)
        document.token_changed.connect(self._on_token_changed)
        document.font_changed.connect(self._on_font_changed)
        document.metadata_changed.connect(self._on_metadata_changed)
        document.file_path_changed.connect(self._on_file_path_changed)

        # Connect undo stack signals to menu items (Task 9.2)
        # Get undo/redo actions from keybinding manager
        undo_action = self.actions_by_id.get("edit.undo")
        redo_action = self.actions_by_id.get("edit.redo")

        if undo_action and redo_action:
            document._undo_stack.canUndoChanged.connect(undo_action.setEnabled)
            document._undo_stack.canRedoChanged.connect(redo_action.setEnabled)
            # Update initial state
            undo_action.setEnabled(document._undo_stack.canUndo())
            redo_action.setEnabled(document._undo_stack.canRedo())

        # Create token tree model and set it on the color browser (Task 3.2)
        token_model = TokenTreeModel(document)
        self.color_browser.set_model(token_model)

        # Set document on font browser (uses FontTreeModel internally)
        self.font_browser.set_document(document)

        # Set initial theme for preview (Task 10.1)
        # ARCHITECTURAL FIX: Only update preview, not entire app
        try:
            self._update_preview_theme(document.theme)
        except Exception as e:
            print(f"Warning: Failed to set initial theme: {e}")

        # Update UI
        self._update_window_title()
        self._update_status_bar()

    def _update_preview_theme(self, theme):
        """Apply edited theme to preview widgets only.

        This manually generates and applies stylesheets from the edited theme
        directly to preview widgets, without using the global theme system.

        Theme Studio UI maintains OS/system appearance.

        Args:
            theme: Theme object to apply to preview widgets
        """
        logger.debug("_update_preview_theme: START")
        if not hasattr(self, "preview_canvas") or not self.preview_canvas:
            logger.debug("_update_preview_theme: No preview canvas")
            return

        # Get the actual plugin widget being displayed
        plugin_widget = self.preview_canvas._current_plugin
        if not plugin_widget:
            logger.debug("_update_preview_theme: No plugin widget")
            return

        logger.debug(
            f"_update_preview_theme: Plugin widget class={plugin_widget.__class__.__name__}"
        )

        # Check if widget is being destroyed
        try:
            if not plugin_widget.isVisible() and plugin_widget.parent() is None:
                # Widget is being deleted, don't apply theme
                logger.debug("_update_preview_theme: Widget being deleted, skipping")
                return
        except RuntimeError:
            # Widget already deleted
            logger.debug("_update_preview_theme: Widget already deleted")
            return

        try:
            # Import theme system generators
            from vfwidgets_theme.widgets.palette_generator import PaletteGenerator
            from vfwidgets_theme.widgets.stylesheet_generator import StylesheetGenerator

            logger.debug("_update_preview_theme: Generating stylesheet and palette")
            # Generate stylesheet for the plugin widget
            generator = StylesheetGenerator(theme, plugin_widget.__class__.__name__)
            stylesheet = generator.generate_comprehensive_stylesheet()

            # Generate QPalette for proper Qt widget theming
            palette_gen = PaletteGenerator(theme)
            palette = palette_gen.generate_palette()

            logger.debug(f"_update_preview_theme: Generated stylesheet ({len(stylesheet)} chars):")
            logger.debug(f"_update_preview_theme: First 500 chars:\n{stylesheet[:500]}")
            # Also log QGroupBox section to verify background-color fix
            groupbox_start = stylesheet.find("/* QGroupBox */")
            if groupbox_start != -1:
                groupbox_section = stylesheet[groupbox_start : groupbox_start + 200]
                logger.debug(f"_update_preview_theme: QGroupBox section:\n{groupbox_section}")
            logger.debug("_update_preview_theme: Stylesheet and palette generated, applying...")

            # Double-check widget is still valid before applying
            try:
                if not plugin_widget.isVisible() and plugin_widget.parent() is None:
                    logger.debug("_update_preview_theme: Widget deleted before apply, skipping")
                    return
            except RuntimeError:
                logger.debug("_update_preview_theme: Widget deleted (RuntimeError)")
                return

            # Apply ONLY to plugin widget (not to Theme Studio UI)
            # Wrap in try/except in case widget gets deleted mid-application
            try:
                logger.debug("_update_preview_theme: Setting stylesheet...")
                plugin_widget.setStyleSheet(stylesheet)
                logger.debug("_update_preview_theme: Stylesheet applied")
            except RuntimeError:
                logger.debug("_update_preview_theme: RuntimeError setting stylesheet")
                return

            try:
                logger.debug("_update_preview_theme: Setting palette...")
                plugin_widget.setPalette(palette)
                logger.debug("_update_preview_theme: Palette applied")
            except RuntimeError:
                logger.debug("_update_preview_theme: RuntimeError setting palette")
                return

            # Call on_theme_changed() for widgets with custom theme handling
            # This is essential for widgets like TerminalWidget that need to inject
            # JavaScript or perform other custom theme updates beyond stylesheet/palette
            if hasattr(plugin_widget, "on_theme_changed") and callable(
                plugin_widget.on_theme_changed
            ):
                try:
                    logger.debug(
                        "_update_preview_theme: Calling widget's on_theme_changed() method"
                    )

                    # Temporarily update widget's theme manager to use the edited theme
                    # This allows the widget to read correct theme values via self.theme
                    old_theme = None
                    if hasattr(plugin_widget, "_theme_manager") and plugin_widget._theme_manager:
                        old_theme = plugin_widget._theme_manager.current_theme
                        plugin_widget._theme_manager._current_theme = theme
                        # Invalidate property cache so it reads from new theme
                        if hasattr(plugin_widget, "_theme_properties"):
                            plugin_widget._theme_properties.invalidate_cache()

                    # Call the widget's custom theme handler with the theme
                    # Pass theme directly to support widgets that don't use ThemedWidget's
                    # theme manager (like terminal widget with custom theme handling)
                    logger.info("🔍 [Theme Studio] About to call plugin_widget.on_theme_changed()")
                    logger.info(f"🔍 [Theme Studio] theme parameter: {theme}")
                    logger.info(f"🔍 [Theme Studio] theme type: {type(theme)}")
                    logger.info(f"🔍 [Theme Studio] theme.colors type: {type(theme.colors)}")
                    logger.info(
                        f"🔍 [Theme Studio] theme.colors keys (first 10): {list(theme.colors.keys())[:10]}"
                    )
                    if "colors.background" in theme.colors:
                        logger.info(
                            f"🔍 [Theme Studio] theme.colors['colors.background'] = {theme.colors['colors.background']}"
                        )
                    else:
                        logger.warning(
                            "🔥 [Theme Studio] 'colors.background' NOT FOUND in theme.colors!"
                        )

                    # Log font information
                    logger.info(f"🔍 [Theme Studio] theme has fonts: {hasattr(theme, 'fonts')}")
                    if hasattr(theme, "fonts"):
                        logger.info(f"🔍 [Theme Studio] theme.fonts type: {type(theme.fonts)}")
                        logger.info(f"🔍 [Theme Studio] theme.fonts keys: {list(theme.fonts.keys())[:10] if theme.fonts else 'None'}")
                        if theme.fonts and "terminal.fontSize" in theme.fonts:
                            logger.info(f"🔍 [Theme Studio] theme.fonts['terminal.fontSize'] = {theme.fonts['terminal.fontSize']}")
                        if theme.fonts and "fonts.mono" in theme.fonts:
                            logger.info(f"🔍 [Theme Studio] theme.fonts['fonts.mono'] = {theme.fonts['fonts.mono']}")

                    plugin_widget.on_theme_changed(theme)

                    # Restore original theme
                    if old_theme is not None and hasattr(plugin_widget, "_theme_manager"):
                        plugin_widget._theme_manager._current_theme = old_theme
                        if hasattr(plugin_widget, "_theme_properties"):
                            plugin_widget._theme_properties.invalidate_cache()

                    logger.info("🔍 [Theme Studio] on_theme_changed() completed")
                except Exception as e:
                    logger.warning(
                        f"_update_preview_theme: Error in widget's on_theme_changed(): {e}"
                    )

            # Also apply theme to the canvas background for better visual feedback
            try:
                bg_color = theme.colors.get("colors.background", "#1e1e1e")
                fg_color = theme.colors.get("colors.foreground", "#d4d4d4")
                logger.debug(
                    f"_update_preview_theme: Applying canvas theme: bg={bg_color}, fg={fg_color}"
                )
                self.preview_canvas.apply_canvas_theme(bg_color, fg_color)
                logger.debug("_update_preview_theme: Canvas theme applied")
            except Exception as e:
                logger.warning(f"_update_preview_theme: Failed to apply canvas theme: {e}")

            logger.debug("_update_preview_theme: END")

        except RuntimeError:
            # Widget was deleted during theme application
            pass
        except Exception as e:
            print(f"Error applying preview theme: {e}")
            import traceback

            traceback.print_exc()

    def _on_document_modified(self, is_modified: bool):
        """Handle document modified state change.

        Args:
            is_modified: Whether document is modified
        """
        self._update_window_title()

    def _on_token_changed(self, token_name: str, token_value: str):
        """Handle token value change.

        Args:
            token_name: Name of changed token
            token_value: New token value
        """
        logger.debug(f"_on_token_changed: token={token_name}, value={token_value}")

        # Update status bar with token count
        self._update_status_bar()

        # Update preview canvas with new theme (Task 10.1)
        # ARCHITECTURAL FIX: Only update preview widgets, NOT the entire application!
        # The Theme Studio UI should maintain its own stable theme.
        #
        # IMPORTANT: Defer theme update to next event loop iteration to avoid
        # conflicts with active widget operations.
        if self._current_document and hasattr(self, "preview_canvas"):
            logger.debug("_on_token_changed: Scheduling deferred preview theme update")
            # Use QTimer.singleShot with method reference (no lambda to avoid capture issues)
            QTimer.singleShot(0, self._deferred_update_preview_theme)

        # NOTE: Do NOT update inspector here!
        # The inspector already updated its own UI in _apply_color_change_immediate().
        # Calling inspector.set_token() here causes a synchronous UI update during
        # the signal chain, which can conflict with dialog cleanup and cause segfaults.

    def _on_font_changed(self, token_path: str, new_value):
        """Handle font token value change.

        Args:
            token_path: Path of changed font token
            new_value: New font value (list, int, float, or str)
        """
        logger.debug(f"_on_font_changed: token={token_path}, value={new_value}")

        # Font browser updates automatically via FontTreeModel's font_changed connection
        # No manual update needed

        # Update status bar
        self._update_status_bar()

        # Update preview canvas (fonts affect rendering)
        if self._current_document and hasattr(self, "preview_canvas"):
            logger.debug("_on_font_changed: Scheduling deferred preview theme update")
            QTimer.singleShot(0, self._deferred_update_preview_theme)

    def _on_metadata_changed(self, field: str, value: str):
        """Handle metadata field change.

        Args:
            field: Metadata field name (name, version, type, author, description)
            value: New field value
        """
        logger.debug(f"_on_metadata_changed: field={field}, value={value}")

        # Update window title if name or version changed
        if field in ("name", "version"):
            self._update_window_title()

        # Update inspector panel metadata fields (for undo/redo support)
        if hasattr(self, "inspector_panel"):
            self.inspector_panel.on_metadata_changed(field, value)

    def _deferred_update_preview_theme(self):
        """Deferred theme update for preview widgets.

        This is called via QTimer.singleShot to ensure theme updates happen
        after the current event handler completes, avoiding conflicts with
        active dialogs or widget operations.
        """
        logger.debug("_deferred_update_preview_theme: START")
        if not self._current_document or not hasattr(self, "preview_canvas"):
            logger.debug("_deferred_update_preview_theme: No document or preview canvas, skipping")
            return

        try:
            # Apply theme ONLY to preview widgets, not the entire app
            logger.debug("_deferred_update_preview_theme: Calling _update_preview_theme")
            self._update_preview_theme(self._current_document.theme)
            logger.debug("_deferred_update_preview_theme: Theme update complete, END")
        except Exception as e:
            logger.error(f"Failed to update preview theme: {e}", exc_info=True)

    def _on_file_path_changed(self, file_path: str):
        """Handle file path change.

        Args:
            file_path: New file path
        """
        self._update_window_title()
        self.status_bar.show_status(f"Loaded: {file_path}", 3000)

    def _update_window_title(self):
        """Update window title with theme name, version, and modified state."""
        if not self._current_document:
            self.setWindowTitle("VFTheme Studio")
            return

        # Get theme name and version
        name = self._current_document.theme.name or "Untitled"
        version = self._current_document.theme.version or "1.0.0"

        # Add modified indicator
        modified = "*" if self._current_document.is_modified() else ""

        # Set title: "Theme Name v1.0.0* - VFTheme Studio"
        self.setWindowTitle(f"{name} v{version}{modified} - VFTheme Studio")

    def _update_status_bar(self):
        """Update status bar with current document info."""
        if not self._current_document:
            self.status_bar.update_theme_info("No theme loaded", False)
            self.status_bar.update_token_count(0, 197)
            self.status_bar.update_font_count(0, 22)
            return

        # Update theme info
        theme_name = self._current_document.file_name or self._current_document.theme.name
        is_modified = self._current_document.is_modified()
        self.status_bar.update_theme_info(theme_name, is_modified)

        # Update color token count
        color_defined, color_total = self._current_document.get_token_count()
        self.status_bar.update_token_count(color_defined, color_total)

        # Update font token count
        font_defined, font_total = self._current_document.get_font_count()
        self.status_bar.update_font_count(font_defined, font_total)

    # File actions (Task 6.1-6.3)
    def new_theme(self):
        """Create new theme.

        Prompts to save if current document is modified, then creates a new empty theme.
        """
        # Check if we need to save current document
        if self._current_document and self._current_document.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current theme has unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                # Try to save, cancel if save fails
                if not self._save_current_document():
                    return
            elif reply == QMessageBox.Cancel:
                return
            # If Discard, continue with creating new theme

        # Create new document
        document = ThemeDocument()
        self.set_document(document)

        # Show status
        self.status_bar.show_status("Created new theme", 2000)

    def _save_current_document(self) -> bool:
        """Save the current document.

        Returns:
            True if save successful, False if cancelled or failed
        """
        if not self._current_document:
            return False

        # If document has no file path, use Save As
        if not self._current_document.file_path:
            return self._save_document_as()
        else:
            return self._save_document_to_path(self._current_document.file_path)

    def open_theme(self):
        """Open theme from file.

        Prompts to save if current document is modified, then shows open dialog.
        """
        # Check if we need to save current document
        if self._current_document and self._current_document.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current theme has unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                # Try to save, cancel if save fails
                if not self._save_current_document():
                    return
            elif reply == QMessageBox.Cancel:
                return
            # If Discard, continue with opening

        # Show open file dialog
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Theme",
            "",
            "Theme Files (*.json);;All Files (*)",  # Default directory
        )

        if not file_path:
            # User cancelled
            return

        # Load theme
        try:
            document = ThemeDocument()
            document.load(file_path)
            self.set_document(document)
            self.status_bar.show_status(f"Opened: {document.file_name}", 3000)
        except Exception as e:
            QMessageBox.critical(
                self, "Error Opening Theme", f"Failed to open theme file:\n\n{str(e)}"
            )
            self.status_bar.show_status("Failed to open theme", 3000)

    def save_theme(self):
        """Save theme to current file."""
        if not self._save_current_document():
            self.status_bar.show_status("Save cancelled", 2000)

    def save_theme_as(self):
        """Save theme to a new file."""
        if self._save_document_as():
            self.status_bar.show_status("Theme saved", 2000)
        else:
            self.status_bar.show_status("Save cancelled", 2000)

    def _save_document_as(self) -> bool:
        """Show save dialog and save to selected path.

        Returns:
            True if save successful, False if cancelled or failed
        """
        if not self._current_document:
            return False

        # Show save file dialog
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Theme As",
            "",
            "Theme Files (*.json);;All Files (*)",  # Default directory
        )

        if not file_path:
            # User cancelled
            return False

        # Ensure .json extension
        if not file_path.endswith(".json"):
            file_path += ".json"

        # Save to path
        return self._save_document_to_path(file_path)

    def _save_document_to_path(self, file_path: str) -> bool:
        """Save document to specific path.

        Args:
            file_path: Path to save to

        Returns:
            True if save successful, False if failed
        """
        if not self._current_document:
            return False

        try:
            self._current_document.save(file_path)
            self.status_bar.show_status(f"Saved: {self._current_document.file_name}", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(
                self, "Error Saving Theme", f"Failed to save theme file:\n\n{str(e)}"
            )
            self.status_bar.show_status("Failed to save theme", 3000)
            return False

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_about(self):
        """Show about dialog."""
        from . import __version__

        QMessageBox.about(
            self,
            "About VFTheme Studio",
            f"<h3>VFTheme Studio v{__version__}</h3>"
            f"<p>Visual Theme Designer for VFWidgets Applications</p>"
            f"<p>Phase 1 Development - Foundation</p>"
            f"<p><small>© 2025 Vilosource</small></p>",
        )

    # Undo/Redo Actions (Task 9.2)

    def undo(self):
        """Undo last action."""
        if self._current_document and self._current_document._undo_stack.canUndo():
            self._current_document._undo_stack.undo()
            self.status_bar.show_status("Undo", 1000)

    def redo(self):
        """Redo last undone action."""
        if self._current_document and self._current_document._undo_stack.canRedo():
            self._current_document._undo_stack.redo()
            self.status_bar.show_status("Redo", 1000)

    def focus_metadata(self):
        """Focus the theme properties metadata section in inspector (Ctrl+I)."""
        if hasattr(self, "inspector_panel"):
            self.inspector_panel.focus_metadata()
