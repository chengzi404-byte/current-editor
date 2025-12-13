"""
多文件编辑器模块
支持选项卡式多文件编辑功能
"""

import json
import os
from pathlib import Path
from tkinter import Text, messagebox, BOTH
from tkinter.font import Font
from tkinter.ttk import Notebook, Frame
from library.highlighter_factory import HighlighterFactory
from library.logger import setup_logger
from library.api import Settings

logger = setup_logger()


class MultiFileEditor:
    """多文件编辑器类"""
    
    def __init__(self, parent, printarea, inputarea, commandarea):
        """
        初始化多文件编辑器
        
        Args:
            parent: 父容器
            printarea: 输出区域
            inputarea: 输入区域
            commandarea: 命令区域
        """
        self.parent = parent
        self.printarea = printarea
        self.inputarea = inputarea
        self.commandarea = commandarea
        
        # 创建选项卡控件
        self.notebook = Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # 文件标签映射
        self.tab_files = {}  # {tab_id: file_path}
        self.tab_editors = {}  # {tab_id: editor_widget}
        self.tab_highlighters = {}  # {tab_id: highlighter}
        self.current_tab = None
        
        # 高亮器工厂
        self.highlighter_factory = HighlighterFactory()
        
        # 加载语言设置
        with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
            self.lang_dict = json.load(fp)
        
        # 绑定选项卡切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 创建初始选项卡
        self.create_new_tab("Untitled", "")
    
    def create_new_tab(self, title, content, file_path=None):
        """
        创建新的编辑选项卡
        
        Args:
            title: 选项卡标题
            content: 初始内容
            file_path: 文件路径（可选）
        """
        # 创建选项卡框架
        tab_frame = Frame(self.notebook)
        
        # 创建文本编辑器
        editor = Text(tab_frame, font=Font(self.parent, family=Settings.Editor.font(), 
                                          size=Settings.Editor.font_size()))
        editor.pack(fill=BOTH, expand=True)
        
        # 插入初始内容
        editor.insert("1.0", content)
        
        # 添加选项卡
        tab_id = self.notebook.add(tab_frame, text=title)
        
        # 创建语法高亮器
        highlighter = self.highlighter_factory.create_highlighter(editor, file_path)
        
        # 应用主题
        try:
            theme_file = f"{Path.cwd() / 'asset' / 'theme' / Settings.Highlighter.syntax_highlighting()['theme']}.json"
            if os.path.exists(theme_file):
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                highlighter.set_theme(theme_data)
                highlighter.highlight()
        except Exception as e:
            logger.warning(f"Failed to apply theme to new tab: {str(e)}")
        
        # 保存引用
        self.tab_files[tab_id] = file_path
        self.tab_editors[tab_id] = editor
        self.tab_highlighters[tab_id] = highlighter
        
        # 切换到新选项卡
        self.notebook.select(tab_id)
        self.current_tab = tab_id
        
        return tab_id
    
    def get_current_editor(self):
        """获取当前活动的编辑器"""
        if self.current_tab and self.current_tab in self.tab_editors:
            return self.tab_editors[self.current_tab]
        
        # 如果没有当前选项卡，尝试获取第一个选项卡的编辑器
        if self.tab_editors:
            first_tab = list(self.tab_editors.keys())[0]
            return self.tab_editors[first_tab]
        
        # 如果没有任何选项卡，创建一个新的
        self.create_new_tab("Untitled", "")
        return self.tab_editors[self.current_tab]
    
    def get_current_file_path(self):
        """获取当前活动文件的路径"""
        if self.current_tab and self.current_tab in self.tab_files:
            return self.tab_files[self.current_tab]
        return None
    
    def get_current_highlighter(self):
        """获取当前活动的高亮器"""
        if self.current_tab and self.current_tab in self.tab_highlighters:
            return self.tab_highlighters[self.current_tab]
        return None
    
    def on_tab_changed(self, event):
        """选项卡切换事件处理"""
        selected_tab = self.notebook.select()
        if selected_tab:
            self.current_tab = selected_tab
    
    def close_current_tab(self):
        """关闭当前选项卡"""
        if not self.current_tab:
            return
        
        # 检查是否有未保存的更改
        editor = self.get_current_editor()
        if editor and self.has_unsaved_changes():
            if not self.prompt_save_changes():
                return  # 用户取消关闭
        
        # 关闭选项卡
        self.notebook.forget(self.current_tab)
        
        # 清理资源
        if self.current_tab in self.tab_files:
            del self.tab_files[self.current_tab]
        if self.current_tab in self.tab_editors:
            del self.tab_editors[self.current_tab]
        if self.current_tab in self.tab_highlighters:
            del self.tab_highlighters[self.current_tab]
        
        # 如果没有选项卡了，创建一个新的
        if len(self.notebook.tabs()) == 0:
            self.create_new_tab("Untitled", "")
        else:
            self.current_tab = self.notebook.select()
    
    def has_unsaved_changes(self):
        """检查当前选项卡是否有未保存的更改"""
        editor = self.get_current_editor()
        if not editor:
            return False
        
        current_content = editor.get("1.0", "end-1c")
        file_path = self.get_current_file_path()
        
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                saved_content = f.read()
            return current_content != saved_content
        else:
            # 新文件，如果有内容则视为有未保存更改
            return bool(current_content.strip())
    
    def prompt_save_changes(self):
        """提示用户保存更改"""
        result = messagebox.askyesnocancel(
            "提示",
            "文件有未保存的更改，是否保存？"
        )
        
        if result is None:  # 取消
            return False
        elif result:  # 是，保存
            return self.save_current_file()
        else:  # 否，不保存
            return True
    
    def save_current_file(self):
        """保存当前文件"""
        editor = self.get_current_editor()
        file_path = self.get_current_file_path()
        
        if not editor:
            return False
        
        if not file_path:
            # 需要选择保存路径
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title=self.lang_dict["file"]["save-as"],
                filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not file_path:
                return False
            
            # 更新文件路径和选项卡标题
            self.tab_files[self.current_tab] = file_path
            self.notebook.tab(self.current_tab, text=os.path.basename(file_path))
        
        try:
            content = editor.get("1.0", "end-1c")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror(
                self.lang_dict["info-window-title"],
                f"{self.lang_dict['file']['save-error']}: {str(e)}"
            )
            return False
    
    def open_file_in_new_tab(self, file_path=None):
        """在新选项卡中打开文件"""
        if not file_path:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="打开文件",
                filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
        
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 检查文件是否已经在其他选项卡中打开
            for tab_id, path in self.tab_files.items():
                if path == file_path:
                    # 切换到已打开的选项卡
                    self.notebook.select(tab_id)
                    return True
            
            # 创建新选项卡
            tab_title = os.path.basename(file_path)
            self.create_new_tab(tab_title, content, file_path)
            return True
            
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"打开文件失败: {str(e)}"
            )
            return False
    
    def get_all_content(self):
        """获取所有选项卡的内容"""
        all_content = {}
        for tab_id, editor in self.tab_editors.items():
            file_path = self.tab_files.get(tab_id, "Untitled")
            content = editor.get("1.0", "end-1c")
            all_content[file_path] = content
        return all_content
    
    def apply_theme_to_all(self, theme_data):
        """对所有选项卡应用主题"""
        for highlighter in self.tab_highlighters.values():
            try:
                highlighter.set_theme(theme_data)
                highlighter.highlight()
            except Exception as e:
                logger.warning(f"Failed to apply theme: {str(e)}")
    
    def update_font_for_all(self, font_family, font_size):
        """更新所有编辑器的字体"""
        for editor in self.tab_editors.values():
            editor.configure(font=Font(self.parent, family=font_family, size=font_size))