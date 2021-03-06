#coding=utf-8
import os
import time
import common.Math as Math
import jprize.JcConfig  as JcConfig
from decimal import *
from util.tools import Log
logger = Log().getLog()

#竞足票对象
class JzTicket:

    def __init__(self,ticket,jzresult):
        self._ticket = ticket #票对象
        self._jzresult = jzresult #赛果对象
        self.tkt_valid = True #票是否有效
        self.tkt_zhushu = 0  #票注数
        self.tkt_cancels =[] #票取消场次
        self.tkt_prize = 0   #单倍奖金
        self.tkt_preprize = 0 #单倍税前奖金
        self.tkt_returnprize = 0 #单倍返款
        self.tkt_returnnum  = 0 #单倍返还注数

    def handTicket(self):
        #计算票奖金
        matchList = self.parseCodeRate(self._ticket['f_ticketid'],self._ticket['f_fileorcode'],self._ticket['f_ratelist'])
        ggTypeInfo = JcConfig.getGGType(self._ticket['f_ggtype'])
        # logger.debug(Math.combination(matchList,int(ggTypeInfo['PlayNum'])))
        for items in Math.combination(matchList,int(ggTypeInfo['PlayNum'])):    #几串几
            gg_arr = ggTypeInfo['SelCodeNum'].split(',')  #选择场次数
            for sel in gg_arr:   #几关
                # logger.debug(Math.combination(items,int(sel)))
                for matchComb in Math.combination(items,int(sel)): #组合投注场次
                    comb_ret = self.handMatchComb(matchComb,self.tkt_cancels)
                    logger.debug(comb_ret)
                    if comb_ret['valid'] == False: #无效立即终止,提高效率
                        self.tkt_valid = False
                        return { 'tid':self._ticket['f_ticketid'],'orderid':self._ticket['f_orderid'],'valid':self.tkt_valid,
                                 'getmoney':0,'pregetmoney':0,'returnmoney':0,'returnnum':0 }
                    if comb_ret['isreturn'] == True: #返款
                        self.tkt_returnprize += comb_ret['pre_prize']
                        self.tkt_returnnum += comb_ret['zhushu']
                    else:
                        self.tkt_preprize += comb_ret['pre_prize'] #税前奖金
                        self.tkt_prize  += comb_ret['prize'] #税后奖金
                    self.tkt_zhushu += comb_ret['zhushu'] 
        
        getmoney = 0
        pregetmoney = 0
        returnmoney = 0
        returnnum = 0
        if self.tkt_valid == True:
            beishu = Decimal(self._ticket['f_beishu'])
            pregetmoney = JcConfig.sixRound(self.tkt_preprize*beishu)
            getmoney = JcConfig.sixRound(self.tkt_prize*beishu)
            returnmoney = Decimal(self.tkt_returnprize)*beishu
            returnnum = self.tkt_returnnum*self._ticket['f_beishu']
            """
            #多关单式，无取消场次，中奖的，以出票返回的maxmoney为准
            if len(matchList)>1 and self.tkt_zhushu == 1 and len(self.tkt_cancels) == 0 and self.tkt_prize>0 and self._ticket['maxmoney']>0: 
                pregetmoney = JcConfig.sixRound(Decimal(self._ticket['maxmoney']))
                getmoney = pregetmoney
                if (pregetmoney/beishu) > 10000: #单倍大于10000要扣税
                    getmoney = JcConfig.sixRound(Decimal(pregetmoney*Decimal('0.8')))
            """
                   
        return { 'tid':self._ticket['f_ticketid'],'orderid':self._ticket['f_orderid'],'valid':self.tkt_valid,
                 'getmoney':getmoney,'pregetmoney':pregetmoney,'returnmoney':returnmoney,'returnnum':returnnum }


    def handMatchComb(self,matchComb,tkt_cancels):
        #处理最终投注组合
        comb_valid = True   #是否有效
        comb_rate = Decimal('1.0') #赔率
        comb_zhushu = 1       #注数
        comb_cancelbeishu = 1   #取消倍数
        comb_isreturn = True     #是否还款
       
        for match in matchComb:
            comb_wtype = int(self._ticket['f_wtype'])
            if comb_wtype in [312, 313]: #混串解析投注内容里的玩法
                comb_wtype = int(match.wtype)

            comb_zhushu *= match.optCount()
            jzresult = self._jzresult.get(str(match.id))
            if jzresult is None:   #未审核的对阵
                comb_valid = False
                comb_isreturn = False
                comb_rate = 0
                break
            
            if int(jzresult['f_iscancel']) == 1:
                comb_cancelbeishu *= match.optCount()
                if tkt_cancels.count(match.name) == 0:
                    tkt_cancels.append(match.name)
                continue

            ret = self.parseResult(jzresult,comb_wtype)

            logger.debug(jzresult)
            logger.debug(ret)
            if match.contains(ret): #命中
                comb_rate *= match.getRate(ret)
                comb_isreturn = False
            else:
                comb_rate = 0
                comb_isreturn = False
        
        prize = 0 
        pre_prize = 0
        if comb_valid == True and comb_rate >0 : #有效组合计算奖金
            pre_prize = JcConfig.sixRound(comb_rate*Decimal(2))
            if pre_prize > 10000: #单注
                if len(matchComb) in [2,3] and pre_prize > 200000:
                    pre_prize = Decimal(200000) #2或3场过关投注时，单注最高奖金限额为20万元
                elif len(matchComb) in [4,5] and pre_prize > 500000:
                    pre_prize = Decimal(500000) #4或5场过关投注时，单注最高奖金限额为50万元
                elif len(matchComb)>=6 and pre_prize > 1000000:
                    pre_prize = Decimal(1000000) #6或7或8场过关投注时，单注最高奖金限额为100万元
                prize = JcConfig.sixRound(pre_prize*Decimal('0.8')) #扣税 
            else:
                prize = pre_prize  #无需扣税
            prize *= Decimal(comb_cancelbeishu) #和取消倍数相乘
            pre_prize *= Decimal(comb_cancelbeishu)
        return {'valid':comb_valid, 'zhushu':comb_zhushu, 'isreturn':comb_isreturn,'prize':prize,'pre_prize':pre_prize}       
        
        
    def parseCodeRate(self, tid, codes, rates):
        #解析投注内容和赔率
        codeList = codes.split('/')
        rateList = rates.split('/')
        if len(codeList) != len(rateList):
            raise Exception('parseCodeRate: codes length and rates length is not equals:[%s][%s][%s]' % (tid,codes,rates))
        logger.debug('parseCodeRate: ticket[%s] codes[%s] rates[%s]',tid,codes,rates)
        matchList = []
        for i in range(0,len(codeList)):
            code = codeList[i].strip()
            rate = rateList[i].strip()
            bet = code[code.find('[') + 1 : code.find(']')]  #玩法选项
            tempArr = code[:code.find('[')].split('|')  #xid|processname
            if len(tempArr)< 2 or len(tempArr)>3:
                raise Exception('parseCodeRate: error code formats:[%s]' % codes)
            name = rate[:rate.find('→')]
            if name != tempArr[1]:
                raise Exception('parseCodeRate: error code or ratelist formats:[%s][%s]' % (codes,rates))
            betrate = rate[rate.find('[') + 1 : rate.find(']')]
            wtype = self._ticket['f_wtype']
            if len(tempArr) == 3:  #针对混投
                wtype = tempArr[2]
            info = { 'id': tempArr[0], 'name':name, 'bet':bet, 'rate':betrate, 'wtype': wtype }
            match = JzMatch(info)
            matchList.append(match)

        return matchList

    def parseSpfResult(self, score, rangqiu):
        #解析让球胜平负赛果
        arr = score.split(':')
        logger.debug(arr)
        logger.debug(rangqiu)
        ret = int(arr[0]) + int(rangqiu) - int(arr[1])
        logger.debug(ret)
        if ret > 0:
            return '3'
        elif ret == 0:
            return '1'
        else:
            return '0'

    def parseJqsResult(self, score):
        #解析进球数赛果
        arr = score.split(':')
        ret = int(arr[0])+int(arr[1])
        if ret > 7:
            return '7'
        else:
            return str(ret)

    def parseBqcResult(self, halfScore, score):
        #解析半全场赛果
        return '%s-%s' % (self.parseSpfResult(halfScore,0),self.parseSpfResult(score,0))

    def parseBfResult(self, score):
        #解析比分赛果
        bfarr = ["1:0","2:0","2:1","3:0","3:1","3:2","4:0","4:1","4:2","5:0","5:1","5:2","0:0",
               "1:1","2:2","3:3",
               "0:1","0:2","1:2","0:3","1:3","2:3","0:4","1:4","2:4","0:5","1:5","2:5"]
        if bfarr.count(score)>0:
            return score
        arr = score.split(':')
        if int(arr[0]) > int(arr[1]) :
            return '胜其它'
        elif  int(arr[0])==int(arr[1]):
            return '平其它'
        else:
            return '负其它'

    def parseDxqResult(self,score,yszf):
        #大小球
        arr = score.split(':')
        total = Decimal(arr[0]) + Decimal(arr[1])
        if total > Decimal(yszf):
            return '1'
        elif total < Decimal(yszf):
            return '2'
        else:
            return ''

    def parseResult(self,jzresult,wtype):
        #解析赛果
        if wtype in [269,294]:
            return self.parseSpfResult(jzresult['f_qcbf'], jzresult['f_rangqiu'])
        elif wtype in [270,295]:
            return self.parseJqsResult(jzresult['f_qcbf'])
        elif wtype in [271,296]:
            return self.parseBfResult(jzresult['f_qcbf'])
        elif wtype in [272,297]:
            return self.parseBqcResult(jzresult['f_bcbf'], jzresult['f_qcbf'])
        elif wtype in [353,354]:
            return self.parseSpfResult(jzresult['f_qcbf'], 0)
        elif wtype in [406]: #大小球
            return self.parseDxqResult(jzresult['qcbf'], jzresult['f_rangqiu'])
        else:
            raise Exception('parseResult:undefined playtype[%s]'% wtype)

#竞足对阵
class JzMatch:

    def __init__(self,info):
        self.id = info['id'] #对阵ID
        self.name = info['name'] #对阵编号
        self.bet = info['bet'] #投注内容
        self.rate = info['rate'] #赔率
        self.wtype = info['wtype'] #玩法
        self.betlist = self.bet.split(',')
        self.ratemap = dict()
        for item in self.rate.split(','):
            itemArr = item.split('#')
            self.ratemap[itemArr[0]]=itemArr[1]


    def contains(self,opt):
        #是否包含投注选项
        return self.betlist.count(opt)

    def getRate(self,opt):
        #取选项赔率
        rate = self.ratemap[opt]
        return Decimal(str(rate))

    def optCount(self):
        #选项数目
        return len(self.betlist)
