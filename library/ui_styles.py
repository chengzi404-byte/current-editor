"""
现代化UI样式管理模块
为tkinter应用程序提供现代化的配色方案和样式定义
"""

from tkinter import font as tkfont
import json
from pathlib import Path


class ModernStyles:
    """现代化UI样式类"""
    
    # 现代化配色方案
    COLOR_SCHEMES = {
        "dark": {
            "primary": "#2196F3",       # 主色调 - 蓝色
            "primary_hover": "#1976D2",  # 主色调悬停
            "secondary": "#FF9800",     # 次要色 - 橙色
            "success": "#4CAF50",       # 成功色 - 绿色
            "danger": "#F44336",        # 危险色 - 红色
            "warning": "#FFC107",       # 警告色 - 黄色
            "info": "#00BCD4",          # 信息色 - 青色
            
            "background": "#121212",    # 背景色
            "surface": "#1E1E1E",       # 表面色
            "surface_hover": "#252525",  # 表面悬停色
            "card": "#2D2D30",          # 卡片色
            "surface_variant": "#2D2D30", # 表面变体色
            "surface_variant_hover": "#353535", # 表面变体悬停色
            "text_primary": "#FFFFFF",  # 主要文字
            "text_secondary": "#B0B0B0", # 次要文字
            "text_muted": "#888888",    # 弱化文字
            "border": "#3E3E42",        # 边框色
            "hover": "#37373d",         # 悬停色
            "active": "#2196F3",        # 激活色
            "on_surface": "#FFFFFF",    # 表面上的文字
            "on_surface_variant": "#CCCCCC", # 表面变体上的文字
            "on_background": "#FFFFFF"   # 背景上的文字
        },
        "light": {
            "primary": "#1976D2",
            "primary_hover": "#1565C0",
            "secondary": "#F57C00",
            "success": "#388E3C",
            "danger": "#D32F2F",
            "warning": "#FBC02D",
            "info": "#0288D1",
            
            "background": "#FAFAFA",
            "surface": "#FFFFFF",
            "surface_hover": "#F5F5F5",
            "card": "#F5F5F5",
            "surface_variant": "#F5F5F5",
            "surface_variant_hover": "#EEEEEE",
            "text_primary": "#000000",
            "text_secondary": "#666666",
            "text_muted": "#888888",
            "border": "#E0E0E0",
            "hover": "#E0E0E0",
            "active": "#1976D2",
            "on_surface": "#000000",
            "on_surface_variant": "#666666",
            "on_background": "#000000"
        }
    }
    
    def __init__(self, theme="dark"):
        """初始化样式管理器"""
        self.theme = theme
        self.colors = self.COLOR_SCHEMES.get(theme, self.COLOR_SCHEMES["dark"])
        self.setup_fonts()
        
    def setup_fonts(self):
        """设置现代化字体"""
        # 尝试使用现代化字体，如果系统没有则使用默认字体
        modern_fonts = ["Microsoft YaHei UI", "Segoe UI", "PingFang SC", "SF Pro Display", "Inter"]

        for font_name in modern_fonts:
            try:
                test_font = tkfont.Font(family=font_name, size=10)
                actual = test_font.actual()
                # 更宽松的匹配：实际字体名包含我们想要的字体
                if actual and actual.get("family"):
                    actual_family = actual["family"]
                    # 检查是否匹配或包含
                    if (actual_family == font_name or
                        font_name in actual_family or
                        any(modern in actual_family for modern in modern_fonts)):
                        self.font_family = actual_family
                        break
            except Exception:
                continue
        else:
            # 如果没有找到现代化字体，使用安全字体检测
            self.font_family = self._get_safe_font_family()
        
        # 字体大小定义
        self.font_sizes = {
            "xs": 10,
            "sm": 12,
            "base": 14,
            "lg": 16,
            "xl": 18,
            "2xl": 20,
            "3xl": 24
        }
    
    def get_font(self, size="base", weight="normal"):
        """获取字体配置"""
        # 使用 setup_fonts 中检测到的可用字体，或提供安全默认值
        font_family = getattr(self, 'font_family', None)
        
        if not font_family or font_family == "TkDefaultFont":
            # 在 Conda 环境下使用更可靠的方法检测可用字体
            font_family = self._get_safe_font_family()
        
        font_size = self.font_sizes.get(size, 14)
        
        if weight == "bold":
            return (font_family, font_size, "bold")
        elif weight == "light":
            return (font_family, font_size, "normal")
        else:
            return (font_family, font_size, "normal")
    
    def _get_safe_font_family(self):
        """获取在不同环境下都可用的安全字体"""
        # 字体列表按优先级排序（包括服务器环境中的字体）
        safe_fonts = [
            "Microsoft YaHei UI",    # Windows 中文系统
            "Microsoft YaHei",       # Windows 中文系统（无UI后缀）
            "SimHei",                # Windows 黑体
            "SimSun",                # Windows 宋体
            "Segoe UI",              # Windows 10/11
            "Arial Unicode MS",      # 多语言支持
            "WenQuanYi Micro Hei",   # Linux 文泉驿
            "wenquanyi bitmap song", # Linux 文泉驿点阵宋体
            "Noto Sans CJK SC",      # Linux Noto
            "DejaVu Sans",           # Linux 常见字体
            "Liberation Sans",       # Linux 常见字体
            "Arial",                 # 通用字体
            "Helvetica",             # 通用字体
            "fixed",                 # X11 默认等宽字体
            "clean",                 # X11 字体
        ]

        try:
            # 导入 tkinter
            import tkinter as tk

            # 创建临时 root 窗口（需要创建 root 才能使用 font.families()）
            root = tk.Tk()
            root.withdraw()

            # 获取系统所有可用字体
            all_families = set(tkfont.families())

            # 首先尝试完全匹配的字体
            for font_name in safe_fonts:
                if font_name in all_families:
                    try:
                        test_font = tkfont.Font(family=font_name, size=10)
                        actual_family = test_font.actual("family")
                        if actual_family and actual_family != "":
                            root.destroy()
                            return actual_family
                    except Exception:
                        continue

            # 其次尝试不区分大小写的匹配
            all_families_lower = {f.lower(): f for f in all_families}
            for font_name in safe_fonts:
                if font_name.lower() in all_families_lower:
                    try:
                        actual_name = all_families_lower[font_name.lower()]
                        test_font = tkfont.Font(family=actual_name, size=10)
                        actual_family = test_font.actual("family")
                        if actual_family and actual_family != "":
                            root.destroy()
                            return actual_family
                    except Exception:
                        continue

            root.destroy()

        except Exception:
            pass

        # 如果都不可用，使用系统默认字体
        return "TkDefaultFont"

    def get_icon(self, icon_name, size="md"):
        """获取图标字符（使用emoji作为图标）"""
        icon_map = {
            # 文件操作
            "file": "📄", "folder": "📁", "save": "💾", "open": "📂",
            "new": "🆕", "refresh": "🔄", "search": "🔍", "filter": "🔧",
            
            # 编辑操作
            "edit": "✏️", "copy": "📋", "paste": "📝", "cut": "✂️",
            "undo": "↩️", "redo": "↪️", "delete": "🗑️", "settings": "⚙️",
            
            # 界面元素
            "menu": "☰", "close": "✕", "minimize": "➖", "maximize": "➕",
            "home": "🏠", "back": "⬅️", "forward": "➡️", "up": "⬆️",
            "down": "⬇️", "left": "⬅️", "right": "➡️", "expand": "⏬",
            
            # 状态和操作
            "success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️",
            "question": "❓", "loading": "⏳", "done": "✔️", "cancel": "❌",
            "play": "▶️", "pause": "⏸️", "stop": "⏹️", "record": "🔴",
            
            # 开发相关
            "code": "💻", "bug": "🐛", "test": "🧪", "deploy": "🚀",
            "git": "📚", "branch": "🌿", "commit": "💎", "merge": "🔄",
            
            # 用户界面
            "user": "👤", "lock": "🔒", "unlock": "🔓", "key": "🔑",
            "bell": "🔔", "star": "⭐", "heart": "❤️", "bookmark": "🔖"
        }
        
        return icon_map.get(icon_name, "⚙️")  # 默认图标
    
    def get_color(self, color_type):
        """获取颜色值"""
        return self.colors.get(color_type, "#000000")
    
    def apply_window_style(self, window):
        """应用窗口样式"""
        window.configure(
            bg=self.get_color("background"),
            highlightbackground=self.get_color("border")
        )
    
    def apply_frame_style(self, frame, style="surface"):
        """应用框架样式"""
        frame.configure(
            bg=self.get_color(style),
            highlightbackground=self.get_color("border")
        )
    
    def apply_label_style(self, label, style="text_primary"):
        """应用标签样式"""
        label.configure(
            bg=self.get_color("surface"),
            fg=self.get_color(style),
            font=self.get_font("sm")
        )
    
    def apply_button_style(self, button, variant="primary", size="sm"):
        """应用按钮样式"""
        if variant == "primary":
            button.configure(
                bg=self.get_color("primary"),
                fg="white",
                font=self.get_font(size, "bold"),
                relief="flat",
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2"
            )
            
            # 添加悬停效果
            def on_enter(e):
                button.configure(bg=self._lighten_color(self.get_color("primary"), 0.1))
            
            def on_leave(e):
                button.configure(bg=self.get_color("primary"))
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
        elif variant == "secondary":
            button.configure(
                bg=self.get_color("surface"),
                fg=self.get_color("text_primary"),
                font=self.get_font(size),
                relief="flat",
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2"
            )
            
            # 添加悬停效果
            def on_enter(e):
                button.configure(bg=self._lighten_color(self.get_color("surface"), 0.1))
            
            def on_leave(e):
                button.configure(bg=self.get_color("surface"))
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
        elif variant == "outline":
            button.configure(
                bg=self.get_color("surface"),
                fg=self.get_color("primary"),
                font=self.get_font(size),
                relief="solid",
                bd=1,
                padx=20,
                pady=10,
                cursor="hand2"
            )
            
            # 添加悬停效果
            def on_enter(e):
                button.configure(bg=self.get_color("primary"), fg="white")
            
            def on_leave(e):
                button.configure(bg=self.get_color("surface"), fg=self.get_color("primary"))
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        else:
            # 其他变体保持原有逻辑
            colors = {
                "success": {"bg": self.get_color("success"), "fg": "white"},
                "danger": {"bg": self.get_color("danger"), "fg": "white"},
                "warning": {"bg": self.get_color("warning"), "fg": "black"},
                "info": {"bg": self.get_color("info"), "fg": "white"}
            }
            
            style_config = colors.get(variant, {"bg": self.get_color("primary"), "fg": "white"})
            
            button.configure(
                **style_config,
                font=self.get_font(size),
                relief="flat",
                bd=0,
                padx=16,
                pady=8,
                cursor="hand2"
            )
            
            # 添加悬停效果
            def on_enter(e):
                button.configure(bg=self._lighten_color(style_config["bg"], 0.1))
            
            def on_leave(e):
                button.configure(bg=style_config["bg"])
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
    
    def apply_entry_style(self, entry):
        """应用输入框样式"""
        entry.configure(
            bg=self.get_color("surface"),
            fg=self.get_color("text_primary"),
            insertbackground=self.get_color("text_primary"),
            selectbackground=self.get_color("primary"),
            selectforeground="white",
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=self.get_font("sm")
        )
    
    def apply_text_style(self, text_widget):
        """应用文本区域样式"""
        text_widget.configure(
            bg=self.get_color("surface"),
            fg=self.get_color("text_primary"),
            insertbackground=self.get_color("text_primary"),
            selectbackground=self.get_color("primary"),
            selectforeground="white",
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=self.get_font("sm")
        )
    
    def apply_treeview_style(self, treeview):
        """应用树形视图样式"""
        from tkinter import ttk
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.get_color("surface"),
                       foreground=self.get_color("text_primary"),
                       fieldbackground=self.get_color("surface"),
                       font=self.get_font("sm"),
                       rowheight=30,
                       borderwidth=0,
                       relief="flat")
        
        style.map("Treeview", 
                 background=[("selected", self.get_color("primary"))],
                 foreground=[("selected", "white")],
                 focuscolor=[("selected", self.get_color("primary"))])
        
        # 配置Treeview.Heading样式
        style.configure("Treeview.Heading",
                       background=self.get_color("card"),
                       foreground=self.get_color("text_primary"),
                       font=self.get_font("sm", "bold"),
                       relief="flat")
        
        style.map("Treeview.Heading",
                 background=[("active", self.get_color("primary"))],
                 foreground=[("active", "white")])
    
    def apply_label_frame_style(self, labelframe):
        """应用标签框架样式"""
        labelframe.configure(
            bg=self.get_color("surface"),
            fg=self.get_color("primary"),
            font=self.get_font("lg", "bold"),
            relief="flat",
            bd=0
        )
    
    def apply_menu_style(self, menu):
        """
        应用菜单样式
        """
        menu.configure(
            bg=self.get_color("surface"),
            fg=self.get_color("text_primary"),
            activebackground=self.get_color("primary"),
            activeforeground="white",
            font=self.get_font("sm")
        )
    
    def apply_notebook_style(self):
        """
        应用Notebook样式，包括激活Tab的蓝色底部横条和过渡动画
        """
        from tkinter import ttk
        style = ttk.Style()
        
        # 获取主题色彩
        bg_color = self.get_color("surface")
        fg_color = self.get_color("text_primary")
        primary_color = self.get_color("primary")
        border_color = self.get_color("border")
        hover_color = self.get_color("surface_hover")
        
        # 配置Notebook基本样式
        style.configure("ModernNotebook.TNotebook",
                       background=bg_color,
                       foreground=fg_color,
                       borderwidth=0,
                       relief="flat")
        
        # 配置Notebook标签页样式
        style.configure("ModernNotebook.TNotebook.Tab",
                       background=bg_color,
                       foreground=fg_color,
                       font=self.get_font("sm"),
                       padding=[15, 8, 15, 8],
                       borderwidth=0,
                       relief="flat")
        
        # 配置激活状态的Tab样式，添加蓝色底部横条
        style.map("ModernNotebook.TNotebook.Tab",
                 background=[("selected", bg_color),
                            ("active", hover_color),
                            ("!active", bg_color)],
                 foreground=[("selected", fg_color),
                            ("active", fg_color),
                            ("!active", self.get_color("text_secondary"))],
                 borderwidth=[("selected", 2),
                             ("active", 1),
                             ("!active", 0)],
                 bordercolor=[("selected", primary_color),
                             ("active", primary_color),
                             ("!active", border_color)],
                 relief=[("selected", "flat"),
                        ("active", "flat"),
                        ("!active", "flat")])
        
        # 添加底部蓝色横条效果
        style.configure("ModernNotebook.TNotebook.Tab",
                       compound="bottom",
                       borderwidth=2,
                       focuscolor=primary_color)
        
        # 为Tab切换添加过渡效果，使用不同状态的颜色映射
        style.map("ModernNotebook.TNotebook.Tab",
                 lightcolor=[("selected", primary_color),
                            ("active", primary_color),
                            ("!active", border_color)],
                 darkcolor=[("selected", primary_color),
                           ("active", primary_color),
                           ("!active", border_color)],
                 highlightcolor=[("selected", primary_color),
                               ("active", primary_color),
                               ("!active", border_color)],
                 highlightbackground=[("selected", primary_color),
                                    ("active", primary_color),
                                    ("!active", border_color)])
        
        # 优化Tab内容区域样式
        style.configure("ModernNotebook.TNotebook.Content",
                       background=bg_color,
                       borderwidth=0,
                       relief="flat")
    
    def _lighten_color(self, color, factor):
        """颜色变亮"""
        if color.startswith("#"):
            color = color[1:]
        
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def switch_theme(self, theme):
        """切换主题"""
        self.theme = theme
        self.colors = self.COLOR_SCHEMES.get(theme, self.COLOR_SCHEMES["dark"])


# 全局样式实例
current_style = ModernStyles("light")  # 默认使用浅色主题，便于调试


def get_style():
    """获取当前样式实例"""
    return current_style


def set_theme(theme):
    """设置主题"""
    global current_style
    current_style = ModernStyles(theme)


def apply_modern_style(widget, widget_type, **kwargs):
    """
    应用现代化样式到指定组件
    """
    style = get_style()
    
    style_methods = {
        "window": style.apply_window_style,
        "frame": style.apply_frame_style,
        "label": style.apply_label_style,
        "button": style.apply_button_style,
        "entry": style.apply_entry_style,
        "text": style.apply_text_style,
        "treeview": style.apply_treeview_style,
        "labelframe": style.apply_label_frame_style,
        "menu": style.apply_menu_style,
        "notebook": style.apply_notebook_style,
        "scrollbar": lambda widget, **kwargs: None,  # scrollbar组件不需要特殊样式，使用默认样式
    }
    
    if widget_type in style_methods:
        try:
            style_methods[widget_type](widget, **kwargs)
        except Exception as e:
            print(f"应用样式失败 ({widget_type}): {e}")
            # 打印堆栈信息，便于调试
            import traceback
            traceback.print_exc()
    else:
        print(f"未知的组件类型: {widget_type}")