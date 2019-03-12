#encoding=utf-8

import os
import sys
import copy
import logging
import traceback

import Config
import Operator
import LotCommon
from util.tools import Log

logger = Log().getLog()

class LotJk( LotCommon.Lottery ):
    ''' 11选5'''
    def __init__( self, lotid ):
        ''' 初始化 '''
        LotCommon.Lottery.__init__( self, lotid )

    #处理拆分后的票信息 插入票信息和修改方案状态必须放在同一个事务里面
    def dealSplitTicketInfo( self, data, checksplit=False ):

        #票数据参数
        inargs = {'wtype'        :   data['f_wtype'],
		          'fileorcode'   :   data['f_fileorcode'],
				  'allmoney'     :   data['f_allmoney'],
				  'beishu'       :   data['f_beishu'],
				  'zhushu'       :   data['f_zhushu'],
				  'expect'       :   data['f_expect'],
				  'selecttype'   :   ''}

        #调用拆票
        tickets = list()
        allmoney = 0
        try:
            tickets, allmoney = self.splitFileOrCode( data, inargs )
            if allmoney != float( data['f_allmoney'] ):
                logger.error("拆分后实际票金额总和与实际金额不符!")
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
        args_split = {'wtype'      :   data['f_wtype'],
                    'fileorcode'   :   data['f_fileorcode'],
                    'allmoney'     :   data['f_allmoney'],
                    'beishu'       :   data['f_beishu'],
                    'zhushu'       :   data['f_zhushu'],
                    'expect'       :   data['f_expect'],
                      }

        split_obj = Operator.get( data['f_lotid'] )
        logger.info(args_split)
        ret       = split_obj.splitCodes( args_split )

        allmoney    = 0
        singlemoney = Config.SINGLEMONEY
        for info in ret:
            tmp_dict = copy.deepcopy( args )
            tmp_dict['wtype']      = info['wtype']
            tmp_dict['beishu']     = info['beishu']
            tmp_dict['zhushu']     = info['zhushu']
            tmp_dict['fileorcode'] = info['code']
            tmp_dict['selecttype'] = info['selecttype']
            tmp_dict['allmoney']   = int( info['beishu'] ) * int( info['zhushu'] ) * singlemoney

            ret_list.append(tmp_dict)
            allmoney += tmp_dict['allmoney']

        logger.info(allmoney)
        logger.info(data['f_allmoney'])
        return ret_list, allmoney
