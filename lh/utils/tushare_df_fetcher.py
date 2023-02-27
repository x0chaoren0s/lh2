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
        # ts_code	    str	    股票代码
        # trade_date	str	    交易日期
        # open	        float	开盘价
        # high	        float	最高价
        # low	        float	最低价
        # close	        float	收盘价
        # pre_close	    float	昨收价(前复权)
        # change	    float	涨跌额
        # pct_chg	    float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
        # vol	        float	成交量 （手）
        # amount	    float	成交额 （千元）
        self._dates_have_all_stk = set()

        self.stk_basic_df_buf = self.pro.stock_basic(
            fields='ts_code,name,industry,list_date,is_hs'
            ).set_index('ts_code').rename(columns={'name':'ts_name'})
        '''
        ts_code	    str	Y	TS代码
        symbol	    str	Y	股票代码
        name	    str	Y	股票名称
        area	    str	Y	地域
        industry	str	Y	所属行业
        fullname	str	N	股票全称
        enname	    str	N	英文全称
        cnspell	    str	N	拼音缩写
        market	    str	Y	市场类型（主板/创业板/科创板/CDR）
        exchange	str	N	交易所代码
        curr_type	str	N	交易货币
        list_status	str	N	上市状态 L上市 D退市 P暂停上市
        list_date	str	Y	上市日期
        delist_date	str	N	退市日期
        is_hs	    str	N	是否沪深港通标的，N否 H沪股通 S深股通
        '''

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
    
    def stock_name(self, ts_code=None) -> str:
        return self.stock_basic(ts_code=ts_code)['ts_name']