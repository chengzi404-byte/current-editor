import logging
import os
import pathlib
import threading
import queue
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

class AsyncLogHandler:
    """异步日志处理器"""
    
    def __init__(self, log_dir="./logs", max_queue_size=1000, cleanup_days=10):
        self.log_dir = pathlib.Path(log_dir)
        self.max_queue_size = max_queue_size
        self.cleanup_days = cleanup_days
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.running = True
        
        # 确保日志目录存在
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)
        
        # 启动日志处理线程
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()
        
        # 启动自动清理线程
        self.cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def _get_log_file_path(self, date_str=None):
        """获取按日期分块的日志文件路径"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"editor_{date_str}.log"
    
    def _process_logs(self):
        """处理日志队列的线程函数"""
        current_date = None
        current_handler = None
        
        while self.running:
            try:
                # 从队列获取日志记录，设置超时避免无限阻塞
                log_record = self.log_queue.get(timeout=1.0)
                
                # 检查是否需要切换日志文件
                today = datetime.now().strftime("%Y-%m-%d")
                if current_date != today:
                    if current_handler:
                        current_handler.close()
                    
                    log_file = self._get_log_file_path(today)
                    current_handler = RotatingFileHandler(
                        str(log_file), 
                        maxBytes=10 * 1024 * 1024,  # 10MB
                        backupCount=5,
                        encoding='utf-8'
                    )
                    formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
                    )
                    current_handler.setFormatter(formatter)
                    current_date = today
                
                # 写入日志
                if current_handler:
                    current_handler.emit(log_record)
                
                self.log_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                # 记录错误但继续运行
                print(f"日志处理错误: {e}")
                continue
        
        # 清理资源
        if current_handler:
            current_handler.close()
    
    def _auto_cleanup(self):
        """自动清理过期日志文件的线程函数"""
        while self.running:
            try:
                # 每天检查一次
                time.sleep(24 * 60 * 60)  # 24小时
                
                cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)
                
                for log_file in self.log_dir.glob("editor_*.log*"):
                    try:
                        # 从文件名提取日期
                        filename = log_file.stem
                        if filename.startswith("editor_"):
                            date_str = filename[7:]  # 移除"editor_"前缀
                            file_date = datetime.strptime(date_str, "%Y-%m-%d")
                            
                            if file_date < cutoff_date:
                                log_file.unlink()
                                print(f"已清理过期日志文件: {log_file}")
                    except (ValueError, IndexError):
                        # 文件名格式不正确，跳过
                        continue
                        
            except Exception as e:
                print(f"日志清理错误: {e}")
    
    def enqueue_log(self, record):
        """将日志记录放入队列"""
        try:
            # 如果队列已满，丢弃最旧的记录
            if self.log_queue.full():
                try:
                    self.log_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self.log_queue.put_nowait(record)
            return True
        except Exception:
            return False
    
    def shutdown(self):
        """关闭日志处理器"""
        self.running = False
        self.executor.shutdown(wait=True)
        
        # 等待队列处理完成
        self.log_queue.join()

class AsyncLogger:
    """异步日志记录器"""
    
    def __init__(self, name='Phoenix Editor', log_dir="./logs", level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建异步处理器
        self.async_handler = AsyncLogHandler(log_dir)
        
        # 添加自定义处理器来捕获日志记录
        class CustomHandler(logging.Handler):
            def __init__(self, async_handler):
                super().__init__()
                self.async_handler = async_handler
            
            def emit(self, record):
                self.async_handler.enqueue_log(record)
        
        self.logger.addHandler(CustomHandler(self.async_handler))
        
    def _make_log_record(self, level, msg, *args, **kwargs):
        """创建日志记录"""
        # 提取文件名和行号信息，使用不同的字段名避免冲突
        source_file = kwargs.pop('source_file', '')
        source_line = kwargs.pop('source_line', 0)
        
        return self.logger.makeRecord(
            self.logger.name, level, 
            source_file, source_line,
            msg, args, None, **kwargs
        )
    
    def debug(self, msg, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(msg, *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        """记录异常信息"""
        self.logger.exception(msg, *args, **kwargs)
    
    def shutdown(self):
        """关闭日志记录器"""
        self.async_handler.shutdown()

def setup_logger(log_dir="./logs", name='Phoenix Editor', level=logging.DEBUG):
    """设置异步日志记录器"""
    return AsyncLogger(name, log_dir, level)

# 全局日志记录器实例
_global_logger = None

def get_logger():
    """获取全局日志记录器"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logger()
    return _global_logger

def shutdown_logger():
    """关闭全局日志记录器"""
    global _global_logger
    if _global_logger:
        _global_logger.shutdown()
        _global_logger = None