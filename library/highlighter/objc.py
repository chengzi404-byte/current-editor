from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Objective-C specific syntax highlighting rules
        self.keywords = {
            # C keyword
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while',
            # Objective-C special keyword
            '@interface', '@implementation', '@protocol', '@end', '@private',
            '@protected', '@public', '@class', '@selector', '@encode',
            '@synchronized', '@try', '@catch', '@finally', '@throw',
            '@property', '@synthesize', '@dynamic', 'self', 'super'
        }
        
        self.syntax_colors.update({
            "message": "#DCDCAA",
            "directive": "#C586C0",
            "protocol": "#4EC9B0",
            "property": "#9CDCFE"
        })
        
        self.setup_tags() 
