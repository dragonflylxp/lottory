# coding: utf-8
import random

import ews
import time
from cbrpc import CBClient
from util.configer import *
import traceback
import session
import ujson
from hook import Hook
from dbpool import db_pool
import rediskey
import define
from commonEntity.Recharge import RechargeBean
from util.tools import Log
from wechat.Monitor import send_textcard_message

global logger
logger = Log().getLog()


@ews.route_sync_func('/recharge/list', kwargs={})
def recharge_list(handler, *args, **kwargs):

    ret = [{
        "channel": "1001",
        "logo": "",
        "payname": "微信支付",
    }]
    return ret

@ews.route_sync_func('/recharge/place_order', kwargs={})
def recharge_place_order(handler, *args, **kwargs):
    money = handler.json_args.get("money", "")
    ck = handler.json_args.get("ck")
    paychannel = handler.json_args.get("paychannel", "1001")
    uid = session.get_by_ck(ck).get('uid', "")
    channel = handler.json_args.get("channel", "")
    card_no = handler.json_args.get("card_no", "")
    no_agree = handler.json_args.get("no_agree", "")
    bind_mobile = handler.json_args.get("bind_mobile", "")
    platform = handler.json_args.get("platform", "")
    params = {
        "money": money,
        "paychannel": paychannel,
        "uid": uid,
        "channel": channel,
        "ip": handler.request.remote_ip,
        "card_no": card_no,
        "no_agree": no_agree,
        "bind_mobile": bind_mobile,
        "platform": platform
    }
    path = ""
    try:
        ret = RechargeBean().place_order(params)
    except:
        logger.error(traceback.format_exc())
        send_textcard_message(msgtype="充值异常告警", servicename="nncp-api",
                              exceptinfo="充值下单错误 uid:%s paychannel %s"%(uid, paychannel))
        raise
    return handler.ok(ret)
#
@ews.route_sync_func('/jiuzhao/notice', kwargs={})
@Hook.post_hook('user_recharge')
def jiuzhao_notice(handler, *args, **kwargs):
    """
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    logger.info(handler.json_args)
    params = handler.json_args
    ret = RechargeBean().jiuzhao_recharge_notice(params)
    return ret

@ews.route_sync_func('/lianlian/notice', kwargs={})
@Hook.post_hook('user_recharge')
def lianlian_notice(handler, *args, **kwargs):
    """
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    logger.info(handler.request.body)
    params = ujson.loads(handler.request.body)
    ret = RechargeBean().lianlian_recharge_notice(params)
    return ret

@ews.route_sync_func('/lianlian/withdraw', kwargs={'ck': (UserWarning, 'string')})
def lianlian_withdraw(handler, *args, **kwargs):
    """
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    ck = handler.json_args.get("ck")
    code = handler.json_args.get("code", "")
    uid = session.get_by_ck(ck).get('uid', "")
    logger.info(handler.json_args)
    params = handler.json_args

    money = handler.json_args.get("money")
    params.update({
        "uid": uid,
        "fee": define.WITHDRAW_FEE,
        "code": code
    })

    if float(money) >= 100:
        params.update({
            "fee": 0
        })
    ret = RechargeBean().lianlian_withdraw(params)
    return handler.ok(ret)

@ews.route_sync_func('/lianlian/withdraw/notice', kwargs={})
def lianlian_withdraw_notice(handler, *args, **kwargs):
    """
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    logger.info(handler.request.body)
    params = ujson.loads(handler.request.body)
    ret = RechargeBean().lianlian_withdraw_notice(params)
    return ret

@ews.route_sync_func('/recharge/bank/bindlist', kwargs={})
def recharge_bank_bindlist(handler, *args, **kwargs):
    """
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    ck = handler.json_args.get("ck")
    uid = session.get_by_ck(ck).get('uid', "")
    ret = RechargeBean().get_bank_cardlist(uid)
    return handler.ok(ret)
