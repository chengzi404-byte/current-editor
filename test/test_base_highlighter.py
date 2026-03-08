"""
基础高亮器单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from library.highlighter.base import BaseHighlighter


class TestBaseHighlighter:
    """基础高亮器测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        # 使用Mock对象模拟tkinter组件，避免GUI依赖
        self.text_widget = Mock()
        self.text_widget.configure_mock(**{
            'get.return_value': '',
            'index.return_value': '1.0'
        })
        self.highlighter = BaseHighlighter(self.text_widget)
    
    def teardown_method(self):
        """测试方法后置清理"""
        pass
    
    def test_init(self):
        """测试高亮器初始化"""
        assert self.highlighter.text_widget == self.text_widget
        assert self.highlighter.theme_name == "vscode-dark"
        assert isinstance(self.highlighter.syntax_colors, dict)
        assert len(self.highlighter.syntax_colors) > 0
        assert "keyword" in self.highlighter.syntax_colors
        assert "function" in self.highlighter.syntax_colors
    
    def test_load_theme_colors_success(self):
        """测试成功加载主题颜色"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('builtins.open') as mock_open, \
             patch('json.load') as mock_json_load:
            
            mock_exists.return_value = True
            mock_json_load.return_value = {
                "keyword": "#FF0000",
                "function": "#00FF00",
                "base": {"background": "#000000"}
            }
            
            colors = self.highlighter._load_theme_colors("test-theme")
            
            assert colors == {"keyword": "#FF0000", "function": "#00FF00"}
            mock_open.assert_called_once()
    
    def test_load_theme_colors_file_not_found(self):
        """测试主题文件不存在的情况"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            colors = self.highlighter._load_theme_colors("non-existent-theme")
            
            assert colors == {}
    
    def test_load_theme_colors_exception(self):
        """测试加载主题颜色时发生异常"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('builtins.open', side_effect=Exception("File error")):
            
            mock_exists.return_value = True
            
            colors = self.highlighter._load_theme_colors("error-theme")
            
            assert colors == {}
    
    def test_setup_tags(self):
        """测试设置标签配置"""
        # 模拟text_widget的tag_configure方法
        self.text_widget.tag_configure = Mock()
        
        self.highlighter.setup_tags()
        
        # 验证为每个颜色标签调用了tag_configure
        assert self.text_widget.tag_configure.call_count == len(self.highlighter.syntax_colors)
        
        # 验证调用的参数
        for tag, color in self.highlighter.syntax_colors.items():
            self.text_widget.tag_configure.assert_any_call(tag, foreground=color)
    
    def test_keyword_detection(self):
        """测试关键字检测"""
        assert "if" in self.highlighter.keywords
        assert "def" in self.highlighter.keywords
        assert "class" in self.highlighter.keywords
        assert "import" in self.highlighter.keywords
    
    def test_builtin_detection(self):
        """测试内置函数检测"""
        assert "print" in self.highlighter.builtins
        assert "len" in self.highlighter.builtins
        assert "range" in self.highlighter.builtins
    
    def test_language_keywords_categories(self):
        """测试语言关键字分类"""
        assert "control" in self.highlighter.language_keywords
        assert "definition" in self.highlighter.language_keywords
        assert "module" in self.highlighter.language_keywords
        assert "value" in self.highlighter.language_keywords
        assert "context" in self.highlighter.language_keywords
        
        # 验证每个分类都包含预期的关键字
        assert "if" in self.highlighter.language_keywords["control"]
        assert "def" in self.highlighter.language_keywords["definition"]
        assert "import" in self.highlighter.language_keywords["module"]
        assert "True" in self.highlighter.language_keywords["value"]
        assert "global" in self.highlighter.language_keywords["context"]
    
    def test_auto_pairs_configuration(self):
        """测试自动配对配置"""
        expected_pairs = {
            '"': '"', "'": "'", '(': ')', '[': ']', '{': '}',
            '"""': '"""', "'''": "'''"
        }
        
        assert self.highlighter.auto_pairs == expected_pairs
    
    def test_highlight_delay_config(self):
        """测试高亮延迟配置"""
        assert self.highlighter._highlight_delay == 50
        assert self.highlighter._highlight_pending is False
        assert self.highlighter._last_content == ""
    
    @patch.object(BaseHighlighter, 'highlight')
    def test_queue_highlight(self, mock_highlight):
        """测试高亮队列功能"""
        # 模拟after方法
        self.text_widget.after = Mock()
        
        # 第一次调用应该设置pending标志并调用after
        self.highlighter._queue_highlight()
        
        assert self.highlighter._highlight_pending is True
        self.text_widget.after.assert_called_once_with(50, self.highlighter._delayed_highlight)
        
        # 第二次调用不应该重复设置
        self.text_widget.after.reset_mock()
        self.highlighter._queue_highlight()
        
        self.text_widget.after.assert_not_called()
    
    @patch.object(BaseHighlighter, 'highlight')
    def test_delayed_highlight(self, mock_highlight):
        """测试延迟高亮功能"""
        # 设置初始内容
        self.highlighter._last_content = "old content"
        # 模拟获取新内容
        self.text_widget.get.return_value = "new content"
        
        self.highlighter._delayed_highlight()
        
        # 验证高亮方法被调用
        mock_highlight.assert_called_once()
        assert self.highlighter._last_content == "new content"
        assert self.highlighter._highlight_pending is False
    
    def test_delayed_highlight_same_content(self):
        """测试内容相同时不进行高亮"""
        self.highlighter._last_content = "same content"
        # 模拟获取相同内容
        self.text_widget.get.return_value = "same content"
        
        # 模拟highlight方法
        self.highlighter.highlight = Mock()
        
        self.highlighter._delayed_highlight()
        
        # 验证高亮方法没有被调用
        self.highlighter.highlight.assert_not_called()
        assert self.highlighter._highlight_pending is False
    
    def test_basic_highlight(self):
        """测试基本高亮功能"""
        # 准备测试代码
        test_code = """def test_func():
    print("Hello, World!")
    x = 123
    # This is a comment
    return x > 0
"""
        
        # 模拟_add_tag方法以验证高亮逻辑
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行基本高亮
        self.highlighter._basic_highlight(test_code)
        
        # 验证高亮结果
        keyword_tags = [tag for tag, _, _ in added_tags if tag == "keyword"]
        string_tags = [tag for tag, _, _ in added_tags if tag == "string"]
        number_tags = [tag for tag, _, _ in added_tags if tag == "number"]
        comment_tags = [tag for tag, _, _ in added_tags if tag == "comment"]
        
        # 确保至少有一些高亮标签被添加
        assert len(keyword_tags) > 0, "没有关键字被高亮"
        assert len(string_tags) > 0, "没有字符串被高亮"
        assert len(number_tags) > 0, "没有数字被高亮"
        assert len(comment_tags) > 0, "没有注释被高亮"
    
    def test_clear_tags(self):
        """测试清除所有标签"""
        # 模拟tag_remove方法
        self.text_widget.tag_remove = Mock()
        
        # 执行清除标签
        self.highlighter._clear_tags()
        
        # 验证调用次数与颜色数量一致
        expected_call_count = len(self.highlighter.syntax_colors)
        actual_call_count = self.text_widget.tag_remove.call_count
        assert actual_call_count == expected_call_count, f"预期调用 {expected_call_count} 次tag_remove，实际调用 {actual_call_count} 次"
    
    def test_set_theme(self):
        """测试设置主题"""
        # 准备测试主题数据
        test_theme = {
            "base": {"background": "#000000", "foreground": "#ffffff"},
            "keyword": "#ff0000",
            "string": "#00ff00",
            "number": "#0000ff"
        }
        
        # 模拟configure和tag_configure方法
        self.text_widget.configure = Mock()
        self.text_widget.tag_configure = Mock()
        
        # 执行设置主题
        self.highlighter.set_theme(test_theme)
        
        # 验证调用了configure方法
        self.text_widget.configure.assert_called_once_with(**test_theme["base"])
        
        # 验证调用了tag_configure方法至少一次
        assert self.text_widget.tag_configure.call_count > 0, "tag_configure方法没有被调用"
    
    def test_is_likely_class_name(self):
        """测试类名判断方法"""
        # 测试大写开头的类名
        assert self.highlighter._is_likely_class_name("ClassName") is True
        assert self.highlighter._is_likely_class_name("MyClass") is True
        
        # 测试小写开头的非类名
        assert self.highlighter._is_likely_class_name("function_name") is False
        assert self.highlighter._is_likely_class_name("variable") is False
        
        # 测试常见的类名模式
        assert self.highlighter._is_likely_class_name("Tk") is True
        assert self.highlighter._is_likely_class_name("Frame") is True
        assert self.highlighter._is_likely_class_name("Button") is True
        
        # 测试空字符串和None
        assert self.highlighter._is_likely_class_name("") is False
        assert self.highlighter._is_likely_class_name(None) is False
    
    def test_get_position(self):
        """测试获取AST节点位置方法"""
        # 创建一个简单的Name节点用于测试
        import ast
        name_node = ast.Name(id="test_var", ctx=ast.Load())
        name_node.lineno = 5
        name_node.col_offset = 2
        name_node.end_lineno = 5
        name_node.end_col_offset = 10
        
        # 执行获取位置
        start, end = self.highlighter.get_position(name_node)
        
        # 验证结果
        assert start == "5.2", f"预期start位置为'5.2'，实际为'{start}'"
        assert end == "5.10", f"预期end位置为'5.10'，实际为'{end}'"
    
    def test_get_position_without_end_info(self):
        """测试没有end信息时获取AST节点位置"""
        # 创建一个没有end信息的Name节点
        import ast
        name_node = ast.Name(id="test_var", ctx=ast.Load())
        name_node.lineno = 5
        name_node.col_offset = 2
        # 不设置end_lineno和end_col_offset
        
        # 执行获取位置
        start, end = self.highlighter.get_position(name_node)
        
        # 验证结果
        assert start == "5.2", f"预期start位置为'5.2'，实际为'{start}'"
        assert end == "5.10", f"预期end位置为'5.10'，实际为'{end}'"
    
    def test_highlight_comments_and_strings(self):
        """测试注释和字符串高亮功能"""
        # 准备测试代码，包含各种注释和字符串
        test_code = """def test_func():
    # 单行注释
    print("Hello, World!")  # 行尾注释
    x = 123
    
    # 多行字符串
    multi_str = \"\"\"This is a
    multi-line string\"\"\"
    
    # 单引号多行字符串
    single_multi = '''Another
    multi-line string'''
    
    # 数字和布尔值
    y = 3.14
    z = True
    
    return x + y
"""
        
        # 模拟_add_tag方法以验证高亮逻辑
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行注释和字符串高亮
        self.highlighter._highlight_comments_and_strings(test_code)
        
        # 验证高亮结果
        comment_tags = [tag for tag, _, _ in added_tags if tag == "comment"]
        docstring_tags = [tag for tag, _, _ in added_tags if tag == "docstring"]
        string_tags = [tag for tag, _, _ in added_tags if tag == "string"]
        
        # 确保至少有一些高亮标签被添加
        assert len(comment_tags) > 0, "没有注释被高亮"
        assert len(docstring_tags) > 0, "没有多行字符串被高亮"
        assert len(string_tags) > 0, "没有单行字符串被高亮"
    
    def test_highlight_method(self):
        """测试完整的highlight方法"""
        # 准备测试代码
        test_code = """def test_func():
    print("Hello, World!")
    return True
"""
        
        # 模拟_get和_add_tag方法
        self.text_widget.get.return_value = test_code
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        self.highlighter._clear_tags = Mock()
        
        # 执行完整的highlight方法
        self.highlighter.highlight()
        
        # 验证调用了_clear_tags方法
        self.highlighter._clear_tags.assert_called_once()
        
        # 验证至少添加了一些标签
        assert len(added_tags) > 0, "没有标签被添加"


if __name__ == "__main__":
    pytest.main([__file__])