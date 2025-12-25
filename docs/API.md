# 火凤编辑器 API 文档

## 目录

- [概述](#概述)
- [REST API](#rest-api)
  - [文件操作 API](#文件操作-api)
  - [健康检查 API](#健康检查-api)
- [WebSocket API](#websocket-api)
  - [Socket.IO 事件](#socket-io-事件)
- [Python API](#python-api)
  - [配置管理](#配置管理)
  - [编辑器配置](#编辑器配置)
  - [语法高亮配置](#语法高亮配置)
  - [运行配置](#运行配置)
  - [包配置](#包配置)
  - [AI 配置](#ai-配置)
  - [语言配置](#语言配置)
  - [高级配置](#高级配置)
  - [路径配置](#路径配置)
  - [全局设置](#全局设置)

---

## 概述

火凤编辑器提供了两种主要的 API 接口：
1. **REST API** - 用于文件操作和健康检查
2. **WebSocket API** - 用于实时协作和同步
3. **Python API** - 用于桌面端的配置管理

**服务器默认端口**: `5000`
**API 基础路径**: `http://localhost:5000/api`

---

## REST API

### 文件操作 API

#### 获取文件树

获取项目目录的文件树结构。

**端点**: `GET /api/files`

**响应**:
```json
{
  "success": true,
  "files": [
    {
      "name": "src",
      "path": "/src",
      "type": "folder",
      "size": 0,
      "modified": "2025-12-25T10:00:00.000Z",
      "children": [...]
    },
    {
      "name": "main.py",
      "path": "/main.py",
      "type": "file",
      "size": 1234,
      "modified": "2025-12-25T10:00:00.000Z"
    }
  ]
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误描述"
}
```

---

#### 读取文件或目录

读取文件内容或目录文件列表。

**端点**: `GET /api/file/:filePath(*)`

**路径参数**:
- `filePath` - 文件或目录的相对路径

**响应 (文件)**:
```json
{
  "success": true,
  "content": "文件内容字符串",
  "stats": {
    "size": 1234,
    "modified": "2025-12-25T10:00:00.000Z",
    "created": "2025-12-25T09:00:00.000Z"
  }
}
```

**响应 (目录)**:
```json
{
  "success": true,
  "files": [
    {
      "name": "file.py",
      "path": "/path/to/file.py",
      "type": "file",
      "size": 567,
      "modified": "2025-12-25T10:00:00.000Z"
    }
  ]
}
```

**限制**:
- 单个文件最大 5MB

**错误响应**:
- `403` - 访问被拒绝（路径超出项目目录）
- `413` - 文件过大（超过 5MB）
- `500` - 服务器错误

---

#### 保存文件

创建或更新文件内容。

**端点**: `POST /api/file/:filePath(*)`

**路径参数**:
- `filePath` - 文件的相对路径

**请求体**:
```json
{
  "content": "文件内容字符串"
}
```

**响应**:
```json
{
  "success": true
}
```

**WebSocket 广播**:
文件保存成功后，会向所有连接的客户端广播 `file_saved` 事件。

```json
{
  "filePath": "/path/to/file.py",
  "timestamp": 1735123200000
}
```

**错误响应**:
- `403` - 访问被拒绝
- `500` - 服务器错误

---

#### 删除文件

删除指定文件。

**端点**: `DELETE /api/file/:filePath(*)`

**路径参数**:
- `filePath` - 文件的相对路径

**响应**:
```json
{
  "success": true
}
```

**WebSocket 广播**:
文件删除成功后，会向所有连接的客户端广播 `file_deleted` 事件。

```json
{
  "filePath": "/path/to/file.py",
  "timestamp": 1735123200000
}
```

**错误响应**:
- `403` - 访问被拒绝
- `500` - 服务器错误

---

### 健康检查 API

#### 健康检查

检查服务器健康状态。

**端点**: `GET /health`

**响应**:
```json
{
  "status": "ok",
  "timestamp": "2025-12-25T10:00:00.000Z",
  "version": "1.0.0"
}
```

---

## WebSocket API

### Socket.IO 事件

#### 连接事件

**事件**: `connection`

客户端连接时触发。

**示例日志**:
```
用户连接: <socket_id>
```

---

#### 加入房间

**事件**: `join_room`

**参数**:
```json
{
  "roomId": "room_123"
}
```

客户端加入指定的协作房间。

---

#### 离开房间

**事件**: `leave_room`

**参数**:
```json
{
  "roomId": "room_123"
}
```

客户端离开指定的协作房间。

---

#### 文件变更

**事件**: `file_change`

**参数**:
```json
{
  "roomId": "room_123",
  "filePath": "/path/to/file.py",
  "content": "文件内容",
  "changes": [...]
}
```

广播文件变更给同一房间的其他用户。

**广播格式**:
```json
{
  "roomId": "room_123",
  "filePath": "/path/to/file.py",
  "content": "文件内容",
  "changes": [...],
  "userId": "<socket_id>"
}
```

---

#### 光标移动

**事件**: `cursor_move`

**参数**:
```json
{
  "roomId": "room_123",
  "filePath": "/path/to/file.py",
  "line": 10,
  "column": 20
}
```

广播光标位置给同一房间的其他用户。

**广播格式**:
```json
{
  "roomId": "room_123",
  "filePath": "/path/to/file.py",
  "line": 10,
  "column": 20,
  "userId": "<socket_id>"
}
```

---

#### 断开连接

**事件**: `disconnect`

客户端断开连接时触发。

**示例日志**:
```
用户断开连接: <socket_id>
```

---

#### 文件保存通知

**事件**: `file_saved` (服务器广播)

**参数**:
```json
{
  "filePath": "/path/to/file.py",
  "timestamp": 1735123200000
}
```

当有文件被保存时，服务器会向所有连接的客户端广播此事件。

---

#### 文件删除通知

**事件**: `file_deleted` (服务器广播)

**参数**:
```json
{
  "filePath": "/path/to/file.py",
  "timestamp": 1735123200000
}
```

当有文件被删除时，服务器会向所有连接的客户端广播此事件。

---

## Python API

Python API 主要用于桌面端应用程序的配置管理。

### 配置管理

#### ConfigManager 类

配置管理器，负责加载、保存和访问配置文件。

**初始化**:
```python
from library.api import ConfigManager

config = ConfigManager(config_file="./asset/settings.json")
```

**方法**:

##### `get(key, default=None)`

获取配置值。

**参数**:
- `key` (str) - 配置键
- `default` (any, optional) - 默认值

**返回**: 配置值

**示例**:
```python
font_size = config.get("editor.fontsize", 12)
```

---

##### `set(key, value)`

设置配置值并保存。

**参数**:
- `key` (str) - 配置键
- `value` (any) - 配置值

**示例**:
```python
config.set("editor.fontsize", 14)
```

---

##### `get_nested(keys, default=None)`

获取嵌套配置值。

**参数**:
- `keys` (list) - 配置键列表
- `default` (any, optional) - 默认值

**返回**: 配置值

**示例**:
```python
theme = config.get_nested(["highlighter.syntax-highlighting", "theme"], "github-dark")
```

---

##### `set_nested(keys, value)`

设置嵌套配置值并保存。

**参数**:
- `keys` (list) - 配置键列表
- `value` (any) - 配置值

**示例**:
```python
config.set_nested(["highlighter.syntax-highlighting", "theme"], "monokai")
```

---

##### `save_settings()`

保存设置到文件。

**示例**:
```python
config.save_settings()
```

---

### 编辑器配置

#### EditorConfig 类

编辑器配置类。

**初始化**:
```python
from library.api import Settings

editor_config = Settings.Editor
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `file_encoding()` | str | 获取文件编码 |
| `lang()` | str | 获取语言设置 |
| `langfile()` | str | 获取语言文件路径 |
| `font()` | str | 获取字体设置 |
| `font_size()` | int | 获取字体大小 |
| `file_path()` | str | 获取文件路径 |
| `wrap()` | bool | 获取自动换行设置 |
| `line_numbers()` | bool | 获取行号显示设置 |
| `highlight_current_line()` | bool | 获取高亮当前行设置 |
| `indent()` | int | 获取缩进大小设置 |
| `scrollbar()` | bool | 获取滚动条显示设置 |
| `change(key, value)` | None | 更改编辑器设置 |

**示例**:
```python
from library.api import Settings

# 获取字体大小
font_size = Settings.Editor.font_size()

# 更改字体
Settings.Editor.change("font", "Fira Code")
```

---

### 语法高亮配置

#### HighlighterConfig 类

语法高亮配置类。

**初始化**:
```python
from library.api import Settings

highlighter_config = Settings.Highlighter
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `syntax_highlighting()` | dict | 获取语法高亮设置 |
| `theme()` | str | 获取主题 |
| `code_type()` | str | 获取代码类型 |
| `enable_type_hints()` | bool | 是否启用类型提示 |
| `enable_docstrings()` | bool | 是否启用文档字符串 |
| `change(key, value)` | None | 更改高亮设置 |

**示例**:
```python
from library.api import Settings

# 获取当前主题
theme = Settings.Highlighter.theme()

# 切换主题
Settings.Highlighter.change("theme", "monokai")
```

---

### 运行配置

#### RunConfig 类

运行配置类。

**初始化**:
```python
from library.api import Settings

run_config = Settings.Run
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `timeout()` | int or None | 获取超时设置（竞赛模式下生效） |
| `race_mode()` | bool | 获取竞赛模式设置 |

**示例**:
```python
from library.api import Settings

# 检查是否启用竞赛模式
if Settings.Run.race_mode():
    timeout = Settings.Run.timeout()
    print(f"竞赛模式超时: {timeout}ms")
```

---

### 包配置

#### PackageConfig 类

包配置类，用于管理主题和代码支持。

**初始化**:
```python
from library.api import Settings

package_config = Settings.Package
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `themes()` | dict | 获取主题配置 |
| `code_support()` | dict | 获取代码支持配置 |

**示例**:
```python
from library.api import Settings

# 获取所有可用主题
themes = Settings.Package.themes()

# 获取代码支持的类型
code_support = Settings.Package.code_support()
```

---

### AI 配置

#### AIConfig 类

AI 配置类。

**初始化**:
```python
from library.api import Settings

ai_config = Settings.AI
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `get_api_key()` | str | 获取 API 密钥 |
| `change(apikey)` | None | 更改 API 密钥 |

**示例**:
```python
from library.api import Settings

# 设置 API 密钥
Settings.AI.change("your-api-key-here")

# 获取 API 密钥
api_key = Settings.AI.get_api_key()
```

---

### 语言配置

#### LanguageConfig 类

语言配置类。

**初始化**:
```python
from library.api import Settings

lang_config = Settings.Language
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `default()` | str | 获取默认语言设置 |
| `auto_detect()` | bool | 获取自动检测编码设置 |
| `change(key, value)` | None | 更改语言设置 |

**示例**:
```python
from library.api import Settings

# 获取默认语言
default_lang = Settings.Language.default()

# 启用自动检测
Settings.Language.change("auto-detect", True)
```

---

### 高级配置

#### AdvancedConfig 类

高级配置类。

**初始化**:
```python
from library.api import Settings

advanced_config = Settings.Advanced
```

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `auto_save()` | bool | 获取自动保存设置 |
| `save_interval()` | int | 获取保存间隔（秒） |
| `debug_mode()` | bool | 获取调试模式设置 |
| `change(key, value)` | None | 更改高级设置 |

**示例**:
```python
from library.api import Settings

# 启用自动保存
Settings.Advanced.change("auto-save", True)

# 设置保存间隔为 10 秒
Settings.Advanced.change("save-interval", 10)

# 启用调试模式
Settings.Advanced.change("debug-mode", True)
```

---

### 路径配置

#### PathConfig 类

路径配置类（静态方法）。

**方法**:

| 方法 | 返回类型 | 描述 |
|------|----------|------|
| `main_dir()` | Path | 获取主目录 |
| `asset_dir()` | Path | 获取资源目录 |
| `theme_dir()` | Path | 获取主题目录 |
| `lang_dir()` | Path | 获取语言目录 |

**示例**:
```python
from library.api import Settings

# 获取资源目录
asset_dir = Settings.Path.asset_dir()

# 获取主题目录
theme_dir = Settings.Path.theme_dir()
```

---

### 全局设置

#### Settings 类

全局设置类，提供统一的配置访问接口。

**方法**:

##### `reload()`

重新加载所有配置。

**示例**:
```python
from library.api import Settings

Settings.reload()
```

---

##### `get_all_settings()`

获取所有设置。

**返回**: dict - 所有设置

**示例**:
```python
from library.api import Settings

all_settings = Settings.get_all_settings()
print(all_settings)
```

---

##### `reset_to_defaults()`

重置为默认设置。

**示例**:
```python
from library.api import Settings

Settings.reset_to_defaults()
```

---

## 配置文件格式

### settings.json

编辑器配置文件，位于 `./asset/settings.json`。

**默认配置**:
```json
{
  "editor.file-encoding": "utf-8",
  "editor.lang": "Chinese",
  "editor.font": "Consolas",
  "editor.fontsize": 12,
  "editor.file-path": "./temp_script.txt",
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

---

## 错误代码

| 代码 | 描述 |
|------|------|
| 200 | 成功 |
| 403 | 访问被拒绝 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |

---

## 速率限制

- 无速率限制（当前版本）

---

## 安全性

- 所有文件操作限制在项目目录内
- 文件大小限制为 5MB
- CORS 配置允许 `http://localhost:3000`

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2025-12-25 | 初始版本 |

---

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 项目文档
