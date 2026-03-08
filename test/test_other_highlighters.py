"""
其他语言高亮器单元测试
"""

import pytest
from unittest.mock import Mock, patch


class TestOtherHighlighters:
    """其他语言高亮器测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        # 使用Mock对象模拟tkinter组件，避免GUI依赖
        self.text_widget = Mock()
        self.text_widget.configure_mock(**{
            'get.return_value': '',
            'index.return_value': '1.0'
        })
    
    def teardown_method(self):
        """测试方法后置清理"""
        pass
    
    def test_javascript_highlighter_creation(self):
        """测试JavaScript高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            highlighter = factory.create_highlighter(self.text_widget, 'script.js')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.javascript')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_html_highlighter_creation(self):
        """测试HTML高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            highlighter = factory.create_highlighter(self.text_widget, 'index.html')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.html')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_css_highlighter_creation(self):
        """测试CSS高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            highlighter = factory.create_highlighter(self.text_widget, 'style.css')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.css')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_json_highlighter_creation(self):
        """测试JSON高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            highlighter = factory.create_highlighter(self.text_widget, 'config.json')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.json')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_markdown_highlighter_creation(self):
        """测试Markdown高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            highlighter = factory.create_highlighter(self.text_widget, 'README.md')
            
            # 验证调用了正确的模块
            mock_import.assert_called_once_with('library.highlighter.markdown')
            
            # 验证返回了高亮器实例
            assert highlighter is not None
    
    def test_log_highlighter_creation(self):
        """测试日志高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            # 测试.log文件
            highlighter1 = factory.create_highlighter(self.text_widget, 'app.log')
            
            # 测试.txt文件（应该使用日志高亮器）
            highlighter2 = factory.create_highlighter(self.text_widget, 'readme.txt')
            
            # 验证调用了正确的模块
            mock_import.assert_any_call('library.highlighter.log')
            
            # 验证返回了高亮器实例
            assert highlighter1 is not None
            assert highlighter2 is not None
    
    def test_cpp_highlighter_creation(self):
        """测试C++高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            # 测试不同C++扩展名
            extensions = ['.cpp', '.cxx', '.cc', '.hpp']
            
            for ext in extensions:
                highlighter = factory.create_highlighter(self.text_widget, f'test{ext}')
                mock_import.assert_called_with('library.highlighter.cpp')
                assert highlighter is not None
    
    def test_c_highlighter_creation(self):
        """测试C高亮器创建"""
        with patch('importlib.import_module') as mock_import:
            # 模拟模块导入
            mock_module = Mock()
            mock_highlighter_instance = Mock()
            mock_module.CodeHighlighter = Mock(return_value=mock_highlighter_instance)
            mock_import.return_value = mock_module
            
            from library.highlighter_factory import HighlighterFactory
            factory = HighlighterFactory()
            
            # 测试不同C扩展名
            extensions = ['.c', '.h']
            
            for ext in extensions:
                highlighter = factory.create_highlighter(self.text_widget, f'test{ext}')
                mock_import.assert_called_with('library.highlighter.c')
                assert highlighter is not None


if __name__ == "__main__":
    pytest.main([__file__])