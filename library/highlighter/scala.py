from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Scala keywords
        self.keywords = {
            # Declaration keywords
            'val', 'var', 'def', 'class', 'object', 'trait', 'type',
            'package', 'import', 'extends', 'with', 'new',
            # Control flow
            'if', 'else', 'for', 'while', 'do', 'match', 'case',
            'yield', 'return', 'throw', 'try', 'catch', 'finally',
            # Modifiers
            'private', 'protected', 'override', 'abstract', 'final',
            'sealed', 'implicit', 'lazy', 'macro', 'inline',
            # Other keywords
            'this', 'super', 'null', 'true', 'false', 'unit',
            'using', 'given', 'then', 'end', 'derives', 'transparent'
        }
        
        # Scala built-in types and functions
        self.builtins = {
            # Basic types
            'Boolean', 'Byte', 'Short', 'Int', 'Long', 'Float', 'Double',
            'Char', 'String', 'Unit', 'Nothing', 'Any', 'AnyRef',
            'Null', 'Option', 'Either', 'List', 'Set', 'Map',
            'Tuple', 'Array', 'Seq', 'Vector', 'Range',
            # Common classes
            'Future', 'Promise', 'Try', 'Success', 'Failure'
        }
        
        # Scala syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("trait", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("case_class", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("pattern_match", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("implicit", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("type_parameter", self.syntax_colors.get("type", "#4FC1FF"))
        self.syntax_colors.setdefault("for_comprehension", self.syntax_colors.get("keyword", "#569CD6"))
        
        self.setup_tags()