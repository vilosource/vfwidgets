#!/bin/bash
# Test single-instance behavior

cd /home/kuja/GitHub/vfwidgets/apps/reamde

echo "==========================================="
echo "Single-Instance Behavior Test"
echo "==========================================="
echo ""

# Clean up
rm -f /tmp/vfwidgets-reamde-$USER
echo "Cleaned up stale socket"
echo ""

echo "Step 1: Launch primary instance with DEMO1.md"
echo "----------------------------------------------"
python -m reamde DEMO1.md &
PRIMARY_PID=$!
echo "Primary instance PID: $PRIMARY_PID"
echo "Waiting for it to start..."
sleep 2
echo ""

# Check socket
if [ -e /tmp/vfwidgets-reamde-$USER ]; then
    echo "✅ Socket created: /tmp/vfwidgets-reamde-$USER"
else
    echo "❌ Socket NOT created!"
    kill $PRIMARY_PID 2>/dev/null
    exit 1
fi
echo ""

echo "Step 2: Launch secondary instance with DEMO2.md"
echo "------------------------------------------------"
echo "This should:"
echo "  - Connect to primary instance"
echo "  - Send 'open' message"
echo "  - Exit with code 0"
echo "  - Open DEMO2.md in primary window's new tab"
echo ""

python -m reamde DEMO2.md
EXIT_CODE=$?

echo ""
echo "Secondary instance exit code: $EXIT_CODE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Secondary instance exited cleanly (code 0)"
else
    echo "❌ Secondary instance exit code: $EXIT_CODE (expected 0)"
fi
echo ""

echo "Step 3: Launch another instance with same file (DEMO1.md)"
echo "-----------------------------------------------------------"
echo "This should focus existing tab, not create new one"
echo ""

python -m reamde DEMO1.md
EXIT_CODE=$?

echo ""
echo "Third instance exit code: $EXIT_CODE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Third instance exited cleanly (code 0)"
else
    echo "❌ Third instance exit code: $EXIT_CODE (expected 0)"
fi
echo ""

echo "==========================================="
echo "Test Complete"
echo "==========================================="
echo ""
echo "The primary instance is still running (PID: $PRIMARY_PID)"
echo "You should see:"
echo "  - A window with 2 tabs: DEMO1.md and DEMO2.md"
echo "  - DEMO2.md tab should be focused"
echo ""
echo "Press Ctrl+C to stop, or run: kill $PRIMARY_PID"
echo ""

# Keep script running so user can inspect
wait $PRIMARY_PID
