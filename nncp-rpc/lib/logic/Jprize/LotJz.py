#coding:utf-8
#File: LotJz.py
#Auth: lixp(@500wan.com)
#Date: 2015-10-20 15:17:59
#Desc: 

import traceback
from logic.match import ZQMatch
from logic.ticket import Ticket
from jprize.JzTicket import JzTicket
from util.tools import Log
import LotBase

logger = Log().getLog()

class Lottery(LotBase.Lottery):
    
    def __init__(self, lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname = '竞足'

    def jprize(self):
        try:
            #载入对阵
            matches = self.loadMatches()
            if not matches:
                return

            #以某场比赛为最后一场的所有的票
            for xid,m in matches.iteritems():
                tickets = self.loadTickets(xid)
                if not tickets:continue
                
                results = []
                for t in tickets:
                    try:
                        handler = JzTicket(t, matches) 
                        ret = handler.handTicket()
                        if ret.get("valid") == True:
                            results.append([ret["getmoney"],ret["pregetmoney"],ret["returnmoney"],ret["returnnum"],0,ret["tid"]])
                    except Exception as e:
                        logger.error(traceback.format_exc())
                #更新票状态
                self.updateJprizeStatus(results)
        except Exception as e:
            logger.error(traceback.format_exc())

    def loadMatches(self):
        """回溯最近3天的比赛
        """
        mdict = {}
        mlist= ZQMatch().get_matches_by_date(-4)
        for m in mlist:
            mdict.update({str(m.get("f_xid")):m})
        return mdict

    def loadTickets(self, processid):
        return Ticket().get_tickets_by_match(self.lotid,processid)
