"""
应用程序入口文件
"""

from library.highlighter_factory import HighlighterFactory
from library.logger import get_logger, shutdown_logger
from library.api import Settings
from library.multi_file_editor import MultiFileEditor
from library.editor_operations import EditorOperations
from library.file_handle_manager import get_file_manager, shutdown_file_manager
from library.plugins import PluginManager
from ui.main_window import MainWindow
from ui.file_browser import FileBrowser
from ui.menu import MenuBar
from pathlib import Path
from tkinter import messagebox

import os
import json

# 导入国际化模块
from i18n import t

from library.py_executable_check import is_conda

# 检查是否是支持的系统类型
import platform
if platform.system() not in ["Windows"]:
    messagebox.showwarning("警告", "当前系统不支持，仅在Windows上运行")

# 检查是否在conda环境中
if is_conda():
    messagebox.showwarning("警告", "当前环境为conda环境，可能会导致一些问题，建议在普通环境中运行\n如果仍要运行，请注释 app.py 中的检查部分。")
    exit(1)

# 导入并执行第一次启动操作
from library.startup import first_startup_operations
first_startup_operations()

logger = get_logger()
highlighter_factory = HighlighterFactory()
file_path = "temp_script.txt"

# 记录程序启动信息
logger.info("程序启动")

# 添加全局异常处理，确保崩溃时导出日志
def handle_global_exception(exctype, value, traceback):
    """全局异常处理函数"""
    import traceback as tb_module
    
    # 记录异常信息
    logger.exception("程序崩溃")
    logger.error(f"异常类型: {exctype.__name__}")
    logger.error(f"异常信息: {value}")
    logger.error("堆栈跟踪:")
    
    # 导出崩溃日志
    if hasattr(logger, 'export_crash_logs'):
        # 确保normal_exit为False，这样崩溃日志会被导出
        logger.normal_exit = False
        logger.export_crash_logs()
    
    # 关闭日志记录器，明确指定这是异常退出
    shutdown_logger(normal_exit=False)
    
    # 使用原始的异常处理方式
    import sys
    sys.__excepthook__(exctype, value, traceback)

# 设置全局异常处理器
import sys
sys.excepthook = handle_global_exception

# 加载设置
with open(f"{Path.cwd() / 'asset' / 'settings.json'}", "r", encoding="utf-8") as fp:
    settings = json.load(fp)

# 加载主题数据
with open(f"{Path.cwd() / 'asset' / 'packages' / 'themes.dark.json'}", "r", encoding="utf-8") as fp:
    dark_themes = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'dark.json'}", "r", encoding="utf-8") as fp:
    dark_terminal_theme = json.load(fp)

with open(f"{Path.cwd() / 'asset' / 'theme' / 'terminalTheme' / 'light.json'}", "r", encoding="utf-8") as fp:
    light_terminal_theme = json.load(fp)


class App:
    """
    应用程序主类
    """
    
    def __init__(self):
        """
        初始化应用程序
        """
        logger.info("开始初始化应用程序")
        
        # 创建主窗口
        logger.info("创建主窗口")
        self.root = MainWindow()
        self.root.title(t("app_title"))  # 使用多语言适配
        self.root.configure(bg="lightgray")  # 设置背景色为浅灰色，便于调试
        
        # 打印主窗口属性
        logger.info(f"主窗口初始尺寸: {self.root.winfo_width()}x{self.root.winfo_height()}")
        logger.info(f"主窗口初始位置: {self.root.winfo_x()},{self.root.winfo_y()}")
        
        # 创建多文件编辑器 - 需要在文件浏览器之前创建
        logger.info("创建多文件编辑器")
        self.multi_editor = MultiFileEditor(self.root.editor_frame, self.root.terminal_area, None, None)
        
        # 创建文件浏览器 - 现在可以安全访问multi_editor
        logger.info("创建文件浏览器")
        self.file_browser = FileBrowser(self.root.file_tree_frame, self)
        
        # 获取当前编辑器
        logger.info("获取当前编辑器")
        self.codearea = self.multi_editor.get_current_editor()
        
        # 打印编辑器信息
        logger.info(f"当前编辑器: {self.codearea}")
        
        # 初始化编辑器操作
        logger.info("初始化编辑器操作")
        self.editor_ops = EditorOperations(
            self.root, self.code[Bug]: 另存为文件时崩溃
https://gitee.com/chengzi404-byte/current-editor/issues/IDPN1Larea, self.root.terminal_area, self.root.terminal_area, self.multi_editor
        )
        
        # 将全局文件树引用附加到root对象上，以便editor_operations可以访问
        logger.info("设置文件树引用")
        self.root.file_tree = self.file_browser.tree
        
        # 初始化插件系统
        logger.info("初始化插件系统")
        self.plugin_manager = PluginManager()
        self.plugin_manager.initialize()
        
        # 创建菜单
        logger.info("创建菜单")
        self.menu_bar = MenuBar(self.root, self)
        
        # 绑定事件
        logger.info("绑定事件")
        self._bind_events()
        
        # 设置自动保存
        logger.info("设置自动保存")
        self._setup_autosave()
        
        # 初始化代码高亮器
        logger.info("初始化代码高亮器")
        self._init_highlighters()
        
        # 绑定右键菜单
        logger.info("绑定右键菜单")
        self._bind_popup_menu()
        
        # 初始化文件句柄管理器
        logger.info("初始化文件句柄管理器")
        self.file_handle_manager = get_file_manager()
        
        logger.info("应用程序初始化完成")
        
        # 添加一个简单的测试文本到编辑器
        if self.codearea:
            self.codearea.insert("1.0", t("startup_test_text"))  # 使用多语言适配
        
        # 强制更新界面
        self.root.update_idletasks()
    
    def _bind_events(self):
        """
        绑定键盘事件
        """
        self.root.bind("<Control-x>", lambda event: self.editor_ops.delete())
        self.root.bind("<Control-z>", lambda event: self.editor_ops.undo())
        self.root.bind("<Control-y>", lambda event: self.editor_ops.redo())
        self.root.bind("<F5>", lambda event: self.editor_ops.run())
    
    def _setup_autosave(self):
        """设置自动保存"""
        print("\n=== 自动保存功能初始化 ===")
        logger.info("=== 自动保存功能初始化 ===")
        
        def schedule_autosave():
            """自动保存定时器"""
            print("\n--- 执行自动保存任务 ---")
            logger.info("--- 执行自动保存任务 ---")
            try:
                # 显式调用autosave方法
                self.editor_ops.autosave()
                print("自动保存方法调用完成")
                logger.info("自动保存方法调用完成")
                
                # 再次设置定时器
                self.root.after(5000, schedule_autosave)  # Auto-save every 5 seconds
                print(f"已安排下一次自动保存（5秒后）")
                logger.info(f"已安排下一次自动保存（5秒后）")
            except Exception as e:
                print(f"自动保存执行异常: {str(e)}")
                logger.error(f"自动保存执行异常: {str(e)}")
                import traceback
                print(f"异常详细信息: {traceback.format_exc()}")
                logger.error(f"异常详细信息: {traceback.format_exc()}")
        
        # Start auto-save
        print("启动第一次自动保存...")
        logger.info("启动第一次自动保存...")
        schedule_autosave()
    
    def _init_highlighters(self):
        """
        初始化代码高亮器
        """
        try:
            logger.info("开始初始化代码高亮器")
            self.codehighlighter = highlighter_factory.create_highlighter(
                self.codearea, self.multi_editor.get_current_file_path()
            )
            
            # 加载主题
            theme_name = Settings.Highlighter.syntax_highlighting()["theme"]
            theme_file = f"{Path.cwd() / 'asset' / 'theme' / theme_name}.json"
            if os.path.exists(theme_file):
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
            else:
                logger.warning(f"主题文件不存在: {theme_file}, 使用默认主题")
                # 使用内置默认主题
                theme_data = {
                    "base": {
                        "background": "#1E1E1E",
                        "foreground": "#D4D4D4",
                        "insertbackground": "#D4D4D4",
                        "selectbackground": "#264F78",
                        "selectforeground": "#D4D4D4"
                    }
                }
            
            # 应用主题
            self.codehighlighter.set_theme(theme_data)
            self.codehighlighter.highlight()
            logger.info("代码高亮器初始化完成")
            
            # 初始化终端高亮器
            self.codehighlighter2 = highlighter_factory.create_highlighter(self.root.terminal_area, "log")
            if Settings.Highlighter.syntax_highlighting()["theme"] in dark_themes: 
                self.codehighlighter2.set_theme(dark_terminal_theme)
                logger.info("使用深色终端主题")
            else: 
                self.codehighlighter2.set_theme(light_terminal_theme)
                logger.info("使用浅色终端主题")

            def on_key(event):
                # Process auto-save
                self.editor_ops.autosave()
                return None
            
            # Remove all the key binds
            for binding in self.root.bind_all():
                if binding.startswith('<Key'):
                    self.root.unbind_all(binding)
            
            # Add new key bind
            self.root.bind("<Key>", on_key, add="+")
            
            logger.info("程序初始化完成，准备启动主循环")
            
        except Exception as e:
            logger.error(f"代码高亮器初始化失败: {str(e)}")
    
    def _bind_popup_menu(self):
        """
        绑定右键菜单
        """
        def show_popup(event):
            """显示右键菜单"""
            self.menu_bar.popmenu.post(event.x_root, event.y_root)
        
        self.codearea.bind("<Button-3>", show_popup)
    
    def run(self):
        """
        启动应用程序主循环
        """
        def on_exit():
            """
            程序退出时的清理操作
            """
            logger.info("程序正在退出...")

            # 立即关闭主窗口
            self.root.withdraw()
            
            # 关闭插件系统
            logger.info("关闭插件系统")
            self.plugin_manager.shutdown()
            
            # 关闭文件句柄管理器
            logger.info("关闭文件句柄管理器")
            shutdown_file_manager()
            
            # 关闭日志系统
            shutdown_logger()
            
            # 销毁主窗口
            self.root.destroy()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", on_exit)
        
        # 添加窗口大小变化事件
        def on_resize(event):
            """
            窗口大小变化事件处理
            """
            # print(f"窗口大小变化: {event.width}x{event.height}")
        
        self.root.bind("<Configure>", on_resize)
        
        # 启动主循环
        try:
            logger.info("启动主循环")
            print(t("starting_main_loop"))  # 使用多语言适配
            self.root.mainloop()
        except Exception as e:
            logger.error(f"程序主循环异常: {str(e)}")
            print(f"程序主循环异常: {str(e)}")
            shutdown_logger(normal_exit=False)


# 应用程序入口
if __name__ == "__main__":
    import sys
    import traceback
    import os
    
    # 打印基本信息
    print("="*50)
    print("代码编辑器")
    print(f"Python路径: {sys.executable}")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    print(f"脚本路径: {__file__}")
    print(f"Python路径列表: {sys.path}")
    print("="*50)
    
    print("="*50)
    print("开始启动代码编辑器...")
    
    try:
        app = App()
        app.run()
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}")
        logger.error(traceback.format_exc())
        # 打印到控制台，方便调试
        print(f"应用程序启动失败: {str(e)}")
        traceback.print_exc()
        # 等待用户按Enter键退出
        input("按Enter键退出...")
