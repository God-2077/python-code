#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import requests
from mutagen.mp3 import MP3
import time
import signal
import sys
import re
from tabulate import tabulate


def download_file(url, file_path, file_type, index, total_files, timeout=10):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(file_path, "wb") as file:
            for data in response.iter_content(chunk_size=4096):
                downloaded_size += len(data)
                file.write(data)
                progress = downloaded_size / total_size * 100 if total_size > 0 else 0
                print(f"正在下载 [{index}/{total_files}][{file_type}] {file_path}，进度：{progress:.2f}%\r", end="")

        print(f"下载完成 [{index}/{total_files}][{file_type}] {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载 [{index}/{total_files}][{file_type}] {file_path} 失败：{e}")
        return False


def download_lyrics(url, lrc_path, song_index, total_songs):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(lrc_path, "w", encoding="utf-8") as lrc_file:
            lrc_file.write(response.content.decode('utf-8'))
        print(f"下载完成 [{song_index}/{total_songs}][LRC] {lrc_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载歌词失败：{e}")
        return False


def safe_filename(filename):
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"删除文件：{file_path}")


def song_table(data):
    table_data = []
    for idx, item in enumerate(data, start=1):
        name = item['name']
        artist = item['artist']
        url_id = re.search(r'\d+', item['url']).group()
        table_data.append([idx, name, artist, url_id])
    table_headers = ["序号", "标题", "艺术家", "ID"]
    table = tabulate(table_data, table_headers, tablefmt="pipe")
    print(table)


def exit_ctrl_c(sig, frame):
    print("\n退出程序...")
    sys.exit(0)


def welcome():
    print("welcome")
    print("欢迎使用我开发的小程序")
    print("Github Rope: https://github.com/God-2077/python-code/")
    print("-------------------------")
    print("网易云音乐歌单批量下载歌曲")


def download_playlist(playlist_id, download_path):
    if not playlist_id.isdigit():
        print("歌单ID必须为数字")
        return

    error_song_name = []
    error_song_id = []

    api_urls = [
        "https://meting.qjqq.cn/?type=playlist&id=",
        "https://api.injahow.cn/meting/?type=playlist&id=",
        "https://meting-api.mnchen.cn/?type=playlist&id=",
        "https://meting-api.mlj-dragon.cn/meting/?type=playlist&id="
    ]

    selected_api = None
    data = None

    for api_url in api_urls:
        try:
            response = requests.get(f"{api_url}{playlist_id}", timeout=10)
            # if requests.status_codes != 200:
            #     print("出错了...")
            #     print(f"状态码：{requests.status_codes}")
            #     return
            response.raise_for_status()
            data = response.json()
            selected_api = api_url
            if 'error' in data:
                error = data.get("error", "")
                print("出错了...")
                print(f"错误详细：{error}")
                return
            break
        except requests.exceptions.RequestException as e:
            print(f"API {api_url} 请求失败：{e}")
            continue

    if not data:
        print("所有API都无法获取数据")
        return

    os.makedirs(download_path, exist_ok=True)

    print(f"Meting API: {selected_api}")

    total_songs = len(data)
    print(f"歌单共有 {total_songs} 首歌曲")
    song_table(data)
    envisage_size = total_songs * 7.7
    print(f"歌单共有 {total_songs} 首歌曲，预计歌曲文件总大小为 {envisage_size} MB")
    chose = str(input("是否继续下载?(yes): "))
    if chose not in ["y", "", "yes"]:
        print("退出程序...")
        sys.exit(0)
    chose = str(input("是否下载小于 60 秒的歌曲（可能为试听音乐）?(not): "))
    if chose not in ["y", "", "yes"]:
        downtrymusic = 1
    else:
        downtrymusic = 0
    successful_downloads = 0
    failed_downloads = []

    def signal_handler(sig, frame):
        print("\n检测到Ctrl+C, exiting gracefully...")
        print(f"程序运行完成，共 {total_songs} 首歌曲，成功下载 {successful_downloads} 首歌曲")
        if failed_downloads:
            print(f"共有 {len(failed_downloads)} 首歌曲下载失败")
            print("失败列表如下")
            table_data = [[i + 1, error_song_name[i], error_song_id[i]] for i in range(len(error_song_name))]
            print(tabulate(table_data, headers=["序号", "标题 - 艺术家", "ID"], tablefmt="grid"))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    for index, song in enumerate(data, start=1):
        name = song.get("name", "")
        artist = song.get("artist", "")
        url = song.get("url", "")
        lrc = song.get("lrc", "")
        pic = song.get("pic", "")

        if not name or not artist or not url or not lrc:
            print(f"歌曲信息不完整：{song}")
            continue

        song_filename = f"{safe_filename(name)} - {safe_filename(artist)}.mp3"
        song_name = f"{safe_filename(name)} - {safe_filename(artist)}"
        song_path = os.path.join(download_path, song_filename)

        retry_count = 0
        while retry_count < 5:
            if download_file(url, song_path, "MP3", index, total_songs):
                successful_downloads += 1
                state = True
                break
            else:
                retry_count += 1
                print(f"重试下载 [{index}/{total_songs}][MP3] {song_path}，次数：{retry_count}")
                state = False
                time.sleep(1)
        if state == False:
            print("")
            match = re.search(r'\d+', url)
            error_song_id.append(int(match.group()))
            error_song_name.append(song_name)
            failed_downloads.append(match)

        if state == True:
            try:
                audio = MP3(song_path)
                audio_duration = audio.info.length
                if downtrymusic == 1:
                    if audio_duration < 60:
                        print(f"歌曲时长小于一分钟，删除歌曲和取消下载歌词和图片：{song_path}")
                        delete_file(song_path)
                        audio_duration_TF = False
                        successful_downloads -= 1
                        match = re.search(r'\d+', url)
                        error_song_id.append(int(match.group()))
                        error_song_name.append(song_name)
                    else:
                        print(f"歌曲时长为 {audio_duration} 秒")
                        audio_duration_TF = True
                else:
                    print(f"歌曲时长为 {audio_duration} 秒")
                    audio_duration_TF = True
            except Exception as e:
                print(f"无法获取歌曲时长：{e}")
                print("应该为 VIP 单曲，删除歌曲文件和取消下载歌词和图片")
                delete_file(song_path)
                audio_duration_TF = False
                successful_downloads -= 1
                match = re.search(r'\d+', url)
                error_song_id.append(int(match.group()))
                error_song_name.append(song_name)
                failed_downloads.append(match)

            if audio_duration_TF:
                lrc_filename = f"{safe_filename(name)} - {safe_filename(artist)}.lrc"
                lrc_path = os.path.join(download_path, lrc_filename)

                retry_count = 0
                while retry_count < 5:
                    if download_lyrics(lrc, lrc_path, index, total_songs):
                        break
                    else:
                        retry_count += 1
                        print(f"重试下载 [{index}/{total_songs}][LRC] {lrc_path}，次数：{retry_count}")
                        time.sleep(1)

                pic_filename = f"{safe_filename(name)} - {safe_filename(artist)}.jpg"
                pic_path = os.path.join(download_path, pic_filename)

                retry_count = 0
                while retry_count < 5:
                    if download_file(pic, pic_path, "PIC", index, total_songs):
                        break
                    else:
                        retry_count += 1
                        print(f"重试下载 [{index}/{total_songs}][PIC] {pic_path}，次数：{retry_count}")
                        time.sleep(1)

    print(f"程序运行完成，共 {total_songs} 首歌曲，成功下载 {successful_downloads} 首歌曲")
    if failed_downloads or error_song_name:
        print(f"共有 {len(failed_downloads)} 首歌曲下载失败")
        print("失败列表如下")
        table_data = [[i + 1, error_song_name[i], error_song_id[i]] for i in range(len(error_song_name))]
        print(tabulate(table_data, headers=["序号", "标题 - 艺术家", "ID"], tablefmt="grid"))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_ctrl_c)
    welcome()
    playlist_id = input("歌单ID：")
    download_path = input(r"下载路径（默认为 ./down）：") or r"./down"
    download_playlist(playlist_id, download_path)
