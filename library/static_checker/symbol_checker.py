"""
符号定义检查器
用于检查函数、类、变量等标识符的定义与引用关系
包含工厂模式和管理器功能
"""

from typing import List, Optional, Dict, Set, Type
from tkinter import Toplevel, Label, Button, Frame
from library.static_checker.base import BaseStaticChecker, StaticCheckError
import ast
import re
import os
import json
import time


class SymbolChecker(BaseStaticChecker):
    """
    符号定义检查器
    检查函数、类、变量等标识符的定义与引用关系
    """

    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", "c", "cpp",
        "csharp", "go", "ruby", "php"
    ]

    LANGUAGE_EXTENSIONS = {
        "javascript": [".js"],
        "typescript": [".ts", ".tsx"],
        "python": [".py", ".pyw"],
        "java": [".java"],
        "c": [".c"],
        "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
        "csharp": [".cs"],
        "go": [".go"],
        "ruby": [".rb"],
        "php": [".php"],
    }

    def __init__(self, language: str, editor_widget=None):
        super().__init__(language, editor_widget)

        self.symbol_table: Dict[str, Dict] = {
            "global": {
                "variables": set(),
                "functions": set(),
                "classes": set()
            },
            "functions": {}
        }

        self.supported_languages = self.SUPPORTED_LANGUAGES

        self._flake8_cache = {}
        self._flake8_cache_timeout = 5
        self._last_flake8_call = 0

    def check(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        self.clear_errors()

        if self.language not in self.supported_languages:
            return self.get_errors()

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
        try:
            print(f"使用flake8检查Python代码，代码长度: {len(code)}")

            import subprocess
            import tempfile

            code_hash = hash(code)
            current_time = time.time()

            if code_hash in self._flake8_cache and \
               (current_time - self._flake8_cache[code_hash]['timestamp'] < self._flake8_cache_timeout):
                print(f"使用缓存的flake8结果")
                self.errors = self._flake8_cache[code_hash]['errors'].copy()
                return self.get_errors()

            code_lines = code.split('\n')

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file_path = f.name

            try:
                result = subprocess.run(
                    ["flake8",
                     "--format", "%(row)d,%(col)d,%(code)s,%(text)s",
                     temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=3
                )

                print(f"flake8返回码: {result.returncode}")
                print(f"flake8输出: {result.stdout}")
                print(f"flake8错误: {result.stderr}")

                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self._parse_flake8_output(line, code_lines)

            finally:
                os.unlink(temp_file_path)

            print(f"flake8检查完成，错误数量: {len(self.errors)}")

            self._flake8_cache[code_hash] = {
                'timestamp': current_time,
                'errors': self.errors.copy()
            }

            if len(self._flake8_cache) > 10:
                oldest_key = min(self._flake8_cache.keys(),
                               key=lambda k: self._flake8_cache[k]['timestamp'])
                del self._flake8_cache[oldest_key]
                print(f"移除最旧的flake8缓存项，当前缓存大小: {len(self._flake8_cache)}")

        except subprocess.TimeoutExpired:
            print("flake8检查超时")
        except Exception as e:
            print(f"flake8检查错误: {str(e)}")
            import traceback
            traceback.print_exc()

        return self.get_errors()

    def _parse_flake8_output(self, output_line: str, code_lines: list):
        try:
            parts = output_line.split(',')
            if len(parts) < 4:
                return

            line = int(parts[0])
            column = int(parts[1])
            error_code = parts[2]
            error_message = ','.join(parts[3:])

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

            end_line = line
            end_column = column

            if 1 <= line <= len(code_lines):
                line_content = code_lines[line - 1]

                if error_code.startswith('E2') or error_code.startswith('E7'):
                    end_column = column + 1
                elif error_code.startswith('E5'):
                    end_column = len(line_content)
                elif error_code.startswith('F'):
                    if column < len(line_content):
                        for i in range(column, len(line_content)):
                            if not (line_content[i].isalnum() or line_content[i] == '_'):
                                end_column = i
                                break
                        else:
                            end_column = len(line_content)
                else:
                    end_column = column + 1

            end_column = min(end_column, len(code_lines[line - 1])) if 1 <= line <= len(code_lines) else column + 1

            self._add_error(
                line=line,
                column=column + 1,
                end_line=end_line,
                end_column=end_column + 1,
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
        self.symbol_table = {
            "global": {
                "variables": set(),
                "functions": set(),
                "classes": set()
            },
            "functions": {}
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.symbol_table["global"]["functions"].add(node.name)

                func_params = set()
                for arg in node.args.args:
                    func_params.add(arg.arg)
                if node.args.vararg:
                    func_params.add(node.args.vararg.arg)
                if node.args.kwarg:
                    func_params.add(node.args.kwarg.arg)
                for kwarg in node.args.kwonlyargs:
                    func_params.add(kwarg.arg)

                self.symbol_table["functions"][node.name] = func_params
            elif isinstance(node, ast.ClassDef):
                self.symbol_table["global"]["classes"].add(node.name)

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name
                        self.symbol_table["global"]["functions"].add(method_name)

                        method_params = set()
                        for arg in item.args.args:
                            method_params.add(arg.arg)
                        if item.args.vararg:
                            method_params.add(item.args.vararg.arg)
                        if item.args.kwarg:
                            method_params.add(item.args.kwarg.arg)
                        for kwarg in item.args.kwonlyargs:
                            method_params.add(kwarg.arg)

                        self.symbol_table["functions"][method_name] = method_params
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                self.symbol_table["global"]["variables"].add(node.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        self.symbol_table["global"]["variables"].add(alias.asname)
                    else:
                        self.symbol_table["global"]["variables"].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname:
                        self.symbol_table["global"]["variables"].add(alias.asname)
                    else:
                        self.symbol_table["global"]["variables"].add(alias.name)

    def _check_python_symbol_references(self, tree: ast.AST):
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                symbol_name = node.id

                if isinstance(node.ctx, ast.Load):
                    print(f"检查符号引用: {symbol_name}, 位置: {node.lineno}:{node.col_offset}")

                    in_symbol_table = (
                        symbol_name in self.symbol_table["global"]["variables"] or
                        symbol_name in self.symbol_table["global"]["functions"] or
                        symbol_name in self.symbol_table["global"]["classes"] or
                        self._is_builtin(symbol_name)
                    )

                    print(f"符号 '{symbol_name}' 在符号表中: {in_symbol_table}")

                    if not in_symbol_table:
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
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    print(f"检查函数调用: {func_name}, 位置: {node.func.lineno}:{node.func.col_offset}")

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
        builtins_map = {
            "python": {
                "print", "input", "len", "range", "type", "int", "float",
                "str", "bool", "list", "dict", "set", "tuple", "lambda",
                "zip", "map", "filter", "enumerate", "reversed", "sorted",
                "sum", "max", "min", "abs", "round", "pow", "divmod",
                "all", "any", "isinstance", "issubclass", "id", "hex",
                "oct", "bin", "chr", "ord", "ascii", "repr", "eval",
                "exec", "compile", "open", "close", "file",
                "if", "else", "elif", "for", "while", "try", "except",
                "finally", "with", "break", "continue", "return", "def",
                "class", "async", "await", "import", "from",
                "as", "global", "nonlocal", "pass", "yield", "del",
                "assert", "raise", "in", "not", "and", "or", "is",
                "True", "False", "None",
                "__name__", "__file__", "__doc__", "__package__", "__init__",
                "__str__", "__repr__", "__dict__", "__class__", "__module__",
            },
            "javascript": {
                "console", "log", "alert", "prompt", "confirm", "document", "window",
                "Math", "Date", "Array", "Object", "String", "Number", "Boolean",
                "Function", "RegExp", "JSON", "Promise", "async", "await", "let", "const",
                "var", "if", "else", "for", "while", "do", "switch", "case", "default",
                "break", "continue", "return", "function", "class", "extends", "super",
                "this", "new", "delete", "typeof", "instanceof", "in",
                "null", "undefined", "true", "false", "try", "catch", "finally", "throw",
                "export", "import", "from", "as"
            },
            "typescript": {
                "console", "log", "alert", "prompt", "confirm", "document", "window",
                "Math", "Date", "Array", "Object", "String", "Number", "Boolean",
                "Function", "RegExp", "JSON", "Promise", "async", "await", "let", "const",
                "var", "if", "else", "for", "while", "do", "switch", "case", "default",
                "break", "continue", "return", "function", "class", "extends", "super",
                "this", "new", "delete", "typeof", "instanceof", "in",
                "null", "undefined", "true", "false", "try", "catch", "finally", "throw",
                "export", "import", "from", "as", "interface", "type", "enum", "any", "void",
            },
            "java": {
                "System", "out", "println", "print", "Scanner", "String", "Integer", "Double",
                "Math", "Random", "ArrayList", "HashMap", "if", "else", "for", "while",
                "break", "continue", "return", "public", "private", "protected", "static",
                "final", "class", "interface", "extends", "implements", "new", "this", "void",
                "int", "double", "float", "long", "short", "byte", "boolean", "char"
            },
            "c": {
                "printf", "scanf", "malloc", "free", "strlen", "strcmp",
                "if", "else", "for", "while", "do", "switch", "case", "default", "break",
                "continue", "return", "void", "int", "double", "float", "long", "short",
                "char", "unsigned", "const", "static", "extern", "struct", "union", "enum"
            },
            "cpp": {
                "cout", "cin", "endl", "printf", "scanf", "malloc", "free",
                "if", "else", "for", "while", "do", "switch", "case", "default", "break",
                "continue", "return", "void", "int", "double", "float", "long", "short",
                "char", "class", "public", "private", "protected", "virtual", "namespace",
                "new", "delete", "this", "try", "catch", "throw", "nullptr"
            },
            "csharp": {
                "Console", "Write", "WriteLine", "String", "Int32", "Double",
                "if", "else", "for", "while", "do", "switch", "case", "default", "break",
                "continue", "return", "public", "private", "protected", "static", "class",
                "void", "int", "double", "true", "false", "null", "try", "catch"
            },
            "go": {
                "fmt", "Print", "Println", "Printf", "log", "os", "json",
                "if", "else", "for", "switch", "case", "default", "break", "continue",
                "return", "func", "var", "const", "type", "struct", "interface", "map",
                "true", "false", "nil"
            },
            "ruby": {
                "puts", "print", "gets", "require", "module", "class",
                "def", "if", "else", "elsif", "end", "for", "while", "do", "break",
                "return", "true", "false", "nil", "self", "new"
            },
            "php": {
                "echo", "print", "printf", "require", "include", "if", "else", "elseif",
                "for", "foreach", "while", "do", "switch", "case", "default", "function",
                "class", "extends", "new", "public", "private", "protected", "true", "false", "null"
            }
        }

        current_builtins = builtins_map.get(self.language, set())
        return symbol_name in current_builtins

    def _check_javascript_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_java_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_c_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_csharp_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_go_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_ruby_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()

    def _check_php_code(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        return self.get_errors()


class StaticCheckerFactory:
    def __init__(self):
        self._checkers: Dict[str, List[Type[BaseStaticChecker]]] = {}
        self._language_to_extensions: Dict[str, List[str]] = {}

        self._register_default_checkers()
        self._register_default_language_mappings()

    def _register_default_checkers(self):
        symbol_checker_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp",
            "csharp", "go", "ruby", "php"
        ]

        for lang in symbol_checker_languages:
            self.register_checker(lang, SymbolChecker)

    def _register_default_language_mappings(self):
        self._language_to_extensions = SymbolChecker.LANGUAGE_EXTENSIONS.copy()

    def register_checker(self, language: str, checker_class: Type[BaseStaticChecker]):
        if language not in self._checkers:
            self._checkers[language] = []

        if checker_class not in self._checkers[language]:
            self._checkers[language].append(checker_class)

    def register_language_extension(self, language: str, extension: str):
        if language not in self._language_to_extensions:
            self._language_to_extensions[language] = []

        if extension not in self._language_to_extensions[language]:
            self._language_to_extensions[language].append(extension)

    def get_language_from_file(self, file_path: str) -> Optional[str]:
        _, ext = os.path.splitext(file_path)

        for lang, extensions in self._language_to_extensions.items():
            if ext in extensions:
                return lang

        return None

    def create_checkers(self, language: str, editor_widget=None) -> List[BaseStaticChecker]:
        checkers = []

        if language in self._checkers:
            for checker_class in self._checkers[language]:
                checkers.append(checker_class(language, editor_widget))

        return checkers

    def create_checkers_for_file(self, file_path: str, editor_widget=None) -> List[BaseStaticChecker]:
        language = self.get_language_from_file(file_path)
        if language:
            return self.create_checkers(language, editor_widget)
        return []

    def get_supported_languages(self) -> List[str]:
        return list(self._checkers.keys())

    def get_supported_extensions(self) -> List[str]:
        extensions = []
        for exts in self._language_to_extensions.values():
            extensions.extend(exts)
        return list(set(extensions))


class StaticCheckManager:
    def __init__(self):
        self.checker_factory = StaticCheckerFactory()
        self._current_errors: Dict[str, List[StaticCheckError]] = {}
        self._editor_mappings = {}
        self.flake8_tree = None

        self._error_theme = self._load_error_theme()

        self._editor_tooltips = {}

    def set_flake8_tree(self, tree_widget):
        """设置flake8结果表格组件"""
        self.flake8_tree = tree_widget

    def _cleanup_editor_resources(self, editor_widget):
        try:
            if hasattr(editor_widget, "_tooltip") and editor_widget._tooltip:
                try:
                    editor_widget._tooltip.destroy()
                except Exception:
                    pass
                finally:
                    editor_widget._tooltip = None

            if hasattr(editor_widget, "tag_names"):
                for tag in editor_widget.tag_names():
                    if tag == "error" or tag == "warning" or tag.startswith("error_"):
                        editor_widget.tag_remove(tag, "1.0", "end")
        except Exception as e:
            print(f"清理编辑器资源失败: {str(e)}")

    def _load_error_theme(self):
        try:
            from pathlib import Path

            theme_dir = Path(__file__).parent.parent.parent / "asset" / "theme"
            theme_file = theme_dir / "vscode-dark.json"

            if not theme_file.exists():
                print(f"主题文件未找到: {theme_file}")
                return self._get_default_error_theme()

            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_config = json.load(f)

            error_theme = {}
            error_theme['error_color'] = theme_config.get('error', '#F44747')
            error_theme['warning_color'] = theme_config.get('warning', '#DDB100')
            error_theme['error_background'] = theme_config.get('error_background', '#FFEBEB')

            print(f"加载错误主题配置: {error_theme}")
            return error_theme

        except Exception as e:
            print(f"加载错误主题失败: {str(e)}")
            return self._get_default_error_theme()

    def _get_default_error_theme(self):
        return {
            'error_color': '#F44747',
            'warning_color': '#DDB100',
            'error_background': '#FFEBEB'
        }

    def register_editor(self, editor_widget, file_path: str | None = None):
        self._editor_mappings[editor_widget] = file_path

    def unregister_editor(self, editor_widget):
        if editor_widget in self._editor_mappings:
            del self._editor_mappings[editor_widget]

    def update_file_path(self, editor_widget, file_path: str):
        if editor_widget in self._editor_mappings:
            self._editor_mappings[editor_widget] = file_path

    def check_code(self, code: str, file_path: Optional[str] = None, editor_widget=None) -> List[StaticCheckError]:
        print(f"静态检查开始，文件路径: {file_path}, 代码长度: {len(code)}")
        language = self.checker_factory.get_language_from_file(file_path) if file_path else None

        print(f"检测到的语言: {language}")

        if not language:
            print("无法从文件路径确定语言，使用默认语言Python")
            language = "python"

        checkers = self.checker_factory.create_checkers(language, editor_widget)
        print(f"创建的检查器数量: {len(checkers)}, 检查器类型: {[type(c).__name__ for c in checkers]}")

        all_errors = []

        for checker in checkers:
            print(f"执行检查器: {type(checker).__name__}")
            errors = checker.check(code, file_path)
            print(f"检查器返回的错误数量: {len(errors)}")
            all_errors.extend(errors)

        print(f"所有检查器完成，总错误数量: {len(all_errors)}")

        if file_path:
            self._current_errors[file_path] = all_errors

        if editor_widget:
            print(f"更新编辑器错误显示，错误数量: {len(all_errors)}")
            self._update_editor_errors(editor_widget, all_errors)

        if self.flake8_tree:
            self._update_flake8_tree(all_errors)

        return all_errors

    def _update_flake8_tree(self, errors: List[StaticCheckError]):
        """更新flake8结果表格"""
        print(f"更新flake8结果表格，错误数量: {len(errors)}")
        
        try:
            for item in self.flake8_tree.get_children():
                self.flake8_tree.delete(item)
            
            for error in errors:
                icon = "❌" if error.severity == "error" else "⚠️"
                self.flake8_tree.insert("", "end", values=(
                    icon,
                    error.line,
                    error.column,
                    error.error_type,
                    error.error_message
                ))
            
            error_count = len(errors)
            error_text = f"{error_count} 个问题"
            
            if hasattr(self.flake8_tree, 'master') and hasattr(self.flake8_tree.master.master, 'error_count_label'):
                try:
                    self.flake8_tree.master.master.error_count_label.config(text=error_text)
                except Exception:
                    pass
            
            print(f"flake8表格更新完成")
        except Exception as e:
            print(f"更新flake8表格失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _update_editor_errors(self, editor_widget, errors: List[StaticCheckError]):
        print(f"更新编辑器错误显示，错误数量: {len(errors)}")

        try:
            for tag in editor_widget.tag_names():
                if tag.startswith("error_marker_") or tag == "error_line" or tag == "warning_line":
                    editor_widget.tag_remove(tag, "1.0", "end")

            editor_widget.tag_remove("error", "1.0", "end")
            editor_widget.tag_remove("warning", "1.0", "end")

            self._hide_error_popup()

            if not errors:
                print("没有错误需要标记")
                return

            line_errors = {}
            for error in errors:
                if error.line not in line_errors:
                    line_errors[error.line] = []
                line_errors[error.line].append(error)

            for line_num, line_errors_list in line_errors.items():
                self._add_error_marker(editor_widget, line_num, line_errors_list)

        except Exception as e:
            print(f"更新编辑器错误显示失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _add_error_marker(self, editor_widget, line_num: int, errors: List[StaticCheckError]):
        """在行末添加错误标记"""
        try:
            line_content = editor_widget.get(f"{line_num}.0", f"{line_num}.end")
            line_len = len(line_content)

            marker_pos = f"{line_num}.{line_len}"

            error_count = len(errors)
            error_count_text = str(error_count)

            is_error = any(e.severity == "error" for e in errors)
            tag = "error" if is_error else "warning"
            bg_color = self._error_theme['error_color'] if is_error else self._error_theme['warning_color']

            editor_widget.tag_configure(tag,
                                        underline=True,
                                        foreground=bg_color)

            marker_tag = f"error_marker_{line_num}"
            editor_widget.tag_configure(marker_tag,
                                        background=bg_color,
                                        foreground="white")

            editor_widget.tag_add(marker_tag, marker_pos, marker_pos + " lineend")

            editor_widget.tag_bind(marker_tag, "<Button-1>", 
                lambda e, ln=line_num, errs=errors: self._show_error_popup(e, editor_widget, ln, errs))

        except Exception as e:
            print(f"添加错误标记失败: {str(e)}")

    def _show_error_popup(self, event, editor_widget, line_num: int, errors: List[StaticCheckError]):
        """显示错误详情弹出窗口"""
        try:
            self._hide_error_popup()

            popup = Toplevel(editor_widget)
            popup.wm_overrideredirect(True)

            x = event.x_root + 10
            y = event.y_root + 10
            popup.wm_geometry(f"+{x}+{y}")

            popup.configure(background="#2d2d2d")

            is_error = any(e.severity == "error" for e in errors)
            header_bg = self._error_theme['error_color'] if is_error else self._error_theme['warning_color']

            header_frame = Frame(popup, background=header_bg, padx=10, pady=5)
            header_frame.pack(fill="x")

            title_text = f"错误 ({len(errors)})" if is_error else f"警告 ({len(errors)})"
            title_label = Label(header_frame, text=title_text, background=header_bg, foreground="white", font=("Arial", 10, "bold"))
            title_label.pack(side="left")

            close_btn = Button(header_frame, text="✕", background=header_bg, foreground="white",
                            borderwidth=0, font=("Arial", 10), cursor="hand2",
                            command=lambda: self._hide_error_popup())
            close_btn.pack(side="right")

            content_frame = Frame(popup, background="#2d2d2d", padx=10, pady=5)
            content_frame.pack(fill="both", expand=True)

            for error in errors:
                error_label = Label(content_frame, 
                                 text=f"• {error.error_message}",
                                 background="#2d2d2d", 
                                 foreground="#ffffff",
                                 font=("Arial", 9),
                                 wraplength=300,
                                 justify="left",
                                 anchor="w")
                error_label.pack(anchor="w", pady=2)

            self._error_popup = popup
            popup.bind("<Leave>", lambda e: self._hide_error_popup())

        except Exception as e:
            print(f"显示错误弹出窗口失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _hide_error_popup(self):
        """隐藏错误弹出窗口"""
        if hasattr(self, '_error_popup') and self._error_popup:
            try:
                self._error_popup.destroy()
            except Exception:
                pass
            self._error_popup = None

    def _show_simple_tooltip(self, event, editor_widget, error):
        try:
            self._hide_simple_tooltip(event, editor_widget)

            from tkinter import Toplevel, Label

            tooltip = Toplevel(editor_widget)
            tooltip.wm_overrideredirect(True)

            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")

            message = f"{error.error_type}: {error.error_message}"
            label = Label(tooltip, text=message,
                         background="#fff3cd",
                         foreground="#856404",
                         borderwidth=1,
                         relief="solid",
                         padx=5,
                         pady=3,
                         font=("Arial", 10))
            label.pack()

            editor_widget._tooltip = tooltip
            print(f"显示简单提示: {message}")
        except Exception as e:
            print(f"显示提示失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _hide_simple_tooltip(self, event, editor_widget):
        try:
            if hasattr(editor_widget, "_tooltip") and editor_widget._tooltip:
                editor_widget._tooltip.destroy()
                editor_widget._tooltip = None
                print("隐藏简单提示")
        except Exception as e:
            print(f"隐藏提示失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _clear_editor_errors(self, editor_widget):
        print("清除编辑器中的所有错误标记")
        try:
            editor_widget.tag_remove("error", "1.0", "end")
            editor_widget.tag_remove("warning", "1.0", "end")
            editor_widget.tag_remove("static_check_error", "1.0", "end")

            for tag in editor_widget.tag_names():
                if tag.startswith("error_"):
                    editor_widget.tag_remove(tag, "1.0", "end")

            if hasattr(editor_widget, "_tooltip") and editor_widget._tooltip:
                try:
                    editor_widget._tooltip.destroy()
                except:
                    pass
                finally:
                    editor_widget._tooltip = None

            print("成功清除错误标记")
        except Exception as e:
            print(f"清除编辑器错误标记失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_current_errors(self, file_path: Optional[str] = None) -> List[StaticCheckError]:
        if file_path:
            return self._current_errors.get(file_path, [])
        return []

    def get_supported_languages(self) -> List[str]:
        return self.checker_factory.get_supported_languages()

    def get_supported_extensions(self) -> List[str]:
        return self.checker_factory.get_supported_extensions()
