# encoding=utf-8
import os
import sys
import re
import copy
import logging
import traceback

from logic.Split import Config
import common.Math as Math
import Spliter_Common
from util.tools import Log

logger = Log().getLog()


class Spliter(Spliter_Common.Spliter):
    def __init__(self, lotid):
        self.lotId = lotid
        self.ArrInfo = Config.TICKET_INFO[str(lotid)]
        self.TICK_RE = Config.TICKET_RESTARICT[str(lotid)]
        self.limitMoney = self.TICK_RE['money']
        self.singleMoney = Config.SINGLEMONEY

    # 入参: 投注内容-fileorcode, 玩法-wtype, 倍数-beishu
    # 返回: [{fileorcode, wtype, beishu, zhushu}]
    def splitCodes(self, prjInfo):
        ret = list()

        if str(prjInfo['wtype']) in Config.ZJWTYPE:
            self.singleMoney = Config.ZJSINGLEMONEY
            self.limitMoney = self.TICK_RE['zjmoney']

        if int(prjInfo['wtype']) not in Config.DTWtype:
            ret = self.splitCodes_PT(prjInfo)

        else:
            ret = self.splitCodes_DT(prjInfo)

        return ret

    def splitCodes_PT(self, prjInfo):
        beishu = int(prjInfo['beishu'])
        ccArray = prjInfo['fileorcode'].split('$')

        # 单注合票列表
        comb_list = list()
        ret = list()

        for item in ccArray:
            # 红球
            rArr = (item.split('|')[0]).split(',')
            # 篮球
            bArr = (item.split('|')[1]).split(',')

            # 红球注数
            r_zhushu = self.ArrInfo[len(rArr)][6]
            # 篮球注数
            b_zhushu = self.ArrInfo[len(bArr)][1]
            zhushu = r_zhushu * b_zhushu

            if zhushu == 1:
                ret_h = self.handDanshi(comb_list, rArr, bArr, beishu, zhushu)
                ret += ret_h
                continue

            if r_zhushu > self.limitMoney / self.singleMoney:
                # 1 拆前区前17球组合
                ret_h = self.handFushi(rArr[0:17], bArr, beishu)
                ret += ret_h

                # 2 拆前区后16个球的组合
                if len(rArr[17:]) > 5:
                    ret_h = self.handFushi(rArr[17:], bArr, beishu)
                    ret += ret_h

                # 3 拆两个区的交集
                for r in self.splitRedBall(rArr):

                    if b_zhushu == 1:
                        ret_h = self.handDanshi(comb_list, r, bArr, beishu, zhushu)

                    else:
                        ret_h = self.handFushi(r, bArr, beishu)

                    ret += ret_h

            else:
                ret_h = self.handFushi(rArr, bArr, beishu)

                ret += ret_h

        # logging.info( comb_list )
        if len(comb_list) > 0:
            tmp_ret = self.splitBeishu('$'.join(comb_list), self.TICK_RE['beishu'], beishu, len(comb_list))
            ret += tmp_ret

        return ret

    # 红球超过10000注拆分红球
    def splitRedBall(self, rArr):
        ret = list()
        r1 = rArr[0:16]
        r2 = rArr[16:]

        max = 5
        if len(r2) < 6:
            max = len(r2)

        for i in range(1, max + 1):
            tmp = list()
            # 不能同时调用两以上yield 蛋疼<<<<<碎了不
            for b in Math.combination(r2, i):
                tmp.append(b)

            for a in Math.combination(r1, 6 - i):
                for b in tmp:
                    yield a + b

    # 单式
    def handDanshi(self, tmp_list, rArr, bArr, beishu, zhushu):

        ret_list = list()
        tmp_list.append(','.join(rArr) + '|' + ','.join(bArr))

        # 5注一票
        if len(tmp_list) == Config.LIMIT_NUM:
            ret_list = self.splitBeishu('$'.join(tmp_list), self.TICK_RE['beishu'], beishu, len(tmp_list))
            del tmp_list[:Config.LIMIT_NUM]

        return ret_list

    # 拆分后的小复式
    def handFushi(self, rArr, bArr, beishu):
        zhushu = 0

        # 红球注数
        r_zhushu = self.ArrInfo[len(rArr)][6]

        # 篮球注数
        b_zhushu = self.ArrInfo[len(bArr)][1]
        zhushu = r_zhushu * b_zhushu

        # 单票最大倍数
        max_beishu = self.TICK_RE['beishu']

        # 可拆分最大倍数
        lmt_beishu = max_beishu

        # 拆分结果
        ret = list()

        # 此处以钱为标杆
        if zhushu * self.singleMoney * max_beishu > self.limitMoney:
            lmt_beishu = self.limitMoney / (zhushu * self.singleMoney)

            # 需要拆蓝球
            if lmt_beishu == 0:
                tmpArr = Math.combination(bArr, 1)

                for info in tmpArr:
                    info_zhushu = self.ArrInfo[len(rArr)][6] * 1
                    lmt_beishu = self.limitMoney / (info_zhushu * self.singleMoney)
                    tmp_ret = self.splitBeishu(','.join(rArr) + '|' + ','.join(bArr), lmt_beishu, beishu, info_zhushu)
                    # ret.append(tmp_ret)
                    ret += tmp_ret

            # 不需要拆篮球
            else:
                tmp_ret = self.splitBeishu(','.join(rArr) + '|' + ','.join(bArr), lmt_beishu, beishu, zhushu)
                # ret.append(tmp_ret)
                ret += tmp_ret

        else:
            tmp_ret = self.splitBeishu(','.join(rArr) + '|' + ','.join(bArr), lmt_beishu, beishu, zhushu)
            ret += tmp_ret

        return ret

    # 倍数拆分
    def splitBeishu(self, code, lmt_beishu, beishu, zhushu):
        ret = list()
        b = beishu

        while b > lmt_beishu:
            item = {'code': code, 'beishu': lmt_beishu, 'zhushu': zhushu}
            ret.append(item)
            b = b - lmt_beishu

        if b > 0:
            item = {'code': code, 'beishu': b, 'zhushu': zhushu}
            ret.append(item)

        return ret

    def splitCodes_DT(self, prjInfo):
        beishu = int(prjInfo['beishu'])
        ccArray = prjInfo['fileorcode'].split('$')

        # 单注合票列表
        comb_list = list()
        ret = list()
        dt_re = re.compile(r'\[D:(.*)\]\[T:(.*)\]\|(.*)')
        for item in ccArray:
            m = dt_re.match(item)

            # 红球胆码
            red_d = m.group(1).split(',')

            # 红球拖码
            red_t = m.group(2).split(',')

            # 篮球0胆全拖
            blue_d = []
            blue_t = m.group(3).split(',')

            if red_d[0] == '':
                del red_d[0]

            # 红球注数
            r_zhushu = self.ArrInfo[len(red_t)][6 - len(red_d)]

            # 篮球注数
            b_zhushu = self.ArrInfo[len(blue_t)][1 - len(blue_d)]
            zhushu = r_zhushu * b_zhushu

            # 单票最大倍数
            max_beishu = self.TICK_RE['beishu']

            # 可拆分最大倍数
            lmt_beishu = max_beishu
            if zhushu * self.singleMoney * max_beishu > self.limitMoney:
                lmt_beishu = self.limitMoney / (zhushu * self.singleMoney)

            ret += self.splitDTBeishu(red_d, red_t, blue_d, blue_t, lmt_beishu, beishu, zhushu)

        return ret

    # 胆拖倍数拆分
    def splitDTBeishu(self, red_d, red_t, blue_d, blue_t, lmt_beishu, beishu, zhushu):
        ret = list()
        b = beishu
        tmpcode = ''

        # 修改无胆的时候的bug，20150216 holyandyao
        if len(red_d) == 0:
            tmpcode = '[D:][T:' + ','.join(red_t) + ']'
        else:
            tmpcode = '[D:' + ','.join(red_d) + '][T:' + ','.join(red_t) + ']'
        tmpcode = tmpcode + '|'

        if len(blue_d) == 0:
            tmpcode = tmpcode + '[D:][T:' + ','.join(blue_t) + ']'
        else:
            tmpcode = tmpcode + '[D:' + ','.join(blue_d) + '][T:' + ','.join(blue_t) + ']'

        while b > lmt_beishu:
            item = {'code': tmpcode, 'beishu': lmt_beishu, 'zhushu': zhushu}
            ret.append(item)
            b = b - lmt_beishu

        if b > 0:
            item = {'code': tmpcode, 'beishu': b, 'zhushu': zhushu}
            ret.append(item)

        return ret


if __name__ == '__main__':
    args = {
        'fileorcode': '[D:28,30][T:09,11,29,30,31]|02,03',
        #'fileorcode': '01,06,07,08,09,10,11,12|02,03,04',
        'beishu': '3', 'wtype': '125'}
    obj = Spliter(3)
    ret = obj.splitCodes(args)
    print ret
