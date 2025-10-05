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
    # title 黄色
    title = f"\033[93m{title}\033[0m"
    print("\n" + title.center(width, char) + "\n")

def is_admin():
    """
    检查当前程序是否以管理员/root权限运行
    返回: bool -  True表示具有管理员权限，False表示没有
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows系统通过ctypes调用Windows API检查
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        
        elif system in ["Linux", "Darwin"]:  # Linux和macOS
            # Unix类系统检查有效用户ID是否为0（root）
            return os.geteuid() == 0
        
        else:
            # 其他未知系统
            raise NotImplementedError(f"不支持的操作系统: {system}")
    
    except Exception as e:
        print(f"权限检查出错: {str(e)}")
        return False

sys.stderr.reconfigure(encoding='utf-8')

center_title("Hello World!", width=50, char='=')

# 显示Python信息
center_title("Python 运行信息")
print("Python版本:", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print("Python编译信息:", sys.version)
print("Python路径:", sys.executable)
print("Python实现:", platform.python_implementation())
print("工作目录:", os.getcwd())
print("系统编码:", sys.getdefaultencoding())
print("文件系统编码:", sys.getfilesystemencoding())
print("是否作为主程序运行:", "True" if __name__ == "__main__" else "False")
print("Python 库路径:", sys.path)
print("管理员权限:", is_admin())
print("命令行参数:", sys.argv)
print("程序名称:", os.path.basename(sys.argv[0]))
print("当前执行的Python文件名:", os.path.basename(sys.argv[0]))
print("进程PID:", os.getpid())
print("进程名称:", psutil.Process(os.getpid()).name())
print("父进程PID:", os.getppid())
print("父进程名称:", psutil.Process(os.getppid()).name())

# 显示系统信息
center_title("系统信息")
print("操作系统:", platform.system())
print("主机名:", platform.node())
print("用户名:", os.getlogin())
print("架构:", platform.machine())
print("版本:", platform.version())
print("平台:", platform.platform())
print("环境变量:", os.environ)
print("开机时间:", datetime.datetime.fromtimestamp(psutil.boot_time()))

# 显示时间信息
center_title("时间信息")
print(f"当前时间(本地): {datetime.datetime.now(datetime.datetime.now().astimezone().tzinfo)}")
print(f"当前时间(UTC): {datetime.datetime.now(datetime.UTC)}")
print(f"当前时区: {datetime.datetime.now().astimezone().tzinfo}")

# 网络信息
center_title("网络信息")

# 获取本机所有 IP 地址
hostname = socket.gethostname()
ip_list = []
# 获取IP地址信息
addr_infos = socket.getaddrinfo(hostname, None)
for addr in addr_infos:
    ip_list.append(addr[4][0])
ip_list = list(set(ip_list))  # 去重

# 获取外网 IP 地址，使用 标准库 +  https://myip.ipip.net/json 接口 path data.ip 字段
remote_ip = None
location = None
try:
    with urllib.request.urlopen("https://myip.ipip.net/json") as response:
        data = json.loads(response.read().decode())
        remote_ip = data.get("data", {}).get("ip", "获取失败")
        location_raw = data.get("data", {}).get("location", ["未知位置"])
        # 去除空字符串
        location_raw = [loc.strip() for loc in location_raw if loc.strip()]
        location = ",".join(location_raw)
except (urllib.request.URLError, json.JSONDecodeError) as e:
    remote_ip = f"获取失败: {e}"
    location = "未知位置"


print("主机名:", hostname)
print("IP 地址:", ip_list)
print("外部IP地址:", remote_ip)
print("位置:", location)



# 显示硬件信息
center_title("CPU 信息")
print(f"CPU 核心数: {psutil.cpu_count(logical=False)}")
print(f"逻辑处理器数: {psutil.cpu_count(logical=True)}")
print("处理器信息:", platform.processor())
cpu_times = psutil.cpu_times()
print(f"用户时间: {cpu_times.user}")
print(f"系统时间: {cpu_times.system}")
print(f"空闲时间: {cpu_times.idle}")

memory_info = psutil.virtual_memory()

center_title("内存 信息")
print(f"总内存: {memory_info.total / (1024 ** 3)} GB")
print(f"空闲内存: {memory_info.free / (1024 ** 3)} GB")
print(f"已用内存: {memory_info.used / (1024 ** 3)} GB")
print(f"可用内存: {memory_info.available / (1024 ** 3)} GB")

# 获取内存详细信息
center_title("交换内存 信息")
swap_memory = psutil.swap_memory()
print(f"交换内存总量: {swap_memory.total / (1024 ** 3)} GB")
print(f"已用交换内存: {swap_memory.used / (1024 ** 3)} GB")
print(f"可用交换内存: {swap_memory.free / (1024 ** 3)} GB")

print('='*50)