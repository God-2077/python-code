import os
import mimetypes
import magic
import argparse
from collections import Counter
from rich import print as rprint
from rich.progress import Progress, BarColumn, TimeRemainingColumn

class FileTypeDetector:
    def __init__(self):
        self.mime_detector = magic.Magic(mime=True)
        self.description_detector = magic.Magic()
        mimetypes.init()  # 初始化MIME类型数据库
    
    def detect_by_extension(self, file_path):
        """通过文件扩展名检测类型"""
        _, extension = os.path.splitext(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        return {
            "method": "扩展名",
            "extension": extension.lower(),
            "mime_type": mime_type
        }
    
    def detect_by_content(self, file_path):
        """通过文件内容检测真实类型"""
        try:
            mime_type = self.mime_detector.from_file(file_path)
            description = self.description_detector.from_file(file_path)
            return {
                "method": "内容分析",
                "mime_type": mime_type,
                "description": description
            }
        except Exception as e:
            return {
                "method": "内容分析",
                "error": f"检测失败: {str(e)}"
            }
    
    def detect_magic_number(self, file_path, bytes=8):
        """读取文件魔数（文件头标识）"""
        try:
            with open(file_path, 'rb') as f:
                magic_bytes = f.read(bytes)
                return {
                    "method": "魔数分析",
                    "magic_number": magic_bytes.hex(' ', 1).upper(),
                    "bytes": bytes
                }
        except Exception as e:
            return {
                "method": "魔数分析",
                "error": f"读取失败: {str(e)}"
            }
    
    def comprehensive_detection(self, file_path):
        """综合检测文件类型"""
        results = {
            "file": os.path.basename(file_path),
            "path": os.path.abspath(file_path),
            "size": f"{os.path.getsize(file_path)/1024:.2f} KB",
            "detections": []
        }
        
        # 执行所有检测方法
        results["detections"].append(self.detect_by_extension(file_path))
        results["detections"].append(self.detect_by_content(file_path))
        results["detections"].append(self.detect_magic_number(file_path))
        
        return results


def analyze_directory(directory):
    """批量分析目录及其所有子目录中的文件类型（带进度条）"""
    detector = FileTypeDetector()
    type_counter = Counter()
    
    # 收集所有文件路径
    all_files = []
    for root, _, files in os.walk(directory):
        all_files.extend(os.path.join(root, f) for f in files)
    
    total_files = len(all_files)
    
    # 初始化进度条
    progress_desc = f"[bold green]扫描目录: {os.path.basename(directory)}"
    with Progress(
        "[bold blue]{task.description}",  # 手动显示任务描述,
        BarColumn(bar_width=60),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        expand=True
    ) as progress:
        task = progress.add_task(progress_desc, total=total_files)
        
        # 处理所有文件并更新进度条
        for i, file_path in enumerate(all_files,start=1):
            result = detector.detect_by_content(file_path)
            mime = result.get('mime_type', 'unknown')
            type_counter[mime] += 1
            progress.update(task, advance=1, description=f"{progress_desc} [{i}/{total_files}]")
            
    
    # 显示统计结果
    rprint("\n📊 [bold green]文件类型分布统计:[/]")
    for mime_type, count in type_counter.most_common():
        rprint(f"  - [cyan]{mime_type} ({round(((count/total_files)*100), 2)}%)[/]: [yellow]{count}[/]个文件")

def display_file_results(result):
    """显示文件检测结果（添加颜色）"""
    rprint(f"\n🔍 [bold green]文件分析报告:[/] [yellow]{result['file']}[/]")
    rprint(f"📂 [bold]路径:[/] [cyan]{result['path']}[/]")
    rprint(f"📏 [bold]大小:[/] [cyan]{result['size']}[/]")
    
    rprint("\n🔧 [bold green]检测方法结果:[/]")
    for detection in result["detections"]:
        # 为不同检测方法添加不同颜色
        if detection['method'] == "扩展名":
            color = "bold yellow"
        elif detection['method'] == "内容分析":
            color = "bold magenta"
        else:  # 魔数分析
            color = "bold cyan"
        
        rprint(f"\n▸ [{color}]{detection['method']}:[/]")
        for k, v in detection.items():
            if k != "method":
                # 为不同信息类型添加颜色
                if k == "magic_number":
                    rprint(f"  - {k}: [bold green]{v}[/]")
                elif k == "error":
                    rprint(f"  - {k}: [red]{v}[/]")
                else:
                    rprint(f"  - {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='文件类型探测器')
    parser.add_argument('-f', '--file', help='分析单个文件')
    parser.add_argument('-d', '--dir', help='分析整个目录')
    parser.add_argument('path', nargs='?', help='自动检测文件或目录')
    args = parser.parse_args()

    detector = FileTypeDetector()
    
    # 自动检测逻辑：优先使用-f或-d，否则使用位置参数
    if args.file:
        if not os.path.exists(args.file):
            rprint(f"[bold red]错误: 文件 '{args.file}' 不存在！[/]")
            exit(1)
        result = detector.comprehensive_detection(args.file)
        display_file_results(result)
    
    elif args.dir:
        if not os.path.exists(args.dir):
            rprint(f"[bold red]错误: 目录 '{args.dir}' 不存在！[/]")
            exit(1)
        analyze_directory(args.dir)
    
    elif args.path:
        # 自动检测文件或目录类型
        if os.path.isfile(args.path):
            result = detector.comprehensive_detection(args.path)
            display_file_results(result)
        elif os.path.isdir(args.path):
            analyze_directory(args.path)
        else:
            rprint(f"[bold red]错误: '{args.path}' 不是有效的文件或目录！[/]")
    
    else:
        rprint("[bold red]请提供文件或目录路径！[/]")
        rprint("使用方法:")
        rprint("  分析文件: [cyan]python t.py -f 文件路径[/] 或 [cyan]python t.py 文件路径[/]")
        rprint("  分析目录: [cyan]python t.py -d 目录路径[/] 或 [cyan]python t.py 目录路径[/]")
