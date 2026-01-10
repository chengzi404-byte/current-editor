"""
Editor Operations Module
包含从main.py中提取的编辑器操作功能

注意：这是一个适配器类，用于将旧的API调用转发到新的操作类
"""

import subprocess
import sys
import zipfile
import shlex
from pathlib import Path
from tkinter import (
    END, messagebox, filedialog
)

from library.logger import get_logger
from operations.file_operations import FileOperations
from operations.edit_operations import EditOperations
from operations.terminal import TerminalOperations
from operations.settings_manager import SettingsManager
from operations.ai_service import AIService

# 导入国际化模块
from i18n import t

logger = get_logger()


class EditorOperations:
    """
    编辑器操作类
    
    注意：这是一个适配器类，用于将旧的API调用转发到新的操作类
    """
    
    def __init__(self, root, codearea, printarea, inputarea, commandarea, 
                 ai_display, ai_input, ai_send_button, ai_queue, ai_loading, multi_editor=None):
        """
        初始化编辑器操作
        
        Args:
            root: 主窗口对象
            codearea: 代码编辑区域
            printarea: 输出区域
            inputarea: 输入区域
            commandarea: 命令区域
            ai_display: AI显示区域
            ai_input: AI输入区域
            ai_send_button: AI发送按钮
            ai_queue: AI队列
            ai_loading: AI加载状态
            multi_editor: 多文件编辑器实例（可选）
        """
        # 初始化新的操作类
        self.file_ops = FileOperations()
        self.edit_ops = EditOperations(codearea, printarea)
        self.terminal_ops = TerminalOperations(printarea)
        self.settings_manager = SettingsManager(root, codearea, printarea, t("settings"))
        self.ai_service = AIService(ai_display, ai_input, ai_send_button, ai_queue, ai_loading)
        
        # 保存旧的API需要的属性
        self.root = root
        self.codearea = codearea
        self.printarea = printarea
        self.inputarea = inputarea
        self.commandarea = commandarea
        self.ai_display = ai_display
        self.ai_input = ai_input
        self.ai_send_button = ai_send_button
        self.ai_queue = ai_queue
        self.ai_loading = ai_loading
        self.multi_editor = multi_editor
        self.file_path = "temp_script.txt"
        self.copy_msg = ""
    
    # -------------------- 文件操作 --------------------
    def new_file(self):
        """文件 > 新建文件"""
        self.file_ops.new_file()
    
    def open_file(self):
        """文件 > 打开文件"""
        self.file_ops.open_file()
    
    def save_file(self):
        """文件 > 保存文件"""
        self.file_ops.save_file()
    
    def save_as_file(self):
        """文件 > 另存为"""
        self.file_ops.save_as_file()
    
    def autosave(self):
        """文件 > 自动保存"""
        # 自动保存功能，暂时为空实现
        # 后续可以在这里添加实际的自动保存逻辑
        pass
    
    def new_window(self):
        """文件 > 新建窗口"""
        subprocess.run([sys.executable, "main.py"])
    
    def show_current_file_dir(self):
        """显示当前文件目录（绝对路径）"""
        self.file_ops.show_current_file_dir()
    
    # -------------------- 编辑操作 --------------------
    def copy(self):
        """编辑 > 复制"""
        self.edit_ops.copy()
    
    def paste(self):
        """编辑 > 粘贴"""
        self.edit_ops.paste()
    
    def delete(self):
        """编辑 > 删除选中"""
        self.edit_ops.delete()
    
    def undo(self):
        """编辑 > 撤销"""
        self.edit_ops.undo()
    
    def redo(self):
        """编辑 > 重做"""
        self.edit_ops.redo()
    
    # -------------------- 运行操作 --------------------
    def run(self):
        """运行 > 运行Python文件"""
        file_path = Settings.Editor.file_path()
        input_data = None
        if self.inputarea:
            input_data = self.inputarea.get(0.0, "end")
        self.terminal_ops.run_python_file(file_path, input_data)
    
    def clear_printarea(self):
        """运行 > 清除输出"""
        self.terminal_ops.clear_output()
    
    # -------------------- 设置操作 --------------------
    def open_settings_panel(self, codehighlighter, codehighlighter2):
        """打开设置面板"""
        self.settings_manager.open_settings_panel(codehighlighter, codehighlighter2)
    
    # -------------------- AI功能 --------------------
    def send_ai_request_to_api(self, prompt, apikey):
        """发送AI请求到API"""
        self.ai_service.send_ai_request_to_api(prompt, apikey)
    
    def process_ai_responses(self):
        """处理AI响应"""
        self.ai_service.process_ai_responses()
    
    def display_ai_response(self, response):
        """显示AI响应"""
        self.ai_service.display_ai_response(response)
    
    def update_ai_loading(self):
        """更新AI加载状态"""
        self.ai_service.update_ai_loading()
    
    def on_ai_input_enter(self, event):
        """AI输入回车事件"""
        self.ai_service.on_ai_input_enter(event)
    
    def send_ai_request(self):
        """发送AI请求"""
        self.ai_service.send_ai_request()
    
    # -------------------- 遗留功能 --------------------
    def download_plugin(self):
        """插件 > 下载插件"""
        try:
            plugin_path = filedialog.askopenfilename(
                title=t("open_plugin"),  # 使用多语言适配
                filetypes=[
                    (t("plugin-types.0"), "*.zip"),  # 使用多语言适配
                    (t("plugin-types.1"), "*.*")    # 使用多语言适配
                ]
            )
            if plugin_path:
                plugin_zip = zipfile.ZipFile(plugin_path, "r")
                plugin_zip.extractall(f"{Path.cwd() / 'asset' / 'plugins'}")
                plugin_zip.close()
                messagebox.showinfo(t("plugin"), t("plugin_installation_successful"))  # 使用多语言适配
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('plugin_installation_failed')}: {str(e)}")  # 使用多语言适配
    
    def exit_editor(self):
        """退出"""
        if messagebox.askokcancel(t("exit"), t("exit_confirmation")):  # 使用多语言适配
            self.root.destroy()
            sys.exit(0)
    
    def execute_commands(self):
        """在命令区域执行命令"""
        command = self.commandarea.get()
        self.terminal_ops.execute_command(command)
    
    def open_folder(self):
        """打开文件夹并更新文件树"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 清空现有的文件树
            for item in self.root.file_tree.get_children():
                self.root.file_tree.delete(item)
            # 重新填充文件树
            self.populate_file_tree_for_open_folder(folder_path)
    
    def populate_file_tree_for_open_folder(self, path):
        """为打开文件夹功能填充文件树"""
        import os
        def _populate_subdirectories(tree, path, parent=""):
            """递归填充子目录"""
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                node_id = tree.insert(parent, "end", text=item, values=[item_path])
                
                if os.path.isdir(item_path):
                    _populate_subdirectories(tree, item_path, node_id)
        
        _populate_subdirectories(self.root.file_tree, path)