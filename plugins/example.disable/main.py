"""
Hello World 示例插件
演示插件系统的基本功能
"""

from library.plugins import PluginBase


class HelloWorldPlugin(PluginBase):
    """Hello World 示例插件"""
    
    def __init__(self, plugin_manager, metadata):
        super().__init__(plugin_manager, metadata)
        self.log("Hello World 插件初始化")
    
    def on_load(self) -> bool:
        """插件加载时调用"""
        self.log("Hello World 插件加载成功")
        
        # 加载配置
        self.greeting_message = self.get_config("greeting_message", "Hello, World!")
        self.show_on_startup = self.get_config("show_on_startup", True)
        
        return True
    
    def on_unload(self) -> bool:
        """插件卸载时调用"""
        self.log("Hello World 插件卸载成功")
        return True
    
    def on_enable(self) -> bool:
        """插件启用时调用"""
        self.log("Hello World 插件已启用")
        
        # 如果配置为启动时显示消息，则显示
        if self.show_on_startup:
            self._show_greeting()
        
        return True
    
    def on_disable(self) -> bool:
        """插件禁用时调用"""
        self.log("Hello World 插件已禁用")
        return True
    
    def on_activate(self) -> bool:
        """插件激活时调用"""
        self.log("Hello World 插件已激活")
        self._show_greeting()
        return True
    
    def on_deactivate(self) -> bool:
        """插件停用时调用"""
        self.log("Hello World 插件已停用")
        return True
    
    def _show_greeting(self):
        """显示问候消息"""
        # 这里可以添加与编辑器交互的代码
        # 例如，在编辑器中插入文本或显示消息框
        self.log(f"显示问候消息: {self.greeting_message}")
    
    def get_greeting(self) -> str:
        """获取问候消息（供其他插件调用）"""
        return self.greeting_message
    
    def set_greeting(self, message: str):
        """设置问候消息"""
        self.greeting_message = message
        self.set_config("greeting_message", message)
        self.log(f"问候消息已更新为: {message}")
    
    def test_event(self):
        """测试事件发送"""
        self.emit_event("hello_world.greeting", {
            "message": self.greeting_message,
            "plugin_name": self.name
        })
        self.log("已发送问候事件")
