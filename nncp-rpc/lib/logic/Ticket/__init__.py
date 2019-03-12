#encoding=utf-8
import os
import sys

import dlt
import ssq
import syxw
import jz
import jl

_TICKET_OBJECT_ ={
    28  :  dlt.DltTicket(),       #大乐透
     3  :  ssq.SsqTicket(),       #双色球
    44  :  syxw.SyxwTicket(44),   #广西11选5
    46  :  jz.JzTicket(),         #竞足
    47  :  jl.JlTicket()          #竞篮
}

def get( lotid ):
    return _TICKET_OBJECT_.get(lotid,None)
