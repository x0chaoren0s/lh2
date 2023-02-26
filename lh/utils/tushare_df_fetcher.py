from lh.utils.singleton_ import singleton
from lh.time.trade_time import Trade_time
import tushare as ts
import pandas as pd

@singleton
class Tushare_df_fetcher:
    '''
    用于获取和缓存tushare表格
    '''
    pro = ts.pro_api()
    tt = Trade_time()
    def __init__(self) -> None:
        self.buf_start_date = '20191228'
        self.daily_df_buf = self.pro.daily(start_date=self.buf_start_date) # 一次能下载6000条数据，只能携带一天的所有数据
        self._dates_have_all_stk = set()

        self.stk_basic_df_buf = self.pro.stock_basic().set_index('ts_code').rename(columns={'name':'ts_name'})

    def daily(self, ts_code=None, trade_date=None, end_date=None):
        if end_date is None:
            end_date = self.tt.nowTradeDate()
        if ts_code is None and trade_date is not None:
            # if len(self.daily_df_buf[self.daily_df_buf['trade_date']==trade_date]) == 0:
            if trade_date not in self._dates_have_all_stk:
                daily_df = self.pro.daily(trade_date=trade_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
                self._dates_have_all_stk |= {trade_date}
            return self.daily_df_buf[
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None and trade_date is not None:
            if len(self.daily_df_buf[(self.daily_df_buf.ts_code==ts_code)&(self.daily_df_buf['trade_date']==trade_date)]) == 0:
                daily_df = self.pro.daily(trade_date=trade_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None:
            if len(self.daily_df_buf[(self.daily_df_buf.ts_code==ts_code)&(self.daily_df_buf['trade_date']<=trade_date)]) <= 1:
                daily_df = self.pro.daily(ts_code=ts_code, end_date=end_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']<=end_date)
            ]

    def stock_basic(self, ts_code=None):
        assert ts_code in self.stk_basic_df_buf.index
        return self.stk_basic_df_buf.loc[ts_code]
    
    def stock_name(self, ts_code=None):
        return self.stock_basic(ts_code=ts_code)['ts_name']