# Legacy Examples

This directory contains older examples that are being reorganized to follow the progressive disclosure philosophy.

## What's Here

- **tutorials/** - Old tutorial series (6 examples)
- **basic/** - Basic widget examples (5 examples)
- **layouts/** - Layout examples (5 examples)
- **user_examples/** - User-contributed examples
- **development_examples/** - Development/testing examples

## Status

These examples are **functional** but use a mix of API styles. They are being:
1. Reviewed for best practices
2. Updated to follow progressive disclosure
3. Migrated to the main examples/ directory

## Using These Examples

These examples still work! You can run them:

```bash
# Tutorial series
python legacy/tutorials/01_hello_theme.py
python legacy/tutorials/02_custom_theme.py

# Basic widgets
python legacy/basic/themed_button.py
python legacy/basic/themed_label.py

# Layouts
python legacy/layouts/grid_layout.py
python legacy/layouts/tab_widget.py
```

## Migration Plan

These examples will be reorganized into:
- **Examples 01-04** - Simple API only (already complete)
- **Example 05+** - Progressive introduction to ThemedWidget (in progress)
- **Advanced/** - Complex examples for widget library authors (planned)

## Why Legacy?

The theme system has evolved to use **progressive disclosure**:
- Start simple (ThemedMainWindow, ThemedDialog, ThemedQWidget)
- Graduate to advanced (ThemedWidget mixin) only when needed

These examples mixed the APIs without clear progression, which could be confusing for newcomers. The new examples/ structure teaches the system progressively.

## Contributing

If you want to help reorganize these examples:
1. Check the API-CONSOLIDATION-PLAN.md for guidance
2. Follow the progressive disclosure philosophy
3. Update examples to clearly show WHEN and WHY to use each API level

---

**Note:** These examples will be removed in a future release once migration is complete. For new learning, use the main examples/ directory (01_hello_world.py and up).
