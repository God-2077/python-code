#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/03
# @Author  : Kissablecho
# @Software: Visual Studio Code
# @Blog    : https://blog.ksable.top/
# @Github  : https://github.com/God-2077/

import os
import requests
from bs4 import BeautifulSoup
import sys
import time
import re
import signal
import uuid
from ebooklib import epub
import traceback
import yaml
# 导入rich库
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.prompt import Confirm, Prompt

# 定义全局变量
if len(sys.argv) < 2:
    print("Usage: python script.py config.yml")
    sys.exit(1)

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
request_interval_ms = config['network']['request_interval_ms']

debug = config['basic']['debug']

# 创建全局Console对象
console = Console()
last_request_time = None

# 函数定义

def get_unique_file_path(file_path):
    base_path, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base_path}({counter}){ext}"
        counter += 1
    return file_path

def console_log(text, level='log', end='\n'):
    """使用rich库增强的日志输出函数"""
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # 定义日志级别及其对应的样式
    log_styles = {
        'log': Style(color="blue", bold=False),
        'info': Style(color="green", bold=False),
        'warn': Style(color="yellow", bold=True),
        'error': Style(color="red", bold=True),
        'debug': Style(color="magenta", bold=False)
    }
    
    # 日志标签映射
    log_labels = {
        'log': '[LOG]',
        'info': '[INFO]',
        'warn': '[WARN]',
        'error': '[ERROR]',
        'debug': '[DEBUG]'
    }
    
    if level in log_styles:
        label = log_labels[level]
        style = log_styles[level]
        # 使用Text对象组合不同样式的文本
        output_text = Text(f"{localtime} ")
        output_text.append(label.ljust(8), style=style)
        output_text.append(f": {text}")
        console.print(output_text, end=end)
    else:
        # 未知级别处理
        unknown_label = f"[{level.upper()}]".ljust(8)
        console.print(f"{localtime} {unknown_label}: {text}", end=end)

# 网络请求
def get_url(url):
    global last_request_time
    # 毫秒级的时间戳
    if last_request_time is not None:
        current_time = int(time.time() * 1000)
        if current_time - last_request_time < request_interval_ms:
            time.sleep((current_time - last_request_time) / 1000)
    retries = 0
    while retries < max_retries:
        try:
            if cookies and cookies != {}:  # 当cookies存在时使用
                response = requests.get(url, headers=headers, timeout=timeout, cookies=cookies)
            else:
                response = requests.get(url, headers=headers, timeout=timeout)
            if debug:
                console_log(f"请求成功[{response.status_code}]: {url}", level='debug')
            return response
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            console_log(f"请求失败，正在重试 ({retries + 1}/{max_retries})...", level='warn')
            if debug:
                console_log(f"错误信息: URL({url}) {e}", level='debug')
            time.sleep(1)
            retries += 1
    console_log("请求失败，已达到最大重试次数。", level='error')
    return None

# 解析网页内容，返回 BeautifulSoup 对象
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    return soup

# css 选择器，返回解析后的内容
def css_select(soup, rule):
    try:
        return soup.select(rule)
    except AttributeError:
        console_log(f"找不到符合规则 {rule} 的内容", level='error')
        return []

# 退出程序
def exit_program(status_code=0):
    console_log("程序退出", level='info')
    sys.exit(status_code)

# 安全的文件名
def safe_filename(filename):
    return re.sub(r'[\\/:*?"<>|]', '', filename)

# 追加写入文件
def write_file_a(text, path, encoding='utf-8'):
    try:
        with open(path, 'a', encoding=encoding) as file_a:
            file_a.write(text)
            file_a.close()
    except Exception as e:
        console_log(f"写入文件失败: {e}", level='error')
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
    console_log("\n程序被中断，正在退出...", level='info')
    exit_program(1)

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

# 主函数开始

def main():
    if debug:
        console_log("Debug模式已开启", level='debug')
        console_log("参数列表:", level='debug')
        console_log(f"小说详情页面的 URL: {novel_detail_url}", level='debug')
        console_log(f"小说章节列表页面的 URL 列表: {novel_chapter_url}", level='debug')
        console_log(f"小说名称的规则表达式: {rule_novel_name}", level='debug')
        console_log(f"小说作者的规则表达式: {rule_novel_author}", level='debug')
        console_log(f"小说简介的规则表达式: {rule_novel_intro}", level='debug')
        console_log(f"小说章节区域的规则表达式: {rule_novel_chapter_div}", level='debug')
        console_log(f"小说章节区域的规则表达式(仅单个章节): {rule_novel_chapter_div_only}", level='debug')
        console_log(f"小说章节名称的规则表达式: {rule_novel_chapter_name}", level='debug')
        console_log(f"小说章节 URL 的规则表达式: {rule_novel_chapter_url}", level='debug')
        console_log(f"小说章节内容区域的规则表达式: {rule_novel_chapter_content_div}", level='debug')
        console_log(f"小说分段规则的规则表达式: {rule_novel_chapter_content_p}", level='debug')
        console_log(f"缩进字符串: {indent_string}", level='debug')
        console_log(f"小说净化内容的文本规则表达式: {rule_novel_chapter_content_purify_text}", level='debug')
        console_log(f"小说净化内容的正则表达式规则表达式: {rule_novel_chapter_content_purify_re}", level='debug')
        console_log(f"小说的保存路径: {download_path}", level='debug')
        console_log(f"小说文件的编码: {novel_file_encoding}", level='debug')
        console_log(f"输出格式: {output_format}", level='debug')
        console_log(f"网络请求头: {headers}", level='debug')
        console_log(f"网络请求超时时间: {timeout}", level='debug')
        console_log(f"网络请求失败重试次数: {max_retries}", level='debug')
        console_log(f"网络请求间隔时间（ms）: {request_interval_ms}", level='debug')
        console_log(f"上次请求时间: {last_request_time}", level='debug')
        console_log(f"Debug 模式: {debug}", level='debug')
        console_log("参数列表结束", level='debug')

    # 开始时间
    start_time = time.time()
    
    # 显示小说信息面板
    with console.status("[bold green]正在获取小说信息...[/]"):
        # 获取小说详情页面的内容
        response_novel_detail = get_url(novel_detail_url)
        if response_novel_detail is None:
            console_log("获取小说详情页面失败", level='error')
            exit_program(1)
        soup = parse_html(response_novel_detail.content)

        # 获取小说名称
        if rule_novel_name == '' or rule_novel_name is None:
            console_log("小说名称的规则表达式为空，使用“小说”作为小说名称", level='warn')
            novel_name = "小说"
        else:
            novel_name = css_select(soup, rule_novel_name)[0].text.strip()
        
        # 获取小说作者
        if rule_novel_author == '' or rule_novel_author is None:
            console_log("小说作者的规则表达式为空，使用“佚名”作为小说作者", level='warn')
            novel_author = "佚名"
        else:
            novel_author = css_select(soup, rule_novel_author)[0].text.strip()
        
        # 获取小说简介
        if rule_novel_intro == '' or rule_novel_intro is None:
            console_log("小说简介的规则表达式为空，使用“暂无简介”作为小说简介", level='warn')
            novel_intro = "暂无简介"
        else:
            novel_intro = css_select(soup, rule_novel_intro)[0].text.strip()
    
    # 显示小说信息面板
    info_panel = Panel(
        f"[bold]小说名称:[/bold] {novel_name}\n"
        f"[bold]作者:[/bold] {novel_author}\n"
        f"[bold]来源:[/bold] {novel_detail_url}\n"
        f"[bold]简介:[/bold] {novel_intro[:200]}{'...' if len(novel_intro) > 200 else ''}",
        title="小说信息",
        border_style="bold blue",
        expand=False
    )
    console.print(info_panel)

    # 获取章节列表
    chapter_list = []
    
    if not (novel_chapter_url and rule_novel_chapter_div and rule_novel_chapter_div_only and rule_novel_chapter_name and rule_novel_chapter_url):
        console_log("小说章节列表页面的 URL 列表、小说章节区域、小说单个章节的区域、小说章节名称、小说章节 URL的规则表达式不可为空", level='error')
        exit_program(1)
    else:
        with console.status("[bold green]正在获取章节列表..."):
            console_log("开始获取章节列表", level='info')
            for chapter_url in novel_chapter_url:
                # 获取章节列表页面的内容
                response_chapter_list = get_url(chapter_url)
                response_chapter_list = parse_html(response_chapter_list.content)
                response_chapter_list_base_url = get_base_url(chapter_url)
                response_chapter_list_root_url = get_root_url(chapter_url)
                # 使用css_select函数选择所有符合rule_novel_chapter_div规则的章节div
                chapter_divs_list = css_select(response_chapter_list, rule_novel_chapter_div)
                if len(chapter_divs_list) == 0:
                    console_log("找不到符合规则的章节区域", level='error')
                    console_log("请检查规则表达式是否正确", level='info')
                    # 输出调试信息
                    if debug:
                        console_log(f"章节区域规则: {rule_novel_chapter_div}", level='debug')
                        console_log(f"chapter_divs_list: {chapter_divs_list}", level='debug')  # 输出部分页面内容进行调试
                        console_log(f"页面内容: {response_chapter_list.text}", level='debug')  # 输出部分页面内容进行调试
                    exit_program(1)
                elif len(chapter_divs_list) > 1:
                    console_log("找到多个符合规则的章节区域", level='warn')
                    console_log("将遍历所用章节区域", level='info')

                chapter_div_list = []
                for chapter_div in chapter_divs_list:
                    chapter_div_list += css_select(chapter_div, rule_novel_chapter_div_only)
                if len(chapter_div_list) == 0:
                    console_log("找不到符合规则的单个章节区域", level='error')
                    exit_program(1)
                elif len(chapter_div_list) == 1:
                    console_log("找到一个符合规则的单个章节区域", level='warn')
                    console_log("只有一章？", level='info')

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
                        chapter_url = response_chapter_list_root_url + chapter_url
                    elif chapter_url.startswith("./"):
                        chapter_url = response_chapter_list_base_url + chapter_url[2:]
                    elif chapter_url.startswith("."):
                        chapter_url = response_chapter_list_base_url + chapter_url[1:]
                    else:
                        chapter_url = chapter_url
                    # 检查章节URL是否为空
                    if chapter_url == '' or chapter_url is None:
                        console_log("章节URL为空，跳过该章节", level='warn')
                        continue
                    # 检查章节 URL 是否为JS链接
                    if chapter_url.startswith('javascript:'):
                        # 使用正则提取真实路径
                        match = re.search(r"dd_show\('(.*?)'\)", chapter_url)
                        if match:
                            chapter_url = match.group(1)
                        else:
                            console_log(f"无法解析的JS链接: {chapter_url}", level='warn')
                            continue
                    # 将章节名称和URL作为元组添加到chapter_list列表中
                    chapter_list.append((chapter_name, chapter_url))

    # 小说章节总数
    chapter_count = len(chapter_list)

    console_log(f"章节列表获取完成，共 {chapter_count} 章", level='info')

    # 检查章节列表是否为空
    if chapter_count == 0:
        console_log("章节列表为空，无法下载小说", level='error')
        exit_program(1)
    
    # 显示章节预览表格
    if chapter_count > 0:
        table = Table(title="章节预览", show_header=True, header_style="bold magenta")
        table.add_column("序号", style="cyan", width=6)
        table.add_column("章节名称", style="green")
        table.add_column("URL", style="blue", overflow="fold")
        
        # 显示前5章和后5章
        for i, (chapter_name, chapter_url) in enumerate(chapter_list[:5]):
            table.add_row(str(i+1), chapter_name, chapter_url)
        
        if chapter_count > 10:
            table.add_row("...", "...", "...")
            for i in range(max(0, chapter_count-5), chapter_count):
                chapter_name, chapter_url = chapter_list[i]
                table.add_row(str(i+1), chapter_name, chapter_url)
        elif chapter_count > 5:
            for i in range(5, chapter_count):
                chapter_name, chapter_url = chapter_list[i]
                table.add_row(str(i+1), chapter_name, chapter_url)
        
        console.print(table)

    # 开始下载小说
    console_log("小说信息获取完成，即将开始下载小说", level='info')

    # 用户确认
    if not Confirm.ask("是否开始下载？", default=True):
        console.print("[bold yellow]用户取消下载[/]")
        exit(0)
    else:
        console.print("[bold green]开始下载...[/]")
    
    # 下载小说

    # 创建小说文件
    if output_format == 'epub':
        novel_file = f"{novel_name} - {novel_author}.epub"
    elif output_format == 'txt':
        novel_file = f"{novel_name} - {novel_author}.txt"
    else:
        console_log("输出格式不支持，请选择 txt 或 epub", level='error')
        exit_program(1)
    novel_file = safe_filename(novel_file)
    novel_file_path = os.path.join(download_path, novel_file)
    
    # 检查文件是否存在
    if os.path.exists(novel_file_path):
        console.print(f"[bold yellow]文件 {novel_file_path} 已存在[/]")
        if Confirm.ask("是否覆盖下载？", default=False):
            console.print("[bold yellow]用户选择覆盖下载[/]")
        else:
            if Confirm.ask("是否跳过该文件名，使用“小说名（序号）”下载？", default=True):
                novel_file_path = get_unique_file_path(novel_file_path)
                console.print(f"[bold green]新文件名: {novel_file_path}[/]")
            else:
                console.print("[bold yellow]取消下载[/]")
                exit_program(0)
    console.print(f"[bold green]小说保存文件路径: {novel_file_path}[/]")
    
    # 写入小说信息
    # 创建 txt 文件
    if output_format == 'txt':
        try:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            with open(novel_file_path, 'w', encoding=novel_file_encoding) as novel_file_x:
                novel_file_x.write(f"书名：{novel_name}\n")
                novel_file_x.write(f"来源：{novel_detail_url}\n")
                novel_file_x.write(f"作者：{novel_author}\n")
                novel_file_x.write(f"简介：\n{indent_string}{novel_intro}\n\n")
        except Exception as e:
            console_log(f"写入文件失败: {e}", level='error')
            exit_program(1)
    # 创建 epub 文件
    elif output_format == 'epub':
        if not os.path.exists(download_path):
            os.makedirs(download_path)
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
        # 存储章节对象的列表
        epub_chapter_items = []
        # 添加介绍章节到章节列表
        epub_chapter_items.append(epub_book_intro)
        epub_book_chapter_count = 0  # 初始化章节计数
        epub_book_chapter_listtoc = []

    # 使用rich的Progress创建进度条
    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        TimeRemainingColumn(),
        console=console,
        expand=True
    )
    
    # 遍历爬取章节内容
    task_id = progress.add_task("[cyan]下载章节...", total=chapter_count)
    
    with progress:
        for i, (chapter_name, chapter_url) in enumerate(chapter_list):
            try:
                # 更新进度条描述
                progress.update(task_id, description=f"[cyan]下载中[{i+1}/{chapter_count}]: {chapter_name[:20]}{'...' if len(chapter_name) > 20 else ''}")

                
                # 初始化章节内容
                chapter_content = ''
                
                # 获取章节内容
                chapter_response = get_url(chapter_url)
                if chapter_response is None:
                    console_log("获取章节内容失败", level='error')
                    if not Confirm.ask("是否跳过该章节？", default=True):
                        console_log("用户选择跳过该章节", level='info')
                        progress.update(task_id, advance=1)
                        continue
                    else:
                        console_log("那就取消下载吧", level='info')
                        exit_program(1)
                chapter_soup = parse_html(chapter_response.content)
                # 获取章节内容区域
                chapter_content_div = css_select(chapter_soup, rule_novel_chapter_content_div)
                if len(chapter_content_div) == 0:
                    console_log("找不到符合规则的章节内容区域，将跳过该章节", level='error')
                    progress.update(task_id, advance=1)
                    continue
                elif len(chapter_content_div) > 1:
                    console_log("找到多个符合规则的章节内容区域", level='warn')
                    console_log("将遍历爬取", level='info')
                elif len(chapter_content_div) == 1:
                    pass
                else:
                    console_log("未知错误", level='error')
                    exit_program(1)
                
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
                        console_log("找不到符合规则的章节内容段落", level='warn')
                        # 记录错误信息并继续处理下一个章节
                        continue
                    else:
                        for chapter_content_p in chapter_content_p_list:
                            # 处理 br 模式获取的预分割段落
                            if rule_novel_chapter_content_p.lower() == 'br':
                                paragraph_text = chapter_content_p
                            else:
                                paragraph_text = chapter_content_p.text.strip()
                            
                            if not paragraph_text:
                                continue

                            if chapter_content_p == '':
                                continue
                            else:
                                # 组合章节内容
                                if output_format == 'epub':
                                    # 对于 epub 格式，使用 HTML 标签
                                    chapter_content += f"<p>{chapter_content_p}</p>\n"
                                elif output_format == 'txt':
                                    # 对于 txt 格式，使用纯文本
                                    chapter_content += f"{indent_string}{chapter_content_p}\n"
                
                if chapter_content == '':
                    console_log("章节内容为空", level='warn')
                else:
                    # 净化章节内容
                    chapter_content = purify_content(chapter_content)

                # 写入文件
                if output_format == 'txt':
                    write_file_a(f"{chapter_name}\n\n{chapter_content}\n\n", novel_file_path, encoding=novel_file_encoding)
                elif output_format == 'epub':
                    epub_book_chapter_count = int(epub_book_chapter_count) + 1
                    epub_book_chapter_count = "{:0>4d}".format(epub_book_chapter_count)
                    epub_chapter = epub.EpubHtml(
                        title=chapter_name,
                        file_name=f"chap_{epub_book_chapter_count}.xhtml",
                        lang="zh"
                    )
                    epub_chapter.content = epub_chapter_html_render(chapter_name, chapter_content)
                    epub_book_chapter_listtoc.append((epub_book_chapter_count,chapter_name))
                    # 添加到书籍
                    epub_book.add_item(epub_chapter)
                    # 添加到章节列表
                    epub_chapter_items.append(epub_chapter)

                # 更新进度条
                progress.update(task_id, advance=1)
                
            except Exception as e:
                console_log(f"章节处理失败: {chapter_name} - {str(e)}", level='error')
                console_log("错误详情:", level='debug')
                console_log(traceback.format_exc(), level='debug')
                progress.update(task_id, advance=1)
                continue

    if output_format == 'epub':
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
            text-align: center;
            font-size: 1.8em;
            margin-top: 2em;
            margin-bottom: 1.5em;
            border-bottom: 1px solid #ccc;
            padding-bottom: 0.5em;
        }
        h2 {
            font-size: 1.4em;
            margin-top: 1.8em;
        }
        p {
            text-indent: 2em;
            margin: 0.8em 0;
        }
        ul {
            padding-left: 3em;
        }
        li {
            margin: 0.5em 0;
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
            epub_book.toc.append(epub.Link(f"chap_{i}.xhtml", title, f"chap_{i}"))

        #添加导航
        epub_book.add_item(epub.EpubNcx())
        epub_book.add_item(epub.EpubNav())

        # 设置阅读顺序
        # 书脊（阅读顺序）：封面、导航、介绍、各章节
        epub_book.spine = ["nav", *epub_chapter_items]

        # 生成文件
        with console.status("[bold green]正在生成EPUB文件..."):
            epub.write_epub(novel_file_path,epub_book,{})

    # 下载用时
    end_time = time.time()
    download_time = end_time - start_time
    console.print(Panel(
        f"[bold green]下载完成![/]\n"
        f"小说名称: [bold]{novel_name}[/]\n"
        f"作者: [bold]{novel_author}[/]\n"
        f"章节数: [bold]{chapter_count}[/]\n"
        f"保存路径: [bold]{novel_file_path}[/]\n"
        f"用时: [bold]{format_time(download_time)}[/]",
        title="下载完成",
        border_style="bold green",
        expand=False
    ))

if __name__ == '__main__':
    # 监听程序退出信号
    signal.signal(signal.SIGINT, signal_handler)
    # 运行主函数
    try:
        main()
    except Exception as e:
        console_log(f"程序发生错误: {e}", level='error')
        if debug:
            console_log("错误详情:", level='debug')
            console_log(traceback.format_exc(), level='debug')
        exit_program(1)