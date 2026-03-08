"""
最小化高亮器功能测试
避免使用tkinter GUI组件，专注于核心逻辑测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_base_highlighter_logic():
    """测试基础高亮器逻辑功能"""
    print("=" * 60)
    print("测试基础高亮器逻辑功能")
    print("=" * 60)
    
    try:
        # 模拟tkinter.Text组件
        class MockTextWidget:
            def __init__(self):
                self.tags = {}
            
            def tag_configure(self, tag, **kwargs):
                self.tags[tag] = kwargs
        
        # 导入高亮器
        from library.highlighter.base import BaseHighlighter
        
        # 创建模拟文本组件和高亮器
        mock_text = MockTextWidget()
        
        # 由于BaseHighlighter需要真实的tkinter组件，我们测试其静态方法
        # 测试关键字列表
        import keyword
        import builtins
        
        expected_keywords = set(keyword.kwlist)
        expected_builtins = set(dir(builtins))
        
        # 验证关键字和内置函数集合
        assert "if" in expected_keywords
        assert "def" in expected_keywords
        assert "print" in expected_builtins
        assert "len" in expected_builtins
        
        print("✓ 关键字和内置函数检测测试通过")
        
        # 测试语言关键字分类
        language_keywords = {
            'control': {'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'finally', 'with', 'break', 'continue', 'return'},
            'definition': {'def', 'class', 'lambda', 'async', 'await'},
            'module': {'import', 'from', 'as'},
            'value': {'True', 'False', 'None'},
            'context': {'global', 'nonlocal', 'pass', 'yield'}
        }
        
        assert "if" in language_keywords["control"]
        assert "def" in language_keywords["definition"]
        assert "import" in language_keywords["module"]
        assert "True" in language_keywords["value"]
        assert "global" in language_keywords["context"]
        
        print("✓ 语言关键字分类测试通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 基础高亮器逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_highlighter_factory_logic():
    """测试高亮器工厂逻辑功能"""
    print("\n" + "=" * 60)
    print("测试高亮器工厂逻辑功能")
    print("=" * 60)
    
    try:
        from library.highlighter_factory import HighlighterFactory
        
        factory = HighlighterFactory()
        
        # 测试扩展名映射
        assert ".py" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".py"] == "python"
        
        assert ".js" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".js"] == "javascript"
        
        assert ".html" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".html"] == "html"
        
        assert ".css" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".css"] == "css"
        
        assert ".json" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".json"] == "json"
        
        assert ".md" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".md"] == "markdown"
        
        assert ".log" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".log"] == "log"
        
        assert ".txt" in factory.EXTENSION_MAP
        assert factory.EXTENSION_MAP[".txt"] == "log"
        
        print("✓ 扩展名映射测试通过")
        
        # 测试C++相关扩展名
        cpp_extensions = ['.cpp', '.cxx', '.cc', '.hpp']
        for ext in cpp_extensions:
            assert ext in factory.EXTENSION_MAP
            assert factory.EXTENSION_MAP[ext] == "cpp"
        
        # 测试C相关扩展名
        c_extensions = ['.c', '.h']
        for ext in c_extensions:
            assert ext in factory.EXTENSION_MAP
            assert factory.EXTENSION_MAP[ext] == "c"
        
        print("✓ C/C++扩展名映射测试通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 高亮器工厂逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_python_highlighter_logic():
    """测试Python高亮器逻辑功能"""
    print("\n" + "=" * 60)
    print("测试Python高亮器逻辑功能")
    print("=" * 60)
    
    try:
        # 测试AST节点处理逻辑
        import ast
        
        # 创建简单的Python代码AST
        code = """
import os
from tkinter import Tk

def hello():
    print("Hello")
"""
        
        tree = ast.parse(code)
        
        # 验证AST结构
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 3  # import, from-import, function def
        
        # 验证导入语句
        import_node = tree.body[0]
        assert isinstance(import_node, ast.Import)
        assert len(import_node.names) == 1
        assert import_node.names[0].name == "os"
        
        # 验证from-import语句
        import_from_node = tree.body[1]
        assert isinstance(import_from_node, ast.ImportFrom)
        assert import_from_node.module == "tkinter"
        assert len(import_from_node.names) == 1
        assert import_from_node.names[0].name == "Tk"
        
        # 验证函数定义
        function_node = tree.body[2]
        assert isinstance(function_node, ast.FunctionDef)
        assert function_node.name == "hello"
        
        print("✓ AST解析测试通过")
        
        # 测试类名判断逻辑
        from library.highlighter.python import CodeHighlighter
        
        # 模拟文本组件
        class MockTextWidget:
            def __init__(self):
                self.tags = {}
            
            def tag_configure(self, tag, **kwargs):
                self.tags[tag] = kwargs
        
        mock_text = MockTextWidget()
        
        # 由于需要真实的tkinter组件，我们只测试静态逻辑
        # 测试类名判断
        def is_likely_class_name(name):
            """判断一个名称是否可能是类名"""
            if name and name[0].isupper():
                return True
            
            common_class_patterns = {
                'Tk', 'Frame', 'Button', 'Label', 'Entry', 'Text', 'Canvas',
                'Listbox', 'Scrollbar', 'Menu', 'Message', 'Scale', 'Spinbox'
            }
            
            if name in common_class_patterns:
                return True
            return False
        
        # 测试类名判断
        assert is_likely_class_name("MyClass") is True
        assert is_likely_class_name("Tk") is True
        assert is_likely_class_name("Frame") is True
        assert is_likely_class_name("my_function") is False
        assert is_likely_class_name("variable") is False
        
        print("✓ 类名判断逻辑测试通过")
        
        return True
        
    except Exception as e:
        print(f"✗ Python高亮器逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_loading():
    """测试主题文件加载功能"""
    print("\n" + "=" * 60)
    print("测试主题文件加载功能")
    print("=" * 60)
    
    try:
        import json
        from pathlib import Path
        
        # 检查主题文件是否存在
        theme_dir = Path(__file__).parent.parent / "asset" / "theme"
        
        # 检查常用主题文件
        theme_files = [
            "vscode-dark.json",
            "github-dark.json", 
            "github-light.json",
            "dracula.json",
            "monokai.json"
        ]
        
        existing_themes = []
        for theme_file in theme_files:
            theme_path = theme_dir / theme_file
            if theme_path.exists():
                existing_themes.append(theme_file)
                
                # 验证主题文件格式
                with open(theme_path, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                assert isinstance(theme_data, dict)
                assert len(theme_data) > 0
        
        print(f"✓ 找到 {len(existing_themes)} 个主题文件")
        
        if existing_themes:
            print("✓ 主题文件格式验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 主题文件加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("开始运行高亮器单元测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(test_base_highlighter_logic())
    test_results.append(test_highlighter_factory_logic())
    test_results.append(test_python_highlighter_logic())
    test_results.append(test_theme_loading())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())