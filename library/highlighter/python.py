from .base import BaseHighlighter
import ast
import builtins
import keyword

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)

        self.builtins = set(dir(builtins))
        self.keywords = set(keyword.kwlist)
        
        # Python syntax colors
        self.syntax_colors.update({
            "f_string": self.syntax_colors["string"],     # f-string (use the string color)
            "bytes": self.syntax_colors["string"],        # byte-string
            "exception": self.syntax_colors["class"],     # exception
            "magic_method": self.syntax_colors["function"], # magic method
        })
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        

        if isinstance(node, ast.JoinedStr):  # f-string
            self._highlight_f_string(node, start, end)
        elif isinstance(node, ast.Constant):     # byte string
            self._add_tag("bytes", start, end)
        elif isinstance(node, ast.Try):       # try-except block
            self._highlight_try_except(node)
        elif isinstance(node, ast.AsyncFunctionDef):  # async function def
            self._highlight_async_function(node)
            
    def _highlight_f_string(self, node: ast.JoinedStr, start: str, end: str):
        """Highlight f-strings"""
        self._add_tag("f_string", start, end)
        # process f-string
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                expr_start, expr_end = self.get_position(value)
                self._add_tag("variable", expr_start, expr_end)
                
    def _highlight_try_except(self, node: ast.Try):
        """Highlight try-except blocks"""
        # try-except blocks
        for handler in node.handlers:
            if handler.type:
                start, end = self.get_position(handler.type)
                self._add_tag("exception", start, end)
                
    def _highlight_async_function(self, node: ast.AsyncFunctionDef):
        """Highlight async functions"""
        start, end = self.get_position(node)
        # highlight async keyword
        async_end = f"{node.lineno}.{node.col_offset + 5}"
        self._add_tag("keyword", start, async_end)
        
        # highlight function name
        name_start = f"{node.lineno}.{node.col_offset + 9}"  # async def after
        name_end = f"{node.lineno}.{node.col_offset + 9 + len(node.name)}"
        self._add_tag("function", name_start, name_end)
