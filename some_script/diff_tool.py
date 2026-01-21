#!/usr/bin/env python3
"""
Diff 工具: 比较文件或文件夹差异，支持彩色输出
修复了多余空行的问题
"""

import os
import sys
import difflib
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# 尝试导入 rich 库
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("提示: 安装 rich 库以获得更好的彩色输出: pip install rich")
    print("回退到基本输出模式...")


class DiffGenerator:
    """生成 diff 的核心类"""
    
    def __init__(self, context_lines: int = 3, ignore_case: bool = False):
        self.context_lines = context_lines
        self.ignore_case = ignore_case
        self.console = Console() if RICH_AVAILABLE else None
    
    def read_file_lines(self, filepath: str) -> List[str]:
        """读取文件内容，处理行尾换行符"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n') for line in f]
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return [line.rstrip('\n') for line in f]
            except Exception:
                return None
    
    def is_binary_file(self, filepath: str) -> bool:
        """检查文件是否为二进制文件"""
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return True
                text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | 
                                      set(range(0x20, 0x100)) - {0x7f})
                if chunk:
                    return bool(chunk.translate(None, text_chars))
                return False
        except Exception:
            return True
    
    def generate_file_diff(self, old_file: str, new_file: str) -> Optional[List[str]]:
        """生成单个文件的 diff，返回行列表"""
        
        if not os.path.exists(old_file) or not os.path.exists(new_file):
            return None
        
        if self.is_binary_file(old_file) or self.is_binary_file(new_file):
            return ["二进制文件，无法生成文本差异"]
        
        old_lines = self.read_file_lines(old_file)
        new_lines = self.read_file_lines(new_file)
        
        if old_lines is None or new_lines is None:
            return None
        
        # 生成 diff，不包含原始行尾的换行符
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=os.path.basename(old_file),
            tofile=os.path.basename(new_file),
            lineterm='',
            n=self.context_lines
        ))
        
        return diff if diff else None
    
    def generate_directory_diff(self, old_dir: str, new_dir: str) -> dict:
        """生成目录的 diff"""
        results = {}
        old_path = Path(old_dir)
        new_path = Path(new_dir)
        
        # 收集所有文件
        all_files = set()
        
        if old_path.exists():
            for file_path in old_path.rglob('*'):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(old_path))
                    all_files.add(rel_path)
        
        if new_path.exists():
            for file_path in new_path.rglob('*'):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(new_path))
                    all_files.add(rel_path)
        
        # 比较每个文件
        for rel_path in sorted(all_files):
            old_file = old_path / rel_path
            new_file = new_path / rel_path
            
            if old_file.exists() and new_file.exists():
                diff = self.generate_file_diff(str(old_file), str(new_file))
                if diff:
                    results[rel_path] = {
                        'type': 'modified',
                        'old_path': str(old_file),
                        'new_path': str(new_file),
                        'diff': diff
                    }
            elif old_file.exists() and not new_file.exists():
                results[rel_path] = {
                    'type': 'deleted',
                    'old_path': str(old_file),
                    'new_path': None,
                    'diff': [f"文件被删除: {rel_path}"]
                }
            elif not old_file.exists() and new_file.exists():
                results[rel_path] = {
                    'type': 'added',
                    'old_path': None,
                    'new_path': str(new_file),
                    'diff': [f"新文件: {rel_path}"]
                }
        
        return results


class DiffPrinter:
    """打印 diff 的类"""
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color and RICH_AVAILABLE
        if self.use_color:
            self.console = Console()
    
    def print_diff(self, diff_lines: List[str], file_info: str = ""):
        """打印 diff 行，解决多余空行问题"""
        if not diff_lines:
            return
        
        if file_info and not file_info.startswith("\n"):
            print(f"\n{file_info}")
            print("=" * 60)
        
        for line in diff_lines:
            if self.use_color:
                if line.startswith('---'):
                    self.console.print(f"[blue]{line}[/blue]")
                elif line.startswith('+++'):
                    self.console.print(f"[blue]{line}[/blue]")
                elif line.startswith('@@'):
                    self.console.print(f"[cyan]{line}[/cyan]")
                elif line.startswith('+'):
                    self.console.print(f"[green]{line}[/green]")
                elif line.startswith('-'):
                    self.console.print(f"[red]{line}[/red]")
                else:
                    self.console.print(line)
            else:
                print(line)
    
    def print_summary(self, results: dict, old_path: str, new_path: str):
        """打印摘要信息"""
        if not results:
            print("没有发现差异")
            return
        
        total = len(results)
        modified = sum(1 for r in results.values() if r['type'] == 'modified')
        added = sum(1 for r in results.values() if r['type'] == 'added')
        deleted = sum(1 for r in results.values() if r['type'] == 'deleted')
        
        if self.use_color:
            table = Table(title="Diff 摘要", show_header=True)
            table.add_column("文件", style="cyan")
            table.add_column("状态", justify="center")
            table.add_column("变更", justify="right")
            
            for rel_path, info in results.items():
                if info['type'] == 'modified':
                    status = "[yellow]修改[/yellow]"
                    changes = self._count_changes(info['diff'])
                elif info['type'] == 'added':
                    status = "[green]新增[/green]"
                    changes = "-"
                else:  # deleted
                    status = "[red]删除[/red]"
                    changes = "-"
                table.add_row(rel_path, status, changes)
            
            self.console.print(table)
            
            stats = Panel(
                f"[bold]统计信息:[/bold]\n"
                f"总文件数: {total}\n"
                f"修改: {modified}\n"
                f"新增: {added}\n"
                f"删除: {deleted}\n"
                f"\n[dim]比较: {old_path} → {new_path}[/dim]",
                title="统计",
                border_style="green"
            )
            self.console.print(stats)
        else:
            print("\n" + "=" * 60)
            print("DIFF 摘要")
            print("=" * 60)
            print(f"比较: {old_path} → {new_path}")
            print(f"总文件数: {total}")
            print(f"修改: {modified}")
            print(f"新增: {added}")
            print(f"删除: {deleted}")
            print("-" * 60)
            
            for rel_path, info in results.items():
                if info['type'] == 'modified':
                    changes = self._count_changes(info['diff'])
                    print(f"{rel_path}: 修改 ({changes})")
                elif info['type'] == 'added':
                    print(f"{rel_path}: 新增")
                else:
                    print(f"{rel_path}: 删除")
    
    def _count_changes(self, diff_lines: List[str]) -> str:
        """统计变更行数"""
        added = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        return f"+{added}/-{removed}"


def save_diff_to_file(output_path: str, results: dict, old_path: str, new_path: str):
    """将 diff 保存到文件，确保正确的换行符"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Diff generated at {datetime.now()}\n")
        f.write(f"# Old: {old_path}\n")
        f.write(f"# New: {new_path}\n\n")
        
        for rel_path, info in results.items():
            if info['type'] == 'binary':
                continue
                
            f.write(f"\n{'='*60}\n")
            f.write(f"File: {rel_path}\n")
            f.write(f"{'='*60}\n")
            
            for line in info['diff']:
                f.write(line + '\n')  # 每行只添加一个换行符


def main():
    parser = argparse.ArgumentParser(
        description='彩色 Diff 工具 - 比较文件或文件夹的差异',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s old.txt new.txt              # 比较两个文件
  %(prog)s old_dir/ new_dir/           # 比较两个目录
  %(prog)s file1.txt file2.txt -c 5   # 显示5行上下文
  %(prog)s dir1/ dir2/ -o diff.patch  # 保存到文件
  %(prog)s dir1/ dir2/ --no-color     # 禁用彩色输出
        """
    )
    
    parser.add_argument('old', help='旧文件或旧目录路径')
    parser.add_argument('new', help='新文件或新目录路径')
    parser.add_argument('-c', '--context', type=int, default=3,
                       help='显示差异上下文的行数 (默认: 3)')
    parser.add_argument('-o', '--output', 
                       help='将 diff 输出到文件')
    parser.add_argument('--no-color', action='store_true',
                       help='禁用彩色输出')
    parser.add_argument('--summary-only', action='store_true',
                       help='只显示摘要，不显示详细差异')
    
    args = parser.parse_args()
    
    # 检查路径
    if not os.path.exists(args.old):
        print(f"错误: 路径不存在: {args.old}")
        sys.exit(1)
    if not os.path.exists(args.new):
        print(f"错误: 路径不存在: {args.new}")
        sys.exit(1)
    
    # 初始化
    diff_gen = DiffGenerator(context_lines=args.context)
    printer = DiffPrinter(use_color=not args.no_color)
    
    old_is_dir = os.path.isdir(args.old)
    new_is_dir = os.path.isdir(args.new)
    
    if old_is_dir != new_is_dir:
        print("错误: 不能比较文件和目录")
        sys.exit(1)
    
    if old_is_dir:
        # 目录比较
        print(f"比较目录:")
        print(f"  旧: {args.old}")
        print(f"  新: {args.new}\n")
        
        results = diff_gen.generate_directory_diff(args.old, args.new)
        
        if not args.summary_only:
            for rel_path, info in results.items():
                if info['type'] == 'binary':
                    continue
                file_info = f"{rel_path} ({info['type']})"
                printer.print_diff(info['diff'], file_info)
        
        printer.print_summary(results, args.old, args.new)
        
        if args.output and results:
            save_diff_to_file(args.output, results, args.old, args.new)
            print(f"\nDiff 已保存到: {args.output}")
    
    else:
        # 文件比较
        print(f"比较文件:")
        print(f"  旧: {args.old}")
        print(f"  新: {args.new}\n")
        
        diff = diff_gen.generate_file_diff(args.old, args.new)
        
        if diff is None:
            print("没有差异或无法比较")
        elif diff and diff[0] == "二进制文件，无法生成文本差异":
            print(diff[0])
        elif diff:
            printer.print_diff(diff, f"文件差异")
            
            # 统计
            added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            print(f"\n统计: 新增 {added} 行, 删除 {removed} 行")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"# Diff: {args.old} -> {args.new}\n")
                    f.write(f"# Generated at {datetime.now()}\n\n")
                    for line in diff:
                        f.write(line + '\n')
                print(f"\nDiff 已保存到: {args.output}")
        else:
            print("文件内容相同")


if __name__ == "__main__":
    main()
