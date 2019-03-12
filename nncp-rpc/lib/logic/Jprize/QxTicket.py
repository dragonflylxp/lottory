#coding=utf-8
import os
import re
import traceback
from util.tools import Log
logger = Log().getLog()

_BONUS_ = {
    7: 'onenum',
    6: 'twonum',
    5: 'threenum',
    4: 'fournum',
    3: 'fivenum',
    2: 'sixnum',
}

''' 计算命中注数
openCode  开奖号码
singleCode 拆分后的单注
'''
def calBonus(openCode, singleCode):
    count = 0 #连续命中个数
    max = 0 #最大连续命中个数
    for index in range(0,7):
        if singleCode[index] == openCode[index]:
            count += 1
        else:
            if count>max:
                max = count
            count = 0
    if count > max:
        max = count

    return _BONUS_.get(max)

''' 递归拆分投注号码
codeArr 号码数组
idx 号码数下标
temp 保存临时投注号码
res 返回拆分结果
'''
def split (codeArr,idx,temp,res):
    for code in codeArr[idx]:
        if len(codeArr) == idx + 1:
            res.append(temp+code)
        else:
            split(codeArr,idx+1,temp+code,res)

''' 计算税后奖金
expectinfo 期号信息
bonus 中奖信息
'''
def calcGetmoney(expectinfo,bonus):
    getmoney = 0
    if bonus['zmax'] ==1:
        getmoney = bonus['onenum']*expectinfo['onemoney'] 
        getmoney += bonus['twonum']*expectinfo['twomoney'] 
        getmoney +=  bonus['threenum']*expectinfo['threemoney'] 
        getmoney +=  bonus['fournum']*expectinfo['fourmoney'] 
        getmoney +=  bonus['fivenum']*expectinfo['fivemoney'] 
        getmoney +=  bonus['sixnum']*expectinfo['sixmoney'] 
    return getmoney

''' 计算税前奖金
expectinfo 期号信息
bonus 中奖信息
'''
def calcPreGetmoney(expectinfo,bonus):
    pregetmoney = 0
    if bonus['zmax'] ==1:
        pregetmoney = bonus['onenum']*expectinfo['onemoney']
        pregetmoney += bonus['twonum']*expectinfo['twomoney']
        pregetmoney +=  bonus['threenum']*expectinfo['threemoney'] 
        pregetmoney +=  bonus['fournum']*expectinfo['fourmoney'] 
        pregetmoney +=  bonus['fivenum']*expectinfo['fivemoney'] 
        pregetmoney +=  bonus['sixnum']*expectinfo['sixmoney'] 
    return pregetmoney

''' 票算奖
expectinfo 期号信息
openCode   开奖号码
ticket   票
'''
def procTicket(expectinfo, openCode, ticket):
    bonus = {'onenum': 0,
             'twonum': 0,
             'threenum': 0,
             'fournum': 0,
             'fivenum': 0,
             'sixnum': 0,
             'zmax': 0,
             'getmoney':0,
             'pregetmoney':0}
    try:
        res = []
        beishu = ticket['f_beishu']     
        for line in ticket['f_fileorcode'].split('$'):
            codeArr = line.split('|')
            '''拆分投注号码到res '''
            split(codeArr,0,'',res)

        for singleCode in res:
            bonusName = calBonus(openCode,singleCode)
            if bonusName:
                bonus[bonusName] += beishu
                bonus['zmax'] = 1
        getmoney = calcGetmoney(expectinfo,bonus)
        pregetmoney = calcPreGetmoney(expectinfo,bonus)
        bonus['getmoney'] = getmoney
        bonus['pregetmoney'] = pregetmoney
        bonus['tid'] = ticket['f_ticketid']
        bonus.update(ticket)
        return bonus
    except:
        logger.error('qxc procticket failed: %s [%s]', ticket, traceback.format_exc())
        return {} 

if __name__ == '__main__':
    expectinfo = {'expect':'15001',
                  'opencode':'1,2,3,4,5,6,7',
                  'pre_onemoney': 100000,
                  'pre_twomoney':10000,
                  'onemoney':80000,
                  'twomoney':10000,
                  'threemoney':1800,
                  'fourmoney':300,
                  'fivemoney':20,
                  'sixmoney':5}
    ticket = {'f_ticketid':'14009QX22582',
              'f_wtype':390,
              'f_beishu':1,
              'f_allmoney':10,
              'f_fileorcode':'1,2,3,4,5,6,7$8,5,0,2,7,8,8$2,3,3,3,5,4,4$4,0,3,7,3,8,9$4,5,8,8,8,5,2',
              'f_expect':'14009'}
    openCode = expectinfo['opencode'].split(',')
    bonus = procTicket(expectinfo,openCode,ticket)
    print bonus
