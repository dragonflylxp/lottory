#encoding=utf-8

import copy
import logging
import itertools
from common import Math
import Spliter_Common


class Spliter( Spliter_Common.Spliter ):
    def __init__( self, lotid ):
        Spliter_Common.Spliter.__init__( self, lotid )

    #入参: 投注内容-fileorcode, 玩法-wtype, 倍数-beishu
    #返回: [{fileorcode, wtype, beishu, zhushu}]
    def splitCodes( self, prjInfo ):
        retlist    = list()
        tmplist    = list()
        fileorcode = prjInfo['fileorcode']
        beishu     = prjInfo['beishu']
        wtype      = prjInfo['wtype']

        #解析selecttype
        indexlist = list()
        if '' != prjInfo.get('selecttype', ''):
            indexlist = prjInfo['selecttype'].split(',')

        #拆codes
        codelist = fileorcode.split('$')
        if list() == codelist:
            return list()
        for index in range( len(codelist) ):
            tmpdict = dict()
            if int(wtype) == 256 and codelist[index].find('#') != -1: #混投
                tmpdict['code'],tmpdict['wtype'] = codelist[index].split('#')
            else:
                tmpdict['code'] = codelist[index]
                tmpdict['wtype'] = wtype

            if list() != indexlist:
                tmpdict['index'] = indexlist[index]
            else:
                tmpdict['index'] = ''

            if int(tmpdict['wtype']) == 255:
                # 任选八复式转单式
                code_fs = tmpdict['code'].split(',')
                code_ds_list = [','.join(x) for x in list(itertools.combinations(code_fs, 8))]
                for code_ds in code_ds_list:
                    dstmpdict = dict()
                    dstmpdict['wtype'] = tmpdict['wtype']
                    dstmpdict['code'] = code_ds
                    dstmpdict['zhushu'] = 1
                    tmplist.append( dstmpdict )
                continue

            tmpdict['zhushu'] = self.countAllZhuShu( tmpdict['code'],tmpdict['wtype'] )

            tmplist.append( tmpdict )
        tmplist.sort(key=lambda tmp: tmp.get('wtype'))

        #按照票面规则组织初始出票内容
        tlist   = list()
        tflist  = list()
        tzhushu = 0
        num     = 0
        tdict   = {'zhushu':0, 'fileorcode':''}
        tfdict  = {'zhushu':0, 'fileorcode':''}
        wtype_tmp = tmplist[0].get('wtype')
        for info in tmplist:
            if info.get('zhushu') > self.flagzhushu or info.get('zhushu') > 1:
                tfdict['zhushu']     = info.get('zhushu')
                tfdict['fileorcode'] = info.get('code')
                tfdict['beishu']     = beishu
                tfdict['wtype']      = info.get('wtype')
                tflist.append( copy.deepcopy( tfdict ) )
                tfdict = {'zhushu':0, 'fileorcode':''}
                continue

            # 如果玩法变更并且不足票数要求
            if wtype_tmp != info.get('wtype') and num != 0:
                tdict['zhushu']     += tzhushu
                tdict['beishu']     =  beishu
                tdict['wtype']      = wtype_tmp
                tlist.append( copy.deepcopy( tdict ) )
                tdict  = {'zhushu':0, 'fileorcode':''}
                tzhushu= 0
                num    = 0

            tzhushu += info.get('zhushu')
            if tzhushu > self.flagzhushu or 5 == num+1:
                tdict['zhushu']     += tzhushu
                tdict['beishu']     =  beishu
                tdict['fileorcode'] += '$' + info.get('code')
                tdict['wtype']      = info.get('wtype')
                tlist.append( copy.deepcopy( tdict ) )
                tdict  = {'zhushu':0, 'fileorcode':''}
                tzhushu= 0
                num    = 0
            else:
                num += 1
                wtype_tmp = info.get('wtype')
                if '' == tdict['fileorcode']:
                    tdict['fileorcode'] = info.get('code')
                else:
                    tdict['fileorcode'] += '$' + info.get('code')

        if tzhushu > 0:
            tdict['zhushu'] = tzhushu
            tdict['beishu'] = beishu
            tdict['wtype']  = wtype_tmp
            tlist.append( copy.deepcopy( tdict ) )

        flist = tlist + tflist

        #组织出票
        for info in flist:
            retlist += self.splitCodesChild( info )

        return retlist

    def countAllZhuShu(self, codes, wtype):
        wtype = int(wtype)
        #任选
        if wtype in [249,250,251,252,253,254,255]:
            nneeds = wtype - 247
            nchose = len(codes.split(','))
            if nneeds > nchose:
                return 0
            return Math.C(nchose,nneeds)

        #直选
        # if wtype == 244:
        #     return len(codes.split(','))
        if wtype in [244,245,246]:
            chose = codes.split('|')
            chose[0] = chose[0].split(',') if chose[0]!='-' else ['-1']
            chose[1] = chose[1].split(',') if chose[1]!='-' else ['-1']
            chose[2] = chose[2].split(',') if chose[2]!='-' else ['-1']
            zhushu = 0
            for a in chose[0]:
                for b in chose[1]:
                    for c in chose[2]:
                        if a==b and a!='-1':continue
                        if b==c and b!='-1':continue
                        if c==a and c!='-1':continue
                        zhushu+= 1
            return zhushu

        #组选
        if wtype in [247,248]:
            nneeds = wtype - 245
            nchose = len(codes.split(','))
            if nneeds > nchose:
                return 0
            return Math.C(nchose,nneeds)

if __name__ == '__main__':
    import time
    t1 = time.time()
    fileorcode = {'wtype':256,'fileorcode':'02,03,05,06,09#252$01,07#249$03,05,08#250$03,04,05,07#251$02,03,04,05,06,08#253$01,02,03,04,05,06,07,08,09,10,11#255$01,02,03,04,05,06,07,08,09,10,11#255$01,02,03,04,05,06,07,08,09,10,11|-|-|-|-#244$01,02,03,04,05,06,07,08,09,10,11#249$01,02,03,04,05,06,07,08,09,10,11#250$01,02,03,04,05,06,07,08,09,10,11#251$01,02,03,04,05,06,07,08,09,10,11#252$01,02,03,04,05,06,07,08,09,10,11#253', 'beishu':1 }
    obj = Spliter(45)
    print obj.splitCodes( fileorcode )
    print time.time() - t1
