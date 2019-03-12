#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback
from commonEntity import JcInfo
from commonEntity.JcTool import JcBase
import define

global logger
logger = Log().getLog()

class JczqBean(JcBase):
    def __init__(self):
        self.jc_obj = JcInfo.get(define.LOTTE_JCZQ_ID)

    def get_on_sale_matches(self, platform="android"):
        matches = self.jc_obj.get_jc_on_sale_matches()
        matches = self.deal_jc_matches(matches)
        return matches

    def get_matches_by_matchid(self, matchid):
        """
        通过mathid 获取matches
        :param matchid:
        :return:
        """
        matches = self.jc_obj.get_matches_by_matchid(matchid)
        matches = self.deal_jc_matches(matches)
        return matches

    def get_matches_by_matchids(self, matchids):
        """
        通过mathid 获取matches
        :param matchid:
        :return:
        """
        matches = self.jc_obj.get_matches_by_matchids(matchids)
        matches = self.deal_jc_matches(matches)
        return matches

    def get_firsttime_and_lasttime(self, fileorcode):
        """
        :param filecode:
        :return:
        """
        ccArray = fileorcode.split('/')
        firstfid = ccArray[0].split("|")[0]
        lastfid = ccArray[-1].split("|")[0]

        matches = self.jc_obj.get_matches_by_matchids([firstfid, lastfid])
        firsttime = ""
        lasttime = ""
        for match in matches:
            matchid = match.get("matchId", "")
            endtime = match.get("endTime", "")
            if str(matchid) == firstfid:
                firsttime = endtime
            if str(matchid) == lastfid:
                lasttime = endtime
        return firsttime, lasttime
