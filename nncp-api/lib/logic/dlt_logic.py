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


class DltDraw(BaseDraw):
    def __init__(self):
        super(DltDraw, self).__init__(define.LOTTE_DLT_ID)


class DltExpect(BaseExpect):
    def __init__(self):
        super(DltExpect, self).__init__(define.LOTTE_DLT_ID)



    # def get_expect_info_list(self):
    #     dlt_expect_info = self.dao.find('lottery_dlt_expect_info', {}, sort=[('expect', -1)], rn=10)
    #     return dlt_expect_info

    # def get_current_expect(self):
    #     curr_expect = self.dao.find('lottery_dlt_expect_info', {"isCurrent": "1"})
    #     curr_expect = curr_expect[0] if curr_expect else {}
    #     return curr_expect.get("expect") if curr_expect else ""

    # def get_dlt_opencode_by_expects(self, expects):
    #
    #     opencode = self.dao.find('lottery_dlt_open_info', {"expect": {"$in": expects}}, sort=[('expect', -1)])
    #     return opencode

    # def get_dlt_opencode_by_expect(self, expect):
    #     opencode = self.dao.find_one('lottery_dlt_open_info', {'expect': expect})
    #     return opencode

    # def get_current_expect_info(self):
    #     curr_expect = self.dao.find('lottery_dlt_expect_info', {"isCurrent": "1"})
    #     curr_expect = curr_expect[0] if curr_expect else {}
    #     return curr_expect

    # def get_newest_dlt_opencode(self):
    #     opencode = self.dao.find_one('lottery_dlt_open_info', {"openCode": {"$ne": ""}}, sort=[('expect', -1)])
    #     return opencode
