# Bug Fix: Single-Instance Not Working

## Problem

**User Report**: "testing it, and it opened a second window"

**Expected Behavior**:
- Run `reamde FILE1.md` → opens window
- Run `reamde FILE2.md` → opens FILE2.md in new tab of existing window
- Second invocation should exit immediately after sending message

**Actual Behavior**:
- Both invocations created separate windows
- Each thought it was the primary instance

## Root Cause

**Location**: `shared/vfwidgets_common/src/vfwidgets_common/single_instance.py:142`

**Buggy Code**:
```python
def _create_local_server(self) -> bool:
    server_name = self._get_server_name()

    # BUG: This unconditionally removes the server!
    QLocalServer.removeServer(server_name)

    # Now listen will always succeed because we just removed it
    self._local_server = QLocalServer(self)
    if not self._local_server.listen(server_name):
        return False  # This never happens!

    return True  # Every instance thinks it's primary!
```

**Why This Is Wrong**:
1. First instance creates server → becomes primary ✅
2. Second instance **removes the server** → primary instance's server is gone! ❌
3. Second instance creates new server → becomes "primary" ❌
4. Result: Two primary instances, no IPC communication

## Solution

**Strategy**: Only remove the server if it's **stale** (from crashed instance)

**How To Detect Stale Server**:
1. Try to create server
2. If that fails, try to **connect** to the existing server
3. If connection succeeds → server is alive, we're secondary ✅
4. If connection fails → server is stale, remove and retry ✅

**Fixed Code**:
```python
def _create_local_server(self) -> bool:
    server_name = self._get_server_name()

    # Try to create server first (don't remove yet!)
    self._local_server = QLocalServer(self)
    if self._local_server.listen(server_name):
        # Success - we're the primary instance
        self._local_server.newConnection.connect(self._on_new_connection)
        return True

    # Server name already in use - check if it's alive or stale
    # Try to connect to it
    test_socket = QLocalSocket()
    test_socket.connectToServer(server_name)

    if test_socket.waitForConnected(1000):
        # Server is alive - we're a secondary instance
        test_socket.disconnectFromServer()
        return False  # Correctly identified as secondary!

    # Server is stale (from crashed instance) - remove and try again
    print(f"[SingleInstanceApplication] Removing stale server: {server_name}")
    QLocalServer.removeServer(server_name)

    if self._local_server.listen(server_name):
        # Successfully created after removing stale server
        self._local_server.newConnection.connect(self._on_new_connection)
        return True

    # Still can't create server - something is wrong
    print(f"[SingleInstanceApplication] Failed to create server: {server_name}")
    return False
```

## Flow Diagrams

### Before Fix (Broken)

```
Instance 1:                    Instance 2:
  Start                          Start
    ↓                              ↓
  Remove server (none)         Remove server (kills Instance 1's!)
    ↓                              ↓
  Create server ✅              Create server ✅
    ↓                              ↓
  is_primary = True            is_primary = True
    ↓                              ↓
  Show window                   Show window
    ↓                              ↓
  [Two windows!] ❌            [Two windows!] ❌
```

### After Fix (Correct)

```
Instance 1:                    Instance 2:
  Start                          Start
    ↓                              ↓
  Try create server            Try create server (fails)
    ↓                              ↓
  Success ✅                    Try connect to server
    ↓                              ↓
  is_primary = True            Success ✅
    ↓                              ↓
  Show window                   is_primary = False
    ↓                              ↓
  Listen for IPC ←─────────── Send "open" message
    ↓                              ↓
  Receive message              Exit (code 0)
    ↓
  Open in new tab              [One window, two tabs!] ✅
```

## Testing

### Manual Test

```bash
# Clean up
rm -f /tmp/vfwidgets-reamde-$USER

# Terminal 1: Launch primary
python -m reamde DEMO1.md

# Terminal 2: Launch secondary
python -m reamde DEMO2.md
```

**Expected**:
- ✅ Only one window appears
- ✅ Two tabs: DEMO1.md and DEMO2.md
- ✅ Terminal 2 exits immediately (code 0)
- ✅ DEMO2.md tab is focused

### Automated Test

Run the test script:
```bash
cd /home/kuja/GitHub/vfwidgets/apps/reamde
./test_single_instance.sh
```

## Files Modified

1. `shared/vfwidgets_common/src/vfwidgets_common/single_instance.py`
   - Modified `_create_local_server()` method
   - Added connection test before removing stale server
   - Added debug logging for stale server removal

## Impact

This fix affects **all applications** using `SingleInstanceApplication`:
- ✅ reamde (markdown viewer)
- ✅ Any future applications using the pattern

The fix is **backward compatible** - no API changes required.

## Lessons Learned

1. **Never unconditionally remove IPC resources** - always check if they're in use
2. **Test with actual IPC** - unit tests missed this because they didn't test concurrent instances
3. **Connection test is the right check** - trying to connect verifies the server is actually alive

## Prevention

**Added to future checklist**:
- [ ] Test single-instance behavior with actual concurrent launches
- [ ] Verify secondary instance exits with code 0
- [ ] Verify IPC messages are received by primary
- [ ] Test with stale socket file (crash scenario)

---

**Bug fixed**: 2025-10-11
**Tested with**: reamde application
**Severity**: High (core functionality broken)
**Status**: ✅ Resolved
