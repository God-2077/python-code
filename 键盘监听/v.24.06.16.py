from datetime import datetime
import keyboard
from configparser import ConfigParser, NoSectionError, NoOptionError
import signal
import sys
import os
import time

# 初始化设置
current_script_path = os.path.abspath(__file__)
current_working_directory = os.getcwd()
timestamp = int(time.time())
wait_sequence, wait_time, exit_sequence, keynumber = '654321', 300, 'qqqwe', 6
starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

print(f"-----------------------------------------------------\nstart in {starttime}\n脚本的路径: {current_script_path}\n工作目录的路径: {current_working_directory}")

# 读取配置文件
conf = ConfigParser()
config_path = os.path.join(os.path.dirname(current_script_path), 'config.ini')

try:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    print(f"配置文件路径: {config_path}")
    conf.read(config_path, encoding='utf-8')
    if 'config' not in conf:
        raise NoSectionError('config')

    keypath = conf.get('config', 'file', fallback='Keyboard.txt')
    wait_sequence = conf.get('config', 'wait', fallback='654321')
    wait_time = conf.getint('config', 'waittime', fallback=300)
    exit_sequence = conf.get('config', 'exit', fallback='qqqwe')
    keynumber = conf.get('config', 'keynumber', fallback=6)

except (FileNotFoundError, NoSectionError, NoOptionError) as e:
    print(f"错误: {e}")
    keypath = os.path.join(os.path.dirname(current_script_path), 'Keyboard.txt')

# 初始化键盘记录文件
with open(keypath, 'a', encoding='utf-8') as f:
    f.write(f"-----------------------------------------------------\nstart in {starttime}\n脚本的路径: {current_script_path}\n工作目录的路径: {current_working_directory}\n键盘记录文件路径: {keypath}\n")

input_buffer, input_buffertwo, number_buffer = [], [], []

# 键盘按键事件处理函数
def on_key(event):
    global timestamp
    input_buffertwo.append(event.name)
    if len(input_buffertwo) > len(exit_sequence):
        input_buffertwo.pop(0)
    if ''.join(input_buffertwo) == exit_sequence:
        log_exit_sequence()
    
    input_buffer.append(event.name)
    if len(input_buffer) > len(wait_sequence):
        input_buffer.pop(0)
    if ''.join(input_buffer) == wait_sequence:
        log_wait_sequence()

    if int(time.time()) > timestamp:
        log_key(event.name)
        detect_continuous_numbers(event.name)

# 记录退出序列的函数
def log_exit_sequence():
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{localtime}: 检测到输入序列 {exit_sequence}，exiting...")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime}: 检测到输入序列 {exit_sequence}，exiting...\n")
    sys.exit(0)

# 记录等待序列的函数
def log_wait_sequence():
    global timestamp
    timestamp = int(time.time()) + wait_time
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{localtime}: 检测到输入序列 {wait_sequence}，暂停 {wait_time} 秒")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime}: 检测到输入序列 {wait_sequence}，暂停 {wait_time} 秒\n")
    for i in range(wait_time, 0, -1):
        print(f"\r等待 {i} 秒！", end="", flush=True)
        time.sleep(1)
    print()

# 记录按键的函数
def log_key(key_name):
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{localtime} : {key_name}")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime} : {key_name}\n")

# 检测连续数字的函数
def detect_continuous_numbers(key_name):
    global keynumber
    if key_name.isdigit():
        number_buffer.append(key_name)
        if len(number_buffer) > keynumber:
            number_buffer.pop(0)
        if len(number_buffer) == keynumber:
            log_continuous_numbers()
    else:
        number_buffer.clear()

# 记录连续数字的函数
def log_continuous_numbers():
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{localtime} : number")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime} : number\n")
    number_buffer.clear()

# 信号处理函数，捕捉Ctrl+C
def signal_handler(sig, frame):
    exittime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{exittime}: 检测到Ctrl+C, exiting...")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{exittime}: 检测到Ctrl+C, exiting...\n")
    sys.exit(0)

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)
# 监听键盘按键事件
keyboard.on_press(on_key)
# 等待键盘事件
keyboard.wait()