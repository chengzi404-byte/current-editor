"""
多文件编辑器模块
支持选项卡式多文件编辑功能
"""

import json
import os
from pathlib import Path
from tkinter import Text, messagebox, BOTH, filedialog
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
        
        # 添加状态栏用于显示文件数

    def set_status_bar(self, status_bar):
        """设置状态栏"""
        self.status_bar = status_bar
        self.update_status_bar()

    def update_status_bar(self):
        """更新状态栏显示的文件数"""
        if hasattr(self, 'status_bar') and self.status_bar:
            file_count = len(self.tab_files)
            self.status_bar.config(text=f"文件数: {file_count}")

    def create_new_tab(self, title, content="", file_path=None):
        """创建新选项卡"""
        tab_frame = Frame(self.notebook)
        editor = Text(tab_frame, font=Font(family=Settings.Editor.font(), 
                                          size=Settings.Editor.font_size()))
        editor.insert("1.0", content)
        editor.pack(fill=BOTH, expand=True)
        
        self.notebook.add(tab_frame, text=title)
        tab_id = tab_frame
        
        self.tab_files[tab_id] = file_path
        self.tab_editors[tab_id] = editor
        self.current_tab = tab_id
        
        # 创建高亮器
        highlighter = self.highlighter_factory.create_highlighter(editor, file_path)
        self.tab_highlighters[tab_id] = highlighter
        
        # 应用主题
        self.apply_theme_to_editor(tab_id)
        
        # 切换到新标签页
        self.notebook.select(tab_frame)
        
        # 更新状态栏
        self.update_status_bar()
        
        return tab_id

    def close_tab(self, tab_id=None):
        """关闭选项卡"""
        if tab_id is None:
            tab_id = self.current_tab
            
        if tab_id and tab_id in self.tab_files:
            # 检查是否有未保存的更改
            if self.has_unsaved_changes(tab_id):
                if not self.prompt_save_changes():
                    return  # 用户取消关闭
            
            # 关闭标签页
            self.notebook.forget(tab_id)
            
            # 清理资源
            del self.tab_files[tab_id]
            del self.tab_editors[tab_id]
            del self.tab_highlighters[tab_id]
            
            # 更新当前标签
            if self.notebook.index("end") > 0:
                self.current_tab = self.notebook.tabs()[0] if self.notebook.tabs() else None
            else:
                self.current_tab = None
                # 如果没有标签页了，创建一个新的
                self.create_new_tab("Untitled", "")
            
            # 更新状态栏
            self.update_status_bar()

    def open_file_in_new_tab(self, file_path=None):
        """在新选项卡中打开文件"""
        if file_path:
            try:
                with open(file_path, "r", encoding=Settings.Editor.file_encoding()) as f:
                    content = f.read()
                title = Path(file_path).name
                tab_id = self.create_new_tab(title, content, file_path)
                self.notebook.select(tab_id)
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {str(e)}")
        else:
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
            if file_path:
                self.open_file_in_new_tab(file_path)
        
        # 更新状态栏
        self.update_status_bar()

    def apply_theme_to_editor(self, tab_id):
        """对指定编辑器应用主题"""
        highlighter = self.tab_highlighters.get(tab_id)
        if highlighter:
            try:
                theme_file = f"{Path.cwd() / 'asset' / 'theme' / Settings.Highlighter.syntax_highlighting()['theme']}.json"
                if os.path.exists(theme_file):
                    with open(theme_file, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                    highlighter.set_theme(theme_data)
                    highlighter.highlight()
            except Exception as e:
                logger.warning(f"Failed to apply theme to editor: {str(e)}")

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
            editor.configure(font=Font(family=font_family, size=font_size))

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
    
    def has_unsaved_changes(self, tab_id=None):
        """检查当前选项卡是否有未保存的更改"""
        if tab_id is None:
            tab_id = self.current_tab
        
        editor = self.tab_editors.get(tab_id)
        if not editor:
            return False
        
        current_content = editor.get("1.0", "end-1c")
        file_path = self.tab_files.get(tab_id)
        
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
    
    def get_all_content(self):
        """获取所有选项卡的内容"""
        all_content = {}
        for tab_id, editor in self.tab_editors.items():
            file_path = self.tab_files.get(tab_id, "Untitled")
            content = editor.get("1.0", "end-1c")
            all_content[file_path] = content
        return all_content
    
    def populate_file_tree(self, path=".", parent=""):
        """填充文件树"""
        import os
        from tkinter import filedialog
        from tkinter.ttk import Treeview
        
        # 如果path是默认值，则让用户选择目录
        if path == "." and parent == "":
            path = filedialog.askdirectory()
            if not path:
                return  # 用户取消选择
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                node_id = self.parent.master.master.children['!frame'].winfo_children()[0].insert(
                    parent, "end", text=item, values=[item_path])
                
                if os.path.isdir(item_path):
                    self.populate_file_tree(item_path, node_id)
        except PermissionError:
            pass  # 忽略无权限访问的目录
