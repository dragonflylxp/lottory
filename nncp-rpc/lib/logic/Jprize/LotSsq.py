#coding=utf-8
import traceback
import re
from decimal import *
import define
import LotBase
import ssqTicket
from logic.Ticket.ssq import SsqTicket
from util.tools import Log
import MySQLdb

logger = Log().getLog()

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname='双色球'

    def jprize(self, params):
        #算奖
        try:
            logger.debug('%s算奖开始...params=%s', self.lotname, params)
            expect = params.get("expect", "")
            if not expect:
                logger.info('%s算奖获取开奖期号为空', self.lotname)
                return
            expectinfo = self.getExpect(expect)
            if not expectinfo:
                return
            logger.debug(expectinfo)
            expect = expectinfo['expect']
            opencode = self.parseOpencode(expectinfo['opencode'])
            tickets = self.getTicketsbyExpect(expect)
            if len(tickets) == 0:
                logger.info('%s[%s]期加载未算奖票为空',self.lotname, expect)
                return
            logger.info('%s[%s]期:待算奖彩票%s张', self.lotname, expect, len(tickets))
            results = []
            for row in tickets:
                info = ssqTicket.procGuoguan(expectinfo,opencode,row)
                if info:
                    isjprize = define.TICKET_JPRIZE_PRIZE if float(info["getmoney"]) > 0 else define.TICKET_JPRIZE_LOSE
                    results.append([isjprize, info["getmoney"],info["pregetmoney"],info["tid"]])

            #更新票状态
            if results:
                try:
                    self.updateJprizeStatus(results)
                    logger.info('%s[%s]期:更新彩票中奖状态%s张', self.lotname, expect, len(results))
                except:
                    logger.error('%s[%s]期:更新彩票中奖状态异常', self.lotname, expect)
                    raise
        except:
            logger.error('彩种[%s]算奖出错:%s',self.lotname,traceback.format_exc())
            raise

    def parseOpencode(self, opencode):
        if not re.match(r'^\d\d(,\d\d){6}$', opencode):
            raise Exception('开奖号码错误')
        opcode = opencode.split(',')
        return {'reds': opcode[:6], 'blues': opcode[1:]}

    def getExpect(self, expect):
        # 获取开奖期号、开奖号码、奖金
        expectinfo = {}
        try:
            data = SsqTicket().get_open_expect(expect)
            if not data:
                logger.debug("%s[%s]期数据获取失败", self.lotname, expect)
                return None

            if not data.get("openCode", "") or not data.get("fisrtPrize", ""):
                logger.debug("%s[%s]期还未开奖", self.lotname, data.get("expect"))
                return None

            logger.debug(data)
            expectinfo['expect'] = data.get('expect')

            #税前1,2,3等奖
            expectinfo['pre_onemoney'] = float(data.get('fisrtPrize'))
            expectinfo['pre_twomoney'] = float(data.get('secondPrize'))

            #税后1,2,3等奖
            expectinfo['onemoney'] = expectinfo['pre_onemoney'] * 0.8
            expectinfo['twomoney'] = expectinfo['pre_twomoney'] * 0.8

            #4,5,6等奖
            expectinfo['threemoney'] = 3000
            expectinfo['fourmoney'] = 200
            expectinfo['fivemoney'] = 10
            expectinfo['sixmoney'] =  5

            #开奖号码
            expectinfo['opencode'] = data.get('openCode').replace('|', ',')
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return expectinfo
