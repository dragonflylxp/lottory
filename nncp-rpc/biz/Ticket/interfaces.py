#encoding=utf-8
import traceback
import ujson
from Ticket.jprize import JprizeBiz
from logic import Split
from util.tools import Log

logger = Log().getLog()

"""收集业务类方法作为RPC总入口
"""
class Interfaces(object):

    def Jprize(self, params):
        try:
            obj = JprizeBiz()
            obj.do_jprize(params)
        except:
            logger.error(traceback.format_exc())
            raise


    def split_tickets(self, params):
        try:
            obj_split = Split.get(int(params.get("lotid")))
            order = {
                    "f_lotid": params.get("lotid"),
                    "f_wtype": params.get("wtype"),
                    "f_fileorcode": params.get("fileorcode"),
                    "f_allmoney": params.get("singlemoney") if params.get("singlemoney") else params.get("allmoney"),
                    "f_beishu": params.get("beishu"),
                    "f_zhushu": params.get("zhushu"),
                    "f_isquchu": params.get("isquchu", ""),
                    "f_danma": params.get("danma", ""),
                    "f_expect": params.get("expect", ""),
                    "f_selecttype": params.get("selecttype", ""),
                    "f_ggtype": params.get("ggtype", "")
            }
            tickets = obj_split.dealSplitTicketInfo(order, checksplit=params.get("checksplit", False))
        except:
            logger.error(traceback.format_exc())
            raise
        return tickets










