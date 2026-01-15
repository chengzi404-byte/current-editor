"""
插件系统入口模块
提供插件管理、开发和使用的核心功能
"""

from library.plugins.base import (
    PluginPermission,
    PluginMetadata,
    PluginEvent,
    PluginCommunication,
    PluginBase,
    PluginManifest
)
from library.plugins.manager import PluginManager

__all__ = [
    # 核心管理器
    "PluginManager",
    
    # 基础类和接口
    "PluginBase",
    "PluginCommunication",
    
    # 数据结构和枚举
    "PluginMetadata",
    "PluginEvent",
    "PluginPermission",
    "PluginManifest"
]
