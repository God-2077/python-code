# FTP 扫描所有的文件

import ftplib
import os
import json
import time
import threading
import queue
import datetime
import argparse
import chardet
import hashlib
import shutil
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any
import threading

# ================== 配置区（按需修改这里！） ==================
IP = "127.0.0.1"          # FTP服务器IP（默认本地，改成你的IP）
PORT = 2121                 # 端口（默认21，SFTP用22）
USER = "user"
PASSWORD = "12345"
THREADS = 6               # 线程数（默认3，别设太大防服务器炸）
DIRECTORY = "/"           # 扫描起始目录（默认根目录）
MAX_DEPTH = 5             # 扫描深度（默认8层，别设太高防死循环）
STATE_FILE = "scan_state.json"  # 状态保存文件（自动恢复用）
# 以下两个条件之一满足时保存状态：
# 1. 达到 SAVE_STATE_INTERVAL 秒间隔
# 2. 扫描到 SAVE_STATE_FILE_INTERVAL 个文件
SAVE_STATE_INTERVAL = 20  # 新增：状态保存间隔（秒），默认60秒保存一次
SAVE_STATE_FILE_INTERVAL = 10000  # 新增：每扫描 N 个文件保存状态一次，默认100000个文件保存一次
OUTPUT_FILE = "all_files.json"  # 输出文件，保存所有扫描到的文件信息（JSON格式）
DOWNLOAD_DIR = "d2"  # 新增：下载文件保存目录
DOWNLOAD_THREADS = 1      # 新增：下载线程数（不要设置太大）
MATCH_RULES = []
SKIP_SCAN_AND_GOTO_DOWNLOAD = False  # 新增：是否跳过扫描直接下载匹配文件，读取 OUTPUT_FILE 中的信息，找出需要下载的文件，然后下载（DOWNLOAD_THREADS 个线程）
# ===========================================================

class SmartFTP:
    def __init__(self, host, port=21, username='anonymous', password='', 
                 timeout=10, encoding=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.encoding = encoding or self.detect_encoding()
        self.ftp = None
        
    def detect_encoding(self):
        """探测FTP服务器编码"""
        common_encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port, self.timeout)
            ftp.login(self.username, self.password)
            
            # 获取目录列表进行编码分析
            lines = []
            try:
                ftp.retrlines('LIST', lines.append)
            except:
                # 如果LIST命令失败，尝试NLST
                try:
                    files = ftp.nlst()
                    lines = [f for f in files if f]
                except:
                    pass
            
            ftp.quit()
            
            if lines:
                test_text = '\n'.join(lines)
                test_bytes = test_text.encode('latin-1', errors='ignore')
                
                # 使用chardet检测
                result = chardet.detect(test_bytes)
                if result['encoding'] and result['confidence'] > 0.6:
                    detected = result['encoding'].lower()
                    if detected in common_encodings:
                        return detected
                
                # 逐个尝试
                for encoding in common_encodings:
                    try:
                        decoded = test_bytes.decode(encoding)
                        if self._is_valid_path(decoded):
                            return encoding
                    except:
                        continue
                        
        except Exception as e:
            print(f"编码检测失败: {e}")
            
        return 'utf-8'  # 默认fallback
    
    def _is_valid_path(self, text):
        """检查文本是否看起来像有效的路径"""
        if not text:
            return False
        # 简单的启发式检查
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_/\\ ()[]{}')
        invalid_ratio = sum(1 for c in text if c not in valid_chars) / len(text)
        return invalid_ratio < 0.3  # 允许少量非法字符
    
    def connect(self):
        """建立FTP连接"""
        try:
            self.ftp = ftplib.FTP()
            self.ftp.encoding = self.encoding
            self.ftp.connect(self.host, self.port, self.timeout)
            self.ftp.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"FTP连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开FTP连接"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
    
    def get_file_list(self, path='.'):
        """获取详细的文件列表"""
        lines = []
        try:
            self.ftp.retrlines(f'LIST {path}', lines.append)
        except Exception as e:
            print(f"获取文件列表失败 {path}: {e}")
        return lines
    
    def nlst(self, path='.'):
        """获取文件列表，自动处理编码"""
        try:
            return self.ftp.nlst(path)
        except UnicodeEncodeError:
            # 如果路径编码有问题，尝试使用原始字节
            if isinstance(path, str):
                path_bytes = path.encode(self.encoding)
                files = []
                self.ftp.retrlines(f'NLST {path_bytes}'.encode('ascii'), files.append)
                return [f.decode(self.encoding) for f in files]
            raise
        except Exception as e:
            print(f"NLST命令失败 {path}: {e}")
            return []
    
    def mlsd(self, path='.'):
        """获取目录详细列表（MLSD命令）"""
        entries = []
        try:
            # 尝试使用MLSD命令（更现代的方式）
            for entry in self.ftp.mlsd(path):
                entries.append(entry)
        except Exception as e:
            print(f"MLSD命令失败 {path}，尝试使用LIST: {e}")
            # 如果MLSD失败，回退到LIST命令解析
            lines = self.get_file_list(path)
            for line in lines:
                try:
                    # 解析LIST命令的输出（Unix格式）
                    parts = line.split()
                    if len(parts) >= 9:
                        # 第一个字符表示类型：d=目录，-=文件
                        file_type = 'dir' if parts[0].startswith('d') else 'file'
                        filename = ' '.join(parts[8:])
                        # 尝试解析时间（简化处理）
                        modify = "".join(parts[5:8])  # 月日年或年月日
                        size = parts[4] if file_type == 'file' else 0
                        perm = parts[0]
                        entries.append((filename, {'type': file_type, 'modify': modify, 'size': size, 'perm': perm}))
                except Exception as parse_error:
                    print(f"解析LIST输出失败: {parse_error}")
        return entries
    
    def cwd(self, path):
        """切换目录，处理编码问题"""
        try:
            return self.ftp.cwd(path)
        except Exception as e:
            print(f"切换目录失败 {path}: {e}")
            # 尝试使用原始字节编码
            try:
                path_bytes = path.encode(self.encoding)
                return self.ftp.cwd(path_bytes)
            except Exception as e2:
                print(f"字节编码切换目录也失败 {path}: {e2}")
                raise
    
    def download_file(self, remote_path, local_path):
        """下载文件到本地"""
        try:
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except Exception as e:
            print(f"下载文件失败 {remote_path}: {e}")
            return False

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败 {file_path}: {e}")
        return None

# 创建全局线程池
_async_thread_pool = ThreadPoolExecutor()

def _async(func: Callable, *args: Any, **kwargs: Any) -> Future:
    """异步执行函数
    Args:
        func: 要异步执行的函数
        *args, **kwargs: 函数的参数
    
    Returns:
        Future对象，可以通过future.result()获取结果，如果不需要结果可以忽略返回值
    """
    return _async_thread_pool.submit(func, *args, **kwargs)

def get_unique_filename(directory, filename):
    """生成唯一的文件名，避免重复"""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    file_path = os.path.join(directory, new_filename)
    
    # 如果文件不存在，直接返回原文件名
    if not os.path.exists(file_path):
        return new_filename
    
    # 如果文件存在，尝试添加序号
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    
    return new_filename

def download_worker(worker_id, host, port, username, password, download_queue, 
                   download_dir, file_hash_map, hash_lock, success_count, error_count):
    """下载工作线程"""
    ftp = SmartFTP(host, port, username, password)
    
    if not ftp.connect():
        print(f"下载线程 {worker_id} 连接FTP失败")
        return
    
    print(f"下载线程 {worker_id} 已连接")
    
    while True:
        try:
            remote_path = download_queue.get(timeout=10)
        except queue.Empty:
            break
        
        try:
            # 提取文件名
            filename = os.path.basename(remote_path)
            print(f"线程{worker_id} 正在下载: {filename}")
            
            # 创建临时文件路径
            temp_filename = os.path.join(download_dir, f"temp_{worker_id}_{int(time.time())}")
            
            # 下载文件到临时位置
            if not ftp.download_file(remote_path, temp_filename):
                error_count[0] += 1
                download_queue.task_done()
                continue
            
            # 计算下载文件的哈希值
            file_hash = calculate_file_hash(temp_filename)
            if not file_hash:
                error_count[0] += 1
                os.remove(temp_filename)
                download_queue.task_done()
                continue
            
            # 检查哈希是否已存在
            with hash_lock:
                existing_file = None
                for existing_hash, existing_path in file_hash_map.items():
                    if existing_hash == file_hash:
                        existing_file = existing_path
                        break
            
            final_filename = filename
            if existing_file:
                # 文件内容相同，删除临时文件，记录为跳过
                os.remove(temp_filename)
                print(f"跳过重复文件: {filename} (与 {os.path.basename(existing_file)} 内容相同)")
            else:
                # 文件内容不同，需要处理文件名冲突
                final_filename = get_unique_filename(download_dir, filename)
                final_path = os.path.join(download_dir, final_filename)
                
                # 移动临时文件到最终位置
                shutil.move(temp_filename, final_path)
                
                # 记录文件哈希
                with hash_lock:
                    file_hash_map[file_hash] = final_path
                
                print(f"下载完成: {final_filename}")
                success_count[0] += 1
            
        except Exception as e:
            print(f"下载文件失败 {remote_path}: {e}")
            error_count[0] += 1
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        
        download_queue.task_done()
    
    ftp.disconnect()
    print(f"下载线程 {worker_id} 已完成")

def download_matched_files(matched_files):
    """下载所有匹配的文件"""
    if not matched_files:
        print("没有匹配的文件需要下载")
        return
    
    # 创建下载目录
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"下载目录: {os.path.abspath(DOWNLOAD_DIR)}")
    
    # 初始化下载队列
    download_queue = queue.Queue()
    for file_path in matched_files:
        download_queue.put(file_path)
    
    # 初始化文件哈希映射（用于去重）
    file_hash_map = {}
    hash_lock = threading.Lock()
    
    # 扫描已存在文件的哈希
    print("扫描已存在文件的哈希值...")
    for filename in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                file_hash_map[file_hash] = file_path
    
    print(f"发现 {len(file_hash_map)} 个已存在的唯一文件")
    
    # 统计计数器
    success_count = [0]
    error_count = [0]
    
    # 启动下载线程
    threads = []
    for i in range(min(DOWNLOAD_THREADS, len(matched_files))):
        t = threading.Thread(
            target=download_worker,
            args=(i+1, IP, PORT, USER, PASSWORD, download_queue, DOWNLOAD_DIR, 
                  file_hash_map, hash_lock, success_count, error_count)
        )
        t.daemon = True
        t.start()
        threads.append(t)
    
    # 显示下载进度
    total_files = len(matched_files)
    print(f"开始下载 {total_files} 个匹配文件，使用 {DOWNLOAD_THREADS} 个线程")
    
    try:
        # 等待下载完成，同时显示进度
        while not download_queue.empty():
            remaining = download_queue.qsize()
            downloaded = total_files - remaining
            print(f"下载进度: {downloaded}/{total_files} (剩余: {remaining})")
            time.sleep(5)
        
        download_queue.join()
        print("所有文件下载完成！")
        
    except KeyboardInterrupt:
        print("用户中断下载")
    
    # 输出下载统计
    print(f"下载统计:")
    print(f"成功下载: {success_count[0]} 个文件")
    print(f"下载失败: {error_count[0]} 个文件")
    print(f"跳过重复: {total_files - success_count[0] - error_count[0]} 个文件")
    print(f"保存位置: {os.path.abspath(DOWNLOAD_DIR)}")

def parse_mlsd_time(mod_time_str: str) -> Tuple[str, int]:
    """解析MLSD时间格式，返回格式化时间和时间戳"""
    try:
        # 处理MLSD格式：20251104075035.799
        if '.' in mod_time_str:
            mod_time_str = mod_time_str.split('.')[0]  # 去掉毫秒部分
        
        # 解析标准MLSD时间格式：YYYYMMDDHHMMSS
        if len(mod_time_str) == 14 and mod_time_str.isdigit():
            dt = datetime.datetime.strptime(mod_time_str, "%Y%m%d%H%M%S")
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            timestamp = int(dt.timestamp())
            return formatted_time, timestamp
        
        # 处理其他可能的时间格式
        formats = [
            "%Y%m%d%H%M%S",  # 标准格式
            "%Y-%m-%d %H:%M",  # 其他可能格式
            "%b %d %H:%M",    # 简写月份格式
        ]
        
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(mod_time_str, fmt)
                # 如果是简写格式且没有年份，使用当前年份
                if fmt == "%b %d %H:%M":
                    dt = dt.replace(year=datetime.datetime.now().year)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = int(dt.timestamp())
                return formatted_time, timestamp
            except:
                continue
                
    except Exception as e:
        print(f"时间解析失败 '{mod_time_str}': {e}")
    
    # 如果所有格式都失败，返回当前时间
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(current_time.timestamp())
    return formatted_time, timestamp

def matches_rule(file_info: Dict, rule: Dict) -> bool:
    """检查文件是否匹配给定规则"""
    # 只对文件进行匹配检查
    if file_info["type"] != "file":
        return False
    
    filename = file_info["name"]
    
    # 检查文件名包含所有include词
    if rule["include"]:
        for word in rule["include"]:
            if word.lower() not in filename.lower():
                return False
    
    # 检查文件扩展名
    if rule["suffix"]:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [s.lower() for s in rule["suffix"]]:
            return False
    
    # 修复时间匹配逻辑
    if rule["starttime"] > 0:
        try:
            # 文件时间戳 小于等于 规则开始时间 返回 False
            if file_info.get("timestamp", 0) <= rule["starttime"]: 
                return False
        except Exception:
            return False
    
    # 检查结束时间
    if rule["endtime"] > 0:
        try:
            # 文件时间戳 大于等于 规则结束时间 返回 False
            if file_info.get("timestamp", 0) >= rule["endtime"]:
                return False
        except Exception:
            return False
    
    return True

def filter_files(all_files: List[Dict], rules: List[Dict]) -> List[str]:
    """用规则过滤文件路径（匹配任意一条规则就保留）"""
    filtered = []
    for file_info in all_files:
        if file_info["type"] == "file" and any(matches_rule(file_info, rule) for rule in rules):
            filtered.append(file_info["path"])
    return sorted(filtered)  # 按路径顺序排序

def save_state(queue: queue.Queue, scanned: set, state_file: str, all_files: List[Dict]):
    """保存当前扫描状态（目录队列+已扫描目录+已发现文件）"""
    try:
        state = {
            "queue": list(queue.queue),  # 队列转列表
            "scanned": list(scanned),
            "all_files": all_files,  # 保存所有已扫描的文件信息
            "all_files_count": len(all_files),
            "save_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(state_file, "w", encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"状态已保存到 {state_file} (队列: {queue.qsize()}, 文件: {len(all_files)})")
    except Exception as e:
        print(f"保存状态失败: {e}")

def load_state(state_file: str) -> Tuple[queue.Queue, set, List[Dict]]:
    """加载上次保存的状态，若文件不存在则初始化"""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding='utf-8') as f:
                state = json.load(f)
            q = queue.Queue()
            for item in state.get("queue", []):
                q.put(item)
            scanned_set = set(state.get("scanned", []))
            all_files = state.get("all_files", [])
            print(f"加载状态成功: {len(all_files)} 个文件, 队列: {q.qsize()}")
            return q, scanned_set, all_files
        except Exception as e:
            print(f"加载状态失败: {e}")
    
    # 初始化新队列
    q = queue.Queue()
    q.put((DIRECTORY, 0))  # 初始队列: (目录路径, 深度)
    return q, set(), []

def incremental_scan_needed(scanned_files: List[Dict], current_files: List[Dict]) -> bool:
    """检查是否需要增量扫描（比较文件数量和时间戳）"""
    if len(scanned_files) != len(current_files):
        return True
    
    # 如果文件数量相同，比较最新修改时间
    if scanned_files:
        latest_scanned = max(f.get("timestamp", 0) for f in scanned_files)
        latest_current = max(f.get("timestamp", 0) for f in current_files)
        if latest_current > latest_scanned:
            return True
    
    return False

def state_saver_worker(q, scanned, state_file, all_files, all_files_lock, 
                      file_count, file_count_lock, stop_event):
    """状态保存线程，定期保存扫描状态"""
    last_save_time = time.time()
    last_file_count = file_count[0]
    
    while not stop_event.is_set():
        current_time = time.time()
        
        # 检查是否需要保存状态
        need_save = False
        
        # 条件1：达到时间间隔
        if current_time - last_save_time >= SAVE_STATE_INTERVAL:
            need_save = True
        
        # 条件2：达到文件数量间隔
        with file_count_lock:
            current_file_count = file_count[0]
            if current_file_count - last_file_count >= SAVE_STATE_FILE_INTERVAL:
                need_save = True
        
        if need_save:
            with all_files_lock:
                _async(save_state,q, scanned, state_file, all_files)
                # save_state(q, scanned, state_file, all_files)
            last_save_time = current_time
            last_file_count = current_file_count
        
        # 每5秒检查一次
        stop_event.wait(5)
    
    # 线程结束前保存一次状态
    with all_files_lock:
        # _async(save_state,q, scanned, state_file, all_files).result()
        save_state(q, scanned, state_file, all_files)

def ftp_scan_worker(
    worker_id: int,
    host: str,
    port: int,
    username: str,
    password: str,
    q: queue.Queue, 
    all_files: List[Dict], 
    all_files_lock: threading.Lock,
    scanned: set,
    scanned_lock: threading.Lock,
    max_depth: int,
    state_file: str,
    file_count: list,  # 使用列表来共享计数器
    file_count_lock: threading.Lock
):
    """单个线程的FTP扫描任务"""
    # 为每个线程创建独立的FTP连接
    ftp = SmartFTP(host, port, username, password)
    
    if not ftp.connect():
        print(f"工作线程 {worker_id} 连接FTP失败")
        return
    
    print(f"工作线程 {worker_id} 已连接，使用编码: {ftp.encoding}")
    
    while True:
        try:
            # 从队列取任务（非阻塞方式）
            path, depth = q.get(timeout=5)
        except queue.Empty:
            # 队列为空，检查是否所有任务都完成
            if q.unfinished_tasks == 0:
                break
            continue
        
        # 避免重复扫描
        with scanned_lock:
            if path in scanned:
                q.task_done()
                continue
            scanned.add(path)
        
        print(f"线程{worker_id} 正在扫描: {path} (深度: {depth})")
        
        try:
            # 切换到当前目录
            ftp.cwd(path)
            # 获取目录列表
            entries = ftp.mlsd()
        except Exception as e:
            print(f"线程{worker_id} 目录 {path} 扫描失败: {e}")
            q.task_done()
            continue
        
        # 处理每个条目
        for name, info in entries:
            # 使用正确的路径分隔符
            full_path = path.rstrip('/') + '/' + name.lstrip('/')
            
            # 跳过当前/上层目录
            if name in [".", ".."]:
                continue
            
            # 解析文件信息
            file_type = info.get("type", "file")
            size = info.get("size", 0)
            permissions = info.get("perm", "")
            mod_time_str = info.get("modify", "")
            
            # 解析时间
            modify_time, timestamp = parse_mlsd_time(mod_time_str)
            
            # 创建文件信息字典
            file_info = {
                "path": full_path,
                "name": name,
                "size": int(size) if file_type == "file" else 0,
                "modify_time": modify_time,
                "create_time": "N/A",  # FTP通常不提供创建时间
                "permissions": permissions,
                "type": file_type,
                "timestamp": timestamp
            }
            
            # 添加到总文件列表
            with all_files_lock:
                all_files.append(file_info)
            
            # 如果是目录且深度未超限，添加到队列
            if file_type == "dir" and depth < max_depth:
                q.put((full_path, depth + 1))
            
            # 更新文件计数器
            with file_count_lock:
                file_count[0] += 1
        
        q.task_done()
    
    # 断开连接
    ftp.disconnect()
    print(f"工作线程 {worker_id} 已完成")

def skip_scan_and_download():
    """跳过扫描，直接下载匹配的文件"""
    if not os.path.exists(OUTPUT_FILE):
        print(f"错误：输出文件 {OUTPUT_FILE} 不存在")
        return
    
    try:
        # 读取之前扫描的结果
        with open(OUTPUT_FILE, "r", encoding='utf-8') as f:
            all_files = json.load(f)
        
        print(f"从 {OUTPUT_FILE} 加载了 {len(all_files)} 个文件信息")
        
        # 应用匹配规则
        if MATCH_RULES:
            matched_files = filter_files(all_files, MATCH_RULES)
            print(f"找到 {len(matched_files)} 个匹配的文件")
            
            if matched_files:
                download_matched_files(matched_files)
            else:
                print("没有找到匹配的文件")
        else:
            print("未设置匹配规则")
            
    except Exception as e:
        print(f"跳过扫描直接下载失败: {e}")

def main():
    # 检查是否跳过扫描直接下载
    if SKIP_SCAN_AND_GOTO_DOWNLOAD:
        print("跳过扫描，直接下载匹配的文件")
        skip_scan_and_download()
        return
    
    print(f"开始扫描FTP: {IP}:{PORT} | 目录: {DIRECTORY} | 深度: {MAX_DEPTH}")
    
    # 加载状态或初始化
    q, scanned_set, all_files = load_state(STATE_FILE)
    
    # 检查是否需要全量扫描
    if not all_files:
        print("未找到历史扫描记录，开始全量扫描...")
    else:
        print(f"找到历史扫描记录: {len(all_files)} 个文件")
    
    # 初始化锁和计数器
    all_files_lock = threading.Lock()
    scanned_lock = threading.Lock()
    file_count = [len(all_files)]  # 使用列表以便在线程间共享
    file_count_lock = threading.Lock()
    
    # 创建状态保存线程
    stop_event = threading.Event()
    state_saver_thread = threading.Thread(
        target=state_saver_worker,
        args=(q, scanned_set, STATE_FILE, all_files, all_files_lock, 
              file_count, file_count_lock, stop_event)
    )
    state_saver_thread.daemon = True
    state_saver_thread.start()
    
    # 启动扫描线程
    threads = []
    for i in range(THREADS):
        t = threading.Thread(
            target=ftp_scan_worker,
            args=(i+1, IP, PORT, USER, PASSWORD, q, all_files, all_files_lock, 
                  scanned_set, scanned_lock, MAX_DEPTH, STATE_FILE, file_count, file_count_lock)
        )
        t.daemon = True
        t.start()
        threads.append(t)
    
    # 等待队列完成
    try:
        q.join()
        print("所有目录扫描完成！正在处理文件...")
    except KeyboardInterrupt:
        print("用户中断扫描，保存当前状态...")
        # 通知状态保存线程停止
        stop_event.set()
        state_saver_thread.join(timeout=5)
        _async(save_state,q, scanned_set, STATE_FILE, all_files).result()
        # save_state(q, scanned_set, STATE_FILE, all_files)
        return
    
    # 停止状态保存线程
    stop_event.set()
    state_saver_thread.join(timeout=5)
    
    # 保存最终状态（确保无遗漏）
    save_state(q, scanned_set, STATE_FILE, all_files)
    
    # 保存所有文件到JSON
    try:
        with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
            json.dump(all_files, f, indent=2, ensure_ascii=False)
        print(f"所有文件已保存到 {OUTPUT_FILE} (共 {len(all_files)} 个项目)")
        
        # 统计信息
        file_count = sum(1 for item in all_files if item["type"] == "file")
        dir_count = sum(1 for item in all_files if item["type"] == "dir")
        print(f"统计: {file_count} 个文件, {dir_count} 个文件夹")
        
    except Exception as e:
        print(f"保存文件列表失败: {e}")
    
    # 应用匹配规则
    if MATCH_RULES:
        matched_files = filter_files(all_files, MATCH_RULES)
        match_output = "matched_files.txt"
        try:
            with open(match_output, "w", encoding='utf-8') as f:
                f.write("\n".join(matched_files))
            print(f"匹配结果已保存到 {match_output} (共 {len(matched_files)} 个文件)")
            
            # 下载匹配的文件
            if matched_files:
                print(f"开始下载 {len(matched_files)} 个匹配文件...")
                download_matched_files(matched_files)
            else:
                print("没有找到匹配的文件，跳过下载")
                
        except Exception as e:
            print(f"保存匹配结果失败: {e}")
    else:
        print("未设置匹配规则，跳过文件过滤和下载")
    
    
    
    print("扫描和下载完成！")
    print("如果要修改规则，请编辑脚本顶部的MATCH_RULES配置")

if __name__ == "__main__":
    main()