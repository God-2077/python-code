# UpanScan
from generate_directory_structure import generate_directory_structure
# generate_directory_structure
"""
    生成目录结构对象
    
    Args:
        path (str): 要扫描的路径
        deep (int): 扫描深度，0表示只扫描当前目录，1表示扫描一级子目录，依此类推
    
    Returns:
        list: 目录结构对象列表
    
    Example:

        ```python
        structure = generate_directory_structure("E:\\temp", 2)
        print(structure)
        ```
        result
        ```json
            [
                {
                    "path": "E:\\temp",
                    "name": "temp",
                    "size": 0,
                    "modify_time": "2023-10-10 10:10:10",
                    "create_time": "2023-10-10 10:10:10",
                    "permissions": "RWD",
                    "type": "dir",
                    "timestamp": 1696944210,
                    "items_count": 2,
                    "items_dir_count": 1,
                    "items_files_count": 1,
                    "items": [
                        {
                            "path": "E:\\temp\\dir1",
                            "name": "dir1",
                            "size": 0,
                            "modify_time": "2023-10-10 10:10:10",
                            "create_time": "2023-10-10 10:10:10",
                            "permissions": "RWD",
                            "type": "dir",
                            "timestamp": 1696944210,
                            "items_count": 0,
                            "items_dir_count": 0,
                            "items_files_count": 0,
                            "items": []
                        },
                        {
                            "path": "E:\\temp\\file1.txt",
                            "name": "file1.txt",
                            "size": 1024,
                            "modify_time": "2023-10-10 10:10:10",
                            "create_time": "2023-10-10 10:10:10",
                            "permissions": "RWD",
                            "type": "file",
                            "timestamp": 1696944210,
                            "items_count": 0,
                            "items_dir_count": 0,
                            "items_files_count": 0,
                            "items": []
                        }
                    ]
                }
            ]
        ```json
"""
from get_usb_info_wmi import get_usb_info_wmi
# get_usb_info_wmi
'''
    使用WMI获取所有 U盘 信息

    Args:
        None
    
    Returns:
        list: 包含所有U盘信息的列表，每个元素是一个字典，包含U盘的设备ID、卷名、大小、可用空间、文件系统和序列号。
    
    Example:
        ```python
        usb_drives = get_usb_info_wmi()
        print(usb_drives)
        # 示例输出:
        # [
        #     {'device': 'E:', 'volume_name': 'U盘1', 'size': 128000000, 'free_space': 100000000, 'file_system': 'FAT32', 'serial_number': '12345678'},
        #     {'device': 'F:', 'volume_name': 'U盘2', 'size': 256000000, 'free_space': 200000000, 'file_system': 'NTFS', 'serial_number': '87654321'}
        # ]
        ```
    '''
from _Logger import Logger
import os
import sys
from rich import print
from pathlib import Path

# 获取当前脚本所在目录的上上级目录路径
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# 将上上级目录添加到 sys.path
sys.path.append(parent_dir)

from my_untils.modules._async import _async

# -----------------------
# 配置区

# 工作目录
BASE_PWD = os.getcwd()

# 保存的路径，文件夹不存在会自动创建
SAVE_PATH = "D:/UpanScan/"
# SAVE_PATH 文件夹结构
# SAVE_PATH
#     |-- UpanScan_logs.log
#     |-- SAVE
#     |    |-- files
#     |    |    |-- USB_序列号1
#     |    |    |   |-- 文件夹1
#     |    |    |   |   |-- 文件1.txt
#     |    |    |   |   |-- 文件2.txt
#     |    |    |   |-- 文件夹2
#     |    |    |   |   |-- 文件3.txt
#     |    |    |-- USB_序列号2
#     |    |    |   |-- 文件夹3
#     |    |    |   |   |-- 文件4.txt
#     |    |    |   |   |-- 文件5.txt
#     |-- 序列号1.json 记录每次扫描的文件信息，json格式
# example SAVE_PATH/序列号1.json
# {
#     "device": "E:",
#     "volume_name": "u盘",
#     "serial_number": "USB_序列号1",
#     "insertion_records": [
#         {
#             "id": 1,
#             "insertion_time": "2023-10-10 10:10:10",
#             "removal_time": "2023-10-10 10:10:10",
#             "duration": 0,
#             "total_count": 3,
#             "files_count": 2,
#             "dirs_count": 1,
#             "total_size": 1024
#         }
#     ],
#     "files_records": {
#         "id1": [
#             {
#                 "id": 1,
#                 "path": "E:\\temp",
#                 "name": "temp",
#                 "size": 0,
#                 "modify_time": "2023-10-10 10:10:10",
#                 "create_time": "2023-10-10 10:10:10",
#                 "permissions": "RWD",
#                 "type": "dir",
#                 "timestamp": 1696944210,
#                 "items_count": 2,
#                 "items_dir_count": 1,
#                 "items_files_count": 1,
#                 "items": [
#                     {
#                         "path": "E:\\temp\\dir1",
#                         "name": "dir1",
#                         "size": 0,
#                         "modify_time": "2023-10-10 10:10:10",
#                         "create_time": "2023-10-10 10:10:10",
#                         "permissions": "RWD",
#                         "type": "dir",
#                         "timestamp": 1696944210,
#                         "items_count": 0,
#                         "items_dir_count": 0,
#                         "items_files_count": 0,
#                         "items": []
#                     },
#                     {
#                         "path": "E:\\temp\\file1.txt",
#                         "name": "file1.txt",
#                         "size": 1024,
#                         "modify_time": "2023-10-10 10:10:10",
#                         "create_time": "2023-10-10 10:10:10",
#                         "permissions": "RWD",
#                         "type": "file",
#                         "timestamp": 1696944210,
#                         "items_count": 0,
#                         "items_dir_count": 0,
#                         "items_files_count": 0,
#                         "items": []
#                     }
#                 ]
#             }
#         ]
#     }
# }

# 序列号黑白名单
# 模式说明
# WHITE: 白名单模式，只有在白名单中的USB设备才会被扫描到
# BLACK: 黑名单模式，黑名单中的USB设备不会被扫描到
MODE = "WHITE"
WHITE_LIST = ["12345678901234567890123456789012"]
BLACK_LIST = ["09876543210987654321098765432109"]

# 扫描深度
SACN_DEEP = 8

# 复制文件
COPY_FILE_ENABLE = True # 是否复制文件，默认True
COPY_FILE_RATE = 0.5 # 复制文件的速率，默认0.5Mb/s，仅当 COPY_FILE_THREAD 为 1 时生效
COPY_FILE_THREAD = 1  # 复制文件的线程数，默认5，复制小文件可能有奇效，建议保持默认值（1）
# 匹配规则
MATCH_RULE = [
    {
        "name": {
            "enable": True,
            # 留空则不考虑
            "include": ["A"],
            "exclude": ["B"],
            "startwith": ["c"],
            "endwith": ["d"],
            "re": ["[0-9]+"], # 正则表达式匹配，留空则不考虑
        },
        "path": {
            "enable": True,
            "path": {
                "_include": ["G"], # 路径应该包含的内容
                "path_exclude": ["H"]
            },
            "parent_path": {
                "include": ["E"], # 父文件夹应该包含的内容
                "exclude": ["F"]
            }
        },
        "size": {
            "enable": True,
            "min": 1,  # 最小值，单位Mb，默认0
            "max": 10,  # 最大值，单位Mb，默认无穷大
        },
        "time": {
            "enable": True,
            "modify": {
                "start": "2023-01-01 00:00:00",  # 起始时间，格式"YYYY-MM-DD HH:MM:SS"，默认无起始时间
                "end": "2023-12-31 23:59:59",    # 结束时间，格式"YYYY-MM-DD HH:MM:SS"，默认无结束时间
            },
            "create": {
                "start": "2023-01-01 00:00:00",  # 起始时间，格式"YYYY-MM-DD HH:MM:SS"，默认无起始时间
                "end": "2023-12-31 23:59:59",    # 结束时间，格式"YYYY-MM-DD HH:MM:SS"，默认无结束时间
            },
        },
    }
]
# -----------------------

BASE_PATH = Path(BASE_PWD)
LOG_FILE_PATH = BASE_PATH / LOG_FILE_PATH

log=Logger(log_file_path=LOG_FILE_PATH)

log.info("Hello World!")

