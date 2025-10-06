"""Unit tests for KeybindingStorage."""

import json

from vfwidgets_keybinding.storage import KeybindingStorage


class TestKeybindingStorage:
    """Test KeybindingStorage class."""

    def test_in_memory_storage(self):
        """Test storage without file path."""
        storage = KeybindingStorage(file_path=None)

        bindings = {"file.save": "Ctrl+S"}
        assert storage.save(bindings) is True

        loaded = storage.load()
        assert loaded == bindings

    def test_save_and_load(self, temp_storage_file):
        """Test saving and loading from file."""
        storage = KeybindingStorage(str(temp_storage_file))

        bindings = {"file.save": "Ctrl+S", "edit.copy": "Ctrl+C"}
        assert storage.save(bindings) is True

        loaded = storage.load()
        assert loaded == bindings

    def test_load_nonexistent_file(self, temp_storage_file):
        """Test loading from file that doesn't exist."""
        # Don't create the file
        temp_storage_file.unlink()

        storage = KeybindingStorage(str(temp_storage_file))
        loaded = storage.load()
        assert loaded == {}

    def test_load_invalid_json(self, temp_storage_file):
        """Test loading file with invalid JSON."""
        temp_storage_file.write_text("invalid json {")

        storage = KeybindingStorage(str(temp_storage_file))
        loaded = storage.load()
        assert loaded == {}  # Returns empty dict, doesn't crash

    def test_load_validates_format(self, temp_storage_file):
        """Test that load validates key/value types."""
        # Write file with invalid entries
        # Note: JSON will convert integer keys to strings, so we test invalid values
        temp_storage_file.write_text(
            json.dumps(
                {
                    "valid.action": "Ctrl+S",
                    "invalid.value": 123,  # Non-string value
                    "null.value": None,  # None is actually valid
                }
            )
        )

        storage = KeybindingStorage(str(temp_storage_file))
        loaded = storage.load()

        # Valid entries should be loaded (including None for unbound actions)
        assert loaded == {"valid.action": "Ctrl+S", "null.value": None}
        assert "invalid.value" not in loaded  # Invalid value should be skipped

    def test_save_creates_parent_directory(self, temp_storage_file):
        """Test that save creates parent directories."""
        nested_path = temp_storage_file.parent / "subdir" / "keys.json"
        storage = KeybindingStorage(str(nested_path))

        assert storage.save({"test": "Ctrl+T"}) is True
        assert nested_path.exists()

        # Cleanup
        nested_path.unlink()
        nested_path.parent.rmdir()

    def test_save_is_atomic(self, temp_storage_file):
        """Test that save uses atomic write."""
        storage = KeybindingStorage(str(temp_storage_file))
        storage.save({"initial": "Ctrl+I"})

        # Verify temp file doesn't exist after save
        temp_file = temp_storage_file.with_suffix(".tmp")
        assert not temp_file.exists()

    def test_merge_defaults_and_overrides(self):
        """Test merging default and override bindings."""
        storage = KeybindingStorage()

        defaults = {"file.save": "Ctrl+S", "file.open": "Ctrl+O", "edit.copy": "Ctrl+C"}

        overrides = {
            "file.save": "Ctrl+Alt+S",  # Override
            "custom.action": "Ctrl+X",  # New binding
        }

        merged = storage.merge(defaults, overrides)

        assert merged["file.save"] == "Ctrl+Alt+S"  # Overridden
        assert merged["file.open"] == "Ctrl+O"  # Default
        assert merged["edit.copy"] == "Ctrl+C"  # Default
        assert merged["custom.action"] == "Ctrl+X"  # New

    def test_merge_with_none_overrides(self):
        """Test merge when overrides is None."""
        storage = KeybindingStorage()

        defaults = {"file.save": "Ctrl+S"}
        merged = storage.merge(defaults, None)

        assert merged == defaults

    def test_reset_deletes_file(self, temp_storage_file):
        """Test that reset deletes storage file."""
        storage = KeybindingStorage(str(temp_storage_file))
        storage.save({"test": "Ctrl+T"})

        assert temp_storage_file.exists()
        assert storage.reset() is True
        assert not temp_storage_file.exists()

    def test_reset_in_memory(self):
        """Test reset with in-memory storage."""
        storage = KeybindingStorage()
        storage.save({"test": "Ctrl+T"})

        assert storage.reset() is True
        assert storage.load() == {}
