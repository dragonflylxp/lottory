#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: commonEntity/Coupon.py
#
#        Author:
#   Description: ---
#        Create: 2018-04-24 19:52:06
# Last Modified: 2018-04-24 19:52:06
#   Changes Log:

import datetime
import traceback
import ujson
import define
import ews
from cbrpc import get_rpc_conn
from util.tools import Log

logger = Log().getLog()


class CouponBean():
    def __init__(self):
        pass

    def coupon_list(self, params):
        coupons = {}
        with get_rpc_conn("account") as proxy:
            try:
                coupons = proxy.call("coupon_list", params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_COUPON_LIST_FAIL)
        coupons = ujson.loads(coupons)
        count = coupons.get("count", 0)
        coupons = coupons.get("coupons")

        #排序规则
        lotid = params.get("lotid")
        allmoney = params.get("allmoney")
        if int(lotid) > 0 and int(allmoney) > 0:
            coupons = sorted(coupons, key=lambda x:float(x["f_couponmoney"]), reverse=True)
            coupons = sorted(coupons, key=lambda x:x["f_expiretime"])
        else:
            coupons = sorted(coupons, key=lambda x:x["f_expiretime"])
            coupons = sorted(coupons, key=lambda x:float(x["f_couponmoney"]))

        lst = []
        for coupon in coupons:
            # lotid定向过滤
            lotids = coupon.get("f_lotids")
            if lotids != "0":
                lotids = lotids.split(",")
                logger.debug(lotid)
                if int(lotid)>0 and str(lotid) not in lotids:
                    continue
            else:
                lotids = []

            # 优惠券跳转
            weekday = datetime.datetime.today().weekday()+1
            if weekday in [1, 3, 6]:
                if not lotids or str(define.LOTTE_DLT_ID) in lotids:
                    jumplotid = str(define.LOTTE_DLT_ID)
                else:
                    jumplotid = lotids[0]
            elif weekday in [2, 4, 7]:
                if not lotids or str(define.LOTTE_SSQ_ID) in lotids:
                    jumplotid = str(define.LOTTE_SSQ_ID)
                else:
                    jumplotid = lotids[0]
            else:
                jumplotid = lotids[0] if lotids else str(define.LOTTE_GX11X5_ID)

            lst.append({
                "cid": coupon.get("f_cid"),
                "uid": coupon.get("f_uid"),
                "pid": coupon.get("f_pid"),
                "lotids": lotids,
                "jumplotid": jumplotid,
                "couponstatus": coupon.get("f_couponstatus"),
                "couponmoney": coupon.get("f_couponmoney"),
                "requiremoney": coupon.get("f_requiremoney"),
                "crtime": coupon.get("f_crtime"),
                "activedays": coupon.get("f_activedays"),
                "activetime": coupon.get("f_activetime"),
                "expiretime": coupon.get("f_expiretime")
            })
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        ret = {
            "list": lst,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno
        }
        return ret
