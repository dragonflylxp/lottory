#!/usr/bin/env python
# encoding: utf-8

import traceback
import copy
import xmsgbus
import ujson
import define
from alert import AlertMoniter
from dbpool import db_pool
from util.tools import Log
from logic import Split, Trade, Ticket
from msgbus.rmq import rmq_cli

global logger
logger = Log().getLog()

@xmsgbus.subscribe_callback_register("TRADE#ORDER#SUCCPAY")
def project_split_tickets(channel, msg):
    """订单支付成功，执行拆票
    """
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)
    msg = ujson.loads(msg)

    #校验支付状态
    paystatus = msg.get("paystatus")
    if paystatus != define.ORDER_PAY_STATUS_SUCC:
        return

    #校验订单数据
    mid = msg.get("mid")
    lotid = int(msg.get("lotid", 0))
    pid = msg.get("pid")
    save = int(msg.get("save", 1))  #save=0 拆票重放，不存票

    #调用拆票服务
    obj_order = Trade.get(lotid)
    obj_split = Split.get(lotid)
    obj_ticket = Ticket.get(lotid)
    order = obj_order.get_project_by_pid(pid) if obj_order else {}
    tickets = []
    if order:
        try:
            tickets = obj_split.dealSplitTicketInfo(copy.deepcopy(order)) if obj_split else {}
            if not tickets:
                raise Exception("拆票异常!lotid={}|pid={}".format(lotid, pid))
            params = {
                "mid": mid,
                "project": order,
                "tickets": tickets
            }
            if save == 1: obj_ticket.save_tickets(params)
        except:
            #拆票异常处理, 告警+重试
            logger.error(traceback.format_exc())
            AlertMoniter().add_alert_msg("拆票异常!lotid={}|pid={}".format(lotid, pid))
        else:
            # 异步通知出票
            print_notify(pid, lotid, tickets)
    return

def print_notify(pid, lotid, tickets):
    msg = {
        "pid": pid,
        "lotid": lotid,
        "ticketnum": len(tickets)
    }
    logger.debug('Print notify!msg=%s', msg)
    rmq_cli.publish(ujson.dumps(msg), define.MQ_TICKET_EXCHANGE, define.MQ_TICKET_ROUTING_KEY, 2)
