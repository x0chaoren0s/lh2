from lh.utils import singleton, get_tdx_api, tdx_disconnect
from lh.utils.tushare_df_fetcher import Tushare_df_fetcher
from lh.time import Trade_time
import tushare as ts
import pandas as pd
# import pandas as pd

@singleton
class SingleStock_daily:
    '''用于查询某日的特定股票的信息'''
    pro = ts.pro_api()
    tt = Trade_time()
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    tt = Trade_time()
    tf = Tushare_df_fetcher()
    def __init__(self) -> None:
        self.tdxapi = get_tdx_api() # 不设置为静态成员变量，防止声明该类的时候被自动运行get_tdx_api，从而无法正常结束
        self.stock2tags_buf = dict()
    # def getPrice(self, ts_code, trade_date):
    #     '''
    #     日线数据
    #     返回一个字典: keys: {ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount}
    #     '''
    #     ret = {'ts_code':ts_code, 'trade_date':trade_date}
    #     # 先尝试tushare获取数据
    #     # daily = self.pro.daily(ts_code=ts_code, trade_date=trade_date).iloc[0]
    #     # ['688639.SH', '20221018', 138.13, 139.98, 134.98, 136.89, 140.0, -3.11, -2.2214, 9250.91, 126681.448]
    #     # daily_df = self.pro.daily(ts_code=ts_code, trade_date=trade_date)
    #     daily_df = _tf.daily(ts_code=ts_code, trade_date=trade_date)
    #     if len(daily_df)>0:
    #     # if False:
    #         daily = daily_df.iloc[0]
    #         ret.update({'open':daily['open'], 'high':daily['high'], 'low':daily['low'], 'close':daily['close'], 
    #             'pre_close':daily['pre_close'], 'change':daily['change'], 'pct_chg':daily['pct_chg'], 
    #             'vol':daily['vol'], 'amount':daily['amount']})
    #     # return {'error_info': 'no price info'}
    #     # tushare数据缺失再从东财爬
    #     else:
    #         url = f'http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13' + \
    #                 '&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbf' + \
    #                 f'ba10b&rtntype=6&secid={tscode2code(ts_code)}&klt=101&fqt=1'
    #         res = requests.get(url = url, headers=self.headers)
    #         resjson = res.json()
    #         klines = resjson['data']['klines']
    #         date = normalize_date(trade_date, '%Y%m%d', '%Y-%m-%d')
    #         for i,record in enumerate(klines):
    #             if record.startswith(date):
    #                 break
    #         prerecord = klines[i-1]
    #         prerecord = prerecord.split(',')
    #         record = record.split(',')
    #         # ['2022-10-18', '138.13', '136.89', '139.98', '134.98', '9251', '126681448.00', '3.57', '-2.22', '-3.11', '1.32']
    #         ret.update({'open':float(record[1]), 'high':float(record[3]), 'low':float(record[4]), 'close':float(record[2]), 
    #             'pre_close':float(prerecord[2]), 'change':float(record[9]), 'pct_chg':float(record[8]), 
    #             'vol':float(record[5]), 'amount':float(record[6])/1000.0})
    #     return ret
    
    def getPrice_df(self, ts_code=None, trade_date=None, end_date=None) -> pd.DataFrame:
        '''
        日线数据
        返回一个dataframe: {ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount}
        '''
        return self.tf.daily(ts_code, trade_date, end_date)

    def getPreClose(self, ts_code, trade_date) -> float:
        '''
        返回特定股票trade_date的上一个交易日的收盘价
        '''
        return self.getPrice_df(ts_code=ts_code,trade_date=trade_date)['pre_close'].tolist()[0]

    # def getFenshi(self, ts_code, trade_date):
    #     '''
    #     #### 获取历史分时数据，即历史1分钟数据。
    #     #### trade_date会自动转换为最近的历史交易日。
    #     #### 返回一个dataframe，共240行（0-239，代表一个交易日的4个小时开盘时间），两列：[price, vol, trade_time]
    #     '''
    #     # if not self.tdxapi.connect(self.tdxip, self.tdxport):
    #     #     raise RuntimeError('通达信服务器连接失败。')
    #     tdx_market = 0 if ts_code[-2:]=='SZ' else 1
    #     tdx_code = ts_code[:-3]
    #     tdx_date = self.tt.toTradeDate(trade_date)
    #     ret_df = self.tdxapi.to_df(self.tdxapi.get_history_minute_time_data(tdx_market, tdx_code, tdx_date))
    #     ret_df['trade_time'] = self.tt.trade_mins[:len(ret_df)]
    #     return ret_df
        
    
    # def isLimitDown(self, ts_code, trade_date) -> bool:
    #     '''
    #     判断当日该股票是否收盘跌停
    #     '''
    #     price_info = self.getPrice(ts_code, trade_date)
    #     if 'error_info' in price_info:
    #         return False
    #     return int(price_info['pre_close']*80)/100.0 == price_info['close'] or \
    #             int(price_info['pre_close']*90)/100.0 == price_info['close'] or \
    #             int(price_info['pre_close']*95)/100.0 == price_info['close']

    # def isLimitUp(self, ts_code, trade_date) -> bool:
    #     '''
    #     判断当日该股票是否收盘涨停
    #     '''
    #     daily_df = _tf.daily(ts_code=ts_code, trade_date=trade_date)
    #     return _tp.isLimitUp(daily_df)['isLimitUp'].tolist()
    #     # price_info = self.getPrice(ts_code, trade_date)
    #     # if 'error_info' in price_info:
    #     #     return False
    #     # return int(price_info['pre_close']*120)/100.0 == price_info['close'] or \
    #     #         int(price_info['pre_close']*110)/100.0 == price_info['close'] or \
    #     #         int(price_info['pre_close']*105)/100.0 == price_info['close']

    # def getInfo(self, ts_code) -> dict:
    #     '''
    #     获取个股基本信息，返回一个dict, keys: {'ts_code', 'ts_name','list_date'}
    #     '''
    #     ret = {'ts_code': ts_code}
    #     url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code={ts_code[-2:]+ts_code[:-3]}'
    #     res = requests.get(url = url, headers=self.headers)
    #     while res.status_code!=200:
    #         res = requests.get(url = url, headers=self.headers)
    #     try:
    #         resjson = res.json()
    #     except:
    #         # 数据损坏重新运行
    #         return self.getInfo(ts_code)

            
    #     ret['ts_name'] = resjson['jbzl'][0]['STR_NAMEA']
    #     listing_date = resjson['fxxg'][0]['LISTING_DATE'] # '2007-06-13 00:00:00'
    #     listing_date = normalize_date(listing_date, '%Y-%m-%d %H:%M:%S', '%Y%m%d') # '20070613'
    #     ret['list_date'] = listing_date
    #     return ret.copy()

    # def isJustListed(self, ts_code, trade_date):
    #     '''
    #     判断该股票是否是当日刚刚上市第一天
    #     '''
    #     # return len(self.pro.daily(ts_code=ts_code, end_date=trade_date)) == 1
    #     # return len(_tf.daily(ts_code=ts_code, end_date=trade_date)) == 1
    #     # return self.pro.bak_basic(ts_code=ts_code)['list_date'].iloc[0] == trade_date
    #     return self.getInfo(ts_code=ts_code)['list_date'] == trade_date

    # def getTags(self, ts_code) -> set:
    #     '''
    #     从东财网页获取该股票的题材板块。
    #     爬虫参考 https://www.jianshu.com/p/883c74f939ee
    #     动态加载内容爬取参考 https://blog.csdn.net/sinat_38682860/article/details/105798818

    #     返回一个包含所有题材板块名称的集合，如
    #     {'昨日涨停_含一字', '广东板块', '国产芯片', '无线耳机', '植物照明', '电子元件', '参股新三板', '5G概念', 
    #     '昨日连板_含一字', '国家安防', '深圳特区', '字节概念', '新能源车', 
    #     '网红直播', '智能穿戴', '独角兽', '物联网', '区块链', '华为概念'}
    #     '''
    #     if ts_code not in self.stock2tags_buf:
    #         # 浏览器网页 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=web&code=SZ002137#
    #         # f12搜索 所属板块 和 经营范围 得动态加载接口 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137
    #         # url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137'
    #         url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={ts_code[-2:]+ts_code[:-3]}'
    #         res = requests.get(url = url, headers=self.headers)
    #         while res.status_code!=200:
    #             res = requests.get(url = url, headers=self.headers)
    #         resjson = res.json()
    #         tags = {bk['BOARD_NAME'] for bk in resjson['ssbk']}
    #         self.stock2tags_buf[ts_code] = tags
    #     return self.stock2tags_buf[ts_code]
