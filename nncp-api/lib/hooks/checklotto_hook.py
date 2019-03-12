#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: fileorcode.py
#
#        Author:
#   Description:
#        Create: 2018-03-30 20:23:55
# Last Modified: 2018-03-30 20:23:55
#   Changes Log:


#hook callback 注册路径：服务启动时import hooks(__init__.py中导入)

from hook import Hook
import lotto
from util.tools import Log

logger = Log().getLog()


@Hook.register_callback('check_lotto')
def check_lotto(ret, *args, **kwargs):
    params = args[0].json_args
    lotid = params.get("lotid")
    obj_lotto = lotto.get(int(lotid))
    obj_lotto.check_lotto(params)
