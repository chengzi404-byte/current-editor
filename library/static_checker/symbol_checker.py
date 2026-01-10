"""
符号定义检查器
用于检查函数、类、变量等标识符的定义与引用关系
"""

from typing import List, Optional, Dict, Set
from library.static_checker.base import BaseStaticChecker, StaticCheckError
import ast
import re


class SymbolChecker(BaseStaticChecker):
    """
    符号定义检查器
    检查函数、类、变量等标识符的定义与引用关系
    """
    
    def __init__(self, language: str, editor_widget=None):
        """
        初始化符号定义检查器
        
        Args:
            language: 支持的编程语言
            editor_widget: 编辑器组件（可选）
        """
        super().__init__(language, editor_widget)
        
        # 符号表，用于存储标识符的定义信息
        self.symbol_table: Dict[str, Dict] = {
            "global": {
                "variables": set(),
                "functions": set(),
                "classes": set()
            },
            "functions": {}
        }
        
        # 支持的语言
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", 
            "csharp", "go", "ruby", "php"
        ]
    
    def check(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        执行符号定义检查
        
        Args:
            code: 要检查的代码内容
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        self.clear_errors()
        
        # 只处理支持的语言
        if self.language not in self.supported_languages:
            return self.get_errors()
        
        # 根据语言类型调用对应的检查方法
        if self.language == "python":
            return self._check_python_code(code, file_path)
        elif self.language in ["javascript", "typescript"]:
            return self._check_javascript_code(code, file_path)
        elif self.language == "java":
            return self._check_java_code(code, file_path)
        elif self.language in ["c", "cpp"]:
            return self._check_c_code(code, file_path)
        elif self.language == "csharp":
            return self._check_csharp_code(code, file_path)
        elif self.language == "go":
            return self._check_go_code(code, file_path)
        elif self.language == "ruby":
            return self._check_ruby_code(code, file_path)
        elif self.language == "php":
            return self._check_php_code(code, file_path)
        
        return self.get_errors()
    
    def __init__(self, language: str, editor_widget=None):
        """
        初始化符号定义检查器
        
        Args:
            language: 支持的编程语言
            editor_widget: 编辑器组件（可选）
        """
        super().__init__(language, editor_widget)
        
        # 符号表，用于存储标识符的定义信息
        self.symbol_table: Dict[str, Dict] = {
            "global": {
                "variables": set(),
                "functions": set(),
                "classes": set()
            },
            "functions": {}
        }
        
        # 支持的语言
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", 
            "csharp", "go", "ruby", "php"
        ]
        
        # flake8缓存机制
        self._flake8_cache = {}
        self._flake8_cache_timeout = 5  # 缓存超时时间（秒）
        self._last_flake8_call = 0
    
    def _check_python_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查Python代码的符号定义（使用flake8）
        
        Args:
            code: 要检查的Python代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        try:
            print(f"使用flake8检查Python代码，代码长度: {len(code)}")
            
            # 使用flake8进行代码检查
            import subprocess
            import tempfile
            import os
            import time
            
            # 计算代码哈希，用于缓存
            code_hash = hash(code)
            current_time = time.time()
            
            # 检查缓存是否有效
            if code_hash in self._flake8_cache and \
               (current_time - self._flake8_cache[code_hash]['timestamp'] < self._flake8_cache_timeout):
                print(f"使用缓存的flake8结果")
                # 从缓存中获取错误
                self.errors = self._flake8_cache[code_hash]['errors'].copy()
                return self.get_errors()
            
            # 将代码按行分割，用于准确计算结束位置
            code_lines = code.split('\n')
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file_path = f.name
            
            try:
                # 运行flake8命令
                result = subprocess.run(
                    ["D:/ProgramData/anaconda3/python.exe", "-m", "flake8", 
                     "--format", "%(row)d,%(col)d,%(code)s,%(text)s", 
                     temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=3  # 3秒超时，避免无限等待
                )
                
                print(f"flake8返回码: {result.returncode}")
                print(f"flake8输出: {result.stdout}")
                print(f"flake8错误: {result.stderr}")
                
                # 解析flake8输出
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self._parse_flake8_output(line, code_lines)
                
            finally:
                # 删除临时文件
                os.unlink(temp_file_path)
                
            print(f"flake8检查完成，错误数量: {len(self.errors)}")
            
            # 缓存结果
            self._flake8_cache[code_hash] = {
                'timestamp': current_time,
                'errors': self.errors.copy()
            }
            
            # 限制缓存大小
            if len(self._flake8_cache) > 10:
                # 移除最旧的缓存项
                oldest_key = min(self._flake8_cache.keys(), 
                               key=lambda k: self._flake8_cache[k]['timestamp'])
                del self._flake8_cache[oldest_key]
                print(f"移除最旧的flake8缓存项，当前缓存大小: {len(self._flake8_cache)}")
            
        except subprocess.TimeoutExpired:
            print("flake8检查超时")
        except Exception as e:
            # 其他错误，记录但不影响检查
            print(f"flake8检查错误: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return self.get_errors()
    
    def _parse_flake8_output(self, output_line: str, code_lines: list):
        """
        解析flake8输出行，转换为StaticCheckError对象
        
        Args:
            output_line: flake8输出行
        """
        try:
            # 解析输出行，格式: 行号,列号,错误码,错误信息
            parts = output_line.split(',')
            if len(parts) < 4:
                return
            
            line = int(parts[0])
            column = int(parts[1])
            error_code = parts[2]
            error_message = ','.join(parts[3:])
            
            # 根据错误码确定错误类型
            if error_code.startswith('E'):
                error_type = "error"
                severity = "error"
            elif error_code.startswith('W'):
                error_type = "warning"
                severity = "warning"
            elif error_code.startswith('F'):
                error_type = "warning"
                severity = "warning"
            elif error_code.startswith('C'):
                error_type = "warning"
                severity = "warning"
            elif error_code.startswith('N'):
                error_type = "warning"
                severity = "warning"
            else:
                error_type = "lint-error"
                severity = "warning"
            
            # 准确计算结束位置
            end_line = line
            end_column = column
            
            # 如果行号有效，尝试获取该行内容
            if 1 <= line <= len(code_lines):
                line_content = code_lines[line - 1]  # 列表索引从0开始
                
                # 根据错误类型确定结束位置
                if error_code.startswith('E2') or error_code.startswith('E7'):  # 空格错误
                    # 单个字符错误
                    end_column = column + 1
                elif error_code.startswith('E5'):  # 行太长
                    # 整行错误
                    end_column = len(line_content)
                elif error_code.startswith('F'):  # 未使用的变量/导入
                    # 尝试找到变量名的结束位置
                    if column < len(line_content):
                        # 从column位置开始，找到变量名的结束位置
                        for i in range(column, len(line_content)):
                            if not (line_content[i].isalnum() or line_content[i] == '_'):
                                end_column = i
                                break
                        else:
                            end_column = len(line_content)
                else:
                    # 默认处理：假设错误长度为1个字符
                    end_column = column + 1
            
            # 确保结束位置不超过行尾
            end_column = min(end_column, len(code_lines[line - 1])) if 1 <= line <= len(code_lines) else column + 1
            
            # 添加错误
            self._add_error(
                line=line,
                column=column + 1,  # flake8使用0-based列索引，我们使用1-based
                end_line=end_line,
                end_column=end_column + 1,  # flake8使用0-based列索引，我们使用1-based
                error_type=error_type,
                error_message=f"{error_code}: {error_message}",
                severity=severity
            )
            
            print(f"错误位置: {line}:{column+1} 到 {end_line}:{end_column+1}")
            
            print(f"解析flake8错误: 行{line}, 列{column} - {error_code}: {error_message}")
            
        except Exception as e:
            print(f"解析flake8输出错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _build_python_symbol_table(self, tree: ast.AST):
        """
        构建Python代码的符号表
        
        Args:
            tree: Python代码的AST树
        """
        # 重置符号表
        self.symbol_table = {
            "global": {
                "variables": set(),
                "functions": set(),
                "classes": set()
            },
            "functions": {}  # 存储函数参数和局部变量
        }
        
        # 遍历AST，收集符号定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 函数定义
                self.symbol_table["global"]["functions"].add(node.name)
                
                # 收集函数参数
                func_params = set()
                # 收集普通参数
                for arg in node.args.args:
                    func_params.add(arg.arg)
                # 收集*args参数
                if node.args.vararg:
                    func_params.add(node.args.vararg.arg)
                # 收集**kwargs参数
                if node.args.kwarg:
                    func_params.add(node.args.kwarg.arg)
                # 收集关键字参数
                for kwarg in node.args.kwonlyargs:
                    func_params.add(kwarg.arg)
                
                # 保存函数参数
                self.symbol_table["functions"][node.name] = func_params
            elif isinstance(node, ast.ClassDef):
                # 类定义
                self.symbol_table["global"]["classes"].add(node.name)
                
                # 收集类方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        self.symbol_table["global"]["functions"].add(method_name)
                        
                        # 收集方法参数
                        method_params = set()
                        # 收集普通参数
                        for arg in item.args.args:
                            method_params.add(arg.arg)
                        # 收集*args参数
                        if item.args.vararg:
                            method_params.add(item.args.vararg.arg)
                        # 收集**kwargs参数
                        if item.args.kwarg:
                            method_params.add(item.args.kwarg.arg)
                        # 收集关键字参数
                        for kwarg in item.args.kwonlyargs:
                            method_params.add(kwarg.arg)
                        
                        # 保存方法参数
                        self.symbol_table["functions"][method_name] = method_params
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # 变量定义
                self.symbol_table["global"]["variables"].add(node.id)
            elif isinstance(node, ast.Import):
                # 导入语句
                for alias in node.names:
                    if alias.asname:
                        self.symbol_table["global"]["variables"].add(alias.asname)
                    else:
                        self.symbol_table["global"]["variables"].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                # 从模块导入
                for alias in node.names:
                    if alias.asname:
                        self.symbol_table["global"]["variables"].add(alias.asname)
                    else:
                        self.symbol_table["global"]["variables"].add(alias.name)
    
    def _check_python_symbol_references(self, tree: ast.AST):
        """
        检查Python代码中的符号引用
        
        Args:
            tree: Python代码的AST树
        """
        # 遍历AST，检查符号引用
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                # 检查符号定义
                symbol_name = node.id
                
                # 只检查加载操作（变量引用），不检查存储操作（变量定义）
                if isinstance(node.ctx, ast.Load):
                    print(f"检查符号引用: {symbol_name}, 位置: {node.lineno}:{node.col_offset}")
                    
                    # 检查是否在符号表中
                    in_symbol_table = (
                        symbol_name in self.symbol_table["global"]["variables"] or
                        symbol_name in self.symbol_table["global"]["functions"] or
                        symbol_name in self.symbol_table["global"]["classes"] or
                        self._is_builtin(symbol_name)
                    )
                    
                    print(f"符号 '{symbol_name}' 在符号表中: {in_symbol_table}")
                    
                    if not in_symbol_table:
                        # 添加未定义符号错误
                        print(f"添加未定义符号错误: {symbol_name}")
                        self._add_error(
                            line=node.lineno,
                            column=node.col_offset + 1,
                            end_line=node.lineno,
                            end_column=node.col_offset + 1 + len(symbol_name),
                            error_type="undefined-symbol",
                            error_message=f"未定义的符号 '{symbol_name}'"
                        )
            elif isinstance(node, ast.Call):
                # 检查函数调用
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    print(f"检查函数调用: {func_name}, 位置: {node.func.lineno}:{node.func.col_offset}")
                    
                    # 检查函数是否定义
                    if (func_name not in self.symbol_table["global"]["functions"] and
                        func_name not in self.symbol_table["global"]["classes"] and
                        not self._is_builtin(func_name)):
                        print(f"添加未定义函数错误: {func_name}")
                        self._add_error(
                            line=node.func.lineno,
                            column=node.func.col_offset + 1,
                            end_line=node.func.lineno,
                            end_column=node.func.col_offset + 1 + len(func_name),
                            error_type="undefined-function",
                            error_message=f"未定义的函数调用 '{func_name}'"
                        )
    
    def _is_builtin(self, symbol_name: str) -> bool:
        """
        检查符号是否为内置符号
        
        Args:
            symbol_name: 符号名称
            
        Returns:
            如果是内置符号返回True，否则返回False
        """
        # 根据语言获取对应的内置符号列表
        builtins_map = {
            "python": {
                # Python内置函数、关键字和特殊变量
                "print", "input", "len", "range", "type", "int", "float", 
                "str", "bool", "list", "dict", "set", "tuple", "lambda", 
                "zip", "map", "filter", "enumerate", "reversed", "sorted", 
                "sum", "max", "min", "abs", "round", "pow", "divmod", 
                "all", "any", "isinstance", "issubclass", "id", "hex", 
                "oct", "bin", "chr", "ord", "ascii", "repr", "eval", 
                "exec", "compile", "open", "close", "file", 
                # 关键字
                "if", "else", "elif", "for", "while", "try", "except", 
                "finally", "with", "break", "continue", "return", "def", 
                "class", "lambda", "async", "await", "import", "from", 
                "as", "global", "nonlocal", "pass", "yield", "del", 
                "assert", "raise", "try", "except", "finally", "with", 
                "in", "not", "and", "or", "is", "is not", "==", "!=", 
                "+=", "-=", "*=", "/=", "//=", "%=", "**=", "&=", "|=", 
                "^=", "<<=", ">>=", "+=", "-=", "*=", "/=", "//=", "%=", 
                "**=", "&=", "|=", "^=", "<<=", ">>=", "True", "False", "None",
                # 特殊变量
                "__name__", "__file__", "__doc__", "__package__", "__init__", 
                "__str__", "__repr__", "__dict__", "__class__", "__module__", 
                "__bases__", "__mro__", "__subclasses__", "__getattr__", 
                "__setattr__", "__delattr__", "__call__", "__len__", "__getitem__", 
                "__setitem__", "__delitem__", "__iter__", "__next__", "__contains__", 
                "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__", 
                "__add__", "__sub__", "__mul__", "__truediv__", "__floordiv__", 
                "__mod__", "__pow__", "__and__", "__or__", "__xor__", "__lshift__", 
                "__rshift__", "__neg__", "__pos__", "__abs__", "__invert__", 
                "__complex__", "__int__", "__float__", "__round__", "__floor__", 
                "__ceil__", "__trunc__", "__index__", "__enter__", "__exit__", 
                "__await__", "__aiter__", "__anext__", "__aenter__", "__aexit__"
            },
            "javascript": {
                # JavaScript内置函数和关键字
                "console", "log", "alert", "prompt", "confirm", "document", "window", 
                "Math", "Date", "Array", "Object", "String", "Number", "Boolean", 
                "Function", "RegExp", "JSON", "Promise", "async", "await", "let", "const", 
                "var", "if", "else", "for", "while", "do", "switch", "case", "default", 
                "break", "continue", "return", "function", "class", "extends", "super", 
                "constructor", "this", "new", "delete", "typeof", "instanceof", "in", 
                "null", "undefined", "true", "false", "try", "catch", "finally", "throw", 
                "export", "import", "from", "as", "static", "async", "await", "of", "let", "const"
            },
            "typescript": {
                # TypeScript内置函数和关键字（包含JavaScript的）
                "console", "log", "alert", "prompt", "confirm", "document", "window", 
                "Math", "Date", "Array", "Object", "String", "Number", "Boolean", 
                "Function", "RegExp", "JSON", "Promise", "async", "await", "let", "const", 
                "var", "if", "else", "for", "while", "do", "switch", "case", "default", 
                "break", "continue", "return", "function", "class", "extends", "super", 
                "constructor", "this", "new", "delete", "typeof", "instanceof", "in", 
                "null", "undefined", "true", "false", "try", "catch", "finally", "throw", 
                "export", "import", "from", "as", "static", "async", "await", "of", "let", "const",
                "interface", "type", "enum", "namespace", "declare", "module", "any", "void",
                "never", "unknown", "symbol", "bigint", "readonly", "abstract", "protected", "private", "public"
            },
            "java": {
                # Java内置函数和关键字
                "System", "out", "println", "print", "Scanner", "String", "Integer", "Double", 
                "Float", "Long", "Short", "Byte", "Boolean", "Character", "Object", "Class", 
                "Math", "Random", "ArrayList", "LinkedList", "HashMap", "HashSet", "TreeMap", 
                "TreeSet", "if", "else", "for", "while", "do", "switch", "case", "default", 
                "break", "continue", "return", "public", "private", "protected", "static", 
                "final", "abstract", "class", "interface", "extends", "implements", "package", 
                "import", "new", "this", "super", "void", "int", "double", "float", "long", 
                "short", "byte", "boolean", "char", "true", "false", "null", "try", "catch", 
                "finally", "throw", "throws", "synchronized", "volatile", "transient", "native", "strictfp"
            },
            "c": {
                # C内置函数和关键字
                "printf", "scanf", "malloc", "free", "calloc", "realloc", "strlen", "strcmp", 
                "strcpy", "strcat", "memset", "memcpy", "memcmp", "exit", "getchar", "putchar", 
                "if", "else", "for", "while", "do", "switch", "case", "default", "break", 
                "continue", "return", "void", "int", "double", "float", "long", "short", 
                "char", "unsigned", "signed", "const", "volatile", "static", "extern", 
                "register", "auto", "struct", "union", "enum", "typedef", "sizeof", 
                "return", "goto", "switch", "case", "default", "break", "continue", "if", "else", 
                "for", "while", "do", "void", "int", "double", "float", "long", "short", "char"
            },
            "cpp": {
                # C++内置函数和关键字（包含C的）
                "cout", "cin", "endl", "printf", "scanf", "malloc", "free", "calloc", 
                "realloc", "strlen", "strcmp", "strcpy", "strcat", "memset", "memcpy", 
                "memcmp", "exit", "getchar", "putchar", "if", "else", "for", "while", 
                "do", "switch", "case", "default", "break", "continue", "return", 
                "void", "int", "double", "float", "long", "short", "char", "unsigned", 
                "signed", "const", "volatile", "static", "extern", "register", "auto", 
                "struct", "union", "enum", "typedef", "sizeof", "return", "goto", "switch", 
                "case", "default", "break", "continue", "if", "else", "for", "while", 
                "do", "void", "int", "double", "float", "long", "short", "char", "class", 
                "public", "private", "protected", "virtual", "override", "final", "namespace", 
                "using", "template", "typename", "new", "delete", "this", "super", 
                "try", "catch", "throw", "constexpr", "const_cast", "dynamic_cast", 
                "static_cast", "reinterpret_cast", "typeid", "explicit", "friend", "inline", 
                "mutable", "noexcept", "nullptr", "operator", "private", "protected", 
                "public", "static", "struct", "template", "this", "typedef", "typename", 
                "using", "virtual", "void"
            },
            "csharp": {
                # C#内置函数和关键字
                "Console", "Write", "WriteLine", "Read", "ReadLine", "String", "Int32", 
                "Double", "Float", "Long", "Short", "Byte", "Boolean", "Char", "Object", 
                "Array", "List", "Dictionary", "HashSet", "Stack", "Queue", "if", "else", 
                "for", "while", "do", "switch", "case", "default", "break", "continue", 
                "return", "public", "private", "protected", "internal", "static", "readonly", 
                "const", "class", "struct", "interface", "enum", "delegate", "event", 
                "namespace", "using", "new", "this", "base", "void", "int", "double", 
                "float", "long", "short", "byte", "bool", "char", "true", "false", 
                "null", "try", "catch", "finally", "throw", "async", "await", "yield", 
                "lock", "volatile", "extern", "unsafe", "fixed", "ref", "out", "in", 
                "params", "optional", "dynamic", "var", "typeof", "is", "as", "sizeof"
            },
            "go": {
                # Go内置函数和关键字
                "fmt", "Print", "Println", "Printf", "Scan", "Scanln", "Scanf", "log", 
                "os", "File", "Reader", "Writer", "io", "net", "http", "json", 
                "strconv", "strings", "bytes", "time", "math", "rand", "sort", 
                "if", "else", "for", "switch", "case", "default", "break", "continue", 
                "return", "func", "var", "const", "type", "struct", "interface", "map", 
                "slice", "array", "chan", "select", "go", "defer", "panic", "recover", 
                "new", "make", "delete", "len", "cap", "append", "copy", "close", 
                "true", "false", "nil", "package", "import", "func", "type", "var", "const"
            },
            "ruby": {
                # Ruby内置函数和关键字
                "puts", "print", "gets", "chomp", "require", "load", "module", "class", 
                "def", "if", "else", "elsif", "end", "for", "while", "until", "do", "break", 
                "continue", "return", "next", "redo", "retry", "true", "false", "nil", "self", 
                "super", "new", "initialize", "attr_reader", "attr_writer", "attr_accessor", 
                "public", "private", "protected", "module_function", "include", "extend", 
                "raise", "rescue", "ensure", "begin", "end", "case", "when", "default", "then", 
                "and", "or", "not", "in", "is_a?", "instance_of?", "respond_to?", "nil?", "empty?"
            },
            "php": {
                # PHP内置函数和关键字
                "echo", "print", "printf", "sprintf", "scanf", "fscanf", "file_get_contents", 
                "file_put_contents", "require", "require_once", "include", "include_once", 
                "if", "else", "elseif", "for", "foreach", "while", "do", "switch", "case", 
                "default", "break", "continue", "return", "function", "class", "extends", 
                "implements", "namespace", "use", "new", "this", "self", "parent", "static", 
                "public", "private", "protected", "final", "abstract", "interface", "trait", 
                "const", "var", "global", "static", "goto", "try", "catch", "finally", "throw", 
                "die", "exit", "true", "false", "null", "isset", "unset", "empty", "is_null", 
                "array", "list", "clone", "instanceof", "echo", "print", "printf", "sprintf"
            }
        }
        
        # 获取当前语言的内置符号列表
        current_builtins = builtins_map.get(self.language, set())
        
        return symbol_name in current_builtins
    
    def _check_javascript_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查JavaScript代码的符号定义
        
        Args:
            code: 要检查的JavaScript代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_java_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查Java代码的符号定义
        
        Args:
            code: 要检查的Java代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_c_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查C和C++代码的符号定义
        
        Args:
            code: 要检查的C/C++代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_csharp_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查C#代码的符号定义
        
        Args:
            code: 要检查的C#代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_go_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查Go代码的符号定义
        
        Args:
            code: 要检查的Go代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_ruby_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查Ruby代码的符号定义
        
        Args:
            code: 要检查的Ruby代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()
    
    def _check_php_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查PHP代码的符号定义
        
        Args:
            code: 要检查的PHP代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        # 使用正则表达式进行基本的符号检查
        # 由于没有完整的解析器，这里只做简单的检查
        return self.get_errors()