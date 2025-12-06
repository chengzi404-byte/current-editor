from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # JSON syntax colors
        self.syntax_colors.update({
            "key": "#9CDCFE",
            "string": "#CE9178",
            "number": "#B5CEA8",
            "boolean": "#569CD6",
            "null": "#569CD6",
            "punctuation": "#D4D4D4"
        })
        
        self.setup_tags() 