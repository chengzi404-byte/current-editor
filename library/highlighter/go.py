from .base import BaseHighlighter
import re

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Go语言关键字
        self.keywords = {
            # 声明关键字
            'var', 'const', 'type', 'func', 'package', 'import',
            # 控制流
            'if', 'else', 'switch', 'case', 'default', 'for', 'range',
            'break', 'continue', 'goto', 'fallthrough',
            # 函数控制
            'return', 'defer', 'go',
            # 类型系统
            'struct', 'interface', 'map', 'chan',
            # 错误处理
            'panic', 'recover',
            # 可见性
            'nil', 'true', 'false', 'iota'
        }
        
        # Go内置类型和函数
        self.builtins = {
            # 内置类型
            'bool', 'string', 'int', 'int8', 'int16', 'int32', 'int64',
            'uint', 'uint8', 'uint16', 'uint32', 'uint64', 'uintptr',
            'byte', 'rune', 'float32', 'float64', 'complex64', 'complex128',
            'error',
            # 内置函数
            'append', 'cap', 'close', 'complex', 'copy', 'delete', 'imag',
            'len', 'make', 'new', 'panic', 'print', 'println', 'real', 'recover'
        }
        
        # 导入信息存储
        self.imported_packages = set()
        self.imported_symbols = {}
        
        # Go syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("builtin", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("struct", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("interface", self.syntax_colors.get("interface", "#4EC9B0"))
        self.syntax_colors.setdefault("channel", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("goroutine", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("pointer", self.syntax_colors.get("operator", "#D4D4D4"))
        self.syntax_colors.setdefault("defer", self.syntax_colors.get("keyword", "#FF8C00"))
        
        self.setup_tags()
    
    def highlight(self):
        """重写高亮方法，专门处理Go语言语法"""
        try:
            # 保存当前状态
            current_insert = self.text_widget.index("insert")
            current_view = self.text_widget.yview()
            current_selection = None
            try:
                current_selection = (
                    self.text_widget.index("sel.first"),
                    self.text_widget.index("sel.last")
                )
            except:
                pass
                
            # 清除标签
            self._clear_tags()
            text = self.text_widget.get("1.0", "end-1c")
            
            # 初始化标签批处理
            self._tag_batch = {}
            
            # 处理注释和字符串
            self._highlight_comments_and_strings(text)
            
            # 处理Go语言特定的语法
            self._highlight_go_syntax(text)
            
            # 刷新剩余的批处理标签操作
            self._flush_all_tag_batches()
            
            # 恢复状态
            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"Go高亮失败: {str(e)}")
            # 回退到基础高亮
            self._basic_highlight(text)
    
    def _highlight_go_syntax(self, text: str):
        """处理Go语言特定的语法高亮"""
        # 重置导入信息
        self.imported_packages = set()
        self.imported_symbols = {}
        
        # 按行处理
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 处理导入语句
            self._process_go_imports(line, line_num)
            
            # 高亮关键字
            self._highlight_go_keywords(line, line_num)
            
            # 高亮内置类型和函数
            self._highlight_go_builtins(line, line_num)
            
            # 高亮导入的符号
            self._highlight_imported_symbols(line, line_num)
    
    def _process_go_imports(self, line: str, line_num: int):
        """处理Go导入语句"""
        # 匹配导入语句
        import_pattern = r'^\s*import\s+(?:\((?:[^)]*)\)|(?:[^\n;]*))'
        import_match = re.search(import_pattern, line)
        
        if import_match:
            # 高亮import关键字
            import_start = line.find('import')
            if import_start != -1:
                start = f"{line_num}.{import_start}"
                end = f"{line_num}.{import_start + 6}"
                self._add_tag("keyword", start, end)
            
            # 提取导入的包名
            self._extract_go_packages(line, line_num)
    
    def _extract_go_packages(self, line: str, line_num: int):
        """提取Go导入的包名"""
        # 匹配单行导入
        single_import_pattern = r'import\s+"([^"]+)"'
        single_matches = re.findall(single_import_pattern, line)
        
        for package in single_matches:
            self.imported_packages.add(package)
            # 高亮包名
            package_start = line.find(f'"{package}"')
            if package_start != -1:
                start = f"{line_num}.{package_start + 1}"
                end = f"{line_num}.{package_start + 1 + len(package)}"
                self._add_tag("imported_package", start, end)
        
        # 匹配多行导入（括号内的导入）
        if '(' in line and ')' in line:
            # 提取括号内的内容
            start_idx = line.find('(')
            end_idx = line.find(')')
            if start_idx != -1 and end_idx != -1:
                import_block = line[start_idx + 1:end_idx]
                # 匹配每个导入项
                block_matches = re.findall(r'"([^"]+)"', import_block)
                for package in block_matches:
                    self.imported_packages.add(package)
                    # 高亮包名
                    package_start = import_block.find(f'"{package}"')
                    if package_start != -1:
                        actual_start = start_idx + 1 + package_start + 1
                        start = f"{line_num}.{actual_start}"
                        end = f"{line_num}.{actual_start + len(package)}"
                        self._add_tag("imported_package", start, end)
    
    def _highlight_go_keywords(self, line: str, line_num: int):
        """高亮Go关键字"""
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self._add_tag("keyword", start, end)
    
    def _highlight_go_builtins(self, line: str, line_num: int):
        """高亮Go内置类型和函数"""
        for builtin in self.builtins:
            pattern = r'\b' + re.escape(builtin) + r'\b'
            for match in re.finditer(pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self._add_tag("builtin", start, end)
    
    def _highlight_imported_symbols(self, line: str, line_num: int):
        """高亮导入的符号"""
        # 高亮包名访问（如 fmt.Println）
        for package in self.imported_packages:
            # 提取包名（最后一个部分）
            package_name = package.split('/')[-1]
            
            # 匹配包名.符号的模式
            pattern = r'\b' + re.escape(package_name) + r'\.(\w+)'
            for match in re.finditer(pattern, line):
                # 高亮包名部分
                package_start = f"{line_num}.{match.start()}"
                package_end = f"{line_num}.{match.start() + len(package_name)}"
                self._add_tag("imported_package", package_start, package_end)
                
                # 高亮符号部分
                symbol = match.group(1)
                symbol_start = f"{line_num}.{match.start() + len(package_name) + 1}"
                symbol_end = f"{line_num}.{match.end()}"
                
                # 根据符号命名约定判断类型
                if symbol[0].isupper():
                    # 大写开头：可能是类型、接口、结构体
                    if symbol.endswith('er') or symbol.startswith('I'):
                        self._add_tag("imported_interface", symbol_start, symbol_end)
                    else:
                        self._add_tag("imported_type", symbol_start, symbol_end)
                else:
                    # 小写开头：可能是函数、方法、变量
                    if symbol.startswith('get') or symbol.startswith('set') or symbol.endswith('Func'):
                        self._add_tag("imported_function", symbol_start, symbol_end)
                    else:
                        self._add_tag("imported_variable", symbol_start, symbol_end)
        
        # 高亮直接使用的导入符号（如 math.Pi）
        for package in self.imported_packages:
            package_name = package.split('/')[-1]
            # 匹配包名后跟符号的模式
            pattern = r'\b' + re.escape(package_name) + r'\b'
            for match in re.finditer(pattern, line):
                # 检查是否在包名访问的上下文中
                context_start = max(0, match.start() - 1)
                context_end = min(len(line), match.end() + 1)
                context = line[context_start:context_end]
                
                # 如果不是包名访问的一部分（后面没有点），则高亮为包名
                if not (context_end < len(line) and line[context_end] == '.'):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("imported_package", start, end)