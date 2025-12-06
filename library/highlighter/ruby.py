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
        
        self.syntax_colors.update({
            "symbol": "#4EC9B0",
            "instance_var": "#9CDCFE",
            "class_var": "#4EC9B0",
            "global_var": "#D16969",
            "constant": "#4FC1FF",
            "interpolation": "#D7BA7D"
        })
        
        self.setup_tags() 