#encoding=utf-8

# 方案状态
PROSTATE_INIT     =   0      #方案初始态
PROSTATE_SPLITED  =   100    #已经切票
PROSTATE_FINISHED =   300    #方案已出票
PROSTATE_PARTRT   =   290    #部分撤单
PROSTATE_FAUIL    =   -200   #方案失败

# 票状态
CPSTATE_INIT      =   0      #票初始态
CPSTATE_SUC       =   300    #已成功
CPSTATE_FAUIL     =   -200   #失败

# 玩法列表
DANSHI_WTYPE      =   [312, 313]
FUSHI_WTYPE       =   [269,270,271,272,354,274,275,276,277,313]


# 每次查询的条数
CUNTNUMBER        =   50

# 限制重复发送次数
CNTNUM = 10000

# 彩种对应表
LOT_OBJ = {'46':'FB', '47':'BK', '28':'LGL'}

#竞彩足球
WTYPENAME = {}
WTYPENAME['353'] = 'HAD'           #胜平负-
WTYPENAME['354'] = 'HAD'           #胜平负
WTYPENAME['294'] = 'HHAD'          #让球胜平负-
WTYPENAME['269'] = 'HHAD'          #让球胜平负
WTYPENAME['297'] = 'HAFU'          #半全场胜平负-
WTYPENAME['272'] = 'HAFU'          #半全场胜平负
WTYPENAME['271'] = 'CRS'           #比分
WTYPENAME['296'] = 'CRS'           #比分-
WTYPENAME['295'] = 'TTG'           #总进球数-
WTYPENAME['270'] = 'TTG'           #总进球数
WTYPENAME['273'] = 'OUOE'          #上下盘单双
WTYPENAME['355'] = 'FCA'           #足球混合过关-
WTYPENAME['312'] = 'FCA'           #足球混合过关

#竞彩篮球
WTYPENAME['275'] = 'HDC'           #让分胜负
WTYPENAME['277'] = 'HILO'          #大小分
WTYPENAME['276'] = 'WNM'           #胜分差
WTYPENAME['274'] = 'MNL'           #胜负
WTYPENAME['313'] = 'BCA'           #篮球混合过关

PooId = {'46':{'3005':{'HHAD':'11796','HAFU':'11797','CRS':'11798','TTG':'11799','OUOE':'11800','HAD':'11795'},
	             '3006':{'HHAD':'11802','HAFU':'11803','CRS':'11804','TTG':'11805','OUOE':'11806','HAD':'11801'},
	             '3007':{'HHAD':'11808','HAFU':'11809','CRS':'11810','TTG':'11811','OUOE':'11812','HAD':'11807'},
	             '3008':{'HHAD':'11814','HAFU':'11815','CRS':'11816','TTG':'11817','OUOE':'11818','HAD':'11813'},
	             '3009':{'HHAD':'11902','HAFU':'11903','CRS':'11904','TTG':'11905','OUOE':'11906','HAD':'11901'}},
         '47':{'3304':{'HDC':'11819','MNL':'11820','WNM':'11821','HILO':'11822'},
               '3305':{'HDC':'11823','MNL':'11824','WNM':'11825','HILO':'11826'},
               '3306':{'HDC':'11827','MNL':'11828','WNM':'11829','HILO':'11830'},
               '3307':{'HDC':'11907','MNL':'11908','WNM':'11909','HILO':'11910'}}}

WNM = {'11':'0-0','12':'0-1','13':'0-2','14':'0-3','15':'0-4','16':'0-5',
       '01':'1-0','02':'1-1','03':'1-2','04':'1-3','05':'1-4','06':'1-5'}

#投注类型
CHOICE_WAY = dict()
CHOICE_WAY['ZX']  = '10'
CHOICE_WAY['JX']  = '20'
CHOICE_WAY['FZ']  = '30'
CHOICE_WAY['TZD'] = '40'

#票类型
TICKET_WAY = dict()
TICKET_WAY['PT'] = '10'
TICKET_WAY['ZP'] = '20'
TICKET_WAY['CS'] = '30'

#游戏方式
GAME_WAY = dict()
GAME_WAY['28'] = dict()
GAME_WAY['28']['GW'] = '1'

#拆票所容许最好倍数
TICKET_RESTARICT = { '1':{'beishu':20, 'money':20000,},  #SFC投注单最多20倍
                     '3':{'beishu':99, 'money':20000,},
                     '4':{'beishu':99, 'money':20000,},
                     '5':{'beishu':99, 'money':20000,},
                    '15':{'beishu':99, 'money':20000,},
                    '17':{'beishu':99, 'money':20000,},
                    '28':{'beishu':99, 'money':20000, 'zjmoney':30000},
                    '44':{'beishu':99, 'money':20000,},
                    '45':{'beishu':99, 'money':20000,},
                    '46':{'beishu':99, 'money':20000,},
                    '47':{'beishu':99, 'money':20000,},
                    '60':{'beishu':99, 'money':20000,},
                    '61':{'beishu':20, 'money':20000,}}  #任9投注单最多20倍

#竞足过关方式
GGType_JZ={
       '1' :{'Name':'2串1'   ,'PlayNum':'2',      'ZhuShu':'1',   'SelCodeNum':'2',              'GTDID':'2001'},
       '2' :{'Name':'2串3'   ,'PlayNum':'2',      'ZhuShu':'3',   'SelCodeNum':'1,2',            'GTDID':'2003'},
       '3' :{'Name':'3串1'   ,'PlayNum':'3',      'ZhuShu':'1',   'SelCodeNum':'3',              'GTDID':'3001'},
       '4' :{'Name':'3串4'   ,'PlayNum':'3',      'ZhuShu':'4',   'SelCodeNum':'2,3',            'GTDID':'3004'},
       '5' :{'Name':'3串6'   ,'PlayNum':'3',      'ZhuShu':'6',   'SelCodeNum':'1,2',            'GTDID':'3006'},
       '6' :{'Name':'3串7'   ,'PlayNum':'3',      'ZhuShu':'7',   'SelCodeNum':'1,2,3',          'GTDID':'3007'},
       '7' :{'Name':'4串1'   ,'PlayNum':'4',      'ZhuShu':'1',   'SelCodeNum':'4',              'GTDID':'4001'},
       '8' :{'Name':'4串4'   ,'PlayNum':'4',      'ZhuShu':'4',   'SelCodeNum':'3',              'GTDID':'4004'},
       '9' :{'Name':'4串5'   ,'PlayNum':'4',      'ZhuShu':'5',   'SelCodeNum':'3,4',            'GTDID':'4005'},
       '10':{'Name':'4串6'   ,'PlayNum':'4',      'ZhuShu':'6',   'SelCodeNum':'2',              'GTDID':'4006'},
       '11':{'Name':'4串10'  ,'PlayNum':'4',      'ZhuShu':'10',  'SelCodeNum':'1,2',            'GTDID':'4010'},
       '12':{'Name':'4串11'  ,'PlayNum':'4',      'ZhuShu':'11',  'SelCodeNum':'2,3,4',          'GTDID':'4011'},
       '13':{'Name':'4串14'  ,'PlayNum':'4',      'ZhuShu':'14',  'SelCodeNum':'1,2,3',          'GTDID':'4014'},
       '14':{'Name':'4串15'  ,'PlayNum':'4',      'ZhuShu':'15',  'SelCodeNum':'1,2,3,4',        'GTDID':'4015'},
       '15':{'Name':'5串1'   ,'PlayNum':'5',      'ZhuShu':'1',   'SelCodeNum':'5',              'GTDID':'5001'},
       '16':{'Name':'5串5'   ,'PlayNum':'5',      'ZhuShu':'5',   'SelCodeNum':'4',              'GTDID':'5005'},
       '17':{'Name':'5串6'   ,'PlayNum':'5',      'ZhuShu':'6',   'SelCodeNum':'4,5',            'GTDID':'5006'},
       '18':{'Name':'5串10'  ,'PlayNum':'5',      'ZhuShu':'10',  'SelCodeNum':'2',              'GTDID':'5010'},
       '19':{'Name':'5串15'  ,'PlayNum':'5',      'ZhuShu':'15',  'SelCodeNum':'1,2',            'GTDID':'5015'},
       '20':{'Name':'5串16'  ,'PlayNum':'5',      'ZhuShu':'16',  'SelCodeNum':'3,4,5',          'GTDID':'5016'},
       '21':{'Name':'5串20'  ,'PlayNum':'5',      'ZhuShu':'20',  'SelCodeNum':'2,3',            'GTDID':'5020'},
       '22':{'Name':'5串25'  ,'PlayNum':'5',      'ZhuShu':'25',  'SelCodeNum':'1,2,3',          'GTDID':'5025'},
       '23':{'Name':'5串26'  ,'PlayNum':'5',      'ZhuShu':'26',  'SelCodeNum':'2,3,4,5',        'GTDID':'5026'},
       '24':{'Name':'5串30'  ,'PlayNum':'5',      'ZhuShu':'30',  'SelCodeNum':'1,2,3,4',        'GTDID':'5030'},
       '25':{'Name':'5串31'  ,'PlayNum':'5',      'ZhuShu':'31',  'SelCodeNum':'1,2,3,4,5',      'GTDID':'5031'},
       '26':{'Name':'6串1'   ,'PlayNum':'6',      'ZhuShu':'1',   'SelCodeNum':'6',              'GTDID':'6001'},
       '27':{'Name':'6串6'   ,'PlayNum':'6',      'ZhuShu':'6',   'SelCodeNum':'5',              'GTDID':'6006'},
       '28':{'Name':'6串7'   ,'PlayNum':'6',      'ZhuShu':'7',   'SelCodeNum':'5,6',            'GTDID':'6007'},
       '29':{'Name':'6串15'  ,'PlayNum':'6',      'ZhuShu':'15',  'SelCodeNum':'2',              'GTDID':'6015'},
       '30':{'Name':'6串20'  ,'PlayNum':'6',      'ZhuShu':'20',  'SelCodeNum':'3',              'GTDID':'6020'},
       '31':{'Name':'6串21'  ,'PlayNum':'6',      'ZhuShu':'21',  'SelCodeNum':'1,2',            'GTDID':'6021'},
       '32':{'Name':'6串35'  ,'PlayNum':'6',      'ZhuShu':'35',  'SelCodeNum':'2,3',            'GTDID':'6035'},
       '33':{'Name':'6串41'  ,'PlayNum':'6',      'ZhuShu':'41',  'SelCodeNum':'1,2,3',          'GTDID':'6041'},
       '34':{'Name':'6串42'  ,'PlayNum':'6',      'ZhuShu':'42',  'SelCodeNum':'3,4,5,6',        'GTDID':'6042'},
       '35':{'Name':'6串50'  ,'PlayNum':'6',      'ZhuShu':'50',  'SelCodeNum':'2,3,4',          'GTDID':'6050'},
       '36':{'Name':'6串56'  ,'PlayNum':'6',      'ZhuShu':'56',  'SelCodeNum':'1,2,3,4',        'GTDID':'6056'},
       '37':{'Name':'6串57'  ,'PlayNum':'6',      'ZhuShu':'57',  'SelCodeNum':'2,3,4,5,6',      'GTDID':'6057'},
       '38':{'Name':'6串62'  ,'PlayNum':'6',      'ZhuShu':'62',  'SelCodeNum':'1,2,3,4,5',      'GTDID':'6062'},
       '39':{'Name':'6串63'  ,'PlayNum':'6',      'ZhuShu':'63',  'SelCodeNum':'1,2,3,4,5,6',    'GTDID':'6063'},
       '40':{'Name':'单关'   ,'PlayNum':'1',      'ZhuShu':'1',   'SelCodeNum':'1',              'GTDID':'1001'},
       '41':{'Name':'7串1'   ,'PlayNum':'7',      'ZhuShu':'1',   'SelCodeNum':'7',              'GTDID':'7001'},
       '42':{'Name':'7串7'   ,'PlayNum':'7',      'ZhuShu':'7',   'SelCodeNum':'6',              'GTDID':'7007'},
       '43':{'Name':'7串8'   ,'PlayNum':'7',      'ZhuShu':'8',   'SelCodeNum':'6,7',            'GTDID':'7008'},
       '44':{'Name':'7串21'  ,'PlayNum':'7',      'ZhuShu':'21',  'SelCodeNum':'5',              'GTDID':'7021'},
       '45':{'Name':'7串35'  ,'PlayNum':'7',      'ZhuShu':'35',  'SelCodeNum':'4',              'GTDID':'7035'},
       '46':{'Name':'7串120' ,'PlayNum':'7',      'ZhuShu':'120', 'SelCodeNum':'2,3,4,5,6,7',    'GTDID':'7120'},
       '47':{'Name':'7串127' ,'PlayNum':'7',      'ZhuShu':'127', 'SelCodeNum':'1,2,3,4,5,6,7',  'GTDID':'7127'},
       '48':{'Name':'8串1'   ,'PlayNum':'8',      'ZhuShu':'1',   'SelCodeNum':'8',              'GTDID':'8001'},
       '49':{'Name':'8串8'   ,'PlayNum':'8',      'ZhuShu':'8',   'SelCodeNum':'7',              'GTDID':'8008'},
       '50':{'Name':'8串9'   ,'PlayNum':'8',      'ZhuShu':'9',   'SelCodeNum':'7,8',            'GTDID':'8009'},
       '51':{'Name':'8串28'  ,'PlayNum':'8',      'ZhuShu':'28',  'SelCodeNum':'6',              'GTDID':'8028'},
       '52':{'Name':'8串56'  ,'PlayNum':'8',      'ZhuShu':'56',  'SelCodeNum':'5',              'GTDID':'8056'},
       '53':{'Name':'8串70'  ,'PlayNum':'8',      'ZhuShu':'70',  'SelCodeNum':'4',              'GTDID':'8070'},
       '54':{'Name':'8串247' ,'PlayNum':'8',      'ZhuShu':'247', 'SelCodeNum':'2,3,4,5,6,7,8',  'GTDID':'8247'},
       '55':{'Name':'8串255' ,'PlayNum':'8',      'ZhuShu':'255', 'SelCodeNum':'1,2,3,4,5,6,7,8','GTDID':'8255'},
       '56':{'Name':'3串3'   ,'PlayNum':'3',      'ZhuShu':'3',   'SelCodeNum':'2',              'GTDID':'3003'},
       '57':{'Name':'6串22'  ,'PlayNum':'6',      'ZhuShu':'22',  'SelCodeNum':'4,5,6',          'GTDID':'6022'},
       '58':{'Name':'单关固赔', 'PlayNum':'1',     'ZhuShu':'1', 'SelCodeNum':'1',                'GTDID':'1001'}
}

#竞篮国光方式
GGType_JL={
       '1' :{'Name':'2串1'   ,'PlayNum':'2',      'ZhuShu':'1',   'SelCodeNum':'2',              'GTDID':'2001'},
       '2' :{'Name':'2串3'   ,'PlayNum':'2',      'ZhuShu':'3',   'SelCodeNum':'1,2',            'GTDID':'2003'},
       '3' :{'Name':'3串1'   ,'PlayNum':'3',      'ZhuShu':'1',   'SelCodeNum':'3',              'GTDID':'3001'},
       '4' :{'Name':'3串4'   ,'PlayNum':'3',      'ZhuShu':'4',   'SelCodeNum':'2,3',            'GTDID':'3004'},
       '5' :{'Name':'3串6'   ,'PlayNum':'3',      'ZhuShu':'6',   'SelCodeNum':'1,2',            'GTDID':'3006'},
       '6' :{'Name':'3串7'   ,'PlayNum':'3',      'ZhuShu':'7',   'SelCodeNum':'1,2,3',          'GTDID':'3007'},
       '7' :{'Name':'4串1'   ,'PlayNum':'4',      'ZhuShu':'1',   'SelCodeNum':'4',              'GTDID':'4001'},
       '8' :{'Name':'4串4'   ,'PlayNum':'4',      'ZhuShu':'4',   'SelCodeNum':'3',              'GTDID':'4004'},
       '9' :{'Name':'4串5'   ,'PlayNum':'4',      'ZhuShu':'5',   'SelCodeNum':'3,4',            'GTDID':'4005'},
       '10':{'Name':'4串6'   ,'PlayNum':'4',      'ZhuShu':'6',   'SelCodeNum':'2',              'GTDID':'4006'},
       '11':{'Name':'4串10'  ,'PlayNum':'4',      'ZhuShu':'10',  'SelCodeNum':'1,2',            'GTDID':'4010'},
       '12':{'Name':'4串11'  ,'PlayNum':'4',      'ZhuShu':'11',  'SelCodeNum':'2,3,4',          'GTDID':'4011'},
       '13':{'Name':'4串14'  ,'PlayNum':'4',      'ZhuShu':'14',  'SelCodeNum':'1,2,3',          'GTDID':'4014'},
       '14':{'Name':'4串15'  ,'PlayNum':'4',      'ZhuShu':'15',  'SelCodeNum':'1,2,3,4',         'GTDID':'4015'},
       '15':{'Name':'5串1'   ,'PlayNum':'5',      'ZhuShu':'1',   'SelCodeNum':'5',              'GTDID':'5001'},
       '16':{'Name':'5串5'   ,'PlayNum':'5',      'ZhuShu':'5',   'SelCodeNum':'4',              'GTDID':'5005'},
       '17':{'Name':'5串6'   ,'PlayNum':'5',      'ZhuShu':'6',   'SelCodeNum':'4,5',            'GTDID':'5006'},
       '18':{'Name':'5串10'  ,'PlayNum':'5',      'ZhuShu':'10',  'SelCodeNum':'2',              'GTDID':'5010'},
       '19':{'Name':'5串15'  ,'PlayNum':'5',      'ZhuShu':'15',  'SelCodeNum':'1,2',            'GTDID':'5015'},
       '20':{'Name':'5串16'  ,'PlayNum':'5',      'ZhuShu':'16',  'SelCodeNum':'3,4,5',          'GTDID':'5016'},
       '21':{'Name':'5串20'  ,'PlayNum':'5',      'ZhuShu':'20',  'SelCodeNum':'2,3',            'GTDID':'5020'},
       '22':{'Name':'5串25'  ,'PlayNum':'5',      'ZhuShu':'25',  'SelCodeNum':'1,2,3',          'GTDID':'5025'},
       '23':{'Name':'5串26'  ,'PlayNum':'5',      'ZhuShu':'26',  'SelCodeNum':'2,3,4,5',        'GTDID':'5026'},
       '24':{'Name':'5串30'  ,'PlayNum':'5',      'ZhuShu':'30',  'SelCodeNum':'1,2,3,4',        'GTDID':'5030'},
       '25':{'Name':'5串31'  ,'PlayNum':'5',      'ZhuShu':'31',  'SelCodeNum':'1,2,3,4,5',      'GTDID':'5031'},
       '26':{'Name':'6串1'   ,'PlayNum':'6',      'ZhuShu':'1',   'SelCodeNum':'6',              'GTDID':'6001'},
       '27':{'Name':'6串6'   ,'PlayNum':'6',      'ZhuShu':'6',   'SelCodeNum':'5',              'GTDID':'6006'},
       '28':{'Name':'6串7'   ,'PlayNum':'6',      'ZhuShu':'7',   'SelCodeNum':'5,6',            'GTDID':'6007'},
       '29':{'Name':'6串15'  ,'PlayNum':'6',      'ZhuShu':'15',  'SelCodeNum':'2',              'GTDID':'6015'},
       '30':{'Name':'6串20'  ,'PlayNum':'6',      'ZhuShu':'20',  'SelCodeNum':'3',              'GTDID':'6020'},
       '31':{'Name':'6串21'  ,'PlayNum':'6',      'ZhuShu':'21',  'SelCodeNum':'1,2',            'GTDID':'6021'},
       '32':{'Name':'6串35'  ,'PlayNum':'6',      'ZhuShu':'35',  'SelCodeNum':'2,3',            'GTDID':'6035'},
       '33':{'Name':'6串41'  ,'PlayNum':'6',      'ZhuShu':'41',  'SelCodeNum':'1,2,3',          'GTDID':'6041'},
       '34':{'Name':'6串42'  ,'PlayNum':'6',      'ZhuShu':'42',  'SelCodeNum':'3,4,5,6',        'GTDID':'6042'},
       '35':{'Name':'6串50'  ,'PlayNum':'6',      'ZhuShu':'50',  'SelCodeNum':'2,3,4',          'GTDID':'6050'},
       '36':{'Name':'6串56'  ,'PlayNum':'6',      'ZhuShu':'56',  'SelCodeNum':'1,2,3,4',        'GTDID':'6056'},
       '37':{'Name':'6串57'  ,'PlayNum':'6',      'ZhuShu':'57',  'SelCodeNum':'2,3,4,5,6',      'GTDID':'6057'},
       '38':{'Name':'6串62'  ,'PlayNum':'6',      'ZhuShu':'62',  'SelCodeNum':'1,2,3,4,5',      'GTDID':'6062'},
       '39':{'Name':'6串63'  ,'PlayNum':'6',      'ZhuShu':'63',  'SelCodeNum':'1,2,3,4,5,6',    'GTDID':'6063'},
       '40':{'Name':'单关'   ,'PlayNum':'1',      'ZhuShu':'1',   'SelCodeNum':'1',              'GTDID':'1001'},
       '41':{'Name':'7串1'   ,'PlayNum':'7',      'ZhuShu':'1',   'SelCodeNum':'7',              'GTDID':'7001'},
       '42':{'Name':'7串7'   ,'PlayNum':'7',      'ZhuShu':'7',   'SelCodeNum':'6',              'GTDID':'7007'},
       '43':{'Name':'7串8'   ,'PlayNum':'7',      'ZhuShu':'8',   'SelCodeNum':'6,7',            'GTDID':'7008'},
       '44':{'Name':'7串21'  ,'PlayNum':'7',      'ZhuShu':'21',  'SelCodeNum':'5',              'GTDID':'7021'},
       '45':{'Name':'7串35'  ,'PlayNum':'7',      'ZhuShu':'35',  'SelCodeNum':'4',              'GTDID':'7035'},
       '46':{'Name':'7串120' ,'PlayNum':'7',      'ZhuShu':'120', 'SelCodeNum':'2,3,4,5,6,7',    'GTDID':'7120'},
       '47':{'Name':'7串127' ,'PlayNum':'7',      'ZhuShu':'127', 'SelCodeNum':'1,2,3,4,5,6,7',  'GTDID':'7127'},
       '48':{'Name':'8串1'   ,'PlayNum':'8',      'ZhuShu':'1',   'SelCodeNum':'8',              'GTDID':'8001'},
       '49':{'Name':'8串8'   ,'PlayNum':'8',      'ZhuShu':'8',   'SelCodeNum':'7',              'GTDID':'8008'},
       '50':{'Name':'8串9'   ,'PlayNum':'8',      'ZhuShu':'9',   'SelCodeNum':'7,8',            'GTDID':'8009'},
       '51':{'Name':'8串28'  ,'PlayNum':'8',      'ZhuShu':'28',  'SelCodeNum':'6',              'GTDID':'8028'},
       '52':{'Name':'8串56'  ,'PlayNum':'8',      'ZhuShu':'56',  'SelCodeNum':'5',              'GTDID':'8056'},
       '53':{'Name':'8串70'  ,'PlayNum':'8',      'ZhuShu':'70',  'SelCodeNum':'4',              'GTDID':'8070'},
       '54':{'Name':'8串247' ,'PlayNum':'8',      'ZhuShu':'247', 'SelCodeNum':'2,3,4,5,6,7,8',  'GTDID':'8247'},
       '55':{'Name':'8串255' ,'PlayNum':'8',      'ZhuShu':'255', 'SelCodeNum':'1,2,3,4,5,6,7,8','GTDID':'8255'},
       '56':{'Name':'3串3'   ,'PlayNum':'3',      'ZhuShu':'3',   'SelCodeNum':'2',              'GTDID':'3003'},
       '57':{'Name':'6串22'  ,'PlayNum':'6',      'ZhuShu':'22',  'SelCodeNum':'4,5,6',          'GTDID':'6022'},
       '58':{'Name':'胜分差单关固赔', 'PlayNum':'1', 'ZhuShu':'1', 'SelCodeNum':'1',            'GTDID':'1001'}
}

#组合字典(大乐透和双色球可共用)
#m选n: COMB_DICT[m][n]
COMB_DICT = [
[ 1, 0, 0, 0, 0, 0, 0, 0 ],
[ 1, 1, 0, 0, 0, 0, 0, 0 ],
[ 1, 2, 1, 0, 0, 0, 0, 0 ],
[ 1, 3, 3, 1, 0, 0, 0, 0 ],
[ 1, 4, 6, 4, 1, 0, 0, 0 ],
[ 1, 5, 10, 10, 5, 1, 0, 0 ],
[ 1, 6, 15, 20, 15, 6, 1, 0 ],
[ 1, 7, 21, 35, 35, 21, 7, 1 ],
[ 1, 8, 28, 56, 70, 56, 28, 8 ],
[ 1, 9, 36, 84, 126, 126, 84, 36 ],
[ 1, 10, 45, 120, 210, 252, 210, 120 ],
[ 1, 11, 55, 165, 330, 462, 462, 330 ],
[ 1, 12, 66, 220, 495, 792, 924, 792 ],
[ 1, 13, 78, 286, 715, 1287, 1716, 1716 ],
[ 1, 14, 91, 364, 1001, 2002, 3003, 3432 ],
[ 1, 15, 105, 455, 1365, 3003, 5005, 6435 ],
[ 1, 16, 120, 560, 1820, 4368, 8008, 11440 ],
[ 1, 17, 136, 680, 2380, 6188, 12376, 19448 ],
[ 1, 18, 153, 816, 3060, 8568, 18564, 31824 ],
[ 1, 19, 171, 969, 3876, 11628, 27132, 50388 ],
[ 1, 20, 190, 1140, 4845, 15504, 38760, 77520 ],
[ 1, 21, 210, 1330, 5985, 20349, 54264, 116280 ],
[ 1, 22, 231, 1540, 7315, 26334, 74613, 170544 ],
[ 1, 23, 253, 1771, 8855, 33649, 100947, 245157 ],
[ 1, 24, 276, 2024, 10626, 42504, 134596, 346104 ],
[ 1, 25, 300, 2300, 12650, 53130, 177100, 480700 ],
[ 1, 26, 325, 2600, 14950, 65780, 230230, 657800 ],
[ 1, 27, 351, 2925, 17550, 80730, 296010, 888030 ],
[ 1, 28, 378, 3276, 20475, 98280, 376740, 1184040 ],
[ 1, 29, 406, 3654, 23751, 118755, 475020, 1560780 ],
[ 1, 30, 435, 4060, 27405, 142506, 593775, 2035800 ],
[ 1, 31, 465, 4495, 31465, 169911, 736281, 2629575 ],
[ 1, 32, 496, 4960, 35960, 201376, 906192, 3365856 ],
[ 1, 33, 528, 5456, 40920, 237336, 1107568, 4272048 ],
[ 1, 34, 561, 5984, 46376, 278256, 1344904, 5379616 ],
[ 1, 35, 595, 6545, 52360, 324632, 1623160, 6724520 ],
[ 1, 36, 630, 7140, 58905, 376992, 1947792, 8347680 ] ]

TICKET_INFO = {'46':GGType_JZ, '47':GGType_JL, '28':COMB_DICT, '3':COMB_DICT}

#竞彩混投玩法列表
HT_LIST = [312, 313]

#大乐透胆拖玩法
#DTWtype = [135, 143]
#大乐透、双色球胆拖玩法
DTWtype = [135, 143, 125]

#大乐透、双色球和票注数
LIMIT_NUM = 5

#大乐透混投玩法
#HTWTYPE = 389
#大乐透、双色球混投玩法
HTWTYPE = [389, 379]

#
PHTWTYPE=395

#
QHTWTYPE=392

#大乐透追加玩法
ZJWTYPE = ['98', '99', '143', '388']

#单注金额
SINGLEMONEY = 2
ZJSINGLEMONEY = 3

#
DSWTYPE  = {1:396, 4:390, 15:401, 17:399, 60:393, 61:403}
FSWTYPE  = {1:397, 4:391, 15:402, 17:400, 60:394, 61:404}
XDTWTYPE = {61:409}

#
CODENUM = {1:14, 4:7, 15:12, 17:8, 45:11, 60:5, 61:{'codenum':9, 'changcinum':14}}

# 竞彩各玩法最大场次
MAX_MATCHES = {
       269: 8,
       354: 8,
       270: 6,
       271: 4,
       272: 4,
       274: 8,
       275: 8,
       276: 4,
       277: 8,
}
