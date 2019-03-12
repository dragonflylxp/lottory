#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: msg.py
#
#        Author:
#   Description: ---
#        Create: 2018-03-14 19:26:30
# Last Modified: 2018-03-14 19:26:30
#   Changes Log:


import ujson
import MySQLdb
import traceback
import define
from util.tools import Log
from common.dbs import BaseModel, access

logger = Log().getLog()


class MsgRecord(BaseModel):
    @access("w")
    def insert(self, params):
        lotid = params.get("lotid")
        oid = params.get("oid")
        msgtype = params.get("msgtype")
        msgcnt = params.get("msgcnt")
        msgstatus = define.MSG_STATUS_NEW

        sql = """
            INSERT INTO t_msg_record(
                f_lotid,
                f_oid,
                f_msgtype,
                f_msgcnt,
                f_msgstatus)
            VALUE(%s,%s,%s,%s,%s)
        """
        mid = None
        try:
            self.cursor.execute(sql, (lotid, oid, msgtype, msgcnt, msgstatus))
            self.conn.commit()
            mid = self.cursor.lastrowid
            logger.debug('[OrderStauts]:lotid=%s|oid=%s|msgtype=%s', lotid, oid, msgtype)
        except Exception as ex:
            self.conn.rollback()
            raise
        else:
            return mid
