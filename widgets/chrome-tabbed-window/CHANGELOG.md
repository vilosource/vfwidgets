# Changelog

All notable changes to ChromeTabbedWindow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **CRITICAL FIX**: Corrected Chrome-style tab implementation
  - Removed incorrect `tabRect()` override that was breaking Qt's internal state
  - Fixed tab width compression using proper `tabSizeHint()` override
  - Changed `setExpanding(True)` to `setExpanding(False)` for correct compression
  - Fixed widget parent relationships for proper layout integration
  - Tabs now properly compress like Chrome (52px min, 240px max)
  - Documentation: Added comprehensive implementation guide at `docs/chrome-tabs-implementation-GUIDE.md`

### Added
- Initial project structure and specification
- Complete requirements specification document
- Python packaging configuration (pyproject.toml)
- README with feature overview and quick start guide
- MIT License

### Planned
- Core ChromeTabbedWindow implementation
- QTabWidget API compatibility layer
- Platform detection and capabilities
- Frameless window support
- Cross-platform testing

## [1.0.0] - TBD

### Added
- Full QTabWidget API compatibility
- Dual-mode operation (top-level and embedded)
- Cross-platform support (Windows, macOS, Linux, WSL)
- Chrome-style tab UI
- Platform-aware automatic degradation
- Comprehensive test suite
- Complete documentation

[Unreleased]: https://github.com/vilosource/vfwidgets/compare/chrome-tabbed-window-v1.0.0...HEAD
[1.0.0]: https://github.com/vilosource/vfwidgets/releases/tag/chrome-tabbed-window-v1.0.0