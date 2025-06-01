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

# 初始化参数

# 基本 URL

# 小说详情页面的 URL
novel_detail_url = ''

# 小说章节列表页面的 URL 列表
novel_chapter_url = ['']
novel_chapter_url = [novel_detail_url] # 如果章节列表在小说详情页面的


# 规则表达式（css选择器）

# 小说名称
rule_novel_name = ''

# 小说作者
rule_novel_author = ''

# 小说简介
rule_novel_intro = ''

# 小说章节区域
rule_novel_chapter_div = ''

# 小说单个章节的区域(相对于小说章节区域)
rule_novel_chapter_div_only = ''

# 小说章节名称(相对于小说章节区域)
rule_novel_chapter_name = rule_novel_chapter_div_only

# 小说章节 URL(相对于小说章节区域)
rule_novel_chapter_url = rule_novel_chapter_div_only

# 小说章节内容区域
rule_novel_chapter_content_div = ''

# 小说分段规则(相对于小说章节内容区域)
rule_novel_chapter_content_p = 'p' # or 'div' or 'span' ?

# 缩进字符串
indent_string = '    '

# 小说净化内容
rule_novel_chapter_content_purify_text = [] # 需要净化的文本
rule_novel_chapter_content_purify_re = [] # 需要净化的正则表达式

# 小说的保存路径
download_path = './' # 小说保存路径，默认为当前目录

# 小说文件的编码
novel_file_encoding = 'utf-8' # 默认为utf-8，可选项：utf-8、gbk、gb2312等

# 网络请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 网络请求超时时间
timeout = 5

# 网络请求失败重试次数
max_retries = 5

# 网络请求间隔时间（ms）
request_interval_ms = 0

# 上次请求时间
last_request_time = None

# Debug 模式
debug = False

# 函数定义

def get_unique_file_path(file_path):
    base_path, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base_path}({counter}){ext}"
        counter += 1
    return file_path

def console_log(text, level='log',end='\n'):
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if level == 'log':
        print(f"{localtime} [LOG]: {text}",end=end)
    elif level == 'info':
        print(f"{localtime} [INFO]: {text}",end=end)
    elif level == 'warn':
        print(f"{localtime} [WARN]: {text}",end=end)
    elif level == 'error':
        print(f"{localtime} [ERROR]: {text}",end=end)
    elif level == 'debug':
        print(f"{localtime} [DEBUG]: {text}",end=end)
    else:
        print(f"{localtime} [UNKNOWN LEVEL]: {text}",end=end)

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
            response = requests.get(url, headers=headers, timeout=timeout)
            return response
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            console_log(f"请求失败，正在重试 ({retries + 1}/{max_retries})...", level='warn')
            if debug:
                console_log(f"错误信息: {e}", level='debug')
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
    if content == '' or content is None:
        return ''
    if rule_novel_chapter_content_purify_text == []:
        for rule in rule_novel_chapter_content_purify_text:
            content = content.replace(rule, '')
    if rule_novel_chapter_content_purify_re == []:
        for rule in rule_novel_chapter_content_purify_re:
            content = re.sub(rule, '', content)
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

# 主函数开始

def main():
    # 开始时间
    start_time = time.time()
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
        console_log(f"小说名称: {novel_name}", level='info')

    # 获取小说作者
    if rule_novel_author == '' or rule_novel_author is None:
        console_log("小说作者的规则表达式为空，使用“佚名”作为小说作者", level='warn')
        novel_author = "佚名"
    else:
        novel_author = css_select(soup, rule_novel_author)[0].text.strip()
        console_log(f"小说作者: {novel_author}", level='info')

    # 获取小说简介
    if rule_novel_intro == '' or rule_novel_intro is None:
        console_log("小说简介的规则表达式为空，使用“暂无简介”作为小说简介", level='warn')
        novel_intro = "暂无简介"
    else:
        novel_intro = css_select(soup, rule_novel_intro)[0].text.strip()
        console_log(f"小说简介: {novel_intro}", level='info')

    # 获取章节列表
    chapter_list = []
    
    if not (novel_chapter_url and rule_novel_chapter_div and rule_novel_chapter_div_only and rule_novel_chapter_name and rule_novel_chapter_url):
        console_log("小说章节列表页面的 URL 列表、小说章节区域、小说单个章节的区域、小说章节名称、小说章节 URL的规则表达式不可为空", level='error')
        exit_program(1)
    else:
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
                chapter_name = css_select(chapter_div, rule_novel_chapter_name)[0].text.strip()

                # 获取章节URL，使用css_select选择符合rule_novel_chapter_url规则的元素，并提取href属性值
                chapter_url = css_select(chapter_div, rule_novel_chapter_url)[0].get('href')
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
                # 将章节名称和URL作为元组添加到chapter_list列表中
                chapter_list.append((chapter_name, chapter_url))

    # 小说章节总数
    chapter_count = len(chapter_list)

    console_log(f"章节列表获取完成，共 {chapter_count} 章", level='info')


    # 检查章节列表是否为空
    if chapter_count == 0:
        console_log("章节列表为空，无法下载小说", level='error')
        exit_program(1)
    

    # 打印章节列表
    chapter_show_count = 8
    chapter_show_status = True
    console_log("章节列表:", level='info')
    for chapter_name, chapter_url in chapter_list:
        if chapter_show_status:
            if chapter_show_count > 0:
                chapter_show_count -= 1
                console_log(f"章节名称: {chapter_name}, 章节链接: {chapter_url}", level='info')
            else:
                console_log("......", level='info')
                chapter_show_status = False
        else:
            pass

    # 开始下载小说
    console_log("小说信息获取完成，即将开始下载小说", level='info')

    # 用户确认
    user_confirm = input("是否开始下载？（Y/N）")
    if user_confirm.lower() not in ['y', 'yes', '']:
        print("用户取消下载")
        exit(0)
    else:
        print("开始下载")
    
    # 下载小说

    # 创建小说文件
    novel_file = f"{novel_name} - {novel_author}.txt"
    novel_file = safe_filename(novel_file)
    novel_file_path = download_path + novel_file
    # console_log(f"小说保存文件路径: {novel_file_path}", level='info')
    # 检查文件是否存在
    if os.path.exists(novel_file_path):
        console_log(f"文件 {novel_file_path} 已存在", level='warn')
        user_confirm = input(f"文件 {novel_file_path} 已存在，是否覆盖下载？（Y/N）")
        if user_confirm.lower() in ['y', 'yes', '']:
            console_log("用户选择覆盖下载", level='info')
        else:
            user_confirm = input("是否跳过该文件名，使用“小说名（序号）.txt”下载？（Y/N）")
            if user_confirm.lower() in ['y', 'yes', '']:
                console_log("用户选择跳过下载", level='info')
                novel_file_path = get_unique_file_path(novel_file_path)
            else:
                console_log("那就取消下载吧", level='info')
                exit_program(0)
    console_log(f"小说保存文件路径: {novel_file_path}", level='info')
        

    # 写入小说信息
    try:
        with open(novel_file_path, 'w', encoding=novel_file_encoding) as novel_file_x:
            novel_file_x.write(f"书名：{novel_name}\n")
            novel_file_x.write(f"来源：{novel_detail_url}\n")
            novel_file_x.write(f"作者：{novel_author}\n")
            novel_file_x.write(f"简介：\n{indent_string}{novel_intro}\n\n")
    except Exception as e:
        console_log(f"写入文件失败: {e}", level='error')
        exit_program(1)
    
    # 遍历爬取章节内容
    for i, (chapter_name, chapter_url) in enumerate(chapter_list):
        # 初始化章节内容
        chapter_content = ''
        console_log(f"[{i}/{chapter_count}]下载章节中: {chapter_name}", level='info',end='\r')
        # 获取章节内容
        chapter_response = get_url(chapter_url)
        if chapter_response is None:
            console_log("获取章节内容失败", level='error')
            user_confirm = input("是否跳过该章节？（Y）或者取消下载（N）")
            if user_confirm.lower() not in ['y', 'yes', '']:
                console_log("用户选择跳过该章节", level='info')
                continue
            else:
                console_log("那就取消下载吧", level='info')
                exit_program(1)
        chapter_soup = parse_html(chapter_response.content)
        # 获取章节内容区域
        chapter_content_div = css_select(chapter_soup, rule_novel_chapter_content_div)
        if len(chapter_content_div) == 0:
            console_log("找不到符合规则的章节内容区域，将跳过该章节", level='error')
            continue
        elif len(chapter_content_div) > 1:
            console_log("找到多个符合规则的章节内容区域", level='warn')
            console_log("将遍历爬取", level='info')
        elif len(chapter_content_div) == 1:
            pass
        else:
            console_log("未知错误", level='error')
            exit_program(1)
        # 获取章节每一段内容
        for chapter_content_div_only in chapter_content_div:
            chapter_content_p_list = css_select(chapter_content_div_only, rule_novel_chapter_content_p)
            if len(chapter_content_p_list) == 0:
                console_log("找不到符合规则的章节内容段落", level='warn')
                # 记录错误信息并继续处理下一个章节
                continue
            else:
                for chapter_content_p in css_select(chapter_content_div_only, rule_novel_chapter_content_p):
                    chapter_content_p = chapter_content_p.text.strip()
                    if chapter_content_p == '':
                        console_log("章节内容为空", level='warn')
                    else:
                        # 组合章节内容
                        chapter_content += f"{indent_string}{chapter_content_p}\n"

            # 净化章节内容
            chapter_content = purify_content(chapter_content)

            # 写入文件
            write_file_a(f"{chapter_name}\n\n{chapter_content}\n\n", novel_file_path, encoding=novel_file_encoding)
        console_log(f"[{i}/{chapter_count}]下载章节完成: {chapter_name}", level='info')
    # 下载用时
    end_time = time.time()
    download_time = end_time - start_time
    console_log(f"下载完成，用时 {download_time} 秒", level='info')

if __name__ == '__main__':
    # 监听程序退出信号
    signal.signal(signal.SIGINT, signal_handler)
    # 运行主函数
    main()