#coding=utf-8
from decimal import *

_GGTYPE_={
"1"   :{  "ID":"1" ,    "Name":"2串1",      "nName":"2*1",     "PlayNum":"2",  "ZhuShu":"1",     "SelCodeNum":"2"               },
"2"   :{  "ID":"2" ,    "Name":"2串3",      "nName":"2*3",     "PlayNum":"2",  "ZhuShu":"3",     "SelCodeNum":"1,2"             },
"3"   :{  "ID":"3" ,    "Name":"3串1",      "nName":"3*1",     "PlayNum":"3",  "ZhuShu":"1",     "SelCodeNum":"3"               },
"4"   :{  "ID":"4" ,    "Name":"3串4",      "nName":"3*4",     "PlayNum":"3",  "ZhuShu":"4",     "SelCodeNum":"2,3"             },
"5"   :{  "ID":"5" ,    "Name":"3串6",      "nName":"3*6",     "PlayNum":"3",  "ZhuShu":"6",     "SelCodeNum":"1,2"             },
"6"   :{  "ID":"6" ,    "Name":"3串7",      "nName":"3*7",     "PlayNum":"3",  "ZhuShu":"7",     "SelCodeNum":"1,2,3"           },
"7"   :{  "ID":"7" ,    "Name":"4串1",      "nName":"4*1",     "PlayNum":"4",  "ZhuShu":"1",     "SelCodeNum":"4"               },
"8"   :{  "ID":"8" ,    "Name":"4串4",      "nName":"4*4",     "PlayNum":"4",  "ZhuShu":"4",     "SelCodeNum":"3"               },
"9"   :{  "ID":"9" ,    "Name":"4串5",      "nName":"4*5",     "PlayNum":"4",  "ZhuShu":"5",     "SelCodeNum":"3,4"             },
"10"  :{  "ID":"10",    "Name":"4串6",      "nName":"4*6",     "PlayNum":"4",  "ZhuShu":"6",     "SelCodeNum":"2"               },
"11"  :{  "ID":"11",    "Name":"4串10",     "nName":"4*10",    "PlayNum":"4",  "ZhuShu":"10",    "SelCodeNum":"1,2"             },
"12"  :{  "ID":"12",    "Name":"4串11",     "nName":"4*11",    "PlayNum":"4",  "ZhuShu":"11",    "SelCodeNum":"2,3,4"           },
"13"  :{  "ID":"13",    "Name":"4串14",     "nName":"4*14",    "PlayNum":"4",  "ZhuShu":"14",    "SelCodeNum":"1,2,3"           },
"14"  :{  "ID":"14",    "Name":"4串15",     "nName":"4*15",    "PlayNum":"4",  "ZhuShu":"15",    "SelCodeNum":"1,2,3,4"         },
"15"  :{  "ID":"15",    "Name":"5串1",      "nName":"5*1",     "PlayNum":"5",  "ZhuShu":"1",     "SelCodeNum":"5"               },
"16"  :{  "ID":"16",    "Name":"5串5",      "nName":"5*5",     "PlayNum":"5",  "ZhuShu":"5",     "SelCodeNum":"4"               },
"17"  :{  "ID":"17",    "Name":"5串6",      "nName":"5*6",     "PlayNum":"5",  "ZhuShu":"6",     "SelCodeNum":"4,5"             },
"18"  :{  "ID":"18",    "Name":"5串10",     "nName":"5*10",    "PlayNum":"5",  "ZhuShu":"10",    "SelCodeNum":"2"               },
"19"  :{  "ID":"19",    "Name":"5串15",     "nName":"5*15",    "PlayNum":"5",  "ZhuShu":"15",    "SelCodeNum":"1,2"             },
"20"  :{  "ID":"20",    "Name":"5串16",     "nName":"5*16",    "PlayNum":"5",  "ZhuShu":"16",    "SelCodeNum":"3,4,5"           },
"21"  :{  "ID":"21",    "Name":"5串20",     "nName":"5*20",    "PlayNum":"5",  "ZhuShu":"20",    "SelCodeNum":"2,3"             },
"22"  :{  "ID":"22",    "Name":"5串25",     "nName":"5*25",    "PlayNum":"5",  "ZhuShu":"25",    "SelCodeNum":"1,2,3"           },
"23"  :{  "ID":"23",    "Name":"5串26",     "nName":"5*26",    "PlayNum":"5",  "ZhuShu":"26",    "SelCodeNum":"2,3,4,5"         },
"24"  :{  "ID":"24",    "Name":"5串30",     "nName":"5*30",    "PlayNum":"5",  "ZhuShu":"30",    "SelCodeNum":"1,2,3,4"         },
"25"  :{  "ID":"25",    "Name":"5串31",     "nName":"5*31",    "PlayNum":"5",  "ZhuShu":"31",    "SelCodeNum":"1,2,3,4,5"       },
"26"  :{  "ID":"26",    "Name":"6串1",      "nName":"6*1" ,    "PlayNum":"6",  "ZhuShu":"1",     "SelCodeNum":"6"               },
"27"  :{  "ID":"27",    "Name":"6串6",      "nName":"6*6" ,    "PlayNum":"6",  "ZhuShu":"6",     "SelCodeNum":"5"               },
"28"  :{  "ID":"28",    "Name":"6串7",      "nName":"6*7" ,    "PlayNum":"6",  "ZhuShu":"7",     "SelCodeNum":"5,6"             },
"29"  :{  "ID":"29",    "Name":"6串15",     "nName":"6*15",    "PlayNum":"6",  "ZhuShu":"15",    "SelCodeNum":"2"               },
"30"  :{  "ID":"30",    "Name":"6串20",     "nName":"6*20",    "PlayNum":"6",  "ZhuShu":"20",    "SelCodeNum":"3"               },
"31"  :{  "ID":"31",    "Name":"6串21",     "nName":"6*21",    "PlayNum":"6",  "ZhuShu":"21",    "SelCodeNum":"1,2"             },
"32"  :{  "ID":"32",    "Name":"6串35",     "nName":"6*35",    "PlayNum":"6",  "ZhuShu":"35",    "SelCodeNum":"2,3"             },
"33"  :{  "ID":"33",    "Name":"6串41",     "nName":"6*41",    "PlayNum":"6",  "ZhuShu":"41",    "SelCodeNum":"1,2,3"           },
"34"  :{  "ID":"34",    "Name":"6串42",     "nName":"6*42",    "PlayNum":"6",  "ZhuShu":"42",    "SelCodeNum":"3,4,5,6"         },
"35"  :{  "ID":"35",    "Name":"6串50",     "nName":"6*50",    "PlayNum":"6",  "ZhuShu":"50",    "SelCodeNum":"2,3,4"           },
"36"  :{  "ID":"36",    "Name":"6串56",     "nName":"6*56",    "PlayNum":"6",  "ZhuShu":"56",    "SelCodeNum":"1,2,3,4"         },
"37"  :{  "ID":"37",    "Name":"6串57",     "nName":"6*57",    "PlayNum":"6",  "ZhuShu":"57",    "SelCodeNum":"2,3,4,5,6"       },
"38"  :{  "ID":"38",    "Name":"6串62",     "nName":"6*62",    "PlayNum":"6",  "ZhuShu":"62",    "SelCodeNum":"1,2,3,4,5"       },
"39"  :{  "ID":"39",    "Name":"6串63",     "nName":"6*63",    "PlayNum":"6",  "ZhuShu":"63",    "SelCodeNum":"1,2,3,4,5,6"     },
"40"  :{  "ID":"40",    "Name":"单关",      "nName":"1*1",     "PlayNum":"1",  "ZhuShu":"1",     "SelCodeNum":"1"               },
"41"  :{  "ID":"41",    "Name":"7串1",      "nName":"7*1",     "PlayNum":"7",  "ZhuShu":"1",     "SelCodeNum":"7"               },
"42"  :{  "ID":"42",    "Name":"7串7",      "nName":"7*7",     "PlayNum":"7",  "ZhuShu":"7",     "SelCodeNum":"6"               },
"43"  :{  "ID":"43",    "Name":"7串8",      "nName":"7*8",     "PlayNum":"7",  "ZhuShu":"8",     "SelCodeNum":"6,7"             },
"44"  :{  "ID":"44",    "Name":"7串21",     "nName":"7*21",    "PlayNum":"7",  "ZhuShu":"21",    "SelCodeNum":"5"               },
"45"  :{  "ID":"45",    "Name":"7串35",     "nName":"7*35",    "PlayNum":"7",  "ZhuShu":"35",    "SelCodeNum":"4"               },
"46"  :{  "ID":"46",    "Name":"7串120",    "nName":"7*120",   "PlayNum":"7",  "ZhuShu":"120",   "SelCodeNum":"2,3,4,5,6,7"     },
"47"  :{  "ID":"47",    "Name":"7串127",    "nName":"7*127",   "PlayNum":"7",  "ZhuShu":"127",   "SelCodeNum":"1,2,3,4,5,6,7"   },
"48"  :{  "ID":"48",    "Name":"8串1",      "nName":"8*1",     "PlayNum":"8",  "ZhuShu":"1",     "SelCodeNum":"8"               },
"49"  :{  "ID":"49",    "Name":"8串8",      "nName":"8*8",     "PlayNum":"8",  "ZhuShu":"8",     "SelCodeNum":"7"               },
"50"  :{  "ID":"50",    "Name":"8串9",      "nName":"8*9",     "PlayNum":"8",  "ZhuShu":"9",     "SelCodeNum":"7,8"             },
"51"  :{  "ID":"51",    "Name":"8串28",     "nName":"8*28",    "PlayNum":"8",  "ZhuShu":"28",    "SelCodeNum":"6"               },
"52"  :{  "ID":"52",    "Name":"8串56",     "nName":"8*56",    "PlayNum":"8",  "ZhuShu":"56",    "SelCodeNum":"5"               },
"53"  :{  "ID":"53",    "Name":"8串70",     "nName":"8*70",    "PlayNum":"8",  "ZhuShu":"70",    "SelCodeNum":"4"               },
"54"  :{  "ID":"54",    "Name":"8串247",    "nName":"8*247",   "PlayNum":"8",  "ZhuShu":"247",   "SelCodeNum":"2,3,4,5,6,7,8"   },
"55"  :{  "ID":"55",    "Name":"8串255",    "nName":"8*255",   "PlayNum":"8",  "ZhuShu":"255",   "SelCodeNum":"1,2,3,4,5,6,7,8" },
"56"  :{  "ID":"56",    "Name":"3串3" ,     "nName":"3*3",     "PlayNum":"3",  "ZhuShu":"3",     "SelCodeNum":"2"               },
"57"  :{  "ID":"57",    "Name":"6串22",     "nName":"6*22",    "PlayNum":"6",  "ZhuShu":"22",    "SelCodeNum":"4,5,6"           },
"58"  :{  "ID":"58",    "Name":"单关固赔",  "nName":"1*1",     "PlayNum":"1",  "ZhuShu":"1",     "SelCodeNum":"1"               }
}

def getGGType(ggtype):
    key = str(ggtype)
    return _GGTYPE_[key]

#竞彩专用 ： 四舍六入五成双保留2位小数
#小数点后第三位如果大于5 进位
#小数点后第三位如果小于5 则舍去
#小数点后第三位如果等于5，判断小数点后第二位是奇数则进位，是偶数则舍去
def sixRound(rate,scale=2):
    s = str(rate)
    if s.find('.') < 0:
        s = s + '.'
    if len(s) - s.find('.') < 4:
        s = s + '000'

    point = s.find('.') + scale
    head = s[:point+1]
    tail = s[point+1:]
    flag = int(tail[0])
    if flag < 5:
        return Decimal(head)
    elif flag > 5:
        return Decimal(head) + Decimal(1)/Decimal(pow(10,scale))
    else:
        if head[-1] in '02468':
            return Decimal(head)
        else:
            return Decimal(head) + Decimal(1)/Decimal(pow(10,scale))

