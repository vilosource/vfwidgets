# ChromeTabbedWindow Extension Guide (v2.0 and Beyond)

## Overview

This guide documents the planned extension points and future features for ChromeTabbedWindow v2.0 and beyond. While v1.0 maintains strict QTabWidget API compatibility, the internal architecture has been designed to support rich extensions without breaking changes.

## Version Roadmap

### v1.x (Current)
- 100% QTabWidget API compatibility
- Chrome-style visuals
- Platform-aware behavior
- No additional public APIs

### v2.0 (Planned)
- Tab services layer
- Plugin system
- Advanced tab management
- Developer tools
- Extended signals

### v3.0 (Future)
- Multi-window coordination
- Tab tearing/docking
- Remote tabs
- Advanced theming

## Extension Architecture

### Service Layer (v2.0)

The service layer will provide shared functionality to tab content widgets:

```python
class TabServices:
    """
    Services provided to tab content (v2.0).
    Currently internal, will be exposed in v2.0.
    """

    def __init__(self, window: ChromeTabbedWindow):
        self._window = window
        self._message_bus = MessageBus()
        self._notification_system = NotificationSystem()
        self._settings_manager = SettingsManager()
        self._command_registry = CommandRegistry()

    # Messaging between tabs
    def broadcast(self, message: Any, exclude: QWidget = None) -> None:
        """Broadcast message to all tabs"""
        for i in range(self._window.count()):
            widget = self._window.widget(i)
            if widget != exclude and hasattr(widget, 'on_message'):
                widget.on_message(message)

    def send_to_tab(self, index: int, message: Any) -> None:
        """Send message to specific tab"""
        widget = self._window.widget(index)
        if widget and hasattr(widget, 'on_message'):
            widget.on_message(message)

    # Notifications
    def show_toast(self, message: str,
                  severity: str = "info",
                  duration: int = 3000) -> None:
        """Show toast notification"""
        self._notification_system.show(message, severity, duration)

    # Settings
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        return self._settings_manager.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set application setting"""
        self._settings_manager.set(key, value)

    # Commands
    def register_command(self, name: str, handler: Callable) -> None:
        """Register a command"""
        self._command_registry.register(name, handler)

    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered command"""
        return self._command_registry.execute(name, *args, **kwargs)
```

### Tab Content Interface (v2.0)

Standard interface for tab widgets to implement:

```python
class ITabContent(Protocol):
    """
    Optional interface for tab content widgets (v2.0).
    Implementing this interface enables advanced features.
    """

    # Lifecycle hooks
    def on_tab_activated(self) -> None:
        """Called when tab becomes active"""
        ...

    def on_tab_deactivated(self) -> None:
        """Called when tab becomes inactive"""
        ...

    def on_before_close(self) -> bool:
        """Called before tab closes. Return False to veto."""
        ...

    def on_after_close(self) -> None:
        """Called after tab is closed"""
        ...

    # State management
    def is_modified(self) -> bool:
        """Return True if content is modified"""
        ...

    def can_close(self) -> bool:
        """Return True if tab can be closed"""
        ...

    def save_state(self) -> dict:
        """Save tab state for session persistence"""
        ...

    def restore_state(self, state: dict) -> None:
        """Restore tab state from saved data"""
        ...

    # Metadata providers
    def get_tab_title(self) -> str:
        """Dynamic tab title"""
        ...

    def get_tab_icon(self) -> QIcon:
        """Dynamic tab icon"""
        ...

    def get_tab_tooltip(self) -> str:
        """Dynamic tab tooltip"""
        ...

    def get_tab_badge(self) -> Optional[str]:
        """Tab badge (e.g., notification count)"""
        ...

    # Services
    def set_services(self, services: TabServices) -> None:
        """Receive reference to tab services"""
        ...

    # Messaging
    def on_message(self, message: Any) -> None:
        """Handle message from other tabs"""
        ...

    # Commands
    def get_commands(self) -> List[Command]:
        """Commands this tab provides"""
        ...

    def can_execute_command(self, command: str) -> bool:
        """Check if command can be executed"""
        ...

    def execute_command(self, command: str, *args) -> Any:
        """Execute a command"""
        ...
```

### Plugin System (v2.0)

Extend ChromeTabbedWindow functionality via plugins:

```python
class ITabPlugin(Protocol):
    """
    Plugin interface for extending ChromeTabbedWindow (v2.0).
    """

    # Metadata
    @property
    def name(self) -> str:
        """Plugin name"""
        ...

    @property
    def version(self) -> str:
        """Plugin version"""
        ...

    @property
    def description(self) -> str:
        """Plugin description"""
        ...

    # Lifecycle
    def initialize(self, window: ChromeTabbedWindow) -> None:
        """Initialize plugin with window reference"""
        ...

    def shutdown(self) -> None:
        """Clean up plugin resources"""
        ...

    # Window events
    def on_window_created(self, window: ChromeTabbedWindow) -> None:
        """Called when window is created"""
        ...

    def on_window_closing(self, window: ChromeTabbedWindow) -> bool:
        """Called before window closes. Return False to veto."""
        ...

    # Tab events
    def on_tab_added(self, index: int, widget: QWidget) -> None:
        """Called when tab is added"""
        ...

    def on_tab_removed(self, index: int, widget: QWidget) -> None:
        """Called when tab is removed"""
        ...

    def on_tab_activated(self, index: int, widget: QWidget) -> None:
        """Called when tab is activated"""
        ...

    # UI contributions
    def contribute_menu_items(self) -> List[QAction]:
        """Contribute menu items"""
        ...

    def contribute_toolbar_items(self) -> List[QWidget]:
        """Contribute toolbar widgets"""
        ...

    def contribute_context_menu(self, index: int) -> List[QAction]:
        """Contribute tab context menu items"""
        ...

    def contribute_status_widget(self) -> Optional[QWidget]:
        """Contribute status bar widget"""
        ...

# Plugin manager
class PluginManager:
    """Manages ChromeTabbedWindow plugins"""

    def __init__(self):
        self._plugins: List[ITabPlugin] = []
        self._enabled: Dict[str, bool] = {}

    def register_plugin(self, plugin: ITabPlugin) -> None:
        """Register a plugin"""
        self._plugins.append(plugin)
        self._enabled[plugin.name] = True

    def enable_plugin(self, name: str) -> None:
        """Enable a plugin by name"""
        self._enabled[name] = True

    def disable_plugin(self, name: str) -> None:
        """Disable a plugin by name"""
        self._enabled[name] = False

    def get_enabled_plugins(self) -> List[ITabPlugin]:
        """Get list of enabled plugins"""
        return [p for p in self._plugins
                if self._enabled.get(p.name, False)]
```

## Advanced Features (v2.0+)

### Tab Groups and Workspaces

```python
class TabGroup:
    """Group related tabs together (v2.0)"""

    def __init__(self, name: str, color: QColor = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.color = color or QColor()
        self.tabs: List[int] = []
        self.collapsed = False

class WorkspaceManager:
    """Manage multiple workspaces (v2.0)"""

    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}
        self._current: Optional[str] = None

    def create_workspace(self, name: str) -> Workspace:
        """Create a new workspace"""
        workspace = Workspace(name)
        self._workspaces[workspace.id] = workspace
        return workspace

    def switch_workspace(self, workspace_id: str) -> None:
        """Switch to a different workspace"""
        if workspace_id in self._workspaces:
            self._current = workspace_id
            self._apply_workspace(self._workspaces[workspace_id])

    def save_current_workspace(self) -> None:
        """Save current tab configuration as workspace"""
        if self._current:
            workspace = self._workspaces[self._current]
            workspace.save_state(self._window)
```

### Session Management

```python
class SessionManager:
    """Manage tab sessions (v2.0)"""

    def __init__(self, window: ChromeTabbedWindow):
        self._window = window
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self.auto_save)

    def save_session(self, path: str = None) -> None:
        """Save current session to file"""
        session = {
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'window_state': self._get_window_state(),
            'tabs': self._get_tabs_state()
        }

        path = path or self._get_default_session_path()
        with open(path, 'w') as f:
            json.dump(session, f, indent=2)

    def restore_session(self, path: str = None) -> None:
        """Restore session from file"""
        path = path or self._get_default_session_path()

        if not os.path.exists(path):
            return

        with open(path, 'r') as f:
            session = json.load(f)

        self._restore_window_state(session['window_state'])
        self._restore_tabs(session['tabs'])

    def enable_auto_save(self, interval: int = 60000) -> None:
        """Enable automatic session saving"""
        self._auto_save_timer.start(interval)

    def restore_after_crash(self) -> bool:
        """Attempt to restore after crash"""
        crash_session = self._get_crash_session_path()
        if os.path.exists(crash_session):
            self.restore_session(crash_session)
            os.remove(crash_session)
            return True
        return False
```

### Tab Lifecycle Extensions

```python
class ExtendedTabLifecycle:
    """Extended tab lifecycle management (v2.0)"""

    def __init__(self, window: ChromeTabbedWindow):
        self._window = window
        self._hibernated: Dict[int, HibernatedTab] = {}

    def hibernate_tab(self, index: int) -> None:
        """Unload tab to save memory"""
        widget = self._window.widget(index)
        if widget:
            # Save state
            state = self._capture_state(widget)

            # Create placeholder
            placeholder = QLabel("Tab hibernated\nClick to restore")
            placeholder.setAlignment(Qt.AlignCenter)

            # Store hibernated data
            self._hibernated[index] = HibernatedTab(widget, state)

            # Replace with placeholder
            self._window.removeTab(index)
            self._window.insertTab(index, placeholder,
                                  self._window.tabText(index))

    def restore_tab(self, index: int) -> None:
        """Restore hibernated tab"""
        if index in self._hibernated:
            hibernated = self._hibernated.pop(index)

            # Recreate widget
            widget = hibernated.recreate()

            # Replace placeholder
            self._window.removeTab(index)
            self._window.insertTab(index, widget,
                                  self._window.tabText(index))

    def pin_tab(self, index: int) -> None:
        """Pin tab to prevent closing"""
        # Mark as pinned
        self._window.setTabData(index,
            {**self._window.tabData(index), 'pinned': True})

        # Update visual
        self._update_pinned_visual(index)

    def protect_tab(self, index: int, password: str) -> None:
        """Password protect a tab"""
        # Store password hash
        self._window.setTabData(index,
            {**self._window.tabData(index),
             'protected': True,
             'password_hash': hash_password(password)})
```

### Developer Tools (v2.0)

```python
class DeveloperTools:
    """Built-in developer tools (v2.0)"""

    def __init__(self, window: ChromeTabbedWindow):
        self._window = window
        self._profiler = TabProfiler()
        self._inspector = WidgetInspector()
        self._console = DeveloperConsole()

    def show_developer_panel(self) -> None:
        """Show developer tools panel"""
        panel = QDockWidget("Developer Tools")
        tabs = QTabWidget()

        tabs.addTab(self._profiler.widget(), "Profiler")
        tabs.addTab(self._inspector.widget(), "Inspector")
        tabs.addTab(self._console.widget(), "Console")

        panel.setWidget(tabs)
        self._window.addDockWidget(Qt.BottomDockWidgetArea, panel)

class TabProfiler:
    """Profile tab performance"""

    def profile_tab(self, index: int) -> TabMetrics:
        """Get performance metrics for a tab"""
        return TabMetrics(
            memory_usage=self._get_memory_usage(index),
            cpu_time=self._get_cpu_time(index),
            render_time=self._get_render_time(index),
            event_count=self._get_event_count(index)
        )

class WidgetInspector:
    """Inspect widget hierarchy"""

    def inspect_tab(self, index: int) -> WidgetTree:
        """Get widget tree for a tab"""
        widget = self._window.widget(index)
        return self._build_tree(widget)

    def highlight_widget(self, widget: QWidget) -> None:
        """Highlight widget in UI"""
        overlay = HighlightOverlay(widget)
        overlay.show()
```

### Theme System (v2.0)

```python
class ThemeManager:
    """Advanced theming system (v2.0)"""

    def __init__(self):
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[str] = None
        self._custom_renderers: Dict[str, TabRenderer] = {}

    def register_theme(self, theme: Theme) -> None:
        """Register a new theme"""
        self._themes[theme.name] = theme

    def apply_theme(self, name: str) -> None:
        """Apply a theme"""
        if name in self._themes:
            theme = self._themes[name]
            self._current_theme = name

            # Apply palette
            QApplication.setPalette(theme.palette)

            # Apply stylesheet
            self._window.setStyleSheet(theme.stylesheet)

            # Apply custom renderer if provided
            if theme.tab_renderer:
                self._window._tab_bar.set_renderer(theme.tab_renderer)

    def create_custom_renderer(self, name: str) -> TabRenderer:
        """Create custom tab renderer"""
        renderer = CustomTabRenderer()
        self._custom_renderers[name] = renderer
        return renderer

class Theme:
    """Theme definition"""

    def __init__(self, name: str):
        self.name = name
        self.palette = QPalette()
        self.stylesheet = ""
        self.tab_renderer: Optional[TabRenderer] = None
        self.animations: Dict[str, QEasingCurve] = {}
        self.colors: Dict[str, QColor] = {}
        self.fonts: Dict[str, QFont] = {}
```

### Multi-Window Coordination (v3.0)

```python
class MultiWindowCoordinator:
    """Coordinate multiple ChromeTabbedWindow instances (v3.0)"""

    def __init__(self):
        self._windows: List[ChromeTabbedWindow] = []
        self._main_window: Optional[ChromeTabbedWindow] = None

    def create_window(self, role: str = "secondary") -> ChromeTabbedWindow:
        """Create a new coordinated window"""
        window = ChromeTabbedWindow()
        window.setAttribute(Qt.WA_DeleteOnClose)

        self._windows.append(window)

        if role == "main":
            self._main_window = window

        # Connect coordination signals
        self._connect_window(window)

        return window

    def move_tab_to_window(self, tab_index: int,
                           from_window: ChromeTabbedWindow,
                           to_window: ChromeTabbedWindow) -> None:
        """Move tab between windows"""
        # Get widget and metadata
        widget = from_window.widget(tab_index)
        text = from_window.tabText(tab_index)
        icon = from_window.tabIcon(tab_index)

        # Remove from source
        from_window.removeTab(tab_index)

        # Add to destination
        new_index = to_window.addTab(widget, text)
        to_window.setTabIcon(new_index, icon)

    def broadcast_to_all_windows(self, message: Any) -> None:
        """Send message to all windows"""
        for window in self._windows:
            if hasattr(window, 'on_broadcast'):
                window.on_broadcast(message)

    def synchronize_theme(self) -> None:
        """Synchronize theme across all windows"""
        if self._main_window:
            theme = self._main_window.current_theme()
            for window in self._windows:
                if window != self._main_window:
                    window.apply_theme(theme)
```

### Tab Tearing and Docking (v3.0)

```python
class TabTearingManager:
    """Handle tab tearing and docking (v3.0)"""

    def __init__(self, window: ChromeTabbedWindow):
        self._window = window
        self._drag_preview: Optional[QWidget] = None
        self._tear_threshold = 50  # pixels

    def start_tear(self, index: int, pos: QPoint) -> None:
        """Start tearing a tab"""
        # Create preview
        widget = self._window.widget(index)
        self._drag_preview = self._create_preview(widget)
        self._drag_preview.move(pos)
        self._drag_preview.show()

    def update_tear(self, pos: QPoint) -> None:
        """Update tear preview position"""
        if self._drag_preview:
            self._drag_preview.move(pos)

            # Check for dock targets
            target = self._find_dock_target(pos)
            if target:
                self._show_dock_preview(target)

    def complete_tear(self, pos: QPoint) -> None:
        """Complete the tear operation"""
        target = self._find_dock_target(pos)

        if target:
            # Dock to target
            self._dock_to_target(target)
        else:
            # Create new window
            self._create_torn_window(pos)

        # Clean up preview
        if self._drag_preview:
            self._drag_preview.deleteLater()
            self._drag_preview = None
```

## Migration Strategies

### From v1.0 to v2.0

```python
# v1.0 code (unchanged)
window = ChromeTabbedWindow()
window.addTab(widget, "Tab")

# v2.0 code (with new features)
window = ChromeTabbedWindow()
window.addTab(widget, "Tab")

# Opt-in to new features
if hasattr(widget, 'set_services'):
    widget.set_services(window.get_services())

# Use new signals if available
if hasattr(window, 'tabAboutToClose'):
    window.tabAboutToClose.connect(handle_closing)
```

### Backward Compatibility

All v2.0+ features will be:
1. **Opt-in**: Existing code continues to work
2. **Discoverable**: Use hasattr() to check for features
3. **Graceful**: Degrade gracefully if not supported
4. **Documented**: Clear migration guides

## Development Guidelines

### Adding New Features

1. **Never break v1.0 API**: All QTabWidget methods must work
2. **Use composition**: Add via services, not inheritance
3. **Make it optional**: Features should be opt-in
4. **Document thoroughly**: Update this guide
5. **Test compatibility**: Ensure v1.0 code still works

### Extension Best Practices

```python
# Good: Check for capability
if hasattr(window, 'get_services'):
    services = window.get_services()
    services.show_toast("Hello")

# Bad: Assume capability exists
services = window.get_services()  # May fail in v1.0

# Good: Progressive enhancement
class MyTab(QWidget):
    def __init__(self):
        super().__init__()

        # Basic functionality
        self.setup_ui()

        # Enhanced functionality if available
        if hasattr(self, 'set_services'):
            self.services_available = True

    def set_services(self, services):
        """Optional: Called if services available"""
        self.services = services
        self.enable_enhanced_features()

# Bad: Require new features
class MyTab(QWidget, ITabContent):  # Fails in v1.0
    def on_tab_activated(self):  # Required method
        pass
```

## Testing Extensions

### Test Framework

```python
class ExtensionTestCase:
    """Base test case for extensions"""

    def get_v1_window(self) -> ChromeTabbedWindow:
        """Get v1.0 compatible window"""
        window = ChromeTabbedWindow()
        # Disable all v2.0 features
        return window

    def get_v2_window(self) -> ChromeTabbedWindow:
        """Get v2.0 window with features"""
        window = ChromeTabbedWindow()
        # Enable v2.0 features
        window._enable_v2_features()
        return window

    def test_backward_compatibility(self):
        """Test v1.0 code still works"""
        window = self.get_v2_window()

        # All v1.0 operations must work
        index = window.addTab(QWidget(), "Test")
        assert window.count() == 1
        assert window.tabText(index) == "Test"

    def test_progressive_enhancement(self):
        """Test feature detection"""
        v1_window = self.get_v1_window()
        v2_window = self.get_v2_window()

        # Features present in v2, absent in v1
        assert not hasattr(v1_window, 'get_services')
        assert hasattr(v2_window, 'get_services')
```

## Roadmap Timeline

### 2024 Q3-Q4
- v1.0 release with QTabWidget parity
- Community feedback gathering
- Extension architecture refinement

### 2025 Q1-Q2
- v2.0 beta with service layer
- Plugin system implementation
- Developer tools preview

### 2025 Q3-Q4
- v2.0 stable release
- Advanced features (groups, workspaces)
- Theme system

### 2026+
- v3.0 with multi-window coordination
- Tab tearing and docking
- Remote tabs
- AI-assisted features

## Contributing

### How to Propose Extensions

1. **Open an issue**: Describe the use case
2. **Create a design doc**: Detail the API
3. **Implement as plugin**: Prove the concept
4. **Submit PR**: With tests and docs

### Extension Requirements

- Must not break v1.0 API
- Must be optional/opt-in
- Must have tests
- Must have documentation
- Must follow MVC architecture

## See Also

- [API Reference](api.md) - v1.0 Public API
- [Architecture](architecture.md) - Internal design
- [Usage Guide](usage.md) - Current usage patterns
- [Platform Notes](platform-notes.md) - Platform details