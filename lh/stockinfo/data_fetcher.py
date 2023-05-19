import sys
sys.path.append(r'D:\Users\60490\lh2')

from lh.time.trade_time import Trade_time
tt = Trade_time()

from lh.time.normalize_date import normalize_date
from lh.utils.tdx_api import get_tdx_api, tdx_disconnect
from lh.utils.time_it import time_it

from pytdx.hq import TdxHq_API, TDXParams
# TDX_API = TdxHq_API()
TDX_API = get_tdx_api()
# TDX_IP, TDX_PORT = '119.147.212.81', 7709

import tushare as ts
pro = ts.pro_api()

import pandas as pd
from typing import Tuple
from tqdm import tqdm
import requests, os, json


def get_fenbi_data(ts_code, trade_date) -> Tuple[bool, pd.DataFrame]:
    '''
    获取单股单日分笔数据
    '''
    code = ts_code[:6]
    market = 1 if code[0]=='6' else 0
    trade_date = int(trade_date)
    ii = 0
    # with TDX_API.connect(TDX_IP, TDX_PORT):
    ret = TDX_API.to_df(TDX_API.get_history_transaction_data(market, code, ii, 2000, trade_date))
    # print(ret)
    has_data = not (len(ret)==0 or len(ret)==1 and ret.value.iloc[0] is None)
    while has_data and ret.time.iloc[0] != '09:25':
        ret = pd.concat([TDX_API.to_df(TDX_API.get_history_transaction_data(market, code, ii, 2000, trade_date)), ret], ignore_index=True)
        ii += 2000
    return has_data, ret

# 此段不要变，用于设置满240个分钟
TRADE_TIME = get_fenbi_data('002380.SH','20230324')[1].time.unique()

def get_minute_k_data(ts_code, trade_date, fenbi=None) -> Tuple[bool, pd.DataFrame]:
    '''
    固定240条数据，但首尾不连续：

    09:25, 09:30, 09:31, ..., 11:29, 13:00, ..., 14:57, 15:00

    不一定240个分钟内都有成交，默认至少09:25一定会有开盘成交，后面没有成交的分钟里补价格同前收盘价，成交量为0

    若传入fenbi，需保证实参fenbi存在
    '''
    if fenbi is None:
        has_data, fenbi = get_fenbi_data(ts_code, trade_date)
        if not has_data:
            return has_data, fenbi
    else:
        has_data, fenbi = True, fenbi.copy()
    ret = fenbi.groupby('time').sum()[['vol']]
    ret['open'] = fenbi.groupby('time').first().price
    ret['close'] = fenbi.groupby('time').last().price
    ret['low'] = fenbi.groupby('time').price.min()
    ret['high'] = fenbi.groupby('time').price.max()
    for i,trade_time in enumerate(TRADE_TIME):
        if trade_time not in ret.index:
            fill_data = ret.loc[TRADE_TIME[i-1]].copy()
            fill_data.vol = 0
            fill_data.open = fill_data.low = fill_data.high = fill_data.close
            ret.loc[trade_time] = fill_data
    ret.sort_index(inplace=True)
    return has_data, ret

def get_day_k_data_single_day(ts_code, trade_date, minute_k=None) -> Tuple[bool, pd.DataFrame]:
    '''
    若传入minute_k，需保证实参minute_k存在
    '''
    if minute_k is None:
        has_data, minute_k = get_minute_k_data(ts_code, trade_date)
        if not has_data:
            return has_data, minute_k
    else:
        has_data, minute_k = True, minute_k.copy()
    ret = minute_k.iloc[0]
    ret.close = minute_k.iloc[-1].close
    ret.low = minute_k.low.min()
    ret.high = minute_k.high.max()
    ret.vol = minute_k.vol.sum()
    return has_data, ret

def get_fenbi_minuteK_dayK_single_day(ts_code, trade_date) -> Tuple[bool, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    has_data, fenbi = get_fenbi_data(ts_code, trade_date)
    if not has_data:
        return has_data, fenbi, fenbi.copy(), fenbi.copy()
    has_data = True
    minute_k = get_minute_k_data(ts_code, trade_date, fenbi)[1]
    day_k = get_day_k_data_single_day(ts_code, trade_date, minute_k)[1]
    return has_data, fenbi, minute_k, day_k

# 替换 Tdx_df_fetcher
def get_fenshi_df(ts_code, trade_date, try_times=1, max_try_times=20) -> pd.DataFrame:
    '''
    #### 获取历史分时数据，即历史1分钟数据。
    #### trade_date会自动转换为最近的历史交易日。
    #### 返回一个dataframe，共240行（0-239，代表一个交易日的4个小时开盘时间），五列：[ts_code, trade_date, trade_time, price, vol]
                ts_code trade_date trade_time  price     vol
        0    603528.SH   20230227      09:30   8.99  100909
        1    603528.SH   20230227      09:31   9.01   30707
        2    603528.SH   20230227      09:32   9.01   21514
        3    603528.SH   20230227      09:33   9.11   15498
        4    603528.SH   20230227      09:34   9.05   18678
        ..         ...        ...        ...    ...     ...
        235  603528.SH   20230227      14:55   9.95    7274
        236  603528.SH   20230227      14:56   9.95    8594
        237  603528.SH   20230227      14:57   9.96     290
        238  603528.SH   20230227      14:58   9.96       0
        239  603528.SH   20230227      14:59   9.96    8335
    '''
    tdx_market = 0 if ts_code[-2:] in ['SZ'] else 1 if ts_code[-2:] in ['SH'] else 2
    tdx_code = ts_code[:-3]
    tdx_date = trade_date
    # with TDX_API.connect(TDX_IP, TDX_PORT):
    fenshi_df = TDX_API.to_df(TDX_API.get_history_minute_time_data(tdx_market, tdx_code, tdx_date))
    while len(fenshi_df)==0:
        # fenshi_df = get_fenshi_df(ts_code, tt.preTradeDate(trade_date))
        tdx_date = tt.preTradeDate(tdx_date)
        fenshi_df = TDX_API.to_df(TDX_API.get_history_minute_time_data(tdx_market, tdx_code, tdx_date))
    if 'ts_code' not in fenshi_df.columns or 'price' not in fenshi_df.columns:
        fenshi_df['ts_code'] = ts_code
        fenshi_df['trade_date'] = trade_date
        try:
            fenshi_df['trade_time'] = TRADE_TIME
        except:
            if try_times<=max_try_times:
                return get_fenshi_df(ts_code, trade_date, try_times+1, max_try_times)
            else:
                raise Exception(f'[get_fenshi_df] {ts_code}, {trade_date}')
    else:
        fenshi_df['trade_date'] = trade_date
        fenshi_df.vol = 0
        fenshi_df.price = fenshi_df.price.iloc[-1]
    return fenshi_df[['ts_code','trade_date','trade_time','price','vol']]
def get_fenshi_df_k_days(ts_code, trade_date_end, k) -> pd.DataFrame:
    '''
    返回包括 trade_date_end 在内的往前最多 k 个连续交易日的某股票分时数据。
    共 240*k 行：
                    ts_code trade_date trade_time  price     vol
        0    603528.SH   20230227      09:30   8.99  100909
        1    603528.SH   20230227      09:31   9.01   30707
    '''
    ret = []
    for trade_date in tt.getTradeDateList(None, trade_date_end, k):
        if trade_date<list_date(ts_code):
            continue
        ret.append(get_fenshi_df(ts_code, trade_date))
    return pd.concat(ret)


# 替换 Dongcai_df_fetcher
def daily(ts_code=None, trade_date=None, end_date=None, try_times=1, max_try_times=3) -> pd.DataFrame:
    '''
    获取日k线，若没有数据则返回空表
    
    共3种调用情况:
    ||ts_code|trade_date|end_date|
    | -- | -- | -- | -- |
    |某股某天|str|str|None|
    |某股某天及之前|str|None|str or None|
    |某天所有股|None|str|None|
    '''
    if ts_code is not None:
        secid = '0.'+ts_code[:-3] if ts_code[-2:] in ['SZ','BJ'] else '1.'+ts_code[:-3]
        buf_file = f'daily_{tt.nowTradeDate()}_{secid}.json'
        buf_folder = r'D:\Users\60490\lh2\buffer\dongcai'
        if buf_file not in os.listdir(buf_folder):
            candles_day_url_template = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?' \
                'fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61' \
                '&beg=0&end=20500101&rtntype=6&secid=SECID&klt=101&fqt=1' # 替换SECID
            candles_url = candles_day_url_template.replace('SECID', secid)
            res = requests.get(candles_url)
            if res.status_code != 200:
                assert try_times<=max_try_times, '超过尝试次数，请检查网络连接'
                return daily(ts_code=ts_code, trade_date=trade_date, end_date=end_date, try_times=try_times+1, max_try_times=max_try_times)
            res_dict = res.json()
            with open(os.path.join(buf_folder,buf_file), 'w') as fout:
                json.dump(res_dict, fout)
        else:
            with open(os.path.join(buf_folder,buf_file), 'r') as fin:
                res_dict = json.load(fin)
        candles = res_dict['data']['klines']
        # ['2023-02-23,9.05,9.05,9.05,9.05,100485,90938473.00,0.00,9.96,0.82,1.61',..]
        col_names = ['trade_date', 'open', 'close', 'high', 'low',
                        'vol', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
        cols = [[] for _ in range(11)]
        for candle in candles:
            for i,item in enumerate(candle.split(',')):
                if i==0:
                    item = normalize_date(item)
                else:
                    item = float(item)
                cols[i].append(item)
        cols = {name: col for name,col in zip(col_names,cols)}
        daily_df = pd.DataFrame(cols)
        daily_df['ts_code'] = ts_code
        daily_df['ts_name'] = res_dict['data']['name']
        daily_df['pre_close'] = [0, *(daily_df.close.tolist()[:-1])]
        if trade_date is not None:      # |某股某天|str|str|None|
            if trade_date<list_date(ts_code):
                return pd.DataFrame(columns=[
                    'trade_date', 'open', 'close', 'high', 'low', 'vol', 'amount', 'amplitude',
                    'pct_chg', 'change', 'turnover', 'ts_code', 'ts_name', 'pre_close'
                ])
            if (trade_date == daily_df.trade_date).any():  # 当日正常交易
                return daily_df[daily_df['trade_date']==trade_date]
            else:                           # 当日停牌没有数据
                try:
                    ret = daily_df[daily_df['trade_date']<trade_date].iloc[-1].copy()  # 此时是series
                except:
                    print(f'[daily] {ts_code}, {trade_date}, {end_date}')
                    exit(1)
                ret.trade_date = trade_date
                ret.open = ret.high = ret.low = ret.pre_close = ret.close
                ret.vol = ret.amount = ret.amplitude = ret.pct_chg = ret.change = ret.turnover = 0
                return ret.to_frame().T
        return daily_df[                # |某股某天及之前|str|None|str or None|
            daily_df['trade_date']<=(end_date if end_date is not None else tt.nowTradeDate())
        ]
    # |某天所有股|None|str|None|
    return pro.daily(trade_date=trade_date)
    
TSCODE_TO_TAGS = dict()
TAGS_TO_IGNORE = {
    '百元股','标准普尔','昨日涨停','股权激励','转债标的','富时罗素','沪股通','深股通','融资融券',
    '上证380',
    '预亏预减','预盈预增', 'QFII重仓','机构重仓','昨日涨停_含一字',
    '内蒙古','上海板块','福建板块','北京板块','广西板块', '京津冀','新疆板块','吉林板块','长江三角',
        '深圳特区',  '贵州板块','浙江板块','广东板块','江苏板块','山东板块','河南板块', 
}
def get_tags(ts_code) -> set:
    '''
    从东财网页获取该股票的题材板块。
    爬虫参考 https://www.jianshu.com/p/883c74f939ee
    动态加载内容爬取参考 https://blog.csdn.net/sinat_38682860/article/details/105798818

    返回一个包含所有题材板块名称的集合，如
    {'昨日涨停_含一字', '广东板块', '国产芯片', '无线耳机', '植物照明', '电子元件', '参股新三板', '5G概念', 
    '昨日连板_含一字', '国家安防', '深圳特区', '字节概念', '新能源车', 
    '网红直播', '智能穿戴', '独角兽', '物联网', '区块链', '华为概念'}
    '''
    global TSCODE_TO_TAGS
    TSCODE_TO_TAGS_buf_file = f'TSCODE_TO_TAGS.json'
    buf_folder = r'D:\Users\60490\lh2\buffer\dongcai'
    buf_file = os.path.join(buf_folder,TSCODE_TO_TAGS_buf_file)
    if len(TSCODE_TO_TAGS)==0 and os.path.exists(buf_file):
        with open(buf_file, 'r') as fin:
            TSCODE_TO_TAGS = {k:set(l) for k,l in json.load(fin).items()}
    if ts_code not in TSCODE_TO_TAGS:
        # 浏览器网页 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=web&code=SZ002137#
        # f12搜索 所属板块 和 经营范围 得动态加载接口 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137
        # url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137'
        url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={ts_code[-2:]+ts_code[:-3]}'
        res = requests.get(url = url)
        while res.status_code!=200:
            res = requests.get(url = url)
        try:
            resjson = res.json()
        except:
            assert False, f'[get_tags] {ts_code} {url}'
        tags = {bk['BOARD_NAME'] for bk in resjson['ssbk']}
        # TSCODE_TO_TAGS[ts_code] = tags
        TSCODE_TO_TAGS[ts_code] = tags-TAGS_TO_IGNORE
        with open(buf_file, 'w') as fout:
            json.dump({k:list(s) for k,s in TSCODE_TO_TAGS.items()}, fout)
    return TSCODE_TO_TAGS[ts_code]
def get_name(ts_code) -> str:
    '''返回股票名称'''
    return stock_name(ts_code)
def get_pre_close(ts_code, trade_date) -> float:
    try:
        return float(daily(ts_code, trade_date).pre_close.iloc[0])
    except:
        return 0.0
def get_high(ts_code, trade_date) -> float:
    return float(daily(ts_code, trade_date).high.iloc[0])
def get_open(ts_code, trade_date) -> float:
    return float(daily(ts_code, trade_date).open.iloc[0])

# 替换 Tushare_df_fetcher
# daily 见上

STK_BASIC_DF = pro.stock_basic(
        fields='ts_code,name,industry,list_date'
    ).set_index('ts_code').rename(columns={'name':'ts_name'})
def stock_basic(ts_code) -> pd.DataFrame:
    # assert ts_code in self.STK_BASIC_DF.index
    return STK_BASIC_DF.loc[ts_code]
def stock_name(ts_code) -> str:
    return stock_basic(ts_code=ts_code)['ts_name']
def list_date(ts_code) -> str:
    return stock_basic(ts_code=ts_code)['list_date']
def is_st(ts_code) -> bool:
    return 'ST' in stock_name(ts_code=ts_code)
def is_listed(ts_code) -> bool:
    '''返回该股票当前是否处于上市状态'''
    return ts_code in STK_BASIC_DF.index

@time_it
def check_time1(n=100):
    for _ in tqdm(range(n)):
        get_fenshi_df('603528.SH', '20230227')        
@time_it
def check_time2(n=100):
    for _ in tqdm(range(n)):
        daily('603528.SH')
@time_it
def check_time3(n=100):
    for _ in tqdm(range(n)):
        daily('603528.SH')

if __name__ == '__main__':
    # print(get_fenshi_df1('603528.SH', '20230227'))
    # print(get_fenshi_df2('603528.SH', '20230227'))
    # check_time1()
    # check_time2()
    # check_time3()
    # print(TDX_API.to_df(TDX_API.get_history_minute_time_data(1,'603528',20230227)))
    # print(daily('603528.SH'))
    # print(get_tags('603528.SH'))
    # print(get_tags('600785.SH'))
    # print(get_name('603528.SH'))
    # print(stock_name('603528.SH'))
    # print(daily('001368.SZ','20230310'))
    # print(daily('603528.SH',end_date='20230327'))
    # print(daily(trade_date='20230327'))
    # print(set(daily(trade_date='20230327').ts_code.tolist()))
    # print(daily('002761.SZ', '20220222'))
    # print(daily('000587.SZ', '20230202'))
    # print(daily('000587.SZ', '20230203'))
    # print(type(daily('000587.SZ', '20230203')))
    # print(daily('000587.SZ', '20230203').to_frame())
    # print(type(daily('000587.SZ', '20230203').to_frame()))
    # print(daily('000587.SZ', '20230203').to_frame().T)
    # print(type(daily('000587.SZ', '20230203').to_frame().T))
    # print(get_fenshi_df('601059.SH', '20230208'))
    # print(get_fenshi_df('000892.SZ', '20220901'))
    # print(get_fenshi_df('002877.SZ', '20230209'))
    print(get_fenshi_df('600629.SH', '20230510'))
    # print(stock_basic('600260.SH'))

    tdx_disconnect(api=TDX_API)