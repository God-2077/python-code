# -*- coding: utf-8 -*-
import time
import threading
class AnimatedSpinner:
    """
    终端动画指示器/加载器

    Attributes:
        message (str): 指示器/加载器显示的消息
        speed (int): 指示器/加载器的刷新速度，单位：秒/帧
        animation_chars (list): 自定义动画字符列表
        default_chars (str): 默认动画字符集，可选值：'dots'、'simple'、'arrows'、'arrows2'、'spinner'、'bouncing_ball'、'moon'、'earth'、'clock'、'simpledots'、'circlepulse'、'linepulse'、'blockpulse'、'blockfill'、'gradientcircle'、'squares'、'gesture'、'grid'
    Example:
    ```
    with AnimatedSpinner("AnimatedSpinner 示例（5s）", 10) as anim:
        time.sleep(5)
    ```
    """
    def __init__(self, message: str = "", speed: int = 10, animation_chars: list = None, default_chars: str = 'dots'):
        if speed <= 0:
            raise ValueError("速度必须大于0")
        self._lock = threading.RLock()
        self.message = message
        self.speed = 1.0 / speed
        self.is_running = False
        self.thread = None
        AnimationChars = {
            'simple': ['-', '\\', '|', '/'],
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'arrows2': ['⇐', '⇖', '⇑', '⇗', '⇒', '⇘', '⇓', '⇙'],
            'spinner': ['◜', '◠', '◝', '◞', '◑', '◟'],
            'bouncing_ball': ['⠁', '⠂', '⠄', '⠈', '⠐', '⠠', '⠐', '⠈', '⠄', '⠂'],
            'moon': ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
            'earth': ['🌍', '🌎', '🌏'],
            'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],    
            'simpledots': ['.', '..', '...', '....'],
            'circlepulse': ['○', '◎', '●', '◎'],
            'linepulse': ['-', '=', '≡', '='],
            'blockpulse': ['█', '▓', '▒', '░'],
            'blockfill': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'],
            'gradientcircle': ['◐', '◓', '◑', '◒'],
            'squares': ['◰', '◳', '◲', '◱'],
            'gesture': ['👆', '👉', '👇', '👈'],
            'grid': ['▖', '▘', '▝', '▗']
        }
        if animation_chars:
            if type(animation_chars) is not list: raise ValueError("自定义动画字符列表必须是列表类型")
            if len(animation_chars) < 2: raise ValueError("自定义动画字符列表必须包含至少2个字符")
            self.animation_chars = animation_chars
        elif not animation_chars and default_chars in AnimationChars:
            self.animation_chars = AnimationChars[default_chars]
        elif not animation_chars and default_chars not in AnimationChars:
            raise ValueError(f"默认字符集 {default_chars} 无效")
        else:
            self.animation_chars = AnimationChars['dots']
    def __enter__(self):
        self.start()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    def start(self):
        """
        启动动画
        """
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
        self.thread = threading.Thread(target=self._run_animation, daemon=True)
        self.thread.start()
    def _run_animation(self):
        frame_index = 0
        last_frame_time = time.time()
        # char 确保长度一致，不足补空格
        char_max_len = max(len(char) for char in self.animation_chars)
        while self.is_running:
            current_time = time.time()
            # 控制帧率
            if current_time - last_frame_time >= self.speed:
                with self._lock:
                    current_chars = self.animation_chars
                    current_message = self.message
                char = "{: <{}}".format(current_chars[frame_index % len(current_chars)], char_max_len)
                print(f'\r{char} {current_message}', end='', flush=True)
                
                frame_index += 1
                last_frame_time = current_time
            # 短暂睡眠减少CPU占用
            time.sleep(0.005)
    def stop(self):
        """
        停止动画
        """
        with self._lock:
            if not self.is_running:
                return
            self.is_running = False
        if self.thread and self.thread.is_alive():
            for i in range(10):
                self.thread.join(timeout=0.1)
                if not self.thread.is_alive():
                    break
            else:
                print("\n警告: 动画线程终止超时")
        
        with self._lock:
            clear_length = len(self.message) + 3
        print('\r' + ' ' * clear_length + '\r', end='', flush=True)
    def update_message(self, new_message):
        """
        更新动画消息
        """
        with self._lock:
            self.message = new_message
    def update_speed(self, new_speed):
        """
        更新动画速度
        """
        with self._lock:
            if new_speed > 0:
                self.speed = 1.0 / new_speed
    def set_animation_chars(self, new_chars):
        """
        更新动画字符列表
        """
        with self._lock:
            if new_chars and len(new_chars) > 0:
                self.animation_chars = new_chars