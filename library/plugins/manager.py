"""
插件管理器核心类
负责插件的注册、生命周期管理、加载发现、通信机制和权限控制
"""

import os
import sys
import json
import importlib.util
import inspect
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from library.plugins.base import (
    PluginBase,
    PluginMetadata,
    PluginPermission,
    PluginEvent,
    PluginCommunication,
    PluginManifest
)
from library.logger import get_logger


class PluginManager:
    """插件管理器核心类"""
    
    def __init__(self):
        self.logger = get_logger()
        self.plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        self.plugins_config_dir = Path(__file__).parent.parent.parent / "asset" / "plugins_config"
        
        # 确保插件配置目录存在
        self.plugins_config_dir.mkdir(exist_ok=True)
        
        # 插件存储
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        self._plugin_status: Dict[str, Dict[str, Any]] = {}
        
        # 权限管理
        self._permissions: Dict[str, List[PluginPermission]] = {}
        
        # 插件通信实例
        self.comm = PluginCommunication()
        self.comm.call_plugin_method = self._call_plugin_method
        
        # 插件配置管理
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # 加载插件配置
        self._load_plugins_config()
    
    # 插件发现与加载
    def discover_plugins(self) -> List[str]:
        """发现插件目录中的所有插件"""
        plugins = []
        
        # 检查插件目录是否存在
        if not self.plugins_dir.exists():
            self.logger.warning(f"插件目录不存在: {self.plugins_dir}")
            return plugins
        
        # 遍历插件目录
        for item in self.plugins_dir.iterdir():
            if item.is_dir():
                plugin_manifest = item / "plugin.json"
                if plugin_manifest.exists():
                    plugins.append(item.name)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载单个插件"""
        try:
            plugin_dir = self.plugins_dir / plugin_name
            manifest_path = plugin_dir / "plugin.json"
            
            # 检查插件目录和清单文件
            if not plugin_dir.exists() or not manifest_path.exists():
                self.logger.error(f"插件 {plugin_name} 不存在或清单文件缺失")
                return False
            
            # 读取插件清单
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # 解析插件元数据
            metadata = PluginManifest.from_dict(manifest_data)
            
            # 检查依赖
            if not self._check_dependencies(metadata.dependencies):
                self.logger.error(f"插件 {plugin_name} 的依赖不满足")
                return False
            
            # 动态加载插件模块
            plugin_module_path = plugin_dir / (metadata.entry_point + ".py")
            if not plugin_module_path.exists():
                self.logger.error(f"插件 {plugin_name} 的入口文件不存在: {plugin_module_path}")
                return False
            
            # 加载插件模块
            spec = importlib.util.spec_from_file_location(metadata.name, plugin_module_path)
            if spec is None:
                self.logger.error(f"无法创建插件 {plugin_name} 的模块规范")
                return False
            
            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules[metadata.name] = plugin_module
            
            # 添加插件目录到系统路径
            sys.path.insert(0, str(plugin_dir))
            
            try:
                spec.loader.exec_module(plugin_module)  # type: ignore
            finally:
                # 移除插件目录从系统路径
                sys.path.pop(0)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                self.logger.error(f"插件 {plugin_name} 中未找到继承自 PluginBase 的类")
                return False
            
            # 创建插件实例
            plugin_instance = plugin_class(self, metadata)
            
            # 调用插件加载方法
            if not plugin_instance.on_load():
                self.logger.error(f"插件 {plugin_name} 加载失败")
                return False
            
            # 加载插件配置
            plugin_instance.config = self._plugin_configs.get(plugin_name, {})
            
            # 保存插件实例和元数据
            self._plugins[plugin_name] = plugin_instance
            self._plugin_metadata[plugin_name] = metadata
            self._plugin_status[plugin_name] = {
                "loaded": True,
                "enabled": False,
                "activated": False
            }
            
            # 初始化权限
            self._permissions[plugin_name] = metadata.permissions
            
            self.logger.info(f"插件 {plugin_name} 加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"加载插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    def load_all_plugins(self) -> int:
        """加载所有发现的插件"""
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in plugins:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        return loaded_count
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载单个插件"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            
            # 确保插件已停用和禁用
            if plugin.is_activated():
                self.deactivate_plugin(plugin_name)
            if plugin.is_enabled():
                self.disable_plugin(plugin_name)
            
            # 调用插件卸载方法
            if not plugin.on_unload():
                self.logger.warning(f"插件 {plugin_name} 卸载方法执行失败")
            
            # 清理资源
            del self._plugins[plugin_name]
            del self._plugin_metadata[plugin_name]
            del self._plugin_status[plugin_name]
            if plugin_name in self._permissions:
                del self._permissions[plugin_name]
            
            # 从模块缓存中移除
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            
            self.logger.info(f"插件 {plugin_name} 卸载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"卸载插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    def unload_all_plugins(self) -> int:
        """卸载所有插件"""
        plugin_names = list(self._plugins.keys())
        unloaded_count = 0
        
        for plugin_name in plugin_names:
            if self.unload_plugin(plugin_name):
                unloaded_count += 1
        
        return unloaded_count
    
    # 插件生命周期管理
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            if plugin.is_enabled():
                self.logger.warning(f"插件 {plugin_name} 已启用")
                return True
            
            if plugin.on_enable():
                self._plugin_status[plugin_name]["enabled"] = True
                self.logger.info(f"插件 {plugin_name} 已启用")
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 启用失败")
                return False
                
        except Exception as e:
            self.logger.error(f"启用插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            if not plugin.is_enabled():
                self.logger.warning(f"插件 {plugin_name} 已禁用")
                return True
            
            if plugin.is_activated():
                self.deactivate_plugin(plugin_name)
            
            if plugin.on_disable():
                self._plugin_status[plugin_name]["enabled"] = False
                self.logger.info(f"插件 {plugin_name} 已禁用")
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 禁用失败")
                return False
                
        except Exception as e:
            self.logger.error(f"禁用插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """激活插件"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            if not plugin.is_enabled():
                self.logger.error(f"插件 {plugin_name} 未启用，无法激活")
                return False
            
            if plugin.is_activated():
                self.logger.warning(f"插件 {plugin_name} 已激活")
                return True
            
            if plugin.on_activate():
                self._plugin_status[plugin_name]["activated"] = True
                self.logger.info(f"插件 {plugin_name} 已激活")
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 激活失败")
                return False
                
        except Exception as e:
            self.logger.error(f"激活插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """停用插件"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            if not plugin.is_activated():
                self.logger.warning(f"插件 {plugin_name} 已停用")
                return True
            
            if plugin.on_deactivate():
                self._plugin_status[plugin_name]["activated"] = False
                self.logger.info(f"插件 {plugin_name} 已停用")
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 停用失败")
                return False
                
        except Exception as e:
            self.logger.error(f"停用插件 {plugin_name} 时发生错误: {str(e)}", exc_info=True)
            return False
    
    # 插件配置管理
    def _load_plugins_config(self):
        """加载所有插件的配置"""
        for config_file in self.plugins_config_dir.iterdir():
            if config_file.suffix == ".json":
                plugin_name = config_file.stem
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self._plugin_configs[plugin_name] = json.load(f)
                except Exception as e:
                    self.logger.error(f"加载插件 {plugin_name} 配置时发生错误: {str(e)}")
    
    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """保存插件配置"""
        try:
            config_file = self.plugins_config_dir / f"{plugin_name}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # 更新内存中的配置
            self._plugin_configs[plugin_name] = config
            self.logger.info(f"插件 {plugin_name} 配置已保存")
        except Exception as e:
            self.logger.error(f"保存插件 {plugin_name} 配置时发生错误: {str(e)}")
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件配置"""
        return self._plugin_configs.get(plugin_name, {})
    
    # 权限管理
    def check_permission(self, plugin_name: str, permission: PluginPermission) -> bool:
        """检查插件是否有指定权限"""
        if plugin_name not in self._permissions:
            return False
        
        return permission in self._permissions[plugin_name]
    
    def grant_permission(self, plugin_name: str, permission: PluginPermission):
        """授予插件权限"""
        if plugin_name not in self._permissions:
            self._permissions[plugin_name] = []
        
        if permission not in self._permissions[plugin_name]:
            self._permissions[plugin_name].append(permission)
            self.logger.info(f"已授予插件 {plugin_name} 权限: {permission.value}")
    
    def revoke_permission(self, plugin_name: str, permission: PluginPermission):
        """撤销插件权限"""
        if plugin_name in self._permissions and permission in self._permissions[plugin_name]:
            self._permissions[plugin_name].remove(permission)
            self.logger.info(f"已撤销插件 {plugin_name} 权限: {permission.value}")
    
    # 插件通信
    def _call_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用其他插件的方法"""
        if plugin_name not in self._plugins:
            self.logger.error(f"插件 {plugin_name} 未加载，无法调用其方法")
            return None
        
        plugin = self._plugins[plugin_name]
        if not hasattr(plugin, method_name):
            self.logger.error(f"插件 {plugin_name} 没有方法 {method_name}")
            return None
        
        try:
            method = getattr(plugin, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"调用插件 {plugin_name} 的方法 {method_name} 时发生错误: {str(e)}", exc_info=True)
            return None
    
    # 插件信息查询
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self._plugins.get(plugin_name)
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """获取插件元数据"""
        return self._plugin_metadata.get(plugin_name)
    
    def get_plugin_status(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件状态"""
        return self._plugin_status.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """列出所有已加载的插件"""
        return list(self._plugins.keys())
    
    def list_enabled_plugins(self) -> List[str]:
        """列出所有已启用的插件"""
        return [name for name, status in self._plugin_status.items() if status.get("enabled", False)]
    
    def list_activated_plugins(self) -> List[str]:
        """列出所有已激活的插件"""
        return [name for name, status in self._plugin_status.items() if status.get("activated", False)]
    
    # 辅助方法
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """检查插件依赖"""
        # 这里可以实现更复杂的依赖检查逻辑
        # 目前简单检查依赖的插件是否已加载
        for dep in dependencies:
            if dep not in self._plugins and not self.load_plugin(dep):
                return False
        return True
    
    def log(self, message: str, level: str = "info"):
        """记录日志"""
        if level == "debug":
            self.logger.debug(message)
        elif level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)
    
    # 插件系统初始化与关闭
    def initialize(self):
        """初始化插件系统"""
        self.logger.info("开始初始化插件系统")
        
        # 加载所有插件
        loaded_count = self.load_all_plugins()
        self.logger.info(f"共加载了 {loaded_count} 个插件")
        
        # 启用所有已配置为自动启用的插件
        # 这里可以读取配置文件，决定哪些插件需要自动启用
    
    def shutdown(self):
        """关闭插件系统"""
        self.logger.info("开始关闭插件系统")
        
        # 卸载所有插件
        unloaded_count = self.unload_all_plugins()
        self.logger.info(f"共卸载了 {unloaded_count} 个插件")
