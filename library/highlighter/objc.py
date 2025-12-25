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
        
        # Objective-C syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("message", self.syntax_colors.get("function", "#DCDCAA"))
        self.syntax_colors.setdefault("directive", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("protocol", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("property", self.syntax_colors.get("variable", "#9CDCFE"))
        
        self.setup_tags() 
