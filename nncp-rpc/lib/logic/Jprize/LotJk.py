# coding:utf-8

import traceback
from decimal import Decimal
import MySQLdb

import define
import LotBase
import jkTicket
from logic.Ticket.syxw import SyxwTicket
from util.tools import Log

logger = Log().getLog()

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        lotname_map = {
            44: '广西11选5',
            45: '江西11选5'

        }
        self.lotname= lotname_map.get(int(lotid))

    def jprize(self, params):
        #算奖
        try:
            logger.debug('%s算奖开始...params=%s', self.lotname, params)
            expect = params.get("expect")
            if not expect:
                logger.info('%s算奖获取开奖期号为空', self.lotname)
                return
            expectinfo = self.getExpect(expect)
            if not expectinfo:
                return
            expect = expectinfo.get('expect')
            opencode = ",".join(expectinfo.get('openCode').split(" "))
            tickets = self.getTicketsbyExpect(expect)
            if len(tickets) == 0:
                logger.info('%s[%s]期加载票为空',self.lotname, expect)
                return
            logger.info('%s[%s]期:待算奖彩票%s张', self.lotname, expect, len(tickets))
            results = []
            for ticket in tickets:
                info = jkTicket.procGuoguan(expectinfo, opencode, ticket)
                if info:
                    isjprize = define.TICKET_JPRIZE_PRIZE if float(info["getmoney"]) > 0 else define.TICKET_JPRIZE_LOSE
                    results.append([isjprize, info["getmoney"],info["pregetmoney"],info["tid"]])
            #更新票状态
            if results:
                self.updateJprizeStatus(results)
            logger.info('%s[%s]期:更新彩票中奖状态%s张', self.lotname, expect, len(results))
        except Exception as e:
            logger.error('彩种[%s]算奖出错:%s',self.lotname,traceback.format_exc())

    def getExpect(self, expect):
        # 获取开奖期号、开奖号码
        try:
            return SyxwTicket(self.lotid).get_open_expect(expect)
        except:
            logger.error(traceback.format_exc())
            return {}
