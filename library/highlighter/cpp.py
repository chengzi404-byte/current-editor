from typing import Any


from .base import BaseHighlighter
import re

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        
        # C++ keywords
        self.keywords = {
            'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'break', 
            'continue', 'return', 'try', 'catch', 'throw', 'new', 'delete',
            'class', 'struct', 'union', 'enum', 'namespace', 'using', 'typedef',
            'public', 'private', 'protected', 'virtual', 'override', 'final',
            'static', 'const', 'mutable', 'volatile', 'explicit', 'friend',
            'template', 'typename', 'this', 'auto', 'decltype', 'constexpr',
            'thread_local', 'alignas', 'alignof', 'noexcept', 'nullptr'
        }
        
        # C++ types
        self.types = {
            'int', 'char', 'short', 'long', 'float', 'double', 'bool', 'void',
            'wchar_t', 'char16_t', 'char32_t', 'uint8_t', 'int8_t', 'uint16_t',
            'int16_t', 'uint32_t', 'int32_t', 'uint64_t', 'int64_t', 'size_t',
            'ptrdiff_t', 'nullptr_t'
        }
        
        # C++ preprocessor
        self.preprocessor = {
            '#include', '#define', '#ifdef', '#ifndef', '#endif', '#if', '#elif',
            '#else', '#pragma', '#error', '#line'
        }
        
        # 导入信息存储
        self.included_headers = set()
        self.imported_symbols = {}
        
        # reset theme
        # C++ syntax colors - use theme colors
        # Import-related colors are now loaded from theme file
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("preprocessor", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("namespace", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("function", self.syntax_colors.get("function", "#DCDCAA"))
        
        self.setup_tags()
        
    def _highlight_comments_and_strings(self, text: str):
        """Highlight C++ Comments and String"""
        try:
            # Process multi line comment
            multi_line_comment_pattern = r'(/\*[\s\S]*?\*/)'
            for match in re.finditer(multi_line_comment_pattern, text):
                self._highlight_match("comment", match, text)
            
            # Process single line comment
            single_line_comment_pattern = r'(//.*?$)'
            for match in re.finditer(single_line_comment_pattern, text, re.MULTILINE):
                self._highlight_match("comment", match, text)
            
            # Process strings
            string_pattern = r'(\".*?\"|\'.*?\')'
            for match in re.finditer(string_pattern, text):
                self._highlight_match("string", match, text)
                
            # Process charactor
            char_pattern = r'(\'.*?\')'
            for match in re.finditer(char_pattern, text):
                self._highlight_match("string", match, text)
                
        except Exception as e:
            print(f"注释和字符串高亮错误: {str(e)}")
            # try
            self._basic_highlight(text)
            
    def _highlight_match(self, tag: str, match: re.Match, text: str):
        """Highlight area"""
        start_pos = match.start()
        end_pos = match.end()
        
        # 计算起始行和列
        start_line = text.count('\n', 0, start_pos) + 1
        start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
        
        # 计算结束行和列
        end_line = text.count('\n', 0, end_pos) + 1
        end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
        
        start = f"{start_line}.{start_col}"
        end = f"{end_line}.{end_col}"
        
        self._add_tag(tag, start, end)
            
    def _basic_highlight(self, text: str):
        """basic highlight"""
        try:
            # Process
            self._highlight_comments_and_strings(text)
            
            # Preprocessor
            preprocessor_pattern = r'(#\w+)'
            for match in re.finditer(preprocessor_pattern, text, re.MULTILINE):
                self._highlight_match("preprocessor", match, text)
            
            # Keywords and types
            keywords_and_types = sorted(self.keywords.union(self.types), key=len, reverse=True)
            pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords_and_types) + r')\b'
            
            for match in re.finditer(pattern, text):
                keyword = match.group(0)
                tag = "type" if keyword in self.types else "keyword"
                self._highlight_match(tag, match, text)
            
            # Process functions
            function_pattern = r'\b(\w+)\s*\('
            for match in re.finditer(function_pattern, text):
                function_name = match.group(1)
                # Match
                if function_name not in self.keywords and function_name not in self.types:
                    self._highlight_match("function", match, text)
            
            # Process numbers
            number_pattern = r'\b(\d+(\.\d+)?([eE][+-]?\d+)?)\b'
            for match in re.finditer(number_pattern, text):
                self._highlight_match("number", match, text)
            
            # Process operators
            operators = r'(\+|-|\*|/|%|=|==|!=|<|>|<=|>=|&&|\|\||!|\^|&|\||~|<<|>>|\+\+|--)'
            for match in re.finditer(operators, text):
                self._highlight_match("operator", match, text)
                
        except Exception as e:
            print(f"基本高亮处理错误: {str(e)}")
            
    def highlight(self):
        """highlight"""
        try:
            # Save current status
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
                
            # Highlight
            self._clear_tags()
            text = self.text_widget.get("1.0", "end-1c")
            
            # 初始化标签批处理
            self._tag_batch = {}
            
            # 处理注释和字符串
            self._highlight_comments_and_strings(text)
            
            # 处理C++特定的语法
            self._highlight_cpp_syntax(text)
            
            # 刷新剩余的批处理标签操作
            self._flush_all_tag_batches()

            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"高亮错误: {str(e)}")
    
    def _highlight_cpp_syntax(self, text: str):
        """处理C++特定的语法高亮"""
        # 重置导入信息
        self.included_headers = set()
        self.imported_symbols = {}
        
        # 按行处理
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 处理#include指令
            self._process_cpp_includes(line, line_num)
            
            # 高亮预处理指令
            self._highlight_cpp_preprocessor(line, line_num)
            
            # 高亮关键字和类型
            self._highlight_cpp_keywords_and_types(line, line_num)
            
            # 高亮导入的符号
            self._highlight_imported_symbols(line, line_num)
    
    def _process_cpp_includes(self, line: str, line_num: int):
        """处理C++ #include指令"""
        # 匹配#include指令
        include_pattern = r'^\s*#include\s+[<"]([^>"]+)[>"]'
        include_match = re.search(include_pattern, line)
        
        if include_match:
            # 提取头文件名
            header = include_match.group(1)
            self.included_headers.add(header)
            
            # 高亮#include关键字
            include_start = line.find('#include')
            if include_start != -1:
                start = f"{line_num}.{include_start}"
                end = f"{line_num}.{include_start + 8}"
                self._add_tag("preprocessor", start, end)
            
            # 高亮头文件名
            header_start = line.find(header)
            if header_start != -1:
                start = f"{line_num}.{header_start}"
                end = f"{line_num}.{header_start + len(header)}"
                self._add_tag("imported_header", start, end)
    
    def _highlight_cpp_preprocessor(self, line: str, line_num: int):
        """高亮C++预处理指令"""
        for directive in self.preprocessor:
            pattern = r'\b' + re.escape(directive) + r'\b'
            for match in re.finditer(pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self._add_tag("preprocessor", start, end)
    
    def _highlight_cpp_keywords_and_types(self, line: str, line_num: int):
        """高亮C++关键字和类型"""
        keywords_and_types = sorted(self.keywords.union(self.types), key=len, reverse=True)
        pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords_and_types) + r')\b'
        
        for match in re.finditer(pattern, line):
            keyword = match.group(0)
            tag = "type" if keyword in self.types else "keyword"
            start = f"{line_num}.{match.start()}"
            end = f"{line_num}.{match.end()}"
            self._add_tag(tag, start, end)
    
    def _highlight_imported_symbols(self, line: str, line_num: int):
        """高亮导入的符号"""
        # 高亮命名空间访问（如 std::cout）
        namespace_pattern = r'\b(\w+)::(\w+)'
        for match in re.finditer(namespace_pattern, line):
            namespace = match.group(1)
            symbol = match.group(2)
            
            # 高亮命名空间部分
            namespace_start = f"{line_num}.{match.start()}"
            namespace_end = f"{line_num}.{match.start() + len(namespace)}"
            self._add_tag("imported_namespace", namespace_start, namespace_end)
            
            # 高亮符号部分
            symbol_start = f"{line_num}.{match.start() + len(namespace) + 2}"
            symbol_end = f"{line_num}.{match.end()}"
            
            # 根据符号命名约定判断类型
            if symbol[0].isupper():
                # 大写开头：可能是类、结构体
                if symbol.startswith('C') or symbol.endswith('Class'):
                    self._add_tag("imported_class", symbol_start, symbol_end)
                else:
                    self._add_tag("imported_struct", symbol_start, symbol_end)
            else:
                # 小写开头：可能是函数、变量
                if symbol.endswith('()') or symbol.startswith('get') or symbol.startswith('set'):
                    self._add_tag("imported_function", symbol_start, symbol_end)
                else:
                    self._add_tag("imported_variable", symbol_start, symbol_end)
        
        # 高亮标准库函数（如 std::cout, std::endl）
        std_patterns = [
            r'\bstd::(\w+)',  # std命名空间
            r'\b(\w+)_t\b',   # 标准类型
        ]
        
        for pattern in std_patterns:
            for match in re.finditer(pattern, line):
                symbol = match.group(1) if match.groups() else match.group(0)
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                
                if pattern == r'\bstd::(\w+)':
                    # std命名空间中的符号
                    if symbol[0].isupper():
                        self._add_tag("imported_class", start, end)
                    else:
                        self._add_tag("imported_function", start, end)
                else:
                    # 标准类型
                    self._add_tag("imported_type", start, end)