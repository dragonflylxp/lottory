#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback
from lib.logic.dlt_logic import DltExpect
from lib.logic.ssq_logic import SsqExpect
from lib.logic.syxw_logic import SyxwExpect

global logger
logger = Log().getLog()


_EXPECT_OBJECT_ = {
    28: DltExpect(),  # 大乐透
    3: SsqExpect(),  # 双色球
    44: SyxwExpect(44),  # 广西11选5
}


def get(lotid):
    return _EXPECT_OBJECT_.get(lotid, None)
