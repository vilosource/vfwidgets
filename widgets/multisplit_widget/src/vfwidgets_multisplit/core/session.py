"""Session management for MultiSplit widget.

Handles saving and loading layout state.
"""

import json
from pathlib import Path

from .model import PaneModel


class SessionManager:
    """Manages session persistence."""

    def __init__(self, model: PaneModel):
        """Initialize session manager.

        Args:
            model: Model to manage
        """
        self.model = model

    def save_to_file(self, filepath: Path) -> bool:
        """Save session to file.

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            data = self.model.to_dict(include_metadata=True)

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Failed to save session: {e}")
            return False

    def load_from_file(self, filepath: Path) -> bool:
        """Load session from file.

        Args:
            filepath: Path to load file

        Returns:
            True if successful
        """
        try:
            if not filepath.exists():
                return False

            with open(filepath) as f:
                data = json.load(f)

            # Create new model from data
            new_model = PaneModel.from_dict(data)

            # Update our model
            self.model.root = new_model.root
            self.model.focused_pane_id = new_model.focused_pane_id
            self.model._rebuild_registry()

            # Emit change signal
            self.model.signals.structure_changed.emit()

            return True
        except Exception as e:
            print(f"Failed to load session: {e}")
            return False

    def save_to_string(self) -> str:
        """Save session to JSON string.

        Returns:
            JSON string representation
        """
        data = self.model.to_dict(include_metadata=True)
        return json.dumps(data, indent=2)

    def load_from_string(self, json_str: str) -> bool:
        """Load session from JSON string.

        Args:
            json_str: JSON string to load

        Returns:
            True if successful
        """
        try:
            data = json.loads(json_str)
            new_model = PaneModel.from_dict(data)

            self.model.root = new_model.root
            self.model.focused_pane_id = new_model.focused_pane_id
            self.model._rebuild_registry()

            self.model.signals.structure_changed.emit()

            return True
        except Exception as e:
            print(f"Failed to load from string: {e}")
            return False
