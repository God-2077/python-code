import os
import hashlib
import sys

def calculate_md5(file_path):
    """计算文件的 MD5 值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"无法计算 {file_path} 的 MD5: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python md5.py directory")
        sys.exit(1)
    directory = sys.argv[1]
    # directory = "./package"
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在。")
        return
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是一个目录。")
        return
    
    # 收集所有文件的相对路径和 MD5 值
    file_md5_list = []
    max_filename_len = 0
    
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, directory)
            md5 = calculate_md5(file_path)
            if md5:
                file_md5_list.append((rel_path, md5))
                # 记录最长的文件名长度
                if len(rel_path) > max_filename_len:
                    max_filename_len = len(rel_path)
    
    # 设置最小间距和总宽度
    min_spacing = 4
    total_width = max_filename_len + min_spacing + 32  # MD5长度固定为32
    
    # 打印标题行
    print(f"{'文件名'.ljust(max_filename_len)}{' ' * min_spacing}MD5 值")
    print("-" * total_width)
    
    # 对齐打印文件和MD5
    for rel_path, md5 in file_md5_list:
        print(f"{rel_path.ljust(max_filename_len)}{' ' * min_spacing}{md5}")

if __name__ == "__main__":
    main()