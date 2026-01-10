"""
简单的高亮器功能测试
不依赖pytest，直接验证高亮器核心功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_base_highlighter():
    """测试基础高亮器功能"""
    print("=" * 60)
    print("测试基础高亮器功能")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from library.highlighter.base import BaseHighlighter
        
        # 创建窗口和文本组件
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        text_widget = tk.Text(root)
        highlighter = BaseHighlighter(text_widget)
        
        # 测试基本属性
        assert highlighter.text_widget == text_widget
        assert highlighter.theme_name == "vscode-dark"
        assert isinstance(highlighter.syntax_colors, dict)
        assert len(highlighter.syntax_colors) > 0
        
        # 测试关键字检测
        assert "if" in highlighter.keywords
        assert "def" in highlighter.keywords
        
        # 测试内置函数检测
        assert "print" in highlighter.builtins
        assert "len" in highlighter.builtins
        
        print("✓ 基础高亮器初始化测试通过")
        
        # 测试主题颜色加载
        colors = highlighter._load_theme_colors("vscode-dark")
        assert isinstance(colors, dict)
        print("✓ 主题颜色加载测试通过")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ 基础高亮器测试失败: {e}")
        return False

def test_python_highlighter():
    """测试Python高亮器功能"""
    print("\n" + "=" * 60)
    print("测试Python高亮器功能")
    print("=" * 60)
    
    try:
        import tkinter as tk
        import ast
        from library.highlighter.python import CodeHighlighter
        
        # 创建窗口和文本组件
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        text_widget = tk.Text(root)
        highlighter = CodeHighlighter(text_widget)
        
        # 测试Python特定属性
        assert isinstance(highlighter.imported_modules, set)
        assert isinstance(highlighter.imported_symbols, dict)
        
        # 测试Python特定颜色设置
        assert "f_string" in highlighter.syntax_colors
        assert "exception" in highlighter.syntax_colors
        
        print("✓ Python高亮器初始化测试通过")
        
        # 测试类名判断
        assert highlighter._is_likely_class_name("MyClass") is True
        assert highlighter._is_likely_class_name("my_function") is False
        print("✓ 类名判断测试通过")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Python高亮器测试失败: {e}")
        return False

def test_highlighter_factory():
    """测试高亮器工厂功能"""
    print("\n" + "=" * 60)
    print("测试高亮器工厂功能")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from library.highlighter_factory import HighlighterFactory
        
        # 创建窗口和文本组件
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        text_widget = tk.Text(root)
        factory = HighlighterFactory()
        
        # 测试扩展名映射
        assert ".py" in factory.EXTENSION_MAP
        assert ".js" in factory.EXTENSION_MAP
        assert ".html" in factory.EXTENSION_MAP
        
        # 测试Python文件高亮器创建
        highlighter = factory.create_highlighter(text_widget, "test.py")
        assert highlighter is not None
        print("✓ Python高亮器创建测试通过")
        
        # 测试未知扩展名（应该回退到默认高亮器）
        highlighter = factory.create_highlighter(text_widget, "test.unknown")
        assert highlighter is not None
        print("✓ 未知扩展名回退测试通过")
        
        # 测试没有文件路径的情况
        highlighter = factory.create_highlighter(text_widget)
        assert highlighter is not None
        print("✓ 无文件路径高亮器创建测试通过")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ 高亮器工厂测试失败: {e}")
        return False

def test_highlighter_integration():
    """测试高亮器集成功能"""
    print("\n" + "=" * 60)
    print("测试高亮器集成功能")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from library.highlighter.python import CodeHighlighter
        
        # 创建窗口和文本组件
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        text_widget = tk.Text(root)
        highlighter = CodeHighlighter(text_widget)
        
        # 插入Python代码
        python_code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        text_widget.insert("1.0", python_code)
        
        # 模拟高亮过程
        added_tags = []
        
        def mock_add_tag(tag, start, end):
            added_tags.append((tag, start, end))
        
        highlighter._add_tag = mock_add_tag
        
        # 执行高亮
        highlighter.highlight()
        
        # 验证高亮结果
        assert len(added_tags) > 0
        
        # 检查是否有关键字高亮
        keyword_tags = [tag for tag, start, end in added_tags if tag == 'keyword']
        assert len(keyword_tags) > 0
        
        print("✓ 高亮器集成测试通过")
        print(f"  添加了 {len(added_tags)} 个高亮标签")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ 高亮器集成测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始运行高亮器单元测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(test_base_highlighter())
    test_results.append(test_python_highlighter())
    test_results.append(test_highlighter_factory())
    test_results.append(test_highlighter_integration())
    
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