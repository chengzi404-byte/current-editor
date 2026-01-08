"""
文件浏览器模块
"""

from tkinter import Frame, Label, Button, LEFT, RIGHT, X, BOTH, Y
from tkinter.ttk import Treeview, Scrollbar
from library.ui_styles import apply_modern_style, get_style
from pathlib import Path
import os


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
        
        # 创建文件树标题栏
        self._create_file_tree_header()
        
        # 创建文件树容器
        self._create_file_tree_container()
        
        # 创建文件树
        self._create_file_tree()
        
        # 绑定文件树事件
        self._bind_file_tree_events()
        
        # 初始化文件树
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
            text="文件浏览器", 
            font=self.style.get_font("lg", "bold")
        )
        apply_modern_style(self.file_tree_title, "label")
        self.file_tree_title.pack(side=LEFT, padx=15, pady=15)
        
        # 添加刷新按钮
        self.refresh_button = Button(
            self.file_tree_header, 
            text=f" {self.style.get_icon('refresh')} 刷新", 
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
        
        # 添加文件树滚动条
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
        abs_path = os.path.abspath(path)  # 转换为绝对路径
        
        # 获取文件列表并按规则排序
        items = os.listdir(abs_path)
        
        # 分离文件夹和文件
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
        
        # 对文件夹按字典序排序
        folders.sort(key=str.lower)
        
        # 对文件进行处理：按扩展名分组，然后排序
        file_groups = {}
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in file_groups:
                file_groups[ext] = []
            file_groups[ext].append(file)
        
        # 对每个扩展名组内的文件按字典序排序
        for ext in file_groups:
            file_groups[ext].sort(key=str.lower)
        
        # 按扩展名的字典序排序各个组
        sorted_extensions = sorted(file_groups.keys())
        
        # 先插入排序后的文件夹
        for folder in folders:
            folder_path = os.path.join(abs_path, folder)
            icon = "📁"
            node_id = self.tree.insert(parent, "end", text=f" {icon} {folder}", values=[folder_path])
            # 为文件夹添加一个空的子节点，实现展开效果
            self.tree.insert(node_id, "end", text="加载中...")
        
        # 再插入排序后的文件组
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
            # 检查是否已经有子节点
            children = self.tree.get_children(item)
            if len(children) == 1 and self.tree.item(children[0])["text"] == "加载中...":
                # 移除加载中的占位符
                self.tree.delete(children[0])
                
                # 获取文件夹路径
                folder_path = self.tree.item(item, "values")[0]
                
                # 填充子节点
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
                # 打开文件
                self.app.multi_editor.open_file_in_new_tab(file_path)
    
    def refresh_file_tree(self):
        """
        刷新文件树
        """
        # 清空文件树
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重新填充文件树
        self.populate_file_tree(".")
    
    def open_folder(self, folder_path):
        """
        打开指定文件夹
        
        Args:
            folder_path: 文件夹路径
        """
        # 清空现有的文件树
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 重新填充文件树
        self.populate_file_tree(folder_path)
