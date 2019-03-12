#!/usr/bin/env python
# encoding: utf-8

import traceback
import xmsgbus
import ujson
import define
from decimal import Decimal
from dbpool import db_pool
from logic.msgrecord import MsgRecord
from logic import Trade, Ticket
from alert import AlertMoniter
from common import MQ
from util.tools import Log

global logger
logger = Log().getLog()

@xmsgbus.subscribe_callback_register("TRADE#ORDER#PAID")
def order_update_paid(channel,msg):
    """投注订单已支付，更新订单状态
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)

    #校验订单数据
    mid = msg.pop("mid")
    lotid = int(msg.get("lotid", 0))
    pid = msg.get("pid")
    uid = msg.get("uid")
    couponid = msg.get("couponid")
    paymoney = msg.get("paymoney")
    couponmoney = msg.get("couponmoney")

    #更新订单状态
    obj_order = Trade.get(lotid)
    paystatus = msg.get("paystatus")
    try:
        params = {
            "mid": mid,
            "pid": pid,
            "couponid": couponid,
            "paymoney": paymoney,
            "couponmoney": couponmoney,
            "originstatus": define.ORDER_STATUS_UNPAY,
            "targetstatus": define.ORDER_STATUS_SUCC if paystatus == define.ORDER_PAY_STATUS_SUCC else define.ORDER_STATUS_FAILPAY,
            "remark": define.PAY_STATUS_REMARK[paystatus]
        }
        obj_order.update_order_status(params)
    except:
        #更新订单状态异常处理, 告警+重试
        logger.error(traceback.format_exc())
        raise
    else:
        if paystatus == define.ORDER_PAY_STATUS_SUCC:
            params = {
                "lotid": lotid,
                "oid": pid,
                "msgtype": define.MSG_TYPE_ORDER_SUCCPAY,
                "msgcnt": ujson.dumps(msg)
            }
            try:
                mid = MsgRecord().insert(params)
                msg.update({"mid": mid})
            except:
                # 防止重复插入
                logger.error(traceback.format_exc())
            else:
                rds = db_pool.get_redis("msgbus")
                rds.publish("TRADE#ORDER#SUCCPAY", ujson.dumps(msg))

                # 活动消息: [用户购买成功]
                order = obj_order.get_project_by_pid(pid)
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
                MQ.send_msg('buy_suc', activity_msg)
        else:
            pass

@xmsgbus.subscribe_callback_register("TRADE#CHASENUMBER#PAID")
def chasenumber_update_paid(channel,msg):
    """追号订单已支付，更新订单状态
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)

    #校验订单数据
    mid = msg.pop("mid")
    lotid = int(msg.get("lotid", 0))
    cid = msg.get("cid")
    pid = msg.get("pid")
    couponid = msg.get("couponid")
    paymoney = msg.get("paymoney")
    couponmoney = msg.get("couponmoney")

    #更新订单状态
    obj_order = Trade.get(lotid)
    paystatus = msg.get("paystatus")
    try:
        params = {
            "mid": mid,
            "cid": cid,
            "pid": pid,
            "couponid": couponid,
            "paymoney": paymoney,
            "couponmoney": couponmoney,
            "chase_originstatus": define.CHASE_STATUS_UNPAY,
            "chase_targetstatus": define.CHASE_STATUS_SUCC if paystatus == define.ORDER_PAY_STATUS_SUCC else define.CHASE_STATUS_FAILPAY,
            "order_originstatus": define.ORDER_STATUS_UNPAY,
            "order_targetstatus": define.ORDER_STATUS_SUCC if paystatus == define.ORDER_PAY_STATUS_SUCC else define.ORDER_STATUS_FAILPAY,
            "remark": define.PAY_STATUS_REMARK[paystatus]
        }
        obj_order.update_chasenumber_status(params)
    except:
        #更新订单状态异常处理, 告警+重试
        logger.error(traceback.format_exc())
        raise
    else:
        # 通知第一期订单成功支付
        if paystatus == define.ORDER_PAY_STATUS_SUCC:
            params = {
                "lotid": lotid,
                "oid": pid,
                "msgtype": define.MSG_TYPE_ORDER_SUCCPAY,
                "msgcnt": ujson.dumps(msg)
            }
            try:
                mid = MsgRecord().insert(params)
                msg.update({"mid": mid})
            except:
                # 防止重复插入
                logger.error(traceback.format_exc())
            else:
                rds = db_pool.get_redis("msgbus")
                rds.publish("TRADE#ORDER#SUCCPAY", ujson.dumps(msg))
        else:
            pass


@xmsgbus.subscribe_callback_register("key_tickets:print:result")
def ticket_status_update(channel,msg):
    """票状态更新,更新订单表
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)
    tid = msg.get("tid")
    pid = msg.get("pid")
    uid = msg.get("uid")
    lotid =  msg.get("lotid")
    ticketstatus = msg.get("statusCode", "")
    if not ticketstatus:
        logger.error("Ticket status update with empty statusCode!")
        return
    orderstatus, isjprize = tickets_update_project(lotid, pid, uid)
    logger.debug('Order status update! lotid=%s|pid=%s|orderstatus=%s|isjprize=%s|tid=%s|ticketstatus=%s',
            lotid, pid, orderstatus, isjprize, tid, ticketstatus)


def tickets_update_project(lotid, pid, uid):
    obj_ticket = Ticket.get(int(lotid))
    prj_tickets_status = obj_ticket.get_tickets_status_by_project(pid)
    ticketnum = sum(ts["cnt"] for ts in prj_tickets_status)
    prj_tickets_status = {ts["status"]:ts["cnt"] for ts in prj_tickets_status}
    logger.debug("prj_tickets_status=%s", prj_tickets_status)

    orderstatus = isjprize = None
    rds = db_pool.get_redis("msgbus")
    # 全部出票
    if define.TICKET_STATUS_SAVED not in prj_tickets_status:
        # 全部算奖
        if define.TICKET_STATUS_PRINTED not in prj_tickets_status:
            # 全部未中奖
            if define.TICKET_STATUS_PRIZED not in prj_tickets_status:
                # 全部撤单
                if define.TICKET_STAUTS_LOSE not in prj_tickets_status:
                    orderstatus = define.ORDER_STATUS_CANCEL
                    isjprize = define.ORDER_JPRIZE_UNCAL
                else:
                    if define.TICKET_STATUS_CANCEL in prj_tickets_status:
                        orderstatus = define.ORDER_STATUS_PRINT_PART
                    else:
                        orderstatus = define.ORDER_STATUS_PRINT_ALL
                    isjprize = define.ORDER_JPRIZE_LOSE
            else:
                #部分撤单
                if define.TICKET_STATUS_CANCEL in prj_tickets_status:
                    orderstatus = define.ORDER_STATUS_PRINT_PART
                else:
                    orderstatus = define.ORDER_STATUS_PRINT_ALL
                isjprize = define.ORDER_JPRIZE_PRIZE

            #全部票已经算奖或者撤单, 触发派奖
            #票状态入库与消息推送异步，此处会有重复消息
            rds.publish("TRADE#ORDER#PRIZE", ujson.dumps({"lotid": lotid, "pid": pid, "uid": uid}))
        else:
            if define.TICKET_STATUS_CANCEL in prj_tickets_status:
                orderstatus = define.ORDER_STATUS_PRINT_PART
            else:
                orderstatus = define.ORDER_STATUS_PRINT_ALL
            isjprize = define.ORDER_JPRIZE_UNCAL
        obj_order = Trade.get(int(lotid))
        order = None
        try:
            obj_order.tickets_update_project(pid, orderstatus, isjprize)
            order = obj_order.get_project_by_pid(pid)
            # 活动消息: [方案出票成功]
            if orderstatus in [define.ORDER_STATUS_PRINT_PART, define.ORDER_STATUS_PRINT_ALL]:
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
                MQ.send_msg('print_suc', activity_msg)
        except:
            pass
        else:
            #非追号订单， 通知解冻扣款
            if order.get("f_chaseid", 0) == 0:
                msg = {
                    "lotid": lotid,
                    "pid": pid,
                    "uid": uid
                }
                params = {
                    "lotid": lotid,
                    "oid": pid,
                    "msgtype": define.MSG_TYPE_TICKET_PRINTED,
                    "msgcnt": ujson.dumps(msg)
                }
                try:
                    mid = MsgRecord().insert(params)
                    msg.update({"mid": mid})
                except:
                    pass
                    # 防止重复插入
                    #logger.error(traceback.format_exc())
                else:
                    rds.publish("TRADE#ORDER#PRINTED", ujson.dumps(msg))
            else:
                pass
    else:
        pass
    return orderstatus, isjprize

@xmsgbus.subscribe_callback_register("TRADE#ORDER#PRIZE")
def project_prize(channel,msg):
    """校验中奖金额,执行派奖
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    try:
        unpack = ujson.loads(msg)
        lotid = unpack.get("lotid")
        pid = unpack.get("pid")
        uid = unpack.get("uid")

        obj_ticket = Ticket.get(int(lotid))
        prj_tickets_status = obj_ticket.get_tickets_status_by_project(pid)
        ticketnum = sum(ts["cnt"] for ts in prj_tickets_status)
        prj_tickets_status = {ts["status"]:{"cnt":ts["cnt"],
                                            "allmoney": ts["allmoney"],
                                            "calgetmoney": ts["calgetmoney"],
                                            "getmoney": ts["getmoney"]} for ts in prj_tickets_status}

        rds = db_pool.get_redis("msgbus")
        obj_order = Trade.get(int(lotid))
        order = obj_order.get_project_by_pid(pid)
        getmoney = Decimal(0)
        if order.get("f_isjprize") == define.ORDER_JPRIZE_PRIZED:
            logger.warning("彩种lotid=%s方案pid=%s重复派奖拦截", lotid, pid)
            AlertMoniter().add_alert_msg("[重要]彩种lotid={}方案pid={}重复派奖拦截".format(lotid, pid))
        else:
            # 全部出票
            if define.TICKET_STATUS_SAVED not in prj_tickets_status:
                # 全部算奖
                if define.TICKET_STATUS_PRINTED not in prj_tickets_status:
                    if define.TICKET_STATUS_PRIZED in prj_tickets_status:
                        calgetmoney = prj_tickets_status[define.TICKET_STATUS_PRIZED].get("calgetmoney")
                        getmoney = prj_tickets_status[define.TICKET_STATUS_PRIZED].get("getmoney")
                        cancelmoney = Decimal(0)
                        #if calgetmoney != getmoney:
                        if False:  #TODO 暂时屏蔽奖金校验
                            logger.debug("彩种lotid=%s方案pid=%s派奖失败[算奖金额不匹配]", lotid, pid)
                            AlertMoniter().add_alert_msg("[重要]彩种lotid={}方案pid={}派奖失败[算奖金额不匹配]".format(lotid, pid))
                        else:
                            #部分撤单
                            if define.TICKET_STATUS_CANCEL in prj_tickets_status:
                                cancelmoney = prj_tickets_status[define.TICKET_STATUS_CANCEL].get("allmoney")
                                logger.debug("彩种lotid=%s方案pid=%s派奖完成[中奖%s元撤单%s元]", lotid, pid, getmoney, cancelmoney)
                            else:
                                logger.debug("彩种lotid=%s方案pid=%s派奖完成[中奖%s元]", lotid, pid, getmoney)
                            rds.publish("TRADE#ORDER#PRIZED", ujson.dumps({"lotid":lotid,
                                                                        "pid":pid,
                                                                        "uid":uid,
                                                                        "allmoney":order.get("f_allmoney"),
                                                                        "couponmoney":order.get("f_couponmoney"),
                                                                        "cid": order.get("f_chaseid", 0) or 0,  #竞篮竞足没有chaseid
                                                                        "fid": order.get("f_fid", 0) or 0,
                                                                        "getmoney":getmoney,
                                                                        "cancelmoney":cancelmoney}))
                    elif define.TICKET_STATUS_CANCEL in prj_tickets_status:
                        cancelmoney = prj_tickets_status[define.TICKET_STATUS_CANCEL].get("allmoney")
                        logger.debug("彩种lotid=%s方案pid=%s派奖完成[撤单%s元]", lotid, pid, cancelmoney)
                        rds.publish("TRADE#ORDER#PRIZED", ujson.dumps({"lotid":lotid,
                                                                    "pid":pid,
                                                                    "uid":uid,
                                                                    "allmoney":order.get("f_allmoney"),
                                                                    "couponmoney":order.get("f_couponmoney"),
                                                                    "cid": order.get("f_chaseid", 0) or 0,  #竞篮竞足没有chaseid
                                                                    "fid": order.get("f_fid", 0) or 0,
                                                                    "getmoney": Decimal(0),
                                                                    "cancelmoney":cancelmoney}))
                    else:
                        logger.debug("彩种lotid=%s方案pid=%s派奖完成[未中奖]", lotid, pid)
                        # 活动消息: [方案派奖成功]
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


                    # 追号方案继续追号
                    chaseid = order.get("f_chaseid", 0)
                    if chaseid > 0:
                        params = {
                            'cid': chaseid,
                            'getmoney': getmoney
                        }
                        resp = obj_order.continue_chasenumber(params)

                        #异步通知拆票
                        if resp.get("pid", ""):
                            params = {
                                "lotid": resp.get("lotid"),
                                "oid": resp.get("pid"),
                                "msgtype": define.MSG_TYPE_ORDER_SUCCPAY,
                                "msgcnt": ujson.dumps(resp)
                            }
                            try:
                                mid = MsgRecord().insert(params)
                                unpack.update({"mid": mid,
                                               "pid": resp.get("pid"),
                                               "paystatus": define.ORDER_PAY_STATUS_SUCC}) #更新为新订单的pid
                            except:
                                # 防止重复插入
                                logger.error(traceback.format_exc())
                            else:
                                rds = db_pool.get_redis("msgbus")
                                rds.publish("TRADE#ORDER#SUCCPAY", ujson.dumps(unpack))
                else:
                    logger.debug("彩种lotid=%s方案pid=%s派奖失败[未全部算奖]", lotid, pid)
            else:
                logger.debug("彩种lotid=%s方案pid=%s派奖失败[未全部出票]", lotid, pid)
    except:
        logger.error(traceback.format_exc())
        AlertMoniter().add_alert_msg("[重要]派奖或追号异常! info={}".format(msg))
