"""Constants and default configurations for the terminal widget."""

# Terminal dimensions
DEFAULT_ROWS = 24
DEFAULT_COLS = 80
DEFAULT_SCROLLBACK = 1000

# Server configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 0  # Random port

# Terminal themes
THEMES = {
    "dark": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "cursor": "#ffcc00",
        "selection": "#264f78",
        "black": "#000000",
        "red": "#cd3131",
        "green": "#0dbc79",
        "yellow": "#e5e510",
        "blue": "#2472c8",
        "magenta": "#bc3fbc",
        "cyan": "#11a8cd",
        "white": "#e5e5e5",
        "brightBlack": "#555753",
        "brightRed": "#f14c4c",
        "brightGreen": "#23d18b",
        "brightYellow": "#f5f543",
        "brightBlue": "#3b8eea",
        "brightMagenta": "#d670d6",
        "brightCyan": "#29b8db",
        "brightWhite": "#f5f5f5",
    },
    "light": {
        "background": "#ffffff",
        "foreground": "#000000",
        "cursor": "#000000",
        "selection": "#b5d5ff",
        "black": "#000000",
        "red": "#c82829",
        "green": "#718c00",
        "yellow": "#eab700",
        "blue": "#4271ae",
        "magenta": "#8959a8",
        "cyan": "#3e999f",
        "white": "#ffffff",
        "brightBlack": "#8e908c",
        "brightRed": "#f5871f",
        "brightGreen": "#90a959",
        "brightYellow": "#f4bf75",
        "brightBlue": "#5e8d87",
        "brightMagenta": "#a3685a",
        "brightCyan": "#ac4142",
        "brightWhite": "#ffffff",
    },
}

# WebSocket settings
WEBSOCKET_NAMESPACE = "/pty"
MAX_READ_BYTES = 1024 * 20  # 20KB

# Environment variables
ENV_NO_AUTO_SETUP = "VFWIDGETS_NO_AUTO_SETUP"
ENV_DEBUG = "VFWIDGETS_DEBUG"
