from lh.stockinfo import SingleStock_daily
from lh.utils import singleton
import pandas as pd

@singleton
class Tushare_df_processor:
    '''
    用于处理已经拿到的tushare表格的工具箱。
    各工具的输入是tushare表格，输出也是pandas表格。
    '''
    def __init__(self) -> None:
        self.headers =  {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        self.sd = SingleStock_daily()

    def isLimitUp(self, tushare_daily_df) -> pd.DataFrame:
        t1 = (tushare_daily_df['pre_close']*120).astype(int)/100. == tushare_daily_df['close']
        t2 = (tushare_daily_df['pre_close']*110).astype(int)/100. == tushare_daily_df['close']
        t3 = (tushare_daily_df['pre_close']*105).astype(int)/100. == tushare_daily_df['close']
        t4 = tushare_daily_df['close'] == tushare_daily_df['high']
        t5 = tushare_daily_df['pct_chg'] >= 10.0
        ret_df = tushare_daily_df.copy()
        # ret_df['isLimitUp'] = (t1 | t2 | t3) & t4
        # ret_df['isLimitUp'] = (t1 | t2 | t5) & t4
        ret_df['isLimitUp'] = (t1 | t2 | t3 | t5) & t4
        return ret_df
    
    def isNewlyListed(self, tushare_daily_df, trade_date) -> pd.DataFrame:
        ret_df = tushare_daily_df.copy()
        col_val_dict = dict((ts_code, self.sd.isJustListed(ts_code, trade_date)) for ts_code in ret_df['ts_code'])
        ret_df['isNewlyListed'] = col_val_dict.values()
        return ret_df