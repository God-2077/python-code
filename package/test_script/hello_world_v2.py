import platform
import os
import sys
import psutil
import datetime
import socket
import urllib.request
import json
import ctypes

def center_title(title, width=50, char='-'):
    """居中显示标题"""
    title = f"\033[93m{title}\033[0m"
    print("\n" + title.center(width, char) + "\n")

def is_admin():
    """
    检查当前程序是否以管理员/root权限运行
    返回: bool - True表示具有管理员权限，False表示没有
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif system in ["Linux", "Darwin"]:
            return os.geteuid() == 0
        else:
            raise NotImplementedError(f"不支持的操作系统: {system}")
    except Exception as e:
        print(f"权限检查出错: {str(e)}")
        return False

def get_remote_ip_info():
    """获取外网IP和位置信息"""
    try:
        with urllib.request.urlopen("https://myip.ipip.net/json", timeout=10) as response:
            data = json.loads(response.read().decode())
            remote_ip = data.get("data", {}).get("ip", "获取失败")
            location_raw = data.get("data", {}).get("location", ["未知位置"])
            location_raw = [loc.strip() for loc in location_raw if loc.strip()]
            location = ",".join(location_raw)
            return remote_ip, location
    except Exception as e:
        return f"获取失败: {e}", "未知位置"

def main():
    # 设置编码
    sys.stderr.reconfigure(encoding='utf-8')
    
    # 程序标题
    center_title("系统信息收集报告", width=50, char='=')
    
    # 1. 基本信息概览
    center_title("基本信息概览")
    print(f"收集时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"程序名称: {os.path.basename(sys.argv[0])}")
    print(f"运行权限: {'管理员/root权限' if is_admin() else '普通用户权限'}")
    
    # 2. 系统核心信息
    center_title("操作系统信息")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"系统版本: {platform.version()}")
    print(f"平台架构: {platform.platform()}")
    print(f"主机名称: {platform.node()}")
    print(f"当前用户: {os.getlogin()}")
    print(f"系统架构: {platform.machine()}")
    print(f"开机时间: {datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 3. 时间信息
    center_title("时间与时区信息")
    current_time = datetime.datetime.now()
    utc_time = datetime.datetime.now(datetime.UTC)
    print(f"本地时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"UTC时间: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"本地时区: {current_time.astimezone().tzinfo}")
    
    # 4. 硬件资源信息
    center_title("CPU信息")
    print(f"物理核心数: {psutil.cpu_count(logical=False)}")
    print(f"逻辑处理器数: {psutil.cpu_count(logical=True)}")
    print(f"处理器型号: {platform.processor()}")
    
    cpu_times = psutil.cpu_times()
    print(f"用户模式时间: {cpu_times.user:.2f}秒")
    print(f"系统模式时间: {cpu_times.system:.2f}秒")
    print(f"空闲时间: {cpu_times.idle:.2f}秒")
    
    center_title("内存信息")
    memory = psutil.virtual_memory()
    print(f"总内存: {memory.total / (1024**3):.2f} GB")
    print(f"已用内存: {memory.used / (1024**3):.2f} GB")
    print(f"可用内存: {memory.available / (1024**3):.2f} GB")
    print(f"内存使用率: {memory.percent}%")
    
    center_title("交换空间信息")
    swap = psutil.swap_memory()
    print(f"交换空间总量: {swap.total / (1024**3):.2f} GB")
    print(f"已用交换空间: {swap.used / (1024**3):.2f} GB")
    print(f"交换空间使用率: {swap.percent}%")
    
    # 5. 网络信息
    center_title("网络连接信息")
    hostname = socket.gethostname()
    addr_infos = socket.getaddrinfo(hostname, None)
    ip_list = list(set(addr[4][0] for addr in addr_infos))
    
    print(f"主机名: {hostname}")
    print(f"本地IP地址: {', '.join(ip_list)}")
    
    remote_ip, location = get_remote_ip_info()
    print(f"公网IP地址: {remote_ip}")
    print(f"地理位置: {location}")
    
    # 6. Python环境信息
    center_title("Python运行环境")
    print(f"Python版本: {platform.python_version()}")
    print(f"Python实现: {platform.python_implementation()}")
    print(f"Python路径: {sys.executable}")
    print(f"系统默认编码: {sys.getdefaultencoding()}")
    print(f"文件系统编码: {sys.getfilesystemencoding()}")
    
    center_title("程序执行信息")
    print(f"进程PID: {os.getpid()}")
    print(f"进程名称: {psutil.Process(os.getpid()).name()}")
    print(f"父进程PID: {os.getppid()}")
    print(f"工作目录: {os.getcwd()}")
    print(f"命令行参数: {sys.argv}")
    print(f"是否主程序: {'是' if __name__ == '__main__' else '否'}")
    
    # 7. 环境变量（简要显示关键变量）
    center_title("关键环境变量")
    key_vars = ['PATH', 'HOME', 'USER', 'LANG', 'TEMP', 'TMP']
    for var in key_vars:
        if var in os.environ:
            value = os.environ[var]
            # 截断过长的值（如PATH）
            if len(value) > 100:
                value = value[:100] + "..."
            print(f"{var}: {value}")
    
    print('=' * 50)

if __name__ == "__main__":
    main()
