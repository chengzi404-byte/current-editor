#!/usr/bin/env python3
"""
测试所有语言高亮器的导入符号识别功能
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import importlib.util

def load_highlighter(highlighter_name):
    """动态加载高亮器模块"""
    highlighter_path = os.path.join(
        os.path.dirname(__file__), 
        'library', 
        'highlighter', 
        f"{highlighter_name}.py"
    )
    
    spec = importlib.util.spec_from_file_location(highlighter_name, highlighter_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return getattr(module, 'CodeHighlighter')

# 动态加载高亮器类
try:
    PythonHighlighter = load_highlighter('python')
    JavaHighlighter = load_highlighter('java')
    CppHighlighter = load_highlighter('cpp')
    RustHighlighter = load_highlighter('rust')
    CHighlighter = load_highlighter('c')
    SwiftHighlighter = load_highlighter('swift')
    KotlinHighlighter = load_highlighter('kotlin')
    GoHighlighter = load_highlighter('go')
    TypeScriptHighlighter = load_highlighter('typescript')
except Exception as e:
    print(f"加载高亮器失败: {e}")
    sys.exit(1)

def test_python_highlighter():
    """测试Python高亮器"""
    print("=== 测试Python高亮器 ===")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("Python高亮测试")
    
    # 创建文本区域
    text_widget = tk.Text(root, width=80, height=20)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # 创建高亮器
    highlighter = PythonHighlighter(text_widget)
    
    # 测试代码
    test_code = '''# Python导入测试
import os
import sys
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

# 使用导入的符号
path = os.path.join("test", "file.txt")
sys.exit(0)

counter = Counter([1,2,3])
dd = defaultdict(list)

arr = np.array([1,2,3])
df = pd.DataFrame({"col": [1,2,3]})

items: List[int] = [1,2,3]
mapping: Dict[str, int] = {"a": 1}
result: Optional[str] = None
'''
    
    text_widget.insert("1.0", test_code)
    
    # 应用高亮
    highlighter.highlight()
    
    # 检查导入的符号
    print("Python高亮器测试完成")
    print(f"导入的模块: {highlighter.imported_modules}")
    print(f"导入的符号: {highlighter.imported_symbols}")
    
    root.destroy()
    return True

def test_java_highlighter():
    """测试Java高亮器"""
    print("\n=== 测试Java高亮器 ===")
    
    root = tk.Tk()
    root.title("Java高亮测试")
    
    text_widget = tk.Text(root, width=80, height=20)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    highlighter = JavaHighlighter(text_widget)
    
    test_code = '''// Java导入测试
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.io.*;
import static java.lang.Math.PI;
import static java.lang.System.out;

public class Test {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>();
        Map<String, Integer> map = new HashMap<>();
        
        out.println("Hello World");
        double area = PI * 10 * 10;
        
        try {
            FileInputStream fis = new FileInputStream("test.txt");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
'''
    
    text_widget.insert("1.0", test_code)
    highlighter.highlight()
    
    print("Java高亮器测试完成")
    print(f"导入的包: {highlighter.imported_packages}")
    print(f"导入的类: {highlighter.imported_classes}")
    
    root.destroy()
    return True

def test_cpp_highlighter():
    """测试C++高亮器"""
    print("\n=== 测试C++高亮器 ===")
    
    root = tk.Tk()
    root.title("C++高亮测试")
    
    text_widget = tk.Text(root, width=80, height=20)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    highlighter = CppHighlighter(text_widget)
    
    test_code = '''// C++导入测试
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include "custom_header.h"

using namespace std;

int main() {
    vector<string> names = {"Alice", "Bob"};
    map<string, int> scores;
    
    cout << "Hello World" << endl;
    
    string input;
    cin >> input;
    
    return 0;
}
'''
    
    text_widget.insert("1.0", test_code)
    highlighter.highlight()
    
    print("C++高亮器测试完成")
    print(f"包含的头文件: {highlighter.included_headers}")
    print(f"导入的符号: {highlighter.imported_symbols}")
    
    root.destroy()
    return True

def test_rust_highlighter():
    """测试Rust高亮器"""
    print("\n=== 测试Rust高亮器 ===")
    
    root = tk.Tk()
    root.title("Rust高亮测试")
    
    text_widget = tk.Text(root, width=80, height=20)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    highlighter = RustHighlighter(text_widget)
    
    test_code = '''// Rust导入测试
use std::collections::HashMap;
use std::io::{self, Read, Write};
use std::fs::File;
use serde::{Deserialize, Serialize};
use tokio::time::sleep;

fn main() {
    let mut map = HashMap::new();
    map.insert("key", "value");
    
    let mut file = File::open("test.txt").unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    
    println!("Hello World");
    
    #[derive(Serialize, Deserialize)]
    struct Data {
        name: String,
        value: i32,
    }
}
'''
    
    text_widget.insert("1.0", test_code)
    highlighter.highlight()
    
    print("Rust高亮器测试完成")
    print(f"导入的crate: {highlighter.imported_crates}")
    print(f"导入的符号: {highlighter.imported_symbols}")
    
    root.destroy()
    return True

def test_all_highlighters():
    """测试所有高亮器"""
    print("开始测试所有语言高亮器的导入符号识别功能...")
    
    results = []
    
    try:
        results.append(("Python", test_python_highlighter()))
    except Exception as e:
        print(f"Python高亮器测试失败: {e}")
        results.append(("Python", False))
    
    try:
        results.append(("Java", test_java_highlighter()))
    except Exception as e:
        print(f"Java高亮器测试失败: {e}")
        results.append(("Java", False))
    
    try:
        results.append(("C++", test_cpp_highlighter()))
    except Exception as e:
        print(f"C++高亮器测试失败: {e}")
        results.append(("C++", False))
    
    try:
        results.append(("Rust", test_rust_highlighter()))
    except Exception as e:
        print(f"Rust高亮器测试失败: {e}")
        results.append(("Rust", False))
    
    # 统计结果
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"成功: {success_count}/{total_count}")
    
    for language, result in results:
        status = "✓ 成功" if result else "✗ 失败"
        print(f"{language}: {status}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_all_highlighters()
    if success:
        print("\n🎉 所有高亮器测试通过！")
    else:
        print("\n⚠️ 部分高亮器测试失败，请检查实现。")
    
    sys.exit(0 if success else 1)