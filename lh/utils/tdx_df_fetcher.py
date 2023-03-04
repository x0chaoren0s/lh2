from pytdx.hq import TdxHq_API
from lh.time import Trade_time

class Tdx_df_fetcher:
    '''
    获取和缓存通达信的 DataFrame 数据

    本 api 内部维护一个自己的 TdxHq_API，且无须关注其连接和断连情况，不影响主程序正常退出
    '''
    tdx_ip = '119.147.212.81'
    tdx_port = 7709
    lazy_tdx_api = TdxHq_API() # 用的时候再连接，用完就断开，以保证不影响主程序正常退出
    tt = Trade_time()
    def __init__(self) -> None:
        self.tscode_To_tradedata_To_fenshi_df_buf = dict()

    def get_fenshi_df(self, ts_code, trade_date):
        '''
        #### 获取历史分时数据，即历史1分钟数据。
        #### trade_date会自动转换为最近的历史交易日。
        #### 返回一个dataframe，共240行（0-239，代表一个交易日的4个小时开盘时间），两列：[price, vol, trade_time]
             price     vol trade_time
        0     8.99  100909      09:30
        1     9.01   30707      09:31
        2     9.01   21514      09:32
        3     9.11   15498      09:33
        4     9.05   18678      09:34
        ..     ...     ...        ...
        235   9.95    7274      14:55
        236   9.95    8594      14:56
        237   9.96     290      14:57
        238   9.96       0      14:58
        239   9.96    8335      14:59
        '''
        if ts_code not in self.tscode_To_tradedata_To_fenshi_df_buf:
            self.tscode_To_tradedata_To_fenshi_df_buf[ts_code] = dict()
        
        if trade_date not in self.tscode_To_tradedata_To_fenshi_df_buf[ts_code]:
            tdx_market = 0 if ts_code[-2:]=='SZ' else 1
            tdx_code = ts_code[:-3]
            tdx_date = self.tt.toTradeDate(trade_date)
            with self.lazy_tdx_api.connect(self.tdx_ip, self.tdx_port):
                ret_df = self.lazy_tdx_api.to_df(self.lazy_tdx_api.get_history_minute_time_data(tdx_market, tdx_code, tdx_date))
            ret_df['trade_time'] = self.tt.trade_mins[:len(ret_df)]
            self.tscode_To_tradedata_To_fenshi_df_buf[ts_code][trade_date] = ret_df
            
        return self.tscode_To_tradedata_To_fenshi_df_buf[ts_code][trade_date]
