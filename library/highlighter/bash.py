from .base import BaseHighlighter
import ast

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Bash keywords
        self.keywords = {
            "if", "then", "else", "elif", "fi", "case", "esac", "for",
            "while", "until", "do", "done", "in", "function", "select",
            "break", "continue", "return", "export", "readonly", "local",
            "unset", "eval", "exec", "set", "shift", "trap", "source",
            "true", "false"
        }
        
        # Bash特定的语法高亮规则
        self.syntax_colors.update({
            "variable": self.syntax_colors["variable"],    # Varible
            "command": self.syntax_colors["function"],     # Command
            "parameter": self.syntax_colors["parameter"],  # Parameter
            "heredoc": self.syntax_colors["string"],      # Heredoc
            "subshell": self.syntax_colors["operator"],   # subshell
        })
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        
        # Bash Process
        if isinstance(node, ast.Name):
            self._highlight_bash_name(node, start, end)
        elif isinstance(node, ast.Call):
            self._highlight_bash_command(node, start, end)
            
    def _highlight_bash_name(self, node: ast.Name, start: str, end: str):
        """Highlight Bash-specific names"""
        name = node.id
        if name in self.keywords:
            self._add_tag("keyword", start, end)
        elif name.startswith("$"):  # 变量
            self._add_tag("variable", start, end)
            
    def _highlight_bash_command(self, node: ast.Call, start: str, end: str):
        """Highlight Bash commands"""
        if isinstance(node.func, ast.Name):
            self._add_tag("command", start, end)
