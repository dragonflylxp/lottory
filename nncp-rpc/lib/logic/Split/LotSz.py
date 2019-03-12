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

class LotSz( LotCommon.Lottery ):
    ''' 排列三，排列五和七星彩'''
    def __init__( self, lotid ):
        ''' 初始化 '''
        LotCommon.Lottery.__init__( self, lotid )

    #处理拆分后的票信息 插入票信息和修改方案状态必须放在同一个事务里面
    def dealSplitTicketInfo( self, data ):

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
        except:
            logger.error( traceback.format_exc() )
            return list() 
            
        if allmoney != float( data['f_allmoney'] ):
            logger.error("拆分后实际票金额总和与实际金额不符!")
            return list()
        return tickets

    #实际拆票处
    def splitFileOrCode( self, data, args ):

        ret_list = list()
        args_split = {'wtype'      : data['f_wtype'],
                      'beishu'     : data['f_beishu'],
                      'fileorcode' : data['f_fileorcode'],
                      'selecttype' : data['f_selecttype']
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
            tmp_dict['printdetail'] = info.get('printdetail', 0)

            ret_list.append(tmp_dict)
            allmoney += tmp_dict['allmoney']

        logger.info(allmoney)
        logger.info(data['f_allmoney'])
        return ret_list, allmoney
