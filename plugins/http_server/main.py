"""
HTTP Server 插件
在本地8000端口展示当前Tab对应的HTML页面预览
"""

from library.plugins import PluginBase
import http.server
import socketserver
import threading
import socket
import json

class HTTPServerPlugin(PluginBase):
    """HTTP服务器插件"""
    
    def __init__(self, plugin_manager, metadata):
        super().__init__(plugin_manager, metadata)
        self.log("HTTP Server 插件初始化")
        
        # 服务器相关属性
        self.server = None
        self.server_thread = None
        self.is_running = False
        
        # 配置默认值
        self.port = 8000
        self.auto_start = False
    
    def on_load(self) -> bool:
        """插件加载时调用"""
        self.log("HTTP Server 插件加载成功")
        
        # 加载配置
        self.port = self.get_config("port", 8000)
        self.auto_start = self.get_config("auto_start", False)
        
        return True
    
    def on_unload(self) -> bool:
        """插件卸载时调用"""
        self.log("HTTP Server 插件卸载成功")
        
        # 确保服务器已停止
        if self.is_running:
            self.stop_server()
        
        return True
    
    def on_enable(self) -> bool:
        """插件启用时调用"""
        self.log("HTTP Server 插件已启用")
        
        # 启用时自动启动服务器
        self.start_server()
        
        return True
    
    def on_disable(self) -> bool:
        """插件禁用时调用"""
        self.log("HTTP Server 插件已禁用")
        
        # 停止服务器
        if self.is_running:
            self.stop_server()
        
        return True
    
    def on_activate(self) -> bool:
        """插件激活时调用"""
        self.log("HTTP Server 插件已激活")
        
        # 启动服务器
        self.start_server()
        
        return True
    
    def on_deactivate(self) -> bool:
        """插件停用时调用"""
        self.log("HTTP Server 插件已停用")
        
        # 停止服务器
        if self.is_running:
            self.stop_server()
        
        return True
    
    def start_server(self):
        """启动HTTP服务器"""
        if self.is_running:
            self.log("HTTP服务器已在运行中")
            return
        
        try:
            # 创建自定义HTTP请求处理器
            class PreviewHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    """处理GET请求"""
                    # 获取插件实例
                    plugin = PreviewHTTPRequestHandler.plugin
                    
                    if self.path == '/':
                        # 返回当前编辑器的HTML内容
                        html_content = plugin._get_current_editor_content()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(html_content.encode('utf-8'))
                    elif self.path == '/status':
                        # 返回服务器状态
                        status = {
                            'running': plugin.is_running,
                            'port': plugin.port,
                            'current_file': plugin._get_current_file_path()
                        }
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps(status).encode('utf-8'))
                    else:
                        # 404响应
                        self.send_response(404)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')
            
            # 将插件实例传递给处理器
            PreviewHTTPRequestHandler.plugin = self
            
            # 创建服务器
            self.server = socketserver.TCPServer(('', self.port), PreviewHTTPRequestHandler)
            
            # 在后台线程中启动服务器
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_running = True
            self.log(f"HTTP服务器已启动，监听端口 {self.port}")
            self.log(f"访问地址: http://localhost:{self.port}")
            
        except Exception as e:
            self.log(f"启动HTTP服务器失败: {str(e)}", level="error")
    
    def stop_server(self):
        """停止HTTP服务器"""
        if not self.is_running:
            self.log("HTTP服务器未运行")
            return
        
        try:
            # 关闭服务器
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                
            # 等待线程结束
            if self.server_thread:
                self.server_thread.join(timeout=1)
            
            self.is_running = False
            self.server = None
            self.server_thread = None
            
            self.log("HTTP服务器已停止")
            
        except Exception as e:
            self.log(f"停止HTTP服务器失败: {str(e)}", level="error")
    
    def _run_server(self):
        """运行服务器的线程函数"""
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.is_running:
                self.log(f"服务器运行出错: {str(e)}", level="error")
                self.is_running = False
    
    def _get_current_editor_content(self) -> str:
        """获取当前编辑器的内容"""
        try:
            # 尝试获取当前编辑器内容
            # 这里需要通过插件通信获取当前编辑器的内容
            # 由于插件系统限制，我们需要通过调用主应用的方法来获取
            
            # 尝试从插件管理器获取app实例
            app = getattr(self.plugin_manager, '_app', None)
            if app is None:
                # 尝试其他方式获取app实例
                for attr_name in dir(self.plugin_manager):
                    attr = getattr(self.plugin_manager, attr_name)
                    if hasattr(attr, 'multi_editor'):
                        app = attr
                        break
            
            if app and hasattr(app, 'multi_editor'):
                # 获取当前编辑器
                current_editor = app.multi_editor.get_current_editor()
                if current_editor:
                    # 获取编辑器内容
                    content = current_editor.get("1.0", "end-1c")
                    return content
            
            # 如果无法获取编辑器内容，返回默认HTML
            return "<html><body><h1>无法获取编辑器内容</h1><p>请确保编辑器已打开并包含内容</p></body></html>"
            
        except Exception as e:
            self.log(f"获取编辑器内容失败: {str(e)}", level="error")
            return f"<html><body><h1>错误</h1><p>{str(e)}</p></body></html>"
    
    def _get_current_file_path(self) -> str:
        """获取当前文件路径"""
        try:
            # 尝试获取当前文件路径
            app = getattr(self.plugin_manager, '_app', None)
            if app is None:
                for attr_name in dir(self.plugin_manager):
                    attr = getattr(self.plugin_manager, attr_name)
                    if hasattr(attr, 'multi_editor'):
                        app = attr
                        break
            
            if app and hasattr(app, 'multi_editor'):
                # 获取当前文件路径
                current_file = app.multi_editor.get_current_file_path()
                return current_file or "未打开文件"
            
            return "未打开文件"
            
        except Exception as e:
            self.log(f"获取当前文件路径失败: {str(e)}", level="error")
            return "获取失败"
    
    def restart_server(self):
        """重启HTTP服务器"""
        self.log("重启HTTP服务器")
        self.stop_server()
        self.start_server()
    
    def get_server_status(self) -> dict:
        """获取服务器状态"""
        return {
            'running': self.is_running,
            'port': self.port,
            'current_file': self._get_current_file_path()
        }
    
    def set_port(self, port: int):
        """设置服务器端口"""
        if port != self.port:
            self.port = port
            self.set_config("port", port)
            
            # 如果服务器正在运行，需要重启
            if self.is_running:
                self.restart_server()
    
    def set_auto_start(self, auto_start: bool):
        """设置是否自动启动"""
        self.auto_start = auto_start
        self.set_config("auto_start", auto_start)
    
    def toggle_server(self):
        """切换服务器状态"""
        if self.is_running:
            self.stop_server()
        else:
            self.start_server()
        
        return self.is_running