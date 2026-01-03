"""
标签页组件模块
包含设置面板和帮助面板的独立Tab类组件
"""

import json
from tkinter import (Frame, Label, Button, Text, Scrollbar, Entry, StringVar, 
                    IntVar, BooleanVar, OptionMenu, Checkbutton, Listbox, 
                    Scale, Canvas, PhotoImage, LabelFrame, Spinbox) 
from tkinter.font import Font
from tkinter.ttk import Notebook, Combobox
from library.ui_styles import apply_modern_style, get_style
from library.api import Settings
from pathlib import Path
import os


class SettingsTab(Frame):
    """
    设置面板Tab组件
    """
    
    def __init__(self, parent, app, codehighlighter, codehighlighter2):
        """
        初始化设置面板Tab
        
        Args:
            parent: 父容器
            app: 应用程序实例
            codehighlighter: 代码高亮器
            codehighlighter2: 终端高亮器
        """
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.codehighlighter = codehighlighter
        self.codehighlighter2 = codehighlighter2
        
        # 加载语言设置
        with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
            self.lang_dict = json.load(fp)
        
        # 应用样式
        self.style = get_style()
        apply_modern_style(self, "frame", style="surface")
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI组件
        """
        # 创建主布局
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建标题
        title_label = Label(self, text=self.lang_dict["settings"]["title"], 
                          font=self.style.get_font("xl", "bold"))
        apply_modern_style(title_label, "label", style="heading")
        title_label.pack(anchor="w", pady=(0, 20))
        
        # 创建设置内容区域
        self._create_settings_content()
    
    def _create_settings_content(self):
        """
        创建设置面板内容
        """
        # 创建搜索框
        search_frame = Frame(self)
        apply_modern_style(search_frame, "frame")
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, font=self.style.get_font("base"))
        apply_modern_style(search_entry, "entry")
        search_entry.pack(fill="x", padx=5, pady=5)
        search_entry.insert(0, "搜索设置...")
        
        def clear_search_placeholder(event):
            if search_var.get() == "搜索设置...":
                search_entry.delete(0, "end")
        
        def restore_search_placeholder(event):
            if not search_var.get():
                search_entry.insert(0, "搜索设置...")
        
        search_entry.bind("<FocusIn>", clear_search_placeholder)
        search_entry.bind("<FocusOut>", restore_search_placeholder)
        
        # 创建搜索结果框架
        search_results_frame = Frame(self)
        apply_modern_style(search_results_frame, "frame")
        search_results_label = Label(search_results_frame, text="", font=self.style.get_font("sm"))
        apply_modern_style(search_results_label, "label", style="text_muted")
        search_results_label.pack(fill="x", pady=(5, 0))
        
        # 存储所有设置项信息
        settings_items = []
        
        def add_setting_item(frame, label_text, widget, category, description=""):
            """添加设置项并记录信息"""
            settings_items.append({
                "frame": frame,
                "label_text": label_text,
                "widget": widget,
                "category": category,
                "description": description
            })
        
        def search_settings(*args):
            """搜索设置项"""
            search_text = search_var.get().lower().strip()
            
            # 如果搜索框为空或为占位符，显示所有设置项
            if not search_text or search_text == "搜索设置":
                for item in settings_items:
                    item["frame"].pack(fill="x", padx=5, pady=5)
                search_results_frame.pack_forget()
                return
            
            # 搜索匹配的设置项
            matched_items = []
            for item in settings_items:
                label_match = search_text in item["label_text"].lower()
                category_match = search_text in item["category"].lower()
                description_match = search_text in item["description"].lower()
                
                if label_match or category_match or description_match:
                    matched_items.append(item)
                    item["frame"].pack(fill="x", padx=5, pady=5)
                else:
                    item["frame"].pack_forget()
            
            # 显示搜索结果信息
            if matched_items:
                search_results_label.config(text=f"找到 {len(matched_items)} 个匹配的设置项")
                search_results_frame.pack(fill="x", pady=(5, 0))
            else:
                search_results_label.config(text="未找到匹配的设置项")
                search_results_frame.pack(fill="x", pady=(5, 0))
        
        # 绑定搜索事件
        search_var.trace_add("write", search_settings)

        # 创建选项卡框架
        notebook = Notebook(self)
        notebook.pack(fill="both", expand=True)

        # 编辑器设置选项卡
        editor_frame = Frame(notebook)
        notebook.add(editor_frame, text="编辑器")

        # 外观设置选项卡
        appearance_frame = Frame(notebook)
        notebook.add(appearance_frame, text="外观")

        # 语言设置选项卡
        language_frame = Frame(notebook)
        notebook.add(language_frame, text="语言")

        # 高级设置选项卡
        advanced_frame = Frame(notebook)
        notebook.add(advanced_frame, text="高级")

        # 从library.api导入Settings
        from library.api import Settings
        
        # 定义设置变量
        theme_var = StringVar(value=Settings.Highlighter.syntax_highlighting()["theme"])
        font_var = StringVar(value=Settings.Editor.font())
        fontsize_var = IntVar(value=Settings.Editor.font_size())
        encoding_var = StringVar(value=Settings.Editor.file_encoding())

        # ========== 编辑器设置选项卡 ==========
        editor_scroll_frame = Frame(editor_frame)
        apply_modern_style(editor_scroll_frame, "frame")
        editor_scroll_frame.pack(fill="both", expand=True)

        # 字体设置
        font_section = LabelFrame(editor_scroll_frame, text="字体设置", font=self.style.get_font("lg", "bold"))
        apply_modern_style(font_section, "labelframe")
        font_section.pack(fill="x", padx=10, pady=10)

        font_label = Label(font_section, text="字体:", font=self.style.get_font("sm"))
        apply_modern_style(font_label, "label")
        font_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        font_menu = OptionMenu(font_section, font_var, "Consolas", "Courier New", "Monaco", "Menlo", "Source Code Pro", "Fira Code")
        apply_modern_style(font_menu, "button", variant="outline")
        font_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(font_section, "字体", font_menu, "编辑器", "设置代码编辑器的字体")

        fontsize_label = Label(font_section, text="字体大小:", font=self.style.get_font("sm"))
        apply_modern_style(fontsize_label, "label")
        fontsize_label.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        fontsize_spinbox = Spinbox(font_section, from_=8, to=24, textvariable=fontsize_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(fontsize_spinbox, "entry")
        fontsize_spinbox.grid(row=1, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(font_section, "字体大小", fontsize_spinbox, "编辑器", "设置代码编辑器的字体大小")

        # 编码设置
        encoding_section = LabelFrame(editor_scroll_frame, text="编码设置", font=self.style.get_font("lg", "bold"))
        apply_modern_style(encoding_section, "labelframe")
        encoding_section.pack(fill="x", padx=10, pady=10)

        encoding_label = Label(encoding_section, text="文件编码:", font=self.style.get_font("sm"))
        apply_modern_style(encoding_label, "label")
        encoding_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        encoding_menu = OptionMenu(encoding_section, encoding_var, "UTF-8", "GBK", "ASCII", "UTF-16")
        apply_modern_style(encoding_menu, "button", variant="outline")
        encoding_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(encoding_section, "文件编码", encoding_menu, "编辑器", "设置文件的默认编码")

        # ========== 外观设置选项卡 ==========
        appearance_scroll_frame = Frame(appearance_frame)
        apply_modern_style(appearance_scroll_frame, "frame")
        appearance_scroll_frame.pack(fill="both", expand=True)

        # 主题设置
        theme_section = LabelFrame(appearance_scroll_frame, text="主题设置", font=self.style.get_font("lg", "bold"))
        apply_modern_style(theme_section, "labelframe")
        theme_section.pack(fill="x", padx=10, pady=10)

        theme_label = Label(theme_section, text="主题:", font=self.style.get_font("sm"))
        apply_modern_style(theme_label, "label")
        theme_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        theme_menu = OptionMenu(theme_section, theme_var, "vscode-dark", "vscode-light", "github-dark", "github-light")
        apply_modern_style(theme_menu, "button", variant="outline")
        theme_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(theme_section, "主题", theme_menu, "外观", "设置编辑器的主题")

        # 界面缩放设置
        zoom_section = LabelFrame(appearance_scroll_frame, text="界面缩放", font=self.style.get_font("lg", "bold"))
        apply_modern_style(zoom_section, "labelframe")
        zoom_section.pack(fill="x", padx=10, pady=10)

        zoom_var = IntVar(value=100)
        zoom_label = Label(zoom_section, text="缩放比例:", font=self.style.get_font("sm"))
        apply_modern_style(zoom_label, "label")
        zoom_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        zoom_spinbox = Spinbox(zoom_section, from_=50, to=200, textvariable=zoom_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(zoom_spinbox, "entry")
        zoom_spinbox.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(zoom_section, "缩放比例", zoom_spinbox, "外观", "设置界面缩放比例")

        # ========== 语言设置选项卡 ==========
        language_scroll_frame = Frame(language_frame)
        apply_modern_style(language_scroll_frame, "frame")
        language_scroll_frame.pack(fill="both", expand=True)

        # 界面语言设置
        ui_language_section = LabelFrame(language_scroll_frame, text="界面语言", font=self.style.get_font("lg", "bold"))
        apply_modern_style(ui_language_section, "labelframe")
        ui_language_section.pack(fill="x", padx=10, pady=10)

        language_var = StringVar(value="zh-CN")
        language_label = Label(ui_language_section, text="界面语言:", font=self.style.get_font("sm"))
        apply_modern_style(language_label, "label")
        language_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        language_menu = OptionMenu(ui_language_section, language_var, "zh-CN", "en-US")
        apply_modern_style(language_menu, "button", variant="outline")
        language_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(ui_language_section, "界面语言", language_menu, "语言", "设置编辑器界面语言")

        # 代码语言支持
        code_language_section = LabelFrame(language_scroll_frame, text="代码语言支持", font=self.style.get_font("lg", "bold"))
        apply_modern_style(code_language_section, "labelframe")
        code_language_section.pack(fill="x", padx=10, pady=10)

        code_language_label = Label(code_language_section, text="启用的语言:", font=self.style.get_font("sm"))
        apply_modern_style(code_language_label, "label")
        code_language_label.grid(row=0, column=0, sticky="w", padx=15, pady=10, columnspan=2)

        # 语言列表
        languages = ["Python", "JavaScript", "HTML", "CSS", "Java", "C++", "Go", "Rust"]
        language_vars = []
        for i, lang in enumerate(languages):
            var = BooleanVar(value=True)
            language_vars.append(var)
            cb = Checkbutton(code_language_section, text=lang, variable=var, font=self.style.get_font("sm"))
            apply_modern_style(cb, "checkbutton")
            cb.grid(row=i//2+1, column=i%2, sticky="w", padx=15, pady=5)
            add_setting_item(code_language_section, f"启用{lang}", cb, "语言", f"是否启用{lang}语言支持")

        # ========== 高级设置选项卡 ==========
        advanced_scroll_frame = Frame(advanced_frame)
        apply_modern_style(advanced_scroll_frame, "frame")
        advanced_scroll_frame.pack(fill="both", expand=True)

        # 自动保存设置
        autosave_section = LabelFrame(advanced_scroll_frame, text="自动保存", font=self.style.get_font("lg", "bold"))
        apply_modern_style(autosave_section, "labelframe")
        autosave_section.pack(fill="x", padx=10, pady=10)

        autosave_var = BooleanVar(value=True)
        autosave_check = Checkbutton(autosave_section, text="启用自动保存", variable=autosave_var, font=self.style.get_font("sm"))
        apply_modern_style(autosave_check, "checkbutton")
        autosave_check.grid(row=0, column=0, sticky="w", padx=15, pady=10, columnspan=2)
        add_setting_item(autosave_section, "启用自动保存", autosave_check, "高级", "是否启用文件自动保存")

        autosave_interval_var = IntVar(value=5)
        autosave_interval_label = Label(autosave_section, text="自动保存间隔(秒):", font=self.style.get_font("sm"))
        apply_modern_style(autosave_interval_label, "label")
        autosave_interval_label.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        autosave_interval_spinbox = Spinbox(autosave_section, from_=1, to=60, textvariable=autosave_interval_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(autosave_interval_spinbox, "entry")
        autosave_interval_spinbox.grid(row=1, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(autosave_section, "自动保存间隔", autosave_interval_spinbox, "高级", "设置自动保存的时间间隔")

        # 日志设置
        log_section = LabelFrame(advanced_scroll_frame, text="日志设置", font=self.style.get_font("lg", "bold"))
        apply_modern_style(log_section, "labelframe")
        log_section.pack(fill="x", padx=10, pady=10)

        log_level_var = StringVar(value="INFO")
        log_level_label = Label(log_section, text="日志级别:", font=self.style.get_font("sm"))
        apply_modern_style(log_level_label, "label")
        log_level_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        log_level_menu = OptionMenu(log_section, log_level_var, "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        apply_modern_style(log_level_menu, "button", variant="outline")
        log_level_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(log_section, "日志级别", log_level_menu, "高级", "设置日志记录的级别")

        # ========== 保存设置按钮 ==========
        save_frame = Frame(self)
        apply_modern_style(save_frame, "frame")
        save_frame.pack(fill="x", padx=5, pady=20)

        save_button = Button(save_frame, text="保存设置", font=self.style.get_font("md"))
        apply_modern_style(save_button, "button")
        save_button.pack(side="right", padx=5, pady=5)
        
        def save_settings():
            """保存设置"""
            # 保存设置到配置文件
            settings_data = {
                "editor": {
                    "font": font_var.get(),
                    "font_size": fontsize_var.get(),
                    "file_encoding": encoding_var.get()
                },
                "highlighter": {
                    "syntax_highlighting": {
                        "theme": theme_var.get()
                    }
                }
            }
            
            # 保存到文件
            settings_path = Path(__file__).parent.parent / "asset" / "settings.json"
            with open(settings_path, "w", encoding="utf-8") as fp:
                json.dump(settings_data, fp, indent=2, ensure_ascii=False)
            
            # 应用设置到当前编辑器
            current_editor = self.app.multi_editor.get_current_editor()
            if current_editor:
                # 更新字体
                font = Font(family=font_var.get(), size=fontsize_var.get())
                current_editor.configure(font=font)
                
                # 更新主题
                if self.codehighlighter:
                    theme_file = Path(__file__).parent.parent / "asset" / "theme" / f"{theme_var.get()}.json"
                    if theme_file.exists():
                        with open(theme_file, "r", encoding="utf-8") as f:
                            theme_data = json.load(f)
                        self.codehighlighter.set_theme(theme_data)
                        self.codehighlighter.highlight()
            
            # 显示保存成功消息
            from tkinter import messagebox
            messagebox.showinfo("设置保存", "设置已成功保存！")
        
        save_button.config(command=save_settings)
    
    def get_title(self):
        """
        获取Tab标题
        """
        return self.lang_dict["settings"]["title"]
    
    def refresh(self):
        """
        刷新设置面板内容
        """
        # 重新加载设置
        pass


class HelpTab(Frame):
    """
    帮助面板Tab组件
    """
    
    def __init__(self, parent, app):
        """
        初始化帮助面板Tab
        
        Args:
            parent: 父容器
            app: 应用程序实例
        """
        super().__init__(parent)
        self.parent = parent
        self.app = app
        
        # 加载语言设置
        with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
            self.lang_dict = json.load(fp)
        
        # 应用样式
        self.style = get_style()
        apply_modern_style(self, "frame", style="surface")
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI组件
        """
        # 创建主布局
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建标题
        title_label = Label(self, text="帮助中心", 
                          font=self.style.get_font("xl", "bold"))
        apply_modern_style(title_label, "label", style="heading")
        title_label.pack(anchor="w", pady=(0, 20))
        
        # 创建帮助内容区域
        self._create_help_content()
    
    def _create_help_content(self):
        """
        创建帮助内容区域
        """
        # 创建帮助内容框架
        content_frame = Frame(self)
        apply_modern_style(content_frame, "frame")
        content_frame.pack(fill="both", expand=True)
        
        # 创建帮助内容笔记本
        notebook = Notebook(content_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 基本使用帮助选项卡
        basic_frame = Frame(notebook)
        notebook.add(basic_frame, text="版本信息")
        
        # 高级功能帮助选项卡
        advanced_frame = Frame(notebook)
        notebook.add(advanced_frame, text="功能介绍")
        
        # 快捷键帮助选项卡
        shortcuts_frame = Frame(notebook)
        notebook.add(shortcuts_frame, text="快捷键")
        
        # 故障排除帮助选项卡
        troubleshooting_frame = Frame(notebook)
        notebook.add(troubleshooting_frame, text="故障排除")
        
        # ========== 版本信息 ==========
        basic_text = Text(basic_frame, wrap="word", font=self.style.get_font("base"))
        basic_scrollbar = Scrollbar(basic_frame, command=basic_text.yview)
        basic_text.config(yscrollcommand=basic_scrollbar.set)
        
        basic_scrollbar.pack(side="right", fill="y")
        basic_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        basic_content = '版本信息\n\n'
        basic_content += 'version: v0.1.1\n'
        basic_content += '- 重构了编辑器的UI界面，使其更加现代化和用户友好\n'
        basic_content += '- 将帮助页面、设置页面整合到了主窗口中\n'
        
        basic_text.insert("1.0", basic_content)
        basic_text.config(state="disabled")
        apply_modern_style(basic_text, "text")
        apply_modern_style(basic_scrollbar, "scrollbar")
        
        # ========== 功能介绍 ==========
        advanced_text = Text(advanced_frame, wrap="word", font=self.style.get_font("base"))
        advanced_scrollbar = Scrollbar(advanced_frame, command=advanced_text.yview)
        advanced_text.config(yscrollcommand=advanced_scrollbar.set)
        
        advanced_scrollbar.pack(side="right", fill="y")
        advanced_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        advanced_content = '功能介绍\n\n'
        advanced_content += '- 代码高亮\n'
        advanced_content += '- 主题设置\n'
        advanced_content += '- 语法检查\n'
        advanced_content += '- 代码格式化\n'
        advanced_content += '- 代码补全\n'
        advanced_content += '- 代码跳转\n'
        advanced_content += '- 代码注释\n'
        advanced_content += '- 代码折叠\n'
        
        advanced_text.insert("1.0", advanced_content)
        advanced_text.config(state="disabled")
        apply_modern_style(advanced_text, "text")
        apply_modern_style(advanced_scrollbar, "scrollbar")
        
        # ========== 快捷键帮助 ==========
        shortcuts_text = Text(shortcuts_frame, wrap="word", font=self.style.get_font("base"))
        shortcuts_scrollbar = Scrollbar(shortcuts_frame, command=shortcuts_text.yview)
        shortcuts_text.config(yscrollcommand=shortcuts_scrollbar.set)
        
        shortcuts_scrollbar.pack(side="right", fill="y")
        shortcuts_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        shortcuts_content = "# 快捷键\n\n"
        shortcuts_content += "## 文件操作\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += "| 新建文件 | Ctrl+N |\n"
        shortcuts_content += "| 打开文件 | Ctrl+O |\n"
        shortcuts_content += "| 保存文件 | Ctrl+S |\n"
        shortcuts_content += "| 另存为 | Ctrl+Shift+S |\n\n"
        
        shortcuts_content += "## 编辑操作\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += "| 撤销 | Ctrl+Z |\n"
        shortcuts_content += "| 重做 | Ctrl+Y |\n"
        shortcuts_content += "| 复制 | Ctrl+C |\n"
        shortcuts_content += "| 粘贴 | Ctrl+V |\n"
        shortcuts_content += "| 删除 | Ctrl+X |\n\n"
        
        shortcuts_content += "## 运行操作\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += "| 运行代码 | F5 |\n"
        shortcuts_content += "| 清空输出 | Ctrl+L |\n\n"
        
        shortcuts_text.insert("1.0", shortcuts_content)
        shortcuts_text.config(state="disabled")
        apply_modern_style(shortcuts_text, "text")
        apply_modern_style(shortcuts_scrollbar, "scrollbar")
        
        # ========== 故障排除帮助 ==========
        troubleshooting_text = Text(troubleshooting_frame, wrap="word", font=self.style.get_font("base"))
        troubleshooting_scrollbar = Scrollbar(troubleshooting_frame, command=troubleshooting_text.yview)
        troubleshooting_text.config(yscrollcommand=troubleshooting_scrollbar.set)
        
        troubleshooting_scrollbar.pack(side="right", fill="y")
        troubleshooting_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        troubleshooting_content = "# 故障排除\n\n"
        troubleshooting_content += "## 1. 常见问题\n\n"
        troubleshooting_content += "### 问题：编辑器无法启动\n"
        troubleshooting_content += "解决方案：检查Python环境是否正确安装，确保所有依赖项已安装。\n\n"
        
        troubleshooting_content += "### 问题：代码无法运行\n"
        troubleshooting_content += "解决方案：\n"
        troubleshooting_content += "1. 检查代码是否有语法错误\n"
        troubleshooting_content += "2. 检查运行配置是否正确\n"
        troubleshooting_content += "3. 查看输出窗口的错误信息\n\n"
        
        troubleshooting_content += "### 问题：主题切换无效\n"
        troubleshooting_content += "解决方案：\n"
        troubleshooting_content += "1. 确保主题文件存在于asset/theme目录中\n"
        troubleshooting_content += "2. 尝试重新启动编辑器\n\n"
        
        troubleshooting_text.insert("1.0", troubleshooting_content)
        troubleshooting_text.config(state="disabled")
        apply_modern_style(troubleshooting_text, "text")
        apply_modern_style(troubleshooting_scrollbar, "scrollbar")
    
    def get_title(self):
        """
        获取Tab标题
        """
        return "帮助"
    
    def refresh(self):
        """
        刷新帮助面板内容
        """
        # 重新加载帮助内容
        pass