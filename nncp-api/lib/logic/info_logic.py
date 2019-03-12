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


class InfoLogic(object):
    def __init__(self):
        self.dao = MongoDataModel()

    def get_info_list(self, tabid, pagesize, pageno):
        pn = int(pageno) - 1
        articles = self.dao.find('dongqiudi_articles', {"tabid": int(tabid)}, projection={"body": 0, "_id": 0},
                                 count=True, rn=int(pagesize), pn=pn, sort=[('display_time', -1)])
        return articles

    def get_info_detail(self, tabid, id):
        articles = self.dao.find_one('dongqiudi_articles', {"tabid": int(tabid), "id": int(id)})
        return articles
