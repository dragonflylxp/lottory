#!/usr/bin/env python
# encoding: utf-8
import MySQLdb
import ujson
import requests
from model.dao import MongoDataModel
from util.tools import Log
from dbpool import db_pool
import traceback
import define
from lotterybase import BaseDraw, BaseExpect

logger = Log().getLog()


class SsqExpect(BaseExpect):
    def __init__(self, lotid=define.LOTTE_SSQ_ID):
        super(SsqExpect, self).__init__(lotid)


class SsqDraw(BaseDraw):
    def __init__(self, lotid=define.LOTTE_SSQ_ID):
        super(SsqDraw, self).__init__(lotid)


#
# class SsqLogic(object):
#     def __init__(self):
#         self.dao = MongoDataModel()
#
#     def get_expect_info_list(self):
#         ssq_expect_info = self.dao.find('lottery_ssq_expect_info', {}, sort=[('expect', -1)], rn=10)
#
#         return ssq_expect_info
#
#     def get_current_expect(self):
#         curr_expect = self.dao.find('lottery_ssq_expect_info', {"isCurrent": "1"})
#         curr_expect = curr_expect[0] if curr_expect else {}
#         return curr_expect.get("expect") if curr_expect else ""
#
#     def get_ssq_opencode_by_expect(self, expect):
#         opencode = self.dao.find('lottery_ssq_open_info', {'expect': expect}, sort=[('expect', -1)])
#         opencode = opencode[0] if opencode else {}
#         return opencode
#
#     def get_current_expect_info(self):
#         curr_expect = self.dao.find('lottery_ssq_expect_info', {"isCurrent": "1"})
#         curr_expect = curr_expect[0] if curr_expect else {}
#         return curr_expect
#
#     def get_newest_ssq_opencode(self):
#         opencode = self.dao.find_one('lottery_ssq_open_info', {"openCode": {"$ne": ""}}, sort=[('expect', -1)])
#         return opencode
