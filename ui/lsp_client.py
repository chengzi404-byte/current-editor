import json
import subprocess
import threading
import queue
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from pathlib import Path

class LSPClient(QObject):
    diagnostic_signal = pyqtSignal(str, list)
    
    def __init__(self, on_diagnostic=None):
        super().__init__()
        self.on_diagnostic = on_diagnostic
        self.process = None
        self.request_id = 0
        self.pending_requests = {}
        self.capabilities = {}
        self.server_ready = False
        self.document_uri = None
        self._message_queue = queue.Queue()
        self._running = False
        
    def start_server(self):
        import sys
        import shutil
        
        pyright_path = shutil.which("pyright") or shutil.which("pyright-langserver")
        
        if not pyright_path:
            print("Pyright not found, trying npx...")
            try:
                self.process = subprocess.Popen(
                    ["npx", "pyright-langserver", "--stdio"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            except FileNotFoundError:
                print("Error: pyright not installed. Please run: npm install -g pyright")
                return False
        else:
            self.process = subprocess.Popen(
                [pyright_path, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        
        self._running = True
        
        self._read_thread = threading.Thread(target=self._read_output, daemon=True)
        self._read_thread.start()
        
        QTimer.singleShot(500, self._initialize)
        
        return True
    
    def _read_output(self):
        buffer = bytearray()
        while self._running and self.process:
            try:
                data = self.process.stdout.read(1024)  # 批量读取
                if not data:
                    break
                
                buffer.extend(data)
                if b'\n' in buffer:
                    lines = buffer.split(b'\n')
                    buffer = lines[-1]  # 保留未处理的部分
                    for line in lines[:-1]:
                        try:
                            message = json.loads(line.decode('utf-8'))
                            self._handle_message(message)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                
                if char == '\n':
                    try:
                        message = json.loads(buffer)
                        self._handle_message(message)
                        buffer = ""
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"Read error: {e}")
                break
    
    def _handle_message(self, message):
        msg_id = message.get("id")
        method = message.get("method")
        
        if method == "textDocument/publishDiagnostics":
            params = message.get("params", {})
            uri = params.get("uri", "")
            diagnostics = params.get("diagnostics", [])
            
            if self.on_diagnostic:
                self.on_diagnostic(uri, diagnostics)
            self.diagnostic_signal.emit(uri, diagnostics)
            
        elif msg_id is not None and msg_id in self.pending_requests:
            callback = self.pending_requests.pop(msg_id)
            callback(message.get("result"))
    
    def _send_message(self, message):
        if not self.process or not self.process.stdin:
            return
        
        content = json.dumps(message)
        message_str = f"Content-Length: {len(content)}\r\n\r\n{content}"
        
        try:
            self.process.stdin.write(message_str)
            self.process.stdin.flush()
        except Exception as e:
            print(f"Send error: {e}")
    
    def _send_request(self, method, params, callback=None):
        self.request_id += 1
        msg_id = self.request_id
        
        message = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params
        }
        
        if callback:
            self.pending_requests[msg_id] = callback
        
        self._send_message(message)
        return msg_id
    
    def _send_notification(self, method, params):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self._send_message(message)
    
    def _initialize(self):
        workspace_path = str(Path.cwd())
        
        self._send_request("initialize", {
            "processId": None,
            "rootUri": f"file://{workspace_path}",
            "capabilities": {
                "textDocument": {
                    "synchronization": {
                        "willSave": False,
                        "didSave": True,
                        "willSaveWaitUntil": False
                    },
                    "completion": {
                        "dynamicRegistration": False,
                        "completionItem": {
                            "snippetSupport": False
                        }
                    },
                    "hover": {
                        "dynamicRegistration": False
                    }
                }
            }
        }, self._on_initialize)
    
    def _on_initialize(self, result):
        if result:
            self.capabilities = result.get("capabilities", {})
            self.server_ready = True
            
            self._send_notification("initialized", {})
            
            print("LSP Server initialized successfully")
    
    def open_document(self, uri, content, language_id="python"):
        self.document_uri = uri
        
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": 1,
                "text": content
            }
        })
    
    def change_document(self, uri, content, version):
        self._send_notification("textDocument/didChange", {
            "textDocument": {
                "uri": uri,
                "version": version
            },
            "contentChanges": [
                {
                    "text": content
                }
            ]
        })
    
    def save_document(self, uri, content):
        self._send_notification("textDocument/didSave", {
            "textDocument": {
                "uri": uri
            },
            "text": content
        })
    
    def close_document(self, uri):
        self._send_notification("textDocument/didClose", {
            "textDocument": {
                "uri": uri
            }
        })
    
    def get_diagnostics(self, uri):
        self._send_request("textDocument/diagnostics", {
            "textDocument": {
                "uri": uri
            }
        }, lambda result: print(f"Diagnostics: {result}"))
    
    def shutdown(self):
        self._running = False
        self._send_request("shutdown", {})
        
        if self.process:
            self._send_notification("exit", {})
            self.process.stdin.close()
            self.process.wait()
    
    def is_ready(self):
        return self.server_ready
