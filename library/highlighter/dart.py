from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Dart keywords
        self.keywords = {
            # Declaration keywords
            'var', 'final', 'const', 'void', 'dynamic', 'late',
            'class', 'interface', 'mixin', 'extension', 'typedef',
            'enum', 'part', 'part of', 'library', 'import', 'export',
            'show', 'hide', 'as',
            # Control flow
            'if', 'else', 'for', 'while', 'do', 'switch', 'case',
            'default', 'break', 'continue', 'return', 'throw',
            'try', 'catch', 'on', 'finally', 'rethrow',
            # Modifiers
            'abstract', 'static', 'covariant', 'extends', 'implements',
            'with', 'get', 'set', 'operator', 'async', 'await',
            'sync', 'yield', 'yield*', 'external', 'factory',
            'assert', 'required', 'super', 'this', 'null',
            'true', 'false'
        }
        
        # Dart built-in types and functions
        self.builtins = {
            # Basic types
            'bool', 'int', 'double', 'num', 'String', 'List',
            'Set', 'Map', 'Iterable', 'Future', 'Stream',
            'Function', 'Object', 'Null', 'Never',
            # Common classes
            'DateTime', 'Duration', 'RegExp', 'Uri', 'BigInt',
            'Symbol', 'Type', 'StackTrace'
        }
        
        # Dart syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("mixin", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("extension", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("future", self.syntax_colors.get("type", "#569CD6"))
        self.syntax_colors.setdefault("stream", self.syntax_colors.get("type", "#569CD6"))
        self.syntax_colors.setdefault("async", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("await", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("null_safety", self.syntax_colors.get("decorator", "#FF8C00"))
        
        self.setup_tags()