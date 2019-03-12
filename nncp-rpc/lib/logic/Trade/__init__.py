#encoding=utf-8
import os
import sys

import baseorder
import dlt
import ssq
import syxw
import jz
import jl

_ORDER_OBJECT_ ={
     0  :  baseorder.BaseOrder(0),  #所有彩种
    28  :  dlt.DltOrder(),          #大乐透
     3  :  ssq.SsqOrder(),          #双色球
    44  :  syxw.SyxwOrder(44),      #广西11选5
    45  :  syxw.SyxwOrder(45),      #江西11选5
    46  :  jz.JzOrder(),            #竞足
    47  :  jl.JlOrder(),            #竞篮
}

def get( lotid ):
    return _ORDER_OBJECT_.get(lotid,None)
