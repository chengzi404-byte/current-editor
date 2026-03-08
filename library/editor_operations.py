"""
Editor Operations Module
包含从main.py中提取的编辑器操作功能

注意：这是一个适配器类，用于将旧的API调用转发到新的操作类
"""

import subprocess
import sys
import zipfile
from library.api import ConfigManager, EditorConfig, Settings
from pathlib import Path
from tkinter import (
    END, messagebox, filedialog
)

from library.logger import get_logger
from operations.file_operations import FileOperations
from operations.edit_operations import EditOperations
from operations.terminal import TerminalOperations
from operations.settings_manager import SettingsManager
import os

# 导入国际化模块
from i18n import t

logger = get_logger()


class EditorOperations:
    """
    编辑器操作类
    
    注意：这是一个适配器类，用于将旧的API调用转发到新的操作类
    """
    
    def __init__(self, root, codearea, commandarea, inputarea, multi_editor=None):
        """
        初始化编辑器操作
        
        Args:
            root: 主窗口对象
            codearea: 代码编辑区域
            commandarea: 命令区域
            inputarea: 输入区域
            multi_editor: 多文件编辑器实例（可选）
        """
        # 初始化新的操作类
        self.file_ops = FileOperations()
        self.edit_ops = EditOperations(codearea, commandarea)
        self.inputarea = inputarea
        self.terminal_ops = TerminalOperations(commandarea)
        self.settings_manager = SettingsManager(root, codearea, commandarea, t("settings"))
        
        # 保存旧的API需要的属性
        self.root = root
        self.codearea = codearea
        self.commandarea = commandarea
        self.multi_editor = multi_editor
        self.file_path = "temp_script.txt"
        self.config = ConfigManager()
        self.editor_conf = EditorConfig(self.config)
    
    # -------------------- 文件操作 --------------------
    def new_file(self):
        """文件 > 新建文件"""
        self.file_ops.new_file()
    
    def open_file(self):
        """文件 > 打开文件"""
        self.file_ops.open_file()
    
    def save_file(self):
        """文件 > 保存文件"""
        if self.file_path == "temp_script.txt" or (not os.path.exists(self.file_path)):
            self.save_as_file()
            return
        self.file_ops.write_file(self.file_path, self.codearea.get("1.0", END))
    
    def save_as_file(self):
        """文件 > 另存为"""
        filepath = filedialog.asksaveasfilename(
            title=t("save_as"),
            filetypes=self.editor_conf.save_file_options(),
            initialdir="./temp",
            defaultextension=".txt"
        )
        if filepath:
            self.file_path = filepath
            self.file_ops.write_file(self.file_path, self.codearea.get("1.0", END))
    
    def autosave(self):
        """文件 > 自动保存"""
        import tkinter as tk
        from pathlib import Path
        import os
        
        try:
            # 1. 检查基本依赖
            if self.multi_editor is None:
                logger.error("自动保存失败: self.multi_editor不存在")
                return
            
            # 2. 获取并验证配置
            save_path_config = self.config.get("editor.file-path", "./temp")
            
            # 确保save_path是Path对象
            if isinstance(save_path_config, str):
                save_path_config = Path(save_path_config)
            
            # 3. 确定保存目录
            if save_path_config.suffix:
                save_dir = save_path_config.parent
            else:
                save_dir = save_path_config
            
            # 4. 确保保存目录存在
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 5. 获取notebook和标签页
            notebook = self.multi_editor.get_notebook()
            tab_ids = notebook.tabs()
            
            # 6. 遍历标签页并保存内容
            save_count = 0
            
            # 方式1: 优先通过notebook.tabs()获取所有标签页
            for i, tab_id in enumerate(tab_ids):
                # 获取标题
                try:
                    title = notebook.tab(tab_id, "text")
                except Exception:
                    title = f"untitled_{i}"
                
                # 获取编辑器
                editor = None
                
                # 方式1.1: 通过get_editor方法
                editor = self.multi_editor.get_editor(tab_id)
                if not editor:
                    # 方式1.2: 直接通过nametowidget获取
                    try:
                        # 获取标签页框架
                        tab_frame = notebook.nametowidget(tab_id)
                        # 查找框架中的Text组件
                        for child in tab_frame.winfo_children():
                            if child.winfo_class() == 'Text':
                                editor = child
                                break
                    except Exception:
                        pass
                
                if editor:
                    try:
                        # 获取编辑器内容
                        content = editor.get("0.0", tk.END)
                        
                        # 检查内容是否为空
                        if not content.strip():
                            continue
                        
                        # 使用安全的文件名
                        safe_title = "".join(c if c.isalnum() or c in ('_', '-', '.') else '' for c in title)
                        file_path = save_dir / f"{safe_title}.txt"
                        
                        # 写入文件
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        # 验证文件是否保存成功
                        if file_path.exists():
                            file_size = os.path.getsize(file_path)
                            logger.info(f"✅ 自动保存成功: {file_path} ({file_size} 字节)")
                            save_count += 1
                        else:
                            logger.error(f"❌ 自动保存失败: 文件不存在: {file_path}")
                            
                    except Exception as save_error:
                        logger.error(f"❌ 自动保存失败: {str(save_error)}")
            
            logger.info(f"自动保存完成，共保存 {save_count} 个编辑器")
            
        except Exception as e:
            logger.error(f"自动保存失败: {str(e)}")
    
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

    @property
    def text_widget(self):
        """
        获取当前文本小部件
        """
        return self.codearea
