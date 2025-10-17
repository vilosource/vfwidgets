"""Custom QWebEnginePage with educational features.

This module demonstrates how to customize QWebEnginePage to add features
like console message handling, certificate error handling, and more.

Educational Focus:
    This code teaches QtWebEngine patterns by showing:
    - How to extend QWebEnginePage
    - How to capture JavaScript console messages
    - How to handle certificate errors
    - How to customize user agent
    - Best practices for web page management
"""

import logging
from typing import Optional

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineCore import (
    QWebEngineCertificateError,
    QWebEnginePage,
    QWebEngineSettings,
)
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class WebPage(QWebEnginePage):
    """Custom web page with enhanced features.

    This class extends QWebEnginePage to provide:
    - JavaScript console message logging
    - Certificate error handling with user prompts
    - Customizable user agent
    - Educational comments explaining QtWebEngine concepts

    Example:
        >>> page = WebPage()
        >>> page.setUrl(QUrl("https://example.com"))

    Signals:
        console_message: Emitted when JavaScript console message occurs
            Args: level (int), message (str), line_number (int), source_id (str)

    Educational Notes:
        QWebEnginePage is the core of web rendering in Qt. It:
        - Represents the actual web page (DOM, JavaScript, etc.)
        - Handles navigation and network requests
        - Executes JavaScript in the page context
        - Can be customized by overriding virtual methods

        Think of it as the "brain" of the web view, while QWebEngineView
        is just the "display" (the visual widget).
    """

    # Signal emitted when JavaScript console message occurs
    # This allows parent widgets to capture and display console output
    console_message = Signal(int, str, int, str)  # level, message, line, source

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize web page.

        Args:
            parent: Parent widget (usually a QWebEngineView)

        Educational Note:
            When creating a custom page, you typically:
            1. Call super().__init__()
            2. Configure settings
            3. Set up custom features
        """
        super().__init__(parent)

        # Configure page settings for better web compatibility
        self._configure_settings()

        # Set custom user agent (identifies our browser to websites)
        self._setup_user_agent()

        logger.debug("WebPage initialized")

    def _configure_settings(self) -> None:
        """Configure page settings.

        Educational Note:
            QWebEngineSettings controls how the browser engine behaves.
            These settings affect JavaScript, plugins, local storage, etc.

            Common settings:
            - JavascriptEnabled: Allow JavaScript execution
            - LocalStorageEnabled: Allow localStorage API
            - AllowRunningInsecureContent: Mixed HTTP/HTTPS content
            - AutoLoadImages: Load images automatically

            Think of this as the browser's "preferences" or "config".
        """
        settings = self.settings()

        # Enable JavaScript (required for most modern websites)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Enable local storage (used by many web apps)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Allow geolocation with user permission
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, False
        )

        # Enable WebGL (for 3D graphics in browser)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        # Enable automatic image loading
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        logger.debug("Page settings configured")

    def _setup_user_agent(self) -> None:
        """Set custom user agent.

        Educational Note:
            The User-Agent string identifies your browser to websites.
            It tells the server what browser/version you're using.

            Format typically: Browser/Version (Platform; Details)

            Example standard user agent:
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
             (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

            We create a custom one to identify our widget.
        """
        # Create a custom user agent identifying this as vfwidgets-webview
        # But maintain compatibility by mimicking Chrome
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
            "VFWidgets-WebView/0.1.0"
        )

        # Note: In Qt6, user agent is set via profile, not page
        # We'll handle this in the WebView where we control the profile
        logger.debug(f"User agent prepared: {user_agent}")

    def javaScriptConsoleMessage(  # noqa: N802
        self,
        level: QWebEnginePage.JavaScriptConsoleMessageLevel,
        message: str,
        lineNumber: int,  # noqa: N803
        sourceID: str,  # noqa: N803
    ) -> None:
        """Handle JavaScript console messages.

        This method is called whenever JavaScript code in the page calls:
        - console.log()
        - console.warn()
        - console.error()
        - console.info()

        Educational Note:
            This is a VIRTUAL METHOD that Qt calls automatically.
            By overriding it, we can:
            1. Log console messages to our application's log
            2. Display them in a developer console UI
            3. Debug web pages
            4. Teach users about JavaScript debugging

            This is incredibly useful for development and debugging!

        Args:
            level: Message level (Info, Warning, Error)
            message: The console message text
            lineNumber: Line number in source file
            sourceID: Source file URL/path

        Example JavaScript that would trigger this:
            console.log("Hello from JavaScript!");
            console.error("Something went wrong!");
        """
        # Map Qt's enum to readable string
        level_names = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR",
        }
        level_name = level_names.get(level, "UNKNOWN")

        # Log to Python's logging system
        log_message = f"JS Console [{level_name}] {sourceID}:{lineNumber} - {message}"

        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            logger.error(log_message)
        elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Emit signal so UI can display it (useful for dev tools panel)
        self.console_message.emit(level, message, lineNumber, sourceID)

    def certificateError(self, error: QWebEngineCertificateError) -> bool:  # noqa: N802
        """Handle SSL/TLS certificate errors.

        This method is called when a website's certificate is invalid.
        Common causes:
        - Expired certificate
        - Self-signed certificate
        - Certificate for wrong domain
        - Untrusted certificate authority

        Educational Note:
            HTTPS security is based on certificates. When you visit
            https://example.com, the server sends a certificate proving
            its identity. This method lets us decide whether to:
            1. Block the connection (secure, default)
            2. Allow it anyway (insecure, user's choice)

            This is a SECURITY-CRITICAL method!

            For educational browsers, we log the error and REJECT it.
            For production browsers, you might show a warning dialog.

        Args:
            error: Certificate error details

        Returns:
            True to accept the certificate (DANGEROUS!)
            False to reject the certificate (SAFE)

        Example Error Types:
            - CertificateExpired: Certificate is out of date
            - CertificateInvalid: Certificate is malformed
            - CertificateAuthorityInvalid: Unknown issuer
        """
        # Log the certificate error
        logger.warning(f"Certificate error for {error.url().toString()}: " f"{error.description()}")

        # Educational: Explain what happened
        logger.info(
            "Certificate rejected for security. In a production browser, "
            "you might show a warning dialog allowing the user to proceed."
        )

        # SECURITY: Always return False (reject) for untrusted certificates
        # Only return True if you want to allow insecure connections
        # (useful for testing with self-signed certificates in dev)
        return False

    def acceptNavigationRequest(  # noqa: N802
        self,
        url: QUrl,
        nav_type: QWebEnginePage.NavigationType,
        isMainFrame: bool,  # noqa: N803
    ) -> bool:
        """Decide whether to allow navigation to a URL.

        This method is called BEFORE navigating to a new page.
        It allows you to:
        - Block certain URLs (parental controls, ad blocking)
        - Handle custom URL schemes (like "app://settings")
        - Log navigation for analytics
        - Implement security policies

        Educational Note:
            This is called for EVERY navigation:
            - User clicks a link
            - JavaScript redirects
            - Form submissions
            - iframe loads

            Return True to allow, False to block.

        Args:
            url: The URL to navigate to
            nav_type: Type of navigation (LinkClicked, Typed, FormSubmitted, etc.)
            isMainFrame: True if main page, False if iframe

        Returns:
            True to allow navigation, False to block

        Example Use Cases:
            - Block ads: if "doubleclick.net" in url.host(): return False
            - Custom schemes: if url.scheme() == "app": handle_app_url(url)
            - Logging: log.info(f"Navigating to {url}")
        """
        # Log navigation (useful for debugging)
        nav_type_names = {
            QWebEnginePage.NavigationType.NavigationTypeLinkClicked: "LinkClicked",
            QWebEnginePage.NavigationType.NavigationTypeTyped: "Typed",
            QWebEnginePage.NavigationType.NavigationTypeFormSubmitted: "FormSubmitted",
            QWebEnginePage.NavigationType.NavigationTypeBackForward: "BackForward",
            QWebEnginePage.NavigationType.NavigationTypeReload: "Reload",
            QWebEnginePage.NavigationType.NavigationTypeRedirect: "Redirect",
            QWebEnginePage.NavigationType.NavigationTypeOther: "Other",
        }
        nav_type_name = nav_type_names.get(nav_type, "Unknown")

        logger.debug(
            f"Navigation request: {url.toString()} "
            f"(type={nav_type_name}, mainFrame={isMainFrame})"
        )

        # Allow all navigation by default
        # Applications built on this widget (like ViloWeb) can subclass
        # and add custom filtering logic here
        return True

    def get_url_string(self) -> str:
        """Get current URL as string.

        Educational Note:
            This is a convenience method. Qt's page.url() returns a QUrl,
            but most Python code wants a string. This helper makes the API
            more pythonic.

        Returns:
            Current URL as string
        """
        current_url = super().url()
        return current_url.toString() if current_url.isValid() else ""

    def get_title_string(self) -> str:
        """Get current page title.

        Educational Note:
            The title is what appears in browser tabs and window titles.
            It comes from the <title> tag in the HTML:
            <title>Example Domain</title>

        Returns:
            Current page title
        """
        current_title = super().title()
        return current_title if current_title else "Untitled"
