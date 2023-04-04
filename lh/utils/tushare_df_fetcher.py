from lh.utils.singleton_ import singleton
from lh.time.trade_time import Trade_time
import tushare as ts
import pandas as pd
import os, json, logging

@singleton
class Tushare_df_fetcher:
    '''
    用于获取和缓存tushare表格
    '''
    pro = ts.pro_api()
    tt = Trade_time()
    buf_folder = 'buffer/tushare'
    def __init__(self) -> None:
        self.buf_start_date = '20191228'
        self.daily_df_buf = pd.DataFrame(columns=[
            'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
            'change', 'pct_chg', 'vol', 'amount'
        ])
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
        self._dates_have_all_stk = []

        # self.stk_basic_df_buf = self.pro.stock_basic(
        #     fields='ts_code,name,industry,list_date,is_hs'
        #     ).set_index('ts_code').rename(columns={'name':'ts_name'})
        self.stk_basic_df_buf = pd.DataFrame(columns=[
            'ts_name', 'industry', 'list_date', 'is_hs'
        ])
        '''
        ts_code	    str	Y	TS代码    ->  index
        symbol	    str	Y	股票代码
        name	    str	Y	股票名称  ->  ts_name
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

        self.buf_to_save = {
            'daily_df_buf': self.daily_df_buf,
            '_dates_have_all_stk': self._dates_have_all_stk,
            'stk_basic_df_buf': self.stk_basic_df_buf
        }
        self.load_or_init_bufs()

    def daily(self, ts_code=None, trade_date=None, end_date=None) -> pd.DataFrame:
        if end_date is None:
            end_date = self.tt.nowTradeDate()
        if ts_code is None and trade_date is not None:
            # if len(self.daily_df_buf[self.daily_df_buf['trade_date']==trade_date]) == 0:
            if trade_date not in self._dates_have_all_stk:
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  parsing from web...')
                daily_df = self.pro.daily(trade_date=trade_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
                self._dates_have_all_stk = list(set(self._dates_have_all_stk)|{trade_date})
            else:
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  using saved buffer.')
            return self.daily_df_buf[
                (self.daily_df_buf['trade_date']==trade_date)
            ].reset_index(drop=True)
        if ts_code is not None and trade_date is not None:
            if len(self.daily_df_buf[(self.daily_df_buf.ts_code==ts_code)&(self.daily_df_buf['trade_date']==trade_date)]) == 0:
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  parsing from web...')
                daily_df = self.pro.daily(trade_date=trade_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            else:
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  using saved buffer.')
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']==trade_date)
            ].reset_index(drop=True)
        if ts_code is not None:
            # pre_date = self.tt.preTradeDate(date=trade_date)
            # t1 = len(self.daily_df_buf[self.daily_df_buf.trade_date==trade_date])>0
            # t2 = len(self.daily_df_buf[self.daily_df_buf.trade_date==pre_date])>0
            if len(self.daily_df_buf[(self.daily_df_buf.ts_code==ts_code)&(self.daily_df_buf.trade_date<=end_date)]) <= 1:
            # if len(self.daily_df_buf[(self.daily_df_buf.ts_code==ts_code)&(self.daily_df_buf['trade_date']<=trade_date)]) <= 1:
            # if not (t1 and t2):
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  parsing from web...')
                daily_df = self.pro.daily(ts_code=ts_code, end_date=end_date)
                self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            else:
                logging.debug(f'[Tushare_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  using saved buffer.')
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']<=end_date)
            ].reset_index(drop=True)

    def stock_basic(self, ts_code=None) -> pd.DataFrame:
        # assert ts_code in self.stk_basic_df_buf.index
        if ts_code not in self.stk_basic_df_buf.index:
            'debug'
        return self.stk_basic_df_buf.loc[ts_code]
    
    def stock_name(self, ts_code=None) -> str:
        return self.stock_basic(ts_code=ts_code)['ts_name']
    
    def list_date(self, ts_code) -> str:
        return self.stock_basic(ts_code=ts_code)['list_date']
        
    def is_st(self, ts_code) -> bool:
        return 'ST' in self.stock_name(ts_code=ts_code)
    
    def is_listed(self, ts_code) -> bool:
        '''返回该股票当前是否处于上市状态'''
        return ts_code in self.stk_basic_df_buf.index
    
    
    def save_buf(self) -> None:
        '''保存缓存的buf数据'''
        self.buf_to_save = {
            'daily_df_buf': self.daily_df_buf,
            '_dates_have_all_stk': self._dates_have_all_stk,
            'stk_basic_df_buf': self.stk_basic_df_buf
        } # 重写一遍防止之前引用的数据是旧数据，其真实数据已经是新的对象
        for buf_name, buf_obj in self.buf_to_save.items():
            with open(os.path.join(self.buf_folder, buf_name+'.json'), 'w') as fout:
                if isinstance(buf_obj, (dict, list)):
                    json.dump(buf_obj, fout, indent=4)
                elif isinstance(buf_obj, pd.DataFrame):
                    buf_obj.to_json(fout, indent=4)

    def load_or_init_bufs(self) -> None:
        '''若存在，则载入已保存的buf数据，否则对其初始化'''
        path = os.path.join(self.buf_folder, 'daily_df_buf.json')
        if os.path.exists(path):
            self.daily_df_buf = pd.read_json(path, dtype={'trade_date': str})

        path = os.path.join(self.buf_folder, '_dates_have_all_stk.json')
        if os.path.exists(path):
            with open(path, 'r') as fin:
                self._dates_have_all_stk = json.load(fin)

        path = os.path.join(self.buf_folder, 'stk_basic_df_buf.json')
        if os.path.exists(path):
            self.stk_basic_df_buf = pd.read_json(path, dtype={'list_date': str})
        else:
            self.stk_basic_df_buf = self.pro.stock_basic(
                    fields='ts_code,name,industry,list_date,is_hs'
                ).set_index('ts_code').rename(columns={'name':'ts_name'})

        
