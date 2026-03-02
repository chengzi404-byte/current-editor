import os
import sys
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette

class TerminalWidget(QWidget):
    commandExecuted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.history_index = -1
        
        self._init_ui()
    
    def _init_ui(self):
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        self.output_widget = QTextEdit()
        self.output_widget.setFont(QFont("Consolas", 10))
        self.output_widget.setReadOnly(True)
        self.output_widget.setAcceptRichText(False)
        self.output_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(0)
        
        self.prompt_label = QLabel("> ")
        self.prompt_label.setFont(QFont("Consolas", 10))
        
        self.input_widget = QLineEdit()
        self.input_widget.setFont(QFont("Consolas", 10))
        self.input_widget.setStyleSheet("border: none; background: transparent;")
        self.input_widget.returnPressed.connect(self._on_return_pressed)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.input_widget)
        
        layout.addWidget(self.output_widget, 1)
        layout.addLayout(input_layout)
        
        self._append_output("Terminal ready. Type a command and press Enter.\n")
        QTimer.singleShot(100, self.input_widget.setFocus)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.input_widget.setFocus()
    
    def _append_output(self, text):
        self.output_widget.moveCursor(QTextCursor.MoveOperation.End)
        self.output_widget.insertPlainText(text)
        self.output_widget.moveCursor(QTextCursor.MoveOperation.End)
    
    def _on_return_pressed(self):
        command = self.input_widget.text().strip()
        self.input_widget.clear()
        
        if not command:
            return
        
        self._append_output(f"> {command}\n")
        self.history.append(command)
        self.history_index = len(self.history)
        
        self._execute_command(command)
    
    def _execute_command(self, command):
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="gbk",
                    timeout=30
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.stdout:
                self._append_output(result.stdout)
            if result.stderr:
                self._append_output(f"[Error] {result.stderr}")
            
            if not result.stdout and not result.stderr:
                self._append_output("[No output]\n")
                
        except subprocess.TimeoutExpired:
            self._append_output("[Command timed out]\n")
        except Exception as e:
            self._append_output(f"[Error] {str(e)}\n")
        
        self._append_output("\n")
    
    def set_theme_colors(self, bg_color, fg_color):
        palette = self.output_widget.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(bg_color))
        palette.setColor(QPalette.ColorRole.Text, QColor(fg_color))
        self.output_widget.setPalette(palette)
        
        self.input_widget.setStyleSheet(f"""
            border: none; 
            background: {bg_color}; 
            color: {fg_color};
        """)
    
    def write(self, text):
        self._append_output(text)
    
    def clear(self):
        self.output_widget.clear()
