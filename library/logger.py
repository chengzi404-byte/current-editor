import logging
import os
from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self, name: str = "CurrentEditor", log_dir: str = "./logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.normal_exit = True
    
    def debug(self, msg: str) -> None:
        self.logger.debug(msg)
    
    def info(self, msg: str) -> None:
        self.logger.info(msg)
    
    def warning(self, msg: str) -> None:
        self.logger.warning(msg)
    
    def error(self, msg: str) -> None:
        self.logger.error(msg)
    
    def exception(self, msg: str) -> None:
        self.logger.exception(msg)
    
    def export_crash_logs(self) -> None:
        crash_log = self.log_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        try:
            with open(crash_log, 'w', encoding='utf-8') as f:
                for handler in self.logger.handlers:
                    if hasattr(handler, 'baseFilename'):
                        log_file = handler.baseFilename
                        if os.path.exists(log_file):
                            with open(log_file, 'r', encoding='utf-8') as lf:
                                f.write(lf.read())
            self.info(f"崩溃日志已导出到: {crash_log}")
        except Exception as e:
            self.error(f"导出崩溃日志失败: {str(e)}")

_logger = None

def get_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger

def shutdown_logger(normal_exit: bool = True) -> None:
    global _logger
    if _logger:
        _logger.normal_exit = normal_exit
        if not normal_exit:
            _logger.export_crash_logs()
        for handler in _logger.logger.handlers:
            handler.close()
            _logger.logger.removeHandler(handler)
        _logger = None
