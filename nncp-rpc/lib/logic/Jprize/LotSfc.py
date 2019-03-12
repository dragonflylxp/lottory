#coding=utf-8
import traceback
from decimal import Decimal

import LotBase
from util.tools import Log

logger = Log().getLog()

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname='胜负彩'

    def jprize(self):
        #算奖
        try:
            expectinfo = self.getExpect()
            if expectinfo is None:
                return
            expect = expectinfo['expect']
            opencode = expectinfo['opencode'].split(',')
            # opencode = ['3','1','1','3','1','1','1','1','1','1','1','1','1','1']
            # expect = '16091'
            tickets = self.getTicketsbyExpect(expect)
            if len(tickets) == 0:
                logger.info('胜负彩[%s]期加载票为空',expect)
                return 
            logger.info('胜负彩[%s]期:待算奖彩票%s张', expect, len(tickets))

            results = []
            for row in tickets:
                info = self.procTicket(expectinfo,opencode, row)
                logger.info('info:%s',info)
                if info:
                    results.append([info['getmoney'],info['pregetmoney'],Decimal('0'),0,info['hit'],info['tid']])
                                   
            #更新票状态
            if results:
                self.updateJprizeStatus(results)
            logger.info('胜负彩[%s]期:更新彩票中奖状态%s张', expect,len(results))
        except:
            logger.error('彩种[%s]算奖出错:%s',self.lotname,traceback.format_exc())

    def procTicket(self,expinfo, openCode, ticket):
        ''' 票算奖入口
            expinfo 期号信息
            opencode 开奖号码 数组
            ticket 票信息 '''
        ret = {}
        ret.update(ticket)
        ret['zmax'] = 0
        ret['hit'] = 0
        try:
            onenum = 0
            twonum = 0
            for code in ticket['f_fileorcode'].split('$'):
                codeArr = code.split(',')
                hit = 0  #命中场数
                for i in range(0,14) :
                    if codeArr[i].count(openCode[i])==1:
                        hit += 1
                if hit > ret['hit']:
                    ret['hit'] = hit

                if hit == 14: #命中14场
                    onenum += 1
                    ret['zmax'] = 1
                    for x in range(0,14):
                        opt = len(codeArr[x])
                        twonum += opt-1

                if hit == 13: #命中13场
                    ret['zmax'] = 1
                    for y in range(0,14):
                        if codeArr[y].count(openCode[y])==0:
                            twonum += len(codeArr[y])
                            break

            ret['onenum'] = onenum*ticket['f_beishu']
            ret['twonum'] = twonum*ticket['f_beishu']
            ret['pregetmoney'] = ret['onenum']*expinfo['pre_onemoney'] + ret['twonum']*expinfo['pre_twomoney']
            ret['getmoney'] = ret['onenum']*expinfo['onemoney'] + ret['twonum']*expinfo['twomoney']
            ret['tid'] = ticket['f_ticketid']
            return ret
        except:
            logger.error('sfc procTicket failed: %s [%s]', ticket, traceback.format_exc())
            return 0
