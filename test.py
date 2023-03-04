from lh import SingleStock_daily, tdx_disconnect, get_tdx_api, Engine_2ban
from lh.time.trade_time import Trade_time
from lh.utils.dongcai_df_fetcher import Dongcai_df_fetcher
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher



if __name__ == '__main__':
    tt = Trade_time()
    ssd = SingleStock_daily()
    df = Dongcai_df_fetcher()
    tf = Tdx_df_fetcher()
    # tdxapi = get_tdx_api()
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
    # print(ssd.getPreClose('002380.SZ','20230131'))
    # print(df.daily('603528.SH'))
    # print(df.daily('603528.SH','20230224'))
    print(tf.get_fenshi_df('603528.SH','20230227'))
    print(tf.get_fenshi_df('603528.SH','20230227').price.tolist())
    # print(ssd.getFenshi('603528.SH', '20230227'))


    # tdx_disconnect()
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=1.603528&klt=101&fqt=1&cb=jsonp1677463807289
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&rtntype=6&secid=1.603528&klt=101&fqt=1
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=0.001260&klt=101&fqt=1&cb=jsonp1677464455041
# http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&rtntype=6&secid=0.001260&klt=101&fqt=1

["09:30","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","10:30","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","11:30/13:00","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","14:00","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","15:00"]
