from lh import SingleStock_daily

class DayStamp:
    ssd = SingleStock_daily()
    def __init__(self, trade_date='20230103', start_cash=10000, end_cash=10000,
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
        for ts_code, vol in self.start_tscode2vol_dict:
            self.start_total += self.ssd.getPreClose(ts_code=ts_code,trade_date=trade_date) * vol
