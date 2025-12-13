"""
API Configuration Module
配置管理和设置API
"""

import json
import pathlib
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "./asset/settings.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果配置文件不存在或格式错误，返回默认配置
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "editor.file-encoding": "utf-8",
            "editor.lang": "Chinese",
            "editor.font": "Consolas",
            "editor.fontsize": 12,
            "editor.file-path": "./temp_script.txt",
            "highlighter.syntax-highlighting": {
                "theme": "github-dark",
                "enable-type-hints": True,
                "enable-docstrings": True,
                "code": "python"
            },
            "run.timeout": 1000,
            "run.racemode": False,
            "apikey": ""
        }
    
    def save_settings(self) -> None:
        """保存设置到文件"""
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, "w", encoding="utf-8") as fp:
            json.dump(self._settings, fp, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._settings[key] = value
        self.save_settings()
    
    def get_nested(self, keys: list, default: Any = None) -> Any:
        """获取嵌套配置值"""
        current = self._settings
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    def set_nested(self, keys: list, value: Any) -> None:
        """设置嵌套配置值"""
        current = self._settings
        for key in keys[:-1]:
            if key not in current or not isinstance(current.get(key), dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.save_settings()


class EditorConfig:
    """编辑器配置类"""
    
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def file_encoding(self) -> str:
        """获取文件编码"""
        return self._config.get("editor.file-encoding", "utf-8")
    
    def lang(self) -> str:
        """获取语言设置"""
        return self._config.get("editor.lang", "Chinese")
    
    def langfile(self) -> str:
        """获取语言文件路径"""
        return f"./asset/packages/lang/{self.lang()}.json"
    
    def font(self) -> str:
        """获取字体设置"""
        return self._config.get("editor.font", "Consolas")
    
    def font_size(self) -> int:
        """获取字体大小"""
        return self._config.get("editor.fontsize", 12)
    
    def file_path(self) -> str:
        """获取文件路径"""
        return self._config.get("editor.file-path", "./temp_script.txt")
    
    def change(self, key: str, value: Any) -> None:
        """更改编辑器设置"""
        self._config.set(f"editor.{key}", value)


class HighlighterConfig:
    """语法高亮配置类"""
    
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def syntax_highlighting(self) -> Dict[str, Any]:
        """获取语法高亮设置"""
        return self._config.get("highlighter.syntax-highlighting", {})
    
    def theme(self) -> str:
        """获取主题"""
        return self.syntax_highlighting().get("theme", "github-dark")
    
    def code_type(self) -> str:
        """获取代码类型"""
        return self.syntax_highlighting().get("code", "python")
    
    def enable_type_hints(self) -> bool:
        """是否启用类型提示"""
        return self.syntax_highlighting().get("enable-type-hints", True)
    
    def enable_docstrings(self) -> bool:
        """是否启用文档字符串"""
        return self.syntax_highlighting().get("enable-docstrings", True)
    
    def change(self, key: str, value: Any) -> None:
        """更改高亮设置"""
        self._config.set_nested(["highlighter.syntax-highlighting", key], value)


class RunConfig:
    """运行配置类"""
    
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def timeout(self) -> Optional[int]:
        """获取超时设置"""
        if self._config.get("run.racemode", False):
            return self._config.get("run.timeout", 1000)
        return None
    
    def race_mode(self) -> bool:
        """获取竞赛模式设置"""
        return self._config.get("run.racemode", False)


class PackageConfig:
    """包配置类"""
    
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def themes(self) -> Dict[str, Any]:
        """获取主题配置"""
        try:
            with open("./asset/packages/themes.json", "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def code_support(self) -> Dict[str, Any]:
        """获取代码支持配置"""
        try:
            with open("./asset/packages/code_support.json", "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


class AIConfig:
    """AI配置类"""
    
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self._config.get("apikey", "")
    
    def change(self, apikey: str) -> None:
        """更改API密钥"""
        self._config.set("apikey", apikey)


class PathConfig:
    """路径配置类"""
    
    @staticmethod
    def main_dir() -> Path:
        """获取主目录"""
        return Path.cwd().parent
    
    @staticmethod
    def asset_dir() -> Path:
        """获取资源目录"""
        return Path.cwd() / "asset"
    
    @staticmethod
    def theme_dir() -> Path:
        """获取主题目录"""
        return Path.cwd() / "asset" / "theme"
    
    @staticmethod
    def lang_dir() -> Path:
        """获取语言目录"""
        return Path.cwd() / "asset" / "packages" / "lang"


# 全局配置管理器实例
_config_manager = ConfigManager()


class Settings:
    """设置类 - 提供全局配置访问接口"""
    
    Editor = EditorConfig(_config_manager)
    Highlighter = HighlighterConfig(_config_manager)
    Run = RunConfig(_config_manager)
    Package = PackageConfig(_config_manager)
    AI = AIConfig(_config_manager)
    Path = PathConfig()
    
    @staticmethod
    def reload() -> None:
        """重新加载配置"""
        global _config_manager
        _config_manager = ConfigManager()
        
        # 重新初始化所有配置类
        Settings.Editor = EditorConfig(_config_manager)
        Settings.Highlighter = HighlighterConfig(_config_manager)
        Settings.Run = RunConfig(_config_manager)
        Settings.Package = PackageConfig(_config_manager)
        Settings.AI = AIConfig(_config_manager)
    
    @staticmethod
    def get_all_settings() -> Dict[str, Any]:
        """获取所有设置"""
        return _config_manager._settings
    
    @staticmethod
    def reset_to_defaults() -> None:
        """重置为默认设置"""
        default_settings = _config_manager._get_default_settings()
        _config_manager._settings = default_settings
        _config_manager.save_settings()
        Settings.reload()


# 向后兼容性 - 保持原有API接口
with open("./asset/settings.json", "r", encoding="utf-8") as fp:
    settings = json.load(fp)

# 注意：以下代码仅为向后兼容性保留，新代码应使用新的Settings类
class LegacySettings:
    """旧版设置类 - 用于向后兼容"""
    
    class Editor:
        @staticmethod
        def file_encoding():        return settings["editor.file-encoding"]
        @staticmethod
        def lang():                 return settings["editor.lang"]
        @staticmethod
        def langfile():             return f"./asset/packages/lang/{settings['editor.lang']}.json"
        @staticmethod
        def font():                 return settings["editor.font"]
        @staticmethod
        def font_size():            return settings["editor.fontsize"]
        @staticmethod
        def file_path():            return settings["editor.file-path"]
        
        @staticmethod
        def change(key, value):
            settings[f"editor.{key}"] = value
            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)

    class Highlighter:
        @staticmethod
        def syntax_highlighting():  return settings["highlighter.syntax-highlighting"]
        
        @staticmethod
        def change(key, value):
            settings[f"highlighter.syntax-highlighting"][f"{key}"] = value
            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)
    
    class Run:
        @staticmethod
        def timeout():
            if settings["run.racemode"]: 
                return settings["run.timeout"] 
            else: 
                return None
    
    class Package:
        @staticmethod
        def themes():
            with open(f"{pathlib.Path.cwd().parent()}/asset/packages/packages/themes.json", "r", encoding="utf-8") as fp:
                return json.load(fp)
            
        @staticmethod
        def code_support():
            with open(f"{pathlib.Path.cwd().parent()}/asset/packages/packages/code_support.json", "r", encoding="utf-8") as fp:
                return json.load(fp)

    class Path:
        @staticmethod
        def main_dir():                  return pathlib.Path.cwd().parent()

    class AI:
        @staticmethod
        def get_api_key():          return settings["apikey"]
        
        @staticmethod
        def change(apikey):
            settings["apikey"] = apikey
            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)