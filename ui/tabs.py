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
from i18n import t


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
        title_label = Label(self, text=t("settings.title"), 
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
        search_entry.insert(0, t("settings.search-placeholder"))
        
        def clear_search_placeholder(event):
            if search_var.get() == t("settings.search-placeholder"):
                search_entry.delete(0, "end")
        
        def restore_search_placeholder(event):
            if not search_var.get():
                search_entry.insert(0, t("settings.search-placeholder"))
        
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
            if not search_text or search_text == t("settings.search-placeholder"):
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
                search_results_label.config(text=t("settings.search-results", count=len(matched_items)))
                search_results_frame.pack(fill="x", pady=(5, 0))
            else:
                search_results_label.config(text=t("settings.no-results"))
                search_results_frame.pack(fill="x", pady=(5, 0))
        
        # 绑定搜索事件
        search_var.trace_add("write", search_settings)

        # 创建选项卡框架
        notebook = Notebook(self)
        notebook.pack(fill="both", expand=True)

        # 编辑器设置选项卡
        editor_frame = Frame(notebook)
        notebook.add(editor_frame, text=t("settings.tab.editor"))

        # 外观设置选项卡
        appearance_frame = Frame(notebook)
        notebook.add(appearance_frame, text=t("settings.tab.appearance"))

        # 语言设置选项卡
        language_frame = Frame(notebook)
        notebook.add(language_frame, text=t("settings.tab.language"))

        # 高级设置选项卡
        advanced_frame = Frame(notebook)
        notebook.add(advanced_frame, text=t("settings.tab.advanced"))

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
        font_section = LabelFrame(editor_scroll_frame, text=t("settings.section.font"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(font_section, "labelframe")
        font_section.pack(fill="x", padx=10, pady=10)

        font_label = Label(font_section, text=t("settings.font.label"), font=self.style.get_font("sm"))
        apply_modern_style(font_label, "label")
        font_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        font_menu = OptionMenu(font_section, font_var, "Consolas", "Courier New", "Monaco", "Menlo", "Source Code Pro", "Fira Code")
        apply_modern_style(font_menu, "button", variant="outline")
        font_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(font_section, t("settings.font.label"), font_menu, "editor", t("settings.font.description"))

        fontsize_label = Label(font_section, text=t("settings.font-size.label"), font=self.style.get_font("sm"))
        apply_modern_style(fontsize_label, "label")
        fontsize_label.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        fontsize_spinbox = Spinbox(font_section, from_=8, to=24, textvariable=fontsize_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(fontsize_spinbox, "entry")
        fontsize_spinbox.grid(row=1, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(font_section, t("settings.font-size.label"), fontsize_spinbox, "editor", t("settings.font-size.description"))

        # 编码设置
        encoding_section = LabelFrame(editor_scroll_frame, text=t("settings.section.encoding"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(encoding_section, "labelframe")
        encoding_section.pack(fill="x", padx=10, pady=10)

        encoding_label = Label(encoding_section, text=t("settings.encoding.label"), font=self.style.get_font("sm"))
        apply_modern_style(encoding_label, "label")
        encoding_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        encoding_menu = OptionMenu(encoding_section, encoding_var, "UTF-8", "GBK", "ASCII", "UTF-16")
        apply_modern_style(encoding_menu, "button", variant="outline")
        encoding_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(encoding_section, t("settings.encoding.label"), encoding_menu, "editor", t("settings.encoding.description"))

        # ========== 外观设置选项卡 ==========
        appearance_scroll_frame = Frame(appearance_frame)
        apply_modern_style(appearance_scroll_frame, "frame")
        appearance_scroll_frame.pack(fill="both", expand=True)

        # 主题设置
        theme_section = LabelFrame(appearance_scroll_frame, text=t("settings.section.theme"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(theme_section, "labelframe")
        theme_section.pack(fill="x", padx=10, pady=10)

        theme_label = Label(theme_section, text=t("settings.theme.label"), font=self.style.get_font("sm"))
        apply_modern_style(theme_label, "label")
        theme_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        theme_menu = OptionMenu(theme_section, theme_var, "vscode-dark", "vscode-light", "github-dark", "github-light")
        apply_modern_style(theme_menu, "button", variant="outline")
        theme_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(theme_section, t("settings.theme.label"), theme_menu, "appearance", t("settings.theme.description"))

        # 界面缩放设置
        zoom_section = LabelFrame(appearance_scroll_frame, text=t("settings.section.zoom"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(zoom_section, "labelframe")
        zoom_section.pack(fill="x", padx=10, pady=10)

        zoom_var = IntVar(value=100)
        zoom_label = Label(zoom_section, text=t("settings.zoom.label"), font=self.style.get_font("sm"))
        apply_modern_style(zoom_label, "label")
        zoom_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        zoom_spinbox = Spinbox(zoom_section, from_=50, to=200, textvariable=zoom_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(zoom_spinbox, "entry")
        zoom_spinbox.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(zoom_section, t("settings.zoom.label"), zoom_spinbox, "appearance", t("settings.zoom.description"))

        # ========== 语言设置选项卡 ==========
        language_scroll_frame = Frame(language_frame)
        apply_modern_style(language_scroll_frame, "frame")
        language_scroll_frame.pack(fill="both", expand=True)

        # 界面语言设置
        ui_language_section = LabelFrame(language_scroll_frame, text=t("settings.section.interface-language"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(ui_language_section, "labelframe")
        ui_language_section.pack(fill="x", padx=10, pady=10)

        language_var = StringVar(value="zh-CN")
        language_label = Label(ui_language_section, text=t("settings.language.label"), font=self.style.get_font("sm"))
        apply_modern_style(language_label, "label")
        language_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        language_menu = OptionMenu(ui_language_section, language_var, "zh-CN", "en-US")
        apply_modern_style(language_menu, "button", variant="outline")
        language_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(ui_language_section, t("settings.language.label"), language_menu, "language", t("settings.language.description"))

        # 代码语言支持
        code_language_section = LabelFrame(language_scroll_frame, text=t("settings.section.code-languages"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(code_language_section, "labelframe")
        code_language_section.pack(fill="x", padx=10, pady=10)

        code_language_label = Label(code_language_section, text=t("settings.code-languages.label"), font=self.style.get_font("sm"))
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
            add_setting_item(code_language_section, t("settings.enable-language", lang=lang), cb, "language", t("settings.enable-language-desc", lang=lang))

        # ========== 高级设置选项卡 ==========
        advanced_scroll_frame = Frame(advanced_frame)
        apply_modern_style(advanced_scroll_frame, "frame")
        advanced_scroll_frame.pack(fill="both", expand=True)

        # 自动保存设置
        autosave_section = LabelFrame(advanced_scroll_frame, text=t("settings.section.autosave"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(autosave_section, "labelframe")
        autosave_section.pack(fill="x", padx=10, pady=10)

        autosave_var = BooleanVar(value=True)
        autosave_check = Checkbutton(autosave_section, text=t("settings.autosave.label"), variable=autosave_var, font=self.style.get_font("sm"))
        apply_modern_style(autosave_check, "checkbutton")
        autosave_check.grid(row=0, column=0, sticky="w", padx=15, pady=10, columnspan=2)
        add_setting_item(autosave_section, t("settings.autosave.label"), autosave_check, "advanced", t("settings.autosave.description"))

        autosave_interval_var = IntVar(value=5)
        autosave_interval_label = Label(autosave_section, text=t("settings.autosave-interval.label"), font=self.style.get_font("sm"))
        apply_modern_style(autosave_interval_label, "label")
        autosave_interval_label.grid(row=1, column=0, sticky="w", padx=15, pady=10)
        autosave_interval_spinbox = Spinbox(autosave_section, from_=1, to=60, textvariable=autosave_interval_var, width=10, font=self.style.get_font("sm"))
        apply_modern_style(autosave_interval_spinbox, "entry")
        autosave_interval_spinbox.grid(row=1, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(autosave_section, t("settings.autosave-interval.label"), autosave_interval_spinbox, "advanced", t("settings.autosave-interval.description"))

        # 日志设置
        log_section = LabelFrame(advanced_scroll_frame, text=t("settings.section.logging"), font=self.style.get_font("lg", "bold"))
        apply_modern_style(log_section, "labelframe")
        log_section.pack(fill="x", padx=10, pady=10)

        log_level_var = StringVar(value="INFO")
        log_level_label = Label(log_section, text=t("settings.log-level.label"), font=self.style.get_font("sm"))
        apply_modern_style(log_level_label, "label")
        log_level_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        log_level_menu = OptionMenu(log_section, log_level_var, "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        apply_modern_style(log_level_menu, "button", variant="outline")
        log_level_menu.grid(row=0, column=1, sticky="w", padx=15, pady=10)
        add_setting_item(log_section, t("settings.log-level.label"), log_level_menu, "advanced", t("settings.log-level.description"))

        # ========== 保存设置按钮 ==========
        save_frame = Frame(self)
        apply_modern_style(save_frame, "frame")
        save_frame.pack(fill="x", padx=5, pady=20)

        save_button = Button(save_frame, text=t("settings.save-button"), font=self.style.get_font("md"))
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
            messagebox.showinfo(t("settings.save-title"), t("settings.save-message"))
        
        save_button.config(command=save_settings)
    
    def get_title(self):
        """
        获取Tab标题
        """
        return t("settings.title")
    
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
        title_label = Label(self, text=t("help.title"), 
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
        notebook.add(basic_frame, text=t("help.tab.about"))
        
        # 高级功能帮助选项卡
        advanced_frame = Frame(notebook)
        notebook.add(advanced_frame, text=t("help.tab.features"))
        
        # 快捷键帮助选项卡
        shortcuts_frame = Frame(notebook)
        notebook.add(shortcuts_frame, text=t("help.tab.shortcuts"))
        
        # 故障排除帮助选项卡
        troubleshooting_frame = Frame(notebook)
        notebook.add(troubleshooting_frame, text=t("help.tab.troubleshooting"))
        
        # ========== 版本信息 ==========
        basic_text = Text(basic_frame, wrap="word", font=self.style.get_font("base"))
        basic_scrollbar = Scrollbar(basic_frame, command=basic_text.yview)
        basic_text.config(yscrollcommand=basic_scrollbar.set)
        
        basic_scrollbar.pack(side="right", fill="y")
        basic_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        basic_content = f'{t("help.about.title")}\n\n'
        basic_content += f'version: v0.1.1\n'
        basic_content += f'{t("help.about.description")}\n'
        
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
        
        advanced_content = f'{t("help.features.title")}\n\n'
        advanced_content += f'- {t("help.features.code-highlight")}\n'
        advanced_content += f'- {t("help.features.theme-setting")}\n'
        advanced_content += f'- {t("help.features.syntax-check")}\n'
        advanced_content += f'- {t("help.features.code-format")}\n'
        advanced_content += f'- {t("help.features.code-completion")}\n'
        advanced_content += f'- {t("help.features.code-navigation")}\n'
        advanced_content += f'- {t("help.features.code-comment")}\n'
        advanced_content += f'- {t("help.features.code-folding")}\n'
        
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
        
        shortcuts_content = f"# {t('help.shortcuts.title')}\n\n"
        shortcuts_content += f"## {t('help.shortcuts.file-operations')}\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += f"| {t('menus.new-file')} | Ctrl+N |\n"
        shortcuts_content += f"| {t('menus.open-file')} | Ctrl+O |\n"
        shortcuts_content += f"| {t('menus.save-file')} | Ctrl+S |\n"
        shortcuts_content += f"| {t('menus.save-as-file')} | Ctrl+Shift+S |\n\n"
        
        shortcuts_content += f"## {t('help.shortcuts.edit-operations')}\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += f"| {t('menus.undo')} | Ctrl+Z |\n"
        shortcuts_content += f"| {t('menus.redo')} | Ctrl+Y |\n"
        shortcuts_content += f"| {t('menus.copy')} | Ctrl+C |\n"
        shortcuts_content += f"| {t('menus.paste')} | Ctrl+V |\n"
        shortcuts_content += f"| {t('menus.delete')} | Ctrl+X |\n\n"
        
        shortcuts_content += f"## {t('help.shortcuts.run-operations')}\n\n"
        shortcuts_content += "| 操作 | 快捷键 |\n"
        shortcuts_content += "|------|--------|\n"
        shortcuts_content += f"| {t('menus.run')} | F5 |\n"
        shortcuts_content += f"| {t('menus.clear-output')} | Ctrl+L |\n\n"
        
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
        
        troubleshooting_content = f"# {t('help.troubleshooting.title')}\n\n"
        troubleshooting_content += f"## 1. {t('help.troubleshooting.common-issues')}\n\n"
        troubleshooting_content += f"### {t('help.troubleshooting.issue-not-start-title')}\n"
        troubleshooting_content += f"{t('help.troubleshooting.issue-not-start-desc')}\n\n"
        
        troubleshooting_content += f"### {t('help.troubleshooting.issue-cannot-run-title')}\n"
        troubleshooting_content += f"{t('help.troubleshooting.issue-cannot-run-desc')}\n\n"
        
        troubleshooting_content += f"### {t('help.troubleshooting.issue-theme-title')}\n"
        troubleshooting_content += f"{t('help.troubleshooting.issue-theme-desc')}\n\n"
        
        troubleshooting_text.insert("1.0", troubleshooting_content)
        troubleshooting_text.config(state="disabled")
        apply_modern_style(troubleshooting_text, "text")
        apply_modern_style(troubleshooting_scrollbar, "scrollbar")
    
    def get_title(self):
        """
        获取Tab标题
        """
        return t("help.title")
    
    def refresh(self):
        """
        刷新帮助面板内容
        """
        # 重新加载帮助内容
        pass