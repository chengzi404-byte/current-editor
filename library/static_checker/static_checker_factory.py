"""
静态代码检查器工厂
用于创建和管理不同类型的静态代码检查器
"""

from typing import Dict, Type, Optional, List
from library.static_checker.base import BaseStaticChecker
from library.static_checker.bracket_checker import BracketChecker
from library.static_checker.symbol_checker import SymbolChecker


class StaticCheckerFactory:
    """
    静态代码检查器工厂
    """
    
    def __init__(self):
        """
        初始化检查器工厂
        """
        self._checkers: Dict[str, List[Type[BaseStaticChecker]]] = {}
        self._language_to_extensions: Dict[str, List[str]] = {}
        
        # 注册默认的检查器和语言映射
        self._register_default_checkers()
        self._register_default_language_mappings()
    
    def _register_default_checkers(self):
        """
        注册默认的检查器
        """
        # 括号检查器支持所有语言
        all_languages = [
            "javascript", "typescript", "python", "java", "c", "cpp", 
            "csharp", "go", "ruby", "php", "html", "css", "json", 
            "xml", "yaml", "markdown"
        ]
        
        for lang in all_languages:
            self.register_checker(lang, BracketChecker)
        
        # 符号定义检查器，支持多种语言
        symbol_checker_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", 
            "csharp", "go", "ruby", "php"
        ]
        
        for lang in symbol_checker_languages:
            self.register_checker(lang, SymbolChecker)
    
    def _register_default_language_mappings(self):
        """
        注册默认的语言到文件扩展名映射
        """
        self._language_to_extensions = {
            "javascript": [".js"],
            "typescript": [".ts", ".tsx"],
            "python": [".py", ".pyw"],
            "java": [".java"],
            "c": [".c"],
            "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
            "csharp": [".cs"],
            "go": [".go"],
            "ruby": [".rb"],
            "php": [".php"],
            "html": [".html", ".htm"],
            "css": [".css"],
            "json": [".json"],
            "xml": [".xml"],
            "yaml": [".yaml", ".yml"],
            "markdown": [".md", ".markdown"]
        }
    
    def register_checker(self, language: str, checker_class: Type[BaseStaticChecker]):
        """
        注册一个新的检查器
        
        Args:
            language: 支持的编程语言
            checker_class: 检查器类
        """
        if language not in self._checkers:
            self._checkers[language] = []
        
        if checker_class not in self._checkers[language]:
            self._checkers[language].append(checker_class)
    
    def register_language_extension(self, language: str, extension: str):
        """
        注册语言到文件扩展名的映射
        
        Args:
            language: 编程语言
            extension: 文件扩展名（带点号，如 ".py"）
        """
        if language not in self._language_to_extensions:
            self._language_to_extensions[language] = []
        
        if extension not in self._language_to_extensions[language]:
            self._language_to_extensions[language].append(extension)
    
    def get_language_from_file(self, file_path: str) -> Optional[str]:
        """
        根据文件路径获取对应的编程语言
        
        Args:
            file_path: 文件路径
            
        Returns:
            对应的编程语言，如果无法确定则返回None
        """
        import os
        _, ext = os.path.splitext(file_path)
        
        for lang, extensions in self._language_to_extensions.items():
            if ext in extensions:
                return lang
        
        return None
    
    def create_checkers(self, language: str, editor_widget=None) -> List[BaseStaticChecker]:
        """
        创建指定语言的所有检查器实例
        
        Args:
            language: 编程语言
            editor_widget: 编辑器组件（可选）
            
        Returns:
            检查器实例列表
        """
        checkers = []
        
        if language in self._checkers:
            for checker_class in self._checkers[language]:
                checkers.append(checker_class(language, editor_widget))
        
        return checkers
    
    def create_checkers_for_file(self, file_path: str, editor_widget=None) -> List[BaseStaticChecker]:
        """
        根据文件路径创建对应的检查器实例
        
        Args:
            file_path: 文件路径
            editor_widget: 编辑器组件（可选）
            
        Returns:
            检查器实例列表
        """
        language = self.get_language_from_file(file_path)
        if language:
            return self.create_checkers(language, editor_widget)
        return []
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的编程语言列表
        
        Returns:
            支持的语言列表
        """
        return list(self._checkers.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            支持的文件扩展名列表
        """
        extensions = []
        for exts in self._language_to_extensions.values():
            extensions.extend(exts)
        return list(set(extensions))
