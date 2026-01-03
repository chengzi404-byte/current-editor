"""
编辑操作模块
处理复制、粘贴、撤销、重做等编辑操作
"""


class EditOperations:
    """
    编辑操作类
    处理复制、粘贴、撤销、重做等编辑操作
    """
    
    def __init__(self, codearea, printarea=None):
        """
        初始化编辑操作类
        
        Args:
            codearea: 代码编辑区域
            printarea: 输出区域（可选）
        """
        self.codearea = codearea
        self.printarea = printarea
        self.copy_msg = ""
    
    def copy(self):
        """
        复制选中内容
        """
        try:
            self.copy_msg = self.codearea.selection_get()
        except:
            try:
                if self.printarea:
                    self.copy_msg = self.printarea.selection_get()
            except:
                pass
    
    def paste(self):
        """
        粘贴内容
        """
        try:
            self.codearea.insert("insert", self.copy_msg)
        except:
            pass
    
    def delete(self):
        """
        删除选中内容
        """
        try:
            self.codearea.delete("sel.first", "sel.last")
        except:
            pass
    
    def undo(self):
        """
        撤销操作
        """
        try:
            self.codearea.edit_undo()
        except:
            pass
    
    def redo(self):
        """
        重做操作
        """
        try:
            self.codearea.edit_redo()
        except:
            pass
