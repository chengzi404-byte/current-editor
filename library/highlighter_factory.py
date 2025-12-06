from . import api
import importlib

class HighlighterFactory:
    """Code highlighter factory class"""
    def create_highlighter(self, text_widget):
        """Create appropriate highlighter based on file extension"""
        # Get highlighter type
        highlighter_type = api.Settings.Highlighter.syntax_highlighting()["code"]
        
        # Import module
        module_name = f"library.highlighter.{highlighter_type}"
        module = importlib.import_module(module_name)
        
        # Create highlighter
        highlighter_class = getattr(module, 'CodeHighlighter')
        return highlighter_class(text_widget)
