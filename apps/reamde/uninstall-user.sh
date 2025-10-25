#!/bin/bash
# Reamde User-Level Uninstallation Script
# Removes Reamde from user directories
#
# Usage: ./uninstall-user.sh

set -e  # Exit on error

echo "=========================================="
echo "Reamde User Uninstallation"
echo "=========================================="
echo ""

# User installation paths
BIN_PATH="$HOME/bin/reamde"
DESKTOP_INSTALL_PATH="$HOME/.local/share/applications/reamde.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor"

# Track if anything was removed
REMOVED=0

# Remove binary
if [ -f "$BIN_PATH" ]; then
    echo "🗑️  Removing binary..."
    rm -f "$BIN_PATH"
    echo "  ✅ Removed: $BIN_PATH"
    REMOVED=1
else
    echo "  ℹ️  Binary not found: $BIN_PATH"
fi
echo ""

# Remove desktop file
if [ -f "$DESKTOP_INSTALL_PATH" ]; then
    echo "🗑️  Removing desktop entry..."
    rm -f "$DESKTOP_INSTALL_PATH"
    echo "  ✅ Removed: $DESKTOP_INSTALL_PATH"
    REMOVED=1
else
    echo "  ℹ️  Desktop file not found: $DESKTOP_INSTALL_PATH"
fi
echo ""

# Remove icons
echo "🗑️  Removing icons..."
ICONS_REMOVED=0
for size in scalable 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
    if [ "$size" = "scalable" ]; then
        ICON_PATH="$ICON_DIR/$size/apps/reamde.svg"
    else
        ICON_PATH="$ICON_DIR/$size/apps/reamde.png"
    fi

    if [ -f "$ICON_PATH" ]; then
        rm -f "$ICON_PATH"
        echo "  ✅ Removed: $ICON_PATH"
        ICONS_REMOVED=1
        REMOVED=1
    fi
done

if [ $ICONS_REMOVED -eq 0 ]; then
    echo "  ℹ️  No icons found to remove"
fi
echo ""

# Update icon cache
if [ $ICONS_REMOVED -eq 1 ]; then
    echo "🔄 Updating icon cache..."
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
        echo "  ✅ Icon cache updated"
    else
        echo "  ⚠️  gtk-update-icon-cache not found"
    fi
    echo ""
fi

# Update desktop database
echo "🔄 Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "  ✅ Desktop database updated"
else
    echo "  ⚠️  update-desktop-database not found"
fi
echo ""

if [ $REMOVED -eq 1 ]; then
    echo "=========================================="
    echo "✅ Uninstallation Complete!"
    echo "=========================================="
    echo ""
    echo "Reamde has been removed from your user directories."
    echo ""
    echo "Note: You may need to log out and log back in for the"
    echo "      application to disappear from GNOME Activities."
    echo ""
else
    echo "=========================================="
    echo "ℹ️  Nothing to Uninstall"
    echo "=========================================="
    echo ""
    echo "Reamde was not found in user directories."
    echo "It may have been installed system-wide or not at all."
    echo ""
fi
