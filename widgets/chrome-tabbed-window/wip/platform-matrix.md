# Platform Testing Matrix

## Overview
Comprehensive platform testing requirements for ChromeTabbedWindow v1.0.

---

## Supported Platforms

### Primary Platforms (Must Work Perfectly)

| Platform | Versions | Frameless | Move | Resize | Shadows | Status |
|----------|----------|-----------|------|--------|---------|--------|
| **Windows 11** | 22H2, 23H2 | ✅ | ✅ | ✅ | ✅ | ⬜ |
| **Windows 10** | 21H2, 22H2 | ✅ | ✅ | ✅ | ✅ | ⬜ |
| **macOS 14** | Sonoma | ✅ | ✅ | ✅ | ✅ | ⬜ |
| **macOS 13** | Ventura | ✅ | ✅ | ✅ | ✅ | ⬜ |
| **Ubuntu 22.04** | X11 | ✅ | ✅ | ✅ | ⚠️ | ⬜ |
| **Ubuntu 22.04** | Wayland | ⚠️ | ⚠️ | ⚠️ | ❌ | ⬜ |

### Secondary Platforms (Should Work Well)

| Platform | Versions | Frameless | Move | Resize | Shadows | Status |
|----------|----------|-----------|------|--------|---------|--------|
| **Fedora 38** | Wayland | ⚠️ | ⚠️ | ⚠️ | ❌ | ⬜ |
| **KDE Neon** | X11 | ✅ | ✅ | ✅ | ✅ | ⬜ |
| **Debian 12** | X11 | ✅ | ✅ | ✅ | ⚠️ | ⬜ |
| **Manjaro** | X11/Wayland | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⬜ |
| **macOS 12** | Monterey | ✅ | ✅ | ✅ | ✅ | ⬜ |

### Special Environments (Graceful Degradation)

| Platform | Versions | Frameless | Move | Resize | Shadows | Status |
|----------|----------|-----------|------|--------|---------|--------|
| **WSL2** | WSLg | ⚠️ | ⚠️ | ⚠️ | ❌ | ⬜ |
| **Docker** | X11 Forward | ❌ | ❌ | ❌ | ❌ | ⬜ |
| **VirtualBox** | Various | ⚠️ | ⚠️ | ⚠️ | ❌ | ⬜ |
| **Remote Desktop** | RDP/VNC | ⚠️ | ⚠️ | ⚠️ | ❌ | ⬜ |

**Legend:**
- ✅ Full support expected
- ⚠️ Limited support / Fallback available
- ❌ Not supported / Native decorations used
- ⬜ Not tested yet

---

## Test Scenarios

### Display Configurations

| Configuration | Test Required | Status | Notes |
|---------------|---------------|--------|-------|
| Single Monitor 1080p | ✅ | ⬜ | Base case |
| Single Monitor 4K | ✅ | ⬜ | High DPI |
| Dual Monitor Same DPI | ✅ | ⬜ | Multi-monitor |
| Dual Monitor Mixed DPI | ✅ | ⬜ | DPI handling |
| Triple+ Monitors | ⚠️ | ⬜ | Edge case |
| Vertical Monitor | ⚠️ | ⬜ | Orientation |

### DPI Settings

| Platform | DPI Settings | Test Required | Status |
|----------|-------------|---------------|--------|
| Windows | 100%, 125%, 150%, 200% | ✅ | ⬜ |
| macOS | Retina, Non-Retina | ✅ | ⬜ |
| Linux | 1x, 1.5x, 2x | ✅ | ⬜ |

### Theme Configurations

| Configuration | Test Required | Status | Notes |
|---------------|---------------|--------|-------|
| Light Mode | ✅ | ⬜ | Default |
| Dark Mode | ✅ | ⬜ | System theme |
| High Contrast | ✅ | ⬜ | Accessibility |
| Custom Themes | ⚠️ | ⬜ | QSS support |

---

## Feature Support Matrix

### Windows Features

| Feature | Win 11 | Win 10 | Status | Notes |
|---------|--------|--------|--------|-------|
| Aero Snap | ✅ | ✅ | ⬜ | Window snapping |
| Snap Layouts | ✅ | ❌ | ⬜ | Win 11 only |
| DWM Shadow | ✅ | ✅ | ⬜ | Native shadow |
| Taskbar Preview | ✅ | ✅ | ⬜ | Thumbnail |
| Touch Support | ✅ | ✅ | ⬜ | Touch events |
| Tablet Mode | ✅ | ✅ | ⬜ | Auto-adapt |

### macOS Features

| Feature | macOS 14 | macOS 13 | macOS 12 | Status |
|---------|----------|----------|----------|--------|
| Native Fullscreen | ✅ | ✅ | ✅ | ⬜ |
| Mission Control | ✅ | ✅ | ✅ | ⬜ |
| Stage Manager | ✅ | ✅ | ❌ | ⬜ |
| Traffic Lights | ✅ | ✅ | ✅ | ⬜ |
| Notch Support | ✅ | ✅ | ⚠️ | ⬜ |

### Linux Features

| Feature | X11 | Wayland | Status | Notes |
|---------|-----|---------|--------|-------|
| Compositor Effects | ✅ | ⚠️ | ⬜ | Varies |
| Window Hints | ✅ | ⚠️ | ⬜ | EWMH |
| Global Coordinates | ✅ | ❌ | ⬜ | Security |
| System Move/Resize | ✅ | ⚠️ | ⬜ | Qt 6.5+ |
| CSD/SSD | ✅ | ✅ | ⬜ | Decorations |

---

## Desktop Environment Testing

### Linux Desktop Environments

| DE | Window Manager | Compositor | Test Required | Status |
|----|---------------|------------|---------------|--------|
| GNOME | Mutter | Yes | ✅ | ⬜ |
| KDE Plasma | KWin | Yes | ✅ | ⬜ |
| XFCE | Xfwm4 | Optional | ⚠️ | ⬜ |
| Cinnamon | Muffin | Yes | ⚠️ | ⬜ |
| MATE | Marco | Optional | ⚠️ | ⬜ |
| i3 | i3 | No | ⚠️ | ⬜ |
| Sway | Sway | Yes | ⚠️ | ⬜ |

---

## Test Cases by Platform

### Windows Test Cases

- [ ] Frameless window appears correctly
- [ ] Aero Snap to edges works
- [ ] Aero Snap to corners works
- [ ] Maximize/restore animation smooth
- [ ] DWM shadow visible
- [ ] DPI scaling correct
- [ ] Multi-monitor movement
- [ ] Taskbar preview works
- [ ] Alt+Tab preview correct
- [ ] Touch gestures work

### macOS Test Cases

- [ ] Traffic lights positioned correctly
- [ ] Native fullscreen works
- [ ] Mission Control shows window
- [ ] Spaces behavior correct
- [ ] Stage Manager compatible
- [ ] Notch avoidance works
- [ ] Retina rendering sharp
- [ ] Gestures work
- [ ] Menu bar integration
- [ ] Dark mode follows system

### Linux Test Cases

- [ ] Window manager detection works
- [ ] Compositor effects apply
- [ ] Window hints set correctly
- [ ] Virtual desktops work
- [ ] Alt+Tab shows correctly
- [ ] Theme follows system
- [ ] CSD/SSD negotiation
- [ ] Multi-monitor works
- [ ] DPI scaling correct
- [ ] Input methods work

### WSL Test Cases

- [ ] WSL detection works
- [ ] Fallback to native decorations
- [ ] Basic functionality works
- [ ] Clipboard integration
- [ ] File system access
- [ ] Performance acceptable

---

## Performance Benchmarks by Platform

| Metric | Target | Windows | macOS | Linux | WSL |
|--------|--------|---------|-------|-------|-----|
| Startup Time | < 100ms | ⬜ | ⬜ | ⬜ | ⬜ |
| Tab Switch | < 50ms | ⬜ | ⬜ | ⬜ | ⬜ |
| Tab Create | < 50ms | ⬜ | ⬜ | ⬜ | ⬜ |
| Animation FPS | 60 FPS | ⬜ | ⬜ | ⬜ | ⬜ |
| Memory/Tab | < 1MB | ⬜ | ⬜ | ⬜ | ⬜ |

---

## Known Platform Issues

### Windows Issues
- DPI changes may require restart
- DWM disabled falls back to basic window

### macOS Issues
- Permission prompts for accessibility
- Notch may interfere with tabs

### Linux Issues
- Wayland has many restrictions
- Compositor required for shadows
- Window manager fragmentation

### WSL Issues
- Frameless unreliable
- Performance may be slower
- GPU acceleration varies

---

## Testing Tools

### Automated Testing
```bash
# Platform detection test
pytest tests/platform/test_detection.py

# Platform-specific tests
pytest tests/platform/test_windows.py -m windows
pytest tests/platform/test_macos.py -m macos
pytest tests/platform/test_linux.py -m linux

# Cross-platform tests
pytest tests/integration/
```

### Manual Testing
1. Visual appearance check
2. Interaction testing
3. Performance profiling
4. Memory profiling
5. Multi-monitor testing

---

## CI/CD Matrix

### GitHub Actions Matrix
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.9', '3.10', '3.11', '3.12']
    qt-version: ['6.5', '6.6', '6.7']
```

---

## Acceptance Criteria

### Minimum Requirements
- Works on Windows 10/11
- Works on macOS 13/14
- Works on Ubuntu 22.04 (X11)
- Graceful degradation elsewhere

### Performance Requirements
- 60 FPS animations on all primary platforms
- < 100ms startup on all primary platforms
- No crashes on any platform

---

**Last Updated:** [Current Date]
**Test Coverage:** 0%
**Platforms Validated:** 0/15