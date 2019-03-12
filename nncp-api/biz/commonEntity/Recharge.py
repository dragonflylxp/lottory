#!/usr/bin/env python
# encoding: utf-8
import calendar
import datetime
import ews
import time

import ujson
from util.tools import Log
import traceback
import define
from cbrpc import get_rpc_conn, RpcException
from jiuzhao import build_unifiedorder, jz_verify
from wechat.Monitor import send_textcard_message
import lianlian
from dbpool import db_pool
import rediskey

global logger
logger = Log().getLog()


class RechargeBean(object):
    def __init__(self):
        pass

    def place_order(self, params):
        module = "account"
        method = "recharge_order"

        oid = None
        with get_rpc_conn(module) as proxy:
            try:
                oid = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

        if not oid:
            raise

        paychannel = params.get("paychannel")

        params.update({"oid": oid})

        if paychannel == "1001":
            path = build_unifiedorder(params)
            return {"url": path}
        elif paychannel == "1002":
            ret = self.order_lianlian_web(params)
            return ret
        elif paychannel in ["1003", "1004"]:
            ret = self.order_lianlian_web(params)
            return ret
        elif paychannel == "1004":
            ret = self.order_lianlian_sdk(params)
            return ret
        return

    def jiuzhao_recharge_notice(self, params):
        """
        充值入账
        :return:
        """
        amount = params.get("amount")
        mchId = params.get("mchId")
        oid = params.get("outTradeNo")
        tradeno = params.get("outOrderId")
        paytime = params.get("thirdPayTime")
        status = params.get("orderStatus")
        sign = params.get("sign")

        is_verify = jz_verify(params)
        if is_verify:
            module = "account"
            method = "search_recharge_order"
            orderinfo = {}
            with get_rpc_conn(module) as proxy:
                try:
                    orderinfo = proxy.call(method, params)
                    orderinfo = ujson.loads(orderinfo)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

                if not orderinfo:
                    logger.error("order not found %s", oid)
                    return "fail"
                logger.info("orderinfo:%s", orderinfo)
                orderstatus = str(orderinfo.get("f_orderstatus", "-1"))
                _money = orderinfo.get("f_rechargemoney")
                if orderstatus == "1":
                    logger.info("already recharge %s", oid)
                    return "fail"
                amount = round(int(amount) / 100.0, 2)
                if float(_money) != float(amount):
                    logger.info("notice money nq amount")
                    return "fail"

                elif orderstatus == "0" and status == "00":
                    params = {
                        "uid": orderinfo.get("f_uid"),
                        "oid": oid,
                        "tradeno": tradeno,
                        "money": amount
                    }
                    status = proxy.call("recharge_notify", params)
                    if status:
                        return "success"
                    else:
                        return "fail"
                else:
                    send_textcard_message(msgtype="充值异常告警", servicename="nncp-api", exceptinfo="充值入账异常")

        else:
            # raise #todo 验签失败
            send_textcard_message(msgtype="充值异常告警", servicename="nncp-api", exceptinfo="充值验签错误")
            return "fail"

    def lianlian_withdraw(self, params):

        money = params.get("money")
        if float(money) < 1:
            raise ews.EwsError(ews.STATUS_WITHDRAW_MONEY_LIMIT)

        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

                # 获取实名信息接口
        if not user_info.get("realname", ""):
            # 实名认证
            raise ews.EwsError(ews.STATUS_USER_NOT_AUTH)

        card_no = user_info.get("cardno", "")

        if not user_info.get("cardno", ""):
            raise ews.EwsError(ews.STATUS_NOT_BIND_CARD)

        params.update({
            "card_no": card_no
        })

        rds = db_pool.get_redis('main')
        mobile = user_info.get("mobile")

        code = params.get("code", "")
        uid = params.get("uid")
        _code = rds.get(rediskey.REDIS_USER_MOBILE_SMS_CODE.format(mobile=mobile))
        limit_count = rds.incr(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))
        rds.expire(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile), 6*60*60)
        if limit_count >= 6:
            raise ews.EwsError(ews.STATUS_USER_VERIDFY_CODE_LIMIT_ERROR)
        if not _code or _code != code:
            raise ews.EwsError(ews.STATUS_USER_SMS_CODE_ERROR)
        rds.delete(rediskey.REDIS_USER_MOBILE_SMS_CODE_VERIFY_LIMIT.format(mobile=mobile))
        module = "account"
        method = "recharge_withdraw"

        oid = None
        with get_rpc_conn(module) as proxy:
            try:
                oid = proxy.call(method, params)

            except RpcException as ex:
                raise ews.EwsError(ews.STATUS_RPC_ERROR, ex.message)

            except:
                logger.error(traceback.format_exc())
                send_textcard_message(msgtype="提款下单异常", servicename="nncp-api",
                                      exceptinfo="提款下单错误 uid:%s" % (uid))
                raise ews.EwsError(ews.STATUS_USER_WITHDRAW_PLACEORDER_FAIL)

        if not oid:
            send_textcard_message(msgtype="提款下单异常", servicename="nncp-api",
                                  exceptinfo="提款下单错误 uid:%s" % (uid))
            raise ews.EwsError(ews.STATUS_USER_WITHDRAW_PLACEORDER_FAIL)

        return {}

    def order_lianlian_web(self, params):
        '''连连web充值
        :param
        ck
        truename: 实名认证的用户名
        idcard： 身份证号
        card_no： 身份证号
        no_agree： 绑定临时银行卡
        bank_code: 银行编码
        no_agree: 协议号
        '''

        platform = params.get("platform", "android")

        # 绑定临时银行卡
        no_agree = params.get('no_agree', None)
        card_no = params.get('card_no', None)

        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

        # 获取实名信息接口

        if not user_info.get("realname", ""):
            # 没有实名认证
            raise ews.EwsError(ews.STATUS_USER_NOT_AUTH)

        if (not params.get("no_agree")) and params.get("card_no"):
            req = {
                'username': "",
                'orderid': "",
                'cardno': params.get("card_no"),
                'truename': "",
                'idcode': "",
                'channel': "",
            }
            # 快捷绑定
            pass

        bank_code = params.get("bank_code", "")
        if params.get("card_no") and not bank_code:
            bank_code_info = lianlian.bank_card_test(params.get("card_no"))
            print bank_code_info
            bank_code = bank_code_info.get("bank_code") if bank_code_info.get("bank_code") else ""

        data = {
            'acct_name': user_info.get("realname"),
            'bank_code': bank_code,
            'busi_partner': "101001",
            'card_no': params.get("card_no"),
            'dt_order': time.strftime('%Y%m%d%H%M%S'),
            'flag_modify': '1',
            'id_no': user_info.get("idcard"),
            'id_type': "0",
            'money_order': params.get("money"),
            "name_goods": "充值",
            'no_order': params.get("oid"),
            'notify_url': lianlian.notify_url_web,
            'oid_partner': lianlian.partner_num_web,
            'sign_type': 'RSA',
            'url_return': params.get("callback_url", ""),
            'user_id': str(params.get("uid")),
            'valid_order': '1440',
            'version': "1.0",
            "no_agree": params.get("no_agree"),
            "timestamp": time.strftime('%Y%m%d%H%M%S'),
            "info_order": "nncp"
        }

        if params.get("paychannel") == "1003":
            # 1-Android 2-ios 3-WAP
            data.update({
                "app_request": "1" if platform == "android"  else "2" if platform == "ios" else "3"
            })
            data.update({
                "version": "1.1"
            })
        if params.get("paychannel") == "1004":
            del data["bank_code"]
            del data["timestamp"]
            del data["version"]
            del data["info_order"]
            del data["id_type"]
            logger.info(data)
        data = dict((k, v) for k, v in data.items() if v)  # 空值过滤掉
        reg_time = lianlian.to_format_datatime(user_info.get("crtime", ""))
        risk_item = lianlian.lianlian_make_risk_item(data["user_id"], reg_time, data["acct_name"],
                                                     data["id_no"], params.get("bind_mobile"))
        data["risk_item"] = ujson.dumps(risk_item)
        if params.get("paychannel") == "1004":
            data["sign"] = lianlian.esun_sign(data)
        else:
            data['sign'] = lianlian.esun_sign_wap(data)

        return data

    def lianlian_recharge_notice(self, checked_args):
        '''连连web/sdk充值异步入账
        '''

        logger.debug("=========checked_args")
        logger.debug(checked_args)

        amount = checked_args.get("money_order")
        oid = checked_args.get("no_order")
        tradeno = checked_args.get("oid_paybill")
        status = checked_args.get("result_pay")
        sign = checked_args.get("sign")

        # {
        #     "oid_partner": "201103171000000000",
        #     "dt_order": "20130515094013",
        #     "no_order": "2013051500001",
        #     "oid_paybill": "2013051613121201",
        #     "money_order": "10",
        #     "result_pay": "SUCCESS",
        #     "settle_date": "20130516",
        #     "info_order": "用户13958069593购买了3桶羽毛球",
        #     "pay_type": "2",
        #     "bank_code": "01020000",
        #     "sign_type": "RSA",
        #     "sign": "ZPZULntRpJwFmGNIVKwjLEF2Tze7bqs60rxQ22CqT5J1UlvGo575QK9z/
        #             + p + 7E9cOoRoWzqR6xHZ6WVv3dloyGKDR0btvrdqPgUAoeaX / YOWzTh00vwcQ + HBtX
        #     E + vPTfAqjCTxiiSJEOY7ATCF1q7iP3sfQxhS0nDUug1LP3OLk = "
        # }
        res = lianlian.lian_verify(checked_args, checked_args['sign'])
        if not res:
            logger.info("===lianlian verify fail===")
            logger.info(checked_args)
            return {'ret_code': '1111', 'ret_msg': '验签失败'}

        if checked_args['result_pay'] != 'SUCCESS':
            return {'ret_code': '2222', 'ret_msg': 'result_pay： ' + checked_args['result_pay']}

        module = "account"
        method = "search_recharge_order"
        orderinfo = {}
        with get_rpc_conn(module) as proxy:
            try:
                orderinfo = proxy.call(method, {"oid": oid})
                orderinfo = ujson.loads(orderinfo)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

            if not orderinfo:
                logger.error("order not found %s", oid)
                return {'ret_code': '3333', 'ret_msg': 'order not found'}

            logger.info("orderinfo:%s", orderinfo)
            orderstatus = str(orderinfo.get("f_orderstatus", "-1"))
            _money = orderinfo.get("f_rechargemoney")
            if orderstatus == "1":
                logger.info("already recharge %s", oid)
                return {'ret_code': '0000', 'ret_msg': 'already recharge'}

            if float(_money) != float(amount):
                logger.info("notice money nq amount")
                return {'ret_code': '5555', 'ret_msg': 'notice money nq amount'}

            elif orderstatus == "0" and status == "SUCCESS":
                params = {
                    "uid": orderinfo.get("f_uid"),
                    "oid": oid,
                    "tradeno": tradeno,
                    "money": amount
                }
                status = proxy.call("recharge_notify", params)
                if status:
                    ret = {'ret_code': '0000', 'ret_msg': '交易成功'}
                    # req = {
                    #    'agree_no': checked_args['no_agree'],
                    #    'bank_code': checked_args['bank_code'],
                    #    'card_type': checked_args['pay_type'],
                    #    'id_code': checked_args.get('id_no', '')
                    # }

                    # if checked_args['no_agree']:
                    #    pass

                    return ret
                else:
                    return {'ret_code': '6666', 'ret_msg': 'fail'}
        return {'ret_code': '6666', 'ret_msg': 'fail'}

    def lianlian_withdraw_notice(self, checked_args):
        '''连连web/sdk充值异步入账
        '''

        logger.debug("=========checked_args")
        logger.info("lianlian_withdraw_notice： %s", checked_args)

        # {
        #     "oid_partner": "201103171000000000",
        #     "dt_order": "20130515094018",
        #     "no_order": "2013051500005",
        #     "oid_paybill": "2013051613121201",
        #     "money_order": "200.01",
        #     "result_pay": "SUCCESS",
        #     "settle_date": "20130627",
        #     "sign_type ": "RSA",
        #     "sign": "ZPZULntRpJwFmGNIVKwjLEF2Tze7bqs60rxQ22CqT5J1UlvGo575QK9z/
        #             + p + 7E9cOoRoWzqR6xHZ6WVv3dloyGKDR0btvrdqPgUAoeaX / YOWzTh00vwcQ + HBtXE + vP
        #     TfAqjCTxiiSJEOY7ATCF1q7iP3sfQxhS0nDUug1LP3OLk = "
        # }

        amount = checked_args.get("money_order")
        oid = checked_args.get("no_order")
        tradeno = checked_args.get("oid_paybill")
        result_pay = checked_args.get("result_pay")
        sign = checked_args.get("sign")

        if not sign:
            return {'ret_code': '8888', 'ret_msg': '参数异常'}

        res = lianlian.lian_verify(checked_args, checked_args['sign'])
        if not res:
            logger.info("===lianlian verify fail===")
            logger.info(checked_args)
            return {'ret_code': '1111', 'ret_msg': '验签失败'}

        if checked_args['result_pay'] != 'SUCCESS':
            logger.info("===lianlian result_pay status fail ===")
            # return {'ret_code': '2222', 'ret_msg': 'result_pay： ' + checked_args['result_pay']}

        module = "account"
        method = "search_withdraw_order"
        orderinfo = {}
        with get_rpc_conn(module) as proxy:
            try:
                orderinfo = proxy.call(method, {"oid": oid})
                orderinfo = ujson.loads(orderinfo)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_ACCOUNT_FAIL)

            if not orderinfo:
                logger.error("order not found %s", oid)
                return {'ret_code': '3333', 'ret_msg': 'order not found'}

            logger.info("orderinfo:%s", orderinfo)
            orderstatus = str(orderinfo.get("f_orderstatus", "-1"))
            _money = orderinfo.get("f_money")
            if orderstatus == "2":
                logger.info("already deal %s", oid)
                return {'ret_code': '0000', 'ret_msg': 'already deal'}

            if float(_money) != float(amount):
                logger.info("notice money nq amount")
                return {'ret_code': '5555', 'ret_msg': 'notice money nq amount'}

            elif orderstatus == "1":
                if result_pay == "SUCCESS":
                    status = define.WITHDRAW_STATUS_SUC
                else:
                    status = define.WITHDRAW_STATUS_FAIL
                params = {
                    "oid": oid,
                    "orderstatus": status,
                    "tradeno": tradeno
                }

                module = "account"
                method = "update_withdraw_orderstatus"
                status = False
                with get_rpc_conn(module) as proxy:
                    try:
                        status = proxy.call(method, params)
                    except:
                        logger.error(traceback.format_exc())
                if status:
                    ret = {'ret_code': '0000', 'ret_msg': '交易成功'}
                    return ret
                else:
                    return {'ret_code': '6666', 'ret_msg': 'fail'}
        return {'ret_code': '6666', 'ret_msg': 'fail'}

    def get_bank_cardlist(self, uid):
        cardbinds = lianlian.get_cardbind_list(uid)
        return cardbinds

    def order_lianlian_sdk(self, params):
        '''连连sdk充值
        :param
        ck
        truename: 实名认证的用户名
        idcard： 身份证号
        card_no： 身份证号
        no_agree： 绑定临时银行卡
        bank_code: 银行编码
        no_agree: 协议号
        '''

        platform = params.get("platform", "android")

        # 绑定临时银行卡
        no_agree = params.get('no_agree', None)
        card_no = params.get('card_no', None)

        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, params)
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

        # 获取实名信息接口

        if not user_info.get("realname", ""):
            # 没有实名认证
            raise ews.EwsError(ews.STATUS_USER_NOT_AUTH)

        if (not params.get("no_agree")) and params.get("card_no"):
            req = {
                'username': "",
                'orderid': "",
                'cardno': params.get("card_no"),
                'truename': "",
                'idcode': "",
                'channel': "",
            }
            # 快捷绑定
            pass

        bank_code = params.get("bank_code", "")
        if params.get("card_no") and not bank_code:
            bank_code_info = lianlian.bank_card_test(params.get("card_no"))
            print bank_code_info
            bank_code = bank_code_info.get("bank_code") if bank_code_info.get("bank_code") else ""

        data = {
            'acct_name': user_info.get("realname"),
            'bank_code': bank_code,
            'busi_partner': "101001",
            'card_no': params.get("card_no"),
            'dt_order': time.strftime('%Y%m%d%H%M%S'),
            'flag_modify': '1',
            'id_no': user_info.get("idcard"),
            'id_type': "0",
            'money_order': params.get("money"),
            "name_goods": "充值",
            'no_order': params.get("oid"),
            'notify_url': lianlian.notify_url_web,
            'oid_partner': lianlian.partner_num_web,
            'sign_type': 'RSA',
            'url_return': params.get("callback_url", ""),
            'user_id': str(params.get("uid")),
            'valid_order': '1440',
            'version': "1.0",
            "no_agree": params.get("no_agree"),
            "timestamp": time.strftime('%Y%m%d%H%M%S'),
            "info_order": "nncp"
        }

        data = dict((k, v) for k, v in data.items() if v)  # 空值过滤掉
        reg_time = lianlian.to_format_datatime(user_info.get("crtime", ""))
        risk_item = lianlian.lianlian_make_risk_item(data["user_id"], reg_time, data["acct_name"],
                                                     data["id_no"], params.get("bind_mobile"))
        data["risk_item"] = ujson.dumps(risk_item)
        data['sign'] = lianlian.esun_sign_wap(data)

        return data
