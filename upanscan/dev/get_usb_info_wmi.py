import wmi
import os
import sys
import time

# 配置区

MAX_DEEP = 5



try:
    from rich import print
except ImportError:
    pass
def get_usb_info_wmi():
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
    c = wmi.WMI()
    usb_drives = []
    
    # 获取逻辑磁盘信息
    for disk in c.Win32_LogicalDisk(DriveType=2):  # DriveType=2 表示可移动驱动器
        try:
            drive_info = {
                'device': disk.DeviceID,
                'volume_name': disk.VolumeName if disk.VolumeName else "未命名",
                'size': int(disk.Size) if disk.Size else 0,
                'free_space': int(disk.FreeSpace) if disk.FreeSpace else 0,
                'file_system': disk.FileSystem,
                'serial_number': disk.VolumeSerialNumber if disk.VolumeSerialNumber else "未知"
            }
            usb_drives.append(drive_info)
        except Exception as e:
            continue
    
    return usb_drives

def judgment_path(path: str):
    if os.path.isdir(path):
        return "dir"
    elif os.path.isfile(path):
        return "file"
    else:
        return "unknown"

# def sacn_usb_files(path: str, deep: int = 0):
#     if deep > MAX_DEEP:
#         return []
    
#     items = []
#     try:
#         for entry in os.scandir(path):
#             item_info = {
#                 'name': entry.name,
#                 'path': entry.path,
#                 'type': judgment_path(entry.path),
#                 'size': int(entry.stat().st_size) if entry.is_file() else 0,
#             }
#             items.append(item_info)
            
#             if entry.is_dir(follow_symlinks=False):
#                 items.extend(sacn_usb_files(entry.path, deep + 1))
#     except PermissionError:
#         pass  # 忽略权限错误
#     except Exception as e:
#         print(f"扫描路径时出错: {e}")
    
#     return items

    


# 使用示例
if __name__ == "__main__":
    try:
        usb_drives = get_usb_info_wmi()
        
        print("通过WMI获取的U盘信息：")
        print("-" * 60)
        
        for i, drive in enumerate(usb_drives, 1):
            print(f"U盘 {i}:")
            print(f"  设备名: {drive['device']}")
            print(f"  卷标: {drive['volume_name']}")
            print(f"  总大小: {drive['size'] / (1024**3):.2f} GB")
            print(f"  可用空间: {drive['free_space'] / (1024**3):.2f} GB")
            print(f"  文件系统: {drive['file_system']}")
            print(f"  序列号: {drive['serial_number']}")
            print("-" * 60)
    except Exception as e:
        print(f"错误: {e}")
        print("请确保已安装pywin32: pip install pywin32")