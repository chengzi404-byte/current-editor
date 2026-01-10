#!/usr/bin/env python3
"""
测试symbol_checker.py的flake8功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from library.static_checker.symbol_checker import SymbolChecker

# 读取测试文件内容
with open('test_flake8.py', 'r', encoding='utf-8') as f:
    test_code = f.read()

# 创建符号检查器
checker = SymbolChecker('python')

# 执行检查
errors = checker.check(test_code, 'test_flake8.py')

# 打印结果
print(f"检测到 {len(errors)} 个错误:")
for error in errors:
    print(f"行 {error.line}, 列 {error.column} - {error.end_line}:{error.end_column} - {error.error_type} - {error.error_message}")
