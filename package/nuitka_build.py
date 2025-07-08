import os
import sys
import yaml
import subprocess
import platform
import argparse
from pathlib import Path
# from zip import zip_files_and_folders

def main():
    print("="*50)
    print("="*50)
    # 修复编码问题 - 设置UTF-8输出
    sys.stdout.reconfigure(encoding='utf-8')  # Python 3.7+
    sys.stderr.reconfigure(encoding='utf-8')

    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 请使用Python 3.7或更高版本")
        return
    
    Machine = platform.system()
    arrch = platform.machine()

    print(f"当前操作系统: {Machine} {arrch}")
    print(f"平台详情: {platform.platform()}")
    print(f"Python版本: {sys.version}")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Nuitka打包脚本')
    parser.add_argument('config', help='配置文件路径')
    args = parser.parse_args()

    # 读取配置文件
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 基础路径设置
    base_dir = Path(__file__).parent.parent  # 项目根目录
    upx_dir = base_dir / './upx/'  # UPX目录
    
    success_count = 0
    task_error_list = []
    # 遍历所有打包任务
    for i, task in enumerate(config, start=1):
        try:
            print(f"\n{'='*40}")
            print(f"开始打包任务: [{i}/{len(config)}] {task['name']}")
            print(f"{'='*40}")
            
            # 解析任务参数
            python_file = base_dir / task['python-file']
            dist_path = base_dir / task['distpath']
            requirements = task.get('install-requirements', [])
            use_upx = task.get('upx', False)
            # onefile = task.get('onefile', 0)
            icon = task.get('icon')
            windows_disable_console = task.get('windows-disable-console', False)
            name = task.get('name')
            version = task.get('version')
            output_name_template = task.get('output-name-template', '{{name}}_{{version}}_nuitka_{{os}}_{{arch}}')
            if arrch == "AMD64":
                arrch = "x64"
            output_name = output_name_template.replace('{{name}}', name).replace('{{version}}', version).replace('{{arch}}', arrch).replace('{{os}}', Machine)

            # 检查操作系统和架构
            # if Machine not in task.get('os', []):
            #     print(f"警告: 任务 [{i}/{len(config)} {task['name']}] 不支持当前操作系统 {Machine}")
            #     continue
            # if arrch not in task.get('arch', []):
            #     print(f"警告: 任务 [{i}/{len(config)} {task['name']}] 不支持当前架构 {arrch}")
            #     continue
            
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
                sys.executable, '-m', 'nuitka',
                f'--output-filename={output_name}.exe',
                f'--output-dir={dist_path}', # 输出目录
                '--onefile', # 单文件
                '--standalone',
                '--mingw64',
                # '--mode',
                '--assume-yes-for-downloads', #自动下载外部代码
                '--show-memory'
                
            ]
            
            # 添加窗口模式选项
            if windows_disable_console:
                cmd.append('--windows-disable-console')
            
            # 添加图标选项
            if icon:
                icon_path = base_dir / icon
                if icon_path.exists():
                    cmd.extend(['--windows-icon-from-ico=icon.ico', str(icon_path)])
                else:
                    print(f"警告: 图标文件不存在 {icon_path}")
                    
            # if arrch == "ARM64":
            #     print("UPX不支持当前架构")
            # else:
            #     if use_upx:
            #         if upx_dir.exists():
            #             cmd.append('--plugin-enable=upx')
            #             cmd.extend(['--upx-binary', str(upx_dir)])
            #             print(f"使用UPX压缩: {upx_dir}")
            #         else:
            #             print(f"警告: UPX目录不存在 {upx_dir}")
            #     else:
            #         print("不使用UPX压缩")
            # 添加主Python文件
            cmd.append(str(python_file))
            
            # 打印并执行命令
            print("执行命令:", ' '.join(cmd))
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                print(f"(onefile)打包成功: {dist_path / output_name}")
                success_count += 1
            else:
                print(f"打包失败，退出码: {result.returncode}")
        except Exception as e:
            print(f"任务[{i}/{len(config)} {task['name']}]失败: {e}")
            task_error_list.append(task['name'])
            continue
    if success_count != 0:
        print(f"打包完成，成功打包 [{success_count}/{len(config)}] 个任务")
        if task_error_list != []:
            print(f"打包失败的任务: {', '.join(task_error_list)}")
    else:
        print("打包失败，没有成功打包任何任务")
        print(f"失败的任务: {', '.join(task_error_list)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
