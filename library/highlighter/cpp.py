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
        
        # reset theme
        self.syntax_colors.update({
            "keyword": "#569CD6",        # 关键字
            "type": "#4EC9B0",           # 数据类型
            "preprocessor": "#C586C0",   # 预处理指令
            "namespace": "#4EC9B0",      # 命名空间/类名
            "function": "#DCDCAA",       # 函数名
            "string": "#CE9178",         # 字符串
            "comment": "#6A9955",        # 注释
            "number": "#B5CEA8",         # 数字
            "operator": "#D4D4D4",       # 运算符
        })
        
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
            
            # Basic highlight
            self._basic_highlight(text)

            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"高亮错误: {str(e)}")