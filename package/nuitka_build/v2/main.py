import time
start_time = time.time()
import os
import sys
import yaml
import subprocess
import datetime
import platform
import psutil
import argparse
from pathlib import Path
import logging
import traceback
import json
import ctypes
import shutil
import uuid

# 全局变量初始化
not_exit_code = False  # 默认值为False
project_base_path = None  # 初始化项目目录变量

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def format_time(seconds):
    """
    将秒数转换为易读的时间格式（Y年 D天 H小时 M分钟 S秒 MS毫秒）
    只显示非零的时间单位，并按照从大到小的顺序排列
    
    参数:
        seconds (float): 要转换的秒数（可以是小数）
    
    返回:
        str: 格式化后的时间字符串，如 "3M 4S 500MS"
    """
    if seconds < 0:
        return "无效输入"
    # 定义时间常数（以秒计）
    SECONDS_PER_YEAR = 365 * 24 * 3600
    SECONDS_PER_DAY = 24 * 3600
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60
    # 计算整数部分
    years = int(seconds // SECONDS_PER_YEAR)
    remainder = seconds % SECONDS_PER_YEAR
    days = int(remainder // SECONDS_PER_DAY)
    remainder %= SECONDS_PER_DAY
    hours = int(remainder // SECONDS_PER_HOUR)
    remainder %= SECONDS_PER_HOUR
    minutes = int(remainder // SECONDS_PER_MINUTE)
    seconds_remaining = remainder % SECONDS_PER_MINUTE
    seconds_int = int(seconds_remaining)
    milliseconds = int((seconds_remaining - seconds_int) * 1000)
    parts = []
    if years > 0:
        parts.append(f"{years}Y")
    if days > 0:
        parts.append(f"{days}D")
    if hours > 0:
        parts.append(f"{hours}H")
    if minutes > 0:
        parts.append(f"{minutes}M")
    if seconds_int > 0 or (not parts and milliseconds == 0):  # 确保至少显示0S
        parts.append(f"{seconds_int}S")
    if milliseconds > 0:
        parts.append(f"{milliseconds}MS")
    # 处理全零情况
    if not parts:
        return "0S"
    return " ".join(parts)

# 退出程序
def exit_program(error_code=0):
    global not_exit_code
    exit_code = error_code if not not_exit_code else 0
    
    if project_base_path and os.path.exists(project_base_path):
        shutil.rmtree(project_base_path)
    logging.info(f"退出程序，耗时: {format_time(time.time() - start_time)}")
    logging.info(f"退出程序，退出码: {exit_code}")
    sys.exit(exit_code)

# str 右填充=，默认宽度50
def rjust_str(s, width=50, fillchar="-"):
    return s.ljust(width, fillchar)

def is_admin():
    """
    检查当前程序是否以管理员/root权限运行
    返回: bool -  True表示具有管理员权限，False表示没有
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows系统通过ctypes调用Windows API检查
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        
        elif system in ["Linux", "Darwin"]:  # Linux和macOS
            # Unix类系统检查有效用户ID是否为0（root）
            return os.geteuid() == 0
        
        else:
            # 其他未知系统
            logging.warning(f"不支持的操作系统: {system}")
            return False
    
    except Exception as e:
        print(f"权限检查出错: {str(e)}")
        return False
def get_exe_suffix():
    sys_os = platform.system()
    if sys_os == "Windows":
        return ".exe"
    else:
        return ".bin"

def os_short_name(sys_os):
    if sys_os == "Windows":
        return "win"
    elif sys_os == "Linux":
        return "lin"
    elif sys_os == "Darwin":
        return "mac"
    else:
        return sys_os.lower()

# 合并配置
def merge_configs(default_config, custom_config):
    merged = {}
    
    # 处理 custom_config 中的非 None 值
    for key, value in custom_config.items():
        if value is not None:
            merged[key] = value
    
    # 处理 default_config 的所有键
    for key, value in default_config.items():
        # 如果 custom_config 中有 None 值，保留 default_config 的值
        if key in custom_config and custom_config[key] is None:
            merged[key] = value
        # 如果 custom_config 没有这个键，直接添加 default_config 的值
        elif key not in custom_config:
            merged[key] = value
    
    # 处理 custom_config 中值为 None 但 default_config 没有的键
    for key, value in custom_config.items():
        if value is None and key not in default_config:
            merged[key] = None

    return merged

def get_nuitka_version():
    python_executable = sys.executable
    try:
        result = subprocess.run(
            [python_executable, '-m', 'nuitka', '--version'],
            check=True,
            capture_output=True,
            text=True
        )
        return parse_nuitka_version(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Get Nuitka version failed: {e}")
        return "unknown"

def parse_nuitka_version(version_str):
    # 版本号在第一行
    lines = version_str.splitlines()
    if lines:
        first_line =  lines[0].strip()
        # 提取主版本和子版本号部分
        version_parts = first_line.split(".")
        if len(version_parts) >= 2:
            return f"{version_parts[0]}{version_parts[1]}" # 不要添加小数点

    return "unknown"
def get_utc_time():
    """获取当前UTC时间"""
    # python < 3.11 时，需要使用 datetime.UTC 而不是 datetime.timezone.utc
    if sys.version_info < (3, 11):
        return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

def main():
    # utf-8 编码
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    
    global project_base_path

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Nuitka Build Script")
    parser.add_argument("config", type=str, help="Path to the configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-level", "-l", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="DEBUG", help="Set the logging level")
    parser.add_argument("--log-output", "-o", type=str, default="log/build_log.log", help="Output directory for the build")
    parser.add_argument("--not-exit-code", "-n", action="store_true", help="Do not exit with error code if build fails")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent.parent.parent  # 项目根目录
    log_output_path = base_dir / args.log_output
    log_output_path.parent.mkdir(parents=True, exist_ok=True)

    # 日志配置 - 同时输出到屏幕和文件
    # log_output_path = Path(args.log_output).resolve()
    log_output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 清除现有的日志处理器
    # for handler in logging.root.handlers[:]:
    #     logging.root.removeHandler(handler)
    
    # 设置日志格式
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_output_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 获取根日志器并配置
    logger = logging.getLogger()
    logger.setLevel(args.log_level.upper())
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        # 解析日志级别
        log_level = getattr(logging, args.log_level.upper(), None)
        if not isinstance(log_level, int):
            logging.error(f"Invalid log level: {args.log_level}")
            sys.exit(1)
        logger.setLevel(log_level)
    if args.not_exit_code:
        global not_exit_code
        not_exit_code = args.not_exit_code

    # 设置
    start_time = time.time()
    system_os = platform.system()
    arch = platform.machine()
    cpu_count = os.cpu_count()
    py_version = f"{sys.version_info.major}{sys.version_info.minor}" # 主版本 加 次版本 312

    # 路径设置
    python_executable = sys.executable
    script_file_path = Path(__file__).resolve()  # 当前脚本路径
    script_file_dir = script_file_path.parent  # 当前脚本所在目录
    default_config_path = script_file_dir / 'example_config' / 'default_config.yml'
    upx_dir = base_dir / 'upx'  # UPX目录
    dist_path = base_dir / 'dist'  # 输出目录
    dist_path.mkdir(parents=True, exist_ok=True)  # 创建输出目录
    temp_uuid = uuid.uuid4().hex
    new_project_base_path = base_dir / temp_uuid

    # 替换 \ 为 /
    if True:
        config_path = base_dir / args.config.replace('\\','/')

    # welcome message
    logging.info("=" * 50)
    logging.info("Nuitka Build Script Start...")

    # 系统概览

    logging.info(f"{rjust_str('系统信息概览',fillchar='=')}")

    # 时间
    logging.info(f"{rjust_str('时间信息')}")
    logging.info(f"当前时间(本地): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"当前时间(UTC): {get_utc_time}")
    logging.info(f"当前时区: {time.strftime('%Z')} (UTC{time.strftime('%z')})")

    logging.debug(f"命令行参数: {args}")
    logging.info(f"当前工作目录: {os.getcwd()}")
    logging.info(f"进程 PID: {os.getpid()}")
    logging.info(f"进程名称: {psutil.Process(os.getpid()).name()}")
    logging.info(f"是否具有管理员权限: {'True' if is_admin() else 'False'}")
    logging.info(f"配置文件路径: {config_path}")
    logging.info(f"日志输出路径: {log_output_path}")

    # python 信息
    logging.info(f"{rjust_str('Python 信息')}")    
    logging.info(f"Python 解释器路径: {sys.executable}")
    logging.info(f"Python版本: {platform.python_version()}")
    logging.info(f"Python实现: {platform.python_implementation()}")
    logging.info(f"Python路径: {sys.executable}")
    logging.info(f"Python编译信息: {platform.python_compiler()}")
    logging.info(f"系统编码: {sys.getdefaultencoding()}")
    logging.info(f"文件系统编码: {sys.getfilesystemencoding()}")

    # 系统信息
    logging.info(f"{rjust_str('系统信息')}")    
    logging.info(f"系统: {system_os}")
    logging.info(f"版本: {platform.version()}")
    logging.info(f"架构: {arch}")
    logging.info(f"CPU核心数: {cpu_count}")
    logging.info(f"处理器: {platform.processor()}")
    
    # 路径信息
    logging.info(f"{rjust_str('路径信息')}")    
    logging.info(f"项目根目录: {base_dir}")
    logging.info(f"默认配置文件路径: {default_config_path}")
    logging.info(f"UPX目录: {upx_dir}")
    logging.info(f"输出目录: {dist_path}")

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        logging.error(f"配置文件 {config_path} 不存在")
        exit_program(1)
    # 检查默认配置文件是否存在
    if not os.path.exists(default_config_path):
        logging.error(f"默认配置文件 {default_config_path} 不存在")
        exit_program(1)
    

    # 读取配置文件
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            config_keys = config.keys()
            logging.info(f"读取配置文件成功")
            logging.info(f"配置文件包含的 {len(config_keys)} 个键")
    except Exception as e:
        logging.error(f"读取配置文件 {args.config} 失败: {e}")
        exit_program(1)
    # 读取默认配置
    try:
        with open(default_config_path, "r", encoding="utf-8") as f:
            default_config = yaml.safe_load(f)
            default_config_keys = default_config.keys()
            logging.info(f"读取默认配置文件成功")
    except Exception as e:
        logging.error(f"读取默认配置文件失败: {e}")
        exit_program(1)
    
    # 检查必要的键是否存在
    required_keys = ["init-file","project-base-path"]
    for key in required_keys:
        if key not in config_keys:
            logging.error(f"配置文件缺少必要的键: {key}")
            exit_program(1)

    # 合并默认配置
    # config = {**default_config, **config}
    config = merge_configs(default_config, config)
    logging.debug(f"最终配置: {json.dumps(config, ensure_ascii=False, indent=2)}")




    # 项目目录
    app_ver = config.get("version", "unknown")
    project_base_path = base_dir / config.get("project-base-path").format(app_ver=app_ver)
    # 检查项目目录是否存在
    if not os.path.exists(project_base_path):
        logging.error(f"项目目录 {project_base_path} 不存在")
        exit_program(1)
    # 复制项目到新目录，避免特殊文件名导致的问题
    shutil.copytree(project_base_path, new_project_base_path)
    old_project_base_path = project_base_path
    project_base_path = new_project_base_path

    # 解析配置
    logging.info(f"开始解析配置")
    # python
    init_file = project_base_path / config.get("init-file")
    requirements = config.get("install-requirements",[])
    has_requirements_file = True if config.get("install-requirements-file") else False
    requirements_file = project_base_path / config.get("install-requirements-file",'')

    # name
    name = config.get("name", "Untitled")
    # ver = config.get("version", "unknown")
    output_name_template = config.get("output-name-template", "{name}_{app_ver}_py{py_ver}_nk_{os_short}_{arch}{exe_suffix}")
    output_name = output_name_template.format(
        name=name,
        app_ver=app_ver,
        py_ver=py_version,
        nk_ver=get_nuitka_version(),
        os_short=os_short_name(system_os),
        arch=arch,
        exe_suffix=get_exe_suffix()
    )
    print(f"输出文件名: {output_name}")
    
    # nuitka
    plugin_list = ",".join(config.get('plugin-list', []))
    include_files = config.get('include', {}).get('files', [])
    include_dirs = config.get('include', {}).get('dirs', [])
    custom_args = config.get('custom-args', [])
    only_linux_args = config.get('only-linux-args', [])
    only_windows_args = config.get('only-windows-args', [])
    include_modules = config.get('include', {}).get('modules', [])
    include_packages = config.get('include', {}).get('packages', [])
    clean_cache = config.get('clean-cache')
    c_compiler_lto = config.get('c-compiler', {}).get('lto')
    c_compiler_static_libpython = config.get('c-compiler', {}).get('static-libpython')
    windows_specific_controls = config.get('windows-specific-controls', {})
    windows_console_mode = windows_specific_controls.get('console-mode',"force")
    windows_icon = windows_specific_controls.get('icon')
    windows_uac_admin = windows_specific_controls.get('uac-admin', False)
    windows_uac_uiaccess = windows_specific_controls.get('uac-uiaccess', False)

    # build
    build_timeout = config.get("timeout", 2700)
    os_list = config.get("os-list", ["Linux", "Windows"])
    build_pwd = config.get("build-pwd", "script-base-path")
    if build_pwd == "root-base-path":
        build_pwd = base_dir
    elif build_pwd == "script-base-path":
        build_pwd = project_base_path
    else:
        if build_pwd.startswith('./'):
            build_pwd = project_base_path / build_pwd
        else:
            build_pwd = base_dir / build_pwd
    
    # check-program
    check_program = config.get("check-program", {})
    check_program_enable = check_program.get("enable", False)
    check_program_return_code = check_program.get("return-code", 0)
    check_program_timeout = check_program.get("timeout", 10)
    check_program_check_command = check_program.get("check-command", [])
    check_program_return_output = check_program.get("return-output", "success")
    check_program_throw_exception = check_program.get("throw-exception", False)


    
    if not os.path.exists(init_file):
        logging.error(f"入口 {init_file} 不存在")
        exit_program(1)
    
    if has_requirements_file and not requirements_file.exists():
        logging.error(f"requirements 文件路径 {requirements_file} 不存在")
        exit_program(1)
    
    # 系统检测
    if system_os not in os_list:
        logging.error(f"当前系统 {system_os} 不在配置的 os-list 中: {', '.join(os_list)}")
        exit_program(1)
    
    # 安装依赖
    if requirements:
        logging.info(f"安装依赖: {', '.join(requirements)}")
        print(f"\n{'-'*20}\n")
        try:
            subprocess.run([python_executable, '-m', 'pip', 'install'] + requirements, check=True,timeout=1800)
        except subprocess.CalledProcessError as e:
            logging.error(f"安装依赖失败: {e}")
            exit_program(1)
        print(f"\n{'-'*20}\n")
        logging.info(f"依赖安装完成")
    if has_requirements_file and requirements_file.exists():
        logging.info(f"安装 requirements 文件 {os.path.abspath(requirements_file)} 中的依赖")
        try:
            subprocess.check_call([python_executable, "-m", "pip", "install", "-r", str(requirements_file)])
        except subprocess.CalledProcessError as e:
            logging.error(f"安装 requirements 文件 {requirements_file} 中的依赖失败: {e}")
            exit_program(1)
        logging.info(f"requirements 文件中的依赖安装完成")
    
    # 构建 nuitka 参数
    nuitka_cmd = [
        python_executable,
        "-m", "nuitka",
        '--standalone', # 独立模式
        '--onefile', # 单文件模式
        '--follow-imports',
        f'--jobs={cpu_count}',  # 多线程
        '--assume-yes-for-downloads',  # 自动下载外部代码
    ]

    # 插件
    if plugin_list:
        nuitka_cmd.append(f'--plugin-enable={plugin_list}')
        if 'upx' in plugin_list:
            upx_executable = 'upx.exe' if system_os == 'Windows' else 'upx'
            upx_path = upx_dir / upx_executable

            if os.path.exists(upx_path):
                nuitka_cmd.append(f'--upx-binary={upx_path}')
                logging.info(f"检测到 UPX 压缩器: {upx_path} ，已启用")
            else:
                logging.warning(f"UPX 压缩器未找到: {upx_path}")
    
    # include files
    # example
    # nuitka --standalone \
    # --include-data-files=./file1=file1 \
    # --include-data-files=./file2=file2 \
    # --include-data-dir=./dir1=dir1 \
    # --include-data-dir=./dir2=dir2 \
    # your_script.py

    for file in include_files:
        # 替换开头第一个 ./
        end_file = file.replace('./','',1) if file.startswith('./') else file
        nuitka_cmd.append(f'--include-data-files={file}={end_file}')
    for dir in include_dirs:
        end_dir = dir.replace('./','',1) if dir.startswith('./') else dir
        nuitka_cmd.append(f'--include-data-dir={dir}={end_dir}')
    for module in include_modules:
        nuitka_cmd.append(f'--include-module={module}')
    for package in include_packages:
        nuitka_cmd.append(f'--include-package={package}')

    # 自定义参数
    if custom_args:
        if isinstance(custom_args,str):
            nuitka_cmd.append(custom_args)
        elif isinstance(custom_args,list):
            nuitka_cmd.extend(custom_args)
        else:
            logging.warning(f"警告: 无效的 custom-args 选项类型 '{type(custom_args)}'，将忽略")
    if system_os == 'Linux' and only_linux_args:
        if isinstance(only_linux_args,str):
            nuitka_cmd.append(only_linux_args)
        elif isinstance(only_linux_args,list):
            nuitka_cmd.extend(only_linux_args)
        else:
            logging.warning(f"警告: 无效的 only-linux-args 选项类型 '{type(only_linux_args)}'，将忽略")
    elif system_os == 'Windows':
        if isinstance(only_windows_args,str):
            nuitka_cmd.append(only_windows_args)
        elif isinstance(only_windows_args,list):
            nuitka_cmd.extend(only_windows_args)
        else:
            logging.warning(f"警告: 无效的 only-windows-args 选项类型 '{type(only_windows_args)}'，将忽略")
    
    #  禁用缓存
    if clean_cache:
        if not clean_cache in ['all','bytecode','ccache','compression','dll-dependencies']:
            logging.warning(f"警告: 无效的clean-cache选项 '{clean_cache}'，将忽略")
        else:
            nuitka_cmd.append(f'--clean-cache={clean_cache}')
    
    # c-compiler
    if c_compiler_lto and c_compiler_lto in ['auto','on','off']:
        nuitka_cmd.append(f'--lto={c_compiler_lto}')
    elif c_compiler_lto:
        logging.warning(f"警告: 无效的c-compiler-lto选项 '{c_compiler_lto}'，将忽略")
    if c_compiler_static_libpython and c_compiler_static_libpython in ['auto','on','off']:
        nuitka_cmd.append(f'--static-libpython={c_compiler_static_libpython}')
    elif c_compiler_static_libpython:
        logging.warning(f"警告: 无效的c-compiler-static-libpython选项 '{c_compiler_static_libpython}'，将忽略")
    
    # Windows 特定参数
    if system_os == 'Windows':
        # 使用 mingw64 编译
        nuitka_cmd.append('--mingw64')
        # 控制台
        if windows_console_mode in ['force','disable','attach','hide']:
            nuitka_cmd.append(f'--windows-console-mode={windows_console_mode}')
        else:
            logging.warning(f"警告: 无效的windows-console-mode选项 '{windows_console_mode}'，将忽略")
        # 图标
        if windows_icon:
            windows_icon_path = None
            if os.path.exists(  project_base_path / windows_icon):
                windows_icon_path = project_base_path / windows_icon
            elif os.path.exists(windows_icon):
                windows_icon_path = base_dir / windows_icon
            else:
                logging.warning(f"警告: 图标文件 {windows_icon} 不存在，将忽略")
            nuitka_cmd.append(f'--windows-icon-from-ico={windows_icon_path}')
        # UAC 管理员权限
        if windows_uac_admin:
            nuitka_cmd.append('--windows-uac-admin')
        # UAC UI 访问权限
        if windows_uac_uiaccess:
            nuitka_cmd.append('--windows-uac-uiaccess')
    elif system_os == 'Linux':
        # 使用 clang 编译
        nuitka_cmd.append('--clang')
    else:
        # 未知系统
        # logging.warning(f"警告: 未知系统 {system_os}，将忽略")
        pass
    
    # 输出文件名
    nuitka_cmd.append(f'--output-filename={output_name}')
    # 输出目录
    nuitka_cmd.append(f'--output-dir={dist_path}')
    # 入口文件
    nuitka_cmd.append(str(init_file))

    logging.info(f"nuitka 命令: {nuitka_cmd}")

    # 执行 nuitka 命令
    logger.info(f"构建工作路径: {build_pwd}")
    logger.info(f"编译超时: {build_timeout} 秒")
    if int(build_timeout) < 60:
        logger.warning(f"警告: 编译超时设置为 {build_timeout} 秒，建议设置为大于 60 秒")
    logger.info("开始编译...")

    build_start_time = time.time()
    print(f"\n{'-'*20}\n")
    try:
        subprocess.run(
            nuitka_cmd,
            check=True,
            timeout=build_timeout,
            cwd=build_pwd
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"nuitka 编译失败: {e}")
        logger.error(f"打包失败，退出码: {e.returncode}")
        exit_program(1)
    except subprocess.TimeoutExpired as e:
        logging.error(f"nuitka 编译超时: {e}")
        exit_program(1)
    print(f"\n{'-'*20}\n")
    logger.info("编译完成")
    logger.info(f"编译耗时: {format_time(time.time() - build_start_time)}")
    logger.info(f"编译输出: {dist_path / output_name}")
    # 清空  dist 目录下的文件夹
    logger.info("清空 dist 目录下的所有文件夹")
    for item in dist_path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            pass
    logger.info("dist 目录下的文件夹已清空")

    # 检查程序
    # if check_program_enable:
    if False:
        logger.info("开始检查程序是否编译成功")
        logger.info(f"检查程序参数: {check_program_check_command}")
        logging.info(f"超时: {check_program_timeout} 秒")
        logger.info(f"检查程序返回码: {check_program_return_code}")
        logger.info(f"检查程序输出: {check_program_return_output}")

        try:
            check_result = subprocess.run(
                [str(dist_path / output_name)] + check_program_check_command,
                check=False,
                stdout=subprocess.PIPE, # 捕获标准输出
                stderr=subprocess.PIPE, # 捕获错误输出（可选）
                text=True,              # 以文本模式处理输出
                timeout=check_program_timeout,
                cwd=dist_path
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"检查程序失败: {e}")
            check_ok = False
            # 在访问 check_result 之前确保它有值
            check_result = e
        except subprocess.TimeoutExpired as e:
            logging.error(f"检查程序超时: {e}")
            check_ok = False
            # 在访问 check_result 之前确保它有值
            check_result = e
        else:
            # logging.info(f"检查程序成功: {check_result}")
            check_ok = True

        if check_ok and check_result.returncode == check_program_return_code and check_program_return_output in check_result.stdout.strip():
            logging.info(f"检查程序成功: {check_result}")
            logger.info(f"检查程序输出: \n{'-'*20}\n{check_result.stdout}\n{'-'*20}")
        else:
            logging.error(f"检查程序失败: {check_result}")
            logger.error(f"程序返回码: {check_result.returncode}")
            logger.error(f"程序输出: \n{'-'*20}\n{check_result.stdout}\n{'-'*20}")
            if check_program_throw_exception:
                raise Exception(f"check program failed")
    else:
        logger.info("检查程序未启用")
        check_ok = True
                
    if check_ok:
        logger.info("Nuitka Build Script Successfull")

    exit_program(0)
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error: {e}")
        traceback.print_exc()
        exit_program(1)