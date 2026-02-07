import os
import time
import threading
from collections import OrderedDict

class FileHandleManager:
    """文件句柄管理器，用于管理和回收打开的文件句柄，避免泄漏"""
    
    def __init__(self, max_open_files=100, idle_timeout=300):
        """
        初始化文件句柄管理器
        
        Args:
            max_open_files: 最大同时打开的文件数量
            idle_timeout: 文件空闲超时时间（秒），超过该时间自动关闭
        """
        self.max_open_files = max_open_files
        self.idle_timeout = idle_timeout
        
        # 存储打开的文件句柄，使用OrderedDict保持访问顺序
        self._open_files = OrderedDict()  # {file_path: (file_handle, last_access_time)}
        
        # 锁，用于线程安全
        self._lock = threading.Lock()
        
        # 启动清理线程
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_idle_files, daemon=True)
        self._cleanup_thread.start()
    
    def open(self, file_path, mode='r', encoding=None):
        """
        打开文件，返回文件句柄
        
        Args:
            file_path: 文件路径
            mode: 打开模式
            encoding: 编码
            
        Returns:
            file_handle: 文件句柄
        """
        with self._lock:
            # 检查文件是否已经打开
            if file_path in self._open_files:
                file_handle, _ = self._open_files[file_path]
                # 更新访问时间
                self._open_files.move_to_end(file_path)
                self._open_files[file_path] = (file_handle, time.time())
                return file_handle
            
            # 检查是否超过最大打开文件数
            if len(self._open_files) >= self.max_open_files:
                # 关闭最久未使用的文件
                self._close_oldest_file()
            
            # 打开新文件
            file_handle = open(file_path, mode, encoding=encoding)
            # 记录文件句柄和访问时间
            self._open_files[file_path] = (file_handle, time.time())
            return file_handle
    
    def close(self, file_path):
        """
        关闭指定文件
        
        Args:
            file_path: 文件路径
        """
        with self._lock:
            if file_path in self._open_files:
                file_handle, _ = self._open_files.pop(file_path)
                try:
                    file_handle.close()
                except:
                    pass
    
    def close_all(self):
        """
        关闭所有打开的文件
        """
        with self._lock:
            for file_path, (file_handle, _) in self._open_files.items():
                try:
                    file_handle.close()
                except:
                    pass
            self._open_files.clear()
    
    def _close_oldest_file(self):
        """
        关闭最久未使用的文件
        """
        if self._open_files:
            # 移除并返回第一个元素（最久未使用）
            file_path, (file_handle, _) = self._open_files.popitem(last=False)
            try:
                file_handle.close()
            except:
                pass
    
    def _cleanup_idle_files(self):
        """
        定期清理空闲超时的文件
        """
        while self._running:
            time.sleep(60)  # 每分钟检查一次
            with self._lock:
                current_time = time.time()
                # 收集需要关闭的文件
                to_close = []
                for file_path, (_, last_access) in self._open_files.items():
                    if current_time - last_access > self.idle_timeout:
                        to_close.append(file_path)
                
                # 关闭空闲超时的文件
                for file_path in to_close:
                    self.close(file_path)
    
    def shutdown(self):
        """
        关闭管理器，清理所有资源
        """
        self._running = False
        self.close_all()
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=2)
    
    def get_open_file_count(self):
        """
        获取当前打开的文件数量
        
        Returns:
            int: 打开的文件数量
        """
        with self._lock:
            return len(self._open_files)

# 全局文件句柄管理器实例
_global_file_manager = None

def get_file_manager(max_open_files=100, idle_timeout=300):
    """获取全局文件句柄管理器"""
    global _global_file_manager
    if _global_file_manager is None:
        _global_file_manager = FileHandleManager(max_open_files, idle_timeout)
    return _global_file_manager

def shutdown_file_manager():
    """关闭全局文件句柄管理器"""
    global _global_file_manager
    if _global_file_manager:
        _global_file_manager.shutdown()
        _global_file_manager = None