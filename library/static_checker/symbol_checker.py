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
            }
        }
        
        # 支持的语言
        self.supported_languages = ["python"]
    
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
        
        if self.language == "python":
            return self._check_python_code(code, file_path)
        
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
            # 解析Python代码生成AST
            tree = ast.parse(code)
            
            # 构建符号表
            self._build_python_symbol_table(tree)
            
            # 检查符号引用
            self._check_python_symbol_references(tree)
            
        except SyntaxError as e:
            # 语法错误，添加到错误列表
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
        # 构建父节点映射，用于确定节点所在的函数或方法
        parent_map = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parent_map[child] = node
        
        # 遍历AST，检查符号引用
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # 符号引用
                symbol_name = node.id
                
                # 检查是否是函数参数
                in_function = False
                if node in parent_map:
                    # 查找当前节点所在的函数或方法
                    current = parent_map[node]
                    while current:
                        if isinstance(current, ast.FunctionDef):
                            # 检查是否是函数参数
                            if current.name in self.symbol_table["functions"]:
                                if symbol_name in self.symbol_table["functions"][current.name]:
                                    in_function = True
                                    break
                        elif isinstance(current, ast.ClassDef):
                            # 查找类方法
                            for item in current.body:
                                if isinstance(item, ast.FunctionDef):
                                    if item.name in self.symbol_table["functions"]:
                                        if symbol_name in self.symbol_table["functions"][item.name]:
                                            in_function = True
                                            break
                            if in_function:
                                break
                        # 继续向上查找
                        if current in parent_map:
                            current = parent_map[current]
                        else:
                            break
                
                # 检查是否在符号表中或是否是函数参数
                if (symbol_name not in self.symbol_table["global"]["variables"] and
                    symbol_name not in self.symbol_table["global"]["functions"] and
                    symbol_name not in self.symbol_table["global"]["classes"] and
                    not self._is_builtin(symbol_name) and
                    not in_function):
                    
                    # 添加未定义符号错误
                    self._add_error(
                        line=node.lineno,
                        column=node.col_offset + 1,
                        end_line=node.lineno,
                        end_column=node.col_offset + 1 + len(symbol_name),
                        error_type="undefined-symbol",
                        error_message=f"未定义的符号 '{symbol_name}'"
                    )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # 函数调用或类实例化
                func_name = node.func.id
                
                # 检查函数或类是否定义
                if (func_name not in self.symbol_table["global"]["functions"] and
                    func_name not in self.symbol_table["global"]["classes"] and
                    not self._is_builtin(func_name)):
                    
                    # 添加未定义函数错误
                    self._add_error(
                        line=node.func.lineno,
                        column=node.func.col_offset + 1,
                        end_line=node.func.lineno,
                        end_column=node.func.col_offset + 1 + len(func_name),
                        error_type="undefined-function",
                        error_message=f"未定义的函数或类调用 '{func_name}'"
                    )
    
    def _is_builtin(self, symbol_name: str) -> bool:
        """
        检查符号是否为内置符号
        
        Args:
            symbol_name: 符号名称
            
        Returns:
            如果是内置符号返回True，否则返回False
        """
        # Python内置函数、关键字和特殊变量
        python_builtins = {
            # 内置函数
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
        }
        
        return symbol_name in python_builtins