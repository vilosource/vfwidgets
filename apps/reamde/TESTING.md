# Reamde Testing Plan

## Current Status

Reamde is functionally complete. The following manual tests should be performed to verify all features work correctly.

## Test 1: Basic File Opening

**Goal**: Verify a markdown file can be opened and displayed

**Steps**:
```bash
cd /home/kuja/GitHub/vfwidgets/apps/reamde
python -m reamde DEMO1.md
```

**Expected**:
- ✅ Window opens with title "Reamde - DEMO1.md"
- ✅ Content is displayed (headings, code blocks, diagrams)
- ✅ Syntax highlighting works
- ✅ Mermaid diagrams render
- ✅ Math equations render

**Status**: ⏳ Needs manual testing

---

## Test 2: Single-Instance Behavior

**Goal**: Verify second invocation opens in same window

**Steps**:
```bash
# Terminal 1
cd /home/kuja/GitHub/vfwidgets/apps/reamde
python -m reamde DEMO1.md

# Terminal 2 (while first is running)
cd /home/kuja/GitHub/vfwidgets/apps/reamde
python -m reamde DEMO2.md
```

**Expected**:
- ✅ Terminal 2 exits immediately (return code 0)
- ✅ DEMO2.md opens in new tab in existing window
- ✅ New tab is automatically focused
- ✅ Window comes to front (if it was behind other windows)
- ✅ Window title updates to "Reamde - DEMO2.md"

**Status**: ⏳ Needs manual testing

---

## Test 3: Cross-Directory File Opening

**Goal**: Verify files can be opened from different directories

**Steps**:
```bash
# Terminal 1
cd /home/kuja/GitHub/vfwidgets/apps/reamde
python -m reamde DEMO1.md

# Terminal 2 (from different directory)
cd /tmp
python -m reamde /home/kuja/GitHub/vfwidgets/apps/reamde/DEMO2.md
```

**Expected**:
- ✅ File opens in existing window
- ✅ Absolute path resolved correctly
- ✅ Tab shows filename (not full path)
- ✅ Tooltip shows full path

**Status**: ⏳ Needs manual testing

---

## Test 4: Tab Management

**Goal**: Verify tab operations work correctly

**Steps**:
1. Open multiple files in tabs
2. Click × on a tab to close it
3. Drag a tab to reorder
4. Hover over tab to see tooltip
5. Close all tabs

**Expected**:
- ✅ Tabs can be closed via × button
- ✅ Tabs can be reordered by dragging
- ✅ Tooltip shows full file path
- ✅ Closing tab updates window title
- ✅ Last tab can be closed (window stays open)

**Status**: ⏳ Needs manual testing

---

## Test 5: Duplicate File Handling

**Goal**: Verify opening same file twice focuses existing tab

**Steps**:
```bash
# Terminal 1
python -m reamde DEMO1.md

# Terminal 2
python -m reamde DEMO1.md  # Same file again
```

**Expected**:
- ✅ No new tab created
- ✅ Existing DEMO1.md tab is focused
- ✅ Terminal 2 exits immediately

**Status**: ⏳ Needs manual testing

---

## Test 6: No File Argument

**Goal**: Verify app launches without file argument

**Steps**:
```bash
python -m reamde
```

**Expected**:
- ✅ Window opens with no tabs
- ✅ Window title is "Reamde - Markdown Viewer"
- ✅ Application doesn't crash

**Status**: ⏳ Needs manual testing

---

## Test 7: Window Focus/Activation

**Goal**: Verify window comes to front on secondary launch

**Steps**:
1. Launch reamde with a file
2. Minimize or hide window behind other windows
3. Launch reamde with another file from terminal

**Expected**:
- ✅ Window is unminimized (if minimized)
- ✅ Window comes to front
- ✅ Window is activated (has keyboard focus)
- ✅ New tab is focused

**Status**: ⏳ Needs manual testing

---

## Test 8: IPC Communication

**Goal**: Verify IPC socket is created and cleaned up

**Steps**:
```bash
# Check socket doesn't exist
ls -la /tmp/vfwidgets-reamde-$USER

# Launch reamde
python -m reamde DEMO1.md &
REAMDE_PID=$!

# Check socket exists
ls -la /tmp/vfwidgets-reamde-$USER

# Kill reamde
kill $REAMDE_PID

# Wait a moment
sleep 1

# Socket might still exist (this is OK - Qt handles cleanup)
ls -la /tmp/vfwidgets-reamde-$USER
```

**Expected**:
- ✅ Socket created when reamde starts
- ✅ Socket has correct permissions
- ✅ Can be cleaned up manually if needed

**Status**: ⏳ Needs manual testing

---

## Test 9: Relative Image Paths

**Goal**: Verify images with relative paths load correctly

**Steps**:
Create test file with image:
```bash
cd /tmp
echo "# Test\n\n![test](test.png)" > test.md
# Create dummy image (optional)
python -m reamde test.md
```

**Expected**:
- ✅ Markdown renders
- ✅ Image path is resolved relative to file location
- ✅ Base path set correctly

**Status**: ⏳ Needs manual testing

---

## Test 10: Large Files

**Goal**: Verify large markdown files load without issues

**Steps**:
```bash
# Create large file
python -c "print('# Heading\n\n' + 'Line of text.\n' * 10000)" > large.md
python -m reamde large.md
```

**Expected**:
- ✅ File loads (may take a moment)
- ✅ Scrolling is smooth
- ✅ No memory issues

**Status**: ⏳ Needs manual testing

---

## Known Issues / Platform Considerations

### Linux/Wayland
- Window focus/raise may have limited support due to compositor restrictions
- This is a platform limitation, not a reamde bug

### Stale Socket Files
If reamde crashes without cleanup:
```bash
rm /tmp/vfwidgets-reamde-$USER
```

---

## Future Enhancements (Not Required Now)

- [ ] File watching and auto-reload
- [ ] Export to PDF (MarkdownViewer already supports this!)
- [ ] Export to HTML (MarkdownViewer already supports this!)
- [ ] Recent files menu
- [ ] Search within document
- [ ] Bookmarks / navigation
- [ ] Custom CSS themes
- [ ] Plugin system
- [ ] Presentation mode

---

## Quick Test Script

For automated testing, run:

```bash
#!/bin/bash
cd /home/kuja/GitHub/vfwidgets/apps/reamde

echo "Test 1: Basic launch"
timeout 2 python -m reamde DEMO1.md &
PID1=$!
sleep 1

echo "Test 2: Single instance"
timeout 2 python -m reamde DEMO2.md
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✅ Single instance worked (exit code 0)"
else
    echo "❌ Single instance failed (exit code $RESULT)"
fi

kill $PID1 2>/dev/null

echo "Done"
```

Save as `test_reamde.sh` and run with `bash test_reamde.sh`.
