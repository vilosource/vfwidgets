#!/usr/bin/env python3
"""
Prepare for Phase 0 Implementation

This script analyzes existing code and prepares for Phase 0 implementation.
It will:
1. Check what already exists
2. Identify what needs to be modified vs created new
3. Back up existing code
4. Prepare the structure for Phase 0
"""

import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "vfwidgets_multisplit"
BACKUP_DIR = PROJECT_ROOT / "wip" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def analyze_existing():
    """Analyze what already exists."""
    print("=" * 70)
    print("ANALYZING EXISTING CODE")
    print("=" * 70)
    print()

    # Check core/types.py
    types_file = SRC_ROOT / "core" / "types.py"
    if types_file.exists():
        print("✅ core/types.py EXISTS")
        with open(types_file) as f:
            content = f.read()

        print("  Contains:")
        if "PaneId = NewType" in content:
            print("    ✅ PaneId type")
        if "NodeId = NewType" in content:
            print("    ⚠️  NodeId type (NOT FOUND - needs adding)")
        else:
            print("    ❌ NodeId type (missing)")
        if "WidgetId = NewType" in content:
            print("    ⚠️  WidgetId type (NOT FOUND - needs adding)")
        else:
            print("    ❌ WidgetId type (missing)")

        if "class Orientation" in content:
            print("    ✅ Orientation enum")
        if "class WherePosition" in content:
            print("    ✅ WherePosition enum")
        if "class Direction" in content:
            print("    ✅ Direction enum")

        if "def generate_pane_id" in content:
            print("    ⚠️  generate_pane_id() (exists but in wrong file - should be in utils.py)")
        if "def validate_ratio" in content:
            print("    ⚠️  validate_ratio() (exists but in wrong file - should be in utils.py)")
        if "def normalize_ratios" in content:
            print("    ⚠️  normalize_ratios() (exists but in wrong file - should be in tree_utils.py)")

        if "class Size" in content:
            print("    ✅ Size dataclass")
        if "class Position" in content:
            print("    ✅ Position dataclass")
        if "class Rect" in content:
            print("    ✅ Rect dataclass")
        if "class Bounds" in content:
            print("    ⚠️  Bounds dataclass (NOT FOUND - needs adding)")
        else:
            print("    ❌ Bounds dataclass (missing)")

        print("\n  ⚠️  NOTE: Some functions are in types.py but should be moved:")
        print("     - generate_pane_id() → utils.py")
        print("     - validate_ratio(s)() → utils.py")
        print("     - normalize_ratios() → tree_utils.py")

    # Check for other existing files
    print("\n📁 OTHER FILES:")
    existing_files = {
        "core/__init__.py": SRC_ROOT / "core" / "__init__.py",
        "core/utils.py": SRC_ROOT / "core" / "utils.py",
        "core/nodes.py": SRC_ROOT / "core" / "nodes.py",
        "view/__init__.py": SRC_ROOT / "view" / "__init__.py",
        "controller/__init__.py": SRC_ROOT / "controller" / "__init__.py",
    }

    for name, path in existing_files.items():
        if path.exists():
            print(f"  ✅ {name} exists")
        else:
            print(f"  ❌ {name} missing")

def create_backup():
    """Create backup of existing code."""
    print("\n" + "=" * 70)
    print("CREATING BACKUP")
    print("=" * 70)

    if (SRC_ROOT / "core" / "types.py").exists():
        print(f"\nBacking up to: {BACKUP_DIR}")
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # Backup core/types.py
        src = SRC_ROOT / "core" / "types.py"
        dst = BACKUP_DIR / "types.py.backup"
        shutil.copy2(src, dst)
        print(f"  ✅ Backed up core/types.py → {dst.name}")

        # Save analysis
        analysis_file = BACKUP_DIR / "analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write("BACKUP ANALYSIS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("Files backed up:\n")
            f.write("- core/types.py\n")
            f.write("\nReason: Preparing for Phase 0 implementation\n")
            f.write("\nExisting functionality to preserve:\n")
            f.write("- PaneId type\n")
            f.write("- Orientation, WherePosition, Direction enums\n")
            f.write("- Exception classes\n")
            f.write("- Size, Position, Rect dataclasses\n")
            f.write("\nFunctionality to move:\n")
            f.write("- generate_pane_id() → utils.py\n")
            f.write("- validate_ratio(s)() → utils.py\n")
            f.write("- normalize_ratios() → tree_utils.py\n")
            f.write("\nFunctionality to add:\n")
            f.write("- NodeId, WidgetId types\n")
            f.write("- Bounds dataclass\n")

        print(f"  ✅ Analysis saved to {analysis_file.name}")
    else:
        print("  ℹ️  No existing files to backup")

def prepare_structure():
    """Create necessary directories and __init__.py files."""
    print("\n" + "=" * 70)
    print("PREPARING STRUCTURE")
    print("=" * 70)

    directories = [
        SRC_ROOT / "core",
        SRC_ROOT / "view",
        SRC_ROOT / "controller",
    ]

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True)
            print(f"  ✅ Created {directory.relative_to(PROJECT_ROOT)}/")

        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Package initialization."""\n')
            print(f"  ✅ Created {init_file.relative_to(PROJECT_ROOT)}")

def create_migration_guide():
    """Create a guide for migrating existing code."""
    guide_path = PROJECT_ROOT / "wip" / "phase0-migration-GUIDE.md"

    content = """# Phase 0 Migration Guide

## Existing Code Analysis

### core/types.py
**Status**: EXISTS - Needs modification

**Keep in place**:
- PaneId type definition
- Orientation, WherePosition, Direction enums
- All exception classes
- Size, Position, Rect dataclasses

**Add**:
- NodeId = NewType('NodeId', str)
- WidgetId = NewType('WidgetId', str)
- Bounds dataclass (see P0.4.1)

**Move to core/utils.py** (P0.1.2):
- generate_pane_id() function
- Lines 96-99 in current file

**Move to core/tree_utils.py** (P0.2.3):
- normalize_ratios() function
- validate_ratio() function
- validate_ratios() function
- Lines 102-128 in current file

## Implementation Order

### Step 1: Enhance types.py (P0.1.1)
```python
# Add after line 15
NodeId = NewType('NodeId', str)
WidgetId = NewType('WidgetId', str)

# Add Bounds dataclass (P0.4.1) after Rect class
@dataclass(frozen=True)
class Bounds:
    x: int
    y: int
    width: int
    height: int
    # ... rest of implementation
```

### Step 2: Create utils.py (P0.1.2)
Move these functions from types.py:
- generate_pane_id() (lines 96-99)

Add new functions:
- generate_node_id()
- generate_widget_id()
- validate_id_format()
- parse_widget_id()

### Step 3: Continue with remaining tasks
Follow P0.2.1 onwards as documented in phase0-tasks-IMPLEMENTATION.md

## Testing Strategy

1. After each modification, run:
   ```bash
   python -c "from vfwidgets_multisplit.core.types import PaneId, NodeId, WidgetId"
   ```

2. Ensure backward compatibility:
   ```python
   # Old imports should still work
   from vfwidgets_multisplit.core.types import PaneId, Orientation
   ```

3. Run validation script:
   ```bash
   python wip/run_phase0_tests.py
   ```

## Notes

- The existing types.py has good foundation but mixes concerns
- Functions will be moved to appropriate modules for better organization
- All existing functionality will be preserved
- New functionality will be added incrementally
"""

    guide_path.write_text(content)
    print(f"\n✅ Migration guide created: {guide_path.relative_to(PROJECT_ROOT)}")

def main():
    print("PHASE 0 PREPARATION SCRIPT")
    print("=" * 70)
    print()

    # Analyze what exists
    analyze_existing()

    # Create backup
    create_backup()

    # Prepare structure
    prepare_structure()

    # Create migration guide
    create_migration_guide()

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()
    print("1. ✅ Existing core/types.py has a good foundation")
    print("2. ⚠️  Some refactoring needed:")
    print("   - Add missing types (NodeId, WidgetId, Bounds)")
    print("   - Move utility functions to appropriate modules")
    print("3. 📋 Follow the migration guide: wip/phase0-migration-GUIDE.md")
    print("4. 🚀 Start with task P0.1.1 (Enhance Type System)")
    print()
    print("Ready to begin Phase 0 implementation!")
    print("\nNext command:")
    print("> Use the multisplit-developer agent to implement task P0.1.1")

if __name__ == "__main__":
    main()
