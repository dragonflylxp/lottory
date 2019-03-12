#!/usr/bin/env python
# encoding: utf-8

import traceback
import define
import job
from cbrpc import get_rpc_conn
from util.tools import Log

logger = Log().getLog()


@job.scheduler.scheduled_job('cron', second='*/30')
def scan_unprint_projects():
    """扫描未出票且创建时间超过5分钟的订单
    """
    pass
    """
    try:
        with get_rpc_conn("trade") as proxy:
            params = {
                "lotid": 28
                "orderstatus": define.ORDER_STATUS_SUCC
            }
            prjnum = proxy.call("scan_update_projects", params)
            logger.info("Projects updated! project_num=%s", prjnum)
    except:
        logger.error(traceback.format_exc())
    """
