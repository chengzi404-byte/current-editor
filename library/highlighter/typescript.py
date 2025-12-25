from .base import BaseHighlighter
import ast

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # TypeScript keywords (JavaScript keywords + TypeScript specific)
        self.keywords = {
            # JavaScript keywords
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'continue', 'return', 'try', 'catch', 'finally', 'throw',
            'var', 'let', 'const', 'function', 'class', 'extends',
            'constructor', 'super', 'new', 'this',
            'import', 'export', 'default', 'from', 'as',
            'typeof', 'instanceof', 'in', 'of', 'void', 'delete',
            'async', 'await', 'yield',
            
            # TypeScript specific keywords
            'interface', 'type', 'namespace', 'module', 'declare',
            'implements', 'abstract', 'public', 'private', 'protected',
            'readonly', 'static', 'get', 'set', 'enum', 'keyof',
            'any', 'unknown', 'never', 'void', 'null', 'undefined',
            'string', 'number', 'boolean', 'symbol', 'bigint', 'object',
            'true', 'false', 'null', 'undefined',
            'as', 'is', 'infer', 'extends', 'keyof', 'typeof',
            'unique', 'readonly', 'override', 'satisfies'
        }
        
        # 存储导入的模块和符号信息
        self.imported_modules = set()
        self.imported_symbols = {}  # {symbol_name: module_name}
        
        # TypeScript syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("type", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("interface", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("enum", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("generic", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("decorator", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("regex", self.syntax_colors.get("string", "#D16969"))
        self.syntax_colors.setdefault("template", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("arrow", self.syntax_colors.get("function", "#569CD6"))
        self.syntax_colors.setdefault("object", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("array", self.syntax_colors.get("class", "#4EC9B0"))
        
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing for TypeScript/JavaScript"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        
        # 处理导入语句
        if isinstance(node, ast.Import):
            self._process_typescript_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._process_typescript_import_from(node)
        
        # 处理符号引用
        elif isinstance(node, ast.Name):
            self._highlight_typescript_imported_symbol(node, start, end)
        elif isinstance(node, ast.Attribute):
            self._highlight_typescript_imported_attribute(node)
            
    def _process_typescript_import(self, node: ast.Import):
        """处理TypeScript/JavaScript的import语句"""
        for alias in node.names:
            module_name = alias.name
            self.imported_modules.add(module_name)
            
            # TypeScript/JavaScript的import语句通常使用默认导入
            if not alias.asname:
                # 使用模块的最后一部分作为符号名
                module_parts = module_name.split('/')
                symbol_name = module_parts[-1].replace('.js', '').replace('.ts', '')
                self.imported_symbols[symbol_name] = module_name
            else:
                self.imported_symbols[alias.asname] = module_name
                
    def _process_typescript_import_from(self, node: ast.ImportFrom):
        """处理TypeScript/JavaScript的from-import语句"""
        module_name = node.module or ""
        for alias in node.names:
            symbol_name = alias.name
            
            # 记录导入的符号
            if alias.asname:
                self.imported_symbols[alias.asname] = f"{module_name}.{symbol_name}"
            else:
                self.imported_symbols[symbol_name] = f"{module_name}.{symbol_name}"
                
    def _highlight_typescript_imported_symbol(self, node: ast.Name, start: str, end: str):
        """高亮TypeScript/JavaScript导入的符号"""
        symbol_name = node.id
        
        if symbol_name in self.imported_symbols:
            # 根据命名约定判断符号类型
            if symbol_name[0].isupper() or self._is_typescript_class_name(symbol_name):
                self._add_tag("imported_class", start, end)
            elif symbol_name.startswith('I') and symbol_name[1].isupper():
                self._add_tag("imported_interface", start, end)
            elif symbol_name.endswith('Type') or symbol_name.endswith('Props'):
                self._add_tag("imported_type", start, end)
            else:
                # 检查是否是函数调用
                parent = self._get_parent_node(node)
                if parent and isinstance(parent, ast.Call) and parent.func == node:
                    self._add_tag("imported_function", start, end)
                else:
                    self._add_tag("imported_variable", start, end)
                    
    def _highlight_typescript_imported_attribute(self, node: ast.Attribute):
        """高亮TypeScript/JavaScript导入模块的属性访问"""
        try:
            if isinstance(node.value, ast.Name):
                module_name = node.value.id
                if module_name in self.imported_modules:
                    # 高亮模块名
                    module_start, module_end = self.get_position(node.value)
                    self._add_tag("imported_module", module_start, module_end)
                    
                    # 高亮属性名
                    attr_start = f"{node.lineno}.{node.col_offset + len(module_name) + 1}"
                    attr_end = f"{node.lineno}.{node.col_offset + len(module_name) + 1 + len(node.attr)}"
                    
                    # 根据属性名判断类型
                    if node.attr[0].isupper() or self._is_typescript_class_name(node.attr):
                        self._add_tag("imported_class", attr_start, attr_end)
                    elif node.attr.startswith('I') and node.attr[1].isupper():
                        self._add_tag("imported_interface", attr_start, attr_end)
                    elif node.attr.endswith('Type') or node.attr.endswith('Props'):
                        self._add_tag("imported_type", attr_start, attr_end)
                    else:
                        self._add_tag("imported_function", attr_start, attr_end)
        except Exception as e:
            print(f"Error highlighting TypeScript imported attribute: {e}")
            
    def _is_typescript_class_name(self, name: str) -> bool:
        """判断TypeScript/JavaScript类名"""
        # TypeScript类名通常以大写字母开头
        if name and name[0].isupper():
            return True
        # 常见的TypeScript类名模式
        common_class_patterns = {
            'React', 'Component', 'App', 'Button', 'Input', 'Form',
            'Service', 'Controller', 'Model', 'View', 'Router'
        }
        if name in common_class_patterns:
            return True
        return False