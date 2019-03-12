#!/usr/bin/env python
# encoding: utf-8
import MySQLdb
import ujson
import requests
import time
from model.dao import MongoDataModel
from util.tools import Log
from dbpool import db_pool
import traceback
import define

logger = Log().getLog()



class BaseDraw(object):

    def __init__(self, lotid):
        super(BaseDraw, self).__init__()
        TABLE_MAP = {
            3: "lottery_ssq_open_info",
            28: "lottery_dlt_open_info",
            44: "lottery_gx11x5_expect_info",
            46: "lottery_ticket_jczq_match_result",
            47: "lottery_ticket_jclq_match_result"
        }
        self.lotid = lotid
        self.table = TABLE_MAP.get(int(self.lotid), "")
        self.dao = MongoDataModel()

    def get_opencode_by_expects(self, expects):
        """通过期号获取开奖信息
        """

        opencode = self.dao.find(self.table, {"expect": {"$in": expects}}, sort=[('expect', -1)])
        return opencode

    def get_opencode_by_expect(self, expect):
        opencode = self.dao.find_one(self.table, {'expect': expect})
        return opencode

    def get_newest_opencode(self):
        opencode = self.dao.find_one(self.table, {"openCode": {"$ne": ""}}, sort=[('expect', -1)])
        return opencode

    def get_history_opencode_list(self, pn=1, rn=10):
        pn = (pn-1) * 10
        opencode = self.dao.find(self.table, {"openCode": {"$ne": ""}}, sort=[('expect', -1)], pn=pn, rn=rn)
        return opencode

    def get_latest_matchscore(self):
        match = self.dao.find_one(self.table, {}, sort=[('matchId', -1)])
        return match




class BaseExpect(object):

    def __init__(self, lotid):

        TABLE_MAP = {
            3: "lottery_ssq_expect_info",
            28: "lottery_dlt_expect_info",
            44: "lottery_gx11x5_expect_info"
        }

        self.dao = MongoDataModel()
        self.lotid = lotid
        self.table = TABLE_MAP.get(int(self.lotid), "")

    def get_expect_info_list(self, pn=1, rn=10):
        """ 获取期号列表
        :param pn:
        :param rn:
        :return:
        """
        pn = (pn-1)*10
        expect_info = self.dao.find(self.table, {}, sort=[('expect', -1)], rn=rn, pn=pn)

        return expect_info

    def get_current_expect(self):
        """
        获取当前期
        :return:
        """
        curr_expect = self.dao.find_one(self.table, {"isCurrent": "1"})
        return curr_expect.get("expect") if curr_expect else ""

    def get_current_expect_info(self):
        """当前期号信息
        :return:
        """
        curr_expect = self.dao.find_one(self.table, {"isCurrent": "1"})
        return curr_expect


class BaseJc(object):

    def __init__(self, lotid):

        TABLE_MAP = {
            46: "lottery_ticket_jczq_match_info",
            47: "lottery_ticket_jclq_match_info"

        }

        self.dao = MongoDataModel()
        self.lotid = lotid
        self.table = TABLE_MAP.get(int(self.lotid), "")

    def get_jc_on_sale_matches(self):
        """ 获取竞彩对阵
        :param pn:
        :param rn:
        :return:
        """
        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        matches_info = self.dao.find(self.table, {"endTime": {"$gt": curtime}})

        return matches_info

    def get_matches_by_matchid(self, matchid):
        """
            通过matchid 获取对阵数据
        :return:
        """
        matches_info = self.dao.find_one(self.table, {"matchId": matchid})
        return matches_info

    def get_matches_by_matchids(self, matchids):
        """
            通过matchids 批量获取对阵数据
        :return:
        """
        matches_info = self.dao.find(self.table, {"matchId": {"$in": matchids}})
        return matches_info



