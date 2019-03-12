# coding: utf-8

import traceback
import define
import ews
from decimal import Decimal

import ujson

import time
from hook import Hook
from util.configer import *
from cbrpc import get_rpc_conn, RpcException
from commonEntity.User import UserBean
from commonEntity.Jz import JczqBean
import session
from util.tools import Log

logger = Log().getLog()


@ews.route_sync_func('/jz/trade', kwargs={'ck': (UserWarning,),
                                          'lotid': (UserWarning, 'unsigned int'),
                                          'wtype': (UserWarning, 'unsigned int'),
                                          'beishu': (UserWarning, 'unsigned int'),
                                          'zhushu': (UserWarning, 'unsigned int'),
                                          'ggtype': (UserWarning,),
                                          'allmoney': (UserWarning, 'unsigned int'),
                                          'couponid': (UserWarning, 'int'),
                                          'isquchu': (UserWarning, 'int'),
                                          'danma': (UserWarning,),
                                          'rqlist': (UserWarning,),
                                          'ratelist': (UserWarning,),
                                          'fileorcode': (UserWarning,)})
@Hook.pre_hook('check_lotto')
def trade(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    fileorcode = handler.json_args.get("fileorcode")
    params = handler.json_args
    params.update({"uid": uid})
    pid = None

    firsttime, lasttime = JczqBean().get_firsttime_and_lasttime(fileorcode)
    params.update({
        "uid": uid,
        "firsttime": firsttime,
        "lasttime": lasttime
    })
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
    ret = {"pid": resp.get("pid"), "balance": Decimal(account.get("balance")) - Decimal(paymoney),
           "balance_draw": account.get("balance_draw")}
    return handler.ok(ret)


@ews.route_sync_func('/jz/matches')
def jz_matches(handler, *args, **kwargs):
    platform = handler.json_args.get("platform", "")
    ret = JczqBean().get_on_sale_matches(platform)
    return handler.ok(ret)


@ews.route_sync_func('/jz/follow', kwargs={'ck': (UserWarning,),
                                           'lotid': (UserWarning, 'unsigned int'),
                                           'beishu': (UserWarning, 'unsigned int'),
                                           'allmoney': (UserWarning, 'unsigned int'),
                                           'pid': (UserWarning, 'int')})
def trade_follow(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pid = handler.json_args.get("pid")
    lotid = handler.json_args.get("lotid")
    allmoney = handler.json_args.get("allmoney")
    beishu = handler.json_args.get("beishu")

    params = handler.json_args
    params.update({"uid": uid,
                   "couponid": 0})
    try:

        module = "trade"
        method = "proj_detail"
        proj_detail = {}
        with get_rpc_conn(module) as proxy:
            proj_detail = proxy.call(method, params)
            proj_detail = ujson.loads(proj_detail)

        if not proj_detail:
            raise ews.EwsError(ews.STATUS_PROJ_NOT_FOUND)
        ptype = proj_detail.get("f_ptype")
        if str(ptype) != "1":
            raise ews.EwsError(ews.STATUS_PROJ_FORBID_FOLLOW)

        orderstatus = proj_detail.get("f_orderstatus")

        if orderstatus in [2, 4]:
            raise ews.EwsError(ews.STATUS_PROJ_FORBID_FOLLOW)

        firsttime = proj_detail.get("f_firsttime")
        if firsttime < time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()):
            raise ews.EwsError(ews.STATUS_PROJ_DEADLINE)

        _allmoney = proj_detail.get("f_allmoney")
        _beishu = proj_detail.get("f_beishu")
        # 下单

        if int(beishu) > 10000:
            raise ews.EwsError(ews.STATUS_PROJ_ALLMONEY_ERROR)
        single = int(float(_allmoney))/int(_beishu)
        if allmoney != str(single * int(beishu)):
            raise ews.EwsError(ews.STATUS_PROJ_ALLMONEY_ERROR)

        # 账户检查
        paymoney = UserBean().check_account(params)
        params = {
            'lotid': lotid,
            'wtype': proj_detail.get("f_wtype"),
            'beishu': beishu,
            'zhushu': proj_detail.get("f_zhushu"),
            'ggtype': proj_detail.get("f_ggtype"),
            'allmoney': allmoney,
            'couponid': proj_detail.get("f_couponid"),
            'isquchu': proj_detail.get("f_isquchu"),
            'danma': proj_detail.get("f_danma"),
            'rqlist': proj_detail.get("f_rqlist"),
            'ratelist': proj_detail.get("f_ratelist"),
            'fileorcode': proj_detail.get("f_fileorcode"),
            'uid': uid,
            'fid': pid,
            'ptype': '-1',
            'firsttime': proj_detail.get("f_firsttime"),
            'lasttime': proj_detail.get("f_lasttime")
        }
        with get_rpc_conn("trade") as proxy:
            try:
                resp = proxy.call("place_order", params)
            except RpcException as ex:
                raise ews.EwsError(ews.STATUS_RPC_TRADE_ERROR, ex.message)
    except:
        logger.error(traceback.format_exc())
        raise

    account = UserBean().user_account({"uid": uid})
    ret = {"pid": resp.get("pid"), "balance": Decimal(account.get("balance")) - Decimal(paymoney),
           "balance_draw": account.get("balance_draw")}
    return handler.ok(ret)
