import tkinter as tk

# 实时显示窗口的位置和大小

class WindowTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("窗口位置和大小跟踪器")
        self.root.geometry("400x200+100+100")  # 设置初始位置和大小
        
        # 创建显示信息的标签
        self.info_label = tk.Label(
            self.root, 
            text="", 
            font=("Arial", 12),
            justify=tk.LEFT,
            bg="lightgray",
            padx=10,
            pady=10
        )
        self.info_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 绑定窗口移动和大小变化事件
        self.root.bind('<Configure>', self.on_window_change)
        
        # 初始显示信息
        self.update_info()
    
    def on_window_change(self, event):
        """当窗口位置或大小改变时调用"""
        # 只有当事件是主窗口时更新（避免子控件触发）
        if event.widget == self.root:
            self.update_info()
    
    def update_info(self):
        """更新显示窗口位置和大小信息"""
        # 获取窗口位置和大小
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 格式化显示信息
        info_text = f"""窗口位置和大小信息:
        
X坐标: {x} 像素
Y坐标: {y} 像素
宽度: {width} 像素
高度: {height} 像素

几何位置: {self.root.geometry()}

提示: 移动或调整窗口大小，信息会自动更新"""
        
        print('='*40)
        print(info_text)
        
        self.info_label.config(text=info_text)
    
    def run(self):
        """启动应用程序"""
        self.root.mainloop()

# 创建并运行应用程序
if __name__ == "__main__":
    app = WindowTracker()
    app.run()