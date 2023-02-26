import time

def normalize_date(datestr: str, date_pattern: str="%Y-%m-%d", normalizing_pattern: str="%Y%m%d") -> str:
    """
    #### 可将网站给的时间日期格式转换成本项目采用的标准日期格式 "%Y%m%d"
    如把 ' 2022-07-17' 标准化成 '20220717'
    """
    return time.strftime(normalizing_pattern, time.strptime(datestr,date_pattern))

if __name__ == '__main__':
    print(normalize_date('2022-07-17'))