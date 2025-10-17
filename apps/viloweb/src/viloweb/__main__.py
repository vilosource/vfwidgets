"""Entry point for running ViloWeb as a module.

This allows running ViloWeb with:
    python -m viloweb

or via the installed script:
    viloweb
"""

import sys

from .application import main

if __name__ == "__main__":
    sys.exit(main())
