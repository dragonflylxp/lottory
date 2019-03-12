# encoding=utf-8

import inspect
import MySQLdb
import traceback
from  decimal import Decimal

import datetime
import define
from cbrpc import RpcException
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from common import MQ
from common.dbs import BaseModel, access

logger = Log().getLog()

TABLE_MAP = {
    28: "t_project_dlt",
     3: "t_project_ssq",
    44: "t_project_gx11x5",
    46: "t_project_jz",
    47: "t_project_jl"
}

class UserAccountLogic(BaseModel):

    @access("r")
    def user_account(self, uid):
        ret = {}
        try:
            sql = """
                  SELECT
                        f_balance_recharge balance_recharge,
                        f_balance_draw balance_draw,
                        f_balance_recharge+f_balance_draw balance,
                        f_freeze freeze
                  FROM t_account_info
                  WHERE  f_uid = %s LIMIT 1
              """

            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return ret

    @access("r")
    def get_coupon_by_cid(self, couponid):
        ret = {}
        try:
            sql = """
                  SELECT * FROM t_account_coupon WHERE f_cid=%s
              """
            self.cursor.execute(sql, (couponid, ))
            ret = self.cursor.fetchone() or {}
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return ret

    @access("w")
    def order_freeze(self, params):
        """下单冻结资金
        """
        uid = params.get("uid")
        pid = params.get("pid")
        lotid = params.get("lotid")
        couponid = params.get("couponid")
        allmoney = Decimal(params.get("allmoney"))
        mid = params.get("mid", None)
        couponmoney = paymoney = Decimal(0)

        logger.debug(params)
        paystatus = define.ORDER_PAY_STATUS_FAILED
        try:
            if mid is not None:
                #更新msg状态
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    paystatus = define.ORDER_PAY_STATUS_ALREADY_PAID
                    raise RpcException("订单已支付")

            #查询余额
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s FOR UPDATE"
            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
            balance_recharge  = ret.get("f_balance_recharge")
            balance_draw = ret.get("f_balance_draw")
            freeze = ret.get("f_freeze")

            #优惠券判断
            if int(couponid) > 0:
                sql = "SELECT * FROM t_account_coupon WHERE f_cid=%s"
                self.cursor.execute(sql, (couponid, ))
                coupon = self.cursor.fetchone() or {}
                if not coupon:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_UNKNOWN
                    raise RpcException("未知的优惠券")
                if coupon.get("f_couponstatus") == define.COUPON_STATUS_USED:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_USED
                    raise RpcException("优惠券已使用")
                if coupon.get("f_couponstatus") == define.COUPON_STATUS_EXPIRE:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_EXPIRE
                    raise RpcException("优惠券已过期")
                if coupon.get("f_expiretime") < datetime.datetime.now():
                    paystatus = define.ORDER_PAY_STATUS_COUPON_EXPIRE
                    raise RpcException("优惠券已过期")
                if coupon.get("f_activetime") > datetime.datetime.now():
                    paystatus = define.ORDER_PAY_STATUS_COUPON_NEGTIVE
                    raise RpcException("优惠券未激活")
                couponmoney = coupon.get("f_couponmoney")
                requiremoney = coupon.get("f_requiremoney")
                if allmoney < requiremoney:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_ILLEGAL
                    raise RpcException("优惠券不满足使用条件")
                lotids = coupon.get("f_lotids")
                if lotids != "0":
                    lotids = lotids.split(",")
                    if str(lotid) not in lotids:
                        paystatus = define.ORDER_PAY_STATUS_COUPON_ILLEGAL
                        raise RpcException("优惠券不满足使用条件")
            else:
                couponmoney = Decimal(0)

            paymoney = allmoney - couponmoney
            if paymoney > balance_recharge + balance_draw:
                paystatus = define.ORDER_PAY_STATUS_NOTENOUGH_MONEY
                raise RpcException("账户余额不足")

            #冻结扣款(优先使用充值账户)
            if balance_recharge >= paymoney:
                balance_recharge = balance_recharge - paymoney
            else:
                balance_draw = balance_draw + balance_recharge - paymoney
                balance_recharge = Decimal(0)
            freeze = freeze + paymoney
            sql = "UPDATE t_account_info SET f_balance_recharge=%s, f_balance_draw=%s, f_freeze=%s WHERE f_uid=%s"
            self.cursor.execute(sql, (balance_recharge, balance_draw, freeze, uid))

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
            self.cursor.execute(sql, (uid, pid, lotid, define.ACCOUNT_LOG_TYPE_FREEZE, paymoney, balance_recharge, balance_draw, freeze))
            self.conn.commit()
            paystatus = define.ORDER_PAY_STATUS_SUCC
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
        finally:
            return paystatus, paymoney, couponmoney


    @access("w")
    def order_pay(self, params):
        """解冻扣款
        """
        pid = params.get("pid")
        lotid = params.get("lotid")
        uid = params.get("uid")
        mid = params.get("mid", None)
        paystatus = define.ORDER_PAY_STATUS_FAILED
        try:
            if mid is not None:
                #更新msg状态
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    paystatus = define.ORDER_PAY_STATUS_ALREADY_PAID
                    raise RpcException("订单已支付")

            #查询余额
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s FOR UPDATE"
            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
            balance_recharge = ret.get("f_balance_recharge")
            balance_draw = ret.get("f_balance_draw")
            freeze = ret.get("f_freeze")

            sql = "SELECT * FROM t_account_log WHERE f_inout=%s AND f_uid=%s AND f_lotid=%s AND f_oid=%s"
            self.cursor.execute(sql, (define.ACCOUNT_LOG_TYPE_FREEZE, uid, lotid, pid ))
            ret = self.cursor.fetchone() or {}
            if not ret:
                paystatus = define.ORDER_PAY_STATUS_NOT_FREEZE
                raise RpcException("订单已解冻")
            paymoney = ret.get("f_money")

            #解冻扣款
            if freeze < paymoney:
                paystatus = define.ORDER_PAY_STATUS_FREEZE_ERROR
                raise RpcException("冻结金额不足")
            freeze = freeze - paymoney
            sql = "UPDATE t_account_info SET f_freeze=%s WHERE f_uid=%s"
            self.cursor.execute(sql, (freeze, uid))

            #标记订单扣款时间
            sql = "UPDATE {} SET f_paytime=%s WHERE f_pid=%s".format(TABLE_MAP.get(int(lotid)))
            self.cursor.execute(sql, (datetime.datetime.now(), pid))

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
            self.cursor.execute(sql, (uid, pid, lotid, define.ACCOUNT_LOG_TYPE_PAID, paymoney, balance_recharge, balance_draw, freeze))
            self.conn.commit()
            paystatus = define.ORDER_PAY_STATUS_SUCC
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
        finally:
            return paystatus

    @access("w")
    def order_chasepay(self, params):
        """追号扣款
        """
        cid = params.get("cid")
        pid = params.get("pid")
        lotid = params.get("lotid")
        uid = params.get("uid")
        mid = params.get("mid", None)
        allmoney = Decimal(params.get("allmoney"))
        paystatus = define.ORDER_PAY_STATUS_FAILED
        couponmoney = paymoney = Decimal(0)
        try:
            if mid is not None:
                #更新msg状态
                sql = "UPDATE t_msg_record SET f_msgstatus=%s WHERE f_mid=%s AND f_msgstatus=%s"
                ret = self.cursor.execute(sql, (define.MSG_STATUS_DONE, mid, define.MSG_STATUS_NEW))
                if ret < 1:
                    paystatus = define.ORDER_PAY_STATUS_ALREADY_PAID
                    raise RpcException("订单已支付")

            #查询余额
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s FOR UPDATE"
            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
            balance_recharge = ret.get("f_balance_recharge")
            balance_draw = ret.get("f_balance_draw")
            freeze = ret.get("f_freeze")

            #直接扣款
            paymoney = allmoney - couponmoney
            if paymoney> balance_recharge + balance_draw:
                paystatus = define.ORDER_PAY_STATUS_NOTENOUGH_MONEY
                raise RpcException("账户余额不足")
            if balance_recharge >= paymoney:
                balance_recharge = balance_recharge - paymoney
            else:
                balance_draw = balance_draw + balance_recharge - paymoney
                balance_recharge = Decimal(0)
            sql = "UPDATE t_account_info SET f_balance_recharge=%s,f_balance_draw=%s WHERE f_uid=%s"
            self.cursor.execute(sql, (balance_recharge, balance_draw, uid))

            #标记订单扣款时间
            sql = "UPDATE {} SET f_paytime=%s WHERE f_pid=%s".format(TABLE_MAP.get(int(lotid)))
            self.cursor.execute(sql, (datetime.datetime.now(), pid))

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
            self.cursor.execute(sql, (uid, cid, lotid, define.ACCOUNT_LOG_TYPE_CHASEPAY, paymoney, balance_recharge, balance_draw, freeze))
            self.conn.commit()
            paystatus = define.ORDER_PAY_STATUS_SUCC
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
        finally:
            return paystatus, paymoney, couponmoney

    @access("r")
    def user_account_detail(self, uid, biztype, pageno, pagesize):
        ret = {}
        details = []
        count = 0
        endtime = datetime.date.today() - datetime.timedelta(days=3)
        endtime = endtime.strftime("%Y-%m-%d")
        try:
            sql = """
                      SELECT SQL_CALC_FOUND_ROWS  *
                      FROM t_account_log
                      WHERE  f_uid = %s  and f_crtime> %s {inout}
                      ORDER  by f_id  desc
                      limit %s, %s

                  """

            search_project_count = """
                SELECT FOUND_ROWS()
            """

            if str(biztype) != "0":
                inout_str = " and  f_inout={inout}" .format(inout=biztype)
            else:
                inout_str = " and f_inout!=2"
            sql = sql.format(inout=inout_str)

            offset = (int(pageno) - 1) * int(pagesize)
            self.cursor.execute(sql, (uid, endtime, offset, int(pagesize)))
            details = self.cursor.fetchall() or []

            self.cursor.execute(search_project_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")

        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            ret = {
                "count": count,
                "details": details
            }
            return ret

    def check_account(self, uid, lotid, allmoney, couponid):
        paymoney = 0
        allmoney = Decimal(allmoney)
        paystatus = define.ORDER_PAY_STATUS_FAILED
        try:
            #查询余额
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s"
            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
            balance_recharge = ret.get("f_balance_recharge")
            balance_draw = ret.get("f_balance_draw")
            freeze = ret.get("f_freeze")

            #优惠券判断
            if int(couponid) > 0:
                sql = "SELECT * FROM t_account_coupon WHERE f_cid=%s"
                self.cursor.execute(sql, (couponid, ))
                coupon = self.cursor.fetchone() or {}
                if not coupon:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_UNKNOWN
                    raise RpcException("未知的优惠券")
                if coupon.get("f_couponstatus") == define.COUPON_STATUS_USED:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_USED
                    raise RpcException("优惠券已使用")
                if coupon.get("f_couponstatus") == define.COUPON_STATUS_EXPIRE:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_EXPIRE
                    raise RpcException("优惠券已过期")
                if coupon.get("f_expiretime") < datetime.datetime.now():
                    paystatus = define.ORDER_PAY_STATUS_COUPON_EXPIRE
                    raise RpcException("优惠券已过期")
                if coupon.get("f_activetime") > datetime.datetime.now():
                    paystatus = define.ORDER_PAY_STATUS_COUPON_NEGTIVE
                    raise RpcException("优惠券未激活")
                couponmoney = coupon.get("f_couponmoney")
                requiremoney = coupon.get("f_requiremoney")
                if allmoney < requiremoney:
                    paystatus = define.ORDER_PAY_STATUS_COUPON_ILLEGAL
                    raise RpcException("优惠券不满足使用条件")
                lotids = coupon.get("f_lotids")
                if lotids != "0":
                    lotids = lotids.split(",")
                    if str(lotid) not in lotids:
                        paystatus = define.ORDER_PAY_STATUS_COUPON_ILLEGAL
                        raise RpcException("优惠券不满足使用条件")
            else:
                couponmoney = Decimal(0)

            paymoney = allmoney - couponmoney
            if paymoney > balance_recharge + balance_draw:
                paystatus = define.ORDER_PAY_STATUS_NOTENOUGH_MONEY
                raise RpcException("账户余额不足")
            paystatus = define.ORDER_PAY_STATUS_SUCC
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return paystatus, paymoney

    @access("w")
    def order_prize(self, params):
        """派奖加钱
        """
        pid = params.get("pid")
        uid = params.get("uid")
        cid = params.get("cid")
        fid = params.get("fid")
        lotid = params.get("lotid")
        allmoney = Decimal(params.get("allmoney"))
        couponmoney = Decimal(params.get("couponmoney"))
        getmoney = Decimal(params.get("getmoney"))
        cancelmoney = Decimal(params.get("cancelmoney"))
        try:
            paymoney = allmoney - couponmoney
            cancelmoney = paymoney if cancelmoney > paymoney else cancelmoney

            #查询余额
            sql = "SELECT * FROM t_account_info WHERE f_uid=%s FOR UPDATE"
            self.cursor.execute(sql, (uid, ))
            ret = self.cursor.fetchone() or {}
            balance_recharge = ret.get("f_balance_recharge")
            balance_draw = ret.get("f_balance_draw")
            freeze = ret.get("f_freeze")

            #处理奖金
            if getmoney> 0:
                #订单加奖金
                sql = "UPDATE {} SET f_isjprize=%s, f_getmoney=%s,f_prizetime=%s WHERE f_pid=%s AND f_isjprize!=%s".format(TABLE_MAP.get(int(lotid)))
                ret = self.cursor.execute(sql, (define.ORDER_JPRIZE_PRIZED, getmoney, datetime.datetime.now(), pid, define.ORDER_JPRIZE_PRIZED))
                if ret < 1:
                    raise Exception("彩种lotid={}方案pid={}重复派奖拦截".format(lotid, pid))

                #追号方案加奖金
                if int(cid) > 0:
                    sql = "UPDATE t_chasenumber SET f_totalgetmoney=f_totalgetmoney+%s WHERE f_cid=%s"
                    self.cursor.execute(sql, (getmoney, cid))

                #同步更新方案汇总表
                sql = "UPDATE t_project_union SET f_isjprize=%s  WHERE f_pid=%s AND f_lotid=%s"
                self.cursor.execute(sql, (define.ORDER_JPRIZE_PRIZED, pid, lotid))

                #加钱(奖金加到提款账户中)
                balance_draw = balance_draw + getmoney
                sql = "UPDATE t_account_info SET f_balance_draw=%s WHERE f_uid=%s"
                self.cursor.execute(sql, (balance_draw, uid))

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
                self.cursor.execute(sql, (uid, pid, lotid, define.ACCOUNT_LOG_TYPE_PRIZE, getmoney, balance_recharge, balance_draw, freeze))

                # 处理跟单佣金
                if int(fid) > 0:
                    # 计算佣金
                    sql = "SELECT * FROM t_followorder WHERE f_oid=%s"
                    self.cursor.execute(sql, (fid,))
                    follow = self.cursor.fetchone()
                    fq_uid = follow.get("f_uid")
                    fq_oid = follow.get("f_oid")
                    guarantee_odd = follow.get("f_guarantee_odd")
                    if Decimal(guarantee_odd) > getmoney / (allmoney - cancelmoney):
                        feemoney = Decimal(0)
                    else:
                        feemoney = getmoney * Decimal(0.1)

                    #跟单方案加奖金
                    sql = "UPDATE t_followorder SET f_totalgetmoney=f_totalgetmoney+%s, f_totalfeemoney=f_totalfeemoney+%s WHERE f_oid=%s"
                    self.cursor.execute(sql, (getmoney, feemoney, fid))

                    #佣金处理: 佣金大于0且不是发起的原始订单
                    if feemoney > 0 and int(fq_oid) != int(pid):
                        # 跟单人扣除佣金
                        balance_draw = balance_draw - feemoney
                        sql = "UPDATE t_account_info SET f_balance_draw=%s WHERE f_uid=%s"
                        self.cursor.execute(sql, (balance_draw, uid))

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
                        self.cursor.execute(sql, (uid, pid, lotid, define.ACCOUNT_LOG_TYPE_FOLLOWFEE_SUB, -feemoney, balance_recharge, balance_draw, freeze))

                        # 发单人加佣金
                        sql = "SELECT * FROM t_account_info WHERE f_uid=%s FOR UPDATE"
                        self.cursor.execute(sql, (fq_uid, ))
                        fq = self.cursor.fetchone() or {}
                        fq_balance_recharge = fq.get("f_balance_recharge")
                        fq_balance_draw = fq.get("f_balance_draw")
                        fq_freeze = fq.get("f_freeze")
                        fq_balance_draw = fq_balance_draw + feemoney
                        sql = "UPDATE t_account_info SET f_balance_draw=%s WHERE f_uid=%s"
                        self.cursor.execute(sql, (fq_balance_draw, fq_uid))

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
                        self.cursor.execute(sql, (fq_uid, pid, lotid, define.ACCOUNT_LOG_TYPE_FOLLOWFEE_ADD, feemoney, fq_balance_recharge, fq_balance_draw, fq_freeze))

            #处理退款
            if cancelmoney > 0:
                # 反写撤单金额
                sql = "UPDATE {} SET f_cancelmoney=%s,f_canceltime=%s WHERE f_pid=%s AND f_cancelmoney=0".format(TABLE_MAP.get(int(lotid)))
                ret = self.cursor.execute(sql, (cancelmoney,datetime.datetime.now(), pid))
                if ret < 1:
                    raise Exception("彩种lotid={}方案pid={}重复退款拦截".format(lotid, pid))

                #加钱(退款到提款账户中)
                balance_draw = balance_draw + getmoney + cancelmoney  # 累加上奖金
                sql = "UPDATE t_account_info SET f_balance_draw=%s WHERE f_uid=%s"
                self.cursor.execute(sql, (balance_draw, uid))

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
                self.cursor.execute(sql, (uid, pid, lotid, define.ACCOUNT_LOG_TYPE_CANCEL, cancelmoney, balance_recharge, balance_draw, freeze))
            self.conn.commit()

            # 活动消息: [方案派奖成功]
            sql = "SELECT * FROM {} WHERE f_pid=%s".format(TABLE_MAP.get(int(lotid)))
            self.cursor.execute(sql, (pid,))
            order = self.cursor.fetchone()
            activity_msg = {
                "uid": order.get("f_uid"),
                "pid": order.get("f_pid"),
                "lotid": order.get("f_lotid"),
                "wtype": order.get("f_wtype"),
                "zhushu": order.get("f_zhushu"),
                "beishu": order.get("f_beishu"),
                "allmoney": order.get("f_allmoney"),
                "couponmoney": order.get("f_couponmoney"),
                "returnmoney": order.get("f_cancelmoney"),
                "prize": order.get("f_getmoney"),
                "buytime": order.get("f_crtime"),
                "firsttime": order.get("f_firsttime", "") or "",
                "lasttime": order.get("f_lasttime", "") or "",
                "fadan": order.get("f_ptype", 0) or 0,
                "followpid": order.get("f_fid", 0) or 0,
                "orderstatus": order.get("f_orderstatus"),
                "isjprize": order.get("f_isjprize"),
                "platform": order.get("f_platform")
            }
            MQ.send_msg('prize_suc', activity_msg)
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())


    @access("r")
    def coupon_list(self, uid, group, lotid, allmoney, pageno, pagesize):
        search_count = """
            SELECT FOUND_ROWS()
        """
        offset = (int(pageno) - 1) * int(pagesize)
        coupons = []
        count = 0
        try:
            if group == 'all':
                group = (-1, 0, 1)

            if group == 'active':
                group = (0,)

            if group == 'negtive':
                group = (-1,1)
            if int(lotid) > 0 and int(allmoney) > 0:
                sql = """
                    SELECT SQL_CALC_FOUND_ROWS *
                    FROM t_account_coupon
                    WHERE
                        f_uid=%s
                    AND
                        f_requiremoney<=%s
                    AND
                        f_activetime<%s
                    AND
                        f_expiretime>%s
                    AND
                        f_couponstatus in %s
                    ORDER BY f_crtime DESC
                    LIMIT %s, %s
                    """
                group = (0,)  # 选择优惠券时，一定是可用优惠券
                timenow =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute(sql, (uid, allmoney, timenow, timenow, group, offset, int(pagesize)))
            else:
                sql = """
                    SELECT SQL_CALC_FOUND_ROWS *
                    FROM t_account_coupon
                    WHERE  f_uid=%s AND f_couponstatus in %s
                    ORDER BY f_crtime DESC
                    LIMIT %s, %s
                    """
                self.cursor.execute(sql, (uid, group, offset, int(pagesize)))
            coupons = self.cursor.fetchall()
            self.cursor.execute(search_count)
            count = self.cursor.fetchone()
            count = count.get("FOUND_ROWS()")
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return {
                "count": count,
                "coupons": coupons
            }
