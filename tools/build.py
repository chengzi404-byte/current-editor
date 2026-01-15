#!/usr/bin/env python3
"""
Current Editor 构建脚本
使用 PyInstaller 将程序打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('build_script')

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
logger.info(f"项目根目录: {PROJECT_ROOT}")

# 构建输出目录
BUILD_DIR = PROJECT_ROOT / "dist"
BUILD_CACHE_DIR = PROJECT_ROOT / "build"
logger.info(f"构建输出目录: {BUILD_DIR}")
logger.info(f"构建缓存目录: {BUILD_CACHE_DIR}")

# 入口文件
ENTRY_FILE = PROJECT_ROOT / "app.py"
logger.info(f"入口文件: {ENTRY_FILE}")

# 需要包含的资源目录和文件
RESOURCE_DIRS = [
    (PROJECT_ROOT / "library", "library"),
    (PROJECT_ROOT / "ui", "ui"),
    (PROJECT_ROOT / "operations", "operations"),
    (PROJECT_ROOT / "lang", "lang"),
    (PROJECT_ROOT / "asset", "asset"),
]

RESOURCE_FILES = [
    (PROJECT_ROOT / "i18n.py", "i18n.py"),
]

# PyInstaller 配置
PYINSTALLER_CONFIG = {
    "name": "CurrentEditor",
    "onefile": False,  # 生成目录而不是单个文件，便于调试和资源管理
    "windowed": True,  # 不显示控制台窗口
    "icon": None,  # 可以添加图标文件路径，例如 "asset/icons/python.ico"
    "clean": True,  # 清理构建缓存
    "noconfirm": True,  # 不确认覆盖输出目录
    "add_data": [],  # 动态添加数据文件
    "add_binary": [],  # 添加二进制文件
    "hidden_imports": [
        "i18n",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "pathlib",
        "json",
        "os",
        "sys",
        "platform",
        "subprocess",
        "logging",
        "datetime",
        "traceback",
    ]
}

def prepare_build():
    """准备构建环境"""
    logger.info("开始准备构建环境")
    
    # 检查 PyInstaller 是否安装
    try:
        subprocess.run(["pyinstaller", "--version"], 
                      capture_output=True, check=True)
        logger.info("PyInstaller 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("PyInstaller 未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True)
            logger.info("PyInstaller 安装成功")
        except subprocess.CalledProcessError:
            logger.error("PyInstaller 安装失败，请手动安装")
            sys.exit(1)
    
    # 清理之前的构建文件
    if BUILD_DIR.exists():
        logger.info(f"清理之前的构建输出目录: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)
    
    if BUILD_CACHE_DIR.exists():
        logger.info(f"清理构建缓存目录: {BUILD_CACHE_DIR}")
        shutil.rmtree(BUILD_CACHE_DIR)
    
    # 准备资源文件
    prepare_resources()
    
    logger.info("构建环境准备完成")

def prepare_resources():
    """准备资源文件列表"""
    logger.info("准备资源文件列表")
    
    # 添加目录资源
    for src_dir, dst_dir in RESOURCE_DIRS:
        if src_dir.exists():
            # 使用 PyInstaller 的格式: "src;dst"
            data_path = f"{src_dir};{dst_dir}"
            PYINSTALLER_CONFIG["add_data"].append(data_path)
            logger.info(f"添加资源目录: {data_path}")
        else:
            logger.warning(f"资源目录不存在: {src_dir}")
    
    # 添加文件资源
    for src_file, dst_file in RESOURCE_FILES:
        if src_file.exists():
            data_path = f"{src_file};{dst_file}"
            PYINSTALLER_CONFIG["add_data"].append(data_path)
            logger.info(f"添加资源文件: {data_path}")
        else:
            logger.warning(f"资源文件不存在: {src_file}")

def build_with_pyinstaller():
    """使用 PyInstaller 构建程序"""
    logger.info("开始使用 PyInstaller 构建程序")
    
    # 构建 PyInstaller 命令
    cmd = [
        "pyinstaller"
    ]
    
    # 基本配置
    cmd.append(f"--name={PYINSTALLER_CONFIG['name']}")
    
    if PYINSTALLER_CONFIG["onefile"]:
        cmd.append("--onefile")
    
    if PYINSTALLER_CONFIG["windowed"]:
        cmd.append("--windowed")
    
    if PYINSTALLER_CONFIG["icon"]:
        cmd.append(f"--icon={PYINSTALLER_CONFIG['icon']}")
    
    if PYINSTALLER_CONFIG["clean"]:
        cmd.append("--clean")
    
    if PYINSTALLER_CONFIG["noconfirm"]:
        cmd.append("--noconfirm")
    
    # 添加数据文件
    for data in PYINSTALLER_CONFIG["add_data"]:
        cmd.append(f"--add-data={data}")
    
    # 添加二进制文件
    for binary in PYINSTALLER_CONFIG["add_binary"]:
        cmd.append(f"--add-binary={binary}")
    
    # 添加隐藏导入
    for hidden_import in PYINSTALLER_CONFIG["hidden_imports"]:
        cmd.append(f"--hidden-import={hidden_import}")
    
    # 添加入口文件
    cmd.append(str(ENTRY_FILE))
    
    logger.info(f"执行 PyInstaller 命令: {' '.join(cmd)}")
    
    # 执行构建命令
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        logger.info("PyInstaller 构建成功")
        logger.debug(f"PyInstaller 输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"PyInstaller 构建失败，退出码: {e.returncode}")
        logger.error(f"错误输出: {e.stderr}")
        return False

def post_build():
    """构建后处理"""
    logger.info("开始构建后处理")
    
    # 检查构建结果
    build_output = BUILD_DIR / PYINSTALLER_CONFIG["name"]
    if build_output.exists():
        logger.info(f"构建输出目录: {build_output}")
        
        # 验证关键文件是否存在
        exe_file = build_output / f"{PYINSTALLER_CONFIG['name']}.exe"
        if exe_file.exists():
            logger.info(f"可执行文件生成成功: {exe_file}")
            return True
        else:
            logger.error(f"可执行文件生成失败: {exe_file}")
            return False
    else:
        logger.error(f"构建输出目录不存在: {build_output}")
        return False

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info(f"Current Editor 构建脚本 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 准备构建
        prepare_build()
        
        # 执行构建
        if build_with_pyinstaller():
            # 构建后处理
            if post_build():
                logger.info("=" * 60)
                logger.info("✅ 构建成功！")
                logger.info(f"可执行文件位置: {BUILD_DIR / PYINSTALLER_CONFIG['name']}")
                logger.info("请查看 build.log 获取完整构建日志")
                logger.info("=" * 60)
                return 0
            else:
                logger.error("❌ 构建后处理失败")
        else:
            logger.error("❌ PyInstaller 构建失败")
            
    except Exception as e:
        logger.error(f"❌ 构建过程中发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("=" * 60)
    logger.info("❌ 构建失败！")
    logger.info("请查看 build.log 获取详细错误信息")
    logger.info("=" * 60)
    return 1

if __name__ == "__main__":
    sys.exit(main())
