#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: MQ.py
#
#        Author:
#   Description: ---
#        Create: 2018-05-02 21:05:41
# Last Modified: 2018-05-02 21:05:41
#   Changes Log:

import ujson
import define
from msgbus.rmq import rmq_cli
from util.tools import Log

logger = Log().getLog()

def send_msg(mtype, msg):
    exchange = define.MQ_MSG_EXCHANGE
    routing_key = define.MQ_MSG_ROUTING_KEYS.get(mtype)
    rmq_cli.publish(ujson.dumps(msg), exchange, routing_key, 2)
