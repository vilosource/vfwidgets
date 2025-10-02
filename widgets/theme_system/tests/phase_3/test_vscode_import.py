#!/usr/bin/env python3
"""
Test Suite for Task 17: VSCode Theme Import

Tests for VSCode theme import with color mapping, tokenColors handling, and validation.
"""

import json
import os

# Import the code under test
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vfwidgets_theme.importers.vscode import (
    TokenColorMapper,
    VSCodeColorMapper,
    VSCodeImporter,
    VSCodeImportError,
    VSCodeThemeInfo,
)


class TestVSCodeColorMapper:
    """Test VSCode color mapping functionality."""

    def test_basic_color_mapping(self):
        """Test basic color mapping from VSCode to Qt."""
        mapper = VSCodeColorMapper()

        vscode_colors = {
            'editor.background': '#1e1e1e',
            'editor.foreground': '#d4d4d4',
            'button.background': '#0e639c',
            'unknown.color': '#123456'  # Should not be mapped
        }

        mapped = mapper.map_colors(vscode_colors)

        # Check mapped colors
        assert mapped['window.background'] == '#1e1e1e'
        assert mapped['window.foreground'] == '#d4d4d4'
        assert mapped['button.background'] == '#0e639c'

        # Unknown color should not be in mapped colors
        assert 'unknown.color' not in mapped
        assert 'vscode.unknown.color' not in mapped

    def test_color_mapping_with_unmapped_included(self):
        """Test color mapping when including unmapped colors."""
        mapper = VSCodeColorMapper(include_unmapped=True)

        vscode_colors = {
            'editor.background': '#1e1e1e',
            'unknown.color': '#123456',
            'custom.border': '#ff0000'
        }

        mapped = mapper.map_colors(vscode_colors)

        # Check mapped colors
        assert mapped['window.background'] == '#1e1e1e'

        # Check unmapped colors are included with vscode prefix
        assert mapped['vscode.unknown.color'] == '#123456'
        assert mapped['vscode.custom.border'] == '#ff0000'

        # Check unmapped colors are tracked
        unmapped = mapper.get_unmapped_colors()
        assert 'unknown.color' in unmapped
        assert 'custom.border' in unmapped

    def test_fallback_pattern_matching(self):
        """Test fallback pattern matching for unmapped colors."""
        mapper = VSCodeColorMapper(include_unmapped=True)

        vscode_colors = {
            'customWidget.background': '#123456',
            'myEditor.foreground': '#654321',
            'toolTip.border': '#abcdef'
        }

        mapped = mapper.map_colors(vscode_colors)

        # These should be mapped using fallback patterns
        assert 'custom.widget.background' in mapped or 'vscode.customWidget.background' in mapped
        assert 'my.editor.foreground' in mapped or 'vscode.myEditor.foreground' in mapped

    def test_comprehensive_color_mapping(self):
        """Test mapping of comprehensive VSCode color set."""
        mapper = VSCodeColorMapper()

        # Create comprehensive VSCode theme colors
        vscode_colors = {
            # Editor
            'editor.background': '#1e1e1e',
            'editor.foreground': '#d4d4d4',
            'editorCursor.foreground': '#ffffff',

            # UI
            'foreground': '#cccccc',
            'focusBorder': '#007acc',

            # Button
            'button.background': '#0e639c',
            'button.foreground': '#ffffff',
            'button.hoverBackground': '#1177bb',

            # Terminal
            'terminal.ansiRed': '#cd3131',
            'terminal.ansiGreen': '#0dbc79',
            'terminal.ansiBlue': '#2472c8',

            # Activity bar
            'activityBar.background': '#333333',
            'activityBarBadge.background': '#007acc',

            # Status bar
            'statusBar.background': '#007acc',
            'statusBar.foreground': '#ffffff',
        }

        mapped = mapper.map_colors(vscode_colors)

        # Verify key mappings
        expected_mappings = [
            ('editor.background', 'window.background'),
            ('editor.foreground', 'window.foreground'),
            ('button.background', 'button.background'),
            ('terminal.ansiRed', 'terminal.ansi.red'),
            ('activityBar.background', 'activitybar.background'),
            ('statusBar.background', 'statusbar.background'),
        ]

        for vscode_key, expected_qt_key in expected_mappings:
            assert expected_qt_key in mapped
            assert mapped[expected_qt_key] == vscode_colors[vscode_key]


class TestTokenColorMapper:
    """Test VSCode token color mapping functionality."""

    def test_basic_token_color_mapping(self):
        """Test basic token color mapping."""
        mapper = TokenColorMapper()

        vscode_tokens = [
            {
                'name': 'Comments',
                'scope': 'comment',
                'settings': {
                    'foreground': '#6A9955',
                    'fontStyle': 'italic'
                }
            },
            {
                'name': 'Keywords',
                'scope': ['keyword', 'storage.type'],
                'settings': {
                    'foreground': '#569CD6'
                }
            }
        ]

        mapped = mapper.map_token_colors(vscode_tokens)

        # Check first token (single scope)
        assert len(mapped) >= 1
        comment_token = next((t for t in mapped if t['scope'] == 'comment'), None)
        assert comment_token is not None
        assert comment_token['settings']['foreground'] == '#6A9955'
        assert comment_token['settings']['fontStyle'] == 'italic'
        assert comment_token['name'] == 'Comments'

        # Check second token (multiple scopes - should create multiple tokens)
        keyword_tokens = [t for t in mapped if t['scope'] in ['keyword', 'storage.type']]
        assert len(keyword_tokens) == 2

        for token in keyword_tokens:
            assert token['settings']['foreground'] == '#569CD6'
            assert token['name'] == 'Keywords'

    def test_token_color_validation(self):
        """Test that invalid token colors are filtered out."""
        mapper = TokenColorMapper()

        vscode_tokens = [
            # Valid token
            {
                'name': 'Valid',
                'scope': 'valid.scope',
                'settings': {'foreground': '#ffffff'}
            },
            # Invalid tokens
            {
                'name': 'No scope'
                # Missing scope
            },
            {
                'scope': 'no.settings'
                # Missing settings
            },
            {
                'scope': 'empty.settings',
                'settings': {}  # Empty settings
            },
            'invalid_format',  # Not a dict
            {
                'scope': None,  # Invalid scope type
                'settings': {'foreground': '#000000'}
            }
        ]

        mapped = mapper.map_token_colors(vscode_tokens)

        # Should only have the valid token
        assert len(mapped) == 1
        assert mapped[0]['scope'] == 'valid.scope'
        assert mapped[0]['settings']['foreground'] == '#ffffff'

    def test_scope_normalization(self):
        """Test scope normalization (string vs list)."""
        mapper = TokenColorMapper()

        vscode_tokens = [
            {
                'scope': 'single.scope',
                'settings': {'foreground': '#111111'}
            },
            {
                'scope': ['multiple', 'scopes'],
                'settings': {'foreground': '#222222'}
            },
            {
                'scope': ' whitespace.scope ',  # With whitespace
                'settings': {'foreground': '#333333'}
            }
        ]

        mapped = mapper.map_token_colors(vscode_tokens)

        # Check single scope
        single_token = next((t for t in mapped if t['scope'] == 'single.scope'), None)
        assert single_token is not None

        # Check multiple scopes
        multiple_tokens = [t for t in mapped if t['scope'] in ['multiple', 'scopes']]
        assert len(multiple_tokens) == 2

        # Check whitespace handling
        whitespace_token = next((t for t in mapped if t['scope'] == 'whitespace.scope'), None)
        assert whitespace_token is not None


class TestVSCodeThemeInfo:
    """Test VSCode theme info extraction."""

    def test_theme_info_creation(self):
        """Test creating theme info from data."""
        info = VSCodeThemeInfo(
            name='Test Theme',
            type='dark',
            description='A test theme',
            author='Test Author',
            version='1.0.0'
        )

        assert info.name == 'Test Theme'
        assert info.type == 'dark'
        assert info.description == 'A test theme'
        assert info.author == 'Test Author'
        assert info.version == '1.0.0'


class TestVSCodeImporter:
    """Test VSCode theme import functionality."""

    def create_sample_vscode_theme(self) -> dict:
        """Create a sample VSCode theme for testing."""
        return {
            'name': 'Sample Dark Theme',
            'type': 'dark',
            'author': 'Test Author',
            'description': 'A sample dark theme for testing',
            'colors': {
                'editor.background': '#1e1e1e',
                'editor.foreground': '#d4d4d4',
                'button.background': '#0e639c',
                'button.foreground': '#ffffff',
                'activityBar.background': '#333333',
                'statusBar.background': '#007acc',
                'terminal.ansiRed': '#cd3131',
                'terminal.ansiGreen': '#0dbc79'
            },
            'tokenColors': [
                {
                    'name': 'Comments',
                    'scope': 'comment',
                    'settings': {
                        'foreground': '#6A9955',
                        'fontStyle': 'italic'
                    }
                },
                {
                    'name': 'Keywords',
                    'scope': ['keyword', 'storage.type'],
                    'settings': {
                        'foreground': '#569CD6'
                    }
                },
                {
                    'name': 'Strings',
                    'scope': 'string',
                    'settings': {
                        'foreground': '#CE9178'
                    }
                }
            ]
        }

    def test_import_from_data_success(self):
        """Test successful import from VSCode theme data."""
        importer = VSCodeImporter()
        vscode_data = self.create_sample_vscode_theme()

        theme = importer.import_from_data(vscode_data)

        # Check basic theme properties
        assert theme.name == 'Sample Dark Theme'
        assert theme.type == 'dark'
        assert theme.version == '1.0.0'

        # Check colors were mapped
        assert len(theme.colors) > 0
        assert theme.colors['window.background'] == '#1e1e1e'
        assert theme.colors['window.foreground'] == '#d4d4d4'
        assert theme.colors['button.background'] == '#0e639c'

        # Check token colors were mapped
        assert len(theme.token_colors) >= 4  # Should have at least 4 tokens (keywords split)

        # Find comment token
        comment_token = next((t for t in theme.token_colors if t['scope'] == 'comment'), None)
        assert comment_token is not None
        assert comment_token['settings']['foreground'] == '#6A9955'

        # Check metadata
        assert theme.metadata['author'] == 'Test Author'
        assert theme.metadata['imported_from'] == 'vscode'

    def test_import_from_file_success(self):
        """Test successful import from VSCode theme file."""
        importer = VSCodeImporter()
        vscode_data = self.create_sample_vscode_theme()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(vscode_data, f)
            temp_path = Path(f.name)

        try:
            theme = importer.import_theme(temp_path)

            assert theme.name == 'Sample Dark Theme'
            assert theme.type == 'dark'
            assert len(theme.colors) > 0
            assert len(theme.token_colors) >= 4

        finally:
            temp_path.unlink()

    def test_import_nonexistent_file_raises_error(self):
        """Test that importing non-existent file raises error."""
        importer = VSCodeImporter()
        nonexistent_path = Path('/nonexistent/theme.json')

        with pytest.raises(VSCodeImportError, match="VSCode theme file not found"):
            importer.import_theme(nonexistent_path)

    def test_import_invalid_json_raises_error(self):
        """Test that importing invalid JSON raises error."""
        importer = VSCodeImporter()

        # Create file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json syntax}')
            temp_path = Path(f.name)

        try:
            with pytest.raises(VSCodeImportError, match="Invalid JSON"):
                importer.import_theme(temp_path)
        finally:
            temp_path.unlink()

    def test_import_with_theme_name_override(self):
        """Test importing with custom theme name."""
        importer = VSCodeImporter()
        vscode_data = self.create_sample_vscode_theme()

        theme = importer.import_from_data(vscode_data, theme_name='Custom Name')

        assert theme.name == 'Custom Name'  # Should use override
        assert theme.metadata['author'] == 'Test Author'  # Other properties preserved

    def test_theme_type_inference(self):
        """Test theme type inference from background color."""
        importer = VSCodeImporter()

        # Test dark theme inference
        dark_data = {
            'name': 'Dark Theme',
            'colors': {'editor.background': '#1e1e1e'}  # Dark background
        }
        dark_theme = importer.import_from_data(dark_data)
        assert dark_theme.type == 'dark'

        # Test light theme inference
        light_data = {
            'name': 'Light Theme',
            'colors': {'editor.background': '#ffffff'}  # Light background
        }
        light_theme = importer.import_from_data(light_data)
        assert light_theme.type == 'light'

        # Test explicit type override
        explicit_data = {
            'name': 'Explicit Theme',
            'type': 'light',
            'colors': {'editor.background': '#000000'}  # Dark bg but explicit light type
        }
        explicit_theme = importer.import_from_data(explicit_data)
        assert explicit_theme.type == 'light'

    def test_high_contrast_theme_handling(self):
        """Test handling of high contrast themes."""
        importer = VSCodeImporter()

        hc_data = {
            'name': 'High Contrast Theme',
            'type': 'hc',
            'colors': {'editor.background': '#000000'}
        }

        theme = importer.import_from_data(hc_data)
        assert theme.type == 'high-contrast'

    def test_import_with_unmapped_colors(self):
        """Test import with unmapped colors included."""
        importer = VSCodeImporter(include_unmapped_colors=True)

        vscode_data = {
            'name': 'Test Theme',
            'colors': {
                'editor.background': '#1e1e1e',  # Mapped
                'custom.unknown.color': '#123456',  # Unmapped
                'myExtension.border': '#ff0000'  # Unmapped
            }
        }

        theme = importer.import_from_data(vscode_data)

        # Check mapped color
        assert theme.colors['window.background'] == '#1e1e1e'

        # Check unmapped colors are included
        assert 'vscode.custom.unknown.color' in theme.colors
        assert theme.colors['vscode.custom.unknown.color'] == '#123456'

        # Check unmapped colors are tracked in metadata
        assert 'unmapped_colors' in theme.metadata
        assert 'custom.unknown.color' in theme.metadata['unmapped_colors']

    def test_import_summary(self):
        """Test getting import summary information."""
        importer = VSCodeImporter(include_unmapped_colors=True)

        vscode_data = {
            'name': 'Test Theme',
            'colors': {
                'editor.background': '#1e1e1e',
                'unknown.color': '#123456'
            }
        }

        importer.import_from_data(vscode_data)
        summary = importer.get_import_summary()

        assert 'mapped_colors' in summary
        assert 'unmapped_colors' in summary
        assert 'fallback_patterns' in summary
        assert summary['mapped_colors'] > 0
        assert summary['fallback_patterns'] > 0

    def test_minimal_theme_import(self):
        """Test importing minimal VSCode theme."""
        importer = VSCodeImporter()

        minimal_data = {
            'name': 'Minimal Theme'
            # No colors, no tokenColors - should still work
        }

        theme = importer.import_from_data(minimal_data)

        assert theme.name == 'Minimal Theme'
        assert theme.type == 'dark'  # Default
        assert len(theme.colors) == 0
        assert len(theme.token_colors) == 0
        assert theme.metadata['imported_from'] == 'vscode'


class TestPerformanceRequirements:
    """Test performance requirements for VSCode import."""

    def test_vscode_import_performance(self):
        """Test that VSCode import meets <100ms requirement."""
        importer = VSCodeImporter()

        # Create large VSCode theme
        large_vscode_data = {
            'name': 'Large Theme',
            'type': 'dark',
            'colors': {f'custom.color.{i}': f'#ff{i:04x}' for i in range(200)},
            'tokenColors': [
                {
                    'name': f'Token {i}',
                    'scope': f'token.{i}',
                    'settings': {'foreground': f'#00{i:04x}'}
                } for i in range(100)
            ]
        }

        # Measure import time
        import time
        start_time = time.perf_counter()

        for _ in range(5):  # Multiple imports for average
            importer.import_from_data(large_vscode_data)

        end_time = time.perf_counter()
        avg_time_ms = (end_time - start_time) * 1000 / 5

        assert avg_time_ms < 100, f"VSCode import took {avg_time_ms:.2f}ms, requirement is <100ms"

    def test_color_mapping_performance(self):
        """Test color mapping performance."""
        mapper = VSCodeColorMapper()

        # Create large color set
        large_colors = {f'custom.color.{i}': f'#ff{i:04x}' for i in range(1000)}

        # Measure mapping time
        import time
        start_time = time.perf_counter()

        for _ in range(10):
            mapper.map_colors(large_colors)

        end_time = time.perf_counter()
        avg_time_ms = (end_time - start_time) * 1000 / 10

        # Should be very fast (sub-millisecond for 1000 colors)
        assert avg_time_ms < 50, f"Color mapping took {avg_time_ms:.2f}ms for 1000 colors"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
