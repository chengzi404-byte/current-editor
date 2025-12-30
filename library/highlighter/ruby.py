from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Ruby keywords
        self.keywords = {
            'def', 'class', 'module', 'if', 'else', 'elsif', 'unless',
            'case', 'when', 'while', 'until', 'for', 'break', 'next',
            'redo', 'retry', 'in', 'do', 'end', 'begin', 'rescue', 'ensure',
            'raise', 'yield', 'return', 'super', 'self', 'nil', 'true',
            'false', 'and', 'or', 'not', 'alias'
        }
        
        # Ruby syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("symbol", self.syntax_colors.get("constant", "#4EC9B0"))
        self.syntax_colors.setdefault("instance_var", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("class_var", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("global_var", self.syntax_colors.get("variable", "#D16969"))
        self.syntax_colors.setdefault("constant", self.syntax_colors.get("constant", "#4FC1FF"))
        self.syntax_colors.setdefault("interpolation", self.syntax_colors.get("operator", "#D7BA7D"))
        
        self.setup_tags() 