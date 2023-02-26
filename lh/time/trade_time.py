import tushare as ts
from lh.utils.singleton_ import singleton
import time

@singleton
class Trade_time:
    '''
    查询交易时间的工具箱
    假定SSE上交所和SZSE深交所的交易日历相同，只查询SSE。
    '''
    def __init__(self) -> None:
        self.pro = ts.pro_api()
        self.trade_cal = self.pro.trade_cal(exchange='SSE', start_date='20190101')
        self.trade_cal = self.trade_cal[self.trade_cal['cal_date']>='20190101']
        self.trade_cal = self.trade_cal.reset_index(drop=True)
        self.trade_mins = set() # 即开盘时间4小时共240分钟，从09:30到14：59
        self.trade_mins |= {f'{hh:02d}:{mm:02d}' for hh in range(9,10) for mm in range(30,60)}
        self.trade_mins |= {f'{hh:02d}:{mm:02d}' for hh in range(10,11) for mm in range(0,60)}
        self.trade_mins |= {f'{hh:02d}:{mm:02d}' for hh in range(11,12) for mm in range(0,30)}
        self.trade_mins |= {f'{hh:02d}:{mm:02d}' for hh in range(13,15) for mm in range(0,60)}
        self.trade_mins = sorted(self.trade_mins) # 是一个list

    def toTradeDate(self, date='20221016'):
        '''
        将形参date(YYYYMMDD)转换为交易日(YYYYMMDD)。
        如果本来就是交易日那就返回当天，否则就返回距离最近的上一个交易日。
        '''
        return date if self.trade_cal[self.trade_cal['cal_date']==date]['is_open'].tolist()[0] \
                else self.trade_cal[self.trade_cal['cal_date']==date]['pretrade_date'].tolist()[0]
        
    def preTradeDate(self, date='20221016'):
        '''
        返回交易日date（若date不是交易日，则会将其自动转化为最近的上一个交易日）的上一个交易日。
        '''
        return self.trade_cal[self.trade_cal['cal_date']==self.toTradeDate(date)]['pretrade_date'].tolist()[0]

    def nextTradeDate(self, date='20221016'):
        '''
        返回date的下一个交易日。
        '''
        return self.trade_cal[
                (self.trade_cal['pretrade_date']==self.toTradeDate(date)) &
                (self.trade_cal['is_open'])
            ]['cal_date'].tolist()[0]
    
    def nowTradeDate(self):
        '''
        如果今天本来就是交易日那就返回今天，否则返回最近的上一个交易日
        '''
        return self.toTradeDate(date=time.strftime("%Y%m%d", time.localtime()))
    