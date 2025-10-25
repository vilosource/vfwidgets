#!/bin/bash
# Reamde Build Script
# Creates a single executable binary using pyside6-deploy

set -e  # Exit on error

echo "======================================"
echo "Reamde Binary Build Script"
echo "======================================"
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not running in a virtual environment"
    echo "   It's recommended to use a venv to avoid version conflicts"
    echo ""
fi

# Check if pyside6-deploy is available
if ! command -v pyside6-deploy &> /dev/null; then
    echo "❌ Error: pyside6-deploy not found"
    echo "   Install with: pip install PySide6"
    exit 1
fi

echo "✅ pyside6-deploy found"

# Check for required Python packages
echo "📦 Checking build dependencies..."
python -c "import tomlkit" 2>/dev/null || {
    echo "   Installing tomlkit (required by pyside6-deploy)..."
    pip install tomlkit -q
}
python -c "import nuitka" 2>/dev/null || {
    echo "   Installing Nuitka (required for compilation)..."
    pip install nuitka -q
}
echo "✅ Build dependencies ready"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf deployment
rm -f Reamde Reamde.exe Reamde.bin Reamde.app
echo "✅ Cleaned"
echo ""

# Install dependencies in development mode if needed
echo "📦 Ensuring all dependencies are installed..."
pip install -e . -q
echo "✅ Dependencies ready"
echo ""

# Run pyside6-deploy
echo "🔨 Building Reamde binary..."
echo "   This may take several minutes..."
echo ""

if pyside6-deploy -c pysidedeploy.spec -f; then
    echo ""
    echo "======================================"
    echo "✅ Build Complete!"
    echo "======================================"
    echo ""

    # Find and report the created binary
    if [ -f "Reamde.bin" ]; then
        SIZE=$(du -h "Reamde.bin" | cut -f1)
        echo "📦 Binary created: Reamde.bin (${SIZE})"
        echo ""
        echo "Run with: ./Reamde.bin"
    elif [ -f "Reamde" ]; then
        SIZE=$(du -h "Reamde" | cut -f1)
        echo "📦 Binary created: Reamde (${SIZE})"
        echo ""
        echo "Run with: ./Reamde"
    elif [ -f "Reamde.exe" ]; then
        SIZE=$(du -h "Reamde.exe" | cut -f1)
        echo "📦 Binary created: Reamde.exe (${SIZE})"
        echo ""
        echo "Run with: ./Reamde.exe"
    elif [ -d "Reamde.app" ]; then
        SIZE=$(du -sh "Reamde.app" | cut -f1)
        echo "📦 App bundle created: Reamde.app (${SIZE})"
        echo ""
        echo "Run with: open Reamde.app"
    else
        echo "⚠️  Warning: Binary not found at expected location"
        exit 1
    fi
else
    echo ""
    echo "======================================"
    echo "❌ Build Failed!"
    echo "======================================"
    echo ""
    echo "Check the error messages above for details."
    exit 1
fi
