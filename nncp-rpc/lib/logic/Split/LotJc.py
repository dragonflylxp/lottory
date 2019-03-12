#encoding=utf-8

import os
import sys
import copy
import traceback

import Config
import LotCommon
import Operator
from util.tools import Log

logger = Log().getLog()

class LotJc( LotCommon.Lottery ):
    ''' 竞彩类 '''
    def __init__( self, lotid ):
        ''' 初始化 '''
        LotCommon.Lottery.__init__( self, lotid )

    #处理拆分后的票信息 插入票信息和修改方案状态必须放在同一个事物里面
    def dealSplitTicketInfo( self, data, checksplit=False ):

        #票数据参数
        inargs = { 'wtype':        data['f_wtype'],
            'fileorcode':   data['f_fileorcode'],
            'allmoney':     data['f_allmoney'],
            'beishu':       data['f_beishu'],
            'ggtype':       data['f_ggtype'],
            'lotid':       data['f_lotid'],
        }
        #调用拆票
        tickets = list()
        allmoney = 0
        try:
            tickets = self.splitFileOrCode( data, inargs )
            allmoney = sum([ticket["allmoney"] for ticket in tickets])
            logger.info("拆票总金额:%s", allmoney)
            if allmoney != float( data['f_allmoney'] ):
                logger.error("拆分后实际票金额总和与投注金额不符! %s != %s", allmoney, data['f_allmoney'])
                raise Exception("投注金额(%s)与拆票金额(%s)不符!".format(data['f_allmoney'], allmoney))
        except:
            logger.error( traceback.format_exc() )
            if checksplit:
                raise Exception("投注金额(%s)与拆票金额(%s)不符!".format(data['f_allmoney'], allmoney))
            else:
                return list()
        return tickets

    #实际拆票处
    def splitFileOrCode( self, data, args ):

        ret_list = list()
        logger.info(data)
        args_split = {
            'ggtype':       data['f_ggtype'],
            'wtype':        data['f_wtype'],
            'beishu':       data['f_beishu'],
            'fileorcode':   data['f_fileorcode'],
            'isquchu':      data['f_isquchu'],
            'danma':        data['f_danma'],
            'lotid':       data['f_lotid'],
        }

        split_obj = Operator.get( data['f_lotid'] )

        logger.info(args_split)
        ret = split_obj.splitCodes( args_split )
        for info in ret:
            tmp_dict = copy.deepcopy( args )
            tmp_dict['wtype']      = info['wtype']
            tmp_dict['ggtype']     = info['ggtype']
            tmp_dict['fileorcode'] = info['fileorcode']
            tmp_dict['code']       = info['fileorcode']
            tmp_dict['cptype']     = info['wtype']
            tmp_dict['beishu']     = info['beishu']
            tmp_dict['zhushu']     = info['zhushu']
            tmp_dict['allmoney']   = int( info['beishu'] ) * int( info['zhushu'] ) * 2
            tmp_dict['firstprocessid']  = (info['fileorcode'].split('/')[0]).split('|')[0]   # 投注内容的第一场，不是比赛的第一场，有疑问
            tmp_dict['lastprocessid']   = (info['fileorcode'].split('/')[-1]).split('|')[0]
            ret_list.append(tmp_dict)

        return ret_list
