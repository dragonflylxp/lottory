# coding: utf-8

import ews
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import session
import ujson
from commonEntity.Lottery import LotteBean, DrawBean


@ews.route_sync_func('/lottery/draw/list', kwargs={})
def lotte_draw_list(handler, *args, **kwargs):
    ret = LotteBean().get_lotte_draw_list()
    return handler.ok(ret)

@ews.route_sync_func('/lottery/draw/history', kwargs={'lotid': (UserWarning, 'string')})
def lotte_draw_history(handler, *args, **kwargs):
    lotid = handler.json_args.get("lotid")
    pageno = handler.json_args.get("pageno", 1)
    pagesize = handler.json_args.get("pagesize", 10)
    ret = DrawBean(int(lotid)).get_lotte_history_opencode(pageno, pagesize)
    return handler.ok(ret)

@ews.route_sync_func('/lottery/draw/detail', kwargs={'lotid': (UserWarning, 'string'), 'expect': (UserWarning, 'string')})
def lotte_draw_detail(handler, *args, **kwargs):
    lotid = handler.json_args.get("lotid")
    expect = handler.json_args.get("expect")
    ret = DrawBean(int(lotid)).lotte_draw_detail(expect)
    return handler.ok(ret)
