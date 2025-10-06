# Context Menu Architecture Specification

**Version**: 1.0
**Status**: Draft
**Author**: VFWidgets Team
**Date**: 2025-10-06

## Overview

This specification defines a composable context menu architecture for VFWidgets that enables heterogeneous widget types (TerminalWidget, TextEditor, Browser, etc.) to coexist in MultisplitWidget with appropriate context-specific menus at each layer of the widget hierarchy.

## Design Goals

1. **Separation of Concerns**: Each layer manages its own context menu actions
2. **Composition**: Menus automatically merge from widget → pane → tab → application
3. **Optional Participation**: Widgets can opt-in to context menu system
4. **Backward Compatible**: Existing widgets work without modifications
5. **Type-Specific**: Different widget types can have different context menus
6. **DRY Principle**: Reuse existing QAction infrastructure (shortcuts included automatically)
7. **Leverage VFWidgets Infrastructure**: Use KeybindingManager, Theme System, and existing protocols

## VFWidgets Infrastructure Integration

This design leverages existing VFWidgets components to avoid reinventing solutions:

### KeybindingManager Integration

**Component**: `vfwidgets-keybinding-manager`

**Benefits**:
- QActions pre-configured with shortcuts
- Action categories for organization
- i18n-ready descriptions via `tr()`
- Persistent user customization
- Conflict detection

**Usage Pattern**:
```python
# Application creates and registers actions ONCE
keybinding_manager = KeybindingManager(storage_path="~/.config/myapp/keys.json")
keybinding_manager.register_actions([
    ActionDefinition(id="pane.split_vertical", description="Split Vertical",
                    default_shortcut="Ctrl+Shift+V", category="Pane"),
    ActionDefinition(id="pane.split_horizontal", description="Split Horizontal",
                    default_shortcut="Ctrl+Shift+H", category="Pane"),
    ActionDefinition(id="pane.close", description="Close Pane",
                    default_shortcut="Ctrl+W", category="Pane"),
])

# Get actions to pass to MultisplitWidget
actions = keybinding_manager.apply_shortcuts(main_window)

# MultisplitWidget uses these actions in context menus
multisplit.set_pane_actions([
    actions["pane.split_vertical"],
    actions["pane.split_horizontal"],
    None,  # Separator
    actions["pane.close"]
])
```

### Theme System Integration

**Component**: `vfwidgets-theme-system`

**Benefits**:
- Consistent menu styling across application
- Dark/light theme support
- Custom theme colors: `menu.background`, `menu.selection.background`, etc.

**Usage Pattern**:
```python
# QMenu automatically styled by theme
menu = QMenu(self)
# Theme system applies stylesheet to menu based on current theme
```

### MultisplitWidget Protocol

**Component**: `vfwidgets-multisplit-widget`

**Existing Infrastructure**:
- `WidgetProvider` protocol for widget lifecycle
- `PaneId`, `WidgetId` type system
- Event system for pane lifecycle

**Extension**: Add optional context menu methods to existing protocols (see below)

## Architecture Layers

The system composes context menus across four distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Application (ViloxTerm)                            │
│ - App-wide actions (Preferences, About, etc.)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: ChromeTabbedWindow                                 │
│ - Tab actions (Close Tab, Close Others, etc.)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: MultisplitWidget                                   │
│ - Pane actions (Split Vertical, Split Horizontal, Close)    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Individual Widgets (TerminalWidget, TextEdit, etc.)│
│ - Widget-specific actions (Copy, Paste, Find, etc.)         │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1: Individual Widgets

### Current State

**TerminalWidget** already implements a complete context menu system:

```python
# Three customization approaches:

# A) Add actions to default menu
terminal.add_context_menu_action(action)

# B) Replace menu entirely
def custom_menu(pos: QPoint, selected_text: str) -> Optional[QMenu]:
    menu = QMenu()
    # ... build menu
    return menu
terminal.set_context_menu_handler(custom_menu)

# C) React to signal
terminal.contextMenuRequested.connect(lambda event: ...)
```

### Specification

**No changes required** for Layer 1. Individual widgets handle their own context menus using Qt's standard `contextMenuEvent()` mechanism or custom implementations.

**Contract**: Widgets are responsible for their own widget-specific actions (Copy, Paste, Find, formatting, etc.).

---

## Layer 2: MultisplitWidget - Pane Context Menus

### Integration with KeybindingManager

**Key Insight**: VFWidgets already has `KeybindingManager` which provides:
- QAction objects with shortcuts already configured
- Action categories for organization
- i18n-ready action descriptions
- Persistent shortcut customization

**Design Decision**: Pane-level actions (Split, Close) should be managed by `KeybindingManager` and passed to `MultisplitWidget` via API, NOT created internally.

### New Protocol: `ContextMenuProvider`

**Purpose**: Optional protocol for widgets that want to participate in context menu composition.

**Location**: `vfwidgets_multisplit/view/container.py`

```python
from typing import Protocol, Optional, List
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint

class ContextMenuProvider(Protocol):
    """Optional protocol for widgets that want to participate in context menu composition.

    Widgets implementing this protocol can contribute their own actions to the
    composed context menu shown by MultisplitWidget.
    """

    def get_context_menu_actions(self, position: QPoint) -> List[QAction]:
        """Return list of actions to include in context menu.

        Args:
            position: Position where context menu was requested (widget coordinates)

        Returns:
            List of QActions to add to menu. Return empty list for no actions.
            Use None in list to represent a separator.

        Note:
            This is called by MultisplitWidget when building the composed context menu.
            The widget can return dynamic actions based on position/state.

        Example:
            def get_context_menu_actions(self, position):
                actions = []

                # Add Copy action (only if text selected)
                if self.has_selection():
                    copy = QAction("Copy", self)
                    copy.triggered.connect(self.copy)
                    actions.append(copy)

                # Add Paste action
                paste = QAction("Paste", self)
                paste.triggered.connect(self.paste)
                actions.append(paste)

                return actions
        """
        ...
```

### WidgetProvider - No Changes Needed

**Important**: The `WidgetProvider` protocol does **NOT** need any context menu-related methods.

**Rationale**:
- Pane actions come from KeybindingManager via `set_pane_actions()`
- WidgetProvider focuses on widget lifecycle only
- Keeps protocol simple and focused

**Existing WidgetProvider** (unchanged):
```python
class WidgetProvider(Protocol):
    """Protocol for widget provider."""

    def provide_widget(self, widget_id: WidgetId, pane_id: PaneId) -> QWidget:
        """Provide widget for pane."""
        ...

    def widget_closing(self, widget_id: WidgetId, pane_id: PaneId, widget: QWidget) -> None:
        """Called before widget removal."""
        ...

    # No context menu methods needed - actions come from KeybindingManager
```

### MultisplitWidget Public API

**Location**: `vfwidgets_multisplit/multisplit.py`

```python
class MultisplitWidget:

    def enable_context_menus(self, enabled: bool = True) -> None:
        """Enable/disable automatic context menu handling for panes.

        Args:
            enabled: If True, right-click on panes shows composed context menu

        When enabled, the context menu includes (in order):
        1. Widget's own actions (if widget implements ContextMenuProvider)
        2. Separator (if widget provided actions)
        3. Pane actions from set_pane_actions()
        4. Separator (if app actions exist)
        5. App-level actions from add_context_menu_action()

        Default: False (disabled)

        Example:
            multisplit = MultisplitWidget(provider=my_provider)
            multisplit.enable_context_menus(True)
        """
        self._context_menus_enabled = enabled

    def set_pane_actions(self, actions: List[QAction | None]) -> None:
        """Set pane-level actions (Split, Close, etc.) for context menus.

        Args:
            actions: List of QActions for pane operations. Use None for separators.

        Note:
            These actions should come from KeybindingManager with shortcuts already configured.
            Actions are shown in all pane context menus between widget actions and app actions.

        Example (using KeybindingManager):
            # Get actions from keybinding manager
            kb_actions = keybinding_manager.apply_shortcuts(main_window)

            # Set pane actions for context menu
            multisplit.set_pane_actions([
                kb_actions["pane.split_vertical"],
                kb_actions["pane.split_horizontal"],
                None,  # Separator
                kb_actions["pane.close"]
            ])
        """
        self._pane_actions = actions

    def add_context_menu_action(self, action: QAction) -> None:
        """Add app-level action to all pane context menus.

        Args:
            action: QAction to add to context menus (shown at bottom of menu)

        Note:
            These actions appear in all pane context menus, regardless of widget type.
            Use this for app-wide actions like Preferences, About, etc.
            Actions should come from KeybindingManager.

        Example (using KeybindingManager):
            kb_actions = keybinding_manager.apply_shortcuts(main_window)
            multisplit.add_context_menu_action(kb_actions["appearance.terminal_preferences"])
            multisplit.add_context_menu_action(kb_actions["appearance.terminal_theme"])
        """
        if not hasattr(self, '_app_context_actions'):
            self._app_context_actions = []
        self._app_context_actions.append(action)

    def remove_context_menu_action(self, action: QAction) -> None:
        """Remove app-level action from pane context menus.

        Args:
            action: QAction to remove
        """
        if hasattr(self, '_app_context_actions') and action in self._app_context_actions:
            self._app_context_actions.remove(action)

    def clear_context_menu_actions(self) -> None:
        """Remove all app-level actions from pane context menus."""
        if hasattr(self, '_app_context_actions'):
            self._app_context_actions.clear()

    def set_pane_action_provider(
        self,
        provider: Optional[Callable[[PaneId, QWidget], List[QAction]]]
    ) -> None:
        """Set custom provider for pane-level actions (advanced).

        Args:
            provider: Function(pane_id, widget) -> List[QAction], or None to reset

        This overrides WidgetProvider.get_pane_context_actions() and the default
        Split/Close actions. Use this for complete customization of pane actions.

        Example:
            def custom_pane_actions(pane_id, widget):
                return [
                    QAction("Custom Split", widget),
                    QAction("Custom Close", widget)
                ]

            multisplit.set_pane_action_provider(custom_pane_actions)
        """
        self._custom_pane_action_provider = provider
```

### Context Menu Composition Algorithm

**Location**: `vfwidgets_multisplit/view/container.py` (in Container class)

```python
def _show_pane_context_menu(self, pane_id: PaneId, global_pos: QPoint, widget_pos: QPoint) -> None:
    """Show composed context menu for pane.

    Args:
        pane_id: ID of the pane
        global_pos: Global position for menu (screen coordinates)
        widget_pos: Position in widget coordinates
    """
    if not self._context_menus_enabled:
        return

    menu = QMenu(self)
    widget = self._widget_pool.get_widget(pane_id)

    # 1. Widget-specific actions (if widget implements ContextMenuProvider)
    if hasattr(widget, 'get_context_menu_actions'):
        widget_actions = widget.get_context_menu_actions(widget_pos)
        if widget_actions:
            for action in widget_actions:
                if action is None:
                    menu.addSeparator()
                else:
                    menu.addAction(action)
            menu.addSeparator()  # Separator before pane actions

    # 2. Pane-level actions
    pane_actions = self._get_pane_actions(pane_id, widget)
    if pane_actions:
        for action in pane_actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)

    # 3. App-level actions
    if hasattr(self, '_app_context_actions') and self._app_context_actions:
        menu.addSeparator()
        for action in self._app_context_actions:
            menu.addAction(action)

    # Show menu if it has any actions
    if not menu.isEmpty():
        menu.exec_(global_pos)

def _get_pane_actions(self, pane_id: PaneId, widget: QWidget) -> List[QAction]:
    """Get pane-level actions from set_pane_actions() or custom provider.

    Priority:
    1. Custom provider (set_pane_action_provider) - for advanced customization
    2. Actions from set_pane_actions() - RECOMMENDED (KeybindingManager actions)
    3. Empty list - no pane actions

    Note: Does NOT create actions internally. Actions should come from
          KeybindingManager via set_pane_actions().
    """
    # Check for custom provider (advanced use case)
    if hasattr(self, '_custom_pane_action_provider') and self._custom_pane_action_provider:
        return self._custom_pane_action_provider(pane_id, widget)

    # Return actions from set_pane_actions() (RECOMMENDED)
    if hasattr(self, '_pane_actions') and self._pane_actions:
        return self._pane_actions

    # No actions configured
    return []
```

---

## Layer 3: ChromeTabbedWindow - Tab Context Menus

### Public API

**Location**: `chrome_tabbed_window/chrome_tabbed_window.py`

```python
class ChromeTabbedWindow:

    def enable_tab_context_menu(self, enabled: bool = True) -> None:
        """Enable/disable context menu on tab bar.

        Args:
            enabled: If True, right-click on tabs shows context menu

        Default menu includes:
        - Close Tab (Ctrl+W)
        - Close Other Tabs
        - Close Tabs to the Right
        - (Separator)
        - Custom actions (if any)

        Default: False (disabled)

        Example:
            window = ChromeTabbedWindow()
            window.enable_tab_context_menu(True)
        """
        self._tab_context_menu_enabled = enabled
        if enabled and not hasattr(self, '_tab_context_handler'):
            from .view.tab_context_menu import TabContextMenuHandler
            self._tab_context_handler = TabContextMenuHandler(self)

    def add_tab_context_action(self, action: QAction) -> None:
        """Add custom action to tab context menu.

        Args:
            action: QAction to add after default tab actions

        Note:
            Action is added to all tab context menus.
            A separator is automatically added before custom actions.

        Example:
            duplicate = QAction("Duplicate Tab", self)
            duplicate.triggered.connect(self.duplicate_current_tab)
            window.add_tab_context_action(duplicate)
        """
        if not self._tab_context_menu_enabled:
            self.enable_tab_context_menu(True)
        self._tab_context_handler.add_action(action)

    def remove_tab_context_action(self, action: QAction) -> None:
        """Remove custom action from tab context menu.

        Args:
            action: QAction to remove
        """
        if hasattr(self, '_tab_context_handler'):
            self._tab_context_handler.remove_action(action)

    def clear_tab_context_actions(self) -> None:
        """Remove all custom actions from tab context menu."""
        if hasattr(self, '_tab_context_handler'):
            self._tab_context_handler.clear_actions()

    def set_tab_context_menu_handler(
        self,
        handler: Optional[Callable[[int, QPoint], Optional[QMenu]]]
    ) -> None:
        """Set custom handler for tab context menu (advanced).

        Args:
            handler: Function(tab_index, position) -> QMenu or None
                     If returns None, default menu is shown.
                     If returns QMenu, that menu is shown instead.
                     If handler is None, resets to default behavior.

        Example:
            def custom_tab_menu(tab_index, pos):
                menu = QMenu()
                menu.addAction(f"Custom action for tab {tab_index}")
                return menu

            window.set_tab_context_menu_handler(custom_tab_menu)
        """
        if not self._tab_context_menu_enabled:
            self.enable_tab_context_menu(True)
        self._tab_context_handler.set_custom_handler(handler)
```

### Implementation: TabContextMenuHandler

**Location**: `chrome_tabbed_window/view/tab_context_menu.py` (new file)

```python
"""Tab context menu handler for ChromeTabbedWindow."""

from typing import Callable, List, Optional
from PySide6.QtCore import QObject, QPoint
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


class TabContextMenuHandler(QObject):
    """Manages context menu for tab bar.

    Handles right-click on tabs to show context menu with:
    - Close Tab
    - Close Other Tabs
    - Close Tabs to the Right
    - Custom actions
    """

    def __init__(self, parent):
        """Initialize tab context menu handler.

        Args:
            parent: ChromeTabbedWindow instance
        """
        super().__init__(parent)
        self.parent = parent
        self.custom_actions: List[QAction] = []
        self.custom_handler: Optional[Callable] = None

        # Install event filter on tab bar to catch right-clicks
        self.parent.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        """Filter events to catch right-clicks on tab bar."""
        from PySide6.QtCore import QEvent, Qt

        if event.type() == QEvent.Type.ContextMenu:
            # Get tab index at position
            tab_bar = self.parent.tabBar()
            tab_index = tab_bar.tabAt(event.pos())

            if tab_index >= 0:
                self.show_menu(tab_index, event.globalPos())
                return True  # Event handled

        return super().eventFilter(obj, event)

    def show_menu(self, tab_index: int, global_pos: QPoint) -> None:
        """Show context menu for tab.

        Args:
            tab_index: Index of tab that was right-clicked
            global_pos: Global position for menu (screen coordinates)
        """
        # Check custom handler first
        if self.custom_handler:
            menu = self.custom_handler(tab_index, global_pos)
            if menu:
                menu.exec_(global_pos)
                return

        # Build default menu
        menu = self._build_default_menu(tab_index)
        if not menu.isEmpty():
            menu.exec_(global_pos)

    def _build_default_menu(self, tab_index: int) -> QMenu:
        """Build default tab context menu.

        Args:
            tab_index: Index of tab

        Returns:
            QMenu with default tab actions
        """
        menu = QMenu(self.parent)

        # Close This Tab
        close_action = QAction("Close Tab", menu)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(lambda: self.parent.removeTab(tab_index))
        menu.addAction(close_action)

        # Close Other Tabs (only if multiple tabs exist)
        if self.parent.count() > 1:
            close_others = QAction("Close Other Tabs", menu)
            close_others.triggered.connect(lambda: self._close_other_tabs(tab_index))
            menu.addAction(close_others)

        # Close Tabs to the Right (only if tabs exist to the right)
        if tab_index < self.parent.count() - 1:
            close_right = QAction("Close Tabs to the Right", menu)
            close_right.triggered.connect(lambda: self._close_tabs_to_right(tab_index))
            menu.addAction(close_right)

        # Add custom actions
        if self.custom_actions:
            menu.addSeparator()
            for action in self.custom_actions:
                menu.addAction(action)

        return menu

    def _close_other_tabs(self, keep_index: int) -> None:
        """Close all tabs except the specified one.

        Args:
            keep_index: Index of tab to keep open
        """
        # Close tabs after keep_index
        while self.parent.count() > keep_index + 1:
            self.parent.removeTab(self.parent.count() - 1)

        # Close tabs before keep_index
        while keep_index > 0:
            self.parent.removeTab(0)
            keep_index -= 1  # Adjust index as tabs are removed

    def _close_tabs_to_right(self, tab_index: int) -> None:
        """Close all tabs to the right of specified index.

        Args:
            tab_index: Index of tab (tabs after this will be closed)
        """
        while self.parent.count() > tab_index + 1:
            self.parent.removeTab(self.parent.count() - 1)

    def add_action(self, action: QAction) -> None:
        """Add custom action to tab context menu."""
        self.custom_actions.append(action)

    def remove_action(self, action: QAction) -> None:
        """Remove custom action from tab context menu."""
        if action in self.custom_actions:
            self.custom_actions.remove(action)

    def clear_actions(self) -> None:
        """Remove all custom actions."""
        self.custom_actions.clear()

    def set_custom_handler(self, handler: Optional[Callable]) -> None:
        """Set custom menu handler."""
        self.custom_handler = handler
```

---

## Layer 4: Application Integration

### ViloxTerm Example

**Location**: `apps/viloxterm/src/viloxterm/app.py`

```python
class ViloxTermApp(ChromeTabbedWindow):
    """ViloxTerm application using ChromeTabbedWindow."""

    def __init__(self):
        super().__init__()

        # ... existing initialization ...

        # Get all actions from keybinding manager
        kb_actions = self.keybinding_manager.apply_shortcuts(self)

        # Enable tab context menus
        self.enable_tab_context_menu(True)

        # Enable pane context menus in multisplit
        self.multisplit.enable_context_menus(True)

        # Set pane-level actions (Split, Close)
        self._setup_pane_context_actions(kb_actions)

        # Add app-level actions to all pane menus
        self._setup_app_context_actions(kb_actions)

    def _setup_pane_context_actions(self, kb_actions: Dict[str, QAction]) -> None:
        """Set pane-level actions for context menus."""
        self.multisplit.set_pane_actions([
            kb_actions["pane.split_vertical"],      # Ctrl+Shift+V
            kb_actions["pane.split_horizontal"],    # Ctrl+Shift+H
            None,  # Separator
            kb_actions["pane.close"],               # Ctrl+W
        ])

    def _setup_app_context_actions(self, kb_actions: Dict[str, QAction]) -> None:
        """Add app-level actions to pane context menus."""
        # Terminal Preferences (Ctrl+,)
        self.multisplit.add_context_menu_action(kb_actions["appearance.terminal_preferences"])

        # Terminal Theme (Ctrl+Shift+,)
        self.multisplit.add_context_menu_action(kb_actions["appearance.terminal_theme"])
```

**Location**: `apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

```python
class TerminalProvider(WidgetProvider):
    """Provides TerminalWidget instances for MultisplitWidget panes."""

    def __init__(self, server: MultiSessionTerminalServer, app: 'ViloxTermApp'):
        self.server = server
        self.app = app  # Reference to app for split/close operations
        self.pane_to_session: dict[str, str] = {}
        self._default_theme: Optional[dict] = None
        self._default_config: Optional[dict] = None

    def provide_widget(self, widget_id: str, pane_id: str) -> QWidget:
        """Create a new terminal widget for a pane."""
        # ... existing widget creation ...

        # Terminal handles its own context menu (Copy/Paste/Clear)
        # No additional configuration needed

        return terminal

    # NO get_pane_context_actions() implementation needed!
    # Pane actions come from KeybindingManager via set_pane_actions()
```

---

## Context Menu Composition Example

### Right-click on terminal pane in ViloxTerm:

```
┌─────────────────────────────────┐
│ Copy                    Ctrl+C  │  ← From TerminalWidget
│ Paste                   Ctrl+V  │  ← From TerminalWidget
│ Clear Terminal                  │  ← From TerminalWidget
├─────────────────────────────────┤
│ Split Vertical     Ctrl+Shift+V │  ← From TerminalProvider
│ Split Horizontal   Ctrl+Shift+H │  ← From TerminalProvider
│ Close Pane               Ctrl+W │  ← From TerminalProvider
├─────────────────────────────────┤
│ Terminal Preferences     Ctrl+, │  ← From ViloxTermApp
│ Terminal Theme     Ctrl+Shift+, │  ← From ViloxTermApp
└─────────────────────────────────┘
```

### Right-click on tab in ViloxTerm:

```
┌─────────────────────────────────┐
│ Close Tab                Ctrl+W │  ← From ChromeTabbedWindow
│ Close Other Tabs                │  ← From ChromeTabbedWindow
│ Close Tabs to the Right         │  ← From ChromeTabbedWindow
└─────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: MultisplitWidget Context Menu Support

**Files to Create/Modify**:
- `vfwidgets_multisplit/view/container.py` - Add ContextMenuProvider protocol
- `vfwidgets_multisplit/multisplit.py` - Add public API methods

**Tasks**:
1. Add `ContextMenuProvider` protocol definition
2. Extend `WidgetProvider` with optional `get_pane_context_actions()` method
3. Add `enable_context_menus()` method to MultisplitWidget
4. Add `add_context_menu_action()` and related methods
5. Add `set_pane_action_provider()` method
6. Implement `_show_pane_context_menu()` composition logic
7. Install event filter on Container to catch right-clicks on widgets
8. Implement default pane actions (Split V/H, Close)

**Testing**:
- Test with single widget type (all terminals)
- Test with heterogeneous widgets (terminal + text editor)
- Test custom pane action provider
- Test app-level actions
- Verify separator placement

### Phase 2: ChromeTabbedWindow Tab Context Menu

**Files to Create/Modify**:
- `chrome_tabbed_window/view/tab_context_menu.py` - New file
- `chrome_tabbed_window/chrome_tabbed_window.py` - Add public API methods

**Tasks**:
1. Create `TabContextMenuHandler` class
2. Add `enable_tab_context_menu()` to ChromeTabbedWindow
3. Add `add_tab_context_action()` and related methods
4. Add `set_tab_context_menu_handler()` method
5. Implement event filter for tab bar right-clicks
6. Implement default tab menu (Close, Close Others, Close Right)
7. Wire up menu actions to existing tab management methods

**Testing**:
- Test "Close Tab" action
- Test "Close Other Tabs" action
- Test "Close Tabs to the Right" action
- Test custom tab actions
- Test custom tab menu handler
- Verify proper tab index handling during closure

### Phase 3: ViloxTerm Integration

**Files to Modify**:
- `apps/viloxterm/src/viloxterm/app.py`
- `apps/viloxterm/src/viloxterm/providers/terminal_provider.py`

**Tasks**:
1. Enable tab context menus in ViloxTermApp.__init__()
2. Enable pane context menus in ViloxTermApp.__init__()
3. Implement `get_pane_context_actions()` in TerminalProvider
4. Wire up split/close actions to existing keyboard shortcut handlers
5. Add app-level actions (Preferences, Theme)
6. Test full composition: Widget + Pane + App actions

**Testing**:
- Test terminal pane context menu shows all layers
- Test tab context menu
- Verify keyboard shortcuts work from context menu
- Test split operations from context menu
- Test close operations from context menu
- Verify preferences dialog opens from context menu

### Phase 4: Documentation & Examples

**Files to Create/Modify**:
- `vfwidgets_multisplit/examples/05_heterogeneous_widgets.py` - New example
- `vfwidgets_multisplit/examples/06_custom_context_menus.py` - New example
- `vfwidgets_multisplit/README.md` - Update with context menu docs
- `chrome_tabbed_window/README.md` - Update with tab context menu docs
- `docs/context-menu-architecture-GUIDE.md` - Developer guide

**Content**:
1. Create example with Terminal + TextEdit + Browser widgets
2. Demonstrate ContextMenuProvider implementation
3. Demonstrate custom pane action provider
4. Demonstrate tab context menu customization
5. Document context menu composition pattern
6. Add API reference for all context menu methods
7. Add troubleshooting guide

---

## API Summary

### MultisplitWidget

| Method | Description |
|--------|-------------|
| `enable_context_menus(enabled)` | Enable/disable pane context menus |
| `add_context_menu_action(action)` | Add app-level action to all panes |
| `remove_context_menu_action(action)` | Remove app-level action |
| `clear_context_menu_actions()` | Clear all app-level actions |
| `set_pane_action_provider(provider)` | Set custom pane action provider |

### ChromeTabbedWindow

| Method | Description |
|--------|-------------|
| `enable_tab_context_menu(enabled)` | Enable/disable tab context menus |
| `add_tab_context_action(action)` | Add custom action to tab menu |
| `remove_tab_context_action(action)` | Remove custom action |
| `clear_tab_context_actions()` | Clear all custom actions |
| `set_tab_context_menu_handler(handler)` | Set custom menu handler |

### WidgetProvider Protocol

| Method | Description |
|--------|-------------|
| `get_pane_context_actions(pane_id, widget)` | Optional: Return pane-level actions |

### ContextMenuProvider Protocol

| Method | Description |
|--------|-------------|
| `get_context_menu_actions(position)` | Optional: Return widget-specific actions |

---

## Benefits

1. **Separation of Concerns**: Each layer manages its own actions independently
2. **Type-Specific Menus**: Different widget types can have different actions
3. **Composition**: Menus automatically merge from all participating layers
4. **Optional**: Widgets/providers can opt-in via protocol implementation
5. **Backward Compatible**: Existing code works without modifications
6. **DRY**: Reuses QAction infrastructure (shortcuts, icons, tooltips)
7. **Flexible**: Override at any level for custom behavior
8. **Discoverable**: Context menus expose available keyboard shortcuts

---

## Future Enhancements

1. **Dynamic Actions**: Actions that change based on state (e.g., "Maximize Pane" ↔ "Restore Pane")
2. **Action Groups**: Radio buttons or checkboxes in context menus
3. **Submenus**: Hierarchical menu organization for many actions
4. **Icons**: Add icons to context menu actions
5. **Mnemonics**: Keyboard navigation within context menus
6. **Drag-to-Tab**: Context menu action to "Move to New Tab"
7. **Recent Items**: "Reopen Closed Tab" with history

---

## Appendix A: Migration Guide

### For Existing Applications

**No migration required** - The context menu system is opt-in:

```python
# Existing code continues to work unchanged
multisplit = MultisplitWidget(provider=my_provider)

# Enable context menus when ready
multisplit.enable_context_menus(True)
```

### For Widget Authors

**Optional enhancement** - Implement `ContextMenuProvider` to participate:

```python
class MyCustomWidget(QWidget):
    def get_context_menu_actions(self, position: QPoint) -> List[QAction]:
        """Provide widget-specific context menu actions."""
        actions = []

        # Add your widget's actions
        copy = QAction("Copy", self)
        copy.triggered.connect(self.copy)
        actions.append(copy)

        return actions
```

---

## Appendix B: Design Decisions

### Why Not Unified Context Menu Handler?

**Rejected**: Single handler for all layers

**Reason**: Violates separation of concerns. Each layer should manage its own actions without knowledge of other layers.

### Why Protocols Instead of Base Classes?

**Chosen**: Use Python protocols for `ContextMenuProvider`

**Reason**: More flexible, no forced inheritance, works with existing widgets, duck typing support.

### Why Composition Instead of Override?

**Chosen**: Compose menus from multiple sources

**Reason**: Allows widgets to retain their own context menus while adding pane/app actions. More flexible than requiring widgets to implement full menu.

### Why Optional Instead of Required?

**Chosen**: Make context menu participation optional

**Reason**: Backward compatibility, gradual adoption, not all widgets need context menus.

---

---

## Appendix C: Additional Considerations

### 1. Context Menu on Splitter Handles

**Question**: What happens when right-clicking on splitter handles between panes?

**Recommendation**: Show pane menu for the pane on the **left** (for vertical splits) or **top** (for horizontal splits) of the handle.

**Implementation**: Detect if click is on QSplitter handle and route to nearest pane.

### 2. Context Menu on Empty Container

**Question**: What about right-clicking empty space (no panes exist)?

**Recommendation**: Show minimal menu with app-level actions only. Optionally include "New Pane" if applicable.

**Implementation**: Check if click is in empty area and show simplified menu.

### 3. Pane-Specific Split/Close Actions

**Issue**: Current spec shows `self.app._on_split_vertical()` without pane context.

**Fix Required**: Actions must include pane_id to operate on correct pane:

```python
def get_pane_context_actions(self, pane_id: str, widget: QWidget) -> List[QAction]:
    actions = []

    # Pass pane_id to handler
    split_v = QAction("Split Vertical", widget)
    split_v.triggered.connect(
        lambda checked=False, pid=pane_id: self._split_pane(pid, Direction.RIGHT)
    )
    actions.append(split_v)

    return actions

def _split_pane(self, pane_id: str, direction: Direction) -> None:
    """Split specific pane by ID."""
    self.multisplit.split_pane(pane_id, direction)
```

**Critical**: Lambda capture of `pane_id` is required to avoid late-binding issues.

### 4. Tab Content vs Tab Button Context Menus

**Clarification**:
- **Right-click on tab button** → Tab menu (Close Tab, Close Others, etc.)
- **Right-click on tab content** (MultisplitWidget area) → Pane menu (Split, Close Pane, etc.)

These are **separate** context menus for different areas. No conflict.

### 5. Event Propagation and Suppression

**Rule**: Widget's `contextMenuEvent()` takes precedence.

**Behavior**:
1. Widget receives `QContextMenuEvent`
2. If widget handles it (shows menu or accepts event), **stop**
3. If widget ignores event, MultisplitWidget shows composed menu

**Implementation**: Use event filter, check `event.isAccepted()` before showing pane menu.

### 6. Focus Behavior on Right-Click

**Question**: Should right-clicking a pane focus it before showing menu?

**Recommendation**: **Yes** - focus pane on right-click for consistency.

**Rationale**:
- User expects keyboard shortcuts to operate on right-clicked item
- Matches VS Code, terminal emulators behavior
- Prevents confusion when multiple panes exist

**Implementation**:
```python
def eventFilter(self, obj, event):
    if event.type() == QEvent.Type.ContextMenu:
        # Focus the widget before showing menu
        widget.setFocus(Qt.FocusReason.MouseFocusReason)
        # Then show context menu
        self._show_pane_context_menu(...)
```

### 7. Keyboard-Triggered Context Menus

**Keyboard Access**: Shift+F10 or Menu key should show context menu.

**Behavior**: Show menu for currently **focused** pane.

**Implementation**: Handle `QEvent.Type.ContextMenu` in event filter, check if triggered by keyboard (event.reason() == QContextMenuEvent.Keyboard).

### 8. Menu Positioning

**Off-Screen Protection**: Qt's `QMenu.exec_(QPoint)` automatically adjusts position if menu would go off-screen.

**Custom Position**: For keyboard-triggered menus, show at center of focused widget:
```python
if event.reason() == QContextMenuEvent.Keyboard:
    widget_center = widget.rect().center()
    global_pos = widget.mapToGlobal(widget_center)
    menu.exec_(global_pos)
```

### 9. Signal-Based Menu Customization

**New Signal**: Allow apps to modify menu before display.

**API Addition** to MultisplitWidget:
```python
contextMenuAboutToShow = Signal(str, QMenu)  # (pane_id, menu)
```

**Usage**:
```python
def customize_menu(pane_id, menu):
    # Add custom separator
    menu.addSeparator()
    # Add dynamic action
    menu.addAction(f"Debug Pane {pane_id}")

multisplit.contextMenuAboutToShow.connect(customize_menu)
```

### 10. Widget Lifecycle and Cleanup

**Question**: What happens to QActions when widget is removed?

**Answer**: QActions are children of widget, automatically destroyed with widget via Qt parent-child system.

**Best Practice**: Make actions children of the widget they operate on:
```python
action = QAction("Copy", widget)  # widget is parent
# Action automatically destroyed when widget is destroyed
```

**Provider Cleanup**: Not required - Qt handles it.

### 11. Theme Integration for Context Menus

**QMenu Theming**: Context menus should respect application theme.

**Implementation Options**:

**Option A**: Use QSS stylesheet (recommended for consistency):
```python
menu.setStyleSheet("""
    QMenu {
        background-color: {menu.background};
        border: 1px solid {menu.border};
    }
    QMenu::item:selected {
        background-color: {menu.selection.background};
    }
""".format(theme.colors))
```

**Option B**: Platform native menus (no custom theming).

**Recommendation**: For VFWidgets, use Option A for cross-platform consistency.

### 12. Multiple Selection Actions

**Future Enhancement**: When multiple panes are selected (via Ctrl+Click), show actions that operate on all selected panes:
- "Close Selected Panes"
- "Merge Selected Panes"

**Not in Scope**: Current spec assumes single-pane context menus only.

### 13. Right-Click Drag Behavior

**Issue**: Right-click-and-drag might conflict with context menu.

**Solution**: Only show menu on button **release**, not press. This allows drag gestures.

**Implementation**:
```python
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.RightButton:
        self._right_click_pos = event.pos()  # Remember position

def mouseReleaseEvent(self, event):
    if event.button() == Qt.MouseButton.RightButton:
        # Only show menu if mouse hasn't moved much
        if (event.pos() - self._right_click_pos).manhattanLength() < 5:
            self._show_context_menu(event.globalPos())
```

### 14. Disabled Actions

**Requirement**: Actions should be disabled when not applicable.

**Examples**:
- "Split Vertical" disabled if pane is already at minimum size
- "Close Pane" disabled if it's the last pane
- "Close Tab" disabled if it's the last tab

**Implementation**: Check conditions before adding actions:
```python
def get_pane_context_actions(self, pane_id, widget):
    actions = []

    # Only add split if pane is splittable
    if self._can_split_pane(pane_id):
        split_action = QAction("Split Vertical", widget)
        # ...
        actions.append(split_action)

    # Disable close if last pane
    close_action = QAction("Close Pane", widget)
    close_action.setEnabled(self.pane_count() > 1)
    actions.append(close_action)

    return actions
```

---

## Appendix D: Implementation Quality Considerations

This appendix covers additional considerations for production-ready implementation. While not blocking for Phase 1-3 (basic functionality), these should be addressed in Phase 4 (Production Readiness).

### 15. Testing Strategy

**Requirements**: Comprehensive test coverage across all layers and interaction patterns.

**Test Categories**:

**A) Unit Tests**:
```python
# Test individual layer in isolation
def test_terminal_widget_context_menu_actions():
    """Test TerminalWidget provides Copy/Paste actions."""
    terminal = TerminalWidget()
    actions = terminal.get_context_menu_actions(QPoint(10, 10))
    assert len(actions) == 3  # Copy, Paste, Clear
    assert actions[0].text() == "Copy"

def test_multisplit_default_pane_actions():
    """Test MultisplitWidget provides default Split/Close actions."""
    container = Container(provider)
    actions = container._get_default_pane_actions(pane_id="test")
    assert len(actions) == 4  # Split V, Split H, Separator, Close
```

**B) Integration Tests**:
```python
def test_context_menu_composition():
    """Test menu composes actions from all layers."""
    multisplit = MultisplitWidget(provider)
    multisplit.enable_context_menus(True)
    multisplit.add_context_menu_action(prefs_action)

    # Simulate right-click
    widget = multisplit.get_widget(pane_id)
    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(10, 10))
    multisplit.eventFilter(widget, event)

    # Verify menu contains all layers
    # Widget actions + Pane actions + App actions
```

**C) Event Simulation Tests**:
```python
def test_keyboard_triggered_context_menu():
    """Test Shift+F10 shows context menu."""
    QTest.keyClick(widget, Qt.Key_F10, Qt.ShiftModifier)
    # Verify menu appears

def test_right_click_focuses_pane():
    """Test right-click focuses pane before showing menu."""
    assert widget.hasFocus() == False
    # Simulate right-click
    assert widget.hasFocus() == True
```

**D) Async Action Tests**:
```python
def test_split_action_async():
    """Test split action completes asynchronously."""
    split_action.trigger()
    QTest.qWait(100)  # Wait for async operation
    assert multisplit.pane_count() == 2
```

**Testing Tools**:
- `pytest-qt` for Qt event simulation
- `QTest.mouseClick()` for simulated clicks
- `QTest.keyClick()` for keyboard events
- `QSignalSpy` for signal verification

---

### 16. Performance Considerations

**Issue**: Creating QActions on every right-click can be expensive with many panes.

**Optimization Strategies**:

**A) Action Caching for Static Menus**:
```python
class MultisplitWidget:
    def __init__(self):
        self._cached_pane_actions = {}  # Cache per pane_id

    def _get_pane_actions(self, pane_id):
        # Return cached actions if menu hasn't changed
        if pane_id in self._cached_pane_actions:
            return self._cached_pane_actions[pane_id]

        actions = self._create_pane_actions(pane_id)
        self._cached_pane_actions[pane_id] = actions
        return actions

    def _invalidate_pane_cache(self, pane_id):
        """Call when pane state changes."""
        if pane_id in self._cached_pane_actions:
            del self._cached_pane_actions[pane_id]
```

**B) Lazy Menu Construction**:
```python
# Don't create QMenu until actually needed
def contextMenuEvent(self, event):
    if not event.isAccepted():  # Only if widget didn't handle it
        menu = self._build_menu()  # Lazy construction
        menu.exec_(event.globalPos())
```

**C) Event Filter Overhead**:
- **Issue**: Installing event filters on 100+ widgets can slow down event processing
- **Solution**: Use single event filter on container instead of per-widget filters
- **Measurement**: Profile with `cProfile` to measure event filter impact

**D) Large Action Lists**:
```python
# For menus with 20+ actions, consider submenus
menu.addMenu("Split Options").addActions([split_v, split_h, split_window])
```

**Performance Metrics**:
- Menu construction: < 5ms for typical menu (10 actions)
- Event filter overhead: < 0.1ms per event
- Memory: ~200 bytes per QAction

---

### 17. Platform-Specific Behavior

**macOS Differences**:

```python
import sys
from PySide6.QtCore import Qt

class MultisplitWidget:
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.ContextMenu:
            # macOS: Ctrl+Click also triggers context menu
            if sys.platform == 'darwin':
                # Handle both right-click and Ctrl+Click
                if event.reason() == QContextMenuEvent.Mouse:
                    modifiers = event.modifiers()
                    if modifiers & Qt.ControlModifier:
                        # This is Ctrl+Click on macOS
                        pass
```

**Linux Middle-Click Paste**:
```python
# Linux terminals use middle-click for paste
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.MiddleButton:
        # Don't interfere with terminal's middle-click paste
        event.ignore()  # Let terminal handle it
        return
    super().mousePressEvent(event)
```

**Windows Right-Click Timing**:
- Windows may show tooltips before context menu if right-click is held
- **Solution**: Show menu on mouse release, not press (see Appendix C, item 13)

**Platform Detection**:
```python
import platform

def get_platform():
    system = platform.system()
    return {
        'Darwin': 'macos',
        'Linux': 'linux',
        'Windows': 'windows'
    }.get(system, 'unknown')
```

---

### 18. Internationalization (i18n)

**Requirement**: All menu text must be translatable.

**Implementation**:

**A) Use Qt's Translation System**:
```python
from PySide6.QtCore import QCoreApplication

class MultisplitWidget:
    def _get_default_pane_actions(self, pane_id):
        actions = []

        # Use tr() for translatable strings
        split_v = QAction(self.tr("Split Vertical"), self)
        split_h = QAction(self.tr("Split Horizontal"), self)
        close = QAction(self.tr("Close Pane"), self)

        return actions
```

**B) Translation Files**:
```bash
# Generate translation template
pylupdate6 src/**/*.py -ts translations/vfwidgets_multisplit_en.ts

# Translate using Qt Linguist
linguist translations/vfwidgets_multisplit_en.ts

# Compile translations
lrelease translations/vfwidgets_multisplit_en.ts
```

**C) Load Translations at Runtime**:
```python
from PySide6.QtCore import QTranslator, QLocale

def load_translations(app):
    translator = QTranslator()
    locale = QLocale.system().name()  # e.g., 'en_US', 'fr_FR'

    if translator.load(f"vfwidgets_multisplit_{locale}", ":/translations"):
        app.installTranslator(translator)
```

**D) Keyboard Shortcuts Localization**:
```python
# Shortcuts don't need translation (Ctrl+C is universal)
# But display text should be localized
action.setShortcut(QKeySequence.Copy)  # Uses platform-standard shortcut
action.setText(self.tr("Copy"))  # Translatable text
```

**Supported Languages** (example):
- English (en_US)
- French (fr_FR)
- German (de_DE)
- Spanish (es_ES)
- Japanese (ja_JP)
- Chinese Simplified (zh_CN)

---

### 19. Icons in Context Menus

**Enhancement**: Add icons to menu items for better visual recognition.

**Implementation**:

**A) Theme-Aware Icons**:
```python
from PySide6.QtGui import QIcon

class MultisplitWidget:
    def _get_default_pane_actions(self, pane_id):
        actions = []

        # Add icons to actions
        split_v = QAction(self.tr("Split Vertical"), self)
        split_v.setIcon(self._get_themed_icon("split-vertical"))

        close = QAction(self.tr("Close Pane"), self)
        close.setIcon(self._get_themed_icon("close"))

        return actions

    def _get_themed_icon(self, name):
        """Get icon that respects current theme (light/dark)."""
        theme = self._get_current_theme()
        if theme and theme.is_dark:
            return QIcon(f":/icons/dark/{name}.svg")
        else:
            return QIcon(f":/icons/light/{name}.svg")
```

**B) Icon Resources**:
```python
# In resources.qrc
<RCC>
    <qresource prefix="/icons/light">
        <file>split-vertical.svg</file>
        <file>split-horizontal.svg</file>
        <file>close.svg</file>
        <file>copy.svg</file>
        <file>paste.svg</file>
    </qresource>
    <qresource prefix="/icons/dark">
        <file>split-vertical.svg</file>
        <file>split-horizontal.svg</file>
        <file>close.svg</file>
        <file>copy.svg</file>
        <file>paste.svg</file>
    </qresource>
</RCC>
```

**C) Icon Guidelines**:
- **Size**: 16x16px for menu icons
- **Format**: SVG (scalable) or PNG with @2x retina variants
- **Style**: Match application icon style (outlined, filled, etc.)
- **Color**: Monochrome SVGs that can be recolored by theme

**D) Optional Icons**:
- Make icons opt-in via configuration:
```python
multisplit.set_context_menu_icons_enabled(True)
```

---

### 20. Dynamic Action State Updates

**Issue**: Actions created in `get_context_menu_actions()` are ephemeral - how to update based on state?

**Solutions**:

**A) Query State at Menu Creation** (Recommended):
```python
def get_pane_context_actions(self, pane_id, widget):
    actions = []

    # Check current pane state
    pane = self._get_pane(pane_id)
    is_maximized = pane.is_maximized

    # Create action with current state
    if is_maximized:
        action = QAction("Restore Pane", widget)
        action.triggered.connect(lambda: self._restore_pane(pane_id))
    else:
        action = QAction("Maximize Pane", widget)
        action.triggered.connect(lambda: self._maximize_pane(pane_id))

    actions.append(action)
    return actions
```

**B) Update Before Showing (for complex state)**:
```python
# Emit signal before showing menu
contextMenuAboutToShow = Signal(str, QMenu)

def _show_pane_context_menu(self, pane_id, global_pos, widget_pos):
    menu = self._build_menu(pane_id, widget_pos)

    # Allow external state updates
    self.contextMenuAboutToShow.emit(pane_id, menu)

    menu.exec_(global_pos)

# In application code:
def update_menu_state(pane_id, menu):
    # Update action states based on current state
    for action in menu.actions():
        if action.text() == "Close Pane":
            action.setEnabled(multisplit.pane_count() > 1)
```

**C) Persistent Actions with State Tracking** (for frequently used menus):
```python
class MultisplitWidget:
    def __init__(self):
        # Create persistent actions
        self._maximize_action = QAction("Maximize Pane", self)
        self._restore_action = QAction("Restore Pane", self)
        self._current_pane_maximized = False

    def _show_pane_context_menu(self, pane_id, global_pos, widget_pos):
        menu = QMenu(self)

        # Update action visibility based on state
        pane = self._get_pane(pane_id)
        if pane.is_maximized:
            menu.addAction(self._restore_action)
        else:
            menu.addAction(self._maximize_action)

        menu.exec_(global_pos)
```

**State Examples**:
- Maximize ↔ Restore Pane
- Lock ↔ Unlock Pane
- Show ↔ Hide Sidebar
- Mute ↔ Unmute (for media widgets)

---

### 21. Context Menu Hiding/Lifecycle

**Requirements**: Menus should close appropriately in various scenarios.

**A) Window Deactivation**:
```python
def changeEvent(self, event):
    if event.type() == QEvent.Type.ActivationChange:
        if not self.isActiveWindow():
            # Close any open context menus
            if hasattr(self, '_current_context_menu'):
                self._current_context_menu.close()
    super().changeEvent(event)
```

**B) Pane Closure During Menu Display**:
```python
def remove_pane(self, pane_id):
    # Close menu if it's for the pane being removed
    if hasattr(self, '_current_context_menu_pane'):
        if self._current_context_menu_pane == pane_id:
            self._current_context_menu.close()

    # Remove pane
    self._container.remove_pane(pane_id)
```

**C) Menu Lifetime Tracking**:
```python
def _show_pane_context_menu(self, pane_id, global_pos, widget_pos):
    menu = QMenu(self)

    # Track current menu
    self._current_context_menu = menu
    self._current_context_menu_pane = pane_id

    # Clear tracking when menu closes
    menu.aboutToHide.connect(lambda: self._on_menu_closed())

    menu.exec_(global_pos)

def _on_menu_closed(self):
    self._current_context_menu = None
    self._current_context_menu_pane = None
```

**D) Escape Key Handling**:
- Qt's QMenu automatically closes on Escape key
- No additional implementation needed

---

### 22. Accessibility (a11y)

**Requirements**: Context menus must be accessible to users with disabilities.

**A) Screen Reader Support**:
```python
# Set accessible names and descriptions
action = QAction("Split Vertical", self)
action.setShortcut("Ctrl+Shift+V")
action.setToolTip("Split the current pane vertically")
action.setStatusTip("Create a new pane to the right of this one")

# Qt automatically announces:
# "Split Vertical, Ctrl+Shift+V, Split the current pane vertically"
```

**B) Keyboard Navigation**:
```python
# Qt menus automatically support:
# - Arrow keys for navigation
# - Enter/Space to activate
# - Escape to close
# - Mnemonics (Alt+Letter)

# Add mnemonics to actions:
action = QAction("&Split Vertical", self)  # Alt+S activates
action = QAction("&Close Pane", self)      # Alt+C activates
```

**C) High Contrast Mode**:
```python
def _apply_accessibility_theme(self, menu):
    """Apply high-contrast theme if enabled."""
    if self._is_high_contrast_mode():
        menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 2px solid white;
            }
            QMenu::item:selected {
                background-color: white;
                color: black;
            }
        """)

def _is_high_contrast_mode(self):
    # Check system setting
    palette = QApplication.palette()
    return palette.color(QPalette.Window).lightness() < 10 or \
           palette.color(QPalette.Window).lightness() > 245
```

**D) Focus Indicators**:
```python
# Ensure selected menu items have clear focus indicators
menu.setStyleSheet("""
    QMenu::item:selected {
        border: 2px solid {selection.border};
        outline: none;
    }
""")
```

**E) Voice Control**:
- Menu items with clear names are voice-activatable
- Use descriptive action names (not "OK", "Do it", etc.)
- Example: "Split Vertical" is voice-friendly

**F) Testing with Accessibility Tools**:
- **Linux**: Orca screen reader, Accerciser
- **Windows**: NVDA, Narrator
- **macOS**: VoiceOver

**Accessibility Checklist**:
- ✓ All actions have descriptive text
- ✓ Keyboard shortcuts announced by screen readers
- ✓ Keyboard navigation works (arrow keys, Enter, Escape)
- ✓ High contrast mode supported
- ✓ Focus indicators visible
- ✓ Mnemonics for keyboard access
- ✓ Tested with screen reader

---

## Summary of VFWidgets Infrastructure Benefits

The v1.3 update fully integrates existing VFWidgets infrastructure, providing significant advantages:

### KeybindingManager Integration

**Instead of**:
- Creating QActions with hardcoded shortcuts in MultisplitWidget
- Duplicating shortcut definitions across widgets
- No user customization support
- Manual i18n for action text

**We get**:
- ✅ Single source of truth for all keyboard shortcuts
- ✅ User-customizable shortcuts with persistent storage
- ✅ i18n-ready action descriptions via `tr()`
- ✅ Action categories for organization
- ✅ Conflict detection across application
- ✅ Shortcuts work globally (keyboard) AND locally (context menus)

### Theme System Integration

**Instead of**:
- Hardcoded menu colors
- Separate light/dark theme handling
- Inconsistent styling across widgets

**We get**:
- ✅ Automatic menu theming from current theme
- ✅ Consistent colors: `menu.background`, `menu.selection.background`, etc.
- ✅ Dark/light theme support out of the box
- ✅ Custom themes supported without code changes

### Simplified Implementation

**Before (creating actions in MultisplitWidget)**:
```python
# MultisplitWidget creates actions internally
def _get_default_pane_actions(self, pane_id):
    split_v = QAction("Split Vertical", self)  # ❌ Hardcoded text
    split_v.setShortcut("Ctrl+Shift+V")        # ❌ Hardcoded shortcut
    split_v.triggered.connect(...)             # ❌ Manual connection
    # ... more boilerplate
```

**After (using KeybindingManager)**:
```python
# Application setup (once)
kb_actions = keybinding_manager.apply_shortcuts(main_window)

# MultisplitWidget just uses the actions
multisplit.set_pane_actions([
    kb_actions["pane.split_vertical"],    # ✅ Centralized, customizable, i18n-ready
    kb_actions["pane.close"],
])
```

### Real-World Impact

For **ViloxTerm**:
- All actions already managed by KeybindingManager ✅
- Theme system already integrated ✅
- NO new infrastructure needed ✅
- Context menus just reuse existing QActions ✅

**Result**: Simpler implementation, fewer bugs, better UX, full feature parity with keyboard shortcuts.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-06 | Initial specification |
| 1.1 | 2025-10-06 | Added Appendix C: Additional Considerations (14 items) |
| 1.2 | 2025-10-06 | Added Appendix D: Implementation Quality Considerations (8 items: testing, performance, platform, i18n, icons, dynamic state, lifecycle, accessibility) |
| 1.3 | 2025-10-06 | **MAJOR UPDATE**: Integrated VFWidgets infrastructure (KeybindingManager, Theme System, MultisplitWidget protocols). Removed internal action creation in favor of KeybindingManager-provided QActions. Simplified API and implementation. |
