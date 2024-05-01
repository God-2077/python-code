#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
import librosa
from urllib.parse import quote
import time
import signal
import sys

def download_song(url, song_path, song_index, total_songs):
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
                print(f"正在下载 [{song_index}/{total_songs}] {song_path}，进度：{progress:.2f}%\r", end="")
        
        print(f"下载完成 [{song_index}/{total_songs}] {song_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载 [{song_index}/{total_songs}] {song_path} 失败：{e}")
        return False

# def safe_filename(filename):
#     # 将特殊字符（/）改成（-）
#     return filename.replace("/", "-")

def safe_filename(filename):
    # 将无效字符替换为下划线
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"删除文件：{file_path}")

def download_playlist(playlist_id, download_path):
    if not playlist_id.isdigit():
        print("歌单ID必须为数字")
        return

    # JSON链接
    api_urls = [
        "https://api.injahow.cn/meting/?type=playlist&id=",
        "https://meting.qjqq.cn/?type=playlist&id="
    ]

    selected_api = None
    data = None

    for api_url in api_urls:
        try:
            response = requests.get(f"{api_url}{playlist_id}")
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            selected_api = api_url
            if 'error' in data:
                error = data.get("error", "")
                print("出错了...")
                print(f"错误详细：{error}")
                return  # Exit the function if error is encountered in JSON response
            break
        except requests.exceptions.RequestException as e:
            print(f"API {api_url} 请求失败：{e}")
            continue

    if not data:
        print("所有API都无法获取数据")
        return

    # 创建下载路径
    os.makedirs(download_path, exist_ok=True)

    total_songs = len(data)
    print(f"歌单共有 {total_songs} 首歌曲")

    successful_downloads = 0
    failed_downloads = []

    def signal_handler(sig, frame):
        print("检测到Ctrl+C, exiting gracefully...")
        print(f"程序运行完成，共 {total_songs} 首歌曲，成功下载 {successful_downloads} 首歌曲")
        if failed_downloads:
            print(f"共有 {len(failed_downloads)} 首歌曲下载失败，id为：{','.join(failed_downloads)}")
        sys.exit(0)
        input()

    signal.signal(signal.SIGINT, signal_handler)

    for index, song in enumerate(data, start=1):
        # 歌曲信息
        name = song.get("name", "")
        artist = song.get("artist", "")
        url = song.get("url", "")
        lrc = song.get("lrc", "")
        # duration = song.get("duration", 0)  # 歌曲时长，单位：秒

        if not name or not artist or not url or not lrc:
            print(f"歌曲信息不完整：{song}")
            continue

        # 歌曲文件名和路径
        song_filename = f"{safe_filename(name)} - {safe_filename(artist)}.mp3"
        song_path = os.path.join(download_path, song_filename)

        # 下载歌曲
        retry_count = 0
        while retry_count < 5:
            if download_song(url, song_path, index, total_songs):
                successful_downloads += 1
                break
            else:
                retry_count += 1
                print(f"重试下载 [{index}/{total_songs}] {song_path}，次数：{retry_count}")
                time.sleep(1)  # 等待1秒后重试
        
        # 下载歌词
        lrc_response = requests.get(lrc)
        lrc_filename = f"{safe_filename(name)} - {safe_filename(artist)}.lrc"
        lrc_path = os.path.join(download_path, lrc_filename)
        with open(lrc_path, "w", encoding="utf-8") as lrc_file:  # 修改这里，指定编码为utf-8
            lrc_file.write(lrc_response.content.decode('utf-8'))  # 将内容以utf-8解码后写入文件
            
        # 检查歌曲时长是否小于一分钟
#        if duration < 60:
#            print(f"歌曲时长小于一分钟，删除歌曲和歌词：{song_path}")
#            delete_file(song_path)
#            lrc_filename = f"{safe_filename(name)} - {safe_filename(artist)}.lrc"
#            lrc_path = os.path.join(download_path, lrc_filename)
#            delete_file(lrc_path)
#            failed_downloads.append(song.get('id', '')) # 添加到下载失败列表
#            successful_downloads -= 1 # 减去下载成功计数

                # 使用librosa获取音频持续时间
        try:
            audio_duration = librosa.get_duration(path=song_path)
            if audio_duration < 60:
                print(f"歌曲时长小于一分钟，删除歌曲和歌词：{song_path}")
                delete_file(song_path)
                delete_file(lrc_path)
                failed_downloads.append(song.get('id', '')) # 添加到下载失败列表
                successful_downloads -= 1 # 减去下载成功计数
            else:
                print(f"歌曲时长为 {audio_duration} 秒")
        except Exception as e:
            print(f"无法获取歌曲时长：{e}")
            # failed_downloads.append(song.get('id', ''))

    print(f"程序运行完成，共 {total_songs} 首歌曲，成功下载 {successful_downloads} 首歌曲")
    if failed_downloads:
        # print(f"共有 {len(failed_downloads)} 首歌曲下载失败，id为：{','.join(failed_downloads)}")
        print(f"共有 {len(failed_downloads)} 首歌曲下载失败...")

if __name__ == "__main__":
    playlist_id = input("歌单ID：")
    download_path = input(r"下载路径（默认为 D:\down）：") or r"D:\down"

    download_playlist(playlist_id, download_path)
