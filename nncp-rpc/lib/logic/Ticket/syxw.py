#encoding=utf-8

import MySQLdb
import traceback
import define
from dbpool import db_pool
from util.tools import Log
from common.dbs import BaseModel, access
from baseticket import BaseTicket

logger = Log().getLog()

class SyxwTicket(BaseTicket):

    def __init__(self, lotid):
        super(SyxwTicket, self).__init__(lotid)

    @access("w")
    def save_tickets(self, params):
        project = params.get("project")
        tickets = params.get("tickets")
        mid = params.get("mid", None)
        uid = project.get("f_uid")
        pid = project.get("f_pid")
        lotid = project.get("f_lotid")

        try:
            if mid is not None:
                #更新msg状态
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    logger.warning("Tickets already saved! lotid=%s|pid=%s|mid=%s", 28, pid, mid)
                    raise Exception("Tickets already saved!")

            sql = """
                INSERT INTO {}(
                    f_uid,
                    f_pid,
                    f_lotid,
                    f_wtype,
                    f_beishu,
                    f_zhushu,
                    f_expect,
                    f_allmoney,
                    f_fileorcode,
                    f_selecttype,
                    f_ticketstatus)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            sql = sql.format(self.table)
            args = []
            for tkt in tickets:
                tpl = (uid, pid, lotid, tkt["wtype"], tkt["beishu"],
                       tkt["zhushu"], tkt["expect"], tkt["allmoney"],
                       tkt["fileorcode"], tkt["selecttype"], define.TICKET_STATUS_SAVED)
                args.append(tpl)
            self.cursor.executemany(sql, args)
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        return pid


    def get_open_expect(self, expect):
        table_map = {
            '44': 'lottery_gx11x5_expect_info',
            '45': 'lottery_jx11x5_expect_info',
        }
        tb = table_map.get(str(self.lotid))
        expectinfo = self.mongo.find(tb, {"expect":expect})
        expectinfo = expectinfo[0] if expectinfo else {}
        return expectinfo
