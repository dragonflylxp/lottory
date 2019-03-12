#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: coupon.py
#
#        Author:
#   Description: ---
#        Create: 2018-04-24 19:46:14
# Last Modified: 2018-04-24 19:46:14
#   Changes Log:

import traceback
import ews
import session
from commonEntity.Coupon import CouponBean
from util.tools import Log

logger = Log().getLog()


@ews.route_sync_func('/coupon/list', kwargs={'ck':(UserWarning, )})
def coupon_list(handler, *args, **kwargs):
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    group = handler.json_args.get("group", "all")
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")
    lotid = handler.json_args.get("lotid", 0)
    allmoney = handler.json_args.get("allmoney", 0)

    params = {
        "uid": uid,
        "group": group,
        "lotid": lotid,
        "allmoney": allmoney,
        "pageno": pageno,
        "pagesize": pagesize
    }
    coupons = CouponBean().coupon_list(params)
    coupons.update({"group": group})
    return handler.ok(coupons)
