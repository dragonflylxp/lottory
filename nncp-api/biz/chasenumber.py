# coding: utf-8

import traceback
import ews
import define
from decimal import Decimal
from hook import Hook
from util.configer import *
from cbrpc import get_rpc_conn, RpcException
from commonEntity.User import UserBean
from commonEntity.Project import ProjBean
import session
from util.tools import Log

logger = Log().getLog()


@ews.route_sync_func('/chasenumber/place', kwargs={'ck': (UserWarning, ),
                                           'allmoney': (UserWarning, 'unsigned int'),
                                           'singlemoney': (UserWarning, 'unsigned int'),
                                           'expecttotal': (UserWarning, 'unsigned int'),
                                           'israndom': (UserWarning, 'int'),
                                           'stopprize': (UserWarning, 'int'),
                                           'lotid': (UserWarning, 'unsigned int'),
                                           'wtype': (UserWarning, 'unsigned int'),
                                           'beishu': (UserWarning, 'unsigned int'),
                                           'zhushu': (UserWarning, 'unsigned int'),
                                           'couponid': (UserWarning, 'int'),
                                           'expect': (UserWarning, ),
                                           'selecttype': (UserWarning, ),
                                           'fileorcode': (UserWarning, )})
@Hook.pre_hook('check_lotto')
def chasenumber(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    params = handler.json_args
    params.update({"uid": uid})
    pid = None
    try:
        #账户检查
        paymoney = UserBean().check_account(params)

        #下单
        with get_rpc_conn("trade") as proxy:
            try:
                resp = proxy.call("place_chasenumber", params)
            except RpcException as ex:
                raise ews.EwsError(ews.STATUS_RPC_TRADE_ERROR, ex.message)
    except:
        logger.error(traceback.format_exc())
        raise
    account = UserBean().user_account({"uid":uid})
    ret = {"cid": resp.get("cid"), "pid": resp.get("pid"), "balance": Decimal(account.get("balance"))-Decimal(paymoney), "balance_draw": account.get("balance_draw")}
    return handler.ok(ret)


@ews.route_sync_func('/chasenumber/cancel', kwargs={'ck': (UserWarning, ),
                                           'cid': (UserWarning, 'unsigned int')})
def chasecancel(handler, *args, **kwargs):
    ck = handler.json_args.get("ck")
    uid = session.get_by_ck(ck).get('uid')
    cid = handler.json_args.get("cid")

    try:
        with get_rpc_conn("trade") as proxy:
            try:
                params = {"uid": uid, "cid": cid}
                resp = proxy.call("cancel_chasenumber", params)
            except RpcException as ex:
                raise ews.EwsError(ews.STATUS_RPC_TRADE_ERROR, ex.message)
    except:
        logger.error(traceback.format_exc())
        raise
    return handler.ok(resp)


@ews.route_sync_func('/chasenumber/list', kwargs={'ck': (UserWarning, 'string')})
def chasenumber_list(handler, *args, **kwargs):
    ck = handler.json_args.get("ck")
    uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")

    params = {
        "uid": uid,
        "pageno": pageno,
        "pagesize": pagesize
    }
    ret = ProjBean().get_chasenumber_list(params)
    return handler.ok(ret)


@ews.route_sync_func('/chasenumber/detail', kwargs={'ck': (UserWarning, 'string'),
                                                    'lotid': (UserWarning, 'int'),
                                                    'cid': (UserWarning, 'int')})
def chasenumber_detail(handler, *args, **kwargs):
    lotid = handler.json_args.get("lotid")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    cid = handler.json_args.get("cid")
    params = {
        "uid": uid,
        "cid": cid,
        "lotid": lotid
    }
    ret = ProjBean(int(lotid)).get_chasenumber_router(params)
    return handler.ok(ret)

