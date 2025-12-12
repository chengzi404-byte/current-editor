from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # JSON syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("key", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("string", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("number", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("boolean", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("null", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("punctuation", self.syntax_colors.get("operator", "#D4D4D4"))
        
        self.setup_tags() 