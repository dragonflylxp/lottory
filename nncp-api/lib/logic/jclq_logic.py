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
from lotterybase import BaseJc, BaseDraw

logger = Log().getLog()


class JclqLogic(BaseJc):
    def __init__(self):
        super(JclqLogic, self).__init__(define.LOTTE_JCLQ_ID)

class JlDraw(BaseDraw):
    def __init__(self):
        super(JlDraw, self).__init__(define.LOTTE_JCLQ_ID)
