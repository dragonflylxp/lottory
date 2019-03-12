#coding=utf-8

from jprize import QxTicket
import traceback
from decimal import Decimal
import LotBase
from esun.lottery.lottery_info_cache import QxcXmlCache
from util.tools import Log

logger = Log().getLog()

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname='七星彩'


    def jprize(self):
        #算奖
        try:
            expectinfos = self.getExpect()
            for expectinfo in expectinfos:
                if expectinfo is None:
                    continue
                expect = expectinfo['expect']
                opencode = expectinfo['opencode'].split(',')
                tickets = self.getTicketsbyExpect(expect)
                if len(tickets) == 0:
                    logger.info('七星彩[%s]期加载票为空',expect)
                    continue
                logger.info('七星彩[%s]期:待算奖彩票%s张', expect, len(tickets))
                results  = []
                for ticket in tickets:
                    info = QxTicket.procTicket(expectinfo,opencode, ticket)
                    if info:
                        results.append([info["getmoney"],info["pregetmoney"],Decimal("0"),0,0,info["tid"]])
                #更新票状态
                if results:
                    self.updateJprizeStatus(results)
                logger.info('七星彩[%s]期:更新彩票中奖状态%s张', expect, len(results))
        except:
            logger.error('彩种[%s]算奖出错:%s',self.lotname,traceback.format_exc())

    # def procTicket(self,expinfo, openCode, ticket):
    #     ''' 票算奖入口
    #         expinfo 期号信息
    #         opencode 开奖号码 数组
    #         ticket 票信息 '''
    #     ret = {}
    #     ret.update(ticket)
    #     try:
    #         onenum = 0
    #         for code in ticket['f_fileorcode'].split('$'):
    #             # 直选
    #             codeArr = code.split('|')
    #             hit = 1
    #             for i in range(len(openCode)):
    #                 if openCode[i] not in codeArr[i]:
    #                     hit = 0
    #                     break
    #             if hit == 1:
    #                 onenum += 1
    #         ret['pregetmoney'] = onenum * float(expinfo['levalmoney01'])
    #         ret['getmoney'] = ret['pregetmoney'] * 0.8
    #         ret['tid'] = ticket['f_ticketid']
    #         return ret
    #     except:
    #         logger.error('proc failed: %s [%s]', ticket, traceback.format_exc())

    def getExpect(self):
        # 获取开奖期号、开奖号码
        list5 = list()
        con = None
        try:
            basicinfo = QxcXmlCache().get_qxc_basic_info()
            list5 = QxcXmlCache().get_qxc_list5_info()
            for info in list5:
                info.update({
                    'onemoney': basicinfo['levalmoney01'],
                    'twomoney': basicinfo['levalmoney02'],
                    'threemoney': basicinfo['levalmoney03'],
                    'fourmoney': basicinfo['levalmoney04'],
                    'fivemoney': basicinfo['levalmoney05'],
                    'sixmoney': basicinfo['levalmoney06'],
                })
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if con: con.close()
            return list5