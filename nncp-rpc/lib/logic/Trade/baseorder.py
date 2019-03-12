# encoding=utf-8

import time
import ujson
import MySQLdb
import traceback
import datetime
from decimal import Decimal

import cbrpc
import define
from dbpool import db_pool
from model.dao import MongoDataModel
from util.tools import Log
from common.dbs import BaseModel, access

logger = Log().getLog()


TABLE_MAP = {
    28: "t_project_dlt",
     3: "t_project_ssq",
    44: "t_project_gx11x5",
    46: "t_project_jz",
    47: "t_project_jl"
}

EXPECT_MAP = {
    28: "lottery_dlt_expect_info",
     3: "lottery_ssq_expect_info",
    44: "lottery_gx11x5_expect_info"
}

TICKET_MAP = {
     3: "t_ticket_ssq",
    28: "t_ticket_dlt",
    44: "t_ticket_gx11x5",
    46: "t_ticket_jz",
    47: "t_ticket_jl"
}

class BaseOrder(BaseModel):

    def __init__(self, lotid):
        super(BaseOrder, self).__init__()
        self.lotid = lotid
        self.table = TABLE_MAP.get(int(self.lotid), "")
        self.expecttable = EXPECT_MAP.get(int(self.lotid), "")
        self.tickettable = TICKET_MAP.get(int(self.lotid), "")

    @access("r")
    def get_project_by_pid(self, pid):
        """
        方案详情
        """
        sql = "SELECT * FROM {} WHERE f_pid=%s".format(self.table)
        order = {}
        try:
            self.cursor.execute(sql, (pid,))
            order = self.cursor.fetchone() or {}

            #补充方案详情撤单金额
            sql = "SELECT SUM(f_allmoney) as cancelmoney FROM {} WHERE f_pid=%s AND f_ticketstatus=%s".format(self.tickettable)
            self.cursor.execute(sql, (pid, define.TICKET_STATUS_CANCEL))
            ticket = self.cursor.fetchone() or {}
            cancelmoney = ticket.get("cancelmoney", Decimal(0.00)) or Decimal(0.00)
            order["f_cancelmoney"] = cancelmoney
        except Exception as ex:
            logger.error(traceback.format_exc())
        finally:
            return order

    @access("r")
    def get_chasenumber_by_cid(self, cid):
        """
        追号详情
        """
        chasenumber = {}
        try:
            # 追号信息
            sql = "SELECT * FROM t_chasenumber WHERE f_cid=%s"
            self.cursor.execute(sql, (cid,))
            chasenumber  = self.cursor.fetchone() or {}

            # 订单数据
            sql = "SELECT * FROM {} WHERE f_chaseid=%s ORDER BY f_pid DESC".format(self.table)
            self.cursor.execute(sql, (cid,))
            projects = self.cursor.fetchall() or []
            chasenumber.update({"projects": projects})
        except Exception as ex:
            logger.error(traceback.format_exc())
        finally:
            return chasenumber

    @access("r")
    def get_project_list(self, uid, pageno, pagesize):
        """
        #方案记录列表
        :param orderid:
        :return:
        """
        if int(self.lotid) == 0:
            return self.get_all_project_list(uid, pageno, pagesize)

        endtime = datetime.date.today() - datetime.timedelta(days=3)
        endtime = endtime.strftime("%Y-%m-%d")

        sql = """
          SELECT SQL_CALC_FOUND_ROWS *
          FROM {}
          WHERE  f_uid=%s and f_crtime>%s
          ORDER BY f_crtime desc
          LIMIT %s, %s
        """
        sql = sql.format(self.table)

        search_project_count = """
            SELECT FOUND_ROWS()
        """
        offset = (int(pageno) - 1) * int(pagesize)
        orders = []
        count = 0
        try:
            self.cursor.execute(sql, (uid, endtime, offset, int(pagesize)))
            orders = self.cursor.fetchall()

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
    def get_chasenumber_list(self, uid, pageno, pagesize):
        """
        追号列表
        """
        sql = """
          SELECT SQL_CALC_FOUND_ROWS *
          FROM t_chasenumber
          WHERE  f_uid=%s AND f_chasestatus>%s
          ORDER BY f_crtime DESC
          LIMIT %s, %s
        """
        search_chasenumber_count = """
            SELECT FOUND_ROWS()
        """
        offset = (int(pageno) - 1) * int(pagesize)
        orders = []
        count = 0
        try:
            self.cursor.execute(sql, (uid, define.CHASE_STATUS_UNPAY, offset, int(pagesize)))
            orders = self.cursor.fetchall()

            self.cursor.execute(search_chasenumber_count)
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

    @access("w")
    def tickets_update_project(self, pid, orderstatus=None, isjprize=None):
        """
        汇总票状态修改方案状态
        """
        try:
            if orderstatus is not None and isjprize is not None:
                sql = "UPDATE {} SET f_orderstatus=%s, f_isjprize=%s WHERE f_pid=%s".format(self.table)
                self.cursor.execute(sql, (orderstatus, isjprize, pid))
                sql = "UPDATE t_project_union SET f_orderstatus=%s, f_isjprize=%s WHERE f_pid=%s AND f_lotid=%s"
                self.cursor.execute(sql, (orderstatus, isjprize, pid, self.lotid))
            elif orderstatus is not None:
                sql = "UPDATE {} SET f_orderstatus=%s WHERE f_pid=%s".format(self.table)
                self.cursor.execute(sql, (orderstatus, pid))
                sql = "UPDATE t_project_union SET f_orderstatus=%s WHERE f_pid=%s AND f_lotid=%s"
                self.cursor.execute(sql, (orderstatus, pid, self.lotid))
            elif isjprize is not None:
                sql = "UPDATE {} SET f_isjprize=%s WHERE f_pid=%s".format(self.table)
                self.cursor.execute(sql, (isjprize, pid))
                sql = "UPDATE t_project_union SET f_isjprize=%s WHERE f_pid=%s AND f_lotid=%s"
                self.cursor.execute(sql, (isjprize,  pid, self.lotid))
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise

    @access("w")
    def update_order_status(self, params):
        """
        将方案从指定状态修改为目标状态
            更新方案支付状态时用到
        """
        pid = params.get("pid")
        couponid = params.get("couponid")
        couponmoney = params.get("couponmoney")
        paymoney = params.get("paymoney")
        originstatus = params.get("originstatus")
        targetstatus = params.get("targetstatus")
        remark = params.get("remark", "")
        mid = params.get("mid", None)
        try:
            # 更新msg状态
            if mid is not None:
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    logger.warning("Order status already updated! lotid=%s|pid=%s|mid=%s", self.lotid, pid, mid)
                    raise Exception("Order status already updated!")

            # 更新优惠券状态
            if int(couponid) > 0 and targetstatus == define.ORDER_STATUS_SUCC:
                sql = "UPDATE t_account_coupon SET f_couponstatus=%s, f_pid=%s WHERE f_cid=%s"
                self.cursor.execute(sql, (define.COUPON_STATUS_USED, pid, couponid))

            # 更新订单状态
            sql = "UPDATE {} SET f_orderstatus=%s, f_paymoney=%s, f_couponmoney=%s, f_remark=%s WHERE f_pid=%s AND f_orderstatus=%s".format(self.table)
            ret = self.cursor.execute(sql, (targetstatus, paymoney, couponmoney, remark, pid, originstatus))
            if ret < 1:
                raise Exception("Can't find order with lotid={}|pid={}|orderstatus={}".format(self.lotid, pid, originstatus))

            #同步更新方案汇总表
            sql = "UPDATE t_project_union SET f_orderstatus=%s WHERE f_pid=%s AND f_lotid=%s"
            self.cursor.execute(sql, (targetstatus, pid, self.lotid))
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise

    @access("w")
    def update_chasenumber_status(self, params):
        """
        将追号计划从指定状态修改为目标状态
            更新追号支付状态时用到
        """
        cid = params.get("cid")
        pid = params.get("pid")
        couponid = params.get("couponid")
        couponmoney = params.get("couponmoney")
        paymoney = params.get("paymoney")
        chase_originstatus = params.get("chase_originstatus")
        chase_targetstatus = params.get("chase_targetstatus")
        order_originstatus = params.get("order_originstatus")
        order_targetstatus = params.get("order_targetstatus")
        remark = params.get("remark", "")
        mid = params.get("mid", None)
        try:
            if mid is not None:
                #更新msg状态
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    logger.warning("Chasenumber status already updated! lotid=%s|cid=%s|mid=%s", self.lotid, cid, mid)
                    raise Exception("Chasenumber status already updated!")

            sql = "UPDATE t_chasenumber SET f_chasestatus=%s, f_totalpaymoney=%s, f_remark=%s  WHERE f_cid=%s AND f_chasestatus=%s"
            ret = self.cursor.execute(sql, (chase_targetstatus, paymoney, remark, cid, chase_originstatus))
            if ret < 1:
                raise Exception("Can't find chasernumber with lotid={}|cid={}|orderstatus={}".format(self.lotid, cid, chase_originstatus))

            sql = "UPDATE {} SET f_orderstatus=%s, f_paymoney=%s, f_couponmoney=%s, f_remark=%s WHERE f_pid=%s AND f_orderstatus=%s".format(self.table)
            ret = self.cursor.execute(sql, (order_targetstatus, paymoney, couponmoney, remark, pid, order_originstatus))
            if ret < 1:
                raise Exception("Can't find order with lotid={}|pid={}|orderstatus={}".format(self.lotid, pid, order_originstatus))
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise

    def _insert_project_union(self, pid, ptype=0):
        """
        @beief: 同步插入方案汇总表
            各彩种下单时，在事务内调用
            此处不提交事务也不回滚事务
        """
        try:
            sql = "SELECT f_uid, f_crtime, f_uptime  FROM {} WHERE f_pid=%s".format(self.table)
            self.cursor.execute(sql, (pid,))
            ret = self.cursor.fetchone() or {}
            uid = ret.get("f_uid")
            crtime = ret.get("f_crtime")
            uptime = ret.get("f_uptime")
            #ptype = ret.get("f_ptype", 0)
            sql = "INSERT INTO t_project_union(f_uid,f_lotid,f_pid,f_crtime,f_uptime, f_ptype) VALUES(%s,%s,%s,%s,%s, %s)"
            self.cursor.execute(sql, (uid, self.lotid, pid, crtime, uptime, ptype))
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise

    def _update_project_union(self, pid):
        """
        @beief: 同步更新方案汇总表
            各彩种方案更新时，在事务内调用
            此处不提交事务也不回滚事务
        """
        try:
            sql = "SELECT f_orderstatus, f_isjprize, f_uptime FROM {} WHERE f_pid=%s".format(self.table)
            ret = self.cursor.fetchone() or {}
            orderstatus = ret.get("f_orderstatus") or 0
            isjprize = ret.get("f_isjprize") or 0
            uptime = ret.get("f_uptime")
            sql = "UPDATE t_project_union SET f_orderstatus=%s, f_isjprize=%s, f_uptime=%s  WHERE f_pid=%s AND f_lotid=%s"
            self.cursor.execute(sql, (orderstatus, isjprize, uptime, pid, self.lotid))
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
    #
    # def get_all_proj_list(self, biztype, pageno, pagesize):
    #     pass

    @access("r")
    def get_project_list_by_pids(self, pids):
        """
        #方案记录列表
        :param pids:
        :return:
        """
        sql = """
              SELECT *
              FROM {}
              WHERE  f_pid in %s

            """
        sql = sql.format(self.table)
        pids = tuple(pids)
        try:
            self.cursor.execute(sql, (pids, ))
            orders = self.cursor.fetchall()
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        return orders

    @access("w")
    def cancel_chasenumber(self, params):
        """取消追号
        """
        uid = params.get("uid")
        cid = params.get("cid")
        try:
            sql = "SELECT * FROM t_chasenumber WHERE f_uid=%s AND f_cid=%s AND f_chasestatus=%s FOR UPDATE"
            self.cursor.execute(sql, (uid, cid, define.CHASE_STATUS_SUCC))
            chasenumber = self.cursor.fetchone() or {}
            if not chasenumber:
                raise cbrpc.RpcException("追号计划不存在或已完成! lotid={}|chaseid={}".format(self.lotid, cid))

            stopprize = chasenumber.get("f_stopprize")
            expecttotal = chasenumber.get("f_expecttotal")
            expectnum = chasenumber.get("f_expectnum")
            lastexpect = chasenumber.get("f_lastexpect")
            allmoney = chasenumber.get("f_allmoney")
            lotid = chasenumber.get("f_lotid")
            uid = chasenumber.get("f_uid")

            #追号方案退款
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s"
            self.cursor.execute(sql, (uid,))
            uinfo = self.cursor.fetchone() or {}
            returnmoney = allmoney * (expecttotal - expectnum)
            balance_recharge = uinfo.get("f_balance_recharge")
            balance_draw = uinfo.get("f_balance_draw")
            freeze = uinfo.get("f_freeze")
            #取消追号，退款到充值余额
            balance_recharge = balance_recharge + returnmoney
            sql = "UPDATE t_account_info SET f_balance_recharge=%s WHERE f_uid=%s"
            self.cursor.execute(sql, (balance_recharge, uid))

            #修改追号方案状态
            sql = "UPDATE t_chasenumber SET f_chasestatus=%s, f_stopreturnmoney=%s WHERE f_cid=%s"
            self.cursor.execute(sql, (define.CHASE_STATUS_CANCEL, returnmoney, cid))

            #流水日志
            sql = """INSERT INTO t_account_log(
                        f_uid,
                        f_oid,
                        f_lotid,
                        f_inout,
                        f_money,
                        f_balance_recharge,
                        f_balance_draw,
                        f_freeze)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                """
            self.cursor.execute(sql, (uid, cid, lotid, define.ACCOUNT_LOG_TYPE_CHASECANCEL, returnmoney, balance_recharge, balance_draw, freeze))
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        return {"cid": cid, "uid": uid, "status": "1"}

    @access("w")
    def place_chasenumber(self, params):
        """追号计划发起
        """
        uid = params.get("uid")

        #追号信息
        totalallmoney = params.get("allmoney")
        expecttotal = params.get("expecttotal")
        israndom = params.get("israndom")
        stopprize = params.get("stopprize")

        #投注信息
        lotid = params.get("lotid")
        wtype = params.get("wtype")
        beishu = params.get("beishu")
        zhushu = params.get("zhushu")
        expect = params.get("expect")
        fileorcode = params.get("fileorcode")
        selecttype = params.get("selecttype")
        allmoney = params.get("singlemoney")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")
        couponid = 0

        cid = pid = None
        try:
            #追号计划入库
            sql = """
                INSERT INTO t_chasenumber(
                    f_uid,
                    f_lotid,
                    f_expecttotal,
                    f_expectnum,
                    f_lastexpect,
                    f_totalallmoney,
                    f_israndom,
                    f_stopprize,
                    f_chasestatus,
                    f_wtype,
                    f_beishu,
                    f_zhushu,
                    f_allmoney,
                    f_fileorcode,
                    f_selecttype)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            self.cursor.execute(sql, (uid, lotid, expecttotal, 1, expect, totalallmoney, israndom, stopprize,
                               define.CHASE_STATUS_UNPAY, wtype, beishu, zhushu, allmoney, fileorcode, selecttype))
            cid = self.cursor.lastrowid


            #当前期投注
            sql = """
                INSERT INTO {}(
                    f_uid,
                    f_chaseid,
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
                VALUES(%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            sql = sql.format(self.table)
            self.cursor.execute(sql, (uid, cid, lotid, wtype, beishu, zhushu, expect, allmoney,
                                      couponid, fileorcode, selecttype, platform, channel, subchannel,
                                      datetime.datetime.now(),define.ORDER_STATUS_UNPAY))


            pid = self.cursor.lastrowid
            #同步插入方案汇总表
            self._insert_project_union(pid)
            self.conn.commit()
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            raise
        logger.debug("[TRADE SVR]Place chasenumber! uid=%s|lotid=%s|cid=%s", uid, lotid, cid)
        return {
            "uid": uid,
            "pid": pid,
            "cid": cid,
            "lotid": lotid,
            "allmoney": totalallmoney,
            "couponid": couponid
        }


    @access("w")
    def continue_chasenumber(self, params):
        """追号计划继续
        """
        cid = params.get("cid")
        getmoney = params.get("getmoney")
        pid = None
        try:
            sql = "SELECT * FROM t_chasenumber WHERE f_cid=%s AND f_chasestatus=%s FOR UPDATE"
            self.cursor.execute(sql, (cid, define.CHASE_STATUS_SUCC))
            chasenumber = self.cursor.fetchone() or {}
            if not chasenumber:
                raise Exception("追号计划不存在或已完成! lotid={}|chaseid={}".format(self.lotid, cid))

            #命中中奖停止条件
            stopprize = chasenumber.get("f_stopprize")
            expecttotal = chasenumber.get("f_expecttotal")
            expectnum = chasenumber.get("f_expectnum")
            lastexpect = chasenumber.get("f_lastexpect")
            allmoney = chasenumber.get("f_allmoney")
            lotid = chasenumber.get("f_lotid")
            uid = chasenumber.get("f_uid")

            if stopprize > 0 and getmoney > stopprize:
                #追号方案退款
                sql = "SELECT * FROM t_account_info WHERE f_uid=%s"
                self.cursor.execute(sql, (uid,))
                uinfo = self.cursor.fetchone() or {}
                returnmoney = allmoney * (expecttotal - expectnum)
                balance_recharge = uinfo.get("f_balance_recharge")
                balance_draw = uinfo.get("f_balance_draw")
                freeze = uinfo.get("f_freeze")
                balance_draw = balance_draw + returnmoney
                sql = "UPDATE t_account_info SET f_balance_draw=%s WHERE f_uid=%s"
                self.cursor.execute(sql, (balance_draw, uid))

                #更新追号状态
                sql = "UPDATE t_chasenumber SET f_chasestatus=%s, f_stopreturnmoney=%s WHERE f_cid=%s"
                self.cursor.execute(sql, (define.CHASE_STATUS_PRIZESTOP, returnmoney, cid))

                #流水日志
                sql = """INSERT INTO t_account_log(
                            f_uid,
                            f_oid,
                            f_lotid,
                            f_inout,
                            f_money,
                            f_balance_recharge,
                            f_balance_draw,
                            f_freeze)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                self.cursor.execute(sql, (uid, cid, lotid, define.ACCOUNT_LOG_TYPE_CHASECANCEL, returnmoney, balance_recharge, balance_draw, freeze))
                self.conn.commit()
                return {}
            else:
                #查询当前期号
                curr_expect = ""
                try:
                    if int(self.lotid) in [28, 3]:
                        curr_expect = MongoDataModel().find_one(self.expecttable, {"isCurrent": "1"})
                        curr_expect = curr_expect.get("expect") if curr_expect else ""
                    elif int(self.lotid) in [44]:
                        curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        curr_expect = MongoDataModel().find_one(self.expecttable, {"startTime": {"$lte": curtime}, "stopTime": {"$gt": curtime}},
                                                            sort=[('expect', -1)], rn=10)
                        curr_expect = curr_expect.get("expect") if curr_expect else ""
                except:
                    logger.error(traceback.format_exc())
                if not curr_expect:
                    raise Exception("追号获取当前期号失败! lotid={}|chaseid={}".format(self.lotid, cid))
                if curr_expect == lastexpect:
                    raise Exception("当前期重复追号拦截! lotid={}|chaseid={}|expect={}".format(self.lotid, cid, lastexpect))

                #更新追号进度
                israndom = chasenumber.get("israndom")
                expectnum += 1
                chasestatus = define.CHASE_STATUS_SUCC if expectnum < expecttotal else define.CHASE_STATUS_FINISHSTOP
                sql = "UPDATE t_chasenumber SET f_expectnum=%s, f_chasestatus=%s, f_lastexpect=%s WHERE f_cid=%s"
                self.cursor.execute(sql, (expectnum, chasestatus, curr_expect, cid))

                #投注下单
                uid = chasenumber.get("f_uid")
                lotid = chasenumber.get("f_lotid")
                wtype = chasenumber.get("f_wtype")
                fileorcode = chasenumber.get("f_fileorcode")
                selecttype = chasenumber.get("f_selecttype")
                zhushu = chasenumber.get("f_zhushu")
                beishu = chasenumber.get("f_beishu")
                couponid = 0
                sql = """
                    INSERT INTO {}(
                        f_uid,
                        f_chaseid,
                        f_lotid,
                        f_wtype,
                        f_beishu,
                        f_zhushu,
                        f_expect,
                        f_allmoney,
                        f_couponid,
                        f_fileorcode,
                        f_selecttype,
                        f_placetime,
                        f_orderstatus)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
                sql = sql.format(self.table)
                self.cursor.execute(sql, (uid, cid, lotid, wtype, beishu, zhushu, curr_expect, allmoney,
                                        couponid, fileorcode, selecttype, datetime.datetime.now(), define.ORDER_STATUS_SUCC))

                pid = self.cursor.lastrowid
                #同步插入方案汇总表
                self._insert_project_union(pid)
                self.conn.commit()

                logger.debug("[TRADE SVR]Continue chasenumber! uid=%s|lotid=%s|cid=%s|pid=%s", uid, lotid, cid, pid)
                return {
                    "uid": uid,
                    "pid": pid,
                    "cid": cid,
                    "lotid": lotid,
                    "allmoney": allmoney,
                    "couponid": couponid
                }
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.conn.rollback()
            return {}

    @access("r")
    def get_follow_project_by_pid(self, pid):
        """
        方案详情
        """
        sql = "SELECT * FROM {} WHERE f_pid=%s".format(self.table)
        follow_sql = "SELECT * FROM t_followorder WHERE f_oid=%s"

        order = {}
        try:
            self.cursor.execute(sql, (pid,))
            order = self.cursor.fetchone() or {}
            fid = order.get("f_fid") if order.get("f_fid") else pid

            self.cursor.execute(follow_sql, (fid, ))
            follow = self.cursor.fetchone() or {}
            order.update({
                "fuid": follow.get("f_uid"),
                "oid": follow.get("f_oid"),
                "guarantee_odd": follow.get("f_guarantee_odd", "0.0"),
                "remark": follow.get("f_remark"),
                "totalgetmoney": follow.get("f_totalgetmoney", ""),
                "totalfeemoney": follow.get("f_totalfeemoney", "")

            })
        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        finally:
            return order


    @access("r")
    def get_follow_top_five(self, fid):
        sql = "SELECT * FROM {} WHERE f_fid=%s  order by f_allmoney desc limit 0,5".format(self.table)
        order = {}
        try:
            self.cursor.execute(sql, (fid,))
            order = self.cursor.fetchall() or {}

        except Exception as ex:
            logger.error(traceback.format_exc())
            raise
        finally:
            return order
