"""
AI服务模块
处理AI相关操作
"""

import time
import threading
import requests
from library.logger import get_logger


class AIService:
    """
    AI服务类
    处理AI相关操作
    """
    
    def __init__(self, ai_display, ai_input, ai_send_button, ai_queue, ai_loading=None):
        """
        初始化AI服务类
        
        Args:
            ai_display: AI显示区域
            ai_input: AI输入区域
            ai_send_button: AI发送按钮
            ai_queue: AI队列
            ai_loading: AI加载状态（可选）
        """
        self.ai_display = ai_display
        self.ai_input = ai_input
        self.ai_send_button = ai_send_button
        self.ai_queue = ai_queue
        self.ai_loading = ai_loading
        self.logger = get_logger()
    
    def send_ai_request_to_api(self, prompt, apikey):
        """
        发送AI请求到API
        
        Args:
            prompt: AI请求提示
            apikey: API密钥
        """
        self.ai_loading = True
        self.update_ai_loading()
        
        try:
            headers = {
                "Authorization": f"Bearer {apikey}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                self.ai_queue.put(ai_response)
            else:
                error_msg = f"AI Error: {response.status_code}, {response.text}"
                self.logger.error(error_msg)
                self.ai_queue.put(error_msg)
                
        except Exception as e:
            error_msg = f"AI Responce Error: {str(e)}"
            self.logger.error(error_msg)
            self.ai_queue.put(error_msg)
        finally:
            self.ai_loading = False
            self.update_ai_loading()
    
    def process_ai_responses(self):
        """
        处理AI响应
        """
        while not self.ai_queue.empty():
            response = self.ai_queue.get()
            self.display_ai_response(response)
            self.ai_queue.task_done()
    
    def display_ai_response(self, response):
        """
        显示AI响应
        
        Args:
            response: AI响应内容
        """
        current_time = time.strftime("%H:%M:%S")
        self.ai_display.config(state="normal")
        self.ai_display.insert("end", f"AI [{current_time}]:\n{response}\n\n")
        self.ai_display.see("end")
        self.ai_display.config(state="disabled")
    
    def update_ai_loading(self):
        """
        更新AI加载状态
        """
        if self.ai_loading and self.ai_send_button:
            self.ai_send_button.config(text="发送中...", state="disabled")
        elif self.ai_send_button:
            self.ai_send_button.config(text="发送", state="normal")
    
    def on_ai_input_enter(self, event):
        """
        AI输入回车事件
        
        Args:
            event: 事件对象
        """
        self.send_ai_request()
    
    def send_ai_request(self, prompt=None, apikey=None):
        """
        发送AI请求
        
        Args:
            prompt: AI请求提示（可选）
            apikey: API密钥（可选）
        """
        if prompt is None:
            prompt = self.ai_input.get()
        
        if not prompt:
            return
            
        current_time = time.strftime("%H:%M:%S")
        self.ai_display.config(state="normal")
        self.ai_display.insert("end", f"用户 [{current_time}]:\n{prompt}\n\n")
        self.ai_display.see("end")
        self.ai_display.config(state="disabled")
        
        self.ai_input.delete(0, "end")
        
        # 这里应该从设置中获取API密钥
        if apikey is None:
            from library.api import Settings
            apikey = Settings.AI.get_api_key()
        
        threading.Thread(target=self.send_ai_request_to_api, args=(prompt, apikey), daemon=True).start()
