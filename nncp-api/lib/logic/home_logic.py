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

logger = Log().getLog()


class HomeLogic(object):
    def __init__(self):
        self.dao = MongoDataModel()

    def get_banner_config_info(self):
        banner_config_info = self.dao.find('banner_config_info', {"status": 1}, sort=[('sort', -1)])
        return banner_config_info

    def get_mian_lottery_info(self):
        lottery_config_info = self.dao.find('lottery_config_info', {}, sort=[('sort', -1)])
        return lottery_config_info

    def get_main_focus_matches_info(self):
        matches = self.dao.find_one('focus_matches_info', {"status": 1},  sort=[('endtime', -1)])
        return matches

    def get_operation_config_info(self):
        operation_config = self.dao.find('operation_config_info', {"status": "1"}, sort=[('sort', -1)])
        return operation_config

    def get_bulletin_list(self, pn=1, rn=10):
        pn = (pn -1) * rn
        bulletin_info = self.dao.find('bulletin_info', {"status": "1"}, sort=[('crtime', -1)], pn=pn, rn=rn)
        return bulletin_info
