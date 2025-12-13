from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # YAML keywords and special constructs
        self.keywords = {
            # YAML directives
            '%YAML', '%TAG',
            # Document markers
            '---', '...',
            # Special values
            'true', 'false', 'null', 'True', 'False', 'Null',
            'YES', 'NO', 'ON', 'OFF',
            # Anchors and aliases
            '&', '*', '<<'
        }
        
        # YAML syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("key", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("anchor", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("alias", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("directive", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("document_marker", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("boolean", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("null", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("number", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("string", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("comment", self.syntax_colors.get("comment", "#6A9955"))
        
        self.setup_tags()