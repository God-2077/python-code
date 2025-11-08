# -*- coding: utf-8 -*-
import tkinter as tk
import time
from _untils import generate_heart_coordinates, y_inverted, singleMessagePopup
import random

def calculate_window_count(screen_width, screen_height):
    """
    选择合适的窗口数量
    
    参数:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
    
    返回:
        int:  窗口数量
    """
    count = (screen_width + screen_height) // 20
    
    return count

if __name__ == '__main__':
    print("开始创建多个窗口...")

    theme = [
        {'bg': '#34dbcb', 'fg': '#ffffff'},
        {'bg': '#34c2db', 'fg': '#ffffff'},
        {'bg': '#f8c291', 'fg': '#3d3d3d'},
        {'bg': '#a55eea', 'fg': '#ffffff'},
        {'bg': '#20bf6b', 'fg': '#ffffff'},
        {'bg': '#f7b731', 'fg': '#3d3d3d'},
        {'bg': '#eb4d4b', 'fg': '#ffffff'},
        {'bg': '#6ab04c', 'fg': '#ffffff'},
        {'bg': '#dff9fb', 'fg': '#2c3e50'},
        {'bg': '#2c3e50', 'fg': '#ecf0f1'},
        {'bg': '#ff9ff3', 'fg': '#574b90'},
        {'bg': '#48dbfb', 'fg': '#1e272e'}
    ]

    message = [
        'Hello, World!', '你好，世界！', 'Bonjour, le monde！', 
        'Hola, Mundo！', 'Ciao, mondo！', 'Privet, mir！', 
        'Guten Tag, Welt！', 'Cześć, świecie！', 'Hallo, Welt！', 
        'Olá, Mundo！', 'Merhaba, Dünya！', 'Sveiki, pasauli！'
    ]

    # 窗口大小
    window_width = 208
    window_height = 62

    # 获取当前屏幕分辨率
    root = tk.Tk()
    screen_width = root.winfo_screenwidth() - 28 - window_width
    screen_height = root.winfo_screenheight() - 80 - window_height
    root.destroy()

    # 计算屏幕中心点
    center_x = screen_width / 2
    center_y = screen_height / 2

    # 生成心形坐标点
    num_windows = calculate_window_count(screen_width, screen_height)
    heart_points = y_inverted(screen_width, screen_height, generate_heart_coordinates(screen_width, screen_height, num_windows,size=1.4))

    # info
    print(f'屏幕分辨率: {screen_width} x {screen_height}')
    print(f'窗口大小: {window_width} x {window_height}')
    print(f'窗口数量: {num_windows}')

    # 创建窗口
    for i in range(num_windows):

        time.sleep(0.01)

        x, y = heart_points[i]
        
        # 随机选择一个主题
        theme_index = random.randint(0, len(theme) - 1)
        bg_color = theme[theme_index]['bg']
        fg_color = theme[theme_index]['fg']

        # 随机选择一条消息
        message_index = random.randint(0, len(message) - 1)
        message_text = message[message_index]
        
        singleMessagePopup(
            title=f'测试窗口{i+1}',
            message=message_text,
            position={'x': int(x), 'y': int(y)},
            size={'width': window_width, 'height': window_height},
            background=bg_color,
            foreground=fg_color,
            font=('Arial', 18)
        )

    print("输入 'q' 并按回车退出程序...")
    
    # 保持主程序运行
    while True:
        user_input = input().strip().lower()
        if user_input == 'q':
            print("程序退出中...")
            break
        else:
            print("输入 'q' 退出程序")