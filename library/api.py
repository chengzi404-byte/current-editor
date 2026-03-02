import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_file: str = "./asset/settings.json"):
        self.config_file = Path(config_file)
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "editor.file-encoding": "utf-8",
            "editor.lang": "zh",
            "editor.font": "Consolas",
            "editor.fontsize": 12,
            "editor.file-path": "./temp",
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
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as fp:
            json.dump(self._settings, fp, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self.save_settings()

class EditorConfig:
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def file_encoding(self) -> str:
        return self._config.get("editor.file-encoding", "utf-8")
    
    def lang(self) -> str:
        return self._config.get("editor.lang", "zh")
    
    def font(self) -> str:
        return self._config.get("editor.font", "Consolas")
    
    def font_size(self) -> int:
        return self._config.get("editor.fontsize", 12)
    
    def file_path(self) -> str:
        return self._config.get("editor.file-path", "./temp")
    
    def wrap(self) -> bool:
        return self._config.get("editor.wrap", True)
    
    def line_numbers(self) -> bool:
        return self._config.get("editor.line-numbers", True)
    
    def indent(self) -> int:
        return self._config.get("editor.indent", 4)
    
    def change(self, key: str, value: Any) -> None:
        self._config.set(f"editor.{key}", value)

class HighlighterConfig:
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def syntax_highlighting(self) -> Dict[str, Any]:
        return self._config.get("highlighter.syntax-highlighting", {})
    
    def theme(self) -> str:
        return self.syntax_highlighting().get("theme", "github-dark")
    
    def code_type(self) -> str:
        return self.syntax_highlighting().get("code", "python")
    
    def change(self, key: str, value: Any) -> None:
        current = self.syntax_highlighting()
        current[key] = value
        self._config.set("highlighter.syntax-highlighting", current)

class RunConfig:
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def timeout(self) -> Optional[int]:
        if self._config.get("run.racemode", False):
            return self._config.get("run.timeout", 1000)
        return None
    
    def race_mode(self) -> bool:
        return self._config.get("run.racemode", False)

class AIConfig:
    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager
    
    def get_api_key(self) -> str:
        return self._config.get("apikey", "")
    
    def change(self, apikey: str) -> None:
        self._config.set("apikey", apikey)

class Settings:
    Editor = None
    Highlighter = None
    Run = None
    AI = None
    
    @classmethod
    def initialize(cls) -> None:
        config_manager = ConfigManager()
        cls.Editor = EditorConfig(config_manager)
        cls.Highlighter = HighlighterConfig(config_manager)
        cls.Run = RunConfig(config_manager)
        cls.AI = AIConfig(config_manager)

Settings.initialize()
