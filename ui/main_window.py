"""
主窗口UI模块
"""

from tkinter import (Tk, Frame, BOTH, VERTICAL, HORIZONTAL, Label, Button, Text)
from tkinter.ttk import PanedWindow, Scrollbar, Treeview, Entry, Notebook
from tkinter.font import Font
from library.ui_styles import apply_modern_style, get_style
from library.api import Settings
from pathlib import Path
import json


class MainWindow(Tk):
    """
    主窗口类，继承自Tk
    负责创建和管理主窗口UI组件
    """
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        # 加载设置
        with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
            self.lang_dict = json.load(fp)
        
        # 设置窗口属性
        self.title(self.lang_dict["title"])
        self.geometry("1200x800+0+0")  # 使用适中的默认尺寸
        self.resizable(width=True, height=True)
        
        # 应用现代化样式
        self.style = get_style()
        apply_modern_style(self, "window")
        
        # 创建UI组件
        self._create_main_paned()
        self._create_file_tree_frame()
        self._create_code_paned()
        self._create_editor_frame()
        self._create_terminal_area()
        
        # 强制更新布局
        self.update_idletasks()
    
    def _create_main_paned(self):
        """
        创建主分割窗口
        """
        self.main_paned = PanedWindow(self, orient=HORIZONTAL)
        self.main_paned.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 设置初始分割位置
        self.after(100, lambda: self.main_paned.sashpos(0, 280))
    
    def _create_file_tree_frame(self):
        """
        创建文件树框架
        """
        self.file_tree_frame = Frame(self.main_paned, width=280)
        apply_modern_style(self.file_tree_frame, "frame", style="card")
        self.main_paned.add(self.file_tree_frame, weight=1)
    
    def _create_code_paned(self):
        """
        创建代码区域分割窗口
        """
        self.code_paned = PanedWindow(self.main_paned, orient=VERTICAL)
        self.main_paned.add(self.code_paned)
    
    def _create_editor_frame(self):
        """
        创建编辑器框架
        """
        self.editor_frame = Frame(self.code_paned)
        apply_modern_style(self.editor_frame, "frame", style="surface")
        self.code_paned.add(self.editor_frame, weight=2)
    
    def _create_terminal_area(self):
        """
        创建终端区域
        """
        from tkinter.font import Font
        self.terminal_area = Text(
            self.code_paned, 
            font=Font(
                self, 
                family=Settings.Editor.font(), 
                size=Settings.Editor.font_size()
            )
        )
        apply_modern_style(self.terminal_area, "text")
        self.code_paned.add(self.terminal_area, weight=1)
        
        # 设置初始分割位置，确保编辑器区域大于终端区域
        self.after(100, lambda: self.code_paned.sashpos(0, int(self.winfo_height() * 0.7)))
