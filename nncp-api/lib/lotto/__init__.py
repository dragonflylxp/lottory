#!/usr/bin/env python
#-*-coding:utf-8-*-
#
#      Filename: __init__.py
#
#        Author:
#   Description: ---
#        Create: 2018-03-30 21:22:16
# Last Modified: 2018-03-30 21:22:16
#   Changes Log:


import LotDlt
import LotSsq
import LotSyxw
import LotJc

_LOTTERY_ = {
        28 : LotDlt.Lottery(28),  #大乐透
         3 : LotSsq.Lottery(3),   #双色球
        44 : LotSyxw.Lottery(44),  #广西11选5
        46 : LotJc.Lottery(46),  #竞足
        47 : LotJc.Lottery(47)  #竞蓝
}


def get(lotId):
    return _LOTTERY_.get(int(lotId), '')
