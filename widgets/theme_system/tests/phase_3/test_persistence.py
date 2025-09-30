#!/usr/bin/env python3
"""
Test Suite for Task 16: Theme Persistence System

Tests for theme saving/loading with validation, backups, migration, and compression.
"""

import pytest
import json
import gzip
import tempfile
import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Import the code under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vfwidgets_theme.persistence.storage import (
    ThemePersistence,
    ThemeValidationResult,
    PersistenceError,
    ThemeFormatError,
    BackupManager,
    ThemeMigrator,
    ThemeValidator
)
from vfwidgets_theme.core.theme import Theme


class TestThemeValidator:
    """Test theme validation functionality."""

    def test_valid_theme_passes_validation(self):
        """Test that valid theme data passes validation."""
        theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'properties': {
                'window.background': '#ffffff',
                'window.foreground': '#000000'
            },
            'description': 'A test theme',
            'author': 'Test Author'
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert result.is_valid
        assert not result.has_errors
        # Note: We expect a warning about missing created_at field
        # This is expected behavior for the validator

    def test_missing_required_fields_fail_validation(self):
        """Test that missing required fields cause validation failure."""
        theme_data = {
            'name': 'Test Theme'
            # Missing version and properties
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert not result.is_valid
        assert result.has_errors
        assert 'Missing required field: version' in result.errors
        assert 'Missing required field: properties' in result.errors

    def test_missing_recommended_fields_generate_warnings(self):
        """Test that missing recommended fields generate warnings."""
        theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'properties': {}
            # Missing description and author
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert result.is_valid  # Still valid, just warnings
        assert not result.has_errors
        assert result.has_warnings
        assert 'Missing recommended field: description' in result.warnings
        assert 'Missing recommended field: author' in result.warnings

    def test_invalid_properties_type_fails_validation(self):
        """Test that invalid properties type fails validation."""
        theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'properties': 'not a dict'  # Should be dict
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert not result.is_valid
        assert result.has_errors
        assert 'Properties must be a dictionary' in result.errors

    def test_invalid_version_type_fails_validation(self):
        """Test that invalid version type fails validation."""
        theme_data = {
            'name': 'Test Theme',
            'version': 123,  # Should be string
            'properties': {}
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert not result.is_valid
        assert result.has_errors
        assert 'Version must be a string' in result.errors

    def test_unknown_fields_generate_warnings(self):
        """Test that unknown fields generate warnings."""
        theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'properties': {},
            'unknown_field': 'value',  # Unknown field
            'typo_descriptin': 'value'  # Possible typo
        }

        result = ThemeValidator.validate_theme(theme_data)

        assert result.is_valid
        assert result.has_warnings
        assert any('unknown_field' in w for w in result.warnings)
        assert any('typo_descriptin' in w for w in result.warnings)


class TestThemeMigrator:
    """Test theme migration functionality."""

    def test_current_version_theme_no_migration(self):
        """Test that current version themes don't need migration."""
        theme_data = {
            'version': '1.0.0',
            'name': 'Test Theme',
            'properties': {}
        }

        migrated = ThemeMigrator.migrate_theme(theme_data)

        assert migrated == theme_data  # Should be unchanged

    def test_v09_theme_migration(self):
        """Test migration from v0.9 format."""
        old_theme_data = {
            'version': '0.9',
            'name': 'Old Theme',
            'properties': {
                'window.background': '#ffffff'
            }
        }

        migrated = ThemeMigrator.migrate_theme(old_theme_data)

        assert migrated['version'] == '1.0.0'
        assert migrated['name'] == 'Old Theme'
        assert migrated['properties'] == old_theme_data['properties']
        assert 'migration_info' in migrated
        assert migrated['migration_info']['original_version'] == '0.9'

    def test_unknown_format_migration(self):
        """Test best-effort migration from unknown format."""
        unknown_data = {
            'colors': {
                'background': '#ffffff',
                'text': '#000000'
            },
            'fonts': {
                'default': 'Arial'
            }
        }

        migrated = ThemeMigrator.migrate_theme(unknown_data)

        assert migrated['version'] == '1.0.0'
        assert migrated['name'] == 'Unknown Format Theme'
        assert 'color.background' in migrated['properties']
        assert 'color.text' in migrated['properties']
        assert 'font.default' in migrated['properties']
        assert 'migration_info' in migrated
        assert migrated['migration_info']['original_version'] == 'unknown'

    def test_unsupported_version_raises_error(self):
        """Test that unsupported versions raise error."""
        theme_data = {
            'version': '999.0',
            'name': 'Future Theme'
        }

        with pytest.raises(ThemeFormatError, match="Unsupported theme version"):
            ThemeMigrator.migrate_theme(theme_data)

    def test_detect_version_legacy(self):
        """Test version detection for legacy formats."""
        legacy_data = {
            'properties': {}  # No version field, but has properties
        }

        version = ThemeMigrator.detect_version(legacy_data)
        assert version == '0.9'

    def test_detect_version_unknown(self):
        """Test version detection for unknown formats."""
        unknown_data = {
            'some_field': 'value'
        }

        version = ThemeMigrator.detect_version(unknown_data)
        assert version == 'unknown'


class TestBackupManager:
    """Test backup management functionality."""

    def test_create_backup_success(self):
        """Test successful backup creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            original_file = temp_dir / 'theme.json'
            backup_dir = temp_dir / 'backups'

            # Create original file
            original_file.write_text('{"test": "data"}')

            backup_manager = BackupManager(backup_dir, max_backups=5)
            backup_path = backup_manager.create_backup(original_file)

            assert backup_path is not None
            assert backup_path.exists()
            assert backup_path.parent == backup_dir
            assert 'theme_' in backup_path.name
            assert backup_path.name.endswith('.bak')

    def test_create_backup_nonexistent_file(self):
        """Test backup creation for non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            nonexistent_file = temp_dir / 'nonexistent.json'
            backup_dir = temp_dir / 'backups'

            backup_manager = BackupManager(backup_dir)
            backup_path = backup_manager.create_backup(nonexistent_file)

            assert backup_path is None

    def test_backup_rotation(self):
        """Test that old backups are rotated out."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            original_file = temp_dir / 'theme.json'
            backup_dir = temp_dir / 'backups'

            # Create original file
            original_file.write_text('{"test": "data"}')

            backup_manager = BackupManager(backup_dir, max_backups=3)

            # Create more backups than the limit
            backup_paths = []
            for i in range(5):
                backup_path = backup_manager.create_backup(original_file)
                backup_paths.append(backup_path)
                # Small delay to ensure different timestamps
                import time
                time.sleep(0.001)

            # Should only have max_backups files
            remaining_backups = backup_manager.list_backups('theme')
            assert len(remaining_backups) <= 3  # Should be max_backups or less

    def test_list_backups(self):
        """Test listing backups for a theme."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            original_file = temp_dir / 'theme.json'
            backup_dir = temp_dir / 'backups'

            original_file.write_text('{"test": "data"}')
            backup_manager = BackupManager(backup_dir)

            # Create multiple backups
            backup_manager.create_backup(original_file)
            import time
            time.sleep(0.001)  # Ensure different timestamps
            backup_manager.create_backup(original_file)

            backups = backup_manager.list_backups('theme')
            assert len(backups) >= 1  # Should have at least one backup
            assert all(b.name.startswith('theme_') and b.name.endswith('.bak') for b in backups)

    def test_restore_backup(self):
        """Test restoring a backup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            original_file = temp_dir / 'theme.json'
            target_file = temp_dir / 'restored.json'
            backup_dir = temp_dir / 'backups'

            # Create original file and backup
            original_content = '{"original": "data"}'
            original_file.write_text(original_content)

            backup_manager = BackupManager(backup_dir)
            backup_path = backup_manager.create_backup(original_file)

            # Restore backup to new location
            success = backup_manager.restore_backup(backup_path, target_file)

            assert success
            assert target_file.exists()
            assert target_file.read_text() == original_content


class TestThemePersistence:
    """Test theme persistence functionality."""

    def test_save_and_load_theme_success(self):
        """Test successful theme save and load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create test theme
            theme = Theme(
                name='Test Theme',
                colors={
                    'window.background': '#ffffff',
                    'window.foreground': '#000000'
                }
            )

            # Save theme
            saved_path = persistence.save_theme(theme)

            assert saved_path.exists()
            assert saved_path.name == 'test_theme.json'

            # Load theme
            loaded_theme = persistence.load_theme(saved_path)

            assert loaded_theme.name == theme.name
            assert loaded_theme.colors['window.background'] == '#ffffff'
            assert loaded_theme.colors['window.foreground'] == '#000000'

    def test_save_compressed_theme(self):
        """Test saving compressed theme."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            theme = Theme(
                name='Compressed Theme',
                styles={'test.property': 'value'}
            )

            # Save compressed
            saved_path = persistence.save_theme(theme, compress=True)

            assert saved_path.exists()
            assert saved_path.name.endswith('.json.gz')

            # Verify it's compressed
            with gzip.open(saved_path, 'rt') as f:
                data = json.load(f)
                assert data['name'] == 'Compressed Theme'

            # Load compressed theme
            loaded_theme = persistence.load_theme(saved_path)
            assert loaded_theme.name == 'Compressed Theme'

    def test_backup_creation_on_overwrite(self):
        """Test that backup is created when overwriting existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            theme1 = Theme(name='Theme', styles={'prop1': 'value1'})
            theme2 = Theme(name='Theme', styles={'prop2': 'value2'})

            # Save first theme
            saved_path = persistence.save_theme(theme1, filename='theme.json')

            # Save second theme with same filename (should create backup)
            persistence.save_theme(theme2, filename='theme.json')

            # Check backup was created
            backups = persistence.backup_manager.list_backups('theme')
            assert len(backups) >= 1

            # Verify current file has new content
            current_theme = persistence.load_theme(saved_path)
            assert 'prop2' in current_theme.styles

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            with pytest.raises(PersistenceError, match="Theme file not found"):
                persistence.load_theme(storage_dir / 'nonexistent.json')

    def test_save_invalid_theme_raises_error(self):
        """Test that saving invalid theme raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Mock an invalid theme - but we need to be careful since Theme has validation
            # Let's create a theme with invalid data and patch the serialization method to fail
            theme = Theme(name="Test Theme")

            # Patch _serialize_theme to raise an error to simulate invalid theme
            def failing_serialize(self, theme):
                raise ValueError("Invalid theme data")

            original_serialize = persistence._serialize_theme
            persistence._serialize_theme = lambda theme: failing_serialize(persistence, theme)

            try:
                with pytest.raises(PersistenceError):
                    persistence.save_theme(theme)
            finally:
                # Restore original method
                persistence._serialize_theme = original_serialize

    def test_load_corrupted_file_raises_error(self):
        """Test that loading corrupted file raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create corrupted JSON file
            corrupted_file = storage_dir / 'corrupted.json'
            storage_dir.mkdir(parents=True, exist_ok=True)
            corrupted_file.write_text('{"invalid": json syntax}')

            with pytest.raises(ThemeFormatError, match="Invalid theme file format"):
                persistence.load_theme(corrupted_file)

    def test_list_themes(self):
        """Test listing available theme files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create multiple themes
            theme1 = Theme(name='Theme 1')
            theme2 = Theme(name='Theme 2')

            persistence.save_theme(theme1, 'theme1.json')
            persistence.save_theme(theme2, 'theme2.json', compress=True)

            # List themes
            themes = persistence.list_themes()

            assert len(themes) == 2
            theme_names = [t.name for t in themes]
            assert 'theme1.json' in theme_names
            assert 'theme2.json.gz' in theme_names

    def test_get_theme_info(self):
        """Test getting theme metadata without full loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            theme = Theme(name='Info Test', styles={'test': 'value'})
            saved_path = persistence.save_theme(theme)

            info = persistence.get_theme_info(saved_path)

            assert info['name'] == 'Info Test'
            assert info['version'] == '1.0.0'
            assert info['file_size'] > 0
            assert not info['compressed']

    def test_migration_during_load(self):
        """Test that old themes are migrated during load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create old format theme file
            old_theme_data = {
                'version': '0.9',
                'name': 'Old Theme',
                'properties': {'old.property': 'value'}
            }

            old_file = storage_dir / 'old_theme.json'
            storage_dir.mkdir(parents=True, exist_ok=True)
            with open(old_file, 'w') as f:
                json.dump(old_theme_data, f)

            # Load theme (should migrate)
            loaded_theme = persistence.load_theme(old_file)

            assert loaded_theme.name == 'Old Theme'
            # Check that property was migrated (should be in colors or styles based on heuristic)
            assert ('old.property' in loaded_theme.colors or
                    'old.property' in loaded_theme.styles)


class TestPerformanceRequirements:
    """Test performance requirements for persistence operations."""

    def test_theme_loading_performance(self):
        """Test that theme loading meets <50ms requirement."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create typical theme
            colors = {f'color.{i}': f'#ff00{i:02x}' for i in range(50)}
            styles = {f'property.{i}': f'value_{i}' for i in range(50)}
            theme = Theme(name='Performance Test', colors=colors, styles=styles)
            saved_path = persistence.save_theme(theme)

            # Measure loading time
            import time
            start_time = time.perf_counter()

            for _ in range(10):  # Multiple loads for average
                persistence.load_theme(saved_path)

            end_time = time.perf_counter()
            avg_time_ms = (end_time - start_time) * 1000 / 10

            assert avg_time_ms < 50, f"Theme loading took {avg_time_ms:.2f}ms, requirement is <50ms"

    def test_theme_saving_performance(self):
        """Test theme saving performance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir) / 'themes'
            persistence = ThemePersistence(storage_dir)

            # Create typical theme
            colors = {f'color.{i}': f'#ff00{i:02x}' for i in range(50)}
            styles = {f'property.{i}': f'value_{i}' for i in range(50)}
            theme = Theme(name='Save Performance Test', colors=colors, styles=styles)

            # Measure saving time
            import time
            start_time = time.perf_counter()

            for i in range(10):
                persistence.save_theme(theme, f'perf_test_{i}.json')

            end_time = time.perf_counter()
            avg_time_ms = (end_time - start_time) * 1000 / 10

            # Saving should be reasonably fast (not specified, but < 100ms is reasonable)
            assert avg_time_ms < 100, f"Theme saving took {avg_time_ms:.2f}ms"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])