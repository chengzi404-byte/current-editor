import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from library.api import Settings
from library.logger import get_logger, shutdown_logger

def setup_environment():
    os.chdir(Path(__file__).parent)

def main():
    setup_environment()
    
    logger = get_logger()
    logger.info("程序启动")
    
    def handle_global_exception(exctype, value, traceback_obj):
        logger.exception("程序崩溃")
        logger.error(f"异常类型: {exctype.__name__}")
        logger.error(f"异常信息: {value}")
        
        if hasattr(logger, 'export_crash_logs'):
            logger.normal_exit = False
            logger.export_crash_logs()
        
        shutdown_logger(normal_exit=False)
        
        sys.__excepthook__(exctype, value, traceback_obj)
    
    sys.excepthook = handle_global_exception
    
    app = QApplication(sys.argv)
    app.setApplicationName("Current Editor")
    app.setOrganizationName("CurrentEditor")
    
    window = MainWindow()
    window.show()
    
    logger.info("程序初始化完成，准备启动主循环")
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"程序主循环异常: {str(e)}")
        shutdown_logger(normal_exit=False)

if __name__ == "__main__":
    main()
