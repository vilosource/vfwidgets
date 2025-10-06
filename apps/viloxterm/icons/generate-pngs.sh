#!/bin/bash
# Generate PNG icons from SVG source
# Requires: inkscape or imagemagick (rsvg-convert)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SVG_SOURCE="$SCRIPT_DIR/viloxterm.svg"

# Icon sizes to generate (following freedesktop.org standards)
SIZES=(16 22 24 32 48 64 128 256 512)

echo "=========================================="
echo "ViloxTerm PNG Icon Generation"
echo "=========================================="
echo ""

if [ ! -f "$SVG_SOURCE" ]; then
    echo "❌ Error: SVG source not found: $SVG_SOURCE"
    exit 1
fi

echo "📄 Source: $SVG_SOURCE"
echo ""

# Check for available tools (prefer inkscape, fallback to imagemagick)
if command -v inkscape &> /dev/null; then
    CONVERTER="inkscape"
    echo "✅ Using Inkscape for conversion"
elif command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
    echo "✅ Using ImageMagick for conversion"
elif command -v rsvg-convert &> /dev/null; then
    CONVERTER="rsvg"
    echo "✅ Using rsvg-convert for conversion"
else
    echo "❌ Error: No SVG converter found"
    echo "   Please install one of:"
    echo "   - inkscape:     sudo apt install inkscape"
    echo "   - imagemagick:  sudo apt install imagemagick"
    echo "   - rsvg-convert: sudo apt install librsvg2-bin"
    exit 1
fi

echo ""
echo "🔨 Generating PNG icons..."
echo ""

# Generate PNG files for each size
for size in "${SIZES[@]}"; do
    output="$SCRIPT_DIR/viloxterm-${size}.png"

    case $CONVERTER in
        inkscape)
            inkscape "$SVG_SOURCE" \
                --export-type=png \
                --export-filename="$output" \
                --export-width=$size \
                --export-height=$size \
                &> /dev/null
            ;;
        imagemagick)
            convert -background none \
                -resize ${size}x${size} \
                "$SVG_SOURCE" \
                "$output"
            ;;
        rsvg)
            rsvg-convert -w $size -h $size \
                "$SVG_SOURCE" \
                -o "$output"
            ;;
    esac

    if [ -f "$output" ]; then
        file_size=$(du -h "$output" | cut -f1)
        echo "  ✅ ${size}x${size} → viloxterm-${size}.png (${file_size})"
    else
        echo "  ❌ Failed to generate ${size}x${size}"
    fi
done

echo ""
echo "=========================================="
echo "✅ Icon generation complete!"
echo "=========================================="
echo ""
echo "Generated files:"
ls -lh "$SCRIPT_DIR"/*.png 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
