#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: fileorcode.py
#
#        Author:
#   Description:
#        Create: 2018-03-30 20:23:55
# Last Modified: 2018-03-30 20:23:55
#   Changes Log:


import time
import ujson
import MQ
from hook import Hook
from cbrpc import get_rpc_conn, RpcException
from util.tools import Log

logger = Log().getLog()


@Hook.register_callback('user_reg')
def user_reg(ret, *args, **kwargs):
    params = args[0].json_args
    request = args[0].request
    ret = ujson.loads(ret)
    if ret.get("status") == "100":
        data = ret.get("data")
        msg = {
            "ip": request.remote_ip,
            "ua": request.headers.get("User-Agent", ""),
            "platform": params.get("platform", ""),
            "channel": params.get("channel", ""),
            "uid": data.get("uid", ""),
            "regtime": int(time.time())
        }
        MQ.send_msg('reg_suc', msg)


@Hook.register_callback('user_login')
def user_login(ret, *args, **kwargs):
    params = args[0].json_args
    request = args[0].request
    ret = ujson.loads(ret)
    if ret.get("status") == "100":
        data = ret.get("data")
        msg = {
            "ip": request.remote_ip,
            "ua": request.headers.get("User-Agent", ""),
            "platform": params.get("platform", ""),
            "channel": params.get("channel", ""),
            "uid": data.get("uid", ""),
            "logintime": int(time.time())
        }
        MQ.send_msg('login_suc', msg)
    else:
        params.update({
            "ip": request.remote_ip,
            "ua": request.headers.get("User-Agent", ""),
            "logintime": int(time.time())
            })
        MQ.send_msg('login_fail', params)


@Hook.register_callback('user_recharge')
def user_recharge(ret, *args, **kwargs):
    params = args[0].json_args
    request = args[0].request
    route_path = args[0].route_path
    #ret = ujson.loads(ret)
    #if ret.get("status") == "100":
    #区分不同充值渠道
    try:
        recharge_channel = route_path.split('/')[1]
        msg = {"paychannel": recharge_channel}
        module = "account"
        method = "search_recharge_order"
        orderinfo = {}
        if recharge_channel == 'jiuzhao':
            if ret == "success":
                oid = params.get("outTradeNo")
                with get_rpc_conn(module) as proxy:
                    try:
                        orderinfo = proxy.call(method, {"oid": oid})
                        orderinfo = ujson.loads(orderinfo)
                    except:
                        logger.error(traceback.format_exc())
                msg.update({
                    "oid": oid,
                    "uid": orderinfo.get("f_uid", ""),
                    "platform": orderinfo.get("f_platform", ""),
                    "realMoney": params.get("amount", ""),
                    "rechargeMoney": params.get("amount", ""),
                    "paytime": params.get("thirdPayTime", "")
                })
                MQ.send_msg('recharge_suc', msg)
            else:
                pass
        elif recharge_channel == 'lianlian':
            if ret.get("ret_code") == "0000":
                oid = params.get("no_order")
                with get_rpc_conn(module) as proxy:
                    try:
                        orderinfo = proxy.call(method, {"oid": oid})
                        orderinfo = ujson.loads(orderinfo)
                    except:
                        logger.error(traceback.format_exc())
                msg.update({
                    "oid": oid,
                    "uid": orderinfo.get("f_uid", ""),
                    "platform": orderinfo.get("f_platform", ""),
                    "realMoney": params.get("money_order", ""),
                    "rechargeMoney": params.get("money_order", "")
                })
                MQ.send_msg('recharge_suc', msg)
            else:
                pass
        else:
            pass
    except:
        logger.error(traceback.format_exc())
