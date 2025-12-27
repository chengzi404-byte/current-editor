from . import api
import importlib
import os

class HighlighterFactory:
    """Code highlighter factory class"""
    
    # 文件扩展名到高亮器类型的映射
    EXTENSION_MAP = {
        # 编程语言
        '.py': 'python',
        '.cpp': 'cpp',
        '.cxx': 'cpp',
        '.cc': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.java': 'java',
        '.rs': 'rust',
        '.sh': 'bash',
        '.bash': 'bash',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.js': 'javascript',
        '.rb': 'ruby',
        '.json': 'json',
        '.m': 'objc',
        
        # 新添加的文件类型
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.log': 'log',
        '.txt': 'log',  # 文本文件也使用日志高亮器
    }
    
    def create_highlighter(self, text_widget, file_path=None):
        """Create appropriate highlighter based on file extension"""
        # 优先根据文件扩展名选择高亮器
        if file_path:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext in self.EXTENSION_MAP:
                highlighter_type = self.EXTENSION_MAP[ext]
            else:
                # 如果没有匹配的扩展名，使用配置中的默认类型
                highlighter_type = api.Settings.Highlighter.syntax_highlighting()["code"]
        else:
            # 如果没有文件路径，使用配置中的默认类型
            highlighter_type = api.Settings.Highlighter.syntax_highlighting()["code"]
        
        # Import module
        try:
            module_name = f"library.highlighter.{highlighter_type}"
            module = importlib.import_module(module_name)
            
            # Create highlighter
            highlighter_class = getattr(module, 'CodeHighlighter')
            return highlighter_class(text_widget)
        except (ImportError, AttributeError):
            # 如果高亮器模块不存在，回退到默认高亮器
            module_name = "library.highlighter.python"
            module = importlib.import_module(module_name)
            highlighter_class = getattr(module, 'CodeHighlighter')
            return highlighter_class(text_widget)