#coding=utf-8

import os
import re
import sys
import copy
import logging
import operator
import traceback


from logic.Split import Config
import Spliter_Common

class Spliter( Spliter_Common.Spliter ):
    def __init__( self,lotid ):
          self.lotId       = lotid
          self.TICK_RE     = Config.TICKET_RESTARICT[str(lotid)]
          self.limitMoney  = self.TICK_RE['money']
          self.singleMoney = Config.SINGLEMONEY

    def splitCodes(self,prjInfo):
          allarray = prjInfo['fileorcode'].split('$')
          beishu   = int( prjInfo['beishu'] )

          #单注合票列表
          comb_list=list()
          ret1=list()

          #将投注码去除机选还是手选的标识
          for array1 in allarray:
            item=''
            index1=''
            for s in array1.split(','):
                if item=='':

                   item=s.split('@')[0]
                   index1=s.split('@')[1]
                else:
                   item+=','+s.split('@')[0]

            Arr=item.split(",")
            zhushu=1
            for i in range(0,len(Arr)):
                zhushu*=len(Arr[i])

            #处理单式
            if zhushu==1:
                ret=self.Danshi(comb_list,Arr,beishu,zhushu,index1)
                ret1+=ret
                continue

            #处理超过10000注的复式
            if zhushu>(self.limitMoney/self.singleMoney):
                c_dict=dict()
                #将数组以字典的形式存起来，键为在数组的下标，值为长度，并按值降序
                for i in range(0,len(Arr)):
                   if i in c_dict.keys():
                      c_dict[i].append(len(Arr[i]))
                   else:
                      c_dict[i]=list()
                      c_dict[i].append(len(Arr[i]))
                sorted_dict = sorted(c_dict.iteritems(), key=operator.itemgetter(1),reverse=True)
                sum=1
                #计算所有位数中包含号码最多的四位的注数
                for i in range(0,4):
                     sum*= sorted_dict[i][1][0]
                fz=(self.limitMoney/self.singleMoney)/sum
                ret=self.complicFushi(sorted_dict,Arr,fz,beishu,index1)
                ret1+=ret
            #处理普通复式
            else:
                ret=self.Fushi(Arr,beishu,index1)
                ret1+=ret
          if len(comb_list)>0:
                tmp_ret=self.splitBeishu('$'.join(comb_list),self.TICK_RE['beishu'],beishu,len(comb_list))
                ret1+=tmp_ret
          return ret1
          
    #处理单式
    def Danshi(self,tmp_list,Arr,beishu,zhushu,index1):
          ret_list=list()
          Arr1=copy.deepcopy(Arr)
          for i in range(len(Arr1)):
                  Arr1[i]=Arr1[i]+'@'+index1  
          tmp_list.append(','.join(Arr1))
          if len(tmp_list)==5:
             ret_list=self.splitBeishu('$'.join(tmp_list),self.TICK_RE['beishu'],beishu,len(tmp_list))
             del tmp_list[:5]
          return ret_list

    #处理超过10000注的复式
    def complicFushi(self,sorted_dict,Arr,fz,beishu,index1):
          ret=list()
          i=0
          Arr1=copy.deepcopy(Arr)
          if 5==len(sorted_dict):
             while(i<len(Arr[sorted_dict[4][0]])):
                     Arr1[sorted_dict[4][0]]=Arr[sorted_dict[4][0]][i:i+fz]
                     i=i+fz
                     ret1=self.Fushi(Arr1,beishu,index1)
                     ret+=ret1
          else:
              #fz1和fz2主要处理的是最后两位的
              fz1,fz2=1,1
              #若前四位的注数较少，则调整后面的阀值，以便拆成更少的票
              if(fz>sorted_dict[4][1][0]):
                fz1=fz/sorted_dict[4][1][0]
                if(fz1>sorted_dict[5][1][0]):
                   fz2=fz1/sorted_dict[5][1][0]

              while(i<len(Arr[sorted_dict[4][0]])):
                   Arr1[sorted_dict[4][0]]=Arr[sorted_dict[4][0]][i:i+fz]
                   j=0
                   while(j<len(Arr[sorted_dict[5][0]])):
                      Arr1[sorted_dict[5][0]]=Arr[sorted_dict[5][0]][j:j+fz1]
                      k=0
                      while(k<len(Arr[sorted_dict[6][0]])):
                        Arr1[sorted_dict[6][0]]=Arr[sorted_dict[6][0]][k:k+fz2]
                        ret1=self.Fushi(Arr1,beishu,index1)
                        ret+=ret1
                        k+=fz2
                      j+=fz1
                   i=i+fz
          return ret

    #处理复式
    def Fushi(self,Arr,beishu,index1):
          zhushu=1
          for i in range(0,len(Arr)):                                            
            zhushu*=len(Arr[i])
          Arr1=copy.deepcopy(Arr)
          for i in range(len(Arr1)):
            Arr1[i]=Arr1[i]+'@'+index1
          ret_list1=list()
          tmp_list1=list()
          tmp_list1.append(','.join(Arr1))
          #单票最大倍数
          max_beishu = self.TICK_RE['beishu']
          #可拆分最大倍数
          lmt_beishu = max_beishu
          if zhushu*self.singleMoney * max_beishu > self.limitMoney:
             lmt_beishu=self.limitMoney/(zhushu*self.singleMoney)

             ret_list1=self.splitBeishu('$'.join(tmp_list1),lmt_beishu,beishu,zhushu)
          else:
             ret_list1=self.splitBeishu('$'.join(tmp_list1),self.TICK_RE['beishu'],beishu,zhushu)
          return ret_list1

    #拆分倍数
    def splitBeishu(self,code,lmt_beishu,beishu,zhushu):
          ret =list()
          b   =beishu

          while b>lmt_beishu:
                item={'code':code,'beishu':lmt_beishu,'zhushu':zhushu}
                ret.append(item)
                b=b-lmt_beishu
          if b>0:
                item={'code':code,'beishu':b,'zhushu':zhushu}
                ret.append(item)
          return ret



if __name__ == '__main__':
   #args="0123456789|0123456789|0123|12345|56789|0123|0"
   args={'fileorcode':'01234@0,01234@0,01234@0,01234@0,01234@0,01234@0,01234@0', 'beishu':'1', 'wtype':'135'}
   obj = Spliter(4)
   ret=obj.splitCodes(args)
   print ret
