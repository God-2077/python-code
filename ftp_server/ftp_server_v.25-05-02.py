#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/05/02
# @Author  : Kissablecho
# @Software: Visual Studio Code
# @Blog    : https://blog.ksable.top/
# @Github  : https://github.com/God-2077/

import sys
import os
import getopt
import signal
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# 默认配置参数
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 2121
DEFAULT_USER = "user"
DEFAULT_PASSWORD = "12345"
DEFAULT_DIRECTORY = os.getcwd()
DEFAULT_PERM = "elradfmw"
DEFAULT_PASSIVE_PORTS = "40000-40009"

def parse_arguments():
    """
    解析命令行参数
    返回: (host, port, user, password, directory, perm, passive_ports, anonymous)
    """
    # 初始化默认值
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    user = DEFAULT_USER
    password = DEFAULT_PASSWORD
    directory = DEFAULT_DIRECTORY
    perm = DEFAULT_PERM
    passive_ports = DEFAULT_PASSIVE_PORTS
    anonymous = False

    # 帮助信息
    help_text = f"""
Usage: {sys.argv[0]} [options]

Options:
  -h, --help            显示帮助信息
  -H, --host HOST       绑定主机 (默认: {DEFAULT_HOST})
  -p, --port PORT       监听端口 (默认: {DEFAULT_PORT})
  -u, --user USER       用户名 (默认: {DEFAULT_USER})
  -P, --password PASS   密码 (默认: {DEFAULT_PASSWORD})
  -d, --dir DIRECTORY   服务器根目录 (默认: 当前目录)
  -m, --perm PERMISSIONS 权限设置 (默认: {DEFAULT_PERM})
  -r, --passive-ports RANGE 被动端口范围 (格式: start-end) (默认: {DEFAULT_PASSIVE_PORTS})
  -a, --anonymous       启用匿名访问
    """

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hH:p:u:P:d:m:r:a",
            ["help", "host=", "port=", "user=", "password=", 
             "dir=", "perm=", "passive-ports=", "anonymous"]
        )
    except getopt.GetoptError as e:
        print(f"参数错误: {e}")
        print(help_text)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-H", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            try:
                port = int(arg)
                if not 1 <= port <= 65535:
                    raise ValueError
            except ValueError:
                print(f"错误: 无效端口号 {arg}")
                sys.exit(1)
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-P", "--password"):
            password = arg
        elif opt in ("-d", "--dir"):
            directory = os.path.abspath(arg)
            if not os.path.isdir(directory):
                print(f"错误: 目录不存在: {directory}")
                sys.exit(1)
        elif opt in ("-m", "--perm"):
            perm = arg
        elif opt in ("-r", "--passive-ports"):
            passive_ports = arg
        elif opt in ("-a", "--anonymous"):
            anonymous = True

    return (host, port, user, password, directory, perm, passive_ports, anonymous)

def parse_passive_ports(passive_str):
    """解析被动端口范围"""
    try:
        start, end = map(int, passive_str.split("-"))
        if 0 < start <= end <= 65535:
            return range(start, end + 1)
        raise ValueError
    except Exception:
        print(f"错误: 无效端口范围 {passive_str}")
        print("正确格式示例: 40000-40009")
        sys.exit(1)

def main():
    # 解析参数
    config = parse_arguments()
    host, port, user, password, directory, perm, passive_ports, anonymous = config
    
    # 初始化授权器
    authorizer = DummyAuthorizer()
    
    # 添加普通用户
    authorizer.add_user(user, password, directory, perm=perm)
    
    # 处理匿名访问
    if anonymous:
        authorizer.add_anonymous(directory)

    # 配置FTP处理器
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "PyFTPServer (custom)"
    
    # 设置被动端口
    handler.passive_ports = parse_passive_ports(passive_ports)

    # 创建服务器
    server = FTPServer((host, port), handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # 显式注册信号处理（新增部分）
    def signal_handler(signum, frame):
        print("\n接收到关闭信号，正在停止服务器...")
        server.close_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)  # 处理 Ctrl + C
    signal.signal(signal.SIGTERM, signal_handler) # 处理其他终止信号

    print(f"FTP 服务器配置:")
    print(f"• 监听地址: {host}:{port}")
    print(f"• 用户认证: {user}/{password}" + (" + 匿名" if anonymous else ""))
    print(f"• 根目录: {directory}")
    print(f"• 权限设置: {perm}")
    print(f"• 被动端口: {passive_ports}")
    print("\n按 Ctrl+C 停止服务器")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
        server.close_all()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)