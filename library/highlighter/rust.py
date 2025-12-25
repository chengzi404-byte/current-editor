from .base import BaseHighlighter
import ast
import re

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
        
        # Import information storage
        self.imported_crates = set()
        self.imported_symbols = {}  # symbol_name -> symbol_type
        
        # Rust syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("macro", self.syntax_colors.get("function", "#DCDCAA"))
        self.syntax_colors.setdefault("lifetime", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("attribute", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("trait", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("enum", self.syntax_colors.get("type", "#4EC9B0"))
        self.syntax_colors.setdefault("struct", self.syntax_colors.get("type", "#4EC9B0"))
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
    
    def highlight(self, event=None):
        """Main highlighting method for Rust"""
        if not self.text_widget:
            return
            
        # Initialize tag batch
        self._tag_batch = []
        
        # Process comments and strings first
        self._highlight_comments_and_strings()
        
        # Process Rust-specific syntax
        self._highlight_rust_syntax()
        
        # Refresh batch tags
        self._refresh_batch_tags()
    
    def _highlight_rust_syntax(self):
        """Process Rust-specific syntax highlighting"""
        code = self.text_widget.get("1.0", "end")
        
        # Process use statements (imports)
        self._process_rust_imports(code)
        
        # Highlight Rust keywords and types
        self._highlight_rust_keywords_and_types(code)
        
        # Highlight imported symbols
        self._highlight_imported_symbols()
    
    def _process_rust_imports(self, code):
        """Process Rust use statements to extract imported symbols"""
        self.imported_crates.clear()
        self.imported_symbols.clear()
        
        # Match use statements
        use_pattern = r'use\s+([^;]+);'
        
        for match in re.finditer(use_pattern, code):
            use_statement = match.group(1).strip()
            
            # Extract crate/module name
            crate_match = re.match(r'^(\w+)(?:::|\s*as\s*\w+)?', use_statement)
            if crate_match:
                crate_name = crate_match.group(1)
                self.imported_crates.add(crate_name)
            
            # Extract symbols from use statements
            self._extract_rust_symbols(use_statement)
    
    def _extract_rust_symbols(self, use_statement):
        """Extract symbols from Rust use statements"""
        # Handle different use patterns
        # 1. use crate::module::symbol;
        # 2. use crate::module::{symbol1, symbol2};
        # 3. use crate::module::symbol as alias;
        
        # Handle braces for multiple imports
        brace_match = re.search(r'\{([^}]+)\}', use_statement)
        if brace_match:
            symbols_text = brace_match.group(1)
            symbols = [s.strip() for s in symbols_text.split(',') if s.strip()]
            
            for symbol in symbols:
                # Handle aliases
                alias_match = re.match(r'^(\w+)(?:\s+as\s+(\w+))?', symbol)
                if alias_match:
                    symbol_name = alias_match.group(1)
                    alias_name = alias_match.group(2) or symbol_name
                    self._classify_rust_symbol(symbol_name, alias_name)
        else:
            # Single symbol import
            symbol_match = re.match(r'^[^:]+::(\w+)(?:\s+as\s+(\w+))?$', use_statement)
            if symbol_match:
                symbol_name = symbol_match.group(1)
                alias_name = symbol_match.group(2) or symbol_name
                self._classify_rust_symbol(symbol_name, alias_name)
    
    def _classify_rust_symbol(self, symbol_name, display_name):
        """Classify Rust symbol based on naming conventions"""
        # Rust naming conventions:
        # - Functions/methods: snake_case
        # - Types (structs, enums, traits): PascalCase
        # - Constants: SCREAMING_SNAKE_CASE
        # - Macros: end with !
        # - Modules: snake_case
        
        if symbol_name.endswith('!'):
            self.imported_symbols[display_name] = 'macro'
        elif symbol_name.isupper() and '_' in symbol_name:
            self.imported_symbols[display_name] = 'constant'
        elif symbol_name[0].isupper():
            # PascalCase - likely a type
            if symbol_name.endswith('Trait'):
                self.imported_symbols[display_name] = 'trait'
            elif symbol_name.endswith('Enum'):
                self.imported_symbols[display_name] = 'enum'
            else:
                self.imported_symbols[display_name] = 'type'
        else:
            # snake_case - likely a function or module
            self.imported_symbols[display_name] = 'function'
    
    def _highlight_rust_keywords_and_types(self, code):
        """Highlight Rust keywords and built-in types"""
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self._add_tag("keyword", start, end)
        
        # Highlight built-in types
        builtin_types = {
            'bool', 'char', 'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
            'u8', 'u16', 'u32', 'u64', 'u128', 'usize', 'f32', 'f64',
            'str', 'String', 'Vec', 'Option', 'Result', 'Box', 'Rc', 'Arc'
        }
        
        for builtin in builtin_types:
            pattern = r'\b' + re.escape(builtin) + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self._add_tag("type", start, end)
    
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
                elif symbol_type == 'trait':
                    self._add_tag("imported_trait", start, end)
                elif symbol_type == 'enum':
                    self._add_tag("imported_enum", start, end)
                elif symbol_type == 'type':
                    self._add_tag("imported_type", start, end)
                else:  # function/module
                    self._add_tag("imported_function", start, end)
