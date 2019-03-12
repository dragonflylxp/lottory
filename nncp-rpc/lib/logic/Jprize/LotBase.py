# coding:utf-8
# File: LotBase.py
# Auth: lixp(@500wan.com)
# Date: 2015-10-20 15:18:48
# Desc:

import datetime
import traceback
from decimal import *
from logic import Ticket
from util.tools import RequestXml
from util.tools import Log

logger = Log().getLog()


class Lottery(object):
    def __init__(self, lotid):
        self.lotid = lotid

    def jprize(self):
        pass

    def getExpect(self):
        # 获取开奖期号、开奖号码、奖金
        expectinfo = {}
        expect = ""

        # 胜负彩开奖信息
        if self.lotid == '1':
            # 期号
            try:
                url = ""#define_data.url_xml_conf.get("URL_SFC_EXPECT")
                dom = RequestXml.get_xml_dom(url)
                node_list = dom.findall('row')
                for node in node_list:
                    if node.get('active') == '1':
                        expect = str(int(node.get('expect')) - 1)
                        break
            except Exception as e:
                logger.error(traceback.format_exc())
                return None

            if not expect:
                return None
            expectinfo['expect'] = expect

            # 开奖号码、奖金
            try:
                url = ""#define_data.url_xml_conf.get("URL_SFC_KAIJIANG") % int(expect)
                dom = RequestXml.get_xml_dom(url)
                data = dict((row.tag, row.text) for row in dom.iterchildren())
                expectinfo['pre_onemoney'] = Decimal(data.get('BaseMoney1'))
                expectinfo['pre_twomoney'] = Decimal(data.get('BaseMoney2'))
                expectinfo['onemoney'] = expectinfo['pre_onemoney'] * Decimal('0.8')
                expectinfo['twomoney'] = expectinfo['pre_twomoney'] * Decimal('0.8')
                matchresult = dom.find('MatchTeams').getchildren()
                expectinfo['opencode'] = ','.join([mr.attrib.get('Result') for mr in matchresult])
            except Exception as e:
                logger.error(traceback.format_exc())
                return None
            return expectinfo

        # 任九开奖信息
        if self.lotid == '61':
            # 期号
            try:
                url = define_data.url_xml_conf.get("URL_SFC_EXPECT")
                dom = RequestXml.get_xml_dom(url)
                node_list = dom.findall('row')
                for node in node_list:
                    if node.get('active') == '1':
                        expect = str(int(node.get('expect')) - 1)
                        break
            except Exception as e:
                logger.error(traceback.format_exc())
                return None

            if not expect:
                return None
            expectinfo['expect'] = expect

            # 开奖号码、奖金
            try:
                url = define_data.url_xml_conf.get("URL_RJ_KAIJIANG") % int(expect)
                dom = RequestXml.get_xml_dom(url)
                data = dict((row.tag, row.text) for row in dom.iterchildren())
                expectinfo['pre_onemoney'] = Decimal(data.get('BaseMoney1'))
                expectinfo['onemoney'] = expectinfo['pre_onemoney'] * Decimal('0.8')
                matchresult = dom.find('MatchTeams').getchildren()
                expectinfo['opencode'] = ','.join([mr.attrib.get('Result') for mr in matchresult])
            except Exception as e:
                logger.error(traceback.format_exc())
                return None
            return expectinfo

        # dlt获取取1~6等奖奖金
        if self.lotid == '28':
            # 体彩开奖信息
            try:
                dom = RequestXml.get_xml_dom(define_data.url_xml_conf['URL_DLT_ACTIVE_EXPECT'])
                for row in dom.iterchildren():
                    d = dict((k, v) for k, v in row.items())
                    if d.get('lotid', '0') == self.lotid:
                        endtime = d.get('endtime').split(' ')[0].split('-')
                        endtime = datetime.date(int(endtime[0]), int(endtime[1]), int(endtime[2]))
                        if endtime > datetime.date.today():  # 切换到新一期之后开始计算
                            expect = str(int(d.get('expect')) - 1)
                        break
            except Exception as e:
                logger.error(traceback.format_exc())
                return None

            if not expect:
                return None
            expectinfo['expect'] = expect
            try:
                dom = RequestXml.get_xml_dom(define_data.url_xml_conf['URL_DLT_KAIJIANG'] % ('dlt', int(expect)))
                data = dict((row.tag, row.text) for row in dom.iterchildren())
                expectinfo['pre_onemoney'] = Decimal(data.get('BaseMoney1'))
                expectinfo['pre_twomoney'] = Decimal(data.get('BaseMoney2'))
                expectinfo['pre_threemoney'] = Decimal(data.get('BaseMoney3'))
                expectinfo['onemoney'] = expectinfo['pre_onemoney'] * Decimal('0.8')
                expectinfo['twomoney'] = expectinfo['pre_twomoney'] * Decimal('0.8')
                expectinfo['threemoney'] = expectinfo['pre_threemoney'] * Decimal('0.8')
                expectinfo['fourmoney'] = Decimal(data.get('BaseMoney4'))
                expectinfo['fivemoney'] = Decimal(data.get('BaseMoney5'))
                expectinfo['sixmoney'] = Decimal(data.get('BaseMoney6'))

                expectinfo['pre_jzonemoney'] = Decimal(data.get('BaseMoney1')) + Decimal(data.get('AdditionMoney1'))
                expectinfo['pre_jztwomoney'] = Decimal(data.get('BaseMoney2')) + Decimal(data.get('AdditionMoney2'))
                expectinfo['pre_jzthreemoney'] = Decimal(data.get('BaseMoney3')) + Decimal(data.get('AdditionMoney3'))
                expectinfo['jzonemoney'] = expectinfo['pre_jzonemoney'] * Decimal('0.8')
                expectinfo['jztwomoney'] = expectinfo['pre_jztwomoney'] * Decimal('0.8')
                expectinfo['jzthreemoney'] = expectinfo['pre_jzthreemoney'] * Decimal('0.8')
                expectinfo['jzfourmoney'] = Decimal(data.get('BaseMoney4')) + Decimal(data.get('AdditionMoney4'))
                expectinfo['jzfivemoney'] = Decimal(data.get('BaseMoney5')) + Decimal(data.get('AdditionMoney5'))
                expectinfo['jzsixmoney'] = Decimal(data.get('BaseMoney6')) + Decimal(data.get('AdditionMoney6'))

                expectinfo['opencode'] = ','.join([data.get('ForeResult'), data.get('BackResult')])

            except Exception as e:
                logger.error(traceback.format_exc())
                return None

        #qxc获取取1~6等奖奖金
        if self.lotid == '4':
            # http://tc.500boss.com/static/info/prizeinfo/xml/qx/14019.xml
            try:
                dom = RequestXml.get_xml_dom(define_data.url_xml_conf['URL_DLT_KAIJIANG'] % ('qx', int(expect)))
                expectinfo = {'expect': '15001',
                              'opencode': '1,2,3,4,5,6,7',
                              'pre_onemoney': 100000,
                              'pre_twomoney': 10000,
                              'onemoney': 80000,
                              'twomoney': 10000,
                              'threemoney': 1800,
                              'fourmoney': 300,
                              'fivemoney': 20,
                              'sixmoney': 5}
            except Exception as e:
                logger.error(traceback.format_exc())
                return None

        # pls固定奖金
        if self.lotid == '5':
            pass

        # plw固定奖金
        if self.lotid == '60':
            # http://tc.500boss.com/static/info/prizeinfo/xml/plw/14017.xml
            try:
                dom = RequestXml.get_xml_dom(define_data.url_xml_conf['URL_DLT_KAIJIANG'] % ('plw', int(expect)))
            except Exception as e:
                logger.error(traceback.format_exc())
                return None

        return expectinfo

    def getTicketsbyExpect(self, expect):
        obj_ticket = Ticket.get(int(self.lotid))
        return obj_ticket.get_tickets_by_expect(expect)

    def updateJprizeStatus(self, results):
        obj_ticket = Ticket.get(int(self.lotid))
        try:
            obj_ticket.update_jprize_status(results)
        except:
            logger.error(traceback.format_exc())
            raise
