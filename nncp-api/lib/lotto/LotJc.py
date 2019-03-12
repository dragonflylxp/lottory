#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: LotJc.py
#
#        Author:
#   Description: ---
#        Create: 2018-04-08 21:43:46
# Last Modified: 2018-04-08 21:43:46
#   Changes Log:

import re
import traceback
import ews
import define
import LotBase
from util.tools import Log

logger = Log().getLog()
dt_dy = re.compile(r'(\d+)\|(\d+)\[(.*)\]')  # 17816|3301[1]
dt_ht = re.compile(r'(\d+)\|(\d+)\|(\d+)\[(.*)\]') # 17817|3302|276[03]
dt_dg = re.compile(r'(\d+)\|(\d+)\|(\d+)\[(.*)\]') # 17816|3301|354[1@2]

lotname_map = {
    '46': '竞足',
    '47': '竞篮'
}

opt_map = {
    '269': ['3', '1', '0'],
    '270': ['0', '1', '2', '3', '4', '5', '6', '7'],
    '271': ['胜其他', '1:0', '2:0', '2:1', '3:0', '3:1', '3:2', '4:0', '4:1', '4:2', '5:0', '5:1', '5:2',
            '平其他', '0:0', '1:1', '2:2', '3:3',
            '负其他', '0:1', '0:2', '1:2', '0:3', '1:3', '2:3', '0:4', '1:4', '2:4', '0:5', '1:5', '2:5'],
    '272': ['3-3', '3-1', '3-0', '1-3', '1-1', '1-0', '0-3', '0-1', '0-0'],
    '354': ['3', '1', '0'],

    '274': ['2', '1'],
    '275': ['2', '1'],
    '276': ['01', '02', '03', '04', '05', '06', '11', '12', '13', '14', '15', '16'],
    '277': ['2', '1']
}

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname = lotname_map.get(str(lotid), '')

    def check_lotto(self, params):
        self.check_switch()

        fileorcode = params.get("fileorcode")
        wtype = params.get("wtype")
        ggtype = params.get("ggtype")
        zhushu = params.get("zhushu")
        beishu = params.get("beishu")
        allmoney = params.get("allmoney")

        self.check_wtype(wtype)
        self.check_ggtype(ggtype)
        self.check_beishu(beishu)
        self.check_fileorcode(fileorcode, wtype)
        self.check_split_tickets(params)


    def check_fileorcode(self, fileorcode, wtype):
        try:
            ccArray = fileorcode.split('/')
            if int(wtype) in [269, 270, 271, 272, 354, 274, 275, 276, 277]:
                for cc in ccArray:
                    m = dt_dy.match(cc)
                    if not m:
                        raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '{}单一玩法格式错误'.format(self.lotname))
                    opts = m.group(3)
                    for opt in opts.split(','):
                        self._check_opt(opt, wtype)

            elif int(wtype) == 58:
                for cc in ccArray:
                    m = dt_dg.match(cc)
                    if not m:
                        raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '{}单关玩法格式错误'.format(self.lotname))
                    wtype = m.group(3)
                    opts = m.group(4)
                    for opt in opts.split(','):
                        opt = opt.split('@')[0]
                        self._check_opt(opt, wtype)

            elif int(wtype) in [312, 313]:
                for cc in ccArray:
                    m = dt_ht.match(cc)
                    if not m:
                        raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '{}混投格式错误'.format(self.lotname))
                    wtype = m.group(3)
                    opts = m.group(4)
                    for opt in opts.split(','):
                        self._check_opt(opt, wtype)
                    if int(wtype) not in [269, 270, 271, 272, 354, 274, 275, 276, 277]:
                        raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '混投玩法中子玩法类型错误')
            else:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的玩法类型')
        except ews.EwsError:
            raise
        except:
            logger.error(traceback.format_exc())
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '投注格式解析错误')

    def _check_opt(self, opt, wtype):
        if opt not in opt_map.get(str(wtype)):
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '{}{}玩法选项{}错误'.format(self.lotname, wtype, opt))
