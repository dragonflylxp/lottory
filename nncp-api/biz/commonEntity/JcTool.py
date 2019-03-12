#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback

global logger
logger = Log().getLog()

class JcBase(object):

    def deal_jc_matches(self, infos):

        ret = []
        for info in infos:
            oddsStatus = info.get("oddsStatus", -1)
            if oddsStatus == "1":
                ret.append(info)

            odds = []
            # for k, v in oddsInfo.items():
            #     v.update({
            #         "playname": k
            #     })
            #     odds.append(v)
            #
            # ret.append({
            #     "matchid": info.get("matchId", ""),
            #     "league_name": info.get("league", ""),
            #     "home": info.get("home", ""),
            #     "away": info.get("visiting", ""),
            #     "matchnum": info.get("matchNum", ""),
            #     "endtime": info.get("endTime", ""),
            #     "matchtime": info.get("matchDate", "") + " " + info.get("matchTime", ""),
            #     "rangfen": info.get("rangfen", ""),
            #     "isSingle": info.get("isSingle", ""),
            #     "presetscore": info.get("presetScore", ""),
            #     "status": info.get("status", ""),
            #     "rangqiu": info.get("rangQiu", ""),
            #     "matchcode": info.get("matchCode", ""),
            #     "oddsinfo": oddsInfo,
            #     "score": info.get("score", ""),
            #     "halfScore": info.get("halfScore", "")
            #
            # })
        return ret

    def split_code(self, lotid, code):
        """
        拆票
        :param lotid:
        :param code:
        :return:
        """
        pass

