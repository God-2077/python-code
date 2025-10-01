import os
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

def get_folder_size(path):
    """计算文件夹大小（字节）"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total

def format_size(size_bytes):
    """格式化文件大小为易读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def find_residual_folders(root_path):
    """查找残留文件夹（没有project.json的文件夹）"""
    residual_folders = []
    
    with Progress(
        TextColumn("[bold blue]扫描目录...", justify="right"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True
    ) as progress:
        task = progress.add_task("", total=len(os.listdir(root_path)))
        
        for folder_name in os.listdir(root_path):
            folder_path = os.path.join(root_path, folder_name)
            if os.path.isdir(folder_path):
                # 检查是否存在project.json
                project_json = os.path.join(folder_path, "project.json")
                if not os.path.exists(project_json):
                    # 获取文件夹大小和修改时间
                    size_bytes = get_folder_size(folder_path)
                    mod_time = os.path.getmtime(folder_path)
                    mod_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(mod_time))
                    
                    residual_folders.append({
                        'name': folder_name,
                        'size': size_bytes,
                        'date': mod_date
                    })
            
            progress.update(task, advance=1)
    
    return residual_folders

def rm_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(folder)

def main():
    console = Console()

    # 欢迎信息
    welcome_text = Text(
        "Wallpaper Engine Workshop 残留文件清理工具\nby Kissablecho",
        justify="center",  # 文本在面板内部居中
        style="bold yellow"  # 文本样式
    )
    centered_panel = Panel(
        welcome_text,
        width=int(console.width * 2 / 3),  # 动态计算宽度（避免过宽或过窄）
        style="yellow"  # 面板边框样式（可选）
    )

    # 4. 打印居中面板
    console.print(centered_panel, justify="center")
    
    # 设置Wallpaper Engine Workshop路径（用户可以修改此路径）
    # wallpaper_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/431960"
    wallpaper_path = input("请输入Wallpaper Engine Workshop目录路径: \n>")
    
    console.print(f"[bold green]正在扫描Wallpaper Engine Workshop目录:[/bold green]\n {wallpaper_path}")
    if wallpaper_path == "":
        console.print("[bold red]错误: 路径不能为空![/bold red]")
        return
    elif not os.path.exists(wallpaper_path):
        console.print("[bold red]错误: 指定的路径不存在![/bold red]")
        return
    
    # 查找残留文件夹
    residual_folders = find_residual_folders(wallpaper_path)
    
    if not residual_folders:
        console.print("[bold green]🎉 未发现残留文件![/bold green]")
        return
    
    # 计算总大小
    total_size = sum(folder['size'] for folder in residual_folders)
    
    # 创建并显示表格
    table = Table(title="壁纸残留文件列表", show_header=True, header_style="bold magenta")
    table.add_column("文件夹名称", style="cyan")
    table.add_column("大小", justify="right")
    table.add_column("修改日期", justify="center")
    
    for folder in residual_folders:
        table.add_row(
            folder['name'],
            format_size(folder['size']),
            folder['date']
        )
    
    console.print(table)
    console.print(f"[bold yellow]残留壁纸总数:[/bold yellow] {len(residual_folders)}")
    console.print(f"[bold yellow]总占用空间:[/bold yellow] {format_size(total_size)}")
    
    # 安全提示
    console.print("\n[bold red]⚠️ 注意:[/bold red] 这些文件夹没有project.json文件，可能是残留文件。")
    console.print("请手动确认后再删除，避免误删重要数据!")

    console.print("\n[bold red]删除这些文件夹吗?[/bold red] (Y/n)")
    confirm = input().strip().lower()
    
    if confirm == 'y' or confirm == '':
        for folder in residual_folders:
            folder_path = os.path.join(wallpaper_path, folder['name'])
            rm_folder(folder_path)
            console.print(f"[bold green]成功删除:[/bold green] {folder['name']}")
    else:
        console.print("[bold yellow]操作已取消.[/bold yellow]")

if __name__ == "__main__":
    main()
