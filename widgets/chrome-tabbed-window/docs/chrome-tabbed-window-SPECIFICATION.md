# ChromeTabbedWindow — Full Requirements Specification (v1.0)

## Version Scope

**v1.0 Focus**: This specification defines ChromeTabbedWindow v1.0, which provides:
- 100% QTabWidget API compatibility (drop-in replacement)
- Chrome-style visual rendering
- Platform-aware window management
- **No additional public APIs beyond QTabWidget**

Future versions (v2.0+) will add services, plugins, and advanced features while maintaining backward compatibility. See [Extension Guide](extension-guide.md) for future roadmap.

## 1) Purpose

* Provide a reusable, Chrome-style **tabbed main window** component that developers can treat as a drop‑in `QTabWidget`/tabbed main window.
* Offer a unified tab strip with optional window controls when used as a top-level window.

## 2) Scope

* Single class that operates in two modes:
  1. **Top‑level mode:** Frameless (when supported) with custom title strip (tabs + window buttons), native move/resize.
  2. **Embedded mode:** Acts like a regular tab widget, no window buttons, no window move/resize.
* No business logic or page content included.

## 3) Non‑Goals

* No browser features or HTML engine.
* No theme packs beyond Qt palette (QSS hooks only).
* No detachable/tear‑out tabs in v1 (may be v2).

## 4) Platforms & Compatibility

* Qt/PySide6 on Windows, macOS, Linux (Wayland & X11), including WSL/WSLg.
* High‑DPI/Per‑monitor DPI supported.
* Keyboard/mouse/trackpad parity with native Qt widgets.

## 5) Dependencies & Runtime

* Qt/PySide6 **6.5+** (pref. 6.6+) for `startSystemMove`/`startSystemResize`.
* No third‑party libraries.

## 6) Public API Compatibility (QTabWidget Surface)

**v1.0 Strict Compatibility**: ChromeTabbedWindow v1.0 exposes ONLY the QTabWidget API - nothing more. All additional features (window management, Chrome styling) work automatically without new APIs.

Expose names/semantics identical to `QTabWidget`:

### Core Methods
* `addTab(widget, label)` - Add tab at end
* `insertTab(index, widget, label)` - Insert at position
* `removeTab(index)` - Remove tab at index
* `clear()` - Remove all tabs
* `count()` - Number of tabs
* `currentIndex()` - Current tab index
* `setCurrentIndex(index)` - Set current tab
* `widget(index)` - Get widget at index
* `indexOf(widget)` - Get index of widget

### Tab Attributes
* `setTabText(index, text)` / `tabText(index)`
* `setTabIcon(index, icon)` / `tabIcon(index)`
* `setTabToolTip(index, tip)` / `tabToolTip(index)`
* `setTabWhatsThis(index, text)` / `tabWhatsThis(index)`
* `setTabEnabled(index, enabled)` / `isTabEnabled(index)`
* `setTabData(index, data)` / `tabData(index)`

### Behavior/Appearance
* `setTabsClosable(closable)` / `tabsClosable()`
* `setMovable(movable)` / `isMovable()`
* `setIconSize(size)` / `iconSize()`
* `setDocumentMode(set)` / `documentMode()`
* `setElideMode(mode)` / `elideMode()`
* `setUsesScrollButtons(useButtons)` / `usesScrollButtons()`
* `setTabPosition(position)` / `tabPosition()`
* `setTabShape(shape)` / `tabShape()`

### Corner/Bar
* `setCornerWidget(widget, corner)` / `cornerWidget(corner)`
* `tabBar()` - Get tab bar widget
* `setTabBar(tabBar)` - Set custom tab bar

### Signals
* `currentChanged(int)` - Current tab changed
* `tabCloseRequested(int)` - Close button clicked
* `tabBarClicked(int)` - Tab clicked
* `tabBarDoubleClicked(int)` - Tab double-clicked
* `tabMoved(int, int)` - Tab reordered (if movable)

## 7) Additional Public API (Window Mode)

**v1.0 Note**: These APIs are internal in v1.0 and not exposed publicly. They are documented here for completeness but will be added in v2.0+. In v1.0, window management happens automatically based on parent widget.

### Future Signals (v2.0+)
* `newTabRequested()` - New tab button clicked

### Future Methods (v2.0+)
* `isTopLevel()` - Check if in top-level mode
* `toggleMaximizeRestore()` - Toggle maximize state

### Note
In v1.0, top-level vs embedded mode is determined automatically by the presence of a parent widget.

## 8) Behavioral Requirements

* Tab order mirrors page stack order at all times.
* Ownership matches `QTabWidget`: widgets reparented on add; released on remove.
* Signals emitted in same order/conditions as `QTabWidget`.
* Defaults mirror `QTabWidget` unless explicitly set by caller.

## 9) Signals & Event Model (Split‑Pane–Safe)

* Do **not** intercept/transform events destined for tab content.
* Window drag/resize hit‑testing only in empty title areas; never over tabs or content.
* Container shortcuts use **WindowShortcut** scope and yield to focused child if consumed.
* Tab reordering drag confined to tab strip; never interferes with child DnD.

### Additional Lifecycle Signals (v2.0+)
**v1.0 Note**: These enhanced signals are planned for v2.0+ and not available in v1.0. Use standard QTabWidget signals in v1.0.

* `tabAboutToClose(int)` - With **veto** capability (close prevented when vetoed)
* `currentAboutToChange(int from, int to)` - Before tab switch
* `tabAdded(int)` - After tab added
* `tabRemoved(int)` - After tab removed

### Optional Content Contracts (non‑required)
* Mirror `windowTitleChanged(QString)` and per‑tab icon changes when present.

## 10) Runtime Awareness (Wayland, X11, WSL/WSLg)

### Detection
* Auto‑detect platform and windowing system: Windows, macOS, Linux/**Wayland** vs **X11**, and **WSLg**.
* Expose a read‑only capability struct:
  ```python
  @dataclass
  class PlatformCapabilities:
      supports_system_move: bool
      supports_system_resize: bool
      supports_client_side_decorations: bool
      has_native_shadows: bool
      xdg_portals_available: bool
      running_under_wsl: bool
  ```

### Fallback Policy
* If move/resize unsupported → **disable frameless**, use **native decorations**.
* If client‑side decorations unsupported → keep native title bar; place tab strip below.
* Always degrade gracefully; the widget must always show.

### Wayland
* Avoid X11‑specific assumptions; rely on compositor control for maximize/fullscreen.
* If compositor lacks shadows for frameless → draw minimal 1‑px border.
* Respect portals; don't block portal modality.

### X11
* Frameless supported; enable edge hit‑testing and native move/resize through Qt when available.

### WSL/WSLg
* Detect WSLg; prefer native decorations if frameless is unreliable.
* Ensure DPI scaling and fonts correct; no OpenGL dependency.
* Clipboard/DnD/file dialogs rely on Qt; degrade without crashing if unavailable.

### Developer Overrides
* `setWindowingMode(auto|frameless|native)` with safe‑guard: ignore unsupported modes with warning.
* Read‑only diagnostics string/JSON of detected environment and chosen mode.

## 11) Main‑Window Parity

### Optional Areas and Slots
* `setMenuBar(widget)` - Set menu bar (top‑level only)
* `addToolBar(widget)` - Add toolbar (top‑level only)
* `setStatusBar(widget)` - Set status bar (top‑level only)

### Window Title
* Window title mirrors current tab text; host may override via `setWindowTitle()`.
* Corner widgets allowed on left/right of tab bar; optional "+" button.

## 12) Configuration (Declarative, Simple)

### Properties
* `tabsClosable` - Show close buttons
* `movable` - Allow tab reordering
* `documentMode` - Document-style tabs
* `iconSize` - Tab icon size
* `elideMode` - Text eliding mode
* `usesScrollButtons` - Show scroll buttons
* `showNewTabButton` - Show "+" button
* `showWindowButtons` - Show min/max/close (auto-detected)
* `edgeResizeMarginPx` - Resize border width (default 8)
* `minimumWindowSize` - Minimum window dimensions

### Styling
* No hardcoded colors; use Qt palette
* QSS object names for theming

## 13) Embedding & Composition

* **Top‑level mode:** Frameless (when supported) with system buttons and native move/resize.
* **Embedded mode:** Acts as pure tab container; window features disabled automatically.
* API semantics identical in both modes.

## 14) Input, Focus, Shortcuts

* Provide `Ctrl+T` (new tab) and `Ctrl+W` (close tab) by default; respect platform variants (Cmd on macOS).
* Focus return: optionally remember/restore last focused child per tab.
* Wheel/gesture routing: scrolling over tab bar scrolls tabs; over content goes to content.

## 15) Platform Details

### Windows
* Support snap, restore‑to‑pre‑maximize bounds
* Aero shadows (or 1‑px border fallback)
* Vertical maximize on edge double‑click

### macOS
* Default to native title bar; frameless optional
* Support full‑screen API and Escape to exit

### Linux
* KDE/GNOME/others parity
* X11/Wayland specifics per §10

## 16) Geometry & State

* Optional helpers to persist/restore:
  * Window geometry
  * Maximized/full‑screen flags
  * Current tab index
* React to DPI/screen changes and palette/theme changes without artifacting.

## 17) Error Handling & Edge Cases

* Invalid indices → no‑ops matching `QTabWidget`.
* Closing last tab → configurable:
  1. Open new blank tab (default)
  2. Emit `lastTabClosed()`
  3. Close window (top‑level only)
* Unified close path: middle‑click/API/shortcut all run through the **vetoable** close signal.

## 18) Performance

* Target responsiveness: open/close ≤50 ms per tab on typical dev hardware; switch O(1).
* No per‑frame heap allocations in paint paths.
* Removed tab widgets are promptly deleted (optionally delayed deletion for heavy pages).

## 19) Accessibility & i18n

* Accessible roles/names for title bar, tab bar, add button, window buttons.
* High‑contrast compatibility; RTL languages support (tab order, icons, corner widgets mirrored).
* All strings translatable via Qt.

## 20) Security & Privacy

* No external I/O, telemetry, or analytics.
* Only Qt public APIs used.

## 21) Testing & QA

### Automated Tests
* API‑parity tests vs `QTabWidget` (methods, returns, signals, edge behavior).

### Integration Tests
* Move/resize hit‑testing, maximize/restore, tab reordering, middle‑click close.
* Split‑pane scenarios (nested `QSplitter`, editors, DnD, shortcuts precedence).
* High‑DPI, high‑contrast, RTL.

### Platform Matrix
* Windows 11
* macOS
* Linux (Wayland GNOME/KDE, X11 KDE/XFCE)
* **WSLg**

## 22) Documentation

* Quick‑start examples for top‑level and embedded usage (no internals required).
* API parity table mapping each `QTabWidget` method/signal to this class.
* Environment behavior table (Wayland/X11/WSLg/Windows/macOS) and `auto` mode rationale.

## 23) Packaging & Versioning

* Distributed as a single module/package; zero extra dependencies.
* Semantic versioning: **1.x** guarantees `QTabWidget` API parity and stable behavior.
* Clear deprecation policy for any future behavioral changes.

---

## Implementation Priority

### v1.0 Implementation Phases

#### Phase 1: Foundation (Week 1-2)
1. Platform detection and capabilities
2. Complete QTabWidget API parity
3. Embedded mode fully working
4. **Strict MVC architecture** following patterns in [Architecture](architecture.md)

#### Phase 2: Window Mode (Week 3-4)
1. Frameless window support (automatic, no new APIs)
2. Native move/resize integration (automatic)
3. Window controls (automatic when top-level)

#### Phase 3: Platform Refinement (Week 5-6)
1. Windows-specific features (snap, Aero)
2. macOS-specific features (fullscreen)
3. Linux/Wayland/X11 optimization
4. WSL/WSLg fallback strategies

#### Phase 4: Polish & Testing (Week 7-8)
1. Performance optimization (< 50ms operations)
2. Comprehensive test suite
3. Documentation and examples
4. API compatibility validation

### Post-v1.0 Roadmap
See [Extension Guide](extension-guide.md) for v2.0+ features including:
- Tab services layer
- Plugin system
- Advanced lifecycle signals
- Developer tools

---

## Success Criteria

### v1.0 Success Metrics

1. **API Parity**: 100% QTabWidget method/signal compatibility - can replace QTabWidget without code changes
2. **Platform Coverage**: Works on Windows, macOS, Linux (X11/Wayland), WSL with automatic adaptation
3. **Performance**: Tab operations < 50ms, 60 FPS animations
4. **Stability**: Zero crashes, graceful degradation when features unavailable
5. **Developer Experience**: Drop-in replacement with zero learning curve for QTabWidget users
6. **Architecture**: Clean MVC separation enabling future extensions without breaking changes

### v1.0 Non-Goals (Future Versions)
- No plugin system (v2.0)
- No tab services (v2.0)
- No advanced lifecycle hooks (v2.0)
- No developer tools (v2.0)
- No multi-window coordination (v3.0)

## Related Documentation

- [API Reference](api.md) - Complete v1.0 API documentation (QTabWidget compatible)
- [Architecture](architecture.md) - Internal MVC architecture for maintainers
- [Usage Guide](usage.md) - Practical examples and patterns
- [Platform Notes](platform-notes.md) - Platform-specific behavior details
- [Extension Guide](extension-guide.md) - v2.0+ roadmap and future features