import requests
import time
import os
import subprocess
import platform


def measure_latency(url, timeout=3):
    """
    测量指定URL的延迟
    :param url: 要测量的URL
    :param timeout: 超时时间
    :return: 延迟时间（毫秒），如果失败则返回一个大值
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # 转换为毫秒
        return latency
    except Exception as e:
        return float('inf')  # 失败时返回无穷大


def get_fastest_python_source():
    """
    比较阿里云源和官方源的延迟，选择更快的安装来源
    :return: 更快的源URL
    """
    sources = {
        "官方源": "https://www.python.org",
        "阿里云源": "https://mirrors.aliyun.com/python"
    }
    
    print("正在测试Python源延迟...")
    
    # 测试每个源的延迟
    results = {}
    for name, url in sources.items():
        latency = measure_latency(url)
        results[name] = latency
        print(f"{name}延迟: {latency:.2f}ms")
    
    # 选择延迟最低的源
    fastest_name = min(results, key=results.get)
    fastest_url = sources[fastest_name]
    
    print(f"\n选择最快的源: {fastest_name} ({fastest_url})")
    
    return fastest_name, fastest_url


def download_python_environment():
    """
    自动下载Python环境
    """
    print("开始自动下载Python环境...")
    
    # 获取最快的源
    fastest_name, fastest_url = get_fastest_python_source()
    
    # 根据操作系统下载合适的Python版本
    os_type = platform.system()
    
    # 定义Python版本（可根据需要调整）
    python_version = "3.11.4"
    
    if os_type == "Windows":
        # Windows下载逻辑
        print("Windows系统检测到")
        
        # 检查是否安装了pyenv-win
        try:
            subprocess.run(["pyenv", "--version"], check=True, capture_output=True)
            print("已安装pyenv-win")
        except:
            # 安装pyenv-win
            print("正在安装pyenv-win...")
            subprocess.run(["powershell", "-Command", "Invoke-WebRequest -UseBasicParsing -Uri https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1 -OutFile install-pyenv-win.ps1; ./install-pyenv-win.ps1"], check=True, shell=True)
            
        # 使用pyenv-win安装Python
        print(f"使用pyenv-win安装Python {python_version}...")
        
        # 设置源（如果是阿里云源）
        if fastest_name == "阿里云源":
            subprocess.run(["pyenv", "config", "set", "pip_mirror", "https://mirrors.aliyun.com/pypi/simple/"], check=True)
        
        subprocess.run(["pyenv", "install", python_version], check=True)
        subprocess.run(["pyenv", "global", python_version], check=True)
        
    elif os_type == "Darwin":
        # macOS下载逻辑
        print("macOS系统检测到")
        
        # 检查是否安装了pyenv
        try:
            subprocess.run(["pyenv", "--version"], check=True, capture_output=True)
            print("已安装pyenv")
        except:
            # 安装pyenv
            print("正在安装pyenv...")
            subprocess.run(["brew", "install", "pyenv"], check=True)
        
        # 使用pyenv安装Python
        print(f"使用pyenv安装Python {python_version}...")
        
        # 设置源（如果是阿里云源）
        if fastest_name == "阿里云源":
            subprocess.run(["echo", "export PIP_MIRROR='https://mirrors.aliyun.com/pypi/simple/'", " >> ~/.bash_profile"], check=True, shell=True)
            subprocess.run(["source", "~/.bash_profile"], check=True, shell=True)
        
        subprocess.run(["pyenv", "install", python_version], check=True)
        subprocess.run(["pyenv", "global", python_version], check=True)
        
    elif os_type == "Linux":
        # Linux下载逻辑
        print("Linux系统检测到")
        
        # 检查是否安装了pyenv
        try:
            subprocess.run(["pyenv", "--version"], check=True, capture_output=True)
            print("已安装pyenv")
        except:
            # 安装pyenv
            print("正在安装pyenv...")
            subprocess.run(["curl", "https://pyenv.run", "|", "bash"], check=True, shell=True)
            
            # 添加到环境变量
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write("\nexport PATH=\"$HOME/.pyenv/bin:$PATH\"\n")
                f.write("eval \"$(pyenv init --path)\"\n")
                f.write("eval \"$(pyenv virtualenv-init -)\"\n")
            
            subprocess.run(["source", "~/.bashrc"], check=True, shell=True)
        
        # 使用pyenv安装Python
        print(f"使用pyenv安装Python {python_version}...")
        
        # 设置源（如果是阿里云源）
        if fastest_name == "阿里云源":
            subprocess.run(["echo", "export PIP_MIRROR='https://mirrors.aliyun.com/pypi/simple/'", " >> ~/.bashrc"], check=True, shell=True)
            subprocess.run(["source", "~/.bashrc"], check=True, shell=True)
        
        subprocess.run(["pyenv", "install", python_version], check=True)
        subprocess.run(["pyenv", "global", python_version], check=True)
        
    else:
        print(f"不支持的操作系统: {os_type}")
        return False
    
    print("Python环境下载完成！")
    return True


def first_startup_operations():
    """
    第一次启动时执行的操作
    """
    print("=== 编辑器第一次启动操作 ===")
    
    # 检查是否已经下载了Python环境
    python_installed = False
    
    try:
        # 检查是否有可用的Python版本
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            python_version = result.stdout.strip()
            print(f"已检测到Python环境: {python_version}")
            python_installed = True
        else:
            # 尝试使用pyenv检查
            try:
                subprocess.run(["pyenv", "versions"], check=True, capture_output=True)
                print("已检测到通过pyenv安装的Python环境")
                python_installed = True
            except:
                pass
    except:
        pass
    
    # 如果未安装，则自动下载Python环境
    if not python_installed:
        print("未检测到Python环境，开始自动下载...")
        download_python_environment()
    else:
        print("Python环境已存在，跳过下载")
    
    print("=== 启动操作完成 ===")


if __name__ == "__main__":
    first_startup_operations()