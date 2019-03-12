#!/usr/bin/env python
# encoding: utf-8
import calendar
import datetime
import ews
import time
from util.tools import Log
import traceback
from logic.home_logic import HomeLogic
global logger
import define
from commonEntity import ExpectInfo
from commonEntity import DrawInfo

logger = Log().getLog()


class LotteBean(object):

    def __init__(self):
        self.dlt_draw_obj = DrawInfo.get(define.LOTTE_DLT_ID)
        self.ssq_draw_obj = DrawInfo.get(define.LOTTE_SSQ_ID)
        self.gx11x5_draw_obj = DrawInfo.get(define.LOTTE_GX11X5_ID)
        self.jz_draw_obj = DrawInfo.get(define.LOTTE_JCZQ_ID)
        self.jl_draw_obj = DrawInfo.get(define.LOTTE_JCLQ_ID)


    def get_lotte_draw_list(self):
        ssq_opencode = self.ssq_draw_obj.get_newest_opencode()
        dlt_opencode = self.dlt_draw_obj.get_newest_opencode()
        gx11x5_opencode = self.gx11x5_draw_obj.get_newest_opencode()
        jz_matchscore = self.jz_draw_obj.get_latest_matchscore()
        jl_matchscore = self.jl_draw_obj.get_latest_matchscore()

        ret = []
        info = self.deal_number_lotte_format(define.LOTTE_DLT_ID, dlt_opencode)
        if info:
            ret.append(info)
        info = self.deal_number_lotte_format(define.LOTTE_SSQ_ID, ssq_opencode)
        if info:
            ret.append(info)
        info = self.deal_number_lotte_format(define.LOTTE_GX11X5_ID, gx11x5_opencode)
        if info:
            ret.append(info)
        info = self.deal_jc_lotte_format(define.LOTTE_JCZQ_ID, jz_matchscore)
        if info:
            ret.append(info)
        info = self.deal_jc_lotte_format(define.LOTTE_JCLQ_ID, jl_matchscore)
        if info:
            ret.append(info)
        return ret

    def deal_jc_lotte_format(self, lotid, info):
        if not info:
            return
        info.update({
            "lotid": lotid,
            "lotname": define.LOTTE_NAME.get(lotid, ""),
            "updateTime": info["updateTime"].strftime("%Y-%m-%d %H:%M:%S")
            })
        return info

    def deal_number_lotte_format(self, lotid, info):
        if not info:
            return
        opentime = info.get("openTime", "")[:10]
        if not opentime:
            return
        try:
            _opentime = time.strptime(opentime, "%Y-%m-%d")
            weekday = calendar.weekday(_opentime.tm_year, _opentime.tm_mon, _opentime.tm_mday)
        except:
            logger.error(traceback.format_exc())
            weekday = 8
        ret = {
            "lotid": lotid,
            "lotname": define.LOTTE_NAME.get(lotid, ""),
            "issue": info.get("expect", ""),
            "opentime": opentime,
            "weeknum": define.WEEK_NUM.get(weekday, ""),
            "opencode": info.get("openCode", "")
        }
        return ret

class DrawBean():
    def __init__(self, lotid):
        self.lotid = lotid
        self.draw_obj = DrawInfo.get(lotid)

    def get_lotte_history_opencode(self, pageno, pagesize):
        opencode_list = self.draw_obj.get_history_opencode_list(int(pageno), int(pagesize))

        ret = []

        for info in opencode_list:
            if info:
                ret.append(self.deal_number_lotte_format(self.lotid, info))

        return ret

    def deal_number_lotte_format(self, lotid, info):
        opentime = info.get("openTime", "")[:10]
        _opentime = time.strptime(opentime, "%Y-%m-%d")
        weekday = calendar.weekday(_opentime.tm_year, _opentime.tm_mon, _opentime.tm_mday)

        ret = {
            "lotid": lotid,
            "lotname": define.LOTTE_NAME.get(lotid, ""),
            "issue": info.get("expect", ""),
            "opentime": opentime,
            "weeknum": define.WEEK_NUM.get(weekday, ""),
            "opencode": info.get("openCode", "")

        }
        return ret

    def lotte_draw_detail(self, expect):
        expect_info = self.draw_obj.get_opencode_by_expect(expect)
        ret = {}
        if self.lotid == define.LOTTE_DLT_ID:
            ret = {
                "sale_money": expect_info.get("totalSaleMoney", ""),
                "prize_pool": expect_info.get("prizePool", ""),
                "first_prize": expect_info.get("firstPrize", ""),
                "first_num": expect_info.get("firstNum", ""),
                "first_add_prize": expect_info.get("firstAddPrize", ""),
                "second_add_prize": expect_info.get("secondAddPrize", ""),
                "second_num": expect_info.get("secondNum", ""),
                "second_prize": expect_info.get("secondPrize", ""),
                "second_add_num": expect_info.get("secondAddNum", ""),
                "third_add_prize": expect_info.get("thirdAddPrize", ""),
                "third_num": expect_info.get("thirdNum", ""),
                "third_prize": expect_info.get("thirdPrize", ""),
                "third_add_num": expect_info.get("thirdAddNum", ""),
                "fourth_add_prize": expect_info.get("fourthAddPrize", ""),
                "fourth_num": expect_info.get("fourthNum", ""),
                "fourth_prize": expect_info.get("fourthPrize", ""),
                "fourth_add_num": expect_info.get("fourthAddNum", ""),
                "fifth_add_prize": expect_info.get("fifthAddPrize", ""),
                "fifth_num": expect_info.get("fifthNum", ""),
                "fifth_prize": expect_info.get("fifthPrize", ""),
                "fifth_add_num": expect_info.get("fifthAddNum", ""),
                "sixth_rize": expect_info.get("sixthPrize", ""),
                "sixth_num": expect_info.get("sixthNum", "")
            }
        elif self.lotid == define.LOTTE_SSQ_ID:
            ret = {
                "sale_money": expect_info.get("totalSaleMoney", ""),
                "prize_pool": expect_info.get("prizePool", ""),
                "first_prize": expect_info.get("firstPrize", ""),
                "first_num": expect_info.get("firstNum", ""),
                "second_num": expect_info.get("secondNum", ""),
                "second_prize": expect_info.get("secondPrize", ""),
                "third_num": expect_info.get("thirdNum", ""),
                "third_prize": expect_info.get("thirdPrize", ""),
                "fourth_num": expect_info.get("fourthNum", ""),
                "fourth_prize": expect_info.get("fourthPrize", ""),
                "fifth_num": expect_info.get("fifthNum", ""),
                "fifth_prize": expect_info.get("fifthPrize", ""),

            }

        return ret
