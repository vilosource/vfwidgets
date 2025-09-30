# Phase 6: VSCode & Extensions - Implementation Tasks

## Overview
This phase completes VSCode integration and implements the extension system for the theme framework. Focus is on real VSCode compatibility and plugin architecture.

## Critical Development Rules (from writing-dev-AGENTS.md)

1. **Integration-First Development**: You CANNOT proceed to the next task until the current task integrates with all previous work
2. **VSCode Compatibility**: Must work with actual VSCode theme files
3. **Extension Safety**: Plugins must be sandboxed and validated
4. **Performance**: Extensions cannot degrade core performance
5. **Documentation**: Extension API must be well-documented
6. **Backward Compatibility**: Extensions must not break existing code

## Phase 6 Tasks

### Task 34: VSCode Theme Marketplace Integration
**Objective**: Download and import themes directly from VSCode marketplace

**Requirements**:
1. Create `MarketplaceClient` in `src/vfwidgets_theme/vscode/marketplace.py`
2. Search VSCode marketplace API
3. Download theme extensions
4. Extract and import themes
5. Cache downloaded themes
6. Handle extension updates

**Implementation Details**:
```python
class MarketplaceClient:
    """VSCode marketplace integration for theme downloads."""

    MARKETPLACE_API = "https://marketplace.visualstudio.com/_apis/public/gallery"

    async def search_themes(self, query: str) -> List[ThemeExtension]:
        # Search marketplace for themes
        pass

    async def download_theme(self, extension_id: str) -> Path:
        # Download and cache theme
        pass

    def import_from_extension(self, extension_path: Path) -> List[Theme]:
        # Extract themes from extension
        pass
```

**Validation Criteria**:
- [ ] Marketplace search works
- [ ] Popular themes download correctly
- [ ] Themes import successfully
- [ ] Caching reduces downloads
- [ ] Updates handled gracefully
- [ ] Integration with ThemedApplication

### Task 35: Theme Extension System
**Objective**: Plugin system for extending theme capabilities

**Requirements**:
1. Create `ExtensionSystem` in `src/vfwidgets_theme/extensions/system.py`
2. Extension discovery and loading
3. Sandboxed execution
4. Extension API
5. Dependency management
6. Hot reload support

**Implementation Details**:
```python
class ExtensionSystem:
    """Secure plugin system for theme extensions."""

    def __init__(self):
        self.extensions = {}
        self.sandbox = ExtensionSandbox()

    def load_extension(self, path: Path) -> Extension:
        # Load and validate extension
        pass

    def register_api(self, api: ExtensionAPI):
        # Register safe API for extensions
        pass

    @sandboxed
    def execute_extension(self, extension: Extension, method: str, *args):
        # Execute in sandbox
        pass
```

**Validation Criteria**:
- [ ] Extensions load safely
- [ ] Sandbox prevents malicious code
- [ ] API provides needed functionality
- [ ] Dependencies resolved
- [ ] Hot reload works
- [ ] Performance maintained

### Task 36: Icon Theme Support
**Objective**: Support VSCode icon themes for file trees

**Requirements**:
1. Create `IconTheme` in `src/vfwidgets_theme/icons/theme.py`
2. Parse VSCode icon theme format
3. Icon font loading
4. SVG icon support
5. File association mapping
6. Fallback icons

**Implementation Details**:
```python
class IconTheme:
    """VSCode-compatible icon theme support."""

    def __init__(self, theme_path: Path):
        self.icons = {}
        self.associations = {}

    def get_icon(self, file_path: Path) -> QIcon:
        # Return icon for file type
        pass

    def load_icon_font(self, font_path: Path):
        # Load icon font
        pass
```

**Validation Criteria**:
- [ ] VSCode icon themes work
- [ ] File associations correct
- [ ] SVG icons render properly
- [ ] Font icons display correctly
- [ ] Fallbacks work
- [ ] Performance acceptable

### Task 37: Syntax Highlighting Engine
**Objective**: TextMate grammar support for code highlighting

**Requirements**:
1. Create `SyntaxHighlighter` in `src/vfwidgets_theme/syntax/highlighter.py`
2. TextMate grammar parsing
3. Token colorization
4. Language detection
5. Theme integration
6. Performance optimization

**Implementation Details**:
```python
class SyntaxHighlighter:
    """TextMate grammar-based syntax highlighting."""

    def __init__(self, theme: Theme):
        self.theme = theme
        self.grammars = {}

    def load_grammar(self, language: str, grammar_path: Path):
        # Load TextMate grammar
        pass

    def highlight(self, text: str, language: str) -> List[Token]:
        # Tokenize and colorize
        pass
```

**Validation Criteria**:
- [ ] TextMate grammars parse
- [ ] Tokenization accurate
- [ ] Colors from theme applied
- [ ] Performance acceptable
- [ ] Language detection works
- [ ] Integration with code widgets

## Integration Requirements

After Task 35 (mid-phase checkpoint):
1. Test extension system security
2. Verify sandbox containment
3. Check performance impact
4. Run integration tests
5. Fix any issues before continuing

## Living Example for Phase 6

Create `examples/phase_6_living_example.py`:
```python
#!/usr/bin/env python3
"""
Phase 6 Living Example - VSCode Integration & Extensions
"""

from vfwidgets_theme import ThemedApplication
from vfwidgets_theme.vscode import MarketplaceClient
from vfwidgets_theme.extensions import ExtensionSystem
from vfwidgets_theme.icons import IconTheme
from vfwidgets_theme.syntax import SyntaxHighlighter

# Task 34: Marketplace integration
async def download_popular_themes():
    client = MarketplaceClient()
    themes = await client.search_themes("popular dark")
    for theme in themes[:5]:
        await client.download_theme(theme.id)

# Task 35: Extension system
extension_system = ExtensionSystem()
extension_system.load_extension("extensions/my_extension.py")

# Task 36: Icon themes
icon_theme = IconTheme("vscode-icons.json")
file_icon = icon_theme.get_icon("main.py")

# Task 37: Syntax highlighting
highlighter = SyntaxHighlighter(app.current_theme)
highlighter.load_grammar("python", "python.tmLanguage.json")
tokens = highlighter.highlight(code_text, "python")
```

## Test Organization

- `tests/vscode/` - VSCode integration tests
- `tests/extensions/` - Extension system tests
- `tests/security/` - Sandbox security tests
- `tests/phase_6_integration.py` - Integration tests

## Performance Requirements

- Marketplace search: <2 seconds
- Theme download: <5 seconds
- Extension loading: <100ms
- Icon lookup: <10ms
- Syntax highlighting: <50ms for 1000 lines

## Success Criteria for Phase 6

Phase 6 is complete when:
1. ✅ VSCode marketplace integration works
2. ✅ Extension system secure and functional
3. ✅ Icon themes supported
4. ✅ Syntax highlighting operational
5. ✅ Performance requirements met
6. ✅ Security validated
7. ✅ Documentation complete

## Notes for Agent

- VSCode compatibility is critical
- Security is paramount for extensions
- Performance must be maintained
- Test with real VSCode themes/extensions
- Document extension API thoroughly