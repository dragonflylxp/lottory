# coding: utf-8

import ews
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import session
import ujson
from commonEntity.Info import Infobean


@ews.route_sync_func('/info/list', kwargs={})
def info_list(handler, *args, **kwargs):
    tabid = handler.json_args.get("tabid", "1")
    pageno = handler.json_args.get("pageno", 1)
    pagesize = handler.json_args.get("pagesize", 10)
    ret = Infobean().get_info_list(tabid, pageno, pagesize)
    return handler.ok(ret)

@ews.route_sync_func('/info/detail', kwargs={})
def info_detail(handler, *args, **kwargs):
    tabid = handler.json_args.get("tabid", "1")
    id = handler.json_args.get("id", 1)

    ret = Infobean().get_info_detail(tabid, id)
    return handler.ok(ret)