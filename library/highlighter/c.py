from .base import BaseHighlighter
import re

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # C keywords
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while'
        }
        
        # Import information storage
        self.included_headers = set()
        self.imported_symbols = {}  # symbol_name -> symbol_type
        
        # C syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("preprocessor", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("macro", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("type", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("struct", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("pointer", self.syntax_colors.get("operator", "#D4D4D4"))
        
        self.setup_tags()
    
    def highlight(self, event=None):
        """Main highlighting method for C"""
        if not self.text_widget:
            return
            
        # Initialize tag batch
        self._tag_batch = []
        
        # Process comments and strings first
        self._highlight_comments_and_strings()
        
        # Process C-specific syntax
        self._highlight_c_syntax()
        
        # Refresh batch tags
        self._refresh_batch_tags()
    
    def _highlight_c_syntax(self):
        """Process C-specific syntax highlighting"""
        code = self.text_widget.get("1.0", "end")
        
        # Process include directives
        self._process_c_includes(code)
        
        # Highlight C keywords and types
        self._highlight_c_keywords_and_types(code)
        
        # Highlight imported symbols
        self._highlight_imported_symbols()
    
    def _process_c_includes(self, code):
        """Process C include directives to extract included headers"""
        self.included_headers.clear()
        self.imported_symbols.clear()
        
        # Match include directives
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        
        for match in re.finditer(include_pattern, code):
            header_name = match.group(1)
            self.included_headers.add(header_name)
            
            # Extract common symbols from standard headers
            self._extract_c_symbols(header_name)
    
    def _extract_c_symbols(self, header_name):
        """Extract common symbols from C standard headers"""
        # Common symbols from standard C headers
        standard_symbols = {
            'stdio.h': {
                'printf', 'scanf', 'fprintf', 'fscanf', 'sprintf', 'sscanf',
                'fopen', 'fclose', 'fread', 'fwrite', 'fseek', 'ftell',
                'getchar', 'putchar', 'gets', 'puts', 'fgets', 'fputs'
            },
            'stdlib.h': {
                'malloc', 'calloc', 'realloc', 'free', 'exit', 'abort',
                'atoi', 'atof', 'atol', 'rand', 'srand', 'qsort',
                'abs', 'labs', 'div', 'ldiv'
            },
            'string.h': {
                'strcpy', 'strncpy', 'strcat', 'strncat', 'strcmp', 'strncmp',
                'strlen', 'strchr', 'strrchr', 'strstr', 'strtok', 'memset',
                'memcpy', 'memmove', 'memcmp'
            },
            'math.h': {
                'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10', 'pow',
                'sqrt', 'ceil', 'floor', 'fabs', 'fmod'
            },
            'time.h': {
                'time', 'ctime', 'localtime', 'gmtime', 'mktime', 'strftime',
                'clock', 'difftime'
            }
        }
        
        if header_name in standard_symbols:
            for symbol in standard_symbols[header_name]:
                self.imported_symbols[symbol] = 'function'
    
    def _highlight_c_keywords_and_types(self, code):
        """Highlight C keywords and built-in types"""
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self._add_tag("keyword", start, end)
        
        # Highlight preprocessor directives
        preprocessor_pattern = r'#\s*(include|define|undef|if|ifdef|ifndef|else|elif|endif|error|pragma)'
        for match in re.finditer(preprocessor_pattern, code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self._add_tag("preprocessor", start, end)
        
        # Highlight macros (defined with #define)
        macro_pattern = r'#define\s+(\w+)'
        for match in re.finditer(macro_pattern, code):
            macro_name = match.group(1)
            # Highlight macro usage
            usage_pattern = r'\b' + re.escape(macro_name) + r'\b'
            for usage_match in re.finditer(usage_pattern, code):
                start = f"1.0+{usage_match.start()}c"
                end = f"1.0+{usage_match.end()}c"
                self._add_tag("macro", start, end)
    
    def _highlight_imported_symbols(self):
        """Highlight imported symbols in the code"""
        if not self.imported_symbols:
            return
            
        code = self.text_widget.get("1.0", "end")
        
        for symbol_name, symbol_type in self.imported_symbols.items():
            # Create pattern to match the symbol (avoid matching in strings/comments)
            pattern = r'\b' + re.escape(symbol_name) + r'\b'
            
            for match in re.finditer(pattern, code):
                start_pos = match.start()
                end_pos = match.end()
                
                # Check if this is inside a string or comment
                if self._is_in_string_or_comment(start_pos):
                    continue
                
                start = f"1.0+{start_pos}c"
                end = f"1.0+{end_pos}c"
                
                # Determine tag based on symbol type
                if symbol_type == 'macro':
                    self._add_tag("imported_macro", start, end)
                elif symbol_type == 'constant':
                    self._add_tag("imported_constant", start, end)
                elif symbol_type == 'struct':
                    self._add_tag("imported_struct", start, end)
                elif symbol_type == 'enum':
                    self._add_tag("imported_enum", start, end)
                elif symbol_type == 'type':
                    self._add_tag("imported_type", start, end)
                else:  # function
                    self._add_tag("imported_function", start, end) 