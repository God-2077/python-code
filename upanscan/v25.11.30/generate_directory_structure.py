import os
import time
from datetime import datetime
from rich import print

def get_permissions_str(file_path):
    """获取文件/目录的权限字符串"""
    try:
        mode = os.stat(file_path).st_mode
        permissions = []
        # 读权限
        permissions.append('R' if mode & 0o400 else '-')
        # 写权限
        permissions.append('W' if mode & 0o200 else '-')
        # 执行权限
        permissions.append('X' if mode & 0o100 else '-')
        return ''.join(permissions)
    except:
        return '---'

def get_file_info(file_path, current_depth, max_depth):
    """获取单个文件/目录的信息"""
    try:
        stat_info = os.stat(file_path)
        name = os.path.basename(file_path)
        is_dir = os.path.isdir(file_path)
        
        # 格式化时间
        modify_time = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        create_time = datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        
        file_info = {
            "path": file_path,
            "name": name,
            "size": stat_info.st_size,
            "modify_time": modify_time,
            "create_time": create_time,
            "permissions": get_permissions_str(file_path),
            "type": "dir" if is_dir else "file",
            "timestamp": int(stat_info.st_mtime),
            "items_count": 0,
            "items_dir_count": 0,
            "items_files_count": 0,
            "items": []
        }
        
        # 如果是目录且未达到最大深度，递归获取子项
        if is_dir and current_depth < max_depth:
            try:
                items = []
                dir_count = 0
                file_count = 0
                
                for item in os.listdir(file_path):
                    item_path = os.path.join(file_path, item)
                    item_info = get_file_info(item_path, current_depth + 1, max_depth)
                    items.append(item_info)
                    
                    if item_info["type"] == "dir":
                        dir_count += 1
                    else:
                        file_count += 1
                
                file_info["items"] = items
                file_info["items_count"] = len(items)
                file_info["items_dir_count"] = dir_count
                file_info["items_files_count"] = file_count
                
            except PermissionError:
                # 无权限访问的目录
                pass
                
        return file_info
        
    except (OSError, PermissionError) as e:
        # 处理无法访问的文件/目录
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": 0,
            "modify_time": "1970-01-01 00:00:00",
            "create_time": "1970-01-01 00:00:00",
            "permissions": "---",
            "type": "unknown",
            "timestamp": 0,
            "items_count": 0,
            "items_dir_count": 0,
            "items_files_count": 0,
            "items": []
        }

def generate_directory_structure(path, deep=1):
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
    if not os.path.exists(path):
        raise ValueError(f"路径不存在: {path}")
    
    result = []
    
    # 如果传入的是文件，直接返回文件信息
    if os.path.isfile(path):
        file_info = get_file_info(path, 0, deep)
        result.append(file_info)
        return result
    
    # 如果是目录，获取目录内容
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_info = get_file_info(item_path, 0, deep)
            result.append(item_info)
    except PermissionError:
        # 无权限访问目录
        pass
    
    return result

# 使用示例
if __name__ == "__main__":
    # 示例用法
    path = "E:\\"  # 替换为您的路径
    deep = 8  # 扫描深度
    
    try:
        structure = generate_directory_structure(path, deep)
        
        # 打印结果（格式化输出）
        # print(structure)
        
        with open("data.json", "w", encoding="utf-8") as file:
            import json
            json.dump(structure, file, indent=2, ensure_ascii=False)
        
        # 保存到文件
        # with open("directory_structure.json", "w", encoding="utf-8") as f:
        #     json.dump(structure, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"错误: {e}")