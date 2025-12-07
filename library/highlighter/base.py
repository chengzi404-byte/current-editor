import ast
from typing import Tuple, Optional
import tokenize
import io
import keyword
import builtins
import re
import json
from pathlib import Path

class BaseHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # Initlaze normal syntax colors
        self.syntax_colors = {
            "keyword": "#569CD6",
            "control": "#C586C0",
            "operator": "#D4D4D4",
            "punctuation": "#D4D4D4",
            "class": "#4EC9B0",
            "function": "#DCDCAA",
            "method": "#DCDCAA",
            "variable": "#9CDCFE",
            "parameter": "#9CDCFE",
            "property": "#9CDCFE",
            "string": "#CE9178",
            "number": "#B5CEA8",
            "boolean": "#569CD6",
            "null": "#569CD6",
            "constant": "#4FC1FF",
            "comment": "#6A9955",
            "docstring": "#6A9955",
            "todo": "#FF8C00",
            "decorator": "#C586C0",
            "builtin": "#4EC9B0",
            "self": "#569CD6",
            "namespace": "#4EC9B0",
            "type": "#4EC9B0",
            "type_annotation": "#4EC9B0",
            "interface": "#4EC9B0"
        }
        
        self.setup_tags()
        self._setup_bindings()
        
        # Highlight delay config
        self._highlight_pending = False
        self._last_change_time = 0
        self._highlight_delay = 50  # Lower delay
        self._last_content = ""     # Add content cache
        
        # Auto pairs
        self.auto_pairs = {
            '"': '"',
            "'": "'",
            '(': ')',
            '[': ']',
            '{': '}',
            '"""': '"""',
            "'''": "'''"
        }
        
        # Basic keyword list
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(builtins))
        
        # Class names collection for class reference highlighting
        self.class_names = set()
        
        # Languange keywords
        self.language_keywords = {
            'control': {'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'finally', 'with', 'break', 'continue', 'return'},
            'definition': {'def', 'class', 'lambda', 'async', 'await'},
            'module': {'import', 'from', 'as'},
            'value': {'True', 'False', 'None'},
            'context': {'global', 'nonlocal', 'pass', 'yield'}
        }
        
    def setup_tags(self):
        """Configure all syntax highlighting tags"""
        for tag, color in self.syntax_colors.items():
            self.text_widget.tag_configure(tag, foreground=color)
            
    def _setup_bindings(self):
        """Set up event bindings"""
        self.text_widget.bind('<<Modified>>', self._on_text_change)
        self.text_widget.bind('<KeyRelease>', self._on_key_release)
        self.text_widget.bind('(', self._handle_open_parenthesis)  # 绑定左括号
        self.text_widget.bind('<Return>', self._handle_return_key)  # 绑定回车键
        self.text_widget.bind('<Tab>', self._handle_tab_key)  # 绑定Tab键
        
    def _on_text_change(self, event=None):
        """Handle text modification events"""
        if self.text_widget.edit_modified():
            self.text_widget.edit_modified(False)
            self._queue_highlight()
            
    def _on_key_release(self, event=None):
        """Handle key release events"""
        if event and event.keysym in ('Return', 'BackSpace', 'Delete'):
            self._queue_highlight()
            
    def _queue_highlight(self):
        """Queue highlight task"""
        if not self._highlight_pending:
            self._highlight_pending = True
            self.text_widget.after(self._highlight_delay, self._delayed_highlight)
            
    def _delayed_highlight(self):
        """Execute highlighting with delay"""
        try:
            current_content = self.text_widget.get("1.0", "end-1c")
            # Highlight when content changed
            if current_content != self._last_content:
                self.highlight()
                self._last_content = current_content
        except Exception as e:
            print(f"Highlight failed: {str(e)}")
        finally:
            self._highlight_pending = False
            
    def _add_tag(self, tag: str, start: str, end: str):
        """Add syntax highlighting tag with performance optimization"""
        try:
            # Batch tag operations for better performance
            if not hasattr(self, '_tag_batch'):
                self._tag_batch = {}
            
            if tag not in self._tag_batch:
                self._tag_batch[tag] = []
            
            self._tag_batch[tag].append((start, end))
            
            # Flush batch when it reaches a certain size
            if len(self._tag_batch[tag]) >= 50:
                self._flush_tag_batch(tag)
                
        except Exception as e:
            print(f"Add tag error - tag: {tag}, start: {start}, end: {end}, err: {str(e)}")
    
    def _flush_tag_batch(self, tag: str):
        """Flush batched tag operations"""
        if hasattr(self, '_tag_batch') and tag in self._tag_batch:
            for start, end in self._tag_batch[tag]:
                try:
                    self.text_widget.tag_add(tag, start, end)
                except Exception as e:
                    print(f"Batch add tag error: {str(e)}")
            self._tag_batch[tag] = []
    
    def _flush_all_tag_batches(self):
        """Flush all batched tag operations"""
        if hasattr(self, '_tag_batch'):
            for tag in self._tag_batch:
                self._flush_tag_batch(tag)

    def highlight(self):
        """Perform syntax highlighting with performance optimization"""
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
            
            # Initialize tag batch
            self._tag_batch = {}
            
            # Process comments and strings
            self._highlight_comments_and_strings(text)
            
            try:
                tree = ast.parse(text)
                self._process_ast(tree)
            except SyntaxError:
                self._basic_highlight(text)
            
            # Flush any remaining batched tag operations
            self._flush_all_tag_batches()
            
            # Backup
            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"Highlight failed: {str(e)}")
            # Fallback to basic highlighting
            # Ensure text is defined before using it
            if 'text' in locals() or 'text' in globals():
                self._basic_highlight(text)
            else:
                # If text is not defined, get it from the widget
                text = self.text_widget.get("1.0", "end-1c")
                self._basic_highlight(text)

    def _basic_highlight(self, text: str):
        """Basic highlighting when syntax errors occur"""
        try:
            import re
            
            # Split words into lines
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Highlight keywords
                for keyword in self.keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    for match in re.finditer(pattern, line):
                        start = f"{line_num}.{match.start()}"
                        end = f"{line_num}.{match.end()}"
                        self._add_tag("keyword", start, end)
                        
                # Highlight strings
                string_pattern = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
                for match in re.finditer(string_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("string", start, end)
                    
                # Highlight numbers
                number_pattern = r'\b\d+(\.\d+)?\b'
                for match in re.finditer(number_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("number", start, end)
                    
                # Highlight comments
                comment_pattern = r'#.*$'
                for match in re.finditer(comment_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self._add_tag("comment", start, end)
                    
        except Exception as e:
            print(f"Basic highlight failed: {str(e)}")
            
    def _clear_tags(self):
        """Remove all syntax highlighting tags"""
        try:
            for tag in self.syntax_colors.keys():
                self.text_widget.tag_remove(tag, "1.0", "end")
        except Exception as e:
            print(f"Clear tag error: {str(e)}")
            
    def _highlight_comments_and_strings(self, text: str):
        """Highlight comments and strings with performance optimization"""
        try:
            # Pre-compile regex pattern for better performance
            triple_quote_pattern = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')')
            
            # Process multi-line strings first
            for match in triple_quote_pattern.finditer(text):
                start_pos = match.start()
                end_pos = match.end()
                
                # Calculate line and column positions efficiently
                start_line = text.count('\n', 0, start_pos) + 1
                start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
                
                end_line = text.count('\n', 0, end_pos) + 1
                end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
                
                start = f"{start_line}.{start_col}"
                end = f"{end_line}.{end_col}"
                self._add_tag("docstring", start, end)
            
            # Process single-line tokens using tokenize module
            # Use a single tokenize call for the entire text for better performance
            try:
                tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
                for token in tokens:
                    token_type = token.type
                    token_string = token.string
                    start_line, start_col = token.start
                    end_line, end_col = token.end
                    
                    # Skip tokens that are part of multi-line strings (already processed)
                    if token_type == tokenize.STRING and (token_string.startswith('"""') or token_string.startswith("\'\'\'")):
                        continue
                        
                    start = f"{start_line}.{start_col}"
                    end = f"{end_line}.{end_col}"
                    
                    if token_type == tokenize.COMMENT:
                        self._add_tag("comment", start, end)
                    elif token_type == tokenize.STRING:
                        self._add_tag("string", start, end)
                    elif token_type == tokenize.NUMBER:
                        self._add_tag("number", start, end)
                    elif token_type == tokenize.OP:
                        self._add_tag("operator", start, end)
                        
            except tokenize.TokenError:
                # Fallback to line-by-line processing for malformed code
                self._basic_highlight(text)
                
        except Exception as e:
            print(f"Comment and strings highlight error: {str(e)}")

    def _process_ast(self, tree: ast.AST):
        """Process AST tree with performance optimization"""
        # Class names collection for class reference highlighting
        self.class_names = set()
        
        # Build parent map and collect class names in a single pass
        self._parent_map = {}
        
        # Use a more efficient AST traversal
        for node in ast.walk(tree):
            # Collect class names
            if isinstance(node, ast.ClassDef):
                self.class_names.add(node.name)
            
            # Build parent map
            for child in ast.iter_child_nodes(node):
                self._parent_map[child] = node
                
        # Highlight nodes with batched operations
        self._highlight_nodes_batch(tree)
    
    def _highlight_nodes_batch(self, tree: ast.AST):
        """Highlight AST nodes in batches for better performance"""
        # Group nodes by type for batch processing
        nodes_by_type = {}
        
        for node in ast.walk(tree):
            node_type = type(node)
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        # Process nodes in batches for better cache locality
        for node_type, nodes in nodes_by_type.items():
            for node in nodes:
                self._highlight_node(node)

    def _get_parent_node(self, node: ast.AST) -> Optional[ast.AST]:
        """Get parent node of the given node"""
        return self._parent_map.get(node)
            
    def _highlight_node(self, node: ast.AST):
        """Highlight specific AST node"""
        # 使用getattr安全地检查lineno属性
        lineno = getattr(node, 'lineno', None)
        if lineno is None:
            return
        
        start, end = self.get_position(node)
        
        # Process different nodes
        if isinstance(node, ast.ClassDef):
            self._highlight_class_def(node, start, end)
        elif isinstance(node, ast.FunctionDef):
            self._highlight_function_def(node, start, end)
        elif isinstance(node, ast.Name):
            self._highlight_name(node, start, end)
        elif isinstance(node, ast.Call):
            self._highlight_call(node)
        elif isinstance(node, ast.Constant):
            self._highlight_constant(node, start, end)
        elif isinstance(node, ast.arg):
            self._highlight_arg(node, start, end)
        elif isinstance(node, ast.AnnAssign):
            self._highlight_annotation(node)
        elif isinstance(node, ast.Import):
            self._highlight_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._highlight_import_from(node)
        elif isinstance(node, ast.Attribute):
            self._highlight_attribute(node)
        elif isinstance(node, ast.Assign):
            self._highlight_assignment(node)
        elif isinstance(node, ast.BinOp):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.Compare):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.BoolOp):
            self._highlight_bool_op(node)
        elif isinstance(node, ast.UnaryOp):
            self._highlight_operator(node, start, end)
        elif isinstance(node, ast.If):
            self._highlight_if_statement(node)
        elif isinstance(node, ast.For):
            self._highlight_for_statement(node)
        elif isinstance(node, ast.While):
            self._highlight_while_statement(node)
        elif isinstance(node, ast.Try):
            self._highlight_try_statement(node)
        elif isinstance(node, ast.With):
            self._highlight_with_statement(node)

    def _highlight_class_def(self, node: ast.ClassDef, start: str, end: str):
        """Highlight class definition"""
        # 使用getattr安全地访问属性
        lineno = getattr(node, 'lineno', 1)
        col_offset = getattr(node, 'col_offset', 0)
        
        # Class keyword
        keyword_end = f"{lineno}.{col_offset + 5}"
        self._add_tag("keyword", start, keyword_end)
        
        # Class name
        name_start = f"{lineno}.{col_offset + 6}"
        name_end = f"{lineno}.{col_offset + 6 + len(node.name)}"
        self._add_tag("class", name_start, name_end)
        
        # Base class
        for base in node.bases:
            base_start, base_end = self.get_position(base)
            self._add_tag("class", base_start, base_end)

    def _highlight_function_def(self, node: ast.FunctionDef, start: str, end: str):
        """Highlight function definition"""
        # 使用getattr安全地访问属性
        lineno = getattr(node, 'lineno', 1)
        col_offset = getattr(node, 'col_offset', 0)
        
        # Def keyword
        keyword_end = f"{lineno}.{col_offset + 3}"
        self._add_tag("keyword", start, keyword_end)
        
        # Name highlight
        name_start = f"{lineno}.{col_offset + 4}"
        name_end = f"{lineno}.{col_offset + 4 + len(node.name)}"
        # Check
        if node.name.startswith('__') and node.name.endswith('__'):
            self._add_tag("method", name_start, name_end)
        else:
            self._add_tag("function", name_start, name_end)
        
        # Decorator highlight
        for decorator in node.decorator_list:
            dec_start, dec_end = self.get_position(decorator)
            self._add_tag("decorator", dec_start, dec_end)
        
        # Argument highlight
        for arg in node.args.args:
            arg_start, arg_end = self.get_position(arg)
            self._add_tag("parameter", arg_start, arg_end)

            if arg.annotation:
                ann_start, ann_end = self.get_position(arg.annotation)
                self._add_tag("type_annotation", ann_start, ann_end)

    def _highlight_import(self, node: ast.Import):
        """Highlight import statements"""
        # 使用getattr安全地访问属性
        lineno = getattr(node, 'lineno', 1)
        col_offset = getattr(node, 'col_offset', 0)
        
        # Highlight 'import' keyword
        import_start = f"{lineno}.{col_offset}"
        import_end = f"{lineno}.{col_offset + 6}"  # "import" has 6 characters
        self._add_tag("keyword", import_start, import_end)
        
        for alias in node.names:
            alias_lineno = getattr(alias, 'lineno', None)
            alias_col_offset = getattr(alias, 'col_offset', None)
            if alias_lineno is not None and alias_col_offset is not None:
                start = f"{alias_lineno}.{alias_col_offset}"
                end = f"{alias_lineno}.{alias_col_offset + len(alias.name)}"
                self._add_tag("namespace", start, end)
                if alias.asname:
                    as_start = f"{alias_lineno}.{alias_col_offset + len(alias.name) + 4}"
                    as_end = f"{alias_lineno}.{alias_col_offset + len(alias.name) + 4 + len(alias.asname)}"
                    self._add_tag("variable", as_start, as_end)

    def _highlight_import_from(self, node: ast.ImportFrom):
        """Highlight from-import statements"""
        try:
            # 使用getattr安全地访问属性
            lineno = getattr(node, 'lineno', 1)
            col_offset = getattr(node, 'col_offset', 0)
            
            # Highlight 'from' keyword
            from_start = f"{lineno}.{col_offset}"
            from_end = f"{lineno}.{col_offset + 4}"
            self._add_tag("keyword", from_start, from_end)
            
            # Highlight module name or relative path
            if node.module:
                # Absolute import: from module import ...
                module_start = f"{lineno}.{col_offset + 5}"
                module_end = f"{lineno}.{col_offset + 5 + len(node.module)}"
                self._add_tag("namespace", module_start, module_end)
            elif node.level > 0:
                # Relative import: from .. import ...
                dots = "." * node.level
                dots_start = f"{lineno}.{col_offset + 5}"
                dots_end = f"{lineno}.{col_offset + 5 + len(dots)}"
                self._add_tag("namespace", dots_start, dots_end)
            
            # Highlight 'import' keyword
            import_pos = self._find_import_keyword_position(node)
            if import_pos:
                import_start, import_end = import_pos
                self._add_tag("keyword", import_start, import_end)
            
            # Highlight imported names
            for alias in node.names:
                alias_lineno = getattr(alias, 'lineno', None)
                alias_col_offset = getattr(alias, 'col_offset', None)
                if alias_lineno is not None and alias_col_offset is not None:
                    start = f"{alias_lineno}.{alias_col_offset}"
                    end = f"{alias_lineno}.{alias_col_offset + len(alias.name)}"
                    self._add_tag("namespace", start, end)
                    if alias.asname:
                        as_start = f"{alias_lineno}.{alias_col_offset + len(alias.name) + 4}"
                        as_end = f"{alias_lineno}.{alias_col_offset + len(alias.name) + 4 + len(alias.asname)}"
                        self._add_tag("variable", as_start, as_end)
        except Exception as e:
            print(f"Error highlighting import from: {e}")

    def _find_import_keyword_position(self, node: ast.ImportFrom) -> Optional[Tuple[str, str]]:
        """Find the position of 'import' keyword in from-import statement"""
        try:
            # 使用getattr安全地访问属性
            lineno = getattr(node, 'lineno', 1)
            col_offset = getattr(node, 'col_offset', 0)
            
            # Get the line content
            line_start = f"{lineno}.0"
            line_end = f"{lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # Find 'import' keyword position
            import_pos = line_content.find("import", col_offset)
            if import_pos != -1:
                import_start = f"{lineno}.{import_pos}"
                import_end = f"{lineno}.{import_pos + 6}"  # "import" has 6 characters
                return import_start, import_end
        except Exception as e:
            print(f"Error finding import keyword: {e}")
        return None

    def _highlight_attribute(self, node: ast.Attribute):
        """Highlight attribute access"""
        # Highlight the base object
        if hasattr(node.value, 'lineno'):
            start, end = self.get_position(node.value)
            if isinstance(node.value, ast.Name):
                self._add_tag("variable", start, end)
            elif isinstance(node.value, ast.Attribute):
                self._highlight_attribute(node.value)
        
        # Highlight the attribute
        if hasattr(node, 'lineno'):
            # Calculate attribute position more accurately
            if hasattr(node.value, 'end_col_offset') and node.value.end_col_offset is not None:
                attr_start = f"{node.lineno}.{node.value.end_col_offset + 1}"
            else:
                # 安全地计算属性位置
                node_value_str = str(node.value) if node.value else ""
                attr_start = f"{node.lineno}.{node.col_offset + len(node_value_str) + 1}"
            # 安全地计算属性结束位置
            node_value_str = str(node.value) if node.value else ""
            attr_end = f"{node.lineno}.{node.col_offset + len(node_value_str) + 1 + len(node.attr)}"
            self._add_tag("property", attr_start, attr_end)
    
    def _highlight_attribute_call(self, node: ast.Attribute):
        """Highlight attribute call (method calls, class method calls)"""
        # Highlight the base object
        if isinstance(node.value, ast.Name):
            start, end = self.get_position(node.value)
            self._add_tag("variable", start, end)
        elif isinstance(node.value, ast.Attribute):
            self._highlight_attribute(node.value)
        
        # Highlight the method/function name
        if hasattr(node, 'lineno'):
            # Calculate method name position
            if hasattr(node.value, 'end_col_offset') and node.value.end_col_offset is not None:
                method_start = f"{node.lineno}.{node.value.end_col_offset + 1}"
            else:
                # 安全地计算方法名称位置
                node_value_str = str(node.value) if node.value else ""
                method_start = f"{node.lineno}.{node.col_offset + len(node_value_str) + 1}"
            # 安全地计算方法名称结束位置
            node_value_str = str(node.value) if node.value else ""
            method_end = f"{node.lineno}.{node.col_offset + len(node_value_str) + 1 + len(node.attr)}"
            self._add_tag("function", method_start, method_end)

    def _highlight_name(self, node: ast.Name, start: str, end: str):
        """Highlight name with context awareness"""
        if node.id in keyword.kwlist:
            self._add_tag("keyword", start, end)
        elif node.id in dir(builtins):
            self._add_tag("builtin", start, end)
        elif node.id.isupper():
            self._add_tag("constant", start, end)
        elif node.id == 'self':
            self._add_tag("self", start, end)
        else:
            # 根据上下文判断是函数引用还是变量引用
            parent = self._get_parent_node(node)
            if parent and isinstance(parent, ast.Call) and parent.func == node:
                # 如果是函数调用的函数名，检查是否是类名
                if node.id in self.class_names or self._is_likely_class_name(node.id):
                    # 如果是类实例化，高亮为class
                    self._add_tag("class", start, end)
                else:
                    # 如果是函数调用，高亮为function
                    self._add_tag("function", start, end)
            elif parent and isinstance(parent, ast.Attribute) and parent.value == node:
                # 如果是属性访问的基础对象，高亮为variable
                self._add_tag("variable", start, end)
            elif parent and isinstance(parent, ast.Assign) and node in parent.targets:
                # 如果是赋值语句的目标，高亮为variable
                self._add_tag("variable", start, end)
            elif node.id in self.class_names or self._is_likely_class_name(node.id):
                # 如果是类引用（如类型注解），高亮为class
                self._add_tag("class", start, end)
            else:
                # 默认情况下，高亮为variable
                self._add_tag("variable", start, end)
                
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

    def _highlight_call(self, node: ast.Call):
        """Highlight function call"""
        if isinstance(node.func, ast.Name):
            start, end = self.get_position(node.func)
            if node.func.id in dir(builtins):
                self._add_tag("builtin", start, end)
            elif node.func.id in self.class_names or self._is_likely_class_name(node.func.id):
                # 类实例化应该高亮为class
                self._add_tag("class", start, end)
            else:
                # 函数调用应该高亮为function
                self._add_tag("function", start, end)
        elif isinstance(node.func, ast.Attribute):
            # 处理属性调用，如 obj.method() 或 module.function()
            self._highlight_attribute_call(node.func)
                
    def _highlight_constant(self, node: ast.Constant, start: str, end: str):
        """Highlight constant"""
        if isinstance(node.value, (int, float)):
            self._add_tag("number", start, end)
        elif isinstance(node.value, str):
            self._add_tag("string", start, end)
            
    def _highlight_arg(self, node: ast.arg, start: str, end: str):
        """Highlight function argument"""
        self._add_tag("parameter", start, end)
        
    def _highlight_annotation(self, node: ast.AnnAssign):
        """Highlight type annotation"""
        if node.annotation:
            start, end = self.get_position(node.annotation)
            self._add_tag("type_annotation", start, end)

    def _highlight_assignment(self, node: ast.Assign):
        """Highlight assignment statement"""
        for target in node.targets:
            start, end = self.get_position(target)
            self._add_tag("variable", start, end)
            
        if isinstance(node.value, ast.Name):
            start, end = self.get_position(node.value)
            self._add_tag("variable", start, end)

    def _handle_open_parenthesis(self, event):
        """Handle parenthesis auto-completion"""
        try:
            current_pos = self.text_widget.index("insert")
            self.text_widget.insert(current_pos, '(')  # Insert left
            self.text_widget.insert(f"{current_pos} + 1c", self.auto_pairs['('])  # Insert right
            self.text_widget.mark_set("insert", f"{current_pos} + 1c")  # Move the curser
            return "break"  
        except Exception as e:
            print(f"Auto completion error: {str(e)}")
        return None

    def _highlight_operator(self, node: ast.AST, start: str, end: str):
        """Highlight operator"""
        self._add_tag("operator", start, end)

    def _highlight_bool_op(self, node: ast.BoolOp):
        """Highlight boolean operators (and, or, not)"""
        # 布尔运算符在AST中是BoolOp节点，但我们需要高亮具体的运算符
        # 由于AST不直接提供运算符的位置，我们需要从源代码中查找
        try:
            # 获取包含布尔运算符的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找布尔运算符的位置
            bool_operators = [' and ', ' or ', ' not ']
            for op in bool_operators:
                op_clean = op.strip()
                # 查找运算符在行中的位置
                pos = line_content.find(op)
                if pos != -1:
                    # 计算运算符的起始和结束位置
                    op_start = f"{node.lineno}.{pos + 1}"  # +1 跳过空格
                    op_end = f"{node.lineno}.{pos + 1 + len(op_clean)}"
                    self._add_tag("keyword", op_start, op_end)
        except Exception as e:
            print(f"Error highlighting boolean operator: {e}")

    def _highlight_if_statement(self, node: ast.If):
        """Highlight if statement keywords"""
        try:
            # 获取包含if语句的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找if关键字的位置
            if_pos = line_content.find("if ")
            if if_pos != -1:
                if_start = f"{node.lineno}.{if_pos}"
                if_end = f"{node.lineno}.{if_pos + 2}"  # "if" 有2个字符
                self._add_tag("keyword", if_start, if_end)
            
            # 查找elif关键字（如果有）
            if hasattr(node, 'orelse') and node.orelse:
                for orelse_node in node.orelse:
                    if isinstance(orelse_node, ast.If):
                        # 这是elif分支
                        elif_line_start = f"{orelse_node.lineno}.0"
                        elif_line_end = f"{orelse_node.lineno}.end"
                        elif_line_content = self.text_widget.get(elif_line_start, elif_line_end)
                        
                        elif_pos = elif_line_content.find("elif ")
                        if elif_pos != -1:
                            elif_start = f"{orelse_node.lineno}.{elif_pos}"
                            elif_end = f"{orelse_node.lineno}.{elif_pos + 4}"  # "elif" 有4个字符
                            self._add_tag("keyword", elif_start, elif_end)
            
            # 查找else关键字（如果有）
            if hasattr(node, 'orelse') and node.orelse:
                for orelse_node in node.orelse:
                    if not isinstance(orelse_node, ast.If):
                        # 这是else分支
                        else_line_start = f"{orelse_node.lineno}.0"
                        else_line_end = f"{orelse_node.lineno}.end"
                        else_line_content = self.text_widget.get(else_line_start, else_line_end)
                        
                        else_pos = else_line_content.find("else:")
                        if else_pos != -1:
                            else_start = f"{orelse_node.lineno}.{else_pos}"
                            else_end = f"{orelse_node.lineno}.{else_pos + 4}"  # "else" 有4个字符
                            self._add_tag("keyword", else_start, else_end)
        except Exception as e:
            print(f"Error highlighting if statement: {e}")

    def _highlight_for_statement(self, node: ast.For):
        """Highlight for statement keywords"""
        try:
            # 获取包含for语句的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找for关键字的位置
            for_pos = line_content.find("for ")
            if for_pos != -1:
                for_start = f"{node.lineno}.{for_pos}"
                for_end = f"{node.lineno}.{for_pos + 3}"  # "for" 有3个字符
                self._add_tag("keyword", for_start, for_end)
            
            # 查找in关键字的位置
            in_pos = line_content.find(" in ")
            if in_pos != -1:
                in_start = f"{node.lineno}.{in_pos + 1}"  # +1 跳过空格
                in_end = f"{node.lineno}.{in_pos + 3}"  # "in" 有2个字符
                self._add_tag("keyword", in_start, in_end)
        except Exception as e:
            print(f"Error highlighting for statement: {e}")

    def _highlight_while_statement(self, node: ast.While):
        """Highlight while statement keywords"""
        try:
            # 获取包含while语句的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找while关键字的位置
            while_pos = line_content.find("while ")
            if while_pos != -1:
                while_start = f"{node.lineno}.{while_pos}"
                while_end = f"{node.lineno}.{while_pos + 5}"  # "while" 有5个字符
                self._add_tag("keyword", while_start, while_end)
        except Exception as e:
            print(f"Error highlighting while statement: {e}")

    def _highlight_try_statement(self, node: ast.Try):
        """Highlight try statement keywords"""
        try:
            # 获取包含try语句的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找try关键字的位置
            try_pos = line_content.find("try:")
            if try_pos != -1:
                try_start = f"{node.lineno}.{try_pos}"
                try_end = f"{node.lineno}.{try_pos + 3}"  # "try" 有3个字符
                self._add_tag("keyword", try_start, try_end)
            
            # 查找except关键字的位置
            for handler in node.handlers:
                handler_line_start = f"{handler.lineno}.0"
                handler_line_end = f"{handler.lineno}.end"
                handler_line_content = self.text_widget.get(handler_line_start, handler_line_end)
                
                except_pos = handler_line_content.find("except ")
                if except_pos != -1:
                    except_start = f"{handler.lineno}.{except_pos}"
                    except_end = f"{handler.lineno}.{except_pos + 6}"  # "except" 有6个字符
                    self._add_tag("keyword", except_start, except_end)
            
            # 查找finally关键字的位置（如果有）
            if node.finalbody:
                for final_node in node.finalbody:
                    if hasattr(final_node, 'lineno'):
                        final_line_start = f"{final_node.lineno}.0"
                        final_line_end = f"{final_node.lineno}.end"
                        final_line_content = self.text_widget.get(final_line_start, final_line_end)
                        
                        finally_pos = final_line_content.find("finally:")
                        if finally_pos != -1:
                            finally_start = f"{final_node.lineno}.{finally_pos}"
                            finally_end = f"{final_node.lineno}.{finally_pos + 7}"  # "finally" 有7个字符
                            self._add_tag("keyword", finally_start, finally_end)
        except Exception as e:
            print(f"Error highlighting try statement: {e}")

    def _highlight_with_statement(self, node: ast.With):
        """Highlight with statement keywords"""
        try:
            # 获取包含with语句的整行代码
            line_start = f"{node.lineno}.0"
            line_end = f"{node.lineno}.end"
            line_content = self.text_widget.get(line_start, line_end)
            
            # 查找with关键字的位置
            with_pos = line_content.find("with ")
            if with_pos != -1:
                with_start = f"{node.lineno}.{with_pos}"
                with_end = f"{node.lineno}.{with_pos + 4}"  # "with" 有4个字符
                self._add_tag("keyword", with_start, with_end)
            
            # 查找as关键字的位置（如果有）
            for item in node.items:
                if item.optional_vars:
                    as_pos = line_content.find(" as ")
                    if as_pos != -1:
                        as_start = f"{node.lineno}.{as_pos + 1}"  # +1 跳过空格
                        as_end = f"{node.lineno}.{as_pos + 3}"  # "as" 有2个字符
                        self._add_tag("keyword", as_start, as_end)
        except Exception as e:
            print(f"Error highlighting with statement: {e}")

    def _handle_return_key(self, event):
        """Handle return key for auto-indentation"""
        try:
            current_line = self.text_widget.get("insert linestart", "insert")
            indent = len(current_line) - len(current_line.lstrip())

            if current_line.rstrip().endswith(":"):
                indent += 4  # Indentation
            self.text_widget.insert("insert", "\n" + " " * indent)
            return "break" 
        except Exception as e:
            print(f"Auto indentation error: {str(e)}")
        return None

    def _handle_tab_key(self, event):
        """Handle tab key to insert 4 spaces"""
        self.text_widget.insert("insert", " " * 4)
        return "break" 

    def set_theme(self, theme_data):
        """Set theme
        
        Args:
            theme_data: Can be theme config dict
        """
        try:
            # Basic properties
            if "base" in theme_data:
                self.text_widget.configure(**theme_data["base"])
                
            # Update colors
            for tag, color in theme_data.items():
                if tag != "base" and isinstance(color, str):
                    self.syntax_colors[tag] = color
                    
            # Setup tags
            self.setup_tags()
            
        except Exception as e:
            print(f"Theme error: {str(e)}")

    def get_position(self, node: ast.AST) -> Tuple[str, str]:
        """Get start and end positions of AST node"""
        # 使用getattr安全地访问可能不存在的属性
        lineno = getattr(node, 'lineno', None)
        col_offset = getattr(node, 'col_offset', None)
        
        if lineno is not None and col_offset is not None:
            start = f"{lineno}.{col_offset}"
            
            end_lineno = getattr(node, 'end_lineno', None)
            end_col_offset = getattr(node, 'end_col_offset', None)
            
            if end_lineno is not None and end_col_offset is not None:
                end = f"{end_lineno}.{end_col_offset}"
            else:
                # 计算节点长度作为备用方案
                node_str = str(node) if node is not None else ""
                end = f"{lineno}.{col_offset + len(node_str)}"
            return start, end
        return "1.0", "1.0"