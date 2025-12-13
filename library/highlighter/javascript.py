from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # JavaScript keywords
        self.keywords = {
            # Control flow
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'continue', 'return', 'try', 'catch', 'finally', 'throw',
            # Declarations
            'var', 'let', 'const', 'function', 'class', 'extends',
            'constructor', 'super', 'new', 'this',
            # Modules
            'import', 'export', 'default', 'from', 'as',
            # Others
            'typeof', 'instanceof', 'in', 'of', 'void', 'delete',
            'async', 'await', 'yield'
        }
        
        # JavaScript syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("regex", self.syntax_colors.get("string", "#D16969"))
        self.syntax_colors.setdefault("template", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("arrow", self.syntax_colors.get("function", "#569CD6"))
        self.syntax_colors.setdefault("object", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("array", self.syntax_colors.get("class", "#4EC9B0"))
        
        self.setup_tags() 
