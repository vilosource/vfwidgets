# Pane Maximize/Toggle Feature - Implementation Plan

## Overview

Add Ctrl+M keyboard shortcut to toggle the focused pane to "full screen" within its MultisplitWidget tab, hiding all other panes and splitters while preserving the layout for perfect restoration.

## Goals

- Toggle focused pane to fill entire container
- Preserve layout structure for seamless restoration
- Maintain MultisplitWidget's clean MVC architecture
- Support undo/redo via Command pattern
- Handle all edge cases gracefully

## Architecture

MultisplitWidget follows strict MVC separation:
- **Model** (`core/model.py`): Pure Python, tracks tree state
- **View** (`view/container.py`): Qt widgets, renders the tree
- **Controller** (`controller/`): Commands for mutations, undo/redo
- **Signals**: Communication between layers

## Strategy: Hide/Show with State Preservation

**Why this approach:**
- ✅ Model structure unchanged (just tracks maximize state)
- ✅ Fast toggle (hide/show, no tree manipulation)
- ✅ Perfect restoration (original layout preserved)
- ✅ Clean MVC separation maintained
- ✅ Undo/redo support free via Command pattern

## Phase 1: Model Layer

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/core/model.py`

**1.1 Add maximize state to PaneModel**

```python
@dataclass
class PaneModel:
    root: Optional[PaneNode] = None
    focused_pane_id: Optional[PaneId] = None
    maximized_pane_id: Optional[PaneId] = None  # NEW
    signals: ModelSignals = field(default_factory=ModelSignals)
    # ... rest of fields ...
```

**1.2 Add methods to PaneModel**

```python
def set_maximized_pane(self, pane_id: Optional[PaneId]) -> bool:
    """Set the maximized pane.

    Args:
        pane_id: ID of pane to maximize, or None to restore

    Returns:
        True if maximize state changed, False otherwise
    """
    if pane_id and pane_id not in self._pane_registry:
        return False

    if self.maximized_pane_id != pane_id:
        old_id = self.maximized_pane_id
        self.maximized_pane_id = pane_id
        self.signals.maximize_changed.emit(pane_id)
        return True
    return False

def get_maximized_pane(self) -> Optional[PaneId]:
    """Get the currently maximized pane ID."""
    return self.maximized_pane_id

def is_maximized(self) -> bool:
    """Check if any pane is currently maximized."""
    return self.maximized_pane_id is not None

def is_pane_maximized(self, pane_id: PaneId) -> bool:
    """Check if specific pane is maximized."""
    return self.maximized_pane_id == pane_id
```

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/core/signals.py`

**1.3 Add maximize signal to ModelSignals**

```python
@dataclass
class ModelSignals:
    # ... existing signals ...
    maximize_changed: Signal = field(default_factory=lambda: Signal(object))  # Optional[PaneId]
```

## Phase 2: Controller Layer

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/controller/commands.py`

**2.1 Create ToggleMaximizePaneCommand**

```python
@dataclass
class ToggleMaximizePaneCommand(Command):
    """Command to toggle maximize state of a pane.

    Toggles between maximized and restored states. Undoing this command
    simply toggles back to the previous state.
    """

    pane_id: PaneId

    def __init__(self, model: PaneModel, pane_id: PaneId):
        """Initialize toggle maximize command.

        Args:
            model: PaneModel to operate on
            pane_id: ID of pane to toggle
        """
        super().__init__(model)
        self.pane_id = pane_id
        self._was_maximized = False

    def execute(self) -> bool:
        """Execute the toggle maximize command.

        Returns:
            True if successful, False if pane doesn't exist
        """
        # Check if pane exists
        pane = self.model.get_pane(self.pane_id)
        if not pane:
            logger.warning(f"Cannot maximize pane {self.pane_id}: pane not found")
            return False

        # Store current state for undo
        self._was_maximized = self.model.is_pane_maximized(self.pane_id)

        # Toggle maximize state
        if self._was_maximized:
            # Currently maximized → restore
            success = self.model.set_maximized_pane(None)
            if success:
                logger.info(f"Restored pane {self.pane_id} from maximize")
        else:
            # Currently not maximized → maximize
            success = self.model.set_maximized_pane(self.pane_id)
            if success:
                logger.info(f"Maximized pane {self.pane_id}")

        if success:
            self.executed = True
            self.model.signals.layout_changed.emit()

        return success

    def undo(self) -> bool:
        """Undo the toggle (toggle back to previous state).

        Returns:
            True if successful
        """
        if not self.can_undo():
            return False

        # Toggle back to previous state
        if self._was_maximized:
            # Was maximized before, restore it
            success = self.model.set_maximized_pane(self.pane_id)
        else:
            # Was not maximized before, restore to normal
            success = self.model.set_maximized_pane(None)

        if success:
            self.executed = False
            self.model.signals.layout_changed.emit()

        return success

    def description(self) -> str:
        """Get human-readable description."""
        return f"Toggle maximize pane {self.pane_id}"
```

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/controller/controller.py`

**2.2 Add toggle_maximize_pane to PaneController**

```python
def toggle_maximize_pane(self, pane_id: PaneId) -> bool:
    """Toggle maximize state of a pane.

    Args:
        pane_id: ID of pane to toggle

    Returns:
        True if successful, False if pane doesn't exist
    """
    cmd = ToggleMaximizePaneCommand(self.model, pane_id)
    return self.execute_command(cmd)
```

**2.3 Modify SplitPaneCommand to auto-restore**

In `SplitPaneCommand.execute()`, add at the beginning:

```python
def execute(self) -> bool:
    """Execute the split command."""
    # Auto-restore from maximize mode before splitting
    if self.model.is_maximized():
        logger.info("Auto-restoring from maximize mode before split")
        self.model.set_maximized_pane(None)

    # ... rest of existing execute() code ...
```

## Phase 3: View Layer - Core Logic

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py`

**3.1 Connect to maximize signal in PaneContainer.__init__**

```python
def __init__(self, ...):
    # ... existing init code ...

    # Connect to maximize state changes
    self.model.signals.maximize_changed.connect(self._on_maximize_changed)
```

**3.2 Implement _on_maximize_changed handler**

```python
def _on_maximize_changed(self, pane_id: Optional[PaneId]) -> None:
    """Handle maximize state change.

    Args:
        pane_id: ID of pane to maximize, or None to restore
    """
    if pane_id:
        self._enter_maximize_mode(pane_id)
    else:
        self._exit_maximize_mode()

def _enter_maximize_mode(self, pane_id: PaneId) -> None:
    """Enter maximize mode for specific pane.

    Args:
        pane_id: ID of pane to maximize
    """
    logger.info(f"Entering maximize mode for pane {pane_id}")

    # Get the maximized pane widget
    maximized_widget = self._pane_widgets.get(pane_id)
    if not maximized_widget:
        logger.warning(f"Cannot maximize pane {pane_id}: widget not found")
        return

    # 1. Hide all other pane widgets
    for pid, widget in self._pane_widgets.items():
        if pid == pane_id:
            widget.show()
            widget.raise_()  # Bring to front
        else:
            widget.hide()

    # 2. Hide all splitters
    for splitter in self._splitters.values():
        splitter.hide()

    # 3. Make maximized pane fill entire container
    maximized_widget.setGeometry(self.rect())

    logger.info(f"Maximize mode active: pane {pane_id} fills container")

def _exit_maximize_mode(self) -> None:
    """Exit maximize mode and restore normal layout."""
    logger.info("Exiting maximize mode, restoring layout")

    # 1. Show all pane widgets
    for widget in self._pane_widgets.values():
        widget.show()

    # 2. Show all splitters
    for splitter in self._splitters.values():
        splitter.show()

    # 3. Force full tree reconciliation to restore layout
    self._reconcile_tree(force_full_rebuild=True)

    logger.info("Maximize mode exited, layout restored")
```

**3.3 Override resizeEvent to handle maximize mode**

```python
def resizeEvent(self, event) -> None:
    """Handle container resize.

    In maximize mode, resize only the maximized pane.
    In normal mode, use standard resize behavior.
    """
    if self.model.is_maximized():
        # Maximize mode: resize only maximized pane
        pane_id = self.model.get_maximized_pane()
        if pane_id and pane_id in self._pane_widgets:
            self._pane_widgets[pane_id].setGeometry(self.rect())
    else:
        # Normal mode: standard resize
        super().resizeEvent(event)

    event.accept()
```

## Phase 4: View Layer - Coordination

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/view/tree_reconciler.py`

**4.1 Skip reconciliation when maximized**

In `TreeReconciler.reconcile()`, add check at beginning:

```python
def reconcile(self, force_full_rebuild: bool = False) -> None:
    """Reconcile Qt widget tree with model tree.

    Args:
        force_full_rebuild: Force complete rebuild of tree
    """
    # Skip reconciliation if in maximize mode (unless forcing rebuild for restore)
    if self.model.is_maximized() and not force_full_rebuild:
        return

    # ... rest of existing reconcile() code ...
```

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/view/geometry_manager.py`

**4.2 Skip geometry updates when maximized**

In `GeometryManager.update_geometry()`, add check:

```python
def update_geometry(self, container_rect: QRect) -> None:
    """Update geometry of all panes and splitters.

    Args:
        container_rect: Available space for layout
    """
    # Skip geometry updates if in maximize mode
    if self.model.is_maximized():
        return

    # ... rest of existing update_geometry() code ...
```

## Phase 5: Focus Management

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/core/focus.py`

**5.1 Auto-restore on focus change (Option B - Recommended)**

In `FocusManager.set_focus()` or wherever focus changes:

```python
def set_focus(self, pane_id: Optional[PaneId]) -> bool:
    """Set focus to a pane.

    Args:
        pane_id: ID of pane to focus

    Returns:
        True if focus changed
    """
    # Auto-restore from maximize if trying to focus different pane
    if self.model.is_maximized():
        maximized_id = self.model.get_maximized_pane()
        if pane_id and pane_id != maximized_id:
            logger.info("Auto-restoring from maximize due to focus change")
            self.model.set_maximized_pane(None)

    # ... rest of existing set_focus() code ...
```

**Alternative Option A (Simpler):** Lock focus to maximized pane

```python
def set_focus(self, pane_id: Optional[PaneId]) -> bool:
    """Set focus to a pane."""
    # Lock focus to maximized pane
    if self.model.is_maximized():
        maximized_id = self.model.get_maximized_pane()
        if pane_id != maximized_id:
            logger.debug("Focus locked to maximized pane")
            return False  # Reject focus change

    # ... rest of code ...
```

## Phase 6: Visual Indicator

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/view/container.py`

**6.1 Add maximize indicator widget**

```python
class MaximizeIndicator(QWidget):
    """Small indicator shown in corner of maximized pane."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 24)

        # Position in top-right corner
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent background
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 4, 4)

        # Draw text
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Maximized")
```

**6.2 Show/hide indicator in maximize mode**

```python
def __init__(self, ...):
    # ... existing init ...
    self._maximize_indicator = MaximizeIndicator(self)
    self._maximize_indicator.hide()

def _enter_maximize_mode(self, pane_id: PaneId) -> None:
    # ... existing code to hide/show widgets ...

    # Show maximize indicator
    self._maximize_indicator.move(self.width() - 90, 10)
    self._maximize_indicator.show()
    self._maximize_indicator.raise_()

def _exit_maximize_mode(self) -> None:
    # ... existing code to restore layout ...

    # Hide maximize indicator
    self._maximize_indicator.hide()
```

## Phase 7: Public API

### File: `widgets/multisplit_widget/src/vfwidgets_multisplit/multisplit.py`

**7.1 Add public methods to MultisplitWidget**

```python
def toggle_maximize_focused_pane(self) -> bool:
    """Toggle maximize state of currently focused pane.

    Maximizes the focused pane to fill the entire container, hiding all
    other panes and splitters. Call again to restore original layout.

    Returns:
        True if successful, False if no pane is focused

    Example:
        >>> multisplit.toggle_maximize_focused_pane()  # Maximize
        True
        >>> multisplit.toggle_maximize_focused_pane()  # Restore
        True
    """
    focused_id = self._model.focused_pane_id
    if not focused_id:
        logger.warning("Cannot toggle maximize: no pane is focused")
        return False

    return self._controller.toggle_maximize_pane(focused_id)

def maximize_pane(self, pane_id: str) -> bool:
    """Maximize a specific pane.

    Args:
        pane_id: ID of pane to maximize

    Returns:
        True if successful, False if pane doesn't exist or already maximized
    """
    if self._model.is_pane_maximized(pane_id):
        return False  # Already maximized

    return self._controller.toggle_maximize_pane(pane_id)

def restore_maximize(self) -> bool:
    """Restore from maximize mode to normal layout.

    Returns:
        True if successful, False if not currently maximized
    """
    if not self._model.is_maximized():
        return False  # Not maximized

    self._model.set_maximized_pane(None)
    return True

def is_pane_maximized(self) -> bool:
    """Check if any pane is currently maximized.

    Returns:
        True if a pane is maximized, False otherwise
    """
    return self._model.is_maximized()

def get_maximized_pane_id(self) -> Optional[str]:
    """Get ID of currently maximized pane.

    Returns:
        Pane ID if maximized, None if not maximized
    """
    return self._model.get_maximized_pane()
```

**7.2 Add maximize signal to MultisplitWidget**

```python
class MultisplitWidget(QWidget):
    # ... existing signals ...
    maximize_changed = Signal(object)  # Optional[str] - pane_id or None

    def __init__(self, ...):
        # ... existing init ...

        # Connect model maximize signal to public signal
        self._model.signals.maximize_changed.connect(self.maximize_changed.emit)
```

## Phase 8: ViloxTermApp Integration

### File: `apps/viloxterm/src/viloxterm/app.py`

**8.1 Add keybinding action**

In `_setup_keybinding_manager()`, add to action definitions:

```python
ActionDefinition(
    id="pane.toggle_maximize",
    description="Toggle Maximize Pane",
    default_shortcut="Ctrl+M",
    category="Pane",
    callback=self._on_toggle_maximize_pane,
),
```

**8.2 Implement callback handler**

```python
def _on_toggle_maximize_pane(self) -> None:
    """Toggle maximize state of focused pane in current tab.

    Maximizes the currently focused pane to fill the entire tab,
    or restores to normal layout if already maximized.
    """
    # Get current tab widget
    current_tab = self.widget(self.currentIndex())

    # Check if it's a MultisplitWidget
    if not isinstance(current_tab, MultisplitWidget):
        logger.warning("Current tab is not a MultisplitWidget")
        return

    # Toggle maximize on the multisplit widget
    success = current_tab.toggle_maximize_focused_pane()

    if success:
        # Log for debugging
        if current_tab.is_pane_maximized():
            pane_id = current_tab.get_maximized_pane_id()
            logger.info(f"Pane {pane_id} maximized")
        else:
            logger.info("Pane restored from maximize")
```

## Edge Cases & Interactions

### Handled Automatically

1. **Pane closed while maximized**
   - `RemovePaneCommand` removes from registry
   - Model validation catches invalid maximized_pane_id
   - Auto-restore via signal handler

2. **Tab switching**
   - Each MultisplitWidget has independent state
   - No cross-tab interference

3. **Window resize**
   - `resizeEvent()` handles maximize mode specially
   - Maximized pane tracks container size

### Requires Implementation

4. **Splitting while maximized**
   - ✅ Handled: Auto-restore in `SplitPaneCommand.execute()`

5. **Focus changes**
   - ✅ Handled: Auto-restore in `FocusManager.set_focus()`
   - Alternative: Lock focus to maximized pane

6. **TreeReconciler interference**
   - ✅ Handled: Skip reconciliation when maximized

7. **GeometryManager updates**
   - ✅ Handled: Skip geometry updates when maximized

### Session Persistence

**Decision: Do NOT persist maximize state**
- Always load sessions in restored (non-maximized) state
- Simpler implementation, fewer edge cases
- User can easily re-maximize with Ctrl+M
- No need to validate maximized pane still exists on load

## Testing Checklist

### Basic Functionality
- [ ] Ctrl+M maximizes focused pane
- [ ] Ctrl+M again restores original layout
- [ ] Maximized pane fills entire container
- [ ] All other panes hidden
- [ ] All splitters hidden

### Layout Restoration
- [ ] Exact same layout after restore
- [ ] Pane sizes preserved
- [ ] Split ratios preserved
- [ ] Focus preserved

### Edge Cases
- [ ] No focused pane → Ctrl+M does nothing
- [ ] Close maximized pane → Auto-restores
- [ ] Split while maximized → Auto-restores, then splits
- [ ] Navigate focus while maximized → Auto-restores
- [ ] Window resize while maximized → Pane tracks size
- [ ] Window resize while restored → Normal behavior

### Multi-Tab
- [ ] Tab 1 maximized, switch to Tab 2 → Independent states
- [ ] Each tab maintains own maximize state
- [ ] Switching tabs doesn't affect maximize

### Visual
- [ ] Maximize indicator appears in top-right
- [ ] Indicator shows "Maximized" text
- [ ] Indicator disappears on restore
- [ ] No visual artifacts during toggle

### Undo/Redo
- [ ] Undo after maximize → Restores
- [ ] Redo after undo → Maximizes again
- [ ] Undo/redo stack works correctly

### Performance
- [ ] Toggle is instant (<50ms)
- [ ] No flickering during toggle
- [ ] Resize while maximized is smooth

## API Documentation

### MultisplitWidget Public API

```python
# Toggle maximize state of focused pane
success = multisplit.toggle_maximize_focused_pane()

# Maximize specific pane
success = multisplit.maximize_pane("pane-123")

# Restore from maximize mode
success = multisplit.restore_maximize()

# Check if maximized
is_max = multisplit.is_pane_maximized()

# Get maximized pane ID
pane_id = multisplit.get_maximized_pane_id()  # or None

# Listen to maximize state changes
multisplit.maximize_changed.connect(on_maximize_changed)
```

### ViloxTermApp Keybinding

```
Ctrl+M - Toggle maximize focused pane
```

## Implementation Order

1. **Phase 1**: Model layer (state tracking)
2. **Phase 2**: Controller layer (command + auto-restore)
3. **Phase 3**: View core logic (hide/show)
4. **Phase 4**: View coordination (skip reconciler/geometry)
5. **Phase 5**: Focus management (auto-restore on focus)
6. **Phase 6**: Visual indicator
7. **Phase 7**: Public API
8. **Phase 8**: ViloxTermApp integration

## Success Criteria

- ✅ Ctrl+M toggles maximize for focused pane
- ✅ Perfect layout restoration
- ✅ All edge cases handled gracefully
- ✅ Clean MVC architecture maintained
- ✅ Undo/redo support works
- ✅ Per-tab independent state
- ✅ Visual feedback to user
- ✅ Fast, smooth, no flickering
