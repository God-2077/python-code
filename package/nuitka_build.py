import os
import sys
import yaml
import subprocess
import platform
import argparse
from pathlib import Path
import uuid
import shutil

def normalize_path(path_str):
    """将路径字符串中的反斜杠转换为当前系统的分隔符"""
    return Path(path_str.replace('\\', os.sep))

def delete_folders(directory):
    """删除指定目录下的所有文件夹，但保留文件"""
    if os.path.basename(directory) == '' or os.path.basename(directory):
        dir_name = os.path.basename(os.path.dirname(directory))
    else:
        dir_name = os.path.basename(directory)
    print(f'清理文件夹({dir_name})下的文件夹')
    try:
        # 确保目录存在
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            return True

        # 遍历目录中的所有项
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            # 如果是文件夹，则删除
            if os.path.isdir(item_path):
                # print(f"删除文件夹: {item_path}")
                rm_item_dir = ','.join(item_path)
                shutil.rmtree(item_path)
            # else:
            #     print(f"保留文件: {item_path}")
        print(f'清理文件夹({dir_name})下的文件夹完成: {rm_item_dir}')
        print("操作完成")
        return True
    except Exception as e:
        print(f"发生错误: {e}")
        return False

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
    
    system_os = platform.system()
    arch = platform.machine()

    print(f"当前操作系统: {system_os}")
    print(f'架构: {arch}')
    print(f"平台详情: {platform.platform()}")
    print("CPU核心数:", os.cpu_count())
    print("处理器信息:", platform.processor())
    print(f"Python版本: {sys.version}")
    print(f'工作目录: {os.getcwd()}')
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Nuitka打包脚本')
    parser.add_argument('config', help='配置文件路径')
    args = parser.parse_args()
    
    # 基础路径设置
    base_dir = Path(__file__).resolve().parent.parent  # 项目根目录
    upx_dir = base_dir / 'upx'  # UPX目录
    dist_path = base_dir / 'dist'
    # 读取配置文件
    # config_path = base_dir / args.config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"错误: 配置文件不存在 {config_path}")
        sys.exit(1)
    
    with config_path.open('r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    success_count = 0
    task_error_list = []
    
    # 遍历所有打包任务
    for i, task in enumerate(config, start=1):
        try:
            print(f"\n{'='*40}")
            print(f"开始打包任务: [{i}/{len(config)}] {task['name']}")
            print(f"{'='*40}")
            
            # 解析任务参数 - 使用路径规范化
            python_file = base_dir / normalize_path(task['python-file'])
            # dist_path = base_dir / normalize_path(task['distpath'])
            requirements = task.get('install-requirements', [])
            enable_plugins = task.get('enable-plugins', [])
            
            icon = task.get('icon')
            windows_disable_console = task.get('windows-disable-console', False)
            name = task.get('name')
            version = task.get('version')
            timeout = task.get('timeout', 60 * 45)
            
            # 处理输出文件名模板
            output_name_template = task.get('output-name-template', '{{name}}_{{version}}_nuitka_{{os}}_{{arch}}{{exe_suffix}}')
            
            # 处理架构名称统一
            normalized_arch = "x64" if arch == "AMD64" else arch
            exe_suffix = '.exe' if system_os == 'Windows' else ''
            
            output_name = output_name_template.replace('{{name}}', name) \
                .replace('{{version}}', version) \
                .replace('{{arch}}', normalized_arch) \
                .replace('{{os}}', system_os) \
                .replace('{{exe_suffix}}', exe_suffix)
            
            custom_command = task.get('custom-command')
            only_linux_command = task.get('only-linux-command')
            only_windows_command = task.get('only-windows-command')
            
            # 检查Python文件是否存在
            if not python_file.exists():
                print(f"错误: Python文件不存在 {python_file}")
                continue
            
            # 创建输出目录
            dist_path.mkdir(parents=True, exist_ok=True)
            
            # 安装依赖
            if requirements:
                print(f"安装依赖: {', '.join(requirements)}")
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + requirements, check=True)
            
            # 构建Nuitka命令
            cmd = [
                sys.executable, '-m', 'nuitka',
                f'--output-filename={output_name}',
                f'--output-dir={dist_path}',  # 输出目录
                '--onefile',  # 单文件
                '--standalone',
                f'--jobs={os.cpu_count()}',  # 多线程
                '--assume-yes-for-downloads',  # 自动下载外部代码
            ]
            
            # Windows特定参数
            if system_os == 'Windows':
                cmd.append('--mingw64')
                if windows_disable_console:
                    cmd.append('--windows-disable-console')
                
                if icon:
                    icon_path = base_dir / normalize_path(icon)
                    if icon_path.exists():
                        cmd.append(f'--windows-icon-from-ico={icon_path}')
                    else:
                        print(f"警告: 图标文件不存在 {icon_path}")
                if only_windows_command:
                    if isinstance(only_windows_command, str):
                        cmd.extend(only_windows_command.split())
                    elif isinstance(only_windows_command, list):
                        cmd.extend(only_windows_command)
            elif system_os == 'Linux':
                if only_linux_command:
                    if isinstance(only_linux_command, str):
                        cmd.extend(only_linux_command.split())
                    elif isinstance(only_linux_command, list):
                        cmd.extend(only_linux_command)
                cmd.append('--clang')
            else:
                # Linux/macOS 使用 clang
                cmd.append('--clang')
            
            # 启用插件
            if enable_plugins:
                plugin_list = ','.join(enable_plugins)
                cmd.append(f'--plugin-enable={plugin_list}')
                
                # UPX处理
                if 'upx' in enable_plugins:
                    upx_exe = 'upx.exe' if system_os == 'Windows' else 'upx'
                    upx_path = upx_dir / upx_exe
                    
                    if upx_path.exists():
                        cmd.append(f'--upx-binary={upx_path}')
                        print(f"使用UPX压缩: {upx_path}")
                    else:
                        print(f"警告: UPX可执行文件不存在 {upx_path}")
            
            # 添加自定义命令
            if custom_command:
                if isinstance(custom_command, str):
                    cmd.extend(custom_command.split())
                elif isinstance(custom_command, list):
                    cmd.extend(custom_command)
            
            # 创建临时文件避免中文路径问题
            temp_file = base_dir / f"{uuid.uuid4().hex}.py"
            shutil.copy(python_file, temp_file)
            cmd.append(str(temp_file))
            
            # 打印并执行命令
            print("执行命令:", ' '.join(cmd))
            
            try:
                # 执行打包命令
                result = subprocess.run(
                    cmd, 
                    timeout=timeout,
                    check=True
                )
                
                print(f"打包成功: {dist_path / output_name}")
                success_count += 1
                
            except subprocess.TimeoutExpired:
                print(f"任务[{i}/{len(config)} {task['name']}] 执行超时 {timeout} 秒")
                task_error_list.append(task['name'])
            except subprocess.CalledProcessError as e:
                print(f"打包失败，退出码: {e.returncode}")
                print(f"错误输出: {e.stderr}")
                task_error_list.append(task['name'])
            finally:
                # 确保临时文件被删除
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            print(f"任务[{i}/{len(config)} {task['name']}]失败: {str(e)}")
            import traceback
            traceback.print_exc()
            task_error_list.append(task['name'])
    
    # 输出最终结果
    print("\n" + "="*50)
    print(f"打包完成: 成功 {success_count} 个, 失败 {len(task_error_list)} 个")

    if success_count != 0:
        files_list = []

        # 遍历目录下的所有条目
        for entry in os.listdir(str(base_dir / 'dist')):
            # 拼接完整的文件路径
            full_path = os.path.join(str(base_dir / 'dist'), entry)
            # 检查该路径是否为文件
            if os.path.isfile(full_path):
                files_list.append(entry)

        # 输出文件列表
        print(f'Dist: {str(files_list)}')
        # 清理文件夹
        if delete_folders(dist_path):
            print(f"已清理dist目录下文件夹: {dist_path}")
    
    if task_error_list:
        print(f"失败的任务: {', '.join(task_error_list)}")
        sys.exit(1)

if __name__ == '__main__':
    main()