import platform
import os
import sys
import psutil
import datetime
import socket
import urllib.request
import json
import ctypes
import time
import traceback

start_time = time.time()

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

def format_bytes(size):
    """将字节转换为可读格式"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

# 人性化的时间显示
def format_time(seconds):
    """
    将秒数转换为易读的时间格式（Y年 D天 H小时 M分钟 S秒 MS毫秒）
    只显示非零的时间单位，并按照从大到小的顺序排列
    
    参数:
        seconds (float): 要转换的秒数（可以是小数）
    
    返回:
        str: 格式化后的时间字符串，如 "3M 4S 500MS"
    """
    if seconds < 0:
        return "无效输入"
    # 定义时间常数（以秒计）
    SECONDS_PER_YEAR = 365 * 24 * 3600
    SECONDS_PER_DAY = 24 * 3600
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60
    # 计算整数部分
    years = int(seconds // SECONDS_PER_YEAR)
    remainder = seconds % SECONDS_PER_YEAR
    days = int(remainder // SECONDS_PER_DAY)
    remainder %= SECONDS_PER_DAY
    hours = int(remainder // SECONDS_PER_HOUR)
    remainder %= SECONDS_PER_HOUR
    minutes = int(remainder // SECONDS_PER_MINUTE)
    seconds_remaining = remainder % SECONDS_PER_MINUTE
    seconds_int = int(seconds_remaining)
    milliseconds = int((seconds_remaining - seconds_int) * 1000)
    parts = []
    if years > 0:
        parts.append(f"{years}Y")
    if days > 0:
        parts.append(f"{days}D")
    if hours > 0:
        parts.append(f"{hours}H")
    if minutes > 0:
        parts.append(f"{minutes}M")
    if seconds_int > 0 or (not parts and milliseconds == 0):  # 确保至少显示0S
        parts.append(f"{seconds_int}S")
    if milliseconds > 0:
        parts.append(f"{milliseconds}MS")
    # 处理全零情况
    if not parts:
        return "0S"
    return " ".join(parts)

def get_boot_time():
    """获取系统开机时间"""
    res = {"ok": True, "msg": "success", "boot_time": 0, "runtime": 0}
    # if not is_admin() and platform.system() in ["Linux", "Darwin"]:
    #     # print("警告: 非管理员权限无法获取准确的开机时间")
    #     res["ok"] = False
    #     res["msg"] = "无权限"
    #     res["boot_time"] = 0
    #     res["runtime"] = 0
    #     return res
    
    try:
        boot_time = psutil.boot_time()
        res["boot_time"] = datetime.datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        res["runtime"] = str(datetime.timedelta(seconds=time.time() - boot_time))
        return res
    except PermissionError:
        # print(f"获取开机时间出错: {e}")
        res["ok"] = False
        res["msg"] = "无权限"
        return res

def is_internet_available():
    test_url = ["https://www.bing.com", "https://www.google.com", "https://www.baidu.com"]
    res = {}
    res["status"] = True
    for url in test_url:
        try:
            urllib.request.urlopen(url, timeout=5)
            res[url] = True
        except (urllib.error.URLError, socket.timeout):
            res[url] = False
    if True not in res.values():
        res["status"] = False
    return res

def get_utc_time():
    """获取当前UTC时间"""
    # python < 3.11 时，需要使用 datetime.UTC 而不是 datetime.timezone.utc
    if sys.version_info < (3, 11):
        return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
        

def main():

    # 配置输出编码
    sys.stderr.reconfigure(encoding='utf-8')

    # ======================
    # 系统概览
    # ======================
    center_title("系统概览", width=50, char='=')
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"主机名: {platform.node()}")
    try:
        # 尝试用 os.getlogin() 获取用户名
        print(f"用户名: {os.getlogin()}")
    except (PermissionError, OSError):
        # 捕获权限错误和终端环境错误，使用替代方案
        try:
            # 备选方案：通过环境变量获取用户名
            print(f"用户名: {os.environ.get('USER', os.environ.get('USERNAME', '未知'))}")
        except:
            print(f"用户名: 无法获取")
    print(f"架构: {platform.machine()}")
    print(f"平台: {platform.platform()}")
    boot_time = get_boot_time()
    print(f"开机时间: {boot_time['boot_time'] if boot_time['ok'] else boot_time['msg']}")
    print(f"运行时长: {boot_time['runtime'] if boot_time['ok'] else boot_time['msg']}")
    print(f"管理员权限: {'True' if is_admin() else 'False'}")

    # ======================
    # 时间信息
    # ======================
    center_title("时间信息")
    print(f"当前时间(本地): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前时间(UTC): {get_utc_time()}")
    print(f"当前时区: {time.strftime('%Z')} (UTC{time.strftime('%z')})")

    # ======================
    # 硬件信息
    # ======================
    center_title("CPU 信息")
    print(f"物理核心数: {psutil.cpu_count(logical=False)}")
    print(f"逻辑处理器数: {psutil.cpu_count(logical=True)}")
    print(f"处理器型号: {platform.processor() if platform.processor() != '' else 'Unknown'}")
    try:
        print(f"当前使用率: {psutil.cpu_percent(interval=0.1)}%")
    except PermissionError:
        print(f"当前使用率: N/A %")
    try:
        cpu_freq = psutil.cpu_freq()
        print(f"当前频率: {cpu_freq.current if cpu_freq else 'N/A'} MHz")
        print(f"最大频率: {cpu_freq.max if cpu_freq else 'N/A'} MHz")
    except PermissionError:
        print(f"当前频率: 无权限")
        print(f"最大频率: 无权限")

    center_title("内存信息")
    try:
        mem = psutil.virtual_memory()
        print(f"总内存: {format_bytes(mem.total)}")
        print(f"已用内存: {format_bytes(mem.used)} ({mem.percent}%)")
        print(f"空闲内存: {format_bytes(mem.free)}")
        print(f"可用内存: {format_bytes(mem.available)}")
    except PermissionError:
        print(f"总内存: 无权限")
        print(f"已用内存: 无权限")
        print(f"空闲内存: 无权限")
        print(f"可用内存: 无权限")

    center_title("交换内存")
    try:
        swap = psutil.swap_memory()
        print(f"交换内存总量: {format_bytes(swap.total)}")
        print(f"已用交换内存: {format_bytes(swap.used)} ({swap.percent}%)")
        print(f"可用交换内存: {format_bytes(swap.free)}")
    except PermissionError:
        print(f"交换内存总量: 无权限")
        print(f"已用交换内存: 无权限")
        print(f"可用交换内存: 无权限")

    center_title("磁盘信息")
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            print(f"\n设备: {partition.device}")
            print(f"挂载点: {partition.mountpoint}")
            print(f"文件系统: {partition.fstype}")
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"总空间: {format_bytes(usage.total)}")
                print(f"已用空间: {format_bytes(usage.used)} ({usage.percent}%)")
                print(f"可用空间: {format_bytes(usage.free)}")
            except PermissionError:
                print("无权限")
    except PermissionError:
        print("无权限")

    # ======================
    # 网络信息
    # ======================
    center_title("网络信息")
    try:
        hostname = socket.gethostname()
        print(f"主机名: {hostname}")

        # 获取所有网络接口信息
        net_io = psutil.net_io_counters(pernic=True)
        net_addrs = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()

        for interface, addrs in net_addrs.items():
            print(f"\n{'='*12}\n接口: {interface}")
            
            # 接口状态
            status = "启用" if net_stats[interface].isup else "禁用"
            print(f"状态: {status}")
            
            # IP地址
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"IPv4地址: {addr.address}")
                    print(f"子网掩码: {addr.netmask}")
                elif addr.family == socket.AF_INET6:
                    print(f"IPv6地址: {addr.address}")
            
            # 网络统计
            if interface in net_io:
                io = net_io[interface]
                print(f"发送: {format_bytes(io.bytes_sent)}")
                print(f"接收: {format_bytes(io.bytes_recv)}")
    except PermissionError:
        print("无权限")

    # 获取公网IP
    center_title("公网信息")
    try:
        # 获取本机所有 IP 地址
        hostname = socket.gethostname()
        ip_list = []
        # 获取IP地址信息
        addr_infos = socket.getaddrinfo(hostname, None)
        for addr in addr_infos:
            ip_list.append(addr[4][0])
        ip_list = list(set(ip_list))  # 去重
        print("主机名:", hostname)
        print("IP 地址:", ip_list)
    except PermissionError:
        print("主机名:", 'Unknown')
        print("IP 地址:", 'N/A')
    try:
        # dns 测试
        test_url = ["www.bing.com", "www.google.com", "www.baidu.com"]
        res = {}
        res_status = True
        for url in test_url:
            addrs = socket.getaddrinfo(url, None)
            ips = [addr[4][0] for addr in addrs]
            # 去除 127.0.0.1
            ips = [ip for ip in ips if not ip.startswith("127.")]
            if len(ips) >= 1:
                res[url] = True
            else:
                res[url] = False
        if True not in res.values():
            res_status = False
        print("dns 测试:", res_status)
        for url, status in res.items():
            print(f"{' '*8}{url}: {status}")
    except PermissionError:
        print("dns 测试: 无权限")

    try:
        # 网络连通性

        res = is_internet_available()
        print("网络连通性:", res["status"])
        for url, status in res.items():
            if url != "status":
                print(f"{' '*8}{url}: {status}")
    except PermissionError:
        print("网络连通性: 无权限")

    try:
        try:
            with urllib.request.urlopen("https://myip.ipip.net/json", timeout=5) as response:
                data = json.loads(response.read().decode())
                remote_ip = data.get("data", {}).get("ip", "获取失败")
                location_raw = data.get("data", {}).get("location", ["未知位置"])
                # 去除空字符串
                location_raw = [loc.strip() for loc in location_raw if loc.strip()]
                location = ",".join(location_raw)
                print(f"公网IP地址: {remote_ip}")
                print(f"位置: {location}")
        except Exception as e:
            print(f"获取公网信息失败: {str(e)}")
    except PermissionError:
        print("无权限")

    # ======================
    # Python环境信息
    # ======================
    center_title("Python 环境")
    print(f"Python版本: {platform.python_version()}")
    print(f"Python实现: {platform.python_implementation()}")
    print(f"Python路径: {sys.executable}")
    print(f"Python编译信息: {platform.python_compiler()}")
    print(f"系统编码: {sys.getdefaultencoding()}")
    print(f"文件系统编码: {sys.getfilesystemencoding()}")

    # ======================
    # 进程信息
    # ======================
    center_title("进程信息")
    print(f"程序名称: {os.path.basename(sys.argv[0])}")
    print(f"命令行参数: {sys.argv}")
    print(f"工作目录: {os.getcwd()}")
    print(f"进程PID: {os.getpid()}")
    try:
        print(f"进程名称: {psutil.Process(os.getpid()).name()}")
    except PermissionError:
        print(f"进程名称: 无权限")
    print(f"父进程PID: {os.getppid()}")
    try:
        print(f"父进程名称: {psutil.Process(os.getppid()).name()}")
    except PermissionError:
        print(f"父进程名称: 无权限")
    print(f"是否作为主程序运行: {'是' if __name__ == '__main__' else '否'}")

    # ======================
    # 环境信息
    # ======================
    center_title("环境变量")
    sensitive_keys = ['PASSWORD', 'TOKEN', 'SECRET']
    for key, value in os.environ.items():
        for item in sensitive_keys:
            if item.lower() in key.lower():
                value = '*' * len(value)
                break
        print(f"{key}: {value}")

    # ======================
    # Python路径
    # ======================
    center_title("Python 库路径")
    for path in sys.path:
        print(path)

    # 计算运行时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n程序运行时间: {format_time(elapsed_time)}")

    print('='*50)

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 计算运行时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n程序运行时间: {format_time(elapsed_time)}")

        print('='*50)

        print(f"\n程序运行出错: {e}")
        # 打印异常栈跟踪
        traceback.print_exc()

        print('='*50)

        sys.exit(1)
