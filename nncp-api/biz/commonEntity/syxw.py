#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback
from commonEntity import ExpectInfo
from commonEntity import DrawInfo
import define

global logger
logger = Log().getLog()

class SyxwBean(object):

    def __init__(self, lotid=define.LOTTE_GX11X5_ID):
        self.lotid = int(lotid)
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

    def get_syxw_expect_list(self):
        """广西11x5
        """
        try:
            current_expect_info = self.expect_obj.get_current_expect_by_time()
            expect_info = self.draw_obj.get_history_opencode_list()
        except:
            logger.error(traceback.format_exc())
            raise ews.EwsError(ews.STATUS_LOTTERY_ISSUE_ERROR)


        ret = {}
        history_expect = []
        try:
            endtime = current_expect_info.get("stopTime", "")
            # prizepool = str(round(int(prizepool)/10.0 ** 9, 2)) + "亿"
            diff = int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S')) - time.time())
        except:
            logger.info(traceback.format_exc())
            logger.info(current_expect_info)
            diff = 0
        ret.update({
            "status": current_expect_info.get("status", "0"),
            "iscurrent": "1",
            "expect": current_expect_info.get("expect", ""),
            "diff": diff,
            "opencode": current_expect_info.get("openCode", ""),
            "expect": current_expect_info.get("expect", ""),
            "starttime": current_expect_info.get("startTime", ""),
            "stoptime": current_expect_info.get("stopTime", ""),
            "opentime": current_expect_info.get("openTime", "")
        })

        for item in expect_info:
            opencode = item.get("openCode", "")
            if opencode and opencode != "":
                history_expect.append({
                    "opencode": item.get("openCode", ""),
                    "expect": item.get("expect", ""),
                    "starttime": item.get("startTime", ""),
                    "stoptime": item.get("stopTime", ""),
                    "opentime": item.get("openTime", "")
                })
        ret.update({
            "historical_code": history_expect
        })
        return ret

