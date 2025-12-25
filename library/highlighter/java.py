from .base import BaseHighlighter
import ast

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Java keywords
        self.keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'final', 'finally', 'float', 'for',
            'if', 'implements', 'import', 'instanceof', 'int', 'interface',
            'long', 'native', 'new', 'package', 'private', 'protected',
            'public', 'return', 'short', 'static', 'strictfp', 'super',
            'switch', 'synchronized', 'this', 'throw', 'throws', 'transient',
            'try', 'void', 'volatile', 'while'
        }
        
        # 存储导入的包和类信息
        self.imported_packages = set()
        self.imported_classes = {}  # {class_name: package_name}
        
        # Java syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("annotation", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("generic", self.syntax_colors.get("type", "#4EC9B0"))
        self.syntax_colors.setdefault("interface", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("enum", self.syntax_colors.get("type", "#4EC9B0"))
        self.syntax_colors.setdefault("package", self.syntax_colors.get("namespace", "#4EC9B0"))
        self.setup_tags()
        
    def _highlight_node(self, node: ast.AST):
        """Extend base highlighter's node processing"""
        super()._highlight_node(node)
        
        if not hasattr(node, 'lineno'):
            return
            
        start, end = self.get_position(node)
        
        # 处理Java导入语句
        if isinstance(node, ast.Import):
            self._process_java_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._process_java_import_from(node)
        
        # 处理符号引用
        elif isinstance(node, ast.Name):
            self._highlight_java_imported_symbol(node, start, end)
            self._highlight_java_name(node, start, end)
        elif isinstance(node, ast.Attribute):
            self._highlight_java_imported_attribute(node)
        elif isinstance(node, ast.ClassDef):
            self._highlight_java_class(node, start, end)
            
    def _highlight_java_name(self, node: ast.Name, start: str, end: str):
        """Highlight Java-specific names"""
        name = node.id
        if name in self.keywords:
            self._add_tag("keyword", start, end)
        elif name.startswith("@"):  # Comment
            self._add_tag("annotation", start, end)
            
    def _highlight_java_class(self, node: ast.ClassDef, start: str, end: str):
        """Highlight Java class definitions"""
        # Process generic
        for base in node.bases:
            if isinstance(base, ast.Subscript):
                base_start, base_end = self.get_position(base)
                self._add_tag("generic", base_start, base_end)
                
    def _process_java_import(self, node: ast.Import):
        """处理Java的import语句"""
        for alias in node.names:
            import_path = alias.name
            
            # 记录导入的包
            if import_path.endswith('.*'):
                # 通配符导入：import java.util.*;
                package_name = import_path[:-2]
                self.imported_packages.add(package_name)
            else:
                # 具体类导入：import java.util.ArrayList;
                package_parts = import_path.split('.')
                if len(package_parts) > 1:
                    package_name = '.'.join(package_parts[:-1])
                    class_name = package_parts[-1]
                    self.imported_packages.add(package_name)
                    self.imported_classes[class_name] = package_name
                
    def _process_java_import_from(self, node: ast.ImportFrom):
        """处理Java的静态导入（import static）"""
        package_name = node.module or ""
        for alias in node.names:
            symbol_name = alias.name
            
            if symbol_name == '*':
                # 静态通配符导入：import static java.lang.Math.*;
                self.imported_packages.add(package_name)
            else:
                # 具体静态导入：import static java.lang.Math.PI;
                full_symbol_name = f"{package_name}.{symbol_name}"
                self.imported_classes[symbol_name] = package_name
                
    def _highlight_java_imported_symbol(self, node: ast.Name, start: str, end: str):
        """高亮Java导入的符号"""
        symbol_name = node.id
        
        if symbol_name in self.imported_classes:
            package_name = self.imported_classes[symbol_name]
            
            # 根据命名约定判断符号类型
            if symbol_name.endswith('Exception') or symbol_name.endswith('Error'):
                self._add_tag("imported_class", start, end)
            elif symbol_name.endswith('Interface'):
                self._add_tag("imported_interface", start, end)
            elif symbol_name.endswith('Enum'):
                self._add_tag("imported_enum", start, end)
            elif symbol_name.endswith('Annotation'):
                self._add_tag("imported_annotation", start, end)
            elif symbol_name.isupper() or symbol_name.endswith('_CONSTANT'):
                # 常量（通常全大写）
                self._add_tag("imported_variable", start, end)
            elif symbol_name[0].isupper():
                # 类名（首字母大写）
                self._add_tag("imported_class", start, end)
            else:
                # 方法或变量
                parent = self._get_parent_node(node)
                if parent and isinstance(parent, ast.Call) and parent.func == node:
                    self._add_tag("imported_function", start, end)
                else:
                    self._add_tag("imported_variable", start, end)
                    
    def _highlight_java_imported_attribute(self, node: ast.Attribute):
        """高亮Java导入包的属性访问"""
        try:
            if isinstance(node.value, ast.Name):
                package_name = node.value.id
                if package_name in self.imported_packages:
                    # 高亮包名
                    package_start, package_end = self.get_position(node.value)
                    self._add_tag("imported_package", package_start, package_end)
                    
                    # 高亮类名或静态成员
                    attr_start = f"{node.lineno}.{node.col_offset + len(package_name) + 1}"
                    attr_end = f"{node.lineno}.{node.col_offset + len(package_name) + 1 + len(node.attr)}"
                    
                    if node.attr[0].isupper():
                        self._add_tag("imported_class", attr_start, attr_end)
                    elif node.attr.isupper():
                        self._add_tag("imported_variable", attr_start, attr_end)
                    else:
                        self._add_tag("imported_function", attr_start, attr_end)
        except Exception as e:
            print(f"Error highlighting Java imported attribute: {e}")
