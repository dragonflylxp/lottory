# encoding=utf-8

import inspect
import MySQLdb
import traceback

import ujson
from dbpool import db_pool
from util.tools import Log
from logic import Trade, Ticket
from logic.Trade.project import Proj

logger = Log().getLog()


class ProjectBiz(object):
    def proj_list(self, params):
        lotid = params.get("lotid", "0")
        uid = params.get("uid")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")

        all_info = Proj().get_all_proj_list(uid, biztype, pageno, pagesize)
        orders = all_info.get("orders", [])
        count = all_info.get("count", 0)
        lotte_orders = {}
        for order in orders:
            lotid = order.get("f_lotid")
            pid = order.get("f_pid")
            if lotte_orders.has_key(lotid):
                lotte_orders[lotid].append(pid)
            else:
                lotte_orders.update({
                    lotid: [pid, ]
                })
        ret = []
        for lotid, pids in lotte_orders.items():
            obj_order = Trade.get(int(lotid))
            tmp_order = obj_order.get_project_list_by_pids(pids)
            ret.extend(list(tmp_order))

        ret.sort(key=lambda x: x.get("f_crtime"), reverse=True)
        return {"orders": ret, "count": count}

    def chasenumber_list(self, params):
        uid = params.get("uid")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")

        all_info = Proj().get_chasenumber_list(uid, pageno, pagesize)
        orders = all_info.get("orders", [])
        count = all_info.get("count", 0)
        return {"chasenumbers": orders, "count": count}

    def chasenumber_detail(self, params):
        """
        追号详情
        :param params: cid
        :return:
        """
        lotid = params.get("lotid")
        cid = params.get("cid")
        obj_order = Trade.get(int(lotid))
        return obj_order.get_chasenumber_by_cid(cid)

    def proj_detail(self, params):
        """
        方案详情
        :param params: pid
        :return:
        """
        lotid = params.get("lotid")
        pid = params.get("pid")
        obj_order = Trade.get(int(lotid))
        return obj_order.get_project_by_pid(pid)

    def proj_tickets(self, params):
        """
        方案票号信息
        :param params: pid
        :return:
        """
        lotid = params.get("lotid")
        pid = params.get("pid")
        obj_ticket = Ticket.get(int(lotid))
        return obj_ticket.get_project_tickets(pid)

    def launch_list(self, params):
        lotid = params.get("lotid", "0")
        uid = params.get("uid")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")

        all_info = Proj().get_lanuch_proj_list(uid, pageno, pagesize)
        orders = all_info.get("orders", [])
        count = all_info.get("count", 0)
        stats = all_info.get("stat", [])
        lotte_orders = {}

        stat_dict = {}
        for stat in stats:
            stat_dict.update({
                stat.get("f_pid"): stat
            })
        orderbypid = {}
        for order in orders:
            lotid = order.get("f_lotid")
            pid = order.get("f_oid")
            orderbypid.update({pid: order})
            if lotte_orders.has_key(lotid):
                lotte_orders[lotid].append(pid)
            else:
                lotte_orders.update({
                    lotid: [pid, ]
                })
        ret = []
        for lotid, pids in lotte_orders.items():
            obj_order = Trade.get(int(lotid))
            tmp_order = obj_order.get_project_list_by_pids(pids)
            ret.extend(list(tmp_order))

        for proj in ret:
            pid = proj.get("f_pid")
            statinfo = stat_dict.get(pid, {})
            _tmp_order = orderbypid.get(pid, {})
            proj.update(_tmp_order)
            proj.update({
                "join_num": statinfo.get("f_follownum", "")
            })

        ret.sort(key=lambda x: x.get("f_crtime"), reverse=True)
        return {"orders": ret, "count": count}

    def follow_detail(self, params):
        """
        方案详情
        :param params: pid
        :return:
        """
        lotid = params.get("lotid")
        pid = params.get("pid")
        obj_order = Trade.get(int(lotid))
        return obj_order.get_follow_project_by_pid(pid)

    def follow_list(self, params):
        lotid = params.get("lotid", "0")
        uid = params.get("uid")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")

        all_info = Proj().get_follow_proj_list(uid, pageno, pagesize)
        orders = all_info.get("orders", [])
        count = all_info.get("count", 0)
        lotte_orders = {}
        for order in orders:
            lotid = order.get("f_lotid")
            pid = order.get("f_pid")
            if lotte_orders.has_key(lotid):
                lotte_orders[lotid].append(pid)
            else:
                lotte_orders.update({
                    lotid: [pid, ]
                })
        ret = []
        fids = []
        for lotid, pids in lotte_orders.items():
            obj_order = Trade.get(int(lotid))
            tmp_order = obj_order.get_project_list_by_pids(pids)
            # fids.extend([order.get("f_fid") if order.get("f_fid") else order.get("f_pid") for order in tmp_order])
            ret.extend(list(tmp_order))

        ret.sort(key=lambda x: x.get("f_crtime"), reverse=True)
        return {"orders": ret, "count": count}

    def lanuch_recommend_list(self, params):
        lotid = params.get("lotid", "0")
        uids = params.get("uids")
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")

        all_info = Proj().get_lanuch_recommend_list(pageno, pagesize)
        orders = all_info.get("orders", [])
        count = all_info.get("count", 0)
        sellerinfo = all_info.get("sellerinfo", [])

        seller_by_uid = {}
        for seller in sellerinfo:
            seller_by_uid.update({
                seller.get("f_uid"): seller
            })

        ret = []
        for order in orders:
            uid = order.get("f_uid")
            seller = seller_by_uid.get(uid)
            order.update({
                "f_followpnum": seller.get("f_followpnum", ""),
                "f_continuswin": seller.get("f_continuswin", ""),
                "photo": seller.get("f_headimg", ""),
                "username": seller.get("f_username", ""),
                "launch_uid": seller.get("f_uid")
            })
            ret.append(order)

        ret.sort(key=lambda x: x.get("f_crtime"), reverse=True)
        return {"orders": ret, "count": count}


    def follow_hot_seller(self):
        """
        热门跟单
        :return:
        """
        all_info = Proj().get_follow_hot_seller()
        return all_info

    def get_seller_info(self, params):
        uid = params.get("uid")
        return Proj().get_seller_info_by_uid(uid)

    def get_history_gains(self, params):
        uid = params.get("uid")
        return Proj().get_history_gains(uid)

    def get_follow_top_five(self, params):
        fid = params.get("fid")
        lotid = params.get("lotid")

        obj_order = Trade.get(int(lotid))
        return obj_order.get_follow_top_five(fid)

