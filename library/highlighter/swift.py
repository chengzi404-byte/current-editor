from .base import BaseHighlighter
import re

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Swift keywords
        self.keywords = {
            # Declaration keywords
            'let', 'var', 'func', 'class', 'struct', 'enum', 'protocol',
            'extension', 'import', 'typealias', 'associatedtype',
            # Control flow
            'if', 'else', 'switch', 'case', 'default', 'for', 'while',
            'repeat', 'do', 'break', 'continue', 'fallthrough',
            'guard', 'defer', 'return', 'throw', 'throws', 'rethrows',
            # Access control
            'public', 'private', 'fileprivate', 'internal', 'open',
            # Other keywords
            'in', 'is', 'as', 'try', 'catch', 'where', 'nil', 'self',
            'super', 'true', 'false', 'some', 'any', 'actor', 'nonisolated',
            'isolated', 'sendable', 'async', 'await', 'convenience',
            'dynamic', 'final', 'indirect', 'lazy', 'optional', 'override',
            'required', 'static', 'unowned', 'weak', 'willSet', 'didSet'
        }
        
        # Swift built-in types and functions
        self.builtins = {
            # Basic types
            'Bool', 'Int', 'Int8', 'Int16', 'Int32', 'Int64',
            'UInt', 'UInt8', 'UInt16', 'UInt32', 'UInt64',
            'Float', 'Double', 'String', 'Character', 'Array',
            'Dictionary', 'Set', 'Optional', 'Result', 'Error',
            # Common protocols
            'Equatable', 'Comparable', 'Hashable', 'Identifiable',
            'Codable', 'Decodable', 'Encodable', 'CaseIterable',
            'CustomStringConvertible', 'CustomDebugStringConvertible'
        }
        
        # Import information storage
        self.imported_modules = set()
        self.imported_symbols = {}  # symbol_name -> symbol_type
        
        # Swift syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("attribute", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("property_wrapper", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("macro", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("result_builder", self.syntax_colors.get("function", "#4FC1FF"))
        self.syntax_colors.setdefault("actor", self.syntax_colors.get("class", "#569CD6"))
        self.syntax_colors.setdefault("protocol", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("extension", self.syntax_colors.get("class", "#4EC9B0"))
        # Import-related colors are now loaded from theme file
        
        self.setup_tags()
    
    def highlight(self, event=None):
        """Main highlighting method for Swift"""
        if not self.text_widget:
            return
            
        # Initialize tag batch
        self._tag_batch = []
        
        # Process comments and strings first
        self._highlight_comments_and_strings()
        
        # Process Swift-specific syntax
        self._highlight_swift_syntax()
        
        # Refresh batch tags
        self._refresh_batch_tags()
    
    def _highlight_swift_syntax(self):
        """Process Swift-specific syntax highlighting"""
        code = self.text_widget.get("1.0", "end")
        
        # Process import statements
        self._process_swift_imports(code)
        
        # Highlight Swift keywords and types
        self._highlight_swift_keywords_and_types(code)
        
        # Highlight imported symbols
        self._highlight_imported_symbols()
    
    def _process_swift_imports(self, code):
        """Process Swift import statements to extract imported symbols"""
        self.imported_modules.clear()
        self.imported_symbols.clear()
        
        # Match import statements
        import_pattern = r'import\s+([^;\n]+)'
        
        for match in re.finditer(import_pattern, code):
            import_statement = match.group(1).strip()
            
            # Extract module name
            module_match = re.match(r'^(\w+)', import_statement)
            if module_match:
                module_name = module_match.group(1)
                self.imported_modules.add(module_name)
            
            # Extract symbols from import statements
            self._extract_swift_symbols(import_statement)
    
    def _extract_swift_symbols(self, import_statement):
        """Extract symbols from Swift import statements"""
        # Handle different import patterns
        # 1. import Module
        # 2. import Module.Symbol
        # 3. import class Module.Class
        # 4. import func Module.function
        
        # Check for specific import types
        type_pattern = r'^(class|struct|enum|protocol|func|var|let|typealias)\s+([^\s]+)'
        type_match = re.match(type_pattern, import_statement)
        
        if type_match:
            import_type = type_match.group(1)
            symbol_path = type_match.group(2)
            
            # Extract symbol name from path
            symbol_parts = symbol_path.split('.')
            if len(symbol_parts) > 1:
                symbol_name = symbol_parts[-1]
                
                # Map import type to symbol type
                if import_type in ('class', 'struct', 'enum', 'protocol'):
                    self.imported_symbols[symbol_name] = import_type
                elif import_type == 'func':
                    self.imported_symbols[symbol_name] = 'function'
                elif import_type in ('var', 'let'):
                    self.imported_symbols[symbol_name] = 'property'
                elif import_type == 'typealias':
                    self.imported_symbols[symbol_name] = 'typealias'
        else:
            # Simple module import - extract symbols from module name
            module_match = re.match(r'^(\w+)$', import_statement)
            if module_match:
                module_name = module_match.group(1)
                # For simple imports, we'll classify based on naming conventions
                self._classify_swift_module_symbols(module_name)
    
    def _classify_swift_module_symbols(self, module_name):
        """Classify Swift symbols based on naming conventions"""
        # Swift naming conventions:
        # - Classes, structs, enums, protocols: PascalCase
        # - Functions, methods, variables: camelCase
        # - Typealiases: PascalCase
        
        # For now, we'll add common Swift standard library symbols
        swift_stdlib_symbols = {
            'Foundation': {
                'NSObject', 'NSString', 'NSArray', 'NSDictionary',
                'NSDate', 'NSData', 'NSURL', 'NSError'
            },
            'UIKit': {
                'UIView', 'UIViewController', 'UILabel', 'UIButton',
                'UITableView', 'UICollectionView', 'UIImage', 'UIColor'
            },
            'SwiftUI': {
                'View', 'Text', 'Button', 'VStack', 'HStack', 'ZStack',
                'Image', 'Color', 'State', 'Binding', 'Environment'
            }
        }
        
        if module_name in swift_stdlib_symbols:
            for symbol in swift_stdlib_symbols[module_name]:
                if symbol[0].isupper():
                    self.imported_symbols[symbol] = 'class'
                else:
                    self.imported_symbols[symbol] = 'property'
    
    def _highlight_swift_keywords_and_types(self, code):
        """Highlight Swift keywords and built-in types"""
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self._add_tag("keyword", start, end)
        
        # Highlight built-in types and protocols
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
                elif symbol_type == 'struct':
                    self._add_tag("imported_struct", start, end)
                elif symbol_type == 'enum':
                    self._add_tag("imported_enum", start, end)
                elif symbol_type == 'protocol':
                    self._add_tag("imported_protocol", start, end)
                elif symbol_type == 'function':
                    self._add_tag("imported_function", start, end)
                elif symbol_type == 'property':
                    self._add_tag("imported_property", start, end)
                elif symbol_type == 'typealias':
                    self._add_tag("imported_typealias", start, end)