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


if __name__ == "__main__":
    pytest.main([__file__])