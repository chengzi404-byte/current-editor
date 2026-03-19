"""
文件浏览器模块
"""

from tkinter import Frame, Label, Button, LEFT, RIGHT, X, BOTH
from tkinter.ttk import Treeview, Scrollbar
from library.ui_styles import apply_modern_style, get_style
import os
from i18n import t

class FileBrowser:
    """
    文件浏览器类
    负责文件树的创建、填充和事件处理
    """
    
    def __init__(self, parent_frame, app):
        """
        初始化文件浏览器
        
        Args:
            parent_frame: 父框架
            app: 应用程序实例
        """
        self.parent_frame = parent_frame
        self.app = app
        self.style = get_style()

        self._create_file_tree_header()
        self._create_file_tree_container()
        self._create_file_tree()
        self._bind_file_tree_events()
        self._init_file_tree()
    
    def _create_file_tree_header(self):
        """
        创建文件树标题栏
        """
        self.file_tree_header = Frame(self.parent_frame)
        apply_modern_style(self.file_tree_header, "frame", style="card")
        self.file_tree_header.pack(fill=X, padx=0, pady=0)
        
        # 文件树标题
        self.file_tree_title = Label(
            self.file_tree_header,
            text=t("file_browser.title"),
            font=self.style.get_font("lg", "bold")
        )
        apply_modern_style(self.file_tree_title, "label")
        self.file_tree_title.pack(side=LEFT, padx=15, pady=15)

        self.refresh_button = Button(
            self.file_tree_header, 
            text=f" {self.style.get_icon('refresh')} {t('file_browser.refresh')}", 
            font=self.style.get_font("sm"), 
            command=self.refresh_file_tree
        )
        apply_modern_style(self.refresh_button, "button", variant="outline")
        self.refresh_button.pack(side=RIGHT, padx=10, pady=10)
    
    def _create_file_tree_container(self):
        """
        创建文件树容器
        """
        self.file_tree_container = Frame(self.parent_frame)
        apply_modern_style(self.file_tree_container, "frame")
        self.file_tree_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _create_file_tree(self):
        """
        创建文件树
        """
        self.tree = Treeview(self.file_tree_container, show="tree")
        self.tree.heading("#0", text="")
        apply_modern_style(self.tree, "treeview")
        self.tree.pack(fill=BOTH, expand=True, side=LEFT)

        self.tree_scrollbar = Scrollbar(
            self.file_tree_container, 
            orient="vertical", 
            command=self.tree.yview
        )
        apply_modern_style(self.tree_scrollbar, "scrollbar")
        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
    
    def _bind_file_tree_events(self):
        """
        绑定文件树事件
        """
        self.tree.bind("<<TreeviewSelect>>", self.on_file_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_file_tree_expand)
    
    def _init_file_tree(self):
        """
        初始化文件树
        """
        self.populate_file_tree(".")
    
    def populate_file_tree(self, path=".", parent=""):
        """
        填充文件树
        
        Args:
            path: 路径
            parent: 父节点
        """
        abs_path = os.path.abspath(path)

        items = os.listdir(abs_path)

        folders = []
        files = []
        
        for item in items:
            item_path = os.path.join(abs_path, item)
            if item.startswith('.'):
                continue
            if os.path.isdir(item_path):
                folders.append(item)
            else:
                files.append(item)
        
        folders.sort(key=str.lower)

        file_groups = {}
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in file_groups:
                file_groups[ext] = []
            file_groups[ext].append(file)
        
        for ext in file_groups:
            file_groups[ext].sort(key=str.lower)

        sorted_extensions = sorted(file_groups.keys())

        for folder in folders:
            folder_path = os.path.join(abs_path, folder)
            icon = "📁"
            node_id = self.tree.insert(parent, "end", text=f" {icon} {folder}", values=[folder_path])
            self.tree.insert(node_id, "end", text=t("file_browser.loading"))

        for ext in sorted_extensions:
            for file in file_groups[ext]:
                file_path = os.path.join(abs_path, file)
                icon = self.get_file_icon(file)
                self.tree.insert(parent, "end", text=f" {icon} {file}", values=[file_path])
    
    def get_file_icon(self, filename):
        """
        根据文件扩展名返回对应的图标
        
        Args:
            filename: 文件名
            
        Returns:
            str: 文件图标
        """
        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
            '.json': '📋', '.md': '📝', '.txt': '📄', '.xml': '📊',
            '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.h': '⚙️',
            '.php': '🐘', '.rb': '💎', '.go': '🐹', '.rs': '🦀',
            '.ts': '📘', '.jsx': '⚛️', '.tsx': '⚛️', '.vue': '💚',
            '.png': '🖼️', '.jpg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.zip': '📦', '.rar': '📦', '.tar': '📦', '.gz': '📦',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗',
            '.xlsx': '📗', '.ppt': '📙', '.pptx': '📙'
        }
        return icon_map.get(ext, '📄')
    
    def on_file_tree_expand(self, event):
        """
        处理文件树展开事件
        
        Args:
            event: 事件对象
        """
        item = self.tree.focus()
        if item:
            children = self.tree.get_children(item)
            if len(children) == 1 and self.tree.item(children[0])["text"] == t("file_browser.loading"):
                self.tree.delete(children[0])

                folder_path = self.tree.item(item, "values")[0]

                self.populate_file_tree(folder_path, item)
    
    def on_file_tree_select(self, event):
        """
        处理文件树选择事件
        
        Args:
            event: 事件对象
        """
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_path = self.tree.item(item, "values")[0] if self.tree.item(item, "values") else None
            if file_path and os.path.isfile(file_path):
                self.app.multi_editor.open_file_in_new_tab(file_path)
    
    def refresh_file_tree(self):
        """
        刷新文件树
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.populate_file_tree(".")
    
    def open_folder(self, folder_path):
        """
        打开指定文件夹

        Args:
            folder_path: 文件夹路径
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.populate_file_tree(folder_path)