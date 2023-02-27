from lh.utils.singleton_ import singleton
from lh.time.trade_time import Trade_time
from lh.time import normalize_date
import tushare as ts
import pandas as pd
import requests

@singleton
class Dongcai_df_fetcher:
    '''
    用于获取和缓存东方财富api拿到的json并转换成的DataFrame

    使用tushare的ts_code即可，内部自动转化为东财的secid
    '''
    # pro = ts.pro_api()
    tt = Trade_time()
    candles_day_url_template = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?' \
        'fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61' \
        '&beg=0&end=20500101&rtntype=6&secid=SECID&klt=101&fqt=1' # 替换SECID
    def __init__(self) -> None:
        self.daily_df_buf = pd.DataFrame(columns=[
            'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'change', 
            'pct_chg', 'vol', 'amount', 'amplitude', 'turnover'
        ])
        # ts_code	    str	    股票代码
        # trade_date	str	    交易日期
        # open	        float	开盘价
        # high	        float	最高价
        # low	        float	最低价
        # close	        float	收盘价
        # change	    float	涨跌额
        # pct_chg	    float	涨跌幅
        # vol	        float	成交量
        # amount	    float	成交额
        # amplitude     float   振幅
        # turnover      float   换手率

    @staticmethod
    def to_secid(ts_code) -> str:
        '''将tushare的ts_code(如000638.SZ)转换成东方财富的secid(如0.000638)'''
        return '0.'+ts_code[:-3] if ts_code[-2:]=='SZ' else '1.'+ts_code[:-3]

    @staticmethod
    def to_trade_date(dc_date) -> str:
        '''将东方财富的日期(如2016-05-04)转换成tushare的trade_date(如20160504)'''
        return normalize_date(datestr=dc_date)

    def daily(self, ts_code, trade_date=None, end_date=None, try_times=1, max_try_times=3) -> dict:
        '''获取日k线'''
        if end_date is None:
            end_date = self.tt.nowTradeDate()
        if ts_code not in self.daily_df_buf.ts_code:
            secid = self.to_secid(ts_code=ts_code)
            candles_url = self.candles_day_url_template.replace('SECID', secid)
            res = requests.get(candles_url)
            if res.status_code != 200:
                assert try_times<=max_try_times, '超过尝试次数，请检查网络连接'
                return self.getCandles(ts_code=ts_code, try_times=try_times+1, max_try_times=max_try_times)
            candles = res.json()['data']['klines']
            # ['2023-02-23,9.05,9.05,9.05,9.05,100485,90938473.00,0.00,9.96,0.82,1.61',..]
            col_names = ['trade_date', 'open', 'close', 'high', 'low',
                         'vol', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            cols = [[] for _ in range(11)]
            for candle in candles:
                for i,item in enumerate(candle.split(',')):
                    if i==0:
                        item = self.to_trade_date(item)
                    else:
                        item = float(item)
                    cols[i].append(item)
            cols = {name: col for name,col in zip(col_names,cols)}
            daily_df = pd.DataFrame(cols)
            daily_df['ts_code'] = ts_code
            self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        if ts_code is None and trade_date is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None and trade_date is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']<=end_date)
            ]
