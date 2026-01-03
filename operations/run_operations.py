"""
运行操作模块
处理代码运行相关操作
"""

import subprocess
import sys
import threading
from library.api import Settings


class RunOperations:
    """
    运行操作类
    处理代码运行相关操作
    """
    
    def __init__(self, codearea, printarea, inputarea=None):
        """
        初始化运行操作类
        
        Args:
            codearea: 代码编辑区域
            printarea: 输出区域
            inputarea: 输入区域（可选）
        """
        self.codearea = codearea
        self.printarea = printarea
        self.inputarea = inputarea
    
    def run(self):
        """
        运行Python文件
        """
        def execute_in_thread():
            """在线程中执行代码"""
            try:
                runtool = subprocess.Popen(
                    [sys.executable, Settings.Editor.file_path()],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                input_data = b""
                if self.inputarea:
                    input_data = self.inputarea.get(0.0, "end").encode('utf-8')
                
                stdout, stderr = runtool.communicate(input=input_data)

                self.printarea.after(0, lambda: self._update_printarea(stdout, stderr))
            except Exception as e:
                self.printarea.after(0, lambda: self.printarea.insert("end", f"执行错误: {str(e)}\n"))
        
        threading.Thread(target=execute_in_thread, daemon=True).start()
    
    def _update_printarea(self, stdout, stderr):
        """
        更新输出区域
        
        Args:
            stdout: 标准输出
            stderr: 标准错误
        """
        self.printarea.delete(0.0, "end")
        self.printarea.insert("end", f"%Run {Settings.Editor.file_path()}\n")
        self.printarea.insert("end", f"------------------Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}------------------\n")
        self.printarea.insert("end", stdout.decode(errors="replace"))
        self.printarea.insert("end", stderr.decode(errors="replace"))
        self.printarea.insert("end", "\n>>> ")
    
    def clear_printarea(self):
        """
        清除输出区域
        """
        self.printarea.delete(0.0, "end")
