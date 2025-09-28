# ChromeTabbedWindow Platform Notes

## Overview

ChromeTabbedWindow automatically detects and adapts to the host platform. This document details platform-specific behavior, capabilities, and considerations for each supported platform.

## Platform Detection

ChromeTabbedWindow uses a multi-layered detection strategy:

```python
# Detection hierarchy
1. Operating System (Windows, macOS, Linux)
2. Window System (X11, Wayland, Cocoa, Win32)
3. Environment (Native, WSL, Docker, VM)
4. Compositor/WM (KDE, GNOME, XFCE, etc.)
5. Qt Version and Capabilities
```

## Platform Capabilities

### Capability Structure

```python
@dataclass
class PlatformCapabilities:
    """Platform capability detection results"""

    # Window management
    supports_frameless: bool           # Can create frameless windows
    supports_system_move: bool         # Native window dragging
    supports_system_resize: bool       # Native window resizing
    supports_client_side_decorations: bool  # Custom title bar

    # Visual features
    has_native_shadows: bool          # Window shadows without borders
    supports_transparency: bool       # Alpha channel support
    supports_blur_behind: bool        # Backdrop blur effects

    # System integration
    supports_global_menu: bool        # macOS/Unity global menu
    supports_taskbar_progress: bool   # Progress in taskbar
    supports_jump_lists: bool         # Windows jump lists

    # Environment
    running_under_wsl: bool           # WSL detection
    running_under_wayland: bool       # Wayland session
    running_under_x11: bool           # X11 session
    compositor_name: str              # KDE, GNOME, etc.
```

## Windows Platform

### Windows 10/11 Features

#### Full Support
- ✅ Frameless windows with DWM composition
- ✅ Native shadows and transparency
- ✅ Aero Snap (Windows + Arrow keys)
- ✅ System move/resize via Qt 6.5+ APIs
- ✅ Per-monitor DPI awareness
- ✅ Taskbar thumbnail previews
- ✅ Jump lists (future)

#### Implementation Details

```python
class WindowsPlatformAdapter:
    def setup_window(self, window):
        """Windows-specific setup"""

        # Enable DWM composition
        if self.is_windows_10_or_later():
            # Use modern DWM APIs
            window.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowSystemMenuHint |
                Qt.WindowMinMaxButtonsHint
            )

            # Enable native shadows
            self.enable_dwm_shadow(window)

            # Set up hit testing for resize
            self.setup_nonclient_area(window)

        # Enable Aero Snap
        self.enable_aero_snap(window)

        # High DPI support
        window.setAttribute(Qt.AA_EnableHighDpiScaling)
```

#### Windows 7/8 Compatibility
- Falls back to classic window frame if DWM unavailable
- No transparency effects
- Basic window management only

#### Known Issues
1. **Multiple Monitors**: DPI changes when moving between monitors handled automatically
2. **Dark Mode**: Follows system theme via Qt palette
3. **Touch Input**: Full touch support including gestures

### Windows-Specific Code

```python
# Detecting Windows version
def get_windows_version():
    import sys
    if sys.platform == 'win32':
        import platform
        version = platform.version()
        major = int(version.split('.')[0])
        build = int(version.split('.')[2])

        if major >= 10:
            if build >= 22000:
                return "Windows 11"
            else:
                return "Windows 10"
    return None

# Aero Snap handling
def handle_windows_snap(window, edge):
    """Handle Windows Aero Snap"""
    if edge == "left":
        # Snap to left half
        screen = window.screen()
        available = screen.availableGeometry()
        window.setGeometry(
            available.x(),
            available.y(),
            available.width() // 2,
            available.height()
        )
```

## macOS Platform

### macOS 10.14+ Features

#### Full Support
- ✅ Native fullscreen mode
- ✅ Traffic light buttons
- ✅ Unified toolbar appearance
- ✅ System move via title bar
- ✅ Native shadows
- ✅ Dark mode support

#### Implementation Details

```python
class MacOSPlatformAdapter:
    def setup_window(self, window):
        """macOS-specific setup"""

        # macOS prefers native title bar
        if self.should_use_native_titlebar():
            # Keep native traffic lights
            window.setWindowFlags(Qt.Window)
        else:
            # Custom frameless
            window.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowFullscreenButtonHint
            )

        # Enable native fullscreen
        window.setAttribute(Qt.WA_MacNormalFullScreen)

        # Unified toolbar look
        window.setUnifiedTitleAndToolBarOnMac(True)
```

#### macOS-Specific Behavior
1. **Fullscreen**: Uses native fullscreen spaces
2. **Menu Bar**: Integrates with global menu bar
3. **Gestures**: Supports trackpad gestures
4. **Notch**: Safe area handling for MacBooks with notch

### macOS-Specific Code

```python
# Fullscreen handling
def toggle_macos_fullscreen(window):
    """Toggle native macOS fullscreen"""
    if window.isFullScreen():
        window.showNormal()
    else:
        window.showFullScreen()

# Traffic light customization
def customize_traffic_lights(window):
    """Customize traffic light button behavior"""
    # This requires Objective-C bridge
    # Example with PyObjC (if available):
    try:
        from AppKit import NSWindow
        ns_window = window.winId()
        # Customize button behavior
    except ImportError:
        pass  # PyObjC not available
```

## Linux Platform

### X11 Session

#### Full Support
- ✅ Frameless windows
- ✅ System move/resize (via _NET_WM)
- ✅ Window manager hints
- ✅ EWMH compliance
- ✅ Compositor effects (if available)

#### Implementation

```python
class LinuxX11Adapter:
    def setup_window(self, window):
        """X11-specific setup"""

        # Set window type hint
        window.setWindowFlags(Qt.FramelessWindowHint)

        # EWMH hints for window managers
        self.set_ewmh_hints(window)

        # Enable compositor effects if available
        if self.has_compositor():
            self.enable_transparency(window)
            self.enable_shadows(window)

    def detect_window_manager(self):
        """Detect running window manager"""
        # Check _NET_WM_NAME
        wm_name = self.get_wm_name()

        return {
            'kwin': 'KDE',
            'mutter': 'GNOME',
            'xfwm4': 'XFCE',
            'openbox': 'Openbox',
            'i3': 'i3wm'
        }.get(wm_name, 'Unknown')
```

### Wayland Session

#### Conditional Support
- ⚠️ Frameless (compositor-dependent)
- ⚠️ System move/resize (requires Qt 6.5+)
- ✅ Client-side decorations
- ❌ Global coordinates (security restriction)
- ⚠️ Window positioning (compositor-controlled)

#### Implementation

```python
class LinuxWaylandAdapter:
    def setup_window(self, window):
        """Wayland-specific setup"""

        # Check Qt version for native support
        if QT_VERSION >= 0x060500:  # Qt 6.5+
            # Use native Wayland APIs
            window.setWindowFlags(Qt.FramelessWindowHint)

            # Request xdg-decoration if available
            if self.supports_server_side_decorations():
                self.request_server_decorations(window)
            else:
                # Fall back to client-side decorations
                self.setup_client_decorations(window)
        else:
            # Older Qt - use native decorations
            window.setWindowFlags(Qt.Window)
            print("Wayland: Using native decorations (Qt < 6.5)")
```

### Desktop Environment Specific

#### KDE Plasma
```python
# KDE-specific features
- KWin effects integration
- Plasma theme following
- Activities support
- KDE Connect integration (future)
```

#### GNOME Shell
```python
# GNOME-specific features
- CSD (Client-Side Decorations) preferred
- HeaderBar style support
- GNOME Shell extensions compatibility
- Adwaita theme integration
```

#### XFCE
```python
# XFCE-specific features
- Lighter resource usage
- XFWM4 compositor support
- Traditional window decorations
```

### Linux-Specific Code

```python
# Desktop environment detection
def detect_desktop_environment():
    """Detect the current desktop environment"""
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '')

    if 'KDE' in desktop:
        return 'KDE'
    elif 'GNOME' in desktop:
        return 'GNOME'
    elif 'XFCE' in desktop:
        return 'XFCE'
    else:
        # Check for window manager
        return detect_window_manager()

# Wayland detection
def is_wayland_session():
    """Check if running under Wayland"""
    return os.environ.get('XDG_SESSION_TYPE') == 'wayland'

# X11 window properties
def set_x11_window_type(window, window_type):
    """Set X11 window type hint"""
    # Requires X11 extras
    try:
        from PySide6.QtX11Extras import QX11Info
        # Set _NET_WM_WINDOW_TYPE
    except ImportError:
        pass
```

## WSL/WSLg Platform

### WSL2 with WSLg Support

#### Limited Support
- ⚠️ Frameless (may not work reliably)
- ⚠️ System move/resize (limited)
- ❌ Native shadows (no compositor)
- ⚠️ Transparency (depends on X server)
- ✅ Basic window management

#### Implementation

```python
class WSLPlatformAdapter:
    def setup_window(self, window):
        """WSL-specific setup"""

        # Detect WSLg vs WSL1
        if self.is_wslg():
            # WSLg has better support
            if self.test_frameless_support():
                window.setWindowFlags(Qt.FramelessWindowHint)
            else:
                # Fall back to native
                window.setWindowFlags(Qt.Window)
                print("WSLg: Frameless not reliable, using native")
        else:
            # WSL1 - always use native
            window.setWindowFlags(Qt.Window)
            print("WSL1: Using native decorations")

        # Disable features that don't work in WSL
        self.disable_transparency(window)
        self.disable_shadows(window)
```

### WSL Detection

```python
def detect_wsl():
    """Comprehensive WSL detection"""

    # Method 1: Check for Microsoft in kernel version
    with open('/proc/version', 'r') as f:
        if 'microsoft' in f.read().lower():
            return True

    # Method 2: Check for WSL-specific files
    if os.path.exists('/mnt/wslg'):
        return 'WSLg'
    elif os.path.exists('/mnt/c'):
        return 'WSL'

    return False
```

### WSL-Specific Considerations

1. **File System**: Use `/mnt/c/` for Windows files
2. **Display Server**: X11 via WSLg or X server
3. **Performance**: May be slower than native
4. **Clipboard**: Shared with Windows
5. **GPU**: Hardware acceleration if supported

## Docker/Container Environments

### Detection and Adaptation

```python
def detect_container():
    """Detect if running in container"""

    # Check for Docker
    if os.path.exists('/.dockerenv'):
        return 'docker'

    # Check for Kubernetes
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        return 'kubernetes'

    # Check cgroup
    with open('/proc/1/cgroup', 'r') as f:
        if 'docker' in f.read():
            return 'docker'

    return None
```

### Container Limitations
- No frameless support
- No system integration
- Limited clipboard access
- Display via X11 forwarding or VNC

## Cross-Platform Testing

### Test Matrix

| Platform | Version | Frameless | Move | Resize | Shadows |
|----------|---------|-----------|------|--------|---------|
| Windows 11 | 22H2 | ✅ | ✅ | ✅ | ✅ |
| Windows 10 | 21H2 | ✅ | ✅ | ✅ | ✅ |
| macOS 14 | Sonoma | ✅ | ✅ | ✅ | ✅ |
| macOS 13 | Ventura | ✅ | ✅ | ✅ | ✅ |
| Ubuntu 22.04 | X11 | ✅ | ✅ | ✅ | ⚠️ |
| Ubuntu 22.04 | Wayland | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Fedora 38 | Wayland | ⚠️ | ⚠️ | ⚠️ | ❌ |
| KDE Neon | X11 | ✅ | ✅ | ✅ | ✅ |
| WSL2 | WSLg | ⚠️ | ⚠️ | ⚠️ | ❌ |

### Platform-Specific Test Code

```python
import pytest
import platform

class TestPlatformBehavior:
    """Platform-specific tests"""

    @pytest.mark.skipif(
        platform.system() != 'Windows',
        reason="Windows-only test"
    )
    def test_windows_aero_snap(self):
        """Test Aero Snap on Windows"""
        window = ChromeTabbedWindow()
        # Test snap behavior

    @pytest.mark.skipif(
        platform.system() != 'Darwin',
        reason="macOS-only test"
    )
    def test_macos_fullscreen(self):
        """Test native fullscreen on macOS"""
        window = ChromeTabbedWindow()
        window.showFullScreen()
        assert window.isFullScreen()

    @pytest.mark.skipif(
        not is_wayland_session(),
        reason="Wayland-only test"
    )
    def test_wayland_decorations(self):
        """Test Wayland client-side decorations"""
        window = ChromeTabbedWindow()
        # Test CSD behavior
```

## Fallback Strategies

### Graceful Degradation

```python
class PlatformFallback:
    """Fallback strategies for unsupported features"""

    def setup_with_fallback(self, window):
        """Progressive enhancement approach"""

        # Try frameless first
        if self.try_frameless(window):
            print("Using frameless mode")
        elif self.try_borderless(window):
            print("Using borderless mode")
        else:
            print("Using native decorations")
            window.setWindowFlags(Qt.Window)

        # Try system move
        if not self.try_system_move(window):
            print("Using manual move implementation")
            self.setup_manual_move(window)

        # Try shadows
        if not self.try_native_shadows(window):
            print("Drawing custom shadow border")
            self.draw_shadow_border(window)
```

### Feature Detection

```python
def detect_feature_support():
    """Runtime feature detection"""

    features = {
        'frameless': test_frameless_window(),
        'system_move': test_system_move(),
        'system_resize': test_system_resize(),
        'transparency': test_transparency(),
        'blur': test_blur_behind(),
        'shadows': test_native_shadows()
    }

    return features

def test_frameless_window():
    """Test if frameless windows work"""
    try:
        test_window = QWidget()
        test_window.setWindowFlags(Qt.FramelessWindowHint)
        test_window.setAttribute(Qt.WA_DontShowOnScreen)
        test_window.show()
        success = test_window.isVisible()
        test_window.close()
        return success
    except:
        return False
```

## Performance Considerations

### Platform-Specific Optimizations

```python
class PlatformOptimizer:
    """Platform-specific performance optimizations"""

    def optimize_for_platform(self, window):
        system = platform.system()

        if system == "Windows":
            # Use Direct2D rendering
            window.setAttribute(Qt.WA_PaintOnScreen, False)

        elif system == "Darwin":
            # Use Core Animation layers
            window.setAttribute(Qt.WA_MacNormalFullScreen)

        elif system == "Linux":
            if is_wayland_session():
                # Minimize surface commits
                window.setAttribute(Qt.WA_DontCreateNativeChildren)
            else:
                # Use X11 backing store
                window.setAttribute(Qt.WA_X11NetWmWindowType)
```

## Debugging Platform Issues

### Diagnostic Information

```python
def get_platform_diagnostics():
    """Comprehensive platform diagnostics"""

    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'qt_version': QT_VERSION_STR,
        'display_server': detect_display_server(),
        'desktop_env': detect_desktop_environment(),
        'dpi': QApplication.primaryScreen().logicalDotsPerInch(),
        'screens': QApplication.screens(),
        'capabilities': detect_capabilities()
    }

    return json.dumps(info, indent=2)

# Usage
print("Platform Diagnostics:")
print(get_platform_diagnostics())
```

### Common Issues by Platform

#### Windows
- **Issue**: DWM disabled
  - **Solution**: Check Windows visual effects settings

- **Issue**: Scaling issues on HiDPI
  - **Solution**: Enable Qt HighDPI scaling

#### macOS
- **Issue**: Permission dialogs
  - **Solution**: Code sign the application

- **Issue**: Notch interference
  - **Solution**: Use safe area layout guides

#### Linux
- **Issue**: No window shadows
  - **Solution**: Enable compositor

- **Issue**: Wayland restrictions
  - **Solution**: Fall back to X11 or use native decorations

#### WSL
- **Issue**: Poor performance
  - **Solution**: Use WSL2 with WSLg

- **Issue**: No GPU acceleration
  - **Solution**: Enable GPU passthrough in WSL2

## See Also

- [API Reference](api.md) - Public API documentation
- [Architecture](architecture.md) - Internal architecture
- [Usage Guide](usage.md) - Usage patterns and examples
- [Extension Guide](extension-guide.md) - Future extensibility