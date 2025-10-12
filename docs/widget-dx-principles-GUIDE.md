# VFWidgets DX Principles & Design Guidelines

## Philosophy: Make The Right Thing Easy

**Core Principle:** If developers struggle, we failed - not them.

Every widget should follow these principles to ensure excellent developer experience.

---

## The Four Pillars of Good DX

### 1. Zero-Config Defaults (Pit of Success)

**Principle:** Widgets work perfectly with zero configuration.

**Bad:**
```python
# Requires setup before use
window = ViloCodeWindow()
menubar = QMenuBar()  # Why do I need to know this?
window.set_menu_bar(menubar)
file_menu = menubar.addMenu("File")
```

**Good:**
```python
# Works immediately, no setup needed
window = ViloCodeWindow()
file_menu = window.add_menu("File")  # Just works!
```

**Implementation Requirements:**
- Auto-create required components on first access
- Sensible defaults that work for 90% of use cases
- No mandatory setup/initialization code

---

### 2. Progressive Disclosure (Layers of Complexity)

**Principle:** Simple API for simple needs, advanced API for advanced needs.

**Layer 1: Declarative (90% of users)**
```python
# Minimal code, maximum clarity
window.add_menu("File") \
    .add_action("Open", self.on_open, "Ctrl+O") \
    .add_action("Save", self.on_save, "Ctrl+S")
```

**Layer 2: Imperative (9% of users)**
```python
# More control, still straightforward
menubar = window.get_menu_bar()  # Auto-created
file_menu = menubar.addMenu("File")
file_menu.addAction("Open", self.on_open)
```

**Layer 3: Custom (1% of users)**
```python
# Full control for advanced users
custom_menubar = MyCustomMenuBar()
window.set_menu_bar(custom_menubar, replace=True)
```

**Implementation Requirements:**
- Level 1 API covers common cases
- Level 2 API exposes Qt primitives
- Level 3 API allows complete customization
- Each level documented separately

---

### 3. Automatic Integration (Magic That Just Works)

**Principle:** Components integrate automatically without manual wiring.

**Bad:**
```python
# Manual integration everywhere
window = ViloCodeWindow()
menubar = QMenuBar()
window.set_menu_bar(menubar)  # Manual
menubar.addMenu("File")  # Manual
window.show()
# Oh no, menu invisible due to theme!
window._title_bar.update_menu_bar_styling()  # Manual fix!
```

**Good:**
```python
# Automatic integration
window = ViloCodeWindow()
window.add_menu("File").add_action("Open", handler)
window.show()
# Theme automatically applied, menu visible, everything works!
```

**Implementation Requirements:**
- Components register with parent automatically
- Theme updates propagate automatically
- Layout updates happen automatically
- No manual "wire-up" code needed

---

### 4. Fail Fast with Clear Errors (Guard Rails)

**Principle:** Catch mistakes early with helpful error messages.

**Bad:**
```python
# Silent failure - menu never appears
menubar = QMenuBar()
window.set_menu_bar(menubar)  # Empty menubar accepted silently
menubar.addMenu("File")  # Too late, already transferred empty
```

**Good:**
```python
# Immediate error with fix suggestion
menubar = QMenuBar()
window.set_menu_bar(menubar)

# ⚠️  Warning: Menu bar is empty. Did you mean:
#     menubar.addMenu("File")
#     window.set_menu_bar(menubar)
# Or use: window.add_menu("File") for automatic setup.
```

**Implementation Requirements:**
- Validate inputs, reject invalid states
- Error messages explain what's wrong AND how to fix
- Warnings for deprecated patterns with migration path
- Link to documentation in error messages

---

## Widget Design Checklist

Before releasing any widget, ensure:

### API Design
- [ ] **Zero-config works:** Widget functional with `MyWidget()` alone
- [ ] **Three API layers:** Simple/Intermediate/Advanced all available
- [ ] **Fluent interface:** Builder pattern for common operations
- [ ] **No initialization traps:** Order of operations doesn't matter
- [ ] **No hidden state:** All configuration explicit or auto-discovered

### Theme Integration
- [ ] **Auto-themed:** Widget respects theme without setup
- [ ] **Theme updates:** Widget re-styles automatically on theme change
- [ ] **Fallback colors:** Widget usable even without theme system
- [ ] **Custom styling:** Advanced users can override theme
- [ ] **No invisible elements:** All colors have contrast

### Documentation
- [ ] **5-minute quickstart:** Complete working example ≤ 10 lines
- [ ] **API reference:** Every public method documented with examples
- [ ] **Common patterns:** 5-10 recipes for typical use cases
- [ ] **Troubleshooting:** List of common mistakes with solutions
- [ ] **Migration guide:** If replacing existing widget

### Error Handling
- [ ] **Invalid inputs rejected:** Clear error messages
- [ ] **Common mistakes warned:** Helpful suggestions
- [ ] **Debugging helpers:** Methods to inspect state
- [ ] **Error messages link to docs:** Direct path to solutions

### Testing
- [ ] **Unit tests:** All public methods covered
- [ ] **Integration tests:** Widget works with other widgets
- [ ] **Example tests:** All examples run successfully
- [ ] **Theme tests:** Widget works with all built-in themes
- [ ] **Regression tests:** Fixed bugs have tests

---

## Specific Widget Improvements

### ViloCodeWindow Menu Bar

**Current Problems:**
1. No auto-creation of menu bar
2. Initialization order matters (trap)
3. No automatic theme integration
4. Silent failures

**Improved API Design:**

```python
class ViloCodeWindow:
    """VS Code-style window with automatic menu bar integration."""

    # ==================== Layer 1: Simple API ====================

    def add_menu(self, title: str) -> MenuBuilder:
        """Add a menu to the menu bar (auto-created if needed).

        This is the recommended way to add menus. Handles all integration
        automatically including theme styling and title bar placement.

        Args:
            title: Menu title (e.g., "File", "Edit", "View")

        Returns:
            MenuBuilder for adding actions with fluent interface

        Example:
            >>> window.add_menu("File") \\
            ...     .add_action("Open", on_open, "Ctrl+O") \\
            ...     .add_separator() \\
            ...     .add_action("Exit", window.close, "Ctrl+Q")

        See Also:
            - get_menu_bar() for Qt QMenuBar access
            - set_menu_bar() for custom menu bar
        """
        menubar = self._ensure_menu_bar()
        menu = menubar.addMenu(title)
        return MenuBuilder(menu, self)

    def add_action_to_menu(
        self,
        menu_title: str,
        action_title: str,
        callback: Callable,
        shortcut: Optional[str] = None,
        icon: Optional[QIcon] = None,
    ) -> QAction:
        """Add an action to a menu (creates menu if needed).

        Convenience method for single actions.

        Args:
            menu_title: Name of menu (e.g., "File")
            action_title: Action text (e.g., "Open...")
            callback: Function to call when triggered
            shortcut: Optional keyboard shortcut (e.g., "Ctrl+O")
            icon: Optional icon

        Returns:
            Created QAction

        Example:
            >>> window.add_action_to_menu(
            ...     "File", "Open...", on_open, "Ctrl+O"
            ... )
        """
        # Implementation that finds or creates menu

    # ==================== Layer 2: Intermediate API ====================

    def get_menu_bar(self) -> QMenuBar:
        """Get the menu bar, creating it automatically if needed.

        Returns the underlying Qt QMenuBar for direct manipulation.
        The menu bar is automatically integrated with the title bar
        and styled according to the current theme.

        Returns:
            QMenuBar instance (never None)

        Example:
            >>> menubar = window.get_menu_bar()
            >>> file_menu = menubar.addMenu("File")
            >>> file_menu.addAction("Open", on_open)

        Note:
            Using add_menu() is recommended for simpler code.
        """
        return self._ensure_menu_bar()

    # ==================== Layer 3: Advanced API ====================

    def set_menu_bar(
        self,
        menubar: QMenuBar,
        *,
        auto_integrate: bool = True,
        auto_style: bool = True,
    ) -> None:
        """Set a custom menu bar.

        For advanced users who need complete control over the menu bar.

        Args:
            menubar: Custom QMenuBar instance
            auto_integrate: Automatically integrate with title bar (default: True)
            auto_style: Automatically apply theme styling (default: True)

        Example:
            >>> class MyMenuBar(QMenuBar):
            ...     # Custom implementation
            ...     pass
            >>>
            >>> window.set_menu_bar(MyMenuBar())

        Warning:
            If auto_integrate=False, you must manually handle title bar
            integration and theme styling.
        """
        # Implementation with validation and auto-integration

    # ==================== Internal Implementation ====================

    def _ensure_menu_bar(self) -> QMenuBar:
        """Ensure menu bar exists, creating if needed."""
        if self._menu_bar is None:
            self._menu_bar = QMenuBar()
            self._menu_bar_needs_integration = True

        return self._menu_bar

    def _integrate_menu_bar(self) -> None:
        """Integrate menu bar with title bar and theme system.

        Called automatically before first show. Handles:
        - Transferring menu bar to title bar (frameless mode)
        - Applying theme styling
        - Registering for theme change notifications
        """
        if not self._menu_bar or not self._menu_bar_needs_integration:
            return

        # Transfer to title bar
        if self._window_mode == WindowMode.Frameless and self._title_bar:
            self._title_bar.integrate_menu_bar(self._menu_bar)

        # Apply theme styling
        self._apply_menu_theme()

        # Register for theme changes
        try:
            from vfwidgets_theme import get_themed_application
            app = get_themed_application()
            if app:
                app.theme_changed.connect(self._on_theme_changed_for_menu)
        except ImportError:
            pass

        self._menu_bar_needs_integration = False

    def showEvent(self, event):
        """Auto-integrate menu bar before first show."""
        if self._menu_bar_needs_integration:
            self._integrate_menu_bar()
        super().showEvent(event)
```

**MenuBuilder Class:**

```python
class MenuBuilder:
    """Fluent interface for building menus.

    Provides chainable methods for adding menu items.

    Example:
        >>> window.add_menu("File") \\
        ...     .add_action("New", on_new, "Ctrl+N") \\
        ...     .add_action("Open", on_open, "Ctrl+O") \\
        ...     .add_separator() \\
        ...     .add_submenu("Recent Files") \\
        ...         .add_action("file1.txt", lambda: open("file1.txt")) \\
        ...         .add_action("file2.txt", lambda: open("file2.txt")) \\
        ...         .end_submenu() \\
        ...     .add_separator() \\
        ...     .add_action("Exit", window.close, "Ctrl+Q")
    """

    def __init__(self, menu: QMenu, window: ViloCodeWindow):
        self._menu = menu
        self._window = window
        self._submenu_stack: list[QMenu] = []

    def add_action(
        self,
        text: str,
        callback: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        icon: Optional[QIcon] = None,
        checkable: bool = False,
    ) -> 'MenuBuilder':
        """Add an action to the menu.

        Args:
            text: Action text
            callback: Function to call when triggered
            shortcut: Keyboard shortcut (e.g., "Ctrl+O")
            icon: Optional icon
            checkable: Whether action is checkable

        Returns:
            Self for chaining
        """
        action = self._current_menu().addAction(text)

        if callback:
            action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        if icon:
            action.setIcon(icon)
        if checkable:
            action.setCheckable(True)

        return self

    def add_separator(self) -> 'MenuBuilder':
        """Add a separator to the menu."""
        self._current_menu().addSeparator()
        return self

    def add_submenu(self, title: str) -> 'MenuBuilder':
        """Add a submenu.

        Args:
            title: Submenu title

        Returns:
            Self for chaining (subsequent calls affect submenu)

        Note:
            Call end_submenu() to return to parent menu
        """
        submenu = self._current_menu().addMenu(title)
        self._submenu_stack.append(submenu)
        return self

    def end_submenu(self) -> 'MenuBuilder':
        """Return to parent menu after adding submenu items."""
        if self._submenu_stack:
            self._submenu_stack.pop()
        return self

    def add_toggle_action(
        self,
        text: str,
        callback: Optional[Callable[[bool], None]] = None,
        shortcut: Optional[str] = None,
        default_checked: bool = False,
    ) -> 'MenuBuilder':
        """Add a checkable toggle action.

        Args:
            text: Action text
            callback: Function called with bool (checked state)
            shortcut: Keyboard shortcut
            default_checked: Initial checked state

        Returns:
            Self for chaining
        """
        action = self._current_menu().addAction(text)
        action.setCheckable(True)
        action.setChecked(default_checked)

        if callback:
            action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)

        return self

    def _current_menu(self) -> QMenu:
        """Get current menu (top of submenu stack or root menu)."""
        return self._submenu_stack[-1] if self._submenu_stack else self._menu
```

---

### ThemedApplication Improvements

**Current Problems:**
1. Initialization bug (`_is_initialized` too late)
2. No validation of theme names
3. Silent failures when theme not found
4. `prefer_dark` parameter doesn't work due to persistence

**Improved API Design:**

```python
class ThemedApplication:
    """Application with centralized theme management.

    Automatically applies themes to all ThemedWidget instances.
    """

    def __init__(
        self,
        argv: list[str],
        *,
        theme: Optional[str] = None,
        theme_config: Optional[ThemeConfig] = None,
        prefer_dark: bool = False,
        prefer_light: bool = False,
    ):
        """Initialize themed application.

        Args:
            argv: Command-line arguments
            theme: Specific theme to use (e.g., "dark", "light", "VSCode Dark+")
            theme_config: Advanced theme configuration
            prefer_dark: Use dark theme if available (ignored if theme set)
            prefer_light: Use light theme if available (ignored if theme set)

        Example (Simple):
            >>> app = ThemedApplication(sys.argv, prefer_dark=True)

        Example (Specific Theme):
            >>> app = ThemedApplication(sys.argv, theme="VSCode Dark+")

        Example (Advanced):
            >>> config = ThemeConfig(
            ...     default_theme="dark",
            ...     persist_theme=True,
            ...     auto_detect_system=True,
            ... )
            >>> app = ThemedApplication(sys.argv, theme_config=config)

        Raises:
            ThemeNotFoundError: If specified theme doesn't exist
        """
        # Build theme config with validation
        config = self._build_theme_config(
            theme, theme_config, prefer_dark, prefer_light
        )

        super().__init__(argv, theme_config=config)

    def set_theme(self, theme: Union[str, Theme], *, persist: bool = None) -> None:
        """Set the application theme.

        Args:
            theme: Theme name or Theme object
            persist: Save preference for next launch (default: use config)

        Raises:
            ThemeNotFoundError: If theme doesn't exist
            ValueError: If theme is invalid

        Example:
            >>> app.set_theme("dark")
            >>> app.set_theme("VSCode Dark+", persist=True)
        """
        # Validate theme exists
        if isinstance(theme, str):
            if not self._theme_manager.has_theme(theme):
                available = self._theme_manager.list_themes()
                raise ThemeNotFoundError(
                    f"Theme '{theme}' not found. "
                    f"Available themes: {', '.join(available)}. "
                    f"See: https://docs.vfwidgets.com/themes"
                )

        # Apply theme with validation
        super().set_theme(theme, persist=persist)

    def get_available_themes(self) -> dict[str, ThemeInfo]:
        """Get all available themes with metadata.

        Returns:
            Dictionary mapping theme name to ThemeInfo

        Example:
            >>> themes = app.get_available_themes()
            >>> for name, info in themes.items():
            ...     print(f"{name}: {info.type} theme by {info.author}")
        """
        # Return rich theme information

    def suggest_theme(self, *, prefer_dark: bool = False) -> Optional[str]:
        """Get suggested theme name based on preferences.

        Args:
            prefer_dark: Prefer dark themes

        Returns:
            Suggested theme name, or None if no themes available

        Example:
            >>> theme = app.suggest_theme(prefer_dark=True)
            >>> if theme:
            ...     app.set_theme(theme)
        """
        # Intelligent theme suggestion based on:
        # - User preference (prefer_dark)
        # - System theme (if detectable)
        # - Previously used theme
        # - Theme quality/popularity

    def _build_theme_config(
        self,
        theme: Optional[str],
        theme_config: Optional[ThemeConfig],
        prefer_dark: bool,
        prefer_light: bool,
    ) -> ThemeConfig:
        """Build validated theme config from parameters."""
        if theme_config:
            return theme_config

        # Explicit theme specified
        if theme:
            return ThemeConfig(
                default_theme=theme,
                persist_theme=False,  # Don't override explicit choice
                auto_detect_system=False,
            )

        # Preference specified
        if prefer_dark:
            return ThemeConfig(
                default_theme="dark",
                persist_theme=False,  # Don't override preference
                auto_detect_system=False,
            )

        if prefer_light:
            return ThemeConfig(
                default_theme="light",
                persist_theme=False,
                auto_detect_system=False,
            )

        # Default: use system theme or saved preference
        return ThemeConfig(
            auto_detect_system=True,
            persist_theme=True,
        )
```

**Error Classes:**

```python
class ThemeError(Exception):
    """Base class for theme-related errors."""
    pass

class ThemeNotFoundError(ThemeError):
    """Raised when requested theme doesn't exist."""

    def __init__(self, message: str, available_themes: Optional[list[str]] = None):
        super().__init__(message)
        self.available_themes = available_themes
```

---

### SingleInstanceApplication Improvements

**Current Problems:**
1. `prefer_dark` doesn't work due to theme persistence override
2. No way to detect if primary or secondary instance before init
3. No timeout configuration for IPC

**Improved API Design:**

```python
class SingleInstanceApplication(ThemedApplication):
    """Application ensuring only one instance runs.

    Automatically handles IPC between instances.
    """

    def __init__(
        self,
        argv: list[str],
        *,
        app_id: str,
        theme: Optional[str] = None,
        prefer_dark: bool = False,
        theme_config: Optional[ThemeConfig] = None,
        ipc_timeout: int = 5000,
    ):
        """Initialize single-instance application.

        Args:
            argv: Command-line arguments
            app_id: Unique application identifier
            theme: Specific theme to use
            prefer_dark: Prefer dark theme
            theme_config: Advanced theme configuration
            ipc_timeout: IPC connection timeout in ms (default: 5000)

        Example:
            >>> app = MyApp(sys.argv, app_id="myapp", prefer_dark=True)
            >>> if not app.is_primary_instance:
            ...     # Send message to primary and exit
            ...     app.send_to_primary({"action": "focus"})
            ...     sys.exit(0)
            >>> sys.exit(app.exec())
        """
        # Build theme config that respects prefer_dark
        if prefer_dark and not theme and not theme_config:
            theme_config = ThemeConfig(
                default_theme="dark",
                persist_theme=False,  # Preference overrides persistence
                auto_detect_system=False,
            )

        super().__init__(
            argv,
            theme=theme,
            theme_config=theme_config,
        )

        self._app_id = app_id
        self._ipc_timeout = ipc_timeout
        self._is_primary = self._create_local_server()

    @classmethod
    def is_already_running(cls, app_id: str) -> bool:
        """Check if instance is already running (without creating app).

        Useful for checking before creating QApplication.

        Args:
            app_id: Application identifier

        Returns:
            True if instance already running

        Example:
            >>> if SingleInstanceApplication.is_already_running("myapp"):
            ...     print("Already running!")
            ...     sys.exit(1)
        """
        # Check without creating QApplication

    def send_to_primary(
        self,
        message: dict,
        *,
        timeout: Optional[int] = None,
        wait_for_response: bool = True,
    ) -> int:
        """Send message to primary instance.

        Args:
            message: Dictionary to send (will be JSON-encoded)
            timeout: Override default IPC timeout
            wait_for_response: Wait for acknowledgment

        Returns:
            Exit code: 0 on success, 1 on failure

        Example:
            >>> if not app.is_primary_instance:
            ...     app.send_to_primary({
            ...         "action": "open",
            ...         "file": "/path/to/file"
            ...     })
            ...     sys.exit(0)
        """
        return self.send_to_running_instance(
            message,
            timeout=timeout or self._ipc_timeout,
        )
```

---

## Implementation Strategy

### Phase 1: Core API Improvements (2 weeks)

**Priority:** Foundation that other improvements build on

1. **ViloCodeWindow Menu API** (3 days)
   - Implement `add_menu()` with auto-creation
   - Implement MenuBuilder fluent interface
   - Implement `_ensure_menu_bar()` and lazy integration
   - Add validation and warnings

2. **ThemedApplication API** (2 days)
   - Fix initialization bug (move `_is_initialized`)
   - Add theme validation and ThemeNotFoundError
   - Fix `prefer_dark` to override persistence
   - Add `suggest_theme()` helper

3. **SingleInstanceApplication API** (1 day)
   - Fix `prefer_dark` to work correctly
   - Add `is_already_running()` class method
   - Add `send_to_primary()` convenience method

4. **TitleBar Auto-Theming** (2 days)
   - Listen to theme changes automatically
   - Auto-update menu bar styling
   - Remove need for manual showEvent handling

**Deliverables:**
- All APIs implemented
- Unit tests for new methods
- Integration tests for workflows
- Updated examples

---

### Phase 2: Documentation & Migration (1 week)

**Priority:** Help developers use new APIs

1. **Quick Start Guides** (2 days)
   - ViloCodeWindow with menus (5-minute guide)
   - ThemedApplication basics (5-minute guide)
   - SingleInstanceApplication (5-minute guide)

2. **API Reference** (2 days)
   - Document all new methods with examples
   - Add "See Also" cross-references
   - Include common patterns section

3. **Migration Guide** (1 day)
   - Old pattern → New pattern examples
   - Automated migration script (if possible)
   - Deprecation warnings in old methods

**Deliverables:**
- docs/vilocode-window-QUICKSTART.md
- docs/themed-application-QUICKSTART.md
- docs/MIGRATION-v2.0.md
- Deprecation warnings in code

---

### Phase 3: Extended Widgets (2 weeks)

**Priority:** Apply DX principles to other widgets

1. **Audit All Widgets** (2 days)
   - Review API surface of each widget
   - Identify DX issues similar to menu bar
   - Prioritize improvements

2. **Apply Patterns** (8 days)
   - Add zero-config defaults where missing
   - Add fluent interfaces where appropriate
   - Add validation and error messages
   - Ensure theme integration automatic

**Widgets to Review:**
- ChromeTabbedWindow
- MarkdownViewer
- TerminalWidget
- MultiSplitWidget
- ActivityBar, SideBar, AuxiliaryBar

**Deliverables:**
- DX audit report for each widget
- Improved APIs for identified issues
- Updated documentation

---

### Phase 4: Developer Tools (1 week)

**Priority:** Make debugging easier

1. **Widget Inspector** (3 days)
   - Runtime inspection of widget tree
   - Theme color viewer
   - Layout debugger

2. **Error Messages** (2 days)
   - Review all error messages
   - Add suggestions for fixes
   - Link to documentation

**Deliverables:**
- WidgetInspector utility
- Improved error messages throughout
- Debugging guide in documentation

---

## Success Metrics

### Quantitative

- **Time to first working app:** < 5 minutes (from docs)
- **Lines of code:** Reduce by 50% for common tasks
- **API calls:** ≤ 3 method calls for common operations
- **Documentation coverage:** 100% of public APIs
- **Test coverage:** > 90% for new APIs

### Qualitative

- **"It just works":** Developers successful without reading docs
- **Clear errors:** Error messages lead to solution immediately
- **No surprises:** Behavior matches expectations
- **Discoverable:** IDE autocomplete reveals capabilities

---

## Conclusion

**The Goal:** Make VFWidgets the easiest Qt framework to use.

**The Strategy:**
1. Design APIs that make the right thing easy
2. Provide multiple layers (simple → advanced)
3. Automate integration and theming
4. Fail fast with helpful errors
5. Document with runnable examples

**The Outcome:** Developers build apps in minutes, not hours.

Let's build widgets that are a joy to use. 🚀
