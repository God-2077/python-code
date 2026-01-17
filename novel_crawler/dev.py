#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Kissablecho
# @Software: Visual Studio Code
# @Blog    : https://blog.ksable.top/
# @Github  : https://github.com/God-2077/
# @Github Repo: https://github.com/God-2077/python-code

import os
import requests
from bs4 import BeautifulSoup
import sys
import time
import re
import signal
import uuid
from ebooklib import epub
# import traceback
import yaml
# 导入rich库
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.prompt import Confirm, Prompt
from rich.logging import RichHandler
from rich.traceback import Traceback
from rich.theme import Theme
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
import logging
from PIL import Image

# 安装rich的traceback处理器
from rich.traceback import install
install(show_locals=True)

# 创建全局Console对象
custom_theme = Theme({
    "info": "dim cyan",
    "warn": "bold yellow",
    "error": "bold red",
    "debug": "magenta",
    "success": "bold green",
    "highlight": "bold cyan",
    "progress": "bold blue",
    "title": "bold #FF8C00",
    "subtitle": "bold #FFA500",
    "data": "#87CEEB",
    "url": "underline blue"
})


# 配置日志系统
console = Console(theme=custom_theme)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(console=console, markup=True, show_path=True, show_time=True, rich_tracebacks=True)]
)
logger = logging.getLogger("rich")
logger.propagate = True

# 定义全局变量
if len(sys.argv) < 2:
    logger.error("Usage: python script.py config.yml")
    sys.exit(1)

def load_config():
    """加载配置文件"""
    # 全局变量
    global novel_detail_url, novel_chapter_url, rule_novel_name, rule_novel_author, rule_novel_intro, rule_novel_chapter_div, rule_novel_chapter_div_only, rule_novel_chapter_name, rule_novel_chapter_url, rule_novel_chapter_content_div, rule_novel_chapter_content_p, rule_novel_chapter_content_purify_text, rule_novel_chapter_content_purify_re, download_path, novel_file_encoding, output_format, indent_string, headers, cookies, timeout, max_retries, request_interval_ms, debug, multi_threading, thread_count, last_request_time, novel_cover_img, rule_novel_volume_div, rule_novel_volume_name, rule_novel_chapter_name_from_content
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 将配置映射到原始变量名
    novel_detail_url = config['basic']['novel_detail_url']
    novel_chapter_url = config['basic']['novel_chapter_url']

    rule_novel_name = config['rules']['novel_name']
    rule_novel_author = config['rules']['novel_author']
    rule_novel_intro = config['rules']['novel_intro']
    rule_novel_chapter_div = config['rules']['novel_chapter_div']
    rule_novel_chapter_div_only = config['rules']['novel_chapter_div_only']
    rule_novel_chapter_name = config['rules']['novel_chapter_name']
    rule_novel_chapter_url = config['rules']['novel_chapter_url']
    rule_novel_chapter_content_div = config['rules']['novel_chapter_content_div']
    rule_novel_chapter_content_p = config['rules']['novel_chapter_content_p']
    novel_cover_img = config['rules']['novel_cover_img']
    # 新增：从小说正文页面提取章节名称的规则
    rule_novel_chapter_name_from_content = config['rules'].get('novel_chapter_name_from_content', '')

    
    # 新增分卷配置
    rule_novel_volume_div = config['rules'].get('novel_volume_div', '')
    rule_novel_volume_name = config['rules'].get('novel_volume_name', '')

    rule_novel_chapter_content_purify_text = config['rules']['purify']['text']
    rule_novel_chapter_content_purify_re = config['rules']['purify']['re']

    download_path = config['basic']['download_path']
    novel_file_encoding = config['basic']['novel_file_encoding']
    output_format = config['basic']['output_format']
    indent_string = config['basic']['indent_string']

    headers = config['network']['headers']
    cookies = config['network']['cookies']
    timeout = config['network']['timeout']
    max_retries = config['network']['max_retries']

    if config['network']['request_interval_time'] != None and config['network']['request_interval_time'] > 0:
        request_interval_ms = 60/config['network']['request_interval_time']
    else:
        request_interval_ms = 0

    debug = config['basic']['debug']

    # 新增多线程配置
    multi_threading = config['network']['multi_threading']
    thread_count = config['network']['thread_count']

    last_request_time = None

    # 函数定义

    # 设置 logger 级别
    if debug:
        logger.setLevel(logging.DEBUG)

def get_unique_file_path(file_path):
    base_path, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base_path}({counter}){ext}"
        counter += 1
    logger.info(f"生成唯一文件路径: {file_path}")
    return file_path

def log_message(message, level="info", highlight=False):
    """使用rich库增强的日志输出函数"""
    styles = {
        "debug": "debug",
        "info": "info",
        "warn": "warn",
        "error": "error",
        "success": "success"
    }
    
    style = styles.get(level, "info")
    if highlight:
        message = f"[highlight]{message}[/]"
    
    console.print(f"[{style}]{message}[/]", highlight=False)

def print_header(title, subtitle=None):
    """打印带边框的标题"""
    title_panel = Panel(
        Text(title, justify="center", style="title"),
        expand=True,
        border_style="bold #FF8C00",
        padding=(1, 4)
    )
    console.print(title_panel)
    
    if subtitle:
        console.print(Text(subtitle, style="subtitle", justify="center"), justify="center")

def print_data_table(title, data):
    """打印数据表格"""
    table = Table(title=title, show_header=True, header_style="bold #FFA500")
    table.add_column("项目", style="bold #87CEEB", min_width=15)
    table.add_column("值", style="data", overflow="fold")
    
    for key, value in data.items():
        if isinstance(value, list):
            value = "\n".join([f"• {item}" for item in value])
        table.add_row(key, str(value))
    
    console.print(table)

def print_debug_table(title, data):
    """打印调试信息表格"""
    if not debug:
        return
        
    table = Table(title=f"[debug]DEBUG: {title}[/]", show_header=True, header_style="bold magenta")
    table.add_column("参数", style="bold cyan", min_width=20)
    table.add_column("值", style="magenta")
    
    for key, value in data.items():
        if isinstance(value, list):
            value = "\n".join([f"• {item}" for item in value])
        table.add_row(key, str(value))
    
    console.print(table)

def get_url(url, skip_wait=False):
    """ 网络请求（添加多线程支持）"""
    global last_request_time
    # 如果是多线程模式且不需要等待，则跳过等待逻辑
    if not skip_wait and last_request_time is not None and not multi_threading:
        current_time = int(time.time() * 1000)
        if current_time - last_request_time < request_interval_ms:
            time.sleep((request_interval_ms - (current_time - last_request_time)) / 1000.0)
    last_request_time = int(time.time() * 1000)
    
    retries = 0
    while retries < max_retries:
        try:
            if cookies and cookies != {}:  # 当cookies存在时使用
                response = requests.get(url, headers=headers, timeout=timeout, cookies=cookies)
            else:
                response = requests.get(url, headers=headers, timeout=timeout)
                
            if debug:
                logger.debug(f"请求成功[{response.status_code}]: [url]{url}[/]")
            return response
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            logger.warning(f"请求失败，正在重试 ({retries + 1}/{max_retries}) URL:{url}")
            if debug:
                logger.debug(f"错误信息: URL({url}) {e}")
            time.sleep(1)
            retries += 1
            
    logger.error("请求失败，已达到最大重试次数 URL:{url}")
    return None

def parse_html(html_content):
    """解析网页内容，返回 BeautifulSoup 对象"""
    soup = BeautifulSoup(html_content, 'lxml')
    return soup

# css 选择器，返回解析后的内容
def css_select(soup, rule):
    """css 选择器，返回解析后的内容"""
    try:
        return soup.select(rule)
    except AttributeError:
        logger.warning(f"找不到符合规则 [highlight]{rule}[/] 的内容")
        return []

# 退出程序
def exit_program(status_code=0):
    """退出程序并打印状态信息"""
    logger.info(f"程序退出，状态码: {status_code}")
    sys.exit(status_code)

# 安全的文件名
def safe_filename(filename):
    """移除文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '', filename)

# 追加写入文件
def write_file_a(text, path, encoding='utf-8'):
    """追加写入文件"""
    try:
        with open(path, 'a', encoding=encoding) as file_a:
            file_a.write(text)
            file_a.close()
            # logger.debug(f"文件写入成功文件: {path}")
    except Exception as e:
        logger.error(f"写入文件失败: {e}")
        exit_program(1)

# 净化内容
def purify_content(content):
    if not content:
        return ''
    # 处理文本替换
    for text in rule_novel_chapter_content_purify_text:
        content = content.replace(text, '')
    # 处理正则替换
    for pattern in rule_novel_chapter_content_purify_re:
        content = re.sub(pattern, '', content)
    # 新增：移除空白段落
    content = re.sub(r'\n\s*\n', '\n\n', content)
    return content

# 首页url
def get_base_url(url):
    # 去掉任何末尾的路径部分，只保留域名和最后的路径部分
    url = re.sub(r'/[^/]*$', '/', url)
    return url

# url_root
def get_root_url(url):
    # 正则表达式匹配协议和域名部分
    match = re.match(r'(https?://[^/]+)', url)
    if match:
        return match.group(1)
    return None

# 更人性化的时间格式
def format_time(seconds):
    """
    将秒数转换为更人性化的时间格式（时:分:秒）
    """
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours} 小时 {minutes} 分钟 {seconds} 秒"
    elif minutes > 0:
        return f"{minutes} 分钟 {seconds} 秒"
    else:
        return f"{seconds} 秒"

# 信号处理函数
def signal_handler(sig, frame):
    logger.warning("\n程序被中断，正在退出...")
    exit_program(0)

# epub 章节html渲染
def epub_chapter_html_render(chapter_name, chapter_content):
    """
    渲染章节内容为 HTML 格式
    """
    return f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh" xml:lang="zh">
<head>
    <meta charset="UTF-8" />
    <title>{chapter_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link href="./style/default.css" rel="stylesheet" type="text/css" />
</head>
<body>
    <!-- 章节标题 -->
    <section id="ch01" epub:type="chapter">
        <header>
            <h1>{chapter_name}</h1>
        </header>
            {chapter_content}
    </section>
</body>
</html>
"""

# epub 分卷html渲染
def epub_volume_html_render(volume_name):
    """
    渲染分卷标题为 HTML 格式
    """
    return f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="zh" xml:lang="zh">
<head>
    <meta charset="UTF-8" />
    <title>{volume_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link href="./style/default.css" rel="stylesheet" type="text/css" />
</head>
<body>
    <!-- 分卷标题 -->
    <section id="vol01" epub:type="chapter">
        <header>
            <h1>{volume_name}</h1>
        </header>
    </section>
</body>
</html>
"""

# 下载单个章节的函数
def download_chapter(chapter_info, progress, task_id, chapter_count):
    index, (volume_name, chapter_name, chapter_url) = chapter_info
    try:
        # 根据下载模式更新不同的进度条描述
        if multi_threading:
            # 多线程模式：显示索引但不显示章节名
            progress.update(task_id, description=f"[progress]下载中[{index+1}/{chapter_count}]: ")
        else:
            # 单线程模式：显示索引和章节名前20字符
            short_name = chapter_name[:20] + '...' if len(chapter_name) > 20 else chapter_name
            progress.update(task_id, description=f"[progress]下载中[{index+1}/{chapter_count}]: {short_name}")
        
        # 初始化章节内容
        chapter_content = ''
        
        # 获取章节内容（多线程模式下跳过等待）
        chapter_response = get_url(chapter_url, skip_wait=multi_threading)
        if chapter_response is None:
            logger.error(f"获取章节内容失败: [highlight]{chapter_name}[/]")
            return (index, volume_name, chapter_name, "", False, "请求失败")
        
        chapter_soup = parse_html(chapter_response.content)
        
        # 新增：从小说正文页面提取章节名称（优先级高于章节页面的章节名称）
        if rule_novel_chapter_name_from_content:
            chapter_name_elements = css_select(chapter_soup, rule_novel_chapter_name_from_content)
            if chapter_name_elements:
                new_chapter_name = chapter_name_elements[0].text.strip()
                if new_chapter_name and new_chapter_name != chapter_name:
                    if debug:
                        logger.debug(f"章节名称已更新: {chapter_name} -> {new_chapter_name}")
                    chapter_name = new_chapter_name
        
        # 获取章节内容区域
        chapter_content_div = css_select(chapter_soup, rule_novel_chapter_content_div)
        if len(chapter_content_div) == 0:
            logger.error(f"找不到符合规则的章节内容区域: [highlight]{chapter_name}[/]")
            return (index, volume_name, chapter_name, "", False, "内容区域未找到")
        
        # 处理章节内容
        for chapter_content_div_only in chapter_content_div:
            # 增加对 br 标签的特殊处理逻辑
            if rule_novel_chapter_content_p.lower() == 'br':
                # 使用换行符分割内容（处理多种 br 标签写法）
                raw_content = str(chapter_content_div_only)
                paragraphs = re.split(r'<br\s*/?>', raw_content, flags=re.IGNORECASE)
                chapter_content_p_list = [
                    BeautifulSoup(p, 'lxml').get_text('\n').strip() 
                    for p in paragraphs if p.strip()
                ]
            else:
                chapter_content_p_list = css_select(chapter_content_div_only, rule_novel_chapter_content_p)

            if len(chapter_content_p_list) == 0:
                logger.warning(f"找不到符合规则的章节内容段落: [highlight]{chapter_name}[/]")
                continue
            
            for chapter_content_p in chapter_content_p_list:
                # 处理 br 模式获取的预分割段落
                if rule_novel_chapter_content_p.lower() == 'br':
                    paragraph_text = chapter_content_p
                else:
                    paragraph_text = chapter_content_p.text.strip()
                
                if not paragraph_text:
                    continue

                # 组合章节内容
                if output_format == 'epub':
                    # 对于 epub 格式，使用 HTML 标签
                    chapter_content += f"<p>{paragraph_text}</p>\n"
                elif output_format == 'txt':
                    # 对于 txt 格式，使用纯文本
                    chapter_content += f"{indent_string}{paragraph_text}\n"
        
        if chapter_content == '':
            logger.warning(f"章节内容为空: [highlight]{chapter_name}[/]")
            return (index, volume_name, chapter_name, "", True, "内容为空")
        else:
            # 净化章节内容
            chapter_content = purify_content(chapter_content)
            return (index, volume_name, chapter_name, chapter_content, True, "下载成功")
            
    except Exception as e:
        error_msg = f"章节处理失败: {chapter_name} - {str(e)}"
        logger.error(error_msg)
        if debug:
            logger.debug(f"错误详情:\n{Traceback(show_locals=True)}")
        return (index, volume_name, chapter_name, "", False, error_msg)


# 主函数开始
def main():
    print_header("小说爬虫工具")
    
    if debug:
        logger.debug("Debug模式已开启")
        print_debug_table("基本配置", {
            "小说详情页面URL": novel_detail_url,
            "小说章节列表URL": novel_chapter_url,
            "小说名称规则": rule_novel_name,
            "小说作者规则": rule_novel_author,
            "小说简介规则": rule_novel_intro,
            "章节区域规则": rule_novel_chapter_div,
            "单个章节规则": rule_novel_chapter_div_only,
            "分卷区域规则": rule_novel_volume_div,
            "分卷名称规则": rule_novel_volume_name,
            "章节名称规则": rule_novel_chapter_name,
            "章节URL规则": rule_novel_chapter_url,
            "内容区域规则": rule_novel_chapter_content_div,
            "分段规则": rule_novel_chapter_content_p,
            "缩进字符串": indent_string,
            "文本净化规则": rule_novel_chapter_content_purify_text,
            "正则净化规则": rule_novel_chapter_content_purify_re,
            "保存路径": download_path,
            "文件编码": novel_file_encoding,
            "输出格式": output_format
        })
        
        print_debug_table("网络配置", {
            "请求头": headers,
            "超时时间": timeout,
            "最大重试次数": max_retries,
            "请求间隔": request_interval_ms,
            "多线程模式": multi_threading,
            "线程数": thread_count
        })

    # 开始时间
    start_time = time.time()
    
    # 显示小说信息面板
    with console.status("[bold green]正在获取小说信息...[/]", spinner="dots"):
        # 获取小说详情页面的内容
        response_novel_detail = get_url(novel_detail_url)
        if response_novel_detail is None:
            logger.error("获取小说详情页面失败")
            exit_program(1)
        logger.debug("获取小说详情页面成功")
        soup = parse_html(response_novel_detail.content)

        # 获取小说名称
        if rule_novel_name == '' or rule_novel_name is None:
            logger.warning("小说名称的规则表达式为空，使用'小说'作为小说名称")
            novel_name = "小说"
        else:
            novel_name = css_select(soup, rule_novel_name)[0].text.strip()
            logger.debug(f"获取到的小说名称: {novel_name}")
        
        # 获取小说作者
        if rule_novel_author == '' or rule_novel_author is None:
            logger.warning("小说作者的规则表达式为空，使用'佚名'作为小说作者")
            novel_author = "佚名"
        else:
            novel_author = css_select(soup, rule_novel_author)[0].text.strip()
            logger.debug(f"获取到的小说作者: {novel_author}")
        
        # 获取小说简介
        if rule_novel_intro == '' or rule_novel_intro is None:
            logger.warning("小说简介的规则表达式为空，使用'暂无简介'作为小说简介")
            novel_intro = "暂无简介"
        else:
            novel_intro = css_select(soup, rule_novel_intro)[0].text.strip()
            logger.debug(f"获取到的小说简介: {novel_intro[:50]}")

    
    # 显示小说信息面板
    info_panel = Panel(
        f"[bold]小说名称:[/bold] [data]{novel_name}[/]\n"
        f"[bold]作者:[/bold] [data]{novel_author}[/]\n"
        f"[bold]来源:[/bold] [url]{novel_detail_url}[/]\n"
        f"[bold]简介:[/bold] {novel_intro[:200]}{'...' if len(novel_intro) > 200 else ''}",
        title="[title]小说信息[/]",
        border_style="bold #87CEEB",
        expand=True,
        padding=(1, 2)
    )
    console.print(info_panel)

    # 获取章节列表（支持分卷）
    chapter_list = []
    
    if not (novel_chapter_url and rule_novel_chapter_div and rule_novel_chapter_div_only and rule_novel_chapter_name and rule_novel_chapter_url):
        logger.error("小说章节列表页面的URL列表、小说章节区域、小说单个章节的区域、小说章节名称、小说章节URL的规则表达式不可为空")
        exit_program(1)
    else:
        with console.status("[bold green]正在获取章节列表...[/]", spinner="dots"):
            logger.info("开始获取章节列表")
            for chapter_url in novel_chapter_url:
                # 获取章节列表页面的内容
                response_chapter_list = get_url(chapter_url)
                response_chapter_list = parse_html(response_chapter_list.content)
                response_chapter_list_base_url = get_base_url(chapter_url)
                response_chapter_list_root_url = get_root_url(chapter_url)
                
                # 检查是否启用分卷功能
                enable_volume = rule_novel_volume_div and rule_novel_volume_name
                
                if enable_volume:
                    logger.info("检测到分卷配置，启用分卷功能")
                    # 分卷模式：先获取分卷，再获取每个分卷下的章节
                    volume_divs = css_select(response_chapter_list, rule_novel_volume_div)
                    
                    if len(volume_divs) == 0:
                        logger.warning("未找到分卷区域，将整个页面视为一个分卷")
                        # 如果没有找到分卷，将整个章节区域视为一个分卷
                        volume_name = "正文卷"
                        chapter_divs_list = css_select(response_chapter_list, rule_novel_chapter_div)
                        process_chapter_divs(chapter_divs_list, volume_name, chapter_list, response_chapter_list_base_url, response_chapter_list_root_url)
                    else:
                        logger.info(f"找到 {len(volume_divs)} 个分卷")
                        for volume_div in volume_divs:
                            # 获取分卷名称
                            volume_name_elements = css_select(volume_div, rule_novel_volume_name)
                            if volume_name_elements:
                                volume_name = volume_name_elements[0].text.strip()
                            else:
                                volume_name = "未知分卷"
                            
                            logger.debug(f"处理分卷: {volume_name}")
                            
                            # 在当前分卷下查找章节
                            chapter_divs_in_volume = css_select(volume_div, rule_novel_chapter_div)
                            if not chapter_divs_in_volume:
                                # 如果分卷内没有章节区域，尝试直接在分卷内查找章节
                                chapter_divs_in_volume = [volume_div]
                            
                            process_chapter_divs(chapter_divs_in_volume, volume_name, chapter_list, response_chapter_list_base_url, response_chapter_list_root_url)
                else:
                    logger.info("未启用分卷功能，使用普通章节模式")
                    # 普通模式：直接获取所有章节
                    volume_name = ""  # 空分卷名称
                    chapter_divs_list = css_select(response_chapter_list, rule_novel_chapter_div)
                    process_chapter_divs(chapter_divs_list, volume_name, chapter_list, response_chapter_list_base_url, response_chapter_list_root_url)

    # 小说章节总数
    chapter_count = len(chapter_list)

    logger.info(f"章节列表获取完成，共 [highlight]{chapter_count}[/] 章")

    # 检查章节列表是否为空
    if chapter_count == 0:
        logger.error("章节列表为空，无法下载小说")
        exit_program(1)
    
    # 显示章节预览表格（包含分卷信息）
    if chapter_count > 0:
        table = Table(title="[title]章节预览[/]", show_header=True, header_style="bold #FFA500")
        table.add_column("序号", style="bold #87CEEB", width=6)
        table.add_column("分卷", style="data", width=15)
        table.add_column("章节名称", style="data")
        table.add_column("URL", style="url", overflow="fold")
        
        # 显示前5章和后5章
        for i, (volume_name, chapter_name, chapter_url) in enumerate(chapter_list[:5]):
            table.add_row(str(i+1), volume_name, chapter_name, chapter_url)
        
        if chapter_count > 10:
            table.add_row("...", "...", "...", "...")
            for i in range(max(0, chapter_count-5), chapter_count):
                volume_name, chapter_name, chapter_url = chapter_list[i]
                table.add_row(str(i+1), volume_name, chapter_name, chapter_url)
        elif chapter_count > 5:
            for i in range(5, chapter_count):
                volume_name, chapter_name, chapter_url = chapter_list[i]
                table.add_row(str(i+1), volume_name, chapter_name, chapter_url)
        
        console.print(table)

    # 开始下载小说
    logger.info("小说信息获取完成，即将开始下载小说")
    
    # 用户确认
    if not Confirm.ask("[bold]是否开始下载？[/]", default=True):
        logger.info("[bold yellow]用户取消下载[/]")
        exit(0)
    else:
        logger.info("[bold green]开始下载...[/]")
    
    # 下载小说

    # 创建小说文件
    if output_format == 'epub':
        novel_file = f"{novel_name} - {novel_author}.epub"
    elif output_format == 'txt':
        novel_file = f"{novel_name} - {novel_author}.txt"
    else:
        logger.error("输出格式不支持，请选择 txt 或 epub")
        exit_program(1)
    novel_file = safe_filename(novel_file)
    novel_file_path = os.path.join(download_path, novel_file)
    
    # 检查文件是否存在
    if os.path.exists(novel_file_path):
        logger.info(f"[bold yellow]文件 [highlight]{novel_file_path}[/] 已存在[/]")
        if Confirm.ask("[bold]是否覆盖下载？[/]", default=False):
            logger.info("[bold yellow]用户选择覆盖下载[/]")
        else:
            if Confirm.ask("[bold]是否跳过该文件名，使用'小说名（序号）'下载？[/]", default=True):
                novel_file_path = get_unique_file_path(novel_file_path)
                logger.info(f"[bold green]新文件名: [highlight]{novel_file_path}[/][/]")
            else:
                logger.info("[bold yellow]取消下载[/]")
                exit_program(0)
    logger.info(f"[bold green]小说保存文件路径: [highlight]{novel_file_path}[/][/]")
    
    # 创建下载目录
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        logger.info(f"创建下载目录: [highlight]{download_path}[/]")
    
    # 初始化文件
    if output_format == 'txt':
        try:
            with open(novel_file_path, 'w', encoding=novel_file_encoding) as novel_file_x:
                novel_file_x.write(f"书名：{novel_name}\n")
                novel_file_x.write(f"来源：{novel_detail_url}\n")
                novel_file_x.write(f"作者：{novel_author}\n")
                novel_file_x.write(f"简介：\n{indent_string}{novel_intro}\n\n")
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            exit_program(1)
    # 创建 epub 文件结构
    elif output_format == 'epub':
        # 创建书对象
        epub_book = epub.EpubBook()
        epub_book.set_identifier(str(uuid.uuid4()))
        epub_book.set_title(novel_name)
        epub_book.set_language("zh-CN")
        epub_book.add_author(novel_author)
        epub_book.add_metadata('DC', 'description', novel_intro)
        # 详情页
        epub_book_intro = epub.EpubHtml(title="详情", file_name="intro.xhtml", lang="zh")
        epub_book_intro.content = f"""
        <h1>详情</h1>
        <p>书名：{novel_name}</p>
        <p>来源：{novel_detail_url}</p>
        <p>作者：{novel_author}</p>
        <p>简介：<br/>
        {indent_string}{novel_intro}</p>"""
        epub_book.add_item(epub_book_intro)
        if novel_cover_img:
            novel_cover_img_url = css_select(soup,novel_cover_img)
            novel_cover_img_url = novel_cover_img_url[0].get('src')
            
            # 添加相对链接转换逻辑（类似于章节链接处理）
            if novel_cover_img_url.startswith('/'):
                novel_cover_img_url = get_root_url(novel_detail_url) + novel_cover_img_url
            elif novel_cover_img_url.startswith("./"):
                novel_cover_img_url = get_base_url(novel_detail_url) + novel_cover_img_url[2:]
            elif novel_cover_img_url.startswith("."):
                novel_cover_img_url = get_base_url(novel_detail_url) + novel_cover_img_url[1:]
    # 其他情况保持原样
    
            # 下载封面图片
            novel_cover_img_url_response = get_url(novel_cover_img_url)
            if novel_cover_img_url_response.status_code == 200:
                # 保存封面图片到临时文件
                with open("temp_cover", "wb") as f:
                    f.write(novel_cover_img_url_response.content)
            else:
                logger.error(f"下载封面图片失败: {novel_cover_img_url_response.status_code}")
                exit_program(1)

            # 打开并检查封面图片
            with Image.open("temp_cover") as img:
                width, height = img.size
                # 转换图片为 RGB 格式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # 保存临时图片文件
                img.save("temp_cover.jpg", 'JPEG')

            # 读取临时图片文件内容
            with open("temp_cover.jpg", 'rb') as f:
                epub_book_cover_content = f.read()
            os.remove("temp_cover.jpg")
            os.remove("temp_cover")

            # 创建封面图片项
            epub_book_cover_item = epub.EpubImage()
            epub_book_cover_item.file_name = 'cover.jpg'
            epub_book_cover_item.media_type = 'image/jpeg'
            epub_book_cover_item.content = epub_book_cover_content

            # 将封面图片添加到 EPUB
            epub_book.add_item(epub_book_cover_item)

            # 设置封面元数据
            epub_book.set_cover('cover.jpg', epub_book_cover_content, create_page=True)
            logger.info("设置封面元数据成功")


        # 存储章节对象的列表
        epub_chapter_items = []
        # 添加介绍章节到章节列表
        epub_chapter_items.append(epub_book_intro)
        epub_book_chapter_count = 0  # 初始化章节计数
        epub_book_chapter_listtoc = []
    logger.info("初始化文件")
    logger.info("开始下载章节")

    # 创建线程安全的写入队列（用于TXT格式的顺序写入）
    write_queue = Queue()
    
    # 创建进度条
    progress = Progress(
        TextColumn("[progress]{task.description}", justify="right"),
        BarColumn(bar_width=None, style="yellow", complete_style="green"),
        TaskProgressColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
        expand=True
    )
    
    # 添加多线程状态显示
    if multi_threading:
        console.print(Panel(
            f"[bold green]多线程模式已启用[/]\n"
            f"[bold]线程数:[/] [highlight]{thread_count}[/]\n"
            f"[bold]请求间隔限制:[/] [highlight]已禁用[/]",
            title="[title]多线程设置[/]",
            border_style="bold #87CEEB",
            expand=True,
            padding=(1, 2)
        ))

    
    task_id = progress.add_task("[progress]下载章节...", total=chapter_count)
    
    # 定义线程安全的计数器
    completed_counter = 0
    lock = threading.Lock()
    
    # 存储当前分卷信息（用于TXT格式的分卷标记）
    current_volume = ""
    
    # TXT文件写入线程函数（支持分卷）
    def txt_writer():
        nonlocal completed_counter, current_volume
        next_index = 0
        results = {}
        
        while completed_counter < chapter_count:
            # 从队列中获取结果
            index, volume_name, chapter_name, chapter_content, success, message = write_queue.get()
            
            # 存储结果
            results[index] = (volume_name, chapter_name, chapter_content, success, message)
            
            # 按顺序处理结果
            while next_index in results:
                volume_name, chapter_name, chapter_content, success, message = results.pop(next_index)
                
                if output_format == 'txt' and success and chapter_content:
                    try:
                        with open(novel_file_path, 'a', encoding=novel_file_encoding) as f:
                            # 检查分卷变化，写入分卷标题
                            if volume_name and volume_name != current_volume:
                                f.write(f"\n\n=== {volume_name} ===\n\n")
                                current_volume = volume_name
                            
                            # 写入章节内容
                            f.write(f"{chapter_name}\n\n{chapter_content}\n\n")
                    except Exception as e:
                        logger.error(f"写入章节失败: {chapter_name} - {e}")
                
                next_index += 1
            
            write_queue.task_done()
    
    # 启动TXT写入线程
    if output_format == 'txt':
        writer_thread = threading.Thread(target=txt_writer, daemon=True)
        writer_thread.start()
    
    # 创建线程池（如果启用多线程）
    executor = None
    if multi_threading:
        executor = ThreadPoolExecutor(max_workers=thread_count)
        futures = []
    
    # EPUB章节存储（包含分卷信息）
    epub_chapters = {}
    epub_volumes = {}  # 存储分卷信息
    
    # 下载章节
    with progress:
        if multi_threading:
            # 多线程模式
            for i, chapter in enumerate(chapter_list):
                futures.append(executor.submit(
                    download_chapter, 
                    (i, chapter), 
                    progress, 
                    task_id,
                    chapter_count
                ))
            
            # 处理结果
            for future in as_completed(futures):
                index, volume_name, chapter_name, chapter_content, success, message = future.result()
                
                with lock:
                    completed_counter += 1
                
                # EPUB直接存储结果
                if output_format == 'epub' and success and chapter_content:
                    # 存储章节内容，稍后按顺序处理
                    epub_chapters[index] = (volume_name, chapter_name, chapter_content)
                    # 记录分卷信息
                    if volume_name and volume_name not in epub_volumes:
                        epub_volumes[volume_name] = True
                
                # TXT将结果放入队列
                elif output_format == 'txt':
                    write_queue.put((index, volume_name, chapter_name, chapter_content, success, message))
                
                progress.update(task_id, advance=1)
            
            # 关闭线程池
            executor.shutdown(wait=True)
            
        else:
            # 单线程模式
            current_volume_txt = ""  # 用于TXT格式的分卷跟踪
            for i, (volume_name, chapter_name, chapter_url) in enumerate(chapter_list):
                result = download_chapter(
                    (i, (volume_name, chapter_name, chapter_url)), 
                    progress, 
                    task_id,
                    chapter_count
                )
                index, volume_name, chapter_name, chapter_content, success, message = result
                
                # 直接处理结果
                if output_format == 'txt' and success and chapter_content:
                    # 检查分卷变化
                    if volume_name and volume_name != current_volume_txt:
                        write_file_a(f"\n\n=== {volume_name} ===\n\n", novel_file_path, encoding=novel_file_encoding)
                        current_volume_txt = volume_name
                    
                    write_file_a(f"{chapter_name}\n\n{chapter_content}\n\n", novel_file_path, encoding=novel_file_encoding)
                elif output_format == 'epub' and success and chapter_content:
                    # 存储章节内容
                    epub_chapters[i] = (volume_name, chapter_name, chapter_content)
                    # 记录分卷信息
                    if volume_name and volume_name not in epub_volumes:
                        epub_volumes[volume_name] = True
                
                progress.update(task_id, advance=1)
    
    # 等待TXT写入线程完成
    if output_format == 'txt':
        write_queue.join()
        if writer_thread.is_alive():
            writer_thread.join(timeout=5)
    
    # EPUB文件处理（支持分卷）
    if output_format == 'epub':
        # 按顺序处理所有章节
        current_volume_epub = ""  # 当前分卷名称
        for index in sorted(epub_chapters.keys()):
            volume_name, chapter_name, chapter_content = epub_chapters[index]
            
            # 检查分卷变化，添加分卷标题
            if volume_name and volume_name != current_volume_epub:
                current_volume_epub = volume_name
                epub_book_chapter_count += 1
                volume_id = f"{epub_book_chapter_count:04d}"
                
                # 创建分卷标题章节
                epub_volume = epub.EpubHtml(
                    title=volume_name,
                    file_name=f"vol_{volume_id}.xhtml",
                    lang="zh"
                )
                epub_volume.content = epub_volume_html_render(volume_name)
                
                # 添加到书籍
                epub_book.add_item(epub_volume)
                # 添加到章节列表
                epub_chapter_items.append(epub_volume)
                # 添加到目录
                epub_book_chapter_listtoc.append((f"vol_{volume_id}", volume_name))
            
            # 创建章节
            epub_book_chapter_count += 1
            chapter_id = f"{epub_book_chapter_count:04d}"
            epub_chapter = epub.EpubHtml(
                title=chapter_name,
                file_name=f"chap_{chapter_id}.xhtml",
                lang="zh"
            )
            epub_chapter.content = epub_chapter_html_render(chapter_name, chapter_content)
            
            # 添加到书籍
            epub_book.add_item(epub_chapter)
            # 添加到章节列表
            epub_chapter_items.append(epub_chapter)
            # 添加到目录
            epub_book_chapter_listtoc.append((f"chap_{chapter_id}", chapter_name))
        
        # 创建CSS样式
        epub_css_content = """
            body {
                font-family: "Microsoft YaHei", "STXihei", sans-serif;
                font-size: 1.0em;
                line-height: 1.6;
                margin: 1em auto;
                max-width: 800px;
                padding: 0 1em;
                text-align: justify;
            }
            h1 {
                font-size: 28px;
                text-align: center;
                color: #91531d;
                font-weight: normal;
                margin-top: 2.5em;
                margin-bottom: 2.5em;
            }
            h2 {
                color: #1f4a92;
                font-size: 22px;
                font-family: "DK-XIAOBIAOSONG", "方正小标宋简体";
                font-weight: normal;
                border-bottom: solid 1px #1f4a92;
                padding: 0.2em 0em 0.5em 0em;
                text-indent: 0em;
            }

            p {
                font-family: "DK-SONGTI", "方正宋三简体", "方正书宋", "宋体";
                font-size: 16px;
                text-indent: 2em;
            }

            blockquote {
                font-size: 16px;
                text-indent: 2em;
            }

            img {
                width: 100%;
                height: auto;
                /* 居中 */
                margin: 0 auto;
            }

            hr {
                height: 10px;
                border: none;
                margin-top: 12px;
                border-top: 10px groove #87ceeb;
            }

            hr {
                color: #3dd9b6;
                border: double;
                border-width: 3px 5px;
                border-color: #3dd9b6 transparent;
                height: 1px;
                overflow: visible;
                margin-left: 20px;
                margin-right: 20px;
                position: relative;
            }

            hr:before,
            hr:after {
                content: '';
                position: absolute;
                width: 5px;
                height: 5px;
                border-width: 0 3px 3px 0;
                border-style: double;
                top: -3px;
                background: radial-gradient(2px at 1px 1px, currentColor 2px, transparent 0) no-repeat;
            }

            hr:before {
                transform: rotate(-45deg);
                left: -20px;
            }

            hr:after {
                transform: rotate(135deg);
                right: -20px;
            }
        """

        # 创建CSS项目
        epub_style = epub.EpubItem(
            uid="style_default",
            file_name="style/default.css",
            media_type="text/css",
            content=epub_css_content
        )
        epub_book.add_item(epub_style)

        # 目录
        epub_book.toc = []
        epub_book.toc.append(epub.Link("intro.xhtml", "详情", "intro"))
        for (i,title) in epub_book_chapter_listtoc:
            epub_book.toc.append(epub.Link(f"{i}.xhtml", title, i))

        #添加导航
        epub_book.add_item(epub.EpubNcx())
        epub_book.add_item(epub.EpubNav())

        # 设置阅读顺序
        # 书脊（阅读顺序）：封面、导航、介绍、各章节
        epub_book.spine = ["nav", *epub_chapter_items]

        # 生成文件
        with console.status("[bold green]正在生成EPUB文件...[/]", spinner="dots"):
            epub.write_epub(novel_file_path, epub_book, {})
            logger.info(f"EPUB文件生成完成: [highlight]{novel_file_path}[/]")

    # 下载用时
    end_time = time.time()
    download_time = end_time - start_time
    
    # 下载统计
    success_count = len(epub_chapters) if output_format == 'epub' else chapter_count
    success_rate = (success_count / chapter_count) * 100 if chapter_count > 0 else 0
    
    # 分卷统计
    volume_count = len(epub_volumes) if output_format == 'epub' else len(set(volume_name for volume_name, _, _ in chapter_list if volume_name))
    
    console.print(Panel(
        f"[bold green]✓ 下载完成![/]\n\n"
        f"[bold]小说名称:[/] [data]{novel_name}[/]\n"
        f"[bold]作者:[/] [data]{novel_author}[/]\n"
        f"[bold]分卷数:[/] [data]{volume_count}[/]\n"
        f"[bold]章节数:[/] [data]{chapter_count}[/] ([success]{success_count} 成功[/], [warn]{chapter_count - success_count} 失败[/])\n"
        f"[bold]成功率:[/] [data]{success_rate:.2f}%[/]\n"
        f"[bold]保存路径:[/] [url]{novel_file_path}[/]\n"
        f"[bold]用时:[/] [data]{format_time(download_time)}[/]",
        title="[title]下载完成[/]",
        border_style="bold green",
        expand=True,
        padding=(1, 4)
    ))

def process_chapter_divs(chapter_divs_list, volume_name, chapter_list, base_url, root_url):
    """处理章节div列表，提取章节信息"""
    if len(chapter_divs_list) == 0:
        logger.error("找不到符合规则的章节区域")
        logger.info("请检查规则表达式是否正确")
        # 输出调试信息
        logger.debug(f"章节区域规则: {rule_novel_chapter_div}")
        logger.debug(f"chapter_divs_list: {chapter_divs_list}")
        exit_program(1)
    elif len(chapter_divs_list) > 1:
        logger.warning("找到多个符合规则的章节区域")
        logger.info("将遍历所用章节区域")

    chapter_div_list = []
    for chapter_div in chapter_divs_list:
        chapter_div_list += css_select(chapter_div, rule_novel_chapter_div_only)
    
    if len(chapter_div_list) == 0:
        logger.error("找不到符合规则的单个章节区域")
        exit_program(1)
    elif len(chapter_div_list) == 1:
        logger.warning("找到一个符合规则的单个章节区域")
        logger.info("只有一章？")

    # 遍历所有章节div
    for chapter_div in chapter_div_list:
        # 获取章节名称，使用css_select选择符合rule_novel_chapter_name规则的元素，并提取文本内容，去除首尾空格
        if rule_novel_chapter_name:
            # 如果有指定规则，使用选择器
            name_elements = css_select(chapter_div, rule_novel_chapter_name)
            if name_elements:
                chapter_name = name_elements[0].text.strip()
            else:
                # 回退方案：尝试获取当前元素的文本
                chapter_name = chapter_div.text.strip()
        else:
            # 没有指定规则时直接使用元素文本
            chapter_name = chapter_div.text.strip()

        # 获取章节URL，使用css_select选择符合rule_novel_chapter_url规则的元素，并提取href属性值
        if rule_novel_chapter_url:
            url_elements = css_select(chapter_div, rule_novel_chapter_url)
            if url_elements:
                chapter_url = url_elements[0].get('href')
            else:
                chapter_url = chapter_div.get('href', '')
        else:
            chapter_url = chapter_div.get('href', '')
        
        if chapter_url.startswith('/'):
            chapter_url = root_url + chapter_url
        elif chapter_url.startswith("./"):
            chapter_url = base_url + chapter_url[2:]
        elif chapter_url.startswith("."):
            chapter_url = base_url + chapter_url[1:]
        else:
            chapter_url = chapter_url
        
        # 检查章节URL是否为空
        if chapter_url == '' or chapter_url is None:
            logger.warning("章节URL为空，跳过该章节")
            continue
        
        # 检查章节 URL 是否为JS链接
        if chapter_url.startswith('javascript:'):
            # 使用正则提取真实路径
            match = re.search(r"dd_show\('(.*?)'\)", chapter_url)
            if match:
                chapter_url = match.group(1)
            else:
                logger.warning(f"无法解析的JS链接: {chapter_url}")
                continue
        
        # 将分卷名称、章节名称和URL添加到chapter_list列表中
        chapter_list.append((volume_name, chapter_name, chapter_url))

if __name__ == '__main__':
    # 监听程序退出信号
    signal.signal(signal.SIGINT, signal_handler)
    # 运行主函数
    try:
        try:
            load_config()
            logger.info(f"配置文件加载完成")
        except Exception as e:
            logger.error(f"[error]✗ 加载配置文件失败: {e}[/]")
            exit_program(1)
        main()
    except Exception as e:
        logger.critical(f"[error]✗ 程序发生错误: {e}[/]")
        if debug:
            console.print(Traceback(show_locals=True))
        exit_program(1)
