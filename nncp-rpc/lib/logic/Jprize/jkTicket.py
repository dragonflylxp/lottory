# coding:utf-8

import os
import re
import traceback
from decimal import Decimal

import common.Math as Math
from util.tools import Log
import itertools
import functools

logger = Log().getLog()

decoder = lambda code: tuple(int(i) for i in code.split(','))
fixed_decoder = lambda code: tuple(set(decoder(i)) for i in code.split('-')[:2]) # 胆码, 拖码

prize_level = {"F1": 13,    # 前一
               "F2": 130,   # 前二
               "F3": 1170,  # 前三
               "G2": 65,    # 前二组选
               "G3": 195,   # 前三组选
               "I2": 6,     # 任二
               "I3": 19,    # 任三
               "I4": 78,    # 任四
               "I5": 540,   # 任五
               "I6": 90,    # 任六
               "I7": 26,    # 任七
               "I8": 9,     # 任八
               }

def procGuoguan(expectinfo, opencode, ticketinfo):
    # 过关入口
    # == 玩法 ==
    # ** 244:前一直选 245:前二直选 246:前三直选 247:前二组选 248:前三组选
    # ** 249:任选二 250:任选三 251:任选四 252:任选五 253:任选六 254:任选七 255:任选八
    ret = None
    try:
        ret = {'getmoney': Decimal('0.00'),
               'pregetmoney': Decimal('0.00'),
               'tid': ticketinfo.get('f_tid')}
        fileorcode = ticketinfo.get('f_fileorcode').split('$')
        wtype = ticketinfo.get('f_wtype')
        beishu = ticketinfo.get('f_beishu')
        allgetmoney = 0
        allpregetmoney = 0
        allgetnum = 0
        for usercode in fileorcode:
            level, zzhushu, money = _guoguan(decoder(opencode), wtype, usercode, prize_level)
            logger.info('------->算奖结果%s %s %s<--------------', level, zzhushu, money)
            allgetmoney += money
            allpregetmoney += money if money < 10000 else money * 0.8
            allgetnum += zzhushu
        ret['getmoney'] = allgetmoney * beishu
        ret['pregetmoney'] = allpregetmoney * beishu
        ret['zhushu'] = allgetnum * beishu
    except:
        logger.error('proc failed: %s [%s]', ticketinfo, traceback.format_exc())
    finally:
        return ret

##
# @param opencode int_list (1, 2, 3, 4, 5)
# @param usercode string   [356]08,12
# @param plevel 奖级 {F1, F2, G2, F3, G3, I2, I3, I4, I5, I6, I7, I8}
# @return (奖级, 中奖注数, 中奖金额)
def _guoguan(opencode, wtype, usercode, plevel):
    """
    :param opencode: 开奖号码
    :param wtype:   玩法
    :param usercode:  投注内容
    :param plevel:   奖级
    :return:
    """
    logger.debug("11选5过关 %s %s" % (opencode, usercode))
    gg_func = "_guoguan%s" % wtype
    f = globals().get(gg_func, None)
    if f:
        l = f(opencode, usercode, plevel)
        logger.debug("RESULT: %s OPENCODE: %s USERCODE: %s" % (l, opencode, usercode))
        return l
    else:
        logger.error("invalid wtype %s" % wtype)
        return tuple()

# 前X
def _first(x, opencode, code, plevel):
    PLEVEL = "F%d" % int(x)
    c = [decoder(i) for i in code.split('|')[:x]]
    return (PLEVEL, 1, plevel[PLEVEL]) if False not in map(lambda param: param[0] in param[1], zip(opencode[:x], c)) else (PLEVEL, 0, 0)

_guoguan244 = functools.partial(_first, 1)
_guoguan245 = functools.partial(_first, 2)
_guoguan246 = functools.partial(_first, 3)

# 前X组选
def _group(x, opencode, code, plevel):
    PLEVEL = "G%d" % int(x)
    c = decoder(code)
    return (PLEVEL, 1, plevel[PLEVEL]) if set(opencode[:x]).issubset(set(c)) else (PLEVEL, 0, 0)

_guoguan247 = functools.partial(_group, 2)
_guoguan248 = functools.partial(_group, 3)

# 任选X [1 - 5]
def _optionalA(x, opencode, code, plevel):
    PLEVEL = "I%d" % int(x)
    c = decoder(code)
    cnt = [set(set(i)).issubset(opencode) for i in itertools.combinations(c, x)].count(True)
    return (PLEVEL, cnt, cnt * plevel[PLEVEL])

_guoguan249 = functools.partial(_optionalA, 2)
_guoguan250 = functools.partial(_optionalA, 3)
_guoguan251 = functools.partial(_optionalA, 4)
_guoguan252 = functools.partial(_optionalA, 5)

# 任选X [6 - 8]
def _optionalB(x, opencode, code, plevel):
    PLEVEL = "I%d" % int(x)
    c = decoder(code)
    cnt = [set(opencode).issubset(set(i)) for i in itertools.combinations(c, x)].count(True)
    return (PLEVEL, cnt, cnt * plevel[PLEVEL])

_guoguan253 = functools.partial(_optionalB, 6)
_guoguan254 = functools.partial(_optionalB, 7)
_guoguan255 = functools.partial(_optionalB, 8)

# 前X组选胆拖
def _group_fixed(x, opencode, code, plevel):
    PLEVEL = "G%d" % int(x)
    fixeds, unfixeds = fixed_decoder(code)
    opencodes = set(opencode[:x])
    return (PLEVEL, 1, plevel[PLEVEL]) if fixeds.issubset(opencodes) and (opencodes - fixeds).issubset(unfixeds) else (PLEVEL, 0, 0)

_guoguan261 = functools.partial(_group_fixed, 2)
_guoguan264 = functools.partial(_group_fixed, 3)

# 任选X胆拖 [1 - 5]
def _optionalA_fixed(x, opencode, code, plevel):
    PLEVEL = "I%d" % int(x)
    fixeds, unfixeds = fixed_decoder(code)
    opencodes = set(opencode)
    cnt = 0
    # a. 胆码全在开奖号码里面
    # b. 拖码中选 X-len(胆码) 个, 在开奖号码里面, 则中一注
    if fixeds.issubset(opencodes):
        cnt = [set(i).issubset(opencodes) for i in itertools.combinations(unfixeds, x - len(fixeds))].count(True)
    return (PLEVEL, cnt, cnt * plevel[PLEVEL])

_guoguan278 = functools.partial(_optionalA_fixed, 2)
_guoguan279 = functools.partial(_optionalA_fixed, 3)
_guoguan265 = functools.partial(_optionalA_fixed, 4)
_guoguan266 = functools.partial(_optionalA_fixed, 5)

# 任选X胆拖 [6 - 8]
def _optionalB_fixed(x, opencode, code, plevel):
    PLEVEL = "I%d" % int(x)
    fixeds, unfixeds = fixed_decoder(code)
    opencodes = set(opencode)
    # a. 开奖号码中去除胆码
    # b. 拖码中选 X-len(胆码) 个, 剩下的号码在里面, 则中一注
    remains = opencodes - fixeds
    cnt = [remains.issubset(i) for i in itertools.combinations(unfixeds, x - len(fixeds))].count(True)
    return (PLEVEL, cnt, cnt * plevel[PLEVEL])

_guoguan267 = functools.partial(_optionalB_fixed, 6)
_guoguan268 = functools.partial(_optionalB_fixed, 7)
_guoguan280 = functools.partial(_optionalB_fixed, 8)


