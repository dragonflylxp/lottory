# coding: utf-8

import traceback
import ews
import define
from decimal import Decimal
from hook import Hook
from util.configer import *
from cbrpc import get_rpc_conn, RpcException
from commonEntity.Ssq import SsqBean
from commonEntity.User import UserBean
import session
from util.tools import Log

logger = Log().getLog()


@ews.route_sync_func('/ssq/issue')
def ssq_issue(handler, *args, **kwargs):
    ret = SsqBean().get_ssq_expect_list()
    return handler.ok(ret)


@ews.route_sync_func('/ssq/trade', kwargs={'ck': (UserWarning,),
                                           'lotid': (UserWarning, 'unsigned int'),
                                           'wtype': (UserWarning, 'unsigned int'),
                                           'beishu': (UserWarning, 'unsigned int'),
                                           'zhushu': (UserWarning, 'unsigned int'),
                                           'allmoney': (UserWarning, 'unsigned int'),
                                           'couponid': (UserWarning, 'int'),
                                           'expect': (UserWarning,),
                                           'selecttype': (UserWarning,),
                                           'fileorcode': (UserWarning,)})
@Hook.pre_hook('check_lotto')
def trade(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    params = handler.json_args
    params.update({"uid": uid})
    pid = None
    try:
        # 账户检查
        paymoney = UserBean().check_account(params)

        # 下单
        with get_rpc_conn("trade") as proxy:
            try:
                resp = proxy.call("place_order", params)
            except RpcException as ex:
                raise ews.EwsError(ews.STATUS_RPC_TRADE_ERROR, ex.message)
    except:
        logger.error(traceback.format_exc())
        raise
    account = UserBean().user_account({"uid": uid})
    ret = {"pid": resp.get("pid"), "balance": Decimal(account.get("balance"))-Decimal(paymoney), "balance_draw": account.get("balance_draw")}
    return handler.ok(ret)
