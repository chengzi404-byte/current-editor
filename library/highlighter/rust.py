from .base import BaseHighlighter
import ast

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Rust keyword
        self.keywords = {
            "as", "async", "await", "break", "const", "continue", "crate", 
            "dyn", "else", "enum", "extern", "false", "fn", "for", "if", 
            "impl", "in", "let", "loop", "match", "mod", "move", "mut", 
            "pub", "ref", "return", "self", "Self", "static", "struct", 
            "super", "trait", "true", "type", "unsafe", "use", "where", "while"
        }
        
        self.syntax_colors.update({
            "macro": self.syntax_colors["function"],      # Macro
            "lifetime": self.syntax_colors["decorator"],  # Lifetime
            "attribute": self.syntax_colors["decorator"], # Attr
            "trait": self.syntax_colors["interface"],    # trait
            "enum": self.syntax_colors["type"],          # Enum
            "struct": self.syntax_colors["type"],        # Struct
        })
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        
        if isinstance(node, ast.Name):
            self._highlight_rust_name(node, start, end)
        elif isinstance(node, ast.Call):
            self._highlight_rust_macro(node, start, end)
            
    def _highlight_rust_name(self, node: ast.Name, start: str, end: str):
        """Highlight Rust-specific names"""
        name = node.id
        if name in self.keywords:
            self._add_tag("keyword", start, end)
        elif name.startswith("'"):  # Lifetime
            self._add_tag("lifetime", start, end)
        elif name.isupper():  # Constant
            self._add_tag("constant", start, end)
            
    def _highlight_rust_macro(self, node: ast.Call, start: str, end: str):
        """Highlight Rust macro calls"""
        if isinstance(node.func, ast.Name) and node.func.id.endswith("!"):
            self._add_tag("macro", start, end)
