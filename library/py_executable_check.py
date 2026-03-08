"""
检查Python环境
"""

import sys
import os

def is_conda_env():
    """
    检查是否在conda环境中
    """

    python_executable = sys.executable

    if 'conda' in python_executable.lower() or 'envs' in python_executable.lower():
        return True

    conda_meta_path = os.path.join(os.path.dirname(python_executable), 'conda-meta')
    if os.path.exists(conda_meta_path) and os.path.isdir(conda_meta_path):
        return True
    
    return False

def is_conda_env2():
    if 'CONDA_PREFIX' in os.environ:
        return True

    if 'CONDA_DEFAULT_ENV' in os.environ:
        return True

    return False

def is_conda():
    if is_conda_env() and not is_conda_env2():
        return False

    if is_conda_env2() and is_conda_env():
        return True

    return False    # 缺省情况，不是conda环境
    