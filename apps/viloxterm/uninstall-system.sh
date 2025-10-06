#!/bin/bash
# ViloxTerm System-Wide Uninstallation Script
# Removes ViloxTerm from /usr/local and cleans up desktop integration
#
# Usage: sudo ./uninstall-system.sh

set -e  # Exit on error

echo "=========================================="
echo "ViloxTerm System Uninstallation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "   Please run: sudo ./uninstall-system.sh"
    exit 1
fi

# Installation paths to remove
BIN_PATH="/usr/local/bin/viloxterm"
DESKTOP_INSTALL_PATH="/usr/local/share/applications/viloxterm.desktop"
ICON_DIR="/usr/local/share/icons/hicolor"

echo "🔍 Checking for installed files..."
echo ""

FOUND_FILES=0

# Check binary
if [ -f "$BIN_PATH" ]; then
    echo "  ✓ Found binary: $BIN_PATH"
    FOUND_FILES=$((FOUND_FILES + 1))
fi

# Check desktop file
if [ -f "$DESKTOP_INSTALL_PATH" ]; then
    echo "  ✓ Found desktop file: $DESKTOP_INSTALL_PATH"
    FOUND_FILES=$((FOUND_FILES + 1))
fi

# Check for icons
ICON_COUNT=$(find "$ICON_DIR" -name "viloxterm.*" 2>/dev/null | wc -l)
if [ "$ICON_COUNT" -gt 0 ]; then
    echo "  ✓ Found $ICON_COUNT icon file(s)"
    FOUND_FILES=$((FOUND_FILES + ICON_COUNT))
fi

echo ""

if [ "$FOUND_FILES" -eq 0 ]; then
    echo "✅ ViloxTerm is not installed (nothing to uninstall)"
    exit 0
fi

echo "Found $FOUND_FILES file(s) to remove"
echo ""

# Ask for confirmation
read -p "Proceed with uninstallation? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Uninstallation cancelled"
    exit 0
fi

echo ""
echo "🗑️  Removing ViloxTerm..."
echo ""

# Remove binary
if [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
    echo "  ✅ Removed binary: $BIN_PATH"
fi

# Remove desktop file
if [ -f "$DESKTOP_INSTALL_PATH" ]; then
    rm -f "$DESKTOP_INSTALL_PATH"
    echo "  ✅ Removed desktop file: $DESKTOP_INSTALL_PATH"
fi

# Remove icons
for size in scalable 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    ICON_PNG="$ICON_DIR/$size/apps/viloxterm.png"
    ICON_SVG="$ICON_DIR/$size/apps/viloxterm.svg"

    if [ -f "$ICON_PNG" ]; then
        rm -f "$ICON_PNG"
        echo "  ✅ Removed icon: $ICON_DIR/$size/apps/viloxterm.png"
    fi

    if [ -f "$ICON_SVG" ]; then
        rm -f "$ICON_SVG"
        echo "  ✅ Removed icon: $ICON_DIR/$size/apps/viloxterm.svg"
    fi
done

echo ""

# Update icon cache
echo "🔄 Updating icon cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
    echo "  ✅ Icon cache updated"
else
    echo "  ⚠️  gtk-update-icon-cache not found"
fi
echo ""

# Update desktop database
echo "🔄 Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/local/share/applications 2>/dev/null || true
    echo "  ✅ Desktop database updated"
else
    echo "  ⚠️  update-desktop-database not found"
fi
echo ""

echo "=========================================="
echo "✅ Uninstallation Complete!"
echo "=========================================="
echo ""
echo "ViloxTerm has been removed from your system."
echo ""
echo "Note: The icon may still appear in GNOME for a few seconds"
echo "      until the cache is fully refreshed."
echo ""
