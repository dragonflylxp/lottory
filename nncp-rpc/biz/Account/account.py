# encoding=utf-8

import inspect
import MySQLdb
import traceback
from dbpool import db_pool
from util.tools import Log
from util.configer import *
from logic.Account.useraccount import UserAccountLogic
from logic.Account.recharge import RechargeLogic

logger = Log().getLog()


class UserAccount(object):
    def user_account(self, uid):
        user_account = UserAccountLogic().user_account(uid)
        return user_account

    def user_account_detail(self, uid, biztype, pageno, pagesize):
        account_detail = UserAccountLogic().user_account_detail(uid, biztype, pageno, pagesize)
        return account_detail

    def check_account(self, uid, lotid, allmoney, couponid):
        return UserAccountLogic().check_account(uid, lotid, allmoney, couponid)

    def coupon_list(self, uid, group, lotid, allmoney, pageno, pagesize):
        return UserAccountLogic().coupon_list(uid, group, lotid, allmoney,  pageno, pagesize)


class Recharge():
    def recharge_order(self, uid, money, platform, channel, paychannel):
        return RechargeLogic().recharge_order(uid, money, platform, channel, paychannel)

    def get_recharge_order_by_oid(self, oid):
        return RechargeLogic().get_recharge_order_by_oid(oid)

    def recharge_notify(self, uid, oid, money, tradeno):
        return RechargeLogic().recharge_update_user_account(uid, oid, money, tradeno)

    def recharge_withdraw(self, uid, money, fee, card_no,  platform, channel, subchannel):
        return RechargeLogic().recharge_withdraw(uid, money, fee, card_no,  platform, channel, subchannel)

    def withdraw_orderstatus(self, oid, orderstatus, tradeno):
        return RechargeLogic().update_withdraw_status(oid, orderstatus, tradeno)

    def get_obligation_order(self, orderstatus):
        return RechargeLogic().search_obligation_order(orderstatus)

    def withdraw_refund(self, oid):
        return RechargeLogic().withdraw_refund(oid)

    def search_withdraw_order_by_oid(self, oid):
        return RechargeLogic().search_withdraw_order_by_oid(oid)

