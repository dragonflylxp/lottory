#!/usr/bin/env python
# encoding: utf-8

import traceback
import copy
import ujson
import datetime
import xmsgbus
import define
from logic.msgrecord import MsgRecord
from dbpool import db_pool
from util.tools import Log
from logic.Account.useraccount import UserAccountLogic

global logger
logger = Log().getLog()

@xmsgbus.subscribe_callback_register("TRADE#ORDER#PRIZED")
def project_prized(channel,msg):
    """执行派奖，账户加钱
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)
    try:
        UserAccountLogic().order_prize(msg)
    except:
        logger.error(traceback.format_exc())


@xmsgbus.subscribe_callback_register("TRADE#ORDER#PRINTED")
def order_pay(channel,msg):
    """订单出票成功，解冻扣款
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)
    pid = msg.get("pid", None)
    uid = msg.get("uid")
    mid = msg.get("mid")
    lotid = msg.get("lotid")
    if pid is None:
        return
    params = {
        "mid": mid,
        "pid": pid,
        "uid": uid,
        "lotid": lotid
    }
    paystatus = UserAccountLogic().order_pay(params)
    if paystatus != define.ORDER_PAY_STATUS_SUCC:
        #解冻扣款失败处理, 告警+重试
        logger.error("Order unfreeze and pay faild!lotid=%s|pid=%s", lotid, pid)


@xmsgbus.subscribe_callback_register("TRADE#ORDER#PLACED")
def order_freeze(channel,msg):
    """订单下单成功，冻结扣款
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)
    pid = msg.get("pid")
    uid = msg.get("uid")
    lotid = msg.get("lotid")
    mid = msg.get("mid")
    allmoney = float(msg.get("allmoney"))
    couponid = int(msg.get("couponid"))

    #冻结扣款
    params = {
        "uid": uid,
        "pid": pid,
        "lotid": lotid,
        "couponid": couponid,
        "allmoney": allmoney,
        "mid": mid
    }
    paystatus, paymoney, couponmoney = UserAccountLogic().order_freeze(params)
    logger.debug('pay status:%s', paystatus)

    #异步通知支付状态
    msg = {
        "uid": uid,
        "pid": pid,
        "lotid": lotid,
        "allmoney": allmoney,
        "paymoney": paymoney,
        "couponmoney": couponmoney,
        "couponid": couponid,
        "paystatus": paystatus
    }

    params = {
        "oid": pid,
        "lotid": lotid,
        "msgtype": define.MSG_TYPE_ORDER_PAID,
        "msgcnt": ujson.dumps(msg)
    }
    try:
        mid = MsgRecord().insert(params)
        msg.update({"mid": mid})
    except:
        # 防止重复插入
        logger.error(traceback.format_exc())
        raise
    else:
        rds = db_pool.get_redis("msgbus")
        rds.publish("TRADE#ORDER#PAID", ujson.dumps(msg))
    return


@xmsgbus.subscribe_callback_register("TRADE#CHASENUMBER#PLACED")
def order_chasepay(channel,msg):
    """追号下单成功，直接扣款
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)
    cid = msg.get("cid")
    pid = msg.get("pid")
    uid = msg.get("uid")
    lotid = msg.get("lotid")
    mid = msg.get("mid")
    allmoney = float(msg.get("allmoney"))
    couponid = int(msg.get("couponid"))

    #直接扣款
    params = {
        "uid": uid,
        "cid": cid,
        "pid": pid,
        "lotid": lotid,
        "couponid": couponid,
        "allmoney": allmoney,
        "mid": mid
    }
    paystatus, paymoney, couponmoney = UserAccountLogic().order_chasepay(params)

    #异步通知支付状态
    msg = {
        "uid": uid,
        "cid": cid,
        "pid": pid,
        "lotid": lotid,
        "allmoney": allmoney,
        "paymoney": paymoney,
        "couponmoney": couponmoney,
        "couponid": couponid,
        "paystatus": paystatus
    }

    params = {
        "oid": cid,
        "lotid": lotid,
        "msgtype": define.MSG_TYPE_CHASENUMBER_PAID,
        "msgcnt": ujson.dumps(msg)
    }
    try:
        mid = MsgRecord().insert(params)
        msg.update({"mid": mid})
    except:
        # 防止重复插入
        logger.error(traceback.format_exc())
        raise
    else:
        rds = db_pool.get_redis("msgbus")
        rds.publish("TRADE#CHASENUMBER#PAID", ujson.dumps(msg))
    return
