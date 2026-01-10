"""
括号检查器
实现对各类括号的完整性检查
"""

from typing import List, Optional
from library.static_checker.base import BaseStaticChecker, StaticCheckError


class BracketChecker(BaseStaticChecker):
    """
    括号检查器
    支持检查各类括号：() [] {} <>
    """
    
    BRACKET_PAIRS = {
        '(': ')',
        '[': ']',
        '{': '}',
        '<': '>'
    }
    
    BRACKET_OPENERS = set(BRACKET_PAIRS.keys())
    BRACKET_CLOSERS = set(BRACKET_PAIRS.values())
    
    def __init__(self, language: str, editor_widget=None):
        """
        初始化括号检查器
        
        Args:
            language: 支持的编程语言
            editor_widget: 编辑器组件（可选）
        """
        super().__init__(language, editor_widget)
    
    def check(self, code: str, file_path: Optional[str] = None) -> List[StaticCheckError]:
        """
        执行括号检查
        
        Args:
            code: 要检查的代码内容
            file_path: 文件路径（可选）
            
        Returns:
            检查到的错误列表
        """
        self.clear_errors()
        
        # 按行分割代码
        lines = code.split('\n')
        
        # 括号栈，用于跟踪未闭合的括号
        bracket_stack = []
        
        for line_num, line in enumerate(lines, 1):
            # 跳过Python类型注解中的箭头符号
            if self.language == "python":
                # 检查是否在类型注解上下文中
                in_type_annotation = False
                for i, char in enumerate(line):
                    if i > 0 and line[i-1:i+1] == "->":
                        in_type_annotation = True
                        break
                
                # 临时替换类型注解中的箭头符号，避免被当作尖括号处理
                processed_line = line
                if "->" in line:
                    processed_line = processed_line.replace("->", "__ARROW__")
            else:
                processed_line = line
            
            for col_num, char in enumerate(processed_line, 1):
                # 跳过替换后的箭头符号
                if char == "__ARROW__":
                    continue
                    
                if char in self.BRACKET_OPENERS:
                    # 遇到开括号，压入栈
                    bracket_stack.append((char, line_num, col_num))
                elif char in self.BRACKET_CLOSERS:
                    # 遇到闭括号，检查匹配
                    if not bracket_stack:
                        # 没有对应的开括号
                        self._add_error(
                            line=line_num,
                            column=col_num,
                            end_line=line_num,
                            end_column=col_num + 1,
                            error_type="bracket-mismatch",
                            error_message=f"发现未匹配的闭括号 '{char}'，缺少对应的开括号"
                        )
                    else:
                        # 获取栈顶的开括号
                        last_opener, opener_line, opener_col = bracket_stack.pop()
                        expected_closer = self.BRACKET_PAIRS[last_opener]
                        
                        if char != expected_closer:
                            # 括号类型不匹配
                            self._add_error(
                                line=line_num,
                                column=col_num,
                                end_line=line_num,
                                end_column=col_num + 1,
                                error_type="bracket-mismatch",
                                error_message=f"括号类型不匹配：开括号 '{last_opener}' 期望 '{expected_closer}'，但得到 '{char}'"
                            )
                
        # 检查栈中是否有未闭合的开括号
        for opener, line_num, col_num in bracket_stack:
            expected_closer = self.BRACKET_PAIRS[opener]
            self._add_error(
                line=line_num,
                column=col_num,
                end_line=line_num,
                end_column=col_num + 1,
                error_type="bracket-unclosed",
                error_message=f"开括号 '{opener}' 未闭合，缺少对应的 '{expected_closer}'"
            )
        
        return self.get_errors()
