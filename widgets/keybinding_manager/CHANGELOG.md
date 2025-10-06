# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ActionRegistry for managing application actions
- KeybindingStorage for persistent keybinding storage with JSON format
- KeybindingManager for orchestrating keybindings
- Unit tests with 89% coverage
- Type hints with mypy --strict compliance
- Comprehensive docstrings for all public APIs
- Minimal usage example (01_minimal_usage.py)
- Full application example (02_full_application.py)
- Architecture design documentation
- Developer experience plan documentation
- Implementation roadmap documentation
- Step-by-step implementation tasks documentation

## [0.1.0] - 2025-10-03

### Added
- Initial Phase 1 (MVP + Core DX) implementation
- ActionDefinition dataclass for defining actions
- ActionRegistry class for centralized action management
- KeybindingStorage class with atomic file writes
- KeybindingManager class as main API
- Support for action categories
- Persistent storage with user overrides
- Auto-save functionality
- Query methods for bindings and categories
- Reset to defaults functionality
- Package exports in __init__.py
- Development tooling (pytest, mypy, coverage)
- MIT License
