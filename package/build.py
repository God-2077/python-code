import os
import sys
import yaml
import subprocess
import argparse
from pathlib import Path

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='PyInstaller打包脚本')
    parser.add_argument('config', help='配置文件路径')
    args = parser.parse_args()

    # 读取配置文件
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 基础路径设置
    base_dir = Path(__file__).parent.parent  # 项目根目录
    upx_dir = base_dir / 'upx'  # UPX目录
    
    # 遍历所有打包任务
    for task in config:
        print(f"\n{'='*40}")
        print(f"开始打包任务: {task['name']}")
        print(f"{'='*40}")
        
        # 解析任务参数
        python_file = base_dir / task['python-file']
        output_name = task['output-name']
        dist_path = base_dir / task['distpath']
        requirements = task.get('install-requirements', [])
        use_upx = task.get('upx', False)
        icon = task.get('icon')
        windowed = task.get('windowed', False)
        
        # 检查Python文件是否存在
        if not python_file.exists():
            print(f"错误: Python文件不存在 {python_file}")
            continue
        
        # 安装依赖
        if requirements:
            print(f"安装依赖: {', '.join(requirements)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + requirements, check=True)
        
        # 构建PyInstaller命令
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name', output_name,
            '--distpath', str(dist_path),
            '--specpath', str(base_dir / 'build'),
            '--workpath', str(base_dir / 'build' / 'temp'),
            '--noconfirm',
            '--clean'
        ]
        
        # 添加窗口模式选项
        if windowed:
            cmd.append('--windowed')
        
        # 添加图标选项
        if icon:
            icon_path = base_dir / icon
            if icon_path.exists():
                cmd.extend(['--icon', str(icon_path)])
            else:
                print(f"警告: 图标文件不存在 {icon_path}")
        
        # 添加UPX选项
        if use_upx:
            if upx_dir.exists():
                cmd.extend(['--upx-dir', str(upx_dir)])
                print(f"使用UPX压缩: {upx_dir}")
            else:
                print(f"警告: UPX目录不存在 {upx_dir}")
        
        # 添加主Python文件
        cmd.append(str(python_file))
        
        # 打印并执行命令
        print("执行命令:", ' '.join(cmd))
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"打包成功: {dist_path / output_name}")
        else:
            print(f"打包失败，退出码: {result.returncode}")

if __name__ == '__main__':
    main()