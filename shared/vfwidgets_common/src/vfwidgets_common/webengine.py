"""Qt WebEngine configuration utilities for VFWidgets.

Provides automatic configuration for Qt WebEngine in special environments
like WSL where hardware acceleration is not available.
"""

import logging
import os
from typing import Optional

from .platform import is_wsl, is_remote_desktop

logger = logging.getLogger(__name__)


def get_chromium_flags_for_environment() -> list[str]:
    """Get appropriate Chromium flags for the current environment.

    Returns:
        List of Chromium command-line flags
    """
    flags = []

    if is_wsl():
        # WSL requires software rendering and GPU disable
        flags.extend([
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",  # Avoid /dev/shm issues in containers
            "--no-sandbox",  # Required for some WSL configurations
        ])
        logger.info("WSL detected: Using software rendering for Qt WebEngine")

    elif is_remote_desktop():
        # Remote desktop benefits from reduced GPU usage
        flags.extend([
            "--disable-gpu",
            "--disable-software-rasterizer",
        ])
        logger.info("Remote desktop detected: Disabling GPU acceleration")

    return flags


def configure_webengine_environment() -> dict[str, str]:
    """Configure Qt WebEngine environment variables.

    This should be called BEFORE importing any Qt WebEngine modules
    to ensure proper Chromium initialization.

    Returns:
        Dictionary of environment variables that were set
    """
    changes = {}

    # Get flags for current environment
    flags = get_chromium_flags_for_environment()

    if flags:
        # Check if user has already set flags
        existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")

        if existing_flags:
            # User has custom flags, append ours if not already present
            new_flags = []
            for flag in flags:
                if flag not in existing_flags:
                    new_flags.append(flag)

            if new_flags:
                combined_flags = f"{existing_flags} {' '.join(new_flags)}"
                os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = combined_flags
                changes["QTWEBENGINE_CHROMIUM_FLAGS"] = combined_flags
                logger.debug(f"Appended WebEngine flags: {' '.join(new_flags)}")
        else:
            # No existing flags, set ours
            flags_str = " ".join(flags)
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = flags_str
            changes["QTWEBENGINE_CHROMIUM_FLAGS"] = flags_str
            logger.debug(f"Set WebEngine flags: {flags_str}")

    return changes


def configure_all_for_webengine() -> dict[str, str]:
    """Configure both Qt and WebEngine environment variables.

    This is a convenience function that calls both platform.configure_qt_environment()
    and configure_webengine_environment().

    Returns:
        Dictionary of all environment variables that were set
    """
    from .platform import configure_qt_environment

    changes = {}

    # First configure Qt general environment
    qt_changes = configure_qt_environment()
    changes.update(qt_changes)

    # Then configure WebEngine-specific settings
    webengine_changes = configure_webengine_environment()
    changes.update(webengine_changes)

    if changes:
        logger.info(f"Configured environment for WebEngine: {list(changes.keys())}")

    return changes


def get_webengine_info() -> dict[str, any]:
    """Get information about WebEngine configuration.

    Returns:
        Dictionary containing WebEngine configuration details
    """
    return {
        "chromium_flags": os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", ""),
        "recommended_flags": get_chromium_flags_for_environment(),
        "is_wsl": is_wsl(),
        "is_remote_desktop": is_remote_desktop(),
        "libgl_software": os.environ.get("LIBGL_ALWAYS_SOFTWARE", ""),
        "qt_quick_backend": os.environ.get("QT_QUICK_BACKEND", ""),
    }


def log_webengine_configuration() -> None:
    """Log the current WebEngine configuration for debugging."""
    info = get_webengine_info()

    logger.info("Qt WebEngine Configuration:")
    logger.info(f"  WSL Environment: {info['is_wsl']}")
    logger.info(f"  Remote Desktop: {info['is_remote_desktop']}")
    logger.info(f"  Chromium Flags: {info['chromium_flags'] or '(none)'}")
    logger.info(f"  LIBGL Software: {info['libgl_software'] or '(none)'}")
    logger.info(f"  Qt Quick Backend: {info['qt_quick_backend'] or '(default)'}")

    if info['recommended_flags']:
        logger.info(f"  Recommended Flags: {' '.join(info['recommended_flags'])}")
