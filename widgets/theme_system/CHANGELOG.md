# Changelog

All notable changes to the VFWidgets Theme System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-29

### Added
- Initial release of VFWidgets Theme System
- Core theme management functionality
- VSCode theme compatibility and import
- Built-in dark, light, and high-contrast themes
- Zero-configuration theming with VFWidget base class
- Theme property decorators for easy integration
- Dynamic runtime theme switching
- Comprehensive documentation suite
- Theme editor GUI (planned for 1.1.0)
- Testing utilities for themed widgets
- Migration tools for existing codebases

### Features
- Progressive enhancement model (zero to full customization)
- Automatic theme application to Qt widgets
- Theme inheritance and composition
- Color manipulation functions
- Contrast checking and accessibility features
- Performance optimizations with caching
- Type-safe theme properties with IDE support
- System theme detection and synchronization

### Documentation
- Complete API reference
- Developer getting started guide
- Widget integration guide
- Migration guide for existing code
- Best practices guide
- VSCode compatibility specification
- Theme format specification
- Architecture design document

### Known Issues
- Theme editor GUI not yet implemented (coming in 1.1.0)
- Remote theme loading not yet available
- Marketplace integration pending

## [Unreleased]

### Added - Phase 2 Features (Developer Experience)
- **Theme Inheritance**: `ThemeBuilder.extend()` method for inheriting from parent themes
  - Extend built-in themes with `.extend("dark")`
  - Extend custom Theme instances
  - Automatic property inheritance with override support
  - Property priority: BEFORE extend preserves, AFTER extend overrides
  - Inheritance chain support (grandparent → parent → child)

- **Theme Composition**: `ThemeComposer` class for merging multiple themes
  - Compose multiple themes with priority (later overrides earlier)
  - `compose(*themes, name)` for basic composition
  - `compose_chain(themes)` for composing lists
  - Result caching for performance
  - Component library theming pattern support

- **Accessibility Validation**: `ThemeValidator.validate_accessibility()` for WCAG compliance
  - WCAG AA contrast ratio checking (4.5:1 for normal text, 3:1 for large text)
  - Button contrast validation
  - Input field contrast validation
  - `ValidationResult` with errors and warnings
  - Detailed accessibility reports

- **Enhanced Error Messages**: `ThemeValidator.format_error()` with helpful suggestions
  - Typo correction suggestions using fuzzy matching
  - Available properties listing by category
  - Documentation links for each token category
  - `suggest_correction()` for property name typos
  - `get_available_properties(prefix)` for discovery

### Fixed
- Removed all references to non-existent "vscode" built-in theme
- Updated documentation to reflect actual built-in themes: "dark", "light", "default", "minimal"
- Fixed `Theme.get()` calls → `Theme.get_property()` (96 occurrences)
- Fixed `cleanup_callback()` signature to accept weakref parameter
- Fixed dark theme missing `"type": "dark"` field

### Changed
- **ROADMAP.md** updated to mark Phase 2 as COMPLETED
- **api-REFERENCE.md** now documents all Phase 2 classes and methods
- **theme-customization-GUIDE.md** added 3 new sections for Phase 2 features
- All documentation examples updated to use correct built-in theme names

## [2.0.0-rc4] - 2025-10-01

### Added - API Consolidation (Phase 1-5)
- **Examples Reorganization** (Phase 1): Restructured examples to show progressive learning path
  - Examples 01-04 now use simple API only (ThemedMainWindow, ThemedDialog, ThemedQWidget)
  - Example 05 serves as bridge to advanced API (introduces ThemedWidget)
  - Example 06+ demonstrates advanced features (Tokens, ThemeProperty, WidgetRole)
  - Added `examples/README.md` with clear progression guide

- **Tokens Constants** (Phase 2): Token constants for IDE autocomplete
  - `Tokens` class with all 179 theme tokens as constants
  - Example: `Tokens.WINDOW_BACKGROUND` instead of magic strings
  - Full autocomplete support in modern IDEs
  - Export in main `__init__.py` for easy access

- **ThemeProperty Descriptors** (Phase 3): Property descriptors for clean theme access
  - `ThemeProperty` base descriptor class
  - `ColorProperty` for QColor instances
  - `FontProperty` for QFont instances
  - Read-only enforcement with helpful error messages
  - Fallback to default values when properties not found

- **WidgetRole Enum** (Phase 4): Type-safe widget roles for semantic styling
  - `WidgetRole` enum with semantic roles (DANGER, SUCCESS, WARNING, etc.)
  - `set_widget_role()` helper function with automatic style refresh
  - `get_widget_role()` helper function for retrieving current role
  - Type-safe API replacing string-based roles

- **Inheritance Order Validation** (Phase 5): Runtime validation for correct inheritance patterns
  - `_validate_inheritance_order()` validates ThemedWidget comes BEFORE Qt base classes
  - Helpful error messages showing wrong vs correct inheritance patterns
  - Prevents common mistake: `class MyWidget(QWidget, ThemedWidget)` (wrong)
  - Enforces correct pattern: `class MyWidget(ThemedWidget, QWidget)` (correct)
  - Comprehensive test suite with 28 passing tests

### Changed
- **Documentation** reorganized around progressive disclosure strategy
  - `quick-start-GUIDE.md` now shows ONLY simple API
  - `widget-development-GUIDE.md` created for Stage 2-3 users
  - `api-REFERENCE.md` reorganized by skill level (Simple vs Advanced)
  - `theme-customization-GUIDE.md` updated with new features
  - `API-STRATEGY.md` documents progressive disclosure philosophy
  - `ROADMAP.md` updated with API philosophy section

### Fixed
- Improved error messages throughout codebase for better developer experience

### Developer Experience
- All new features designed for IDE autocomplete and type safety
- Clear progression path from simple to advanced usage
- No breaking changes - all additions are backward compatible

## [Unreleased]

### Planned for 1.1.0
- Visual theme editor GUI
- Theme marketplace integration
- Animation support for theme transitions
- Remote theme loading from URLs
- Additional built-in themes
- Theme validation CLI tool
- Performance profiler improvements

### Planned for 2.0.0
- AI-powered theme generation
- Theme version management
- Multi-theme composition
- Conditional theme properties
- Advanced gradient support
- Theme plugin system

---

For more details on upcoming features, see our [Roadmap](README.md#roadmap).