# -*- coding: utf-8 -*-
# language: English
import sys
import os
from pathlib import Path
import argparse
import json
import logging
import datetime

base_dir = Path(__file__).resolve().parent.parent.parent

log_dir = base_dir / 'log'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'get_dir_detalis.log'

# 先配置日志，然后再使用日志功能
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=str(log_file),
    filemode='a'
    # encoding='utf-8' # 低版本不支持
)

# 现在再记录开始信息
logging.info(f"Start get dir details at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def get_file_info(file_path):
    """获取文件或目录的详细信息"""
    stat_info = file_path.stat()
    
    return {
        "name": file_path.name,
        "type": "dir" if file_path.is_dir() else "file",
        "relative_path": str(file_path.relative_to(base_dir)),
        "absolute_path": str(file_path.resolve()),
        "date": datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        "timestamp": stat_info.st_ctime,
        "update": datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        "size": stat_info.st_size if file_path.is_file() else None
    }

def main():
    parser = argparse.ArgumentParser(description='Get dir details')
    parser.add_argument('--dir',"-d", type=str, default='dist', help='Path to the directory (default: dist)')
    parser.add_argument('--json',"-j", type=str, default=None, help='Output file as JSON')
    parser.add_argument('--output-to-console', '-c', action='store_true',default=False, help='Output to console')
    parser.add_argument('--get-latest-file-name', '-l', action='store_true', help='Get latest file name')

    args = parser.parse_args()

    dist_dir = Path(args.dir)
    dist_dir = base_dir / dist_dir
    logging.info(f"base_dir: {base_dir}")
    logging.info(f"Directory: {dist_dir}")
    if not dist_dir.exists():
        logging.error(f"Directory does not exist: {dist_dir}")
        sys.exit(1)

    # 获取目录下所有文件和子目录
    res = {
        "directory": str(dist_dir.relative_to(base_dir)),
        "total_files": 0,
        "total_dirs": 0,
        "items": []
    }
    
    try:
        # 遍历目录
        for item in dist_dir.iterdir():
            try:
                item_info = get_file_info(item)
                res["items"].append(item_info)
                
                if item.is_dir():
                    res["total_dirs"] += 1
                else:
                    res["total_files"] += 1
                    
            except Exception as e:
                logging.warning(f"Failed to get info for {item}: {e}")
                continue
        
        # 按名称排序
        res["items"].sort(key=lambda x: x["name"])
            
        logging.info(f"Successfully processed directory: {res['total_files']} files, {res['total_dirs']} directories")

        logging.info(f"Directory details:")
        logging.info(f"\n{json.dumps(res, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        logging.error(f"Error processing directory: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    
    # 输出结果
    if args.json:
        # 保存到JSON文件
        logging.info(f"JSON file: {args.json}")
        json_path = base_dir / args.json
        os.makedirs(json_path.parent, exist_ok=True)
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=2, ensure_ascii=False)
            print(f"Directory details saved to: {json_path}")
        except Exception as e:
            logging.error(f"Failed to save JSON file {json_path}: {e}")
    
    if args.output_to_console:
        # 打印到控制台
        print(json.dumps(res, indent=2, ensure_ascii=False))
    
    if args.get_latest_file_name:
        # 获取最新文件名称
        latest_file = max(res["items"], key=lambda x: x["timestamp"])
        print(f"{latest_file['name']}")
    


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    finally:
        logging.info(f"Finish get dir details at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")