#!/usr/bin/env python
# encoding: utf-8

import xmsgbus
import ujson
from util.tools import Log

global logger
logger = Log().getLog()

@xmsgbus.subscribe_callback_register("user#define#channle")
def user_define_channel(channel,msg):
    logger.debug('callback for [channel:%s]:[msg:%s]',channel,msg)

