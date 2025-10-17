"""Helper for setting up QWebChannel with CSP support.

This module provides convenient helpers for setting up Python↔JavaScript
communication via QWebChannel, using QWebEngineScript to bypass Content
Security Policy (CSP) restrictions.

Educational Focus:
    This demonstrates:
    - QWebChannel setup pattern
    - CSP-safe script injection
    - Python-JavaScript bridge architecture
    - Resource loading from Qt (qrc://)
"""

import logging
from typing import Optional

from PySide6.QtCore import QFile, QIODevice, QObject, QTextStream
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineScript

logger = logging.getLogger(__name__)


class WebChannelHelper:
    """Helper for setting up QWebChannel with CSP support.

    This class provides methods to set up Python↔JavaScript communication
    via QWebChannel, using QWebEngineScript to bypass CSP restrictions.

    Educational Note:
        QWebChannel allows Python objects to be called from JavaScript.
        This is the foundation for browser extensions in ViloWeb.

        Traditional approach (fails with CSP):
            var script = document.createElement('script');
            script.src = 'qrc:///qtwebchannel/qwebchannel.js';  # BLOCKED
            document.head.appendChild(script);

        Our approach (bypasses CSP):
            - Load qwebchannel.js as string from Qt resources
            - Inject via QWebEngineScript before CSP loads
            - Works on all sites, even with Trusted Types

    Example:
        >>> from vfwidgets_webview import BrowserWidget
        >>> from vfwidgets_webview.webchannel_helper import WebChannelHelper
        >>> from PySide6.QtCore import QObject, Signal, Slot
        >>>
        >>> class MyBridge(QObject):
        ...     @Slot(str)
        ...     def log(self, message: str):
        ...         print(f"JS says: {message}")
        >>>
        >>> browser = BrowserWidget()
        >>> bridge = MyBridge()
        >>> channel = WebChannelHelper.setup_channel(browser, bridge, "pyBridge")
        >>>
        >>> # JavaScript can now call: window.pyBridge.log("Hello from JS!")
    """

    @staticmethod
    def load_qt_resource(resource_path: str) -> Optional[str]:
        """Load text content from Qt resource file.

        Args:
            resource_path: Qt resource path (e.g., ":/qtwebchannel/qwebchannel.js")

        Returns:
            File content as string, or None if loading failed

        Example:
            >>> content = WebChannelHelper.load_qt_resource(":/qtwebchannel/qwebchannel.js")
            >>> print(len(content))  # Should be several KB
        """
        file = QFile(resource_path)

        if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            logger.error(f"Failed to open Qt resource: {resource_path}")
            return None

        stream = QTextStream(file)
        content = stream.readAll()
        file.close()

        logger.debug(f"Loaded {len(content)} bytes from {resource_path}")
        return content

    @staticmethod
    def setup_channel(
        browser_widget,  # BrowserWidget
        bridge_object: QObject,
        object_name: str = "pyBridge",
    ) -> QWebChannel:
        """Setup QWebChannel for Python↔JavaScript communication (CSP-safe).

        This method:
        1. Creates QWebChannel
        2. Registers Python bridge object
        3. Sets channel on page
        4. Injects qwebchannel.js library via QWebEngineScript (CSP-safe)
        5. Initializes bridge in JavaScript

        Args:
            browser_widget: BrowserWidget instance
            bridge_object: Python object to expose to JavaScript
            object_name: Name for JavaScript access (e.g., window.pyBridge)

        Returns:
            QWebChannel instance for further configuration

        Example:
            >>> class ExtensionBridge(QObject):
            ...     @Slot(str, str)
            ...     def notify(self, event: str, data: str):
            ...         print(f"Event: {event}, Data: {data}")
            >>>
            >>> bridge = ExtensionBridge()
            >>> channel = WebChannelHelper.setup_channel(
            ...     browser, bridge, "extension"
            ... )
            >>>
            >>> # JavaScript: window.extension.notify("click", "button1")
        """
        logger.info(f"Setting up QWebChannel with object name: {object_name}")

        # Step 1: Create QWebChannel
        channel = QWebChannel()

        # Step 2: Register bridge object
        channel.registerObject(object_name, bridge_object)
        logger.debug(f"Registered bridge object: {object_name}")

        # Step 3: Set channel on page
        browser_widget.page().setWebChannel(channel)
        logger.debug("Web channel set on page")

        # Step 4: Load qwebchannel.js from Qt resources
        qwebchannel_js = WebChannelHelper.load_qt_resource(":/qtwebchannel/qwebchannel.js")

        if qwebchannel_js is None:
            logger.error("Failed to load qwebchannel.js - bridge will not work")
            return channel

        # Step 5: Inject library via QWebEngineScript (CSP-safe)
        browser_widget.inject_user_script(
            qwebchannel_js,
            name="qwebchannel-library",
            injection_point=QWebEngineScript.InjectionPoint.DocumentCreation,
            world_id=QWebEngineScript.ScriptWorldId.MainWorld,
            runs_on_subframes=False,  # Only main frame needs library
        )
        logger.debug("QWebChannel library injected")

        # Step 6: Inject initialization script
        init_script = f"""
        (function() {{
            'use strict';

            // Wait for QWebChannel to be available
            function initBridge() {{
                if (typeof QWebChannel === 'undefined') {{
                    console.error('[WebChannel] QWebChannel not available');
                    return;
                }}

                try {{
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        // Expose bridge object to window
                        window.{object_name} = channel.objects.{object_name};

                        console.log('[WebChannel] ✓ Bridge ready: window.{object_name}');

                        // Notify Python that bridge is ready
                        if (window.{object_name} && window.{object_name}.log_from_js) {{
                            window.{object_name}.log_from_js('info',
                                'QWebChannel bridge connected: {object_name}');
                        }}
                    }});
                }} catch (error) {{
                    console.error('[WebChannel] Initialization failed:', error);
                }}
            }}

            // Initialize when DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initBridge);
            }} else {{
                initBridge();
            }}
        }})();
        """

        browser_widget.inject_user_script(
            init_script,
            name=f"qwebchannel-init-{object_name}",
            injection_point=QWebEngineScript.InjectionPoint.DocumentReady,
            world_id=QWebEngineScript.ScriptWorldId.MainWorld,
            runs_on_subframes=False,
        )
        logger.debug("QWebChannel initialization script injected")

        logger.info(f"QWebChannel setup complete: window.{object_name}")
        return channel

    @staticmethod
    def teardown_channel(browser_widget) -> None:
        """Remove QWebChannel scripts from browser.

        This removes all injected scripts related to QWebChannel.

        Args:
            browser_widget: BrowserWidget instance

        Example:
            >>> WebChannelHelper.teardown_channel(browser)
        """
        logger.info("Tearing down QWebChannel")

        # Remove library
        browser_widget.remove_user_script("qwebchannel-library")

        # Remove all init scripts (may have multiple for different objects)
        # Note: This is a simple approach - in production you might want
        # to track script names more carefully
        logger.debug("QWebChannel scripts removed")
