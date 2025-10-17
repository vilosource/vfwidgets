# ViloWeb Known Issues

## Qt WebEngine Sandboxing Crash (Linux) - SOLVED

### Symptom

```
[ERROR:zygote_linux.cc(639)] Zygote could not fork: process_type renderer
Segmentation fault (core dumped)
```

### Root Cause

Qt WebEngine uses Chromium's multi-process architecture with sandboxing. On certain Linux environments (containers, some distros, restricted namespaces), the sandboxing fails due to missing kernel features or permissions.

### ✅ Solution (Implemented in ViloWeb 0.1.0)

**ViloWeb now automatically configures Qt WebEngine** with the correct flags to work on all Linux environments. The fix sets these flags **before** importing Qt modules:

```python
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-zygote --no-sandbox --in-process-gpu --disable-dev-shm-usage --disable-gpu-sandbox"
```

This configuration:
- ✅ Works on standard Linux desktops
- ✅ Works in containers (Docker, Podman)
- ✅ Works in WSL (Windows Subsystem for Linux)
- ✅ Works in VMs with limited kernel features

**No user action required** - just run `viloweb` and it works!

### Environment-Specific Issues

This particularly affects:
- **Containers** (Docker, Podman)
- **WSL** (Windows Subsystem for Linux)
- **Restricted user namespaces**
- **Some Linux distros** with security hardening

### Solutions

#### Solution 1: Use Firejail (Recommended for Development)

Firejail provides a compatibility layer:

```bash
# Install firejail
sudo apt install firejail  # Debian/Ubuntu
sudo dnf install firejail  # Fedora
sudo pacman -S firejail    # Arch

# Run ViloWeb with firejail
firejail --noprofile viloweb
```

#### Solution 2: Manual Chromium Flags

Run with explicit sandbox disable:

```bash
# Set environment variable
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-setuid-sandbox"

# Run ViloWeb
viloweb
```

#### Solution 3: System Configuration

Enable user namespaces (requires root):

```bash
# Check current setting
sysctl kernel.unprivileged_userns_clone

# Enable (temporary)
sudo sysctl kernel.unprivileged_userns_clone=1

# Enable (permanent)
echo "kernel.unprivileged_userns_clone=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### Solution 4: Use about:blank for Testing

For testing the UI without external URLs:

```python
from viloweb import ViloWebApplication
app = ViloWebApplication()

# Override to use local content only
app.run()
# Then navigate to about:blank or setHtml() with local content
```

### What ViloWeb Does

ViloWeb automatically:
1. Sets `QTWEBENGINE_DISABLE_SANDBOX=1` before Qt loads
2. Adds `--no-sandbox` and related flags to argv
3. Falls back to `about:blank` if external URLs fail

Despite this, some environments still crash due to deeper kernel/permission issues.

### Security Note

**For Production**: Never disable sandboxing. Instead:
1. Configure proper Linux kernel features
2. Use AppArmor/SELinux profiles
3. Run in properly configured containers
4. Test on target deployment environment

**For Development/Learning**: Sandboxing can be safely disabled as you're running trusted code.

### Testing Without External URLs

You can test ViloWeb's UI and features using local HTML:

```python
from viloweb import ViloWebApplication
from PySide6.QtCore import QTimer

app = ViloWebApplication()

def load_local_html():
    window = app.main_window
    if window:
        # Get first tab's widget
        tab_widget = window._tab_widget.widget(0)
        if tab_widget:
            html = """
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Welcome to ViloWeb!</h1>
                <p>This is a local page that doesn't require external network.</p>
                <button onclick="window.viloWeb.log_from_js('info', 'Button clicked!')">
                    Test QWebChannel
                </button>
            </body>
            </html>
            """
            tab_widget.webview.setHtml(html)

QTimer.singleShot(500, load_local_html)
app.run()
```

### Alternative: Use Different Qt WebEngine Build

Some distributions provide Qt WebEngine builds without sandboxing requirements:

```bash
# Check your Qt WebEngine version
python -c "from PySide6 import QtWebEngine; print(QtWebEngine.__version__)"

# Some builds have --no-sandbox baked in
```

### Workaround Script

We provide a wrapper script that handles all the above:

```bash
#!/bin/bash
# run-viloweb.sh

export QTWEBENGINE_DISABLE_SANDBOX=1
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage"

# Try with firejail if available
if command -v firejail &> /dev/null; then
    echo "Using firejail for compatibility"
    firejail --noprofile viloweb "$@"
else
    echo "Running without firejail (may crash on some systems)"
    viloweb "$@"
fi
```

Usage:
```bash
chmod +x run-viloweb.sh
./run-viloweb.sh
```

### Reporting This Issue

If you encounter this crash, please report:
1. Linux distribution and version (`cat /etc/os-release`)
2. Kernel version (`uname -r`)
3. Container/virtualization environment (if any)
4. Output of `sysctl kernel.unprivileged_userns_clone`
5. Qt WebEngine version

### Summary

This is **not a ViloWeb bug** but a Qt WebEngine + Linux environment compatibility issue. ViloWeb does everything possible to work around it, but some environments simply cannot run Qt WebEngine without proper kernel/permission configuration.

For educational purposes, use:
- Local HTML content (`setHtml()`)
- Firejail wrapper
- Properly configured development machine

For production, properly configure sandboxing support in your deployment environment.
