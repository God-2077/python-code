# -*- coding: utf-8 -*-
import sys
import tkinter as tk
import time
from _untils import generate_heart_coordinates, y_inverted, singleMessagePopup
import random
from gaokao import get_gaokao_info
import os

# 重写print函数
print_original = print
print("PRINT_DISABLED:", 0 if os.environ.get('PRINT_DISABLED') == '1' else 1)
def print(*args, **kwargs):
    """
    重写print函数，可通过环境变量控制打印输出
    当PRINT_DISABLED='1'时禁用打印，其他情况正常打印
    """
    if os.environ.get('PRINT_DISABLED') == '1':
        return
    else:
        print_original(*args, **kwargs)

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

def mainwindow(theme):
    """
    创建主窗口
    """
    
    root = tk.Tk()
    root.title("高考倒计时")

    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight() - 80
    
    window_width = int(0.8 * screen_width)
    window_height = int(0.8 * screen_height)

    # 窗口位置
    window_x = int(screen_width // 2 - window_width // 2)
    window_y = int(screen_height // 2 - window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")  # 设置初始位置和大小
    
    # 窗口置顶
    root.attributes('-topmost', True)

    # 随机选择主题
    theme = random.choice(theme)
    root.configure(bg=theme['bg'])

    message = get_gaokao_info()['status']

    # 创建消息标签
    message_label = tk.Label(
        root, 
        text=message,
        bg=theme['bg'],
        fg=theme['fg'],
        font=('Helvetica', 36),
        wraplength=window_width,  # 自动换行
        justify='center'
    )
    message_label.pack(expand=True, padx=10, pady=10)

    # 按钮
    # 创建关闭按钮
    close_button = tk.Button(
        root,
        text="关闭",
        bg=theme['bg'],
        fg=theme['fg'],
        font=('Helvetica', 24),
        command=root.destroy,
        width=10
    )
    close_button.pack(pady=10)

    # 绑定关闭按钮点击事件到退出函数
    close_button.bind("<Button-1>", lambda e: exit_program())

    # 绑定窗口控件关闭按钮到退出函数
    root.protocol("WM_DELETE_WINDOW", exit_program)
    
    root.mainloop()
def exit_program():
    """
    退出程序
    """
    sys.exit(0)

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
            font=('Arial', 18),
            topItem=True
        )

    print("输入 'q' 并按回车退出程序...")

    # 主窗口
    mainwindow(theme)
    
    # 保持主程序运行
    while True:
        user_input = input().strip().lower()
        if user_input == 'q':
            print("程序退出中...")
            break
        else:
            print("输入 'q' 退出程序")