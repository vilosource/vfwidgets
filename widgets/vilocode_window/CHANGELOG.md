# Changelog

All notable changes to ViloCodeWindow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Fluent Menu API** - New `add_menu()` method with MenuBuilder for clean, readable menu creation
  - 75% code reduction (67 lines → 17 lines for typical menu setup)
  - Automatic menu bar creation (no manual `QMenuBar()` needed)
  - Automatic theme integration (no manual color management)
  - Lazy integration pattern eliminates initialization order traps
  - Method chaining for clean syntax: `window.add_menu("File").add_action(...).add_separator()`
- `MenuBuilder` class with full fluent interface:
  - `add_action()` - Add menu actions with callbacks, shortcuts, tooltips, icons
  - `add_separator()` - Add visual separators
  - `add_submenu()` / `end_submenu()` - Nested submenu support
  - `add_checkable()` - Toggle/checkbox actions
  - `add_action_group()` - Radio button groups for mutually exclusive options
- Menu Quick Start Guide (`docs/menu-quick-start-GUIDE.md`) - Complete menu API documentation with examples
- Example 06 (`examples/06_menu_fluent_api.py`) - Comprehensive MenuBuilder demonstration
- `py.typed` marker file for better IDE type checking support

### Changed
- `get_menu_bar()` now auto-creates menu bar if needed (returns `QMenuBar`, never `None`)
- Updated all menu examples (04, 05, 06) to use new fluent API
- Updated README with "With Menu Bar" quick start example
- Updated API documentation with fluent API as recommended approach
- `TitleBar.integrate_menu_bar()` added as new recommended method (replaces `set_menu_bar()`)

### Deprecated
- `set_menu_bar()` - Still works but `add_menu()` is recommended for new code
- `TitleBar.update_menu_bar_styling()` - Now called automatically, manual calls not needed

### Fixed
- Menu bar initialization order trap - menus can now be created in any order
- Theme colors not applying to menu bar - now automatic with fluent API
- Manual theme integration workarounds no longer needed

## [0.1.0] - Previous Release

Initial release with VS Code-style window layout, activity bar, sidebar, main pane, auxiliary bar, and status bar.
