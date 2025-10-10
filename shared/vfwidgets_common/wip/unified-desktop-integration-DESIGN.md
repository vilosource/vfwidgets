# Unified Cross-Platform Desktop Integration - Design Document

**Status**: 🚧 Work in Progress
**Created**: 2025-10-10
**Target**: vfwidgets_common 0.2.0

## Problem Statement

VFWidgets applications need to handle multiple cross-platform concerns:

1. **Platform Detection**: WSL, Wayland, X11, Remote Desktop, containers
2. **Desktop Integration**: GNOME/KDE icons and .desktop files, Windows shortcuts, macOS .app bundles
3. **Platform Quirks**: Software rendering in WSL, Wayland scaling, RDP optimizations
4. **Qt Configuration**: WebEngine flags, OpenGL settings, HiDPI handling
5. **Application Identity**: Icons, metadata, system integration

Currently this is **scattered** across:
- `platform.py` - Some detection
- `webengine.py` - WebEngine quirks
- App-specific code - Desktop integration
- Manual setup in each app's `__main__.py`

## Vision: One API to Rule Them All

```python
# This is ALL developers need to write:
from vfwidgets_common.desktop import configure_desktop

def main():
    app = configure_desktop(
        app_name="viloxterm",
        app_display_name="ViloxTerm",
        icon_name="viloxterm",
        desktop_categories="System;TerminalEmulator;",
    )

    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

Behind the scenes, this:
- ✅ Detects platform (Linux/Windows/macOS, WSL, Wayland, etc.)
- ✅ Applies platform-specific workarounds (env vars, Qt flags)
- ✅ Checks desktop integration (icons, shortcuts, .desktop files)
- ✅ Auto-installs integration if missing
- ✅ Sets up application icon
- ✅ Creates configured QApplication
- ✅ Returns ready-to-use app

## Architecture

### Module Structure

```
vfwidgets_common/
└── desktop/                       # NEW unified module
    ├── __init__.py               # Public API exports
    ├── config.py                 # Configuration dataclasses
    ├── environment.py            # Comprehensive environment detection
    ├── configurator.py           # Main orchestrator
    │
    ├── quirks/                   # Platform-specific workarounds
    │   ├── __init__.py          # Quirk registry
    │   ├── base.py              # Abstract quirk base class
    │   ├── wsl.py               # WSL software rendering
    │   ├── wayland.py           # Wayland HiDPI scaling
    │   └── windows_rdp.py       # Windows RDP optimizations
    │
    ├── integration/              # Desktop integration backends
    │   ├── __init__.py
    │   ├── base.py              # Abstract backend
    │   ├── linux_xdg.py         # GNOME/KDE/XFCE (XDG standard)
    │   ├── windows.py           # Windows shortcuts/registry (future)
    │   └── macos.py             # macOS .app bundles (future)
    │
    └── resources/                # Icon and resource loading
        ├── __init__.py
        └── icon_loader.py        # Cross-platform icon loading
```

### Data Structures

```python
@dataclass
class DesktopConfig:
    """Configuration for desktop integration."""
    app_name: str              # "viloxterm"
    app_display_name: str      # "ViloxTerm"
    icon_name: str             # "viloxterm"
    desktop_categories: str    # "System;TerminalEmulator;"
    auto_install: bool = True
    create_application: bool = True
    application_class: type = QApplication
    application_kwargs: dict = field(default_factory=dict)

@dataclass
class EnvironmentInfo:
    """Complete environment information."""
    # OS
    os: str                          # "linux", "windows", "darwin"
    os_version: str

    # Desktop (Linux)
    desktop_env: Optional[str]       # "GNOME", "KDE", "XFCE"
    display_server: Optional[str]    # "wayland", "x11"

    # Special environments
    is_wsl: bool
    is_wsl2: bool
    is_remote_desktop: bool
    is_container: bool
    is_vm: bool

    # Graphics capabilities
    needs_software_rendering: bool
    has_hardware_acceleration: bool

    # Desktop capabilities
    supports_system_tray: bool
    supports_notifications: bool
    supports_global_shortcuts: bool

@dataclass
class IntegrationStatus:
    """Status of desktop integration."""
    is_installed: bool
    has_desktop_file: bool
    has_icon: bool
    missing_files: list[str]
    platform_name: str
```

## Component Design

### 1. Environment Detection (`environment.py`)

Comprehensive detection that consolidates existing `platform.py` functions:

```python
def detect_environment() -> EnvironmentInfo:
    """Detect complete environment information."""
    return EnvironmentInfo(
        os=detect_os(),
        os_version=detect_os_version(),
        desktop_env=detect_desktop_environment(),
        display_server=detect_display_server(),
        is_wsl=detect_wsl(),
        is_wsl2=detect_wsl2(),
        is_remote_desktop=detect_remote_desktop(),
        # ... more detection
    )
```

### 2. Quirk System (`quirks/`)

Platform-specific workarounds as pluggable components:

```python
class PlatformQuirk(ABC):
    """Base class for platform workarounds."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""

    @abstractmethod
    def is_applicable(self, env: EnvironmentInfo) -> bool:
        """Check if this quirk applies."""

    @abstractmethod
    def apply(self) -> dict[str, str]:
        """Apply the quirk, return changed env vars."""

# Example: WSL Quirk
class WSLSoftwareRenderingQuirk(PlatformQuirk):
    name = "WSL Software Rendering"

    def is_applicable(self, env: EnvironmentInfo) -> bool:
        return env.is_wsl

    def apply(self) -> dict[str, str]:
        changes = {}
        os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu ..."
        changes.update(...)
        return changes
```

**Registry**: All quirks registered in `quirks/__init__.py`:

```python
QUIRKS = [
    WSLSoftwareRenderingQuirk(),
    WaylandScalingQuirk(),
    WindowsRDPQuirk(),
    # Easy to add more...
]

def apply_all_quirks(env: EnvironmentInfo) -> dict[str, str]:
    """Apply all applicable quirks."""
    all_changes = {}
    for quirk in QUIRKS:
        if quirk.is_applicable(env):
            logger.info(f"Applying quirk: {quirk.name}")
            changes = quirk.apply()
            all_changes.update(changes)
    return all_changes
```

### 3. Integration Backends (`integration/`)

Platform-specific desktop integration:

```python
class DesktopIntegrationBackend(ABC):
    """Abstract base for platform integration."""

    @abstractmethod
    def check_status(self) -> IntegrationStatus:
        """Check if integration is installed."""

    @abstractmethod
    def install(self) -> bool:
        """Install desktop integration."""

    @abstractmethod
    def setup_icon(self, app: QApplication) -> bool:
        """Set up application icon."""

# Linux Implementation
class LinuxXDGIntegration(DesktopIntegrationBackend):
    """XDG Desktop Entry Specification (GNOME, KDE, XFCE, etc.)"""

    def check_status(self) -> IntegrationStatus:
        desktop_file = Path.home() / ".local/share/applications" / f"{self.app_name}.desktop"
        icon_file = Path.home() / ".local/share/icons/hicolor/scalable/apps" / f"{self.icon_name}.svg"
        # Check files exist...

    def install(self) -> bool:
        # Find and run install-user.sh
        # Or create files directly

    def setup_icon(self, app: QApplication) -> bool:
        # 1. Try QIcon.fromTheme()
        # 2. Try user-installed icon
        # 3. Try bundled icon
```

### 4. Main Configurator (`configurator.py`)

Orchestrates everything:

```python
class DesktopConfigurator:
    """Main desktop configuration orchestrator."""

    def __init__(self, config: DesktopConfig):
        self.config = config
        self.env = detect_environment()
        self.backend = self._select_backend()

    def _select_backend(self) -> DesktopIntegrationBackend:
        if self.env.os == "linux":
            return LinuxXDGIntegration(self.config, self.env)
        elif self.env.os == "windows":
            return WindowsIntegration(self.config, self.env)
        elif self.env.os == "darwin":
            return MacOSIntegration(self.config, self.env)
        return NullIntegration()

    def configure(self) -> QApplication:
        """Main configuration pipeline."""

        # 1. Apply platform quirks
        quirks = apply_all_quirks(self.env)

        # 2. Check integration status
        status = self.backend.check_status()

        # 3. Auto-install if needed
        if not status.is_installed and self.config.auto_install:
            self.backend.install()

        # 4. Create QApplication
        app_class = self.config.application_class
        app = app_class(sys.argv, **self.config.application_kwargs)

        # 5. Set up icon
        self.backend.setup_icon(app)

        # 6. Set metadata
        app.setApplicationName(self.config.app_name)
        app.setApplicationDisplayName(self.config.app_display_name)
        app.setDesktopFileName(self.config.app_name)  # Important for Wayland!

        return app
```

### 5. Public API (`__init__.py`)

Simple interface for developers:

```python
def configure_desktop(
    app_name: str,
    app_display_name: str,
    icon_name: str,
    desktop_categories: Optional[str] = None,
    auto_install: bool = True,
    application_class: type = None,
    **application_kwargs
) -> QApplication:
    """
    Configure desktop integration and create QApplication.

    This handles everything:
    - Platform detection
    - Quirk application
    - Desktop integration
    - Icon setup
    - QApplication creation

    Example:
        app = configure_desktop(
            app_name="viloxterm",
            app_display_name="ViloxTerm",
            icon_name="viloxterm",
            desktop_categories="System;TerminalEmulator;",
        )
    """
    from PySide6.QtWidgets import QApplication

    if application_class is None:
        application_class = QApplication

    config = DesktopConfig(
        app_name=app_name,
        app_display_name=app_display_name,
        icon_name=icon_name,
        desktop_categories=desktop_categories or "",
        auto_install=auto_install,
        application_class=application_class,
        application_kwargs=application_kwargs,
    )

    configurator = DesktopConfigurator(config)
    return configurator.configure()
```

## Migration from Existing Code

### Code to Consolidate

**From `platform.py`** (keep but mark as deprecated):
- `is_wsl()` → `EnvironmentInfo.is_wsl`
- `get_desktop_environment()` → `EnvironmentInfo.desktop_env`
- `needs_software_rendering()` → `EnvironmentInfo.needs_software_rendering`
- `configure_qt_environment()` → Quirk system

**From `webengine.py`** (keep but mark as deprecated):
- `configure_webengine_environment()` → `WSLSoftwareRenderingQuirk`
- `configure_all_for_webengine()` → `configure_desktop()`

**New Capabilities**:
- Desktop file installation
- Icon loading and setup
- Application metadata
- Cross-platform abstractions
- Extensible quirk system

### Backward Compatibility

Existing code continues to work:
```python
# Old way (still works)
from vfwidgets_common import configure_all_for_webengine
configure_all_for_webengine()

# New way (recommended)
from vfwidgets_common.desktop import configure_desktop
app = configure_desktop(...)
```

## Implementation Plan

### Phase 1: Core Structure (This WIP)
- ✅ Create WIP document
- ⏳ Create module structure
- ⏳ Implement `EnvironmentInfo` and detection
- ⏳ Implement quirk base classes

### Phase 2: Quirks (Session 1)
- ⏳ Migrate WSL quirk from `webengine.py`
- ⏳ Add Wayland quirks
- ⏳ Add Windows RDP quirks
- ⏳ Test quirk application

### Phase 3: Integration (Session 2)
- ⏳ Implement `LinuxXDGIntegration`
- ⏳ Test with existing `install-user.sh`
- ⏳ Implement icon loading
- ⏳ Test on GNOME/KDE

### Phase 4: Configurator & API (Session 3)
- ⏳ Implement `DesktopConfigurator`
- ⏳ Implement public API
- ⏳ Add comprehensive tests
- ⏳ Write usage documentation

### Phase 5: Integration (Session 4)
- ⏳ Migrate ViloxTerm to use new API
- ⏳ Test thoroughly
- ⏳ Update documentation
- ⏳ Mark old APIs as deprecated

## Benefits

1. **Single API** - One function call for all desktop concerns
2. **Cross-Platform** - Works on Linux, Windows, macOS (future)
3. **Extensible** - Easy to add new quirks and backends
4. **Maintainable** - All platform code in one place
5. **Testable** - Isolated components, easy to mock
6. **Reusable** - Every VFWidgets app can use it
7. **Self-Healing** - Auto-installs missing integration

## Testing Strategy

1. **Unit Tests** - Each component isolated
2. **Integration Tests** - Full pipeline with mocks
3. **Manual Tests**:
   - Fresh install (no desktop files)
   - WSL environment
   - Wayland vs X11
   - GNOME vs KDE
   - Already installed (idempotent)

## Future Enhancements

- Windows Start Menu shortcuts
- macOS .app bundle integration
- System tray icon management
- Desktop notifications
- Global keyboard shortcuts
- File associations
- Protocol handlers (e.g., `viloxterm://`)

## Notes

- Must be called BEFORE any Qt imports for env var quirks
- Icon loading happens AFTER QApplication creation
- Desktop file installation is optional (auto_install flag)
- Gracefully degrades if integration fails
- Logs everything for debugging
