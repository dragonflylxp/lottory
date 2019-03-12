# coding: utf-8

import ews
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import session
import ujson
from commonEntity.Home import HomeBean


@ews.route_sync_func('/home/info', kwargs={})
def home_info(handler, *args, **kwargs):
    platform = handler.json_args.get("platform", "android")
    if platform == "pc":
        ret = HomeBean().main_info_pc(platform)
    else:
        ret = HomeBean().main_info(platform)
    return handler.ok(ret)


@ews.route_sync_func('/home/switch', kwargs={})
def home_switch(handler, *args, **kwargs):
    # platform = handler.json_args.get("platform", "android")
    channel = handler.json_args.get("channel", "")
    ret = {"info_switch": 1}
    return handler.ok(ret)



