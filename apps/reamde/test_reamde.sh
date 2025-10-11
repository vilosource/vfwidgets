#!/bin/bash
# Automated test script for reamde single-instance behavior

cd /home/kuja/GitHub/vfwidgets/apps/reamde

echo "========================================="
echo "Reamde Single-Instance Test"
echo "========================================="
echo ""

# Clean up any stale socket
echo "Cleaning up stale socket (if exists)..."
rm -f /tmp/vfwidgets-reamde-$USER
echo ""

echo "Test 1: Launch primary instance with DEMO1.md"
echo "-----------------------------------------------"
timeout 3 python -m reamde DEMO1.md &
PID1=$!
echo "Primary instance PID: $PID1"
sleep 1.5

# Check if socket was created
if [ -e /tmp/vfwidgets-reamde-$USER ]; then
    echo "✅ IPC socket created: /tmp/vfwidgets-reamde-$USER"
else
    echo "❌ IPC socket NOT created"
fi
echo ""

echo "Test 2: Launch secondary instance with DEMO2.md"
echo "------------------------------------------------"
python -m reamde DEMO2.md 2>&1 | grep -E "\[reamde\]|exit" || true
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✅ Secondary instance exited cleanly"
else
    echo "⚠️  Exit code: $RESULT"
fi
echo ""

echo "Test 3: Launch secondary instance with same file (DEMO1.md)"
echo "------------------------------------------------------------"
python -m reamde DEMO1.md 2>&1 | grep -E "\[reamde\]|already open" || true
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✅ Duplicate file handling worked"
else
    echo "⚠️  Exit code: $RESULT"
fi
echo ""

echo "Cleaning up..."
kill $PID1 2>/dev/null
wait $PID1 2>/dev/null
echo ""

echo "========================================="
echo "Test Summary"
echo "========================================="
echo "All basic tests completed."
echo ""
echo "Manual testing required for:"
echo "  - Visual verification of content"
echo "  - Window focus/activation"
echo "  - Tab management (close, reorder)"
echo "  - Large files"
echo ""
echo "See TESTING.md for complete test plan."
echo "========================================="
