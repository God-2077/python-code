import platform
import os
import sys
import psutil
print('='*50)

# 显示系统信息
print('hello world')
print('-'*50)
print('系统信息')
print("操作系统:", platform.system())
print("架构:", platform.machine())
print("版本:", platform.version())
print("平台:", platform.platform())

# 显示硬件信息
print('-'*50)
print('CPU 信息')
print(f"CPU 核心数: {psutil.cpu_count(logical=False)}")
print(f"逻辑处理器数: {psutil.cpu_count(logical=True)}")
print("处理器信息:", platform.processor())
cpu_times = psutil.cpu_times()
print(f"用户时间: {cpu_times.user}")
print(f"系统时间: {cpu_times.system}")
print(f"空闲时间: {cpu_times.idle}")

memory_info = psutil.virtual_memory()

print('-'*50)
print('内存 信息')
print(f"总内存: {memory_info.total / (1024 ** 3)} GB")
print(f"空闲内存: {memory_info.free / (1024 ** 3)} GB")
print(f"已用内存: {memory_info.used / (1024 ** 3)} GB")
print(f"可用内存: {memory_info.available / (1024 ** 3)} GB")

# 获取内存详细信息
print('-'*50)
print('交换内存 信息')
swap_memory = psutil.swap_memory()
print(f"交换内存总量: {swap_memory.total / (1024 ** 3)} GB")
print(f"已用交换内存: {swap_memory.used / (1024 ** 3)} GB")
print(f"可用交换内存: {swap_memory.free / (1024 ** 3)} GB")

print("系统编码:", sys.getdefaultencoding())
print("文件系统编码:", sys.getfilesystemencoding())



# 显示Python信息
print("Python版本:", sys.version)
print("Python路径:", sys.executable)
print("当前工作目录:", os.getcwd())


print('='*50)
