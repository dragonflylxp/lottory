#!/usr/bin/env python
# encoding: utf-8

import traceback
import define
import job
from cbrpc import get_rpc_conn
from util.tools import Log
from wechat.Monitor import send_textcard_message
import ujson
import lianlian

logger = Log().getLog()


#@job.scheduler.scheduled_job('cron', second='*/10')
def comfirm_withdraw():
    """
    审核提款
    :return:
    """

    module = "account"
    method = "get_obligation_order"

    params = {
        "orderstatus": define.WITHDRAW_STATUS_CHECK
    }
    orders = []
    with get_rpc_conn(module) as proxy:
        try:
            orders = proxy.call(method, params)
        except:
            logger.error(traceback.format_exc())
            send_textcard_message(msgtype="提款异常", servicename="nncp-job", exceptinfo="获取待支付失败")
            raise

    orders = ujson.loads(orders)
    for order in orders:
        module = "user"
        method = "user_info"
        uid = order.get("f_uid")
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, {"uid": uid})
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())

        uid = order.get("f_uid")
        oid = order.get("f_oid")
        money = order.get("f_money")
        card_no = order.get("f_card_no")
        acct_name = user_info.get("realname")
        #todo 订单状态检查，防止重复
        resp = lianlian.query_withdraw_order(oid)
        logger.info("lianlian.query_withdraw_order %s", resp)
        if resp.get("ret_code") == "0000":
            continue
        try:
            status = lianlian.withdraw(oid, money, card_no, acct_name)
        except:
            logger.info(traceback.format_exc())
        logger.info("withdraw %s", status)
        # resp = lianlian.query_withdraw_order(oid)
        #
        # if resp.get("ret_code") == "0000":
        #
        #     result_pay = resp.get("result_pay")
        #     logger.info(resp)
        #     if status:
        #         orderstatus = define.WITHDRAW_STATUS_SUC
        #     else:
        #         orderstatus = define.WITHDRAW_STATUS_FAIL
        #
        #         send_textcard_message(msgtype="提款异常", servicename="nncp-job",
        #                               exceptinfo="提款请求失败,需要人工操作 uid:%s oid: %s" % (uid, oid))
            # params = {
            #     "oid": oid,
            #     "orderstatus": orderstatus
            # }
            #
            # module = "account"
            # method = "update_withdraw_orderstatus"
            # status = False
            # with get_rpc_conn(module) as proxy:
            #     try:
            #         status = proxy.call(method, params)
            #     except:
            #         logger.error(traceback.format_exc())
            #         send_textcard_message(msgtype="提款异常", servicename="nncp-job",
            #                               exceptinfo="提款更新状态失败,需要人工操作 uid:%s oid: %s" % (uid, oid))
        # else:
        #     continue
            # APPLY
            # 付款申请
            # CHECK
            # 复核申请
            # SUCCESS
            # 付款成功
            # PROCESSING
            # 付款处理中
            # CANCEL
            # 付款退款（付款成
            # 功后，有可能发生退款）
            # FAILURE
            # 付款失败
            # CLOSED
            # 付款关闭





#@job.scheduler.scheduled_job('cron', second='*/10')
def withdraw_fail():
    """
    审核提款
    :return:
    """

    module = "account"
    method = "get_obligation_order"

    params = {
        "orderstatus": define.WITHDRAW_STATUS_FAIL
    }
    orders = []
    with get_rpc_conn(module) as proxy:
        try:
            orders = proxy.call(method, params)
        except:
            logger.error(traceback.format_exc())
            send_textcard_message(msgtype="提款异常", servicename="nncp-job", exceptinfo="获取待支付失败")
            raise

    orders = ujson.loads(orders)
    for order in orders:
        module = "account"
        method = "withdraw_refund"
        status = False
        oid = order.get("f_oid")
        uid = order.get("f_uid")
        with get_rpc_conn(module) as proxy:
            try:
                status = proxy.call(method, {"oid": oid})
            except:
                logger.error(traceback.format_exc())
                send_textcard_message(msgtype="提款提款异常", servicename="nncp-job",
                                      exceptinfo="提款退款异常,需要人工操作 uid:%s oid: %s" % (uid, oid))

        if not status:
            pass
