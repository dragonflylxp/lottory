#!/usr/bin/env python
# encoding: utf-8

import traceback
import define
import rediskey
import job
from dbpool import db_pool
from logic import dlt_logic, syxw_logic, ssq_logic
from cbrpc import get_rpc_conn
from util.tools import Log

logger = Log().getLog()


@job.scheduler.scheduled_job('cron', second='*/20')
def search_open_expect():
    """轮询开奖期号
    """
    rds = db_pool.get_redis("main")
    dlt_expect = dlt_logic.DltDraw().get_newest_opencode()
    dlt_expect = dlt_expect.get("expect", None)
    if dlt_expect:
        rds.set(rediskey.REDIS_OPENCODE_EXPECT.format("dlt"), dlt_expect, ex=60)
    logger.debug("Search opencode expect! lotname=dlt|expect=%s", dlt_expect)

    gx11x5_expect = syxw_logic.SyxwDraw(44).get_newest_opencode()
    gx11x5_expect = gx11x5_expect.get("expect", None)
    if gx11x5_expect:
        rds.set(rediskey.REDIS_OPENCODE_EXPECT.format("gx11x5"), gx11x5_expect, ex=60)
    logger.debug("Search opencode expect! lotname=gx11x5|expect=%s", gx11x5_expect)

    ssq_expect = ssq_logic.SsqDraw().get_newest_opencode()
    ssq_expect = ssq_expect.get("expect", None)
    if ssq_expect:
        rds.set(rediskey.REDIS_OPENCODE_EXPECT.format("ssq"), ssq_expect, ex=60)
    logger.debug("Search opencode expect! lotname=ssq|expect=%s", ssq_expect)


@job.scheduler.scheduled_job('cron', second='*/30')
def cal_prize_dlt():
    """大乐透算奖
    """
    try:
        rds = db_pool.get_redis("main")
        expect = rds.get(rediskey.REDIS_OPENCODE_EXPECT.format("dlt"))
        with get_rpc_conn("ticket") as proxy:
            proxy.call("Jprize", {"lotid":28, "expect": expect})
    except:
        logger.error(traceback.format_exc())


@job.scheduler.scheduled_job('cron', second='*/30')
def cal_prize_gx11x5():
    """gx11选5算奖
    """
    try:
        rds = db_pool.get_redis("main")
        expect = rds.get(rediskey.REDIS_OPENCODE_EXPECT.format("gx11x5"))
        with get_rpc_conn("ticket") as proxy:
            proxy.call("Jprize", {"lotid":44, "expect": expect})
    except:
        logger.error(traceback.format_exc())


@job.scheduler.scheduled_job('cron', second='*/30')
def cal_prize_ssq():
    """双色球算奖
    """
    try:
        rds = db_pool.get_redis("main")
        expect = rds.get(rediskey.REDIS_OPENCODE_EXPECT.format("ssq"))
        with get_rpc_conn("ticket") as proxy:
            proxy.call("Jprize", {"lotid":3, "expect": expect})
    except:
        logger.error(traceback.format_exc())
