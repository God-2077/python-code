#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import os
import json


# JSON链接
# json_url = "https://api.injahow.cn/meting/?type=playlist&id=9313871605"

playlist = input("歌单ID：")


if playlist == '':
    print("必须输入歌单ID")
    exit()


json_url = "https://api.injahow.cn/meting/?type=playlist&id=" + playlist

# 下载路径
# download_path = "./s"
print(r"默认下载路径 D:\down")
download_path = input("下载路径：")

if download_path == '':
   download_path = r"D:\down"

# 创建下载路径
os.makedirs(download_path, exist_ok=True)



def download_song(url, song_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length'))
    downloaded_size = 0
    
    with open(song_path, "wb") as song_file:
        for data in response.iter_content(chunk_size=4096):
            downloaded_size += len(data)
            song_file.write(data)
            progress = downloaded_size / total_size * 100
            print(f"正在下载 {song_path}，进度：{progress:.2f}%\r", end="")
    
    print(f"下载完成 {song_path}")

def safe_filename(filename):
    # 将特殊字符（/）改成（-）
    return filename.replace("/", "-")
    




# 发送GET请求获取JSON数据
response = requests.get(json_url)
data = json.loads(response.text)

# 遍历每首歌曲
for song in data:
    # 歌曲信息
    name = song["name"]
    artist = song["artist"]
    url = song["url"]
    lrc = song["lrc"]

    # 歌曲文件名和路径
    song_filename = f"{safe_filename(name)} - {safe_filename(artist)}.mp3"
    song_path = os.path.join(download_path, song_filename)

    # 下载歌曲
    download_song(url, song_path)

    # 下载歌词
    lrc_response = requests.get(lrc)
    lrc_filename = f"{safe_filename(name)} - {safe_filename(artist)}.lrc"
    lrc_path = os.path.join(download_path, lrc_filename)
    with open(lrc_path, "wb") as lrc_file:
        lrc_file.write(lrc_response.content)


print("The and.")
a = input()