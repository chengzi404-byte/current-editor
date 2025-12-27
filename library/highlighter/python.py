from .base import BaseHighlighter
import ast
import builtins
import keyword

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)

        self.builtins = set(dir(builtins))
        self.keywords = set(keyword.kwlist)
        
        # 存储导入的模块和符号信息
        self.imported_modules = set()
        self.imported_symbols = {}  # {symbol_name: module_name}
        
        # Python syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Additional language-specific colors with fallback
        self.syntax_colors.setdefault("f_string", self.syntax_colors["string"])     # f-string (use the string color)
        self.syntax_colors.setdefault("bytes", self.syntax_colors["string"])        # byte-string
        self.syntax_colors.setdefault("exception", self.syntax_colors["class"])     # exception
        self.syntax_colors.setdefault("magic_method", self.syntax_colors["function"]) # magic method
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        
        # 处理导入语句，收集导入的符号信息
        if isinstance(node, ast.Import):
            self._process_import_statement(node)
        elif isinstance(node, ast.ImportFrom):
            self._process_import_from_statement(node)
        
        # 处理符号引用，根据导入信息进行高亮
        elif isinstance(node, ast.Name):
            self._highlight_imported_symbol(node, start, end)
        elif isinstance(node, ast.Attribute):
            self._highlight_imported_attribute(node)

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
        
    def _process_import_statement(self, node: ast.Import):
        """处理import语句，收集导入的模块信息"""
        for alias in node.names:
            module_name = alias.name
            self.imported_modules.add(module_name)
            
            # 如果使用了别名，记录别名和原模块名的映射
            if alias.asname:
                self.imported_symbols[alias.asname] = module_name
            else:
                # 如果没有别名，使用模块的最后一部分作为符号名
                module_parts = module_name.split('.')
                symbol_name = module_parts[-1]
                self.imported_symbols[symbol_name] = module_name
                
    def _process_import_from_statement(self, node: ast.ImportFrom):
        """处理from-import语句，收集导入的符号信息"""
        module_name = node.module or ""
        for alias in node.names:
            symbol_name = alias.name
            full_symbol_name = f"{module_name}.{symbol_name}" if module_name else symbol_name
            
            # 记录导入的符号
            if alias.asname:
                self.imported_symbols[alias.asname] = full_symbol_name
            else:
                self.imported_symbols[symbol_name] = full_symbol_name
                
    def _highlight_imported_symbol(self, node: ast.Name, start: str, end: str):
        """高亮导入的符号"""
        symbol_name = node.id
        
        # 检查是否是导入的符号
        if symbol_name in self.imported_symbols:
            full_symbol_name = self.imported_symbols[symbol_name]
            
            # 根据上下文判断符号类型
            parent = self._get_parent_node(node)
            
            if parent and isinstance(parent, ast.Call) and parent.func == node:
                # 函数调用
                self._add_tag("imported_function", start, end)
            elif self._is_likely_class_name(symbol_name):
                # 类引用
                self._add_tag("imported_class", start, end)
            else:
                # 变量引用
                self._add_tag("imported_variable", start, end)
                
    def _highlight_imported_attribute(self, node: ast.Attribute):
        """高亮导入模块的属性访问"""
        try:
            # 检查是否是模块属性访问
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
                    if node.attr[0].isupper() or self._is_likely_class_name(node.attr):
                        self._add_tag("imported_class", attr_start, attr_end)
                    elif node.attr.endswith('_') or node.attr.isupper():
                        self._add_tag("imported_variable", attr_start, attr_end)
                    else:
                        self._add_tag("imported_function", attr_start, attr_end)
        except Exception as e:
            print(f"Error highlighting imported attribute: {e}")
            
    def _is_likely_class_name(self, name: str) -> bool:
        """判断一个名称是否可能是类名（基于命名约定）"""
        # 类名通常以大写字母开头
        if name and name[0].isupper():
            return True
        # 常见的类名模式
        common_class_patterns = {
            'Tk', 'Frame', 'Button', 'Label', 'Entry', 'Text', 'Canvas',
            'Listbox', 'Scrollbar', 'Menu', 'Message', 'Scale', 'Spinbox'
        }
        if name in common_class_patterns:
            return True
        return False
