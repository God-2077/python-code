# -*- coding: utf-8 -*-
import tkinter as tk
import threading
import numpy as np
import math
from collections import deque
import tkinter as tk

def create_window(title='', message='', position={'x':500, 'y':500}, size={'width':208, 'height':62}, background='#CC7B00', foreground='#158A8E', font=('Helvetica', 18), borderless=True):
    """
    创建一个单独的窗口，不阻碍主程序运行
    
    参数:
        title: 窗口标题
        message: 窗口显示的消息
        position: 窗口位置
        size: 窗口大小
        background: 窗口背景颜色，默认 #CC7B00
        foreground: 窗口前景颜色，默认 #158A8E
        font: 窗口字体，默认 Arial 18
        borderless: 是否隐藏窗口边框，默认 True
    
    返回:
        无
    """
    
    def window_thread():
        # 创建窗口
        window = tk.Tk()
        window.title(title)

        # 隐藏窗口边框
        if borderless:
            window.overrideredirect(True)
        
        # 设置窗口位置和大小
        geometry_str = f"{size['width']}x{size['height']}+{position['x']}+{position['y']}"
        window.geometry(geometry_str)
        
        # 设置窗口背景色
        window.configure(bg=background)
        
        # 创建消息标签
        message_label = tk.Label(
            window, 
            text=message,
            bg=background,
            fg=foreground,
            font=font,
            wraplength=size['width'] - 20,  # 自动换行
            justify='center'
        )
        message_label.pack(expand=True, padx=10, pady=10)
        
        # 设置窗口属性
        window.resizable(True, True)
        
        # 运行窗口主循环
        window.mainloop()
    
    # 在新线程中创建窗口
    thread = threading.Thread(target=window_thread)
    thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
    thread.start()




def generate_heart_coordinates(width, height, quantity, size=1.0):
    """
    生成心形图案的坐标点，自动居中在画布上
    
    参数:
        width: 画布宽度
        height: 画布高度
        quantity: 坐标点的数量
        size: 心形大小比例，默认为1.0（原始大小），可调整
    
    返回:
        list: 包含(x, y)坐标的列表
    """
    
    # 确保点的数量合理
    quantity = max(30, min(quantity, 1000))
    
    # 确保size在合理范围内
    size = max(0.1, min(size, 5.0))  # 限制在0.1到5.0之间
    
    coordinates = []
    
    # 计算心形在画布中的合适大小（留出边距）
    margin = 0.1  # 10%的边距
    available_width = width * (1 - 2 * margin)
    available_height = height * (1 - 2 * margin)
    
    # 将size参数应用到缩放计算中
    base_scale = min(available_width / 35, available_height / 35)
    scale = base_scale * size  # 应用size参数
    
    # 画布中心点
    center_x = width / 2
    center_y = height / 2
    
    # 生成心形坐标
    for i in range(quantity):
        # 使用参数t生成均匀分布的点
        t = 2 * math.pi * i / quantity
        
        # 心形曲线的参数方程
        x_coord = 16 * (math.sin(t) ** 3)
        y_coord = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        # 缩放并平移到画布中心
        x_coord = x_coord * scale + center_x
        y_coord = y_coord * scale + center_y
        
        coordinates.append((x_coord, y_coord))
    
    return coordinates

def y_inverted(width, height,coordinates):
    """
    对y坐标进行反转，使心形图案在垂直方向上对称
    
    参数:
        width: 画布宽度
        height: 画布高度
        coordinates: 原始坐标列表
    
    返回:
        list: 反转后的坐标列表
    """
    inverted_coordinates = []
    for x, y in coordinates:
        inverted_y = height - y
        inverted_coordinates.append((x, inverted_y))
    return inverted_coordinates