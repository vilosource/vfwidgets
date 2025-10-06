"""Terminal configuration presets for common use cases.

This module provides pre-configured terminal settings for various scenarios,
making it easy to create terminals optimized for specific workflows.
"""

# Default configuration (matches xterm.js defaults)
DEFAULT_CONFIG = {
    "scrollback": 1000,
    "cursorBlink": True,
    "cursorStyle": "block",
    "tabStopWidth": 4,
    "bellStyle": "none",
    "scrollSensitivity": 1,
    "fastScrollSensitivity": 5,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": False,
    "convertEol": False,
}

# Developer configuration (large scrollback, visual bell)
DEVELOPER_CONFIG = {
    "scrollback": 10000,
    "cursorBlink": True,
    "cursorStyle": "bar",
    "tabStopWidth": 4,
    "bellStyle": "visual",
    "scrollSensitivity": 2,
    "fastScrollSensitivity": 10,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": True,
    "convertEol": False,
}

# Power user configuration (maximum scrollback, fast scrolling)
POWER_USER_CONFIG = {
    "scrollback": 50000,
    "cursorBlink": False,
    "cursorStyle": "block",
    "tabStopWidth": 8,
    "bellStyle": "none",
    "scrollSensitivity": 3,
    "fastScrollSensitivity": 20,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": True,
    "convertEol": False,
}

# Minimal configuration (low memory, basic features)
MINIMAL_CONFIG = {
    "scrollback": 500,
    "cursorBlink": False,
    "cursorStyle": "block",
    "tabStopWidth": 4,
    "bellStyle": "none",
    "scrollSensitivity": 1,
    "fastScrollSensitivity": 5,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": False,
    "convertEol": False,
}

# Accessibility configuration (high visibility, visual bell)
ACCESSIBLE_CONFIG = {
    "scrollback": 2000,
    "cursorBlink": True,
    "cursorStyle": "block",
    "tabStopWidth": 4,
    "bellStyle": "visual",
    "scrollSensitivity": 1,
    "fastScrollSensitivity": 3,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": True,
    "convertEol": False,
}

# Log viewer configuration (maximum scrollback, no cursor blink)
LOG_VIEWER_CONFIG = {
    "scrollback": 100000,
    "cursorBlink": False,
    "cursorStyle": "underline",
    "tabStopWidth": 4,
    "bellStyle": "none",
    "scrollSensitivity": 5,
    "fastScrollSensitivity": 25,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": True,
    "convertEol": False,
}

# SSH/Remote configuration (balanced settings for remote connections)
REMOTE_CONFIG = {
    "scrollback": 5000,
    "cursorBlink": True,
    "cursorStyle": "block",
    "tabStopWidth": 4,
    "bellStyle": "visual",
    "scrollSensitivity": 1,
    "fastScrollSensitivity": 5,
    "fastScrollModifier": "shift",
    "rightClickSelectsWord": False,
    "convertEol": False,
}

# Dictionary of all presets for easy access
TERMINAL_CONFIGS = {
    "default": DEFAULT_CONFIG,
    "developer": DEVELOPER_CONFIG,
    "power_user": POWER_USER_CONFIG,
    "minimal": MINIMAL_CONFIG,
    "accessible": ACCESSIBLE_CONFIG,
    "log_viewer": LOG_VIEWER_CONFIG,
    "remote": REMOTE_CONFIG,
}


def get_config(preset_name: str) -> dict:
    """Get a terminal configuration by preset name.

    Args:
        preset_name: Name of the preset (e.g., 'developer', 'minimal')

    Returns:
        Dictionary with terminal configuration

    Raises:
        KeyError: If preset_name is not found

    Example:
        >>> config = get_config('developer')
        >>> terminal = TerminalWidget(terminal_config=config)
    """
    if preset_name not in TERMINAL_CONFIGS:
        available = ", ".join(TERMINAL_CONFIGS.keys())
        raise KeyError(f"Unknown preset '{preset_name}'. Available presets: {available}")
    return TERMINAL_CONFIGS[preset_name].copy()


def list_presets() -> list[str]:
    """List all available configuration presets.

    Returns:
        List of preset names

    Example:
        >>> presets = list_presets()
        >>> print(presets)
        ['default', 'developer', 'power_user', ...]
    """
    return list(TERMINAL_CONFIGS.keys())
