from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # XML keywords and constructs
        self.keywords = {
            'xml', 'version', 'encoding', 'standalone',
            'DOCTYPE', 'ELEMENT', 'ATTLIST', 'ENTITY',
            'NOTATION', 'CDATA', 'PCDATA', 'ANY', 'EMPTY'
        }
        
        # XML syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("tag", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("attribute", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("attribute_value", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("comment", self.syntax_colors.get("comment", "#6A9955"))
        self.syntax_colors.setdefault("cdata", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("doctype", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("entity", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("processing_instruction", self.syntax_colors.get("function", "#4FC1FF"))
        
        self.setup_tags()