# encoding=utf-8

from common import Math
from logic.Split import Config
import copy
import Spliter_Common
from util.tools import Log

logger = Log().getLog()


class Spliter(Spliter_Common.Spliter):
    def __init__(self, lotid):
        self.lotId = lotid
        self.GGType_JC = Config.TICKET_INFO[str(lotid)]
        self.TICK_RE = Config.TICKET_RESTARICT[str(lotid)]
        self.ZHUSHU = 0

    # 总体的入口
    def splitCodes(self, prjInfo):
        ret_list = list()
        cc_dict = dict()
        ret = list()
        ccArray = prjInfo['fileorcode'].split('/')
        danma = prjInfo['danma'].strip()

        # 胆码标志
        danmaflag = 0
        if '' != danma:
            danmaflag = 1

        for info in ccArray:
            tmp_key = info.split('|')[0]

            if tmp_key in cc_dict.keys():
                cc_dict[tmp_key].append(info)
            else:
                cc_dict[tmp_key] = list()
                cc_dict[tmp_key].append(info)

        for info in prjInfo['ggtype'].split(','):
            tmp_info = self.GGType_JC[info]
            ret.append({'filelist': self.PlayNum_CM(tmp_info, cc_dict, prjInfo['wtype'], prjInfo['beishu'], info),
                        'ggtype': info})
        for filelist in ret:
            for info in filelist['filelist']:
                tmpcode, wtype = self.orgaize_fileorcode(info, prjInfo['wtype'])
                fileorcode = tmpcode
                beishu = prjInfo['beishu']
                flag = tmpcode.find('@')
                zhushu = self.countzhushu(tmpcode, filelist['ggtype'])

                # 去除单一玩法
                if 1 == int(prjInfo['isquchu']) and flag < 0:
                    # logging.info( tmpcode )
                    ret_quchu = self.moveSinglePlay(tmpcode)
                    if not ret_quchu:
                        continue

                # 判断胆码
                if 1 == danmaflag:
                    if not self.splitFileorcodeDanma(tmpcode, danma):
                        continue

                # 拆分单关
                if 58 == int(filelist['ggtype']) and flag >= 0:
                    fileorcode = tmpcode.split('@')[0] + ']'
                    beishu = int((tmpcode.split('@')[-1]).split(']')[0]) * int(prjInfo['beishu'])

                tmp_dict = {'fileorcode': fileorcode, 'ggtype': filelist['ggtype'], 'zhushu': zhushu, 'wtype': wtype}
                logger.debug(tmp_dict)
                ret_list += self.orgaize_beishu(tmp_dict, beishu)
        ret_list = self.merge_tickets(ret_list)
        return ret_list

    def merge_tickets(self, tickets):
        cur_matches = 0
        start = 0
        merged_tickets = []
        tickets.sort(key=lambda t: t.get('wtype'))
        logger.debug(tickets)
        if int(tickets[0].get('ggtype')) == 58:
            if len(tickets) == 1:
                return tickets
            max_matches = Config.MAX_MATCHES[int(tickets[0].get('wtype'))]
            if len(set([t.get('beishu') for t in tickets])) == 1 and len(set([t.get('wtype') for t in tickets])) == 1:        # 倍数和玩法一致再合票
                for index in range(1, len(tickets)):
                    max_matches = min(max_matches, Config.MAX_MATCHES[int(tickets[index].get('wtype'))])
                    if cur_matches == max_matches or index + 1 == len(tickets):
                        merged_tickets.append({
                            'fileorcode': '/'.join([t.get('fileorcode') for t in tickets[start: index + 1]]),
                            'ggtype': 58,
                            'zhushu': sum([int(t.get('zhushu')) for t in tickets[start: index + 1]]),
                            'wtype': tickets[0].get('wtype') if len(set([t.get('wtype') for t in tickets[start: index + 1]])) == 1 else (312 if int(self.lotId) == 46 else 313),
                            'beishu': tickets[0].get('beishu')
                        })
                        if index + 1 < len(tickets):
                            max_matches = Config.MAX_MATCHES[int(tickets[index + 1].get('wtype'))]
                        start = index + 1
                        cur_matches = 0
                    elif cur_matches > max_matches:
                        merged_tickets.append({
                            'fileorcode': '/'.join([t.get('fileorcode') for t in tickets[start: index]]),
                            'ggtype': 58,
                            'zhushu': sum([int(t.get('zhushu')) for t in tickets[start: index]]),
                            'wtype': tickets[0].get('wtype') if len(set([t.get('wtype') == 1 for t in tickets[start: index]])) == 1 else (312 if int(self.lotId) == 46 else 313),
                            'beishu': tickets[0].get('beishu')
                        })
                        max_matches = Config.MAX_MATCHES[int(tickets[index].get('wtype'))]
                        start = index
                        cur_matches = 1
                    elif cur_matches < max_matches:
                        cur_matches += 1
                return merged_tickets
        else: # 过关
            for t in tickets:
                wtype_list = [code.split('|')[2].split('[')[0] if len(code.split('|')) == 3 else t.get('wtype') for code in t.get('fileorcode').split('/')]
                if len(wtype_list) > min([Config.MAX_MATCHES[int(wtype)] for wtype in wtype_list]):
                    t.update({'printdetail': 1})
        return tickets

    # 组织投注内容
    def PlayNum_CM(self, tmp_info, cc_dict, wtype, beishu, ggtype):
        playnum = int(tmp_info['PlayNum'])
        cc_list = cc_dict.keys()
        ret_list = list()
        tmp_code = list()
        finally_list = list()

        ret_m = Math.combination(cc_list, playnum)

        for info in ret_m:
            ret_code = list()
            tmp_list = list()
            for i in info:
                tmp_list.append(cc_dict[i])

            self.orgaize_code(tmp_list, ret_code, tmp_code)

            ret_list += copy.deepcopy(ret_code)


        finally_list = ret_list
        """
        if 58 == int(ggtype):
            for info in ret_list:
                for i in info:
                    head = i.split('[')[0]
                    for j in (i.split('[')[-1].split(']')[0]).split(','):
                        finally_list.append([head + '[' + j + ']'])

        else:
            finally_list = ret_list
        """

        return finally_list

    # 组织号码
    def orgaize_code(self, code_src, ret_code, tmp_code):

        if len(tmp_code) + 1 == len(code_src):
            tmp_src = code_src[len(tmp_code)]
            for info in tmp_src:
                i = copy.deepcopy(tmp_code)
                i.append(info)
                ret_code.append(i)

        else:
            item = code_src[len(tmp_code)]
            for info in item:
                tmp_code.append(info)
                self.orgaize_code(code_src, ret_code, tmp_code)
                tmp_code.remove(info)

    # 组织票的玩法
    def orgaize_fileorcode(self, code_list, wtype):
        tmp_dict = dict()
        tmp_list = list()
        ret_str = ''
        tmp_wtype = ''
        ret_wtype = ''
        flag = True

        # 混投则取第一个投注内容的玩法作为标杆
        if int(wtype) in Config.HT_LIST:
            tmp_wtype = int(code_list[0].split('|')[-1].split('[')[0])

        for info in code_list:
            if int(wtype) in Config.HT_LIST and flag:
                if tmp_wtype != int(info.split('|')[-1].split('[')[0]):
                    ret_wtype = int(wtype)
                    flag = False
                else:
                    ret_wtype = tmp_wtype

            tmp_dict[info.split('|')[1]] = info

        for info in sorted(tmp_dict.keys()):
            tmp_list.append(tmp_dict[info])

        ret_str = '/'.join(tmp_list)

        # 如果方案不是混投则票玩法就是方案的玩法
        if '' == ret_wtype:
            ret_wtype = wtype

        return ret_str, ret_wtype

    # 拆解倍数
    def orgaize_beishu(self, code_dict, beishu):
        beishu = int(beishu)
        ret_list = list()
        zhushu = code_dict['zhushu']
        beishu_flag = self.TICK_RE['money'] / (int(zhushu) * 2)

        # 判断标杆
        if beishu_flag > self.TICK_RE['beishu']:
            beishu_flag = self.TICK_RE['beishu']

        tmp_dict = dict()
        while beishu > beishu_flag:
            tmp_dict = copy.deepcopy(code_dict)
            tmp_dict['beishu'] = beishu_flag
            ret_list.append(tmp_dict)
            beishu -= beishu_flag

        if beishu > 0:
            tmp_dict = copy.deepcopy(code_dict)
            tmp_dict['beishu'] = beishu
            ret_list.append(tmp_dict)

        return ret_list

    def countnum(self, codearr, index, start, all):
        if start > all:
            self.ZHUSHU = self.ZHUSHU + 1
        else:
            for i in range(index, len(codearr)):
                length = len(codearr[i].split(','))
                for j in range(0, length):
                    self.countnum(codearr, i + 1, start + 1, all)

                    # 计算注数

    def countzhushu(self, fileorcode, ggtype):
        self.ZHUSHU = 0
        gginfo = self.GGType_JC[ggtype]['SelCodeNum']
        for ggitem in gginfo.split(','):
            self.countnum(fileorcode.split('/'), 0, 1, int(ggitem))
        return self.ZHUSHU

    # 去除单一玩法
    def moveSinglePlay(self, fileorcode):
        flagplay = fileorcode.split('/')[0].split('|')[-1].split('[')[0]
        for info in fileorcode.split('/'):
            if int(flagplay) != int(info.split('|')[-1].split('[')[0]):
                return True
            else:
                continue

        return False

    # 拆分胆码
    def splitFileorcodeDanma(self, fileorcode, danma):
        code_list = list()
        for info in fileorcode.split('/'):
            code_list.append(int(info.split('|')[0]))

        # logging.debug(fileorcode)
        # logging.debug(danma)
        danma_list = list()
        for info in danma.split('/'):
            danma_list.append(int(info.split('|')[0]))

        code_list = set(code_list)
        danma_list = set(danma_list)

        for info in danma_list:
            if info not in code_list:
                return False

        return True


if __name__ == '__main__':
    args = {'danma': '',
            'fileorcode': '97630|7003|269[0]/97648|7005|354[0]/97649|7006|269[0]/97651|7013|269[0]/97653|7015|269[0]/97637|7024|354[0]',
            'ggtype': '1,3,26', 'beishu': '300', 'wtype': '312', 'isquchu': '0'}
    obj = Spliter_JC(46)
    ret = obj.splitCodes(args)
    for r in ret:
        print r
