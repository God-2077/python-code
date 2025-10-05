from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
import sys

# 获取当前带时区的时间
now_with_tz = datetime.now().astimezone()
current_timezone = now_with_tz.tzinfo

print("当前时区对象：", current_timezone)

# 兼容两种时区对象的名称获取方式
if "zoneinfo" in sys.modules and isinstance(current_timezone, ZoneInfo):
    # 对于zoneinfo的时区对象，使用key属性
    print("当前时区名称：", current_timezone.key)
else:
    # 对于普通timezone对象，使用tzname()方法
    print("当前时区名称：", current_timezone.tzname(now_with_tz))