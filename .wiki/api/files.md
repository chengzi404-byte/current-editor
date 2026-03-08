# 文件操作 API 文档

## 1. 模块概述

文件操作 API (`library/file_operations.py`) 是 Current Editor 的核心文件管理模块，提供文件的创建、打开、保存、关闭等功能。它采用了面向对象的设计模式，封装了文件系统的操作，便于编辑器其他模块调用。

## 2. 核心类与结构

### 2.1 FileOperations 类

FileOperations 是文件操作的主要类，负责管理文件的基本操作：

```python
class FileOperations:
    def __init__(self)
    def new_file(self)
    def open_file(self)
    def save_file(self, editor=None)
    def save_as_file(self, editor=None)
    def close_file(self, editor=None)
    def save_all_files(self)
    def get_current_file_path(self)
    def set_current_file_path(self, file_path)
```

### 2.2 文件操作流程

文件操作的典型流程如下：

```
新建文件 → 编辑内容 → 保存文件 → 关闭文件
打开文件 → 编辑内容 → 保存文件 → 关闭文件
```

## 3. 详细 API 参考

### 3.1 基本文件操作

#### `new_file()`

创建一个新文件。

**参数**：无

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
file_ops.new_file()
```

#### `open_file()`

打开一个现有文件。

**参数**：无

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
file_ops.open_file()
```

#### `save_file(editor=None)`

保存当前文件。

**参数**：
- `editor`: 编辑器对象（可选）

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
# 保存当前文件
file_ops.save_file()
# 保存特定编辑器的文件
file_ops.save_file(current_editor)
```

#### `save_as_file(editor=None)`

另存为新文件。

**参数**：
- `editor`: 编辑器对象（可选）

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
# 另存为新文件
file_ops.save_as_file()
# 特定编辑器的文件另存为
file_ops.save_as_file(current_editor)
```

#### `close_file(editor=None)`

关闭当前文件。

**参数**：
- `editor`: 编辑器对象（可选）

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
# 关闭当前文件
file_ops.close_file()
# 关闭特定编辑器的文件
file_ops.close_file(current_editor)
```

#### `save_all_files()`

保存所有打开的文件。

**参数**：无

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
file_ops.save_all_files()
```

### 3.2 文件路径管理

#### `get_current_file_path()`

获取当前文件路径。

**参数**：无

**返回值**：`str` - 当前文件路径

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
current_path = file_ops.get_current_file_path()
print(f"当前文件路径：{current_path}")
```

#### `set_current_file_path(file_path)`

设置当前文件路径。

**参数**：
- `file_path`: `str` - 文件路径

**返回值**：无

**示例**：
```python
from operations.file_operations import FileOperations

file_ops = FileOperations()
file_ops.set_current_file_path("D:\\projects\\test.py")
```

## 4. 高级文件操作

### 4.1 文件内容处理

文件操作 API 支持各种文件内容处理功能：

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 文本编码 | 支持 UTF-8、GBK 等多种编码 | 使用 Python 内置的 `open()` 函数 |
| 行号管理 | 自动处理行号显示 | 通过编辑器组件实现 |
| 语法高亮 | 根据文件类型进行语法高亮 | 结合 `HighlighterFactory` 实现 |

### 4.2 自动保存功能

自动保存功能是文件操作的重要扩展：

```python
# 自动保存功能在 app.py 中初始化
def initialize_autosave():
    logger.info("初始化自动保存功能")
    # 创建保存目录
    os.makedirs(autosave_dir, exist_ok=True)
    # 设置自动保存定时器
    root.after(autosave_interval * 1000, autosave_task)
```

自动保存任务：

```python
def autosave_task():
    logger.info("--- 执行自动保存任务 ---")
    file_ops = FileOperations()
    file_ops.save_all_files()
    # 重新设置定时器
    root.after(autosave_interval * 1000, autosave_task)
```

## 5. 最佳实践

### 5.1 基本文件操作流程

```python
from operations.file_operations import FileOperations

# 初始化文件操作对象
file_ops = FileOperations()

# 创建新文件
file_ops.new_file()

# 编辑内容...

# 保存文件
file_ops.save_file()

# 另存为新文件
file_ops.save_as_file()

# 关闭文件
file_ops.close_file()
```

### 5.2 多文件管理

```python
from operations.file_operations import FileOperations

file_ops = FileOperations()

# 打开多个文件
file_ops.open_file()  # 第一个文件
file_ops.open_file()  # 第二个文件
file_ops.open_file()  # 第三个文件

# 保存所有文件
file_ops.save_all_files()
```

### 5.3 处理文件路径

```python
from operations.file_operations import FileOperations
import os

file_ops = FileOperations()

# 获取当前文件路径
current_path = file_ops.get_current_file_path()

# 检查文件是否存在
if os.path.exists(current_path):
    print(f"文件存在：{current_path}")
else:
    print(f"文件不存在：{current_path}")

# 获取文件目录
if current_path:
    file_dir = os.path.dirname(current_path)
    print(f"文件目录：{file_dir}")
```

## 6. 常见问题

### 6.1 文件无法保存

**解决方案**：
- 检查文件路径是否有效
- 确保有足够的权限写入文件
- 检查文件是否被其他程序锁定

### 6.2 文件编码问题

**解决方案**：
- 确保使用正确的编码打开文件
- 在设置中检查默认编码设置
- 使用 `save_as_file()` 选择正确的编码保存文件

### 6.3 自动保存失败

**解决方案**：
- 检查自动保存目录是否存在
- 确保有足够的权限写入自动保存目录
- 检查自动保存间隔设置是否合理

### 6.4 文件打开错误

**解决方案**：
- 检查文件是否存在
- 确保有足够的权限读取文件
- 检查文件格式是否被编辑器支持

## 7. 相关模块

| 模块 | 描述 | 对应文件 |
|------|------|---------|
| 编辑器操作 | 编辑器的核心操作 | `library/editor_operations.py` |
| 语法高亮 | 文件内容的语法高亮 | `library/highlighter.py` |
| 设置管理 | 文件操作相关设置 | `library/api.py` |
| 日志管理 | 文件操作的日志记录 | `library/logger.py` |
