#coding:utf-8


import traceback
from logic.match import LQMatch
from logic.ticket import Ticket
from jprize.JlTicket import JlTicket
from util.tools import Log
import LotBase

logger = Log().getLog()

class Lottery(LotBase.Lottery):
    
    def __init__(self, lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname = '竞篮'

    def jprize(self):
        try:
            #载入对阵
            matches = self.loadMatches()
            if not matches:
                return
            num = 0
            #以某场比赛为最后一场的所有的票
            for xid,m in matches.iteritems():
                tickets = self.loadTickets(xid)
                if not tickets:continue
                
                results = []
                for t in tickets:
                    try:
                        handler = JlTicket(t, matches)
                        ret = handler.handTicket()
                        if ret.get("valid") == True:
                            results.append([ret["getmoney"],ret["pregetmoney"],ret["returnmoney"],ret["returnnum"],0,ret["tid"]])
                    except Exception as e:
                        logger.error(traceback.format_exc())
                #更新票状态
                self.updateJprizeStatus(results)
                num += len(results)
            logger.info('竞彩篮球:更新彩票中奖状态%s张', num)
        except Exception as e:
            logger.error(traceback.format_exc())

    def loadMatches(self):
        """回溯最近3天的比赛
        """
        mdict = {}
        mlist= LQMatch().get_matches_by_date(-3)
        for m in mlist:
            mdict.update({str(m.get("f_xid")):m})
        return mdict

    def loadTickets(self, processid):
        return Ticket().get_tickets_by_match(self.lotid,processid)
