# Phase 3: Platform Refinement Tasks (Weeks 5-6)

## Overview
Optimize platform-specific features, handle edge cases, and ensure robust behavior across all supported platforms.

## Prerequisites
- Phase 1 & 2 complete
- Basic Chrome rendering working
- Frameless window functional
- Platform adapters in place

## Success Criteria
- [ ] Windows Aero Snap working perfectly
- [ ] macOS native fullscreen support
- [ ] Linux compositor integration
- [ ] WSL/WSLg graceful fallback
- [ ] All platform quirks handled
- [ ] Smooth experience on all platforms

---

## 1. Windows Platform Optimization

### 1.1 Windows 11 Features
```python
# In platform/windows.py
- [ ] Detect Windows 11 vs Windows 10
- [ ] Use Windows 11 snap layouts
- [ ] Support rounded corners (Windows 11)
- [ ] Handle new maximize behaviors
- [ ] Support auto-hide taskbar
```

### 1.2 Aero Snap Enhancement
- [ ] Detect snap zones correctly
- [ ] Handle half-screen snapping
- [ ] Handle quarter-screen snapping
- [ ] Support snap groups (Windows 11)
- [ ] Restore to pre-snap size
- [ ] Save/restore snap state

### 1.3 DWM Integration
```python
- [ ] Enable DWM shadow properly
- [ ] Handle DWM composition changes
- [ ] Support Windows accent color
- [ ] Handle high contrast mode
- [ ] Support transparency effects
```

### 1.4 DPI Handling
- [ ] Per-monitor DPI awareness
- [ ] Handle DPI change events
- [ ] Scale UI elements correctly
- [ ] Update tab sizes on DPI change
- [ ] Test with multiple monitors

### 1.5 Windows-Specific Features
- [ ] Taskbar thumbnail preview
- [ ] Jump list support (future)
- [ ] Progress indicator (future)
- [ ] Overlay icons (future)

---

## 2. macOS Platform Optimization

### 2.1 Native Integration
```python
# In platform/macos.py
- [ ] Proper traffic light button positioning
- [ ] Handle native fullscreen transition
- [ ] Support Mission Control
- [ ] Handle Spaces correctly
- [ ] Support Stage Manager (macOS 13+)
```

### 2.2 macOS Window Behavior
- [ ] Double-click title bar to minimize
- [ ] Option-click maximize for fullscreen
- [ ] Support native gestures
- [ ] Handle notch on newer MacBooks
- [ ] Safe area management

### 2.3 Visual Integration
- [ ] Match macOS visual style
- [ ] Support vibrancy effects
- [ ] Handle dark mode properly
- [ ] Use native shadows
- [ ] Respect system accent color

### 2.4 Event Handling
- [ ] Handle macOS-specific events
- [ ] Support trackpad gestures
- [ ] Handle menu bar integration
- [ ] Support keyboard shortcuts (Cmd vs Ctrl)

---

## 3. Linux X11 Optimization

### 3.1 Window Manager Detection
```python
# In platform/linux_x11.py
- [ ] Detect window manager (KWin, Mutter, XFWM4, etc.)
- [ ] Apply WM-specific hints
- [ ] Handle different behaviors
- [ ] Test with major DEs
```

### 3.2 EWMH Compliance
- [ ] Set _NET_WM_WINDOW_TYPE
- [ ] Handle _NET_WM_STATE
- [ ] Support _NET_WM_ALLOWED_ACTIONS
- [ ] Implement _MOTIF_WM_HINTS
- [ ] Handle virtual desktops

### 3.3 Compositor Support
- [ ] Detect compositor presence
- [ ] Enable transparency when available
- [ ] Handle compositor on/off
- [ ] Support blur effects (KDE)
- [ ] Handle shadow rendering

### 3.4 X11-Specific Features
- [ ] Handle X11 session management
- [ ] Support X11 clipboard
- [ ] Handle X11 drag and drop
- [ ] Support X11 selections

---

## 4. Linux Wayland Optimization

### 4.1 Wayland Limitations
```python
# In platform/linux_wayland.py
- [ ] Handle no global coordinates
- [ ] Work with window positioning limits
- [ ] Handle decoration negotiation
- [ ] Support xdg-decoration protocol
```

### 4.2 Client-Side Decorations
- [ ] Implement CSD when needed
- [ ] Match desktop theme
- [ ] Handle CSD/SSD negotiation
- [ ] Support headerbar style (GNOME)

### 4.3 Wayland Protocols
- [ ] Use appropriate protocols
- [ ] Handle protocol availability
- [ ] Support portal APIs
- [ ] Handle sandboxing (Flatpak/Snap)

### 4.4 Compositor-Specific
- [ ] Test with GNOME/Mutter
- [ ] Test with KDE/KWin
- [ ] Test with Sway
- [ ] Handle compositor differences

---

## 5. WSL/WSLg Support

### 5.1 WSL Detection
```python
# In platform/wsl.py
- [ ] Detect WSL1 vs WSL2
- [ ] Detect WSLg availability
- [ ] Check for GPU support
- [ ] Detect X server type
```

### 5.2 WSL Fallbacks
- [ ] Disable frameless if unreliable
- [ ] Use native decorations
- [ ] Disable transparency
- [ ] Simplified rendering
- [ ] Handle clipboard properly

### 5.3 WSL-Specific Issues
- [ ] Handle file system differences
- [ ] Work with WSL networking
- [ ] Handle WSL display server
- [ ] Support WSL GPU acceleration

---

## 6. Cross-Platform Edge Cases

### 6.1 Multi-Monitor Support
- [ ] Handle monitor arrangement changes
- [ ] Support different DPI per monitor
- [ ] Handle monitor disconnection
- [ ] Restore to visible monitor
- [ ] Handle resolution changes

### 6.2 Theme Changes
- [ ] Detect system theme changes
- [ ] Update colors dynamically
- [ ] Handle dark/light mode switch
- [ ] Update platform-specific styling

### 6.3 Accessibility
- [ ] Screen reader support
- [ ] High contrast mode
- [ ] Keyboard navigation
- [ ] Focus indicators
- [ ] Tooltip support

### 6.4 Input Methods
- [ ] Handle IME properly
- [ ] Support RTL languages
- [ ] Handle complex text
- [ ] Support input method switching

---

## 7. Performance Optimization

### 7.1 Rendering Performance
- [ ] Profile paint operations
- [ ] Optimize tab rendering
- [ ] Reduce overdraw
- [ ] Cache rendered elements
- [ ] Use hardware acceleration

### 7.2 Animation Performance
- [ ] Ensure 60 FPS consistently
- [ ] Optimize animation paths
- [ ] Reduce animation complexity on weak hardware
- [ ] Profile on different platforms

### 7.3 Memory Optimization
- [ ] Profile memory usage
- [ ] Optimize resource caching
- [ ] Handle many tabs efficiently
- [ ] Clean up properly

### 7.4 Startup Performance
- [ ] Optimize initialization
- [ ] Lazy load features
- [ ] Measure startup time
- [ ] Target < 100ms

---

## 8. Platform Testing Matrix

### 8.1 Windows Testing
```
- [ ] Windows 10 (1909, 2004, 20H2, 21H1, 21H2)
- [ ] Windows 11 (21H2, 22H2)
- [ ] Different DPI settings (100%, 125%, 150%, 200%)
- [ ] Multiple monitors
- [ ] Tablet mode
```

### 8.2 macOS Testing
```
- [ ] macOS 12 Monterey
- [ ] macOS 13 Ventura
- [ ] macOS 14 Sonoma
- [ ] Retina display
- [ ] External monitors
```

### 8.3 Linux Testing
```
- [ ] Ubuntu 20.04, 22.04 (GNOME, X11/Wayland)
- [ ] Fedora 38 (GNOME, Wayland)
- [ ] KDE Neon (KDE, X11)
- [ ] Manjaro (Various DEs)
- [ ] Debian 12
```

### 8.4 Special Environments
```
- [ ] WSL2 with WSLg
- [ ] Docker containers
- [ ] VirtualBox VMs
- [ ] Remote desktop
- [ ] VNC sessions
```

---

## 9. Bug Fixes and Edge Cases

### 9.1 Known Issues List
- [ ] Document all platform-specific issues
- [ ] Create workarounds
- [ ] Test edge cases
- [ ] Handle gracefully

### 9.2 Common Problems
- [ ] Window restore position
- [ ] Maximized state persistence
- [ ] Focus issues
- [ ] Rendering glitches
- [ ] Animation stuttering

### 9.3 Platform Workarounds
- [ ] Windows: DWM disabled
- [ ] macOS: Permission issues
- [ ] Linux: Missing compositor
- [ ] WSL: Display issues

---

## 10. Platform Documentation

### 10.1 Platform Notes Update
- [ ] Document all platform behaviors
- [ ] List known limitations
- [ ] Provide workarounds
- [ ] Include test results

### 10.2 Platform Examples
```python
# In examples/platform_specific/
- [ ] windows_features.py
- [ ] macos_features.py
- [ ] linux_features.py
- [ ] wsl_fallback.py
```

---

## Validation Checklist

### Before Moving to Phase 4
- [ ] All platforms tested thoroughly
- [ ] Platform-specific features working
- [ ] Edge cases handled
- [ ] Performance acceptable on all platforms
- [ ] Fallbacks working correctly
- [ ] Documentation updated

### Platform Feature Matrix
| Feature | Windows | macOS | Linux X11 | Linux Wayland | WSL |
|---------|---------|-------|-----------|---------------|-----|
| Frameless | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| System Move | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| System Resize | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| Shadows | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| Transparency | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| Snap/Fullscreen | ✅ | ✅ | ✅ | ✅ | ⚠️ |

---

## Risk Areas

### Platform Risks
1. **Wayland limitations**: Many features restricted
2. **WSL reliability**: Frameless may not work
3. **Linux fragmentation**: Many WMs/DEs to support

### Mitigation
1. **Graceful degradation**: Always have fallback
2. **Feature detection**: Test capabilities at runtime
3. **User overrides**: Allow disabling features

---

## Daily Goals

### Day 1-3: Windows
- Aero Snap perfection
- DPI handling
- Windows 11 features

### Day 4-6: macOS
- Native fullscreen
- Traffic lights
- Gestures

### Day 7-8: Linux X11
- WM detection
- Compositor support
- EWMH compliance

### Day 9-10: Linux Wayland & WSL
- Wayland workarounds
- WSL fallbacks
- Testing

### Day 11-12: Cross-platform
- Multi-monitor
- Theme changes
- Performance

---

**End of Phase 3: Platform-specific optimization complete!**