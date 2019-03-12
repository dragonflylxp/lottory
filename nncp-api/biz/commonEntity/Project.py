# coding: utf-8
from decimal import Decimal

import ews
import time
from cbrpc import CBClient
from util.configer import *
import traceback
from cbrpc import get_rpc_conn
import re
import define
import hashlib
import session
import ujson
from util.tools import Log

from commonEntity import ExpectInfo
from commonEntity import DrawInfo
from commonEntity import JcInfo
from commonEntity.JcTool import JcBase
import rediskey
from dbpool import db_pool

global logger
logger = Log().getLog()


class ProjBean():
    def __init__(self, lotid=0):
        if lotid != 0:
            self.expect_obj = ExpectInfo.get(lotid)
            self.draw_obj = DrawInfo.get(lotid)
            self.jc_obj = JcInfo.get(lotid)

    def get_chasenumber_list(self, params):
        module = "trade"
        method = "chasenumber_list"
        chasenumber_list = {}
        with get_rpc_conn(module) as proxy:
            try:
                chasenumber_list = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_CHASENUMBER_LIST_FAIL)
        chasenumber_list = ujson.loads(chasenumber_list)
        chasenumbers = chasenumber_list.get("chasenumbers", [])
        count = chasenumber_list.get("count", 0)
        orders = []
        for chasenumber in chasenumbers:
            orders.append({
                "uid": chasenumber.get("f_uid"),
                "cid": chasenumber.get("f_cid"),
                "lotid": chasenumber.get("f_lotid"),
                "chasestatus": chasenumber.get("f_chasestatus"),
                "stopprize": chasenumber.get("f_stopprize"),
                "totalallmoney": chasenumber.get("f_totalallmoney"),
                "totalgetmoney": chasenumber.get("f_totalgetmoney"),
                "expecttotal": chasenumber.get("f_expecttotal"),
                "expectnum": chasenumber.get("f_expectnum"),
                "crtime": chasenumber.get("f_crtime"),
            })
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        ret = {
            "list": orders,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno
        }
        return ret

    def get_proj_list(self, params):
        module = "trade"
        method = "proj_list"
        proj_list = {}
        with get_rpc_conn(module) as proxy:
            try:
                proj_list = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_PROJ_LIST_FAIL)

        proj_list = ujson.loads(proj_list)
        projs = proj_list.get("orders", [])
        count = proj_list.get("count", 0)
        orders = []
        for proj in projs:

            orderstatus = proj.get("f_orderstatus", "")
            isjprize = proj.get("f_isjprize", "")
            if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
                proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
            else:
                proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

            orders.append({
                "pid": proj.get("f_pid", ""),
                "allmoney": proj.get("f_allmoney", ""),
                "beishu": proj.get("f_beishu", ""),
                "couponmoney": proj.get("f_couponmoney", ""),
                "expect": proj.get("f_expect", ""),
                "ticketnum": proj.get("f_ticketnum", "0"),
                "paymoney": proj.get("f_paymoney", ""),
                "selecttype": proj.get("f_selecttype", ""),
                "lotid": proj.get("f_lotid", ""),
                "crtime": proj.get("f_crtime", ""),
                "zhushu": proj.get("f_zhushu", ""),
                "wtype": proj.get("f_wtype", ""),
                "isjprize": proj.get("f_isjprize", ""),
                "getmoney": proj.get("f_getmoney", ""),
                "cancelmoney": proj.get("f_cancelmoney", ""),
                "orderstatus": proj.get("f_orderstatus", ""),
                "proj_desc": proj_desc
            })
        ret = {}
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")
        ret.update({
            "list": orders,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno,
            "biztype": biztype
        })

        return ret

    def get_proj_router(self, params):
        lotid = params.get("lotid")
        if str(lotid) in ["28", "44", "3"]:
            return self.get_number_lotte_proj_detail(params)
        elif str(lotid) in ["46", "47"]:
            return self.get_jc_lotte_proj_detail(params)

    def get_chasenumber_router(self, params):
        lotid = params.get("lotid")
        if str(lotid) in ["28", "44", "3"]:
            return self.get_number_lotte_chasenumber_detail(params)
        else:
            return {}

    def get_number_lotte_chasenumber_detail(self, params):
        """
        获取数字彩追号详情
        :param params:
        :return:
        """
        module = "trade"
        method = "chasenumber_detail"
        chasenumber_detail = {}
        with get_rpc_conn(module) as proxy:
            chasenumber_detail = proxy.call(method, params)
            chasenumber_detail = ujson.loads(chasenumber_detail)

        if not chasenumber_detail:
            raise ews.EwsError(ews.STATUS_CHASENUMBER_NOTFOUND)

        ret = {}
        try:
            lst = []
            for proj in chasenumber_detail.get("projects"):
                orderstatus = proj.get("f_orderstatus")
                isjprize = proj.get("f_isjprize")
                proj_desc = ""
                if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
                    proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
                else:
                    proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")
                lst.append({
                    "lotid": params.get("lotid"),
                    "crtime": proj.get("f_crtime"),
                    "pid": proj.get("f_pid"),
                    "wtype": proj.get("f_wtype"),
                    "expect": proj.get("f_expect"),
                    "allmoney": proj.get("f_allmoney"),
                    "getmoney": proj.get("f_getmoney"),
                    "cancelmoney": proj.get("f_cancelmoney"),
                    "orderstatus": orderstatus,
                    "isjprize": isjprize,
                    "proj_desc": proj_desc
                })

            ret.update({
                "uid": params.get("uid"),
                "cid": params.get("cid"),
                "lotid": params.get("lotid"),
                "chasestatus": chasenumber_detail.get("f_chasestatus"),
                "stopprize": chasenumber_detail.get("f_stopprize"),
                "totalallmoney": chasenumber_detail.get("f_totalallmoney"),
                "totalgetmoney": chasenumber_detail.get("f_totalgetmoney"),
                "expecttotal": chasenumber_detail.get("f_expecttotal"),
                "expectnum": chasenumber_detail.get("f_expectnum"),
                "crtime": chasenumber_detail.get("f_crtime"),
                "projects": lst
            })
        except:
            logger.error(traceback.format_exc())
        finally:
            return ret

    def get_number_lotte_proj_detail(self, params):
        """
        获取数字彩方案详情
        :param params:
        :return:
        """
        module = "trade"
        method = "proj_detail"
        proj_detail = {}
        with get_rpc_conn(module) as proxy:
            proj_detail = proxy.call(method, params)
            proj_detail = ujson.loads(proj_detail)
        #
        # method = "proj_tickets"
        # proj_tickets = []
        # with get_rpc_conn(module) as proxy:
        #     proj_tickets = proxy.call(method, params)
        #     proj_tickets = ujson.loads(proj_tickets)

        ret = {}

        if not proj_detail:
            raise ews.EwsError(ews.STATUS_PROJ_NOTFOUND)

        lotid = params.get("lotid")
        expect = proj_detail.get("f_expect", "")
        opencode = ""
        if str(lotid) == "28":
            opencode_info = self.draw_obj.get_opencode_by_expect(expect)
            opencode = opencode_info.get("openCode", "")
        elif str(lotid) == "44":
            opencode_info = self.draw_obj.get_opencode_by_expect(expect) or {}
            opencode = opencode_info.get("openCode", "")

        orderstatus = proj_detail.get("f_orderstatus", "")
        isjprize = proj_detail.get("f_isjprize", "")
        proj_desc = ""
        if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
            proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
        else:
            proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

        fileorcode = proj_detail.get("f_fileorcode", "")
        try:
            ret.update({
                "pid": proj_detail.get("f_pid", ""),
                "allmoney": proj_detail.get("f_allmoney", ""),
                "beishu": proj_detail.get("f_beishu", ""),
                "couponmoney": proj_detail.get("f_couponmoney", ""),
                "expect": expect,
                "ticketnum": proj_detail.get("f_ticketnum", "0"),
                "paymoney": proj_detail.get("f_paymoney", ""),
                "selecttype": proj_detail.get("f_selecttype", ""),
                "lotid": proj_detail.get("lotid", ""),
                "crtime": proj_detail.get("f_crtime", ""),
                "zhushu": proj_detail.get("f_zhushu", ""),
                "wtype": proj_detail.get("f_wtype", ""),
                "isjprize": isjprize,
                "getmoney": proj_detail.get("f_getmoney", ""),
                "cancelmoney": proj_detail.get("f_cancelmoney", ""),
                "orderstatus": orderstatus,
                "fileorcode": fileorcode,
                "opencode": opencode,
                "proj_desc": proj_desc
            })
        except:
            logger.error(traceback.format_exc())
            raise  # todo
        return ret

    def get_jc_lotte_proj_detail(self, params):
        """
        获取数字彩方案详情
        :param params:
        :return:
        """
        module = "trade"
        method = "proj_detail"
        proj_detail = []
        with get_rpc_conn(module) as proxy:
            proj_detail = proxy.call(method, params)
            proj_detail = ujson.loads(proj_detail)

        # method = "proj_tickets"
        # proj_tickets = []
        # with get_rpc_conn(module) as proxy:
        #     proj_tickets = proxy.call(method, params)
        #     proj_tickets = ujson.loads(proj_tickets)

        ret = {}

        if not proj_detail:
            raise ews.EwsError(ews.STATUS_PROJ_NOTFOUND)

        lotid = params.get("lotid")
        expect = proj_detail.get("f_expect", "")
        opencode = ""

        orderstatus = proj_detail.get("f_orderstatus", "")
        isjprize = proj_detail.get("f_isjprize", "")
        proj_desc = ""
        if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
            proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
        else:
            proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

        fileorcode = proj_detail.get("f_fileorcode", "")
        playid = proj_detail.get("f_wtype", "")
        beishu = proj_detail.get("f_beishu", "")
        danma = proj_detail.get("f_danma", "")
        ptype = proj_detail.get("f_ptype")
        lasttime = proj_detail.get("f_lasttime", "")
        if str(ptype) != "-1" or lasttime < time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()):
            matchids, tz_opt = self.deal_fileorcode(fileorcode, playid, beishu=beishu)
            danma_list = self.deal_danma(danma)
            matches_info = self.jc_obj.get_matches_by_matchids(matchids)
        else:
            matches_info = []

        bet_match = []
        for matches in matches_info:
            matchcode = matches.get("matchCode", "")
            matchid = matches.get("matchId", "")

            result = self.get_jc_result(matches, lotid)
            opt = tz_opt.get(matchid, [])
            for op in opt:
                codes = op.get("codes", [])
                playresult = result.get(str(op.get("playid")), "")
                for code in codes:
                    code.update({
                        "ismark": "1" if opt == playresult else "0"
                    })
                op.update({
                    "result": playresult
                })
            opts = tz_opt.get(matchid, {})
            bet_match.append({
                "matchid": matchid,
                "league_name": matches.get("league", ""),
                "home": matches.get("home", ""),
                "away": matches.get("visiting", ""),
                "matchnum": matches.get("matchNum", ""),
                "endtime": matches.get("endTime", ""),
                "matchtime": matches.get("matchDate", "") + " " + matches.get("matchTime", ""),
                "rangfen": matches.get("rangfen", ""),
                "presetscore": matches.get("presetScore", ""),
                "status": matches.get("status", ""),
                "matchstate": matches.get("matchState", ""),
                "rangqiu": matches.get("rangQiu", ""),
                "matchcode": matchcode,
                "options": opts,
                "score": matches.get("score", ""),
                "halfScore": matches.get("halfScore", "")
            })

        try:
            ret.update({
                "pid": proj_detail.get("f_pid", ""),
                "allmoney": proj_detail.get("f_allmoney", ""),
                "beishu": beishu,
                "couponmoney": proj_detail.get("f_couponmoney", ""),
                "expect": expect,
                "ticketnum": proj_detail.get("f_ticketnum", "0"),
                "paymoney": proj_detail.get("f_paymoney", ""),
                "selecttype": proj_detail.get("f_selecttype", ""),
                "lotid": proj_detail.get("f_lotid", ""),
                "crtime": proj_detail.get("f_crtime", ""),
                "zhushu": proj_detail.get("f_zhushu", ""),
                "wtype": playid,
                "isjprize": isjprize,
                "getmoney": proj_detail.get("f_getmoney", ""),
                "cancelmoney": proj_detail.get("f_cancelmoney", ""),
                "orderstatus": orderstatus,
                "fileorcode": fileorcode,
                "opencode": opencode,
                "proj_desc": proj_desc,
                "danma": danma,
                "ratelist": proj_detail.get("f_ratelist", ""),
                "ggtype": proj_detail.get("f_ggtype", ""),
                "isquchu": proj_detail.get("f_isquchu", ""),
                "rqlist": proj_detail.get("f_rqlist", ""),
                "matches": bet_match
            })
        except:
            logger.error(traceback.format_exc())
            raise  # todo
        return ret

    def deal_danma(self, danmas):
        """解析胆码
        """
        danma_processname = []
        if not danmas:
            return danma_processname

        danam_list = danmas.split("/")
        p = re.compile('(\d+)(\[.+\])')
        for danma in danam_list:
            danmas = danma.split("|")
            if len(danmas) == 3:
                matchesid, processname, opts = danmas
                danma_processname.append(processname)
            else:
                matchesid, opts = danmas
                m = p.match(opts)
                if m:
                    processname, opt = m.groups()
                    danma_processname.append(processname)

        return danma_processname

    def deal_fileorcode(self, fileorcode, playid, rate={}, beishu="", is_chupiao_rate=False):
        """解析fileorcode
        """
        matchesids = []
        tz_opt = {}
        p = re.compile('(\d+)\[(.+)\]')
        # u'109685|6011[1:0]' xid|processname|[code]
        # "109685|6011|270[2@1]/109685|6011|271[3:0@1,负其它@1,3:3@1]  混合情况

        beishu = int(beishu) if beishu else 1
        codelist = fileorcode.split("/")
        for code in codelist:
            opt = ""
            rate_opt = code.split("|")
            if len(rate_opt) == 3:
                xid, processname, tz = rate_opt
                m = p.match(tz)
                if m:
                    playid, opt = m.groups()
            else:
                xid, tz = rate_opt[0], rate_opt[1]
                m = p.match(tz)
                if m: processname, opt = m.groups()
                playid = playid

            matchesids.append(xid)
            code_tmp = {}
            opt = opt.split(",")
            opt_beishu = 1
            opts_list = []
            for op in opt:
                is_dg = "0"
                if "@" in op:  # 单关的解析倍数
                    option, opt_beishu = op.split("@")  # 解析倍数
                    is_dg = "1"
                else:
                    option = op

                proj_rate = []
                if is_chupiao_rate:  # 未支付订单使用投注赔率，方案详情使用出票赔率
                    chupiao_rate = rate.get(processname, {}).get(playid, {})
                    proj_rate = chupiao_rate.get(option) if chupiao_rate.get(option) else []

                ratestr = ""
                if proj_rate:
                    ratestr = "%s#%s" % (option, proj_rate[0]) if is_dg == "0" else "%s#%s@%s" % (
                        option, proj_rate[0], opt_beishu)

                if code_tmp:
                    code_tmp.get("code").append({
                        "opt": option,
                        # "rate": proj_rate,
                        "beishu": str(int(beishu) * int(opt_beishu)),
                        # "ratestr": ratestr,
                        "ismark": "0"

                    })
                else:
                    code_tmp.update({
                        "playid": playid,
                        "processname": processname,
                        "code": [{
                            "opt": option,
                            # "rate": proj_rate,
                            "beishu": str(beishu * int(opt_beishu)) if beishu and opt_beishu else 1,
                            # "ratestr": ratestr,
                            "ismark": "0"
                        }],

                    })
            if tz_opt.has_key(xid):
                tz_opt[xid].append(code_tmp)
            else:
                tz_opt.update({xid: [code_tmp]})

        return matchesids, tz_opt

    def deal_jc_tickets(self, tickets, project_data, lotid):
        """处理足球的电子票号对阵信息
        """
        ret = []
        if not tickets:
            return ret

        fileorcode = project_data.get("fileorcode")
        danma = project_data.get("danma") if project_data else ""
        playid = project_data.get("playid", "")
        beishu = project_data.get("beishu", "")
        issuc = project_data.get("issuc")

        # bean = InfoBean()
        matchesids, tz_opt = self.deal_fileorcode(fileorcode, playid, beishu=beishu)
        danma_list = self.deal_danma(danma)
        matches_info = self.get_matches_by_matchids(matchesids, lotid)

        for ticket in tickets:
            matches = []
            ticketid = ticket.get("ticketid", "")
            if issuc == "1" or ticketid:
                matchesids, tmp_dict, tickets = self.deal_tickets_ratelist(ticket)
            else:
                matchesids, tmp_dict, tickets = self.deal_fileorcode(ticket)

            rqlist_info = self.deal_rq_list_info(lotid, ticket)
            for matchesid in matchesids:
                tmp_opt = []
                for match in matches_info:
                    if match.get("ID", "") == matchesid:
                        result = bean.get_jc_result(match, lotid)
                        processname = match.get("PROCESSNAME", "")
                        ticket_opt = tmp_dict.get(processname)

                        for opt in ticket_opt:
                            opt.update({
                                "result": result.get(opt.get("playid"), "")
                            })
                            tmp_opt.append(opt)
                        # expect = dtime.strptime(match.get("PROCESSDATE", ""), "%Y%m%d").strftime("%Y-%m-%d")

                        # detail_url = ""
                        # if lotid == "46":
                        #     detail_url = InfoBean().get_proj_detail_url(lotid, match.get("INFOID", ""))
                        # elif lotid == "47":
                        #     detail_url = InfoBean().get_proj_detail_url(lotid, match.get("INFOID", ""))
                        # if lotid == "46":
                        #     detail_url = InfoBean().get_proj_detail_url(lotid, expect, processname)
                        # elif lotid == "47":
                        #     detail_url = InfoBean().get_proj_detail_url(lotid, match.get("PROCESSDATE", ""),
                        #                                                 processname)
                        matches.append({
                            "homename": match.get("ZCNAME", "")[:4],
                            "awayname": match.get("KCNAME", "")[:4],
                            "matchesid": match.get("ID", ""),
                            "codelist": tmp_opt,
                            "processname": processname,
                            "half_score": match.get("BCBF", ""),
                            "score": match.get("QCBF", ""),
                            "rangqiu": match.get("RANGQIUNUM", ""),
                            "iscancel": match.get("ISCANCEL", ""),
                            "isdanma": "1" if processname in danma_list else "0",
                            "yszf": rqlist_info.get(processname, {}).get("277", ""),
                            "rangfen": rqlist_info.get(processname, {}).get("275", ""),
                            "yszjqs": rqlist_info.get(processname, {}).get("406", ""),
                        })
            ticket["matches"] = matches
            ret.append(ticket)
        return ret

    def deal_tickets_ratelist(self, ticket):
        """解析电子票号的ratelist，
        """
        matchesids = []
        tmp_dict = {}
        p = re.compile('(\d+)\[(.+)\]')
        tz_pattern = re.compile('.+\[(.+)\]')
        rate_list = ticket.get("ratelist", "").split("/")
        code_list = ticket.get("fileorcode", "").split("/")

        playid = ticket.get("wtype", "")
        beishu = ticket.get("beishu")
        ticket_matchesids = []

        if not rate_list:
            return matchesids, tmp_dict, ticket

        try:
            for i in range(len(rate_list)):
                code_tmp = {}
                if not rate_list[i]:
                    continue

                processname, opt = rate_list[i].split("→")
                tz_m = tz_pattern.match(rate_list[i])
                tz_opt = tz_m.groups()[0] if tz_m else ""

                code_opt = code_list[i].split("|")
                xid = code_opt[0]
                matchesids.append(xid)
                ticket_matchesids.append(xid)
                if len(code_opt) == 3:
                    m = p.match(code_opt[2])
                    if m:
                        playid, option = m.groups()

                opts = tz_opt.split(",")
                for op in opts:
                    if "#" in op:
                        option, rateinfo = op.split("#")
                    else:
                        rateinfo = option

                    if "@" in rateinfo:
                        proj_rate, beishu = op.split("@")
                    else:
                        proj_rate = rateinfo

                    proj_rate = [proj_rate, ]
                    if code_tmp:
                        code_tmp.get("code").append({
                            "opt": option,
                            "rate": proj_rate,
                            "beishu": beishu
                        })
                    else:
                        code_tmp.update({
                            "playid": playid,
                            "code": [{
                                "opt": option,
                                "rate": proj_rate,
                                "beishu": beishu
                            }]
                        })
                if tmp_dict.has_key(processname):
                    tmp_dict[processname].append(code_tmp)
                else:
                    tmp_dict.update({processname: [code_tmp]})
        except:
            logger.error(traceback.format_exc())
            logger.info("chupiao ratelist error:%s", ticket)
            matchesids = []
            tmp_dict = {}

        return matchesids, tmp_dict, ticket

    def deal_rq_list_info(self, lotid, tickets):
        """解析rqlist 获取让球和让分数据
        """
        rqlist = tickets.get("rq_list", "0")
        if rqlist == "0" or rqlist == "":
            return {}

        tmp_dict = {}
        # u'1301→[主+58.5]/1302→[主+58.5]/1303→[主+58.5]' u'1301→[140.5]/1302→[140.5]/1303→[140.5]/1304→[140.5]/1305→[140.5]'
        rq_list = rqlist.split("/")
        try:
            for code in rq_list:
                processname, opt = code.split("→")
                _playid, tz_opt = opt.split("[")
                tz_opt = tz_opt[:-1]
                playid = tickets.get("playid")

                if playid in ["312", "313"]:
                    playid = _playid

                if playid == "275":  # 让分去掉（主）
                    tz_opt = tz_opt[1:]

                if tmp_dict.has_key(processname):
                    tmp_dict.update({playid: tz_opt})
                else:
                    tmp_dict.setdefault(processname, {playid: tz_opt})
        except:
            logger.error(traceback.format_exc())
            logger.info("chupiao rangfen error:%s", tickets)
            tmp_dict = {}

        return tmp_dict

    def get_jc_result(self, match, lotid):

        result = {}
        if lotid == "46":
            result = self.parse_jz_Result(match)
        elif lotid == "47":
            result = self.parse_jl_Result(match)

        return result

    def parseSfResult(self, score, rangfen):
        # 解析胜负赛果
        # arr = score.split(':')
        ret = float(score[1]) + float(rangfen) - float(score[0])
        if ret > 0:
            return '1'
        else:
            return '2'

    def parseSfcResult(self, score):
        # 解析胜分差赛果
        # arr = score.split(':')
        dif = int(score[1]) - int(score[0])
        if dif > 0:
            # 主胜
            l = (dif - 1) / 5 + 1
            if l > 6: l = 6
            return '%02d' % l
        else:
            # 客胜
            l = (- dif - 1) / 5 + 1
            if l > 6: l = 6
            return '%2d' % (10 + l)

    def parseDxfResult(self, score, yszf):
        # 大小分
        # arr = score.split(':')
        total = Decimal(score[0]) + Decimal(score[1])
        if total > Decimal(yszf):
            return '1'
        elif total < Decimal(yszf):
            return '2'
        else:
            return ''

    def parse_jl_Result(self,match):
        # 解析赛果

        presetscore = match.get("presetScore", "0")
        score = match.get("score", "0")
        rangfen = match.get("rangfen", "0")
        matchstate = match.get("matchState", "0")


        # 274
        # 胜负
        # 275
        # 让分胜负
        # 276
        # 胜分差
        # 277
        # 大小分
        if matchstate != "4":
            return {}

        if not score:
            return {}
        ret = {}
        home, away = score.split(':')

        result = self.parseSfResult([home, away], 0)
        ret.update({"274": result})
        result = self.parseSfResult([home, away], rangfen)
        ret.update({"274": result})
        result = self.parseSfcResult([home, away])
        ret.update({"276": result})
        result = self.parseDxfResult([home, away], presetscore)
        ret.update({"277": result})
        return ret


    def parseSpfResult(self, score, rangqiu):
        # 解析让球胜平负赛果
        # arr = score.split(':')
        # logger.debug(arr)
        # logger.debug(rangqiu)
        ret = int(score[0]) + int(rangqiu) - int(score[1])
        logger.debug(ret)
        if ret > 0:
            return '3'
        elif ret == 0:
            return '1'
        else:
            return '0'

    def parseJqsResult(self, score):
        # 解析进球数赛果
        # arr = score.split(':')
        ret = int(score[0]) + int(score[1])
        if ret > 7:
            return '7'
        else:
            return str(ret)

    def parseBqcResult(self, halfScore, score):
        # 解析半全场赛果
        return '%s-%s' % (self.parseSpfResult(halfScore, 0), self.parseSpfResult(score, 0))

    def parseBfResult(self, score, arr):
        # 解析比分赛果
        bfarr = ["1:0", "2:0", "2:1", "3:0", "3:1", "3:2", "4:0", "4:1", "4:2", "5:0", "5:1", "5:2", "0:0",
                 "1:1", "2:2", "3:3",
                 "0:1", "0:2", "1:2", "0:3", "1:3", "2:3", "0:4", "1:4", "2:4", "0:5", "1:5", "2:5"]
        if bfarr.count(score) > 0:
            return score
        # arr = score.split(':')
        if int(arr[0]) > int(arr[1]):
            return '胜其他'
        elif int(arr[0]) == int(arr[1]):
            return '平其他'
        else:
            return '负其他'

    def parseDxqResult(self, score, yszf):
        # 大小球
        # arr = score.split(':')
        total = Decimal(score[0]) + Decimal(score[1])
        if total > Decimal(yszf):
            return '1'
        elif total < Decimal(yszf):
            return '2'
        else:
            return ''

    def parse_jz_Result(self, match):
        # 解析赛果
        ret = {}
        rangqiu = match.get("rangQiu", "0")
        score = match.get("score", "0")
        halfscore = match.get("halfScore", "0")
        matchstate = match.get("matchState", "0")

        if matchstate != "4":
            return {}

        # 269
        # 让球胜平负
        # 270
        # 进球数
        # 271
        # 比分
        # 272
        # 半全场
        # 354
        # 胜平负
        if not score:
            return {}

        home, away = score.split(":")
        halfhome, halfaway = halfscore.split(":")

        result = self.parseSpfResult([home, away], rangqiu)
        ret.update({"269": result})

        result = self.parseJqsResult([home, away])
        ret.update({"270": result})

        result = self.parseBfResult(score, [home, away])
        ret.update({"271": result})

        result = self.parseBqcResult([halfhome, halfaway], [home, away])
        ret.update({"272": result})

        result = self.parseSpfResult([home, away], 0)
        ret.update({"354": result})

        # if wtype in [406]:  # 大小球
        #     return self.parseDxqResult(jzresult['qcbf'], jzresult['f_rangqiu'])


        return ret

    def get_lanuch_list(self, params):
        module = "trade"
        method = "launch_list"
        proj_list = {}
        with get_rpc_conn(module) as proxy:
            try:
                proj_list = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_PROJ_LIST_FAIL)

        proj_list = ujson.loads(proj_list)
        projs = proj_list.get("orders", [])
        count = proj_list.get("count", 0)
        orders = []
        for proj in projs:

            orderstatus = proj.get("f_orderstatus", "")
            isjprize = proj.get("f_isjprize", "")
            if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
                proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
            else:
                proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

            endtime = proj.get("f_firsttime")
            orders.append({
                "uid": proj.get("f_uid"),
                "pid": proj.get("f_pid", ""),
                "allmoney": proj.get("f_allmoney", ""),
                "beishu": proj.get("f_beishu", ""),
                "couponmoney": proj.get("f_couponmoney", ""),
                "expect": proj.get("f_expect", ""),
                "ticketnum": proj.get("f_ticketnum", "0"),
                "paymoney": proj.get("f_paymoney", ""),
                "selecttype": proj.get("f_selecttype", ""),
                "lotid": proj.get("f_lotid", ""),
                "crtime": proj.get("f_crtime", ""),
                "zhushu": proj.get("f_zhushu", ""),
                "wtype": proj.get("f_wtype", ""),
                "isjprize": proj.get("f_isjprize", ""),
                "getmoney": proj.get("f_getmoney", ""),
                "orderstatus": proj.get("f_orderstatus", ""),
                "proj_desc": proj_desc,
                "guarantee_odd": proj.get("f_guarantee_odd", ""),
                "mark": proj.get("f_remark", ""),
                "join_num": proj.get("join_num", 0),
                "endtime": endtime,
                "is_deadline": 1 if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) > endtime else 0
            })
        ret = {}
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        # biztype = params.get("biztype")
        ret.update({
            "list": orders,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno,
            # "biztype": biztype
        })

        return ret

    def get_jc_follow_proj_detail(self, params):
        """
        获取数字彩方案详情
        :param params:
        :return:
        """
        module = "trade"
        method = "follow_detail"
        proj_detail = []
        with get_rpc_conn(module) as proxy:
            proj_detail = proxy.call(method, params)
            proj_detail = ujson.loads(proj_detail)

        ret = {}

        if not proj_detail:
            raise ews.EwsError(ews.STATUS_PROJ_NOTFOUND)

        lotid = params.get("lotid")
        uid = params.get("uid")
        pid = params.get("pid")
        expect = proj_detail.get("f_expect", "")
        opencode = ""

        orderstatus = proj_detail.get("f_orderstatus", "")
        isjprize = proj_detail.get("f_isjprize", "")
        proj_desc = ""
        if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
            proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
        else:
            proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

        fileorcode = proj_detail.get("f_fileorcode", "")
        playid = proj_detail.get("f_wtype", "")
        beishu = proj_detail.get("f_beishu", "")
        danma = proj_detail.get("f_danma", "")
        lasttime = proj_detail.get("f_lasttime", "")
        fuid = str(proj_detail.get("fuid", ""))

        module = "user"
        method = "user_info"
        user_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                user_info = proxy.call(method, {"uid": fuid})
                user_info = ujson.loads(user_info)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)


        matchids, tz_opt = self.deal_fileorcode(fileorcode, playid, beishu=beishu)
        danma_list = self.deal_danma(danma)
        matches_info = self.jc_obj.get_matches_by_matchids(matchids)


        bet_match = []
        for matches in matches_info:
            matchcode = matches.get("matchCode", "")
            matchid = matches.get("matchId", "")

            result = self.get_jc_result(matches, lotid)
            opt = tz_opt.get(matchid, [])
            for op in opt:
                codes = op.get("codes", [])
                playresult = result.get(str(op.get("playid")), "")
                for code in codes:
                    code.update({
                        "ismark": "1" if opt == playresult else "0"
                    })
                op.update({
                    "result": playresult
                })

            if str(uid) == fuid or lasttime < time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()):
                opts = tz_opt.get(matchid, [])
            else:
                opts = []
            bet_match.append({
                "matchid": matchid,
                "league_name": matches.get("league", ""),
                "home": matches.get("home", ""),
                "away": matches.get("visiting", ""),
                "matchnum": matches.get("matchNum", ""),
                "endtime": matches.get("endTime", ""),
                "matchtime": matches.get("matchDate", "") + " " + matches.get("matchTime", ""),
                "rangfen": matches.get("rangfen", ""),
                "presetscore": matches.get("presetScore", ""),
                "status": matches.get("status", ""),
                "matchstate": matches.get("matchState", ""),
                "rangqiu": matches.get("rangQiu", ""),
                "matchcode": matchcode,
                "options": opts,
                "score": matches.get("score", ""),
                "halfScore": matches.get("halfScore", "")
            })

        top_five = self.get_top_five(lotid, pid) or []

        try:
            endtime = proj_detail.get("f_firsttime")
            ret.update({
                "uid": uid,
                "pid": proj_detail.get("f_pid", ""),
                "allmoney": proj_detail.get("f_allmoney", ""),
                "beishu": beishu,
                "couponmoney": proj_detail.get("f_couponmoney", ""),
                "expect": expect,
                "ticketnum": proj_detail.get("f_ticketnum", "0"),
                "paymoney": proj_detail.get("f_paymoney", ""),
                "selecttype": proj_detail.get("f_selecttype", ""),
                "lotid": proj_detail.get("f_lotid", ""),
                "crtime": proj_detail.get("f_crtime", ""),
                "zhushu": proj_detail.get("f_zhushu", ""),
                "wtype": playid,
                "isjprize": isjprize,
                "getmoney": proj_detail.get("f_getmoney", ""),
                "orderstatus": orderstatus,
                "fileorcode": fileorcode,
                "opencode": opencode,
                "proj_desc": proj_desc,
                "danma": danma,
                "ratelist": proj_detail.get("f_ratelist", ""),
                "ggtype": proj_detail.get("f_ggtype", ""),
                "isquchu": proj_detail.get("f_isquchu", ""),
                "rqlist": proj_detail.get("f_rqlist", ""),
                "matches": bet_match,
                "guarantee_odd": proj_detail.get("guarantee_odd", ""),
                "remark": proj_detail.get("remark", ""),
                # "join_num": "111",
                "endtime": endtime,
                "fid": proj_detail.get("f_fid"),
                "ptype": proj_detail.get("f_ptype"),
                "is_deadline": 1 if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) > endtime else 0,
                "launch_username": user_info.get("username", ""),
                "launch_photo": user_info.get("photo", ""),
                "launch_uid": fuid,
                "top_five": top_five,
                "commission": proj_detail.get("totalfeemoney", ""), #佣金
                "user_getmoney": proj_detail.get("totalgetmoney", "")
            })
        except:
            logger.error(traceback.format_exc())
            raise  # todo

        return ret

    def get_follow_wheelinfo(self):

        key = rediskey.REDIS_FOLLOW_WHEEL_INFO
        rds = db_pool.get_redis('main')
        wheelinfo = rds.get(key)
        return ujson.loads(wheelinfo) if wheelinfo else []

    def get_hot_seller(self):
        module = "trade"
        method = "hot_seller"
        hot_sellers = {}
        with get_rpc_conn(module) as proxy:
            try:
                hot_sellers = proxy.call(method, {})
                hot_sellers = ujson.loads(hot_sellers)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_FOLLOW_HOT_SELLER_ERROR)

        ret = []
        for hot in hot_sellers:
            ret.append({
                "photo": hot.get("f_headimg", "") if hot.get("f_headimg", "") else "",
                "username": hot.get("f_username", ""),
                "uid": hot.get("f_uid", "")
            })
        return ret

    def get_follow_list(self, params):
        module = "trade"
        method = "follow_list"
        proj_list = {}
        with get_rpc_conn(module) as proxy:
            try:
                proj_list = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_PROJ_LIST_FAIL)

        proj_list = ujson.loads(proj_list)
        projs = proj_list.get("orders", [])
        count = proj_list.get("count", 0)
        orders = []
        for proj in projs:

            orderstatus = proj.get("f_orderstatus", "")
            isjprize = proj.get("f_isjprize", "")
            if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
                proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
            else:
                proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

            orders.append({
                "uid": proj.get("f_uid", ""),
                "pid": proj.get("f_pid", ""),
                "allmoney": proj.get("f_allmoney", ""),
                "beishu": proj.get("f_beishu", ""),
                "couponmoney": proj.get("f_couponmoney", ""),
                "expect": proj.get("f_expect", ""),
                "ticketnum": proj.get("f_ticketnum", "0"),
                "paymoney": proj.get("f_paymoney", ""),
                "selecttype": proj.get("f_selecttype", ""),
                "lotid": proj.get("f_lotid", ""),
                "crtime": proj.get("f_crtime", ""),
                "zhushu": proj.get("f_zhushu", ""),
                "wtype": proj.get("f_wtype", ""),
                "isjprize": proj.get("f_isjprize", ""),
                "getmoney": proj.get("f_getmoney", ""),
                "orderstatus": proj.get("f_orderstatus", ""),
                "proj_desc": proj_desc,
                "guarantee_odd": proj.get("f_guarantee_odd", ""),
                "remark": proj.get("f_remark", ""),
                # "join_num": "111",
                "endtime": proj.get("f_firsttime")
            })
        ret = {}
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")
        ret.update({
            "list": orders,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno,
            "biztype": biztype
        })

        return ret

    def get_recommend_list(self, params):
        module = "trade"
        method = "launch_recommend_list"
        proj_list = {}
        with get_rpc_conn(module) as proxy:
            try:
                proj_list = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_PROJ_LIST_FAIL)

        proj_list = ujson.loads(proj_list)
        projs = proj_list.get("orders", [])
        count = proj_list.get("count", 0)
        orders = []
        for proj in projs:

            orderstatus = proj.get("f_orderstatus", "")
            isjprize = proj.get("f_isjprize", "")
            if str(orderstatus) in ["2", "3"] and str(isjprize) != "0":
                proj_desc = define.ORDER_JPRIZE_DESC.get(isjprize, "")
            else:
                proj_desc = define.ORDER_STATUS_DESC.get(orderstatus, "")

            endtime = proj.get("f_buyendtime")

            orders.append({
                "uid": proj.get("f_uid"),
                "pid": proj.get("f_pid", ""),
                "allmoney": proj.get("f_allmoney", ""),
                "beishu": proj.get("f_beishu", ""),
                "couponmoney": proj.get("f_couponmoney", ""),
                "expect": proj.get("f_expect", ""),
                "ticketnum": proj.get("f_ticketnum", "0"),
                "paymoney": proj.get("f_paymoney", ""),
                "selecttype": proj.get("f_selecttype", ""),
                "lotid": proj.get("f_lotid", ""),
                "crtime": proj.get("f_crtime", ""),
                "zhushu": proj.get("f_zhushu", ""),
                "wtype": proj.get("f_wtype", ""),
                "isjprize": proj.get("f_isjprize", ""),
                "getmoney": proj.get("f_getmoney", ""),
                "orderstatus": proj.get("f_orderstatus", ""),
                "proj_desc": proj_desc,
                "guarantee_odd": proj.get("f_guarantee_odd", ""),
                "remark": proj.get("f_remark", ""),
                "join_num": proj.get("f_follownum", ""),
                "continuswin": proj.get("f_continuswin", ""),
                "endtime": endtime,
                "is_deadline": 1 if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) > endtime else 0,
                "launch_username": proj.get("username", ""),
                "launch_photo": proj.get("photo", "") if proj.get("photo", "") else "",
                "launch_uid": proj.get("launch_uid"),
                "pscore": proj.get("f_pscore"),
                "hotflag": self.get_hot_flag(proj.get("f_follownum", "0"))

            })
        ret = {}
        pageno = params.get("pageno")
        pagesize = params.get("pagesize")
        biztype = params.get("biztype")
        ret.update({
            "list": orders,
            "count": count,
            "all_page": (count / int(pagesize)) + 1,
            "curr_page": pageno,
            # "biztype": biztype
        })

        return ret

    def get_hot_flag(self, follow_num):
        """hot flag"""
        follow_num = float(follow_num)
        hotflag = 1
        if follow_num >= 0 and follow_num <=20:
            hotflag = 1
        elif follow_num >= 21 and follow_num <=50:
            hotflag = 2
        elif follow_num >=51 and follow_num <= 100:
            hotflag = 3
        elif follow_num >= 101 and follow_num <= 200:
            hotflag = 4
        else:
            hotflag = 5

        return hotflag

    def get_seller_info(self, params):
        module = "trade"
        method = "seller_info"
        seller_info = {}
        with get_rpc_conn(module) as proxy:
            try:
                seller_info = proxy.call(method, params)
            except:
                logger.error(traceback.format_exc())
                raise ews.EwsError(ews.STATUS_FOLLOW_HOT_SELLER_ERROR)

        seller_info = ujson.loads(seller_info)
        uid = params.get("uid")
        ret = {
            "uid": seller_info.get("f_uid", ""),
            "username": seller_info.get("f_username", ""),
            "photo": seller_info.get("f_headimg", "") if seller_info.get("f_headimg", "") else "",
            "prizepnum": seller_info.get("f_prizepnum", ""),
            "pnum": seller_info.get("f_pnum", 0),
            "followprize": seller_info.get("f_followprize", ""),
            "continuswin": seller_info.get("f_continuswin", ""),
            "introduction": seller_info.get("f_introduction", ""),
            "history_gains": self.get_history_gains(uid),
            "totalprize": seller_info.get("totalprize", "")
        }
        return ret

    def get_history_gains(self, uid):
        r = db_pool.get_redis("main")
        key = rediskey.REDIS_SELLER_HISTORY_GAINS.format(uid=uid)

        history_gains = r.get(key)
        if not history_gains:
            module = "trade"
            method = "history_gains"
            history_gains = {}
            with get_rpc_conn(module) as proxy:
                try:
                    history_gains = proxy.call(method, {"uid": uid})
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_FOLLOW_HOT_SELLER_ERROR)

            history_gains = ujson.loads(history_gains)
            orders = history_gains.get("orders", [])
            all_count = history_gains.get("count", 0)
            win_count = 0
            for order in orders:
                totalgetmoney = order.get("f_totalgetmoney", 0)
                if float(totalgetmoney) > 0:
                    win_count += 1

            gains_str = "%s投%s中" % (all_count, win_count)
            r.setex(key, gains_str, 30 * 60)
        else:
            gains_str = history_gains

        return gains_str

    def get_top_five(self, lotid, fid):
        r = db_pool.get_redis("main")
        key = rediskey.REDIS_FOLLOW_PROJ_TOP_FIVE.format(fid=fid)

        top_five = r.get(key)
        if not top_five:
            module = "trade"
            method = "follow_top_five"
            resp = []
            with get_rpc_conn(module) as proxy:
                try:
                    resp = proxy.call(method, {"fid": fid, "lotid": lotid})
                    resp = ujson.loads(resp)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_FOLLOW_HOT_SELLER_ERROR)

            uids = [sp.get("f_uid") for sp in resp]

            if not uids:
                return []

            module = "user"
            method = "userinfo_by_uids"
            user_info = []
            with get_rpc_conn(module) as proxy:
                try:
                    user_info = proxy.call(method, {"uids": uids})
                    # user_info = ujson.loads(user_info)
                except:
                    logger.error(traceback.format_exc())
                    raise ews.EwsError(ews.STATUS_USER_INFO_FAIL)

            userinfo_by_uid = {user.get("f_uid"): user for user in user_info}

            top_five = []
            for top in resp:
                uid = top.get("f_uid")
                uinfo = userinfo_by_uid.get(uid, {})
                if not uinfo:
                    continue
                top_five.append({
                    "username": uinfo.get("f_username", ""),
                    "uid": uinfo.get("f_uid", ""),
                    "allmoney": top.get("f_allmoney", ""),
                    "getmoney": top.get("f_getmoeny", ""),
                    "commission": float(top.get("f_getmoeny", 0)) * 0.1
                })
            r.setex(key, ujson.dumps(top_five), 30 * 60)
        else:
            top_five = ujson.loads(top_five)

        return top_five
