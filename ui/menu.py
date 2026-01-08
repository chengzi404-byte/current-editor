"""
菜单模块
"""

from tkinter import Menu, messagebox
from library.api import Settings
from pathlib import Path
import json
from i18n import t

class MenuBar:
    """
    菜单栏类
    负责菜单的创建和管理
    """
    
    def __init__(self, root, app):
        """
        初始化菜单栏
        
        Args:
            root: 主窗口
            app: 应用程序实例
        """
        self.root = root
        self.app = app
        
        # 创建主菜单
        self._create_main_menu()
        
        # 创建文件菜单
        self._create_file_menu()
        
        # 创建编辑菜单
        self._create_edit_menu()
        
        # 创建运行菜单
        self._create_run_menu()
        
        # 创建右键菜单
        self._create_popup_menu()
        
        # 创建插件菜单
        self._create_plugin_menu()
        
        # 创建帮助菜单
        self._create_help_menu()
        
        # 创建设置菜单
        self._create_settings_menu()
    
    def _create_main_menu(self):
        """
        创建主菜单
        """
        self.menu = Menu()
        self.root.config(menu=self.menu)
    
    def _create_file_menu(self):
        """
        创建文件菜单
        """
        self.filemenu = Menu(tearoff=0)
        self.menu.add_cascade(menu=self.filemenu, label=t("menus.file"))
        self.filemenu.add_command(command=self.app.editor_ops.new_file, label=t("menus.new-file"))
        self.filemenu.add_command(command=self.app.editor_ops.new_window, label=t("menus.new-window"))
        self.filemenu.add_separator()
        self.filemenu.add_command(command=self.app.editor_ops.open_file, label=t("menus.open-file"))
        self.filemenu.add_command(command=self.open_folder_global, label=t("menus.open-folder"))
        self.filemenu.add_command(command=self.app.editor_ops.save_file, label=t("menus.save-file"))
        self.filemenu.add_command(command=self.app.editor_ops.save_as_file, label=t("menus.save-as-file"))
        self.filemenu.add_separator()
        self.filemenu.add_command(command=self.app.editor_ops.show_current_file_dir, label=t("menus.show-file-dir"))
        self.filemenu.add_separator()
        self.filemenu.add_command(command=self.app.editor_ops.exit_editor, label=t("menus.exit"))
    
    def _create_edit_menu(self):
        """
        创建编辑菜单
        """
        self.editmenu = Menu(tearoff=0)
        self.menu.add_cascade(menu=self.editmenu, label=t("menus.edit"))
        self.editmenu.add_command(command=self.app.editor_ops.undo, label=t("menus.undo"))
        self.editmenu.add_command(command=self.app.editor_ops.redo, label=t("menus.redo"))
        self.editmenu.add_separator()
        self.editmenu.add_command(command=self.app.editor_ops.copy, label=t("menus.copy"))
        self.editmenu.add_command(command=self.app.editor_ops.paste, label=t("menus.paste"))
        self.editmenu.add_command(command=self.app.editor_ops.delete, label=t("menus.delete"))
    
    def _create_run_menu(self):
        """
        创建运行菜单
        """
        self.runmenu = Menu(tearoff=0)
        self.menu.add_cascade(menu=self.runmenu, label=t("menus.run"))
        self.runmenu.add_command(command=self.app.editor_ops.run, label=t("menus.run"))
        self.runmenu.add_command(command=self.app.editor_ops.clear_printarea, label=t("menus.clear-output"))
    
    def _create_popup_menu(self):
        """
        创建右键菜单
        """
        self.popmenu = Menu(self.root, tearoff=0)
        self.popmenu.add_command(label=t("menus.copy"), command=self.app.editor_ops.copy)
        self.popmenu.add_command(label=t("menus.paste"), command=self.app.editor_ops.paste)
        self.popmenu.add_command(label=t("menus.undo"), command=self.app.editor_ops.undo)
        self.popmenu.add_command(label=t("menus.redo"), command=self.app.editor_ops.redo)
    
    def _create_plugin_menu(self):
        """
        创建插件菜单
        """
        self.pluginmenu = Menu(tearoff=0)
        self.menu.add_cascade(menu=self.pluginmenu, label=t("menus.plugin"))
    
    def _create_help_menu(self):
        """
        创建帮助菜单
        """
        self.menu.add_command(
            label=t("menus.help"), 
            command=lambda: self.app.multi_editor.show_help_tab(self.app)
        )
    
    def _create_settings_menu(self):
        """
        创建设置菜单
        """
        self.settingsmenu = Menu(tearoff=0)
        self.menu.add_cascade(menu=self.settingsmenu, label=t("menus.configure"))
        # 设置菜单命令绑定
        self.settingsmenu.add_command(
            label=t("menus.open-settings"), 
            command=self.open_settings
        )
    
    def open_folder_global(self):
        """
        全局函数用于打开文件夹
        """
        from tkinter import filedialog
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 更新文件树
            self.app.file_browser.open_folder(folder_path)
    
    def open_settings(self):
        """
        打开设置面板
        """
        # 获取高亮器引用
        codehighlighter_ref = getattr(self.app, 'codehighlighter', None)
        codehighlighter2_ref = getattr(self.app, 'codehighlighter2', None)
        
        # 在Tab中显示设置面板
        self.app.multi_editor.show_settings_tab(
            self.app, 
            codehighlighter_ref, 
            codehighlighter2_ref
        )