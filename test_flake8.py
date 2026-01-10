#!/usr/bin/env python3
"""
测试flake8代码检查功能
"""

# 测试代码：包含多个flake8错误

def test_function():
    x=1  # 缺少空格
    y = 2
    print(x,y)  # 缺少空格
    
    if x>y:  # 缺少空格
        print("x is greater than y")
    
    # 未使用的变量
    z = 3
    
    # 行太长
    very_long_variable_name_that_should_cause_line_too_long_error = 1234567890123456789012345678901234567890123456789012345678901234567890
    
    return x + y

# 缩进错误
    def nested_function():
        return "nested"

# 缺少文档字符串
class TestClass:
    pass

# 未使用的导入
import os
import sys
