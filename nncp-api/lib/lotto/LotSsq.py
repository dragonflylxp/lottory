#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: LotDlt.py
#
#        Author:
#   Description: ---
#        Create: 2018-03-30 21:24:29
# Last Modified: 2018-03-30 21:24:29
#   Changes Log:

import re
import traceback
import ews
import define
import LotBase
from commonEntity.Ssq import SsqBean
from util.tools import Log

logger = Log().getLog()
#dt_re = re.compile(r'\[D:(.*)\]\[T:(.*)\]\|\[D:(.*)\]\[T:(.*)\]')
dt_re = re.compile(r'\[D:(.*)\]\[T:(.*)\]\|(.*)')

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname='双色球'

    def check_lotto(self, params):
        self.check_switch()

        fileorcode = params.get("fileorcode")
        wtype = params.get("wtype")
        zhushu = params.get("zhushu")
        beishu = params.get("beishu")
        allmoney = params.get("allmoney")
        selecttype = params.get("selecttype")
        expect = params.get("expect")

        if 'singlemoney' in params and 'expecttotal' in params:
            singlemoney = params.get("singlemoney")
            expecttotal = params.get("expecttotal")
            self.check_chasemoney(allmoney, singlemoney, expecttotal)

        self.check_expect(expect)
        self.check_wtype(wtype)
        self.check_beishu(beishu)
        self.check_selecttype(selecttype, fileorcode)
        self.check_fileorcode(fileorcode, wtype)
        self.check_split_tickets(params)

    def check_fileorcode(self, fileorcode, wtype):
        try:
            if int(wtype) != 379:
                if fileorcode.find('#') != -1:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '单一玩法投注格式不能包含玩法类型')
            else:
                if fileorcode.find('#') == -1:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '混投玩法投注格式必须包含玩法类型')

            if int(wtype) == 2:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_ds(code)

            elif int(wtype) == 125:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_dt(code)

            elif int(wtype) == 377:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_fs(code)

            elif int(wtype) == 379:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    code, wtype = code.split('#')
                    if int(wtype) == 2:
                        self._split_code_ds(code)
                    elif int(wtype) == 125:
                        self._split_code_dt(code)
                    elif int(wtype) == 377:
                        self._split_code_fs(code)
                    else:
                        raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '混投玩法中子玩法类型错误')
            else:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '未知的玩法类型')
        except ews.EwsError:
            raise
        except:
            logger.error(traceback.format_exc())
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '投注格式解析错误')


    def check_expect(self, expect):
        curr_expect = SsqBean().get_current_expect()
        if expect != curr_expect:
            logger.error("Trade expect error! trade_expect=%s|curr_expect=%s", expect, curr_expect)
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '期号错误')


    def _split_code_ds(self, code):
        redball, blueball = code.split('|')
        redball = redball.split(',')
        blueball = blueball.split(',')

        if len(redball) != 6:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球红球个数错误')
        if len(blueball) != 1:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球蓝球个数错误')

        for ball in redball:
            if int(ball) > 33 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球红球数字范围错误')
        for ball in blueball:
            if int(ball) > 16 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球蓝球数字范围错误')

    def _split_code_dt(self, code):
        redball, blueball = code.split('|')
        m = dt_re.match(code)
        if not m:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球选号不满足胆拖格式')

        red_d = m.group(1).split(',') if m.group(1) else []
        red_t = m.group(2).split(',') if m.group(2) else []
        blue_d = []
        blue_t = m.group(3).split(',') if m.group(3) else []
        if len(red_d+red_t) > len(set(red_d+red_t)):
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球红球胆拖号码有重复')
        if len(blue_d+blue_t) > len(set(blue_d+blue_t)):
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球蓝球胆拖号码有重复')

        for ball in red_d+red_t:
            if int(ball) > 33 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球红球数字范围错误')
        for ball in blue_d+blue_t:
            if int(ball) > 16 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球蓝球数字范围错误')

    def _split_code_fs(self, code):
        redball, blueball = code.split('|')
        redball = redball.split(',')
        blueball = blueball.split(',')

        if len(redball) < 6 or len(blueball) < 1:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球选号不满足复式格式')

        if len(redball) == 6 and len(blueball) == 1:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球选号不满足复式格式')

        for ball in redball:
            if int(ball) > 33 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球红球数字范围错误')
        for ball in blueball:
            if int(ball) > 16 or int(ball) < 1:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '双色球蓝球数字范围错误')
