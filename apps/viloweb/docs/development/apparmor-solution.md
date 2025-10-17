# ViloWeb Qt WebEngine Crash - REAL SOLUTION

## The Actual Problem (UPDATED)

**Root Cause**: QWebChannel object was being registered in multiple QWebChannel instances (one per tab), causing crashes in `libQt6WebChannel.so.6`.

**Previous incorrect diagnosis**: Initially thought AppArmor was blocking QtWebEngineProcess, but that was not the root cause.

## Symptoms

Kernel logs showed:
```
viloweb[242106]: segfault at 1 ip 000078169d1f39f0 sp 00007ffef2b578b0 error 4 in libQt6WebChannel.so.6
```

Key indicators:
- Crash in `libQt6WebChannel.so.6` (NOT QtWebEngineProcess)
- Error 4 = read access to invalid address (null pointer dereference)
- Crash happened right after first page load
- Happened consistently every time viloweb started

## Investigation Steps

1. ✅ Checked kernel settings (unprivileged_userns_clone = 1) - **OK**
2. ✅ Set Qt WebEngine environment variables - **Not sufficient**
3. ✅ Added Chromium flags (--no-zygote, --no-sandbox) - **Not sufficient**
4. ❌ Checked AppArmor status - **Red herring, not the issue**
5. ✅ Checked dmesg kernel logs - **FOUND THE REAL ISSUE**

## The REAL Solution

The crash was in `libQt6WebChannel.so.6`, not QtWebEngineProcess. The problem was in our code:

**Bug**: Creating multiple `QWebChannel` instances (one per tab) and registering the same `ViloWebBridge` object in each channel.

**Qt Limitation**: A QObject can only be registered in ONE QWebChannel at a time. Registering it in multiple channels causes undefined behavior and crashes.

### Fix (Code Change)

**File**: `apps/viloweb/src/viloweb/ui/main_window.py`

**Before** (broken):
```python
def new_tab(self, url: str = "about:blank") -> BrowserTab:
    tab = BrowserTab(self)
    # BUG: Creates NEW channel for each tab!
    WebChannelHelper.setup_channel(tab.widget, self._bridge, "viloWeb")
    # ...
```

**After** (fixed):
```python
def __init__(self):
    # ...
    self._bridge = ViloWebBridge(self)
    self._channel: Optional[QWebChannel] = None  # Shared channel
    # ...

def new_tab(self, url: str = "about:blank") -> BrowserTab:
    tab = BrowserTab(self)

    if self._channel is None:
        # Create channel only ONCE for first tab
        self._channel = WebChannelHelper.setup_channel(tab.widget, self._bridge, "viloWeb")
    else:
        # Reuse existing channel for subsequent tabs
        tab.widget.page().setWebChannel(self._channel)
    # ...
```

### Verification

After applying the fix:
```bash
viloweb
```

**Result**: ✅ Browser launches successfully without crashes!

Log shows:
```
[INFO] vfwidgets_webview.webchannel_helper - Setting up QWebChannel with object name: viloWeb
[INFO] vfwidgets_webview.webchannel_helper - QWebChannel setup complete: window.viloWeb
[INFO] viloweb.browser.browser_tab - Tab navigating to: https://github.com/viloforge/vfwidgets
[INFO] vfwidgets_webview.webview - Loading URL: https://github.com/viloforge/vfwidgets
[INFO] vfwidgets_webview.webpage - JS Console [INFO] - [WebChannel] ✓ Bridge ready: window.viloWeb
[INFO] viloweb.browser.viloweb_bridge - [JS] QWebChannel bridge connected: viloWeb
```

No segfaults in dmesg:
```bash
sudo dmesg | grep viloweb | tail -5
# Shows only OLD crashes from before the fix
```

## Why This Happened

Classic Qt/QWebChannel gotcha:
- QWebChannel uses Qt's meta-object system to expose Python objects to JavaScript
- Registering the same QObject in multiple channels confuses Qt's internal bookkeeping
- Results in null pointer dereference when JavaScript tries to call methods
- This is a **code bug**, not a system configuration issue

## Additional Fix Applied

Also fixed a minor type mismatch in `browser_tab.py`:
```python
# Before:
@Slot(object)  # QUrl
def _on_url_changed(self, url) -> None:
    self._url = url.toString()  # Crashes if url is already a string

# After:
@Slot(str)
def _on_url_changed(self, url: str) -> None:
    self._url = url  # Correct - WebView.url_changed emits str
```

## Lessons Learned

1. **Always check dmesg** for segfaults - it shows which library crashed
2. **QWebChannel limitation**: One QObject can only be registered in one channel
3. **Share QWebChannel** across tabs, don't create one per tab
4. **Read signal signatures** carefully - WebView uses snake_case and emits strings, not QUrl
5. **Don't trust initial hunches** - the zygote/AppArmor theory was completely wrong

## AppArmor Note (Irrelevant)

The AppArmor investigation was a red herring. Setting plasmashell to complain mode didn't help because the crash was in our code, not in Qt WebEngine's process spawning.

## System Information

- **OS**: Ubuntu-based
- **Kernel**: 6.14.0-33-generic
- **PySide6**: 6.9.0
- **Qt WebEngine**: 6.9.0

## Files Modified

1. **apps/viloweb/src/viloweb/ui/main_window.py**:
   - Added `self._channel: Optional[QWebChannel] = None`
   - Modified `new_tab()` to create channel once, reuse for subsequent tabs
   - Added `from PySide6.QtWebChannel import QWebChannel` import

2. **apps/viloweb/src/viloweb/browser/browser_tab.py**:
   - Fixed `_on_url_changed()` to accept `str` instead of `QUrl`

## Summary

**Problem**: QWebChannel object registered in multiple channels
**Solution**: Create ONE channel, reuse it for all tabs
**Result**: ✅ ViloWeb works perfectly without crashes
**Time to Solution**: ~2 hours of investigation (including red herring AppArmor chase)

The real lesson: **Always check dmesg to see WHICH library crashed before guessing!**
