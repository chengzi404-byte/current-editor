from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # C keywords
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while'
        }
        
        self.syntax_colors.update({
            "preprocessor": "#C586C0",
            "macro": "#C586C0",
            "type": "#4EC9B0",
            "struct": "#4EC9B0",
            "pointer": "#D4D4D4"
        })
        
        self.setup_tags() 