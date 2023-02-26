from lh import Trade_time, SingleStock_daily, tdx_disconnect


if __name__ == '__main__':
    tt = Trade_time()
    ssd = SingleStock_daily()
    # print(tt.toTradeDate())
    # print(tt.toTradeDate('20221019'))
    # print(tt.toTradeDate('20221017'))
    # print(tt.toTradeDate('20221015'))
    # print(tt.toTradeDate('20221014'))
    # print(tt.preTradeDate('20221019'))
    # print(tt.nextTradeDate('20221019'))
    # print(tt.nextTradeDate('20221022'))
    # print(tt.nowTradeDate())
    # print(ssd.getPrice_df(ts_code='002380.SZ'))
    print(ssd.getPreClose('002380.SZ','20230131'))

    tdx_disconnect()
