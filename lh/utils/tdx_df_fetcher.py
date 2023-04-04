from pytdx.hq import TdxHq_API
from lh.time import Trade_time
import pandas as pd
import os, json

class Tdx_df_fetcher:
    '''
    获取和缓存通达信的 DataFrame 数据

    本 api 内部维护一个自己的 TdxHq_API，且无须关注其连接和断连情况，不影响主程序正常退出
    '''
    tdx_ip = '119.147.212.81'
    tdx_port = 7709
    lazy_tdx_api = TdxHq_API() # 用的时候再连接，用完就断开，以保证不影响主程序正常退出
    tt = Trade_time()
    buf_folder = 'buffer/tdx'
    
    def __init__(self) -> None:
        # self.tscode_To_tradedata_To_fenshi_df_buf = dict()
        self.fenshi_df_buf = pd.DataFrame(columns=[
            'ts_code', 'trade_date', 'trade_time', 'price', 'vol'
        ])
        
        # self.buf_to_save = {
        #     # 'tscode_To_tradedata_To_fenshi_df_buf': self.tscode_To_tradedata_To_fenshi_df_buf,
        #     'fenshi_df_buf': self.fenshi_df_buf
        # }
        self.load_or_init_bufs()

    def get_fenshi_df(self, ts_code, trade_date) -> pd.DataFrame:
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
        # self.tscode_To_tradedata_To_fenshi_df_buf.setdefault(ts_code, dict())
        # if trade_date not in self.tscode_To_tradedata_To_fenshi_df_buf[ts_code]:
        if len(self.fenshi_df_buf[(self.fenshi_df_buf.ts_code==ts_code)&(self.fenshi_df_buf.trade_date==trade_date)])==0:
            print(f'[Tdx_df_fetcher@get_fenshi_df] {ts_code} {trade_date}:  parsing from web...')
            tdx_market = 0 if ts_code[-2:]=='SZ' else 1
            tdx_code = ts_code[:-3]
            tdx_date = self.tt.toTradeDate(trade_date)
            with self.lazy_tdx_api.connect(self.tdx_ip, self.tdx_port):
                fenshi_df = self.lazy_tdx_api.to_df(self.lazy_tdx_api.get_history_minute_time_data(tdx_market, tdx_code, tdx_date))
            fenshi_df['trade_time'] = self.tt.trade_mins[:len(fenshi_df)]
            fenshi_df['ts_code'] = ts_code
            fenshi_df['trade_date'] = trade_date
            # self.tscode_To_tradedata_To_fenshi_df_buf[ts_code][trade_date] = ret_df
            self.fenshi_df_buf = pd.concat([self.fenshi_df_buf, fenshi_df], ignore_index=True
                                           ).drop_duplicates(subset=['ts_code', 'trade_date', 'trade_time'], keep='last', inplace=False)
            with open(os.path.join(self.buf_folder, 'fenshi_df_buf.json'), 'w') as fout:  # save_buf() 中描述的，这里每次都手动保存
                self.fenshi_df_buf.to_json(fout, indent=4)
        else:
            print(f'[Tdx_df_fetcher@get_fenshi_df] {ts_code} {trade_date}:  using saved buffer.')
            
        # return self.tscode_To_tradedata_To_fenshi_df_buf[ts_code][trade_date]

        return self.fenshi_df_buf[(self.fenshi_df_buf.ts_code==ts_code)&(self.fenshi_df_buf.trade_date==trade_date)
                                  ].reset_index(drop=True)

    
    def save_buf(self) -> None:
        '''保存缓存的buf数据
        
        ????? 这个函数用不了？ 在这个方法内 self.fenshi_df_buf 为空DataFrame

        但 Tushare_df_fetcher 和 Dongcai_df_fetcher 的不会


        '''
        return None   # 用不了就每次获取新数据都手动保存把
        # self.buf_to_save = {
        #     # 'tscode_To_tradedata_To_fenshi_df_buf': self.tscode_To_tradedata_To_fenshi_df_buf,
        #     'fenshi_df_buf': self.fenshi_df_buf
        # } # 重写一遍防止之前引用的数据是旧数据，其真实数据已经是新的对象
        # for buf_name, buf_obj in self.buf_to_save.items():
        #     with open(os.path.join(self.buf_folder, buf_name+'.json'), 'w') as fout:
        #         if isinstance(buf_obj, (dict, list)):
        #             json.dump(buf_obj, fout, indent=4)
        #         elif isinstance(buf_obj, pd.DataFrame):
        #             buf_obj.to_json(fout, indent=4)
        with open(os.path.join(self.buf_folder, 'fenshi_df_buf.json'), 'w') as fout:
            self.fenshi_df_buf.to_json(fout, indent=4)

    def load_or_init_bufs(self) -> None:
        '''若存在，则载入已保存的buf数据，否则对其初始化'''
        # path = os.path.join(self.buf_folder, 'tscode_To_tradedata_To_fenshi_df_buf.json')
        # if os.path.exists(path):
        #     self.tscode_To_tradedata_To_fenshi_df_buf = pd.read_json(path)

        path = os.path.join(self.buf_folder, 'fenshi_df_buf.json')
        if os.path.exists(path):
            self.fenshi_df_buf = pd.read_json(path, dtype={'trade_date': str})