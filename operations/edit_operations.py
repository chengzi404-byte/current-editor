"""
编辑操作模块
处理复制、粘贴、撤销、重做等编辑操作
"""

from i18n import t


class EditOperations:
    """
    编辑操作类
    处理复制、粘贴、撤销、重做等编辑操作
    """
    
    def __init__(self, codearea, commandarea=None):
        """
        初始化编辑操作类
        
        Args:
            codearea: 代码编辑区域
            commandarea: 命令行区域（可选）
        """
        self.codearea = codearea
        self.commandarea = commandarea
        self.copy_msg = ""
    
    def copy(self):
        """
        复制选中内容
        """
        try:
            self.copy_msg = self.codearea.selection_get()
        except:
            try:
                if self.commandarea:
                    self.copy_msg = self.commandarea.selection_get()
            except:
                print(t("no_text_selected_to_copy"))
    
    def paste(self):
        """
        粘贴内容
        """
        try:
            self.codearea.insert("insert", self.copy_msg)
        except:
            print(t("paste_operation_failed"))
    
    def delete(self):
        """
        删除选中内容
        """
        try:
            self.codearea.delete("sel.first", "sel.last")
        except:
            print(t("no_text_selected_to_delete"))
    
    def undo(self):
        """
        撤销操作
        """
        try:
            self.codearea.edit_undo()
        except:
            print(t("undo_operation_failed"))
    
    def redo(self):
        """
        重做操作
        """
        try:
            self.codearea.edit_redo()
        except:
            print(t("redo_operation_failed"))