#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/05/02
# @Author  : Kissablecho
# @Software: Visual Studio Code
# @Blog    : https://blog.ksable.top/
# @Github  : https://github.com/God-2077/

from astral import LocationInfo
from astral.sun import sun
from datetime import datetime
import pytz  # 用于时区处理

def calculate_sun_times(latitude, longitude, date):
    # 创建地点信息，并指定时区为 Asia/Shanghai（北京时区）
    location = LocationInfo(latitude=latitude, longitude=longitude, timezone="Asia/Shanghai")

    # 将输入的日期转换为 datetime 对象
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    # 计算太阳信息
    s = sun(location.observer, date=date_obj, tzinfo=pytz.timezone(location.timezone))

    # 提取日出和日落时间（已经是本地时间）
    sunrise_time = s['sunrise']
    sunset_time = s['sunset']

    # 计算太阳方位角
    def sun_azimuth(time):
        from astral.sun import azimuth
        return azimuth(location.observer, time)

    sunrise_azimuth = sun_azimuth(sunrise_time)
    sunset_azimuth = sun_azimuth(sunset_time)

    # 输出结果
    print(f"日出时间: {sunrise_time.strftime('%Y-%m-%d %H:%M:%S')}, 方位角: {sunrise_azimuth:.2f}°")
    print(f"日落时间: {sunset_time.strftime('%Y-%m-%d %H:%M:%S')}, 方位角: {sunset_azimuth:.2f}°")

if __name__ == "__main__":
    # 输入经纬度和日期
    print("请输入经纬度和日期（时区 Asia/Shanghai）:")
    latitude = float(input("纬度: "))
    longitude = float(input("经度: "))
    date = input("日期 (YYYY-MM-DD): ")

    # 计算并输出太阳的日出、日落时间和方位角
    calculate_sun_times(latitude, longitude, date)