#!/usr/bin/env python3
"""Verify Phase 0 implementation completeness."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def verify_imports():
    """Verify all required imports work."""
    errors = []

    # Core types
    try:
        from vfwidgets_multisplit.core.types import (
            Bounds,
            Direction,
            InvalidStructureError,
            NodeId,
            Orientation,
            PaneError,
            PaneId,
            PaneNotFoundError,
            Position,
            Rect,
            Size,
            WherePosition,
            WidgetId,
        )
    except ImportError as e:
        errors.append(f"Core types import error: {e}")

    # Core utilities
    try:
        from vfwidgets_multisplit.core.utils import (
            generate_node_id,
            generate_pane_id,
            generate_widget_id,
            parse_widget_id,
            validate_id_format,
            validate_ratio,
            validate_ratios,
        )
    except ImportError as e:
        errors.append(f"Core utils import error: {e}")

    # Node system
    try:
        from vfwidgets_multisplit.core.nodes import LeafNode, PaneNode, SplitNode
    except ImportError as e:
        errors.append(f"Node system import error: {e}")

    # Visitor pattern
    try:
        from vfwidgets_multisplit.core.visitor import PaneVisitor
    except ImportError as e:
        errors.append(f"Visitor pattern import error: {e}")

    # Tree utilities
    try:
        from vfwidgets_multisplit.core.tree_utils import (
            calculate_depth,
            collect_leaves,
            find_node,
            normalize_ratios,
            validate_structure,
        )
    except ImportError as e:
        errors.append(f"Tree utils import error: {e}")

    # Signal system
    try:
        from vfwidgets_multisplit.core.signals import AbstractSignal, ModelSignals
    except ImportError as e:
        errors.append(f"Signal system import error: {e}")

    # Signal bridge
    try:
        from vfwidgets_multisplit.bridge.signal_bridge import SignalBridge
    except ImportError as e:
        errors.append(f"Signal bridge import error: {e}")

    # Geometry
    try:
        from vfwidgets_multisplit.core.geometry import GeometryCalculator
    except ImportError as e:
        errors.append(f"Geometry import error: {e}")

    # Reconciler
    try:
        from vfwidgets_multisplit.view.tree_reconciler import (
            DiffResult,
            ReconcilerOperations,
            TreeReconciler,
        )
    except ImportError as e:
        errors.append(f"Reconciler import error: {e}")

    # Transaction
    try:
        from vfwidgets_multisplit.controller.transaction import (
            NestedTransactionContext,
            TransactionContext,
            atomic_operation,
            transaction,
        )
    except ImportError as e:
        errors.append(f"Transaction import error: {e}")

    # Controller
    try:
        from vfwidgets_multisplit.controller.controller import PaneController
    except ImportError as e:
        errors.append(f"Controller import error: {e}")

    return errors

def verify_functionality():
    """Verify basic functionality works."""
    errors = []

    try:
        # Test ID generation
        from vfwidgets_multisplit.core.utils import (
            generate_node_id,
            generate_pane_id,
            generate_widget_id,
        )

        pane_id = generate_pane_id()
        assert pane_id.startswith("pane_")

        node_id = generate_node_id()
        assert node_id.startswith("node_")

        widget_id = generate_widget_id("editor", "main.py")
        assert str(widget_id) == "editor:main.py"

    except Exception as e:
        errors.append(f"ID generation error: {e}")

    try:
        # Test node creation
        from vfwidgets_multisplit.core.nodes import LeafNode, SplitNode
        from vfwidgets_multisplit.core.types import Orientation

        leaf = LeafNode(pane_id="pane_test", widget_id="editor:test.py")
        assert leaf.pane_id == "pane_test"

        split = SplitNode(
            node_id="node_test",
            orientation=Orientation.HORIZONTAL,
            children=[],
            ratios=[]
        )
        assert split.node_id == "node_test"

    except Exception as e:
        errors.append(f"Node creation error: {e}")

    try:
        # Test signals
        from vfwidgets_multisplit.core.signals import AbstractSignal

        signal = AbstractSignal()
        called = []

        # Need to keep a reference to the handler for weak refs
        def handler(x):
            called.append(x)

        signal.connect(handler)
        signal.emit("test")
        assert called == ["test"], f"Expected ['test'], got {called}"

    except Exception as e:
        errors.append(f"Signal system error: {e}")

    try:
        # Test geometry
        from vfwidgets_multisplit.core.geometry import GeometryCalculator
        from vfwidgets_multisplit.core.types import Bounds

        GeometryCalculator()
        Bounds(0, 0, 800, 600)
        # Just verify it instantiates

    except Exception as e:
        errors.append(f"Geometry error: {e}")

    return errors

def main():
    """Run verification."""
    print("Verifying Phase 0 Implementation...")
    print("=" * 60)

    # Check imports
    print("\n1. Checking imports...")
    import_errors = verify_imports()
    if import_errors:
        print("❌ Import errors found:")
        for error in import_errors:
            print(f"   - {error}")
    else:
        print("✅ All imports successful")

    # Check functionality
    print("\n2. Checking functionality...")
    func_errors = verify_functionality()
    if func_errors:
        print("❌ Functionality errors found:")
        for error in func_errors:
            print(f"   - {error}")
    else:
        print("✅ All functionality tests passed")

    # Summary
    print("\n" + "=" * 60)
    total_errors = import_errors + func_errors
    if total_errors:
        print(f"❌ Found {len(total_errors)} issues")
        return 1
    else:
        print("✅ Phase 0 implementation complete and verified!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
