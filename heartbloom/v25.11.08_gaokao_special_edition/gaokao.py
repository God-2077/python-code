from datetime import datetime, date

def gaokao_countdown(target_year=None):
    """
    计算高考倒计时
    高考日期：每年的6月7日

    返回:
        字典，包含倒计时天数、高考日期和目标年份

    example:
        {'days_left': 100, 'gaokao_date': datetime.date(2025, 6, 7), 'target_year': 2025}
    """
    # 获取当前日期
    today = date.today()  # 使用真实日期
    current_year = today.year
    
    # 如果未指定目标年份，自动判断
    if target_year is None:
        # 如果当前日期在6月7日之后，计算下一年的高考
        if today > date(current_year, 6, 7):
            target_year = current_year + 1
        else:
            target_year = current_year
    
    # 设置高考日期
    gaokao_date = date(target_year, 6, 7)
    
    # 计算日期差
    days_left = (gaokao_date - today).days
    
    return {'days_left': days_left, 'gaokao_date': gaokao_date, 'target_year': target_year}

def get_gaokao_info():
    """获取高考倒计时详细信息，返回字典"""
    info = gaokao_countdown()
    days_left = info['days_left']
    gaokao_date = info['gaokao_date']
    target_year = info['target_year']

    today = date.today()
    current_year = today.year

    # 修正状态判断逻辑
    if today < date(current_year, 6, 7):
        # 高考前
        # status = f"距离{current_year}年高考还有 {days_left} 天"
        status = f"距离高考还有 {days_left} 天"
    elif date(current_year, 6, 7) <= today <= date(current_year, 6, 9):
        # 高考期间（6月7日-6月9日）
        status = "今天是高考日！高考加油！"
    else:
        # 高考后（6月9日之后）
        # 检查是否已经进入下一年度的高考准备周期
        if today >= date(current_year, 9, 1):
            # 9月1日之后，已经是下一届高考
            # status = f"距离{target_year}年高考还有 {days_left} 天"
            status = f"距离高考还有 {days_left} 天"
        else:
            # 6月9日到9月1日之间的假期
            status = "高考已结束，去享受高考后的假期吧！"
    
    return {
        'days_left': days_left,
        'gaokao_date': gaokao_date.strftime('%Y-%m-%d'),
        'target_year': target_year,
        'status': status,
        'current_date': today.strftime('%Y-%m-%d')
    }

if __name__ == '__main__':
    print(gaokao_countdown())
    print(get_gaokao_info())