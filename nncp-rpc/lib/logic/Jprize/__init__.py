#coding=utf-8

import LotDlt
import LotJk
import LotSsq

_LOTTERY_ = {
     3 : LotSsq.Lottery(3),  #双色球
    28 : LotDlt.Lottery(28), #大乐透
    44 : LotJk.Lottery(44)   #11选5
}


def get(lotId):
    return _LOTTERY_.get(int(lotId), '')
