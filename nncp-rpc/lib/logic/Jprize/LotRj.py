# coding=utf-8
import time
import logging
import traceback
from decimal import Decimal

import LotBase
import operator

from util.tools import Log

logger = Log().getLog()


class Lottery(LotBase.Lottery):
    def __init__(self, lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname = '任选九场'

    def jprize(self):
        # 算奖
        try:
            expectinfo = self.getExpect()
            if expectinfo is None:
                return
            expect = expectinfo['expect']
            opencode = expectinfo['opencode'].split(',')
            tickets = self.getTicketsbyExpect(expect)
            if len(tickets) == 0:
                logger.info('任选九场[%s]期加载票为空', expect)
                return
            logger.info('任选九场[%s]期:待算奖彩票%s张', expect, len(tickets))

            results = []
            for row in tickets:
                info = self.procTicket(expectinfo, opencode, row)
                logger.info('info:%s', info)
                if info:
                    results.append([info['getmoney'], info['pregetmoney'], Decimal('0'), 0, info['hit'], info['tid']])

            # 更新票状态
            if results:
                self.updateJprizeStatus(results)
            logger.info('任选九场[%s]期:更新彩票中奖状态%s张', expect, len(results))
        except:
            logger.error('彩种[%s]算奖出错:%s', self.lotname, traceback.format_exc())

    def procTicket(self, expinfo, openCode, ticket):
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
            for code in ticket['f_fileorcode'].split('$'):
                codeArr = code.split(',')
                hit = 0  # 命中场数
                for i in range(0, 14):
                    if codeArr[i].count(openCode[i]) == 1:
                        hit += 1
                if hit > ret['hit']:
                    ret['hit'] = hit
                if hit == 9:
                    onenum += reduce(operator.mul, range(hit - 9 + 1, hit + 1)) / reduce(operator.mul, range(1, 9 + 1))
                    ret['zmax'] = 1
            ret['onenum'] = onenum * ticket['f_beishu']
            ret['pregetmoney'] = ret['onenum'] * expinfo['pre_onemoney']
            ret['getmoney'] = ret['onenum'] * expinfo['onemoney']
            ret['tid'] = ticket['f_ticketid']
            return ret
        except:
            logger.error('proc failed: %s [%s]', ticket, traceback.format_exc())
            return 0
