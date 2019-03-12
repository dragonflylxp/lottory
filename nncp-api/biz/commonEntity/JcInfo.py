#!/usr/bin/env python
# encoding: utf-8
import ews
import time
from util.tools import Log
import traceback
from lib.logic.jclq_logic import JclqLogic
from lib.logic.jczq_logic import JczqLogic

global logger
logger = Log().getLog()


_JC_OBJECT_ = {
    46: JczqLogic(),  # 竞彩足球
    47: JclqLogic()  # 竞彩篮球
}


def get(lotid):
    return _JC_OBJECT_.get(lotid, None)
