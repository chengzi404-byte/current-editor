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
            # 配置错误标记样式
            editor_widget.tag_configure("error", 
                                       underline=True, 
                                       foreground="red")
            
            # 添加错误标记
            for error in errors:
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
                
                # 直接添加标记
                editor_widget.tag_add("error", start_pos, end_pos)
                print("成功添加错误标记")
        except Exception as e:
            print(f"更新编辑器错误显示失败: {str(e)}")
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
            
            # 清除旧的标记名称（兼容旧代码）
            editor_widget.tag_remove("static_check_error", "1.0", "end")
            
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
