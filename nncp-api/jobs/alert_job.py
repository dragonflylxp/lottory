#!/usr/bin/env python
# encoding: utf-8

import traceback
import define
import job
from cbrpc import get_rpc_conn
from util.tools import Log
from alert import AlertMoniter
logger = Log().getLog()


@job.scheduler.scheduled_job('cron', second='*/2')
def send_alert_info():
    """发送告警信息
    """
    try:
        AlertMoniter().send_alert()
    except:
        logger.error(traceback.format_exc())

