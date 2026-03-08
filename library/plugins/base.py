"""
插件系统基础类和接口定义
定义插件的生命周期、通信机制和权限控制
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import inspect


class PluginPermission(Enum):
    """插件权限枚举"""
    # 基础权限
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_COMMANDS = "execute_commands"
    ACCESS_EDITOR = "access_editor"
    ACCESS_TERMINAL = "access_terminal"
    ACCESS_SETTINGS = "access_settings"
    ACCESS_UI = "access_ui"
    
    # 高级权限
    MANAGE_PLUGINS = "manage_plugins"
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    MODIFY_CORE_FUNCTIONALITY = "modify_core_functionality"


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str                 # 插件名称
    version: str              # 插件版本
    author: str               # 插件作者
    description: str          # 插件描述
    entry_point: str          # 插件入口点
    permissions: List[PluginPermission] = None  # 插件请求的权限
    dependencies: List[str] = None  # 插件依赖
    config_schema: Dict[str, Any] = None  # 插件配置 schema
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class PluginEvent:
    """插件事件类"""
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self._handled = False
    
    def mark_as_handled(self):
        """标记事件为已处理"""
        self._handled = True
    
    def is_handled(self) -> bool:
        """检查事件是否已处理"""
        return self._handled


class PluginCommunication:
    """插件间通信管理器"""
    
    def __init__(self):
        self._event_listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅事件"""
        if event_type in self._event_listeners:
            self._event_listeners[event_type].remove(callback)
            if not self._event_listeners[event_type]:
                del self._event_listeners[event_type]
    
    def publish(self, event: PluginEvent) -> bool:
        """发布事件"""
        if event.event_type in self._event_listeners:
            for callback in self._event_listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener for {event.event_type}: {e}")
            return True
        return False
    
    def call_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用其他插件的方法"""
        # 此方法将由 PluginManager 实现
        raise NotImplementedError("This method should be implemented by PluginManager")


class PluginBase:
    """插件基础类，所有插件都应继承此类"""
    
    def __init__(self, plugin_manager, metadata: PluginMetadata):
        self.plugin_manager = plugin_manager
        self.metadata = metadata
        self.name = metadata.name
        self.config = {}
        self._enabled = False
        self._activated = False
        
        # 插件通信实例
        self.comm = plugin_manager.comm
    
    # 生命周期方法
    def on_load(self) -> bool:
        """插件加载时调用"""
        return True
    
    def on_unload(self) -> bool:
        """插件卸载时调用"""
        return True
    
    def on_enable(self) -> bool:
        """插件启用时调用"""
        self._enabled = True
        return True
    
    def on_disable(self) -> bool:
        """插件禁用时调用"""
        self._enabled = False
        return True
    
    def on_activate(self) -> bool:
        """插件激活时调用（如用户打开插件功能）"""
        self._activated = True
        return True
    
    def on_deactivate(self) -> bool:
        """插件停用时调用"""
        self._activated = False
        return True
    
    # 配置管理
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取插件配置"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """设置插件配置"""
        self.config[key] = value
        self.plugin_manager.save_plugin_config(self.name, self.config)
    
    # 状态检查
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return self._enabled
    
    def is_activated(self) -> bool:
        """检查插件是否激活"""
        return self._activated
    
    # 工具方法
    def log(self, message: str, level: str = "info"):
        """记录日志"""
        self.plugin_manager.log(f"[{self.name}] {message}", level)
    
    def require_permission(self, permission: PluginPermission) -> bool:
        """检查插件是否有指定权限"""
        return self.plugin_manager.check_permission(self.name, permission)
    
    def emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """发送事件"""
        event = PluginEvent(event_type, data)
        self.comm.publish(event)
    
    def subscribe_event(self, event_type: str, callback: Callable):
        """订阅事件"""
        self.comm.subscribe(event_type, callback)
    
    def unsubscribe_event(self, event_type: str, callback: Callable):
        """取消订阅事件"""
        self.comm.unsubscribe(event_type, callback)
    
    def call_other_plugin(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用其他插件的方法"""
        return self.comm.call_plugin_method(plugin_name, method_name, *args, **kwargs)


class PluginManifest:
    """插件清单类，用于解析插件配置文件"""
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> PluginMetadata:
        """从字典创建插件元数据"""
        permissions = [PluginPermission(p) for p in data.get("permissions", [])]
        return PluginMetadata(
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            entry_point=data["entry_point"],
            permissions=permissions,
            dependencies=data.get("dependencies", []),
            config_schema=data.get("config_schema", {})
        )
    
    @staticmethod
    def to_dict(metadata: PluginMetadata) -> Dict[str, Any]:
        """将插件元数据转换为字典"""
        return {
            "name": metadata.name,
            "version": metadata.version,
            "author": metadata.author,
            "description": metadata.description,
            "entry_point": metadata.entry_point,
            "permissions": [p.value for p in metadata.permissions],
            "dependencies": metadata.dependencies,
            "config_schema": metadata.config_schema
        }
