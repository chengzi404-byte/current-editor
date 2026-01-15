# Settings API 文档

## 1. 模块概述

Settings API (`library/api.py`) 是 Current Editor 的核心配置管理模块，提供全局配置访问接口。它采用了面向对象的设计模式，将不同类型的配置封装到不同的配置类中，便于管理和扩展。

## 2. 核心类与结构

### 2.1 ConfigManager 类

ConfigManager 是底层的配置管理类，负责加载、保存和管理配置数据。

```python
class ConfigManager:
    def __init__(self, config_file: str = "./asset/settings.json")
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def get_nested(self, keys: list, default: Any = None) -> Any
    def set_nested(self, keys: list, value: Any) -> None
```

### 2.2 配置类结构

Settings API 提供了多个配置类，每个类负责管理特定类型的配置：

| 配置类 | 描述 | 对应模块 |
|-------|------|---------|
| EditorConfig | 编辑器基本配置 | `library/api.py` |
| HighlighterConfig | 语法高亮配置 | `library/api.py` |
| RunConfig | 运行配置 | `library/api.py` |
| PackageConfig | 包配置 | `library/api.py` |
| AIConfig | AI功能配置 | `library/api.py` |
| LanguageConfig | 语言配置 | `library/api.py` |
| AdvancedConfig | 高级配置 | `library/api.py` |
| PathConfig | 路径配置 | `library/api.py` |

### 2.3 Settings 类

Settings 类是全局配置访问入口，整合了所有配置类：

```python
class Settings:
    Editor = EditorConfig(_config_manager)
    Highlighter = HighlighterConfig(_config_manager)
    Run = RunConfig(_config_manager)
    Package = PackageConfig(_config_manager)
    AI = AIConfig(_config_manager)
    Language = LanguageConfig(_config_manager)
    Advanced = AdvancedConfig(_config_manager)
    Path = PathConfig()
```

## 3. 详细API参考

### 3.1 EditorConfig

编辑器基本配置类，管理编辑器的核心设置。

```python
# 获取配置
font = Settings.Editor.font()            # 获取字体名称
font_size = Settings.Editor.font_size()  # 获取字体大小
encoding = Settings.Editor.file_encoding()  # 获取文件编码

# 修改配置
Settings.Editor.change("font", "Courier New")
Settings.Editor.change("fontsize", 14)
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `font()` | `str` | 获取编辑器字体 |
| `font_size()` | `int` | 获取字体大小 |
| `file_encoding()` | `str` | 获取文件编码 |
| `lang()` | `str` | 获取界面语言 |
| `file_path()` | `str` | 获取当前文件路径 |
| `wrap()` | `bool` | 获取自动换行设置 |
| `line_numbers()` | `bool` | 获取行号显示设置 |
| `highlight_current_line()` | `bool` | 获取当前行高亮设置 |
| `indent()` | `int` | 获取缩进大小 |
| `scrollbar()` | `bool` | 获取滚动条显示设置 |
| `change(key, value)` | `None` | 修改编辑器设置 |

### 3.2 HighlighterConfig

语法高亮配置类，管理语法高亮相关设置。

```python
# 获取配置
theme = Settings.Highlighter.theme()      # 获取当前主题
type_hints = Settings.Highlighter.enable_type_hints()  # 获取类型提示设置

# 修改配置
Settings.Highlighter.change("theme", "vscode-dark")
Settings.Highlighter.change("enable-type-hints", True)
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `syntax_highlighting()` | `dict` | 获取所有语法高亮设置 |
| `theme()` | `str` | 获取当前主题名称 |
| `code_type()` | `str` | 获取当前代码类型 |
| `enable_type_hints()` | `bool` | 获取类型提示设置 |
| `enable_docstrings()` | `bool` | 获取文档字符串设置 |
| `change(key, value)` | `None` | 修改高亮设置 |

### 3.3 RunConfig

运行配置类，管理代码运行相关设置。

```python
# 获取配置
timeout = Settings.Run.timeout()       # 获取超时时间
race_mode = Settings.Run.race_mode()   # 获取竞赛模式设置
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `timeout()` | `int` | 获取运行超时时间 |
| `race_mode()` | `bool` | 获取竞赛模式设置 |

### 3.4 PackageConfig

包配置类，管理主题和代码支持配置。

```python
# 获取配置
themes = Settings.Package.themes()         # 获取主题配置
code_support = Settings.Package.code_support()  # 获取代码支持配置
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `themes()` | `dict` | 获取主题配置 |
| `code_support()` | `dict` | 获取代码支持配置 |

### 3.5 AIConfig

AI功能配置类，管理AI相关设置。

```python
# 获取配置
api_key = Settings.AI.get_api_key()  # 获取API密钥

# 修改配置
Settings.AI.change("new_api_key")
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `get_api_key()` | `str` | 获取API密钥 |
| `change(apikey)` | `None` | 修改API密钥 |

### 3.6 LanguageConfig

语言配置类，管理语言相关设置。

```python
# 获取配置
default_lang = Settings.Language.default()  # 获取默认语言
auto_detect = Settings.Language.auto_detect()  # 获取自动检测设置

# 修改配置
Settings.Language.change("default", "javascript")
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `default()` | `str` | 获取默认语言 |
| `auto_detect()` | `bool` | 获取自动检测设置 |
| `change(key, value)` | `None` | 修改语言设置 |

### 3.7 AdvancedConfig

高级配置类，管理高级设置。

```python
# 获取配置
auto_save = Settings.Advanced.auto_save()  # 获取自动保存设置
save_interval = Settings.Advanced.save_interval()  # 获取保存间隔

# 修改配置
Settings.Advanced.change("auto-save", True)
Settings.Advanced.change("save-interval", 10)
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `auto_save()` | `bool` | 获取自动保存设置 |
| `save_interval()` | `int` | 获取保存间隔（秒） |
| `debug_mode()` | `bool` | 获取调试模式设置 |
| `change(key, value)` | `None` | 修改高级设置 |

### 3.8 PathConfig

路径配置类，提供路径相关的静态方法。

```python
# 获取路径
main_dir = Settings.Path.main_dir()   # 获取主目录
asset_dir = Settings.Path.asset_dir()  # 获取资源目录
```

#### 方法列表

| 方法名 | 返回类型 | 描述 |
|-------|---------|------|
| `main_dir()` | `Path` | 获取主目录 |
| `asset_dir()` | `Path` | 获取资源目录 |
| `theme_dir()` | `Path` | 获取主题目录 |
| `lang_dir()` | `Path` | 获取语言目录 |

## 4. 全局方法

Settings 类提供了一些全局方法用于管理配置：

```python
# 重新加载配置
Settings.reload()

# 获取所有设置
all_settings = Settings.get_all_settings()

# 重置为默认设置
Settings.reset_to_defaults()
```

## 5. 配置文件结构

配置文件 `asset/settings.json` 的结构如下：

```json
{
  "editor.file-encoding": "utf-8",
  "editor.lang": "Chinese",
  "editor.font": "Consolas",
  "editor.fontsize": 12,
  "highlighter.syntax-highlighting": {
    "theme": "github-dark",
    "enable-type-hints": true,
    "enable-docstrings": true,
    "code": "python"
  },
  "run.timeout": 1000,
  "run.racemode": false,
  "apikey": ""
}
```

## 6. 最佳实践

### 6.1 获取配置

```python
from library.api import Settings

# 在类初始化时获取配置
class MyClass:
    def __init__(self):
        self.font = Settings.Editor.font()
        self.font_size = Settings.Editor.font_size()
        self.theme = Settings.Highlighter.theme()
```

### 6.2 修改配置

```python
# 在用户操作时修改配置
def change_theme(theme_name):
    Settings.Highlighter.change("theme", theme_name)
    # 应用主题到当前编辑器
    current_editor.apply_theme(theme_name)
```

### 6.3 监听配置变化

```python
# 定期检查配置变化
last_theme = Settings.Highlighter.theme()

def check_config_changes():
    global last_theme
    current_theme = Settings.Highlighter.theme()
    if current_theme != last_theme:
        last_theme = current_theme
        apply_new_theme(current_theme)
    # 1秒后再次检查
    root.after(1000, check_config_changes)
```

## 7. 常见问题

### 7.1 配置不生效

**解决方案**：
- 确保调用了正确的配置方法
- 检查配置文件权限是否正确
- 尝试调用 `Settings.reload()` 重新加载配置

### 7.2 默认配置丢失

**解决方案**：
- 删除配置文件，系统会自动创建默认配置
- 调用 `Settings.reset_to_defaults()` 重置为默认设置

### 7.3 配置文件损坏

**解决方案**：
- 删除损坏的配置文件
- 调用 `Settings.reset_to_defaults()` 重置配置
