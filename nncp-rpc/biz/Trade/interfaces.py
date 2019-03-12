#encoding=utf-8
import decimal
import traceback
import ujson

import datetime
from Trade.order import OrderBiz
from Trade.project import ProjectBiz
from util.tools import Log
from common.json_format import rpc_dumps
logger = Log().getLog()

"""收集业务类方法作为RPC总入口
"""


class Interfaces(object):

    def place_order(self, params):
        try:
            return OrderBiz().place_order(params)
        except:
            logger.error(traceback.format_exc())
            raise

    def place_chasenumber(self, params):
        try:
            return OrderBiz().place_chasenumber(params)
        except:
            logger.error(traceback.format_exc())
            raise

    def cancel_chasenumber(self, params):
        try:
            return OrderBiz().cancel_chasenumber(params)
        except:
            logger.error(traceback.format_exc())
            raise

    def proj_list(self, params):
        plist = ProjectBiz().proj_list(params)
        return rpc_dumps(plist)

    def chasenumber_list(self, params):
        clist = ProjectBiz().chasenumber_list(params)
        return rpc_dumps(clist)

    def proj_detail(self, params):
        """
        方案详情
        :param params: pid
        :return:
        """
        detail = ProjectBiz().proj_detail(params)
        return rpc_dumps(detail)

    def chasenumber_detail(self, params):
        """
        追号详情
        :param params: pid
        :return:
        """

        detail = ProjectBiz().chasenumber_detail(params)
        return rpc_dumps(detail)

    def proj_tickets(self, params):
        """
        方案票号信息
        :param params: pid
        :return:
        """

        tickets = ProjectBiz().proj_tickets(params)
        return rpc_dumps(tickets)


    def launch_list(self, params):
        plist = ProjectBiz().launch_list(params)
        return rpc_dumps(plist)

    def follow_detail(self, params):
        """
        方案详情
        :param params: pid
        :return:
        """
        detail = ProjectBiz().follow_detail(params)
        return rpc_dumps(detail)

    def follow_list(self, params):
        plist = ProjectBiz().follow_list(params)
        return rpc_dumps(plist)

    def launch_recommend_list(self, params):
        plist = ProjectBiz().lanuch_recommend_list(params)
        return rpc_dumps(plist)

    def hot_seller(self, params):
        sellers = ProjectBiz().follow_hot_seller()
        return rpc_dumps(sellers)

    def seller_info(self, params):
        info = ProjectBiz().get_seller_info(params)
        return rpc_dumps(info)

    def history_gains(self, params):
        ret = ProjectBiz().get_history_gains(params)
        return rpc_dumps(ret)

    def follow_top_five(self, params):
        ret = ProjectBiz().get_follow_top_five(params)
        return rpc_dumps(ret)

