# Phase 1: Foundation Tasks (Weeks 1-2)

## Overview
Establish the core MVC architecture and achieve 100% QTabWidget API parity in embedded mode.

## Success Criteria
- [ ] All QTabWidget methods implemented
- [ ] All QTabWidget signals working
- [ ] MVC architecture established
- [ ] Platform detection working
- [ ] Embedded mode fully functional

---

## 1. Project Setup & Structure

### 1.1 Core File Structure
- [ ] Create `src/chrome_tabbed_window/chrome_tabbed_window.py` - Main class
- [ ] Create `src/chrome_tabbed_window/core/` directory
- [ ] Create `src/chrome_tabbed_window/core/model.py` - Tab data model
- [ ] Create `src/chrome_tabbed_window/core/types.py` - Data structures
- [ ] Create `src/chrome_tabbed_window/core/constants.py` - Constants/enums

### 1.2 Component Structure
- [ ] Create `src/chrome_tabbed_window/components/` directory
- [ ] Create `src/chrome_tabbed_window/components/tab_bar.py` - Chrome tab bar
- [ ] Create `src/chrome_tabbed_window/components/content_area.py` - Content container
- [ ] Create `src/chrome_tabbed_window/components/renderer.py` - Tab renderer

### 1.3 Platform Structure
- [ ] Create `src/chrome_tabbed_window/platform/` directory
- [ ] Create `src/chrome_tabbed_window/platform/base.py` - Platform interface
- [ ] Create `src/chrome_tabbed_window/platform/detector.py` - Platform detection
- [ ] Create `src/chrome_tabbed_window/platform/capabilities.py` - Capability structure

### 1.4 Utilities
- [ ] Create `src/chrome_tabbed_window/utils/` directory
- [ ] Create `src/chrome_tabbed_window/utils/resources.py` - Resource management
- [ ] Create `src/chrome_tabbed_window/utils/geometry.py` - Geometry helpers

---

## 2. Data Model Implementation

### 2.1 TabData Structure
```python
# In core/types.py
- [ ] Define TabData dataclass
  - widget: QWidget
  - text: str
  - icon: QIcon
  - tooltip: str
  - whats_this: str
  - enabled: bool
  - visible: bool
  - data: Any
  - _internal_id: str
  - _metadata: dict
```

### 2.2 TabModel Class
```python
# In core/model.py
- [ ] Implement TabModel(QObject)
- [ ] Add tab storage list
- [ ] Add current index tracking
- [ ] Implement add_tab(widget, text) -> int
- [ ] Implement insert_tab(index, widget, text) -> int
- [ ] Implement remove_tab(index) -> Optional[TabData]
- [ ] Implement move_tab(from_index, to_index)
- [ ] Implement get_tab(index) -> Optional[TabData]
- [ ] Implement set_current(index) -> bool
- [ ] Implement clear_tabs()
```

### 2.3 Model Signals
- [ ] Define tabAdded(int, TabData) signal
- [ ] Define tabRemoved(int, TabData) signal
- [ ] Define tabMoved(int, int) signal
- [ ] Define tabDataChanged(int, str) signal
- [ ] Define currentChanged(int, int) signal

---

## 3. QTabWidget API Implementation

### 3.1 Core Tab Management
```python
# In chrome_tabbed_window.py
- [ ] addTab(widget, label) -> int
- [ ] insertTab(index, widget, label) -> int
- [ ] removeTab(index) -> None
- [ ] clear() -> None
- [ ] count() -> int
- [ ] widget(index) -> QWidget
- [ ] indexOf(widget) -> int
```

### 3.2 Current Tab Management
- [ ] currentIndex() -> int
- [ ] setCurrentIndex(index) -> None
- [ ] currentWidget() -> QWidget
- [ ] setCurrentWidget(widget) -> None

### 3.3 Tab Properties
- [ ] setTabText(index, text) -> None
- [ ] tabText(index) -> str
- [ ] setTabIcon(index, icon) -> None
- [ ] tabIcon(index) -> QIcon
- [ ] setTabToolTip(index, tip) -> None
- [ ] tabToolTip(index) -> str
- [ ] setTabWhatsThis(index, text) -> None
- [ ] tabWhatsThis(index) -> str

### 3.4 Tab State
- [ ] setTabEnabled(index, enabled) -> None
- [ ] isTabEnabled(index) -> bool
- [ ] setTabVisible(index, visible) -> None
- [ ] isTabVisible(index) -> bool
- [ ] setTabData(index, data) -> None
- [ ] tabData(index) -> Any

### 3.5 Tab Bar Configuration
- [ ] setTabsClosable(closable) -> None
- [ ] tabsClosable() -> bool
- [ ] setMovable(movable) -> None
- [ ] isMovable() -> bool
- [ ] setDocumentMode(enabled) -> None
- [ ] documentMode() -> bool

### 3.6 Visual Properties
- [ ] setIconSize(size) -> None
- [ ] iconSize() -> QSize
- [ ] setElideMode(mode) -> None
- [ ] elideMode() -> Qt.TextElideMode
- [ ] setUsesScrollButtons(useButtons) -> None
- [ ] usesScrollButtons() -> bool

### 3.7 Tab Position & Shape
- [ ] setTabPosition(position) -> None
- [ ] tabPosition() -> QTabWidget.TabPosition
- [ ] setTabShape(shape) -> None
- [ ] tabShape() -> QTabWidget.TabShape

### 3.8 Corner Widgets
- [ ] setCornerWidget(widget, corner) -> None
- [ ] cornerWidget(corner) -> QWidget

### 3.9 Tab Bar Access
- [ ] tabBar() -> QTabBar

---

## 4. Signal Implementation

### 4.1 Public Signals
- [ ] currentChanged(int) signal
- [ ] tabCloseRequested(int) signal
- [ ] tabBarClicked(int) signal
- [ ] tabBarDoubleClicked(int) signal
- [ ] tabMoved(int, int) signal (if movable)

### 4.2 Signal Connections
- [ ] Connect model signals to public signals
- [ ] Ensure signal timing matches QTabWidget
- [ ] Handle signal forwarding correctly

---

## 5. Platform Detection

### 5.1 Platform Detector
```python
# In platform/detector.py
- [ ] Detect operating system (Windows/macOS/Linux)
- [ ] Detect window system (X11/Wayland/Cocoa/Win32)
- [ ] Detect WSL environment
- [ ] Detect Qt version
- [ ] Detect desktop environment (KDE/GNOME/etc)
```

### 5.2 Capability Detection
```python
# In platform/capabilities.py
- [ ] Define PlatformCapabilities dataclass
- [ ] Implement capability detection logic
- [ ] Test frameless support
- [ ] Test system move/resize support
- [ ] Test transparency support
```

### 5.3 Platform Factory
```python
# In platform/base.py
- [ ] Define IPlatformAdapter protocol
- [ ] Create PlatformFactory class
- [ ] Implement platform adapter selection
- [ ] Create fallback adapter
```

---

## 6. Basic View Components

### 6.1 Content Area
```python
# In components/content_area.py
- [ ] Create TabContentArea(QWidget)
- [ ] Embed QStackedWidget
- [ ] Implement add_widget(widget) -> int
- [ ] Implement remove_widget(widget)
- [ ] Implement set_current_widget(widget)
- [ ] Implement current_widget() -> QWidget
```

### 6.2 Basic Tab Bar
```python
# In components/tab_bar.py
- [ ] Create ChromeTabBar(QWidget) - basic version
- [ ] Implement basic tab rendering (rectangles OK for now)
- [ ] Handle mouse clicks for tab selection
- [ ] Connect to model for data
- [ ] Emit necessary signals
```

---

## 7. Controller Integration

### 7.1 ChromeTabbedWindow Assembly
```python
# In chrome_tabbed_window.py
- [ ] Initialize model, view components
- [ ] Set up layout (tab bar + content area)
- [ ] Connect model-view-controller
- [ ] Implement all QTabWidget methods using MVC
- [ ] Handle parent widget (embedded mode)
```

### 7.2 MVC Coordination
- [ ] Model updates trigger view updates
- [ ] View events update model
- [ ] Controller orchestrates both
- [ ] Maintain clean separation

---

## 8. Qt Integration Fundamentals

### 8.1 Meta-Object System
```python
# Essential Qt integration
- [ ] Add Q_OBJECT equivalent for Python (using Qt meta-object)
- [ ] Ensure proper signal/slot mechanism
- [ ] Set up meta properties
- [ ] Enable dynamic properties
- [ ] Support findChild/findChildren
```

### 8.2 Qt Property System
```python
# All properties must use Qt Property system
- [ ] Implement count as Qt Property
- [ ] Implement currentIndex as Qt Property
- [ ] Implement tabPosition as Qt Property
- [ ] Implement tabShape as Qt Property
- [ ] Implement tabsClosable as Qt Property
- [ ] Implement movable as Qt Property
- [ ] Implement documentMode as Qt Property
- [ ] Implement iconSize as Qt Property
- [ ] Implement elideMode as Qt Property
- [ ] Implement usesScrollButtons as Qt Property
```

### 8.3 Event System Completeness
```python
# Override necessary events
- [ ] paintEvent() - Custom painting
- [ ] resizeEvent() - Handle resizing
- [ ] showEvent() - Handle showing
- [ ] hideEvent() - Handle hiding
- [ ] changeEvent() - Handle state changes
- [ ] focusInEvent() / focusOutEvent()
- [ ] keyPressEvent() / keyReleaseEvent()
- [ ] wheelEvent() - Tab scrolling
- [ ] contextMenuEvent() - Right-click menus
- [ ] dragEnterEvent() / dragMoveEvent() / dropEvent()
```

### 8.4 Size Management
```python
# Size hints and policies
- [ ] Implement sizeHint() -> QSize
- [ ] Implement minimumSizeHint() -> QSize
- [ ] Set appropriate size policies
- [ ] Handle minimum/maximum sizes
- [ ] Update size hints when tabs change
```

---

## 9. Behavioral Completeness

### 9.1 Edge Case Handling
```python
# Handle all edge cases like QTabWidget
- [ ] Empty widget (0 tabs) behavior
- [ ] Single tab behavior
- [ ] Current index when removing current tab
- [ ] Current index when removing last tab
- [ ] Invalid index handling (return defaults, no crash)
- [ ] Null widget handling
- [ ] Out-of-bounds index handling
```

### 9.2 Signal Timing Verification
```python
# Match QTabWidget signal timing exactly
- [ ] currentChanged emission timing
- [ ] Order of signals when removing current tab
- [ ] Signal emission during batch operations
- [ ] Signal suppression during initialization
- [ ] Verify with signal spy tests
```

### 9.3 Focus Management
```python
# Complete focus handling
- [ ] Tab order for keyboard navigation
- [ ] Focus proxy setup
- [ ] Focus restoration when switching tabs
- [ ] Save/restore focus within tabs
- [ ] Handle focus chain properly
```

### 9.4 Parent/Child Rules
```python
# Qt parent/child ownership
- [ ] Widget reparenting on addTab
- [ ] Parent clearing on removeTab
- [ ] Proper cleanup with deleteLater
- [ ] Handle widget deletion signals
- [ ] Memory management verification
```

---

## 10. Input & Accessibility

### 10.1 Keyboard Shortcuts
```python
# Standard keyboard navigation
- [ ] Ctrl+Tab / Ctrl+Shift+Tab - Next/Previous tab
- [ ] Ctrl+W - Close current tab
- [ ] Ctrl+T - New tab (optional signal)
- [ ] Arrow keys for tab navigation
- [ ] Alt+1-9 - Jump to tab N
- [ ] Home/End - First/Last tab
```

### 10.2 Accessibility Features
```python
# Screen reader and accessibility
- [ ] Set accessible names
- [ ] Set accessible descriptions
- [ ] Implement accessible roles
- [ ] Tab order for keyboard users
- [ ] Focus indicators
- [ ] High contrast support
```

### 10.3 Drag & Drop
```python
# Tab reordering via drag & drop
- [ ] Drag detection on tabs
- [ ] Visual feedback during drag
- [ ] Drop zone detection
- [ ] Reorder animation
- [ ] Cancel drag with Escape
```

---

## 11. Style System

### 11.1 QSS Support
```python
# Qt Style Sheet compatibility
- [ ] Support QTabWidget selectors
- [ ] Handle custom stylesheets
- [ ] Style inheritance from parent
- [ ] Dynamic style updates
- [ ] Preserve Chrome look with QSS
```

### 11.2 Palette Integration
```python
# Qt Palette system
- [ ] Use QPalette colors
- [ ] Respond to palette changes
- [ ] Support dark/light themes
- [ ] Handle system theme changes
```

---

## 12. Testing Foundation

### 12.1 Unit Test Structure
- [ ] Create `tests/unit/` directory
- [ ] Create `tests/unit/test_api_compatibility.py`
- [ ] Create `tests/unit/test_model.py`
- [ ] Create `tests/unit/test_signals.py`
- [ ] Create `tests/unit/test_properties.py`
- [ ] Create `tests/unit/test_events.py`

### 12.2 API Compatibility Tests
```python
# In test_api_compatibility.py
- [ ] Test all QTabWidget methods exist
- [ ] Test method signatures match
- [ ] Test return types match
- [ ] Test signal signatures match
- [ ] Test property types match
```

### 12.3 Behavioral Comparison Tests
```python
# In test_qtabwidget_parity.py
- [ ] Create QTabWidget reference instance
- [ ] Create ChromeTabbedWindow instance
- [ ] Run identical operations on both
- [ ] Compare results exactly
- [ ] Use property-based testing
- [ ] Test signal emission order
```

### 12.4 Signal Tests
```python
# In test_signals.py
- [ ] Use QSignalSpy to capture signals
- [ ] Verify signal emission timing
- [ ] Test signal parameters
- [ ] Test signal order
- [ ] Test signal suppression cases
```

### 12.5 Edge Case Tests
```python
# In test_edge_cases.py
- [ ] Test with 0 tabs
- [ ] Test with 1 tab
- [ ] Test with 100+ tabs
- [ ] Test invalid indices
- [ ] Test null widgets
- [ ] Test rapid operations
```

### 12.6 Memory Tests
```python
# In test_memory.py
- [ ] Test for memory leaks
- [ ] Test widget cleanup
- [ ] Test circular references
- [ ] Test with large numbers of tabs
```

### 12.7 Thread Safety Tests
```python
# In test_thread_safety.py
- [ ] Test GUI thread requirements
- [ ] Test concurrent access
- [ ] Test signal thread safety
```

### 12.8 Integration Tests
- [ ] Create `tests/integration/` directory
- [ ] Test embedded mode works
- [ ] Test widget parent/child relationships
- [ ] Test with QApplication
- [ ] Test in layouts (QVBoxLayout, QSplitter, etc.)
- [ ] Test with other Qt widgets

---

## 9. Example Applications

### 9.1 Basic Example
```python
# In examples/01_basic.py
- [ ] Create simple tabbed window
- [ ] Add multiple tabs
- [ ] Test tab switching
- [ ] Verify embedded mode
```

### 9.2 API Test Example
```python
# In examples/02_api_test.py
- [ ] Test every QTabWidget method
- [ ] Verify behavior matches
- [ ] Document any differences
```

---

## 10. Documentation Updates

### 10.1 Code Documentation
- [ ] Add docstrings to all public methods
- [ ] Add type hints everywhere
- [ ] Add module-level documentation

### 10.2 Progress Documentation
- [ ] Create `wip/daily-progress.md`
- [ ] Document completed tasks
- [ ] Note any blockers
- [ ] Track decisions made

---

## Validation Checklist

### Before Moving to Phase 2
- [ ] All QTabWidget methods implemented
- [ ] All QTabWidget signals working
- [ ] All Qt properties implemented correctly
- [ ] Event system complete
- [ ] Size hints working
- [ ] Focus management working
- [ ] Keyboard shortcuts functional
- [ ] Edge cases handled properly
- [ ] Can replace QTabWidget in existing code
- [ ] QSS support verified
- [ ] Signal timing matches QTabWidget
- [ ] Embedded mode fully functional
- [ ] Platform detection working
- [ ] MVC architecture clean
- [ ] All tests passing
- [ ] Examples running

### Known Acceptable Limitations for Phase 1
- Chrome styling not required (basic rectangles OK)
- Animations not required
- Window mode not required
- Platform-specific features not required
- Performance optimization not required

---

## Risk Mitigation

### Technical Risks
1. **Signal compatibility**: Test extensively with QTabWidget
2. **Parent/child relationships**: Follow Qt ownership rules
3. **Memory management**: Use Qt's deleteLater()

### Architecture Risks
1. **MVC separation**: Review before Phase 2
2. **Extensibility**: Ensure clean interfaces
3. **Platform abstraction**: Keep it simple

---

## Daily Goals

### Day 1-2: Structure & Qt Fundamentals
- Set up file structure
- Qt meta-object system setup
- Qt property system implementation
- Event system framework

### Day 3-4: Model & API Core
- Implement TabData and TabModel
- Core QTabWidget methods
- Signal definitions
- Property implementations

### Day 5-6: API Completeness
- Complete all QTabWidget methods
- Tab properties and state
- Configuration methods
- Edge case handling

### Day 7-8: Behavioral Parity
- Signal timing verification
- Focus management
- Keyboard shortcuts
- Parent/child rules

### Day 9-10: View & Integration
- Content area with QStackedWidget
- Basic tab bar (rectangles OK)
- Wire up MVC
- Platform detection

### Day 11-12: Testing & Validation
- API compatibility tests
- Behavioral comparison tests
- Signal spy tests
- Edge case tests

### Day 13-14: Polish & Documentation
- Fix issues found in testing
- QSS support verification
- Examples
- Documentation

---

**End of Phase 1: Foundation complete, ready for Chrome styling and window mode!**