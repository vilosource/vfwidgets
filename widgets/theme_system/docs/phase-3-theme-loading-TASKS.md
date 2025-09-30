# Phase 3: Theme Management & Loading - Implementation Tasks

## Overview
This phase implements theme loading capabilities including VSCode theme import, hot reloading, and theme persistence. All tasks must follow the integration-first development approach.

## Critical Development Rules (from writing-dev-AGENTS.md)

1. **Integration-First Development**: You CANNOT proceed to the next task until the current task integrates with all previous work
2. **Examples Are Tests**: Every example created must be executed immediately to verify it works
3. **Living Example Pattern**: Maintain a `living_example.py` that grows with each task
4. **Examples vs Tests Distinction**:
   - Tests are for INTERNAL validation (can expose implementation)
   - Examples are for END USERS (only show ThemedWidget/ThemedApplication)
5. **Continuous Validation**: Previous work must keep working (zero regressions)
6. **Contract Enforcement**: Enforce protocol contracts with runtime validation

## Phase 3 Tasks

### Task 16: Theme Persistence System
**Objective**: Implement theme saving/loading to disk with validation

**Requirements**:
1. Create `ThemePersistence` class in `src/vfwidgets_theme/persistence/storage.py`
2. JSON serialization for theme data
3. Theme validation on load
4. Automatic backup before save
5. Migration support for old formats
6. Compression for large themes

**Implementation Details**:
```python
class ThemePersistence:
    """Save and load themes with validation and migration."""
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self._backup_dir = storage_dir / '.backups'

    def save_theme(self, theme: Theme, compress=False) -> Path:
        # Backup existing, validate, save
        pass

    def load_theme(self, path: Path) -> Theme:
        # Load, migrate if needed, validate
        pass
```

**Validation Criteria**:
- [ ] Themes round-trip perfectly
- [ ] Invalid themes rejected with clear errors
- [ ] Backups created before overwrite
- [ ] Migration from old formats works
- [ ] Integration with ThemedApplication
- [ ] Living example demonstrates saving/loading

### Task 17: VSCode Theme Import
**Objective**: Import VSCode color themes (.json) into our theme system

**Requirements**:
1. Create `VSCodeImporter` in `src/vfwidgets_theme/importers/vscode.py`
2. Parse VSCode theme JSON format
3. Map VSCode colors to Qt properties
4. Handle tokenColors for syntax
5. Support both dark and light themes
6. Validate imported themes

**Implementation Details**:
```python
class VSCodeImporter:
    """Import VSCode themes with intelligent mapping."""

    # VSCode to Qt color mappings
    COLOR_MAP = {
        'editor.background': 'window.background',
        'editor.foreground': 'window.foreground',
        'button.background': 'button.background',
        # ... comprehensive mappings
    }

    def import_theme(self, vscode_path: Path) -> Theme:
        # Parse, map, validate, return Theme
        pass
```

**Validation Criteria**:
- [ ] Popular VSCode themes import correctly
- [ ] Color mapping preserves theme essence
- [ ] Syntax colors handled appropriately
- [ ] Invalid themes rejected gracefully
- [ ] Integration with theme persistence
- [ ] Example imports real VSCode theme

### Task 18: Hot Reload System
**Objective**: Enable theme hot reloading during development

**Requirements**:
1. Create `HotReloader` in `src/vfwidgets_theme/development/hot_reload.py`
2. File system watcher for theme files
3. Automatic reload on change
4. Reload debouncing (avoid rapid reloads)
5. Error recovery on bad reload
6. Development mode toggle

**Implementation Details**:
```python
class HotReloader:
    """Watch and reload themes during development."""

    def __init__(self, watch_dir: Path):
        self.watcher = QFileSystemWatcher()
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)

    def watch_theme(self, theme_path: Path):
        # Add to watcher, connect signals
        pass

    @debounced(100)  # 100ms debounce
    def reload_theme(self):
        # Reload with error recovery
        pass
```

**Validation Criteria**:
- [ ] File changes trigger reload
- [ ] Debouncing prevents rapid reloads
- [ ] Errors don't crash the app
- [ ] Only active in development mode
- [ ] Integration with ThemedApplication
- [ ] Living example shows hot reload

### Task 19: Theme Factory with Builders
**Objective**: Create flexible theme construction system

**Requirements**:
1. Create `ThemeFactory` in `src/vfwidgets_theme/factory/builder.py`
2. Fluent builder API
3. Theme composition (inherit from base)
4. Theme variants (light/dark from same base)
5. Validation during construction
6. Template themes

**Implementation Details**:
```python
class ThemeFactory:
    """Factory for creating themes with builders."""

    def create_builder(self, name: str) -> ThemeBuilder:
        # Return configured builder
        pass

    def create_variant(self, base: Theme, variant: str) -> Theme:
        # Create light/dark variant from base
        pass

    def compose_themes(self, *themes: Theme) -> Theme:
        # Merge multiple themes with priority
        pass
```

**Validation Criteria**:
- [ ] Builder API is intuitive
- [ ] Composition preserves properties correctly
- [ ] Variants maintain consistency
- [ ] Validation catches errors early
- [ ] Integration with existing themes
- [ ] Example creates custom theme

### Task 20: Theme Package Manager
**Objective**: Manage theme packages with dependencies

**Requirements**:
1. Create `ThemePackageManager` in `src/vfwidgets_theme/packages/manager.py`
2. Theme package format (.vftheme)
3. Dependency resolution
4. Version management
5. Package validation
6. Import/export packages

**Implementation Details**:
```python
class ThemePackageManager:
    """Manage theme packages with dependencies."""

    def __init__(self, package_dir: Path):
        self.package_dir = package_dir
        self.installed_packages = {}

    def install_package(self, package: Path):
        # Extract, validate, resolve deps, install
        pass

    def create_package(self, theme: Theme, metadata: Dict) -> Path:
        # Package theme with metadata
        pass
```

**Validation Criteria**:
- [ ] Packages install correctly
- [ ] Dependencies resolved properly
- [ ] Version conflicts handled
- [ ] Invalid packages rejected
- [ ] Integration with ThemedApplication
- [ ] Example creates and installs package

## Integration Checkpoint Requirements

After Task 18 (mid-phase checkpoint):
1. Run all examples from Phase 3
2. Verify no regressions in Phase 0/1/2 work
3. Execute integration test suite
4. Update and run living example
5. Fix ANY issues before continuing

## Living Example for Phase 3

Create `examples/phase_3_living_example.py` that demonstrates:
```python
#!/usr/bin/env python3
"""
Phase 3 Living Example - Theme Management Features
This example grows with each task to demonstrate new capabilities.
"""

from vfwidgets_theme import ThemedApplication, ThemedWidget
from pathlib import Path

# Task 16: Theme persistence
app = ThemedApplication()
app.save_theme('my_custom', Path('themes/my_custom.json'))
app.load_theme(Path('themes/my_custom.json'))

# Task 17: VSCode import
from vfwidgets_theme.importers import VSCodeImporter
importer = VSCodeImporter()
theme = importer.import_theme(Path('monokai.json'))
app.register_theme('monokai', theme)

# Task 18: Hot reload (development mode)
app.enable_hot_reload(Path('themes/'))
# Edit themes/my_theme.json and see changes live!

# Task 19: Theme factory
from vfwidgets_theme.factory import ThemeFactory
factory = ThemeFactory()
custom = (factory.create_builder('custom')
    .set_color('window.background', '#1e1e1e')
    .set_color('window.foreground', '#ffffff')
    .build())

# Task 20: Package management
from vfwidgets_theme.packages import ThemePackageManager
manager = ThemePackageManager(Path('packages/'))
manager.install_package(Path('dark-themes.vftheme'))
```

## Test Organization

All internal tests go in `tests/phase_3/`:
- `test_persistence.py` - Task 16 internals
- `test_vscode_import.py` - Task 17 internals
- `test_hot_reload.py` - Task 18 internals
- `test_factory.py` - Task 19 internals
- `test_packages.py` - Task 20 internals
- `test_phase_3_integration.py` - Full integration test

## Performance Requirements

- Theme loading: <50ms for typical theme
- VSCode import: <100ms per theme
- Hot reload: <200ms from file change to UI update
- Package installation: <500ms for typical package
- Factory creation: <10ms per theme

## Success Criteria for Phase 3

Phase 3 is complete when:
1. ✅ All 5 tasks implemented and tested
2. ✅ Living example runs all features
3. ✅ Integration tests pass
4. ✅ No regressions in Phase 0/1/2
5. ✅ Performance benchmarks met
6. ✅ VSCode themes import successfully
7. ✅ Hot reload works in development
8. ✅ Documentation complete

## Notes for Agent

- Remember: Integration > Isolation
- Test every example immediately
- Update living example with each task
- VSCode import is critical - test with real themes
- Hot reload must not affect production
- Package format should be extensible
- If integration fails, STOP and fix before proceeding