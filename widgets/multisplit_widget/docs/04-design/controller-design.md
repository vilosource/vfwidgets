# Controller Design

## Overview

The MultiSplit controller layer orchestrates all model mutations through a robust command pattern. It provides transactional integrity, undo/redo capabilities, command merging optimizations, and comprehensive error recovery while maintaining strict separation from both model and view layers.

## What This Covers

- **Command Pattern**: All mutations as reversible operations
- **Transaction System**: Atomic multi-command operations
- **Command Merging**: Performance optimization for rapid operations
- **Error Recovery**: Rollback and state repair mechanisms
- **Undo/Redo Stack**: Full operation history management
- **Validation Pipeline**: Pre-execution command validation

## What This Doesn't Cover

- Model data structures (see [Model Design](model-design.md))
- View reconciliation (see [View Design](view-design.md))
- Focus algorithms (see [Focus Management](focus-management.md))
- Direct user interaction (handled by View layer)

---

## Command Architecture

### Base Command Interface

```python
class Command(ABC):
    """Abstract base for all model mutations"""

    def __init__(self):
        self.command_id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.validation_result: Optional[ValidationResult] = None
        self.execution_result: Optional[CommandResult] = None

    @abstractmethod
    def validate(self, model: PaneModel) -> ValidationResult:
        """Check if command can execute safely"""

    @abstractmethod
    def execute(self, model: PaneModel) -> CommandResult:
        """Apply changes to model"""

    @abstractmethod
    def undo(self, model: PaneModel) -> CommandResult:
        """Reverse the changes"""

    @abstractmethod
    def can_merge_with(self, other: 'Command') -> bool:
        """Check if this command can merge with another"""

    @abstractmethod
    def merge_with(self, other: 'Command') -> 'Command':
        """Create merged command"""

    @abstractmethod
    def serialize(self) -> dict:
        """Convert to JSON-serializable dict"""

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> 'Command':
        """Recreate from serialized data"""

    @property
    def name(self) -> str:
        """Human-readable command name"""
        return self.__class__.__name__.replace('Command', '')

    @property
    def is_structure_changing(self) -> bool:
        """Whether this command modifies tree structure"""
        return True  # Conservative default

class CommandResult:
    """Result of command execution"""

    def __init__(self, success: bool = True, error: Optional[Exception] = None,
                 changed_panes: Optional[set[PaneId]] = None,
                 changed_nodes: Optional[set[NodeId]] = None,
                 structure_changed: bool = False,
                 undo_data: Optional[dict] = None):
        self.success = success
        self.error = error
        self.changed_panes = changed_panes or set()
        self.changed_nodes = changed_nodes or set()
        self.structure_changed = structure_changed
        self.undo_data = undo_data or {}
        self.timestamp = time.time()

class ValidationResult:
    """Result of command validation"""

    def __init__(self, is_valid: bool, errors: list[str] = None,
                 warnings: list[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.is_valid
```

### Core Commands Implementation

```python
class SplitCommand(Command):
    """Split a pane into two"""

    def __init__(self, pane_id: PaneId, where: WherePosition,
                 widget_id: WidgetId, ratio: float = 0.5):
        super().__init__()
        self.pane_id = pane_id
        self.where = where
        self.widget_id = widget_id
        self.ratio = ratio
        self.new_pane_id: Optional[PaneId] = None
        self.new_node_id: Optional[NodeId] = None
        self.replaced_node_id: Optional[NodeId] = None

    def validate(self, model: PaneModel) -> ValidationResult:
        """Validate split preconditions"""
        errors = []

        # Check pane exists
        if self.pane_id not in model.pane_registry:
            errors.append(f"Pane {self.pane_id} not found")
            return ValidationResult(False, errors)

        # Check ratio bounds
        if not (0.1 <= self.ratio <= 0.9):
            errors.append(f"Invalid ratio {self.ratio}, must be 0.1-0.9")

        # Check if pane is locked
        if self.pane_id in model.locked_panes:
            errors.append(f"Pane {self.pane_id} is locked")

        # Check resource limits
        pane_count = len(model.pane_registry)
        if pane_count >= model.global_constraints.max_panes:
            errors.append(f"Maximum pane limit reached ({pane_count})")

        return ValidationResult(len(errors) == 0, errors)

    def execute(self, model: PaneModel) -> CommandResult:
        """Execute the split operation"""
        try:
            # Generate IDs for new nodes
            self.new_pane_id = model.generate_pane_id()
            self.new_node_id = model.generate_node_id()

            # Find target leaf node
            target_leaf = model.pane_registry[self.pane_id]
            self.replaced_node_id = target_leaf.node_id

            # Create new leaf node
            new_leaf = LeafNode(
                model.generate_node_id(),
                self.new_pane_id,
                self.widget_id
            )

            # Determine orientation and order
            orientation = (Orientation.HORIZONTAL if self.where in
                          [WherePosition.LEFT, WherePosition.RIGHT]
                          else Orientation.VERTICAL)

            if self.where in [WherePosition.LEFT, WherePosition.TOP]:
                children = [new_leaf, target_leaf]
                ratios = [self.ratio, 1.0 - self.ratio]
            else:
                children = [target_leaf, new_leaf]
                ratios = [1.0 - self.ratio, self.ratio]

            # Create split node
            split_node = SplitNode(self.new_node_id, orientation, children, ratios)

            # Replace in tree
            self._replace_node_in_tree(model, target_leaf, split_node)

            # Update registries
            model.pane_registry[self.new_pane_id] = new_leaf
            model.node_registry[self.new_node_id] = split_node
            model.node_registry[new_leaf.node_id] = new_leaf

            return CommandResult(
                success=True,
                changed_panes={self.pane_id, self.new_pane_id},
                changed_nodes={self.replaced_node_id, self.new_node_id, new_leaf.node_id},
                structure_changed=True
            )

        except Exception as e:
            return CommandResult(success=False, error=e)

    def undo(self, model: PaneModel) -> CommandResult:
        """Undo the split operation"""
        try:
            # Find the split node we created
            split_node = model.node_registry.get(self.new_node_id)
            if not split_node or not isinstance(split_node, SplitNode):
                raise InvalidStateError("Split node not found for undo")

            # Find the original leaf node
            original_leaf = None
            for child in split_node.children:
                if isinstance(child, LeafNode) and child.pane_id == self.pane_id:
                    original_leaf = child
                    break

            if not original_leaf:
                raise InvalidStateError("Original leaf not found for undo")

            # Replace split with original leaf
            self._replace_node_in_tree(model, split_node, original_leaf)

            # Clean up registries
            if self.new_pane_id in model.pane_registry:
                del model.pane_registry[self.new_pane_id]
            if self.new_node_id in model.node_registry:
                del model.node_registry[self.new_node_id]

            return CommandResult(
                success=True,
                changed_panes={self.pane_id},
                changed_nodes={self.replaced_node_id},
                structure_changed=True
            )

        except Exception as e:
            return CommandResult(success=False, error=e)

    def can_merge_with(self, other: Command) -> bool:
        """Split commands cannot merge"""
        return False

    def _replace_node_in_tree(self, model: PaneModel, old_node: PaneNode,
                             new_node: PaneNode):
        """Replace a node in the tree structure"""
        if model.root == old_node:
            model.root = new_node
            return

        # Find parent of old node
        parent_visitor = ParentSearchVisitor(old_node)
        if model.root:
            model.root.accept(parent_visitor)

        if parent_visitor.parent:
            # Replace in parent's children
            children = list(parent_visitor.parent.children)
            children[parent_visitor.child_index] = new_node
            # Update parent with new children
            parent_visitor.parent._children = children

class ResizeCommand(Command):
    """Resize panes by adjusting split ratios"""

    def __init__(self, split_node_id: NodeId, divider_index: int,
                 new_position: float):
        super().__init__()
        self.split_node_id = split_node_id
        self.divider_index = divider_index
        self.new_position = new_position
        self.old_ratios: Optional[list[float]] = None

    def validate(self, model: PaneModel) -> ValidationResult:
        """Validate resize operation"""
        errors = []

        # Check split exists
        split_node = model.node_registry.get(self.split_node_id)
        if not split_node or not isinstance(split_node, SplitNode):
            errors.append(f"Split node {self.split_node_id} not found")
            return ValidationResult(False, errors)

        # Check divider index
        if not (0 <= self.divider_index < len(split_node.children) - 1):
            errors.append(f"Invalid divider index {self.divider_index}")

        # Check position bounds
        if not (0.1 <= self.new_position <= 0.9):
            errors.append(f"Invalid position {self.new_position}")

        return ValidationResult(len(errors) == 0, errors)

    def execute(self, model: PaneModel) -> CommandResult:
        """Execute resize operation"""
        try:
            split_node = model.node_registry[self.split_node_id]
            self.old_ratios = split_node.ratios.copy()

            # Calculate new ratios
            new_ratios = split_node.ratios.copy()

            # For simplicity, handle 2-child splits
            if len(new_ratios) == 2:
                new_ratios[0] = self.new_position
                new_ratios[1] = 1.0 - self.new_position
            else:
                # More complex multi-split logic here
                delta = self.new_position - sum(new_ratios[:self.divider_index + 1])
                new_ratios[self.divider_index] += delta
                new_ratios[self.divider_index + 1] -= delta

            # Apply constraints and normalize
            new_ratios = self._apply_constraints(model, split_node, new_ratios)
            split_node._ratios = new_ratios

            return CommandResult(
                success=True,
                changed_nodes={self.split_node_id},
                structure_changed=False
            )

        except Exception as e:
            return CommandResult(success=False, error=e)

    def undo(self, model: PaneModel) -> CommandResult:
        """Undo resize operation"""
        try:
            if not self.old_ratios:
                raise InvalidStateError("No old ratios saved for undo")

            split_node = model.node_registry[self.split_node_id]
            split_node._ratios = self.old_ratios

            return CommandResult(
                success=True,
                changed_nodes={self.split_node_id},
                structure_changed=False
            )

        except Exception as e:
            return CommandResult(success=False, error=e)

    def can_merge_with(self, other: Command) -> bool:
        """Check if can merge with another resize command"""
        return (isinstance(other, ResizeCommand) and
                other.split_node_id == self.split_node_id and
                other.divider_index == self.divider_index and
                abs(other.timestamp - self.timestamp) < 0.1)  # 100ms window

    def merge_with(self, other: Command) -> Command:
        """Merge with another resize command"""
        if not isinstance(other, ResizeCommand):
            raise ValueError("Cannot merge with non-resize command")

        # Create new command with latest position but original old_ratios
        merged = ResizeCommand(
            self.split_node_id,
            self.divider_index,
            other.new_position
        )
        merged.old_ratios = self.old_ratios  # Keep original state
        return merged
```

---

## Transaction System

### Transaction Manager

```python
class TransactionManager:
    """Manages atomic multi-command operations"""

    def __init__(self, controller: 'PaneController'):
        self.controller = controller
        self.transaction_stack: list[Command] = []
        self.in_transaction = False
        self.transaction_id: Optional[str] = None
        self.rollback_state: Optional[dict] = None

    def begin_transaction(self) -> 'TransactionContext':
        """Start a new transaction"""
        if self.in_transaction:
            raise InvalidOperationError("Transaction already in progress")

        self.in_transaction = True
        self.transaction_id = str(uuid.uuid4())
        self.transaction_stack.clear()

        # Save current state for rollback
        self.rollback_state = self.controller.model.serializer.save_model(
            self.controller.model
        )

        return TransactionContext(self)

    def add_command(self, command: Command):
        """Add command to current transaction"""
        if not self.in_transaction:
            raise InvalidOperationError("No transaction in progress")

        self.transaction_stack.append(command)

    def commit_transaction(self) -> bool:
        """Commit all commands in transaction"""
        if not self.in_transaction:
            raise InvalidOperationError("No transaction to commit")

        try:
            # Validate all commands first
            for command in self.transaction_stack:
                validation = command.validate(self.controller.model)
                if not validation.is_valid:
                    raise CommandValidationError(
                        f"Command {command.name} validation failed: {validation.errors}"
                    )

            # Execute all commands
            executed_commands = []
            for command in self.transaction_stack:
                result = command.execute(self.controller.model)
                if not result.success:
                    # Rollback previous commands in this transaction
                    for executed in reversed(executed_commands):
                        executed.undo(self.controller.model)
                    raise CommandExecutionError(
                        f"Command {command.name} execution failed: {result.error}"
                    )
                executed_commands.append(command)

            # All succeeded - add to undo stack as compound command
            compound = CompoundCommand(executed_commands, self.transaction_id)
            self.controller.undo_stack.append(compound)
            self.controller.redo_stack.clear()

            # Emit signals
            self.controller.model.signals.changed.emit()

            return True

        finally:
            self._cleanup_transaction()

    def rollback_transaction(self):
        """Rollback current transaction"""
        if not self.in_transaction:
            return

        try:
            if self.rollback_state:
                # Restore previous state
                self.controller.model.serializer.restore_model(
                    self.controller.model, self.rollback_state
                )
        finally:
            self._cleanup_transaction()

    def _cleanup_transaction(self):
        """Clean up transaction state"""
        self.in_transaction = False
        self.transaction_id = None
        self.transaction_stack.clear()
        self.rollback_state = None

class TransactionContext:
    """Context manager for transactions"""

    def __init__(self, manager: TransactionManager):
        self.manager = manager
        self.controller = manager.controller

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.manager.rollback_transaction()
        else:
            self.manager.commit_transaction()

    def execute(self, command: Command) -> CommandResult:
        """Execute command within transaction"""
        self.manager.add_command(command)
        return command.execute(self.controller.model)

class CompoundCommand(Command):
    """Container for multiple commands executed as one unit"""

    def __init__(self, commands: list[Command], transaction_id: str):
        super().__init__()
        self.commands = commands
        self.transaction_id = transaction_id

    def validate(self, model: PaneModel) -> ValidationResult:
        """Validate all sub-commands"""
        all_errors = []
        for command in self.commands:
            result = command.validate(model)
            if not result.is_valid:
                all_errors.extend(result.errors)
        return ValidationResult(len(all_errors) == 0, all_errors)

    def execute(self, model: PaneModel) -> CommandResult:
        """Execute all sub-commands"""
        # Should already be executed, this is for replay scenarios
        combined_result = CommandResult()
        for command in self.commands:
            result = command.execute(model)
            combined_result.changed_panes.update(result.changed_panes)
            combined_result.changed_nodes.update(result.changed_nodes)
            combined_result.structure_changed |= result.structure_changed
        return combined_result

    def undo(self, model: PaneModel) -> CommandResult:
        """Undo all sub-commands in reverse order"""
        combined_result = CommandResult()
        for command in reversed(self.commands):
            result = command.undo(model)
            combined_result.changed_panes.update(result.changed_panes)
            combined_result.changed_nodes.update(result.changed_nodes)
            combined_result.structure_changed |= result.structure_changed
        return combined_result

    def can_merge_with(self, other: Command) -> bool:
        """Compound commands don't merge"""
        return False

    @property
    def name(self) -> str:
        return f"Transaction({len(self.commands)} commands)"
```

---

## Command Merging System

### Merge Strategy Engine

```python
class CommandMerger:
    """Handles command merging for performance optimization"""

    def __init__(self):
        self.merge_window = 0.5  # seconds
        self.max_merge_count = 10
        self.merge_strategies = {
            ResizeCommand: ResizeMergeStrategy(),
            FocusCommand: FocusMergeStrategy(),
            # Add more strategies as needed
        }

    def can_merge_commands(self, existing: Command, new: Command) -> bool:
        """Check if two commands can be merged"""
        # Must be same type
        if type(existing) != type(new):
            return False

        # Check time window
        time_delta = new.timestamp - existing.timestamp
        if time_delta > self.merge_window:
            return False

        # Use command-specific logic
        return existing.can_merge_with(new)

    def merge_commands(self, commands: list[Command]) -> Command:
        """Merge a sequence of compatible commands"""
        if len(commands) < 2:
            raise ValueError("Need at least 2 commands to merge")

        command_type = type(commands[0])
        strategy = self.merge_strategies.get(command_type)

        if not strategy:
            raise ValueError(f"No merge strategy for {command_type}")

        return strategy.merge(commands)

class ResizeMergeStrategy:
    """Strategy for merging resize commands"""

    def merge(self, commands: list[ResizeCommand]) -> ResizeCommand:
        """Merge multiple resize commands"""
        if not commands:
            raise ValueError("No commands to merge")

        # All should target same split and divider
        first = commands[0]
        for cmd in commands[1:]:
            if (cmd.split_node_id != first.split_node_id or
                cmd.divider_index != first.divider_index):
                raise ValueError("Cannot merge resizes on different dividers")

        # Create merged command with final position but original old_ratios
        merged = ResizeCommand(
            first.split_node_id,
            first.divider_index,
            commands[-1].new_position  # Final position
        )
        merged.old_ratios = first.old_ratios  # Original state
        return merged

class FocusMergeStrategy:
    """Strategy for merging focus commands"""

    def merge(self, commands: list[FocusCommand]) -> FocusCommand:
        """Merge multiple focus commands"""
        # Just keep the last focus target
        return commands[-1]
```

---

## Error Recovery System

### Recovery Strategies

```python
class ErrorRecoveryManager:
    """Handles error recovery and state repair"""

    def __init__(self, controller: 'PaneController'):
        self.controller = controller
        self.recovery_strategies = {
            InvalidStructureError: self._recover_structure_error,
            CommandExecutionError: self._recover_execution_error,
            StateCorruptionError: self._recover_corruption_error,
        }
        self.checkpoint_interval = 10  # Commands between checkpoints
        self.checkpoints: list[dict] = []
        self.max_checkpoints = 5

    def handle_error(self, error: Exception, context: str = "") -> bool:
        """Handle error with appropriate recovery strategy"""
        error_type = type(error)
        strategy = self.recovery_strategies.get(error_type)

        if strategy:
            try:
                return strategy(error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                return self._fallback_recovery()
        else:
            logger.error(f"No recovery strategy for {error_type}")
            return self._fallback_recovery()

    def _recover_structure_error(self, error: InvalidStructureError,
                                context: str) -> bool:
        """Recover from tree structure corruption"""
        logger.warning(f"Structure error detected: {error}")

        # Try to repair the tree
        if self.controller.model.root:
            try:
                repaired_root = self._attempt_tree_repair(self.controller.model.root)
                if repaired_root:
                    self.controller.model.root = repaired_root
                    self.controller.model._rebuild_registries()
                    return True
            except Exception as repair_error:
                logger.error(f"Tree repair failed: {repair_error}")

        # Fall back to checkpoint recovery
        return self._recover_from_checkpoint()

    def _recover_execution_error(self, error: CommandExecutionError,
                                context: str) -> bool:
        """Recover from command execution failure"""
        logger.warning(f"Command execution error: {error}")

        # Try to undo the failed command if it was partially executed
        if hasattr(error, 'command') and hasattr(error.command, 'undo'):
            try:
                error.command.undo(self.controller.model)
                return True
            except Exception:
                pass

        # Validate current state
        validation = self.controller.model.validate_complete_state()
        if validation.is_valid:
            return True  # State is still valid, continue

        # State is corrupted, try checkpoint recovery
        return self._recover_from_checkpoint()

    def _recover_corruption_error(self, error: StateCorruptionError,
                                 context: str) -> bool:
        """Recover from state corruption"""
        logger.error(f"State corruption detected: {error}")

        # Always try checkpoint recovery for corruption
        return self._recover_from_checkpoint()

    def _recover_from_checkpoint(self) -> bool:
        """Restore from most recent valid checkpoint"""
        while self.checkpoints:
            checkpoint = self.checkpoints.pop()
            try:
                self.controller.model.serializer.restore_model(
                    self.controller.model, checkpoint
                )
                logger.info("Recovered from checkpoint")
                return True
            except Exception as restore_error:
                logger.warning(f"Checkpoint restore failed: {restore_error}")
                continue

        # No valid checkpoints, reset to minimal state
        return self._fallback_recovery()

    def _fallback_recovery(self) -> bool:
        """Last resort: reset to minimal working state"""
        logger.warning("Performing fallback recovery")

        try:
            # Reset model to empty state
            self.controller.model.reset()

            # Clear command stacks
            self.controller.undo_stack.clear()
            self.controller.redo_stack.clear()

            # Clear checkpoints
            self.checkpoints.clear()

            logger.info("Fallback recovery completed")
            return True

        except Exception as fallback_error:
            logger.critical(f"Fallback recovery failed: {fallback_error}")
            return False

    def create_checkpoint(self):
        """Create a recovery checkpoint"""
        try:
            state = self.controller.model.serializer.save_model(
                self.controller.model
            )
            self.checkpoints.append(state)

            # Limit checkpoint count
            if len(self.checkpoints) > self.max_checkpoints:
                self.checkpoints.pop(0)

        except Exception as e:
            logger.warning(f"Checkpoint creation failed: {e}")

    def _attempt_tree_repair(self, root: PaneNode) -> Optional[PaneNode]:
        """Try to repair a corrupted tree"""
        try:
            # Use tree repair visitor
            repair_visitor = TreeRepairVisitor()
            repaired = root.accept(repair_visitor)

            # Validate the repair
            validator = TreeValidator()
            result = validator.validate_tree(repaired)

            if result.is_valid:
                return repaired
            else:
                logger.warning(f"Tree repair validation failed: {result.errors}")
                return None

        except Exception as e:
            logger.error(f"Tree repair attempt failed: {e}")
            return None
```

---

## Controller Implementation

### Main Controller Class

```python
class PaneController:
    """Main controller orchestrating all model mutations"""

    def __init__(self, model: PaneModel):
        self.model = model
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self.max_undo_count = 100

        # Subsystems
        self.transaction_manager = TransactionManager(self)
        self.command_merger = CommandMerger()
        self.error_recovery = ErrorRecoveryManager(self)
        self.validator = CommandValidator()

        # State
        self.last_executed_command: Optional[Command] = None
        self.command_count = 0

    def execute_command(self, command: Command) -> CommandResult:
        """Execute a command with full error handling"""
        try:
            # Increment command counter and maybe checkpoint
            self.command_count += 1
            if self.command_count % self.error_recovery.checkpoint_interval == 0:
                self.error_recovery.create_checkpoint()

            # Pre-execution validation
            validation = self.validator.validate_command(command, self.model)
            if not validation.is_valid:
                return CommandResult(
                    success=False,
                    error=CommandValidationError(validation.errors)
                )

            # Check for command merging opportunity
            if (self.last_executed_command and
                self.command_merger.can_merge_commands(self.last_executed_command, command)):

                # Remove last command from undo stack
                if self.undo_stack:
                    self.undo_stack.pop()

                # Merge commands
                merged = self.command_merger.merge_commands([
                    self.last_executed_command, command
                ])
                command = merged

            # Begin model mutation
            self.model.signals.about_to_change.emit()

            # Execute command
            result = command.execute(self.model)

            if result.success:
                # Post-execution validation
                state_validation = self.model.validate_complete_state()
                if not state_validation.is_valid:
                    # Rollback on corruption
                    command.undo(self.model)
                    raise StateCorruptionError(state_validation.errors)

                # Add to undo stack
                self.undo_stack.append(command)
                if len(self.undo_stack) > self.max_undo_count:
                    self.undo_stack.pop(0)

                # Clear redo stack
                self.redo_stack.clear()

                # Update state
                self.last_executed_command = command

                # Emit completion signals
                self.model.signals.changed.emit()
                if result.structure_changed:
                    self.model.signals.structure_changed.emit()

            return result

        except Exception as e:
            # Handle error with recovery system
            recovery_success = self.error_recovery.handle_error(e, f"execute_command({command.name})")

            return CommandResult(
                success=False,
                error=e if not recovery_success else RecoveredError(e)
            )

    def undo(self) -> bool:
        """Undo the last command"""
        if not self.undo_stack:
            return False

        command = self.undo_stack.pop()

        try:
            self.model.signals.about_to_change.emit()
            result = command.undo(self.model)

            if result.success:
                self.redo_stack.append(command)
                self.model.signals.changed.emit()
                if result.structure_changed:
                    self.model.signals.structure_changed.emit()
                return True

        except Exception as e:
            # Put command back on undo stack
            self.undo_stack.append(command)
            self.error_recovery.handle_error(e, "undo")

        return False

    def redo(self) -> bool:
        """Redo the last undone command"""
        if not self.redo_stack:
            return False

        command = self.redo_stack.pop()
        result = self.execute_command(command)
        return result.success

    def begin_transaction(self) -> TransactionContext:
        """Start a transaction for atomic multi-command operations"""
        return self.transaction_manager.begin_transaction()

    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of operation that would be undone"""
        if self.undo_stack:
            return f"Undo {self.undo_stack[-1].name}"
        return None

    def clear_history(self):
        """Clear undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.last_executed_command = None
```

---

## Command Serialization & Priority

### Full Command Serialization

```python
class CommandSerializer:
    """Complete command serialization system"""

    def serialize_command(self, command: Command) -> dict:
        """Serialize command to JSON-compatible dict"""
        return {
            'type': command.__class__.__name__,
            'command_id': command.command_id,
            'timestamp': command.timestamp,
            'parameters': self._extract_parameters(command),
            'metadata': getattr(command, 'metadata', {}),
            'priority': getattr(command, 'priority', 0)
        }

    def deserialize_command(self, data: dict) -> Command:
        """Recreate command from serialized data"""
        command_type = data['type']
        command_class = self._get_command_class(command_type)

        # Reconstruct command
        command = command_class(**data['parameters'])
        command.command_id = data['command_id']
        command.timestamp = data['timestamp']

        if 'metadata' in data:
            command.metadata = data['metadata']
        if 'priority' in data:
            command.priority = data['priority']

        return command

    def _extract_parameters(self, command: Command) -> dict:
        """Extract constructor parameters"""
        params = {}
        signature = inspect.signature(command.__class__.__init__)

        for param_name in signature.parameters:
            if param_name != 'self' and hasattr(command, param_name):
                value = getattr(command, param_name)
                params[param_name] = self._serialize_value(value)

        return params

    def _serialize_value(self, value: Any) -> Any:
        """Serialize complex types"""
        if isinstance(value, (PaneId, NodeId, WidgetId)):
            return str(value)
        elif isinstance(value, Enum):
            return value.value
        elif hasattr(value, '__dict__'):
            return {k: self._serialize_value(v)
                   for k, v in value.__dict__.items()}
        return value
```

### Command Priority & Ordering

```python
class PriorityCommandQueue:
    """Priority-based command execution"""

    def __init__(self):
        self._queue = []
        self._sequence = 0
        self._rate_limiter = RateLimiter()

    def enqueue(self, command: Command, priority: int = 0):
        """Add command with priority"""
        # Rate limiting check
        if not self._rate_limiter.allow(command):
            raise RateLimitExceeded(f"Command {command.name} rate limited")

        entry = (
            -priority,  # Negative for max heap behavior
            self._sequence,
            command
        )
        heapq.heappush(self._queue, entry)
        self._sequence += 1

    def dequeue(self) -> Optional[Command]:
        """Get highest priority command"""
        if self._queue:
            _, _, command = heapq.heappop(self._queue)
            return command
        return None

    def peek(self) -> Optional[Command]:
        """View next command without removing"""
        if self._queue:
            return self._queue[0][2]
        return None

class RateLimiter:
    """Rate limiting for rapid commands"""

    def __init__(self):
        self.limits = {
            'ResizeCommand': (10, 1.0),  # 10 per second
            'FocusCommand': (5, 1.0),     # 5 per second
            'SplitCommand': (2, 1.0),     # 2 per second
        }
        self.history = defaultdict(deque)

    def allow(self, command: Command) -> bool:
        """Check if command is within rate limit"""
        command_type = command.__class__.__name__

        if command_type not in self.limits:
            return True

        max_count, time_window = self.limits[command_type]
        now = time.time()
        history = self.history[command_type]

        # Remove old entries
        while history and history[0] < now - time_window:
            history.popleft()

        if len(history) >= max_count:
            return False

        history.append(now)
        return True
```

---

## Performance Metrics

### Command Execution Benchmarks

| Command Type | Target Latency | Max Latency | Throughput |
|--------------|---------------|-------------|------------|
| Split | < 10ms | 50ms | 100/sec |
| Close | < 5ms | 20ms | 200/sec |
| Resize | < 2ms | 10ms | 500/sec |
| Focus | < 1ms | 5ms | 1000/sec |
| Move | < 15ms | 60ms | 50/sec |

### Optimization Strategies

```python
class CommandOptimizer:
    """Optimize command execution"""

    def optimize_batch(self, commands: list[Command]) -> list[Command]:
        """Optimize a batch of commands"""
        # Group mergeable commands
        groups = self._group_mergeable(commands)

        # Merge within groups
        optimized = []
        for group in groups:
            if len(group) == 1:
                optimized.append(group[0])
            else:
                merged = self._merge_group(group)
                optimized.append(merged)

        # Reorder for efficiency
        return self._reorder_for_efficiency(optimized)

    def _group_mergeable(self, commands: list[Command]) -> list[list[Command]]:
        """Group commands that can be merged"""
        groups = []
        current_group = []

        for command in commands:
            if not current_group:
                current_group.append(command)
            elif current_group[-1].can_merge_with(command):
                current_group.append(command)
            else:
                groups.append(current_group)
                current_group = [command]

        if current_group:
            groups.append(current_group)

        return groups

    def _merge_group(self, group: list[Command]) -> Command:
        """Merge a group of commands"""
        result = group[0]
        for command in group[1:]:
            result = result.merge_with(command)
        return result

    def _reorder_for_efficiency(self, commands: list[Command]) -> list[Command]:
        """Reorder commands for cache efficiency"""
        # Structure-changing commands first
        structure_changing = [c for c in commands if c.is_structure_changing]
        non_structure = [c for c in commands if not c.is_structure_changing]

        return structure_changing + non_structure
```

---

## Common Pitfalls

### ❌ Bypassing Command Pattern
```python
# DON'T: Mutate model directly
model.root.children.append(new_node)
model.focused_pane_id = "pane-123"

# DO: Use commands for all mutations
controller.execute_command(SplitCommand(pane_id, WHERE, widget_id))
controller.execute_command(FocusCommand("pane-123"))
```

### ❌ Breaking Transaction Atomicity
```python
# DON'T: Execute commands outside transaction
controller.execute_command(split_cmd)
if some_condition:
    controller.execute_command(focus_cmd)  # Inconsistent!

# DO: Use transaction for related operations
with controller.begin_transaction():
    controller.execute_command(split_cmd)
    controller.execute_command(focus_cmd)
```

### ❌ Ignoring Validation Failures
```python
# DON'T: Ignore validation results
result = controller.execute_command(cmd)
# Continue regardless of result.success

# DO: Check and handle validation failures
result = controller.execute_command(cmd)
if not result.success:
    handle_error(result.error)
```

### ❌ Improper Error Recovery
```python
# DON'T: Let errors corrupt state
try:
    risky_command.execute(model)
except Exception:
    pass  # State may be corrupted!

# DO: Use proper error recovery
try:
    result = controller.execute_command(risky_command)
    if not result.success:
        # Controller handles recovery automatically
        handle_failure(result.error)
```

### ❌ Command Merging Bugs
```python
# DON'T: Merge incompatible commands
if type(cmd1) == type(cmd2):  # Too simplistic!
    merged = merge_commands([cmd1, cmd2])

# DO: Use proper merge validation
if command_merger.can_merge_commands(cmd1, cmd2):
    merged = command_merger.merge_commands([cmd1, cmd2])
```

---

## Quick Reference

### Command Lifecycle
| Phase | Actions | Error Handling |
|-------|---------|---------------|
| Validate | Check preconditions | Return ValidationResult |
| Execute | Mutate model state | Rollback on failure |
| Undo | Reverse mutations | Log and continue |
| Merge | Combine compatible operations | Validate compatibility |

### Transaction States
| State | Description | Operations |
|-------|-------------|------------|
| `None` | No transaction | Individual command execution |
| `Active` | Transaction in progress | Commands added to stack |
| `Committing` | Finalizing transaction | All commands executed |
| `Rolling Back` | Undoing transaction | State restored |

### Error Recovery Levels
| Level | Strategy | Fallback |
|-------|----------|----------|
| Command | Undo failed operation | State validation |
| Structure | Repair tree integrity | Checkpoint restore |
| Corruption | Restore valid state | Reset to minimal |
| Critical | Emergency reset | Application restart |

### Command Types
| Command | Purpose | Mergeable | Structure Changing |
|---------|---------|-----------|-------------------|
| `SplitCommand` | Create new pane | No | Yes |
| `CloseCommand` | Remove pane | No | Yes |
| `ResizeCommand` | Adjust ratios | Yes | No |
| `FocusCommand` | Change focus | Yes | No |
| `MoveCommand` | Relocate pane | No | Yes |

### Validation Points
| Point | Checks | Recovery |
|-------|--------|----------|
| Pre-execution | Command validity | Reject command |
| Post-execution | State integrity | Rollback changes |
| Transaction commit | All commands valid | Rollback transaction |
| Periodic | Complete state | Checkpoint restore |

---

## Validation Checklist

- ✅ All model mutations go through commands
- ✅ Commands implement full interface (validate/execute/undo)
- ✅ Transactions are atomic (all-or-nothing)
- ✅ Error recovery preserves state integrity
- ✅ Command merging validates compatibility
- ✅ Undo/redo stacks maintain consistency
- ✅ Validation occurs at all critical points
- ✅ Checkpoints are created regularly
- ✅ State corruption triggers recovery
- ✅ Fallback recovery always succeeds

## Related Documents

- **[Model Design](model-design.md)** - Model data structures and validation
- **[View Design](view-design.md)** - View reconciliation and rendering
- **[Focus Management](focus-management.md)** - Focus command implementations
- **[MVC Architecture](../02-architecture/mvc-architecture.md)** - Layer boundaries
- **[MVP Plan](../03-implementation/mvp-plan.md)** - Command implementations
- **[Development Protocol](../03-implementation/development-protocol.md)** - Command patterns
- **[Tree Structure](../02-architecture/tree-structure.md)** - Tree mutation commands
- **[Widget Provider](../02-architecture/widget-provider.md)** - Widget lifecycle commands
- **[Development Rules](../03-implementation/development-rules.md)** - Command pattern enforcement

---

The controller design ensures that all model mutations are reversible, atomic, and error-resistant while providing the transactional integrity needed for complex multi-pane operations.