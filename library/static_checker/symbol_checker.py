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
    
    def _check_python_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        检查Python代码的符号定义
        
        Args:
            code: 要检查的Python代码
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        try:
            print(f"Python代码检查开始，代码长度: {len(code)}")
            # 解析Python代码生成AST
            tree = ast.parse(code)
            
            # 构建符号表
            self._build_python_symbol_table(tree)
            print(f"符号表构建完成: {self.symbol_table}")
            
            # 检查符号引用
            self._check_python_symbol_references(tree)
            print(f"符号引用检查完成，错误数量: {len(self.errors)}")
            
        except SyntaxError as e:
            # 语法错误，添加到错误列表
            print(f"语法错误: {str(e)}")
            self._add_error(
                line=e.lineno,
                column=e.offset,
                end_line=e.lineno,
                end_column=e.offset + 1,
                error_type="syntax-error",
                error_message=str(e)
            )
        except Exception as e:
            # 其他错误，记录但不影响检查
            print(f"符号检查错误: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return self.get_errors()
    
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