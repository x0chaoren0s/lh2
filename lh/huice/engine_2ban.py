from lh.utils import DayStamp
from lh.time import Trade_time

class Engine_2ban:
    tt = Trade_time()
    def __init__(self, beg_date=None, end_date=None) -> None:
        self.beg_date = beg_date
        self.end_date = end_date
        self.dayStamps = dict() # {trade_date: DayStamp}
        self.trade_date = None
        self.isWorking = False

    def set_date_span(self, beg_date, end_date) -> bool:
        beg_date = self.tt.toTradeDate(date=beg_date)
        end_date = self.tt.toTradeDate(date=end_date)
        if beg_date<=end_date:
            self.beg_date = beg_date
            self.end_date = end_date
            self.trade_date = self.beg_date
            self.isWorking = True
        else:
            self.isWorking = False
        return self.isWorking
    
    def move_on(self) -> None:
        pass
        self.trade_date = self.tt.nextTradeDate(self.trade_date)
    