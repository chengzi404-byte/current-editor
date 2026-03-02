import json
import os
import locale
from pathlib import Path

class I18n:
    def __init__(self):
        self.translations = {}
        self.current_lang = "en"
        self._load_translations()
        self._detect_system_language()
    
    def _load_translations(self):
        translations_dir = Path("./asset/lang")
        
        if not translations_dir.exists():
            translations_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_translations(translations_dir)
        
        for file in translations_dir.glob("*.json"):
            lang_code = file.stem
            try:
                with open(file, "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Failed to load translation file {file}: {e}")
        
        if not self.translations:
            self._create_default_translations(translations_dir)
            for file in translations_dir.glob("*.json"):
                lang_code = file.stem
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        self.translations[lang_code] = json.load(f)
                except:
                    pass
    
    def _create_default_translations(self, translations_dir):
        en_translations = {
            "app_title": "Current Editor",
            "file": "File",
            "new_file": "New File",
            "open_file": "Open File",
            "open_folder": "Open Folder",
            "save": "Save",
            "save_as": "Save As...",
            "exit": "Exit",
            "edit": "Edit",
            "undo": "Undo",
            "redo": "Redo",
            "cut": "Cut",
            "copy": "Copy",
            "paste": "Paste",
            "run": "Run",
            "settings": "Settings",
            "font": "Font",
            "theme": "Theme",
            "help": "Help",
            "about": "About",
            "about_text": "A modern code editor built with PyQt6\nVersion 1.0.0",
            "ready": "Ready",
            "running": "Running...",
            "execution_finished": "Execution finished",
            "execution_timeout": "Execution timed out",
            "clear_output": "Clear Output",
            "untitled": "Untitled",
            "explorer": "Explorer",
            "terminal": "Terminal",
            "confirm_exit": "Are you sure you want to exit?",
            "unsaved_changes": "You have unsaved changes. Save before closing?",
            "select_theme": "Select Theme",
            "select_font": "Select Font",
            "file_filter": "Python Files (*.py);;Text Files (*.txt);;All Files (*)",
            "error": "Error",
            "success": "Success",
            "opened": "Opened",
            "saved": "Saved",
            "new_file_created": "New file created",
            "folder_opened": "Folder opened",
            "lsp_server_ready": "LSP Server Ready",
            "lsp_server_error": "LSP Server Error",
            "no_pyright": "Pyright not found. Please install: npm install -g pyright"
        }
        
        zh_translations = {
            "app_title": "当前编辑器",
            "file": "文件",
            "new_file": "新建文件",
            "open_file": "打开文件",
            "open_folder": "打开文件夹",
            "save": "保存",
            "save_as": "另存为...",
            "exit": "退出",
            "edit": "编辑",
            "undo": "撤销",
            "redo": "重做",
            "cut": "剪切",
            "copy": "复制",
            "paste": "粘贴",
            "run": "运行",
            "settings": "设置",
            "font": "字体",
            "theme": "主题",
            "help": "帮助",
            "about": "关于",
            "about_text": "基于 PyQt6 构建的现代化代码编辑器\n版本 1.0.0",
            "ready": "就绪",
            "running": "运行中...",
            "execution_finished": "执行完成",
            "execution_timeout": "执行超时",
            "clear_output": "清除输出",
            "untitled": "未命名",
            "explorer": "资源管理器",
            "terminal": "终端",
            "confirm_exit": "确定要退出吗？",
            "unsaved_changes": "您有未保存的更改。关闭前是否保存？",
            "select_theme": "选择主题",
            "select_font": "选择字体",
            "file_filter": "Python 文件 (*.py);;文本文件 (*.txt);;所有文件 (*)",
            "error": "错误",
            "success": "成功",
            "opened": "已打开",
            "saved": "已保存",
            "new_file_created": "新文件已创建",
            "folder_opened": "文件夹已打开",
            "lsp_server_ready": "LSP 服务器就绪",
            "lsp_server_error": "LSP 服务器错误",
            "no_pyright": "未找到 Pyright。请运行: npm install -g pyright"
        }
        
        with open(translations_dir / "en.json", "w", encoding="utf-8") as f:
            json.dump(en_translations, f, indent=4, ensure_ascii=False)
        
        with open(translations_dir / "zh.json", "w", encoding="utf-8") as f:
            json.dump(zh_translations, f, indent=4, ensure_ascii=False)
    
    def _detect_system_language(self):
        try:
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                if system_lang.startswith("zh"):
                    self.current_lang = "zh"
                elif system_lang.startswith("en"):
                    self.current_lang = "en"
                else:
                    self.current_lang = "en"
        except:
            self.current_lang = "en"
        
        try:
            import sys
            if sys.platform == "win32":
                import ctypes
                windll = ctypes.windll.kernel32
                lang_id = windll.GetUserDefaultUILanguage()
                if (lang_id & 0x3ff) == 0x04:
                    self.current_lang = "zh"
                else:
                    self.current_lang = "en"
        except:
            pass
        
        if self.current_lang not in self.translations:
            self.current_lang = "en"
    
    def set_language(self, lang_code):
        if lang_code in self.translations:
            self.current_lang = lang_code
            return True
        return False
    
    def t(self, key, default=None):
        if default is None:
            default = key
        
        if self.current_lang in self.translations:
            return self.translations[self.current_lang].get(key, default)
        
        return self.translations.get("en", {}).get(key, default)
    
    def get_current_language(self):
        return self.current_lang
    
    def get_available_languages(self):
        return list(self.translations.keys())

_i18n = I18n()

def get_i18n():
    return _i18n

def t(key, default=None):
    return _i18n.t(key, default)

def set_language(lang_code):
    return _i18n.set_language(lang_code)

def get_current_language():
    return _i18n.get_current_language()
