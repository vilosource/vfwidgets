# ViloxTerm Documentation

**Status**: Current Implementation (v1.0)

This directory contains documentation for the ViloxTerm terminal emulator application.

---

## Quick Start

**New to ViloxTerm?** Start here:

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture and component integration
2. **[lessons-learned-GUIDE.md](lessons-learned-GUIDE.md)** - Critical insights from multi-widget integration
3. **[../README.md](../README.md)** - Main README with quick start guide

---

## Current Documentation

### System Architecture

**[ARCHITECTURE.md](ARCHITECTURE.md)** - Current Implementation Architecture
- Component integration (ChromeTabbedWindow, MultisplitWidget, TerminalWidget, KeybindingManager)
- System design and flow
- Memory efficiency (MultiSessionTerminalServer)
- Performance characteristics
- File structure
- Design decisions

### Developer Guides

**[lessons-learned-GUIDE.md](lessons-learned-GUIDE.md)** - Implementation Lessons Learned
- ChromeTabbedWindow integration pitfalls
- Built-in new tab button pattern
- MultisplitWidget + WidgetProvider pattern
- Window controls customization
- Reference example best practices
- Debugging multi-widget applications

**[focus-handling-GUIDE.md](focus-handling-GUIDE.md)** - Focus Handling with QWebEngineView Widgets ⭐ **New**
- Automatic focus after split pane creation
- QWebEngineView focus proxy architecture
- Signal chain debugging techniques
- `setFocus()` override pattern for web widgets
- Double-click focus issue resolution

**Top 8 Critical Lessons**:
1. Provider MUST be in MultisplitWidget constructor
2. Override `_on_new_tab_requested()`, don't create custom "+" button
3. Import WherePosition from core.types, not main package
4. Don't override `_setup_ui()` in ChromeTabbedWindow
5. Always check widget examples first
6. WidgetProvider creates widgets lazily
7. Window controls only exist in frameless mode
8. ThemedApplication integration is automatic

---

## Historical Documentation (Archive)

The `archive/` directory contains planning and design documents from ViloxTerm's development phase. These are preserved for historical reference but are superseded by the current implementation.

### Migration Documents

**[archive/multisplit-migration/](archive/multisplit-migration/)** - MultisplitWidget v0.2.0 Migration
- Complete migration from MultisplitWidget v0.1.x to v0.2.0
- Implementation tasks and completion summary
- **Status**: ✅ Completed 2025-10-04 - See [multisplit-migration-COMPLETE.md](multisplit-migration-COMPLETE.md)

### Planning Phase Documents

**[archive/implementation-PLAN.md](archive/implementation-PLAN.md)** - Original Implementation Plan
- Detailed implementation steps and code snippets
- Phase-by-phase checklist
- Reference patterns and integration guides
- **Status**: ✅ Implementation complete, archived for reference

**[archive/SUMMARY.md](archive/SUMMARY.md)** - Planning Phase Summary
- Documentation overview from planning phase
- Architecture evolution (embedded → shared server)
- Implementation phases and decisions
- **Status**: Superseded by ARCHITECTURE.md

### Terminal Server Architecture Documents

**[archive/terminal-server-architecture-ARCHITECTURE.md](archive/terminal-server-architecture-ARCHITECTURE.md)** - Old Embedded Server Architecture
- Documents the OLD approach: one server per terminal
- Resource analysis showing ~300MB for 20 terminals
- **Status**: Superseded by MultiSessionTerminalServer (current: ~110MB for 20 terminals)

**[archive/shared-server-refactoring-DESIGN.md](archive/shared-server-refactoring-DESIGN.md)** - Multi-Session Server Design
- Proposed multi-session server architecture
- Design rationale and component details
- **Status**: ✅ Design implemented in vfwidgets-terminal package

**[archive/terminal-server-protocol-SPEC.md](archive/terminal-server-protocol-SPEC.md)** - Protocol Specification
- SocketIO protocol for terminal servers
- Message format and events
- Implementation requirements
- **Status**: Implemented in vfwidgets-terminal, belongs in that package

**[archive/previous-implementation-ANALYSIS.md](archive/previous-implementation-ANALYSIS.md)** - Reference Implementation Analysis
- Analysis of previous ViloxTerm implementation
- Backend abstraction layer patterns
- Code reuse recommendations
- **Status**: Historical analysis, patterns adopted in vfwidgets-terminal

---

## Documentation Roadmap

### Completed ✅
- [x] System architecture documentation (ARCHITECTURE.md)
- [x] Integration lessons learned (lessons-learned-GUIDE.md)
- [x] Historical document archival

### Future Documentation
- [ ] User guide (installation, usage, customization)
- [ ] Configuration guide (keybindings, themes, profiles)
- [ ] Troubleshooting guide
- [ ] Plugin development guide (when plugins are implemented)

---

## Component Documentation

ViloxTerm integrates five VFWidgets components. For detailed component documentation, see:

### Integrated Components

1. **ChromeTabbedWindow**
   - [README](../../widgets/chrome-tabbed-window/README.md)
   - [Example 04: Themed Chrome Tabs](../../widgets/chrome-tabbed-window/examples/04_themed_chrome_tabs.py) ⭐ Reference

2. **MultisplitWidget**
   - [README](../../widgets/multisplit_widget/README.md)
   - [Example 01: Basic Text Editor](../../widgets/multisplit_widget/examples/01_basic_text_editor.py) ⭐ Reference

3. **TerminalWidget**
   - [README](../../widgets/terminal_widget/README.md)
   - [Example 02: Multi-Terminal App](../../widgets/terminal_widget/examples/02_multi_terminal_app.py) ⭐ Reference
   - [Theme Integration Lessons](../../widgets/terminal_widget/docs/theme-integration-lessons-GUIDE.md)

4. **Theme System**
   - [Official Theming Guide](../../widgets/theme_system/docs/THEMING-GUIDE-OFFICIAL.md) ⭐ Primary
   - [Quick Start Guide](../../widgets/theme_system/docs/quick-start-GUIDE.md)
   - [Widget Development Guide](../../widgets/theme_system/docs/widget-development-GUIDE.md)

5. **KeybindingManager**
   - [README](../../widgets/keybinding_manager/README.md)
   - [Developer Integration Guide](../../widgets/keybinding_manager/docs/developer-integration-GUIDE.md) ⭐ Reference
   - [User Guide](../../widgets/keybinding_manager/docs/user-guide-GUIDE.md)
   - [Example 03: Manual File Editing](../../widgets/keybinding_manager/examples/03_manual_file_editing.py)

---

## Key Architecture Patterns

### 1. Frameless Chrome Window
```python
# ChromeTabbedWindow with no parent = automatic frameless mode
app = ThemedApplication(sys.argv)
window = ViloxTermApp()  # Inherits from ChromeTabbedWindow
window.show()
```

### 2. Shared Terminal Server
```python
# One server for all terminals (63% memory savings)
self.terminal_server = MultiSessionTerminalServer(port=0)
self.terminal_provider = TerminalProvider(self.terminal_server)
```

### 3. Lazy Widget Creation
```python
# MultisplitWidget creates widgets on-demand via provider
multisplit = MultisplitWidget(provider=self.terminal_provider)
```

### 4. User-Customizable Shortcuts
```python
# KeybindingManager with JSON persistence
self.keybinding_manager = KeybindingManager(
    storage_path="~/.config/viloxterm/keybindings.json",
    auto_save=True
)
```

---

## Development Timeline

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Core window (ChromeTabbedWindow + ThemedApplication) |
| Phase 2 | ✅ Complete | Terminal integration (MultiSessionTerminalServer) |
| Phase 3 | ✅ Complete | MultisplitWidget integration (dynamic panes) |
| Phase 4 | ✅ Complete | Theme menu (ThemeDialog + MenuButton) |
| Phase 5 | ✅ Complete | Keyboard shortcuts (KeybindingManager) |

**Current Version**: 1.0
**Status**: Production-ready

---

## Contributing

When adding new documentation:

1. Follow the [VFWidgets naming convention](../../../../docs/CLAUDE.md#documentation-naming-convention):
   - Format: `<descriptive-words>-<PURPOSE>.md`
   - Use kebab-case
   - End with PURPOSE suffix (GUIDE, DESIGN, PLAN, etc.)

2. Update this index (README.md)

3. Add cross-references to related documents

4. Include code examples where applicable

---

## License

See [root LICENSE file](../../../../LICENSE).

---

**Last Updated**: 2025-10-04
**Documentation Version**: 1.0
