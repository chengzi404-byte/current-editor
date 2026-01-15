# 插件开发文档

## 1. 插件系统概述

Current Editor 插件系统允许第三方开发者通过插件扩展编辑器的功能。插件系统提供了完整的生命周期管理、通信机制和权限控制，确保插件的安全性和稳定性。

### 1.1 核心功能

- **生命周期管理**：加载、初始化、激活、停用、卸载
- **插件间通信**：事件机制和直接方法调用
- **权限控制**：细粒度的权限管理
- **配置管理**：插件配置的加载和保存
- **自动发现**：自动发现和加载插件

### 1.2 插件系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    编辑器核心                             │
├─────────────────────────────────────────────────────────┤
│                    插件管理器                             │
├─────────────────┬─────────────────┬─────────────────────┤
│   插件 A        │   插件 B        │   插件 C             │
└─────────────────┴─────────────────┴─────────────────────┘
```

## 2. 插件目录结构

每个插件都应该有自己独立的目录，目录结构如下：

```
plugins/
└── your_plugin_name/
    ├── plugin.json          # 插件清单文件
    ├── main.py              # 插件主文件（入口点）
    └── other_files.py       # 其他插件文件（可选）
```

## 3. 插件清单文件

插件清单文件 `plugin.json` 是插件的元数据配置文件，包含插件的基本信息、权限请求和依赖关系。

### 3.1 清单文件格式

```json
{
  "name": "your_plugin_name",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "插件描述",
  "entry_point": "main",
  "permissions": ["permission1", "permission2"],
  "dependencies": ["other_plugin_name"],
  "config_schema": {
    "config_key": {
      "type": "string",
      "default": "default_value",
      "description": "配置描述"
    }
  }
}
```

### 3.2 清单字段说明

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 插件名称，必须唯一 |
| version | string | 是 | 插件版本，遵循语义化版本规范 |
| author | string | 是 | 插件作者 |
| description | string | 是 | 插件描述 |
| entry_point | string | 是 | 插件入口点（不含.py扩展名） |
| permissions | array | 否 | 插件请求的权限列表 |
| dependencies | array | 否 | 插件依赖的其他插件列表 |
| config_schema | object | 否 | 插件配置的JSON Schema |

## 4. 插件开发步骤

### 4.1 步骤1：创建插件目录

首先，在 `plugins` 目录下创建一个新的插件目录，例如：

```bash
mkdir plugins/your_plugin_name
```

### 4.2 步骤2：创建插件清单文件

在插件目录中创建 `plugin.json` 文件，定义插件的元数据。

### 4.3 步骤3：创建插件主文件

创建插件的主文件（与 `entry_point` 字段对应），例如 `main.py`。

### 4.4 步骤4：实现插件类

在主文件中实现一个继承自 `PluginBase` 的插件类：

```python
from library.plugins import PluginBase

class YourPlugin(PluginBase):
    def __init__(self, plugin_manager, metadata):
        super().__init__(plugin_manager, metadata)
        # 初始化代码
    
    def on_load(self) -> bool:
        # 插件加载时的逻辑
        return True
    
    # 实现其他生命周期方法
```

### 4.5 步骤5：实现功能逻辑

在插件类中实现具体的功能逻辑，可以使用插件系统提供的各种API。

### 4.6 步骤6：测试插件

将插件目录放在编辑器的 `plugins` 目录下，启动编辑器，插件会被自动发现和加载。

## 5. 插件生命周期

插件的生命周期包括以下阶段：

### 5.1 加载（Load）

- 调用时机：插件被发现后
- 主要任务：初始化插件实例，加载配置
- 相关方法：`on_load()`

### 5.2 启用（Enable）

- 调用时机：插件被启用时
- 主要任务：初始化插件功能，注册事件监听器
- 相关方法：`on_enable()`

### 5.3 激活（Activate）

- 调用时机：插件被用户激活时（例如，用户点击插件菜单）
- 主要任务：执行插件的核心功能
- 相关方法：`on_activate()`

### 5.4 停用（Deactivate）

- 调用时机：插件被用户停用时
- 主要任务：停止插件的核心功能
- 相关方法：`on_deactivate()`

### 5.5 禁用（Disable）

- 调用时机：插件被禁用时
- 主要任务：清理资源，注销事件监听器
- 相关方法：`on_disable()`

### 5.6 卸载（Unload）

- 调用时机：插件被卸载时
- 主要任务：彻底清理资源
- 相关方法：`on_unload()`

## 6. 插件API

### 6.1 插件基础类（PluginBase）

所有插件都必须继承自 `PluginBase` 类，该类提供了插件开发的核心API。

#### 6.1.1 生命周期方法

```python
def on_load(self) -> bool: ...
def on_unload(self) -> bool: ...
def on_enable(self) -> bool: ...
def on_disable(self) -> bool: ...
def on_activate(self) -> bool: ...
def on_deactivate(self) -> bool: ...
```

#### 6.1.2 配置管理

```python
def get_config(self, key: str, default: Any = None) -> Any: ...
def set_config(self, key: str, value: Any): ...
```

#### 6.1.3 日志记录

```python
def log(self, message: str, level: str = "info"): ...
```

#### 6.1.4 事件系统

```python
def emit_event(self, event_type: str, data: Dict[str, Any] = None): ...
def subscribe_event(self, event_type: str, callback: Callable): ...
def unsubscribe_event(self, event_type: str, callback: Callable): ...
```

#### 6.1.5 插件间通信

```python
def call_other_plugin(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any: ...
```

#### 6.1.6 权限检查

```python
def require_permission(self, permission: PluginPermission) -> bool: ...
```

## 7. 插件间通信

### 7.1 事件机制

插件可以通过事件机制进行通信，一个插件发布事件，其他插件订阅事件。

#### 7.1.1 发布事件

```python
# 在插件A中发布事件
self.emit_event("event_name", {"data": "value"})
```

#### 7.1.2 订阅事件

```python
# 在插件B中订阅事件
def handle_event(event):
    print(f"收到事件: {event.event_type}, 数据: {event.data}")
    event.mark_as_handled()

self.subscribe_event("event_name", handle_event)
```

### 7.2 直接方法调用

插件可以直接调用其他插件的公共方法：

```python
# 调用其他插件的方法
result = self.call_other_plugin("plugin_name", "method_name", arg1, arg2, kwarg1="value1")
```

## 8. 权限控制

插件系统实现了细粒度的权限控制，插件需要明确请求所需的权限。

### 8.1 可用权限

| 权限名称 | 描述 |
|---------|------|
| read_files | 读取文件 |
| write_files | 写入文件 |
| execute_commands | 执行命令 |
| access_editor | 访问编辑器 |
| access_terminal | 访问终端 |
| access_settings | 访问设置 |
| access_ui | 访问UI |
| manage_plugins | 管理插件 |
| access_sensitive_data | 访问敏感数据 |
| modify_core_functionality | 修改核心功能 |

### 8.2 请求权限

在 `plugin.json` 文件中请求权限：

```json
{
  "permissions": ["read_files", "access_editor"]
}
```

### 8.3 检查权限

在插件代码中检查权限：

```python
if self.require_permission(PluginPermission.READ_FILES):
    # 执行需要权限的操作
else:
    # 权限不足，处理错误
```

## 9. 配置管理

插件可以定义自己的配置，并通过插件系统自动加载和保存。

### 9.1 定义配置Schema

在 `plugin.json` 文件中定义配置Schema：

```json
{
  "config_schema": {
    "setting1": {
      "type": "string",
      "default": "default_value",
      "description": "设置1的描述"
    },
    "setting2": {
      "type": "boolean",
      "default": true,
      "description": "设置2的描述"
    }
  }
}
```

### 9.2 访问配置

```python
# 获取配置
setting1 = self.get_config("setting1", "default_value")

# 设置配置
self.set_config("setting1", "new_value")
```

## 10. 示例插件

### 10.1 简单的Hello World插件

#### 10.1.1 plugin.json

```json
{
  "name": "hello_world",
  "version": "1.0.0",
  "author": "Example Author",
  "description": "一个简单的示例插件",
  "entry_point": "main",
  "permissions": ["access_editor"],
  "dependencies": [],
  "config_schema": {
    "greeting": {
      "type": "string",
      "default": "Hello, World!",
      "description": "问候消息"
    }
  }
}
```

#### 10.1.2 main.py

```python
from library.plugins import PluginBase

class HelloWorldPlugin(PluginBase):
    def on_load(self) -> bool:
        self.log("Hello World 插件加载成功")
        self.greeting = self.get_config("greeting", "Hello, World!")
        return True
    
    def on_activate(self) -> bool:
        self.log(f"显示问候: {self.greeting}")
        # 在编辑器中插入文本（需要access_editor权限）
        return True
```

## 11. 调试和测试

### 11.1 日志记录

插件可以使用内置的日志系统记录调试信息：

```python
self.log("调试信息", level="debug")
self.log("错误信息", level="error")
```

### 11.2 常见问题

1. **插件不被加载**
   - 检查插件目录结构是否正确
   - 检查 `plugin.json` 文件格式是否正确
   - 检查入口点文件是否存在

2. **权限错误**
   - 确保在 `plugin.json` 中请求了所需的权限
   - 检查权限名称是否正确

3. **依赖错误**
   - 确保依赖的插件已安装
   - 检查依赖插件的名称是否正确

## 12. 最佳实践

### 12.1 代码组织

- 保持插件代码简洁，专注于单一功能
- 使用模块化设计，将复杂功能拆分为多个文件
- 遵循Python最佳实践和PEP 8规范

### 12.2 性能考虑

- 避免在频繁调用的方法中执行耗时操作
- 及时清理资源，避免内存泄漏
- 合理使用事件机制，避免过度订阅事件

### 12.3 安全性

- 只请求必要的权限
- 对用户输入进行验证
- 避免执行不安全的操作
- 保护敏感数据

### 12.4 兼容性

- 避免使用编辑器内部的私有API
- 考虑不同版本编辑器的兼容性
- 提供详细的版本要求

## 13. 发布插件

### 13.1 插件打包

将插件目录压缩为ZIP文件，便于分发和安装。

### 13.2 插件安装

用户可以将插件ZIP文件解压到编辑器的 `plugins` 目录下，插件会被自动发现和加载。

## 14. 结论

Current Editor 插件系统提供了强大的扩展能力，允许开发者轻松扩展编辑器功能。通过遵循本文档的指导，开发者可以创建安全、稳定、高效的插件。

如果您有任何问题或建议，欢迎提交Issue或Pull Request。

## 15. 更新日志

- v1.0.0 (2026-01-15)：初始版本

---

**文档版本**：1.0.0  
**最后更新**：2026-01-15
