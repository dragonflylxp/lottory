# coding: utf-8

import ews
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import session
import ujson
from commonEntity.Project import ProjBean



@ews.route_sync_func('/proj/list', kwargs={'ck': (UserWarning, 'string')})
def proj_list(handler, *args, **kwargs):
    """
    方案记录
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    biztype = handler.json_args.get("biztype", "0")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")

    params = {
        "uid": uid,
        "lotid": lotid,
        "pageno": pageno,
        "pagesize": pagesize,
        "biztype": biztype
    }
    ret = ProjBean().get_proj_list(params)

    return handler.ok(ret)

@ews.route_sync_func('/proj/detail', kwargs={'ck': (UserWarning, 'string')})
def proj_detail(handler, *args, **kwargs):
    """
    方案详情
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pid = handler.json_args.get("pid", "21")

    params = {
        "uid": uid,
        "pid": pid,
        "lotid": lotid
    }
    ret = ProjBean(int(lotid)).get_proj_router(params)
    return handler.ok(ret)

@ews.route_sync_func('/proj/launch/list', kwargs={'ck': (UserWarning, 'string')})
def launch_list(handler, *args, **kwargs):
    """
    发单详情
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    biztype = handler.json_args.get("biztype", "0")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")

    params = {
        "uid": uid,
        "lotid": lotid,
        "pageno": pageno,
        "pagesize": pagesize,
        "biztype": biztype
    }
    ret = ProjBean().get_lanuch_list(params)

    return handler.ok(ret)

@ews.route_sync_func('/proj/follow/detail', kwargs={'ck': (UserWarning, 'string')})
def follow_detail(handler, *args, **kwargs):
    """
    跟单详情
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pid = handler.json_args.get("pid", "21")

    params = {
        "uid": uid,
        "pid": pid,
        "lotid": lotid
    }
    ret = ProjBean(int(lotid)).get_jc_follow_proj_detail(params)
    return handler.ok(ret)

@ews.route_sync_func('/proj/follow/list', kwargs={'ck': (UserWarning, 'string')})
def follow_list(handler, *args, **kwargs):
    """
    我的跟单列表
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    biztype = handler.json_args.get("biztype", "0")
    ck = handler.json_args.get("ck", "")
    uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")

    params = {
        "uid": uid,
        "lotid": lotid,
        "pageno": pageno,
        "pagesize": pagesize,
        "biztype": biztype
    }
    ret = ProjBean().get_follow_list(params)

    return handler.ok(ret)


@ews.route_sync_func('/follow/recommend', kwargs={})
def follow_recommend(handler, *args, **kwargs):
    """
    推荐订单
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    biztype = handler.json_args.get("biztype", "0")
    # ck = handler.json_args.get("ck", "")
    # uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")


    params = {
        # "uid": uid,
        "lotid": lotid,
        "pageno": pageno,
        "pagesize": pagesize,
        # "biztype": biztype
    }
    ret = ProjBean().get_recommend_list(params)

    return handler.ok(ret)

@ews.route_sync_func('/follow/hot_seller', kwargs={})
def follow_room_header_info(handler, *args, **kwargs):
    """
    推荐大厅顶部信息
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    wheelinfo = ProjBean().get_follow_wheelinfo()
    sellers = ProjBean().get_hot_seller()

    ret = {
        "wheelinfo": wheelinfo,
        "sellers": sellers
    }
    return handler.ok(ret)


@ews.route_sync_func('/follow/seller/order', kwargs={'ck': (UserWarning, 'string')})
def follow_seller_order(handler, *args, **kwargs):
    """
    大神个人页订单
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    lotid = handler.json_args.get("lotid", "28")
    biztype = handler.json_args.get("biztype", "0")
    # ck = handler.json_args.get("ck", "")
    # uid = session.get_by_ck(ck).get('uid')
    pageno = handler.json_args.get("pageno", "1")
    pagesize = handler.json_args.get("pagesize", "10")
    launch_uid= handler.json_args.get("launch_uid")

    params = {
        "uid": launch_uid,
        "lotid": lotid,
        "pageno": pageno,
        "pagesize": pagesize,
        # "biztype": biztype
    }
    ret = ProjBean().get_lanuch_list(params)

    return handler.ok(ret)

@ews.route_sync_func('/follow/seller/info', kwargs={})
def follow_seller_info(handler, *args, **kwargs):
    """
    大神信息
    :param handler:
    :param args:
    :param kwargs:
    :return:
    """
    # lotid = handler.json_args.get("lotid", "28")
    # biztype = handler.json_args.get("biztype", "0")
    # ck = handler.json_args.get("ck", "")
    # uid = session.get_by_ck(ck).get('uid')
    launch_uid = handler.json_args.get("launch_uid")

    params = {
        "uid": launch_uid
    }
    ret = ProjBean().get_seller_info(params)

    return handler.ok(ret)