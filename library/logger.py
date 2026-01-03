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
        self.max_single_file_size = 50 * 1024  # 单文件上限 50KB
        self.max_total_size = 1 * 1024 * 1024  # 文件夹总大小上限 1MB
        self.backup_count = 20  # 最多20个备份文件
        
        # 确保日志目录存在
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)
        
        # 启动日志处理线程
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()
        
        # 启动自动清理线程，每小时检查一次
        self.cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def _get_log_file_path(self, date_str=None, backup_number=0):
        """获取按日期和备份号分块的日志文件路径"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if backup_number == 0:
            return self.log_dir / f"editor_{date_str}.log"
        else:
            return self.log_dir / f"editor_{date_str}.{backup_number}.log"
    
    def _get_current_backup_number(self, date_str):
        """获取当前日期的日志文件的最大备份号"""
        log_files = list(self.log_dir.glob(f"editor_{date_str}*.log"))
        max_backup = 0
        
        for log_file in log_files:
            filename = log_file.stem
            if filename == f"editor_{date_str}":
                continue
            try:
                # 提取备份号，格式为 editor_2023-01-01.1
                backup_str = filename.split(".")[-1]
                backup_num = int(backup_str)
                if backup_num > max_backup:
                    max_backup = backup_num
            except ValueError:
                continue
        
        return max_backup
    
    def _calculate_total_log_size(self):
        """计算日志文件夹的总大小"""
        total_size = 0
        for log_file in self.log_dir.glob("editor_*.log*"):
            try:
                total_size += log_file.stat().st_size
            except OSError:
                continue
        return total_size
    
    def _check_total_size(self):
        """检查日志文件夹总大小，超过限制则清理最旧的文件"""
        total_size = self._calculate_total_log_size()
        
        while total_size > self.max_total_size:
            # 获取所有日志文件并按修改时间排序（最旧的先删除）
            log_files = []
            for log_file in self.log_dir.glob("editor_*.log*"):
                try:
                    mtime = log_file.stat().st_mtime
                    log_files.append((mtime, log_file))
                except OSError:
                    continue
            
            if not log_files:
                break
            
            # 按修改时间排序，最旧的在前面
            log_files.sort(key=lambda x: x[0])
            
            # 删除最旧的文件
            oldest_file = log_files[0][1]
            try:
                oldest_size = oldest_file.stat().st_size
                oldest_file.unlink()
                total_size -= oldest_size
                print(f"已清理旧日志文件: {oldest_file}")
            except OSError as e:
                print(f"清理日志文件失败: {e}")
                break
    
    def _process_logs(self):
        """处理日志队列的线程函数"""
        current_date = None
        log_file = None
        log_file_handle = None
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        while self.running:
            try:
                # 从队列获取日志记录，设置超时避免无限阻塞
                log_record = self.log_queue.get(timeout=1.0)
                
                # 检查是否需要切换日志文件
                today = datetime.now().strftime("%Y-%m-%d")
                if current_date != today:
                    # 关闭当前文件
                    if log_file_handle:
                        log_file_handle.close()
                        log_file_handle = None
                    
                    # 设置新日期和文件路径
                    current_date = today
                    log_file = self._get_log_file_path(today)
                
                # 检查当前文件大小
                if log_file_handle:
                    # 检查文件大小
                    try:
                        current_size = log_file_handle.tell()
                        if current_size >= self.max_single_file_size:
                            # 文件超过大小限制，关闭并轮换
                            log_file_handle.close()
                            log_file_handle = None
                            
                            # 计算新的备份号
                            backup_num = self._get_current_backup_number(current_date) + 1
                            
                            # 重命名当前文件为备份文件
                            backup_path = self._get_log_file_path(current_date, backup_num)
                            log_file.rename(backup_path)
                            
                            # 检查总大小，超过则清理
                            self._check_total_size()
                    except OSError:
                        # 文件可能已被删除，重新打开
                        log_file_handle.close()
                        log_file_handle = None
                
                # 如果文件未打开，打开它
                if not log_file_handle:
                    log_file_handle = open(log_file, 'a', encoding='utf-8')
                
                # 写入日志
                formatted_log = formatter.format(log_record)
                log_file_handle.write(formatted_log + '\n')
                log_file_handle.flush()  # 确保写入磁盘
                
                self.log_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                # 记录错误但继续运行
                print(f"日志处理错误: {e}")
                # 尝试关闭文件
                if log_file_handle:
                    try:
                        log_file_handle.close()
                    except:
                        pass
                    log_file_handle = None
                continue
        
        # 清理资源
        if log_file_handle:
            try:
                log_file_handle.close()
            except:
                pass
    
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