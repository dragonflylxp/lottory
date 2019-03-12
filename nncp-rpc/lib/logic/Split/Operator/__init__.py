#encoding=utf-8

import Spliter_JC
import Spliter_LT
import Spliter_RJ
import Spliter_DLC
import Spliter_Common
import Spliter_PL
import Spliter_SSQ


_LOTTERY_ = {
    1:      Spliter_Common.Spliter(1),  #胜负彩
    3:      Spliter_SSQ.Spliter(3),     #双色球
    4:      Spliter_PL.Spliter(4),      #七星彩
    5:      Spliter_PL.Spliter(5),      #排列三
    15:     Spliter_Common.Spliter(15), #6场半全场
    17:     Spliter_Common.Spliter(17), #4场进球
    28:     Spliter_LT.Spliter(28),     #大乐透
    44:     Spliter_DLC.Spliter(44),    #广西11选5
    45:     Spliter_DLC.Spliter(45),    #江西11选5
    46:     Spliter_JC.Spliter(46),     #竞足
    47:     Spliter_JC.Spliter(47),     #竞蓝
    60:     Spliter_PL.Spliter(60),     #排列五
    61:     Spliter_RJ.Spliter(61)      #任选9场
}

def get(lotId):
    return _LOTTERY_.get(int(lotId), None)
