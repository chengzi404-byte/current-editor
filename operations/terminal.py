"""
终端模块
负责处理终端相关的所有功能，包括命令执行、输出显示和操作系统适配
"""

import subprocess
import sys
import threading
from i18n import t


class TerminalOperations:
    """
    终端操作类
    处理终端相关的所有功能，包括命令执行、输出显示和操作系统适配
    """
    
    def __init__(self, printarea, commandarea=None):
        """
        初始化终端操作类
        
        Args:
            printarea: 输出区域
            commandarea: 命令输入区域（可选）
        """
        self.printarea = printarea
        self.commandarea = commandarea
        self.current_process = None
        self.is_windows = sys.platform.startswith('win')
        self.is_macos = sys.platform == 'darwin'
        self.is_linux = sys.platform.startswith('linux')
    
    def execute_command(self, command, show_prompt=True):
        """
        执行命令
        
        Args:
            command: 要执行的命令
            show_prompt: 是否显示命令提示符
        """
        def execute_in_thread():
            """在线程中执行命令"""
            try:
                if show_prompt:
                    self.printarea.after(0, lambda: self.printarea.insert("end", f">>> {command}\n"))
                
                # 根据操作系统选择不同的命令执行方式
                if self.is_windows:
                    # Windows系统使用cmd.exe执行命令
                    process = subprocess.Popen(
                        ["cmd.exe", "/c", command],
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        shell=False,
                        text=True,
                        universal_newlines=True
                    )
                else:
                    # macOS和Linux系统使用shell执行命令
                    process = subprocess.Popen(
                        command,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        shell=True,
                        text=True,
                        universal_newlines=True
                    )
                
                self.current_process = process
                
                # 读取输出
                stdout, stderr = process.communicate()
                
                # 在UI线程中更新输出
                self.printarea.after(0, lambda: self._update_output(stdout, stderr))
                
            except Exception as e:
                error_msg = f"{t('execution_error')}: {str(e)}\n"
                self.printarea.after(0, lambda: self.printarea.insert("end", error_msg))
        
        threading.Thread(target=execute_in_thread, daemon=True).start()
    
    def run_python_file(self, file_path, input_data=None):
        """
        运行Python文件
        
        Args:
            file_path: Python文件路径
            input_data: 输入数据（可选）
        """
        def execute_in_thread():
            """在线程中执行Python文件"""
            try:
                # 构建Python命令
                python_cmd = [sys.executable, file_path]
                
                # 在UI线程中显示执行信息
                self.printarea.after(0, lambda: self._show_python_exec_info(file_path))
                
                # 执行Python文件
                process = subprocess.Popen(
                    python_cmd,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    shell=False,
                    text=True,
                    universal_newlines=True
                )
                
                self.current_process = process
                
                # 读取输出
                stdout, stderr = process.communicate(input=input_data)
                
                # 在UI线程中更新输出
                self.printarea.after(0, lambda: self._update_python_output(stdout, stderr))
                
            except Exception as e:
                error_msg = f"{t('execution_error')}: {str(e)}\n"
                self.printarea.after(0, lambda: self.printarea.insert("end", error_msg))
        
        threading.Thread(target=execute_in_thread, daemon=True).start()
    
    def stop_current_process(self):
        """
        停止当前运行的进程
        """
        if self.current_process and self.current_process.poll() is None:
            try:
                # 根据操作系统选择不同的进程终止方式
                if self.is_windows:
                    # Windows系统使用taskkill终止进程及其子进程
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.current_process.pid)], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                else:
                    # macOS和Linux系统使用SIGTERM终止进程
                    self.current_process.terminate()
                    # 等待进程终止，如果超时则强制终止
                    try:
                        self.current_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.current_process.kill()
                
                self.printarea.after(0, lambda: self.printarea.insert("end", f"\n{t('process_stopped')}\n>>> "))
            except Exception as e:
                self.printarea.after(0, lambda: self.printarea.insert("end", f"\n{t('error_stopping_process')}: {str(e)}\n>>> "))
    
    def _show_python_exec_info(self, file_path):
        """
        显示Python执行信息
        
        Args:
            file_path: Python文件路径
        """
        self.printarea.delete(0.0, "end")
        self.printarea.insert("end", f">>> {sys.executable} {file_path}\n")
        self.printarea.insert("end", f"------------------Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}------------------\n")
    
    def _update_python_output(self, stdout, stderr):
        """
        更新Python输出
        
        Args:
            stdout: 标准输出
            stderr: 标准错误
        """
        self.printarea.insert("end", stdout)
        self.printarea.insert("end", stderr)
        self.printarea.insert("end", "\n>>> ")
    
    def _update_output(self, stdout, stderr):
        """
        更新终端输出
        
        Args:
            stdout: 标准输出
            stderr: 标准错误
        """
        if stdout:
            self.printarea.insert("end", stdout)
        if stderr:
            self.printarea.insert("end", stderr)
        self.printarea.insert("end", "\n>>> ")
    
    def clear_output(self):
        """
        清除输出区域
        """
        self.printarea.delete(0.0, "end")
        self.printarea.insert("end", ">>> ")
    
    def execute_from_command_area(self):
        """
        从命令区域执行命令
        """
        if self.commandarea:
            command = self.commandarea.get()
            if command.strip():
                self.execute_command(command)
                self.commandarea.delete(0, "end")
    
    def get_operating_system(self):
        """
        获取当前操作系统名称
        
        Returns:
            str: 操作系统名称
        """
        if self.is_windows:
            return "Windows"
        elif self.is_macos:
            return "macOS"
        elif self.is_linux:
            return "Linux"
        else:
            return "Unknown"
