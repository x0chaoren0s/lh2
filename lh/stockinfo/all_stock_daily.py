from lh.utils import singleton, get_tdx_api, tdx_disconnect
from lh.utils.tushare_df_fetcher import Tushare_df_fetcher
from lh.utils.tushare_df_processor import Tushare_df_processor
from lh.time import Trade_time, normalize_date
import tushare as ts
import pandas as pd
import requests

@singleton
class AllStock_daily:
    '''用于查询某日的全市所有股票的信息'''
    pro = ts.pro_api()
    tf = Tushare_df_fetcher()
    tp = Tushare_df_processor()
    tt = Trade_time()
    def __init__(self) -> None:
        self.buffer_df = None

    def getTscodeList(self, trade_date) -> list:
        daily_df = self.getPrice(trade_date=trade_date)
        return daily_df['ts_code'].tolist()
    
    def getPrice(self, trade_date):
        '''返回当日所有股票数据的pandas表格'''
        if self.buffer_df is None or not (self.buffer_df['trade_date']==trade_date).any():
            # 缓存数据中没有该部分数据
            # daily_df = self.pro.daily(trade_date=trade_date)
            daily_df = self.tf.daily(trade_date=trade_date)
            daily_df = daily_df[daily_df['trade_date']==trade_date]
            self.buffer_df = pd.concat([self.buffer_df, daily_df], ignore_index=True)
        return self.buffer_df[self.buffer_df['trade_date']==trade_date]

    def getLimitUps(self, trade_date, ts_name=False, only_hs=False) -> list:
        '''返回一个list: 包含当日所有收盘涨停的股票代码（若ts_name=True则返回的是对应股票名称，若only_hs=True则只返回沪深主板的票）'''
        daily_df = self.getPrice(trade_date=trade_date)
        daily_df = self.tp.isLimitUp(daily_df)
        if only_hs:
            daily_df = daily_df[
                (daily_df['ts_code'].str.startswith('60')) | (daily_df['ts_code'].str.startswith('00'))]
        ret = daily_df[daily_df['isLimitUp']]['ts_code'].tolist()
        if ts_name:
            ret = [self.tf.stock_name(ts_code=ts_code) for ts_code in ret]
        return ret
    
    def get_least_2bans_list(self, trade_date, only_hs=False) -> list:
        '''返回当日至少二连板以上的股票(若only_hs=True则只返回沪深主板的票)'''
        trade_date = self.tt.toTradeDate(date=trade_date)
        pre_date = self.tt.preTradeDate(date=trade_date)
        pre_pool = set(self.getLimitUps(trade_date=pre_date, only_hs=only_hs))
        now_pool = set(self.getLimitUps(trade_date=trade_date, only_hs=only_hs))
        return list(now_pool & pre_pool)

    def getNewlyListed(self, trade_date):
        '''返回一个list: 包含当日新上市的股票代码'''
        daily_df = self.getPrice(trade_date=trade_date)
        daily_df = daily_df[daily_df['pct_chg']>15]
        daily_df = self.tp.isNewlyListed(tushare_daily_df=daily_df, trade_date=trade_date)
        return daily_df[daily_df['isNewlyListed']]['ts_code'].tolist()