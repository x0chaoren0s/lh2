from lh.utils import singleton, get_tdx_api, tdx_disconnect
from lh.utils.tushare_df_fetcher import Tushare_df_fetcher
from lh.utils.tushare_df_processor import Tushare_df_processor
from lh.stockinfo.single_stock_daily import SingleStock_daily
from lh.time import Trade_time, normalize_date
import lh.stockinfo.data_fetcher as df
import tushare as ts
import pandas as pd
import requests

@singleton
class AllStock_daily:
    '''用于查询某日的全市所有股票的信息'''
    pro = ts.pro_api()
    # tf = Tushare_df_fetcher()
    tf = df
    tp = Tushare_df_processor()
    tt = Trade_time()
    ssd = SingleStock_daily()
    def __init__(self) -> None:
        # self.buffer_df = None
        pass

    def getTscodeList(self, trade_date) -> list:
        daily_df = self.getPrice(trade_date=trade_date)
        return daily_df['ts_code'].tolist()
    
    def getPrice(self, trade_date):
        '''返回当日所有股票数据的pandas表格'''
        # if self.buffer_df is None or not (self.buffer_df['trade_date']==trade_date).any():
        #     # 缓存数据中没有该部分数据
        #     # daily_df = self.pro.daily(trade_date=trade_date)
        #     daily_df = self.tf.daily(trade_date=trade_date)
        #     daily_df = daily_df[daily_df['trade_date']==trade_date]
        #     daily_df = daily_df[daily_df.ts_code.map(self.tf.is_listed)]
        #     self.buffer_df = pd.concat([self.buffer_df, daily_df], ignore_index=True)
        # return self.buffer_df[self.buffer_df['trade_date']==trade_date]
        daily_df = self.tf.daily(trade_date=trade_date)
        daily_df = daily_df[daily_df.ts_code.map(self.tf.is_listed)]
        return daily_df

    def getLimitUps(self, trade_date, ts_name=False, only_hs=False, sort=False) -> list:
        '''
        返回一个list: 包含当日所有收盘涨停的股票代码（若ts_name=True则返回的是对应股票名称，若only_hs=True则只返回沪深主板的票）
        
        sort: 是否将结果按照连扳个数从高到低排序
        '''
        daily_df = self.getPrice(trade_date=trade_date)
        daily_df = self.tp.isLimitUp(daily_df)
        if only_hs:
            daily_df = daily_df[
                (daily_df['ts_code'].str.startswith('60')) | (daily_df['ts_code'].str.startswith('00'))]
        ret = daily_df[daily_df['isLimitUp']]['ts_code'].tolist()
        if sort:
            # cmp = self.ssd.numLimitedUps()
            ret = sorted(ret, reverse=True, key=lambda tscode: self.ssd.numLimitedUps(ts_code=tscode, trade_date=trade_date))
        if ts_name:
            ret = [self.tf.stock_name(ts_code=ts_code) for ts_code in ret]
        return ret
    
    def get_least_2bans_list(self, trade_date, ts_name=False, only_hs=False, sort=False) -> list:
        '''
        返回当日至少二连板以上的股票(若only_hs=True则只返回沪深主板的票)
        
        ts_name: 是否返回股票名称
        sort: 是否将结果按照连扳个数从高到低排序
        '''
        trade_date = self.tt.toTradeDate(date=trade_date)
        pre_date = self.tt.preTradeDate(date=trade_date)
        pre_pool = set(self.getLimitUps(trade_date=pre_date, ts_name=False, only_hs=only_hs))
        now_pool = set(self.getLimitUps(trade_date=trade_date, ts_name=False, only_hs=only_hs))
        ret = list(now_pool & pre_pool)
        if sort:
            # cmp = self.ssd.numLimitedUps()
            ret = sorted(ret, reverse=True, key=lambda tscode: self.ssd.numLimitedUps(ts_code=tscode, trade_date=trade_date))
        if ts_name:
            ret = [self.tf.stock_name(ts_code) for ts_code in ret]
        return ret
    
    def get_only_k_bans_list(self, k, date, ts_name=False, only_hs=False) -> list:
        '''
        返回当日最近的已发生交易日刚好k连扳的股票
        
        ts_name: 是否返回股票名称
        only_hs: 是否仅查询沪深主板
        '''
        k = int(k)
        assert k>0
        trade_date = self.tt.toTradeDate(date=date)
        pre_date = self.tt.preTradeDate(date=trade_date)
        if k==1:
            pre_limitups = self.getLimitUps(trade_date=pre_date, ts_name=ts_name, only_hs=only_hs)
            now_limitups = self.getLimitUps(trade_date=trade_date, ts_name=ts_name, only_hs=only_hs)
            return list(set(now_limitups) - set(pre_limitups))
        return list(set(self.get_only_k_bans_list(k-1,pre_date,ts_name,only_hs)) & set(self.getLimitUps(trade_date,ts_name,only_hs)))
            
    def get_least_k_bans_list(self, k, date, ts_name=False, only_hs=False, sort=False) -> list:
        '''
        返回当日至少k连扳及以上的股票
        
        ts_name: 是否返回股票名称
        only_hs: 是否仅查询沪深主板
        sort: 是否将结果按照连扳个数从高到低排序
        '''
        k = int(k)
        assert k>0
        trade_date = self.tt.toTradeDate(date)
        ret = set(self.getLimitUps(trade_date=trade_date, ts_name=False, only_hs=only_hs))
        for _ in range(k-1):
            trade_date = self.tt.preTradeDate(trade_date)
            ret &= set(self.getLimitUps(trade_date=trade_date, ts_name=False, only_hs=only_hs))
            if len(ret)==0:
                break
        ret = list(ret)
        if sort:
            ret = sorted(ret, reverse=True, key=lambda tscode: self.ssd.numLimitedUps(ts_code=tscode, trade_date=trade_date))
        if ts_name:
            ret = [self.tf.stock_name(ts_code) for ts_code in ret]
        return ret

    def getNewlyListed(self, trade_date):
        '''返回一个list: 包含当日新上市的股票代码'''
        daily_df = self.getPrice(trade_date=trade_date)
        daily_df = daily_df[daily_df['pct_chg']>15]
        daily_df = self.tp.isNewlyListed(tushare_daily_df=daily_df, trade_date=trade_date)
        return daily_df[daily_df['isNewlyListed']]['ts_code'].tolist()