"""
文件操作模块
处理文件的打开、保存、新建等操作
"""

import os
from tkinter import filedialog, messagebox
from pathlib import Path
from library.api import Settings


class FileOperations:
    """
    文件操作类
    处理文件的打开、保存、新建等操作
    """
    
    def __init__(self, codearea, multi_editor=None, lang_dict=None):
        """
        初始化文件操作类
        
        Args:
            codearea: 代码编辑区域
            multi_editor: 多文件编辑器实例（可选）
            lang_dict: 语言字典（可选）
        """
        self.codearea = codearea
        self.multi_editor = multi_editor
        self.lang_dict = lang_dict
        self.file_path = "temp_script.txt"
    
    def open_file(self):
        """
        打开文件
        """
        if self.multi_editor:
            # 使用多文件编辑器打开文件
            self.multi_editor.open_file_in_new_tab()
        else:
            # 单文件编辑器模式
            file_path = filedialog.askopenfilename(
                filetypes=[
                    (self.lang_dict["file-types"][0], "*.py"),
                    (self.lang_dict["file-types"][1], "*.html"),
                    (self.lang_dict["file-types"][2], "*.css"),
                    (self.lang_dict["file-types"][3], "*.js"),
                    (self.lang_dict["file-types"][4], "*.json"),
                    (self.lang_dict["file-types"][5], "*.rb"),
                    (self.lang_dict["file-types"][6], "*.c;*.cpp;*.h"),
                    (self.lang_dict["file-types"][7], "*.m"),
                    (self.lang_dict["file-types"][8], "*.*")
                ]
            )
            if file_path:  # 只有当用户选择了文件时才继续
                self.file_path = file_path
                self.codearea.delete(0.0, "end")
                try:
                    with open(self.file_path, encoding=Settings.Editor.file_encoding()) as f:
                        content = f.read()
                    self.codearea.insert(0.0, content)
                except Exception as e:
                    messagebox.showerror("错误", f"打开文件失败: {str(e)}")
    
    def save_file(self):
        """
        保存文件
        """
        if self.multi_editor:
            # 使用多文件编辑器保存文件
            self.multi_editor.save_current_file()
        else:
            # 单文件编辑器模式
            msg = self.codearea.get(0.0, "end")
            if self.file_path == "temp_script.txt":
                file_path = filedialog.asksaveasfilename(
                            filetypes=[
                                (self.lang_dict["file-types"][0], "*.py"),
                                (self.lang_dict["file-types"][1], "*.html"),
                                (self.lang_dict["file-types"][2], "*.css"),
                                (self.lang_dict["file-types"][3], "*.js"),
                                (self.lang_dict["file-types"][4], "*.json"),
                                (self.lang_dict["file-types"][5], "*.rb"),
                                (self.lang_dict["file-types"][6], "*.c;*.cpp;*.h"),
                                (self.lang_dict["file-types"][7], "*.m"),
                                (self.lang_dict["file-types"][8], "*.*")
                            ]
                        )
                if file_path:  # 只有当用户选择了文件时才继续
                    self.file_path = file_path
                else:
                    return  # 用户取消保存，直接返回

            try:
                with open(self.file_path, "w", encoding="utf-8") as fp:
                    fp.write(msg)
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def save_as_file(self):
        """
        另存为文件
        """
        if self.multi_editor:
            # 使用多文件编辑器另存为文件
            self.multi_editor.save_current_file()  # 在多文件编辑器中，另存为和保存逻辑相同
        else:
            # 单文件编辑器模式
            msg = self.codearea.get(0.0, "end")
            file_path = filedialog.asksaveasfilename(
                    filetypes=[
                        (self.lang_dict["file-types"][0], "*.py"),
                        (self.lang_dict["file-types"][1], "*.html"),
                        (self.lang_dict["file-types"][2], "*.css"),
                        (self.lang_dict["file-types"][3], "*.js"),
                        (self.lang_dict["file-types"][4], "*.json"),
                        (self.lang_dict["file-types"][5], "*.rb"),
                        (self.lang_dict["file-types"][6], "*.c;*.cpp;*.h"),
                        (self.lang_dict["file-types"][7], "*.m"),
                        (self.lang_dict["file-types"][8], "*.*")
                    ]
                )
            
            if file_path:  # 只有当用户选择了文件时才继续
                self.file_path = file_path
                try:
                    with open(self.file_path, "w", encoding="utf-8") as fp:
                        fp.write(msg)
                except Exception as e:
                    messagebox.showerror("错误", f"另存为文件失败: {str(e)}")
            # 如果用户取消选择，则不执行任何操作
    
    def new_file(self):
        """
        新建文件
        """
        if self.multi_editor:
            # 使用多文件编辑器新建文件
            self.multi_editor.create_new_tab("Untitled", "")
        else:
            # 单文件编辑器模式
            self.file_path = "temp_script.txt"
            self.codearea.delete(0.0, "end")
    
    def autosave(self, content=None):
        """
        自动保存文件
        
        Args:
            content: 要保存的内容（可选）
        """
        try:
            if content is None:
                content = self.codearea.get("1.0", "end")
            
            if self.multi_editor:
                # 使用多文件编辑器的自动保存功能
                current_file_path = self.multi_editor.get_current_file_path()
                if current_file_path != "temp_script.txt":
                    with open(current_file_path, "w", encoding=Settings.Editor.file_encoding()) as f:
                        f.write(content)
            else:
                # 单文件编辑器模式
                if self.file_path != "temp_script.txt":
                    with open(self.file_path, "w", encoding=Settings.Editor.file_encoding()) as f:
                        f.write(content)
            
            # 保存到临时文件
            with open("temp_script.txt", "w", encoding=Settings.Editor.file_encoding()) as f:
                f.write(content)
        except Exception as e:
            from library.logger import get_logger
            logger = get_logger()
            logger.error(f"自动保存失败: {str(e)}")
    
    def show_current_file_dir(self):
        """
        显示当前文件目录（绝对路径）
        """
        if self.multi_editor:
            current_file_path = self.multi_editor.get_current_file_path()
            messagebox.showinfo(current_file_path, current_file_path)
        else:
            messagebox.showinfo(self.file_path, self.file_path)
