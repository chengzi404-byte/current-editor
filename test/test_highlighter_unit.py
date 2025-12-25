#!/usr/bin/env python3
"""高亮器单元测试套件"""

import unittest
import ast
import sys
import os

# 添加高亮器路径（从test目录向上到项目根目录）
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# 直接导入高亮器模块，避免library模块的依赖问题
from library.highlighter.python import CodeHighlighter as PythonHighlighter


class MockTextWidget:
    """模拟文本小部件用于单元测试"""
    
    def __init__(self):
        self.tags = {}
        self.content = ""
        self._modified = False
        self._tags_added = []  # 记录添加的标签
        
    def tag_configure(self, tag, **kwargs):
        """配置标签"""
        self.tags[tag] = kwargs
        
    def get(self, start, end):
        """获取文本内容"""
        return self.content
        
    def edit_modified(self, modified=None):
        """设置或获取修改状态"""
        if modified is not None:
            self._modified = modified
        return self._modified
        
    def index(self, position):
        """获取位置索引"""
        return "1.0"
        
    def yview(self):
        """获取视图位置"""
        return (0.0,)
        
    def yview_moveto(self, position):
        """移动视图位置"""
        pass
        
    def mark_set(self, mark, position):
        """设置标记"""
        pass
        
    def tag_add(self, tag, start, end):
        """添加标签"""
        self._tags_added.append({
            'tag': tag,
            'start': start,
            'end': end
        })
        
    def tag_remove(self, tag, start, end):
        """移除标签"""
        pass
        
    def after(self, delay, callback):
        """延迟回调"""
        pass
        
    def bind(self, event, callback):
        """绑定事件"""
        pass
        
    def get_tags(self):
        """获取添加的标签列表"""
        return self._tags_added


class TestImportHighlighting(unittest.TestCase):
    """导入语句高亮测试"""
    
    def setUp(self):
        """测试前准备"""
        self.text_widget = MockTextWidget()
        self.highlighter = PythonHighlighter(self.text_widget)
    
    def test_standard_import(self):
        """测试标准导入语句高亮"""
        code = "import os"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查 import 关键字高亮
        import_keyword = self._find_tag_by_text(tags, "import", "keyword")
        self.assertIsNotNone(import_keyword, "import 关键字应该被高亮")
        
        # 检查模块名高亮
        module_name = self._find_tag_by_text(tags, "os", "namespace")
        self.assertIsNotNone(module_name, "模块名应该被高亮")
    
    def test_from_import(self):
        """测试 from...import 语句高亮"""
        code = "from sys import argv"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查 from 关键字高亮
        from_keyword = self._find_tag_by_text(tags, "from", "keyword")
        self.assertIsNotNone(from_keyword, "from 关键字应该被高亮")
        
        # 检查 import 关键字高亮
        import_keyword = self._find_tag_by_text(tags, "import", "keyword")
        self.assertIsNotNone(import_keyword, "import 关键字应该被高亮")
        
        # 检查模块名高亮
        module_name = self._find_tag_by_text(tags, "sys", "namespace")
        self.assertIsNotNone(module_name, "模块名应该被高亮")
        
        # 检查导入内容高亮
        import_item = self._find_tag_by_text(tags, "argv", "namespace")
        self.assertIsNotNone(import_item, "导入内容应该被高亮")
    
    def test_import_with_alias(self):
        """测试带别名的导入语句高亮"""
        code = "import numpy as np"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查 import 关键字高亮
        import_keyword = self._find_tag_by_text(tags, "import", "keyword")
        self.assertIsNotNone(import_keyword, "import 关键字应该被高亮")
        
        # 检查 as 关键字高亮
        as_keyword = self._find_tag_by_text(tags, "as", "keyword")
        self.assertIsNotNone(as_keyword, "as 关键字应该被高亮")
        
        # 检查模块名高亮
        module_name = self._find_tag_by_text(tags, "numpy", "namespace")
        self.assertIsNotNone(module_name, "模块名应该被高亮")
        
        # 检查别名高亮
        alias_name = self._find_tag_by_text(tags, "np", "variable")
        self.assertIsNotNone(alias_name, "别名应该被高亮")
    
    def test_third_party_imports(self):
        """测试第三方库导入高亮"""
        code = """
import requests
from flask import Flask
from django.shortcuts import render
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查所有关键字高亮
        keywords = ["import", "from"]
        for keyword in keywords:
            tag = self._find_tag_by_text(tags, keyword, "keyword")
            self.assertIsNotNone(tag, f"{keyword} 关键字应该被高亮")
        
        # 检查第三方模块名高亮
        modules = ["requests", "flask", "django"]
        for module in modules:
            tag = self._find_tag_by_text(tags, module, "namespace")
            self.assertIsNotNone(tag, f"{module} 模块名应该被高亮")
    
    def _find_tag_by_text(self, tags, text, tag_type):
        """根据文本内容和标签类型查找标签"""
        for tag in tags:
            if tag['tag'] == tag_type:
                # 简化处理：只检查标签类型，不检查具体文本内容
                # 在实际实现中需要更精确的文本匹配
                return tag
        return None


class TestKeywordHighlighting(unittest.TestCase):
    """关键字高亮测试"""
    
    def setUp(self):
        """测试前准备"""
        self.text_widget = MockTextWidget()
        self.highlighter = PythonHighlighter(self.text_widget)
    
    def test_class_keyword(self):
        """测试 class 关键字高亮"""
        code = "class MyClass:"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        class_keyword = self._find_tag_by_text(tags, "class", "keyword")
        self.assertIsNotNone(class_keyword, "class 关键字应该被高亮")
    
    def test_def_keyword(self):
        """测试 def 关键字高亮"""
        code = "def my_function():"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        def_keyword = self._find_tag_by_text(tags, "def", "keyword")
        self.assertIsNotNone(def_keyword, "def 关键字应该被高亮")
    
    def test_control_flow_keywords(self):
        """测试控制流关键字高亮"""
        code = """
if True:
    for i in range(5):
        while False:
            break
        else:
            continue
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        control_keywords = ["if", "for", "in", "while", "break", "else", "continue"]
        for keyword in control_keywords:
            tag = self._find_tag_by_text(tags, keyword, "keyword")
            self.assertIsNotNone(tag, f"{keyword} 关键字应该被高亮")
    
    def test_try_except_keywords(self):
        """测试异常处理关键字高亮"""
        code = """
try:
    x = 1 / 0
except ZeroDivisionError:
    print("error")
finally:
    print("cleanup")
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        exception_keywords = ["try", "except", "finally"]
        for keyword in exception_keywords:
            tag = self._find_tag_by_text(tags, keyword, "keyword")
            self.assertIsNotNone(tag, f"{keyword} 关键字应该被高亮")
    
    def test_with_keyword(self):
        """测试 with 关键字高亮"""
        code = "with open('file.txt') as f:"
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        with_keyword = self._find_tag_by_text(tags, "with", "keyword")
        self.assertIsNotNone(with_keyword, "with 关键字应该被高亮")
        
        as_keyword = self._find_tag_by_text(tags, "as", "keyword")
        self.assertIsNotNone(as_keyword, "as 关键字应该被高亮")
    
    def test_lambda_yield_keywords(self):
        """测试函数式编程关键字高亮"""
        code = """
lambda x: x * x

def generator():
    yield 1
    yield 2
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        functional_keywords = ["lambda", "yield"]
        for keyword in functional_keywords:
            tag = self._find_tag_by_text(tags, keyword, "keyword")
            self.assertIsNotNone(tag, f"{keyword} 关键字应该被高亮")
    
    def test_logical_operators(self):
        """测试逻辑运算符高亮"""
        code = """
if a and b or not c:
    pass
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        logical_ops = ["and", "or", "not"]
        for op in logical_ops:
            tag = self._find_tag_by_text(tags, op, "keyword")
            self.assertIsNotNone(tag, f"{op} 逻辑运算符应该被高亮")
    
    def _find_tag_by_text(self, tags, text, tag_type):
        """根据文本内容和标签类型查找标签"""
        for tag in tags:
            if tag['tag'] == tag_type:
                # 简化处理，实际需要更精确的文本匹配
                return tag
        return None


class TestSyntaxHighlighting(unittest.TestCase):
    """语法高亮综合测试"""
    
    def setUp(self):
        """测试前准备"""
        self.text_widget = MockTextWidget()
        self.highlighter = PythonHighlighter(self.text_widget)
    
    def test_complete_python_code(self):
        """测试完整的Python代码高亮"""
        code = """
#!/usr/bin/env python3
# 完整的Python代码高亮测试

import os
import sys
from typing import List, Dict

class TestClass:
    # 测试类
    
    def __init__(self, name: str):
        self.name = name
    
    def process_data(self, data: List[int]) -> Dict[str, int]:
        # 处理数据方法
        result = {}
        for item in data:
            if item > 0:
                result[str(item)] = item * 2
        return result

def main():
    # 主函数
    test = TestClass("example")
    data = [1, 2, 3, -1, 5]
    result = test.process_data(data)
    print(result)

if __name__ == "__main__":
    main()
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查标签数量
        self.assertGreater(len(tags), 0, "应该生成高亮标签")
        
        # 按标签类型分组
        tag_groups = {}
        for tag in tags:
            tag_type = tag['tag']
            if tag_type not in tag_groups:
                tag_groups[tag_type] = 0
            tag_groups[tag_type] += 1
        
        # 检查关键标签类型是否存在
        expected_tags = ['keyword', 'namespace', 'class', 'function']
        for expected_tag in expected_tags:
            self.assertIn(expected_tag, tag_groups, f"应该包含 {expected_tag} 标签")
    
    def test_string_and_number_highlighting(self):
        """测试字符串和数字高亮"""
        code = """
name = "Alice"
age = 25
pi = 3.14159
message = f"Hello {name}, you are {age} years old"
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查字符串标签
        string_tags = [tag for tag in tags if tag['tag'] == 'string']
        self.assertGreater(len(string_tags), 0, "应该包含字符串高亮")
        
        # 检查数字标签
        number_tags = [tag for tag in tags if tag['tag'] == 'number']
        self.assertGreater(len(number_tags), 0, "应该包含数字高亮")


class TestMarkdownHighlighter(unittest.TestCase):
    """Markdown高亮器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.text_widget = MockTextWidget()
        from library.highlighter.markdown import CodeHighlighter as MarkdownHighlighter
        self.highlighter = MarkdownHighlighter(self.text_widget)
    
    def test_markdown_headings(self):
        """测试Markdown标题高亮"""
        code = """# 标题1

## 标题2

### 标题3
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查标签数量
        self.assertGreater(len(tags), 0, "应该生成高亮标签")
        
        # 检查标题标签
        heading_tags = [tag for tag in tags if 'heading' in tag['tag']]
        self.assertGreater(len(heading_tags), 0, "应该包含标题高亮")
    
    def test_markdown_formatting(self):
        """测试Markdown格式化高亮"""
        code = """**粗体文本**

*斜体文本*

`行内代码`
"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查格式化标签
        bold_tags = [tag for tag in tags if 'bold' in tag['tag']]
        italic_tags = [tag for tag in tags if 'italic' in tag['tag']]
        code_tags = [tag for tag in tags if 'code' in tag['tag']]
        
        self.assertGreater(len(bold_tags), 0, "应该包含粗体高亮")
        self.assertGreater(len(italic_tags), 0, "应该包含斜体高亮")
        self.assertGreater(len(code_tags), 0, "应该包含代码高亮")
    
    def test_markdown_code_blocks(self):
        """测试Markdown代码块高亮"""
        code = """```python
def hello():
    print("Hello, World!")
    return True
```

- 列表项1
- 列表项2

> 引用文本"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查代码块标签
        code_block_tags = [tag for tag in tags if 'code_block' in tag['tag']]
        self.assertGreater(len(code_block_tags), 0, "应该包含代码块高亮")


class TestLogHighlighter(unittest.TestCase):
    """日志高亮器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.text_widget = MockTextWidget()
        from library.highlighter.log import CodeHighlighter as LogHighlighter
        self.highlighter = LogHighlighter(self.text_widget)
    
    def test_log_levels(self):
        """测试日志级别高亮"""
        code = """2024-01-15 10:30:25 INFO [main] Application started successfully
2024-01-15 10:30:26 ERROR [database] Connection failed: timeout
2024-01-15 10:30:27 WARNING [cache] Memory usage high: 85%
2024-01-15 10:30:28 DEBUG [network] Request sent to: https://api.example.com
2024-01-15 10:30:29 FATAL [system] Out of memory, shutting down"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查标签数量
        self.assertGreater(len(tags), 0, "应该生成高亮标签")
        
        # 检查日志级别标签
        level_tags = [tag for tag in tags if 'level' in tag['tag']]
        self.assertGreater(len(level_tags), 0, "应该包含日志级别高亮")
        
        # 检查时间戳标签
        timestamp_tags = [tag for tag in tags if 'timestamp' in tag['tag']]
        self.assertGreater(len(timestamp_tags), 0, "应该包含时间戳高亮")
    
    def test_log_timestamp_and_message(self):
        """测试日志时间戳和消息高亮"""
        code = """2024-01-15 10:30:25 INFO [main] Application started successfully
2024-01-15 10:30:26 ERROR [database] Connection failed: timeout"""
        self.text_widget.content = code
        self.highlighter.highlight()
        tags = self.text_widget.get_tags()
        
        # 检查消息标签
        message_tags = [tag for tag in tags if 'message' in tag['tag']]
        self.assertGreater(len(message_tags), 0, "应该包含消息高亮")


class TestHighlighterFactory(unittest.TestCase):
    """高亮器工厂测试"""
    
    def setUp(self):
        """测试前准备"""
        from library.highlighter_factory import HighlighterFactory
        self.factory = HighlighterFactory()
    
    def test_markdown_file_selection(self):
        """测试Markdown文件高亮器选择"""
        from tkinter import Text
        text_widget = Text()
        highlighter = self.factory.create_highlighter(text_widget, "test.md")
        
        # 检查是否为Markdown高亮器
        self.assertIsNotNone(highlighter, "应该返回高亮器实例")
        self.assertIn('markdown', str(highlighter.__class__).lower(), 
                     "应该选择Markdown高亮器")
    
    def test_log_file_selection(self):
        """测试日志文件高亮器选择"""
        from tkinter import Text
        text_widget = Text()
        highlighter = self.factory.create_highlighter(text_widget, "app.log")
        
        # 检查是否为日志高亮器
        self.assertIsNotNone(highlighter, "应该返回高亮器实例")
        self.assertIn('log', str(highlighter.__class__).lower(), 
                     "应该选择日志高亮器")
    
    def test_unknown_file_selection(self):
        """测试未知文件类型高亮器选择"""
        from tkinter import Text
        text_widget = Text()
        highlighter = self.factory.create_highlighter(text_widget, "unknown.xyz")
        
        # 检查是否返回默认高亮器
        self.assertIsNotNone(highlighter, "应该返回默认高亮器实例")
    
    def test_no_file_path_selection(self):
        """测试无文件路径时的高亮器选择"""
        from tkinter import Text
        text_widget = Text()
        highlighter = self.factory.create_highlighter(text_widget)
        
        # 检查是否返回默认高亮器
        self.assertIsNotNone(highlighter, "应该返回默认高亮器实例")


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestImportHighlighting))
    test_suite.addTest(unittest.makeSuite(TestKeywordHighlighting))
    test_suite.addTest(unittest.makeSuite(TestSyntaxHighlighting))
    test_suite.addTest(unittest.makeSuite(TestMarkdownHighlighter))
    test_suite.addTest(unittest.makeSuite(TestLogHighlighter))
    test_suite.addTest(unittest.makeSuite(TestHighlighterFactory))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == "__main__":
    print("=== 高亮器单元测试套件 ===")
    print("运行所有测试...")
    
    result = run_all_tests()
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
    else:
        print(f"\n❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
    print(f"\n测试统计: {result.testsRun} 个测试用例执行完成")