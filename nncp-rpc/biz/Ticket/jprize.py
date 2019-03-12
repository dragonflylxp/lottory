#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: jprize.py
#
#        Author:
#   Description: ---
#        Create: 2018-03-16 20:39:13
# Last Modified: 2018-03-16 20:39:13
#   Changes Log:

import traceback
from logic import Jprize
from util.tools import Log

logger = Log().getLog()

class JprizeBiz(object):

    def do_jprize(self, params):
        lotid = params.get("lotid")
        obj_jprize = Jprize.get(int(lotid))
        try:
            logger.debug('Jprize: lotid=%s', lotid)
            obj_jprize.jprize(params)
        except:
            raise
