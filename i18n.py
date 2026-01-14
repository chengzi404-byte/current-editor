import json
import os
from typing import Dict, Optional

class I18n:
    def __init__(self, default_lang: str = 'zh'):
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """加载所有语言的翻译文件"""
        lang_dir = os.path.join(os.path.dirname(__file__), 'lang')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        # 查找语言文件
        for filename in os.listdir(lang_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]
                filepath = os.path.join(lang_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {filepath}: {e}")
    
    def set_language(self, lang: str):
        """设置当前语言"""
        if lang in self.translations:
            self.current_lang = lang
        else:
            # 如果指定语言不存在，使用默认语言
            self.current_lang = self.default_lang
    
    def t(self, key: str, **kwargs) -> str:
        """翻译文本"""
        # 首先尝试当前语言
        if self.current_lang in self.translations and key in self.translations[self.current_lang]:
            text = self.translations[self.current_lang][key]
        # 然后尝试默认语言
        elif self.default_lang in self.translations and key in self.translations[self.default_lang]:
            text = self.translations[self.default_lang][key]
        # 如果都找不到，返回key本身
        else:
            text = key
        
        # 支持参数替换
        try:
            return text.format(**kwargs)
        except KeyError:
            return text

# 创建全局实例
i18n = I18n()

def set_language(lang: str):
    i18n.set_language(lang)

def t(key: str, **kwargs) -> str:
    tmp = I18n()
    tmp.set_language("zh")
    return tmp.t(key, **kwargs)

if __name__ == '__main__':
    # 测试
    print(t('app_title'))