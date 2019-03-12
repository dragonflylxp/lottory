#encoding=utf-8

import MySQLdb
import traceback
import define
from dbpool import db_pool
from util.tools import Log
from common.dbs import BaseModel, access

logger = Log().getLog()



TABLE_MAP = {
     3: "t_ticket_ssq",
    28: "t_ticket_dlt",
    44: "t_ticket_gx11x5",
    46: "t_ticket_jz",
    47: "t_ticket_jl"
}

class BaseTicket(BaseModel):

    def __init__(self, lotid):
        super(BaseTicket, self).__init__()
        self.lotid = lotid
        self.table = TABLE_MAP.get(int(self.lotid))

    @access("r")
    def get_project_tickets(self, pid):
        project_detail = """
            SELECT *
            FROM {}
            WHERE f_pid=%s
        """
        project_detail = project_detail.format(self.table)

        tickets = []
        try:
            self.cursor.execute(project_detail, (pid,))
            tickets = self.cursor.fetchall() or []
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        return tickets



    @access("r")
    def get_tickets_status_by_project(self, pid):
        sql = """SELECT
                      COUNT(*) as cnt,
                      SUM(f_allmoney) as allmoney,
                      SUM(f_calgetmoney) as calgetmoney,
                      SUM(f_getmoney) as getmoney,
                      f_ticketstatus as status
                 FROM
                      {}
                 WHERE
                      f_pid=%s
                 GROUP BY
                      f_ticketstatus
              """
        sql = sql.format(self.table)
        ticketstatus = []
        try:
            self.cursor.execute(sql, (pid, ))
            ticketstatus = list(self.cursor.fetchall())
        except Exception as ex:
            logger.error(traceback.format_exc())
            ticketstatus = []
        finally:
            return ticketstatus

    @access("r")
    def get_tickets_by_expect(self, expect):
        """根据期号查票
        """
        sql = "SELECT * FROM {} WHERE f_expect=%s AND f_isjprize=%s".format(self.table)
        tickets = []
        try:
            self.cursor.execute(sql, (expect, define.TICKET_JPRIZE_UNCAL))
            tickets = list(self.cursor.fetchall())
        except Exception as ex:
            logger.error(traceback.format_exc())
            tickets = []
        finally:
            return tickets

    @access("w")
    def update_jprize_status(self, results):
        """results:
            isjprze, calgetmoney,  calpregetmoney, tid
        """
        sql = "UPDATE {} SET f_isjprize=%s, f_calgetmoney=%s, f_calpregetmoney=%s WHERE f_tid=%s".format(self.table)
        try:
            self.cursor.executemany(sql, results)
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
