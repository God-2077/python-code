import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import font as tkfont
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

class AdvancedFontViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter 字体预览")
        self.root.geometry("900x700")
        
        # 获取系统所有字体
        self.all_fonts = sorted(tkfont.families())
        
        # 默认设置
        self.sample_text = """ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789
中文示例文本：你好，世界！
字体效果展示"""
        self.font_size = 12
        self.letter_spacing = 0
        self.line_spacing = 1.0
        self.current_font = "Arial"
        
        # 创建样式对象用于自定义
        self.style = ttkb.Style()
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重，使界面可调整大小
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左侧面板 - 字体列表和设置
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 字体列表标签
        ttk.Label(left_frame, text="字体列表:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 字体搜索框
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(left_frame, textvariable=self.search_var)
        search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        search_entry.bind('<KeyRelease>', self.filter_fonts)
        
        # 字体列表框架
        list_frame = ttk.LabelFrame(left_frame, text="可用字体", padding=5)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建字体列表
        self.font_list = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set, 
            width=25,
            height=15,
            bg="#f8f9fa",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#20c997"
        )
        self.font_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.font_list.yview)
        
        # 填充字体列表
        for font_name in self.all_fonts:
            self.font_list.insert(tk.END, font_name)
        
        # 设置面板
        settings_frame = ttk.LabelFrame(left_frame, text="显示设置", padding="10")
        settings_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # 字体大小设置
        ttk.Label(settings_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.size_var = tk.IntVar(value=self.font_size)
        size_spin = ttk.Spinbox(
            settings_frame, 
            from_=8, 
            to=72, 
            textvariable=self.size_var,
            width=10,
            command=self.update_display
        )
        size_spin.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        size_spin.bind('<KeyRelease>', self.update_display)
        
        # 字间距设置
        ttk.Label(settings_frame, text="字间距:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.letter_spacing_var = tk.IntVar(value=self.letter_spacing)
        letter_spacing_scale = ttk.Scale(
            settings_frame,
            from_=0,
            to=10,
            variable=self.letter_spacing_var,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_display()
        )
        letter_spacing_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 显示字间距数值
        self.letter_spacing_value = ttk.Label(settings_frame, text="0")
        self.letter_spacing_value.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 行间距设置
        ttk.Label(settings_frame, text="行间距:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.line_spacing_var = tk.DoubleVar(value=self.line_spacing)
        line_spacing_scale = ttk.Scale(
            settings_frame,
            from_=0.5,
            to=3.0,
            variable=self.line_spacing_var,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_display()
        )
        line_spacing_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 显示行间距数值
        self.line_spacing_value = ttk.Label(settings_frame, text="1.0")
        self.line_spacing_value.grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 更新数值显示的函数
        def update_letter_spacing_value(*args):
            self.letter_spacing_value.config(text=str(self.letter_spacing_var.get()))
            
        def update_line_spacing_value(*args):
            self.line_spacing_value.config(text=f"{self.line_spacing_var.get():.1f}")
            
        self.letter_spacing_var.trace('w', update_letter_spacing_value)
        self.line_spacing_var.trace('w', update_line_spacing_value)
        
        # 自定义文本按钮
        ttk.Button(
            left_frame, 
            text="自定义示例文本", 
            command=self.customize_text,
            bootstyle=PRIMARY
        ).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 右侧面板 - 示例文本
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 示例文本标签
        ttk.Label(right_frame, text="示例文本预览:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 创建示例文本框框架
        text_frame = ttk.LabelFrame(right_frame, text="字体效果预览", padding=5)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # 创建示例文本框
        self.example_text = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            width=50,
            height=20,
            padx=15,
            pady=15,
            bg="#f8f9fa",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#20c997"
        )
        self.example_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 绑定选择事件
        self.font_list.bind('<<ListboxSelect>>', self.on_font_select)
        
        # 默认选择第一个字体
        if self.all_fonts:
            self.font_list.selection_set(0)
            self.on_font_select(None)
            
        # 更新初始显示
        self.update_display()
    
    def filter_fonts(self, event=None):
        """根据搜索框内容过滤字体列表"""
        search_term = self.search_var.get().lower()
        
        # 清空列表
        self.font_list.delete(0, tk.END)
        
        # 重新填充匹配的字体
        for font_name in self.all_fonts:
            if search_term in font_name.lower():
                self.font_list.insert(tk.END, font_name)
        
        # 如果有匹配项，选择第一个
        if self.font_list.size() > 0:
            self.font_list.selection_clear(0, tk.END)
            self.font_list.selection_set(0)
            self.on_font_select()
    
    def on_font_select(self, event=None):
        """当选择字体时更新显示"""
        # 获取选中的字体
        selection = self.font_list.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < self.font_list.size():
                self.current_font = self.font_list.get(index)
                self.update_display()
    
    def update_display(self, event=None):
        """更新示例文本的显示"""
        # 获取当前设置
        try:
            self.font_size = self.size_var.get()
        except tk.TclError:
            self.font_size = 12  # 默认值
            
        # 清空文本框
        self.example_text.delete(1.0, tk.END)
        
        # 插入示例文本
        self.example_text.insert(1.0, self.sample_text)
        
        # 应用字体
        try:
            # 尝试创建字体对象
            custom_font = tkfont.Font(
                family=self.current_font, 
                size=self.font_size
            )
            self.example_text.config(font=custom_font)
            
            # 应用间距设置
            self.apply_spacing()
            
        except Exception as e:
            # 如果字体不支持，使用默认字体
            self.example_text.config(font=("Arial", self.font_size))
            self.example_text.insert(tk.END, f"\n\n注意：字体 '{self.current_font}' 可能不支持当前字符集: {str(e)}")
    
    def apply_spacing(self):
        """应用字间距和行间距设置（通过文本标签模拟）"""
        # 获取当前间距设置
        letter_spacing = self.letter_spacing_var.get()
        line_spacing = self.line_spacing_var.get()
        
        # 配置文本标签用于间距
        self.example_text.tag_configure("spacing", 
                                      spacing1=int(line_spacing * 2),  # 行前间距
                                      spacing2=int(line_spacing * 2),  # 行间间距
                                      spacing3=int(line_spacing * 2))  # 行后间距
        
        # 将间距标签应用到整个文本
        self.example_text.tag_add("spacing", "1.0", "end")
        
        # 注意：Tkinter的Text组件对字间距的支持有限
        # 这里我们通过插入空格来模拟字间距效果
        if letter_spacing > 0:
            # 获取文本内容
            content = self.example_text.get(1.0, tk.END)
            # 在每个字符后插入空格（简单模拟）
            spaced_content = ""
            for char in content:
                spaced_content += char + " " * letter_spacing
            
            # 清空并重新插入带空格的文本
            self.example_text.delete(1.0, tk.END)
            self.example_text.insert(1.0, spaced_content)
    
    def customize_text(self):
        """打开自定义文本对话框"""
        # 创建新窗口
        text_window = ttkb.Toplevel(self.root)
        text_window.title("自定义示例文本")
        text_window.geometry("500x400")
        text_window.transient(self.root)
        text_window.grab_set()
        
        # 创建框架
        frame = ttk.Frame(text_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_window.columnconfigure(0, weight=1)
        text_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 创建文本编辑框
        text_frame = ttk.LabelFrame(frame, text="编辑示例文本", padding=5)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        text_edit = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=50, height=15)
        text_edit.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_edit.insert(1.0, self.sample_text)
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, sticky=(tk.E, tk.W))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # 确定按钮
        ttk.Button(button_frame, text="确定", bootstyle=SUCCESS,
                  command=lambda: self.save_custom_text(text_edit, text_window)).grid(
            row=0, column=0, sticky=tk.E, padx=(0, 5))
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", bootstyle=SECONDARY,
                  command=text_window.destroy).grid(
            row=0, column=1, sticky=tk.W)
    
    def save_custom_text(self, text_edit, window):
        """保存自定义文本并关闭窗口"""
        self.sample_text = text_edit.get(1.0, tk.END).strip()
        window.destroy()
        self.update_display()

if __name__ == "__main__":
    # 使用ttkbootstrap创建窗口，应用minty主题
    root = ttkb.Window(themename="minty")
    app = AdvancedFontViewer(root)
    root.mainloop()