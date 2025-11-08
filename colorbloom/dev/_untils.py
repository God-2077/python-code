# -*- coding: utf-8 -*-
import tkinter as tk
import threading
import numpy as np
import math
from collections import deque
import tkinter as tk

def singleMessagePopup(title='', message='', position={'x':500, 'y':500}, size={'width':208, 'height':62}, background='#CC7B00', foreground='#158A8E', font=('Helvetica', 18), borderless=True, topItem=False):
    """
    创建一个单独的消息弹窗，不阻碍主程序运行
    
    参数:
        title (str): 窗口标题
        message (str): 窗口显示的消息
        position (dict): 窗口位置，{'x': 窗口横坐标, 'y': 窗口纵坐标}
        size (dict): 窗口大小，{'width': 窗口宽度, 'height': 窗口高度}
        background (str): 窗口背景颜色，默认 #CC7B00
        foreground (str): 窗口前景颜色，默认 #158A8E
        font (tuple): 窗口字体，默认 Arial 18
        borderless (bool): 是否隐藏窗口边框，默认 True
        topItem (bool): 是否置顶窗口，默认 False
    
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

        # 设置窗口置顶
        if topItem:
            window.wm_attributes("-topmost", True)
        
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


def improved_poisson_disk_sampling(x_min, x_max, y_min, y_max, num_points, k=30, radius=None, max_iterations=10000):
    """
    改进的泊松盘采样算法，减少边缘空白问题
    
    参数:
        x_min, x_max: x轴范围
        y_min, y_max: y轴范围
        num_points: 目标采样点数
        k: 每个活跃点的最大尝试次数
        radius: 点之间的最小距离（如未指定则自动计算）
        max_iterations: 最大迭代次数，防止无限循环
    
    返回:
        points: 采样点坐标列表 [(x1, y1), (x2, y2), ...]
    """
    
    # 自动计算合适的半径
    if radius is None:
        area = (x_max - x_min) * (y_max - y_min)
        radius = math.sqrt(area / (num_points * 1.5))  # 调整系数以减少边缘空白
    
    # 初始化网格
    cell_size = radius / math.sqrt(2)
    grid_width = int((x_max - x_min) / cell_size) + 1
    grid_height = int((y_max - y_min) / cell_size) + 1
    grid = np.full((grid_width, grid_height), -1, dtype=int)  # 存储点的索引
    
    # 点列表
    points = []
    active_list = deque()
    
    def grid_coords(point):
        """
        将点坐标转换为网格坐标
        
        返回:
            网格坐标 (i, j)
        """
        x, y = point
        i = int((x - x_min) / cell_size)
        j = int((y - y_min) / cell_size)
        return max(0, min(grid_width-1, i)), max(0, min(grid_height-1, j))
    
    def is_valid_point(point):
        """
        检查新点是否有效（不与现有点冲突）
        
        返回:
            布尔值，表示点是否有效
        """
        x, y = point
        
        # 检查是否在边界内
        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            return False
        
        # 检查邻近网格
        i, j = grid_coords(point)
        
        # 检查3x3网格区域
        for di in range(-2, 3):  # 扩大检查范围到5x5网格
            for dj in range(-2, 3):
                ni, nj = i + di, j + dj
                if 0 <= ni < grid_width and 0 <= nj < grid_height:
                    point_idx = grid[ni, nj]
                    if point_idx != -1:
                        px, py = points[point_idx]
                        if math.hypot(x - px, y - py) < radius:
                            return False
        
        return True
    
    # 生成初始点 - 从中心开始，有助于减少边缘空白
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    first_point = (center_x, center_y)
    points.append(first_point)
    i, j = grid_coords(first_point)
    grid[i, j] = 0
    active_list.append(0)
    
    # 主采样循环
    iterations = 0
    while active_list and len(points) < num_points and iterations < max_iterations:
        iterations += 1
        
        # 随机选择一个活跃点
        active_idx = np.random.randint(len(active_list))
        for _ in range(active_idx):
            active_list.rotate(-1)  # 旋转到随机索引
        
        active_point_idx = active_list[0]
        active_point = points[active_point_idx]
        found = False
        
        # 在活跃点周围尝试生成新点
        for attempt in range(k):
            # 在环形区域随机生成点
            angle = np.random.uniform(0, 2 * math.pi)
            
            # 动态调整距离，尝试更远的点以减少边缘空白
            min_dist = radius
            max_dist = 2 * radius * (1 + 0.2 * (len(points) / num_points))  # 随着采样进行增加最大距离
            distance = np.random.uniform(min_dist, max_dist)
            
            new_x = active_point[0] + distance * math.cos(angle)
            new_y = active_point[1] + distance * math.sin(angle)
            new_point = (new_x, new_y)
            
            if is_valid_point(new_point):
                points.append(new_point)
                i, j = grid_coords(new_point)
                grid[i, j] = len(points) - 1
                active_list.append(len(points) - 1)
                found = True
                break
        
        # 如果未能生成新点，移除当前活跃点
        if not found:
            active_list.popleft()
    
    # 如果点数不足，尝试在空白区域添加点
    if len(points) < num_points:
        additional_points = _fill_empty_areas(x_min, x_max, y_min, y_max, points, 
                                             num_points - len(points), radius)
        points.extend(additional_points)
    
    return points[:num_points]

def _fill_empty_areas(x_min, x_max, y_min, y_max, existing_points, num_additional, radius):
    """
    在空白区域添加点以减少边缘空白
    
    参数:
        x_min, x_max: x轴范围
        y_min, y_max: y轴范围
        existing_points: 现有坐标点列表
        num_additional: 需要添加的额外点数
        radius: 点之间的最小距离
    
    返回:
        additional_points: 额外添加的坐标点列表
    """
    additional_points = []
    attempts = 0
    max_attempts = num_additional * 10  # 最大尝试次数
    
    # 优先在边界附近添加点
    border_width = (x_max - x_min) * 0.1  # 边界区域宽度
    
    while len(additional_points) < num_additional and attempts < max_attempts:
        attempts += 1
        
        # 优先在边界区域采样
        if np.random.random() < 0.7:  # 70%的概率在边界区域采样
            # 选择边界区域
            border_side = np.random.randint(4)
            if border_side == 0:  # 上边界
                x = np.random.uniform(x_min, x_max)
                y = np.random.uniform(y_max - border_width, y_max)
            elif border_side == 1:  # 下边界
                x = np.random.uniform(x_min, x_max)
                y = np.random.uniform(y_min, y_min + border_width)
            elif border_side == 2:  # 左边界
                x = np.random.uniform(x_min, x_min + border_width)
                y = np.random.uniform(y_min, y_max)
            else:  # 右边界
                x = np.random.uniform(x_max - border_width, x_max)
                y = np.random.uniform(y_min, y_max)
        else:
            # 在内部区域采样
            x = np.random.uniform(x_min, x_max)
            y = np.random.uniform(y_min, y_max)
        
        new_point = (x, y)
        
        # 检查点是否有效
        valid = True
        for point in existing_points + additional_points:
            if math.hypot(x - point[0], y - point[1]) < radius:
                valid = False
                break
        
        if valid:
            additional_points.append(new_point)
    
    return additional_points