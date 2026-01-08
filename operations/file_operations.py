import os
import shutil
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# 导入国际化模块 - 修改为绝对路径导入
try:
    from i18n import t
except ImportError:
    # 如果无法导入i18n模块，创建一个模拟函数
    def t(key, **kwargs):
        return "Err: i18n module not found"

class FileOperations:
    """文件操作类，提供常见的文件和目录操作功能"""
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 默认最大10MB
        self.max_file_size = max_file_size
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        读取文件内容
        :param file_path: 文件路径
        :param encoding: 文件编码
        :return: 文件内容字符串，如果失败返回None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(t("file_not_found", file_path=file_path))
                return None
            
            if not path.is_file():
                print(t("operation_failed", error=t("file_not_found", file_path=file_path)))
                return None
                
            # 检查文件大小
            if path.stat().st_size > self.max_file_size:
                print(t("file_size_limit_exceeded", max_size=self.max_file_size))
                return None
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(t("file_content_read"))
                return content
        except UnicodeDecodeError:
            print(t("encoding_error", encoding=encoding))
            return None
        except PermissionError:
            print(t("permission_denied", path=file_path))
            return None
        except Exception as e:
            print(t("read_failed", path=file_path, error=str(e)))
            return None
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文件内容
        :param file_path: 文件路径
        :param content: 要写入的内容
        :param encoding: 文件编码
        :return: 成功返回True，失败返回False
        """
        try:
            path = Path(file_path)
            
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
                
            print(t("file_content_updated"))
            return True
        except PermissionError:
            print(t("permission_denied", path=file_path))
            return False
        except Exception as e:
            print(t("write_failed", path=file_path, error=str(e)))
            return False
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """
        复制文件
        :param src_path: 源文件路径
        :param dst_path: 目标文件路径
        :return: 成功返回True，失败返回False
        """
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            if not src.exists():
                print(t("file_not_found", file_path=src_path))
                return False
                
            if not src.is_file():
                print(t("operation_failed", error=t("file_not_found", file_path=src_path)))
                return False
            
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            print(t("file_copied", src=src_path, dst=dst_path))
            return True
        except Exception as e:
            print(t("copy_failed", src=src_path, dst=dst_path, error=str(e)))
            return False
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """
        移动文件
        :param src_path: 源文件路径
        :param dst_path: 目标文件路径
        :return: 成功返回True，失败返回False
        """
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            if not src.exists():
                print(t("file_not_found", file_path=src_path))
                return False
                
            if not src.is_file():
                print(t("operation_failed", error=t("file_not_found", file_path=src_path)))
                return False
            
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(src_path, dst_path)
            print(t("file_moved", src=src_path, dst=dst_path))
            return True
        except Exception as e:
            print(t("move_failed", src=src_path, dst=dst_path, error=str(e)))
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        :param file_path: 文件路径
        :return: 成功返回True，失败返回False
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                print(t("file_not_found", file_path=file_path))
                return False
                
            if not path.is_file():
                print(t("operation_failed", error=t("file_not_found", file_path=file_path)))
                return False
            
            path.unlink()
            print(t("file_deleted", path=file_path))
            return True
        except PermissionError:
            print(t("permission_denied", path=file_path))
            return False
        except Exception as e:
            print(t("delete_failed", path=file_path, error=str(e)))
            return False
    
    def create_directory(self, dir_path: str) -> bool:
        """
        创建目录
        :param dir_path: 目录路径
        :return: 成功返回True，失败返回False
        """
        try:
            path = Path(dir_path)
            
            if path.exists():
                print(t("directory_already_exists", dir_path=dir_path))
                return False
            
            path.mkdir(parents=True)
            print(t("directory_created", path=dir_path))
            return True
        except PermissionError:
            print(t("permission_denied", path=dir_path))
            return False
        except Exception as e:
            print(t("create_failed", path=dir_path, error=str(e)))
            return False
    
    def list_directory(self, dir_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        列出目录内容
        :param dir_path: 目录路径
        :return: 目录内容列表，失败返回None
        """
        try:
            path = Path(dir_path)
            
            if not path.exists():
                print(t("directory_not_found", dir_path=dir_path))
                return None
            
            if not path.is_dir():
                print(t("operation_failed", error=t("directory_not_found", dir_path=dir_path)))
                return None
            
            items = []
            for item in path.iterdir():
                item_stat = item.stat()
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'is_file': item.is_file(),
                    'is_dir': item.is_dir(),
                    'size': item_stat.st_size,
                    'modified': item_stat.st_mtime
                })
            
            print(t("directory_listed"))
            return items
        except PermissionError:
            print(t("permission_denied", path=dir_path))
            return None
        except Exception as e:
            print(t("list_failed", path=dir_path, error=str(e)))
            return None
    
    def search_files(self, dir_path: str, pattern: str) -> List[str]:
        """
        在目录中搜索匹配特定模式的文件
        :param dir_path: 搜索的目录路径
        :param pattern: 文件名匹配模式
        :return: 匹配的文件路径列表
        """
        try:
            path = Path(dir_path)
            
            if not path.exists() or not path.is_dir():
                print(t("directory_not_found", dir_path=dir_path))
                return []
            
            print(t("searching_in_directory", dir_path=dir_path))
            
            matches = []
            for file_path in path.rglob(pattern):
                if file_path.is_file():
                    matches.append(str(file_path))
            
            print(t("search_complete", count=len(matches)))
            return matches
        except Exception as e:
            print(t("search_error", error=str(e)))
            return []

# 使用示例
if __name__ == "__main__":
    # 创建文件操作实例
    file_ops = FileOperations()
    
    # 测试读取文件
    content = file_ops.read_file("test.txt")
    if content:
        print(f"{t('file_content_read')}: {content}")
    
    # 测试写入文件
    success = file_ops.write_file("test_output.txt", t("test_file_content"), encoding='utf-8')
    if success:
        print(t("file_write_success"))
    
    # 测试列出目录
    items = file_ops.list_directory(".")
    if items:
        for item in items:
            item_type = t('file_type', name=item['name']) if item['is_file'] else t('directory_type', name=item['name'])
            print(f"{item_type}, {t('file_size_too_large', size=item['size'])}")