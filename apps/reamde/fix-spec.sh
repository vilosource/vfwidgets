#!/bin/bash
# Fix pysidedeploy.spec for current machine
# Updates python_path and input_file to match current environment
#
# Run this script after:
# - git pull on a new machine
# - changing virtual environment
# - reinstalling Python

set -e

echo "======================================"
echo "Fixing pysidedeploy.spec"
echo "======================================"
echo ""

SPEC_FILE="pysidedeploy.spec"

if [ ! -f "$SPEC_FILE" ]; then
    echo "❌ Error: $SPEC_FILE not found"
    exit 1
fi

# Get current Python path
PYTHON_PATH=$(which python3)
echo "📍 Detected Python: $PYTHON_PATH"

# Get current script directory (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="$SCRIPT_DIR/reamde_main.py"
echo "📍 Input file: $INPUT_FILE"

# Get PySide6 icon path (fallback to default if not found)
PYSIDE_ICON=$(python3 -c "import PySide6; import os; print(os.path.join(os.path.dirname(PySide6.__file__), 'scripts/deploy_lib/pyside_icon.jpg'))" 2>/dev/null || echo "")
if [ -z "$PYSIDE_ICON" ] || [ ! -f "$PYSIDE_ICON" ]; then
    echo "⚠️  Warning: PySide6 icon not found, using placeholder"
    PYSIDE_ICON="/tmp/pyside_icon.jpg"
fi
echo "📍 Icon: $PYSIDE_ICON"
echo ""

# Update spec file
echo "🔧 Updating $SPEC_FILE..."

# Escape paths for sed
PYTHON_PATH_ESCAPED=$(echo "$PYTHON_PATH" | sed 's/[\/&]/\\&/g')
INPUT_FILE_ESCAPED=$(echo "$INPUT_FILE" | sed 's/[\/&]/\\&/g')
PYSIDE_ICON_ESCAPED=$(echo "$PYSIDE_ICON" | sed 's/[\/&]/\\&/g')

# Update python_path
sed -i "s|^python_path = .*|python_path = $PYTHON_PATH_ESCAPED|" "$SPEC_FILE"

# Update input_file
sed -i "s|^input_file = .*|input_file = $INPUT_FILE_ESCAPED|" "$SPEC_FILE"

# Update icon
sed -i "s|^icon = .*|icon = $PYSIDE_ICON_ESCAPED|" "$SPEC_FILE"

echo "✅ Updated $SPEC_FILE"
echo ""
echo "Changes:"
echo "  python_path = $PYTHON_PATH"
echo "  input_file = $INPUT_FILE"
echo "  icon = $PYSIDE_ICON"
echo ""
echo "You can now run: make build"
echo ""
