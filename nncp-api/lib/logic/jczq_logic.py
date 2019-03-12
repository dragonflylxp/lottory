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


class JczqLogic(BaseJc):
    def __init__(self):
        super(JczqLogic, self).__init__(define.LOTTE_JCZQ_ID)

class JzDraw(BaseDraw):
    def __init__(self):
        super(JzDraw, self).__init__(define.LOTTE_JCZQ_ID)
