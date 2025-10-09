#!/bin/bash
# Fix pysidedeploy.spec with current machine paths
# Run this after switching to a new machine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_FILE="$SCRIPT_DIR/pysidedeploy.spec"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Fixing pysidedeploy.spec for current machine..."

# Get current Python path (from direnv)
PYTHON_PATH=$(which python3)
echo "Detected Python: $PYTHON_PATH"

# Fix input_file to use relative path
sed -i "s|^input_file = .*|input_file = viloxterm_main.py|g" "$SPEC_FILE"

# Fix icon to use relative or empty (will use default)
sed -i "s|^icon = .*|icon =|g" "$SPEC_FILE"

# Fix python_path to current machine
sed -i "s|^python_path = .*|python_path = $PYTHON_PATH|g" "$SPEC_FILE"

echo "✅ Fixed pysidedeploy.spec:"
echo "  - input_file: viloxterm_main.py (relative)"
echo "  - icon: (empty, will use default)"
echo "  - python_path: $PYTHON_PATH"
echo ""
echo "You can now run: make build"
