"""
静态代码检查管理器
用于集成和管理所有静态代码检查器
"""

from typing import List, Optional, Dict, Any
from library.static_checker.base import StaticCheckError
from library.static_checker.static_checker_factory import StaticCheckerFactory


class StaticCheckManager:
    """
    静态代码检查管理器
    负责集成和管理所有静态代码检查器，处理检查请求并管理错误显示
    """
    
    def __init__(self):
        """
        初始化检查管理器
        """
        self.checker_factory = StaticCheckerFactory()
        self._current_errors: Dict[str, List[StaticCheckError]] = {}  # {file_path: errors}
        self._editor_mappings = {}  # {editor_widget: file_path}
        
        # 加载主题配置
        self._error_theme = self._load_error_theme()
    
    def _load_error_theme(self):
        """
        从主题文件加载错误高亮配置
        
        Returns:
            dict: 错误高亮配置
        """
        try:
            from pathlib import Path
            import json
            
            # 确定主题文件路径
            theme_dir = Path(__file__).parent.parent.parent / "asset" / "theme"
            theme_file = theme_dir / "vscode-dark.json"  # 默认使用vscode-dark主题
            
            if not theme_file.exists():
                print(f"主题文件未找到: {theme_file}")
                return self._get_default_error_theme()
            
            # 加载主题配置
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_config = json.load(f)
            
            # 提取错误高亮配置
            error_theme = {}
            error_theme['error_color'] = theme_config.get('error', '#F44747')
            error_theme['warning_color'] = theme_config.get('warning', '#DDB100')
            error_theme['error_background'] = theme_config.get('error_background', '#FFEBEB')
            
            print(f"加载错误主题配置: {error_theme}")
            return error_theme
            
        except Exception as e:
            print(f"加载错误主题失败: {str(e)}")
            return self._get_default_error_theme()
    
    def _get_default_error_theme(self):
        """
        获取默认的错误高亮配置
        
        Returns:
            dict: 默认错误高亮配置
        """
        return {
            'error_color': '#F44747',
            'warning_color': '#DDB100',
            'error_background': '#FFEBEB'
        }
        
    def register_editor(self, editor_widget, file_path: str = None):
        """
        注册编辑器组件到管理器
        
        Args:
            editor_widget: 编辑器组件
            file_path: 文件路径（可选）
        """
        self._editor_mappings[editor_widget] = file_path
    
    def unregister_editor(self, editor_widget):
        """
        从管理器中注销编辑器组件
        
        Args:
            editor_widget: 编辑器组件
        """
        if editor_widget in self._editor_mappings:
            del self._editor_mappings[editor_widget]
    
    def update_file_path(self, editor_widget, file_path: str):
        """
        更新编辑器对应的文件路径
        
        Args:
            editor_widget: 编辑器组件
            file_path: 文件路径
        """
        if editor_widget in self._editor_mappings:
            self._editor_mappings[editor_widget] = file_path
    
    def check_code(self, code: str, file_path: Optional[str] = None, editor_widget = None) -> List[StaticCheckError]:
        """
        执行静态代码检查
        
        Args:
            code: 要检查的代码内容
            file_path: 文件路径（可选）
            editor_widget: 编辑器组件（可选）
            
        Returns:
            检查到的错误列表
        """
        print(f"静态检查开始，文件路径: {file_path}, 代码长度: {len(code)}")
        # 根据文件路径获取语言
        language = self.checker_factory.get_language_from_file(file_path) if file_path else None
        
        print(f"检测到的语言: {language}")
        
        # 如果无法从文件路径确定语言，使用默认语言Python进行检查
        if not language:
            print("无法从文件路径确定语言，使用默认语言Python")
            language = "python"
        
        # 创建对应的检查器
        checkers = self.checker_factory.create_checkers(language, editor_widget)
        print(f"创建的检查器数量: {len(checkers)}, 检查器类型: {[type(c).__name__ for c in checkers]}")
        
        all_errors = []
        
        # 执行所有检查器
        for checker in checkers:
            print(f"执行检查器: {type(checker).__name__}")
            errors = checker.check(code, file_path)
            print(f"检查器返回的错误数量: {len(errors)}")
            all_errors.extend(errors)
        
        print(f"所有检查器完成，总错误数量: {len(all_errors)}")
        
        # 更新当前错误记录
        if file_path:
            self._current_errors[file_path] = all_errors
        
        # 如果提供了编辑器组件，更新编辑器中的错误显示
        if editor_widget:
            print(f"更新编辑器错误显示，错误数量: {len(all_errors)}")
            self._update_editor_errors(editor_widget, all_errors)
        
        return all_errors
    
    def _update_editor_errors(self, editor_widget, errors: List[StaticCheckError]):
        """
        更新编辑器中的错误显示
        
        Args:
            editor_widget: 编辑器组件
            errors: 错误列表
        """
        print(f"更新编辑器错误显示，错误数量: {len(errors)}")
        
        # 清除之前的错误标记
        self._clear_editor_errors(editor_widget)
        
        # 简化的错误标记逻辑：直接使用最兼容的Tkinter标签配置
        try:
            # 根据错误类型配置不同的标记样式
            # 配置错误标记样式（使用主题颜色）
            editor_widget.tag_configure("error", 
                                       underline=True, 
                                       foreground=self._error_theme['error_color'],
                                       background=self._error_theme['error_background'])
            
            # 配置警告标记样式（使用主题颜色）
            editor_widget.tag_configure("warning", 
                                       underline=True, 
                                       foreground=self._error_theme['warning_color'])
            
            # 添加错误标记
            for i, error in enumerate(errors):
                print(f"添加错误: {error.error_type} - {error.error_message}")
                
                # 计算位置
                start_line = error.line
                start_col = error.column - 1  # Tkinter使用0-based列索引
                end_line = error.end_line
                end_col = error.end_column - 1
                
                # 构建位置字符串
                start_pos = f"{start_line}.{start_col}"
                end_pos = f"{end_line}.{end_col}"
                
                print(f"添加错误标记，位置: {start_pos} 到 {end_pos}")
                
                # 根据错误严重程度选择标记类型
                tag = "error" if error.severity == "error" else "warning"
                
                # 直接添加标记
                editor_widget.tag_add(tag, start_pos, end_pos)
                print(f"成功添加{tag}标记")
                
                # 为每个错误添加独特的标签，用于绑定事件
                error_tag = f"error_{i}"
                editor_widget.tag_add(error_tag, start_pos, end_pos)
                
                # 为每个错误标签添加鼠标进入和离开事件
                # 绑定显示提示的事件
                editor_widget.tag_bind(error_tag, "<Enter>", lambda e, err=error, widget=editor_widget: self._show_simple_tooltip(e, widget, err))
                # 绑定隐藏提示的事件
                editor_widget.tag_bind(error_tag, "<Leave>", lambda e, widget=editor_widget: self._hide_simple_tooltip(e, widget))
        except Exception as e:
            print(f"更新编辑器错误显示失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _show_simple_tooltip(self, event, editor_widget, error):
        """
        显示简单的错误提示信息
        
        Args:
            event: 事件对象
            editor_widget: 编辑器组件
            error: 错误信息
        """
        try:
            # 清除之前的提示
            self._hide_simple_tooltip(event, editor_widget)
            
            # 直接在编辑器状态栏显示错误信息（如果有状态栏）
            # 或者使用简单的提示窗口
            
            # 创建简单的提示窗口
            from tkinter import Toplevel, Label
            
            # 创建提示窗口
            tooltip = Toplevel(editor_widget)
            tooltip.wm_overrideredirect(True)  # 无边框
            
            # 设置位置在鼠标附近
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # 创建提示标签
            message = f"{error.error_type}: {error.error_message}"
            label = Label(tooltip, text=message, 
                         background="#fff3cd", 
                         foreground="#856404",
                         borderwidth=1,
                         relief="solid",
                         padx=5,
                         pady=3,
                         font=("Arial", 10))
            label.pack()
            
            # 保存提示窗口引用
            editor_widget._tooltip = tooltip
            print(f"显示简单提示: {message}")
        except Exception as e:
            print(f"显示提示失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _hide_simple_tooltip(self, event, editor_widget):
        """
        隐藏简单的错误提示信息
        
        Args:
            event: 事件对象
            editor_widget: 编辑器组件
        """
        try:
            if hasattr(editor_widget, "_tooltip") and editor_widget._tooltip:
                editor_widget._tooltip.destroy()
                editor_widget._tooltip = None
                print("隐藏简单提示")
        except Exception as e:
            print(f"隐藏提示失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _clear_editor_errors(self, editor_widget):
        """
        清除编辑器中的所有错误标记
        
        Args:
            editor_widget: 编辑器组件
        """
        print("清除编辑器中的所有错误标记")
        try:
            # 清除错误标记
            editor_widget.tag_remove("error", "1.0", "end")
            editor_widget.tag_remove("warning", "1.0", "end")
            
            # 清除旧的标记名称（兼容旧代码）
            editor_widget.tag_remove("static_check_error", "1.0", "end")
            
            # 清除所有自动生成的错误标签
            for tag in editor_widget.tag_names():
                if tag.startswith("error_"):
                    editor_widget.tag_remove(tag, "1.0", "end")
            
            # 清除提示窗口（如果存在）
            if hasattr(editor_widget, "_tooltip") and editor_widget._tooltip:
                try:
                    editor_widget._tooltip.destroy()
                except:
                    pass
                finally:
                    editor_widget._tooltip = None
            
            print("成功清除错误标记")
        except Exception as e:
            print(f"清除编辑器错误标记失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_current_errors(self, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        获取当前文件的错误列表
        
        Args:
            file_path: 文件路径（可选）
            
        Returns:
            错误列表
        """
        if file_path:
            return self._current_errors.get(file_path, [])
        return []
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的编程语言列表
        
        Returns:
            支持的语言列表
        """
        return self.checker_factory.get_supported_languages()
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            支持的文件扩展名列表
        """
        return self.checker_factory.get_supported_extensions()
