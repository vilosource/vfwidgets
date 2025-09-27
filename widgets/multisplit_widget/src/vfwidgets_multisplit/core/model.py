"""Core model for MultiSplit widget.

Pure Python implementation with no Qt dependencies.
Manages tree state and emits signals for changes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .nodes import LeafNode, PaneNode, SplitNode
from .signals import ModelSignals
from .tree_utils import validate_tree_structure
from .types import NodeId, Orientation, PaneId, WidgetId


@dataclass
class PaneModel:
    """Core model managing pane tree state.

    This is the single source of truth for the pane structure.
    All mutations must go through the controller's commands.
    """

    root: Optional[PaneNode] = None
    focused_pane_id: Optional[PaneId] = None
    signals: ModelSignals = field(default_factory=ModelSignals)

    # Internal state
    _pane_registry: Dict[PaneId, PaneNode] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize model state."""
        if self.root:
            self._rebuild_registry()

    def _rebuild_registry(self):
        """Rebuild the pane ID registry."""
        self._pane_registry.clear()
        if not self.root:
            return

        from .tree_utils import get_all_leaves
        for leaf in get_all_leaves(self.root):
            self._pane_registry[leaf.pane_id] = leaf

    def get_pane(self, pane_id: PaneId) -> Optional[PaneNode]:
        """Get pane by ID."""
        return self._pane_registry.get(pane_id)

    def get_all_pane_ids(self) -> List[PaneId]:
        """Get all pane IDs."""
        return list(self._pane_registry.keys())

    def set_focused_pane(self, pane_id: Optional[PaneId]) -> bool:
        """Set the focused pane.

        Args:
            pane_id: ID of pane to focus, or None to clear focus

        Returns:
            True if focus changed, False otherwise
        """
        if pane_id and pane_id not in self._pane_registry:
            return False

        if self.focused_pane_id != pane_id:
            old_id = self.focused_pane_id
            self.focused_pane_id = pane_id
            self.signals.focus_changed.emit(old_id, pane_id)
            return True
        return False

    def get_focused_pane(self) -> Optional[PaneNode]:
        """Get the currently focused pane node."""
        if self.focused_pane_id:
            return self._pane_registry.get(self.focused_pane_id)
        return None

    def focus_first_pane(self) -> bool:
        """Focus the first available pane."""
        pane_ids = self.get_all_pane_ids()
        if pane_ids:
            return self.set_focused_pane(pane_ids[0])
        return False

    def validate(self) -> tuple[bool, List[str]]:
        """Validate model state."""
        if not self.root:
            return True, []  # Empty is valid

        return validate_tree_structure(self.root)

    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """Serialize model to dictionary.

        Args:
            include_metadata: Whether to include metadata

        Returns:
            Serialized model state
        """
        def node_to_dict(node: PaneNode) -> Dict[str, Any]:
            if isinstance(node, LeafNode):
                return {
                    'type': 'leaf',
                    'pane_id': str(node.pane_id),
                    'widget_id': str(node.widget_id),
                    'constraints': {
                        'min_width': node.constraints.min_width,
                        'min_height': node.constraints.min_height,
                        'max_width': node.constraints.max_width,
                        'max_height': node.constraints.max_height,
                    }
                }
            elif isinstance(node, SplitNode):
                return {
                    'type': 'split',
                    'node_id': str(node.node_id),
                    'orientation': node.orientation.value,
                    'ratios': node.ratios,
                    'children': [node_to_dict(child) for child in node.children]
                }
            return {}

        data = {
            'root': node_to_dict(self.root) if self.root else None,
            'focused_pane_id': str(self.focused_pane_id) if self.focused_pane_id else None
        }

        if include_metadata:
            data['version'] = '1.0.0'
            data['widget_version'] = '0.1.0'

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaneModel':
        """Deserialize model from dictionary.

        Args:
            data: Serialized model data

        Returns:
            Restored model instance
        """
        from .types import SizeConstraints

        # Check version compatibility
        version = data.get('version', '1.0.0')
        if version.split('.')[0] != '1':
            raise ValueError(f"Incompatible version: {version}")

        def dict_to_node(node_dict: Dict[str, Any]) -> Optional[PaneNode]:
            if not node_dict:
                return None

            if node_dict['type'] == 'leaf':
                constraints_data = node_dict.get('constraints', {})
                return LeafNode(
                    pane_id=PaneId(node_dict['pane_id']),
                    widget_id=WidgetId(node_dict['widget_id']),
                    constraints=SizeConstraints(
                        min_width=constraints_data.get('min_width', 50),
                        min_height=constraints_data.get('min_height', 50),
                        max_width=constraints_data.get('max_width'),
                        max_height=constraints_data.get('max_height')
                    )
                )
            elif node_dict['type'] == 'split':
                children = [dict_to_node(child) for child in node_dict['children']]
                return SplitNode(
                    node_id=NodeId(node_dict['node_id']),
                    orientation=Orientation(node_dict['orientation']),
                    children=[c for c in children if c],
                    ratios=node_dict['ratios']
                )
            return None

        root = dict_to_node(data.get('root'))
        focused = data.get('focused_pane_id')

        model = cls(root=root)
        if focused:
            model.focused_pane_id = PaneId(focused)

        return model
