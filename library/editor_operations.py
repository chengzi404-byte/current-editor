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
# from operations.ai_service import AIService
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
        self.edit_ops = EditOperations(codearea, commandarea)
        self.inputarea = inputarea
        self.terminal_ops = TerminalOperations(commandarea)
        self.settings_manager = SettingsManager(root, codearea, commandarea, t("settings"))
#       self.ai_service = AIService(ai_display, ai_input, ai_send_button, ai_queue, ai_loading)
        
        # 保存旧的API需要的属性
        self.root = root
        self.codearea = codearea
        self.commandarea = commandarea
        # self.ai_display = ai_display
        # self.ai_input = ai_input
        # self.ai_send_button = ai_send_button
        # self.ai_queue = ai_queue
        # self.ai_loading = ai_loading
        self.multi_editor = multi_editor
        self.file_path = "temp_script.txt"
        self.copy_msg = ""
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
        
        print("\n=== 开始自动保存 ===")
        
        try:
            # 1. 检查基本依赖
            print(f"self.multi_editor 是否存在: {self.multi_editor is not None}")
            if self.multi_editor is None:
                print("ERROR: self.multi_editor 不存在")
                logger.error("自动保存失败: self.multi_editor不存在")
                return
            
            # 2. 获取并验证配置
            save_path_config = self.config.get("editor.file-path", "./temp")
            print(f"配置的保存路径: {save_path_config}")
            
            # 确保save_path是Path对象
            if isinstance(save_path_config, str):
                save_path_config = Path(save_path_config)
            
            # 3. 确定保存目录
            if save_path_config.suffix:
                save_dir = save_path_config.parent
                print(f"配置路径是文件，使用父目录: {save_dir}")
            else:
                save_dir = save_path_config
                print(f"配置路径是目录，直接使用: {save_dir}")
            
            # 4. 确保保存目录存在
            save_dir.mkdir(parents=True, exist_ok=True)
            print(f"保存目录: {save_dir}, 是否存在: {save_dir.exists()}")
            
            # 5. 测试直接保存一个文件到目录
            test_file = save_dir / "test_autosave.txt"
            with open(test_file, "w") as f:
                f.write("测试自动保存功能")
            print(f"✅ 测试文件已保存: {test_file}, 大小: {os.path.getsize(test_file)} 字节")
            
            # 6. 获取notebook和标签页
            notebook = self.multi_editor.get_notebook()
            print(f"notebook 对象: {notebook}")
            
            tab_ids = notebook.tabs()
            print(f"获取到的标签页数量: {len(tab_ids)}")
            print(f"标签页ID列表: {tab_ids}")
            
            # 7. 检查multi_editor的内部状态
            print(f"multi_editor.tab_editors 数量: {len(self.multi_editor.tab_editors)}")
            print(f"multi_editor.tab_editors 内容: {self.multi_editor.tab_editors}")
            
            # 8. 遍历标签页并保存内容的可靠方式
            print("\n--- 遍历标签页并保存内容 ---")
            save_count = 0
            
            # 方式1: 优先通过notebook.tabs()获取所有标签页
            for i, tab_id in enumerate(tab_ids):
                print(f"\n处理标签页 {i}, ID: {tab_id}")
                
                # 获取标题
                try:
                    title = notebook.tab(tab_id, "text")
                    print(f"  标题: '{title}'")
                except Exception as title_error:
                    print(f"  ❌ 获取标题失败: {title_error}")
                    title = f"untitled_{i}"
                    print(f"  使用默认标题: '{title}'")
                
                # 获取编辑器的三种方式
                editor = None
                
                # 方式1.1: 通过get_editor方法
                editor = self.multi_editor.get_editor(tab_id)
                if editor:
                    print(f"  ✅ 通过get_editor获取编辑器成功")
                else:
                    # 方式1.2: 直接从tab_editors字典查找
                    print(f"  ❌ 通过get_editor获取编辑器失败")
                    
                    # 检查tab_editors中是否有None键
                    if None in self.multi_editor.tab_editors:
                        editor = self.multi_editor.tab_editors[None]
                        print(f"  ✅ 从tab_editors[None]获取编辑器成功")
                    else:
                        # 方式1.3: 直接通过nametowidget获取
                        try:
                            # 获取标签页框架
                            tab_frame = notebook.nametowidget(tab_id)
                            # 查找框架中的Text组件
                            for child in tab_frame.winfo_children():
                                if child.winfo_class() == 'Text':
                                    editor = child
                                    print(f"  ✅ 通过nametowidget查找Text组件成功")
                                    break
                        except Exception as widget_error:
                            print(f"  ❌ 通过nametowidget获取编辑器失败: {widget_error}")
                
                if editor:
                    try:
                        # 获取编辑器内容
                        content = editor.get("0.0", tk.END)
                        print(f"  编辑器内容长度: {len(content)} 字符")
                        
                        # 检查内容是否为空
                        if not content.strip():
                            print(f"  ⏭️  跳过空内容")
                            continue
                        
                        # 使用安全的文件名
                        safe_title = "".join(c if c.isalnum() or c in ('_', '-', '.') else '' for c in title)
                        file_path = save_dir / f"{safe_title}.txt"
                        print(f"  准备保存到: {file_path}")
                        
                        # 写入文件
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        # 验证文件是否保存成功
                        if file_path.exists():
                            file_size = os.path.getsize(file_path)
                            print(f"  ✅ 文件保存成功: {file_path}")
                            print(f"  文件大小: {file_size} 字节")
                            logger.info(f"✅ 自动保存成功: {file_path} ({file_size} 字节)")
                            save_count += 1
                        else:
                            print(f"  ❌ 文件保存失败: 文件不存在")
                            logger.error(f"❌ 自动保存失败: 文件不存在: {file_path}")
                            
                    except Exception as save_error:
                        print(f"  ❌ 保存失败: {save_error}")
                        logger.error(f"❌ 自动保存失败: {str(save_error)}")
            
            # 方式2: 额外保存tab_editors中所有编辑器（防止遗漏）
            print("\n--- 额外检查tab_editors字典 ---")
            for tab_id_key, editor in self.multi_editor.tab_editors.items():
                if editor:
                    try:
                        # 检查是否已经保存过
                        content = editor.get("0.0", tk.END)
                        if not content.strip():
                            continue
                        
                        # 使用通用标题
                        title = f"editor_{tab_id_key}"
                        safe_title = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in title)
                        file_path = save_dir / f"extra_{safe_title}.txt"
                        
                        # 只保存未保存过的内容
                        if not file_path.exists():
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            print(f"  ✅ 额外保存编辑器成功: {file_path}")
                            logger.info(f"✅ 额外自动保存成功: {file_path}")
                            save_count += 1
                        else:
                            print(f"  ⏭️  跳过已保存的额外编辑器")
                    except Exception as extra_error:
                        print(f"  ❌ 额外保存失败: {extra_error}")
            
            print(f"\n=== 自动保存完成，共保存 {save_count} 个编辑器 ===")
            logger.info(f"自动保存完成，共保存 {save_count} 个编辑器")
            
            print("\n=== 自动保存完成 ===")
            logger.info("自动保存完成")
            
        except Exception as e:
            print(f"\n❌ 自动保存整体异常: {str(e)}")
            import traceback
            print(f"异常详细信息: {traceback.format_exc()}")
            logger.error(f"自动保存失败: {str(e)}")
            logger.error(f"异常详细信息: {traceback.format_exc()}")
    
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

    def open_file(self, text_widget):
        """
        打开文件并读取内容
        """
        file_path = filedialog.askopenfilename(title=t("open_file"), filetypes=[(t("all_files"), "*.*")])
        if not file_path:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                text_widget.delete('1.0', 'end')
                text_widget.insert('1.0', content)
                self.current_file_path = file_path  # 更新当前文件路径
            self.multi_editor.get_notebook().tab(self.multi_editor.get_current_tab(), text=os.path.basename(file_path))
            self.root.title(f"{os.path.basename(file_path)} - {t('editor_title')}") # 更新窗口标题
        except Exception as e:
            print("Trying to open file but Got exception: ", str(e))

    @property
    def text_widget(self):
        """
        获取当前文本小部件
        """
        return self.codearea