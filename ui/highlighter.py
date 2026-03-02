import re
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextFormat
from PyQt6.QtWidgets import QApplication
import json
from pathlib import Path

try:
    from python_lsp_python import PythonLSPlugin
    LSP_AVAILABLE = True
except ImportError:
    LSP_AVAILABLE = False

class LSPHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, theme_file=None):
        super().__init__(parent)
        self.document = parent.document()
        
        self.formats = {}
        self._load_theme(theme_file)
        
        self.lsp_ready = False
        self._init_lsp()
        
    def _load_theme(self, theme_file=None):
        if theme_file is None:
            theme_file = Path("./asset/theme/github-dark.json")
        
        if isinstance(theme_file, str):
            theme_file = Path(theme_file)
        
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme = json.load(f)
        except:
            theme = {
                "base": {"foreground": "#d4d4d4", "background": "#1e1e1e"},
                "keyword": "#569cd6",
                "string": "#ce9178",
                "number": "#b5cea8",
                "comment": "#6a9955",
                "function": "#dcdcaa",
                "class": "#4ec9b0",
                "variable": "#9cdcfe",
            }
        
        base_fg = theme.get("base", {}).get("foreground", "#d4d4d4")
        base_bg = theme.get("base", {}).get("background", "#1e1e1e")
        
        self.base_format = QTextCharFormat()
        self.base_format.setForeground(QColor(base_fg))
        
        self.editor_background = base_bg
        
        for token_type, color in theme.items():
            if token_type == "base":
                continue
            if not isinstance(color, str):
                continue
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            self.formats[token_type] = fmt
    
    def get_editor_background(self):
        return getattr(self, 'editor_background', '#1e1e1e')
    
    def _init_lsp(self):
        if not LSP_AVAILABLE:
            return
        
        try:
            from pygls.protocol import JsonRPCProtocol
            from pygls.server import LanguageServer
            from pygls.types import DiagnosticSeverity
            from python_lsp_python.basic import BasicDiagnosticsPlugin
            
            self.server = LanguageServer("python-lsp", "v1.0")
            self.lsp_ready = True
        except Exception as e:
            print(f"LSP initialization failed: {e}")
            self.lsp_ready = False
    
    def highlightBlock(self, text):
        if not text:
            return
        
        base_fg = self.base_format.foreground().color().name()
        
        default_format = QTextCharFormat()
        default_format.setForeground(QColor(base_fg))
        
        self.setFormat(0, len(text), default_format)
        
        patterns = self._get_patterns()
        
        for token_type, pattern in patterns:
            fmt = self.formats.get(token_type, default_format)
            
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
    
    def _get_patterns(self):
        return [
            ("variable", re.compile(r'\b[a-z_][a-zA-Z0-9_]*\b')),
            ("keyword", re.compile(r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|True|False|None)\b')),
            ("string", re.compile(r'["\'].*?["\']')),
            ("number", re.compile(r'\b\d+\.?\d*\b')),
            ("comment", re.compile(r'#.*$')),
            ("function", re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')),
            ("class", re.compile(r'\b([A-Z][a-zA-Z0-9_]*)\b')),
            ("decorator", re.compile(r'@\w+')),
            ("builtin", re.compile(r'\b(print|len|range|int|str|float|list|dict|set|tuple|bool|type|isinstance|hasattr|getattr|setattr|input|open|file|map|filter|zip|enumerate|sorted|reversed|sum|min|max|abs|round|pow|divmod)\b')),
        ]

class SyntaxHighlighter:
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.cpp': 'cpp',
        '.c': 'c',
        '.java': 'java',
        '.rs': 'rust',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.sh': 'bash',
    }
    
    def __init__(self, text_edit, theme_file=None):
        self.text_edit = text_edit
        self.highlighter = None
        self.theme_file = theme_file
        self.file_path = None
        
    def set_file_path(self, file_path):
        self.file_path = file_path
        ext = Path(file_path).suffix.lower() if file_path else '.py'
        highlighter_type = self.EXTENSION_MAP.get(ext, 'python')
        self._create_highlighter(highlighter_type)
    
    def _create_highlighter(self, highlighter_type):
        if self.highlighter:
            self.highlighter.deleteLater()
        
        if highlighter_type == 'python':
            self.highlighter = LSPHighlighter(self.text_edit, self.theme_file)
        else:
            self.highlighter = LSPHighlighter(self.text_edit, self.theme_file)
        
        self.highlighter.setDocument(self.text_edit.document())
    
    def set_theme(self, theme_file):
        self.theme_file = theme_file
        if self.highlighter:
            self.highlighter._load_theme(theme_file)
            self.highlighter.rehighlight()
