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
import time

logger = Log().getLog()


class Proj(BaseModel):

    @access("r")
    def get_all_proj_list(self, uid, biztype, pageno, pagesize):
        """
        获取方案详情
        :param biztype:
        :param pageno:
        :param pagesize:
        :return:
        """

        sql = """
            SELECT SQL_CALC_FOUND_ROWS *
            FROM t_project_union
            WHERE f_uid=%s  {biztype}
            ORDER BY f_crtime DESC
            LIMIT %s, %s
        """

        search_project_count = """
            SELECT FOUND_ROWS()
        """

        offset = (int(pageno) - 1) * int(pagesize)

        if biztype == "0":
            biztype_str = ""
            sql = sql.format(biztype=biztype_str)
        elif biztype == "1":
            #biztype_str = " and f_isjprize = {isjprize}".format(isjprize=1)
            biztype_str = " and f_isjprize in (1,3)"
            sql = sql.format(biztype=biztype_str)
        elif biztype == "2":
            #biztype_str = "and f_orderstatus != {orderstatus} and f_isjprize = {isjprize}".format(orderstatus=4, isjprize=0)
            biztype_str = "and f_orderstatus in (2,3) and f_isjprize=0"
            sql = sql.format(biztype=biztype_str)
        else:
            biztype_str = "and f_orderstatus = {orderstatus} ".format(orderstatus=4)
            sql = sql.format(biztype=biztype_str)

        count = 0
        orders = []
        try:
            self.cursor.execute(sql, (uid, offset, int(pagesize)))
            orders = self.cursor.fetchall() or []
            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        ret = {
            "count": count,
            "orders": orders
        }
        return ret

    def get_chasenumber_list(self, uid, pageno, pagesize):
        return BaseOrder(0).get_chasenumber_list(uid, pageno, pagesize)

    @access("r")
    def get_lanuch_proj_list(self, uid, pageno, pagesize):
        """
        获取方案详情
        :param biztype:
        :param pageno:
        :param pagesize:
        :return:
        """

        sql = """
                SELECT SQL_CALC_FOUND_ROWS *
                FROM t_followorder
                WHERE f_uid=%s  
                ORDER BY f_crtime DESC
                LIMIT %s, %s
            """

        search_project_count = """
                SELECT FOUND_ROWS()
            """

        search_proj_stat = """
            SELECT * 
            FROM t_analysis_follow_project
            WHERE f_pid in %s
        """

        offset = (int(pageno) - 1) * int(pagesize)

        count = 0
        orders = []
        stat = []
        try:
            self.cursor.execute(sql, (uid, offset, int(pagesize)))
            orders = self.cursor.fetchall() or []
            pids = [order.get("f_oid") for order in orders]
            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")
            if pids:
                self.cursor.execute(search_proj_stat, (tuple(pids), ))
                stat = self.cursor.fetchall() or []
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        ret = {
            "count": count,
            "orders": orders,
            "stat": stat
        }
        return ret

    @access("r")
    def get_follow_proj_list(self, uid, pageno, pagesize):
        """
        获取方案详情
        :param biztype:
        :param pageno:
        :param pagesize:
        :return:
        """

        sql = """
            SELECT SQL_CALC_FOUND_ROWS *
            FROM t_project_union
            WHERE f_uid=%s and f_ptype=-1
            ORDER BY f_crtime DESC
            LIMIT %s, %s
        """

        search_project_count = """
            SELECT FOUND_ROWS()
        """

        offset = (int(pageno) - 1) * int(pagesize)

        count = 0
        orders = []
        try:
            self.cursor.execute(sql, (uid, offset, int(pagesize)))
            orders = self.cursor.fetchall() or []
            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        ret = {
            "count": count,
            "orders": orders
        }
        return ret

    @access("r")
    def get_lanuch_recommend_list(self, pageno, pagesize):
        """
        获取方案详情
        :param biztype:
        :param pageno:
        :param pagesize:
        :return:
        """

        sql = """
                    SELECT SQL_CALC_FOUND_ROWS *
                    FROM t_analysis_follow_project
                    WHERE f_buyendtime > %s
                    ORDER BY f_buyendtime DESC
                    LIMIT %s, %s
                """

        search_project_count = """
            SELECT FOUND_ROWS()
        """

        seller_sql = """
            SELECT * 
            FROM t_analysis_hot_seller
            WHERE f_uid in %s
        """

        offset = (int(pageno) - 1) * int(pagesize)

        count = 0
        orders = []
        sellerinfo = []
        curtime = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(sql, (curtime, offset, int(pagesize)))
            orders = self.cursor.fetchall() or []
            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")

            uids = [order.get("f_uid") for order in orders]
            if uids:
                self.cursor.execute(seller_sql, (tuple(uids), ))
                sellerinfo = self.cursor.fetchall()
        except Exception as ex:
            logger.error(traceback.format_exc()) or []
            raise

        ret = {
            "count": count,
            "orders": orders,
            "sellerinfo": sellerinfo
        }
        return ret

    @access("r")
    def get_follow_hot_seller(self):
        """
        获取方案详情
        :param biztype:
        :param pageno:
        :param pagesize:
        :return:
        """

        sql = """
                SELECT  *
                FROM t_analysis_hot_seller
                ORDER BY f_hscore DESC
                LIMIT 0, 8
            """

        count = 0
        info = []
        try:
            self.cursor.execute(sql)
            info = self.cursor.fetchall() or []
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        return info

    @access("r")
    def get_seller_info_by_uid(self, uid):

        sql = """
                    SELECT  *
                    FROM t_analysis_hot_seller
                    WHERE f_uid = %s
                """

        count = 0
        info = []
        try:
            self.cursor.execute(sql, (uid, ))
            info = self.cursor.fetchone() or {}
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        return info

    @access("r")
    def get_history_gains(self, uid):
        sql = """
                SELECT SQL_CALC_FOUND_ROWS *
                FROM t_followorder
                WHERE f_uid=%s and f_crtime > %s
                ORDER BY f_crtime DESC
            """

        search_project_count = """
                SELECT FOUND_ROWS()
            """

        count = 0
        orders = []
        curtime = datetime.date.today() - datetime.timedelta(days=7)
        curtime = curtime.strftime("%Y-%m-%d")
        try:
            self.cursor.execute(sql, (uid, curtime))
            orders = self.cursor.fetchall() or []
            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

        ret = {
            "count": count,
            "orders": orders
        }
        return ret