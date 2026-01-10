#!/usr/bin/env python3
"""
测试悬停提示功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 简单的测试代码，包含一个明显的错误
x = 1
x += 2

# 未使用的变量（这会触发flake8的F841警告）
y = 3

# 打印结果
print(f"x = {x}")
