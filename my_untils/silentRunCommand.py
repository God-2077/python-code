#!/usr/bin/env python3
"""
命令行执行器 - 接收并执行系统命令
"""

import subprocess
import sys
import shlex

def run_command(command):
    """
    执行给定的命令并返回结果
    
    Args:
        command (str): 要执行的命令字符串
        
    Returns:
        dict: 包含执行结果、返回码和输出的字典
    """
    try:
        # 使用subprocess运行命令
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': command
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': '命令执行超时（30秒）',
            'command': command
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'执行错误: {str(e)}',
            'command': command
        }

def print_result(result):
    """格式化打印执行结果"""
    print(f"命令: {result['command']}")
    print(f"状态: {'成功' if result['success'] else '失败'}")
    print(f"返回码: {result['returncode']}")
    
    if result['stdout']:
        print("\n标准输出:")
        print(result['stdout'])
    
    if result['stderr']:
        print("\n错误输出:")
        print(result['stderr'])
    
    print("-" * 50)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python command_runner.py \"要执行的命令\"")
        print("示例: python command_runner.py \"ls -la\"")
        print("示例: python command_runner.py \"echo Hello World\"")
        sys.exit(1)
    
    # 获取要执行的命令（支持带空格的命令）
    command = ' '.join(sys.argv[1:])
    
    print(f"准备执行命令: {command}")
    print("=" * 50)
    
    # 执行命令
    result = run_command(command)
    
    # 显示结果
    print_result(result)
    
    # 根据执行结果退出
    sys.exit(0 if result['success'] else 1)

# 测试函数
def test_commands():
    """测试一些常用命令"""
    test_commands = [
        "echo 'Hello, World!'",
        "pwd",
        "whoami"
    ]
    
    print("运行测试命令:")
    print("=" * 50)
    
    for cmd in test_commands:
        result = run_command(cmd)
        print_result(result)

if __name__ == "__main__":
    # 如果没有参数，运行测试；否则执行用户命令
    if len(sys.argv) == 1:
        test_commands()
    else:
        main()
