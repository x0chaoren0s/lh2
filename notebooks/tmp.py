import sys
sys.path.append(r'D:\Users\60490\lh2')

import pandas as pd
from tqdm import tqdm

from lh.stockinfo.all_stock_daily import AllStock_daily
from lh.stockinfo.single_stock_daily import SingleStock_daily
from lh.time import Trade_time
asd = AllStock_daily()
ssd = SingleStock_daily()
tt = Trade_time()

date_beg = '20220901'
date_end = '20220911'
trade_dates = tt.getTradeDateList(date_beg, date_end)
MAX_K = 2
bank_pres = [asd.get_only_k_bans_list(k, tt.preTradeDate(trade_dates[0]), False, True) for k in range(1,MAX_K+1)]
bank_posts = [[]]*MAX_K
cnt_bank_posts = [0 for _ in range(MAX_K)]
cnt_bank_post_yijias = [0]*MAX_K
for trade_date in tqdm(trade_dates):
    banks = [asd.get_only_k_bans_list(k, trade_date, False, True) for k in range(1,MAX_K+1)]

    for i in range(MAX_K):
        for ts_code,buy_price in bank_posts[i]:
            daily = ssd.getDaily_df(ts_code, trade_date)
            cnt_bank_post_yijias[i] += 1 if daily.high.iloc[0] > buy_price else 0
    
    bank_posts = [[] for _ in range(MAX_K)]
    for i in range(MAX_K):
        for ts_code in bank_pres[i]:
            daily = ssd.getDaily_df(ts_code, trade_date)
            if daily.low.iloc[0] == daily.high.iloc[0]:
                continue
            cnt_bank_posts[i] += 1
            bank_posts[i].append((ts_code,daily.open.iloc[0]))

    bank_pres = banks


for i in range(MAX_K):
    k = i+1
    print(k, cnt_bank_posts[i], cnt_bank_post_yijias[i], cnt_bank_post_yijias[i]/cnt_bank_posts[i])