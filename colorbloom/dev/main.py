# -*- coding: utf-8 -*-
import random
import tkinter as tk
from until import create_window, improved_poisson_disk_sampling
import time

def calculate_window_count(screen_width, screen_height, window_width, window_height, offest=12):
    """
    根据屏幕分辨率自动计算合适的窗口数量
    """
    # c_x = screen_width // max((window_width - 5) // 2, window_width // 2)
    # c_y = screen_height // max((window_height - 5) // 2, window_height // 2)
    c_x = screen_width // (window_width + offest)
    c_y = screen_height // (window_height + offest)
    return c_x * c_y

# def draw_positions(positions, screen_width, screen_height, window_width, window_height):
#     """
#     绘制窗口位置
#     """
#     try:
#         import matplotlib.pyplot as plt

#         # 绘制采样点
#         plt.scatter([p[0] for p in positions], [p[1] for p in positions], s=10)
#         plt.title(f'Poisson Disk Sampling ({len(positions)} points)')
#         plt.xlabel('X')
#         plt.ylabel('Y')
#         plt.xlim(0, screen_width)
#         plt.ylim(0, screen_height)
#         plt.gca().set_aspect('equal', adjustable='box')
#         plt.show()
#     except ImportError:
#         print("警告：matplotlib 未安装，无法可视化结果")


if __name__ == '__main__':
    print("开始创建多个窗口...")

    theme = [{'bg': '#34dbcb','fg': '#ffffff',},{'bg': '#34c2db','fg': '#ffffff',},{'bg': '#f8c291','fg': '#3d3d3d',},{'bg': '#a55eea','fg': '#ffffff',},{'bg': '#20bf6b','fg': '#ffffff',},{'bg': '#f7b731','fg': '#3d3d3d',},{'bg': '#eb4d4b','fg': '#ffffff',},{'bg': '#6ab04c','fg': '#ffffff',},{'bg': '#dff9fb','fg': '#2c3e50',},{'bg': '#2c3e50','fg': '#ecf0f1',},{'bg': '#ff9ff3','fg': '#574b90',},{'bg': '#48dbfb','fg': '#1e272e',}]

    message = ['Hello, World!', '你好，世界！', 'Bonjour, le monde！', 'Hola, Mundo！', 'Ciao, mondo！', 'Privet, mir！', 'Guten Tag, Welt！', 'Cześć, świecie！', 'Hallo, Welt！', 'Olá, Mundo！', 'Merhaba, Dünya！', 'Sveiki, pasauli！']

    # 窗口大小
    window_width = 208
    window_height = 62

    # 获取当前屏幕分辨率
    root = tk.Tk()
    screen_width = root.winfo_screenwidth() - 28 - window_width
    screen_height = root.winfo_screenheight() - 80 - window_height # 减去任务栏高度和窗口高度
    root.destroy()

    
    # 生成均匀分布的随机位置
    num_windows = calculate_window_count(screen_width, screen_height, window_width, window_height, offest=-12)
    positions = improved_poisson_disk_sampling(0, screen_width, 0, screen_height, num_windows)

    # 可视化结果
    print(f"num_windows: {num_windows}")
    print(f"screen_width: {screen_width}, screen_height: {screen_height}")
    print(f"window_width: {window_width}, window_height: {window_height}")
    print(f"positions len: {len(positions)}")
    print(f"num_windows args: {screen_width}, {screen_height}, {window_width}, {window_height}")
    print(f"poisson_disk_sampling args: {0}, {screen_width}, {0}, {screen_height}, {num_windows}")
    # draw_positions(positions, screen_width, screen_height, window_width, window_height)
    
    # 随机打乱位置
    random.shuffle(positions)
    
    for i, (x, y) in enumerate(positions):

        time.sleep(0.01)

        # 随机选择一个主题
        theme_index = random.randint(0, len(theme) - 1)
        bg_color = theme[theme_index]['bg']
        fg_color = theme[theme_index]['fg']

        # 随机选择一条消息
        message_index = random.randint(0, len(message) - 1)
        message_text = message[message_index]
        
        create_window(
            title=f'ColorBloom',
            message=message_text,
            position={'x': int(x), 'y': int(y)},
            size={'width': window_width, 'height': window_height},
            background=bg_color,
            foreground=fg_color,
            font=('Arial', 18),
            borderless=True
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