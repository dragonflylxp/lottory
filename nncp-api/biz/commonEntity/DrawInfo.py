#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback
from lib.logic.dlt_logic import DltDraw
from lib.logic.ssq_logic import SsqDraw
from lib.logic.syxw_logic import SyxwDraw
from lib.logic.jczq_logic import JzDraw
from lib.logic.jclq_logic import JlDraw

global logger
logger = Log().getLog()


_EXPECT_OBJECT_ = {
    28: DltDraw(),  # 大乐透
    3: SsqDraw(),  # 双色球
    44: SyxwDraw(44),  # 广西11选5
    46: JzDraw(),  # 竞足
    47: JlDraw()   # 竞篮
}


def get(lotid):
    return _EXPECT_OBJECT_.get(lotid, None)
