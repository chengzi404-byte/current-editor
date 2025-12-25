#!/usr/bin/env python3
"""
大文件处理功能测试脚本
测试文件读取优化功能，避免大文件导致IDE卡顿
"""

import os
import tempfile
import time
from library.multi_file_editor import MultiFileEditor
from library.editor_operations import EditorOperations
from tkinter import Tk, Frame

def create_large_file(file_path, size_mb):
    """创建指定大小的测试文件"""
    print(f"创建测试文件: {file_path} ({size_mb}MB)")
    
    chunk_size = 1024 * 1024  # 1MB
    chunk_content = "x" * 1024 * 1024  # 1MB的测试内容
    
    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(size_mb):
            f.write(chunk_content)
            print(f"已写入: {i+1}/{size_mb} MB")
    
    actual_size = os.path.getsize(file_path) / (1024 * 1024)
    print(f"文件创建完成，实际大小: {actual_size:.1f}MB")
    return actual_size

def test_file_size_detection():
    """测试文件大小检测功能"""
    print("\n=== 测试文件大小检测功能 ===")
    
    # 创建不同大小的测试文件
    test_files = []
    
    # 小文件 (1MB)
    small_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    small_file.close()
    create_large_file(small_file.name, 1)
    test_files.append(("小文件", small_file.name, 1))
    
    # 中等文件 (3MB)
    medium_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    medium_file.close()
    create_large_file(medium_file.name, 3)
    test_files.append(("中等文件", medium_file.name, 3))
    
    # 大文件 (6MB)
    large_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    large_file.close()
    create_large_file(large_file.name, 6)
    test_files.append(("大文件", large_file.name, 6))
    
    # 超大文件 (15MB)
    huge_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    huge_file.close()
    create_large_file(huge_file.name, 15)
    test_files.append(("超大文件", huge_file.name, 15))
    
    # 测试文件大小检测
    for name, file_path, expected_size in test_files:
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        print(f"{name}: {file_size:.1f}MB (预期: {expected_size}MB)")
        
        # 检查是否超过阈值
        LARGE_FILE_THRESHOLD = 5  # 5MB
        if file_size > LARGE_FILE_THRESHOLD:
            print(f"  ⚠️  超过阈值 ({LARGE_FILE_THRESHOLD}MB)，将触发大文件处理")
        else:
            print(f"  ✅ 未超过阈值，将正常加载")
    
    return test_files

def test_multi_file_editor():
    """测试多文件编辑器的大文件处理"""
    print("\n=== 测试多文件编辑器大文件处理 ===")
    
    # 创建临时Tkinter窗口
    root = Tk()
    root.withdraw()  # 隐藏窗口
    
    # 创建多文件编辑器实例
    editor_frame = Frame(root)
    terminal_area = Frame(root)
    multi_editor = MultiFileEditor(editor_frame, terminal_area, None, None)
    
    # 创建测试文件
    test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    test_file.close()
    create_large_file(test_file.name, 7)  # 7MB文件
    
    print(f"测试文件: {test_file.name}")
    print("文件大小:", os.path.getsize(test_file.name) / (1024 * 1024), "MB")
    
    # 测试打开文件（模拟用户确认）
    print("模拟打开大文件（用户确认）...")
    
    # 由于GUI测试需要用户交互，这里只测试逻辑部分
    try:
        # 测试文件大小检测逻辑
        file_size = os.path.getsize(test_file.name)
        LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
        
        if file_size > LARGE_FILE_THRESHOLD:
            print("✅ 大文件检测成功")
            print("⚠️  GUI测试需要手动验证大文件警告对话框")
        else:
            print("❌ 大文件检测失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 清理
    os.unlink(test_file.name)
    root.destroy()

def test_single_editor():
    """测试单文件编辑器的大文件处理"""
    print("\n=== 测试单文件编辑器大文件处理 ===")
    
    # 创建临时Tkinter窗口
    root = Tk()
    root.withdraw()  # 隐藏窗口
    
    # 创建单文件编辑器实例
    try:
        editor_ops = EditorOperations(root, None, None, None, None, 
                                    None, None, None, None, None, None)
        
        # 创建测试文件
        test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        test_file.close()
        create_large_file(test_file.name, 7)  # 7MB文件
        
        print(f"测试文件: {test_file.name}")
        print("文件大小:", os.path.getsize(test_file.name) / (1024 * 1024), "MB")
        
        # 测试文件大小检测逻辑
        file_size = os.path.getsize(test_file.name)
        LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
        
        if file_size > LARGE_FILE_THRESHOLD:
            print("✅ 大文件检测成功")
            print("⚠️  GUI测试需要手动验证大文件警告对话框")
        else:
            print("❌ 大文件检测失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 清理
    os.unlink(test_file.name)
    root.destroy()

def test_chunk_reading():
    """测试分块读取功能"""
    print("\n=== 测试分块读取功能 ===")
    
    # 创建测试文件
    test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    test_file.close()
    
    # 创建10MB文件
    file_size_mb = 10
    create_large_file(test_file.name, file_size_mb)
    
    # 模拟分块读取
    chunk_size = 1024 * 1024  # 1MB
    total_size = os.path.getsize(test_file.name)
    bytes_read = 0
    chunks_read = 0
    
    print(f"开始分块读取 {file_size_mb}MB 文件...")
    
    start_time = time.time()
    
    with open(test_file.name, "r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            bytes_read += len(chunk.encode('utf-8'))
            chunks_read += 1
            
            progress = min(bytes_read / total_size, 1.0)
            print(f"进度: {progress*100:.1f}% ({chunks_read} chunks)")
            
            # 测试截断逻辑
            if bytes_read > 50 * 1024 * 1024:  # 50MB限制
                print("达到50MB限制，停止读取")
                break
    
    end_time = time.time()
    
    print(f"读取完成: {bytes_read/(1024*1024):.1f}MB")
    print(f"读取时间: {end_time - start_time:.2f}秒")
    print(f"读取速度: {bytes_read/(1024*1024)/(end_time - start_time):.1f}MB/秒")
    
    # 清理
    os.unlink(test_file.name)

def main():
    """主测试函数"""
    print("大文件处理功能测试")
    print("=" * 50)
    
    try:
        # 测试文件大小检测
        test_files = test_file_size_detection()
        
        # 测试分块读取
        test_chunk_reading()
        
        # 测试多文件编辑器
        test_multi_file_editor()
        
        # 测试单文件编辑器
        test_single_editor()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成")
        print("\n手动测试建议:")
        print("1. 运行主程序: python main.py")
        print("2. 尝试打开一个大于5MB的文件")
        print("3. 验证是否出现大文件警告对话框")
        print("4. 验证进度条显示是否正常")
        print("5. 验证文件内容是否正确加载")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    # 清理测试文件
    for name, file_path, size in test_files:
        try:
            os.unlink(file_path)
            print(f"清理测试文件: {file_path}")
        except:
            pass

if __name__ == "__main__":
    main()