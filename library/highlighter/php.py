from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # PHP keywords
        self.keywords = {
            # Control structures
            'if', 'else', 'elseif', 'while', 'do', 'for', 'foreach',
            'switch', 'case', 'default', 'break', 'continue', 'return',
            'goto',
            # Function and class related
            'function', 'class', 'interface', 'trait', 'namespace',
            'use', 'as', 'extends', 'implements', 'abstract', 'final',
            'public', 'private', 'protected', 'static', 'const',
            'new', 'clone', 'instanceof',
            # Error handling
            'try', 'catch', 'throw', 'finally',
            # Other
            'echo', 'print', 'isset', 'unset', 'empty', 'die', 'exit',
            'eval', 'include', 'include_once', 'require', 'require_once',
            'global', 'var', 'list', 'array', 'yield', 'from',
            # Magic constants
            '__LINE__', '__FILE__', '__DIR__', '__FUNCTION__',
            '__CLASS__', '__TRAIT__', '__METHOD__', '__NAMESPACE__',
            # Types
            'bool', 'int', 'float', 'string', 'array', 'object',
            'callable', 'iterable', 'void', 'mixed', 'never',
            'true', 'false', 'null'
        }
        
        # PHP built-in functions and constants
        self.builtins = {
            # Common functions
            'array', 'count', 'strlen', 'substr', 'strpos', 'explode',
            'implode', 'json_encode', 'json_decode', 'file_get_contents',
            'file_put_contents', 'date', 'time', 'strtotime', 'isset',
            'empty', 'unset', 'is_array', 'is_string', 'is_int',
            'is_float', 'is_bool', 'is_null', 'is_object', 'is_callable'
        }
        
        # PHP syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("variable", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("constant", self.syntax_colors.get("constant", "#4FC1FF"))
        self.syntax_colors.setdefault("superglobal", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("heredoc", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("nowdoc", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("php_tag", self.syntax_colors.get("decorator", "#FF8C00"))
        
        self.setup_tags()