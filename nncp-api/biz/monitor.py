# coding: utf-8
import random

import ews
import time
from util.configer import *
import traceback
from wechat.Monitor import send_textcard_message


@ews.route_sync_func('/monitor/send', kwargs={'msg': (UserWarning, 'string')})
def monitor_send(handler, *args, **kwargs):
    msgtype = handler.json_args.get("msgtype", "test")
    servicename = handler.json_args.get("servicename", "servicename")
    msg = handler.json_args.get("msg", "msg")
    more_url = handler.json_args.get("more_url", "https://www.baidu.com/")
    send_textcard_message(msgtype=msgtype, servicename=servicename, exceptinfo=msg, more_url=more_url)
    return handler.ok({})