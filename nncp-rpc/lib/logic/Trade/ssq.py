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


class SsqOrder(BaseOrder):

    def __init__(self):
        super(SsqOrder, self).__init__(3)

    @access("w")
    def place_order(self, params):
        uid = params.get("uid")
        lotid = params.get("lotid")
        wtype = params.get("wtype")
        beishu = params.get("beishu")
        zhushu = params.get("zhushu")
        expect = params.get("expect")
        fileorcode = params.get("fileorcode")
        selecttype = params.get("selecttype")
        allmoney = params.get("allmoney")
        couponid = params.get("couponid")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")

        sql = """
            INSERT INTO t_project_ssq(
                f_uid,
                f_lotid,
                f_wtype,
                f_beishu,
                f_zhushu,
                f_expect,
                f_allmoney,
                f_couponid,
                f_fileorcode,
                f_selecttype,
                f_platform,
                f_channel,
                f_subchannel,
                f_placetime,
                f_orderstatus)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        pid = None
        try:
            self.cursor.execute(sql, (uid, lotid, wtype, beishu, zhushu, expect, allmoney,
                                      couponid, fileorcode, selecttype, platform, channel, subchannel,
                                      datetime.datetime.now(), define.ORDER_STATUS_UNPAY))
            pid = self.cursor.lastrowid
            #同步插入方案汇总表
            self._insert_project_union(pid)
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
