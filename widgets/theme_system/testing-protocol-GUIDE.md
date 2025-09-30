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

## Automated Testing Script Template

```python
#!/usr/bin/env python3
import subprocess
import sys

def test_example(script_path):
    """Properly test if an example runs."""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=2,
            check=False  # Don't raise, we check manually
        )

        # CHECK THE EXIT CODE!
        if result.returncode not in [0, -15, 124]:
            print(f"✗ CRASHED: exit code {result.returncode}")
            if "Traceback" in result.stderr:
                print(result.stderr)
            return False

        print("✓ Runs successfully")
        return True

    except subprocess.TimeoutExpired:
        # Timeout is SUCCESS for GUI apps
        print("✓ Running (GUI timeout)")
        return True
```

## Key Lessons

1. **Always verify exit codes** - This is non-negotiable
2. **Run the actual code** - Don't just import it
3. **Show actual output** - "It works" without proof is meaningless
4. **Test all inheritance patterns** - Mixins need all base classes
5. **Fix the first error first** - Don't assume later code works

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
> Only exit code 0 is truth."

Remember: **Execution theater** (claiming success without running code) is the enemy of reliable software. Always run, always verify, always show proof.