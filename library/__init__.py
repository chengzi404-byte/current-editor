"""
Library package
"""

from .logger import get_logger, shutdown_logger
from .highlighter_factory import HighlighterFactory
from .api import Settings
from .multi_file_editor import MultiFileEditor
from .editor_operations import EditorOperations
from .ui_styles import apply_modern_style, get_style
from . import directory
from . import validator
