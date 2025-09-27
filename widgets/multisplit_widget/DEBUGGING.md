# Debugging Guide for MultiSplit Widget

## Overview

The MultiSplit widget now includes comprehensive logging to help trace and debug issues, particularly with widget visibility and split operations.

## Quick Start

### Running the Demo with Debug Logging

```bash
# Basic debug mode (shows all detailed logs in console)
python demo_mvp_enhanced.py --debug

# Log to file for analysis
python demo_mvp_enhanced.py --debug --log-file debug.log

# Specific log level
python demo_mvp_enhanced.py --log-level DEBUG
```

### Testing Logging System

```bash
# Run the logging test script
python test_logging.py
```

## Logging Levels

- **DEBUG**: Most detailed - shows every operation, tree structure changes, widget creation
- **INFO**: Normal operations - split commands, widget creation, major events
- **WARNING**: Potential issues - missing providers, validation warnings
- **ERROR**: Failures - command failures, missing panes, invalid operations

## What Gets Logged

### Split Operations
When you split a pane, the logs show:
1. Split operation parameters (target, position, ratio)
2. Tree structure BEFORE the split
3. ID generation for new panes/nodes
4. Tree modification steps
5. Tree structure AFTER the split
6. Widget creation requests

Example log output:
```
[14:23:45.123] INFO     | Split operation STARTED
[14:23:45.124] INFO     |   Target Pane: pane_a3f2b8c1
[14:23:45.124] INFO     |   New Widget: editor:test.py
[14:23:45.124] INFO     |   Position: WherePosition.RIGHT
[14:23:45.124] INFO     |   Ratio: 0.5
[14:23:45.125] DEBUG    | Tree BEFORE split:
[14:23:45.125] DEBUG    |   Leaf[pane_a3f2b8c1]: widget=editor:main.py
[14:23:45.126] INFO     | Generated new pane ID: pane_d7e9f2a1
[14:23:45.127] DEBUG    | Tree AFTER split:
[14:23:45.127] DEBUG    |   Split[node_5b3c9d7f]: horizontal, ratios=['0.50', '0.50']
[14:23:45.128] DEBUG    |     Leaf[pane_a3f2b8c1]: widget=editor:main.py
[14:23:45.128] DEBUG    |     Leaf[pane_d7e9f2a1]: widget=editor:test.py
```

### Widget Creation
Each widget creation logs:
- Widget ID requested
- Pane ID it's being created for
- Widget type actually created
- Whether provider was available

Example:
```
[14:23:45.234] INFO     | Requesting widget from provider: editor:main.py for pane pane_a3f2b8c1
[14:23:45.235] INFO     | WIDGET CREATED: CodeEditor for editor:main.py in pane pane_a3f2b8c1
```

### Tree Reconciliation
Shows what changes when updating the view:
```
[14:23:45.345] DEBUG    | Reconciliation changes:
[14:23:45.345] DEBUG    |   Added: {PaneId('pane_d7e9f2a1')}
[14:23:45.346] DEBUG    |   Removed: set()
[14:23:45.346] INFO     | Adding pane: pane_d7e9f2a1
[14:23:45.347] DEBUG    | Rebuilding layout
```

## Troubleshooting Common Issues

### Issue: Editor pane not visible

Check logs for:
1. **Widget creation**: Was the widget actually created?
   ```
   grep "WIDGET CREATED" debug.log
   ```

2. **Provider issues**: Is the provider working?
   ```
   grep "No provider available" debug.log
   ```

3. **Tree structure**: Is the pane in the tree?
   ```
   grep "Tree AFTER" debug.log
   ```

### Issue: Split operation not working

Check logs for:
1. **Target pane exists**:
   ```
   grep "Target pane not found" debug.log
   ```

2. **Validation errors**:
   ```
   grep "Validation.*FAILED" debug.log
   ```

3. **Command execution**:
   ```
   grep "Split operation.*SUCCESSFUL" debug.log
   ```

### Issue: Focus not working

Check logs for:
```
grep "Focus changed" debug.log
```

## Advanced Debugging

### Enable Logging in Your Code

```python
from vfwidgets_multisplit.core.logger import setup_logging, logger

# Enable debug logging
setup_logging(level="DEBUG", detailed=True)

# Use in your code
logger.info("Creating widget")
logger.debug(f"Widget details: {widget}")
```

### Custom Log Analysis

Save logs to file and analyze:
```bash
# Run with file logging
python demo_mvp_enhanced.py --debug --log-file session.log

# Count split operations
grep -c "SPLIT OPERATION STARTED" session.log

# See all errors
grep "ERROR" session.log

# Track specific pane
grep "pane_a3f2b8c1" session.log
```

### Using the Operation Tracer

For timing analysis:
```python
from vfwidgets_multisplit.core.logger import OperationTracer

with OperationTracer("MyOperation", param1="value1"):
    # Your code here
    pass
# Automatically logs start, end, and duration
```

## Log Output Format

### Detailed Format (--debug mode)
```
[HH:MM:SS.mmm] LEVEL    | module.function:line | message
```

### Simple Format (default)
```
LEVEL: message
```

## Performance Considerations

- Debug logging can impact performance with many panes
- Use INFO level for production
- File logging is faster than console for large outputs

## Tips

1. **Always start with --debug** when investigating issues
2. **Save logs to file** for complex debugging sessions
3. **Use grep/search** to find specific operations
4. **Check tree structure** before and after operations
5. **Verify widget creation** for visibility issues

## Example Debug Session

```bash
# 1. Start demo in debug mode with file logging
python demo_mvp_enhanced.py --debug --log-file debug.log

# 2. Reproduce the issue (e.g., split a pane)

# 3. Check the log file
tail -f debug.log  # Watch in real-time

# 4. Search for specific issues
grep -A 5 -B 5 "ERROR" debug.log  # Show errors with context

# 5. Check tree structure
grep -A 20 "Tree AFTER" debug.log  # See final tree state
```

## Summary

The logging system provides complete visibility into:
- Command execution flow
- Tree structure changes
- Widget lifecycle
- Focus management
- Validation results

Use `--debug` flag to enable detailed logging and trace any issues with widget visibility or split operations.