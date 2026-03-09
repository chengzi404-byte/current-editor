"""
主窗口UI模块
"""

from tkinter import (Tk, Frame, BOTH, VERTICAL, HORIZONTAL, Text, Label)
from tkinter.ttk import PanedWindow, Treeview, Scrollbar
from library.ui_styles import apply_modern_style, get_style
from library.api import Settings
from i18n import t

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
        
        # 设置窗口属性
        self.title(t("title"))
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
        self._create_flake8_area()
        
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
    
    def _create_flake8_area(self):
        """
        创建flake8结果区域（表格形式）
        """
        from tkinter import ttk as ttk2
        
        flake8_frame = Frame(self.code_paned)
        apply_modern_style(flake8_frame, "frame", style="surface")
        
        header_frame = Frame(flake8_frame, bg="#1e1e1e", height=30)
        header_frame.pack(fill="x", padx=(5, 0))
        header_frame.pack_propagate(False)
        
        title_label = Label(
            header_frame,
            text="🐛 问题检测",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff",
            padx=10,
            anchor="w"
        )
        title_label.pack(side="left", fill="both", expand=True)
        
        self.error_count_label = Label(
            header_frame,
            text="0 个问题",
            font=("Microsoft YaHei UI", 9),
            bg="#1e1e1e",
            fg="#888888",
            padx=10
        )
        self.error_count_label.pack(side="right")
        
        tree_frame = Frame(flake8_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        style2 = ttk2.Style()
        style2.theme_use("clam")
        
        style2.configure(
            "Flake8.Treeview",
            background="#252526",
            foreground="#d4d4d4",
            fieldbackground="#252526",
            rowheight=28,
            font=("Microsoft YaHei UI", 9)
        )
        style2.configure(
            "Flake8.Treeview.Heading",
            background="#333333",
            foreground="#ffffff",
            font=("Microsoft YaHei UI", 9, "bold"),
            relief="flat"
        )
        style2.map(
            "Flake8.Treeview",
            background=[("selected", "#094771")],
            foreground=[("selected", "#ffffff")]
        )
        style2.map(
            "Flake8.Treeview.Heading",
            background=[("active", "#3e3e42")]
        )
        
        self.flake8_tree = Treeview(
            tree_frame,
            columns=("icon", "line", "column", "code", "message"),
            show="tree headings",
            selectmode="browse",
            style="Flake8.Treeview",
            height=5
        )
        
        self.flake8_tree.column("#0", width=0, stretch=False)
        self.flake8_tree.column("icon", width=30, anchor="center", stretch=False)
        self.flake8_tree.column("line", width=50, anchor="center", stretch=False)
        self.flake8_tree.column("column", width=50, anchor="center", stretch=False)
        self.flake8_tree.column("code", width=80, anchor="center", stretch=False)
        self.flake8_tree.column("message", width=300, anchor="w")
        
        self.flake8_tree.heading("#0", text="")
        self.flake8_tree.heading("icon", text="")
        self.flake8_tree.heading("line", text="行")
        self.flake8_tree.heading("column", text="列")
        self.flake8_tree.heading("code", text="类型")
        self.flake8_tree.heading("message", text="描述")
        
        vsb = Scrollbar(tree_frame, orient="vertical", command=self.flake8_tree.yview)
        hsb = Scrollbar(tree_frame, orient="horizontal", command=self.flake8_tree.xview)
        self.flake8_tree.configure(yscrollcommand=self._on_vsb, xscrollcommand=hsb.set)
        
        def on_vsb(*args):
            vsb.set(*args)
            self.flake8_tree.yview_moveto(args[0])
        
        vsb.config(command=on_vsb)
        
        self.flake8_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        self.flake8_tree.bind("<ButtonRelease-1>", self._on_flake8_item_click)
        
        self.code_paned.add(flake8_frame, weight=1)
        
        self.after(100, lambda: self.code_paned.sashpos(0, int(self.winfo_height() * 0.7)))

    def _on_vsb(self, *args):
        pass

    def _on_flake8_item_click(self, event):
        """点击flake8表格项时跳转到对应代码行"""
        selection = self.flake8_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.flake8_tree.item(item, "values")
        if len(values) >= 2:
            try:
                line_num = int(values[1])
                self._goto_line(line_num)
            except (ValueError, IndexError):
                pass

    def _goto_line(self, line_num):
        """跳转到指定行"""
        from library.multi_file_editor import MultiFileEditor
        for widget in self.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, MultiFileEditor):
                    editor = child.get_current_editor()
                    if editor:
                        editor.focus_set()
                        editor.mark_set("insert", f"{line_num}.0")
                        editor.see(f"{line_num}.0")
                        editor.tag_remove("sel", "1.0", "end")
                        editor.tag_add("sel", f"{line_num}.0", f"{line_num}.end")
                        break