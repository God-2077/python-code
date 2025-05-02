#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/01
# @Author  : Kissablecho
# @Software: Visual Studio Code
# @Blog    : https://blog.ksable.top/
# @Github  : https://github.com/God-2077/

import markdownify
import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import signal

# 全局变量

# index_url = 'https://www.runoob.com/python/'
# downdir = '/storage/emulated/0/git/python-code/h/'

# 后续记得写速率控制，和input

index_url = str(input("index_url: "))
downdir = str(input("downdir: "))

if not downdir.endswith('/'):
    downdir = downdir + "/"
# 文件路径生成
if not os.path.exists(downdir):
    os.makedirs(downdir)
#------------------------

# 网络请求，直接返回text
def get_url(url,headers=None,encoding="",return_content_and_reality_url=False):
    # 设置请求头
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    # 发送请求
    response = requests.get(url,headers=headers)
    #设置编码
    if encoding != "":
        response.encoding = encoding
    if return_content_and_reality_url:
        x=[]
        x.append(response.url) # url
        x.append(response.content) # 内容
        return(x)
    return(response.content)



# 转 markdown
def to_markdown(html_text):
    html_text = change_example_code_divs(html_text) # 处理实例代码
    return(markdownify.markdownify(html_text))

# 写入文件，必须用绝对路径
def write_file(text,path,encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as f:
        f.write(text)
        f.close()
# def write_file(text,path):
#     with open(path, 'w') as f:
#         f.write(text)
#         f.close()

# 追加写入文件
def write_file_a(text,path):
    with open(path, 'a', encoding='utf-8') as file_a:
        file_a.write(text)
        file_a.close()

# 读取文件
def read_file(path,encoding='utf-8'):
    x = open(path, 'r', encoding=encoding)
    t = x.read()
    x.close()
    return(t)

# url_root
def get_root_url(url):
    # 去掉任何末尾的路径部分，只保留域名和最后的路径部分
    url = re.sub(r'/[^/]*$', '/', url)
    return url

# 首页url
def get_base_url(url):
    # 正则表达式匹配协议和域名部分
    match = re.match(r'(https?://[^/]+)', url)
    if match:
        return match.group(1)
    return None

# 安全文件名
def safe_filename(filename):
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

# 删除被<>包裹的内容
def remove_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def change_example_code_divs(html_content):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有包含代码的容器
    example_code_divs = soup.find_all('div', class_='example_code')

    # 如果找到了包含代码的容器，进行处理
    for example_code_div in example_code_divs:
        # 提取所有文本内容并去除多余的HTML标签
        code_lines = example_code_div.get_text()
        
        # 去除多余的空行与空格
        cleaned_code = re.sub(r'\n\s*\n', '\n', code_lines).strip()
        
        # 构建标准化的 <pre><code> 结构
        new_code_block = soup.new_tag('pre')
        code_tag = soup.new_tag('code')
        code_tag.string = cleaned_code
        new_code_block.append(code_tag)

        # 将原始代码块替换为新的标准代码块
        example_code_div.replace_with(new_code_block)

    # 输出转换后的HTML
    return((soup.prettify()))

# 退出程序
def exit_ctrl_c(sig, frame):
    print("\n退出程序...")
    sys.exit(0)

print('载入函数成功')
#-------------------------

def main():
    index_response = get_url(index_url,return_content_and_reality_url=True)
    index_html = index_response[1]
    index_url = index_response[0]
    index_url_root = get_root_url(index_url)
    root_url = get_base_url(index_url)

    # 解析网页内容
    print("解析网页内容")
    index_soup = BeautifulSoup(index_html, 'html.parser')

    # 建立 index 列表
    print("建立 index 列表")

    index_links = []
    for link in index_soup.select('div.sidebar-box.gallery-list a'):
        # 去除两侧空格
        list_title = link.string.strip() if link.string else "No Title"
        list_link = link.get('href')
        if list_link.startswith('/'):
            list_link = root_url + list_link
        else:
            list_link = index_url_root + list_link
        index_links.append(list_title + ':::' + list_link)

    print("-----------------------------")
    print(index_links)
    print("-----------------------------")
    # 建立目录文件
    directory_file = downdir + '目录.md'
    write_file_a(f"## {index_soup.title.string}\n",directory_file)
    # with open(directory_file, 'a', encoding='utf-8') as directory_file_x:
        # directory_file_x.write(f"## {index_soup.title.string}\n")

    # 循环爬取
    print("循环爬取")
    index_links_len = len(index_links)
    for i,link in enumerate(index_links):
        # print(link)
        link = link.split(':::')
        link_url = link[1]
        link_html = get_url(link_url)
        # 解析
        link_soup = BeautifulSoup(link_html, 'html.parser')
        # print(link_soup)
        # 提取相关信息
        # title
        link_title_len = len(link_soup.select('.article-body  h1'))
        if link_title_len == 0:
            link_title_len = len(link_soup.select('.article-body  h2'))
            if link_title_len == 0:
                link_title = link[0]
            else:
                link_title = remove_tags(str(link_soup.select('.article-body  h2')[0])).strip()
                if len(link_title) > 35:
                    link_title = link[0]
        else:
            link_title = remove_tags(str(link_soup.select('.article-body  h1')[0])).strip()
            if len(link_title) > 35:
                link_title = link[0]
        # link_title = link[0]
        print(f"[{i+1}/{index_links_len}]:{link_title}")
        link_content = str(link_soup.select('.article-body')[0])
        link_content_markdown = to_markdown(link_content)
        # 生成文本内容
        link_file_content = str(f"## [{link_title}]({link_url})\n\n[index](目录.md)\n\n---\n{link_content_markdown}")
        # 文件路径
        link_file_path = downdir + safe_filename(link_title) + ".md"
        # 写入文件
        write_file(link_file_content,link_file_path)
        # 更新目录
        link_url_top = safe_filename(link_title) + ".md"
        write_file_a(f"- [{link_title}]({link_url_top.replace(" ","%20")})\n",directory_file)

    print('success !')
    print("\n退出程序...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_ctrl_c)
    main()