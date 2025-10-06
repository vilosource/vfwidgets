#!/bin/bash
# ViloxTerm System-Wide Installation Script
# Installs ViloxTerm to /usr/local with full GNOME desktop integration
#
# Usage: sudo ./install-system.sh

set -e  # Exit on error

echo "=========================================="
echo "ViloxTerm System Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "   Please run: sudo ./install-system.sh"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the binary
BINARY=""
if [ -f "$SCRIPT_DIR/ViloXTerm.bin" ]; then
    BINARY="$SCRIPT_DIR/ViloXTerm.bin"
elif [ -f "$SCRIPT_DIR/ViloXTerm" ]; then
    BINARY="$SCRIPT_DIR/ViloXTerm"
else
    echo "❌ Error: ViloxTerm binary not found"
    echo "   Expected: ViloXTerm.bin or ViloXTerm"
    echo "   Please run 'make build' first"
    exit 1
fi

echo "📦 Found binary: $(basename "$BINARY")"
echo ""

# Installation paths
BIN_PATH="/usr/local/bin/viloxterm"
DESKTOP_FILE="$SCRIPT_DIR/viloxterm.desktop"
DESKTOP_INSTALL_PATH="/usr/local/share/applications/viloxterm.desktop"
ICON_SVG="$SCRIPT_DIR/icons/viloxterm.svg"
ICON_DIR="/usr/local/share/icons/hicolor"

# Check if desktop file exists
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "❌ Error: Desktop file not found: $DESKTOP_FILE"
    exit 1
fi

# Check if SVG icon exists
if [ ! -f "$ICON_SVG" ]; then
    echo "❌ Error: SVG icon not found: $ICON_SVG"
    echo "   Please ensure icons/viloxterm.svg exists"
    exit 1
fi

echo "🔍 Pre-flight checks passed"
echo ""

# Step 1: Install binary
echo "📦 Installing binary..."
install -Dm755 "$BINARY" "$BIN_PATH"
echo "  ✅ Installed: $BIN_PATH"
echo ""

# Step 2: Install SVG icon (scalable)
echo "🎨 Installing icons..."
mkdir -p "$ICON_DIR/scalable/apps"
install -Dm644 "$ICON_SVG" "$ICON_DIR/scalable/apps/viloxterm.svg"
echo "  ✅ Scalable: $ICON_DIR/scalable/apps/viloxterm.svg"

# Step 3: Install PNG icons if available
for size in 16 22 24 32 48 64 128 256 512; do
    PNG_ICON="$SCRIPT_DIR/icons/viloxterm-${size}.png"
    if [ -f "$PNG_ICON" ]; then
        mkdir -p "$ICON_DIR/${size}x${size}/apps"
        install -Dm644 "$PNG_ICON" "$ICON_DIR/${size}x${size}/apps/viloxterm.png"
        echo "  ✅ ${size}x${size}: $ICON_DIR/${size}x${size}/apps/viloxterm.png"
    fi
done
echo ""

# Step 4: Install desktop file
echo "🖥️  Installing desktop entry..."
mkdir -p "$(dirname "$DESKTOP_INSTALL_PATH")"
install -Dm644 "$DESKTOP_FILE" "$DESKTOP_INSTALL_PATH"
echo "  ✅ Desktop file: $DESKTOP_INSTALL_PATH"
echo ""

# Step 5: Validate desktop file
echo "✔️  Validating desktop file..."
if command -v desktop-file-validate &> /dev/null; then
    if desktop-file-validate "$DESKTOP_INSTALL_PATH" 2>&1; then
        echo "  ✅ Desktop file is valid"
    else
        echo "  ⚠️  Desktop file validation warnings (non-critical)"
    fi
else
    echo "  ⚠️  desktop-file-validate not found (skipping validation)"
fi
echo ""

# Step 6: Update icon cache
echo "🔄 Updating icon cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
    echo "  ✅ Icon cache updated"
else
    echo "  ⚠️  gtk-update-icon-cache not found (icons may not appear immediately)"
fi
echo ""

# Step 7: Update desktop database
echo "🔄 Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/local/share/applications 2>/dev/null || true
    echo "  ✅ Desktop database updated"
else
    echo "  ⚠️  update-desktop-database not found"
fi
echo ""

echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "ViloxTerm has been installed system-wide:"
echo "  • Binary:       $BIN_PATH"
echo "  • Desktop file: $DESKTOP_INSTALL_PATH"
echo "  • Icons:        $ICON_DIR/*/apps/viloxterm.*"
echo ""
echo "You can now:"
echo "  1. Launch from GNOME Activities (search for 'ViloxTerm')"
echo "  2. Run from terminal: viloxterm"
echo "  3. Find it in your application menu"
echo ""
echo "To uninstall, run: sudo ./uninstall-system.sh"
echo ""
