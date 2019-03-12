#encoding=utf-8

import os
import sys

import LotCommon
import LotJc
import LotLT
import LotSz
import LotJk

_SPLIT_OBJECT_ ={
     1  :  LotCommon.Lottery( 1 ),  #胜负彩
     3  :  LotLT.LotLT( 3 ),        #双色球
     4  :  LotSz.LotSz( 4 ),        #七星彩
     5  :  LotSz.LotSz( 5 ),        #排列三
    15  :  LotCommon.Lottery( 15 ), #6场半全场
    17  :  LotCommon.Lottery( 17 ), #4场进球
    28  :  LotLT.LotLT( 28 ),       #大乐透
    44  :  LotJk.LotJk( 44 ),       #广西11选5
    45  :  LotJk.LotJk( 45 ),       #江西11选5
    46  :  LotJc.LotJc( 46 ),       #竞足
    47  :  LotJc.LotJc( 47 ),       #竞蓝
    60  :  LotSz.LotSz( 60 ),       #排列五
    61  :  LotCommon.Lottery( 61 )  #任选9场
}


def get( lotid ):
    return _SPLIT_OBJECT_.get(lotid,None)
