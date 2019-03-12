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
from commonEntity.syxw import SyxwBean
from util.tools import Log

logger = Log().getLog()
dt_re = re.compile(r'\[D:(.*)\]\[T:(.*)\]\|(.*)')

class Lottery(LotBase.Lottery):

    def __init__(self,lotid):
        super(Lottery, self).__init__(lotid)
        self.lotname='十一选五'

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
            if int(wtype) != 256:
                if fileorcode.find('#') != -1:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '单一玩法投注格式不能包含玩法类型')
            else:
                if fileorcode.find('#') == -1:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '混投玩法投注格式必须包含玩法类型')

            if int(wtype) in [244, 245, 246]:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_zhi(code, wtype)

            elif int(wtype) in [247, 248]:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_zu(code, wtype)

            elif int(wtype) in [249, 250, 251, 252, 253, 254, 255]:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    self._split_code_ren(code, wtype)

            elif int(wtype) == 256:
                fileorcode = fileorcode.split('$')
                for code in fileorcode:
                    code, wtype = code.split('#')
                    if int(wtype) in [244, 245, 246]:
                        self._split_code_zhi(code, wtype)
                    elif int(wtype) in [247, 248]:
                        self._split_code_zu(code, wtype)
                    elif int(wtype) in [249, 250, 251, 252, 253, 254, 255]:
                        self._split_code_ren(code, wtype)
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
        curr_expect = SyxwBean().get_current_expect()
        if expect != curr_expect:
            logger.error("Trade expect error! trade_expect=%s|curr_expect=%s", expect, curr_expect)
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '期号错误')


    def _split_code_zhi(self, code, wtype):
        balls = code.split('|')
        balls = [ball for ball in balls if ball != '-']
        if len(balls) != int(wtype) - 243:
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '直选玩法和号码位数不匹配')
        self._check_number_region(balls)
        self._check_number_repeat(balls)


    def _split_code_zu(self, code, wtype):
        balls = code.split('|')
        balls = [ball for ball in balls if ball != '-']
        self._check_number_region(balls)
        self._check_number_repeat(balls)

    def _split_code_ren(self, code, wtype):
        balls = code.split('|')
        balls = [ball for ball in balls if ball != '-']
        self._check_number_region(balls)
        self._check_number_repeat(balls)


    def _check_number_region(self, balls):
        logger.debug(balls)
        for ball in balls:
            ball = ball.split(',')
            if len(ball) < 1 or len(ball) > 11:
                raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '十一选五号码个数错误')
            for b in ball:
                if int(b) > 11 or int(b) < 1:
                    raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '十一选五数字范围错误')

    def _check_number_repeat(self, balls):
        logger.debug(balls)
        ballnum = [ball.split(',') for ball in balls]
        ballnum = sum(ballnum, [])
        if len(ballnum) > len(set(ballnum)):
            raise ews.EwsError(ews.STATUS_LOTTOCHECK_ERROR, '十一选五选号重复')
