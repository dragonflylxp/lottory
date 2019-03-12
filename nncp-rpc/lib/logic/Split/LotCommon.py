#encoding=utf-8
import os
import sys
import copy
import time
import logging
import datetime
import traceback

import Info
import Config
import Operator
from util.tools import Log

logger = Log().getLog()


class Lottery:
    ''' 公用类 '''
    def __init__( self, lotId ):
        self.lotId = lotId
        self.info  = Info.get(lotId)
        for (i, j) in self.info.items():
            setattr(self, i, j)

    #处理拆分后的票信息 插入票信息和修改方案状态必须放在同一个事物里面
    def dealSplitTicketInfo( self, data, checksplit=False ):

        #票数据参数
        inargs = {'wtype'        :   data['f_wtype'],
		          'fileorcode'   :   data['f_fileorcode'],
				  'allmoney'     :   data['f_allmoney'],
				  'beishu'       :   data['f_beishu'],
				  'zhushu'       :   data['f_zhushu'],
				  'expect'       :   data['f_expect']}

        #调用拆票
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
        args_split = {'wtype'      : data['f_wtype'],
                      'beishu'     : data['f_beishu'],
                      'fileorcode' : data['f_fileorcode']
                     }

        split_obj = Operator.get( data['f_lotid'] )
        ret = split_obj.splitCodes( args_split )

        allmoney    = 0
        singlemoney = Config.SINGLEMONEY
        for info in ret:

            tmp_dict = copy.deepcopy( args )
            tmp_dict['wtype']      = info['wtype']
            tmp_dict['beishu']     = info['beishu']
            tmp_dict['zhushu']     = info['zhushu']
            tmp_dict['fileorcode'] = info['code']
            tmp_dict['allmoney']   = int( info['beishu'] ) * int( info['zhushu'] ) * singlemoney

            ret_list.append(tmp_dict)
            allmoney += tmp_dict['allmoney']

        return ret_list, allmoney
