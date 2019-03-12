#!/usr/bin/env python
# encoding: utf-8
import calendar
import datetime
import ews
import time
from util.tools import Log
import traceback

from logic.home_logic import HomeLogic
from commonEntity import ExpectInfo
from commonEntity import DrawInfo
import define
from commonEntity import JcInfo

global logger
logger = Log().getLog()


class HomeBean(object):
    def __init__(self):
        self.gx11x5_expect_obj = ExpectInfo.get(define.LOTTE_GX11X5_ID)
        self.gx11x5_draw_obj = DrawInfo.get(define.LOTTE_GX11X5_ID)

        self.ssq_expect_obj = ExpectInfo.get(define.LOTTE_SSQ_ID)
        self.ssq_draw_obj = DrawInfo.get(define.LOTTE_SSQ_ID)

        self.dlt_expect_obj = ExpectInfo.get(define.LOTTE_DLT_ID)
        self.dlt_draw_obj = DrawInfo.get(define.LOTTE_DLT_ID)
        self.jc_obj = JcInfo.get(define.LOTTE_JCZQ_ID)

    def get_banner_config(self, platform):
        """banner config
        """
        banner_configs = []
        try:
            banner_configs = HomeLogic().get_banner_config_info()
        except:
            logger.error(traceback.format_exc())
            raise  # todo

        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        banner = []
        for conf in banner_configs:
            _platform = conf.get("platform", [])
            starttime = conf.get("starttime", "")
            endtime = conf.get("endtime", "")

            if platform in _platform and cur_time >= starttime and cur_time <= endtime:
                banner.append({
                    "image": conf.get("img_url", ""),
                    "gourl": conf.get("link_url", "")
                })

        return banner

    def get_lottery_config(self):
        """
        :return:
        """
        lottery_config = []
        try:
            lottery_config = HomeLogic().get_mian_lottery_info()
        except:
            logger.error(traceback.format_exc())
            raise  # todo

        lotteryinfo = []
        for lottery in lottery_config:
            lotteryinfo.append({
                "lotid": lottery.get("lotid", ""),
                "lotname": lottery.get("lotname", ""),
                "image": lottery.get("img_url", ""),
                "gourl": lottery.get("link_url", ""),
                "status": int(lottery.get("status", "0")),
                "corner_mark": lottery.get("corner_mark", ""),
                "state": int(lottery.get("state", "0"))
            })
        return lotteryinfo

    def get_mian_lucky_bet(self):

        today = datetime.datetime.today()
        weekday = calendar.weekday(today.year, today.month, today.day)
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        ret = {}
        if weekday in ["1", "3", "5", "6"]:
            current_info = self.dlt_expect_obj.get_current_expect_info()
            expect = current_info.get("expect")
            endtime = current_info.get("endtime")
            if cur_time < endtime:
                ret = self.get_quick_dlt_config(expect)
            else:
                current_info = self.ssq_expect_obj.get_current_expect_info()
                expect = current_info.get("expect")
                ret = self.get_quick_ssq_config(expect)

        else:
            current_info = self.ssq_expect_obj.get_current_expect_info()
            expect = current_info.get("expect")
            endtime = current_info.get("endtime")

            if cur_time < endtime:
                ret = self.get_quick_ssq_config(expect)
            else:
                current_info = self.dlt_expect_obj.get_current_expect_info()
                expect = current_info.get("expect")
                ret = self.get_quick_dlt_config(expect)

        return ret

    def get_quick_dlt_config(self, expect):

        opencode_info = self.dlt_draw_obj.get_opencode_by_expect(expect) or {}
        prizepool = opencode_info.get("prizePool", "0")
        prizepool = prizepool.replace(",", "")
        opentime = opencode_info.get("openTime", "")
        prizepool = str(round(int(prizepool) / 10.0 ** 8, 1)) + "亿"

        ret = {
            "lotid": "28",
            "issue": expect,
            "playid": "1",
            "title": "幸运号码",
            "subtitle": "【大乐透】奖池{pool}".format(pool=prizepool),
            "desc": "第{issue}期 {opentime}开奖".format(issue=expect, opentime=opentime[5:]),
            "prizepool": prizepool
        }
        return ret

    def get_quick_ssq_config(self, expect):
        opencode_info = self.ssq_draw_obj.get_opencode_by_expect(expect) or {}
        prizepool = opencode_info.get("prizePool", "0")
        prizepool = prizepool.replace(",", "")
        opentime = opencode_info.get("openTime", "")
        prizepool = str(round(int(prizepool) / 10.0 ** 8, 1)) + "亿"

        ret = {
            "lotid": "3",
            "issue": expect,
            "playid": "1",
            "title": "幸运号码",
            "subtitle": "【双色球】奖池{pool}".format(pool=prizepool),
            "desc": "第{issue}期 {opentime}开奖".format(issue=expect, opentime=opentime[5:-3]),
            "prizepool": prizepool

        }
        return ret

    def get_jczq_matches(self):
        matches = HomeLogic().get_main_focus_matches_info()

        matchid = matches.get("matchId", "")

        dym_match = self.jc_obj.get_matches_by_matchid(matchid) or {}
        status = dym_match.get("status")
        issingle = dym_match.get("isSingle")
        endtime = dym_match.get("endTime")
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # endtime =
        ret = {}
        if str(status) == "1" and str(issingle) == "1" and cur_time < endtime:
            endtime_str = ""

            matchdate = dym_match.get("matchDate")
            matchtime = dym_match.get("matchTime")

            odds = dym_match.get("oddsInfo", {}).get("spf", {}).get("odds", {})

            ret = {
                "lotid": "46",
                "playid": "1",
                "matchid": matchid,
                "league_name": dym_match.get("league", ""),
                "home": dym_match.get("home", ""),
                "away": dym_match.get("visiting"),
                "matchnum": dym_match.get("matchNum"),
                "endtime": endtime[5:-3],
                "win_odds": odds.get("win", ''),
                "draw_odds": odds.get("draw", ''),
                "lost_odds": odds.get("lost", ""),
                "matchtime": matchdate + " " + matchtime,
                "matchcode": dym_match.get("matchCode", ''),
                "homeLogo": dym_match.get("homeLogo", ""),
                "homeId": dym_match.get("homeId"),
                "visitingId": dym_match.get("visitingId"),
                "visitingLogo": dym_match.get("visitingLogo")
            }
        return ret

    def get_operation_config(self, platform):
        operation_config = HomeLogic().get_operation_config_info()

        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        ret = []
        for conf in operation_config:
            _platform = conf.get("platform", [])
            if platform in _platform:
                ret.append({
                    "image": conf.get("img_url", ""),
                    "gourl": conf.get("link_url", "")
                })
        return ret

    def main_info(self, platform):

        banner_config = self.get_banner_config(platform)
        lottery_config = self.get_lottery_config()

        lucky_bet = self.get_mian_lucky_bet()
        jczq_matches = self.get_jczq_matches()
        operation_config = self.get_operation_config(platform)

        ret = {
            "banner": banner_config,
            "quick_buy_number": lucky_bet,
            "quick_buy_sport": jczq_matches,
            "operation_config": operation_config,
            "lotto": lottery_config
        }

        return ret

    def bulletin_list(self, platform):
        # ret = [
        #     {
        #         "title": "公告1",
        #         "url": "https://www.baidu.com/"
        #     },
        #     {
        #         "title": "公告2",
        #         "url": "https://www.baidu.com/"
        #     },
        #     {
        #         "title": "公告3",
        #         "url": "https://www.baidu.com/"
        #     }
        # ]

        bulletin_list = HomeLogic().get_bulletin_list()
        ret = []
        for bulletin in bulletin_list:
            ret.append({
                "title": bulletin.get("title"),
                "url": bulletin.get("url", "")
            })
        return ret


    def main_info_pc(self, platform):
        banner_config = self.get_banner_config(platform)
        jczq_matches = self.get_jczq_matches()

        current_info = self.dlt_expect_obj.get_current_expect_info()
        expect = current_info.get("expect")
        dlt_info = self.get_quick_dlt_config(expect)

        current_info = self.ssq_expect_obj.get_current_expect_info()
        expect = current_info.get("expect")
        ssq_info = self.get_quick_ssq_config(expect)

        bulletin = self.bulletin_list(platform)
        newst_opencode = self.newst_opencode_info()

        ret = {
            "banner": banner_config,
            "quick_buy_dlt": dlt_info,
            "quick_buy_ssq": ssq_info,
            "quick_buy_jcdg": jczq_matches,
            "bulletin": bulletin,
            "ssq_prizepool": ssq_info.get("prizepool"),
            "dlt_prizepool": dlt_info.get("prizepool"),
            "newst_opencode": newst_opencode

        }

        return ret

    def newst_opencode_info(self):
        ret = []
        dlt_opencode = self.newest_dlt_opencode()
        ssq_opencode = self.newst_ssq_opencode()
        gx11x5_opencode = self.newst_gx11x5_opencode()
        ret.append(dlt_opencode)
        ret.append(ssq_opencode)
        ret.append(gx11x5_opencode)
        return ret

    def newest_dlt_opencode(self):
        dlt_opencode_info = self.dlt_draw_obj.get_newest_opencode()
        dlt_opencode = dlt_opencode_info.get("openCode", "")

        ret = {
            "lotname": "大乐透",
            "lotid": "28",
            "issue": dlt_opencode_info.get("expect", ""),
            "opentime": dlt_opencode_info.get("openTime", "")[:10],
            "opencode": dlt_opencode
        }
        return ret

    def newst_ssq_opencode(self):
        ssq_opencode_info = self.ssq_draw_obj.get_newest_opencode()
        ssq_opencode = ssq_opencode_info.get("openCode", "")

        ret = {
            "lotname": "双色球",
            "lotid": "3",
            "issue": ssq_opencode_info.get("expect", ""),
            "opentime": ssq_opencode_info.get("openTime", "")[:10],
            "opencode": ssq_opencode
        }
        return ret

    def newst_gx11x5_opencode(self):
        gx11x5_opencode_info = self.gx11x5_draw_obj.get_newest_opencode()
        gx11x5_opencode = gx11x5_opencode_info.get("openCode", "")

        ret = {
            "lotname": "广西11选5",
            "lotid": "44",
            "issue": gx11x5_opencode_info.get("expect", ""),
            "opentime": gx11x5_opencode_info.get("openTime", "")[:10],
            "opencode": gx11x5_opencode
        }
        return ret
