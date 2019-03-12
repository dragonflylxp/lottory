#!/usr/bin/env python
# encoding: utf-8
import calendar
import datetime
import ews
import time

import math
from util.tools import Log
import traceback
from logic.info_logic import InfoLogic
global logger
import define

logger = Log().getLog()

tabs = {1: '头条', 3: '英超', 55: '深度', 56: '中超',}

class Infobean(object):

    def __init__(self):
        pass

    def get_info_list(self, tabid, pageno, pagesize):
        info_list = InfoLogic().get_info_list(tabid, pagesize, pageno)
        articles = []
        for article in info_list[:-1]:
            articles.append({
                "visit_total": article.get("visit_total", ""),
                "display_time": article.get("display_time", ""),
                "tabid": article.get("tabid", ""),
                "user_id": article.get("user_id", ""),
                "description": article.get("description", "") if article.get("description", "") else "",
                "title": article.get("title", ""),
                "comments_total": article.get("comments_total", ""),
                "thumb": article.get("thumb", ""),
                "official_account": article.get("official_account", ""),
                "writer": article.get("writer", ""),
                "web_url": article.get("web_url", ""),
                "type": article.get("type", ""),
                "id": article.get("id", "")
            })
        count = info_list[-1] if info_list and info_list[-1] else 0
        ret = {
            "cur_page": pageno,
            "tabid": tabid,
            "total_page": int(math.ceil((count*1.0)/int(pagesize))),
            "articles": articles
        }
        return ret

    def get_info_detail(self, tabid, id):
        info = InfoLogic().get_info_detail(tabid, id)
        if not info:
            return {}

        ret = {
            "visit_total": info.get("visit_total", ""),
            "display_time": info.get("display_time", ""),
            "tabid": info.get("tabid", ""),
            "user_id": info.get("user_id", ""),
            "description": info.get("description", "") if info.get("description", "") else "",
            "title": info.get("title", ""),
            "comments_total": info.get("comments_total", ""),
            "thumb": info.get("thumb", ""),
            "official_account": info.get("official_account", ""),
            "writer": info.get("writer", ""),
            "web_url": info.get("web_url", ""),
            "type": info.get("type", ""),
            "id": info.get("id", ""),
            "body": info.get("body", "")
        }
        return ret
