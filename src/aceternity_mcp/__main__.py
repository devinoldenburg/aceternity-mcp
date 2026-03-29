#!/usr/bin/env python3
"""Allow running the installer as: python -m aceternity_mcp.install"""

import sys

from .install import main

if __name__ == "__main__":
    sys.exit(main())
