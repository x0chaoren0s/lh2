from lh.stockinfo.single_stock_daily import SingleStock_daily
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher
import lh.stockinfo.data_fetcher as df

class DayStamp:
    ssd = SingleStock_daily()
    # tdf = Tdx_df_fetcher()
    tdf = df
    def __init__(self, trade_date='20230103', start_cash=10000.0, end_cash=10000.0,
                 start_tscode2vol_dict=dict(), end_tscode2vol_dict=dict(),
                 buy_list=[], sell_list=[],
                 meta_dict=dict()) -> None:
        '''
        start_tscode2vol_dict、end_tscode2vol_dict：{'001338.SZ':100}：{ts_code:拥有数量}

        buy_tscode2vol_list、sell_tscode2vol_list：[('001338.SZ',100,19.36)}：[(ts_code,交易数量,成交价格)]

        meta_dict：可用于保存其他信息，如保存当天哪些股票需要跟踪低吸，在下一个交易日读取该信息并把响应股票放入buy_pool
        '''
        self.trade_date = trade_date
        self.start_cash = start_cash
        self.end_cash = end_cash
        self.start_tscode2vol_dict = start_tscode2vol_dict
        self.end_tscode2vol_dict = end_tscode2vol_dict
        self.buy_list = buy_list
        self.sell_list = sell_list

        self.start_total = self.start_cash
        for ts_code, vol in self.start_tscode2vol_dict.items():
            self.start_total += self.ssd.getPreClose(ts_code=ts_code,trade_date=trade_date) * vol

        self.end_total = self.end_cash
        for ts_code, vol in self.end_tscode2vol_dict.items():
            try:
                self.end_total += self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.iloc[0] * vol
            except:
                assert False, f'{ts_code}, {self.trade_date}'

        self.meta_dict = meta_dict

    def update_buy_deals(self, sell_form_dict, buy_form_dict, fenshi_startind:int=None):
        '''
        sell_form_dict = {
            'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
            'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
        }
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="no" checked="checked">不清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="hongpanqingcang">红盘清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="shuishangqingcang">水上清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="dietingqingcang">跌停清仓
        buy_form_dict = {
            'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
            'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
            'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
        }

        fenshi_startind: 日内自动止盈挂单，从该分时数据ind（0~239）开始挂分时单交易。默认为None全天都挂单

        先处理昨日收盘的买单和卖单

        # 再日内分时操作：11点后若出现开板，则红盘出
        '''
        self.buy_list = buy_form_dict['buy_tscode_list']
        for ts_code, hands, price in zip(self.buy_list, buy_form_dict['buy_hands_list'], buy_form_dict['buy_price_list']):
            if hands==0 or price==0.0:
                continue
            daily_df = self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date)
            if len(daily_df)==0 or daily_df.vol.iloc[0]==0:
                continue
            assert len(daily_df)>0, f'{ts_code}, {self.trade_date}'
            if price<daily_df.low.iloc[0]:
                continue
            price = min(price, daily_df.open.iloc[0])
            spend_value = hands*100*price
            if spend_value >= self.end_cash:
                continue
            self.end_tscode2vol_dict.setdefault(ts_code, 0)
            self.end_tscode2vol_dict[ts_code] += hands*100
            # end_value = hands*100*self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.iloc[0]
            self.end_cash -= spend_value
            assert self.end_cash>0
            # self.end_total = self.end_total-spend_value+end_value

        self.sell_list = sell_form_dict['sell_tscode_list']
        for ts_code, sell_type in zip(self.sell_list, sell_form_dict['sell_type_list']):
            # 昨日收盘挂的今日卖单
            if self.tdf.daily(ts_code, self.trade_date).vol.iloc[0]==0:
                continue
            if sell_type=='hongpanqingcang':
                preopen = self.ssd.getPreOpen(ts_code=ts_code, trade_date=self.trade_date)
                vol = self.start_tscode2vol_dict[ts_code]
                self._try_sell(ts_code=ts_code, sell_vol=vol, sell_price=preopen)
            elif sell_type=='shuishangqingcang':
                preclose = self.ssd.getPreClose(ts_code=ts_code, trade_date=self.trade_date)
                vol = self.start_tscode2vol_dict[ts_code]
                self._try_sell(ts_code=ts_code, sell_vol=vol, sell_price=preclose)
            elif sell_type=='dietingqingcang':
                dieting = self.ssd.getDieting(ts_code=ts_code,trade_date=self.trade_date)
                vol = self.start_tscode2vol_dict[ts_code]
                self._try_sell(ts_code=ts_code, sell_vol=vol, sell_price=dieting)

        # for ts_code in set(self.end_tscode2vol_dict.keys()) & set(self.start_tscode2vol_dict.keys()):
        #     if self.end_tscode2vol_dict[ts_code]==self.start_tscode2vol_dict[ts_code]:
        #         continue
        #     fenshi_df = self.tdf.get_fenshi_df(ts_code=ts_code, trade_date=self.trade_date)
        #     zhangting = self.ssd.getZhangting(ts_code=ts_code,trade_date=self.trade_date)
        #     if (fenshi_df.iloc[fenshi_startind:].price<zhangting).any():
        #         preopen = self.ssd.getPreOpen(ts_code=ts_code, trade_date=self.trade_date)
        #         vol = self.start_tscode2vol_dict[ts_code]
        #         self._try_sell(ts_code=ts_code, sell_vol=vol, sell_price=preopen, fenshi_startind=fenshi_startind)

        # 最后统计收盘总值
        self.end_total = self.end_cash
        for ts_code, vol in list(self.end_tscode2vol_dict.items()):
            if vol==0 and ts_code in self.start_tscode2vol_dict and self.start_tscode2vol_dict[ts_code]==0:
                del self.end_tscode2vol_dict[ts_code]
            if vol==0:
                continue
            try:
                self.end_total += self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.iloc[0] * vol
            except:
                assert False, f'{ts_code}, {self.trade_date}'

    def _try_sell(self, ts_code, sell_vol, sell_price, fenshi_startind:int=None):
        '''
        ①校正【卖出量】至多为昨日持有量，【卖出价】为调整单次交易佣金、印花税、过户费后的价格
        
        ②校正【卖出价】最低为当日开盘价

        ③【卖出价】低于当日最高价才卖

        fenshi_startind: 从该分时数据ind（0~239）开始挂分时单交易。默认为None全天都挂单
        '''
        sell_vol = min(sell_vol, self.start_tscode2vol_dict[ts_code])
        if sell_vol==0:
            return
        # sell_price = round((round(sell_price*sell_vol*0.001,2)+5.02+sell_price*sell_vol)/sell_vol,2)
        high = self.ssd.getHigh(ts_code=ts_code, trade_date=self.trade_date)
        # preclose = self.ssd.getPreClose(ts_code=ts_code, trade_date=self.trade_date)
        deal_success = False
        if fenshi_startind is None:
            if sell_price<high:
                open = self.ssd.getOpen(ts_code=ts_code, trade_date=self.trade_date)
                sell_price = max(sell_price, open)
                deal_success = True
        else:
            fenshi_df = self.tdf.get_fenshi_df(ts_code=ts_code, trade_date=self.trade_date)
            if (fenshi_df.iloc[fenshi_startind:].price>sell_price).any():
                open = fenshi_df.iloc[fenshi_startind].price
                sell_price = max(sell_price, open)
                deal_success = True
        if deal_success:
            # prevalue = sell_vol * preclose
            sellvalue = sell_vol * sell_price
            self.end_cash += sellvalue
            # self.end_total = self.end_total-prevalue+sellvalue
            self.end_tscode2vol_dict[ts_code] -= sell_vol
            # if self.end_tscode2vol_dict[ts_code]==0:   # 不再交易完后就删除清仓股票，而是转到所有交易都做完后统一处理
            #     del self.end_tscode2vol_dict[ts_code]

    def update_inday_deals(self, sell_form_dict, buy_form_dict):
        '''
        sell_form_dict = {
            'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
            'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
        }
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="no" checked="checked">不清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="hongpanqingcang">红盘清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="shuishangqingcang">水上清仓<br>
            <input type="radio" name="sell_type_{{stk.ts_code}}" value="dietingqingcang">跌停清仓
        buy_form_dict = {
            'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
            'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
            'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
        }

        fenshi_startind: 日内自动止盈挂单，从该分时数据ind（0~239）开始挂分时单交易。默认为None全天都挂单

        仅处理日内交易，先处理卖单，再处理买单
        '''
        self.sell_list = sell_form_dict['sell_tscode_list']
        for ts_code, sell_price in zip(sell_form_dict['sell_tscode_list'],sell_form_dict['sell_price_list']):
            # 昨日尾盘买入的今日上午卖出
            sell_price = float(sell_price)
            if sell_price == 0.0:
                continue
            if self.tdf.daily(ts_code, self.trade_date).vol.iloc[0]==0:
                continue
            sell_vol = self.start_tscode2vol_dict[ts_code]
            sellvalue = sell_vol * sell_price
            prevalue = sell_vol * self.ssd.getPreClose(ts_code, self.trade_date)
            self.end_cash += sellvalue-5-round(sellvalue/1000,2)
            self.end_cash -= round(sellvalue/1000)/100 if ts_code.startswith('60') else 0
            self.end_total = self.end_total-prevalue+sellvalue-5-round(sellvalue/1000,2)
            self.end_total -= round(sellvalue/1000)/100 if ts_code.startswith('60') else 0
            self.end_tscode2vol_dict[ts_code] -= sell_vol
        self.buy_list = buy_form_dict['buy_tscode_list']
        for ts_code, hands, price in zip(self.buy_list, buy_form_dict['buy_hands_list'], buy_form_dict['buy_price_list']):
            # 今日尾盘买入今日尾盘跌停的
            if hands==0 or price==0.0:
                continue
            daily_df = self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date)
            if len(daily_df)==0 or daily_df.vol.iloc[0]==0:
                continue
            assert len(daily_df)>0, f'{ts_code}, {self.trade_date}'
            if price<daily_df.low.iloc[0]:
                continue
            spend_value = hands*100*price+5
            spend_value += round(spend_value/1000)/100 if ts_code.startswith('60') else 0
            if spend_value >= self.end_cash:
                continue
            self.end_tscode2vol_dict.setdefault(ts_code, 0)
            self.end_tscode2vol_dict[ts_code] += hands*100
            end_value = hands*100*self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.iloc[0]
            self.end_cash -= spend_value
            assert self.end_cash>0
            self.end_total = self.end_total-spend_value+end_value
        for ts_code, vol in list(self.end_tscode2vol_dict.items()):
            if vol==0 and ts_code in self.start_tscode2vol_dict and self.start_tscode2vol_dict[ts_code]==0:
                del self.end_tscode2vol_dict[ts_code]
            if vol==0:
                continue
        
        