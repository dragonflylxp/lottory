#encoding=utf-8
import os
import sys
import re
import copy
import logging
import time
import traceback

from common import Math
from logic.Split import Config
import Spliter_Common


class Spliter( Spliter_Common.Spliter ):
    def __init__( self, lotid ):
        Spliter_Common.Spliter.__init__( self, lotid )

    #入参: 投注内容-fileorcode, 玩法-wtype, 倍数-beishu
    #返回: [{fileorcode, wtype, beishu, zhushu}]
    def splitCodes( self, prjInfo ):
        retlist    = list()
        tmplist    = list()
        wtype = prjInfo['wtype']
        fileorcode = self.handleCodes( prjInfo )
        beishu     = prjInfo['beishu']
        flagzhushu = self.limitMoney / self.singleMoney


        codelist = fileorcode.split('$')
        for info in codelist:
            tmpdict = dict()
            tmpdict['code']   = info
            tmpdict['zhushu'] = self.countAllZhuShu( info )
            tmplist.append( tmpdict )


        tlist   = list()
        tflist  = list()
        tzhushu = 0
        num     = 0
        tdict   = {'zhushu':0, 'fileorcode':''}
        tfdict  = {'zhushu':0, 'fileorcode':''}
        for info in tmplist:
            if info['zhushu'] > flagzhushu or not self.judgeCodeFD(info['code']):
                tfdict['zhushu']     = info['zhushu']
                tfdict['fileorcode'] = info['code'].split('#')[0]
                tfdict['beishu']     = beishu
                tfdict['wtype']      = Config.FSWTYPE[self.lotId]
                tflist.append( copy.deepcopy( tfdict ) )
                tfdict = {'zhushu':0, 'fileorcode':''}
                continue

            tzhushu += info['zhushu']
            if tzhushu > flagzhushu or 3 == num+1:  # RJ投注单最多3注单式
                tdict['zhushu']     += tzhushu
                tdict['beishu']     =  beishu
                tdict['fileorcode'] += '$' + info['code'].split('#')[0]
                tdict['wtype']      =  Config.DSWTYPE[self.lotId]
                tlist.append( copy.deepcopy( tdict ) )
                tdict  = {'zhushu':0, 'fileorcode':''}
                tzhushu= 0
                num    = 0

            else:
                num += 1
                if '' == tdict['fileorcode']:
                    tdict['fileorcode'] = info['code'].split('#')[0]

                else:
                    tdict['fileorcode'] += '$' + info['code'].split('#')[0]

        if tzhushu > 0:
            tdict['zhushu'] = tzhushu
            tdict['beishu'] = beishu
            tdict['wtype']  = Config.DSWTYPE[self.lotId]
            tlist.append( copy.deepcopy( tdict ) )

        flist = tlist + tflist
        #组织出票
        for info in flist:
            retlist += self.splitCodesChild( info )

        return retlist

    #´¦ÀíÈÎ¾ÅºÅÂë
    def handleCodes( self, prjInfo ):
        wtype = int( prjInfo['wtype'] )
        codes = prjInfo['fileorcode']
        ret   = ''

        for info in codes.split('$'):
            tinfo = info.split('#')
            tcode = ''

            if 2 == len( tinfo ):
                wtype = int( tinfo[1].strip() )

            if Config.XDTWTYPE[int(self.lotId)] == wtype:
                tcode = self.splitCodeDT( tinfo[0] )

            else:
                tcode = self.splitCodeFS( tinfo[0] )

            if '' == ret:
                ret = tcode

            else:
                ret += '$' + tcode

        return ret


    #²ð·Öµ¨ÍÏ
    def splitCodeDT( self, codes ):
        dt_re  = re.compile(r'\[D:(.*)\]\[T:(.*)\]')
        tmpstr = dt_re.match(codes)
        dcode  = tmpstr.group(1).split(',')
        tcode  = tmpstr.group(2).split(',')
        ret    = ''

        ddict = dict()
        for info in range(Config.CODENUM[int(self.lotId)]['changcinum']):
            ddict[info] = dcode[info]

        tlist = list()
        for info in range(Config.CODENUM[int(self.lotId)]['changcinum']):
            tmpdict = dict()
            if '*' == tcode[info].strip():
                continue

            tmpdict[info] = tcode[info]
            tlist.append(tmpdict)

        tmplist = list()
        yunum   = Config.CODENUM[int(self.lotId)]['codenum'] - (Config.CODENUM[int(self.lotId)]['changcinum'] - dcode.count('*'))
        for info in Math.combination( tlist, yunum ):
            tmpdict = copy.deepcopy( ddict )

            for var in info:
                tmpdict.update( var )

            if self.countAllZhuShu( ','.join( tmpdict.values() ) ) > self.flagzhushu:
                tmplist += self.splitOverCode( tmpdict, info )

            else:
                tmplist.append( tmpdict )

        for info in tmplist:

            if '' == ret:
                ret = ','.join( info.values() )

            else:
                ret += '$' + ','.join( info.values() )

        return ret

    #²ð·Ö³¬¹ý10000×¢µÄºÅÂë
    def splitOverCode( self, dcode, tcode ):
        ret   = list()
        fdict = dict()

        for info in tcode:

            if len(info.values()) > len(ret):
                fdict = info

        tcode.remove(fdict)

        tmplist = list()
        for info in list( fdict.values()[0] ):
            tmpdict = {fdict.keys()[0]:info}
            tmplist.append( tmpdict )

        for info in tmplist:
            tmpdict = copy.deepcopy( dcode )
            tmpdict.update( info )
            ret.append( tmpdict )

        return ret

    #²ð·Ö¸´Ê½
    def splitCodeFS( self, codes ):
        ret = ''
        fcode = codes.split(',')
        if Config.CODENUM[int(self.lotId)]['codenum'] == (14 - fcode.count('*') ):
            ret = codes
            return ret

        ddict = dict()
        for info in range(14):
            ddict[info] = '*'

        tlist = list()
        for info in range(14):
            tmpdict = dict()

            if '*' == fcode[info].strip():
                continue

            tmpdict[info] = fcode[info]
            tlist.append(tmpdict)

        tmplist = list()
        yunum   = Config.CODENUM[int(self.lotId)]['codenum']
        for info in Math.combination( tlist, yunum ):
            tmpdict = copy.deepcopy( ddict )

            for var in info:
                tmpdict.update( var )

            tmplist.append( tmpdict )

        for info in tmplist:

            if '' == ret:
                ret = ','.join( info.values() )

            else:
                ret += '$' + ','.join( info.values() )

        return ret

if __name__ == '__main__':
    import time
    t1 = time.time()
    fileorcode = {'wtype':409,'fileorcode':'[D:*,*,*,10,*,*,310,*,*,*,*,*,*,*][T:3,1,3,*,0,1,*,1,0,1,1,*,*,*]', 'beishu':1 }
    obj = Spliter(61)
    print obj.splitCodes( fileorcode )
    print time.time() - t1
