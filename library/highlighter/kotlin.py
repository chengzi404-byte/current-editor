from .base import BaseHighlighter
import re

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Kotlin keywords
        self.keywords = {
            # Declaration keywords
            'val', 'var', 'fun', 'class', 'object', 'interface', 'enum',
            'typealias', 'constructor', 'init', 'companion',
            # Control flow
            'if', 'else', 'when', 'for', 'while', 'do', 'break', 'continue',
            'return', 'throw', 'try', 'catch', 'finally',
            # Modifiers
            'public', 'private', 'protected', 'internal', 'open',
            'abstract', 'final', 'override', 'data', 'sealed',
            'inline', 'noinline', 'crossinline', 'tailrec', 'external',
            'annotation', 'const', 'lateinit', 'operator', 'infix',
            'suspend', 'expect', 'actual', 'reified',
            # Other keywords
            'in', 'is', 'as', 'this', 'super', 'null', 'true', 'false',
            'by', 'get', 'set', 'where', 'field', 'property', 'it',
            'out', 'in', 'dynamic', 'typeof', 'package', 'import'
        }
        
        # Kotlin built-in types and functions
        self.builtins = {
            # Basic types
            'Boolean', 'Byte', 'Short', 'Int', 'Long', 'Float', 'Double',
            'Char', 'String', 'Array', 'List', 'Set', 'Map',
            'MutableList', 'MutableSet', 'MutableMap',
            # Common classes
            'Any', 'Unit', 'Nothing', 'Throwable', 'Exception',
            'Error', 'RuntimeException',
            # Standard library functions
            'println', 'print', 'readLine', 'require', 'check', 'error',
            'TODO', 'run', 'let', 'apply', 'also', 'with', 'use',
            'repeat', 'assert', 'lazy'
        }
        
        # Import information storage
        self.imported_packages = set()
        self.imported_symbols = {}  # symbol_name -> symbol_type
        
        # Kotlin syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("annotation", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("lambda", self.syntax_colors.get("function", "#569CD6"))
        self.syntax_colors.setdefault("extension", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("delegation", self.syntax_colors.get("function", "#4FC1FF"))
        self.syntax_colors.setdefault("coroutine", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("data_class", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("sealed_class", self.syntax_colors.get("class", "#4EC9B0"))
        # Import-related colors are now loaded from theme file
        
        self.setup_tags()
    
    def highlight(self, event=None):
        """Main highlighting method for Kotlin"""
        if not self.text_widget:
            return
            
        # Initialize tag batch
        self._tag_batch = []
        
        # Process comments and strings first
        self._highlight_comments_and_strings()
        
        # Process Kotlin-specific syntax
        self._highlight_kotlin_syntax()
        
        # Refresh batch tags
        self._refresh_batch_tags()
    
    def _highlight_kotlin_syntax(self):
        """Process Kotlin-specific syntax highlighting"""
        code = self.text_widget.get("1.0", "end")
        
        # Process import statements
        self._process_kotlin_imports(code)
        
        # Highlight Kotlin keywords and types
        self._highlight_kotlin_keywords_and_types(code)
        
        # Highlight imported symbols
        self._highlight_imported_symbols()
    
    def _process_kotlin_imports(self, code):
        """Process Kotlin import statements to extract imported symbols"""
        self.imported_packages.clear()
        self.imported_symbols.clear()
        
        # Match import statements
        import_pattern = r'import\s+([^;\n]+)'
        
        for match in re.finditer(import_pattern, code):
            import_statement = match.group(1).strip()
            
            # Extract package name
            package_match = re.match(r'^([\w.]+)', import_statement)
            if package_match:
                package_name = package_match.group(1)
                self.imported_packages.add(package_name)
            
            # Extract symbols from import statements
            self._extract_kotlin_symbols(import_statement)
    
    def _extract_kotlin_symbols(self, import_statement):
        """Extract symbols from Kotlin import statements"""
        # Handle different import patterns
        # 1. import package.Class
        # 2. import package.function
        # 3. import package.*
        
        # Check for wildcard import
        if import_statement.endswith('.*'):
            package_name = import_statement[:-2]
            # For wildcard imports, we'll classify based on common package symbols
            self._classify_kotlin_package_symbols(package_name)
        else:
            # Specific symbol import
            symbol_parts = import_statement.split('.')
            if len(symbol_parts) > 1:
                symbol_name = symbol_parts[-1]
                
                # Classify symbol based on naming conventions
                self._classify_kotlin_symbol(symbol_name)
    
    def _classify_kotlin_package_symbols(self, package_name):
        """Classify Kotlin symbols based on package name"""
        # Common Kotlin standard library packages and their symbols
        kotlin_stdlib_symbols = {
            'kotlin': {
                'println', 'print', 'readLine', 'require', 'check', 'error',
                'TODO', 'run', 'let', 'apply', 'also', 'with', 'use'
            },
            'kotlin.collections': {
                'listOf', 'setOf', 'mapOf', 'mutableListOf', 'mutableSetOf',
                'mutableMapOf', 'emptyList', 'emptySet', 'emptyMap'
            },
            'kotlin.io': {
                'readText', 'writeText', 'copyTo', 'forEachLine'
            },
            'kotlin.text': {
                'toInt', 'toDouble', 'toBoolean', 'toUpperCase', 'toLowerCase'
            }
        }
        
        if package_name in kotlin_stdlib_symbols:
            for symbol in kotlin_stdlib_symbols[package_name]:
                self._classify_kotlin_symbol(symbol)
    
    def _classify_kotlin_symbol(self, symbol_name):
        """Classify Kotlin symbol based on naming conventions"""
        # Kotlin naming conventions:
        # - Classes, interfaces, objects: PascalCase
        # - Functions, properties: camelCase
        # - Typealiases: PascalCase
        
        if symbol_name[0].isupper():
            # PascalCase - likely a class, interface, object, or typealias
            if symbol_name.endswith('Interface'):
                self.imported_symbols[symbol_name] = 'interface'
            elif symbol_name.endswith('Object'):
                self.imported_symbols[symbol_name] = 'object'
            else:
                self.imported_symbols[symbol_name] = 'class'
        else:
            # camelCase - likely a function or property
            self.imported_symbols[symbol_name] = 'function'
    
    def _highlight_kotlin_keywords_and_types(self, code):
        """Highlight Kotlin keywords and built-in types"""
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self._add_tag("keyword", start, end)
        
        # Highlight built-in types and functions
        for builtin in self.builtins:
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
                if symbol_type == 'class':
                    self._add_tag("imported_class", start, end)
                elif symbol_type == 'interface':
                    self._add_tag("imported_interface", start, end)
                elif symbol_type == 'object':
                    self._add_tag("imported_object", start, end)
                elif symbol_type == 'function':
                    self._add_tag("imported_function", start, end)
                elif symbol_type == 'property':
                    self._add_tag("imported_property", start, end)
                elif symbol_type == 'typealias':
                    self._add_tag("imported_typealias", start, end)