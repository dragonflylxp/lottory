#encoding=utf-8

import os
import sys
import copy
import logging
import traceback

import Config
import LotCommon
import Operator
from util.tools import Log

logger = Log().getLog()

class LotLT( LotCommon.Lottery ):
    ''' 普通彩种  '''
    def __init__( self, lotid ):
        ''' 初始化 '''
        LotCommon.Lottery.__init__( self, lotid )

    #处理拆分后的票信息 插入票信息和修改方案状态必须放在同一个事物里面
    def dealSplitTicketInfo( self, data, checksplit=False):
        #票数据参数
        inargs = {'wtype'        :   data['f_wtype'],
		          'fileorcode'   :   data['f_fileorcode'],
			      'allmoney'     :   data['f_allmoney'],
				  'beishu'       :   data['f_beishu'],
			      'zhushu'       :   data['f_zhushu'],
				  'code'         :   data['f_fileorcode'],
				  'expect'       :   data['f_expect'],
				  'selecttype'   :   ''}

        #组装-自选OR机选
        data['f_fileorcode'] = self.organizeFileorcode( data['f_fileorcode'], data['f_selecttype'] )

        #调用拆票
        tickets = list()
        if int( data['f_wtype'] ) in Config.HTWTYPE:
            filedict = dict()
            for fcode in data['f_fileorcode'].split('$'):
                fc, wc = fcode.split('#')
                wtype, st = wc.split('@')

                if wtype not in filedict.keys():
                    filedict[wtype] = list()
                    filedict[wtype].append(fc + '@' + st)
                else:
                    filedict[wtype].append(fc + '@' + st)

            for info in filedict:
                data['f_wtype']      = info
                data['f_fileorcode'] = '$'.join( filedict[info] )
                try:
                    tickets += self.splitFileOrCode( data, inargs )
                except:
                    logger.error( traceback.format_exc() )
                    return list()
        else:
            try:
                tickets = self.splitFileOrCode( data, inargs )
            except:
                logger.error( traceback.format_exc() )
                return list()

        allmoney = 0
        for info in tickets:
            singlemoney = 2
            if str( info['wtype'] ) in Config.ZJWTYPE:
                singlemoney = 3

            logger.info("单注金额:%s", singlemoney)
            allmoney += int( info['beishu'] ) * int( info['zhushu'] ) * singlemoney

        logger.info("拆票总金额:%s", allmoney)
        if allmoney != float( data['f_allmoney'] ):
            logger.error("拆分后实际票金额总和与投注金额不符! %s != %s", allmoney, data['f_allmoney'])
            if checksplit:
                raise Exception("投注金额(%s)与拆票金额(%s)不符!".format(data['f_allmoney'], allmoney))
            else:
                return list()
        return tickets

    #实际拆票处
    def splitFileOrCode( self, data, args ):

        ret_list = list()
        args_split = {'wtype'      : data['f_wtype'],
                      'beishu'     : data['f_beishu'],
                      'fileorcode' : data['f_fileorcode']
                     }

        split_obj = Operator.get( data['f_lotid'] )

        ret = split_obj.splitCodes( args_split )

        singlemoney = 2
        if str( data['f_wtype'] ) in Config.ZJWTYPE:
            singlemoney = 3

        for info in ret:
            if type(info) == list:
               info = info[0]
            tmp_dict = copy.deepcopy( args )
            tmp_dict['wtype']      = data['f_wtype']
            tmp_dict['code']       = info['code']
            tmp_dict['beishu']     = info['beishu']
            tmp_dict['zhushu']     = info['zhushu']
            tmp_dict['allmoney']   = int( info['beishu'] ) * int( info['zhushu'] ) * singlemoney

            #解析
            fileorcode, retflag    = self.parseFileorcode( info['code'] )
            tmp_dict['fileorcode'] = fileorcode
            tmp_dict['selecttype'] = retflag
            ret_list.append(tmp_dict)

        logger.debug(ret_list)
        return ret_list

    #为自选or机选号码拆分做准备
    def organizeFileorcode( self, fileorcode, selecttype ):
        filelist   = fileorcode.split('$')
        selectlist = selecttype.split(',')
        retstr     = ''

        for info in range( len(filelist) ):
            redb, blueb = filelist[info].split('|')
            tmpstr = ''

            for i in blueb.split(','):
                if '' == tmpstr:
                    tmpstr = i + '@' + selectlist[info]
                else:
                    tmpstr += ',' + i + '@' + selectlist[info]

            if '' == retstr:
                retstr = redb + '|' + tmpstr

            else:
                retstr += '$' + redb + '|' + tmpstr

        return retstr

    #解析标志位
    def parseFileorcode( self, fileorcode ):
        filelist = fileorcode.split('$')
        retstr   = ''
        retflag  = ''

        for info in filelist:
            redb, blueb = info.split('|')
            if '' == retflag:
                retflag = (blueb.split(',')[0]).split('@')[-1]

            else:
                retflag += ',' + (blueb.split(',')[0]).split('@')[-1]

            tmp = ''
            for i in blueb.split(','):
                if '' == tmp:
                    tmp = i.split('@')[0]
                else:
                    tmp += ',' + i.split('@')[0]

            # 修复胆拖格式bug
            if tmp.count('[') > tmp.count(']'):
                tmp += ']'

            if '' == retstr:
                retstr = redb + '|' + tmp
            else:
                retstr += '$' + redb + '|' + tmp

        return retstr, retflag
