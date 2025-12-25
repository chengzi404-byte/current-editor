from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Lua keywords
        self.keywords = {
            # Control flow
            'if', 'then', 'else', 'elseif', 'end',
            'while', 'do', 'repeat', 'until',
            'for', 'in', 'break', 'return',
            # Function and variable
            'function', 'local', 'nil', 'true', 'false',
            # Other
            'and', 'or', 'not', 'goto'
        }
        
        # Lua built-in functions and variables
        self.builtins = {
            # Basic functions
            'print', 'type', 'tostring', 'tonumber', 'pairs', 'ipairs',
            'next', 'getmetatable', 'setmetatable', 'rawget', 'rawset',
            'rawlen', 'select', 'unpack', 'pack',
            # Math functions
            'math.abs', 'math.floor', 'math.ceil', 'math.max', 'math.min',
            'math.random', 'math.sin', 'math.cos', 'math.tan',
            # String functions
            'string.sub', 'string.find', 'string.gsub', 'string.match',
            'string.format', 'string.len', 'string.upper', 'string.lower',
            # Table functions
            'table.insert', 'table.remove', 'table.concat', 'table.sort',
            # Global variables
            '_G', '_VERSION', 'arg'
        }
        
        # Lua syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("table", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("metatable", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("coroutine", self.syntax_colors.get("function", "#569CD6"))
        self.syntax_colors.setdefault("global", self.syntax_colors.get("variable", "#FF8C00"))
        self.syntax_colors.setdefault("long_string", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("comment_block", self.syntax_colors.get("comment", "#6A9955"))
        
        self.setup_tags()