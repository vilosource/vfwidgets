#!/bin/bash
# ViloxTerm Build Script
# Creates a single executable binary using pyside6-deploy

set -e  # Exit on error

echo "======================================"
echo "ViloXTerm Binary Build Script"
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
rm -f ViloXTerm ViloXTerm.exe ViloXTerm.bin ViloXTerm.app
echo "✅ Cleaned"
echo ""

# Install dependencies in development mode if needed
echo "📦 Ensuring all dependencies are installed..."
pip install -e . -q
echo "✅ Dependencies ready"
echo ""

# Run pyside6-deploy
echo "🔨 Building ViloXTerm binary..."
echo "   This may take several minutes..."
echo ""

if pyside6-deploy -c pysidedeploy.spec -f; then
    echo ""
    echo "======================================"
    echo "✅ Build Complete!"
    echo "======================================"
    echo ""

    # Find and report the created binary
    if [ -f "ViloXTerm.bin" ]; then
        SIZE=$(du -h "ViloXTerm.bin" | cut -f1)
        echo "📦 Binary created: ViloXTerm.bin (${SIZE})"
        echo ""
        echo "Run with: ./ViloXTerm.bin"
    elif [ -f "ViloXTerm" ]; then
        SIZE=$(du -h "ViloXTerm" | cut -f1)
        echo "📦 Binary created: ViloXTerm (${SIZE})"
        echo ""
        echo "Run with: ./ViloXTerm"
    elif [ -f "ViloXTerm.exe" ]; then
        SIZE=$(du -h "ViloXTerm.exe" | cut -f1)
        echo "📦 Binary created: ViloXTerm.exe (${SIZE})"
        echo ""
        echo "Run with: ./ViloXTerm.exe"
    elif [ -d "ViloXTerm.app" ]; then
        SIZE=$(du -sh "ViloXTerm.app" | cut -f1)
        echo "📦 App bundle created: ViloXTerm.app (${SIZE})"
        echo ""
        echo "Run with: open ViloXTerm.app"
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
