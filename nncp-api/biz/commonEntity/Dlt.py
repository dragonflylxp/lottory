#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
# from lib.logic.dlt_logic import DltLogic
from commonEntity import ExpectInfo
from commonEntity import DrawInfo
import define
import traceback

global logger
logger = Log().getLog()

class DltBean(object):
    def __init__(self):
        self.lotid = define.LOTTE_DLT_ID
        self.expect_obj = ExpectInfo.get(self.lotid)
        self.draw_obj = DrawInfo.get(self.lotid)

    def get_current_expect(self):
        """获取当前期号
        """
        cur_expect = ""
        try:
            cur_expect = self.expect_obj.get_current_expect()
        except:
            logger.error(traceback.format_exc())
        finally:
            return cur_expect

    def get_dlt_expect_list(self):
        """大乐透期号
        """
        try:
            dlt_expect = self.expect_obj.get_expect_info_list()
        except:
            logger.error(traceback.format_exc())
            raise ews.EwsError(ews.STATUS_LOTTERY_ISSUE_ERROR)

        expects = [expect.get("expect") for expect in dlt_expect]

        opencodes = self.draw_obj.get_opencode_by_expects(expects)

        opencodes = {opencode.get("expect"): opencode for opencode in opencodes}
        ret = {}
        history_expect = []
        for item in dlt_expect:
            iscurrent = item.get("isCurrent", "")
            # opencode = item.get("openCode", "")
            expect = item.get("expect", "")
            opencode = opencodes.get(expect, {})
            flag = False
            if str(iscurrent) == "1":
                prizepool = opencode.get("prizePool", "0")
                prizepool = prizepool.replace(",", "")
                endtime = opencode.get("endTime", "") or item.get("endTime")
                allow_num = int(prizepool)/(5*10 ** 7)
                prizepool = str(round(int(prizepool)/10.0 ** 8, 2)) + "亿" if opencode else "-"
                diff = 0
                if endtime:
                    diff = int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')) - time.time())

                ret.update({
                    "status": item.get("status", "0"),
                    "endtime": endtime,
                    "opencode": opencode.get("openCode", ""),
                    "prizepool": prizepool,
                    "iscurrent": iscurrent,
                    "expect": expect,
                    "opentime": opencode.get("openTime", ""),
                    "diff": diff,
                    "allow_num": allow_num

                })
                continue
            if opencode.get("openCode", "") and opencode.get("openCode", "") != "":
                if not flag:
                    ret.update({
                        "firstprize": opencode.get("firstPrize", ""),
                        "firstnum": opencode.get("firstNum", "")
                    })
                    flag = True

                history_expect.append({
                    "opencode": opencode.get("openCode", ""),
                    "expect": expect
                })
        ret.update({
            "historical_code": history_expect
        })
        return ret

