"""
Editor Operations Module
包含从main.py中提取的编辑器操作功能
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import zipfile
import shlex
from pathlib import Path
from tkinter.font import Font
from tkinter import (
    NORMAL, END, DISABLED, W, X, E, BOTH, LEFT, RIGHT, TOP, BOTTOM,
    Toplevel, StringVar, IntVar, BooleanVar, Label, Entry, Spinbox, OptionMenu, Button, Checkbutton, messagebox, filedialog,
    Frame, LabelFrame
)
from tkinter.ttk import Notebook
import requests

from library.logger import setup_logger
from library.api import Settings
from library.ui_styles import apply_modern_style, get_style

logger = setup_logger()


class EditorOperations:
    """编辑器操作类"""
    
    def __init__(self, root, codearea, printarea, inputarea, commandarea, 
                 ai_display, ai_input, ai_send_button, ai_queue, ai_loading, multi_editor=None):
        """
        初始化编辑器操作
        
        Args:
            root: 主窗口对象
            codearea: 代码编辑区域
            printarea: 输出区域
            inputarea: 输入区域
            commandarea: 命令区域
            ai_display: AI显示区域
            ai_input: AI输入区域
            ai_send_button: AI发送按钮
            ai_queue: AI队列
            ai_loading: AI加载状态
            multi_editor: 多文件编辑器实例（可选）
        """
        self.root = root
        self.codearea = codearea
        self.printarea = printarea
        self.inputarea = inputarea
        self.commandarea = commandarea
        self.ai_display = ai_display
        self.ai_input = ai_input
        self.ai_send_button = ai_send_button
        self.ai_queue = ai_queue
        self.ai_loading = ai_loading
        self.multi_editor = multi_editor
        self.file_path = "temp_script.txt"
        self.copy_msg = ""
        
        # 加载语言设置
        with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
            self.lang_dict = json.load(fp)

    # -------------------- AI Functions --------------------
    def send_ai_request_to_api(self, prompt, apikey):
        """发送AI请求到API"""
        self.ai_loading = True
        self.update_ai_loading()
        
        try:
            headers = {
                "Authorization": f"Bearer {apikey}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                self.ai_queue.put(ai_response)
            else:
                error_msg = f"AI Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                self.ai_queue.put(error_msg)
                
        except Exception as e:
            error_msg = f"AI Responce Error: {str(e)}"
            logger.error(error_msg)
            self.ai_queue.put(error_msg)
        finally:
            self.ai_loading = False
            self.update_ai_loading()

    def process_ai_responses(self):
        """处理AI响应"""
        while not self.ai_queue.empty():
            response = self.ai_queue.get()
            self.display_ai_response(response)
            self.ai_queue.task_done()
        self.root.after(100, self.process_ai_responses)

    def display_ai_response(self, response):
        """显示AI响应"""
        current_time = time.strftime("%H:%M:%S")
        self.ai_display.config(state=NORMAL)
        self.ai_display.insert(END, f"AI [{current_time}]:\n{response}\n\n")
        self.ai_display.see(END)
        self.ai_display.config(state=DISABLED)

    def update_ai_loading(self):
        """更新AI加载状态"""
        if self.ai_loading:
            self.ai_send_button.config(text=self.lang_dict["ai"]["sending"], state=DISABLED)
        else:
            self.ai_send_button.config(text=self.lang_dict["ai"]["send"], state=NORMAL)

    def on_ai_input_enter(self, event):
        """AI输入回车事件"""
        self.send_ai_request()

    def send_ai_request(self):
        """发送AI请求"""
        prompt = self.ai_input.get()
        if not prompt:
            return
            
        current_time = time.strftime("%H:%M:%S")
        self.ai_display.config(state=NORMAL)
        self.ai_display.insert(END, f"用户 [{current_time}]:\n{prompt}\n\n")
        self.ai_display.see(END)
        self.ai_display.config(state=DISABLED)
        
        self.ai_input.delete(0, END)
        
        threading.Thread(target=self.send_ai_request_to_api, args=(prompt, Settings.AI.get_api_key()), daemon=True).start()

    # -------------------- Settings Panel Functions --------------------
    def open_settings_panel(self, codehighlighter, codehighlighter2):
        """打开设置面板 - 现代化风格"""
        settings_window = Toplevel(self.root)
        settings_window.title(self.lang_dict["settings"]["title"])
        settings_window.geometry("900x700")
        settings_window.minsize(700, 500)

        # 应用现代化样式
        style = get_style()
        apply_modern_style(settings_window, "window")
        
        # 创建主框架
        main_frame = Frame(settings_window)
        apply_modern_style(main_frame, "frame", style="surface")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 创建搜索框
        search_frame = Frame(main_frame)
        apply_modern_style(search_frame, "frame")
        search_frame.pack(fill=X, pady=(0, 15))
        
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, font=style.get_font("base"))
        apply_modern_style(search_entry, "entry")
        search_entry.pack(fill=X, padx=5, pady=5)
        search_entry.insert(0, "搜索设置...")
        
        def clear_search_placeholder(event):
            if search_var.get() == "搜索设置...":
                search_entry.delete(0, END)
        
        def restore_search_placeholder(event):
            if not search_var.get():
                search_entry.insert(0, "搜索设置...")
        
        search_entry.bind("<FocusIn>", clear_search_placeholder)
        search_entry.bind("<FocusOut>", restore_search_placeholder)
        
        # 创建搜索结果框架
        search_results_frame = Frame(main_frame)
        apply_modern_style(search_results_frame, "frame")
        search_results_label = Label(search_results_frame, text="", font=style.get_font("sm"))
        apply_modern_style(search_results_label, "label", style="text_muted")
        search_results_label.pack(fill=X, pady=(5, 0))
        
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
                    item["frame"].pack(fill=X, padx=5, pady=5)
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
                    item["frame"].pack(fill=X, padx=5, pady=5)
                else:
                    item["frame"].pack_forget()
            
            # 显示搜索结果信息
            if matched_items:
                search_results_label.config(text=f"找到 {len(matched_items)} 个匹配的设置项")
                search_results_frame.pack(fill=X, pady=(5, 0))
            else:
                search_results_label.config(text="未找到匹配的设置项")
                search_results_frame.pack(fill=X, pady=(5, 0))
        
        # 绑定搜索事件
        search_var.trace_add("write", search_settings)

        # 创建选项卡框架
        notebook = Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True)

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

        # 定义设置变量
        theme_var = StringVar(value=Settings.Highlighter.syntax_highlighting()["theme"])
        font_var = StringVar(value=Settings.Editor.font())
        fontsize_var = IntVar(value=Settings.Editor.font_size())
        encoding_var = StringVar(value=Settings.Editor.file_encoding())

        # ========== 编辑器设置选项卡 ==========
        editor_scroll_frame = Frame(editor_frame)
        apply_modern_style(editor_scroll_frame, "frame")
        editor_scroll_frame.pack(fill=BOTH, expand=True)

        # 字体设置
        font_section = LabelFrame(editor_scroll_frame, text="字体设置", font=style.get_font("lg", "bold"))
        apply_modern_style(font_section, "labelframe")
        font_section.pack(fill=X, padx=10, pady=10)

        font_label = Label(font_section, text="字体:", font=style.get_font("sm"))
        apply_modern_style(font_label, "label")
        font_label.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        font_menu = OptionMenu(font_section, font_var, "Consolas", "Courier New", "Monaco", "Menlo", "Source Code Pro", "Fira Code")
        apply_modern_style(font_menu, "button", variant="outline")
        font_menu.grid(row=0, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(font_section, "字体", font_menu, "编辑器", "设置代码编辑器的字体")

        fontsize_label = Label(font_section, text="字体大小:", font=style.get_font("sm"))
        apply_modern_style(fontsize_label, "label")
        fontsize_label.grid(row=1, column=0, sticky=W, padx=15, pady=10)
        fontsize_spinbox = Spinbox(font_section, from_=8, to=24, textvariable=fontsize_var, width=10, font=style.get_font("sm"))
        apply_modern_style(fontsize_spinbox, "entry")
        fontsize_spinbox.grid(row=1, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(font_section, "字体大小", fontsize_spinbox, "编辑器", "设置代码编辑器的字体大小")

        # 编码设置
        encoding_section = LabelFrame(editor_scroll_frame, text="编码设置", font=style.get_font("lg", "bold"))
        apply_modern_style(encoding_section, "labelframe")
        encoding_section.pack(fill=X, padx=10, pady=10)

        encoding_label = Label(encoding_section, text="文件编码:", font=style.get_font("sm"))
        apply_modern_style(encoding_label, "label")
        encoding_label.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        encoding_menu = OptionMenu(encoding_section, encoding_var, "utf-8", "gbk", "gb2312", "ascii")
        apply_modern_style(encoding_menu, "button", variant="outline")
        encoding_menu.grid(row=0, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(encoding_section, "文件编码", encoding_menu, "编辑器", "设置文件保存和打开的编码格式")

        # ========== 外观设置选项卡 ==========
        appearance_scroll_frame = Frame(appearance_frame)
        apply_modern_style(appearance_scroll_frame, "frame")
        appearance_scroll_frame.pack(fill=BOTH, expand=True)

        # 主题设置
        theme_section = LabelFrame(appearance_scroll_frame, text="主题设置", font=style.get_font("lg", "bold"))
        apply_modern_style(theme_section, "labelframe")
        theme_section.pack(fill=X, padx=10, pady=10)

        theme_label = Label(theme_section, text="主题:", font=style.get_font("sm"))
        apply_modern_style(theme_label, "label")
        theme_label.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        theme_menu = OptionMenu(theme_section, theme_var, "vscode-dark", "dracula", "github-dark", "github-light", "material", "monokai", "nord", "one-dark-pro", "solarized-dark", "solarized-light")
        apply_modern_style(theme_menu, "button", variant="outline")
        theme_menu.grid(row=0, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(theme_section, "主题", theme_menu, "外观", "设置代码编辑器的主题")

        def apply_settings():
            """立即应用设置"""
            theme_name = theme_var.get()
            # 加载主题文件
            theme_file = f"{Path.cwd() / 'asset' / 'theme' / theme_name}.json"
            try:
                # 应用更改
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                codehighlighter.set_theme(theme_data)
                self.codearea.configure(font=Font(settings_window, family=font_var.get(), size=fontsize_var.get()))

                # 应用界面样式（侧边栏、窗口、文件树）
                if "sidebar" in theme_data:
                    self.root.file_tree_frame.configure(bg=theme_data["sidebar"]["background"])
                if "window" in theme_data:
                    self.root.configure(bg=theme_data["window"]["background"])
                if "treeview" in theme_data:
                    self.root.file_tree.configure(
                        bg=theme_data["treeview"]["background"],
                        fg=theme_data["treeview"]["foreground"],
                        selectbackground=theme_data["treeview"]["selected_background"],
                        selectforeground=theme_data["treeview"]["selected_foreground"]
                    )

                with open(f"{Path.cwd() / 'asset' / 'packages' / 'themes.dark.json'}", "r", encoding="utf-8") as fp:
                    dark_themes = json.load(fp)
                
                with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'dark.json'}", "r", encoding="utf-8") as fp:
                    dark_terminal_theme = json.load(fp)
                
                with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'light.json'}", "r", encoding="utf-8") as fp:
                    light_terminal_theme = json.load(fp)

                if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes: 
                    codehighlighter2.set_theme(dark_terminal_theme)
                else: 
                    codehighlighter2.set_theme(light_terminal_theme)

                # 写入更改
                Settings.Highlighter.change("theme", theme_name)
                Settings.Editor.change("font", font_var.get())

            except Exception as e:
                print(f"Use theme failed: {str(e)}")
        
        # ========== 语言设置选项卡 ==========
        language_scroll_frame = Frame(language_frame)
        apply_modern_style(language_scroll_frame, "frame")
        language_scroll_frame.pack(fill=BOTH, expand=True)

        # 语言偏好
        language_section = LabelFrame(language_scroll_frame, text="语言偏好", font=style.get_font("lg", "bold"))
        apply_modern_style(language_section, "labelframe")
        language_section.pack(fill=X, padx=10, pady=10)

        lang_var = StringVar(value=Settings.Language.default())
        lang_label = Label(language_section, text="默认语言:", font=style.get_font("sm"))
        apply_modern_style(lang_label, "label")
        lang_label.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        lang_menu = OptionMenu(language_section, lang_var, "python", "javascript", "html", "css", "java", "cpp", "csharp", "php", "ruby", "go", "rust")
        apply_modern_style(lang_menu, "button", variant="outline")
        lang_menu.grid(row=0, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(language_section, "默认语言", lang_menu, "语言", "设置默认的编程语言")

        # 代码类型设置
        code_var = StringVar(value=Settings.Highlighter.code_type())
        code_label = Label(language_section, text="代码类型:", font=style.get_font("sm"))
        apply_modern_style(code_label, "label")
        code_label.grid(row=1, column=0, sticky=W, padx=15, pady=10)
        code_menu = OptionMenu(language_section, code_var, "python", "javascript", "html", "css", "java", "cpp", "csharp", "php", "ruby", "go", "rust")
        apply_modern_style(code_menu, "button", variant="outline")
        code_menu.grid(row=1, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(language_section, "代码类型", code_menu, "语言", "设置代码高亮类型")

        def apply_restart_settings():
            """应用需要重启的设置"""
            lang_file = lang_var.get()
            code_type = code_var.get()
            Settings.Editor.change("lang", lang_file)
            Settings.Highlighter.change("code", code_type)
            messagebox.showinfo(self.lang_dict["info-window-title"], self.lang_dict["settings"]["restart"])

        def clear_cache():
            """清除缓存"""
            import shutil
            cache_dir = Path.cwd() / "library" / "__pycache__"
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                messagebox.showinfo(self.lang_dict["info-window-title"], "缓存已清除")
            else:
                messagebox.showinfo(self.lang_dict["info-window-title"], "缓存目录不存在")

        # 编码设置
        encoding_section = LabelFrame(language_scroll_frame, text="编码设置", font=style.get_font("lg", "bold"))
        apply_modern_style(encoding_section, "labelframe")
        encoding_section.pack(fill=X, padx=10, pady=10)

        auto_detect_var = BooleanVar(value=Settings.Language.auto_detect())
        auto_detect_check = Checkbutton(encoding_section, text="自动检测编码", variable=auto_detect_var, font=style.get_font("sm"))
        apply_modern_style(auto_detect_check, "checkbutton")
        auto_detect_check.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        add_setting_item(encoding_section, "自动检测编码", auto_detect_check, "语言", "自动检测文件编码格式")

        # ========== 高级设置选项卡 ==========
        advanced_scroll_frame = Frame(advanced_frame)
        apply_modern_style(advanced_scroll_frame, "frame")
        advanced_scroll_frame.pack(fill=BOTH, expand=True)

        # 性能设置
        performance_section = LabelFrame(advanced_scroll_frame, text="性能设置", font=style.get_font("lg", "bold"))
        apply_modern_style(performance_section, "labelframe")
        performance_section.pack(fill=X, padx=10, pady=10)

        auto_save_var = BooleanVar(value=Settings.Advanced.auto_save())
        auto_save_check = Checkbutton(performance_section, text="自动保存", variable=auto_save_var, font=style.get_font("sm"))
        apply_modern_style(auto_save_check, "checkbutton")
        auto_save_check.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        add_setting_item(performance_section, "自动保存", auto_save_check, "高级", "启用或禁用自动保存功能")

        save_interval_var = IntVar(value=Settings.Advanced.save_interval())
        interval_label = Label(performance_section, text="保存间隔(秒):", font=style.get_font("sm"))
        apply_modern_style(interval_label, "label")
        interval_label.grid(row=1, column=0, sticky=W, padx=15, pady=10)
        save_interval_spinbox = Spinbox(performance_section, from_=5, to=300, textvariable=save_interval_var, width=10, font=style.get_font("sm"))
        apply_modern_style(save_interval_spinbox, "entry")
        save_interval_spinbox.grid(row=1, column=1, sticky=W, padx=15, pady=10)
        add_setting_item(performance_section, "保存间隔", save_interval_spinbox, "高级", "设置自动保存的时间间隔")

        # 调试设置
        debug_section = LabelFrame(advanced_scroll_frame, text="调试设置", font=style.get_font("lg", "bold"))
        apply_modern_style(debug_section, "labelframe")
        debug_section.pack(fill=X, padx=10, pady=10)

        debug_mode_var = BooleanVar(value=Settings.Advanced.debug_mode())
        debug_mode_check = Checkbutton(debug_section, text="调试模式", variable=debug_mode_var, font=style.get_font("sm"))
        apply_modern_style(debug_mode_check, "checkbutton")
        debug_mode_check.grid(row=0, column=0, sticky=W, padx=15, pady=10)
        add_setting_item(debug_section, "调试模式", debug_mode_check, "高级", "启用或禁用调试模式")

        # 缓存设置
        cache_section = LabelFrame(advanced_scroll_frame, text="缓存设置", font=style.get_font("lg", "bold"))
        apply_modern_style(cache_section, "labelframe")
        cache_section.pack(fill=X, padx=10, pady=10)

        clear_cache_button = Button(cache_section, text="清除缓存", command=clear_cache, font=style.get_font("sm"))
        apply_modern_style(clear_cache_button, "button")
        clear_cache_button.pack(padx=15, pady=10)
        add_setting_item(cache_section, "清除缓存", clear_cache_button, "高级", "清除应用程序的缓存文件")

        # 应用设置按钮
        button_frame = Frame(main_frame)
        apply_modern_style(button_frame, "frame")
        button_frame.pack(fill=X, side=BOTTOM, padx=20, pady=20)

        cancel_button = Button(button_frame, text="取消", command=settings_window.destroy, font=style.get_font("sm"))
        apply_modern_style(cancel_button, "button", variant="outline")
        cancel_button.pack(side=RIGHT, padx=10)

        apply_button = Button(button_frame, text="应用", command=apply_settings, font=style.get_font("sm"))
        apply_modern_style(apply_button, "button", variant="secondary")
        apply_button.pack(side=RIGHT, padx=10)

        ok_button = Button(button_frame, text="确定", command=lambda: [apply_settings(), settings_window.destroy()], font=style.get_font("sm"))
        apply_modern_style(ok_button, "button", variant="primary")
        ok_button.pack(side=RIGHT, padx=10)

        # 绑定事件
        settings_window.bind("<Escape>", lambda e: settings_window.destroy())
        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

        # 居中显示
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() - settings_window.winfo_width()) // 2
        y = (settings_window.winfo_screenheight() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")

        # 立即应用设置
        theme_var.trace_add('write', lambda *args: apply_settings())
        font_var.trace_add('write', lambda *args: apply_settings())
        fontsize_var.trace_add('write', lambda *args: apply_settings())
        encoding_var.trace_add('write', lambda *args: Settings.Editor.change("file-encoding", encoding_var.get()))
        lang_var.trace_add('write', lambda *args: apply_restart_settings())
        code_var.trace_add('write', lambda *args: apply_restart_settings())

    def open_folder(self):
        """打开文件夹并更新文件树"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 清空现有的文件树
            for item in self.root.file_tree.get_children():
                self.root.file_tree.delete(item)
            # 重新填充文件树
            self.populate_file_tree_for_open_folder(folder_path)

    def populate_file_tree_for_open_folder(self, path):
        """为打开文件夹功能填充文件树"""
        import os
        def _populate_subdirectories(tree, path, parent=""):
            """递归填充子目录"""
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                node_id = tree.insert(parent, "end", text=item, values=[item_path])
                
                if os.path.isdir(item_path):
                    _populate_subdirectories(tree, item_path, node_id)
        
        _populate_subdirectories(self.root.file_tree, path)

    # -------------------- File Operations --------------------
    def open_file(self):
        """文件 > 打开文件"""
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
                self.codearea.delete(0.0, END)
                try:
                    with open(self.file_path, encoding=Settings.Editor.file_encoding()) as f:
                        content = f.read()
                    self.codearea.insert(0.0, content)
                except Exception as e:
                    messagebox.showerror("错误", f"打开文件失败: {str(e)}")

    def save_file(self):
        """文件 > 保存文件"""
        if self.multi_editor:
            # 使用多文件编辑器保存文件
            self.multi_editor.save_current_file()
        else:
            # 单文件编辑器模式
            msg = self.codearea.get(0.0, END)
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
        """文件 > 另存为"""
        if self.multi_editor:
            # 使用多文件编辑器另存为文件
            self.multi_editor.save_current_file()  # 在多文件编辑器中，另存为和保存逻辑相同
        else:
            # 单文件编辑器模式
            msg = self.codearea.get(0.0, END)
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
        """文件 > 新建文件"""
        if self.multi_editor:
            # 使用多文件编辑器新建文件
            self.multi_editor.create_new_tab("Untitled", "")
        else:
            # 单文件编辑器模式
            self.file_path = "temp_script.txt"
            self.codearea.delete(0.0, END)

    def new_window(self):
        """文件 > 新建窗口"""
        subprocess.run([sys.executable, "main.py"])

    # -------------------- Edit Operations --------------------
    def copy(self):
        """编辑 > 复制"""
        try:
            self.copy_msg = self.codearea.selection_get()
        except:
            try:
                self.copy_msg = self.printarea.selection_get()
            except:
                pass

    def paste(self):
        """编辑 > 粘贴"""
        try:
            self.codearea.insert("insert", self.copy_msg)
        except:
            pass

    def delete(self):
        """编辑 > 删除选中"""
        try:
            self.codearea.delete("sel.first", "sel.last")
        except:
            pass

    def undo(self):
        """编辑 > 撤销"""
        self.codearea.edit_undo()

    def redo(self):
        """编辑 > 重做"""
        self.codearea.edit_redo()

    # -------------------- Run Operations --------------------
    def run(self):
        """运行 > 运行Python文件"""
        def execute_in_thread():
            try:
                runtool = subprocess.Popen(
                    [sys.executable, Settings.Editor.file_path()],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                input_data = self.inputarea.get(0.0, END).encode('utf-8')
                stdout, stderr = runtool.communicate(input=input_data)

                self.root.after(0, lambda: update_printarea(stdout, stderr))
            except Exception as e:
                self.root.after(0, lambda: self.printarea.insert(END, f"执行错误: {str(e)}\n"))

        def update_printarea(stdout, stderr):
            self.printarea.delete(0.0, END)
            self.printarea.insert(END, f"%Run {Settings.Editor.file_path()}\n")
            self.printarea.insert(END, f"------------------Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}------------------\n")
            self.printarea.insert(END, stdout.decode(errors="replace"))
            self.printarea.insert(END, stderr.decode(errors="replace"))
            self.printarea.insert(END, "\n>>> ")

        threading.Thread(target=execute_in_thread, daemon=True).start()

    def autosave(self):
        """文件 > 自动保存"""
        try:
            content = self.codearea.get("1.0", END)
            if Settings.Editor.file_path() != "temp_script.txt":
                with open(Settings.Editor.file_path(), "w", encoding=Settings.Editor.file_encoding()) as f:
                    f.write(content)
            
            with open("temp_script.txt", "w", encoding=Settings.Editor.file_encoding()) as f:
                f.write(content)
        except Exception as e:
            print(f"Auto-saving failed: {str(e)}")

    def clear_printarea(self):
        """运行 > 清除输出"""
        self.printarea.delete(0.0, END)

    def download_plugin(self):
        """插件 > 下载插件"""
        try:
            plugin_path = filedialog.askopenfilename(
                title="打开插件",
                filetypes=[
                    (self.lang_dict["plugin-types"][0], "*.zip"),
                    (self.lang_dict["plugin-types"][1], "*.*")
                ]
            )
            if plugin_path:
                plugin_zip = zipfile.ZipFile(plugin_path, "r")
                plugin_zip.extractall(f"{Path.cwd() / 'asset' / 'plugins'}")
                plugin_zip.close()
                messagebox.showinfo("Plugin", "Plugin installation successful, please restart the software")
        except Exception as e:
            messagebox.showerror("Error", f"Plugin installation failed: {str(e)}")

    def exit_editor(self):
        """退出"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            sys.exit(0)

    def execute_commands(self):
        """在命令区域执行命令"""
        command = self.commandarea.get()
        try:
            args = shlex.split(command)
            runtool = subprocess.Popen(args, stdin=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                       shell=True)
            
            stdout, stderr = runtool.communicate()

            self.printarea.delete(0.0, END)
            self.printarea.insert(END, stdout.decode(errors="replace"))  # 解码为字符串
            self.printarea.insert(END, stderr.decode(errors="replace"))  # 解码为字符串
        except Exception as e:
            self.printarea.insert(END, f"执行命令时出错: {str(e)}\n")

    def show_current_file_dir(self):
        """显示当前文件目录（绝对路径）"""
        messagebox.showinfo(self.file_path, self.file_path)