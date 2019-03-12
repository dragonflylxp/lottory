#encoding=utf-8
import os
import sys
import re
import copy
import logging
import traceback

from common import Math 
from logic.Split import Config

#############################################
#              拆分规则说明                 #
# 1 票面金额不能超过20000元                 #
# 2 票面的倍数不能超过99倍                  #
# 3 单式和复式不能混在一起                  #
# 4 单式票每张不能超过5注                   #
# 5 复式和复式投注投注不能混在一起          #
#############################################
#from configer import JsonConfiger


class Spliter:
    def __init__( self, lotid ):
        self.lotId       = lotid
        self.TICK_RE     = Config.TICKET_RESTARICT[str(lotid)]
        self.limitMoney  = self.TICK_RE['money']
        self.singleMoney = Config.SINGLEMONEY
        self.flagzhushu  = self.limitMoney / self.singleMoney
        self.lmt_ds_zhushu = 3 if lotid in [1,61 ] else 5   #针对SFC/RJ投注单最多3注单式

    #入参: 投注内容-fileorcode, 玩法-wtype, 倍数-beishu
    #返回: [{fileorcode, wtype, beishu, zhushu}]
    def splitCodes( self, prjInfo ):
        retlist    = list()
        tmplist    = list()
        wtype = prjInfo['wtype']
        fileorcode = prjInfo['fileorcode']
        beishu     = prjInfo['beishu']

        #解析selecttype
        indexlist = list()
        if '' != prjInfo.get('selecttype', ''):
            indexlist = prjInfo['selecttype'].split(',')

        codelist = list()
        if int(wtype) == 3:
            """
            filelist = fileorcode.split(';')
            web_path = JsonConfiger.get_instance().get('path/check_web_path')
            save_path = JsonConfiger.get_instance().get('path/check_save_path')
            with open(save_path + filelist[1][len(web_path):]) as f:
                for line in f.readlines():
                    codelist.append(','.join(line.strip('\n')))
            """
            pass
        else:
            codelist = fileorcode.split('$')
        if not codelist:
            return list()

        for index in range( len(codelist) ):
            tmpdict = dict()
            tmpdict['code'] = codelist[index]
            if indexlist:
                tmpdict['index'] = indexlist[index]
            else:
                tmpdict['index'] = ''

            tmpdict['zhushu'] = self.countAllZhuShu( codelist[index].split('#')[0] )
            tmplist.append( tmpdict )

        #按照票面规则组织初始出票内容
        tlist   = list()
        tflist  = list()
        tzhushu = 0
        num     = 0
        tdict   = {'zhushu':0, 'fileorcode':''}
        tfdict  = {'zhushu':0, 'fileorcode':''}

        for info in tmplist:

            if info['zhushu'] > self.flagzhushu or not self.judgeCodeFD(info['code'].split('#')[0]):

                tfdict['zhushu']     = info['zhushu']
                tfdict['fileorcode'] = info['code'].split('#')[0]
                tfdict['beishu']     = beishu               
                tfdict['index']      = info['index']
                tfdict['wtype']      = Config.FSWTYPE[self.lotId]
                tflist.append( copy.deepcopy( tfdict ) )
                tfdict = {'zhushu':0, 'fileorcode':''}
                continue

            tzhushu += info['zhushu']
            if self.lmt_ds_zhushu == num+1:
                tdict['zhushu']     += tzhushu
                tdict['beishu']     =  beishu
                tdict['index']      += ','+info['index']
                tdict['fileorcode'] += '$' + info['code'].split('#')[0]
                tdict['wtype']      =  Config.DSWTYPE[int(self.lotId)]
                tlist.append( copy.deepcopy( tdict ) )              
                tdict  = {'zhushu':0, 'fileorcode':''}
                tzhushu= 0
                num    = 0
            else:
                num += 1
                if '' == tdict['fileorcode']:
                    tdict['index']      = info['index']
                    tdict['fileorcode'] = info['code'].split('#')[0]
                else:
                    tdict['index']      += ','+info['index']
                    tdict['fileorcode'] += '$' + info['code'].split('#')[0]
        if num > 0:
            tdict['zhushu'] = num
            tdict['beishu'] = beishu
            tdict['wtype']  = Config.DSWTYPE[self.lotId]
            tlist.append( copy.deepcopy( tdict ) )

        flist = tlist + tflist

        #组织出票
        for info in flist:
            retlist += self.splitCodesChild( info )

        return retlist

    def splitCodesChild( self, prjInfo ):
        ret = list()

        #根据注数-决定是否需要拆分方案内容
        if prjInfo['zhushu'] > self.flagzhushu:
            tmpret = self.splitCode( prjInfo )
            for info in tmpret:
                ret += self.splitBeishu( info['code'], self.TICK_RE['beishu'], int( prjInfo['beishu'] ), info['zhushu'], prjInfo['wtype'],prjInfo.get('index', '') )

        else:
            ret += self.splitBeishu( prjInfo['fileorcode'], self.TICK_RE['beishu'], int( prjInfo['beishu'] ), prjInfo['zhushu'], prjInfo['wtype'],prjInfo.get('index', '') )

        return ret

    #组织号码
    def splitCode( self, prjInfo ):

        retlist = list()
        tmplist = list()
        retdict = dict()

        #重新组织投注内容
        num      = 0
        codelist = prjInfo['fileorcode'].split(',')

        for i in codelist:
            tmpdict = dict()
            tmpdict['innum'] = num
            tmpdict['len']   = len(i.strip())
            tmpdict['code']  = i.strip()
            tmpdict['index'] = prjInfo.get('index', '')
            tmplist.append(tmpdict)
            num += 1

        tmplist = sorted( tmplist, key=lambda x:x['len'], reverse=True )

        #取得分割点
        innum,zhushu = self.getIndexNum( tmplist )
        if 0 == innum and 0 == zhushu:
            return list()

        qlist = tmplist[:innum]
        hlist = tmplist[innum:]

        for info in qlist:
            retdict[info['innum']] = info['code']

        rethlist = self.splitHlist( hlist, len(tmplist) - innum )

        #组成最终的号码
        for info in rethlist:
            retcode = ''
            tmpdict = dict()
            mdict   = dict(retdict.items() + info.items())
            for key in sorted( mdict.keys() ):
                if '' == retcode:
                    retcode = str( mdict[key] )

                else:
                    retcode += ',' + str( mdict[key] )

            tmpdict['code']  = retcode
            tmpdict['zhushu']= zhushu
            retlist.append(tmpdict)

        return retlist

    #处理N位以后的号码
    def splitHlist( self, hlist, flagnum ):
        tmplist = list()
        for info in hlist:
            for i in list( info['code'] ):
                tmpdict = dict()
                tmpdict[info['innum']] = i
                tmplist.append( tmpdict )

        td      = dict()
        cmblist = list()
        for info in Math.combination( tmplist, flagnum ):
            #去掉重复位置选项
            for i in info:
                td = dict(td, **i)

            if len(td) == flagnum:
                cmblist.append( td )

            td = dict()

        return cmblist

    #获得需要切分的位置
    def getIndexNum( self, codelist ):
        zhushu = 1
        innum  = 0

        for i in range(len(codelist)):
            zhushu = zhushu * codelist[i]['len']

            if zhushu * self.singleMoney > self.limitMoney:
                return i, zhushu/codelist[i]['len']

        return 0, 0

    #倍数拆分
    def splitBeishu( self, strcode, lmt_beishu, beishu, zhushu, wtype,selecttype ):
        ret = list()
        b   = beishu

        #重新计算倍数标杆
        if ( int(zhushu) * int(beishu) * int(self.singleMoney) ) > int( self.limitMoney ):
            lmt_beishu = int( self.limitMoney ) / ( int(zhushu) * int(self.singleMoney) )

        while b > lmt_beishu:
            item = { 'code':strcode, 'beishu':lmt_beishu, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
            ret.append(item)
            b = b - lmt_beishu

        """SFC/RJ投注单支持的倍数: 1,2,3,4,5,6,7,8,9,10,15,20
        """
        if self.lotId in [1,61]:
            while b > 20:
                item = { 'code':strcode, 'beishu':20, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                b = b - 20 
            if b == 20:
                item = { 'code':strcode, 'beishu':20, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                return ret

            while b > 15:
                item = { 'code':strcode, 'beishu':15, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                b = b - 15 
            if b == 15:
                item = { 'code':strcode, 'beishu':15, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                return ret

            while b > 10:
                item = { 'code':strcode, 'beishu':10, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                b = b - 10 
            if b == 10:
                item = { 'code':strcode, 'beishu':10, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
                ret.append(item)
                return ret

        if b > 0:
            item = { 'code':strcode, 'beishu':b, 'zhushu':zhushu, 'wtype':wtype,'selecttype':selecttype }
            ret.append(item)

        return ret

    #计算总注数
    def countAllZhuShu( self, codes ):
        zhushu = 1

        for info in codes.split(','):
           zhushu *= len(info)

        return zhushu

    #判断code是单式还是复式
    def judgeCodeFD( self, codes ):

        for info in codes.split(','):

            if len(list(info)) > 1:
                return False

        return True

if __name__ == '__main__':
    import time
    t1 = time.time()
    fileorcode = {'wtype':395, 'fileorcode':'310,310,310,310,310,310,310,310,310,310,310,310,310,310','beishu':1}
    obj = Spliter(1)
    obj.splitCodes( fileorcode )
    print time.time() - t1
