# Phase 2: Window Mode Tasks (Weeks 3-4)

## Overview
Implement Chrome-style visual rendering, frameless window support, and native window management integration.

## Prerequisites
- Phase 1 complete (QTabWidget API working)
- MVC architecture established
- Platform detection functional

## Success Criteria
- [ ] Chrome-style tab rendering
- [ ] Smooth animations (60 FPS)
- [ ] Frameless window mode working
- [ ] Native move/resize integration
- [ ] Window controls (min/max/close)
- [ ] Automatic mode switching (top-level vs embedded)

---

## 1. Chrome Tab Rendering

### 1.1 Tab Shape Definition
```python
# In components/renderer.py
- [ ] Define Chrome tab shape path
- [ ] Implement curved corners (top-left, top-right)
- [ ] Calculate tab overlap regions
- [ ] Handle tab z-ordering
- [ ] Create hover shape variations
```

### 1.2 Tab Renderer Implementation
```python
class ChromeTabRenderer:
- [ ] draw_tab_background(painter, rect, state)
- [ ] draw_tab_text(painter, rect, text, state)
- [ ] draw_tab_icon(painter, rect, icon, state)
- [ ] draw_close_button(painter, rect, state)
- [ ] draw_tab_separator(painter, rect)
- [ ] get_tab_path(rect, state) -> QPainterPath
```

### 1.3 Tab States
- [ ] Normal state rendering
- [ ] Hover state rendering
- [ ] Selected state rendering
- [ ] Pressed state rendering
- [ ] Disabled state rendering

### 1.4 Visual Constants
```python
# In core/constants.py
- [ ] TAB_HEIGHT = 36
- [ ] TAB_MIN_WIDTH = 100
- [ ] TAB_MAX_WIDTH = 250
- [ ] TAB_OVERLAP = 16
- [ ] TAB_CURVE_RADIUS = 8
- [ ] CLOSE_BUTTON_SIZE = 16
```

---

## 2. Chrome Tab Bar Implementation

### 2.1 Enhanced Tab Bar
```python
# In components/tab_bar.py (enhance from Phase 1)
class ChromeTabBar(QWidget):
- [ ] Replace basic rendering with ChromeTabRenderer
- [ ] Implement tab layout algorithm
- [ ] Handle tab overflow (scrolling)
- [ ] Add new tab button (+)
- [ ] Implement tab drag preview
```

### 2.2 Tab Layout
- [ ] Calculate tab positions
- [ ] Handle variable width tabs
- [ ] Implement tab compression when many tabs
- [ ] Handle tab overflow with scroll buttons
- [ ] Position new tab button

### 2.3 Mouse Interaction
- [ ] Hover detection and effects
- [ ] Click hit testing (including close button)
- [ ] Drag initiation detection
- [ ] Double-click handling
- [ ] Middle-click to close

### 2.4 Tab Animation
```python
# In components/animator.py
- [ ] Create TabAnimator class
- [ ] Implement tab insertion animation
- [ ] Implement tab removal animation
- [ ] Implement tab reorder animation
- [ ] Implement hover animations
- [ ] Use QPropertyAnimation for smooth transitions
```

---

## 3. Frameless Window Support

### 3.1 Window Mode Detection
```python
# In chrome_tabbed_window.py
- [ ] Detect top-level mode (parent == None)
- [ ] Detect embedded mode (parent != None)
- [ ] Switch behavior based on mode
- [ ] Handle reparenting
```

### 3.2 Frameless Setup
```python
# When in top-level mode:
- [ ] Set Qt.FramelessWindowHint
- [ ] Set Qt.WindowSystemMenuHint
- [ ] Handle Qt.WindowMinMaxButtonsHint
- [ ] Set appropriate window attributes
- [ ] Enable transparency if supported
```

### 3.3 Custom Title Bar
```python
# In components/title_bar.py
- [ ] Create integrated title bar area
- [ ] Merge with tab bar visually
- [ ] Reserve space for window controls
- [ ] Handle window title display
```

---

## 4. Window Controls

### 4.1 Control Buttons
```python
# In components/window_controls.py
- [ ] Create WindowControls widget
- [ ] Implement minimize button
- [ ] Implement maximize/restore button
- [ ] Implement close button
- [ ] Platform-appropriate styling
```

### 4.2 Button Styling
- [ ] Windows style (right side, square)
- [ ] macOS style (left side, traffic lights)
- [ ] Linux style (configurable)
- [ ] Hover effects
- [ ] Pressed states

### 4.3 Button Functionality
- [ ] Connect minimize to showMinimized()
- [ ] Connect maximize to showMaximized()/showNormal()
- [ ] Connect close to close()
- [ ] Handle maximize/restore toggle
- [ ] Update button states

---

## 5. Native Window Management

### 5.1 Window Move Implementation
```python
# In platform adapters
- [ ] Detect drag in empty tab bar area
- [ ] Call window.windowHandle().startSystemMove() (Qt 6.5+)
- [ ] Fallback to manual move for older Qt
- [ ] Handle drag threshold
```

### 5.2 Window Resize Implementation
```python
- [ ] Detect mouse at window edges
- [ ] Set appropriate cursor
- [ ] Call window.windowHandle().startSystemResize(edge)
- [ ] Define edge detection margins (8px)
- [ ] Handle corner resize
```

### 5.3 Hit Testing
```python
# In chrome_tabbed_window.py
- [ ] Override nativeEvent() for Windows
- [ ] Implement hitTest() method
- [ ] Return appropriate hit test results
- [ ] Handle tab area vs empty area
```

---

## 6. Platform-Specific Window Features

### 6.1 Windows Platform Adapter
```python
# In platform/windows.py
- [ ] Create WindowsPlatformAdapter
- [ ] Enable DWM composition
- [ ] Add window shadow
- [ ] Handle Aero Snap zones
- [ ] Support Windows 10/11 features
```

### 6.2 macOS Platform Adapter
```python
# In platform/macos.py
- [ ] Create MacOSPlatformAdapter
- [ ] Handle traffic light buttons
- [ ] Support native fullscreen
- [ ] Unified title bar appearance
```

### 6.3 Linux Platform Adapters
```python
# In platform/linux_x11.py
- [ ] Create LinuxX11Adapter
- [ ] Set EWMH window hints
- [ ] Handle compositor effects

# In platform/linux_wayland.py
- [ ] Create LinuxWaylandAdapter
- [ ] Handle Wayland restrictions
- [ ] Client-side decorations
```

### 6.4 Fallback Adapter
```python
# In platform/fallback.py
- [ ] Create FallbackAdapter
- [ ] Use native window decorations
- [ ] Disable unsupported features
- [ ] Provide basic functionality
```

---

## 7. Visual Polish

### 7.1 Colors and Theming
```python
# In components/theme.py
- [ ] Define default Chrome colors
- [ ] Support dark mode
- [ ] Use Qt palette when possible
- [ ] Define color constants
```

### 7.2 Shadows and Effects
- [ ] Tab shadows
- [ ] Window shadow (if supported)
- [ ] Subtle gradients
- [ ] Focus indicators

### 7.3 Animations
- [ ] Tab switch animation
- [ ] Tab hover fade-in
- [ ] Close button appear/disappear
- [ ] Window control hover effects
- [ ] 60 FPS target

---

## 8. Integration and Coordination

### 8.1 Mode Switching
- [ ] Detect parent changes
- [ ] Switch between modes dynamically
- [ ] Update UI appropriately
- [ ] Maintain state during switch

### 8.2 Layout Management
```python
# In chrome_tabbed_window.py
- [ ] Create proper layout hierarchy
- [ ] Handle title bar integration
- [ ] Position window controls
- [ ] Manage content area
- [ ] Handle margin adjustments
```

### 8.3 Event Handling
- [ ] Mouse events for window management
- [ ] Keyboard shortcuts
- [ ] Focus management
- [ ] Paint events
- [ ] Resize events

---

## 9. Testing

### 9.1 Visual Testing
- [ ] Chrome appearance matches reference
- [ ] Animations smooth (60 FPS)
- [ ] All states render correctly
- [ ] Dark mode works

### 9.2 Window Mode Testing
- [ ] Frameless window appears
- [ ] Window controls work
- [ ] Move/resize works
- [ ] Mode switching works

### 9.3 Platform Testing
- [ ] Test on Windows 10/11
- [ ] Test on macOS
- [ ] Test on Linux (X11)
- [ ] Test on Linux (Wayland)
- [ ] Test fallback behavior

### 9.4 Integration Testing
- [ ] QTabWidget compatibility maintained
- [ ] Embedded mode still works
- [ ] Parent/child relationships correct
- [ ] Memory management sound

---

## 10. Example Updates

### 10.1 Window Mode Example
```python
# In examples/03_window_mode.py
- [ ] Create frameless window
- [ ] Add multiple tabs
- [ ] Test window controls
- [ ] Test move/resize
```

### 10.2 Mode Switching Example
```python
# In examples/04_mode_switch.py
- [ ] Start embedded
- [ ] Switch to top-level
- [ ] Switch back to embedded
- [ ] Verify behavior changes
```

---

## Validation Checklist

### Before Moving to Phase 3
- [ ] Chrome tabs rendering correctly
- [ ] Animations at 60 FPS
- [ ] Frameless window working
- [ ] Window controls functional
- [ ] Native move/resize working
- [ ] Platform detection choosing right adapter
- [ ] Mode switching works
- [ ] QTabWidget compatibility maintained

### Known Acceptable Limitations for Phase 2
- Platform-specific optimizations minimal
- Some edge cases may not be handled
- Performance not fully optimized
- Advanced features not implemented

---

## Risk Areas

### Technical Risks
1. **Frameless limitations**: Some platforms may not support
2. **Performance**: Animations might be slow
3. **Platform differences**: Behavior may vary

### Mitigation Strategies
1. **Graceful degradation**: Fall back to native
2. **Performance monitoring**: Profile early
3. **Platform testing**: Test on all platforms

---

## Daily Goals

### Day 1-2: Chrome Rendering
- Implement tab shape
- Basic Chrome renderer
- Integrate with tab bar

### Day 3-4: Animations
- Tab animations
- Hover effects
- Smooth transitions

### Day 5-6: Frameless Window
- Frameless setup
- Window controls
- Title bar integration

### Day 7-8: Native Integration
- Window move/resize
- Platform adapters
- Hit testing

### Day 9-10: Polish
- Visual refinement
- Testing
- Bug fixes

---

**End of Phase 2: Chrome-style window with native integration complete!**