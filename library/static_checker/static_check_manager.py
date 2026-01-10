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
        # 根据文件路径获取语言
        language = self.checker_factory.get_language_from_file(file_path) if file_path else None
        
        if not language:
            # 无法确定语言，返回空错误列表
            return []
        
        # 创建对应的检查器
        checkers = self.checker_factory.create_checkers_for_file(file_path, editor_widget)
        
        all_errors = []
        
        # 执行所有检查器
        for checker in checkers:
            errors = checker.check(code, file_path)
            all_errors.extend(errors)
        
        # 更新当前错误记录
        if file_path:
            self._current_errors[file_path] = all_errors
        
        # 如果提供了编辑器组件，更新编辑器中的错误显示
        if editor_widget:
            self._update_editor_errors(editor_widget, all_errors)
        
        return all_errors
    
    def _update_editor_errors(self, editor_widget, errors: List[StaticCheckError]):
        """
        更新编辑器中的错误显示
        
        Args:
            editor_widget: 编辑器组件
            errors: 错误列表
        """
        # 清除之前的错误标记
        self._clear_editor_errors(editor_widget)
        
        # 添加新的错误标记
        for error in errors:
            self._add_error_to_editor(editor_widget, error)
    
    def _clear_editor_errors(self, editor_widget):
        """
        清除编辑器中的所有错误标记
        
        Args:
            editor_widget: 编辑器组件
        """
        # 删除所有错误标记
        editor_widget.tag_remove("static_check_error", "1.0", "end")
        
        # 删除所有自定义错误标记
        for tag in editor_widget.tag_names():
            if tag.startswith("error_"):
                editor_widget.tag_remove(tag, "1.0", "end")
    
    def _add_error_to_editor(self, editor_widget, error: StaticCheckError):
        """
        向编辑器添加单个错误标记
        
        Args:
            editor_widget: 编辑器组件
            error: 错误信息
        """
        # 设置错误标记的样式：红色波浪线
        editor_widget.tag_configure("static_check_error", 
                                   underline=True, 
                                   underlinefg="red",
                                   background="#ffebee")
        
        # 添加悬停提示信息
        editor_widget.tag_bind("static_check_error", "<Enter>", 
                              lambda e, err=error: self._show_error_tooltip(e, err, editor_widget))
        editor_widget.tag_bind("static_check_error", "<Leave>", 
                              lambda e: self._hide_error_tooltip(e, editor_widget))
        
        # 计算错误位置
        start_pos = f"{error.line}.{error.column - 1}"  # Tkinter使用0-based列索引
        end_pos = f"{error.end_line}.{error.end_column - 1}"
        
        # 添加错误标记
        editor_widget.tag_add("static_check_error", start_pos, end_pos)
        
        # 为每个错误创建唯一的标记，以便存储错误信息
        error_tag = f"error_{len(errors)}_{start_pos.replace('.', '_')}"
        editor_widget.tag_add(error_tag, start_pos, end_pos)
        
        # 绑定唯一标记的悬停事件
        editor_widget.tag_bind(error_tag, "<Enter>", 
                              lambda e, err=error: self._show_error_tooltip(e, err, editor_widget))
        editor_widget.tag_bind(error_tag, "<Leave>", 
                              lambda e: self._hide_error_tooltip(e, editor_widget))
    
    def _show_error_tooltip(self, event, error: StaticCheckError, editor_widget):
        """
        显示错误提示信息
        
        Args:
            event: 事件对象
            error: 错误信息
            editor_widget: 编辑器组件
        """
        # 检查是否已经有提示窗口
        if hasattr(editor_widget, "_error_tooltip") and editor_widget._error_tooltip:
            return
        
        # 创建提示窗口
        from tkinter import Toplevel, Label
        
        tooltip = Toplevel(editor_widget)
        tooltip.wm_overrideredirect(True)  # 无边框
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        # 创建提示标签
        message = f"{error.error_type}: {error.error_message}"
        label = Label(tooltip, text=message, 
                     background="#fff3cd", 
                     foreground="#856404",
                     borderwidth=1,
                     relief="solid",
                     font=editor_widget.cget("font"),
                     padx=8,
                     pady=4,
                     justify="left")
        label.pack()
        
        # 保存提示窗口引用
        editor_widget._error_tooltip = tooltip
    
    def _hide_error_tooltip(self, event, editor_widget):
        """
        隐藏错误提示信息
        
        Args:
            event: 事件对象
            editor_widget: 编辑器组件
        """
        if hasattr(editor_widget, "_error_tooltip") and editor_widget._error_tooltip:
            try:
                editor_widget._error_tooltip.destroy()
            except:
                pass
            finally:
                editor_widget._error_tooltip = None
    
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
