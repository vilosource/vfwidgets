# VFWidgets Testing Protocol Guide

## The Golden Rule of Testing

**"If you didn't verify the exit code, it didn't run successfully."**

## Critical Testing Failures to Avoid

### 1. The "Debug Output Illusion"
**WRONG:**
- Seeing debug logs and assuming the app works
- Looking for specific error strings without checking exit codes
- Assuming "no segfault message" means success

**RIGHT:**
```bash
python example.py
echo "Exit code: $?"  # ALWAYS CHECK THIS
```

### 2. The "Import Success Fallacy"
**WRONG:**
- Testing only that a module can be imported
- Assuming `import module` success means the code works

**RIGHT:**
- Actually run the application
- Verify it creates windows/widgets
- Check that it doesn't crash during initialization

### 3. The "Timeout Trap" ⚠️ **CRITICAL NEW LESSON**
**THE PROBLEM:**
When testing GUI applications with `subprocess.run(timeout=2)`, errors that occur DURING the GUI runtime (after the initial startup) are NOT captured by the default `capture_output=True` mechanism.

**WRONG:**
```python
try:
    result = subprocess.run(
        [sys.executable, "gui_app.py"],
        capture_output=True,
        timeout=2
    )
except subprocess.TimeoutExpired as e:
    # e.stderr only contains output UP TO timeout
    # Errors during GUI interaction are LOST!
    if e.stderr:  # ❌ This misses errors!
        check_errors(e.stderr.decode())
```

**WHY IT FAILS:**
- GUI apps continue running after initial startup
- Errors occur during widget lifecycle (paint, resize, cleanup, etc.)
- `subprocess.TimeoutExpired.stderr` buffer is finalized BEFORE these errors occur
- Result: Tests pass even when runtime errors exist!

**RIGHT:**
```python
# Write stderr to a FILE to capture ALL output
stderr_fd, stderr_path = tempfile.mkstemp(suffix='.log')
try:
    with open(stderr_path, 'w') as stderr_file:
        try:
            subprocess.run(
                [sys.executable, "gui_app.py"],
                stderr=stderr_file,  # ✅ Write to file
                timeout=2
            )
        except subprocess.TimeoutExpired:
            pass  # Expected for GUI apps

    # Read ENTIRE stderr log AFTER process ends
    with open(stderr_path, 'r') as f:
        stderr_content = f.read()

    # NOW check for errors (includes lifecycle errors!)
    if "[ERROR]" in stderr_content:
        print("✗ Runtime errors detected!")
        return False
finally:
    os.close(stderr_fd)
    os.unlink(stderr_path)
```

**WHAT THIS CATCHES:**
- Widget cleanup errors (`Exception ignored in __del__`)
- Qt event loop errors (paint, resize, signal/slot)
- Theme system errors during widget lifecycle
- Async errors that occur after startup
- Errors logged to stderr during GUI interaction

**REAL EXAMPLE:**
```
# Without file capture: "✓ PASS: 05_vscode_editor.py"
# With file capture: "✗ FAIL: [ERROR] Theme object has no attribute 'get'"
```

This trap cost us an entire implementation cycle! Don't let it happen again.

## Proper Testing Protocol

### Level 1: Basic Syntax Check
```python
# Can the file be parsed?
python -m py_compile example.py
```

### Level 2: Import Test
```python
# Can modules be imported?
import example
```

### Level 3: Runtime Test (CRITICAL)
```bash
# Does it actually RUN without crashing?
timeout 3 python example.py
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 124 ]; then
    echo "✓ Success"
else
    echo "✗ FAILED with exit code: $EXIT_CODE"
fi
```

### Level 4: Interactive Test
- Actually run the GUI
- Interact with buttons/widgets
- Switch themes
- Verify visual output

## Testing Checklist for Examples

- [ ] File can be parsed (syntax check)
- [ ] All imports resolve
- [ ] Application starts without crashing
- [ ] Exit code is 0 or timeout (124/-15)
- [ ] No tracebacks in output
- [ ] GUI window appears (for GUI apps)
- [ ] Theme switching works
- [ ] No segmentation faults

## Common Python GUI Exit Codes

- `0` - Success
- `1` - General error (check stderr for traceback)
- `124` - Timeout (expected for GUI apps)
- `-15` - SIGTERM (also expected for timeout)
- `139` or `-11` - Segmentation fault (CRITICAL)
- `134` or `-6` - Abort (CRITICAL)

## Automated Testing Script Template (UPDATED FOR TIMEOUT TRAP!)

```python
#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import os

def test_example(script_path):
    """Properly test if an example runs - IMPROVED VERSION."""
    # Create temp file for stderr to capture ALL output
    stderr_fd, stderr_path = tempfile.mkstemp(suffix='.log', prefix='test_')
    cleanup_done = False

    try:
        with open(stderr_path, 'w') as stderr_file:
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    stdout=subprocess.DEVNULL,
                    stderr=stderr_file,  # ✅ Write to file
                    timeout=2,
                    check=False
                )
                timeout_occurred = False
            except subprocess.TimeoutExpired:
                # Expected for GUI apps
                timeout_occurred = True
                result = None

        # Read ENTIRE stderr log AFTER process ends
        with open(stderr_path, 'r') as f:
            stderr_content = f.read()

        # Clean up
        os.close(stderr_fd)
        os.unlink(stderr_path)
        cleanup_done = True

        # CHECK THE EXIT CODE (if no timeout)
        if not timeout_occurred and result.returncode not in [0, -15, 124]:
            print(f"✗ CRASHED: exit code {result.returncode}")
            if "Traceback" in stderr_content:
                print(stderr_content)
            return False

        # CHECK FOR RUNTIME ERRORS (even during timeout!)
        error_patterns = [
            "[ERROR]",  # Logged errors
            "Exception ignored",  # Cleanup errors
            "TypeError:",
            "AttributeError:",
        ]

        for pattern in error_patterns:
            if pattern in stderr_content:
                print(f"✗ Runtime error: {pattern}")
                return False

        print("✓ Runs successfully" if not timeout_occurred else "✓ GUI running")
        return True

    except Exception as e:
        if not cleanup_done:
            try:
                os.close(stderr_fd)
                os.unlink(stderr_path)
            except:
                pass
        print(f"✗ Test error: {e}")
        return False
```

## Key Lessons

1. **Always verify exit codes** - This is non-negotiable
2. **Run the actual code** - Don't just import it
3. **Show actual output** - "It works" without proof is meaningless
4. **Test all inheritance patterns** - Mixins need all base classes
5. **Fix the first error first** - Don't assume later code works
6. **⚠️ AVOID THE TIMEOUT TRAP** - Capture stderr to a FILE, not just `capture_output=True`
7. **Check for [ERROR] log messages** - Not all errors crash the app
8. **Test the full lifecycle** - Startup success ≠ runtime success

## ThemedWidget Specific Tests

After changing ThemedWidget to a mixin pattern:

1. Check ALL classes that inherit from ThemedWidget
2. Ensure they also inherit from a Qt widget
3. Verify the inheritance order: `(ThemedWidget, QWidget)`
4. Test with actual Qt event loop

```python
# WRONG - will crash
class MyWidget(ThemedWidget):
    pass

# RIGHT - proper mixin usage
class MyWidget(ThemedWidget, QWidget):
    pass
```

## The Testing Mantra

> "Debug output means nothing.
> Import success proves little.
> Timeout without error checking proves nothing.
> Only exit code 0 AND clean stderr is truth."

Remember: **Execution theater** (claiming success without running code) is the enemy of reliable software. Always run, always verify, always show proof.

**The Timeout Trap cost us an entire development cycle. Learn from this mistake.**