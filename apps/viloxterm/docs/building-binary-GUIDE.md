# Building ViloxTerm Binary Distribution

**Status**: Production Ready
**Last Updated**: 2025-10-04

This guide covers how to build ViloxTerm as a single executable binary for distribution.

---

## Overview

ViloxTerm uses **pyside6-deploy**, Qt's official deployment tool that wraps Nuitka to create standalone executables. This produces a single binary file that can run without requiring Python or any dependencies to be installed.

### Why pyside6-deploy?

- **Official Qt Tool**: Maintained by the Qt for Python team
- **Nuitka-based**: Compiles Python to C for better performance
- **Cross-platform**: Works on Linux, Windows, and macOS
- **Single File**: Creates one executable with `--onefile` mode
- **QWebEngineView Support**: Handles complex Qt dependencies automatically

---

## Prerequisites

### All Platforms

1. **Python 3.9+** with pip
2. **Virtual environment** (recommended)
3. **Build dependencies**:
   - `PySide6` (includes pyside6-deploy)
   - `Nuitka` (Python compiler)
   - `tomlkit` (TOML parser for pyside6-deploy)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install ViloxTerm in development mode
pip install -e .

# Install build dependencies (handled automatically by build.sh)
pip install nuitka tomlkit
```

### Platform-Specific Requirements

#### Linux
- **readelf** (usually pre-installed)
- **patchelf** for binary patching:
  ```bash
  # Ubuntu/Debian
  sudo apt install patchelf

  # Fedora
  sudo dnf install patchelf
  ```

#### Windows
- **dumpbin** from MSVC (Visual Studio Build Tools)
- Install from: https://visualstudio.microsoft.com/downloads/

#### macOS
- **dyld_info** (macOS 12+, pre-installed)
- **Xcode Command Line Tools**:
  ```bash
  xcode-select --install
  ```

---

## Quick Build

### Using the Build Script (Recommended)

**Linux/macOS:**
```bash
cd apps/viloxterm
./build.sh
```

**Windows (PowerShell):**
```powershell
cd apps\viloxterm
.\build.ps1
```

The script will:
1. Check for required tools (pyside6-deploy, nuitka, tomlkit)
2. Clean previous builds (deployment/, ViloXTerm.exe)
3. Install project dependencies (pip install -e .)
4. Run pyside6-deploy with pysidedeploy.spec
5. Report the created binary with size

**Windows Notes:**
- Use PowerShell (pre-installed on Windows 7+)
- Requires Visual Studio Build Tools (for dumpbin)
- Creates `ViloXTerm.exe` (typically 200-300 MB)
- First build may take 10-15 minutes (subsequent builds faster)

### Manual Build (All Platforms)

```bash
cd apps/viloxterm
pip install -e .
pyside6-deploy -c pysidedeploy.spec -f
```

---

## Build Configuration

The build is configured via `pysidedeploy.spec`:

```ini
[app]
title = ViloxTerm
input_file = src/viloxterm/__main__.py

[python]
packages = PySide6==6.9.0,vfwidgets-theme-system,...

[qt]
modules = Core,Gui,Widgets,WebEngineWidgets,WebEngineCore,WebChannel,Network

[nuitka]
mode = onefile
jobs = 4
```

### Key Configuration Options

#### `[nuitka]` Section

- **mode**:
  - `onefile` - Single executable (larger, slower startup)
  - `standalone` - Directory with executable + libs (smaller exe, faster startup)

- **lto**: Link-time optimization (slower build, smaller binary)

- **jobs**: Parallel compilation jobs (set to CPU core count)

- **extra_args**: Additional Nuitka flags
  - `--enable-plugin=pyside6` - Required for PySide6
  - `--follow-imports` - Include all imports
  - `--nofollow-import-to=pytest` - Exclude dev dependencies

#### `[qt]` Section

- **modules**: Qt modules to include (keep minimal for smaller binary)
- **excluded_qml_plugins**: QML plugins to exclude (ViloxTerm doesn't use QML)

---

## Build Artifacts

After building, you'll find:

### Linux
- `ViloXTerm` or `ViloXTerm.bin` - Single executable binary
- `deployment/` - Temporary build directory (can be deleted)

### Windows
- `ViloXTerm.exe` - Windows executable
- `deployment/` - Temporary build directory

### macOS
- `ViloXTerm.app` - macOS application bundle
- Right-click > Show Package Contents to see internal structure

---

## Binary Size Expectations

ViloxTerm includes Qt WebEngine, which is a large dependency:

| Platform | Approximate Size | Notes |
|----------|-----------------|-------|
| Linux | 150-250 MB | Includes libQt6WebEngineCore.so (~176MB) |
| Windows | 200-300 MB | Includes Qt WebEngine DLLs |
| macOS | 200-300 MB | Includes frameworks |

### Size Optimization Tips

1. **Use standalone mode** instead of onefile (faster, seems smaller when compressed)
2. **Enable LTO** (link-time optimization): `lto = yes` in spec file
3. **Exclude unused Qt modules** in `[qt]` section
4. **Strip debug symbols** (Linux):
   ```bash
   strip ViloxTerm
   ```
5. **Compress final binary** with UPX (not recommended for WebEngine apps)

---

## GNOME Desktop Integration

ViloxTerm includes comprehensive GNOME desktop integration for Linux systems, following the freedesktop.org specification.

### Components

1. **Desktop Entry** (`viloxterm.desktop`)
   - Appears in GNOME Activities and application grid
   - Searchable by keywords: terminal, shell, command, bash, etc.
   - Categories: System, TerminalEmulator, Utility

2. **Icon Theme**
   - SVG icon (scalable, any resolution)
   - PNG icons (16, 22, 24, 32, 48, 64, 128, 256, 512px)
   - Follows hicolor icon theme specification
   - Modern terminal design with window chrome and >_ prompt

3. **Installation Scripts**
   - `install-system.sh` - System-wide installation with validation
   - `uninstall-system.sh` - Clean removal with confirmation
   - `icons/generate-pngs.sh` - Generates PNG icons from SVG

### Makefile Targets

```bash
make generate-icons     # Generate PNG icons from SVG (requires inkscape/imagemagick/rsvg-convert)
make install-system     # Build, generate icons, and install system-wide (requires sudo)
make uninstall-system   # Remove system-wide installation (requires sudo)
```

### Installation Locations

| Component | Path |
|-----------|------|
| Binary | `/usr/local/bin/viloxterm` |
| Desktop Entry | `/usr/local/share/applications/viloxterm.desktop` |
| SVG Icon | `/usr/local/share/icons/hicolor/scalable/apps/viloxterm.svg` |
| PNG Icons | `/usr/local/share/icons/hicolor/{size}/apps/viloxterm.png` |

### Icon Generation

The icon generation script supports three converters (auto-detected):

1. **Inkscape** (preferred)
   ```bash
   sudo apt install inkscape
   ```

2. **ImageMagick**
   ```bash
   sudo apt install imagemagick
   ```

3. **rsvg-convert**
   ```bash
   sudo apt install librsvg2-bin
   ```

At least one of these tools is required for `make generate-icons`.

### Desktop Integration Validation

After installation, verify:

```bash
# Check desktop file is valid
desktop-file-validate /usr/local/share/applications/viloxterm.desktop

# Check icon cache is updated
gtk-update-icon-cache -f -t /usr/local/share/icons/hicolor

# Verify files are installed
which viloxterm
ls /usr/local/share/applications/viloxterm.desktop
ls /usr/local/share/icons/hicolor/*/apps/viloxterm.*
```

### Usage After Installation

1. **GNOME Activities**: Press Super key, type "viloxterm"
2. **Command Line**: Run `viloxterm` from any terminal
3. **Application Menu**: Find under "System" or "Utilities"

---

## Testing the Binary

### Basic Test
```bash
./ViloXTerm  # Linux/macOS
ViloXTerm.exe  # Windows
```

### Verify Functionality
1. ✅ Window opens with dark theme
2. ✅ Terminal session starts
3. ✅ Can create new tabs (Ctrl+Shift+T)
4. ✅ Can split panes (Ctrl+Shift+H/V)
5. ✅ Keyboard shortcuts work
6. ✅ Terminal renders properly
7. ✅ Theme menu works

---

## Distribution

### Linux

**Option 1: System-Wide Installation with GNOME Integration** (recommended for personal use)

ViloxTerm includes full GNOME desktop integration with icons and app launcher support:

```bash
# 1. Build the binary
make build

# 2. Generate PNG icons from SVG (optional, auto-run by install-system)
make generate-icons

# 3. Install system-wide (requires sudo)
make install-system
```

This will:
- Install binary to `/usr/local/bin/viloxterm`
- Install desktop entry to `/usr/local/share/applications/viloxterm.desktop`
- Install icons to `/usr/local/share/icons/hicolor/{size}/apps/viloxterm.{svg,png}`
- Update GNOME icon cache and desktop database
- Make ViloxTerm available in GNOME Activities and app grid

**Uninstall**:
```bash
make uninstall-system
```

**Option 2: User-Only Installation** (no sudo required)
```bash
make local-release
# Installs to ~/bin/viloxterm
```

**Option 3: AppImage** (portable distribution)
```bash
# Use appimagetool to wrap the standalone build
appimagetool deployment/ ViloXTerm.AppImage
```

**Option 4: Direct Binary Archive**
```bash
tar -czf viloxterm-linux-x64.tar.gz ViloXTerm
```

### Windows

**Option 1: Installer** (recommended)
Use tools like:
- Inno Setup
- NSIS
- WiX Toolset

**Option 2: Portable ZIP**
```bash
zip viloxterm-windows-x64.zip ViloXTerm.exe
```

### macOS

**Option 1: DMG** (recommended)
```bash
hdiutil create -volname "ViloXTerm" -srcfolder ViloXTerm.app -ov -format UDZO ViloXTerm.dmg
```

**Option 2: Notarized App Bundle**
Requires Apple Developer account for distribution outside App Store.

---

## Troubleshooting

### Build Fails: "pyside6-deploy not found"

**Solution**: Install PySide6
```bash
pip install PySide6>=6.9.0
```

### Build Fails: "readelf/dumpbin not found"

**Solution**: Install platform-specific tools (see Prerequisites)

### Binary Crashes on Startup

**Common Causes**:
1. **Missing Qt plugins**: Check `deployment/` for missing `.so`/`.dll` files
2. **QtWebEngine process helper**: Ensure QtWebEngine resources are included
3. **SSL/TLS issues**: May need to include OpenSSL libraries manually

**Debug**:
```bash
# Linux: Check for missing libraries
ldd ViloXTerm

# macOS: Check dependencies
otool -L ViloXTerm.app/Contents/MacOS/ViloXTerm
```

### Binary Too Large

See "Size Optimization Tips" above.

### QWebEngineView Blank/White Screen

**Solution**: Ensure QtWebEngine resources are included
- Check for `qtwebengine_locales/` directory
- Check for `QtWebEngineProcess` helper binary
- Verify in `pysidedeploy.spec`: `modules` includes `WebEngineCore,WebChannel`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Binary

on: [push, pull_request]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          sudo apt install patchelf
          pip install -e apps/viloxterm

      - name: Build binary
        run: |
          cd apps/viloxterm
          ./build.sh

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: viloxterm-linux-x64
          path: apps/viloxterm/ViloXTerm
```

---

## Advanced Options

### Debugging Build Issues

Enable verbose output:
```bash
pyside6-deploy -c pysidedeploy.spec -f --verbose-build
```

### Custom Nuitka Options

Edit `pysidedeploy.spec` and add to `extra_args`:
```ini
extra_args = --enable-plugin=pyside6,--show-progress,--show-memory
```

### Standalone Mode (Directory Distribution)

Change in `pysidedeploy.spec`:
```ini
[nuitka]
mode = standalone
```

This creates a directory with the executable and all dependencies, resulting in faster startup time.

---

## References

- [pyside6-deploy Documentation](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)
- [Nuitka User Manual](https://nuitka.net/user-documentation/user-manual.html)
- [Qt for Python Deployment Guide](https://doc.qt.io/qtforpython-6/deployment/index.html)

---

## Version History

- **v1.1** (2025-10-06): Added GNOME desktop integration with icons and system installation
- **v1.0** (2025-10-04): Initial build system with pyside6-deploy
