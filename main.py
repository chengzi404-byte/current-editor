from library.highlighter_factory import HighlighterFactory
from library.logger import get_logger, shutdown_logger
from library.api import Settings
from library.editor_operations import EditorOperations
from library.ui_styles import apply_modern_style, get_style
from tkinter import messagebox
from tkinter.font import Font
from tkinter import (
    Tk, Menu, Text, BOTH, VERTICAL, HORIZONTAL, Button, Frame, Label, X, Y, LEFT, RIGHT
)
from tkinter.ttk import PanedWindow, Entry, Notebook, Treeview, Scrollbar
from pathlib import Path
from library import directory
import os
import json
import easygui

# -------------------- Global Variables --------------------
global settings, highlighter_factory, file_path, logger
global codehighlighter2, codehighlighter, APIKEY
logger = get_logger()
highlighter_factory = HighlighterFactory()
file_path = "temp_script.txt"

# 记录程序启动信息
logger.info("程序启动")

with open(f"{Path.cwd() / 'asset' / 'settings.json'}", "r", encoding="utf-8") as fp:
    settings = json.load(fp)

# Load language settings
with open(Settings.Editor.langfile(), "r", encoding="utf-8") as fp:
    lang_dict = json.load(fp)

if not directory.test():
    directory.initlaze()

with open(f"{Path.cwd() / 'asset' / 'packages' / 'themes.dark.json'}", "r", encoding="utf-8") as fp:
    dark_themes = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'dark.json'}", "r", encoding="utf-8") as fp:
    dark_terminal_theme = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'light.json'}", "r", encoding="utf-8") as fp:
    light_terminal_theme = json.load(fp)

# -------------------- Create the window and menus --------------------

# Create the main window
root = Tk()
root.title(lang_dict["title"])
root.geometry("1920x980+0+0")

# 应用现代化样式
style = get_style()
apply_modern_style(root, "window")
root.resizable(width=True, height=True)

# Create the main paned window
main_paned = PanedWindow(root, orient=HORIZONTAL)
main_paned.pack(fill=BOTH, expand=True)

# 添加文件树框架
file_tree_frame = Frame(main_paned, width=280)
apply_modern_style(file_tree_frame, "frame", style="card")
main_paned.add(file_tree_frame, weight=1)

# 添加文件树标题栏
file_tree_header = Frame(file_tree_frame)
apply_modern_style(file_tree_header, "frame", style="card")
file_tree_header.pack(fill=X, padx=0, pady=0)

# 文件树标题
file_tree_title = Label(file_tree_header, text="文件浏览器", font=style.get_font("lg", "bold"))
apply_modern_style(file_tree_title, "label")
file_tree_title.pack(side=LEFT, padx=15, pady=15)

# 添加刷新按钮
refresh_button = Button(file_tree_header, text=f" {style.get_icon('refresh')} 刷新", 
                       font=style.get_font("sm"), command=lambda: refresh_file_tree())
apply_modern_style(refresh_button, "button", variant="outline")
refresh_button.pack(side=RIGHT, padx=10, pady=10)

# 创建文件树容器
file_tree_container = Frame(file_tree_frame)
apply_modern_style(file_tree_container, "frame")
file_tree_container.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

# 创建文件树
file_tree = Treeview(file_tree_container, show="tree")
file_tree.heading("#0", text="")
apply_modern_style(file_tree, "treeview")
file_tree.pack(fill=BOTH, expand=True, side=LEFT)

# 添加文件树滚动条
tree_scrollbar = Scrollbar(file_tree_container, orient="vertical", command=file_tree.yview)
apply_modern_style(tree_scrollbar, "scrollbar")
tree_scrollbar.pack(side="right", fill="y")
file_tree.configure(yscrollcommand=tree_scrollbar.set)

# Create the code area paned window
code_paned = PanedWindow(main_paned, orient=VERTICAL)
main_paned.add(code_paned)

# Create the multi-file editor frame
editor_frame = Frame(code_paned)
apply_modern_style(editor_frame, "frame", style="surface")
code_paned.add(editor_frame, weight=2)

# 创建整体终端组件
terminal_area = Text(code_paned, font=Font(root, family=Settings.Editor.font(), size=Settings.Editor.font_size()))
apply_modern_style(terminal_area, "text")
code_paned.add(terminal_area, weight=1)

# commandpaned = PanedWindow(code_paned, orient=HORIZONTAL)
# code_paned.add(commandpaned, weight=1)
# commandarea = Entry(commandpaned, font=Font(root, family=Settings.Editor.font(), size=Settings.Editor.font_size()))
# commandpaned.add(commandarea,weight=18)
# executebutton = Button(text=lang_dict["menus"]["run"])
# commandpaned.add(executebutton, weight=1)

# Initialize multi-file editor
from library.multi_file_editor import MultiFileEditor
multi_editor = MultiFileEditor(editor_frame, terminal_area, None, None)

# 添加文件树功能函数
def populate_file_tree(path=".", parent=""):
    """填充文件树"""
    abs_path = os.path.abspath(path)  # 转换为绝对路径
    
    # 记录文件树填充操作
    logger.info(f"填充文件树: {abs_path}")
    
    # 添加文件夹图标和文件图标
    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        
        # 设置图标
        icon = "📁" if os.path.isdir(item_path) else get_file_icon(item)
        
        node_id = file_tree.insert(parent, "end", text=f" {icon} {item}", values=[item_path])
        
        if os.path.isdir(item_path):
            # 为文件夹添加一个空的子节点，实现展开效果
            file_tree.insert(node_id, "end", text="加载中...")

def get_file_icon(filename):
    """根据文件扩展名返回对应的图标"""
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

def on_file_tree_expand(event):
    """处理文件树展开事件"""
    item = file_tree.focus()
    if item:
        # 检查是否已经有子节点
        children = file_tree.get_children(item)
        if len(children) == 1 and file_tree.item(children[0])["text"] == "加载中...":
            # 移除加载中的占位符
            file_tree.delete(children[0])
            
            # 获取文件夹路径
            folder_path = file_tree.item(item, "values")[0]
            
            # 记录文件夹展开操作
            logger.info(f"展开文件夹: {folder_path}")
            
            # 填充子节点
            populate_file_tree(folder_path, item)

def on_file_tree_select(event):
    """处理文件树选择事件"""
    selection = file_tree.selection()
    if selection:
        item = selection[0]
        file_path = file_tree.item(item, "values")[0] if file_tree.item(item, "values") else None
        if file_path and os.path.isfile(file_path):
            # 记录文件选择操作
            logger.info(f"选择文件: {file_path}")
            multi_editor.open_file_in_new_tab(file_path)

def refresh_file_tree():
    """刷新文件树"""
    # 记录文件树刷新操作
    logger.info("刷新文件树")
    
    # 清空文件树
    for item in file_tree.get_children():
        file_tree.delete(item)
    
    # 重新填充文件树
    populate_file_tree(".")

# 绑定文件树事件
file_tree.bind("<<TreeviewSelect>>", on_file_tree_select)
file_tree.bind("<<TreeviewOpen>>", on_file_tree_expand)

# 初始化文件树
populate_file_tree(".")

# Get the current editor for backward compatibility
codearea = multi_editor.get_current_editor()

# # Config commandpaned widgets background color
# if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes:
#     commandarea.config(background="#2F4F4F")
# else:
#     commandarea.config(background="#F8F8F8")

# Show last edited content
try:
    with open("temp_script.txt", "r", encoding="utf-8") as fp:
        if codearea:
            codearea.insert("1.0", fp.read())
except FileNotFoundError:
    # If temp file doesn't exist, create an empty one
    with open("temp_script.txt", "w", encoding="utf-8") as fp:
        fp.write("")

# 添加全局函数用于打开文件夹
def open_folder_global():
    """全局函数用于打开文件夹"""
    from tkinter import filedialog
    folder_path = filedialog.askdirectory()
    if folder_path:
        # 记录文件夹打开操作
        logger.info(f"打开文件夹: {folder_path}")
        
        # 清空现有的文件树
        for item in file_tree.get_children():
            file_tree.delete(item)
        # 重新填充文件树
        populate_file_tree(folder_path)

# 修改初始化编辑器操作类的代码
editor_ops = EditorOperations(root, codearea, terminal_area, None, None, 
                              None, None, None, None, None, multi_editor)
# 将全局文件树引用附加到root对象上，以便editor_operations可以访问
root.file_tree = file_tree

# Binding
root.bind("<Control-x>", lambda event: editor_ops.delete())
root.bind("<Control-z>", lambda event: editor_ops.undo())
root.bind("<Control-y>", lambda event: editor_ops.redo())
root.bind("<F5>", lambda event: editor_ops.run())
root.bind("<Key>", lambda event: editor_ops.autosave())

# Create all the menus
menu = Menu()
root.config(menu=menu)

# File menu
filemenu = Menu(tearoff=0)
menu.add_cascade(menu=filemenu, label=lang_dict["menus"]["file"])
filemenu.add_command(command=editor_ops.new_file, label=lang_dict["menus"]["new-file"])
filemenu.add_command(command=editor_ops.new_window, label=lang_dict["menus"]["new-window"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.open_file, label=lang_dict["menus"]["open-file"])
filemenu.add_command(command=editor_ops.open_folder, label="打开文件夹")
filemenu.add_command(command=editor_ops.save_file, label=lang_dict["menus"]["save-file"])
filemenu.add_command(command=editor_ops.save_as_file, label=lang_dict["menus"]["save-as-file"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.show_current_file_dir, label=lang_dict["menus"]["show-file-dir"])
filemenu.add_separator()
filemenu.add_command(command=editor_ops.exit_editor, label=lang_dict["menus"]["exit"])

# Edit menu
editmenu = Menu(tearoff=0)
menu.add_cascade(menu=editmenu, label=lang_dict["menus"]["edit"])
editmenu.add_command(command=editor_ops.undo, label=lang_dict["menus"]["undo"])
editmenu.add_command(command=editor_ops.redo, label=lang_dict["menus"]["redo"])
editmenu.add_separator()
editmenu.add_command(command=editor_ops.copy, label=lang_dict["menus"]["copy"])
editmenu.add_command(command=editor_ops.paste, label=lang_dict["menus"]["paste"])
editmenu.add_command(command=editor_ops.delete, label=lang_dict["menus"]["delete"])

# Run menu
runmenu = Menu(tearoff=0)
menu.add_cascade(menu=runmenu, label=lang_dict["menus"]["run"])
runmenu.add_command(command=editor_ops.run, label=lang_dict["menus"]["run"])
runmenu.add_command(command=editor_ops.clear_printarea, label=lang_dict["menus"]["clear-output"])

# Pop menu
popmenu = Menu(root, tearoff=0)
popmenu.add_command(label=lang_dict["menus"]["copy"], command=editor_ops.copy)
popmenu.add_command(label=lang_dict["menus"]["paste"], command=editor_ops.paste)
popmenu.add_command(label=lang_dict["menus"]["undo"], command=editor_ops.undo)
popmenu.add_command(label=lang_dict["menus"]["redo"], command=editor_ops.redo)

# Plugin menu (comming soon)
pluginmenu = Menu(tearoff=0)
menu.add_cascade(menu=pluginmenu, label=lang_dict["menus"]["plugin"])

# Help menu
menu.add_command(label="帮助", command=lambda: messagebox.showinfo(lang_dict["info-window-title"], lang_dict["help"]))

# Settings menu
settingsmenu = Menu(tearoff=0)
menu.add_cascade(menu=settingsmenu, label=lang_dict["menus"]["configure"])
# 设置菜单命令绑定
settingsmenu.add_command(label=lang_dict["menus"]["open-settings"], command=lambda: open_settings())

# 绑定事件
# executebutton.config(command=editor_ops.execute_commands)

# 定义全局变量用于存储高亮器引用
codehighlighter_ref = None
codehighlighter2_ref = None

def open_settings():
    """打开设置面板"""
    editor_ops.open_settings_panel(codehighlighter_ref, codehighlighter2_ref)

# -------------------- 初始化功能 --------------------

# Setup auto-save timer
def schedule_autosave():
    """自动保存定时器"""
    try:
        editor_ops.autosave()
        root.after(5000, schedule_autosave)  # Auto-save every 5 seconds
    except Exception as e:
        logger.error(f"自动保存失败: {str(e)}")

# Start auto-save
schedule_autosave()

# Enable autosave
schedule_autosave()

# Bind popup event
def show_popup(event):
    """显示右键菜单"""
    popmenu.post(event.x_root, event.y_root)

codearea.bind("<Button-3>", show_popup)

# Initialization
try:
    logger.info("开始初始化代码高亮器")
    codehighlighter = highlighter_factory.create_highlighter(codearea, multi_editor.get_current_file_path())
    
    # Check 
    theme_file = f"{Path.cwd() / "asset" / "theme" / Settings.Highlighter.syntax_highlighting()["theme"]}.json"
    if not os.path.exists(theme_file):
        logger.warning(f"主题文件不存在: {theme_file}, 使用默认主题")
        print(f"Theme file {theme_file} not found, using default theme")
        # Use built-in default theme
        theme_data = {
            "base": {
                "background": "#1E1E1E",
                "foreground": "#D4D4D4",
                "insertbackground": "#D4D4D4",
                "selectbackground": "#264F78",
                "selectforeground": "#D4D4D4"
            }
        }
    else:
        # Load theme
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)
            logger.info(f"成功加载主题文件: {theme_file}")
        except Exception as e:
            logger.warning(f"加载主题文件失败: {str(e)}, 使用默认主题")
            theme_data = {
                "base": {
                    "background": "#1E1E1E",
                    "foreground": "#D4D4D4",
                    "insertbackground": "#D4D4D4",
                    "selectbackground": "#264F78",
                    "selectforeground": "#D4D4D4"
                }
            }
    
    # 应用界面样式（侧边栏、窗口、文件树）
    if "sidebar" in theme_data:
        file_tree_frame.configure(bg=theme_data["sidebar"]["background"])
    if "window" in theme_data:
        root.configure(bg=theme_data["window"]["background"])
    if "treeview" in theme_data:
        file_tree.configure(
            bg=theme_data["treeview"]["background"],
            fg=theme_data["treeview"]["foreground"],
            selectbackground=theme_data["treeview"]["selected_background"],
            selectforeground=theme_data["treeview"]["selected_foreground"]
        )
    
    codehighlighter.set_theme(theme_data)
    codehighlighter.highlight()
    logger.info("代码高亮器初始化完成")

    # Use the same configure to the terminal
    codehighlighter2 = highlighter_factory.create_highlighter(terminal_area, "log")
    if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes: 
        codehighlighter2.set_theme(dark_terminal_theme)
        logger.info("使用深色终端主题")
    else: 
        codehighlighter2.set_theme(light_terminal_theme)
        logger.info("使用浅色终端主题")
    
    # Add test log content to demonstrate highlighting
    test_log_content = """2024-01-15 10:30:25 INFO [main] Starting application...
2024-01-15 10:30:26 DEBUG [database] Connected to database at 192.168.1.100:5432
2024-01-15 10:30:27 WARNING [config] Configuration file not found: /etc/app/config.json
2024-01-15 10:30:28 ERROR [api] Failed to connect to API endpoint: https://api.example.com/v1
2024-01-15 10:30:29 CRITICAL [system] Out of memory! Shutting down...
Exception: MemoryError at line 45 in file /usr/local/bin/app.py
Stack trace:
  File "/usr/local/bin/app.py", line 45, in main
    data = load_large_dataset("huge_file.csv")
  File "/usr/local/bin/utils.py", line 123, in load_large_dataset
    return pd.read_csv(filename)
JSON data: {"status": "error", "message": "Memory allocation failed"}
SQL query: SELECT * FROM users WHERE id = 12345;
"""
    terminal_area.insert("1.0", test_log_content)
    
    # 强制设置高亮器标签并立即执行高亮
    codehighlighter2.setup_tags()
    codehighlighter2.highlight()
    
    # 存储高亮器引用到全局变量
    codehighlighter_ref = codehighlighter
    codehighlighter2_ref = codehighlighter2
    
    def on_key(event):
        # Process auto-save
        editor_ops.autosave()
        return None
    
    # Remove all the key binds
    for binding in root.bind_all():
        if binding.startswith('<Key'):
            root.unbind_all(binding)
    
    # Add new key bind
    root.bind("<Key>", on_key, add="+")
    
    logger.info("程序初始化完成，准备启动主循环")
    
except Exception as e:
    logger.error(f"代码高亮器初始化失败: {str(e)}")


# 程序退出时的清理函数
def on_exit():
    """程序退出时的清理操作"""
    logger.info("程序正在退出...")
    
    # 关闭日志系统
    shutdown_logger()
    
    # 销毁主窗口
    root.destroy()

# 绑定窗口关闭事件
root.protocol("WM_DELETE_WINDOW", on_exit)

# 启动主循环
try:
    root.mainloop()
except Exception as e:
    logger.error(f"程序主循环异常: {str(e)}")
    shutdown_logger()