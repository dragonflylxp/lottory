# encoding=utf-8

import ujson
import MySQLdb
import traceback

import datetime
import define
from dbpool import db_pool
from util.tools import Log
from common.dbs import BaseModel, access
from baseorder import BaseOrder

logger = Log().getLog()


class JlOrder(BaseOrder):

    def __init__(self):
        super(JlOrder, self).__init__(47)

    @access("w")
    def place_order(self, params):
        uid = params.get("uid")
        lotid = params.get("lotid")
        wtype = params.get("wtype")
        beishu = params.get("beishu")
        zhushu = params.get("zhushu")
        ggtype  = params.get("ggtype")
        isquchu = params.get("isquchu")
        danma = params.get("danma")
        fileorcode = params.get("fileorcode")
        allmoney = params.get("allmoney")
        couponid = params.get("couponid")
        ratelist = params.get("ratelist")
        rqlist = params.get("rqlist")
        ptype = params.get("ptype", 0)
        fid = params.get("fid", 0)
        guarantee_odd = params.get("guarantee_odd", 0)
        mark = params.get("mark", "")
        firsttime = params.get("firsttime")
        lasttime = params.get("lasttime")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")
        sql = """
            INSERT INTO t_project_jl(
                f_uid,
                f_lotid,
                f_wtype,
                f_beishu,
                f_zhushu,
                f_ggtype,
                f_isquchu,
                f_danma,
                f_allmoney,
                f_couponid,
                f_fileorcode,
                f_rqlist,
                f_ratelist,
                f_orderstatus,
                f_fid,
                f_ptype,
                f_platform,
                f_channel,
                f_subchannel,
                f_placetime,
                f_firsttime,
                f_lasttime)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s)
        """

        gen_dan_sql = """
            INSERT INTO t_followorder(
                 f_uid,
                 f_oid,
                 f_lotid,
                 f_totalbeishu,
                 f_totalallmoney,
                 f_followstatus,
                 f_guarantee_odd,
                 f_remark
            )VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        pid = None
        try:
            self.cursor.execute(sql, (uid, lotid, wtype, beishu, zhushu, ggtype, isquchu, danma, allmoney,
                                      couponid, fileorcode, rqlist, ratelist, define.ORDER_STATUS_UNPAY, fid, ptype,
                                      platform, channel, subchannel, datetime.datetime.now(), firsttime, lasttime))
            pid = self.cursor.lastrowid
            #同步插入方案汇总表
            self._insert_project_union(pid, ptype)

            if str(ptype) == "1":
                self.cursor.execute(gen_dan_sql, (uid, pid, lotid, beishu, allmoney, 1, guarantee_odd, mark))

            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        logger.debug("[TRADE SVR]Place order! uid=%s|lotid=%s|pid=%s", uid, lotid, pid)
        return {
            "uid": uid,
            "pid": pid,
            "lotid": lotid,
            "allmoney": allmoney,
            "couponid": couponid
        }
