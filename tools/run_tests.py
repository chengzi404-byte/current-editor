#!/usr/bin/env python3
"""
一键测试脚本
运行项目的所有测试
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_and_install_pytest():
    """检查并安装pytest"""
    print("\n[2] 检查pytest安装...")
    try:
        # 检查pytest是否已安装
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True, 
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ pytest已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ pytest未安装，正在安装...")
            
            # 安装pytest
            install_result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest"],
                capture_output=True, 
                text=True,
                check=False
            )
            
            if install_result.returncode == 0:
                print("✅ pytest安装成功")
                return True
            else:
                print("❌ pytest安装失败:")
                print(install_result.stderr)
                return False
                
    except Exception as e:
        print(f"❌ 检查/安装pytest时出错: {e}")
        return False


def run_tests():
    """运行项目的所有测试"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("=" * 60)
    print("Current Editor 测试脚本")
    print("=" * 60)
    
    # 检查Python环境
    print("\n[1] 检查Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Python版本: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ Python未找到，请确保已安装Python 3.x")
        return 1
    except Exception as e:
        print(f"❌ 检查Python环境时出错: {e}")
        return 1
    
    # 检查并安装pytest
    if not check_and_install_pytest():
        print("\n❌ 无法继续测试，请手动安装pytest")
        return 1
    
    # 运行测试
    print("\n[3] 运行所有测试...")
    print("=" * 40)
    
    start_time = time.time()
    
    try:
        # 使用pytest运行所有测试
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test/", "-v"],
            check=False, 
            text=True,
            capture_output=True
        )
        
        # 输出测试结果
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  测试警告:")
            print(result.stderr)
        
        # 计算测试时间
        end_time = time.time()
        test_time = end_time - start_time
        
        print("\n" + "=" * 40)
        if result.returncode == 0:
            print(f"✅ 所有测试通过！")
        else:
            print(f"❌ 测试失败！")
        
        print(f"测试耗时: {test_time:.2f} 秒")
        print("=" * 60)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 运行测试时出错: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)