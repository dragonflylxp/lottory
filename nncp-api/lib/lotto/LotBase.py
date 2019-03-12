#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: LotBase.py
#
#        Author:
#   Description: ---
#        Create: 2018-03-30 21:26:23
# Last Modified: 2018-03-30 21:26:23
#   Changes Log:


import traceback
import ews
import define
from cbrpc import get_rpc_conn
from model.dao import MongoDataModel
from util.tools import Log

logger = Log().getLog()


class Lottery(object):
    def __init__(self, lotid):
        self.lotid = lotid

    def check_switch(self):
        config = MongoDataModel().find_one('lottery_config_info', {'lotid': str(self.lotid)})
        if int(config.get('status', -1)) == -1:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '暂停销售')

    def check_fileorcode(self, params):
        raise NotImplementedError

    def check_beishu(self, beishu):
        config = MongoDataModel().find_one('lottery_config_info', {'lotid': str(self.lotid)})
        beishulimit = int(config.get('beishulimit', -1))
        if int(beishu) < beishulimit:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '体彩中心通知【世界杯期间每单投注倍数不得小于{}倍】'.format(beishulimit))

    def check_wtype(self, wtype):
        try:
            if int(wtype) not in define.LOTTE_WTYPE_MAP.get(int(self.lotid)):
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的玩法类型')
        except:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的玩法类型')

    def check_ggtype(self, ggtype):
        try:
            ggtypes = ggtype.split(',')
            for ggtype in ggtypes:
                if int(ggtype) < 1 or int(ggtype) > 58:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的过关类型')
        except:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的过关类型')

    def check_selecttype(self, selecttype, fileorcode):
        try:
            if len(selecttype.split(',')) != len(fileorcode.split('$')):
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '机选手选个数与投注内容不匹配')
        except:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '机选手选个数与投注内容不匹配')

    def check_chasemoney(self, allmoney, singlemoney, expecttotal):
        try:
            if int(allmoney) != int(singlemoney) * int(expecttotal):
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '追号金额错误')
        except:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '追号金额错误')

    def check_split_tickets(self, params):
        try:
            #调用拆票服务
            with get_rpc_conn("ticket") as proxy:
                try:
                    params.update({'checksplit':True})
                    tickets = proxy.call("split_tickets", params)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '投注金额错误')
        except:
            logger.error(traceback.format_exc())
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '投注金额错误')
