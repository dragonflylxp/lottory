#encoding=utf-8

import traceback
import ujson
import define
from cbrpc import RpcException
from logic.msgrecord import MsgRecord
from logic import Trade
from dbpool import db_pool
from util.tools import Log

logger = Log().getLog()

class OrderBiz(object):
    def place_order(self, params):
        #TODO 下单参数校验
        lotid = params.get("lotid")
        obj_order = Trade.get(int(lotid))
        resp = obj_order.place_order(params) if obj_order else {}

        #异步通知支付
        if resp.get("pid", ""):
            params = {
                "lotid": resp.get("lotid"),
                "oid": resp.get("pid"),
                "msgtype": define.MSG_TYPE_ORDER_PLACED,
                "msgcnt": ujson.dumps(resp)
            }
            try:
                mid = MsgRecord().insert(params)
                resp.update({"mid": mid})
            except:
                # 防止重复插入
                logger.error(traceback.format_exc())
                raise
            else:
                rds = db_pool.get_redis("msgbus")
                rds.publish("TRADE#ORDER#PLACED", ujson.dumps(resp))
        else:
            raise RpcException("交易服务下单异常!lotid={}".format(lotid))
        return {"pid":resp.get("pid", "")}


    def place_chasenumber(self, params):
        #TODO 下单参数校验
        lotid = params.get("lotid")
        obj_order = Trade.get(int(lotid))
        resp = obj_order.place_chasenumber(params) if obj_order else {}

        #异步通知支付
        if resp.get("cid"):
            params = {
                "lotid": resp.get("lotid"),
                "oid": resp.get("cid"),
                "msgtype": define.MSG_TYPE_CHASENUMBER_PLACED,
                "msgcnt": ujson.dumps(resp)
            }
            try:
                mid = MsgRecord().insert(params)
                resp.update({"mid": mid})
            except:
                # 防止重复插入
                logger.error(traceback.format_exc())
                raise
            else:
                rds = db_pool.get_redis("msgbus")
                rds.publish("TRADE#CHASENUMBER#PLACED", ujson.dumps(resp))
        else:
            raise RpcException("交易服务发起追号异常!lotid={}".format(lotid))
        return {"cid":resp.get("cid", ""), "pid": resp.get("pid", "")}

    def cancel_chasenumber(self, params):
        obj_order = Trade.get(0)
        resp = obj_order.cancel_chasenumber(params) if obj_order else {}
        return resp
