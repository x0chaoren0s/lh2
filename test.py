from lh import SingleStock_daily, AllStock_daily, tdx_disconnect, get_tdx_api, Engine_2ban
from lh.time.trade_time import Trade_time
from lh.utils.dongcai_df_fetcher import Dongcai_df_fetcher
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher
from lh.utils.tushare_df_fetcher import Tushare_df_fetcher



if __name__ == '__main__':
    tt = Trade_time()
    ssd = SingleStock_daily()
    asd = AllStock_daily()
    df = Dongcai_df_fetcher()
    tdf = Tushare_df_fetcher()
    tf = Tdx_df_fetcher()
    # tdxapi = get_tdx_api()
    # print(tt.toTradeDate())
    # print(tt.toTradeDate('20221019'))
    # print(tt.toTradeDate('20221017'))
    # print(tt.toTradeDate('20221015'))
    # print(tt.toTradeDate('20221014'))
    print(tt.preTradeDate('20221019'))
    print(tt.preTradeDate('20181228'))
    # print(tt.nextTradeDate('20221019'))
    # print(tt.nextTradeDate('20221022'))
    # print(tt.nowTradeDate())
    # print(tt.getTradeDateList('20221230','20230214'))
    # print(len(tt.getTradeDateList('20221230','20230214')))
    # print(len(tt.getTradeDateList('20230214','20230331')))
    # print(ssd.getPrice_df(ts_code='002380.SZ'))
    # print(ssd.getPreClose('002380.SZ','20230131'))
    # print(df.daily('603528.SH'))
    # print(df.daily('603528.SH','20230224'))
    # print(tdf.daily('603528.SH','20230224'))
    # print(tf.get_fenshi_df('603528.SH','20230227'))
    # print(tf.get_fenshi_df('603528.SH','20230227').iloc[60].price)
    # print(tf.get_fenshi_df('603528.SH','20230227').price.tolist())
    # print(ssd.getFenshi('603528.SH', '20230227'))
    # print(asd.get_only_k_bans_list(12,'20230305',True,True))
    # print(len(asd.get_only_k_bans_list(1,'20230305',True,True)))
    # print(ssd.isLimitUp('002089.SZ','20230303'))
    # print(ssd.isLimitUp('002089.SZ','20230302'))
    # print(ssd.isLimitUp('002089.SZ','20230301'))
    # print(ssd.isLimitUp('002089.SZ','20230228'))
    # print(ssd.numLimitedUps('002089.SZ','20230228'))
    # print(ssd.isLimitUp('002813.SZ','20230203'))
    # print(ssd.isLimitUp('000014.SZ','20220901'))
    # print(ssd.getDaily_df(ts_code='000587.SZ',trade_date='20230203').close.iloc[0])
    # print(asd.get_only_k_bans_list(1,'20230214',True,True))
    # print(asd.get_only_k_bans_list(3,'20230216',True,True))
    # print(asd.get_only_k_bans_list(4,'20230216',True,True))
    # print(asd.getLimitUps('20230216',True,True))
    # print(asd.get_least_2bans_list('20230324', True, True, True))
    # print(asd.get_least_k_bans_list(2, '20230324', True, True, True))

    # df.save_buf()
    # tf.save_buf()


    tdx_disconnect()
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=1.603528&klt=101&fqt=1&cb=jsonp1677463807289
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&rtntype=6&secid=1.603528&klt=101&fqt=1
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=0.001260&klt=101&fqt=1&cb=jsonp1677464455041
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&rtntype=6&secid=0.001260&klt=101&fqt=1


["09:30","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","10:30","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","11:30/13:00","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","14:00","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","15:00"]
['ST爱迪尔', '中成股份', '朗博科技', '*ST中安', '亚翔集成', 'ST金正', '瑞泰科技', '蓝科高新', 'ST大集', '*ST深南', '联翔股份', '康强电子', '工业富联', '*ST未来', '好利科技', 'N川黄金', '中船科技', '通富微电', 'N金海通', '*ST辅仁', '人人乐', '远东传动', 'ST泰禾', '美格智能']