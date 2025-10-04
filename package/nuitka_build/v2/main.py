import os
import sys
import yaml
import subprocess
import datetime
import platform
import time
import psutil
import argparse
from pathlib import Path
import logging
import traceback
import json
import ctypes
from multiprocessing import Process, Queue

# 全局变量初始化
not_exit_code = False  # 默认值为False

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TimeoutError(Exception):
    """自定义超时异常"""
    pass

def worker(queue, func, *args, **kwargs):
    """工作进程函数"""
    try:
        result = func(*args, **kwargs)
        queue.put(result)
    except Exception as e:
        # 捕获函数执行中的异常并放入队列
        queue.put(e)

def run_with_timeout(func, timeout, *args, **kwargs):
    """
    带超时限制的函数执行
    :param func: 要执行的函数
    :param timeout: 超时时间（秒）
    :return: 函数执行结果
    :raises TimeoutError: 当函数执行超时时抛出
    :raises Exception: 当函数内部抛出异常时重新抛出
    """
    queue = Queue()
    process = Process(target=worker, args=(queue, func) + args, kwargs=kwargs)
    
    process.start()
    process.join(timeout)  # 等待指定超时时间
    
    if process.is_alive():
        # 超时处理
        process.terminate()  # 终止进程
        process.join()  # 确保进程终止
        raise TimeoutError(f"函数执行超过 {timeout} 秒")
    
    # 获取结果
    result = queue.get()
    
    # 如果结果是异常，重新抛出
    if isinstance(result, Exception):
        raise result
    
    return result

# 退出程序
def exit_program(error_code=0):
    global not_exit_code
    exit_code = error_code if not not_exit_code else 0
    logging.info(f"退出程序，错误码: {exit_code}")
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
    
def main():
    # utf-8 编码
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Nuitka Build Script")
    parser.add_argument("config", type=str, help="Path to the configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-level", "-l", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Set the logging level")
    parser.add_argument("--log-output", "-o", type=str, default="build_log.log", help="Output directory for the build")
    parser.add_argument("--not-exit-code", "-n", action="store_true", help="Do not exit with error code if build fails")
    args = parser.parse_args()

    # 日志配置 - 同时输出到屏幕和文件
    log_output_path = Path(args.log_output).resolve()
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
    base_dir = Path(__file__).resolve().parent.parent.parent.parent  # 项目根目录
    script_file_path = Path(__file__).resolve()  # 当前脚本路径
    script_file_dir = script_file_path.parent  # 当前脚本所在目录
    default_config_path = script_file_dir / 'example_config' / 'default_config.yml'
    upx_dir = base_dir / 'upx'  # UPX目录
    dist_path = base_dir / 'dist'  # 输出目录
    dist_path.mkdir(parents=True, exist_ok=True)  # 创建输出目录


    # welcome message
    logging.info("Nuitka Build Script Start...")

    # 系统概览

    logging.info(f"{rjust_str('系统信息概览',fillchar='=')}")

    # 时间
    logging.info(f"{rjust_str('时间信息')}")
    logging.info(f"当前时间(本地): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"当前时间(UTC): {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"当前时区: {time.strftime('%Z')} (UTC{time.strftime('%z')})")

    logging.debug(f"命令行参数: {args}")
    logging.info(f"当前工作目录: {os.getcwd()}")
    logging.info(f"进程 PID: {os.getpid()}")
    logging.info(f"进程名称: {psutil.Process(os.getpid()).name()}")
    logging.info(f"是否具有管理员权限: {'True' if is_admin() else 'False'}")
    logging.info(f"配置文件路径: {args.config}")
    logging.info(f"日志输出路径: {args.log_output}")

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
    if not os.path.exists(args.config):
        logging.error(f"配置文件 {args.config} 不存在")
        exit_program(1)
    # 检查默认配置文件是否存在
    if not os.path.exists(default_config_path):
        logging.error(f"默认配置文件 {default_config_path} 不存在")
        exit_program(1)
    

    # 读取配置文件
    try:
        with open(args.config, "r", encoding="utf-8") as f:
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
    required_keys = ["python-file"]
    for key in required_keys:
        if key not in config_keys:
            logging.error(f"配置文件缺少必要的键: {key}")
            exit_program(1)

    # 合并默认配置
    config = {**default_config, **config}
    logging.debug(f"最终配置: {json.dumps(config, ensure_ascii=False, indent=2)}")


    # 组建参数
    logger.info("开始组建 build 参数")

    # 解析配置

    # python
    python_file = base_dir / config.get("python-file")
    requirements = config.get("install-requirements",[])
    has_requirements_file = True if config.get("install-requirements-file") else False
    requirements_file = base_dir / config.get("install-requirements-file",'')

    # name
    name = config.get("name", "Untitled")
    ver = config.get("version", "unknown")
    output_name_template = config.get("output-name-template", "{name}_{app_ver}_py{py_ver}_nk_{os_short}_{arch}{exe_suffix}")
    output_name = output_name_template.format(
        name=name,
        app_ver=ver,
        py_ver=py_version,
        os_short=system_os.lower(),
        arch=arch,
        exe_suffix=get_exe_suffix()
    )

    # nuitka
    plugin_list = ",".join(config.get('plugin-list', []))
    include_files = config.get('include', {}).get('files', [])
    include_dirs = config.get('include', {}).get('dirs', [])
    custom_args = config.get('custom-args', [])
    only_linux_args = config.get('only-linux-args', [])
    only_windows_args = config.get('only-windows-args', [])
    clean_cache = config.get('clean-cache')
    c_compiler_lto = config.get('c-compiler', {}).get('lto', 'auto')
    c_compiler_static_libpython = config.get('c-compiler', {}).get('static-libpython', 'auto')
    windows_specific_controls = config.get('windows-specific-controls', {})

    # build
    timeout = config.get("timeout", 2700)
    os_list = config.get("os-list", ["Linux", "Windows"])

    # 检查 python 文件是否存在
    if  not os.path.exists(python_file):
        logging.error(f"python 文件路径 {python_file} 不存在")
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
        try:
            subprocess.run([python_executable, '-m', 'pip', 'install'] + requirements, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"安装依赖失败: {e}")
            exit_program(1)
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
        '--standalone',
        f'--jobs={os.cpu_count()}',  # 多线程
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

    # 自定义参数
    nuitka_cmd.extend(custom_args)
    if system_os == 'Linux':
        nuitka_cmd.extend(only_linux_args)
    elif system_os == 'Windows':
        nuitka_cmd.extend(only_windows_args)
    
    #  禁用缓存
    if clean_cache:
        if not clean_cache in ['all','bytecode','ccache','compression','dll-dependencies']:
            logging.warning(f"警告: 无效的clean-cache选项 '{clean_cache}'，将忽略")
        else:
            nuitka_cmd.append(f'--clean-cache={clean_cache}')
    
    # c-compiler
    if c_compiler_lto in ['auto','on','off']:
        nuitka_cmd.append(f'--lto={c_compiler_lto}')
    else:
        logging.warning(f"警告: 无效的c-compiler-lto选项 '{c_compiler_lto}'，将忽略")
    if c_compiler_static_libpython in ['auto','on','off']:
        nuitka_cmd.append(f'--static-libpython={c_compiler_static_libpython}')
    else:
        logging.warning(f"警告: 无效的c-compiler-static-libpython选项 '{c_compiler_static_libpython}'，将忽略")
    



    
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error: {e}")
        traceback.print_exc()
        exit_program(1)