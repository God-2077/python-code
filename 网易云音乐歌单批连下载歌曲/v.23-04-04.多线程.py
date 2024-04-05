#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

def download_song(url, song_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(song_path, "wb") as song_file:
            for data in response.iter_content(chunk_size=4096):
                downloaded_size += len(data)
                song_file.write(data)
                progress = downloaded_size / total_size * 100 if total_size > 0 else 0
                print(f"正在下载 {song_path}，进度：{progress:.2f}%\r", end="")
        
        print(f"下载完成 {song_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载 {song_path} 失败：{e}")

def safe_filename(filename):
    # 将特殊字符（/）改成（-）
    return filename.replace("/", "-")

def download_playlist(playlist_id, download_path):
    if not playlist_id.isdigit():
        print("歌单ID必须为数字")
        return

    # 创建下载路径
    os.makedirs(download_path, exist_ok=True)

    # JSON链接
    json_url = f"https://api.injahow.cn/meting/?type=playlist&id={quote(playlist_id)}"
    
    try:
        # 发送GET请求获取JSON数据
        response = requests.get(json_url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        # Function to download a song
        def download_song_wrapper(song):
            name = song.get("name", "")
            artist = song.get("artist", "")
            url = song.get("url", "")
            lrc = song.get("lrc", "")

            if not name or not artist or not url or not lrc:
                print(f"歌曲信息不完整：{song}")
                return

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

        # Use ThreadPoolExecutor to download songs concurrently
        with ThreadPoolExecutor(max_workers=16) as executor:
            executor.map(download_song_wrapper, data)

        print("全部歌曲下载完成")
    except requests.exceptions.RequestException as e:
        print(f"下载歌单失败：{e}")

if __name__ == "__main__":
    playlist_id = input("歌单ID：")
    download_path = input(r"下载路径（默认为 D:\down）：") or r"D:\down"
    # max = input(r"下载线程（默认为 5）：") or "5"

    download_playlist(playlist_id, download_path)
