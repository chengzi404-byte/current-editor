"""
Python高亮器单元测试
"""

import pytest
import ast
from unittest.mock import Mock, patch, MagicMock
from library.highlighter.python import CodeHighlighter


class TestPythonHighlighter:
    """Python高亮器测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        # 使用Mock对象模拟tkinter组件，避免GUI依赖
        self.text_widget = Mock()
        self.text_widget.configure_mock(**{
            'get.return_value': '',
            'index.return_value': '1.0'
        })
        self.highlighter = CodeHighlighter(self.text_widget)
    
    def teardown_method(self):
        """测试方法后置清理"""
        pass
    
    def test_init(self):
        """测试Python高亮器初始化"""
        assert isinstance(self.highlighter.builtins, set)
        assert isinstance(self.highlighter.keywords, set)
        assert isinstance(self.highlighter.imported_modules, set)
        assert isinstance(self.highlighter.imported_symbols, dict)
        
        # 验证Python特定的颜色设置
        assert "f_string" in self.highlighter.syntax_colors
        assert "bytes" in self.highlighter.syntax_colors
        assert "exception" in self.highlighter.syntax_colors
        assert "magic_method" in self.highlighter.syntax_colors
    
    def test_process_import_statement(self):
        """测试处理import语句"""
        # 创建模拟的import节点
        import_node = ast.Import(names=[
            ast.alias(name='os', asname=None),
            ast.alias(name='sys', asname='system')
        ])
        
        self.highlighter._process_import_statement(import_node)
        
        # 验证导入的模块
        assert 'os' in self.highlighter.imported_modules
        assert 'sys' in self.highlighter.imported_modules
        
        # 验证导入的符号
        assert 'os' in self.highlighter.imported_symbols
        assert self.highlighter.imported_symbols['os'] == 'os'
        assert 'system' in self.highlighter.imported_symbols
        assert self.highlighter.imported_symbols['system'] == 'sys'
    
    def test_process_import_from_statement(self):
        """测试处理from-import语句"""
        # 创建模拟的from-import节点
        import_from_node = ast.ImportFrom(
            module='tkinter',
            names=[
                ast.alias(name='Tk', asname=None),
                ast.alias(name='messagebox', asname='msgbox')
            ],
            level=0
        )
        
        self.highlighter._process_import_from_statement(import_from_node)
        
        # 验证导入的符号
        assert 'Tk' in self.highlighter.imported_symbols
        assert self.highlighter.imported_symbols['Tk'] == 'tkinter.Tk'
        assert 'msgbox' in self.highlighter.imported_symbols
        assert self.highlighter.imported_symbols['msgbox'] == 'tkinter.messagebox'
    
    def test_is_likely_class_name(self):
        """测试类名判断"""
        # 大写开头的名称应该是类名
        assert self.highlighter._is_likely_class_name('MyClass') is True
        assert self.highlighter._is_likely_class_name('Tk') is True
        assert self.highlighter._is_likely_class_name('Frame') is True
        
        # 小写开头的名称应该不是类名
        assert self.highlighter._is_likely_class_name('my_function') is False
        assert self.highlighter._is_likely_class_name('variable') is False
        
        # 空字符串或None
        assert self.highlighter._is_likely_class_name('') is False
        assert self.highlighter._is_likely_class_name(None) is False
    
    def test_highlight_imported_symbol_function_call(self):
        """测试高亮导入符号（函数调用）"""
        # 创建模拟的函数调用节点
        name_node = ast.Name(id='os', ctx=ast.Load())
        call_node = ast.Call(func=name_node, args=[], keywords=[])
        
        # 设置导入符号
        self.highlighter.imported_symbols['os'] = 'os'
        
        # 模拟_get_parent_node方法
        self.highlighter._get_parent_node = Mock(return_value=call_node)
        
        # 模拟_add_tag方法
        self.highlighter._add_tag = Mock()
        
        # 执行高亮
        self.highlighter._highlight_imported_symbol(name_node, '1.0', '1.2')
        
        # 验证调用了正确的标签
        self.highlighter._add_tag.assert_called_once_with('imported_function', '1.0', '1.2')
    
    def test_highlight_imported_symbol_class_reference(self):
        """测试高亮导入符号（类引用）"""
        # 创建模拟的名称节点
        name_node = ast.Name(id='Tk', ctx=ast.Load())
        
        # 设置导入符号
        self.highlighter.imported_symbols['Tk'] = 'tkinter.Tk'
        
        # 模拟_get_parent_node方法
        self.highlighter._get_parent_node = Mock(return_value=None)
        
        # 模拟_add_tag方法
        self.highlighter._add_tag = Mock()
        
        # 执行高亮
        self.highlighter._highlight_imported_symbol(name_node, '1.0', '1.2')
        
        # 验证调用了正确的标签
        self.highlighter._add_tag.assert_called_once_with('imported_class', '1.0', '1.2')
    
    def test_highlight_imported_attribute(self):
        """测试高亮导入模块的属性访问"""
        # 创建模拟的属性访问节点
        name_node = ast.Name(id='tkinter', ctx=ast.Load())
        attr_node = ast.Attribute(value=name_node, attr='Tk', ctx=ast.Load())
        
        # 设置行号和列偏移量
        attr_node.lineno = 1
        attr_node.col_offset = 0
        name_node.lineno = 1
        name_node.col_offset = 0
        
        # 设置导入的模块
        self.highlighter.imported_modules.add('tkinter')
        
        # 模拟_add_tag方法
        self.highlighter._add_tag = Mock()
        
        # 模拟get_position方法返回正确的位置
        self.highlighter.get_position = Mock(return_value=('1.0', '1.7'))
        
        # 执行高亮
        self.highlighter._highlight_imported_attribute(attr_node)
        
        # 验证调用了正确的标签
        # 根据实际代码，模块名高亮位置应该是 '1.0' 到 '1.7' (tkinter)
        # 属性名高亮位置应该是 '1.8' 到 '1.10' (Tk)
        self.highlighter._add_tag.assert_any_call('imported_module', '1.0', '1.7')
        self.highlighter._add_tag.assert_any_call('imported_class', '1.8', '1.10')
    
    def test_python_specific_syntax_colors(self):
        """测试Python特定语法颜色设置"""
        # 验证Python特定的颜色有默认值
        assert self.highlighter.syntax_colors['f_string'] is not None
        assert self.highlighter.syntax_colors['bytes'] is not None
        assert self.highlighter.syntax_colors['exception'] is not None
        assert self.highlighter.syntax_colors['magic_method'] is not None
        
        # 验证颜色值是有效的十六进制颜色
        import re
        color_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        
        for color_key in ['f_string', 'bytes', 'exception', 'magic_method']:
            color_value = self.highlighter.syntax_colors[color_key]
            assert color_pattern.match(color_value) is not None


class TestPythonHighlighterIntegration:
    """Python高亮器集成测试"""
    
    def setup_method(self):
        """测试方法前置设置"""
        # 使用Mock对象模拟tkinter组件，避免GUI依赖
        self.text_widget = Mock()
        self.text_widget.configure_mock(**{
            'get.return_value': '',
            'index.return_value': '1.0'
        })
        self.highlighter = CodeHighlighter(self.text_widget)
    
    def teardown_method(self):
        """测试方法后置清理"""
        pass
    
    def test_highlight_python_code_basic(self):
        """测试基础Python代码高亮"""
        python_code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法以验证高亮逻辑
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证至少添加了一些标签
        assert len(added_tags) > 0
        
        # 验证关键字被高亮
        keyword_tags = [tag for tag, start, end in added_tags if tag == 'keyword']
        assert len(keyword_tags) > 0
    
    def test_highlight_python_code_with_imports(self):
        """测试包含导入语句的Python代码高亮"""
        python_code = """
import os
from tkinter import Tk, messagebox


def main():
    root = Tk()
    messagebox.showinfo("Info", "Hello")
    return os.getcwd()
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证导入相关的标签被添加
        import_tags = [tag for tag, start, end in added_tags if 'imported' in tag]
        assert len(import_tags) > 0
    
    def test_highlight_f_strings(self):
        """测试f-string高亮"""
        python_code = """
name = "World"
age = 30
message = f\"Hello, {name}! You are {age} years old.\"\nmulti_line_fstring = f'''Hello,\n{name}!\nYou are {age} years old.'''
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证f-string相关的标签被添加
        string_tags = [tag for tag, start, end in added_tags if tag == "string"]
        assert len(string_tags) > 0
    
    def test_highlight_magic_methods(self):
        """测试魔术方法高亮"""
        python_code = """
class TestClass:
    def __init__(self):
        self.value = 0
    
    def __str__(self):
        return f"TestClass({self.value})"
    
    def __repr__(self):
        return f"TestClass(value={self.value})"
    
    def __add__(self, other):
        return TestClass(self.value + other.value)
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证方法相关的标签被添加
        method_tags = [tag for tag, start, end in added_tags if tag == "method"]
        assert len(method_tags) > 0
    
    def test_highlight_class_inheritance(self):
        """测试类继承高亮"""
        python_code = """
class BaseClass:
    def base_method(self):
        pass


class DerivedClass(BaseClass):
    def derived_method(self):
        pass


class MultipleInheritance(BaseClass, AnotherClass):
    def multiple_method(self):
        pass
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证类相关的标签被添加
        class_tags = [tag for tag, start, end in added_tags if tag == "class"]
        assert len(class_tags) > 0
    
    def test_highlight_decorators(self):
        """测试装饰器高亮"""
        python_code = """
import functools


def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@decorator
def decorated_function():
    pass


class TestClass:
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
    
    @classmethod
    def from_string(cls, string):
        return cls()
    
    @staticmethod
    def static_method():
        pass
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证装饰器相关的标签被添加
        decorator_tags = [tag for tag, start, end in added_tags if tag == "decorator"]
        assert len(decorator_tags) > 0
    
    def test_highlight_type_annotations(self):
        """测试类型注解高亮"""
        python_code = """
from typing import List, Dict, Tuple, Optional, Union

def typed_function(x: int, y: str, z: List[float]) -> Dict[str, Union[int, str]]:
    result: Dict[str, Union[int, str]] = {}
    result["x"] = x
    result["y"] = y
    result["z"] = len(z)
    return result


class TypedClass:
    def __init__(self, value: int = 0):
        self.value: int = value
    
    def process(self, data: Optional[List[str]]) -> Tuple[bool, str]:
        if data is None:
            return False, "No data"
        return True, f"Processed {len(data)} items"
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证类型注解相关的标签被添加
        type_tags = [tag for tag, start, end in added_tags if tag == "type_annotation"]
        assert len(type_tags) > 0
    
    def test_highlight_async_syntax(self):
        """测试异步语法高亮"""
        python_code = """
import asyncio


async def async_function():
    await asyncio.sleep(1)
    return "Done"


async def main():
    result = await async_function()
    print(result)


class AsyncClass:
    async def async_method(self):
        pass
    
    @staticmethod
    async def async_static_method():
        pass
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证关键字相关的标签被添加
        keyword_tags = [tag for tag, start, end in added_tags if tag == "keyword"]
        assert len(keyword_tags) > 0
    
    def test_highlight_context_managers(self):
        """测试上下文管理器高亮"""
        python_code = """
with open("file.txt", "r") as f:
    content = f.read()


class ContextManager:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


with ContextManager() as cm:
    cm.some_method()
"""
        
        # 模拟获取代码内容
        self.text_widget.get.return_value = python_code
        
        # 模拟_add_tag方法
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        self.highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        self.highlighter.highlight()
        
        # 验证关键字相关的标签被添加
        keyword_tags = [tag for tag, start, end in added_tags if tag == "keyword"]
        assert len(keyword_tags) > 0


if __name__ == "__main__":
    pytest.main([__file__])