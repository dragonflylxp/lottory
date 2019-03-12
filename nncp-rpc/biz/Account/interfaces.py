#encoding=utf-8
from Account.account import UserAccount, Recharge
import traceback
import ujson
from util.tools import Log
from common.json_format import rpc_dumps
logger = Log().getLog()

"""收集业务类方法作为RPC总入口
"""
class Interfaces(object):
    def user_account(self, params):
        """
        账户信息
        :param params:
        :return:
        """
        uid = params.get("uid")
        ret = UserAccount().user_account(uid)
        return rpc_dumps(ret)

    def user_account_detail(self, params):
        """
        :param params:
        :return:
        """
        uid = params.get("uid")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype",)
        ret = UserAccount().user_account_detail(uid, biztype, pageno, pagesize)

        return rpc_dumps(ret)

    def check_account(self, params):
        """
        校验账户余额
        """
        uid = params.get("uid")
        lotid = params.get("lotid")
        money = params.get("allmoney")
        couponid = params.get("couponid")
        paystatus, paymoney = UserAccount().check_account(uid, lotid, money, couponid)
        ret = {
            "paystatus": paystatus,
            "paymoney": paymoney
        }
        return rpc_dumps(ret)

    def recharge_order(self, params):
        """

        :param params:
        :return:
        """
        uid = params.get("uid", "")
        money = params.get("money", "")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        paychannel = params.get("paychannel", "")

        oid = Recharge().recharge_order(uid, money, platform, channel, paychannel)
        return oid

    def search_recharge_order(self, params):
        """

        :param params:
        :return:
        """
        oid = params.get("outTradeNo", "") or params.get("oid")
        ret = Recharge().get_recharge_order_by_oid(oid)
        return rpc_dumps(ret)

    def recharge_notify(self, params):
        """
        通知入账
        :param params:
        :return:
        """
        uid = params.get("uid")
        oid = params.get("oid")
        money = params.get("money")
        tradeno = params.get("tradeno")
        Recharge().recharge_notify(uid, oid, money, tradeno)
        return True

    def recharge_withdraw(self, params):
        """

        :param params:
        :return:
        """
        uid = params.get("uid", "")
        money = params.get("money", "")
        fee = params.get("fee", "")
        card_no = params.get("card_no")
        platform = params.get("platform", "")
        channel = params.get("channel", "")
        subchannel = params.get("subchannel", "")

        oid = Recharge().recharge_withdraw(uid, money, fee, card_no, platform, channel, subchannel)
        return oid

    def bind_bank_card_info(self, params):
        """
        绑定银行卡信息
        :param params:
        :return:
        """

        uid = params.get("uid")
        cardno = params.get("cardno")
        f_bank_main = params.get("f_bank_main")

    def update_withdraw_orderstatus(self, params):
        """
        提款成功
        :param params:
        :return:
        """
        oid = params.get("oid")
        orderstatus = params.get("orderstatus")
        tradeno = params.get("tradeno")
        status = Recharge().withdraw_orderstatus(oid, orderstatus, tradeno)

        return status

    def coupon_list(self, params):
        uid = params.get("uid")
        group = params.get("group")
        lotid = params.get("lotid")
        allmoney = params.get("allmoney")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        clist = UserAccount().coupon_list(uid, group, lotid, allmoney, pageno, pagesize)
        return rpc_dumps(clist)

    def get_obligation_order(self, params):
        orderstatus = params.get("orderstatus")
        orders = Recharge().get_obligation_order(orderstatus)
        return rpc_dumps(orders)

    def withdraw_refund(self, params):
        oid = params.get("oid")
        status = Recharge().withdraw_refund(oid)
        return status

    def search_withdraw_order(self, params):
        """
        :param params:
        :return:
        """
        oid = params.get("outTradeNo", "") or params.get("oid")
        ret = Recharge().search_withdraw_order_by_oid(oid)
        return rpc_dumps(ret)