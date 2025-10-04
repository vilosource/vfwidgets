# MultisplitWidget API Stability Guide

Understanding API stability and versioning for the MultisplitWidget.

## Version Strategy

### Pre-1.0 (Current: 0.x)

We are currently in **early development** (version 0.x):

- ✅ **Breaking changes allowed** between minor versions (0.1 → 0.2)
- ✅ **No deprecation period required** - old APIs can be removed
- ✅ **Rapid iteration** to improve developer experience
- ❌ **No backward compatibility guarantees**

**What this means for you:**
- Always check the migration guide when upgrading
- Pin to specific versions in production: `vfwidgets-multisplit==0.2.0`
- Expect API improvements and breaking changes

### Post-1.0 (Future)

Once we reach **version 1.0**:

- ✅ **Semantic versioning** will be strictly followed
- ✅ **Deprecation warnings** before breaking changes
- ✅ **Backward compatibility** within major versions
- ✅ **Stable public API** with clear guarantees

## API Stability Levels

### Stable (Safe to Use)

These APIs are stable even in 0.x and unlikely to change:

**Core Widget**
```python
from vfwidgets_multisplit import MultisplitWidget

multisplit = MultisplitWidget(provider=my_provider)
multisplit.split_pane(pane_id, widget_id, position, ratio)
multisplit.remove_pane(pane_id)
multisplit.focus_pane(pane_id)
multisplit.navigate_focus(direction)
```

**Signals**
```python
multisplit.pane_added.connect(handler)
multisplit.pane_removed.connect(handler)
multisplit.focus_changed.connect(handler)  # v0.2.0+
multisplit.layout_changed.connect(handler)
```

**Types and Enums**
```python
from vfwidgets_multisplit import WherePosition, Direction, SplitterStyle

WherePosition.LEFT, WherePosition.RIGHT, WherePosition.TOP, WherePosition.BOTTOM
Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT
SplitterStyle.minimal(), SplitterStyle.compact()
```

### Recently Stabilized (v0.2.0)

These APIs are new in v0.2.0 and expected to remain stable:

**Widget Provider Protocol**
```python
from vfwidgets_multisplit import WidgetProvider

class MyProvider(WidgetProvider):
    def provide_widget(self, widget_id, pane_id):
        """Required: Create widget for pane"""
        return QWidget()

    def widget_closing(self, widget_id, pane_id, widget):
        """Optional: Cleanup before widget removal"""
        pass
```

**Widget Lookup APIs**
```python
widget = multisplit.get_widget(pane_id)
all_widgets = multisplit.get_all_widgets()
pane_id = multisplit.find_pane_by_widget(widget)
```

### Internal (Do Not Use)

These are **internal implementation** and may change without notice:

**Private Attributes** (prefixed with `_`)
```python
multisplit._model  # DON'T USE
multisplit._controller  # DON'T USE
multisplit._container  # DON'T USE
multisplit._focus_manager  # DON'T USE
```

**Internal Modules**
```python
# DON'T import from these
from vfwidgets_multisplit.core.model import PaneModel
from vfwidgets_multisplit.controller.controller import PaneController
from vfwidgets_multisplit.view.container import PaneContainer
```

If you need functionality from internal modules, **request it as a public API feature** instead.

## Breaking Changes History

### v0.2.0 (Current)

**Breaking Changes:**
1. Removed `pane_focused` signal → Use `focus_changed` instead
2. Made internal attributes private (added `_` prefix)
3. Removed access to `multisplit.model.signals`

**New APIs:**
1. `widget_closing()` lifecycle hook in WidgetProvider
2. `get_widget()`, `get_all_widgets()`, `find_pane_by_widget()`
3. `focus_changed` signal with old and new pane IDs
4. Clean package exports for `WherePosition`, `Direction`, `WidgetProvider`

See [Migration Guide](migration-guide-GUIDE.md) for upgrading from v0.1.x.

### v0.1.0 (Initial Release)

- Initial public API
- Basic split/remove/focus operations
- WidgetProvider protocol
- Session persistence

## Deprecation Policy (Post-1.0)

Once we reach 1.0, we will follow this policy:

1. **Deprecation Warning**: API marked as deprecated with clear alternatives
   ```python
   @deprecated("Use new_method() instead")
   def old_method(self):
       ...
   ```

2. **Deprecation Period**: Minimum of 2 minor versions
   - v1.1.0: Deprecation warning added
   - v1.2.0: Warning continues
   - v1.3.0: Warning continues
   - v2.0.0: Removed

3. **Documentation**: Migration guide provided for all breaking changes

4. **Changelog**: All deprecations clearly listed in CHANGELOG.md

## How to Stay Updated

### Check Before Upgrading

1. **Read CHANGELOG.md**: Lists all changes between versions
2. **Read Migration Guide**: Step-by-step upgrade instructions
3. **Run Tests**: Ensure your code still works
4. **Check Deprecation Warnings**: Fix any warnings before upgrading

### Version Pinning

**Development**
```bash
# Allow patch updates
pip install "vfwidgets-multisplit>=0.2.0,<0.3.0"
```

**Production**
```bash
# Pin exact version
pip install "vfwidgets-multisplit==0.2.0"
```

**Adventurous**
```bash
# Latest version (may include breaking changes in 0.x)
pip install "vfwidgets-multisplit"
```

## Requesting API Changes

If you need functionality that requires internal access:

1. **Open an Issue**: Describe your use case
2. **Propose API**: Suggest a public API design
3. **Discuss**: We'll work together on the best approach
4. **Implement**: Add it to the public API properly

**Example**: Instead of accessing `multisplit._model.root`, you might request:
```python
# New public API request
tree_structure = multisplit.get_tree_structure()
```

## Commitment to Stability

While in 0.x, we prioritize **developer experience** over stability. Once we reach 1.0:

- We commit to **semantic versioning**
- We provide **clear migration paths**
- We maintain **backward compatibility** within major versions
- We give **advance notice** for breaking changes

Our goal: Make MultisplitWidget **reliable and predictable** for production use.

## Questions?

- GitHub Issues: https://github.com/yourusername/vfwidgets/issues
- Discussions: https://github.com/yourusername/vfwidgets/discussions
- Documentation: https://vfwidgets.readthedocs.io/
