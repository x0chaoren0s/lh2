from lh.utils.singleton_ import singleton
from lh.time.trade_time import Trade_time
from lh.time import normalize_date
import tushare as ts
import pandas as pd
import requests, os, json

@singleton
class Dongcai_df_fetcher:
    '''
    用于获取和缓存东方财富api拿到的json并转换成的DataFrame

    使用tushare的ts_code即可，内部自动转化为东财的secid
    '''
    # pro = ts.pro_api()
    tt = Trade_time()
    candles_day_url_template = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?' \
        'fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61' \
        '&beg=0&end=20500101&rtntype=6&secid=SECID&klt=101&fqt=1' # 替换SECID
    buf_folder = 'buffer/dongcai'
    def __init__(self) -> None:
        self.daily_df_buf = pd.DataFrame(columns=[
            'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'change', 
            'pct_chg', 'vol', 'amount', 'amplitude', 'turnover', 'ts_name'
        ])
        # ts_code	    str	    股票代码
        # ts_name       str     股票名称
        # trade_date	str	    交易日期
        # open	        float	开盘价
        # high	        float	最高价
        # low	        float	最低价
        # close	        float	收盘价
        # change	    float	涨跌额
        # pct_chg	    float	涨跌幅
        # vol	        float	成交量
        # amount	    float	成交额
        # amplitude     float   振幅
        # turnover      float   换手率
        self.tags_tscode2set_buf = dict()
        
        self.buf_to_save = {
            'daily_df_buf': self.daily_df_buf, 
            'tags_tscode2set_buf': self.tags_tscode2set_buf
        }
        self.load_or_init_bufs()

    @staticmethod
    def to_secid(ts_code) -> str:
        '''将tushare的ts_code(如000638.SZ)转换成东方财富的secid(如0.000638)'''
        return '0.'+ts_code[:-3] if ts_code[-2:]=='SZ' else '1.'+ts_code[:-3]

    @staticmethod
    def to_trade_date(dc_date) -> str:
        '''将东方财富的日期(如2016-05-04)转换成tushare的trade_date(如20160504)'''
        return normalize_date(datestr=dc_date)

    def daily(self, ts_code, trade_date=None, end_date=None, try_times=1, max_try_times=3) -> pd.DataFrame:
        '''获取日k线'''
        if end_date is None:
            end_date = self.tt.nowTradeDate()
        if ts_code not in self.daily_df_buf.ts_code.tolist():
            print(f'[Dongcai_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  parsing from web...')
            secid = self.to_secid(ts_code=ts_code)
            candles_url = self.candles_day_url_template.replace('SECID', secid)
            res = requests.get(candles_url)
            if res.status_code != 200:
                assert try_times<=max_try_times, '超过尝试次数，请检查网络连接'
                return self.getCandles(ts_code=ts_code, try_times=try_times+1, max_try_times=max_try_times)
            res_dict = res.json()
            candles = res_dict['data']['klines']
            # ['2023-02-23,9.05,9.05,9.05,9.05,100485,90938473.00,0.00,9.96,0.82,1.61',..]
            col_names = ['trade_date', 'open', 'close', 'high', 'low',
                         'vol', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            cols = [[] for _ in range(11)]
            for candle in candles:
                for i,item in enumerate(candle.split(',')):
                    if i==0:
                        item = self.to_trade_date(item)
                    else:
                        item = float(item)
                    cols[i].append(item)
            cols = {name: col for name,col in zip(col_names,cols)}
            daily_df = pd.DataFrame(cols)
            daily_df['ts_code'] = ts_code
            daily_df['ts_name'] = res_dict['data']['name']
            self.daily_df_buf = pd.concat([self.daily_df_buf, daily_df], ignore_index=True).drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        else:
            print(f'[Dongcai_df_fetcher@daily] {ts_code} {trade_date} {end_date}:  using saved buffer.')
        if ts_code is None and trade_date is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None and trade_date is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']==trade_date)
            ]
        if ts_code is not None:
            return self.daily_df_buf[
                (self.daily_df_buf['ts_code']==ts_code) &
                (self.daily_df_buf['trade_date']<=end_date)
            ]
        
    def get_name(self, ts_code) -> str:
        '''返回股票名称'''
        try:
            return self.daily(ts_code=ts_code).ts_name
        except:
            assert False, f'{ts_code}'
    
    def get_tags(self, ts_code) -> set:
        '''
        从东财网页获取该股票的题材板块。
        爬虫参考 https://www.jianshu.com/p/883c74f939ee
        动态加载内容爬取参考 https://blog.csdn.net/sinat_38682860/article/details/105798818

        返回一个包含所有题材板块名称的集合，如
        {'昨日涨停_含一字', '广东板块', '国产芯片', '无线耳机', '植物照明', '电子元件', '参股新三板', '5G概念', 
        '昨日连板_含一字', '国家安防', '深圳特区', '字节概念', '新能源车', 
        '网红直播', '智能穿戴', '独角兽', '物联网', '区块链', '华为概念'}
        '''
        if ts_code not in self.tags_tscode2set_buf:
            print(f'[Dongcai_df_fetcher@get_tags] {ts_code}: parsing from web...')
            # 浏览器网页 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=web&code=SZ002137#
            # f12搜索 所属板块 和 经营范围 得动态加载接口 https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137
            # url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002137'
            url = f'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code={ts_code[-2:]+ts_code[:-3]}'
            res = requests.get(url = url)
            while res.status_code!=200:
                res = requests.get(url = url)
            resjson = res.json()
            tags = {bk['BOARD_NAME'] for bk in resjson['ssbk']}
            self.tags_tscode2set_buf[ts_code] = tags
        else:
            print(f'[Dongcai_df_fetcher@get_tags] {ts_code}: using saved buffer.')
        return self.tags_tscode2set_buf[ts_code]
    
    def save_buf(self) -> None:
        '''保存缓存的buf数据'''
        print('[Dongcai_df_fetcher@save_buf]')
        self.buf_to_save = {
            'daily_df_buf': self.daily_df_buf, 
            'tags_tscode2set_buf': self.tags_tscode2set_buf
        } # 重写一遍防止之前引用的数据是旧数据，其真实数据已经是新的对象
        # for buf_name, buf_obj in self.buf_to_save.items():
        #     with open(os.path.join(self.buf_folder, buf_name+'.json'), 'w') as fout:
        #         if isinstance(buf_obj, (dict, list)):
        #             json.dump(buf_obj, fout, indent=4)  # tags_tscode2set_buf 中有set，不能序列化，因此手动转化成list，载入的时候也手动转回来
        #         elif isinstance(buf_obj, pd.DataFrame):
        #             buf_obj.to_json(fout, indent=4)
        with open(os.path.join(self.buf_folder, 'daily_df_buf.json'), 'w') as fout:
            self.daily_df_buf.to_json(fout, indent=4)
        with open(os.path.join(self.buf_folder, 'tags_tscode2set_buf.json'), 'w') as fout:
            tags_tscode2list_buf = {tscode:list(tags_set) for tscode,tags_set in self.tags_tscode2set_buf.items()}
            json.dump(tags_tscode2list_buf, fout, indent=4)

    def load_or_init_bufs(self) -> None:
        '''若存在，则载入已保存的buf数据，否则对其初始化'''
        path = os.path.join(self.buf_folder, 'daily_df_buf.json')
        if os.path.exists(path):
            self.daily_df_buf = pd.read_json(path, dtype={'trade_date': str})

        path = os.path.join(self.buf_folder, 'tags_tscode2set_buf.json')
        if os.path.exists(path):
            with open(path, 'r') as fin:
                tags_tscode2list_buf = json.load(fin)
            self.tags_tscode2set_buf = {tscode:set(tags_list) for tscode,tags_list in tags_tscode2list_buf.items()}