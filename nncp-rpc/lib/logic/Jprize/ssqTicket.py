# coding=utf-8
import os
import re
import traceback
import common.Math as Math
from util.tools import Log

logger = Log().getLog()

_BONUS_ = {
    61: 'onenum',
    60: 'twonum',
    51: 'threenum',
    50: 'fournum',
    41: 'fournum',
    40: 'fivenum',
    31: 'fivenum',
    21: 'sixnum',
    11: 'sixnum'
}

_CODE_RE_ = re.compile('\D+')
_DT_RE_ = re.compile(r'\[D:(.*)\]\[T:(.*)\]\|\[D:(.*)\]\[T:(.*)\]')


def newBonus():
    return {
        'onenum': 0, 'twonum': 0, 'threenum': 0, 'fournum': 0,
        'fivenum': 0, 'sixnum': 0, 'zmax': 0,
    }


def calBonus(openCode, myCode):
    # 计算命中注数
    # code example: {'reds': ['01','02','03','04','05', '06'], 'blues':['01']}
    r = b = 0
    for i in openCode['reds']:
        if i in myCode['reds']:
            r += 1
    for i in openCode['blues']:
        if i in myCode['blues']:
            b += 1
    global _BONUS_
    return [_BONUS_.get(r * 10 + b), r, b]


def procBasic(openCode, info):
    # 普通玩法
    beishu = info['f_beishu']
    zhushu = 0
    bonus = newBonus()

    for code in info['f_fileorcode'].split('$'):
        reds, blues = code.split('|')
        reds = reds.strip().split(',')
        blues = blues.strip().split(',')
        if len(reds) > 6 or len(blues) > 1:
            for r in Math.combination(reds, 6):
                for b in Math.combination(blues, 1):
                    bs = calBonus(openCode, {'reds': r, 'blues': b})
                    zhushu += beishu
                    if bs[0]:
                        bonus[bs[0]] += beishu
                        bonus['zmax'] = 1
        else:
            bs = calBonus(openCode, {'reds': reds, 'blues': blues})
            zhushu += beishu
            if bs[0]:
                bonus[bs[0]] += beishu
                bonus['zmax'] = 1
    money = zhushu * 2
    ret = {'zhushu': zhushu, 'money': money, 'wtype': info['f_wtype'], 'tid': info['f_tid'],
           'srccode': info['f_fileorcode'],
           'onenum': bonus['onenum'], 'twonum': bonus['twonum'], 'threenum': bonus['threenum'],
           'fournum': bonus['fournum'], 'fivenum': bonus['fivenum'], 'sixnum': bonus['sixnum'], 'zmax': bonus['zmax']}
    return ret


def procDantuo(openCode, info):
    # 胆拖玩法
    beishu = info['f_beishu']
    zhushu = 0
    bonus = newBonus()
    cdata = ''
    global _DT_RE_
    for i in info['f_fileorcode'].split('$'):
        m = _DT_RE_.match(i)
        if not m:
            continue
        dan1 = m.group(1).split(',')
        tuo1 = m.group(2).split(',')
        dan2 = m.group(3).split(',')
        tuo2 = m.group(4).split(',')
        if dan1[0] == '':
            del dan1[0]
        if dan2[0] == '':
            del dan2[0]
        for i in Math.combination(tuo1, 6 - len(dan1)):
            reds = dan1 + i
            reds.sort()
            for j in Math.combination(tuo2, 1 - len(dan2)):
                blues = dan2 + j
                blues.sort()
                bs = calBonus(openCode, {'reds': reds, 'blues': blues})
                zhushu += beishu
                if bs[0]:
                    bonus[bs[0]] += beishu
                    bonus['zmax'] = 1

    money = zhushu * 2
    ret = {'zhushu': zhushu, 'money': money, 'wtype': info['f_wtype'], 'tid': info['f_tid'],
           'srccode': info['f_fileorcode'],
           'onenum': bonus['onenum'], 'twonum': bonus['twonum'], 'threenum': bonus['threenum'],
           'fournum': bonus['fournum'], 'fivenum': bonus['fivenum'], 'sixnum': bonus['sixnum'], 'zmax': bonus['zmax']}

    return ret


def calcGetmoney(expectinfo, ret):
    getmoney = 0
    if ret['zmax'] == 1 and [1, 377, 125].count(ret['wtype']) == 1:
        getmoney = ret['onenum'] * expectinfo['onemoney']
        getmoney += ret['twonum'] * expectinfo['twomoney']
        getmoney += ret['threenum'] * expectinfo['threemoney']
        getmoney += ret['fournum'] * expectinfo['fourmoney']
        getmoney += ret['fivenum'] * expectinfo['fivemoney']
        getmoney += ret['sixnum'] * expectinfo['sixmoney']
    else:
        getmoney = 0
    return getmoney


def calcPreGetmoney(expectinfo, ret):
    pregetmoney = 0
    if ret['zmax'] == 1 and [1, 377, 125].count(ret['wtype']) == 1:
        pregetmoney = ret['onenum'] * expectinfo['pre_onemoney']
        pregetmoney += ret['twonum'] * expectinfo['pre_twomoney']
        pregetmoney += ret['threenum'] * expectinfo['threemoney']
        pregetmoney += ret['fournum'] * expectinfo['fourmoney']
        pregetmoney += ret['fivenum'] * expectinfo['fivemoney']
        pregetmoney += ret['sixnum'] * expectinfo['sixmoney']
    else:
        pregetmoney = 0
    return pregetmoney


def procGuoguan(expectinfo, openCode, info):
    # 过关入口
    # 2 单式
    # 377 复式
    # 125 胆拖
    # 379 混投
    ret = []
    try:
        r = 0
        if [2, 377].count(info['f_wtype']) == 1:
            r = procBasic(openCode, info)
        elif [125].count(info['f_wtype']) == 1:
            r = procDantuo(openCode, info)
        else:
            return 0
        if r:
            if r['money'] != info['f_allmoney']:
                logger.error('bad money [%s] %s', r['money'], info)
                return 0
            getmoney = calcGetmoney(expectinfo, r)
            pregetmoney = calcPreGetmoney(expectinfo, r)
            r['getmoney'] = getmoney
            r['pregetmoney'] = pregetmoney
            return r
    except Exception as e:
        logger.error('proc failed: %s [%s]', info, traceback.format_exc())
        return 0
