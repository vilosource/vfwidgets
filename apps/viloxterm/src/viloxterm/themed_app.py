"""ViloxTerm themed application with overlay system support.

This module provides ViloxTermThemedApp which extends VFThemedApplication
to provide automatic theme persistence and potential future color customization.
"""

import logging
import os
from typing import List, Optional

from PySide6.QtCore import QSettings
from vfwidgets_theme.widgets import VFThemedApplication

logger = logging.getLogger(__name__)


class ViloxTermThemedApp(VFThemedApplication):
    """ViloxTerm application with theme overlay support.

    Features:
    - Automatic theme persistence (migrated from old "theme/current" key)
    - Future: Terminal color customization
    - Future: User color preferences

    The app automatically migrates from the old QSettings key on first run.
    """

    theme_config = {
        # Base theme
        "base_theme": "dark",
        # Future: App-level terminal branding
        "app_overrides": {
            # Could override terminal colors here for branding
            # Example: "terminal.background": "#1e1e2e",
        },
        # Allow users to customize UI colors
        "allow_user_customization": True,  # Enabled for UI customization
        "customizable_tokens": [
            # UI customization tokens
            "editorGroupHeader.tabsBackground",  # Top bar background (draggable area)
            # Future: Add more UI tokens as needed
        ],
        # Persistence settings
        "persist_base_theme": True,
        "persist_user_overrides": True,  # Save user color customizations
        "settings_key_prefix": "theme/",  # Uses "theme/base_theme"
    }

    def __init__(self, argv: Optional[List[str]] = None):
        """Initialize ViloxTerm themed application.

        Args:
            argv: Command line arguments (optional)
        """
        # Reduce theme system logging overhead in production
        # DEBUG logging adds ~30ms during startup due to ~100+ log statements
        # IMPORTANT: Must be set BEFORE super().__init__() which initializes theme system
        if os.environ.get("VILOXTERM_DEBUG") != "1":
            logging.getLogger("vftheme").setLevel(logging.WARNING)

        # Migrate old theme settings before initialization
        self._migrate_old_theme_settings()

        # Initialize parent with ViloxTerm app ID
        super().__init__(argv, app_id="ViloxTerm")

        logger.info("ViloxTermThemedApp initialized with overlay system support")

    def _migrate_old_theme_settings(self) -> None:
        """Migrate from old QSettings key to new key.

        Old key: "theme/current"
        New key: "theme/base_theme"

        This ensures existing users don't lose their theme preference.
        """
        try:
            settings = QSettings("ViloxTerm", "ViloxTerm")

            old_key = "theme/current"
            new_key = "theme/base_theme"

            # Check if we need to migrate
            old_theme = settings.value(old_key)
            new_theme = settings.value(new_key)

            if old_theme and not new_theme:
                # Migration needed: copy old to new
                settings.setValue(new_key, old_theme)
                settings.sync()
                logger.info(
                    f"Migrated theme preference from '{old_key}' to '{new_key}': {old_theme}"
                )

                # Optionally remove old key (commented out to preserve backward compat)
                # settings.remove(old_key)

        except Exception as e:
            logger.warning(f"Failed to migrate theme settings: {e}")
            # Non-fatal - will just use default theme
