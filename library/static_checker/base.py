"""
静态代码检查器基类
定义所有检查器的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class StaticCheckError:
    """
    静态检查错误数据类
    """
    line: int             # 错误行号
    column: int           # 错误列号
    end_line: int         # 错误结束行号
    end_column: int       # 错误结束列号
    error_type: str       # 错误类型
    error_message: str    # 错误消息
    severity: str = "error"  # 错误严重程度: error, warning, info


class BaseStaticChecker(ABC):
    """
    静态代码检查器基类
    """
    
    def __init__(self, language: str, editor_widget=None):
        """
        初始化检查器
        
        Args:
            language: 支持的编程语言
            editor_widget: 编辑器组件（可选），用于直接操作编辑器
        """
        self.language = language
        self.editor_widget = editor_widget
        self.errors: List[StaticCheckError] = []
        
    @abstractmethod
    def check(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        执行静态代码检查
        
        Args:
            code: 要检查的代码内容
            file_path: 文件路径（可选），用于上下文分析
            
        Returns:
            检查到的错误列表
        """
        pass
    
    def get_language(self) -> str:
        """
        获取支持的编程语言
        """
        return self.language
    
    def clear_errors(self):
        """
        清空错误列表
        """
        self.errors.clear()
    
    def get_errors(self) -> List[StaticCheckError]:
        """
        获取当前错误列表
        """
        return self.errors.copy()
    
    def _add_error(self, line: int, column: int, end_line: int, end_column: int, 
                   error_type: str, error_message: str, severity: str = "error"):
        """
        添加错误到列表
        
        Args:
            line: 错误行号
            column: 错误列号
            end_line: 错误结束行号
            end_column: 错误结束列号
            error_type: 错误类型
            error_message: 错误消息
            severity: 错误严重程度
        """
        error = StaticCheckError(
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
            error_type=error_type,
            error_message=error_message,
            severity=severity
        )
        self.errors.append(error)
