# API文档

## 1. 项目架构与API设计理念

Current Editor 是一个基于 Python 的桌面代码编辑器，采用模块化架构设计，主要分为以下几个核心模块：

### 1.1 架构概述

```
├── library/           # 核心库模块
│   ├── api.py         # 配置管理API
│   ├── editor_operations.py  # 编辑器操作API
│   ├── multi_file_editor.py  # 多文件编辑器API
│   ├── highlighter/   # 语法高亮API
│   └── ...
├── ui/                # UI界面模块
│   ├── main_window.py # 主窗口API
│   ├── menu.py        # 菜单API
│   └── ...
└── operations/        # 业务操作模块
    ├── edit_operations.py  # 编辑操作API
    ├── file_operations.py  # 文件操作API
    └── ...
```

### 1.2 API设计理念

- **分层设计**：将UI层、业务逻辑层和核心功能层分离
- **面向对象**：主要API都封装在类中，通过实例方法调用
- **可扩展性**：支持插件系统和自定义主题
- **一致性**：统一的命名规范和调用方式

## 2. 核心API模块

### 2.1 Settings API (library/api.py)

Settings API 是编辑器的核心配置管理模块，提供全局配置访问接口。

```python
from library.api import Settings

# 获取编辑器配置
font = Settings.Editor.font()
font_size = Settings.Editor.font_size()

# 获取语法高亮配置
theme = Settings.Highlighter.theme()
code_type = Settings.Highlighter.code_type()

# 获取高级配置
auto_save = Settings.Advanced.auto_save()
save_interval = Settings.Advanced.save_interval()

# 修改配置
Settings.Editor.change("font", "Courier New")
Settings.Highlighter.change("theme", "vscode-dark")
```

详细API文档：[Settings API](./settings.md)

### 2.2 EditorOperations API (library/editor_operations.py)

EditorOperations API 提供了编辑器的核心操作功能。

```python
from library.editor_operations import EditorOperations

# 初始化编辑器操作
editor_ops = EditorOperations(root, text_widget, terminal, multi_editor)

# 文件操作
editor_ops.new_file()
editor_ops.open_file()
editor_ops.save_file()

# 编辑操作
editor_ops.copy()
editor_ops.paste()
editor_ops.undo()
editor_ops.redo()

# 运行代码
editor_ops.run()
```

详细API文档：[EditorOperations API](./editor_operations.md)

### 2.3 MultiFileEditor API (library/multi_file_editor.py)

MultiFileEditor API 管理多标签页编辑功能。

```python
from library.multi_file_editor import MultiFileEditor

# 创建多文件编辑器
multi_editor = MultiFileEditor(editor_frame, terminal_area, file_tree, settings)

# 标签页操作
multi_editor.new_tab()
multi_editor.close_tab(tab_id)
multi_editor.switch_tab(tab_id)

# 获取当前编辑器
current_editor = multi_editor.get_current_editor()

# 显示特殊标签页
multi_editor.show_settings_tab()
multi_editor.show_help_tab()
```

详细API文档：[MultiFileEditor API](./multi_file_editor.md)

### 2.4 Highlighter API (library/highlighter/)

Highlighter API 提供了丰富的语法高亮功能。

```python
from library.highlighter_factory import HighlighterFactory

# 创建高亮器工厂
highlighter_factory = HighlighterFactory()

# 创建特定语言的高亮器
python_highlighter = highlighter_factory.create_highlighter(text_widget, "python")

# 设置主题
python_highlighter.set_theme(theme_data)

# 执行高亮
python_highlighter.highlight()
```

详细API文档：[Highlighter API](./highlighter.md)

### 2.5 Logger API (library/logger.py)

Logger API 提供了完整的日志记录功能。

```python
from library.logger import get_logger, shutdown_logger

# 获取日志记录器
logger = get_logger()

# 记录日志
logger.info("程序启动")
logger.error("发生错误")
logger.exception("异常信息")

# 关闭日志记录器
shutdown_logger()
```

详细API文档：[Logger API](./logger.md)

## 3. 上手指南

### 3.1 环境准备

- Python 3.8+
- Windows 操作系统（目前仅支持Windows）
- 依赖库：
  - tkinter (Python标准库)
  - json (Python标准库)
  - pathlib (Python标准库)
  - requests (用于AI功能)

### 3.2 快速入门

```python
# 导入必要的模块
from library.api import Settings
from library.highlighter_factory import HighlighterFactory
from ui.main_window import MainWindow
from ui.menu import MenuBar

# 创建主窗口
root = MainWindow()

# 创建多文件编辑器
from library.multi_file_editor import MultiFileEditor
multi_editor = MultiFileEditor(root.editor_frame, root.terminal_area, None, None)

# 创建文件浏览器
from ui.file_browser import FileBrowser
file_browser = FileBrowser(root.file_tree_frame, app)

# 创建菜单
menu_bar = MenuBar(root, app)

# 启动主循环
root.mainloop()
```

### 3.3 基础概念解释

- **Editor**: 单个文件的编辑器组件，提供文本编辑功能
- **MultiFileEditor**: 多文件编辑器管理组件，支持标签页管理
- **Highlighter**: 语法高亮器，负责代码的着色显示
- **EditorOperations**: 编辑器操作集合，提供复制、粘贴、运行等功能
- **Settings**: 全局配置管理，提供配置的读取和修改功能

## 4. API快速参考

| 模块 | 主要类/函数 | 功能描述 |
|------|------------|----------|
| library.api | Settings | 全局配置管理 |
| library.editor_operations | EditorOperations | 编辑器核心操作 |
| library.multi_file_editor | MultiFileEditor | 多文件编辑管理 |
| library.highlighter_factory | HighlighterFactory | 语法高亮器工厂 |
| library.logger | get_logger | 日志记录器获取 |
| ui.main_window | MainWindow | 主窗口创建 |
| ui.menu | MenuBar | 菜单创建与管理 |
| ui.file_browser | FileBrowser | 文件浏览器 |

## 5. 文档导航

- [Settings API](./settings.md)
- [EditorOperations API](./editor_operations.md)
- [MultiFileEditor API](./multi_file_editor.md)
- [Highlighter API](./highlighter.md)
- [Logger API](./logger.md)
- [UI组件API](./ui.md)
- [文件操作API](./file_operations.md)
- [编辑操作API](./edit_operations.md)
