from lh.stockinfo.single_stock_daily import SingleStock_daily

class DayStamp:
    ssd = SingleStock_daily()
    def __init__(self, trade_date='20230103', start_cash=10000.0, end_cash=10000.0,
                 start_tscode2vol_dict=dict(), end_tscode2vol_dict=dict(),
                 buy_list=[], sell_list=[]) -> None:
        '''
        start_tscode2vol_dict、end_tscode2vol_dict：{'001338.SZ':100}：{ts_code:拥有数量}

        buy_tscode2vol_list、sell_tscode2vol_list：[('001338.SZ',100,19.36)}：[(ts_code,交易数量,成交价格)]
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
            self.end_total += self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.tolist()[0] * vol

    def update_buy_deals(self, buy_form_dict):
        '''
        buy_form_dict = {
            'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
            'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
            'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
        }

        暂时还没处理手续费印花税等
        '''
        self.buy_list = buy_form_dict['buy_tscode_list']
        for ts_code, hands, price in zip(self.buy_list, buy_form_dict['buy_hands_list'], buy_form_dict['buy_price_list']):
            if hands==0 or price==0.0:
                continue
            if price<self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).low.tolist()[0]:
                continue
            self.end_tscode2vol_dict.setdefault(ts_code, 0)
            self.end_tscode2vol_dict[ts_code] += hands*100
            spend_value = hands*100*price
            end_value = hands*100*self.ssd.getDaily_df(ts_code=ts_code,trade_date=self.trade_date).close.tolist()[0]
            self.end_cash -= spend_value
            self.end_total = self.end_total-spend_value+end_value

        