# encoding=utf-8

import inspect
import MySQLdb
import traceback

import datetime
import define
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from common.dbs import BaseModel, access
from decimal import Decimal
from cbrpc import RpcException
logger = Log().getLog()


class RechargeLogic(BaseModel):
    @access("w")
    def recharge_order(self, uid, money, platform, channel, paychannel):
        oid = None
        try:
            sql = """
                  INSERT INTO t_order_recharge
                    (
                      f_uid,
                      f_rechargemoney,
                      f_platform,
                      f_channel,
                      f_paychannel
                    )
                    VALUES
                    (%s, %s, %s, %s,  %s);

              """

            self.cursor.execute(sql, (uid, money, platform, channel, paychannel))
            oid = self.cursor.lastrowid
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise
        finally:
            return oid


    @access("w")
    def recharge_update_user_account(self, uid, oid, money, tradeno):
        try:
            sql = """
                  UPDATE t_order_recharge
                  SET f_realmoney = %s, f_transaction_no=%s , f_orderstatus=1
                  WHERE f_uid = %s and f_orderstatus = 0 and f_oid=%s

              """
            account_sql = """
                UPDATE
                    t_account_info
                SET
                    f_balance_recharge=%s,
                    f_balance_draw=%s
                WHERE f_uid=%s
            """

            select_account = """
                SELECT * FROM t_account_info
                WHERE f_uid=%s for UPDATE
            """
            # 流水日志
            account_log_sql = """
                  INSERT INTO t_account_log(
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
            money = float(money)
            self.cursor.execute(select_account, (uid,))
            user_account = self.cursor.fetchone()
            balance_recharge = user_account.get("f_balance_recharge")
            balance_draw = user_account.get("f_balance_draw")
            balance_recharge = float(balance_recharge)
            balance_draw = float(balance_draw)

            # 充值金额， 充值账户和提款账户各入50%(TODO 比例系数可调整)
            self.cursor.execute(account_sql, (balance_recharge+money*0.5, balance_draw+money*0.5, uid))
            self.cursor.execute(account_log_sql, (uid, oid, 0, define.ACCOUNT_LOG_TYPE_RECHARGE, money, balance_recharge+money*0.5, balance_draw+money*0.5, 0))
            self.cursor.execute(sql, (money, tradeno, uid, oid))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise
        finally:
            pass

    @access("r")
    def get_recharge_order_by_oid(self, oid):
        orderinfo = {}
        try:
            sql = """
                     SELECT *
                     FROM  t_order_recharge
                     WHERE f_oid = %s
                     LIMIT 1
                 """

            self.cursor.execute(sql, (oid,))
            orderinfo = self.cursor.fetchone()
        except Exception as e:
            logger.error(traceback.format_exc())
            raise
        finally:
            return orderinfo

    @access("w")
    def recharge_withdraw(self, uid, money, fee, card_no, platform, channel, subchannel):
        oid = None
        try:
            sql = """
                  INSERT INTO t_order_draw
                    (
                      f_uid,
                      f_money,
                      f_fee,
                      f_card_no,
                      f_platform,
                      f_channel,
                      f_subchannel
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s);

              """
            account_sql = """
                UPDATE
                    t_account_info
                SET
                    f_balance_draw=%s
                WHERE f_uid=%s
            """

            select_account = """
                SELECT * FROM t_account_info
                WHERE f_uid=%s for UPDATE
            """
            # 流水日志
            # 流水日志
            account_log_sql = """
                  INSERT INTO t_account_log(
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
            self.cursor.execute(select_account, (uid, ))
            user_account = self.cursor.fetchone()
            balance_recharge = user_account.get("f_balance_recharge")
            balance_draw = user_account.get("f_balance_draw")
            balance = float(balance_draw)

            consum = (float(money) + float(fee))
            if consum > balance:
                raise RpcException("账户余额不足")

            total = float(balance) - consum
            self.cursor.execute(account_sql, (total, uid))
            self.cursor.execute(sql, (uid, money, fee, card_no, platform, channel, subchannel))
            oid = self.cursor.lastrowid
            total = float(balance) - float(money)
            self.cursor.execute(account_log_sql,
                                (uid, oid, 0, define.ACCOUNT_LOG_TYPE_WITHDRAW, float(money), balance_recharge, total, 0))
            if float(fee) > 0:
                total = total - float(fee)
                self.cursor.execute(account_log_sql,
                                (uid, oid, 0, define.ACCOUNT_LOG_TYPE_WITHDRAW_FEE, float(fee), balance_recharge, total,0))
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise

        return oid

    @access("w")
    def update_withdraw_status(self, oid,  orderstatus, tradeno):
        status = False
        try:
            sql = """
                   UPDATE t_order_draw
                   SET f_orderstatus = %s, f_transaction_no = %s
                   WHERE f_oid=%s and f_orderstatus=1
                """

            status = self.cursor.execute(sql, (orderstatus, tradeno, oid))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise
        return True if status == 1 else False

    @access("r")
    def search_withdraw_order_by_oid(self, oid):
        orderinfo = {}
        try:
            sql = """
                         SELECT *
                         FROM  t_order_draw
                         WHERE f_oid = %s
                         LIMIT 1
                     """

            self.cursor.execute(sql, (oid,))
            orderinfo = self.cursor.fetchone()
        except Exception as e:
            logger.error(traceback.format_exc())
            raise
        finally:
            return orderinfo

    @access("r")
    def search_obligation_order(self, orderstatus=1):

        orderinfo = {}
        try:
            sql = """
                SELECT *
                FROM  t_order_draw
                WHERE f_orderstatus = %s
            """

            self.cursor.execute(sql, (orderstatus, ))
            orderinfo = self.cursor.fetchall()
        except Exception as e:
            logger.error(traceback.format_exc())
            raise
        finally:
            return orderinfo

    @access("w")
    def withdraw_refund(self, oid):
        status = False
        try:

            select_order = """
                SELECT * 
                FROM t_order_draw 
                WHERE f_oid=%s and f_orderstatus=-1
            """
            sql = """
                       UPDATE t_order_draw
                       SET f_orderstatus = %s
                       WHERE f_oid=%s
                    """

            account_sql = """
                            UPDATE
                                t_account_info
                            SET
                                f_balance_draw=%s
                            WHERE f_uid=%s
                        """

            select_account = """
                            SELECT * FROM t_account_info
                            WHERE f_uid=%s for UPDATE
                        """
            # 流水日志
            account_log_sql = """
                              INSERT INTO t_account_log(
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

            self.cursor.execute(select_order, (oid,))
            orderinfo = self.cursor.fetchone()

            if not orderinfo:
                logger.info("order not found :%s", oid)
                return status
            uid = orderinfo.get("f_uid")
            money = orderinfo.get("f_money")
            fee = orderinfo.get("f_fee")

            self.cursor.execute(select_account, (uid,))
            user_account = self.cursor.fetchone()
            balance_recharge = user_account.get("f_balance_recharge")
            balance_draw = user_account.get("f_balance_draw")
            balance = float(balance_draw)

            refund = (float(money) + float(fee))

            total = float(balance) + refund
            self.cursor.execute(account_sql, (total, uid))
            self.cursor.execute(account_log_sql,
                                (uid, oid, 0, define.ACCOUNT_LOG_TYPE_WITHDRAW_REFUND, refund, balance_recharge, total, 0))

            status = self.cursor.execute(sql, (define.WITHDRAW_STATUS_REFUND, oid))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(traceback.format_exc())
            raise
        return True if status == 1 else False
