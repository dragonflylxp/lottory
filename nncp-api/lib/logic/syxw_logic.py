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
from lotterybase import BaseDraw, BaseExpect

logger = Log().getLog()



class SyxwDraw(BaseDraw):
    def __init__(self, lotid):
        super(SyxwDraw, self).__init__(lotid)


class SyxwExpect(BaseExpect):
    def __init__(self, lotid):
        super(SyxwExpect, self).__init__(lotid)

    def get_current_expect_by_time(self):
        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        logger.info(curtime)
        expect_info = self.dao.find_one(self.table, {"startTime": {"$lte": curtime}, "stopTime": {"$gt": curtime}},
                                        sort=[('expect', -1)], rn=10)
        return expect_info

    def get_current_expect(self):
        curr_expect = self.get_current_expect_by_time()
        logger.debug(curr_expect)
        return curr_expect.get("expect") if curr_expect else ""


# class Gx11x5Logic(object):
#     def __init__(self):
#         self.dao = MongoDataModel()

    # def get_expect_info_list(self):
    #     expect_info = self.dao.find('lottery_gx11x5_expect_info', {}, sort=[('expect', -1)], rn=10)
    #
    #     return expect_info

    # def get_current_expect_by_time(self):
    #     curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #     expect_info = self.dao.find_one('lottery_gx11x5_expect_info', {"startTime": {"$lt": curtime}, "stopTime": {"$gt": curtime}},
    #                                 sort=[('expect', -1)], rn=10)
    #
    #     return expect_info
    #
    # def get_opencode_expect_info_list(self):
    #     expect_info = self.dao.find('lottery_gx11x5_expect_info', {"openCode": {"$ne": ""}}, sort=[('expect', -1)], rn=10)
    #
    #     return expect_info

    # def get_gx11x5_opencode_by_expect(self, expect):
    #     expect_info = self.dao.find_one('lottery_gx11x5_expect_info', {'expect': expect})
    #     return expect_info
    #
    # def get_newest_gx11x5_opencode(self):
    #     opencode = self.dao.find_one('lottery_gx11x5_expect_info', {"openCode": {"$ne": ""}}, sort=[('expect', -1)])
    #     return opencode
