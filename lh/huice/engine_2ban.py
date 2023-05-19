from lh.utils import DayStamp
from lh.time import Trade_time
from lh.stockinfo.data_fetcher import get_tags
from lh.stockinfo import AllStock_daily

from typing import Dict

class Engine_2ban:
    tt = Trade_time()
    def __init__(self, beg_date=None, end_date=None, fenshi_startind=None) -> None:
        '''
        fenshi_startind: 日内自动止盈挂单，从该分时数据ind（0~239）开始挂分时单交易。默认为None全天都挂单
        '''
        self.beg_date = beg_date
        self.end_date = end_date
        self.dayStamps: Dict[str, DayStamp] = dict() # {trade_date: DayStamp}
        self.trade_date = None
        self.pre_trade_date = None
        self.now_dayStamp: DayStamp = None
        self.pre_dayStamp: DayStamp = None
        self.end_total = 0
        self.end_cash = 0

        self.fenshi_startind = fenshi_startind
        self.isWorking = False

    def set_date_span(self, beg_date, end_date) -> bool:
        beg_date = self.tt.toTradeDate(date=beg_date)
        end_date = self.tt.toTradeDate(date=end_date)
        if beg_date<=end_date:
            self.beg_date = beg_date
            self.end_date = end_date
            self.trade_date = self.beg_date
            self.pre_trade_date = self.tt.preTradeDate(self.trade_date)

            self.dayStamps = dict()
            self.dayStamps[self.trade_date] = DayStamp(trade_date=self.trade_date)
            self.pre_dayStamp = DayStamp(trade_date=self.tt.preTradeDate(self.trade_date))
            self.now_dayStamp = self.dayStamps[self.trade_date]
            self.end_total = 0
            self.end_cash = 0

            self.isWorking = True
        else:
            self.isWorking = False
        return self.isWorking
    
    def move_on(self, sell_form_dict, buy_form_dict) -> None:
        pass
        

        next_trade_date = self.tt.nextTradeDate(self.trade_date)
        self.dayStamps[next_trade_date] = DayStamp(
            trade_date=str(next_trade_date),
            start_cash=float(self.dayStamps[self.trade_date].end_cash),
            end_cash=float(self.dayStamps[self.trade_date].end_cash),
            start_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            end_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy()
        )

        self.pre_trade_date = self.trade_date
        self.trade_date = next_trade_date
        self.dayStamps[self.trade_date].update_buy_deals(sell_form_dict=sell_form_dict, 
                                                         buy_form_dict=buy_form_dict, fenshi_startind=self.fenshi_startind)
        self.pre_dayStamp = self.now_dayStamp
        self.now_dayStamp = self.dayStamps[self.trade_date]


class Engine_2ban_dixi(Engine_2ban):
    def __init__(self, beg_date=None, end_date=None, fenshi_startind=None) -> None:
        super().__init__(beg_date, end_date, fenshi_startind)
        self.dayTags = dict() # {trade_date: {'start_tags2count_dict': dict(), 'end_tags2count_dict': dict()}}

    def set_date_span(self, beg_date, end_date) -> bool:
        ret = super().set_date_span(beg_date, end_date)
        if ret==True:
            self.dayTags.clear()
            self.dayTags[self.trade_date] = {'start_tags2count_dict': dict(), 'end_tags2count_dict': dict()}
        return ret

    def move_on(self, sell_form_dict, buy_form_dict, meta_dict=dict()) -> None:
        pass
        
        print('[Engine_2ban_dixi@move_on]')
        assert isinstance(meta_dict, dict)
        next_trade_date = self.tt.nextTradeDate(self.trade_date)
        self.dayStamps[next_trade_date] = DayStamp(
            trade_date=str(next_trade_date),
            start_cash=float(self.dayStamps[self.trade_date].end_cash),
            end_cash=float(self.dayStamps[self.trade_date].end_cash),
            start_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            end_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            meta_dict=meta_dict
        )
        self.dayTags[next_trade_date] = {'start_tags2count_dict': self.dayTags[self.trade_date]['end_tags2count_dict'].copy(),
                                         'end_tags2count_dict': dict()}

        self.trade_date = next_trade_date
        self.dayStamps[self.trade_date].update_buy_deals(sell_form_dict=sell_form_dict, 
                                                         buy_form_dict=buy_form_dict, fenshi_startind=self.fenshi_startind)
        for ts_code in AllStock_daily().get_least_2bans_list(trade_date=self.trade_date, sort=True, only_hs=True):
            for tag in get_tags(ts_code):
                self.dayTags[self.trade_date]['end_tags2count_dict'].setdefault(tag, 0)
                self.dayTags[self.trade_date]['end_tags2count_dict'][tag] += 1
        
    
class Engine_1ban_dixi(Engine_2ban_dixi):
    def move_on(self, sell_form_dict, buy_form_dict, meta_dict=dict()) -> None:
        pass
        
        print('[Engine_1ban_dixi@move_on]')
        assert isinstance(meta_dict, dict)
        next_trade_date = self.tt.nextTradeDate(self.trade_date)
        self.dayStamps[next_trade_date] = DayStamp(
            trade_date=str(next_trade_date),
            start_cash=float(self.dayStamps[self.trade_date].end_cash),
            end_cash=float(self.dayStamps[self.trade_date].end_cash),
            start_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            end_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            meta_dict=meta_dict
        )
        self.dayTags[next_trade_date] = {'start_tags2count_dict': self.dayTags[self.trade_date]['end_tags2count_dict'].copy(),
                                         'end_tags2count_dict': dict()}

        self.trade_date = next_trade_date
        self.dayStamps[self.trade_date].update_buy_deals(sell_form_dict=sell_form_dict, 
                                                         buy_form_dict=buy_form_dict, fenshi_startind=self.fenshi_startind)
        for ts_code in AllStock_daily().getLimitUps(trade_date=self.trade_date, sort=True, only_hs=True):
            for tag in get_tags(ts_code):
                self.dayTags[self.trade_date]['end_tags2count_dict'].setdefault(tag, 0)
                self.dayTags[self.trade_date]['end_tags2count_dict'][tag] += 1
        
class Engine_weipandieting(Engine_2ban):
    def move_on(self, sell_form_dict, buy_form_dict) -> None:
        # 日内解决：上午卖昨天进的货，尾盘买今天的跌停
        self.dayStamps[self.trade_date].update_inday_deals(sell_form_dict, buy_form_dict)

        next_trade_date = self.tt.nextTradeDate(self.trade_date)
        self.dayStamps[next_trade_date] = DayStamp(
            trade_date=str(next_trade_date),
            start_cash=float(self.dayStamps[self.trade_date].end_cash),
            end_cash=float(self.dayStamps[self.trade_date].end_cash),
            start_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy(),
            end_tscode2vol_dict=self.dayStamps[self.trade_date].end_tscode2vol_dict.copy()
        )

        self.pre_trade_date = self.trade_date
        self.trade_date = next_trade_date
        self.pre_dayStamp = self.now_dayStamp
        self.now_dayStamp = self.dayStamps[self.trade_date]

class Engine_wencai(Engine_weipandieting):
    def __init__(self, beg_date=None, end_date=None, fenshi_startind=None) -> None:
        super().__init__(beg_date, end_date, fenshi_startind)
        self.wencai_query: str = ''
        self.pre_wencai_query: str = ''

    def set_wencai_query(self, query:str) -> bool:
        if not isinstance(query, str):
            return False
        self.pre_wencai_query = query.replace('昨日',self.tt.preTradeDate(self.pre_trade_date)).replace('今日',self.pre_trade_date)
        self.wencai_query = query.replace('昨日',self.pre_trade_date).replace('今日',self.trade_date)
        return True
    
    def move_on(self, sell_form_dict, buy_form_dict) -> None:
        super().move_on(sell_form_dict, buy_form_dict)
        self.pre_wencai_query = self.wencai_query
        self.wencai_query = self.wencai_query.replace(self.pre_trade_date,self.trade_date).replace(self.tt.preTradeDate(self.pre_trade_date),self.pre_trade_date)
