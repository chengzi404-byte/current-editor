"""
高亮器工厂单元测试
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from library.highlighter_factory import HighlighterFactory
from library.highlighter.python import CodeHighlighter


class TestHighlighterFactory:
    """高亮器工厂测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        self.factory = HighlighterFactory()
        # 使用Mock对象模拟tkinter组件，避免GUI依赖
        self.text_widget = Mock()
        self.text_widget.configure_mock(**{
            'get.return_value': '',
            'index.return_value': '1.0'
        })
    
    def teardown_method(self):
        """测试方法后置清理"""
        pass
    
    def test_init(self):
        """测试工厂初始化"""
        assert hasattr(self.factory, 'EXTENSION_MAP')
        assert isinstance(self.factory.EXTENSION_MAP, dict)
        assert len(self.factory.EXTENSION_MAP) > 0
    
    def test_extension_map_completeness(self):
        """测试扩展名映射的完整性"""
        # 验证常见编程语言的扩展名映射
        expected_mappings = {
            '.py': 'python',
            '.cpp': 'cpp',
            '.c': 'c',
            '.java': 'java',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.json': 'json',
            '.md': 'markdown',
            '.log': 'log',
            '.txt': 'log'
        }
        
        for ext, expected_type in expected_mappings.items():
            assert ext in self.factory.EXTENSION_MAP
            assert self.factory.EXTENSION_MAP[ext] == expected_type
    
    def test_create_highlighter_with_python_file(self):
        """测试为Python文件创建高亮器"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'test.py')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.python')
            
            # 验证返回了正确类型的高亮器
            assert isinstance(highlighter, CodeHighlighter)
            assert highlighter.text_widget == self.text_widget
    
    def test_create_highlighter_with_html_file(self):
        """测试为HTML文件创建高亮器"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'index.html')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.html')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_create_highlighter_with_unknown_extension(self):
        """测试为未知扩展名创建高亮器"""
        with patch('library.highlighter_factory.api') as mock_api, \
             patch('importlib.import_module') as mock_import:
            
            # 模拟API设置
            mock_api.Settings.Highlighter.syntax_highlighting.return_value = {"code": "python"}
            
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'test.unknown')
            
            # 验证使用了默认的高亮器类型
            mock_api.Settings.Highlighter.syntax_highlighting.assert_called_once()
            mock_import.assert_called_once_with('library.highlighter.python')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter, CodeHighlighter)
    
    def test_create_highlighter_without_file_path(self):
        """测试没有文件路径时创建高亮器"""
        with patch('library.highlighter_factory.api') as mock_api, \
             patch('importlib.import_module') as mock_import:
            
            # 模拟API设置
            mock_api.Settings.Highlighter.syntax_highlighting.return_value = {"code": "python"}
            
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            highlighter = self.factory.create_highlighter(self.text_widget)
            
            # 验证使用了默认的高亮器类型
            mock_api.Settings.Highlighter.syntax_highlighting.assert_called_once()
            mock_import.assert_called_once_with('library.highlighter.python')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter, CodeHighlighter)
    
    def test_create_highlighter_with_import_error(self):
        """测试高亮器模块导入失败时的回退机制"""
        with patch('library.highlighter_factory.api') as mock_api, \
             patch('importlib.import_module') as mock_import:
            
            # 模拟API设置
            mock_api.Settings.Highlighter.syntax_highlighting.return_value = {"code": "nonexistent"}
            
            # 模拟第一次导入失败，第二次成功
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.side_effect = [
                ImportError("Module not found"),  # 第一次调用
                mock_module  # 第二次调用（回退到Python高亮器）
            ]
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'test.nonexistent')
            
            # 验证尝试了两次导入
            assert mock_import.call_count == 2
            
            # 验证第一次尝试导入不存在的模块
            mock_import.assert_any_call('library.highlighter.nonexistent')
            
            # 验证回退到Python高亮器
            mock_import.assert_any_call('library.highlighter.python')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter, CodeHighlighter)
    
    def test_create_highlighter_with_attribute_error(self):
        """测试高亮器类不存在时的回退机制"""
        with patch('library.highlighter_factory.api') as mock_api, \
             patch('importlib.import_module') as mock_import:
            
            # 模拟API设置
            mock_api.Settings.Highlighter.syntax_highlighting.return_value = {"code": "invalid"}
            
            # 模拟第一次导入成功但类不存在，第二次成功
            mock_module1 = Mock()
            # 正确模拟AttributeError：当getattr被调用时抛出异常
            mock_module1.CodeHighlighter = Mock(side_effect=AttributeError("'Mock' object has no attribute 'CodeHighlighter'"))
            
            mock_module2 = Mock()
            mock_module2.CodeHighlighter = CodeHighlighter
            
            mock_import.side_effect = [
                mock_module1,  # 第一次调用（类不存在）
                mock_module2   # 第二次调用（回退到Python高亮器）
            ]
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'test.invalid')
            
            # 验证尝试了两次导入
            assert mock_import.call_count == 2
            
            # 验证返回了高亮器实例（回退到Python高亮器）
            assert isinstance(highlighter, CodeHighlighter)
    
    def test_case_insensitive_extension_matching(self):
        """测试扩展名匹配不区分大小写"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            # 测试大写扩展名
            highlighter1 = self.factory.create_highlighter(self.text_widget, 'test.PY')
            
            # 测试混合大小写扩展名
            highlighter2 = self.factory.create_highlighter(self.text_widget, 'test.HtMl')
            
            # 验证都调用了正确的模块
            mock_import.assert_any_call('library.highlighter.python')
            mock_import.assert_any_call('library.highlighter.html')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter1, CodeHighlighter)
            assert highlighter2 is not None
    
    def test_file_path_with_multiple_dots(self):
        """测试包含多个点的文件路径"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            # 测试包含多个点的文件路径
            highlighter = self.factory.create_highlighter(self.text_widget, 'test.config.py')
            
            # 验证正确提取了扩展名
            mock_import.assert_called_once_with('library.highlighter.python')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter, CodeHighlighter)
    
    def test_file_path_without_extension(self):
        """测试没有扩展名的文件路径"""
        with patch('library.highlighter_factory.api') as mock_api, \
             patch('importlib.import_module') as mock_import:
            
            # 模拟API设置
            mock_api.Settings.Highlighter.syntax_highlighting.return_value = {"code": "python"}
            
            # 模拟模块导入
            mock_module = Mock()
            mock_module.CodeHighlighter = CodeHighlighter
            mock_import.return_value = mock_module
            
            highlighter = self.factory.create_highlighter(self.text_widget, 'README')
            
            # 验证使用了默认的高亮器类型
            mock_api.Settings.Highlighter.syntax_highlighting.assert_called_once()
            mock_import.assert_called_once_with('library.highlighter.python')
            
            # 验证返回了高亮器实例
            assert isinstance(highlighter, CodeHighlighter)


if __name__ == "__main__":
    pytest.main([__file__])