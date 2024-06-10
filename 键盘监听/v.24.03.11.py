#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/03/11
# @Author  : Kissablecho
# @FileName: Keyboard monitoring.py
# @Software: Visual Studio Code
# @Blog    ：https://blog.csdn.net/y223421

import time
import keyboard
from configparser import ConfigParser
import signal
import sys

# 读取config.ini配置文件
conf = ConfigParser()  # 需要实例化一个ConfigParser对象
conf.read('config.ini',encoding='utf-8') 

# 设置变量
keypath = conf['config']['file']

# 打开文件
f = open(keypath, 'a')

# 开始时间
starttime = time.asctime( time.localtime(time.time()) )
print("-----------------------------------------------------")
print("start in", starttime)
print("-----------------------------------------------------", file=f)
print("start in", starttime, file=f)

# 关闭文件
f.close()

# main
def on_key(event):
    localtime = time.asctime( time.localtime(time.time()) )
    print (localtime, ":", event.name)
    # 打开文件
    f = open(keypath, 'a')
    print (localtime, ":", event.name, file=f)
    # 关闭文件
    f.close()

def signal_handler(sig, frame):
    print("检测到Ctrl+C, exiting...")
    sys.exit(0)
    input()
signal.signal(signal.SIGINT, signal_handler)
keyboard.on_press(on_key)
keyboard.wait()