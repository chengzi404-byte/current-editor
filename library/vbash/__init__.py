"""
library.vbash - Cross-platform shell wrapper

Provides VBash class for executing shell commands across different operating systems.
"""

from .vbash import VBash, create_vbash

__all__ = ["VBash", "create_vbash"]
__version__ = "1.1.0"
__author__ = "Phoenix Editor"