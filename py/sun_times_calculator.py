from skyfield import almanac
from skyfield.api import load, Topos
import pytz
from datetime import datetime
from pytz import timezone as pytz_timezone

# 加载星历数据
eph = load('de421.bsp')
sun = eph['sun']
earth = eph['earth']

def calculate_sun_times():
    # 用户输入
    latitude = float(input("请输入纬度（北纬为正，南纬为负）："))
    longitude = float(input("请输入经度（东经为正，西经为负）："))
    date_input = input("请输入日期（格式：YYYY-MM-DD）：")
    tz_str = input("请输入时区（例如 Asia/Shanghai, America/New_York）：")

    # 解析日期
    year, month, day = map(int, date_input.split('-'))
    start_date = datetime(year, month, day, tzinfo=pytz.utc)
    end_date = start_date.replace(hour=23, minute=59, second=59)

    # 创建观察者位置
    observer = earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    # 计算日出日落时间（UTC）
    ts = load.timescale()
    t0 = ts.utc(start_date)
    t1 = ts.utc(end_date)
    times, events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, observer))

    sunrise_utc = None
    sunset_utc = None
    for ti, event in zip(times, events):
        if event and sunrise_utc is None:  # 日出
            sunrise_utc = ti.utc_datetime()
        elif not event and sunset_utc is None:  # 日落
            sunset_utc = ti.utc_datetime()

    if sunrise_utc is None or sunset_utc is None:
        print("该日期在该地点没有日出或日落。")
        return

    # 转换为用户时区
    user_tz = pytz_timezone(tz_str)
    sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(user_tz)
    sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(user_tz)

    # 计算方位角
    def get_azimuth(time_utc):
        t = ts.utc(time_utc)
        astrometric = observer.at(t).observe(sun)
        alt, az, _ = astrometric.apparent().altaz()
        return az.degrees

    sunrise_azimuth = get_azimuth(sunrise_utc)
    sunset_azimuth = get_azimuth(sunset_utc)

    # 输出结果
    print("\n计算结果：")
    print(f"日出时间（本地）：{sunrise_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"日出方位角：{sunrise_azimuth:.2f}°")
    print(f"日落时间（本地）：{sunset_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"日落方位角：{sunset_azimuth:.2f}°")

if __name__ == "__main__":
    calculate_sun_times()