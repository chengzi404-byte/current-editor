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
        
        self.syntax_colors.update({
            "regex": "#D16969",
            "template": "#CE9178",
            "arrow": "#569CD6",
            "object": "#4EC9B0",
            "array": "#4EC9B0"
        })
        
        self.setup_tags() 
